"""EXPLORATORY: P2-draft vs P1 on the 20 screening queries, per configuration (read-only)."""
import json
import sys
from collections import Counter
from pathlib import Path

sys.stdout.reconfigure(encoding="utf-8")
HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[2]
sys.path.insert(0, str(ROOT / "src"))

from cofail_kg.evaluation.screening import aggregate_model  # noqa: E402

REPROMPT = "Your last message was not valid JSON in the required format. Reply with only the JSON object."
P2_RULE = "3. When you are finished, your final message must be only this JSON object, with no other text"
P2_RUNS = ROOT / "results/runs/p2-exploratory/p2-explore-20261105"
S22_RUNS = ROOT / "results/runs/smoke_single_v135"
S22_METRICS = ROOT / "results/diagnostics/smoke_single_v135"
# P1 baseline per P2 config: (record glob root, record agent_id, metrics folder, label)
P1 = {"Ministral3-8B": (S22_RUNS, "Ministral3-8B", S22_METRICS / "Ministral3-8B/metrics", "S22"),
      "Gemma4-E4B": (S22_RUNS, "Gemma4-E4B", S22_METRICS / "Gemma4-E4B/metrics", "S22"),
      "Granite41-8B": (S22_RUNS, "Granite41-8B", S22_METRICS / "Granite41-8B/metrics", "S22"),
      "Qwen35-9B-8K": (S22_RUNS, "Qwen35-9B", S22_METRICS / "Qwen35-9B/metrics", "S22"),
      "Qwen35-9B-16K": (ROOT / "results/runs/screening-5060ti/qwen35-5060ti-16k-20261029", "Qwen35-9B",
                        ROOT / "results/diagnostics/s20/qwen35-5060ti-16k-20261029/metrics", "S20"),
      "Ornith15-9B": (ROOT / "results/runs/screening-5060ti/ornith15-5060ti-32k-20261031", "Ornith15-9B",
                      ROOT / "results/diagnostics/s20/ornith15-5060ti-32k-20261031/metrics", "S20")}
VALID = ("GOLD", "GOLD_BRIDGE_EXTRA", "ALT_VALID")


def load(root, agent, metrics_dir):
    paths = sorted(root.rglob(f"*__{agent}__a1.json"))
    if len(paths) != 20:
        raise ValueError(f"{root} {agent}: {len(paths)} records")
    records = [json.loads(p.read_text(encoding="utf-8")) for p in paths]
    metrics = [json.loads((metrics_dir / f"{r['query_id']}.json").read_text(encoding="utf-8")) for r in records]
    return records, metrics


def start_id(record):
    return record["messages"][1]["content"].split("PrimeKG ID: ")[1].rstrip(")")


def cell(record, metric):
    if record["status"] != "SUCCESS":
        return record["status"]
    ans = metric["answers"]
    if not ans:
        return "no answer"
    if len(ans) == 1 and ans[0]["node_id"] == start_id(record):
        return "start only"
    ok = any(a["label_a"] in VALID and a["label_b"] == "SUPPORTED" for a in ans)
    return ("correct" if ok else "wrong") + f" {sum(a['label_a'] in VALID for a in ans)}/{len(ans)}"


def profile(records, metrics):
    row = aggregate_model(records, metrics, {k: records[0]["model"][k] for k in ("tag", "digest", "quantization")}
                          | {"parameter_size": None, "family": None})
    cut = 0
    for r in records:
        counts = r["token_counts"]
        cut += any(p is not None and c is not None and (p + c >= r["num_ctx"] or c >= r["num_predict"])
                   for p, c in zip(counts["prompt"], counts["completion"]))
    cells = [cell(r, m) for r, m in zip(records, metrics)]
    return {"status": dict(sorted(Counter(r["status"] for r in records).items())),
            "causes": dict(sorted(Counter(f"{r['status']}:{r['cause']}" for r in records
                                          if r["status"] != "SUCCESS").items())),
            "competent": row["competent_episodes"], "d3_pass": row["d3_pass"],
            "well_formed_rate": row["well_formed_rate"], "median_wall_s": row["median_wall_seconds"],
            "largest_prompt": row["largest_prompt_eval_count"],
            "median_tool_calls": row["median_tool_calls"], "budget_hit_share": row["budget_hit_share"],
            "median_answers_success": sorted(len(m["answers"]) for r, m in zip(records, metrics)
                                             if r["status"] == "SUCCESS")[sum(r["status"] == "SUCCESS"
                                                                               for r in records) // 2],
            "reprompted": sum(any(m["role"] == "user" and m.get("content") == REPROMPT for m in r["messages"])
                              for r in records),
            "start_only": cells.count("start only"), "hit_context_or_output_limit": cut,
            "cells": {r["query_id"]: c for r, c in zip(records, cells)}}


def main():
    out = {}
    for cfg, (root, agent, mdir, label) in P1.items():
        p1 = profile(*load(root, agent, mdir))
        p2_records, p2_metrics = load(P2_RUNS, cfg, HERE / cfg / "metrics")
        if not all(P2_RULE in r["messages"][0]["content"] for r in p2_records):
            raise ValueError(f"{cfg}: a P2 record lacks the P2 rule 3 text")
        out[cfg] = {"p1_source": label, "p1": p1, "p2": profile(p2_records, p2_metrics)}
    (HERE / "p1_vs_p2.json").write_text(json.dumps(out, indent=2, sort_keys=True), encoding="utf-8")
    keys = ("competent", "d3_pass", "status", "reprompted", "start_only", "hit_context_or_output_limit",
            "well_formed_rate", "median_wall_s", "largest_prompt", "median_tool_calls", "budget_hit_share",
            "median_answers_success", "causes")
    for cfg, v in out.items():
        print(f"== {cfg} (P1 from {v['p1_source']})")
        for k in keys:
            print(f"  {k:30} P1={v['p1'][k]}  P2={v['p2'][k]}")
    qids = sorted(next(iter(out.values()))["p1"]["cells"])
    print("\n|Query|" + "|".join(out) + "|")
    for q in qids:
        print(f"|{q}|" + "|".join(f"{v['p1']['cells'][q]} → {v['p2']['cells'][q]}" for v in out.values()) + "|")


if __name__ == "__main__":
    main()
