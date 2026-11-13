"""S36 (DESCRIPTIVE) — intervention evaluation, per case, treatment-only, exploratory.

Usage (from the repository root, after S35):
    python scripts/48_s36_evaluation.py --combined pilot_expansion_v1 --after intervention_v1 --reference repeat_v1

Protocol §21 outcomes: CF3/CF4 before vs after; PCF before vs after; recovery = share of agents whose answers
become question-valid; change in no-answer rate (not recovery); displacement per agent: VALID_RELATION,
SAME_WRONG_RELATION_OTHER_NEIGHBOR, OTHER_WRONG, NO_ANSWER. ΔCF and τ_CF need a control and are not computed
(D7 DESCRIPTIVE; decision log 2026-11-12 "Plan after D7", section A4: per case only, treatment-only, no
aggregate ΔCF, no τ_CF, no causal claim — hiding the label removes those answers by construction).

Readings (researcher, 2026-11-13; decision log entry "S36 — Readings of the §21 outcomes"):
1. Before = pilot_v1/expansion_v1 (results of record); the feature (u, r), its step and its holders come
   only from them (results/interventions/candidates.csv). After = intervention_v1. repeat_v1 = descriptive
   reference column (recovery and displacement only, same holders, same rules).
2. Recovery: denominator = holders with a SUCCESS episode; recovered = ≥ 1 resolved answer and all resolved
   answers question-valid. Non-SUCCESS holders are excluded and listed as technical failures.
3. Displacement per holder (SUCCESS episode), first match: NO_ANSWER (no resolved answer);
   SAME_WRONG_RELATION_OTHER_NEIGHBOR (an OFF_QUESTION answer whose primary path has label r at the feature's
   step at a node ≠ u); OTHER_WRONG (another OFF_QUESTION answer); VALID_RELATION. Per-answer counts of the
   three answer categories are reported as well (descriptive).
4. No-answer rate: SUCCESS episodes with 0 resolved answers / SUCCESS episodes, all 4 agents.
5. CF and PCF flags are read from the frozen §16 analyses of the original and the after run.

Engineering conventions (documented, not protocol): per-answer data come from the frozen §15 metrics rows
(latest attempts); the feature step is 1-based in candidates.csv and indexes primary_path[step - 1]; each run
column's inference commit is read from its pinned agent configs; outputs are write-once.
"""
from __future__ import annotations

import argparse
import csv
import importlib.util
import json
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
CATEGORIES = ("VALID_RELATION", "SAME_WRONG_RELATION_OTHER_NEIGHBOR", "OTHER_WRONG", "NO_ANSWER")
ANSWER_CATEGORIES = CATEGORIES[:3]
CF_KEYS = (("CF3^Q", "question", "cf3"), ("CF4^Q", "question", "cf4"), ("CF3^Q grounded", "grounded", "cf3"),
           ("CF4^Q grounded", "grounded", "cf4"), ("CF3^{Q,H1}", "hop1_clean", "cf3"),
           ("CF4^{Q,H1}", "hop1_clean", "cf4"))
PCF_KEYS = ("pcf_rel3", "pcf_rel4", "pcf_node3", "pcf_node4", "pcf_shortcut3")
NOTE = ("DESCRIPTIVE, EXPLORATORY, TREATMENT-ONLY (D7 DESCRIPTIVE; decision log 2026-11-12 \"Plan after D7\", "
        "section A4; readings 2026-11-13 \"S36 — Readings of the §21 outcomes\"). Per case only; no aggregate "
        "ΔCF and no τ_CF (no control exists, C = 0).")


def _load(name, filename):
    spec = importlib.util.spec_from_file_location(name, ROOT / "scripts" / filename)
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


# ------------------------------------------------------------------------------------- per episode

def answer_category(a: dict, u: str, r: str, step: int) -> str:
    """Category of one resolved answer (reading 3)."""
    if a["label_a"] != "OFF_QUESTION":
        return "VALID_RELATION"
    path = a.get("primary_path") or []
    if len(path) >= step and path[step - 1]["label"] == r and path[step - 1]["u"] != u:
        return "SAME_WRONG_RELATION_OTHER_NEIGHBOR"
    return "OTHER_WRONG"


def holder_outcome(row: dict, u: str, r: str, step: int) -> dict:
    """Displacement category (or the episode status), recovery and per-answer counts for one holder."""
    if row["episode_status"] != "SUCCESS":
        return {"status": row["episode_status"], "category": None, "recovered": None,
                "answer_counts": None, "resolved": None}
    resolved = [a for a in row["answers"] if a["node_id"] is not None]
    cats = [answer_category(a, u, r, step) for a in resolved]
    counts = {c: cats.count(c) for c in ANSWER_CATEGORIES}
    if not resolved:
        category = "NO_ANSWER"
    elif counts["SAME_WRONG_RELATION_OTHER_NEIGHBOR"]:
        category = "SAME_WRONG_RELATION_OTHER_NEIGHBOR"
    elif counts["OTHER_WRONG"]:
        category = "OTHER_WRONG"
    else:
        category = "VALID_RELATION"
    return {"status": "SUCCESS", "category": category, "recovered": category == "VALID_RELATION",
            "answer_counts": counts, "resolved": len(resolved)}


def column(rows: dict, qid: str, holders: list[str], u: str, r: str, step: int) -> dict:
    """Recovery and displacement of the holders in one run column (readings 2–3)."""
    per = {a: holder_outcome(rows[(a, qid)], u, r, step) for a in holders}
    ok = [a for a in holders if per[a]["status"] == "SUCCESS"]
    return {"per_holder": per, "denominator": len(ok),
            "recovered": sum(per[a]["recovered"] for a in ok),
            "technical_failures": {a: per[a]["status"] for a in holders if a not in ok},
            "displacement": {c: sum(per[a]["category"] == c for a in ok) for c in CATEGORIES}}


def no_answer(rows: dict, qid: str, agents: list[str]) -> dict:
    success = [rows[(a, qid)] for a in agents if rows[(a, qid)]["episode_status"] == "SUCCESS"]
    none = sum(not any(x["node_id"] is not None for x in r["answers"]) for r in success)
    return {"no_answer": none, "success_episodes": len(success), "rate": none / len(success) if success else None}


def evaluate(cases: list[dict], before_cof: dict, after_cof: dict, rows: dict[str, dict], agents: list[str]) -> list[dict]:
    """`rows` = {'before': ..., 'after': ..., 'reference': ...} (agent, query) -> §15 metrics row."""
    b = {q["query_id"]: q for q in before_cof["queries"]}
    a = {q["query_id"]: q for q in after_cof["queries"]}
    out = []
    for case in cases:
        qid, u, r, step, holders = case["query_id"], case["u"], case["r"], case["step"], case["holders"]
        if qid not in a:
            raise ValueError(f"{qid}: not in the after-run analysis")
        before_holders = [ag for ag in agents if holder_outcome(rows["before"][(ag, qid)], u, r, step)["status"]
                          == "SUCCESS"]
        if not set(holders) <= set(before_holders):
            raise ValueError(f"{qid}: a listed holder has no SUCCESS original episode")
        out.append({
            "query_id": qid, "mechanism": case["mechanism"], "u": u, "r": r, "step": step, "holders": holders,
            "cf": {label: {"before": int(b[qid][blk][f]), "after": int(a[qid][blk][f])} for label, blk, f in CF_KEYS},
            "pcf": {k: {"before": int(b[qid][k]), "after": int(a[qid][k])} for k in PCF_KEYS},
            "no_answer": {"before": no_answer(rows["before"], qid, agents),
                          "after": no_answer(rows["after"], qid, agents)},
            "after": column(rows["after"], qid, holders, u, r, step),
            "reference_repeat": column(rows["reference"], qid, holders, u, r, step),
            "before_holder_answers": {h: holder_outcome(rows["before"][(h, qid)], u, r, step)["answer_counts"]
                                      for h in holders},
            "same_wrong_possible": step != 1,
        })
    return out


# ------------------------------------------------------------------------------------------ output

def _rate(x: dict) -> str:
    return "NA (0/0)" if x["rate"] is None else f"{x['rate']:.2f} ({x['no_answer']}/{x['success_episodes']})"


def to_markdown(result: list[dict], commits: dict, provenance: dict) -> str:
    out = ["# S36 — Intervention evaluation (DESCRIPTIVE, treatment-only, exploratory)\n", f"{NOTE}\n",
           f"Produced by `scripts/48_s36_evaluation.py` at commit `{provenance['git_commit']}` (tracked files clean: "
           f"{provenance['git_tracked_clean']}). Run columns and their inference commits: " +
           "; ".join(f"{k} = " + ", ".join(f"`{run}` @ `{c}`" for run, c in v.items()) for k, v in commits.items())
           + ".\n",
           "## Observed facts\n",
           "### Table 1 — Co-failure before (original run) vs after (intervention_v1), per case\n",
           "| Case | Mechanism | Hidden | " + " | ".join(k for k, _, _ in CF_KEYS) + " | " + " | ".join(PCF_KEYS) + " |",
           "|---|---|---|" + "---|" * (len(CF_KEYS) + len(PCF_KEYS))]
    for c in result:
        cells = [f"{c['cf'][k]['before']} → {c['cf'][k]['after']}" for k, _, _ in CF_KEYS]
        cells += [f"{c['pcf'][k]['before']} → {c['pcf'][k]['after']}" for k in PCF_KEYS]
        out.append(f"| {c['query_id']} | {c['mechanism']} | `{c['r']}` at {c['u']} (step {c['step']}) | "
                   + " | ".join(cells) + " |")
    out += ["", "### Table 2 — Recovery, no-answer rate and technical failures, per case\n",
            "| Case | Holders | Recovery after | Recovery, repeat_v1 reference | No-answer rate before → after | "
            "Technical failures after (holders) | Technical failures, repeat_v1 (holders) |",
            "|---|---|---|---|---|---|---|"]
    for c in result:
        aft, ref = c["after"], c["reference_repeat"]
        tf = lambda col: ", ".join(f"{k} {v}" for k, v in col["technical_failures"].items()) or "—"  # noqa: E731
        out.append(f"| {c['query_id']} | {', '.join(c['holders'])} | {aft['recovered']}/{aft['denominator']} | "
                   f"{ref['recovered']}/{ref['denominator']} | {_rate(c['no_answer']['before'])} → "
                   f"{_rate(c['no_answer']['after'])} | {tf(aft)} | {tf(ref)} |")
    out += ["", "Recovery = holders (SUCCESS episodes only) with ≥ 1 resolved answer, all question-valid.\n",
            "### Table 3 — Displacement per holder (result of record: one category; descriptive: answer counts "
            "VALID / SAME_WRONG_OTHER_NEIGHBOR / OTHER_WRONG)\n",
            "| Case | Holder | Before: answer counts | After: category | After: answer counts | "
            "repeat_v1: category | repeat_v1: answer counts |", "|---|---|---|---|---|---|---|"]

    def cell(o):
        return (o["category"] or o["status"]), ("—" if o["answer_counts"] is None else
                                                " / ".join(str(o["answer_counts"][k]) for k in ANSWER_CATEGORIES))

    for c in result:
        for h in c["holders"]:
            a_cat, a_cnt = cell(c["after"]["per_holder"][h])
            r_cat, r_cnt = cell(c["reference_repeat"]["per_holder"][h])
            bc = c["before_holder_answers"][h]
            out.append(f"| {c['query_id']} | {h} | {' / '.join(str(bc[k]) for k in ANSWER_CATEGORIES)} | {a_cat} | "
                       f"{a_cnt} | {r_cat} | {r_cnt} |")
    out += ["", "### Table 4 — Displacement counts per case (SUCCESS after-episodes of holders)\n",
            "| Case | " + " | ".join(CATEGORIES) + " | Excluded (technical failure) |",
            "|---|" + "---|" * (len(CATEGORIES) + 1)]
    for c in result:
        d = c["after"]["displacement"]
        out.append(f"| {c['query_id']} | " + " | ".join(str(d[k]) for k in CATEGORIES)
                   + f" | {len(c['after']['technical_failures'])} |")
    out += ["", "## Notes\n",
            "- For the SHORTCUT case BH2_04650 (u = s, step 1), SAME_WRONG_RELATION_OTHER_NEIGHBOR cannot occur by "
            "construction: step 1 always starts at s.",
            "- Hiding the label removes the answers reached through it by construction (decision log 2026-11-12, "
            "A4); these tables state observed counts only.",
            "- ΔCF and τ_CF are not computed: both need a matched control, and none exists (C = 0).", ""]
    return "\n".join(out)


def to_csv(result: list[dict]) -> str:
    import io
    buf = io.StringIO()
    w = csv.writer(buf, lineterminator="\n")
    w.writerow(["query_id", "holder", "column", "status", "category", "recovered", *ANSWER_CATEGORIES])
    for c in result:
        for col in ("after", "reference_repeat"):
            for h in c["holders"]:
                o = c[col]["per_holder"][h]
                counts = o["answer_counts"] or {}
                w.writerow([c["query_id"], h, col, o["status"], o["category"] or "", "" if o["recovered"] is None
                            else o["recovered"], *[counts.get(k, "") for k in ANSWER_CATEGORIES]])
    return buf.getvalue()


def run_commits(run_dir: Path) -> str:
    """The inference commit(s) of a run, from its pinned agent configs; several are listed with their agents."""
    by_agent = {p.name.split(".config.json")[0]: json.loads(p.read_text(encoding="utf-8"))["config"]["git_commit"]
                for p in sorted((run_dir / "configs").glob("*.config.json"))}
    commits = sorted(set(by_agent.values()))
    if len(commits) == 1:
        return commits[0]
    return "; ".join(f"{c} ({', '.join(a for a, x in by_agent.items() if x == c)})" for c in commits)


def main(argv=None) -> int:
    if hasattr(sys.stdout, "reconfigure"):
        sys.stdout.reconfigure(encoding="utf-8")
    ap = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    ap.add_argument("--combined", required=True)
    ap.add_argument("--after", required=True)
    ap.add_argument("--reference", required=True)
    ap.add_argument("--out", default="results/interventions/s36")
    args = ap.parse_args(argv)
    report = _load("s28_report", "28_pilot_report.py")
    b5 = _load("b5_concentration", "42_b5_concentration.py")
    original = report.load_combined(args.combined)
    agents = original["agents"]
    runs = ROOT / "results/runs"
    after_cof = json.loads((runs / args.after / "analysis/cofailure.json").read_text(encoding="utf-8"))
    rows = {"before": original["rows"],
            "after": report.latest_rows(runs / args.after / "analysis/metrics", agents),
            "reference": report.latest_rows(runs / args.reference / "analysis/metrics", agents)}
    s33 = [json.loads(x)["query_id"] for x in (ROOT / "results/interventions/manifest.jsonl")
           .read_text(encoding="utf-8").splitlines() if x.strip()]
    cases = []
    for c in csv.DictReader((ROOT / "results/interventions/candidates.csv").open(encoding="utf-8")):
        if c["query_id"] in s33:
            cases.append({"query_id": c["query_id"], "mechanism": c["mechanism"], "u": c["feature_u"],
                          "r": c["feature_r"], "step": int(c["feature_step"]),
                          "holders": [a for a in agents if a in c["feature_agents"].split(";")]})
    if sorted(c["query_id"] for c in cases) != sorted(s33):
        raise ValueError("candidates.csv does not list every S33 case")
    for c in cases:
        if len(c["holders"]) != len(set(c["holders"])) or not c["holders"]:
            raise ValueError(f"{c['query_id']}: bad holder list")
    result = evaluate(sorted(cases, key=lambda c: c["query_id"]), original["cofailure"], after_cof, rows, agents)
    spec = json.loads((ROOT / "results/combined" / args.combined / "components.json").read_text(encoding="utf-8"))
    commits = {"before": {run: run_commits(runs / run) for run in sorted(spec["components"])},
               "after": {args.after: run_commits(runs / args.after)},
               "reference": {args.reference: run_commits(runs / args.reference)}}
    commit, clean = b5.git_state()
    provenance = {"git_commit": commit, "git_tracked_clean": clean}
    payload = {"stage": "S36", "status": "DESCRIPTIVE", "note": NOTE, "run_commits": commits,
               "provenance": provenance, "cases": result}
    out = ROOT / args.out
    b5.write_once(out / "s36.json", json.dumps(payload, indent=2, sort_keys=True, ensure_ascii=False) + "\n")
    b5.write_once(out / "s36_holders.csv", to_csv(result))
    md = to_markdown(result, commits, provenance)
    b5.write_once(out / "s36_report.md", md)
    print(md)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
