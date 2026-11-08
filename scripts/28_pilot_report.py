"""S28 pilot report: descriptive tables over an existing panel run's analysis outputs (no inference).

Usage (from the repository root):
    python scripts/28_pilot_report.py --manifest pilot --run-id pilot_v1

Reads only evaluator outputs already written by `scripts/25_run_panel.py analyze`
(results/runs/<run_id>/analysis/: per-episode §15 metrics, §16 cofailure.json, §17 nulls.json), the
evaluation-side manifest (data/processed/manifests/<manifest>.jsonl), the agent-input sheet (question
text only) and the raw episode records (submitted answer (id, name) pairs and entity names shown in tool
output). Nothing is recomputed that the analysis already holds: labels, paths, H1, co-failure flags and
null distributions are read as stored. No code, definition or threshold is changed.

Writes results/reports/<run_id>_report.md with three sections: (A) observed facts, (B) descriptive
comparisons, (C) open questions. The D6 quantities (decision_rules.md D6) and both interpretation flags
are computed; the gate outcome is not stated (that is S29).

Engineering conventions (documented, not protocol):
* Latest attempt per (query, agent) is used everywhere (§19); a duplicate attempt number is an error.
* Per-model ratio metrics are means of per-episode values over episodes where the value is defined;
  NA episodes are excluded and counted (§15). Pooled (answer-level) ratios are shown beside them.
* Explored-bridge ranks are binned 1 / 2–10 / 11–50 (page 1 at page size 50) / 51–100 / >100 / NA.
* `H` (D6) uses §14.3 "found R1" exactly as stored for every episode, whatever its status; the count
  restricted to SUCCESS episodes is shown beside it for inspection only.
* The unresolved-answer diagnostic (decision log 2026-10-17) compares retained unresolved answers
  within one episode under the rule stated in the report; it changes no official count.
* The rendered report is scanned for a fixed list of causal words; a hit is an error.
"""
from __future__ import annotations

import argparse
from collections import Counter, defaultdict
import json
from pathlib import Path
import re
import statistics
import unicodedata

ROOT = Path(__file__).resolve().parents[1]
AMBIGUOUS_TAGS = ("R1_AMBIGUOUS", "R2_AMBIGUOUS", "BOTH_AMBIGUOUS")  # decision_rules D6 ambiguity flag
TECHNICAL = ("TIMEOUT", "ERROR", "PARSE_FAIL")  # §9.5
STATUSES = ("SUCCESS", "PARSE_FAIL", "ERROR", "TIMEOUT")
LABEL_A = ("GOLD", "GOLD_BRIDGE_EXTRA", "ALT_VALID", "OFF_QUESTION", "UNRESOLVED")
LABEL_B = ("SUPPORTED", "PATH_INVALID", "KG_UNSUPPORTED", "UNGROUNDED", "NOT_APPLICABLE")
REASONS = ("SHORTCUT", "WRONG_RELATION_HOP1", "WRONG_RELATION_HOP2", "WRONG_BRIDGE_TYPE",
           "WRONG_TARGET_TYPE", "WRONG_HOP_COUNT")
HOP1 = ("H1_CLEAN", "H1_MIXED", "H1_WRONG", "H1_NONE")
# (column header, cofailure.json query key, flag key) for every §16 per-query flag.
CF_METRICS = (
    ("CF3^Q", "question", "cf3"), ("CF4^Q", "question", "cf4"),
    ("CF3^Q grounded", "grounded", "cf3"), ("CF4^Q grounded", "grounded", "cf4"),
    ("CF3^{Q,H1}", "hop1_clean", "cf3"), ("CF4^{Q,H1}", "hop1_clean", "cf4"),
    ("CF3^BH", "benchmark", "cf3"), ("CF4^BH", "benchmark", "cf4"),
    ("PCF_REL3", None, "pcf_rel3"), ("PCF_REL4", None, "pcf_rel4"),
    ("PCF_NODE3", None, "pcf_node3"), ("PCF_NODE4", None, "pcf_node4"),
    ("PCF_SHORTCUT3", None, "pcf_shortcut3"),
)
TOTAL_KEYS = {"CF3^Q": "question_cf3", "CF4^Q": "question_cf4", "CF3^Q grounded": "grounded_cf3",
              "CF4^Q grounded": "grounded_cf4", "CF3^{Q,H1}": "hop1_clean_cf3",
              "CF4^{Q,H1}": "hop1_clean_cf4", "CF3^BH": "benchmark_cf3", "CF4^BH": "benchmark_cf4",
              "PCF_REL3": "pcf_rel3", "PCF_REL4": "pcf_rel4", "PCF_NODE3": "pcf_node3",
              "PCF_NODE4": "pcf_node4", "PCF_SHORTCUT3": "pcf_shortcut3"}
RANK_BINS = (("1", 1, 1), ("2–10", 2, 10), ("11–50", 11, 50), ("51–100", 51, 100), (">100", 101, None))
# Words that would state or imply causation; "effect/phenotype" is a PrimeKG node type and is allowed.
CAUSAL = re.compile(r"\b(because|caus\w*|due to|lead(s)? to|led to|driv(e|es|en|ing)|result(s|ed)? in|"
                    r"impact\w*|explain\w*|attribut\w*|induc\w*|trigger\w*|responsible|effects?(?!/))\b",
                    re.IGNORECASE)


# ----------------------------------------------------------------------------------------------- loading

def _jsonl(path: Path) -> list[dict]:
    return [json.loads(line) for line in path.read_text(encoding="utf-8").splitlines() if line.strip()]


def latest_rows(metrics_dir: Path, agent_order: list[str]) -> dict[tuple[str, str], dict]:
    """(agent, query) -> §15 metrics row of the latest attempt (§19)."""
    rows: dict[tuple[str, str], dict] = {}
    for agent in agent_order:
        for path in sorted((metrics_dir / agent).glob("*.json")):
            row = json.loads(path.read_text(encoding="utf-8"))
            if row["agent_id"] != agent:
                raise ValueError(f"{path}: agent_id {row['agent_id']!r} in {agent} folder")
            key = (agent, row["query_id"])
            old = rows.get(key)
            if old is not None and old["attempt"] == row["attempt"]:
                raise ValueError(f"{path}: duplicate attempt {row['attempt']} for {key}")
            if old is None or row["attempt"] > old["attempt"]:
                rows[key] = row
    return rows


def load_run(run_id: str, manifest: str, root: Path = ROOT) -> dict:
    run_dir = root / "results/runs" / run_id
    analysis = run_dir / "analysis"
    cof = json.loads((analysis / "cofailure.json").read_text(encoding="utf-8"))
    nulls = json.loads((analysis / "nulls.json").read_text(encoding="utf-8"))
    agents = cof["agent_order"]
    if nulls["agent_order"] != agents:
        raise ValueError("cofailure.json and nulls.json list different agent orders")
    man = _jsonl(root / "data/processed/manifests" / f"{manifest}.jsonl")
    sheet = {r["query_id"]: r for r in _jsonl(root / "data/agent_inputs" / f"{manifest}.jsonl")}
    query_ids = [r["query_id"] for r in man]
    if sorted(query_ids) != sorted(sheet) or sorted(query_ids) != sorted(q["query_id"] for q in cof["queries"]):
        raise ValueError("manifest, agent-input sheet and cofailure.json list different queries")
    rows = latest_rows(analysis / "metrics", agents)
    expected = {(a, q) for a in agents for q in query_ids}
    if set(rows) != expected:
        raise ValueError(f"metrics rows: missing {sorted(expected - set(rows))[:5]}, "
                         f"extra {sorted(set(rows) - expected)[:5]}")
    records = {}
    for (agent, q), row in rows.items():
        path = run_dir / f"{q}__{agent}__a{row['attempt']}.json"
        records[(agent, q)] = json.loads(path.read_text(encoding="utf-8"))
    return {"run_id": run_id, "manifest": manifest, "agents": agents, "manifest_rows": man,
            "sheet": sheet, "cofailure": cof, "nulls": nulls, "rows": rows, "records": records}


# ------------------------------------------------------------------------------------------- formatting

def frac(num, den, digits=3) -> str:
    if not den:
        return f"NA ({num}/{den})"
    return f"{num / den:.{digits}f} ({num}/{den})"


def fmt(x, digits=3) -> str:
    if x is None:
        return "NA"
    if isinstance(x, float):
        return f"{x:.{digits}f}"
    return str(x)


def table(header: list[str], body: list[list]) -> str:
    out = ["| " + " | ".join(header) + " |", "|" + "|".join("---" for _ in header) + "|"]
    out += ["| " + " | ".join(str(c) for c in r) + " |" for r in body]
    return "\n".join(out)


# ------------------------------------------------------------------------------------- table 1: technical

def technical(rows: dict, agents: list[str]) -> dict:
    """Status counts per model (with ERROR causes) and E = technical failures / episodes (§9.5, D6)."""
    per = {}
    for agent in agents:
        mine = [r for (a, _), r in rows.items() if a == agent]
        counts = Counter(r["episode_status"] for r in mine)
        unknown = set(counts) - set(STATUSES)
        if unknown:
            raise ValueError(f"{agent}: unknown episode status {sorted(unknown)}")
        causes = Counter(r["cause"] for r in mine if r["episode_status"] == "ERROR")
        per[agent] = {"episodes": len(mine), **{s: counts.get(s, 0) for s in STATUSES},
                      "technical": sum(counts.get(s, 0) for s in TECHNICAL),
                      "error_causes": dict(sorted(causes.items(), key=lambda kv: str(kv[0])))}
    episodes = sum(p["episodes"] for p in per.values())
    failures = sum(p["technical"] for p in per.values())
    return {"per_agent": per, "episodes": episodes, "technical_failures": failures,
            "E": failures / episodes if episodes else None}


# ------------------------------------------------------------------------------------- table 2: per model

def _mean_defined(values):
    defined = [v for v in values if v is not None]
    return (statistics.fmean(defined) if defined else None), len(defined), len(values) - len(defined)


def per_model(rows: dict, agents: list[str]) -> dict:
    out = {}
    for agent in agents:
        mine = [r for (a, _), r in sorted(rows.items()) if a == agent]
        success = [r for r in mine if r["episode_status"] == "SUCCESS"]
        la = Counter(); lb = Counter(); prim = Counter(); allp = Counter()
        la_by_c: dict[str, Counter] = defaultdict(Counter)
        for r in success:
            la.update(r["label_a_counts"]); lb.update(r["label_b_counts"])
            prim.update(r["primary_reason_counts"]); allp.update(r["reason_counts"])
            la_by_c[r["construction"]].update(r["label_a_counts"])
        ratios = {}
        for key in ("question_valid_precision", "off_question_rate", "unresolved_rate", "ungrounded_rate",
                    "benchmark_precision", "benchmark_recall", "benchmark_f1"):
            mean, n_def, n_na = _mean_defined([r[key] for r in mine])
            num = sum(r["numerators"][key] or 0 for r in mine if r[key] is not None)
            den = sum(r["denominators"][key] or 0 for r in mine if r[key] is not None)
            ratios[key] = {"mean": mean, "defined": n_def, "na": n_na, "pooled_num": num, "pooled_den": den}
        early = [r["early_stop"] for r in mine if r["early_stop"] is not None]
        out[agent] = {
            "episodes": len(mine), "success": len(success),
            "label_a": {k: la.get(k, 0) for k in LABEL_A}, "label_b": {k: lb.get(k, 0) for k in LABEL_B},
            "label_a_by_construction": {c: {k: v.get(k, 0) for k in LABEL_A} for c, v in sorted(la_by_c.items())},
            "primary_reasons": {k: prim.get(k, 0) for k in REASONS},
            "all_path_reasons": {k: allp.get(k, 0) for k in REASONS},
            "ratios": ratios,
            "hop1": {k: sum(r["hop1_status"] == k for r in mine) for k in HOP1},
            "early_stop": (sum(early), len(early), len(mine) - len(early)),
            "budget_hit": (sum(bool(r["budget_exhausted"]) for r in mine), len(mine)),
            "answers": sum(r["answer_count"] or 0 for r in success),
        }
    return out


# ------------------------------------------------------------------------------- table 3/5: co-failure

def cf_flag(q: dict, block, key) -> int:
    return int(q[block][key]) if block else int(q[key])


def cf_counts(queries: list[dict]) -> dict[str, int]:
    return {name: sum(cf_flag(q, b, k) for q in queries) for name, b, k in CF_METRICS}


def check_totals(cof: dict) -> None:
    """The per-query flags must add up to the stored totals (consistency check, no recomputation)."""
    overlap = set(cof["source_name_overlap_queries"])
    for subset, key in ((cof["queries"], "totals_all_queries"),
                        ([q for q in cof["queries"] if q["query_id"] not in overlap],
                         "totals_without_source_name_overlap")):
        counts = cf_counts(subset)
        for name, total_key in TOTAL_KEYS.items():
            if counts[name] != cof[key][total_key]:
                raise ValueError(f"{key}.{total_key}: stored {cof[key][total_key]} != per-query sum {counts[name]}")


def strata(queries: list[dict], manifest: dict[str, dict], field: str) -> list[tuple[str, int, dict]]:
    groups: dict[str, list[dict]] = defaultdict(list)
    for q in queries:
        groups[manifest[q["query_id"]][field]].append(q)
    return [(k, len(v), cf_counts(v)) for k, v in sorted(groups.items())]


def pairwise_matrix(pairs: list[dict], agents: list[str]) -> list[list[str]]:
    cell = {}
    for p in pairs:
        text = frac(p["numerator"], p["denominator"])
        cell[(p["agent_i"], p["agent_j"])] = cell[(p["agent_j"], p["agent_i"])] = text
    return [[a] + ["—" if a == b else cell[(a, b)] for b in agents] for a in agents]


# ---------------------------------------------------------------------------------- table 6: ordering

def rank_bin(rank) -> str:
    if rank is None:
        return "NA"
    for name, lo, hi in RANK_BINS:
        if rank >= lo and (hi is None or rank <= hi):
            return name
    raise ValueError(f"bridge rank {rank!r} below 1")


def bridge_ranks(rows: dict, agents: list[str]) -> dict:
    out = {}
    for agent in agents + ["All"]:
        ranks = [v for (a, _), r in rows.items() if agent in ("All", a) for v in r["bridge_rank"].values()]
        bins = Counter(rank_bin(v) for v in ranks)
        defined = sorted(v for v in ranks if v is not None)
        out[agent] = {"n": len(ranks), "bins": {name: bins.get(name, 0) for name, _, _ in RANK_BINS + (("NA", 0, 0),)},
                      "median": float(statistics.median(defined)) if defined else None,
                      "max": defined[-1] if defined else None}
    return out


def shared_wrong_answers(cof: dict, rows: dict) -> list[dict]:
    """Every (query, shared CF3^Q entity, holding agent) with its §15 FIRST_SEEN_PAGE and list sizes."""
    out = []
    for q in cof["queries"]:
        for ent in q["question"]["shared_entities"]:
            for agent in ent["agents"]:
                ans = next(a for a in rows[(agent, q["query_id"])]["answers"] if a["node_id"] == ent["entity_id"])
                out.append({"query_id": q["query_id"], "entity_id": ent["entity_id"], "agent": agent,
                            "agent_count": ent["agent_count"], "h1": ans["h1"],
                            "first_seen_page": ans["first_seen_page"], "list_size": ans["list_size"],
                            "primary_path_max_list_size": ans["primary_path_max_list_size"],
                            "path_length": None if ans["primary_path"] is None else len(ans["primary_path"])})
    return out


# ------------------------------------------------------------------------------ table 7: case sheets

def entity_names(records: list[dict]) -> dict[str, str]:
    """Entity names exactly as tool output showed them (first seen wins; sorted record order)."""
    names: dict[str, str] = {}
    for rec in records:
        for call in rec["call_log"]:
            res = call.get("result")
            if not call.get("success") or not isinstance(res, dict):
                continue
            if "id" in res and "name" in res:
                names.setdefault(str(res["id"]), res["name"])
            for item in res.get("items", []):
                names.setdefault(str(item["id"]), item["name"])
    return names


def render_path(path, names: dict[str, str]) -> str:
    if path is None:
        return "(no path in trace graph)"
    if not path:
        return "(length 0: answer is s)"
    def node(n):
        return f"{names.get(n, '?')} [{n}]"
    return node(path[0]["u"]) + "".join(f" —{e['label']}→ {node(e['v'])}" for e in path)


def case_sheets(data: dict) -> list[dict]:
    cof, rows, man = data["cofailure"], data["rows"], {r["query_id"]: r for r in data["manifest_rows"]}
    sheets = []
    for q in sorted(cof["queries"], key=lambda q: q["query_id"]):
        if not q["hop1_clean"]["cf3"]:
            continue
        qid = q["query_id"]
        names = entity_names([data["records"][(a, qid)] for a in data["agents"]])
        entities = []
        for ent in q["hop1_clean"]["shared_entities"]:
            per = []
            for agent in data["agents"]:
                ans = next((a for a in rows[(agent, qid)]["answers"] if a["node_id"] == ent["entity_id"]), None)
                per.append({"agent": agent, "co_failing": agent in ent["agents"],
                            "answer": ans, "path": render_path(ans["primary_path"], names) if ans else None})
            entities.append({**ent, "name": names.get(ent["entity_id"], "?"), "per_agent": per})
        sheets.append({"query_id": qid, "question": data["sheet"][qid]["question_text"],
                       "start": f"{data['sheet'][qid]['start_name']} [{q['s']}]",
                       "relation_type": q["relation_type"], "ambiguity_tag": q["ambiguity_tag"],
                       "multiplicity": man[qid]["multiplicity"], "R1": q["R1"], "R2": q["R2"],
                       "statuses": {a: q["episodes"][a]["episode_status"] for a in data["agents"]},
                       "entities": entities})
    return sheets


# --------------------------------------------------------------------- table 8: unresolved diagnostic

def comparison_key(answer_id, name) -> tuple[str, str]:
    """Diagnostic comparison rule: ID as a whitespace-trimmed string; name NFKC, lower-cased,
    internal whitespace collapsed to one space, trimmed (the §12 string normalization)."""
    norm_name = " ".join(unicodedata.normalize("NFKC", str(name)).lower().split())
    return str(answer_id).strip(), norm_name


def unresolved_diagnostic(rows: dict, records: dict, agents: list[str]) -> dict:
    """Retained unresolved answers of one episode that are distinct as exact (id, name) pairs but share a
    comparison_key. Official deduplication (exact pairs; decision log 2026-10-17) is unchanged."""
    per_agent = {a: {"unresolved_retained": 0, "episodes_with_unresolved": 0} for a in agents}
    groups = []
    for (agent, qid), row in sorted(rows.items()):
        unresolved = [a for a in row["answers"] if a["node_id"] is None]
        if not unresolved:
            continue
        per_agent[agent]["unresolved_retained"] += len(unresolved)
        per_agent[agent]["episodes_with_unresolved"] += 1
        parsed = [e for e in records[(agent, qid)]["log_events"] if e.get("event") == "FINAL_PARSED"]
        if len(parsed) != 1:
            raise ValueError(f"{qid}/{agent}: expected one FINAL_PARSED event, found {len(parsed)}")
        submitted = parsed[0]["parsed"]["answers"]
        by_key: dict[tuple, list] = defaultdict(list)
        for a in unresolved:
            item = submitted[a["submitted_index"]]
            by_key[comparison_key(item["id"], item["name"])].append(
                {"submitted_index": a["submitted_index"], "id": item["id"], "name": item["name"]})
        for key, items in sorted(by_key.items()):
            if len(items) > 1:
                groups.append({"query_id": qid, "agent": agent, "key": list(key), "items": items})
    return {"per_agent": per_agent, "merge_groups": groups}


# ---------------------------------------------------------------------------------- D6 quantities

def d6_quantities(data: dict, tech: dict) -> dict:
    """decision_rules.md D6 quantities and interpretation flags. Outcome deliberately not derived."""
    cof, nulls, rows, agents = data["cofailure"], data["nulls"], data["rows"], data["agents"]
    qids = [q["query_id"] for q in cof["queries"]]
    found = {q: sum(bool(rows[(a, q)]["found_r1"]) for a in agents) for q in qids}
    found_success = {q: sum(bool(rows[(a, q)]["found_r1"]) and rows[(a, q)]["episode_status"] == "SUCCESS"
                            for a in agents) for q in qids}
    n_queries = [q for q in cof["queries"] if q["hop1_clean"]["cf3"]]
    agg = nulls["aggregate_all_queries"]
    def cmp(name):
        c = agg[name]["cf3"]
        return {"observed": c["observed_total"], "p95": c["null_p95"], "mean": c["null_mean"], "p": c["p"],
                "exceeds": c["observed_total"] > c["null_p95"], "stored_exceeds": c["observed_exceeds_null"]}
    o_h1, o_n1, o_n2 = cmp("N1-H1"), cmp("N1"), cmp("N2")
    for c in (o_h1, o_n1, o_n2):
        if c["exceeds"] != c["stored_exceeds"]:
            raise ValueError("stored observed_exceeds_null disagrees with observed > p95")
    ambiguous = [q for q in n_queries if q["ambiguity_tag"] in AMBIGUOUS_TAGS]
    return {
        "E": (tech["technical_failures"], tech["episodes"]),
        "H": (sum(v >= 3 for v in found.values()), len(qids)),
        "H_success_only": (sum(v >= 3 for v in found_success.values()), len(qids)),
        "N": len(n_queries), "N_queries": [q["query_id"] for q in n_queries],
        "O_H1": o_h1, "O_N1": o_n1, "O_N2": o_n2,
        "P": len({q["relation_type"] for q in n_queries}),
        "P_types": sorted({q["relation_type"] for q in n_queries}),
        "ordering_flag": o_n1["exceeds"] and not o_n2["exceeds"],
        "ambiguity_share": (len(ambiguous), len(n_queries)),
        "ambiguity_flag": bool(n_queries) and len(ambiguous) / len(n_queries) > 0.70,
    }


# ------------------------------------------------------------------------------------------- render

def render(data: dict) -> str:
    agents, cof, nulls = data["agents"], data["cofailure"], data["nulls"]
    check_totals(cof)
    man = {r["query_id"]: r for r in data["manifest_rows"]}
    tech = technical(data["rows"], agents)
    pm = per_model(data["rows"], agents)
    d6 = d6_quantities(data, tech)
    overlap = cof["source_name_overlap_queries"]
    L: list[str] = []
    w = L.append

    w(f"# Pilot report — run `{data['run_id']}`\n")
    w(f"Generated by `scripts/28_pilot_report.py` from `results/runs/{data['run_id']}/analysis/` "
      f"(manifest `{data['manifest']}`, {len(man)} queries × {len(agents)} agents, latest attempts, protocol §19). "
      "All numbers are descriptive. Agent order: " + ", ".join(agents) + ".\n")
    w(f"SOURCE_NAME_OVERLAP queries (§19.1): {', '.join(overlap) or 'none'}. Every co-failure table and "
      "chance-baseline comparison is shown on all queries and again without them.\n")

    # ------------------------------------------------------------------ (A)
    w("## (A) Observed facts\n")
    w("### Table 1 — Technical status per model (§9.5)\n")
    body = [[a, p["episodes"], *[p[s] for s in STATUSES], p["technical"],
             ", ".join(f"{k}: {v}" for k, v in p["error_causes"].items()) or "—"]
            for a, p in tech["per_agent"].items()]
    body.append(["All", tech["episodes"], *[sum(p[s] for p in tech["per_agent"].values()) for s in STATUSES],
                 tech["technical_failures"], "—"])
    w(table(["Model", "Episodes", *STATUSES, "Technical failures", "ERROR by §9.5 `cause` field"], body))
    w(f"\n**E** = technical failures / episodes = {frac(*d6['E'], digits=4)}.\n")

    w("### Table 2 — Per-model metrics (§13–§15)\n")
    w("Label counts are over retained answers of SUCCESS episodes. Ratios: mean of per-episode values over "
      "episodes where the value is defined (`n` = defined episodes, NA = undefined, excluded and counted, §15), "
      "with the pooled answer-level ratio in brackets.\n")
    w("**2a. Label A counts**\n")
    w(table(["Model", "SUCCESS episodes", "Answers", *LABEL_A],
            [[a, p["success"], p["answers"], *p["label_a"].values()] for a, p in pm.items()]))
    w("\n**2b. Label A counts by construction (§5.3, §13)**\n")
    w(table(["Model", "Construction", *LABEL_A],
            [[a, c, *v.values()] for a, p in pm.items() for c, v in p["label_a_by_construction"].items()]))
    w("\n**2c. Label B counts**\n")
    w(table(["Model", *LABEL_B], [[a, *p["label_b"].values()] for a, p in pm.items()]))
    w("\n**2d. Reason codes (§14.2), PATH_INVALID answers: primary path / union over simple paths ≤ 3**\n")
    w(table(["Model", *REASONS], [[a, *(f"{p['primary_reasons'][k]} / {p['all_path_reasons'][k]}" for k in REASONS)]
                                  for a, p in pm.items()]))
    w("\n**2e. Ratio metrics**\n")
    keys = (("Question-valid precision", "question_valid_precision"), ("OFF_QUESTION rate", "off_question_rate"),
            ("UNRESOLVED rate", "unresolved_rate"), ("UNGROUNDED rate", "ungrounded_rate"),
            ("Benchmark P", "benchmark_precision"), ("Benchmark R", "benchmark_recall"),
            ("Benchmark F1", "benchmark_f1"))
    body = []
    for label, k in keys:
        cells = []
        for a in agents:
            r = pm[a]["ratios"][k]
            pooled = fmt(r["pooled_num"] / r["pooled_den"]) if r["pooled_den"] else "NA"
            cells.append(f"{fmt(r['mean'])} [{pooled}] (n={r['defined']}, NA={r['na']})")
        body.append([label, *cells])
    w(table(["Metric", *agents], body))
    w("\nBenchmark F1 pooled value = 2·Σcorrect / (Σresolved + Σ|A*_q|).\n")
    w("**2f. Hop-1 status per agent (§14.3), early stop and budget hit (§15)**\n")
    body = []
    for a, p in pm.items():
        es, es_n, es_na = p["early_stop"]
        bh, bh_n = p["budget_hit"]
        body.append([a, *p["hop1"].values(), frac(es, es_n) + f", NA={es_na}", frac(bh, bh_n)])
    w(table(["Model", *HOP1, "Early-stop share", "Budget-hit share"], body))
    w("\nHop-1 status is taken from every episode's calls, whatever its status. Early stop is defined only for "
      "SUCCESS episodes (NA otherwise). Budget hit = tool calls charged ≥ budget (30), over all episodes.\n")

    w("### Table 3 — Co-failure (§16), number of queries with the flag = 1\n")
    no_overlap = [q for q in cof["queries"] if q["query_id"] not in set(overlap)]
    all_c, no_c = cf_counts(cof["queries"]), cf_counts(no_overlap)
    w(table(["Metric", f"All queries (n={len(cof['queries'])})", f"Without SOURCE_NAME_OVERLAP (n={len(no_overlap)})"],
            [[name, frac(all_c[name], len(cof["queries"])), frac(no_c[name], len(no_overlap))]
             for name, _, _ in CF_METRICS]))
    w("\nQueries with each flag = 1:\n")
    for name, b, k in CF_METRICS:
        ids = [q["query_id"] for q in cof["queries"] if cf_flag(q, b, k)]
        if ids:
            w(f"- {name}: {', '.join(ids)}")
    w("\n**3b. Pairwise error agreement (§16.4)** — share of queries where both agents have a non-empty "
      "W (OFF_QUESTION set) and the two sets intersect (numerator/denominator).\n")
    w("All queries:\n")
    w(table(["", *agents], pairwise_matrix(cof["pairwise_all_queries"], agents)))
    w("\nWithout SOURCE_NAME_OVERLAP queries:\n")
    w(table(["", *agents], pairwise_matrix(cof["pairwise_without_source_name_overlap"], agents)))
    w("")

    w("### Table 7 — Case sheets: every query with CF3^{Q,H1} = 1\n")
    sheets = case_sheets(data)
    if not sheets:
        w("No query has CF3^{Q,H1} = 1.\n")
    for sh in sheets:
        w(f"#### Case {sh['query_id']}\n")
        w(f"- **Question:** {sh['question']}")
        w(f"- **Starting entity s:** {sh['start']}")
        w(f"- **Relation type:** `{sh['relation_type']}` · **Ambiguity tag:** {sh['ambiguity_tag']} · "
          f"**Bridge multiplicity:** {sh['multiplicity']}")
        w(f"- **R1:** {', '.join(sh['R1'])} · **R2:** {', '.join(sh['R2'])}")
        w("- **Episode statuses:** " + ", ".join(f"{a}: {s}" for a, s in sh["statuses"].items()))
        for ent in sh["entities"]:
            w(f"\n**Shared OFF_QUESTION entity:** {ent['name']} [{ent['entity_id']}] — hop-1-clean holders "
              f"{ent['agent_count']}/4; degree {ent['degree']}, degree percentile {ent['degree_percentile']:.2f} (§15)\n")
            body = []
            for p in ent["per_agent"]:
                a = p["answer"]
                if a is None:
                    body.append([p["agent"], "no", "not in answers", "—", "—", "—", "—", "—"])
                    continue
                body.append([p["agent"], "yes" if p["co_failing"] else "no (H1=0)", p["path"], a["label_b"],
                             ", ".join(a["primary_reason_codes"]) or "—", ", ".join(a["reason_codes"]) or "—",
                             a["first_seen_page"], fmt(a["primary_path_max_list_size"])])
            w(table(["Agent", "Counts for CF3^{Q,H1}", "Primary path (§14.2)", "Label B",
                     "Reason codes (primary)", "Reason codes (all paths ≤ 3)", "FIRST_SEEN_PAGE",
                     "Largest list size on path"], body))
        w("")

    w("### Table 8 — Unresolved-answer diagnostic (decision log 2026-10-17)\n")
    diag = unresolved_diagnostic(data["rows"], data["records"], agents)
    w("Official deduplication is unchanged: unresolved answers are deduplicated only as exact submitted "
      "(id, name) pairs, with no case or whitespace folding and no ID type coercion. The literal name/ID "
      "mismatch flag (§12 `NAME_ID_MISMATCH`) is diagnostic only and changes no label.\n")
    w("**Comparison rule used for this diagnostic only:** two retained unresolved answers of the same episode "
      "*would merge* if (i) their submitted IDs are equal after converting to a string and trimming leading "
      "and trailing whitespace, and (ii) their submitted names are equal after Unicode NFKC normalization, "
      "lower-casing, collapsing internal whitespace to a single space and trimming (the §12 string "
      "normalization). Answers of different episodes are never compared.\n")
    w(table(["Model", "Retained unresolved answers", "Episodes with ≥ 1 unresolved answer"],
            [[a, v["unresolved_retained"], v["episodes_with_unresolved"]] for a, v in diag["per_agent"].items()]))
    if diag["merge_groups"]:
        w("\nGroups that would merge under the rule above:\n")
        w(table(["Query", "Agent", "Comparison key", "Submitted (index: id, name)"],
                [[g["query_id"], g["agent"], f"`{g['key']}`",
                  "; ".join(f"{i['submitted_index']}: {json.dumps(i['id'])}, {json.dumps(i['name'])}" for i in g["items"])]
                 for g in diag["merge_groups"]]))
    else:
        w("\nNo retained unresolved answers would merge under the rule above.")
    w("")

    # ------------------------------------------------------------------ (B)
    w("## (B) Descriptive comparisons\n")
    w("### Table 4 — Chance baselines (§17), 10,000 trials\n")
    w("Observed total = number of queries where ≥ 3 (or all 4) agents share an entity in the null's observed "
      "set. \"Above p95\" = observed total > the null's 95th percentile (§17 wording: observed exceeds null).\n")
    for title, key in (("All queries", "aggregate_all_queries"),
                       ("Without SOURCE_NAME_OVERLAP queries", "aggregate_without_source_name_overlap"),
                       ("Without queries that have a technical failure", "aggregate_excluding_technical_failures")):
        agg = nulls[key]
        body = []
        for null, obs in (("N1", "O_N1"), ("N1-H1", "O_H1"), ("N2", "O_N2")):
            for version, label in (("cf3", "≥ 3 agents"), ("cf4", "all 4 agents")):
                c = agg[null][version]
                body.append([null, obs, label, c["query_count"], c["observed_total"], fmt(c["null_mean"], 4),
                             fmt(c["null_median"], 1), fmt(c["null_p95"], 1), fmt(c["p"], 4),
                             "yes" if c["observed_total"] > c["null_p95"] else "no"])
        w(f"**{title}**\n")
        w(table(["Null", "Observed", "Version", "Queries", "Observed total", "Null mean", "Null median",
                 "Null p95", "p", "Above p95"], body))
        w("")

    w("### Table 5 — Co-failure strata (§5.2, §5.3, §7.1)\n")
    w("Cells: number of queries with the flag = 1. Strata come from the evaluation-side manifest; construction "
      "from the per-episode rows.\n")
    construction = {q: data["rows"][(agents[0], q)]["construction"] for q in man}
    for q in man:
        man[q] = {**man[q], "construction": construction[q]}
    short = [name for name, _, _ in CF_METRICS]
    for title, field in (("Ambiguity tag", "ambiguity_tag"), ("Bridge multiplicity", "multiplicity"),
                         ("Relation type", "relation_type"), ("Construction", "construction")):
        for subset_name, subset in (("all queries", cof["queries"]), ("without SOURCE_NAME_OVERLAP", no_overlap)):
            w(f"**By {title.lower()} — {subset_name}**\n")
            w(table([title, "Queries", *short], [[k, n, *c.values()] for k, n, c in strata(subset, man, field)]))
            w("")

    w("### Table 6 — Ordering (§15)\n")
    w("**6a. Explored-bridge ranks** (position in the first R1 list from s containing the bridge; page size 50, "
      "so ranks 1–50 are page 1)\n")
    ranks = bridge_ranks(data["rows"], agents)
    w(table(["Model", "Explored bridges", *[n for n, _, _ in RANK_BINS], "NA", "Median", "Max"],
            [[a, r["n"], *r["bins"].values(), fmt(r["median"], 1), fmt(r["max"])] for a, r in ranks.items()]))
    shared = shared_wrong_answers(cof, data["rows"])
    w("\n**6b. FIRST_SEEN_PAGE of shared wrong answers** (each agent holding a CF3^Q shared entity)\n")
    pages = Counter(str(s["first_seen_page"]) for s in shared)
    w(table(["FIRST_SEEN_PAGE", "Agent-answers"], [[k, v] for k, v in sorted(pages.items())]) if shared
      else "No CF3^Q shared entity.")
    w("\n**6c. List sizes (fan-out) of shared wrong answers**\n")
    if shared:
        w("One row per shared entity; per-agent values are listed in agent order (agent: value).\n")
        grouped: dict[tuple, list] = defaultdict(list)
        for s in shared:
            grouped[(s["query_id"], s["entity_id"])].append(s)
        def per(items, key):
            return "; ".join(f"{s['agent']}: {fmt(s[key])}" for s in items)
        w(table(["Query", "Entity", "Holders", "H1", "Path length", "FIRST_SEEN_PAGE", "List size (first list)",
                 "Largest list size on primary path"],
                [[q, e, len(items), per(items, "h1"), per(items, "path_length"), per(items, "first_seen_page"),
                  per(items, "list_size"), per(items, "primary_path_max_list_size")]
                 for (q, e), items in sorted(grouped.items(), key=lambda kv: (kv[0][0], int(kv[0][1])))]))
    else:
        w("No CF3^Q shared entity.")
    w("")

    w("### D6 quantities (decision_rules.md D6; latest attempts) — outcome not stated here (S29)\n")
    o = d6["O_H1"]
    w(table(["Quantity", "Value"], [
        ["E (technical failures / episodes)", frac(*d6["E"], digits=4)],
        ["H (share of queries where ≥ 3 of 4 agents found R1)", frac(*d6["H"])],
        ["N (queries with CF3^{Q,H1} = 1)", f"{d6['N']} ({', '.join(d6['N_queries']) or '—'})"],
        ["O_H1 vs N1-H1", f"O_H1 = {o['observed']}; null mean {fmt(o['mean'], 4)}; p95 {fmt(o['p95'], 1)}; "
                          f"p = {fmt(o['p'], 4)}; O_H1 > p95: {'yes' if o['exceeds'] else 'no'}"],
        ["P (distinct relation types among the N queries)", f"{d6['P']} ({'; '.join(d6['P_types']) or '—'})"],
    ]))
    w(f"\nFor inspection only: H counting found R1 only in SUCCESS episodes = {frac(*d6['H_success_only'])}.\n")
    w("**Interpretation flags (reported, not gates)**\n")
    w(f"- Ordering flag (O_N1 above N1 p95 and O_N2 not above N2 p95): O_N1 above p95 = "
      f"{'yes' if d6['O_N1']['exceeds'] else 'no'}; O_N2 above p95 = {'yes' if d6['O_N2']['exceeds'] else 'no'} "
      f"→ flag = **{'set' if d6['ordering_flag'] else 'not set'}**.")
    w(f"- Ambiguity flag (> 70% of the N queries in R1/R2/BOTH_AMBIGUOUS types): "
      f"{frac(*d6['ambiguity_share'])} → flag = **{'set' if d6['ambiguity_flag'] else 'not set'}**.\n")

    # ------------------------------------------------------------------ (C)
    w("## (C) Open questions\n")
    w("Questions for the researcher's reading of the case sheets; none is answered by this report.\n")
    w("1. For each case sheet: does the shared path look like a structural feature (shortcut, off-path hub, "
      "large list), a wording issue in the question, or a technical artifact?")
    w("2. Are the shared wrong answers mostly first seen on page 1 (Table 6b), and how does that sit beside "
      "the N2 comparison in Table 4?")
    w("3. How do the co-failure counts compare across ambiguity tags and constructions once the small "
      "stratum sizes in Table 5 are taken into account?")
    w("4. Do the counts with and without SOURCE_NAME_OVERLAP queries (Tables 3, 4, 5) differ in a way that "
      "matters for reading them?")
    w("5. Does the difference between H over all episodes and H over SUCCESS episodes only matter for reading H?")
    w("6. Do the PCF_REL cases coincide with the CF3^{Q,H1} cases, and which wrong-turn labels recur?")
    text = "\n".join(L) + "\n"
    # Scan only the report's own wording: quoted data (question text, entity names) is removed first.
    data_strings = {sh["question"] for sh in sheets} | {sh["start"] for sh in sheets}
    data_strings |= {e["name"] for sh in sheets for e in sh["entities"]}
    data_strings |= {p["path"] for sh in sheets for e in sh["entities"] for p in e["per_agent"] if p["path"]}
    data_strings |= {json.dumps(i["name"]) for g in diag["merge_groups"] for i in g["items"]}
    scanned = text.replace("`cause`", "")  # the §9.5 record field name, not a claim
    for s in sorted(data_strings, key=len, reverse=True):
        scanned = scanned.replace(s, "")
    hits = sorted({m.group(0).lower() for m in CAUSAL.finditer(scanned)})
    if hits:
        raise ValueError(f"causal language in rendered report: {hits}")
    return text


def main(argv=None):
    parser = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    parser.add_argument("--manifest", default="pilot")
    parser.add_argument("--run-id", default="pilot_v1")
    parser.add_argument("--out", default=None, help="default: results/reports/<run_id>_report.md")
    args = parser.parse_args(argv)
    data = load_run(args.run_id, args.manifest)
    out = Path(args.out) if args.out else ROOT / "results/reports" / f"{args.run_id}_report.md"
    if out.exists():
        raise FileExistsError(f"{out} exists; reports are not overwritten (use --out for a new file)")
    out.parent.mkdir(parents=True, exist_ok=True)
    out.write_text(render(data), encoding="utf-8")
    print(f"wrote {out.relative_to(ROOT) if out.is_relative_to(ROOT) else out}")


if __name__ == "__main__":
    main()
