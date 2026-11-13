"""S38 — Final analysis and thesis tables (runbook Part 10, S38, with its DESCRIPTIVE additions).

Usage (from the repository root; reads only files that are in git — no raw episode record, no model, no KG):
    python scripts/38_final_tables.py

Writes results/reports/final/: one Markdown file per table (tableNN_<slug>.md), one CSV per sub-table
(tableNNx_<slug>.csv), README.md (index) and provenance.json (commit, code state, input and output SHA256).

Tables
  1  Dataset (protocol §5.1–§5.3, §7.1, §7.2; S6, S8, S9 outputs).
  2  Agent behaviour (§9.5, §13–§15) — results of record, pilot_v1 + expansion_v1.
  3  Co-failure (§16, §17) — results of record.
  4  Mechanisms by stratum (§14.2 reason codes, §15 early stop, §16.3 path-level co-failure, §21 mechanism of
     the shared feature of the flagged queries) — results of record.
  5  Counterfactual (§21), DESCRIPTIVE: per case, treatment-only (no control, no aggregate ΔCF, no τ_CF;
     decision log 2026-11-12 "Plan after D7", section A4; readings 2026-11-13 "S36").
  6–10  EXPLORATORY (decision log 2026-11-12 "Plan after D7"): B1, B2, B5, B6 with the hand-check, RP.
  11 Follow-up (P1, P2): NOT RUN (decision log 2026-11-13 "B1 — Outcome NOT CLEAN; follow-up not run"); P1, P2
     and the secondary measures quoted verbatim from the decision log, section C3 of "Plan after D7".
  12 EXPLORATORY IC independence check (decision log 2026-11-13 "IC"), added on the researcher's instruction
     of 2026-11-14 (numbered 12 so that the runbook's numbers 6–11 stay as written).

Nothing that an earlier stage stored is recomputed: labels, paths, H1, co-failure flags, null distributions, the
§21 case outcomes and every exploratory result are read as stored. Tables 2–4 count the stored per-episode §15
rows and per-query §16 flags with the same functions as scripts/28_pilot_report.py (imported, unchanged), so
they equal the S30 report. Cross-checks stop the script if the inputs disagree with each other.

Engineering conventions (documented, not protocol):
* Latest attempt per (query, agent) everywhere (§19), via scripts/28_pilot_report.py latest_rows.
* §5.3 split: Table 2 rows are given for All and for each construction and each ambiguity tag. Tables 3–4 are
  split by relation type, ambiguity tag, construction and bridge multiplicity, on all queries and without
  SOURCE_NAME_OVERLAP queries (§19.1). Construction of a query = its relation type's construction in
  results/semantics/relation_mapping.json (checked against every metrics row).
* Ratio metrics: mean of per-episode values over episodes where defined, NA counted (§15); pooled ratio beside it.
* Saturation share is read as stored (results/diagnostics/query_validation.csv); SATURATED = share > θ, θ read
  from data/processed/primary_population.csv (one value required).
* Markdown cells: None → "—" (not applicable), floats with 4 decimals; CSV cells: None → empty, floats with
  6 decimals, lists joined with ";".
* Provenance: commit = HEAD; "tracked clean" = no tracked change; "code committed" = this script and
  scripts/28_pilot_report.py are tracked and unchanged at HEAD. If not, every table is marked PROVISIONAL.
  Each input gets its SHA256 (directories: SHA256 over the sorted "path<TAB>sha256" lines of their files) and
  the last commit that touched it. No timestamp is written, so a rerun at the same commit is byte-identical.
* The wording of Tables 1–5 (titles, headers, notes; not data cells) is scanned for the causal-word list of
  scripts/28_pilot_report.py; a hit is an error. The §9.5 field name `cause` is exempt.
* The output folder may contain only files this script writes; anything else stops the script (nothing is
  deleted).
"""
from __future__ import annotations

import argparse
from collections import Counter, defaultdict
import csv
import hashlib
import importlib.util
import io
import json
from pathlib import Path
import statistics
import subprocess

ROOT = Path(__file__).resolve().parents[1]
SCRIPT = "scripts/38_final_tables.py"
REPORT_SCRIPT = "scripts/28_pilot_report.py"
_spec = importlib.util.spec_from_file_location("pilot_report_s28", ROOT / REPORT_SCRIPT)
R28 = importlib.util.module_from_spec(_spec)
_spec.loader.exec_module(R28)

COMBINED = "pilot_expansion_v1"
VIEWS = (("all_queries", "All queries"), ("without_source_name_overlap", "Without SOURCE_NAME_OVERLAP"))
REASON_ORDER = ("QUERY_NOT_FOUND", "QUESTION_TEXT_MISMATCH", "BRIDGE_NOT_FOUND", "GOLD_BRIDGE_NOT_VALID",
                "GOLD_UNMAPPED", "GOLD_MISSING_FROM_KG", "EXTRA_TARGETS")  # §7.1 order
MULTIPLICITY = ("NO_BRIDGE", "SINGLE_BRIDGE", "MULTI_BRIDGE")
AMBIGUITY = ("NONE", "R1_AMBIGUOUS", "R2_AMBIGUOUS", "BOTH_AMBIGUOUS")
CONSTRUCTIONS = ("BRIDGE", "UNION")
STRATA = (("relation_type", "Relation type"), ("ambiguity_tag", "Ambiguity tag"),
          ("construction", "Construction"), ("multiplicity", "Bridge multiplicity"))
PCF_COLS = ("PCF_SHORTCUT3", "PCF_REL3", "PCF_REL4", "PCF_NODE3", "PCF_NODE4")
RATIO_METRICS = (("Question-valid precision", "question_valid_precision"), ("OFF_QUESTION rate", "off_question_rate"),
                 ("UNRESOLVED rate", "unresolved_rate"), ("UNGROUNDED rate", "ungrounded_rate"),
                 ("Benchmark P", "benchmark_precision"), ("Benchmark R", "benchmark_recall"),
                 ("Benchmark F1", "benchmark_f1"))
S36_CF = ("CF3^Q", "CF4^Q", "CF3^Q grounded", "CF4^Q grounded", "CF3^{Q,H1}", "CF4^{Q,H1}")
S36_PCF = (("pcf_rel3", "PCF_REL3"), ("pcf_rel4", "PCF_REL4"), ("pcf_node3", "PCF_NODE3"),
           ("pcf_node4", "PCF_NODE4"), ("pcf_shortcut3", "PCF_SHORTCUT3"))
DISPLACEMENT = ("VALID_RELATION", "SAME_WRONG_RELATION_OTHER_NEIGHBOR", "OTHER_WRONG", "NO_ANSWER")
ANSWER_CATS = ("VALID_RELATION", "SAME_WRONG_RELATION_OTHER_NEIGHBOR", "OTHER_WRONG")
MARKS = ("VALID", "QUESTIONABLE", "NOT_VALID")
B6_CLEAN_MIN_VALID = 12  # decision log 2026-11-12 "B6 — Hand-check mark definitions"

LOG = "docs/decision_log.md"
PLAN = f'{LOG}, entry 2026-11-12 "S30 — Plan after D7"'
RECORD = ("Results of record: pilot_v1 + expansion_v1, 500 queries × 4 agents, latest attempts (protocol §19); "
          "Gate D7 DESCRIPTIVE (decision log 2026-11-12). Descriptive.")
EXPLORATORY = "EXPLORATORY (protocol §20)"


# ------------------------------------------------------------------------------------------- structures

class Part:
    """One sub-table: written as one CSV and one Markdown section. (Plain class, not a dataclass, so that the
    script can be loaded by file path in tests, as the other stage scripts are.)"""

    def __init__(self, key: str, slug: str, title: str, header: list[str], rows: list[list],
                 notes: list[str] | None = None):
        self.key, self.slug, self.title, self.header, self.rows = key, slug, title, header, rows
        self.notes = list(notes or [])


class Table:
    """One numbered table: one Markdown file holding all its parts."""

    def __init__(self, number: int, slug: str, title: str, status: str, basis: list[str], sources: list[str],
                 parts: list[Part], notes: list[str] | None = None):
        self.number, self.slug, self.title, self.status = number, slug, title, status
        self.basis, self.sources, self.parts = basis, sources, parts
        self.notes = list(notes or [])


# ------------------------------------------------------------------------------------------- formatting

def md_cell(v) -> str:
    if v is None:
        return "—"
    if isinstance(v, bool):
        return "yes" if v else "no"
    if isinstance(v, float):
        return f"{v:.4f}"
    if isinstance(v, (list, tuple)):
        return ", ".join(str(x) for x in v) if v else "—"
    return str(v).replace("|", "\\|").replace("\n", " ")


def csv_cell(v) -> str:
    if v is None:
        return ""
    if isinstance(v, bool):
        return "True" if v else "False"
    if isinstance(v, float):
        return f"{v:.6f}"
    if isinstance(v, (list, tuple)):
        return ";".join(str(x) for x in v)
    return str(v)


def md_table(header: list[str], rows: list[list]) -> str:
    out = ["| " + " | ".join(md_cell(h) for h in header) + " |", "|" + "|".join("---" for _ in header) + "|"]
    for r in rows:
        if len(r) != len(header):
            raise ValueError(f"row has {len(r)} cells, header {len(header)}: {r}")
        out.append("| " + " | ".join(md_cell(c) for c in r) + " |")
    return "\n".join(out)


def csv_text(header: list[str], rows: list[list]) -> str:
    buf = io.StringIO()
    w = csv.writer(buf, lineterminator="\n")
    w.writerow(header)
    for r in rows:
        if len(r) != len(header):
            raise ValueError(f"row has {len(r)} cells, header {len(header)}: {r}")
        w.writerow([csv_cell(c) for c in r])
    return buf.getvalue()


def ratio(num, den):
    return num / den if den else None


def number(text: str):
    """CSV value read from an earlier stage: int, float, bool or string, exactly as written."""
    if text in ("True", "False"):
        return text == "True"
    try:
        return int(text)
    except ValueError:
        pass
    try:
        return float(text)
    except ValueError:
        return text


# ----------------------------------------------------------------------------------------------- loading

def _jsonl(path: Path) -> list[dict]:
    return [json.loads(line) for line in path.read_text(encoding="utf-8").splitlines() if line.strip()]


def _json(path: Path):
    return json.loads(path.read_text(encoding="utf-8"))


def _csv(path: Path) -> list[dict]:
    with path.open(encoding="utf-8", newline="") as fh:
        return list(csv.DictReader(fh))


def load_inputs(root: Path, combined: str = COMBINED) -> dict:
    folder = root / "results/combined" / combined
    spec = _json(folder / "components.json")
    agents = spec["agent_order"]
    cof, nulls = _json(folder / "cofailure.json"), _json(folder / "nulls.json")
    if cof["agent_order"] != agents or nulls["agent_order"] != agents:
        raise ValueError("components.json, cofailure.json and nulls.json list different agent orders")
    mapping = _json(root / "results/semantics/relation_mapping.json")["per_type"]
    manifest, rows, sources = {}, {}, [f"results/combined/{combined}/components.json"]
    sampled: dict[str, set] = {}
    for run_id, comp in sorted(spec["components"].items()):
        man_rel = f"data/processed/manifests/{comp['manifest']}.jsonl"
        met_rel = f"results/runs/{run_id}/analysis/metrics"
        sources += [man_rel, met_rel]
        man = _jsonl(root / man_rel)
        sampled[comp["manifest"]] = {m["query_id"] for m in man}
        for m in man:
            if m["query_id"] in manifest:
                raise ValueError(f"{m['query_id']} is in two component manifests")
            ptype = mapping[m["relation_type"]]
            manifest[m["query_id"]] = {**m, "construction": ptype["construction"], "run_id": run_id}
        comp_rows = R28.latest_rows(root / met_rel, agents)
        expected = {(a, m["query_id"]) for a in agents for m in man}
        if set(comp_rows) != expected:
            raise ValueError(f"{run_id}: metrics rows do not equal manifest × agents "
                             f"(missing {sorted(expected - set(comp_rows))[:5]}, extra {sorted(set(comp_rows) - expected)[:5]})")
        rows.update(comp_rows)
    for (agent, qid), r in rows.items():
        if r["construction"] != manifest[qid]["construction"]:
            raise ValueError(f"{qid}/{agent}: metrics construction {r['construction']} != relation mapping "
                             f"{manifest[qid]['construction']}")
    return {
        "agents": agents, "cofailure": cof, "nulls": nulls, "manifest": manifest, "rows": rows,
        "sampled": sampled, "mapping": mapping,
        "validation": _csv(root / "results/diagnostics/query_validation.csv"),
        "primary": _csv(root / "data/processed/primary_population.csv"),
        "primary_summary": _json(root / "data/processed/primary_population_summary.json"),
        "biohopr_types": _csv(root / "results/diagnostics/biohopr/relation_types.csv"),
        "candidates": _csv(root / "results/interventions/candidates.csv"),
        "s36": _json(root / "results/interventions/s36/s36.json"),
        "b1_table": _csv(root / "results/exploratory/b1/b1_table.csv"),
        "b1": _json(root / "results/exploratory/b1/b1.json"),
        "b2": _json(root / "results/exploratory/b2/b2.json"),
        "b5_table": _csv(root / "results/exploratory/b5/b5_table.csv"),
        "b5": _json(root / "results/exploratory/b5/b5.json"),
        "b6_table": _csv(root / "results/exploratory/b6/b6_table.csv"),
        "b6": _json(root / "results/exploratory/b6/b6.json"),
        "handcheck": _csv(root / "results/exploratory/b6_handcheck.csv"),
        "rp": _json(root / "results/exploratory/rp/rp.json"),
        "ic": _json(root / "results/exploratory/ic/ic.json"),
        "decision_log": (root / LOG).read_text(encoding="utf-8"),
        "run_sources": sources,
        "cofailure_path": f"results/combined/{combined}/cofailure.json",
        "nulls_path": f"results/combined/{combined}/nulls.json",
    }


# -------------------------------------------------------------------------------------------- cross-checks

def _cf_by_query(cof: dict) -> dict[str, dict[str, int]]:
    return {q["query_id"]: {name: R28.cf_flag(q, b, k) for name, b, k in R28.CF_METRICS} for q in cof["queries"]}


def cross_check(data: dict, cofailure_sha256: str) -> list[str]:
    """Every check that the inputs agree with each other. Raises on the first disagreement; returns what was
    checked (written to provenance.json)."""
    cof = data["cofailure"]
    R28.check_totals(cof)
    done = ["cofailure.json per-query flags add up to its stored totals (both views)"]
    man = data["manifest"]
    if sorted(man) != sorted(q["query_id"] for q in cof["queries"]):
        raise ValueError("manifests and cofailure.json list different queries")
    for q in cof["queries"]:
        m = man[q["query_id"]]
        if (q["relation_type"], q["ambiguity_tag"]) != (m["relation_type"], m["ambiguity_tag"]):
            raise ValueError(f"{q['query_id']}: relation type / ambiguity tag differ between manifest and cofailure.json")
    done.append("manifest relation type and ambiguity tag equal cofailure.json for all 500 queries")
    for name in ("b1", "b2", "b5", "b6"):
        got = data[name]["provenance"]["inputs"]["cofailure"]["sha256"]
        if got != cofailure_sha256:
            raise ValueError(f"{name}: computed on cofailure.json {got}, current file is {cofailure_sha256}")
    if data["rp"]["provenance"]["inputs"]["original_cofailure"]["sha256"] != cofailure_sha256:
        raise ValueError("RP: computed on a different cofailure.json")
    if data["ic"]["provenance"]["cofailure"]["sha256"] != cofailure_sha256:
        raise ValueError("IC: computed on a different cofailure.json")
    done.append("B1, B2, B5, B6, RP and IC were computed on the current cofailure.json (SHA256)")
    totals = {v: cof["totals_all_queries" if v == "all_queries" else "totals_without_source_name_overlap"]
              for v, _ in VIEWS}
    for view, _ in VIEWS:
        strict = data["b2"]["tables"][view]["cofailure"]["strict"]
        for name in ("CF3^Q", "CF4^Q", "CF3^{Q,H1}", "CF4^{Q,H1}"):
            if strict[name] != totals[view][R28.TOTAL_KEYS[name]]:
                raise ValueError(f"B2 strict {name} ({view}) != cofailure.json")
        both = [r for r in data["b5"]["tables"][view] if r["subset"] == "both" and r["group"] == "total"]
        if len(both) != 1 or any(both[0][n] != totals[view][R28.TOTAL_KEYS[n]] for n in ("CF3^Q", "CF4^Q", "CF3^{Q,H1}")):
            raise ValueError(f"B5 both/total ({view}) != cofailure.json")
        b6_total = [r for r in data["b6_table"] if r["view"] == view and r["relation_type"] == "total"]
        if len(b6_total) != 1 or int(b6_total[0]["CF3^BH"]) != totals[view]["benchmark_cf3"] \
                or int(b6_total[0]["CF3^Q"]) != totals[view]["question_cf3"]:
            raise ValueError(f"B6 total ({view}) != cofailure.json")
    done.append("B2 strict, B5 both/total and B6 total equal the cofailure.json totals (both views)")
    flags = _cf_by_query(cof)
    for q in data["rp"]["queries"]:
        f = flags[q["query_id"]]
        if (q["original_cf3_q"], q["original_cf4_q"], q["original_cf3_q_h1"]) != \
                (f["CF3^Q"], f["CF4^Q"], f["CF3^{Q,H1}"]):
            raise ValueError(f"RP {q['query_id']}: original flags != cofailure.json")
    for view, _ in VIEWS:
        for q in data["ic"][view]["per_query"]:
            if q["CF3_Q_H1"] != flags[q["query_id"]]["CF3^{Q,H1}"]:
                raise ValueError(f"IC {q['query_id']}: CF3^{{Q,H1}} != cofailure.json")
    for case in data["s36"]["cases"]:
        f = flags[case["query_id"]]
        for name in S36_CF:
            if case["cf"][name]["before"] != f[name]:
                raise ValueError(f"S36 {case['query_id']}: before {name} != cofailure.json")
        for key, name in S36_PCF:
            if case["pcf"][key]["before"] != f[name]:
                raise ValueError(f"S36 {case['query_id']}: before {name} != cofailure.json")
    done.append("RP original flags, IC CF3^{Q,H1} and S36 'before' flags equal cofailure.json per query")
    flagged = {q["query_id"] for q in cof["queries"] if q["hop1_clean"]["cf3"] or q["pcf_rel3"] or q["pcf_node3"]
               or q["pcf_shortcut3"]}
    if {c["query_id"] for c in data["candidates"]} != flagged:
        raise ValueError("S31 candidates.csv does not list exactly the queries meeting the flag part of §21")
    done.append("S31 candidates.csv lists exactly the queries meeting the flag part of the §21 candidate rule")
    return done


# ------------------------------------------------------------------------------------------ table 1: dataset

def build_table1(validation: list[dict], primary: list[dict], primary_summary: dict, mapping: dict,
                 biohopr_types: list[dict], sampled: dict[str, set]) -> Table:
    thetas = {r["theta"] for r in primary}
    if len(thetas) != 1:
        raise ValueError(f"primary_population.csv has {len(thetas)} θ values: {sorted(thetas)}")
    theta = float(thetas.pop())
    primary_ids = {r["query_id"] for r in primary}
    pilot, expansion = sampled.get("pilot", set()), sampled.get("expansion", set())
    if not (pilot | expansion) <= primary_ids:
        raise ValueError("a sampled query is not in the primary population")
    confirmation = primary_summary["mapping_confirmation"]
    bh_rows = {r["relation_hop2"]: int(r["n_rows"]) for r in biohopr_types}
    if set(bh_rows) != set(mapping):
        raise ValueError("BioHopR relation types and relation_mapping.json types differ")

    v = []
    for r in validation:
        if r["status"] not in ("CONSISTENT", "INCONSISTENT"):
            raise ValueError(f"{r['query_id']}: status {r['status']!r}")
        share = float(r["saturation_share"])
        v.append({**r, "share": share, "saturated": share > theta, "leaky": number(r["leaky_question"]) is True,
                  "consistent": r["status"] == "CONSISTENT"})
    computed_primary = {r["query_id"] for r in v if r["consistent"] and not r["saturated"] and not r["leaky"]
                        and mapping[r["relation_type"]]["d1_status"] == "PASS"
                        and confirmation.get(r["relation_type"]) in ("CONFIRMED", "UNCONFIRMABLE")}
    if computed_primary != primary_ids:
        raise ValueError(f"§7.2 recount of the primary population ({len(computed_primary)}) != "
                         f"primary_population.csv ({len(primary_ids)})")

    def counts(sel):
        return [len(sel), sum(r["consistent"] for r in sel), sum(not r["consistent"] for r in sel),
                sum(r["leaky"] for r in sel), sum(r["saturated"] for r in sel),
                sum(r["query_id"] in primary_ids for r in sel)]

    by_type = defaultdict(list)
    for r in v:
        by_type[r["relation_type"]].append(r)
    rows_a, tot = [], Counter()
    for t in sorted(mapping):
        p = mapping[t]
        sel = by_type.get(t, [])
        tags = {r["ambiguity_tag"] for r in sel}
        if len(tags) > 1:
            raise ValueError(f"{t}: more than one ambiguity tag {sorted(tags)}")
        prim = [r for r in sel if r["query_id"] in primary_ids]
        mult = Counter(r["bridge_multiplicity"] for r in prim)
        if p["d1_status"] == "PASS":
            c = counts(sel)
            vals = c + [mult.get("SINGLE_BRIDGE", 0), mult.get("MULTI_BRIDGE", 0),
                        sum(r["query_id"] in pilot for r in sel), sum(r["query_id"] in expansion for r in sel)]
            for i, x in enumerate(vals):
                tot[i] += x
        else:
            if sel:
                raise ValueError(f"{t}: D1 {p['d1_status']} but has validated queries")
            vals = [None] * 10
        tot["rows"] += bh_rows[t]
        rows_a.append([t, bh_rows[t], p["d1_status"], p.get("construction"), p.get("R1"), p.get("R2"),
                       tags.pop() if tags else None, *vals])
    rows_a.append(["Total", tot["rows"], f"{sum(p['d1_status'] == 'PASS' for p in mapping.values())} PASS / "
                   f"{sum(p['d1_status'] != 'PASS' for p in mapping.values())} FAIL", None, None, None, None,
                   *[tot[i] for i in range(10)]])
    part_a = Part("a", "relation_types", "Relation types (§5.1–§5.3, Gate D1) and query counts (§7.1, §7.2, §8)",
                  ["Relation type", "BioHopR rows", "Gate D1", "Construction", "R1", "R2", "Ambiguity tag",
                   "Queries validated", "CONSISTENT", "INCONSISTENT", "LEAKY_QUESTION", "SATURATED",
                   "Primary population", "Primary SINGLE_BRIDGE", "Primary MULTI_BRIDGE", "Pilot", "Expansion"],
                  rows_a, ["Relation types that failed Gate D1 were excluded at S6 and never validated (—). "
                           "LEAKY_QUESTION and SATURATED are counted over all validated queries, whatever their status."])

    rows_b = []
    for code in REASON_ORDER:
        rows_b.append([code, sum(r["primary_reason"] == code for r in v),
                       sum(number(r[code]) is True for r in v), sum(r[code] == "NA" for r in v),
                       sorted({r["relation_type"] for r in v if number(r[code]) is True})])
    rows_b.append(["Queries INCONSISTENT", sum(not r["consistent"] for r in v), None, None,
                   sorted({r["relation_type"] for r in v if not r["consistent"]})])
    part_b = Part("b", "inconsistent_reasons", "INCONSISTENT queries by reason code (§7.1)",
                  ["Reason code", "Primary reason (queries)", "Recorded (queries)", "Recorded as NA",
                   "Relation types where recorded"], rows_b,
                  ["Primary reason = the first applicable code in the §7.1 order; every applicable code is recorded."])

    def group_rows(key, values):
        out = []
        for val in values:
            sel = [r for r in v if r[key] == val]
            out.append([val, *counts(sel)[:3], sum(r["query_id"] in primary_ids for r in sel),
                        sum(r["query_id"] in pilot for r in sel), sum(r["query_id"] in expansion for r in sel)])
        return out

    head = ["Queries validated", "CONSISTENT", "INCONSISTENT", "Primary population", "Pilot", "Expansion"]
    part_c = Part("c", "bridge_multiplicity", "Bridge multiplicity (§7.1)", ["Bridge multiplicity", *head],
                  group_rows("bridge_multiplicity", MULTIPLICITY))
    rows_d = []
    for tag, row in zip(AMBIGUITY, group_rows("ambiguity_tag", AMBIGUITY)):
        types = sorted(t for t in by_type if by_type[t][0]["ambiguity_tag"] == tag)
        rows_d.append([tag, len(types), types, *row[1:]])
    part_d = Part("d", "ambiguity_tags", "Relation-ambiguity tags (§5.2), D1-PASS relation types",
                  ["Ambiguity tag", "Relation types", "Relation type names", *head], rows_d)
    rows_e = []
    for con, row in zip(CONSTRUCTIONS, group_rows("construction", CONSTRUCTIONS)):
        types = sorted(t for t in by_type if by_type[t][0]["construction"] == con)
        rows_e.append([con, len(types), types, *row[1:]])
    part_e = Part("e", "construction", "Answer construction (§5.3), D1-PASS relation types",
                  ["Construction", "Relation types", "Relation type names", *head], rows_e)

    rows_f = []
    for t in sorted(by_type):
        sel = by_type[t]
        tt = {(r["target_type"], r["target_type_nodes"]) for r in sel}
        if len(tt) != 1:
            raise ValueError(f"{t}: more than one target type / node count")
        target, nodes = tt.pop()
        shares = [r["share"] for r in sel]
        rows_f.append([t, target, int(nodes), len(sel), min(shares), statistics.median(shares), max(shares),
                       sum(r["saturated"] for r in sel)])
    shares = [r["share"] for r in v]
    rows_f.append(["All validated queries", None, None, len(v), min(shares), statistics.median(shares),
                   max(shares), sum(r["saturated"] for r in v)])
    part_f = Part("f", "saturation", f"Saturation share = |T_q| / PrimeKG nodes of Type_T (§7.1); θ = {theta}",
                  ["Relation type", "Type_T", "Type_T nodes", "Queries validated", "Share min", "Share median",
                   "Share max", f"SATURATED (share > {theta})"], rows_f,
                  ["Saturation share is read as stored (results/diagnostics/query_validation.csv). Shares are "
                   "small numbers: the Markdown shows 4 decimals, the CSV 6."])

    excluded = [r for r in v if r["query_id"] not in primary_ids]
    unconfirmed = [r for r in v if confirmation.get(r["relation_type"]) not in ("CONFIRMED", "UNCONFIRMABLE")]
    rows_g = [["INCONSISTENT", sum(not r["consistent"] for r in v)],
              ["LEAKY_QUESTION", sum(r["leaky"] for r in v)],
              ["SATURATED", sum(r["saturated"] for r in v)],
              ["Relation type neither CONFIRMED nor UNCONFIRMABLE in Gate D2 step 1", len(unconfirmed)],
              ["Excluded (any of the above; counts above may overlap)", len(excluded)],
              ["Primary population", len(primary_ids)],
              ["Sampled: pilot", len(pilot)], ["Sampled: expansion", len(expansion)]]
    part_g = Part("g", "inclusion", "Primary population (§7.2) and the 500 sampled queries (§8)",
                  ["Item", "Queries"], rows_g,
                  [f"Validated queries: {len(v)} of the D1-PASS relation types. The recount of the §7.2 rule from "
                   "the validation file equals data/processed/primary_population.csv (checked)."])
    return Table(1, "dataset", "Dataset", "Dataset description (S6, S8, S9 outputs). Descriptive.",
                 ["protocol §5.1–§5.3, §7.1, §7.2, §8"],
                 ["results/semantics/relation_mapping.json", "results/diagnostics/biohopr/relation_types.csv",
                  "results/diagnostics/query_validation.csv", "data/processed/primary_population.csv",
                  "data/processed/primary_population_summary.json"],
                 [part_a, part_b, part_c, part_d, part_e, part_f, part_g])


# -------------------------------------------------------------------------------- table 2: agent behaviour

def splits(manifest: dict) -> list[tuple[str, callable]]:
    out = [("All", lambda q: True)]
    out += [(f"construction = {c}", lambda q, c=c: manifest[q]["construction"] == c) for c in CONSTRUCTIONS]
    out += [(f"ambiguity tag = {t}", lambda q, t=t: manifest[q]["ambiguity_tag"] == t) for t in AMBIGUITY]
    return out


def build_table2(rows: dict, agents: list[str], manifest: dict, sources: list[str]) -> Table:
    pa, pb, pc, pd, pe, pf = ([] for _ in range(6))
    e_note = None
    for name, pred in splits(manifest):
        sub = {k: r for k, r in rows.items() if pred(k[1])}
        if not sub:
            continue
        tech = R28.technical(sub, agents)
        pm = R28.per_model(sub, agents)
        ranks = R28.bridge_ranks(sub, agents)
        if name == "All":
            e_note = (tech["technical_failures"], tech["episodes"])
        for a in agents:
            t = tech["per_agent"][a]
            pa.append([name, a, t["episodes"], *[t[s] for s in R28.STATUSES], t["technical"],
                       [f"{k}: {v}" for k, v in t["error_causes"].items()]])
        pa.append([name, "All agents", tech["episodes"],
                   *[sum(t[s] for t in tech["per_agent"].values()) for s in R28.STATUSES],
                   tech["technical_failures"], None])
        for a in agents + ["All agents"]:
            if a == "All agents":
                h1 = {k: sum(pm[x]["hop1"][k] for x in agents) for k in R28.HOP1}
                la = {k: sum(pm[x]["label_a"][k] for x in agents) for k in R28.LABEL_A}
                lb = {k: sum(pm[x]["label_b"][k] for x in agents) for k in R28.LABEL_B}
                eps, succ, answers = (sum(pm[x][k] for x in agents) for k in ("episodes", "success", "answers"))
            else:
                h1, la, lb = pm[a]["hop1"], pm[a]["label_a"], pm[a]["label_b"]
                eps, succ, answers = pm[a]["episodes"], pm[a]["success"], pm[a]["answers"]
            pb.append([name, a, eps, *h1.values(), h1["H1_CLEAN"] + h1["H1_MIXED"]])
            pd.append([name, a, succ, answers, *la.values()])
            pe.append([name, a, succ, *lb.values()])
        for a in agents + ["All"]:
            rk = ranks[a]
            pc.append([name, "All agents" if a == "All" else a, rk["n"], *rk["bins"].values(), rk["median"], rk["max"]])
        for a in agents:
            for label, key in RATIO_METRICS:
                r = pm[a]["ratios"][key]
                pf.append([name, a, label, r["mean"], r["defined"], r["na"], r["pooled_num"], r["pooled_den"],
                           ratio(r["pooled_num"], r["pooled_den"])])
    bins = [b for b, _, _ in R28.RANK_BINS] + ["NA"]
    parts = [
        Part("a", "episode_status", "Episode status (§9.5), all episodes",
             ["Split", "Agent", "Episodes", *R28.STATUSES, "Technical failures", "ERROR by §9.5 `cause` field"], pa,
             [f"E = technical failures / episodes = {e_note[0]}/{e_note[1]} = {e_note[0] / e_note[1]:.4f} (all queries)."]),
        Part("b", "hop1_status", "Hop-1 status per agent (§14.3), every episode whatever its status",
             ["Split", "Agent", "Episodes", *R28.HOP1, "Found R1 (CLEAN + MIXED)"], pb),
        Part("c", "bridge_ranks", "Explored-bridge ranks (§15): position in the first R1 list from s that contained "
             "the bridge (page size 50, so ranks 1–50 are page 1)",
             ["Split", "Agent", "Explored bridges", *bins, "Median", "Max"], pc),
        Part("d", "label_a", "Label A (§13), retained answers of SUCCESS episodes",
             ["Split", "Agent", "SUCCESS episodes", "Answers", *R28.LABEL_A], pd),
        Part("e", "label_b", "Label B (§14.1), retained answers of SUCCESS episodes",
             ["Split", "Agent", "SUCCESS episodes", *R28.LABEL_B], pe),
        Part("f", "ratio_metrics", "Ratio metrics including benchmark F1 (§15)",
             ["Split", "Agent", "Metric", "Mean of per-episode values", "Defined episodes", "NA episodes",
              "Pooled numerator", "Pooled denominator", "Pooled ratio"], pf,
             ["Mean over episodes where the value is defined; NA = undefined (division by zero), excluded and "
              "counted (§15). Benchmark F1 pooled = 2·Σcorrect / (Σresolved + Σ|A*_q|)."]),
    ]
    return Table(2, "agent_behaviour", "Agent behaviour", RECORD,
                 ["protocol §9.5, §13, §14.1, §14.3, §15; split by construction and ambiguity tag (§5.3)"],
                 sources, parts,
                 ["Split rows: All; each construction (§5.3); each ambiguity tag (§5.2). A split's rows cover the "
                  "queries of that split only."])


# ------------------------------------------------------------------------------------ table 3: co-failure

def _views(cof: dict) -> list[tuple[str, list[dict]]]:
    overlap = set(cof["source_name_overlap_queries"])
    return [("All queries", cof["queries"]),
            ("Without SOURCE_NAME_OVERLAP", [q for q in cof["queries"] if q["query_id"] not in overlap])]


def strata_rows(queries: list[dict], manifest: dict, cols: list[str]) -> list[list]:
    out = []
    for key, label in STRATA:
        groups = defaultdict(list)
        for q in queries:
            groups[manifest[q["query_id"]][key]].append(q)
        for val in sorted(groups):
            c = R28.cf_counts(groups[val])
            out.append([label, val, len(groups[val]), *[c[m] for m in cols]])
    return out


def build_table3(cof: dict, nulls: dict, manifest: dict, sources: list[str]) -> Table:
    (v1, all_q), (v2, no_q) = _views(cof)
    ca, cn = R28.cf_counts(all_q), R28.cf_counts(no_q)
    overlap = set(cof["source_name_overlap_queries"])
    rows_a = [[name, ca[name], len(all_q), ratio(ca[name], len(all_q)), cn[name], len(no_q), ratio(cn[name], len(no_q))]
              for name, _, _ in R28.CF_METRICS]
    rows_b = []
    for name, b, k in R28.CF_METRICS:
        ids = sorted(q["query_id"] for q in all_q if R28.cf_flag(q, b, k))
        rows_b.append([name, len(ids), ids, sorted(set(ids) & overlap)])
    rows_c = []
    for view, key in ((v1, "pairwise_all_queries"), (v2, "pairwise_without_source_name_overlap")):
        for p in cof[key]:
            rows_c.append([view, p["agent_i"], p["agent_j"], p["numerator"], p["denominator"],
                           ratio(p["numerator"], p["denominator"])])
    rows_d = []
    for view, key in (("All queries", "aggregate_all_queries"),
                      ("Without SOURCE_NAME_OVERLAP", "aggregate_without_source_name_overlap"),
                      ("Excluding queries with a technical failure", "aggregate_excluding_technical_failures")):
        for null, obs in (("N1", "O_N1"), ("N1-H1", "O_H1"), ("N2", "O_N2")):
            for version, vkey in (("≥ 3 agents", "cf3"), ("all 4 agents", "cf4")):
                c = nulls[key][null][vkey]
                above = c["observed_total"] > c["null_p95"]
                if above != c["observed_exceeds_null"]:
                    raise ValueError(f"nulls.json {key}/{null}/{vkey}: stored observed_exceeds_null disagrees")
                rows_d.append([view, null, obs, version, c["query_count"], c["observed_total"], c["null_mean"],
                               c["null_median"], c["null_p95"], c["p"], above])
    metrics = [name for name, _, _ in R28.CF_METRICS]
    rows_e = []
    for view, qs in _views(cof):
        rows_e += [[view, *r] for r in strata_rows(qs, manifest, metrics)]
    parts = [
        Part("a", "cofailure_totals", "Co-failure (§16.1–§16.3): queries with the flag = 1",
             ["Metric", "All: queries flagged", "All: queries", "All: share",
              "Without SNO: queries flagged", "Without SNO: queries", "Without SNO: share"], rows_a,
             [f"SOURCE_NAME_OVERLAP (SNO) queries (§19.1): {', '.join(sorted(overlap))}. Gates use all queries."]),
        Part("b", "flagged_queries", "Queries with each flag = 1 (all queries)",
             ["Metric", "Queries flagged", "Query IDs", "Of which SOURCE_NAME_OVERLAP"], rows_b),
        Part("c", "pairwise_agreement", "Pairwise error agreement (§16.4): among queries where both agents have a "
             "non-empty W (OFF_QUESTION set), the share where the two sets intersect",
             ["View", "Agent i", "Agent j", "Intersecting", "Both non-empty", "Agreement"], rows_c,
             ["Agreement is NA (—) when no query has both sets non-empty; the denominator is always shown."]),
        Part("d", "chance_baselines", f"Chance baselines (§17), {nulls['trials']} trials",
             ["View", "Null", "Observed", "Version", "Queries", "Observed total", "Null mean", "Null median",
              "Null p95", "p", "Observed above p95"], rows_d,
             ["\"Observed exceeds null\" = observed total above the null's 95th percentile (§17). The gate "
              "comparison (D6, D7) is O_H1 against N1-H1. p = (1 + #{trials with null total ≥ observed}) / "
              "(1 + trials)."]),
        Part("e", "cofailure_by_stratum", "Co-failure by stratum (§5.2, §5.3, §7.1): queries with the flag = 1",
             ["View", "Stratum", "Value", "Queries", *metrics], rows_e),
    ]
    return Table(3, "cofailure", "Co-failure", RECORD, ["protocol §16, §17, §19.1; strata §5.2, §5.3, §7.1"],
                 sources + ["results/combined/pilot_expansion_v1/cofailure.json",
                            "results/combined/pilot_expansion_v1/nulls.json"], parts)


# ------------------------------------------------------------------------------------ table 4: mechanisms

def build_table4(rows: dict, agents: list[str], cof: dict, manifest: dict, candidates: list[dict],
                 sources: list[str]) -> Table:
    overlap = set(cof["source_name_overlap_queries"])

    def mech(sub: dict) -> list:
        succ = [r for r in sub.values() if r["episode_status"] == "SUCCESS"]
        prim = Counter()
        for r in succ:
            prim.update(r["primary_reason_counts"])
        early = [r["early_stop"] for r in sub.values() if r["early_stop"] is not None]
        return [len(succ), sum(r["label_b_counts"]["PATH_INVALID"] for r in succ),
                *[prim.get(k, 0) for k in R28.REASONS], sum(early), len(early), ratio(sum(early), len(early))]

    rows_a = []
    for view, keep in (("All queries", lambda q: True), ("Without SOURCE_NAME_OVERLAP", lambda q: q not in overlap)):
        base = {k: r for k, r in rows.items() if keep(k[1])}
        rows_a.append([view, "All", "All", len({q for _, q in base}), *mech(base)])
        for key, label in STRATA:
            for val in sorted({manifest[q][key] for _, q in base}):
                sub = {k: r for k, r in base.items() if manifest[k[1]][key] == val}
                rows_a.append([view, label, val, len({q for _, q in sub}), *mech(sub)])
    rows_b = []
    pm = R28.per_model(rows, agents)
    for a in agents:
        es, es_n, es_na = pm[a]["early_stop"]
        rows_b.append([a, pm[a]["label_b"]["PATH_INVALID"],
                       *[x for k in R28.REASONS for x in (pm[a]["primary_reasons"][k], pm[a]["all_path_reasons"][k])],
                       es, es_n, es_na, ratio(es, es_n)])
    rows_c = []
    for view, qs in _views(cof):
        rows_c += [[view, *r] for r in strata_rows(qs, manifest, list(PCF_COLS))]
    rows_d = []
    for c in sorted(candidates, key=lambda c: c["query_id"]):
        rows_d.append([c["query_id"], c["relation_type"], c["ambiguity_tag"], number(c["source_name_overlap"]),
                       number(c["cf3_q"]), number(c["cf3_h1"]), c["mechanism"], c["feature_u"], c["feature_u_name"],
                       c["feature_r"], number(c["feature_step"]), number(c["feature_holders"]),
                       c["feature_agents"].split(";"), number(c["valid_route_after_block"]),
                       number(c["has_matched_control"])])
    mech_counts = Counter(c["mechanism"] for c in candidates)
    reason_head = [x for k in R28.REASONS for x in (f"{k} (primary)", f"{k} (all paths ≤ 3)")]
    parts = [
        Part("a", "reason_codes_by_stratum", "Answer-level path reason codes (§14.2, primary path) and early stop "
             "(§15) by stratum, all agents pooled",
             ["View", "Stratum", "Value", "Queries", "SUCCESS episodes", "PATH_INVALID answers", *R28.REASONS,
              "Early-stop episodes", "Early stop defined", "Early-stop share"], rows_a,
             ["Reason codes are counted over PATH_INVALID answers of SUCCESS episodes (primary path, §14.2). "
              "An answer can carry more than one code (for example WRONG_TARGET_TYPE and WRONG_HOP_COUNT), so the "
              "code columns can add up to more than the PATH_INVALID answers. WRONG_RELATION is reported as its two "
              "§14.2 codes, WRONG_RELATION_HOP1 and WRONG_RELATION_HOP2. Early stop is defined for SUCCESS episodes "
              "only (§15)."]),
        Part("b", "reason_codes_by_agent", "Path reason codes per agent (§14.2: primary path and union over simple "
             "paths ≤ 3) and early stop (§15), all queries",
             ["Agent", "PATH_INVALID answers", *reason_head, "Early-stop episodes", "Early stop defined",
              "Early stop NA", "Early-stop share"], rows_b),
        Part("c", "path_cofailure_by_stratum", "Path-level co-failure by stratum (§16.3): shortcut, wrong relation "
             "(REL) and off-path node (NODE); queries with the flag = 1",
             ["View", "Stratum", "Value", "Queries", *PCF_COLS], rows_c,
             ["Off-path node is defined by the protocol only at the path co-failure level (§16.3 PCF_NODE: an "
              "intermediate node not in B_q ∪ T_q on the primary path of an OFF_QUESTION answer for ≥ 3 / all 4 "
              "agents). No answer-level off-path-node count is defined, so none is computed."]),
        Part("d", "flagged_query_mechanisms", "§21 mechanism of the shared feature, queries meeting the flag part of "
             "the §21 candidate rule (S31, results/interventions/candidates.csv)",
             ["Query", "Relation type", "Ambiguity tag", "SOURCE_NAME_OVERLAP", "CF3^Q", "CF3^{Q,H1}", "Mechanism",
              "u", "u name", "r", "Step", "Holders", "Holder agents", "Valid route after block",
              "Matched control"], rows_d,
             ["Mechanism counts: " + ", ".join(f"{k} {v}" for k, v in sorted(mech_counts.items())) +
              f" (of {len(candidates)} queries). C = 0: no query has a matched control (decision log 2026-11-11)."]),
    ]
    return Table(4, "mechanisms", "Mechanisms", RECORD,
                 ["protocol §14.2, §15, §16.3, §21; strata §5.2, §5.3, §7.1"],
                 sources + ["results/combined/pilot_expansion_v1/cofailure.json", "results/interventions/candidates.csv"],
                 parts)


# ------------------------------------------------------------------------------- table 5: counterfactual

def build_table5(s36: dict) -> Table:
    if s36.get("status") != "DESCRIPTIVE":
        raise ValueError(f"s36.json status {s36.get('status')!r}, expected DESCRIPTIVE")
    no_control = "no control (C = 0)"
    rows_a, rows_b, rows_c, rows_d = [], [], [], []
    for c in sorted(s36["cases"], key=lambda c: c["query_id"]):
        hidden = f"`{c['r']}` at {c['u']} (step {c['step']})"
        for name in S36_CF:
            rows_a.append([c["query_id"], c["mechanism"], hidden, name, c["cf"][name]["before"],
                           c["cf"][name]["after"], no_control])
        for key, name in S36_PCF:
            rows_a.append([c["query_id"], c["mechanism"], hidden, name, c["pcf"][key]["before"],
                           c["pcf"][key]["after"], no_control])
        after, ref = c["after"], c["reference_repeat"]
        nb, na = c["no_answer"]["before"], c["no_answer"]["after"]
        rows_b.append([c["query_id"], c["holders"], after["recovered"], after["denominator"],
                       ratio(after["recovered"], after["denominator"]), ref["recovered"], ref["denominator"],
                       nb["no_answer"], nb["success_episodes"], nb["rate"], na["no_answer"], na["success_episodes"],
                       na["rate"], [f"{k}: {v}" for k, v in sorted(after["technical_failures"].items())],
                       [f"{k}: {v}" for k, v in sorted(ref["technical_failures"].items())], no_control])
        for h in c["holders"]:
            before = c["before_holder_answers"][h]
            a, r = after["per_holder"][h], ref["per_holder"][h]
            def counts(x):
                return [x["answer_counts"][k] if x["answer_counts"] else None for k in ANSWER_CATS]
            rows_c.append([c["query_id"], h, *[before[k] for k in ANSWER_CATS], a["status"], a["category"],
                           *counts(a), r["status"], r["category"], *counts(r)])
        rows_d.append([c["query_id"], c["mechanism"], *[after["displacement"][k] for k in DISPLACEMENT],
                       len(after["technical_failures"]), c["same_wrong_possible"]])
    rc = s36["run_commits"]
    commits = "; ".join(f"{col}: " + ", ".join(f"{run} @ {sha}" for run, sha in sorted(v.items()))
                        for col, v in sorted(rc.items()))
    parts = [
        Part("a", "cofailure_before_after", "CF3/CF4 and PCF per case: before / after treatment / after control",
             ["Case", "Mechanism", "Hidden (surgery)", "Metric", "Before", "After treatment", "After control"], rows_a,
             ["Before = pilot_v1/expansion_v1 (results of record); after treatment = intervention_v1. No matched "
              "control exists for any case (C = 0, §21: treatment-only exploratory)."]),
        Part("b", "recovery_no_answer", "Recovery and no-answer change per case",
             ["Case", "Holders", "Recovered after", "Holders with SUCCESS after", "Recovery share after",
              "Recovered, repeat_v1 reference", "Holders with SUCCESS, repeat_v1", "No-answer before",
              "SUCCESS episodes before", "No-answer rate before", "No-answer after", "SUCCESS episodes after",
              "No-answer rate after", "Technical failures after (holders)", "Technical failures, repeat_v1 (holders)",
              "Control"], rows_b,
             ["Recovery = holders (SUCCESS after-episodes only) with ≥ 1 resolved answer, all question-valid. "
              "No-answer rate = SUCCESS episodes with 0 resolved answers / SUCCESS episodes, all 4 agents. "
              "repeat_v1 is a descriptive reference for run-to-run variation; it never replaces 'before'."]),
        Part("c", "displacement_per_holder", "Displacement per holder (one category = result of record; answer counts "
             "descriptive)",
             ["Case", "Holder", "Before: VALID_RELATION answers", "Before: SAME_WRONG_RELATION_OTHER_NEIGHBOR answers",
              "Before: OTHER_WRONG answers", "After: status", "After: category", "After: VALID_RELATION answers",
              "After: SAME_WRONG_RELATION_OTHER_NEIGHBOR answers", "After: OTHER_WRONG answers", "repeat_v1: status",
              "repeat_v1: category", "repeat_v1: VALID_RELATION answers",
              "repeat_v1: SAME_WRONG_RELATION_OTHER_NEIGHBOR answers", "repeat_v1: OTHER_WRONG answers"], rows_c,
             ["Category order (decision log 2026-11-13, S36 readings, item 3): NO_ANSWER, "
              "SAME_WRONG_RELATION_OTHER_NEIGHBOR, OTHER_WRONG, VALID_RELATION. A holder with a non-SUCCESS "
              "episode has no category and is left out of the denominators."]),
        Part("d", "displacement_per_case", "Displacement counts per case (holders with a SUCCESS after-episode)",
             ["Case", "Mechanism", *DISPLACEMENT, "Excluded (technical failure)",
              "SAME_WRONG_RELATION_OTHER_NEIGHBOR possible"], rows_d,
             ["For the SHORTCUT case (u = s, step 1) SAME_WRONG_RELATION_OTHER_NEIGHBOR cannot occur: step 1 always "
              "starts at s."]),
    ]
    return Table(5, "counterfactual", "Counterfactual (illustrative cases)",
                 "DESCRIPTIVE, TREATMENT-ONLY, EXPLORATORY (D7 DESCRIPTIVE). Per case only.",
                 [f"protocol §21; {PLAN}, section A4; {LOG}, entry 2026-11-13 \"S36 — Readings of the §21 outcomes\""],
                 ["results/interventions/s36/s36.json"], parts,
                 ["No aggregate ΔCF and no τ_CF are computed: both need a matched control, and none exists (C = 0). "
                  "Hiding the label removes the answers reached through it by construction (decision log 2026-11-12, "
                  "A4); these tables state observed counts only.",
                  f"Run commits (from s36.json): {commits}."])


# --------------------------------------------------------------------------------- tables 6–12: exploratory

def _view_label(view: str) -> str:
    return dict(VIEWS)[view]


def build_table6(b1_table: list[dict], b1: dict) -> Table:
    rows_a = [[_view_label(r["view"]), r["group"], r["agent_id"], *[number(r[k]) for k in (
        "episodes", "opportunity", "opened", "taken", "taken_and_opportunity", "taken_and_opened",
        "taken_outside_opportunity", "uptake", "opened_per_opportunity", "taken_per_opened")]] for r in b1_table]
    rows_b = []
    for key, label, use in (("verdict", "All queries", "outcome (primary)"),
                            ("verdict_without_source_name_overlap_descriptive", "Without SOURCE_NAME_OVERLAP",
                             "descriptive only")):
        v = b1[key]
        rows_b.append([label, "treat-final", v["rule"], v["agents_meeting"], v["count"], v["outcome"], use])
    rows_c = []
    for group, per in sorted(b1["non_success_episodes_excluded"].items()):
        for agent in b1["agent_order"]:
            st = per.get(agent, {})
            rows_c.append([group, agent, sum(st.values()), [f"{k}: {n}" for k, n in sorted(st.items())]])
    return Table(6, "b1_offlabel_uptake", "B1 — Off-label opportunity and uptake", EXPLORATORY,
                 [f"{PLAN}, section B1", f"{LOG}, entries 2026-11-12 \"B1 — Readings of the B1 definitions\" and "
                  "2026-11-13 \"B1 — Outcome NOT CLEAN; follow-up not run; no full run\""],
                 ["results/exploratory/b1/b1_table.csv", "results/exploratory/b1/b1.json"],
                 [Part("a", "uptake", "Opportunity, opened and taken per agent (SUCCESS episodes, latest attempts); "
                       "treat-final primary, treat-first descriptive",
                       ["View", "Group", "Agent", "Episodes", "Opportunity", "Opened", "Taken",
                        "Taken ∧ Opportunity", "Taken ∧ Opened", "Taken outside Opportunity",
                        "Uptake = Taken∧Opp / Opp", "Opened / Opp", "Taken∧Opened / Opened"], rows_a),
                  Part("b", "outcome", "CLEAN / NOT CLEAN (rule fixed 2026-11-12)",
                       ["View", "Group", "Rule", "Agents meeting", "Count", "Outcome", "Use"], rows_b),
                  Part("c", "excluded_episodes", "Non-SUCCESS episodes excluded (latest attempts)",
                       ["Group", "Agent", "Excluded", "By status"], rows_c)],
                 [f"Produced by scripts/40_b1_uptake.py at commit {b1['provenance']['git_commit']}."])


def build_table7(b2: dict) -> Table:
    rows_a, rows_b, rows_c = [], [], []
    for view, label in VIEWS:
        t = b2["tables"][view]
        for name in ("CF3^Q", "CF4^Q", "CF3^{Q,H1}", "CF4^{Q,H1}"):
            s, l = set(t["flagged_queries"]["strict"][name]), set(t["flagged_queries"]["lenient"][name])
            rows_a.append([label, name, t["cofailure"]["strict"][name], t["cofailure"]["lenient"][name],
                           sorted(s - l), sorted(l - s)])
        for key in ("strict", "lenient"):
            for p in t["per_agent"][key]:
                rows_b.append([label, p["agent_id"], key, p["episodes"], p["qv_precision_mean"], p["defined"], p["na"],
                               p["qv_pooled_num"], p["qv_pooled_den"], p["qv_precision_pooled"],
                               p["H1_CLEAN"], p["H1_MIXED"], p["H1_WRONG"], p["H1_NONE"]])
        for p in t["contraindication"]:
            rows_c.append([label, p["agent_id"], p["answers"], p["queries"], p["answers_in_T_q"],
                           p["answers_in_T_q_plus"]])
    return Table(7, "b2_strict_vs_lenient", "B2 — Strict vs lenient answer key", EXPLORATORY,
                 [f"{PLAN}, section B2", f"{LOG}, entry 2026-11-13 \"B2 — Inputs and the contraindication step\""],
                 ["results/exploratory/b2/b2.json"],
                 [Part("a", "cofailure", "Co-failure under the strict key (of record) and the lenient key",
                       ["View", "Metric", "Strict (of record)", "Lenient", "Strict-only queries",
                        "Lenient-only queries"], rows_a, ["CF3^{Q,H1} = N."]),
                  Part("b", "precision_hop1", "Per-agent question-valid precision and hop-1 status under both keys",
                       ["View", "Agent", "Key", "Episodes", "QV precision mean", "Defined", "NA", "Pooled numerator",
                        "Pooled denominator", "QV precision pooled", "H1_CLEAN", "H1_MIXED", "H1_WRONG", "H1_NONE"],
                       rows_b),
                  Part("c", "contraindication", "`contraindication` at an indication step (never accepted)",
                       ["View", "Agent", "Answers", "Queries", "Of the answers: in T_q", "in T_q⁺"], rows_c,
                       ["Indication step: treat-final, the second edge of a primary path with ≥ 2 edges; treat-first, "
                        "the first edge."])],
                 [f"Lenient key: `off-label use` accepted wherever `indication` is (R1⁺, R2⁺); `contraindication` never. "
                  f"{b2['queries_with_lenient_labels']} of {b2['queries']} queries have a changed key; "
                  f"{b2['queries_with_larger_T_q']} of them have T_q⁺ larger than T_q. Strict results remain the "
                  "results of record.",
                  f"Produced by scripts/41_b2_lenient.py at commit {b2['provenance']['git_commit']}."])


def build_table8(b5_table: list[dict], b5: dict) -> Table:
    rows_a = [[_view_label(r["view"]), r["subset"], r["group"], number(r["queries"]), number(r["CF3^Q"]),
               number(r["CF4^Q"]), number(r["CF3^{Q,H1}"]),
               r["CF3^{Q,H1} query IDs"].split(";") if r["CF3^{Q,H1} query IDs"] else []] for r in b5_table]
    rows_b = []
    for view, label in VIEWS:
        h = b5["hypergeometric"][view]
        p = h["probability_all_in_treat_final"]
        rows_b.append([label, h["population_N_expansion_queries"], h["successes_K_expansion_treat_final_queries"],
                       h["draws_n_expansion_CF3_Q_H1_queries"], h["observed_in_treat_final"], h["all_in_treat_final"],
                       p["formula"], f"{p['numerator']}/{p['denominator']} = {p['fraction_reduced']}", p["decimal"]])
    return Table(8, "b5_treat_concentration", "B5 — Treat concentration", EXPLORATORY, [f"{PLAN}, section B5"],
                 ["results/exploratory/b5/b5_table.csv", "results/exploratory/b5/b5.json"],
                 [Part("a", "groups", "Queries and co-failure by group (treat-final, treat-first, other) for pilot, "
                       "expansion and both",
                       ["View", "Subset", "Group", "Queries", "CF3^Q", "CF4^Q", "CF3^{Q,H1}", "CF3^{Q,H1} queries"],
                       rows_a),
                  Part("b", "hypergeometric", "Exact hypergeometric probability that the expansion's CF3^{Q,H1} "
                       "queries all fall in treat-final",
                       ["View", "N (expansion queries)", "K (treat-final)", "n (CF3^{Q,H1} = 1)",
                        "Observed in treat-final", "All in treat-final", "Formula", "Exact", "Decimal"], rows_b,
                       ["P = C(K, n) / C(N, n). Reported as a replication of a pattern seen in the pilot: the pilot "
                        "report was committed (44a2fdd, 2026-11-08) before the expansion run started; no prediction "
                        "was written before the expansion analysis."])],
                 [f"Produced by scripts/42_b5_concentration.py at commit {b5['provenance']['git_commit']}."])


def build_table9(b6_table: list[dict], handcheck: list[dict], b6: dict) -> Table:
    rows_a = [[_view_label(r["view"]), r["relation_type"], *[number(r[k]) for k in
               ("queries", "CF3^BH", "CF3^Q", "both", "BH-only", "Q-only")]] for r in b6_table]
    if len(handcheck) != 15:
        raise ValueError(f"b6_handcheck.csv has {len(handcheck)} rows, expected 15")
    bad = [r["query_id"] for r in handcheck if r["mark"] not in MARKS]
    if bad:
        raise ValueError(f"b6_handcheck.csv rows without a valid mark: {bad}")
    rows_b = [[number(r["order"]), r["query_id"], r["relation_type"], f"{r['entity_name']} [{r['entity_id']}]",
               number(r["holders"]), r["holder_agents"].split(";"), number(r["entity_in_T_q"]), r["graph_paths"],
               number(r["biohopr_gold_size"]), r["biohopr_gold_list"], r["mark"]] for r in handcheck]
    marks = Counter(r["mark"] for r in handcheck)
    outcome = "CLEAN" if marks["VALID"] >= B6_CLEAN_MIN_VALID else "NOT CLEAN"
    rows_c = [[*[marks.get(m, 0) for m in MARKS], len(handcheck),
               f"CLEAN if at least {B6_CLEAN_MIN_VALID} of 15 final marks are VALID", outcome]]
    return Table(9, "b6_benchmark_vs_graph", "B6 — Benchmark vs graph labels, with the hand-check", EXPLORATORY,
                 [f"{PLAN}, section B6", f"{LOG}, entries 2026-11-12 \"B6 — Hand-check mark definitions\" and "
                  "2026-11-12 \"B6 — Outcome: hand-check NOT CLEAN (10 of 15 VALID)\""],
                 ["results/exploratory/b6/b6_table.csv", "results/exploratory/b6/b6.json",
                  "results/exploratory/b6_handcheck.csv"],
                 [Part("a", "by_relation_type", "CF3^BH vs CF3^Q by relation type (BH-only = CF3^BH = 1 and CF3^Q = 0)",
                       ["View", "Relation type", "Queries", "CF3^BH", "CF3^Q", "Both", "BH-only", "Q-only"], rows_a),
                  Part("b", "handcheck", "Hand-check: 15 of the BH-only queries, final marks (researcher)",
                       ["Order", "Query", "Relation type", "Entity", "Holders", "Holder agents", "In T_q",
                        "Graph path(s)", "BioHopR gold size", "BioHopR gold list", "Final mark"], rows_b,
                       ["Selection: first 15 BH-only queries by SHA256(\"42\" + query_id); entity = the benchmark shared "
                        "entity with the smallest node ID. Sources gathered and marks proposed by Claude Code (an LLM); "
                        "every final mark set by the researcher (results/exploratory/b6_handcheck_notes.md)."]),
                  Part("c", "handcheck_outcome", "Hand-check outcome (rule fixed before any mark)",
                       [*MARKS, "Rows", "Rule", "Outcome"], rows_c)],
                 [f"BH-only queries: {b6['bh_only_queries']}. Produced by scripts/43_b6_benchmark.py at commit "
                  f"{b6['provenance']['git_commit']}; marks from results/exploratory/b6_handcheck.csv."])


def build_table10(rp: dict) -> Table:
    rows_a = [[q["query_id"], q["relation_type"], q["source_name_overlap"], q["original_cf3_q"], q["repeat_cf3_q"],
               q["reproduces_cf3_q"], q["original_cf4_q"], q["repeat_cf4_q"], q["original_cf3_q_h1"],
               q["repeat_cf3_q_h1"], q["original_shared_q"], q["repeat_shared_q"]]
              for q in sorted(rp["queries"], key=lambda q: q["query_id"])]
    rows_b = []
    for view, label in VIEWS:
        c = rp["counts"][view]
        rows_b.append([label, c["queries"], c["original_cf3_q"], c["repeat_cf3_q"], c["reproduced"],
                       c["repeat_cf4_q"], c["repeat_cf3_q_h1"], c.get("expectation_at_least"),
                       c.get("expectation_met")])
    rows_c = []
    for p in sorted(rp["pairs"], key=lambda p: (p["query_id"], p["agent_id"])):
        ja, jo = p["jaccard_answers"], p["jaccard_off_question"]
        rows_c.append([p["query_id"], p["agent_id"], p["original_status"], p["repeat_status"], p["original_answers"],
                       p["repeat_answers"], ja["intersection"], ja["union"], ja["value"], jo["intersection"],
                       jo["union"], jo["value"]])
    return Table(10, "rp_repeat_run", "RP — Repeat run (repeat_v1)", EXPLORATORY,
                 [f"{PLAN}, section D", f"{LOG}, entries 2026-11-13 \"RP — Repeat-run inputs\" and \"RP — Pre-run checks\""],
                 ["results/exploratory/rp/rp.json"],
                 [Part("a", "per_query", "Per query: original (results of record) vs repeat_v1",
                       ["Query", "Relation type", "SOURCE_NAME_OVERLAP", "CF3^Q original", "CF3^Q repeat",
                        "CF3^Q reproduces", "CF4^Q original", "CF4^Q repeat", "CF3^{Q,H1} original",
                        "CF3^{Q,H1} repeat", "Shared W^Q entities original", "Shared W^Q entities repeat"], rows_a),
                  Part("b", "summary", "Reproduction counts (expectation, descriptive, not a test: at least 6 of 8)",
                       ["View", "Queries", "CF3^Q original", "CF3^Q repeat", "Reproduced", "CF4^Q repeat",
                        "CF3^{Q,H1} repeat", "Expectation (at least)", "Expectation met"], rows_b),
                  Part("c", "jaccard", "Per agent and query: Jaccard overlap of answer ID sets and OFF_QUESTION sets",
                       ["Query", "Agent", "Status original", "Status repeat", "Answers original", "Answers repeat",
                        "Answers ∩", "Answers ∪", "Jaccard answers", "OFF_QUESTION ∩", "OFF_QUESTION ∪",
                        "Jaccard OFF_QUESTION"], rows_c, ["Jaccard is NA (—) when both sets are empty."])],
                 ["repeat_v1 never replaces pilot_v1/expansion_v1, which remain the results of record.",
                  f"Produced by scripts/45_rp_report.py at commit {rp['provenance']['git_commit']}; repeat_v1 inference "
                  f"commit(s): {', '.join(rp['provenance']['repeat_inference_commits'])}."])


PLAN_HEADING = "## 2026-11-12 — S30 — Plan after D7"
C3_START = "3. Predictions (fixed now"
C3_END = "4. "
NOT_RUN = "Not run (decision log 2026-11-13, B1 NOT CLEAN)"


def c3_text(log_text: str) -> tuple[str, list[str], list[str]]:
    """Section C3 of the decision-log entry 2026-11-12 "Plan after D7", verbatim: its opening line, its bullets
    and its closing line(s). Only the hard line wraps of the log are joined (one space; indentation dropped).
    Stops if the entry or the section cannot be found exactly once."""
    lines = log_text.splitlines()
    heads = [i for i, ln in enumerate(lines) if ln.startswith(PLAN_HEADING)]
    if len(heads) != 1:
        raise ValueError(f"decision log: {len(heads)} entries start with {PLAN_HEADING!r}")
    entry = []
    for ln in lines[heads[0] + 1:]:
        if ln.startswith("## "):
            break
        entry.append(ln)
    starts = [i for i, ln in enumerate(entry) if ln.startswith(C3_START)]
    if len(starts) != 1:
        raise ValueError(f"decision log: section C3 ({C3_START!r}) found {len(starts)} times in the entry")
    block = []
    for ln in entry[starts[0] + 1:]:
        if ln.startswith(C3_END) or ln.startswith("#"):
            break
        block.append(ln)
    items: list[str] = []
    closing: list[str] = []
    for ln in block:
        text = ln.strip()
        if not text:
            continue
        if ln.startswith("   - "):
            items.append(text[2:])
        elif ln.startswith("     ") and items and not closing:
            items[-1] += " " + text
        else:
            closing.append(text)
    if not items:
        raise ValueError("decision log: section C3 has no bullet")
    return entry[starts[0]].strip(), items, closing


def build_table11(log_text: str, b1_outcome: str) -> Table:
    if b1_outcome != "NOT CLEAN":
        raise ValueError(f"B1 outcome is {b1_outcome!r}; Table 11 states 'not run' only after B1 NOT CLEAN")
    opening, items, closing = c3_text(log_text)
    rows = [[item.split(":", 1)[0], item, NOT_RUN] for item in items]
    return Table(11, "followup", "Follow-up (P1, P2)", "EXPLORATORY — NOT RUN",
                 [f"{PLAN}, section C3", f"{LOG}, entry 2026-11-13 \"B1 — Outcome NOT CLEAN; follow-up not run; no "
                  "full run\"", f"{LOG}, entry 2026-11-14 \"S37 — D8 not applicable after D7 DESCRIPTIVE; no scaling\""],
                 [LOG], [Part("a", "predictions", "Pre-registered predictions of the follow-up study",
                              ["Item", "Text of decision log 2026-11-12 \"Plan after D7\", section C3 (verbatim)",
                               "Status"], rows,
                              [f"Section C3 opens: \"{opening}\" and closes: \"{' '.join(closing)}\"",
                               "Quoted verbatim from docs/decision_log.md by the script; only the log's hard line "
                               "wraps are joined."])],
                 [f"{NOT_RUN}: the follow-up (F1–F3) has no episode, so neither prediction is held or not held."])


def build_table12(ic: dict) -> Table:
    rows_a, rows_b = [], []
    for view, label in VIEWS:
        r = ic[view]
        rows_a.append([label, r["queries"], r["queries_with_opportunity"], r["T_obs"], r["E_T"], r["T_2.5th"],
                       r["T_97.5th"], r["P_T_ge_obs"], r["P_T_le_obs"], r["outcome"],
                       "outcome" if view == "all_queries" else "descriptive only", r["S_obs"], r["S_expected"]])
        for a, v in sorted(r["agents"].items()):
            rows_b.append([label, a, v["opportunity"], v["taken_and_opportunity"], v["p"]])
    rows_c = [[q["query_id"], q["A_q"], q["takers"], q["K_q"], q["P_K_ge_3"], q["CF3_Q_H1"]]
              for q in ic["all_queries"]["per_query"] if q["K_q"] >= 2 or q["CF3_Q_H1"] == 1]
    prov = ic["provenance"]
    return Table(12, "ic_independence_check", "IC — Independence check of off-label uptake", EXPLORATORY,
                 [f"{LOG}, entry 2026-11-13 \"IC — Independence check of off-label uptake (rule fixed before "
                  "computing)\"", f"{PLAN} (B1 inputs)"],
                 ["results/exploratory/ic/ic.json"],
                 [Part("a", "summary", "T = number of treat-final queries with K_q ≥ 3, against independence with "
                       "each agent's own B1 uptake rate (exact Poisson-binomial)",
                       ["View", "Queries", "Queries with ≥ 1 agent in A_q", "T_obs", "E[T]", "T 2.5th", "T 97.5th",
                        "P(T ≥ T_obs)", "P(T ≤ T_obs)", "Outcome", "Use", "Pairs S_obs", "Pairs expected"], rows_a,
                       ["Outcome rule (fixed before computing): AGREES if both tail probabilities > 0.025; MORE "
                        "CLUSTERED if P(T ≥ T_obs) ≤ 0.025; LESS CLUSTERED if P(T ≤ T_obs) ≤ 0.025."]),
                  Part("b", "rates", "p_i = (Taken ∧ Opportunity) / Opportunity per agent (B1)",
                       ["View", "Agent", "Opportunity", "Taken ∧ Opportunity", "p_i"], rows_b),
                  Part("c", "per_query", "Queries with K_q ≥ 2 or CF3^{Q,H1} = 1 (all queries)",
                       ["Query", "A_q", "Takers", "K_q", "P(K_q ≥ 3)", "CF3^{Q,H1}"], rows_c,
                       ["All 75 per-query rows: results/exploratory/ic/ic_per_query.csv."])],
                 ["Limits (logged with the rule): p_i is estimated from the same episodes; queries whose off-label "
                  "lists are more tempting would also appear as MORE CLUSTERED. Agents never share anything (§9.3); "
                  "\"independent\" means only that each agent's own rate accounts for the pattern.",
                  f"Produced by scripts/44_independence_check.py at commit {prov['commit']}."])


# ------------------------------------------------------------------------------------------- provenance

def git(root: Path, *args: str) -> str:
    res = subprocess.run(["git", *args], cwd=root, capture_output=True, text=True, encoding="utf-8")
    if res.returncode != 0:
        raise RuntimeError(f"git {' '.join(args)} failed ({res.returncode}): {res.stderr.strip()}")
    return res.stdout.strip()


def sha256_bytes(data: bytes) -> str:
    return hashlib.sha256(data).hexdigest()


def digest(root: Path, rel: str) -> str:
    path = root / rel
    if path.is_file():
        return sha256_bytes(path.read_bytes())
    if not path.is_dir():
        raise FileNotFoundError(f"input {rel} does not exist")
    lines = [f"{p.relative_to(root).as_posix()}\t{sha256_bytes(p.read_bytes())}"
             for p in sorted(path.rglob("*")) if p.is_file()]
    if not lines:
        raise ValueError(f"input folder {rel} is empty")
    return sha256_bytes(("\n".join(lines) + "\n").encode("utf-8"))


def path_state(root: Path, rel: str) -> dict:
    tracked = bool(git(root, "ls-files", "--", rel))
    changed = bool(git(root, "status", "--porcelain", "--untracked-files=all", "--", rel))
    return {"tracked": tracked, "unchanged_at_HEAD": tracked and not changed,
            "last_commit": git(root, "log", "-1", "--format=%H", "--", rel) or None}


def provenance(root: Path, inputs: list[str]) -> dict:
    code = {p: path_state(root, p) for p in (SCRIPT, REPORT_SCRIPT)}
    return {
        "script": SCRIPT, "commit": git(root, "rev-parse", "HEAD"),
        "tracked_clean": not git(root, "status", "--porcelain", "--untracked-files=no"),
        "code": code, "code_committed": all(s["unchanged_at_HEAD"] for s in code.values()),
        "inputs": {p: {"sha256": digest(root, p), **path_state(root, p)} for p in sorted(set(inputs))},
    }


# ------------------------------------------------------------------------------------------- rendering

def part_csv_name(t: Table, p: Part) -> str:
    return f"table{t.number:02d}{p.key}_{p.slug}.csv"


def table_md_name(t: Table) -> str:
    return f"table{t.number:02d}_{t.slug}.md"


def render_table(t: Table, prov: dict) -> str:
    L = [f"# Table {t.number} — {t.title}\n", f"**Status:** {t.status}\n",
         "**Basis:** " + "; ".join(t.basis) + "\n"]
    line = (f"Produced by `{SCRIPT}` at commit `{prov['commit']}` (tracked files clean: {prov['tracked_clean']}; "
            f"producing code committed at this commit: {prov['code_committed']}).")
    L.append(line + "\n")
    if not prov["code_committed"]:
        L.append("**PROVISIONAL** — the producing code (" + ", ".join(
            f"`{p}`" for p, s in prov["code"].items() if not s["unchanged_at_HEAD"]) +
            ") is not committed at this commit, so the hash above does not identify it. Regenerate after "
            "committing.\n")
    if t.sources:
        L.append("Inputs (SHA256 in `provenance.json`; last commit that touched each):\n")
        L += [f"- `{s}` — {prov['inputs'][s]['last_commit'] or 'not committed'}" for s in t.sources]
        L.append("")
    for n in t.notes:
        L.append(n + "\n")
    for p in t.parts:
        L.append(f"## {t.number}{p.key}. {p.title}\n")
        L.append(f"CSV: `{part_csv_name(t, p)}`\n")
        L.append(md_table(p.header, p.rows) + "\n")
        for n in p.notes:
            L.append(n + "\n")
    return "\n".join(L)


def render_index(tables: list[Table], prov: dict, checks: list[str]) -> str:
    L = ["# Final tables (S38)\n",
         f"Produced by `{SCRIPT}` at commit `{prov['commit']}` (tracked files clean: {prov['tracked_clean']}; "
         f"producing code committed at this commit: {prov['code_committed']}). Runbook Part 10, S38, with its "
         "DESCRIPTIVE additions; Table 12 (IC) added on the researcher's instruction of 2026-11-14.\n"]
    if not prov["code_committed"]:
        L.append("**PROVISIONAL** — regenerate after committing the producing code.\n")
    rows = [[t.number, f"[{t.title}]({table_md_name(t)})", t.status, "; ".join(t.basis),
             [part_csv_name(t, p) for p in t.parts]] for t in tables]
    L.append(md_table(["Table", "Title", "Status", "Basis", "CSV files"], rows) + "\n")
    L.append("Cross-checks passed before writing:\n")
    L += [f"- {c}" for c in checks]
    L.append("\nInput and output SHA256: `provenance.json`.\n")
    return "\n".join(L)


def prose(t: Table) -> str:
    """The wording this script writes for a table (title, status, basis, notes, part titles, headers) —
    not the data cells, which hold names from PrimeKG and BioHopR."""
    texts = [t.title, t.status, *t.basis, *t.notes]
    for p in t.parts:
        texts += [p.title, *p.header, *p.notes]
    return "\n".join(texts)


def scan_causal(tables: list[Table]) -> None:
    """Tables 1–5 (observed facts) must use no causal word of the scripts/28_pilot_report.py list. The §9.5
    field name `cause` (written in backticks) is the only exemption."""
    for t in tables:
        if t.number > 5:
            continue
        hit = R28.CAUSAL.search(prose(t).replace("`cause`", ""))
        if hit:
            raise ValueError(f"Table {t.number}: causal word {hit.group(0)!r}")


def build_all(data: dict) -> list[Table]:
    src = data["run_sources"]
    return [
        build_table1(data["validation"], data["primary"], data["primary_summary"], data["mapping"],
                     data["biohopr_types"], data["sampled"]),
        build_table2(data["rows"], data["agents"], data["manifest"], src + ["results/semantics/relation_mapping.json"]),
        build_table3(data["cofailure"], data["nulls"], data["manifest"], src),
        build_table4(data["rows"], data["agents"], data["cofailure"], data["manifest"], data["candidates"], src),
        build_table5(data["s36"]),
        build_table6(data["b1_table"], data["b1"]),
        build_table7(data["b2"]),
        build_table8(data["b5_table"], data["b5"]),
        build_table9(data["b6_table"], data["handcheck"], data["b6"]),
        build_table10(data["rp"]),
        build_table11(data["decision_log"], data["b1"]["verdict"]["outcome"]),
        build_table12(data["ic"]),
    ]


def write_outputs(out: Path, tables: list[Table], prov: dict, checks: list[str]) -> dict[str, str]:
    files: dict[str, str] = {}
    for t in tables:
        files[table_md_name(t)] = render_table(t, prov)
        for p in t.parts:
            files[part_csv_name(t, p)] = csv_text(p.header, p.rows)
    scan_causal(tables)
    files["README.md"] = render_index(tables, prov, checks)
    out.mkdir(parents=True, exist_ok=True)
    extra = sorted(p.name for p in out.iterdir() if p.name not in files and p.name != "provenance.json")
    if extra:
        raise FileExistsError(f"{out} contains files this script does not write: {extra}. Nothing was written.")
    for name, text in files.items():
        (out / name).write_text(text, encoding="utf-8", newline="\n")
    record = {**prov, "cross_checks": checks,
              "outputs": {name: sha256_bytes(text.encode("utf-8")) for name, text in sorted(files.items())}}
    (out / "provenance.json").write_text(json.dumps(record, indent=2, sort_keys=True) + "\n", encoding="utf-8",
                                         newline="\n")
    return files


def main(argv=None) -> None:
    ap = argparse.ArgumentParser(description=__doc__.split("\n")[0])
    ap.add_argument("--combined", default=COMBINED)
    ap.add_argument("--out", default="results/reports/final")
    args = ap.parse_args(argv)
    data = load_inputs(ROOT, args.combined)
    checks = cross_check(data, digest(ROOT, data["cofailure_path"]))
    tables = build_all(data)
    inputs = sorted({s for t in tables for s in t.sources} | {data["cofailure_path"], data["nulls_path"]})
    prov = provenance(ROOT, inputs)
    files = write_outputs(ROOT / args.out, tables, prov, checks)
    print(f"S38: wrote {len(files) + 1} files to {args.out} at commit {prov['commit'][:7]} "
          f"(tracked clean: {prov['tracked_clean']}; code committed: {prov['code_committed']})")
    for t in tables:
        print(f"  table{t.number:02d}_{t.slug}: {len(t.parts)} part(s), "
              f"{sum(len(p.rows) for p in t.parts)} rows")


if __name__ == "__main__":
    main()
