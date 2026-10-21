"""Researcher-authorized full 16K reassessment, protocol section 20; unchanged D3."""

import argparse
from collections import Counter
import csv
from datetime import datetime, timezone
import hashlib
import importlib.util
import json
from pathlib import Path
import subprocess

from cofail_kg.agents.ollama_client import OllamaClient
from cofail_kg.evaluation.agent_metrics import agent_metrics
from cofail_kg.evaluation.screening import aggregate_model, call_counts


ROOT = Path(__file__).resolve().parents[4]
OUT = Path(__file__).resolve().parent


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("agent_id", choices=["Gemma4-E4B", "Qwen35-9B", "Ministral3-8B"])
    parser.add_argument("--report-only", action="store_true")
    args = parser.parse_args()
    spec = importlib.util.spec_from_file_location("screening_launcher", ROOT / "scripts/20_screen_models.py")
    launcher = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(launcher)
    snapshot = json.loads((OUT / f"{args.agent_id}.manifest.json").read_text())
    agent, config, queries = snapshot["agent"], snapshot["config"], snapshot["query_ids"]
    original = json.loads((ROOT / snapshot["original_manifest"]).read_text())
    differences = {k for k in config if config[k] != original["config"][k]}
    assert {"num_ctx", "run_id", "runs_root"} <= differences <= {"num_ctx", "run_id", "runs_root", "git_commit"}
    assert config["num_ctx"] == 16384 and agent == original["agent"]
    assert queries == original["query_ids"] and len(queries) == len(set(queries)) == 20
    assert config["runs_root"] != original["config"]["runs_root"]
    baseline = json.loads((OUT / "integrity-before.json").read_text())
    run_dir = Path(config["runs_root"]) / config["run_id"]
    model_out = OUT / args.agent_id
    launcher.pin_manifest(OUT / "driver-identity.json", {"sha256": hashlib.sha256(Path(__file__).read_bytes()).hexdigest()})
    launcher.pin_manifest(run_dir / f"{args.agent_id}.config.json", snapshot)
    client = OllamaClient(think=False, timeout_seconds=config["request_timeout_seconds"], base_url=config["base_url"])
    observed = 0

    def integrity():
        launcher.check_sources(config)
        for group in baseline.values():
            for path, digest in group.items():
                assert hashlib.sha256((ROOT / path).read_bytes()).hexdigest() == digest, path

    def check():
        nonlocal observed
        integrity()
        assert client.get_model_identity(agent["tag"]) == snapshot["identity"]
        saved = list(run_dir.glob(f"*__{args.agent_id}__a1.json"))
        completed = len(saved)
        ps = client._request("GET", "/api/ps")
        sample = {"timestamp": datetime.now(timezone.utc).isoformat(), "completed": completed, "ps": ps,
                  "gpu": subprocess.check_output(["nvidia-smi", "--query-gpu=name,memory.total,memory.used",
                                                   "--format=csv,noheader"], text=True).strip()}
        model_out.mkdir(exist_ok=True)
        with (model_out / "runtime-samples.jsonl").open("a", encoding="utf-8") as handle:
            handle.write(json.dumps(sample) + "\n")
        if completed:
            assert any(m["digest"] == agent["digest"] and m["context_length"] == 16384 for m in ps["models"]), ps
        if completed > observed:
            record = json.loads((run_dir / f"{queries[completed - 1]}__{args.agent_id}__a1.json").read_text())
            print(f"SAVED {args.agent_id} {completed}/20 {record['query_id']} {record['status']} {record['cause']}", flush=True)
        observed = completed

    integrity()
    records = launcher.run_screening(agent, config, queries, max_new=0 if args.report_only else 20,
                                     check_identity=check)
    assert len(records) == 20 and len(list(run_dir.glob(f"*__{args.agent_id}__a1.json"))) == 20
    refs, targets, mapping, status, kg, degrees = launcher.load_evaluator()
    metrics, per_query = [], []
    label_a, label_b = Counter(), Counter()
    for record in records:
        query = refs[record["query_id"]]
        metric = agent_metrics(record, query, mapping[query["relation_type"]], targets[record["query_id"]],
                               kg, degrees, consistent=status[record["query_id"]] == "CONSISTENT")
        launcher.pin_manifest(model_out / "metrics" / f"{record['query_id']}__metrics.json", metric)
        metrics.append(metric)
        old_record = json.loads((ROOT / snapshot["original_manifest"]).parent.joinpath(
            f"{record['query_id']}__{args.agent_id}__a1.json").read_text())
        wall = (datetime.fromisoformat(record["timestamps"]["finished_at"]) -
                datetime.fromisoformat(record["timestamps"]["started_at"])).total_seconds()
        per_query.append({"query_id": record["query_id"], "status_8k": old_record["status"],
                          "status_16k": record["status"], "cause_16k": record["cause"], "wall_seconds_16k": wall,
                          "answers_16k": len(metric["answers"]), "supported_question_valid_16k": sum(
                              a["label_a"] in ("GOLD", "GOLD_BRIDGE_EXTRA", "ALT_VALID") and a["label_b"] == "SUPPORTED"
                              for a in metric["answers"]), "benchmark_precision_16k": metric["benchmark_precision"],
                          "benchmark_recall_16k": metric["benchmark_recall"],
                          "largest_prompt_16k": max((n for n in record["token_counts"]["prompt"] if n is not None), default=None),
                          "thinking_messages_16k": sum(bool(m.get("thinking")) for m in record["messages"]),
                          **call_counts(record)})
        label_a.update(a["label_a"] for a in metric["answers"])
        label_b.update(a["label_b"] for a in metric["answers"])
    identity = {k: agent[k] for k in ("tag", "digest", "quantization", "parameter_size", "family")}
    row = aggregate_model(records, metrics, identity)
    assert row["complete"] and row["episodes_completed"] == 20
    summary = {"context": 16384, "researcher_authorized_reassessment": True, "screening_row": row,
               "accepted_at_16k": row["d3_pass"], "status_counts": dict(Counter(r["status"] for r in records)),
               "label_a_counts": dict(label_a), "label_b_counts": dict(label_b), "per_query": per_query}
    launcher.pin_manifest(model_out / "summary.json", summary)
    if not (model_out / "per-query.csv").exists():
        with (model_out / "per-query.csv").open("x", newline="", encoding="utf-8") as handle:
            writer = csv.DictWriter(handle, fieldnames=list(per_query[0]))
            writer.writeheader()
            writer.writerows(per_query)
    integrity()
    launcher.pin_manifest(model_out / "final-run-hashes.json", {
        p.relative_to(ROOT).as_posix(): hashlib.sha256(p.read_bytes()).hexdigest()
        for p in [run_dir / f"{args.agent_id}.config.json", *run_dir.glob(f"*__{args.agent_id}__a1.json")]})
    print(json.dumps({k: v for k, v in summary.items() if k != "per_query"}, indent=2), flush=True)
    print(f"COMPLETE {args.agent_id}: 20/20; D3 {'PASS' if row['d3_pass'] else 'FAIL'} at 16K.", flush=True)


if __name__ == "__main__":
    main()
