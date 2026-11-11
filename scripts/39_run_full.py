"""S39 (EXPLORATORY, decision log 2026-11-11): the full run `full_v1`, ONE agent per invocation.

Runs one frozen agent on every query of the `full` manifest, then stops. The researcher chooses the
next agent (decision log 2026-11-11); nothing starts the next agent automatically.

It reuses scripts/25_run_panel.py unchanged (isolated pinned Ollama server, digest and hash checks,
runtime guards, synthetic probe, write-once records, resume that never reruns a completed episode;
protocol §9.1, §9.2, §19) and changes, in memory only:
  * the manifest hashes come from configs/frozen_hashes_full.yaml, key `manifests_full`
    (configs/frozen_hashes.yaml holds only the four S10 sets and is left byte-identical because it
    is a pinned source of pilot_v1 / expansion_v1); that file and this script are pinned with the
    other run sources;
  * progress is rebuilt incrementally (one directory listing per episode instead of re-reading every
    saved record), because the panel runner's version is quadratic in the number of episodes;
  * no analysis is run here: evaluation needs all four agents.
Everything else (model digests, prompt P1, tools T1, §9.1 runtime) is the frozen value.

Usage:
    python scripts/39_run_full.py run --agent Gemma4-12B      (start or resume that agent)
    python scripts/39_run_full.py status                      (counts per agent; no inference)
"""
import argparse
import importlib.util
import json
import os
from datetime import datetime, timezone
from pathlib import Path
import sys

from cofail_kg.agents.panel_runner import FAILED, episode_plan, manifest_query_ids, write_progress
from cofail_kg.agents.trace import record_path
from cofail_kg.kg.prepare import file_hash
from cofail_kg.utils.frozen_hashes import read_frozen_hashes

ROOT = Path(__file__).resolve().parents[1]
MANIFEST = "full"
RUN_ID = "full_v1"
HASH_KEY = "manifests_full"
SELF = "scripts/39_run_full.py"
FULL_HASHES = "configs/frozen_hashes_full.yaml"

spec = importlib.util.spec_from_file_location("panel_driver", ROOT / "scripts/25_run_panel.py")
PANEL = importlib.util.module_from_spec(spec)
spec.loader.exec_module(PANEL)


def pinned_inputs(manifest, root=ROOT):
    """As 25_run_panel.pinned_inputs, with the manifest hashes from `manifests_full`."""
    if manifest != MANIFEST:
        raise ValueError(f"This launcher runs only the `{MANIFEST}` manifest, not {manifest!r}")
    frozen = read_frozen_hashes(root / "configs/frozen_hashes.yaml")
    sheet, processed = f"data/agent_inputs/{manifest}.jsonl", f"data/processed/manifests/{manifest}.jsonl"
    full = read_frozen_hashes(root / FULL_HASHES)[HASH_KEY]
    return frozen, {sheet: full[sheet], processed: full[processed],
                    "data/cache/primekg_metadata.json": frozen["kg_fingerprint"],
                    "src/cofail_kg/agents/tool_schemas.py": frozen["tools"],
                    "results/semantics/relation_mapping.json": frozen["relation_mapping"],
                    SELF: file_hash(root / SELF), FULL_HASHES: file_hash(root / FULL_HASHES)}


class IncrementalProgress:
    """Same result as panel_runner.progress (attempt 1), reading each saved record only once."""

    def __init__(self):
        self.seen = {}

    def __call__(self, runs_root, run_id, plan, attempts=None):
        if attempts:
            raise ValueError("The full run has first attempts only")
        folder = Path(runs_root) / run_id
        names = {entry.name for entry in os.scandir(folder)} if folder.exists() else set()
        done, failures = 0, []
        for agent_id, query_id in plan:
            path = record_path(runs_root, run_id, query_id, agent_id, 1)
            if path.name not in names:
                continue
            if path.name not in self.seen:
                record = json.loads(path.read_text(encoding="utf-8"))
                self.seen[path.name] = (record["status"], record.get("cause"))
            status, cause = self.seen[path.name]
            done += 1
            if status in FAILED:
                failures.append({"agent_id": agent_id, "query_id": query_id, "status": status, "cause": cause})
        return {"run_id": run_id, "episodes_done": done, "episodes_total": len(plan),
                "failures_so_far": len(failures), "failures": failures,
                "updated_at": datetime.now(timezone.utc).isoformat()}


def agent_counts(runs_root, run_id, agent_ids, query_ids, progress):
    out = {}
    for agent_id in agent_ids:
        state = progress(runs_root, run_id, episode_plan([agent_id], query_ids))
        out[agent_id] = {"done": state["episodes_done"], "total": state["episodes_total"],
                         "failures": state["failures_so_far"]}
    return out


def setup():
    PANEL.pinned_inputs = pinned_inputs
    PANEL.progress = IncrementalProgress()
    panel = PANEL.S22.load_panel()
    query_ids = manifest_query_ids(ROOT / f"data/agent_inputs/{MANIFEST}.jsonl")
    return panel, query_ids


def run(agent_id):
    panel, query_ids = setup()
    agent_ids = [row["agent_id"] for row, _ in panel]
    if agent_id not in agent_ids:
        raise ValueError(f"{agent_id!r} is not a frozen agent; choose one of {agent_ids}")
    row, settings = next((r, s) for r, s in panel if r["agent_id"] == agent_id)
    plan = episode_plan(agent_ids, query_ids)  # the whole panel, so progress counts all four agents
    progress_path = PANEL.RUNS_ROOT / RUN_ID / "progress.json"
    state = PANEL.progress(PANEL.RUNS_ROOT, RUN_ID, plan)
    write_progress(progress_path, state)
    print(f"RUN {RUN_ID} (EXPLORATORY): manifest {MANIFEST}, {len(query_ids)} queries; agent {agent_id} only; "
          f"{state['episodes_done']}/{len(plan)} panel episodes already completed", flush=True)
    PANEL.run_agent(MANIFEST, RUN_ID, row, settings, plan, progress_path, -1)  # -1: no halfway prompt
    counts = agent_counts(PANEL.RUNS_ROOT, RUN_ID, agent_ids, query_ids, PANEL.progress)
    write_progress(progress_path, PANEL.progress(PANEL.RUNS_ROOT, RUN_ID, plan))
    if counts[agent_id]["done"] != len(query_ids):
        raise RuntimeError(f"Agent incomplete: {counts[agent_id]}")
    print(f"AGENT COMPLETE: {agent_id} {counts[agent_id]}", flush=True)
    print(json.dumps(counts, indent=2), flush=True)
    print("STOP: the researcher chooses the next agent (decision log 2026-11-11). Nothing else was started.",
          flush=True)


def status():
    panel, query_ids = setup()
    agent_ids = [row["agent_id"] for row, _ in panel]
    print(json.dumps(agent_counts(PANEL.RUNS_ROOT, RUN_ID, agent_ids, query_ids, PANEL.progress), indent=2))


def main(argv=None):
    parser = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    parser.add_argument("phase", choices=("run", "status"))
    parser.add_argument("--agent")
    args = parser.parse_args(argv)
    if args.phase == "run":
        if not args.agent:
            parser.error("run needs --agent")
        run(args.agent)
    else:
        status()


if __name__ == "__main__":
    sys.exit(main())
