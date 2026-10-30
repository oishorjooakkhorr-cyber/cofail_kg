"""Offline paired comparison of the shared resource package against 32K history."""
from collections import Counter
import importlib.util
import json
from pathlib import Path
import sys

spec = importlib.util.spec_from_file_location("shared", Path(__file__).with_name("20_shared_resources.py"))
shared = importlib.util.module_from_spec(spec)
spec.loader.exec_module(shared)


def main():
    # Reuse the already tested detailed trace inspection; its main() never runs here.
    baseline_dir = shared.OUT.parent / shared.MODELS["granite41"]
    sys.modules["run_model"] = shared.load("baseline", baseline_dir / "run_model.py")
    inspect = shared.load("investigation", baseline_dir / "investigate.py").inspect
    rows = []
    for model, baseline in shared.MODELS.items():
        launcher, driver, snapshot, folder = shared.prepare(model)
        shared.integrity(launcher, snapshot)
        agent = snapshot["agent"]["agent_id"]
        run_root = shared.ROOT / "results/runs/screening-5060ti"
        paired = {}
        new_records = []
        for query in snapshot["query_ids"]:
            block, records = {}, {}
            for label, run, metrics in (
                ("baseline32k", baseline, shared.OUT.parent / baseline / "metrics"),
                ("resources32k", shared.run_id(model), folder / "metrics")):
                record = shared.read(run_root / run / f"{query}__{agent}__a1.json")
                metric = shared.read(metrics / f"{query}.json")
                records[label] = record
                block[label] = inspect(record, metric)
                for response in block[label]["response_counts"]:
                    prompt, completion = response["prompt"], response["completion"]
                    response["headroom_after_prompt"] = None if prompt is None else 32768 - prompt
                    response["headroom_after_completion"] = None if prompt is None or completion is None else 32768 - prompt - completion
                for response in block[label]["final_turns"]:
                    response["headroom_after_prompt"] = None if response["prompt"] is None else 32768 - response["prompt"]
            assert records["baseline32k"]["messages"][:2] == records["resources32k"]["messages"][:2]
            new_records.append(records["resources32k"])
            old = set(block["baseline32k"]["supported_ids"])
            new = set(block["resources32k"]["supported_ids"])
            block["supported_gained"] = sorted(new - old, key=int)
            block["supported_lost"] = sorted(old - new, key=int)
            block["quality_changed"] = any(block["baseline32k"][k] != block["resources32k"][k]
                for k in ("status", "competent", "supported_ids", "label_a_counts", "label_b_counts"))
            paired[query] = block
        assert all(a["timestamps"]["finished_at"] <= b["timestamps"]["started_at"]
                   for a, b in zip(new_records, new_records[1:]))
        for path, digest in shared.read(folder / "final-run-hashes.json").items():
            assert launcher.file_hash(shared.ROOT / path) == digest, path
        log = (folder / "server.stderr.log").read_text(errors="replace")
        samples = [json.loads(line) for line in (folder / "runtime-samples.jsonl").read_text().splitlines()]
        for sample in samples:
            driver.guard_runtime(sample["ps"], log)
        launcher.pin_manifest(folder / "paired-inspection.json", paired)
        context_lines = [line for line in log.splitlines()
                         if any(word in line.lower() for word in ("discard", "shift", "truncat"))]
        launcher.pin_manifest(folder / "context-events.json", context_lines)
        quality = {}
        for label in ("baseline32k", "resources32k"):
            a, b = Counter(), Counter()
            for block in paired.values():
                a.update(block[label]["label_a_counts"])
                b.update(block[label]["label_b_counts"])
            quality[label] = {"label_a_counts": dict(a), "label_b_counts": dict(b),
                "supported_items": sum(block[label]["supported_count"] for block in paired.values()),
                "mean_query_precision": sum(block[label]["benchmark_precision"] or 0 for block in paired.values()) / 20,
                "mean_query_recall": sum(block[label]["benchmark_recall"] or 0 for block in paired.values()) / 20}
        proof = {"all_hashes_match": True, "queries": 20, "sequential": True,
                 "identical_initial_messages": True, "runtime_samples": len(samples),
                 "changed_queries": [q for q, block in paired.items() if block["quality_changed"]],
                 "quality": quality, "context_log_events": len(context_lines),
                 "offline_report": True}
        launcher.pin_manifest(folder / "final-validation.json", proof)
        summary = shared.read(folder / "summary.json")
        rows.append({"model": model, **summary, "validation": proof})
    shared.load("screening", shared.ROOT / "scripts/20_screen_models.py").pin_manifest(
        shared.OUT / "comparison.json", rows)
    for row in rows:
        s = row["screening_row"]
        print(row["model"], json.dumps({k: s[k] for k in
            ("d3_pass", "success_episodes", "competent_episodes", "median_wall_seconds")}), flush=True)


if __name__ == "__main__":
    main()
