"""Offline paired trace inspection and integrity assertions; no model calls."""
from collections import Counter
import csv
from datetime import datetime
import hashlib
import json
from pathlib import Path

from cofail_kg.agents.run_agent import parse_final
from cofail_kg.evaluation.screening import call_counts
from run_model import ROOT, OUT, RUN_ID, guard_runtime


def read(path):
    return json.loads(path.read_text(encoding="utf-8"))


def sha(path):
    return hashlib.sha256(path.read_bytes()).hexdigest()


def inspect(record, metric):
    responses = [e for e in record["log_events"] if e["event"] == "CHAT_RESPONSE"]
    supported = [a["node_id"] for a in metric["answers"] if
                 a["label_a"] in ("GOLD", "GOLD_BRIDGE_EXTRA", "ALT_VALID") and a["label_b"] == "SUPPORTED"]
    supported.sort(key=int)
    wall = (datetime.fromisoformat(record["timestamps"]["finished_at"]) -
            datetime.fromisoformat(record["timestamps"]["started_at"])).total_seconds()
    final_turns = []
    for event in responses:
        raw = event["raw_response"]
        if event in responses[-2:] or not raw["message"].get("tool_calls") or raw["message"].get("content") == record["raw_final_output"]:
            final_turns.append({"prompt": raw.get("prompt_eval_count"), "completion": raw.get("eval_count"),
                               "done_reason": raw.get("done_reason"), "message": raw["message"],
                               "latency_seconds": event["latency_seconds"]})
    return {"failure_events": [e for e in record["log_events"] if e["event"] not in ("CHAT_RESPONSE", "EPISODE_CONFIG", "FINAL_PARSED")], "status": record["status"], "cause": record["cause"], "wall_seconds": wall,
            "competent": bool(supported) and record["status"] == "SUCCESS", "supported_ids": supported,
            "supported_count": len(supported), "answer_count": metric["answer_count"],
            "label_a_counts": metric["label_a_counts"], "label_b_counts": metric["label_b_counts"],
            "benchmark_precision": metric["benchmark_precision"], "benchmark_recall": metric["benchmark_recall"],
            "calls": call_counts(record), "tool_calls_used": metric["tool_calls_used"],
            "failed_tools": [c for c in record["call_log"] if not c["success"]],
            "response_counts": [{"prompt":e["raw_response"].get("prompt_eval_count"), "completion":e["raw_response"].get("eval_count"), "done_reason":e["raw_response"].get("done_reason"), "latency":e["latency_seconds"]} for e in responses],
            "token_counts": record["token_counts"], "final_turns": final_turns,
            "raw_final_output": record["raw_final_output"],
            "thinking_messages": sum(bool(e["raw_response"]["message"].get("thinking")) for e in responses)}


def main():
    manifest = read(OUT / "manifest.json")
    queries = manifest["query_ids"]
    roots = {"new": ROOT / "results/runs/screening-5060ti" / RUN_ID,
             "samehost16k": ROOT / "results/runs/screening-5060ti/qwen35-5060ti-16k-20261029",
             "8k": ROOT / "results/runs/screening/primary-3060ti-20261018",
             "16k": ROOT / "results/runs/screening-16k/context16k-3060ti-20261020"}
    metric_roots = {"new": OUT / "metrics", "samehost16k": OUT.parent / "qwen35-5060ti-16k-20261029/metrics", "8k": ROOT / "results/diagnostics/screening/primary-3060ti-20261018",
                    "16k": OUT.parent / "full-16k-20261020/Qwen35-9B/metrics"}
    paired, flat, records = {}, [], []
    for q in queries:
        block, raw_records = {}, {}
        for key, root in roots.items():
            path = root / f"{q}__Qwen35-9B__a1.json"
            if not path.exists():
                assert key == "16k"
                block[key] = {"status": "UNSAVED", "incomplete_historical_block": True}
                continue
            record = read(path)
            suffix = {"new": ".json", "samehost16k": ".json", "8k": "__Qwen35-9B__metrics.json", "16k": "__metrics.json"}[key]
            metric = read(metric_roots[key] / (q + suffix))
            block[key] = inspect(record, metric)
            raw_records[key] = record
        assert raw_records["new"]["messages"][:2] == raw_records["samehost16k"]["messages"][:2]
        assert raw_records["new"]["messages"][:2] == raw_records["8k"]["messages"][:2]
        if "16k" in raw_records:
            assert raw_records["new"]["messages"][:2] == raw_records["16k"]["messages"][:2]
        records.append(raw_records["new"])
        changed = any(block["new"][k] != block["samehost16k"][k] for k in
                      ("status", "competent", "supported_ids", "label_a_counts", "label_b_counts"))
        block["changed_vs_samehost16k"] = changed
        paired[q] = block
        row = {"query_id": q, "changed_vs_samehost16k": changed}
        for key in roots:
            row.update({f"{key}_{k}": block[key].get(k) for k in
                        ("status", "competent", "supported_count", "wall_seconds", "benchmark_precision", "benchmark_recall")})
        flat.append(row)
        if raw_records["new"]["status"] == "PARSE_FAIL":
            try:
                parse_final(raw_records["new"]["raw_final_output"], [])
            except ValueError:
                pass
            else:
                raise AssertionError("Saved parse failure unexpectedly parses")
    assert len(records) == 20 and [r["query_id"] for r in records] == queries
    assert len(list(roots["new"].glob("*__Qwen35-9B__a1.json"))) == 20
    assert all(a["timestamps"]["finished_at"] <= b["timestamps"]["started_at"] for a, b in zip(records, records[1:]))
    for path, digest in read(OUT / "historical-hashes.json").items():
        assert sha(ROOT / path) == digest, path
    for path, digest in manifest["config"]["source_sha256"].items():
        assert sha(ROOT / path) == digest, path
    for path, digest in read(OUT / "final-run-hashes.json").items():
        assert sha(ROOT / path) == digest, path
    samples = [json.loads(line) for line in (OUT / "runtime-samples.jsonl").read_text().splitlines()]
    for sample in samples:
        guard_runtime(sample["ps"], (OUT / "server.stderr.log").read_text(errors="replace"))
    (OUT / "paired-inspection.json").write_text(json.dumps(paired, indent=2) + "\n", encoding="utf-8")
    with (OUT / "paired-comparison.csv").open("w", newline="", encoding="utf-8") as handle:
        writer = csv.DictWriter(handle, fieldnames=list(flat[0])); writer.writeheader(); writer.writerows(flat)
    proof = {"historical_files": len(read(OUT / "historical-hashes.json")),
             "new_run_files": len(read(OUT / "final-run-hashes.json")), "queries": queries,
             "source_files": len(manifest["config"]["source_sha256"]), "runtime_samples": len(samples),
             "sequential": True, "identical_initial_messages": True,
             "new_statuses": dict(Counter(r["status"] for r in records)),
             "changed_vs_samehost16k": [q for q in queries if paired[q]["changed_vs_samehost16k"]],
             "all_hashes_match": True, "report_is_offline": True}
    (OUT / "final-validation.json").write_text(json.dumps(proof, indent=2) + "\n")
    print(json.dumps(proof, indent=2))


if __name__ == "__main__":
    main()
