"""S20 screening (protocol sections 9.1/19, D3); default: one new episode.

Only the unchanged agent runner sees questions/KG. References and scientific
labels are loaded afterwards in evaluator code, never passed into the agent.
Use --max-new 0 to regenerate reports without inference; final statuses are
write-once, including failures. No model selection or S21 config changes.
"""

import argparse
import csv
from datetime import datetime, timezone
import json
import os
from pathlib import Path
import subprocess
from tempfile import NamedTemporaryFile, TemporaryDirectory

import pandas as pd
import pyarrow.parquet as pq
import yaml

from cofail_kg.agents.ollama_client import OllamaClient
from cofail_kg.agents.prompts import PROMPT_VERSION, prompt_sha256
from cofail_kg.agents.run_agent import run_episode
from cofail_kg.agents.trace import load_episode_record, publish_once, record_path
from cofail_kg.evaluation.agent_metrics import agent_metrics, degree_statistics
from cofail_kg.evaluation.screening import aggregate_model
from cofail_kg.kg.prepare import file_hash
from cofail_kg.kg.primekg_index import PrimeKGIndex
from cofail_kg.utils.frozen_hashes import read_frozen_hashes

ROOT = Path(__file__).resolve().parents[1]
SETTINGS = {"temperature": 0, "seed": 42, "num_ctx": 8192, "num_predict": 4096,
            "page_size": 50, "budget": 30, "timeout_seconds": 600}


def pin_manifest(path, value):
    """Publish JSON once; identical resumes are allowed, any changed input stops."""
    if path.exists():
        if json.loads(path.read_text(encoding="utf-8")) != value:
            raise ValueError(f"Existing manifest/evidence differs: {path}")
        return
    path.parent.mkdir(parents=True, exist_ok=True)
    temporary = None
    try:
        with NamedTemporaryFile(mode="w", encoding="utf-8", dir=path.parent, delete=False) as handle:
            temporary = Path(handle.name)
            json.dump(value, handle, indent=2, sort_keys=True, allow_nan=False)
            handle.write("\n")
            handle.flush()
            os.fsync(handle.fileno())
        publish_once(temporary, path)
    finally:
        if temporary is not None:
            temporary.unlink(missing_ok=True)


def validate_resume(record, agent, config):
    """A final record can be skipped only when its provenance matches this run."""
    expected = {k: config[k] for k in ("run_id", "temperature", "seed", "num_ctx", "num_predict",
                                      "git_commit", "kg_fingerprint", "biohopr_revision")}
    expected.update(agent_id=agent["agent_id"], attempt=1,
                    model={k: agent[k] for k in ("tag", "digest", "quantization")},
                    prompt_version=f"{PROMPT_VERSION}:{config['prompt_sha256']}")
    if any(record[k] != v for k, v in expected.items()):
        raise ValueError("Completed episode provenance differs from screening manifest")
    for key in ("page_size", "budget"):
        if record["tool_config"][key] != config[key]:
            raise ValueError("Completed episode tool settings differ")
    if record["tool_config"]["tool_schema_sha256"] != config["tool_schema_sha256"]:
        raise ValueError("Completed episode tool identity differs")
    events = [e for e in record.get("log_events", []) if e.get("event") == "EPISODE_CONFIG"]
    expected_event = {k: config[k] for k in ("source_sha256", "agent_inputs_sha256",
                                             "timeout_seconds", "request_timeout_seconds")}
    expected_event["think"] = False
    if len(events) != 1 or any(events[0].get(k) != v for k, v in expected_event.items()):
        raise ValueError("Completed episode thinking/source/config provenance differs")


def run_screening(agent, config, query_ids, *, max_new, check_identity):
    """Manifest order, fresh episodes, no retries of any saved final status."""
    if type(max_new) is not int or not 0 <= max_new <= 20:
        raise ValueError("max_new must be between 0 and 20")
    existing = {}
    for query_id in query_ids:
        target = record_path(config["runs_root"], config["run_id"], query_id, agent["agent_id"], 1)
        if target.exists():
            rec = load_episode_record(target)
            if rec["query_id"] != query_id:
                raise ValueError("Completed episode query differs from its manifest/file name")
            validate_resume(rec, agent, config)
            existing[query_id] = rec
    records = []
    created = 0
    for query_id in query_ids:
        target = record_path(config["runs_root"], config["run_id"], query_id, agent["agent_id"], 1)
        if query_id not in existing:
            if created >= max_new:
                continue
            check_identity()
            print(f"Starting {query_id} / {agent['tag']} (new episode {created + 1})", flush=True)
            run_episode(query_id, agent, config)
            created += 1
            check_identity()  # The record is retained even when identity changes afterwards.
        rec = load_episode_record(target)
        validate_resume(rec, agent, config)
        records.append(rec)
    return records


def check_sources(config):
    """Never recompute scientific results using different source/input bytes."""
    for path, expected in config["source_sha256"].items():
        if file_hash(ROOT / path) != expected:
            raise ValueError(f"Pinned screening source/input changed: {path}")


def prepare_run(args):
    """Check frozen identities and pin all input/source bytes before inference."""
    root = ROOT
    frozen = read_frozen_hashes(root / "configs/frozen_hashes.yaml")
    required = {"data/agent_inputs/screening.jsonl": frozen["manifests"]["data/agent_inputs/screening.jsonl"],
                "data/processed/manifests/screening.jsonl": frozen["manifests"]["data/processed/manifests/screening.jsonl"],
                "data/cache/primekg_metadata.json": frozen["kg_fingerprint"],
                "src/cofail_kg/agents/tool_schemas.py": frozen["tools"],
                "results/semantics/relation_mapping.json": frozen["relation_mapping"]}
    if any(file_hash(root / p) != h for p, h in required.items()) or prompt_sha256() != frozen["prompt"]:
        raise ValueError("Frozen screening sheet, KG, tools, mapping or prompt differs")
    query_ids = [json.loads(line)["query_id"] for line in
                 (root / "data/agent_inputs/screening.jsonl").read_text(encoding="utf-8").splitlines()]
    manifest_ids = [json.loads(line)["query_id"] for line in
                    (root / "data/processed/manifests/screening.jsonl").read_text(encoding="utf-8").splitlines()]
    if len(query_ids) != 20 or len(set(query_ids)) != 20 or query_ids != manifest_ids:
        raise ValueError("Screening must contain the same 20 ordered unique queries")
    runs_root = root / "results/runs/screening"
    record_path(runs_root, args.run_id, query_ids[0], args.agent_id, 1)  # Validate safe IDs.
    manifest_path = runs_root / args.run_id / f"{args.agent_id}.config.json"
    transport = yaml.safe_load((root / "configs/ollama.yaml").read_text(encoding="utf-8"))
    client = OllamaClient(think=False, timeout_seconds=transport["request_timeout_seconds"],
                          base_url=transport["base_url"])
    identity = (json.loads(manifest_path.read_text())["identity"] if args.max_new == 0
                else client.get_model_identity(args.model))
    if identity["tag"] != args.model or identity["digest"] != args.expected_digest or "tools" not in identity["capabilities"]:
        raise ValueError("Installed model does not match approved native-tools tag/digest")
    sources = sorted({*required, "configs/frozen_hashes.yaml", "configs/ollama.yaml",
                      "docs/frozen_pilot_protocol.md", "docs/decision_rules.md", "scripts/20_screen_models.py",
                      "data/processed/reference_queries.parquet", "data/processed/reference_targets.parquet",
                      "data/processed/primary_population.csv", "data/processed/reference_summary.json",
                      *[p.relative_to(root).as_posix() for p in (root / "src/cofail_kg").rglob("*.py")]})
    commit = subprocess.check_output(["git", "rev-parse", "HEAD"], cwd=root, text=True).strip()
    dirty = bool(subprocess.check_output(["git", "status", "--porcelain"], cwd=root, text=True))
    config = {**SETTINGS, "run_id": args.run_id, "runs_root": str(runs_root),
              "agent_inputs": str(root / "data/agent_inputs/screening.jsonl"),
              "agent_inputs_sha256": required["data/agent_inputs/screening.jsonl"],
              "cache_dir": str(root / "data/cache"), "prompt_sha256": frozen["prompt"],
              "tool_schema_sha256": frozen["tools"], "kg_fingerprint": frozen["kg_fingerprint"],
              "biohopr_revision": frozen["biohopr_revision"], "git_commit": commit + ("-dirty" if dirty else ""),
              "source_sha256": {p: file_hash(root / p) for p in sources},
              "base_url": transport["base_url"], "request_timeout_seconds": transport["request_timeout_seconds"]}
    agent = {**identity, "agent_id": args.agent_id, "family": args.family, "think": False}
    snapshot = {"identity": identity, "agent": agent, "config": config, "query_ids": query_ids}
    if args.max_new:
        runs_root.mkdir(parents=True, exist_ok=True)
        with TemporaryDirectory(prefix=".s20-check-", dir=runs_root) as temporary:
            probe = Path(temporary) / "saved.json"
            pin_manifest(probe, {"probe": True})
            try:
                pin_manifest(probe, {"probe": False})
            except ValueError:
                pass
            else:
                raise RuntimeError("Persistence preflight did not refuse changed data")
    pin_manifest(manifest_path, snapshot)
    return agent, config, query_ids, client


def load_evaluator():
    """Evaluator-only references/KG, loaded after agent inference finishes."""
    root = ROOT
    mapping = json.loads((root / "results/semantics/relation_mapping.json").read_text(encoding="utf-8"))
    references = {q["query_id"]: q for q in pq.read_table(root / "data/processed/reference_queries.parquet").to_pylist()}
    targets = {}
    for row in pq.read_table(root / "data/processed/reference_targets.parquet").to_pylist():
        targets.setdefault(row["query_id"], {}).setdefault(row["bridge"], []).append(row["target"])
    with (root / "data/processed/primary_population.csv").open(encoding="utf-8", newline="") as handle:
        status = {r["query_id"]: r["status"] for r in csv.DictReader(handle)}
    kg = PrimeKGIndex(root / "data/cache")
    degrees = degree_statistics(pd.read_parquet(root / "data/cache/primekg_nodes.parquet"),
                                pd.read_parquet(root / "data/cache/primekg_edges.parquet"))
    return references, targets, mapping["per_type"], status, kg, degrees


def report_screening():
    """Rebuild a cumulative, explicitly partial table from pinned run manifests."""
    manifests = sorted((ROOT / "results/runs/screening").glob("*/*.config.json"))
    context = None
    rows = []
    for manifest in manifests:
        snap = json.loads(manifest.read_text(encoding="utf-8"))
        agent, config = snap["agent"], snap["config"]
        check_sources(config)
        records = run_screening(agent, config, snap["query_ids"], max_new=0, check_identity=lambda: None)
        if not records:
            continue
        if context is None:
            context = load_evaluator()
        refs, targets, mapping, status, kg, degrees = context
        metrics = []
        for rec in records:
            query = refs[rec["query_id"]]
            metric = agent_metrics(rec, query, mapping[query["relation_type"]],
                                   targets[rec["query_id"]], kg, degrees,
                                   consistent=status[rec["query_id"]] == "CONSISTENT")
            metrics.append(metric)
            pin_manifest(ROOT / "results/diagnostics/screening" / config["run_id"] /
                         f"{rec['query_id']}__{agent['agent_id']}__metrics.json", metric)
        identity = {k: agent[k] for k in ("tag", "digest", "quantization", "parameter_size", "family")}
        rows.append(aggregate_model(records, metrics, identity))
    if rows:
        path = ROOT / "results/diagnostics/screening/screening_table.csv"
        path.parent.mkdir(parents=True, exist_ok=True)
        with NamedTemporaryFile(mode="w", encoding="utf-8", newline="", dir=path.parent, delete=False) as handle:
            temporary = Path(handle.name)
            writer = csv.DictWriter(handle, fieldnames=list(rows[0]))
            writer.writeheader()
            writer.writerows(rows)
            handle.flush()
            os.fsync(handle.fileno())
        try:
            os.replace(temporary, path)  # Derived table only; raw episodes/configs are write-once.
        finally:
            temporary.unlink(missing_ok=True)
    return rows


def main(argv=None):
    parser = argparse.ArgumentParser(description=__doc__)
    for name in ("run-id", "model", "agent-id", "family", "expected-digest"):
        parser.add_argument("--" + name, required=True)
    parser.add_argument("--max-new", type=int, choices=range(21), default=1,
                        help="Maximum new episodes, default 1; 0 reports without inference")
    args = parser.parse_args(argv)
    agent, config, queries, client = prepare_run(args)

    def check_identity():
        check_sources(config)
        current = client.get_model_identity(agent["tag"])
        if current != {k: agent[k] for k in current}:
            raise ValueError("Installed model identity changed; saved records are retained")

    records = run_screening(agent, config, queries, max_new=args.max_new, check_identity=check_identity)
    rows = report_screening()
    print(json.dumps({"finished_at": datetime.now(timezone.utc).isoformat(),
                      "episodes_saved_for_model": len(records), "screening_rows": rows}, indent=2), flush=True)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
