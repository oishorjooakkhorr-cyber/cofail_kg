"""Offline per-query comparison of Qwen35-9B blocks; reads saved records only, never calls a model."""
import csv
import importlib.util
import json
from pathlib import Path

from cofail_kg.evaluation.agent_metrics import agent_metrics

ROOT = Path(__file__).resolve().parents[4]
OUT = Path(__file__).resolve().parent
BLOCKS = {
    "3060ti_8k_f16": ROOT / "results/runs/screening/primary-3060ti-20261018",
    "5060ti_16k_f16": ROOT / "results/runs/screening-5060ti/qwen35-5060ti-16k-20261029",
    "5060ti_32k_f16": ROOT / "results/runs/screening-5060ti/qwen35-5060ti-32k-20261029",
    "5060ti_8k_f32": ROOT / "results/runs/screening-5060ti/qwen35-5060ti-8k-f32-20261030",
}
VALID = ("GOLD", "GOLD_BRIDGE_EXTRA", "ALT_VALID")


def main():
    spec = importlib.util.spec_from_file_location("launcher", ROOT / "scripts/20_screen_models.py")
    launcher = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(launcher)
    refs, targets, mapping, status, kg, degrees = launcher.load_evaluator()
    queries = [json.loads(line)["query_id"] for line in (ROOT / "data/agent_inputs/screening.jsonl").read_text().splitlines()]
    rows = []
    for qid in queries:
        row = {"query_id": qid}
        for block, folder in BLOCKS.items():
            record = json.loads((folder / f"{qid}__Qwen35-9B__a1.json").read_text(encoding="utf-8"))
            query = refs[qid]
            metric = agent_metrics(record, query, mapping[query["relation_type"]], targets[qid], kg, degrees,
                                   consistent=status[qid] == "CONSISTENT")
            supported = sum(a["label_a"] in VALID and a["label_b"] == "SUPPORTED" for a in metric["answers"])
            counts = record["token_counts"]
            row.update({f"{block}_status": record["status"], f"{block}_supported": supported,
                        f"{block}_competent": record["status"] == "SUCCESS" and supported > 0,
                        f"{block}_tool_calls": metric["tool_calls_used"],
                        f"{block}_last_prompt": counts["prompt"][-1] if counts["prompt"] else None,
                        f"{block}_last_completion": counts["completion"][-1] if counts["completion"] else None})
        rows.append(row)
    with (OUT / "paired-comparison.csv").open("w", newline="", encoding="utf-8") as handle:
        writer = csv.DictWriter(handle, fieldnames=list(rows[0]))
        writer.writeheader()
        writer.writerows(rows)
    for row in rows:
        print(row["query_id"], " | ".join(f"{b}: {row[b + '_status']}/{row[b + '_supported']}" for b in BLOCKS))
    for block in BLOCKS:
        print(block, "SUCCESS", sum(r[block + "_status"] == "SUCCESS" for r in rows),
              "competent", sum(r[block + "_competent"] for r in rows))


if __name__ == "__main__":
    main()
