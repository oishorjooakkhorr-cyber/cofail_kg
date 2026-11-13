"""Phase J RP — repeat-run report (EXPLORATORY).

Usage (from the repository root, after scripts/25_run_panel.py ... --manifest repeat8 --run-id repeat_v1):
    python scripts/45_rp_report.py --combined pilot_expansion_v1 --run-id repeat_v1

Rule (docs/decision_log.md, entry 2026-11-12 "Plan after D7", section D): the 8 flagged queries × 4 agents
= 32 episodes, original sheet, everything identical, run ID `repeat_v1`. It never replaces the original
records (pilot_v1/expansion_v1 remain the results of record). Report per query whether CF3^Q = 1
reproduces, and per agent-query the Jaccard overlap of answer ID sets and of OFF_QUESTION sets.
Expectation (descriptive, not a test): at least 6 of the 8 queries reproduce CF3^Q = 1.

Inputs (read only): results/runs/<run_id>/analysis/{cofailure.json, metrics/} written by the frozen
analysis (scripts/25_run_panel.py analyze); the original combined analysis results/combined/<id>/ and its
latest-attempt metrics rows (scripts/28_pilot_report.py load_combined). Nothing in pilot_v1 or expansion_v1
is written.

Engineering conventions (documented, not protocol):
* Answer ID set = the resolved node IDs of the episode's retained answers (§12; UNRESOLVED excluded).
  OFF_QUESTION set = W_iq (§16.1). Both come from the §15 metrics rows of the latest attempts.
* Jaccard |A ∩ B| / |A ∪ B|; NA when both sets are empty (0/0), with the counts reported. A non-SUCCESS
  episode has empty sets (§16 convention); its status is shown next to the value.
* "Reproduces" = CF3^Q = 1 in the original and in repeat_v1 for that query. CF3^Q, CF4^Q and CF3^{Q,H1}
  of repeat_v1 are reported per query; the count is given on all 8 queries and again without
  SOURCE_NAME_OVERLAP queries (§19.1).
* Outputs are write-once (an identical re-run is allowed). No interpretation is written.
"""
from __future__ import annotations

import argparse
import csv
import hashlib
import importlib.util
import io
import json
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
EXPECTATION = 6   # section D: "at least 6 of the 8 queries reproduce CF3^Q = 1" (descriptive)
EXPLORATORY_NOTE = ("EXPLORATORY (protocol §20) — docs/decision_log.md, entry 2026-11-12 \"Plan after D7\", "
                    "section D. repeat_v1 never replaces pilot_v1/expansion_v1, which remain the results of "
                    "record.")


def load_script(name: str, filename: str):
    spec = importlib.util.spec_from_file_location(name, ROOT / "scripts" / filename)
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


B5 = load_script("b5_concentration", "42_b5_concentration.py")


def sha256_file(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def answer_sets(row: dict) -> tuple[set[str], set[str]]:
    """(resolved answer IDs, OFF_QUESTION IDs) of one §15 metrics row."""
    ids = {a["node_id"] for a in row["answers"] if a["node_id"] is not None}
    off = {a["node_id"] for a in row["answers"] if a["node_id"] is not None and a["label_a"] == "OFF_QUESTION"}
    return ids, off


def jaccard(a: set, b: set) -> dict:
    union = a | b
    return {"intersection": len(a & b), "union": len(union), "value": len(a & b) / len(union) if union else None}


def compare(original_cof: dict, repeat_cof: dict, original_rows: dict, repeat_rows: dict,
            agents: list[str], overlap: set[str]) -> dict:
    orig_q = {q["query_id"]: q for q in original_cof["queries"]}
    rep_q = {q["query_id"]: q for q in repeat_cof["queries"]}
    if repeat_cof["agent_order"] != agents:
        raise ValueError("repeat run and original list different agent orders")
    missing = sorted(set(rep_q) - set(orig_q))
    if missing:
        raise ValueError(f"repeat queries not in the original analysis: {missing}")
    queries, pairs = [], []
    for qid in sorted(rep_q):
        o, r = orig_q[qid], rep_q[qid]
        queries.append({"query_id": qid, "relation_type": r["relation_type"], "source_name_overlap": qid in overlap,
                        "original_cf3_q": int(o["question"]["cf3"]), "repeat_cf3_q": int(r["question"]["cf3"]),
                        "original_cf4_q": int(o["question"]["cf4"]), "repeat_cf4_q": int(r["question"]["cf4"]),
                        "original_cf3_q_h1": int(o["hop1_clean"]["cf3"]), "repeat_cf3_q_h1": int(r["hop1_clean"]["cf3"]),
                        "reproduces_cf3_q": bool(o["question"]["cf3"] and r["question"]["cf3"]),
                        "original_shared_q": [e["entity_id"] for e in o["question"]["shared_entities"]],
                        "repeat_shared_q": [e["entity_id"] for e in r["question"]["shared_entities"]]})
        for agent in agents:
            ro, rr = original_rows[(agent, qid)], repeat_rows[(agent, qid)]
            (ids_o, off_o), (ids_r, off_r) = answer_sets(ro), answer_sets(rr)
            pairs.append({"query_id": qid, "agent_id": agent,
                          "original_status": ro["episode_status"], "repeat_status": rr["episode_status"],
                          "original_answers": len(ids_o), "repeat_answers": len(ids_r),
                          "jaccard_answers": jaccard(ids_o, ids_r),
                          "original_off_question": sorted(off_o, key=int), "repeat_off_question": sorted(off_r, key=int),
                          "jaccard_off_question": jaccard(off_o, off_r)})
    counts = {}
    for view, sel in (("all_queries", queries), ("without_source_name_overlap",
                                                 [q for q in queries if not q["source_name_overlap"]])):
        orig = [q for q in sel if q["original_cf3_q"]]
        rep = sum(q["reproduces_cf3_q"] for q in orig)
        counts[view] = {"queries": len(sel), "original_cf3_q": len(orig), "reproduced": rep,
                        "repeat_cf3_q": sum(q["repeat_cf3_q"] for q in sel),
                        "repeat_cf4_q": sum(q["repeat_cf4_q"] for q in sel),
                        "repeat_cf3_q_h1": sum(q["repeat_cf3_q_h1"] for q in sel)}
    counts["all_queries"]["expectation_at_least"] = EXPECTATION
    counts["all_queries"]["expectation_met"] = counts["all_queries"]["reproduced"] >= EXPECTATION
    return {"queries": queries, "pairs": pairs, "counts": counts}


def _j(j: dict) -> str:
    return f"NA (0/0)" if j["value"] is None else f"{j['value']:.3f} ({j['intersection']}/{j['union']})"


def to_markdown(result: dict, provenance: dict) -> str:
    c = result["counts"]["all_queries"]
    out = ["# RP — Repeat run `repeat_v1` (EXPLORATORY)\n", f"{EXPLORATORY_NOTE}\n",
           f"Produced by `scripts/45_rp_report.py` at commit `{provenance['git_commit']}` (tracked files clean: "
           f"{provenance['git_tracked_clean']}). repeat_v1 inference commit(s): "
           + ", ".join(f"`{x}`" for x in provenance["repeat_inference_commits"]) + ".\n",
           f"**CF3^Q = 1 reproduced in {c['reproduced']} of {c['original_cf3_q']} queries** (expectation, "
           f"descriptive: at least {EXPECTATION} of 8; met: {'yes' if c['expectation_met'] else 'no'}). "
           f"Without SOURCE_NAME_OVERLAP queries: {result['counts']['without_source_name_overlap']['reproduced']} of "
           f"{result['counts']['without_source_name_overlap']['original_cf3_q']}.\n",
           "## Table 1 — Per query\n",
           "| Query | Relation type | SNO | CF3^Q orig → repeat | Reproduces | CF4^Q orig → repeat | "
           "CF3^{Q,H1} orig → repeat | Shared W^Q entities orig | repeat |",
           "|---|---|---|---|---|---|---|---|---|"]
    for q in result["queries"]:
        out.append(f"| {q['query_id']} | {q['relation_type']} | {'yes' if q['source_name_overlap'] else ''} | "
                   f"{q['original_cf3_q']} → {q['repeat_cf3_q']} | {'yes' if q['reproduces_cf3_q'] else 'no'} | "
                   f"{q['original_cf4_q']} → {q['repeat_cf4_q']} | {q['original_cf3_q_h1']} → {q['repeat_cf3_q_h1']} | "
                   f"{', '.join(q['original_shared_q']) or '—'} | {', '.join(q['repeat_shared_q']) or '—'} |")
    out += ["", "## Table 2 — Per agent and query: Jaccard overlap (original vs repeat)\n",
            "| Query | Agent | Status orig / repeat | Answers orig / repeat | Jaccard answer IDs | "
            "Jaccard OFF_QUESTION |", "|---|---|---|---|---|---|"]
    for p in result["pairs"]:
        out.append(f"| {p['query_id']} | {p['agent_id']} | {p['original_status']} / {p['repeat_status']} | "
                   f"{p['original_answers']} / {p['repeat_answers']} | {_j(p['jaccard_answers'])} | "
                   f"{_j(p['jaccard_off_question'])} |")
    out.append("\nJaccard = |A ∩ B| / |A ∪ B| over resolved answer IDs (and over OFF_QUESTION IDs); NA when both "
               "sets are empty.\n")
    return "\n".join(out)


def to_csv(result: dict) -> str:
    buf = io.StringIO()
    w = csv.writer(buf, lineterminator="\n")
    w.writerow(["query_id", "agent_id", "original_status", "repeat_status", "original_answers", "repeat_answers",
                "jaccard_answers", "jaccard_answers_intersection", "jaccard_answers_union", "jaccard_off_question",
                "jaccard_off_question_intersection", "jaccard_off_question_union"])
    for p in result["pairs"]:
        ja, jo = p["jaccard_answers"], p["jaccard_off_question"]
        w.writerow([p["query_id"], p["agent_id"], p["original_status"], p["repeat_status"], p["original_answers"],
                    p["repeat_answers"], "" if ja["value"] is None else f"{ja['value']:.6f}", ja["intersection"],
                    ja["union"], "" if jo["value"] is None else f"{jo['value']:.6f}", jo["intersection"], jo["union"]])
    return buf.getvalue()


def main(argv=None) -> int:
    if hasattr(sys.stdout, "reconfigure"):
        sys.stdout.reconfigure(encoding="utf-8")
    ap = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    ap.add_argument("--combined", required=True)
    ap.add_argument("--run-id", required=True)
    ap.add_argument("--out", default="results/exploratory/rp")
    args = ap.parse_args(argv)
    report = load_script("s28_report", "28_pilot_report.py")
    original = report.load_combined(args.combined)
    run_dir = ROOT / "results/runs" / args.run_id
    repeat_cof_path = run_dir / "analysis/cofailure.json"
    repeat_cof = json.loads(repeat_cof_path.read_text(encoding="utf-8"))
    repeat_rows = report.latest_rows(run_dir / "analysis/metrics", original["agents"])
    expected = {(a, q["query_id"]) for a in original["agents"] for q in repeat_cof["queries"]}
    if set(repeat_rows) != expected:
        raise ValueError(f"{args.run_id}: metrics rows do not cover the {len(expected)} expected episodes")
    commits = sorted({json.loads(p.read_text(encoding="utf-8"))["config"]["git_commit"]
                      for p in (run_dir / "configs").glob("*.config.json")})
    result = compare(original["cofailure"], repeat_cof, original["rows"], repeat_rows, original["agents"],
                     set(original["cofailure"]["source_name_overlap_queries"]))
    commit, clean = B5.git_state()
    provenance = {"git_commit": commit, "git_tracked_clean": clean, "run_id": args.run_id,
                  "combined_id": args.combined, "repeat_inference_commits": commits,
                  "inputs": {"repeat_cofailure": {"path": repeat_cof_path.relative_to(ROOT).as_posix(),
                                                  "sha256": sha256_file(repeat_cof_path)},
                             "original_cofailure": {"path": f"results/combined/{args.combined}/cofailure.json",
                                                    "sha256": sha256_file(ROOT / "results/combined" /
                                                                          args.combined / "cofailure.json")}}}
    out_dir = ROOT / args.out
    payload = {"stage": "RP", "status": "EXPLORATORY", "note": EXPLORATORY_NOTE, "provenance": provenance, **result}
    B5.write_once(out_dir / "rp.json", json.dumps(payload, indent=2, sort_keys=True, ensure_ascii=False) + "\n")
    B5.write_once(out_dir / "rp_pairs.csv", to_csv(result))
    md = to_markdown(result, provenance)
    B5.write_once(out_dir / "rp_report.md", md)
    print(md)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
