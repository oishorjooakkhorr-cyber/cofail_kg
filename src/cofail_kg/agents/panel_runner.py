"""Panel runner: the four frozen agents on one manifest, one model at a time (protocol §9.2, §19).

Inference orchestration only. Like every agent-facing module it imports nothing from
`cofail_kg.evaluation` and reads only the agent-input sheet (via `run_agent`) and the PrimeKG cache
(§9.3, §19.1b). Model serving, runtime guards and evaluation live in `scripts/25_run_panel.py`.

Rules implemented here:
* Agent-major order: every query for agent 1 in manifest order, then agent 2, ... (§9.2). Each episode
  is a fresh conversation; nothing is carried between agents or episodes.
* Before an agent starts, its installed model identity must equal the frozen tag/digest/quantization,
  and every pinned input/config hash must match; otherwise nothing runs (`IdentityMismatch`).
* An episode is completed once its record exists with any §9.5 status, including failures. Resuming
  never reruns a completed episode, and records are write-once (§19; `save_episode_record`).
* A rerun of failed episodes happens only under a new run ID, for the §19 reasons
  (`RERUN_REASONS`), as attempt = previous attempt + 1 (`rerun_plan`).
* A progress file (episodes done / total, failures so far) is rewritten after every episode. It is a
  status file, not a result: it is replaced atomically and can always be rebuilt from the records.
"""

from __future__ import annotations

from datetime import datetime, timezone
import hashlib
import json
import os
from pathlib import Path
import uuid

from cofail_kg.agents.prompts import PROMPT_VERSION
from cofail_kg.agents.run_agent import run_episode as default_run_episode
from cofail_kg.agents.trace import load_episode_record, record_path

FAILED = ("TIMEOUT", "ERROR", "PARSE_FAIL")  # §9.5 technical failures
RERUN_REASONS = ("D4_FAIL", "D6_HOLD", "D7_HOLD", "CODE_CHANGE")  # §19: the only rerun routes


class IdentityMismatch(ValueError):
    """Installed model or pinned input differs from the frozen value; the run must not start."""


def file_sha256(path) -> str:
    return hashlib.sha256(Path(path).read_bytes()).hexdigest()


def manifest_query_ids(agent_inputs) -> list[str]:
    """Query IDs of an agent-input sheet, in sheet order; duplicates refused."""
    ids = [json.loads(line)["query_id"] for line in
           Path(agent_inputs).read_text(encoding="utf-8").splitlines() if line.strip()]
    if len(ids) != len(set(ids)) or not ids:
        raise ValueError(f"{agent_inputs}: empty sheet or duplicate query IDs")
    return ids


def episode_plan(agent_ids: list[str], query_ids: list[str]) -> list[tuple[str, str]]:
    """(agent_id, query_id) in agent-major order (§9.2)."""
    if len(set(agent_ids)) != len(agent_ids):
        raise ValueError("duplicate agent IDs")
    return [(a, q) for a in agent_ids for q in query_ids]


def check_identity(agent: dict, identity: dict) -> None:
    """Installed identity must equal the frozen tag, digest and quantization, with native tools."""
    for key in ("tag", "digest", "quantization"):
        if identity.get(key) != agent[key]:
            raise IdentityMismatch(f"{agent['agent_id']}: installed {key} {identity.get(key)!r} "
                                   f"!= frozen {agent[key]!r}")
    if "tools" not in identity.get("capabilities", []):
        raise IdentityMismatch(f"{agent['agent_id']}: installed model lacks native tools")


def check_hashes(expected: dict, root) -> None:
    """Every pinned file (path relative to root) must have its frozen SHA256."""
    for path, digest in sorted(expected.items()):
        actual = file_sha256(Path(root) / path)
        if actual != digest:
            raise IdentityMismatch(f"Pinned file changed: {path} ({actual} != {digest})")


def validate_completed(record: dict, agent: dict, config: dict, query_id: str, attempt: int) -> None:
    """A saved record may be skipped only when its provenance matches this run."""
    expected = {k: config[k] for k in ("run_id", "temperature", "seed", "num_ctx", "num_predict",
                                      "git_commit", "kg_fingerprint", "biohopr_revision")}
    expected.update(query_id=query_id, agent_id=agent["agent_id"], attempt=attempt,
                    model={k: agent[k] for k in ("tag", "digest", "quantization")},
                    prompt_version=f"{PROMPT_VERSION}:{config['prompt_sha256']}")
    for key, value in expected.items():
        if record.get(key) != value:
            raise ValueError(f"{query_id}/{agent['agent_id']}: saved {key} {record.get(key)!r} "
                             f"differs from this run's {value!r}")
    for key in ("page_size", "budget", "tool_schema_sha256"):
        if record["tool_config"][key] != config[key]:
            raise ValueError(f"{query_id}/{agent['agent_id']}: saved tool setting {key} differs")
    events = [e for e in record.get("log_events", []) if e.get("event") == "EPISODE_CONFIG"]
    wanted = {k: config[k] for k in ("source_sha256", "agent_inputs_sha256", "timeout_seconds",
                                     "request_timeout_seconds")}
    wanted["think"] = agent["think"]
    if len(events) != 1 or any(events[0].get(k) != v for k, v in wanted.items()):
        raise ValueError(f"{query_id}/{agent['agent_id']}: saved episode config differs")


def progress(runs_root, run_id: str, plan: list[tuple[str, str]], attempts: dict | None = None) -> dict:
    """Episodes done / total and failures so far, rebuilt from the saved records."""
    done, failures = 0, []
    for agent_id, query_id in plan:
        attempt = (attempts or {}).get((agent_id, query_id), 1)
        path = record_path(runs_root, run_id, query_id, agent_id, attempt)
        if path.exists():
            done += 1
            record = json.loads(path.read_text(encoding="utf-8"))
            if record["status"] in FAILED:
                failures.append({"agent_id": agent_id, "query_id": query_id,
                                 "status": record["status"], "cause": record.get("cause")})
    return {"run_id": run_id, "episodes_done": done, "episodes_total": len(plan),
            "failures_so_far": len(failures), "failures": failures,
            "updated_at": datetime.now(timezone.utc).isoformat()}


def write_progress(path, value: dict) -> None:
    """Replace the progress file atomically (status file, not a result)."""
    path = Path(path)
    path.parent.mkdir(parents=True, exist_ok=True)
    temporary = path.parent / f".{path.name}.{uuid.uuid4().hex}.tmp"
    try:
        with open(temporary, "x", encoding="utf-8", newline="\n") as handle:
            json.dump(value, handle, indent=2, sort_keys=True)
            handle.write("\n")
            handle.flush()
            os.fsync(handle.fileno())
        os.replace(temporary, path)
    finally:
        temporary.unlink(missing_ok=True)


def run_agent_block(agent: dict, config: dict, query_ids: list[str], *, check, on_episode,
                    run_episode=default_run_episode, attempts: dict | None = None) -> list[dict]:
    """All of one agent's queries in manifest order; completed episodes are skipped, never rerun.

    `check()` re-verifies identity/runtime before and after each new episode; `on_episode(query_id,
    record, new)` is called after every episode (new or skipped), e.g. to write progress.
    """
    records = []
    for query_id in query_ids:
        attempt = (attempts or {}).get((agent["agent_id"], query_id), 1)
        target = record_path(config["runs_root"], config["run_id"], query_id, agent["agent_id"], attempt)
        new = not target.exists()
        if new:
            check()
            run_episode(query_id, agent, config, attempt=attempt)
            check()  # The record is kept even if the identity check fails afterwards.
        record = load_episode_record(target)
        validate_completed(record, agent, config, query_id, attempt)
        records.append(record)
        on_episode(query_id, record, new)
    return records


def rerun_plan(previous: list[dict], reason: str, decision_log_entry: str) -> dict:
    """§19 rerun under a new run ID, each episode as attempt + 1.

    D6_HOLD / D7_HOLD rerun the failed episodes (decision rules D6/D7); D4_FAIL reruns every smoke
    episode (decision rules D4); CODE_CHANGE reruns every episode unless a decision-log entry clears
    it, so the caller passes only the episodes to rerun. `previous` are the saved records; the latest
    attempt per (query, agent) is used. The reason must cite its decision-log entry.
    """
    if reason not in RERUN_REASONS:
        raise ValueError(f"Rerun reason must be one of {RERUN_REASONS} (§19), got {reason!r}")
    if not isinstance(decision_log_entry, str) or not decision_log_entry.strip():
        raise ValueError("A rerun must cite its decision-log entry")
    latest: dict = {}
    for record in previous:
        key = (record["agent_id"], record["query_id"])
        if key not in latest or record["attempt"] > latest[key]["attempt"]:
            latest[key] = record
    failed_only = reason in ("D6_HOLD", "D7_HOLD")
    episodes = {key: rec["attempt"] + 1 for key, rec in sorted(latest.items())
                if rec["status"] in FAILED or not failed_only}
    return {"reason": reason, "decision_log_entry": decision_log_entry, "attempts": episodes}
