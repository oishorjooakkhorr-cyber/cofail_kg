"""Tests for scripts/38_final_tables.py (S38 final tables) on tiny synthetic fixtures."""
import copy
import importlib.util
import json
from pathlib import Path
import subprocess

import pytest

ROOT = Path(__file__).resolve().parents[1]
spec = importlib.util.spec_from_file_location("final_tables", ROOT / "scripts/38_final_tables.py")
M = importlib.util.module_from_spec(spec)
spec.loader.exec_module(M)
R28 = M.R28

AGENTS = ["A1", "A2", "A3", "A4"]
RATIO_KEYS = [k for _, k in M.RATIO_METRICS]


# ----------------------------------------------------------------------------------------------- helpers

def mrow(agent, q, construction="BRIDGE", status="SUCCESS", la=None, lb=None, prim=None, allp=None, early=False,
         hop1="H1_CLEAN", ranks=None, answers=0):
    ok = status == "SUCCESS"
    return {
        "agent_id": agent, "query_id": q, "attempt": 1, "episode_status": status,
        "cause": "CONNECTION" if status == "ERROR" else None, "construction": construction,
        "label_a_counts": {**{k: 0 for k in R28.LABEL_A}, **(la or {})},
        "label_b_counts": {**{k: 0 for k in R28.LABEL_B}, **(lb or {})},
        "primary_reason_counts": {**{k: 0 for k in R28.REASONS}, **(prim or {})},
        "reason_counts": {**{k: 0 for k in R28.REASONS}, **(allp or prim or {})},
        **{k: (0.5 if ok else None) for k in RATIO_KEYS},
        "numerators": {k: (1 if ok else None) for k in RATIO_KEYS},
        "denominators": {k: (2 if ok else None) for k in RATIO_KEYS},
        "early_stop": early if ok else None, "budget_exhausted": False, "hop1_status": hop1,
        "answer_count": answers if ok else None, "bridge_rank": ranks or {}, "found_r1": hop1 in ("H1_CLEAN", "H1_MIXED"),
    }


def cfq(qid, rt="t1", tag="NONE", question=0, cf4=0, h1=0, bh=0, rel3=0, node3=0, short3=0):
    blk = lambda c3, c4: {"cf3": c3, "cf4": c4, "shared_entities": []}
    return {"query_id": qid, "relation_type": rt, "ambiguity_tag": tag, "question": blk(question, cf4),
            "grounded": blk(question, cf4), "hop1_clean": blk(h1, 0), "benchmark": blk(bh, 0),
            "pcf_rel3": rel3, "pcf_rel4": 0, "pcf_node3": node3, "pcf_node4": 0, "pcf_shortcut3": short3,
            "pcf_rel_cases": [], "pcf_node_cases": [], "pcf_shortcut_cases": []}


def totals(queries):
    c = R28.cf_counts(queries)
    return {R28.TOTAL_KEYS[n]: v for n, v in c.items()}


def cofailure(queries, overlap=()):
    keep = [q for q in queries if q["query_id"] not in set(overlap)]
    return {"agent_order": AGENTS, "queries": queries, "source_name_overlap_queries": list(overlap),
            "totals_all_queries": totals(queries), "totals_without_source_name_overlap": totals(keep),
            "pairwise_all_queries": [{"agent_i": "A1", "agent_j": "A2", "numerator": 1, "denominator": 2}],
            "pairwise_without_source_name_overlap": [{"agent_i": "A1", "agent_j": "A2", "numerator": 0,
                                                      "denominator": 0}]}


def null_block(observed, p95, exceeds=None):
    one = {"null_mean": 1.0, "null_median": 1.0, "null_p95": p95, "observed_total": observed, "p": 0.5,
           "query_count": 3, "observed_exceeds_null": observed > p95 if exceeds is None else exceeds}
    return {"cf3": dict(one), "cf4": dict(one)}


def nulls(exceeds=None):
    agg = {n: null_block(1, 2.0, exceeds) for n in ("N1", "N1-H1", "N2")}
    return {"agent_order": AGENTS, "trials": 10, "aggregate_all_queries": agg,
            "aggregate_without_source_name_overlap": copy.deepcopy(agg),
            "aggregate_excluding_technical_failures": copy.deepcopy(agg)}


MANIFEST = {"Q1": {"relation_type": "t1", "ambiguity_tag": "NONE", "multiplicity": "SINGLE_BRIDGE", "construction": "BRIDGE"},
            "Q2": {"relation_type": "t2", "ambiguity_tag": "R2_AMBIGUOUS", "multiplicity": "SINGLE_BRIDGE",
                   "construction": "BRIDGE"},
            "Q3": {"relation_type": "t3", "ambiguity_tag": "R1_AMBIGUOUS", "multiplicity": "MULTI_BRIDGE",
                   "construction": "UNION"}}


def part(table, key):
    return next(p for p in table.parts if p.key == key)


# --------------------------------------------------------------------------------------------- formatting

def test_cells_markdown_and_csv():
    assert M.md_cell(None) == "—" and M.csv_cell(None) == ""
    assert M.md_cell(True) == "yes" and M.csv_cell(False) == "False"
    assert M.md_cell(0.123456) == "0.1235" and M.csv_cell(0.123456) == "0.123456"
    assert M.md_cell(["a", "b"]) == "a, b" and M.csv_cell(["a", "b"]) == "a;b"
    assert M.md_cell([]) == "—"
    assert M.md_cell("a|b") == "a\\|b"
    assert M.number("12") == 12 and M.number("0.5") == 0.5 and M.number("True") is True and M.number("x") == "x"


def test_tables_refuse_ragged_rows():
    with pytest.raises(ValueError):
        M.md_table(["a", "b"], [[1]])
    with pytest.raises(ValueError):
        M.csv_text(["a"], [[1, 2]])
    assert M.csv_text(["a", "b"], [[None, 0.5]]) == "a,b\n,0.500000\n"


# ---------------------------------------------------------------------------------------------- table 1

def vrow(qid, rt, status="CONSISTENT", reason="NONE", codes=(), mult="SINGLE_BRIDGE", leaky=False, share=0.01,
         tag="NONE", construction="BRIDGE"):
    r = {"query_id": qid, "relation_type": rt, "status": status, "primary_reason": reason,
         "bridge_multiplicity": mult, "leaky_question": str(leaky), "saturation_share": str(share),
         "ambiguity_tag": tag, "construction": construction, "target_type": "drug", "target_type_nodes": "100"}
    for c in M.REASON_ORDER:
        r[c] = "True" if c in codes else "False"
    return r


def table1_inputs():
    validation = [vrow("V1", "a:b:c"), vrow("V2", "a:b:c", leaky=True),
                  vrow("V3", "a:b:c", status="INCONSISTENT", reason="GOLD_MISSING_FROM_KG",
                       codes=("GOLD_MISSING_FROM_KG", "EXTRA_TARGETS")),
                  vrow("V4", "d:e:f", mult="MULTI_BRIDGE", share=0.6, tag="R1_AMBIGUOUS", construction="UNION"),
                  vrow("V5", "d:e:f", mult="MULTI_BRIDGE", tag="R1_AMBIGUOUS", construction="UNION")]
    primary = [{"query_id": q, "theta": "0.5"} for q in ("V1", "V5")]
    summary = {"mapping_confirmation": {"a:b:c": "CONFIRMED", "d:e:f": "UNCONFIRMABLE"}}
    mapping = {"a:b:c": {"d1_status": "PASS", "construction": "BRIDGE", "R1": ["r1"], "R2": ["r2"]},
               "d:e:f": {"d1_status": "PASS", "construction": "UNION", "R1": ["r3"], "R2": ["r4"]},
               "x:y:z": {"d1_status": "FAIL", "construction": None, "R1": None, "R2": None}}
    bh = [{"relation_hop2": "a:b:c", "n_rows": "3"}, {"relation_hop2": "d:e:f", "n_rows": "2"},
          {"relation_hop2": "x:y:z", "n_rows": "7"}]
    return validation, primary, summary, mapping, bh, {"pilot": {"V1"}, "expansion": {"V5"}}


def test_table1_counts():
    t = M.build_table1(*table1_inputs())
    a = {r[0]: r for r in part(t, "a").rows}
    # columns: type, rows, D1, construction, R1, R2, tag, validated, CONS, INCONS, LEAKY, SAT, primary, single,
    #          multi, pilot, expansion
    assert a["a:b:c"][7:] == [3, 2, 1, 1, 0, 1, 1, 0, 1, 0]
    assert a["d:e:f"][7:] == [2, 2, 0, 0, 1, 1, 0, 1, 0, 1]
    assert a["x:y:z"][2] == "FAIL" and a["x:y:z"][7:] == [None] * 10
    assert a["Total"][1] == 12 and a["Total"][7] == 5
    b = {r[0]: r for r in part(t, "b").rows}
    assert b["GOLD_MISSING_FROM_KG"][1:3] == [1, 1] and b["EXTRA_TARGETS"][1:3] == [0, 1]
    g = dict((r[0], r[1]) for r in part(t, "g").rows)
    assert g["SATURATED"] == 1 and g["Excluded (any of the above; counts above may overlap)"] == 3
    assert g["Primary population"] == 2


def test_table1_refuses_inconsistent_inputs():
    validation, primary, summary, mapping, bh, sampled = table1_inputs()
    with pytest.raises(ValueError, match="primary population"):
        M.build_table1(validation, primary + [{"query_id": "V2", "theta": "0.5"}], summary, mapping, bh, sampled)
    with pytest.raises(ValueError, match="θ"):
        M.build_table1(validation, [{"query_id": "V1", "theta": "0.5"}, {"query_id": "V5", "theta": "0.4"}],
                       summary, mapping, bh, sampled)
    with pytest.raises(ValueError, match="sampled"):
        M.build_table1(validation, primary, summary, mapping, bh, {"pilot": {"V2"}})


# ---------------------------------------------------------------------------------------------- table 2

def rows_q1_q3():
    rows = {}
    for a in AGENTS:
        rows[(a, "Q1")] = mrow(a, "Q1", la={"GOLD": 2, "OFF_QUESTION": 1}, lb={"SUPPORTED": 2, "PATH_INVALID": 1},
                               prim={"SHORTCUT": 1}, ranks={"b1": 1}, answers=3, early=(a == "A1"))
        rows[(a, "Q3")] = mrow(a, "Q3", construction="UNION", status="ERROR" if a == "A4" else "SUCCESS",
                               la={"GOLD": 1}, lb={"SUPPORTED": 1}, hop1="H1_NONE" if a == "A4" else "H1_MIXED",
                               answers=1)
    return rows


def test_table2_splits_and_all_agent_sums():
    t = M.build_table2(rows_q1_q3(), AGENTS, MANIFEST, [])
    status = part(t, "a").rows
    splits = {r[0] for r in status}
    # R2_AMBIGUOUS and BOTH_AMBIGUOUS have no query here: those splits are skipped.
    assert splits == {"All", "construction = BRIDGE", "construction = UNION", "ambiguity tag = NONE",
                      "ambiguity tag = R1_AMBIGUOUS"}
    all_agents = next(r for r in status if r[0] == "All" and r[1] == "All agents")
    assert all_agents[2:8] == [8, 7, 0, 1, 0, 1]
    hop1 = next(r for r in part(t, "b").rows if r[0] == "construction = UNION" and r[1] == "All agents")
    assert hop1[2:] == [4, 0, 3, 0, 1, 3]
    la = next(r for r in part(t, "d").rows if r[0] == "All" and r[1] == "A1")
    assert la[2:] == [2, 4, 3, 0, 0, 1, 0]
    ratios = [r for r in part(t, "f").rows if r[0] == "All" and r[1] == "A4" and r[2] == "Benchmark F1"]
    assert ratios == [["All", "A4", "Benchmark F1", 0.5, 1, 1, 1, 2, 0.5]]
    assert "E = technical failures / episodes = 1/8" in part(t, "a").notes[0]


# ---------------------------------------------------------------------------------------------- table 3

def test_table3_views_strata_and_nulls():
    qs = [cfq("Q1", question=1, h1=1, bh=1, rel3=1), cfq("Q2", rt="t2", tag="R2_AMBIGUOUS", question=1, cf4=1,
                                                            bh=1), cfq("Q3", rt="t3", tag="R1_AMBIGUOUS")]
    t = M.build_table3(cofailure(qs, overlap=["Q2"]), nulls(), MANIFEST, [])
    a = {r[0]: r for r in part(t, "a").rows}
    assert a["CF3^Q"][1:3] == [2, 3] and a["CF3^Q"][4:6] == [1, 2]
    assert a["CF4^Q"][1] == 1 and a["CF4^Q"][4] == 0
    b = {r[0]: r for r in part(t, "b").rows}
    assert b["CF3^Q"][2] == ["Q1", "Q2"] and b["CF3^Q"][3] == ["Q2"]
    c = part(t, "c").rows
    assert c[1][-1] is None and c[0][-1] == 0.5
    d = part(t, "d").rows
    assert len(d) == 3 * 3 * 2 and d[0][-1] is False
    e = part(t, "e").rows
    ambig_none = next(r for r in e if r[0] == "All queries" and r[1] == "Ambiguity tag" and r[2] == "NONE")
    assert ambig_none[3] == 1 and ambig_none[4] == 1


def test_table3_refuses_stored_exceeds_disagreeing():
    qs = [cfq("Q1")]
    with pytest.raises(ValueError, match="observed_exceeds_null"):
        M.build_table3(cofailure(qs), nulls(exceeds=True), MANIFEST, [])


# ---------------------------------------------------------------------------------------------- table 4

def test_table4_reason_codes_early_stop_and_mechanisms():
    qs = [cfq("Q1", short3=1, question=1), cfq("Q2", rt="t2", tag="R2_AMBIGUOUS"), cfq("Q3", rt="t3", tag="R1_AMBIGUOUS")]
    cands = [{"query_id": "Q1", "relation_type": "t1", "ambiguity_tag": "NONE", "source_name_overlap": "False",
              "cf3_q": "1", "cf3_h1": "0", "mechanism": "SHORTCUT", "feature_u": "7", "feature_u_name": "n",
              "feature_r": "lab", "feature_step": "1", "feature_holders": "3", "feature_agents": "A1;A2;A3",
              "valid_route_after_block": "True", "has_matched_control": "False"}]
    t = M.build_table4(rows_q1_q3(), AGENTS, cofailure(qs), MANIFEST, cands, [])
    a = part(t, "a").rows
    allrow = next(r for r in a if r[0] == "All queries" and r[1] == "All")
    # queries, SUCCESS episodes, PATH_INVALID answers, SHORTCUT, ..., early stop n, defined, share
    assert allrow[3:7] == [2, 7, 4, 4] and allrow[-3:] == [1, 7, 1 / 7]
    union = next(r for r in a if r[0] == "All queries" and r[2] == "UNION")
    assert union[4:7] == [3, 0, 0]
    b = {r[0]: r for r in part(t, "b").rows}
    assert b["A1"][1:4] == [1, 1, 1]
    c = part(t, "c").rows
    assert next(r for r in c if r[0] == "All queries" and r[2] == "NONE")[4] == 1   # PCF_SHORTCUT3
    d = part(t, "d")
    assert d.rows[0][6] == "SHORTCUT" and d.rows[0][12] == ["A1", "A2", "A3"]
    assert "SHORTCUT 1" in d.notes[0]


# ---------------------------------------------------------------------------------------------- table 5

def s36_case(qid="Q1", before=None):
    """One synthetic S36 case; `before` = the flags that are 1 before (all are 0 after)."""
    before = before or {"CF3^Q"}
    holder = lambda cat, rec: {"status": "SUCCESS", "category": cat, "recovered": rec, "resolved": 2,
                               "answer_counts": {"VALID_RELATION": 2, "SAME_WRONG_RELATION_OTHER_NEIGHBOR": 0,
                                                 "OTHER_WRONG": 0 if rec else 1}}
    fail = {"status": "PARSE_FAIL", "category": None, "recovered": None, "resolved": None, "answer_counts": None}
    col = lambda rec: {"denominator": 1, "recovered": 1 if rec else 0, "technical_failures": {"A2": "PARSE_FAIL"},
                       "displacement": {k: (1 if (k == "VALID_RELATION") == rec else 0) if k in ("VALID_RELATION", "OTHER_WRONG") else 0
                                        for k in M.DISPLACEMENT},
                       "per_holder": {"A1": holder("VALID_RELATION" if rec else "OTHER_WRONG", rec), "A2": fail}}
    return {"query_id": qid, "mechanism": "WRONG_TURN_HOP2", "u": "9", "r": "off-label use", "step": 2,
            "holders": ["A1", "A2"], "same_wrong_possible": True,
            "cf": {n: {"before": int(n in before), "after": 0} for n in M.S36_CF},
            "pcf": {k: {"before": int(name in before), "after": 0} for k, name in M.S36_PCF},
            "before_holder_answers": {h: {"VALID_RELATION": 2, "SAME_WRONG_RELATION_OTHER_NEIGHBOR": 0, "OTHER_WRONG": 1}
                                      for h in ("A1", "A2")},
            "after": col(True), "reference_repeat": col(False),
            "no_answer": {"before": {"no_answer": 0, "success_episodes": 4, "rate": 0.0},
                          "after": {"no_answer": 0, "success_episodes": 3, "rate": 0.0}}}


def test_table5_treatment_only_no_delta_or_tau():
    s36 = {"status": "DESCRIPTIVE", "cases": [s36_case()], "run_commits": {"after": {"iv": "c1"}}}
    t = M.build_table5(s36)
    a = part(t, "a")
    assert a.header[-1] == "After control" and {r[-1] for r in a.rows} == {"no control (C = 0)"}
    cf3 = next(r for r in a.rows if r[3] == "CF3^Q")
    assert cf3[4:6] == [1, 0]
    headers = " ".join(h for p in t.parts for h in p.header)
    assert "ΔCF" not in headers and "τ" not in headers
    b = part(t, "b").rows[0]
    assert b[2:7] == [1, 1, 1.0, 0, 1] and b[13] == ["A2: PARSE_FAIL"]
    c = part(t, "c").rows
    assert c[1][5:10] == ["PARSE_FAIL", None, None, None, None]
    with pytest.raises(ValueError, match="DESCRIPTIVE"):
        M.build_table5({**s36, "status": "CONFIRMATORY"})


# ----------------------------------------------------------------------------------------- tables 9, 11, 12

def handcheck(marks):
    return [{"order": str(i + 1), "query_id": f"Q{i}", "relation_type": "t", "entity_name": "E", "entity_id": "1",
             "holders": "3", "holder_agents": "A1;A2;A3", "entity_in_T_q": "True", "graph_paths": "p",
             "biohopr_gold_size": "1", "biohopr_gold_list": "G", "mark": m} for i, m in enumerate(marks)]


def test_table9_marks_and_outcome_rule():
    b6 = {"bh_only_queries": 31, "provenance": {"git_commit": "c"}}
    t = M.build_table9([], handcheck(["VALID"] * 12 + ["QUESTIONABLE"] * 3), b6)
    assert part(t, "c").rows[0][:3] == [12, 3, 0] and part(t, "c").rows[0][-1] == "CLEAN"
    t = M.build_table9([], handcheck(["VALID"] * 10 + ["QUESTIONABLE"] * 5), b6)
    assert part(t, "c").rows[0][-1] == "NOT CLEAN"
    with pytest.raises(ValueError, match="valid mark"):
        M.build_table9([], handcheck(["VALID"] * 14 + [""]), b6)
    with pytest.raises(ValueError, match="15"):
        M.build_table9([], handcheck(["VALID"] * 14), b6)


LOG_FIXTURE = """## 2026-11-12 — S30 — Plan after D7: something
### C. Follow-up study
2. Two sheets.
3. Predictions (fixed now, before any follow-up episode exists):
   - P1 (original wording): (a) at least 5 of the 150; and (b) in at least 80%
     of those queries, the feature.
   - P2 (approved vs original): X ≥ 3.
   - Also reported, not part of P2: recall, no-answer rate
     (to show whether).
   Each prediction is reported as held or not held, whatever the result.
4. New manifests.

## 2026-11-13 — later entry
3. Predictions (fixed now, a different entry)
"""


def test_table11_quotes_c3_verbatim_and_not_run():
    t = M.build_table11(LOG_FIXTURE, "NOT CLEAN")
    assert t.status == "EXPLORATORY — NOT RUN" and t.sources == ["docs/decision_log.md"]
    rows = t.parts[0].rows
    assert [r[0] for r in rows] == ["P1 (original wording)", "P2 (approved vs original)", "Also reported, not part of P2"]
    assert rows[0][1] == ("P1 (original wording): (a) at least 5 of the 150; and (b) in at least 80% "
                          "of those queries, the feature.")
    assert rows[2][1] == "Also reported, not part of P2: recall, no-answer rate (to show whether)."
    assert {r[2] for r in rows} == {"Not run (decision log 2026-11-13, B1 NOT CLEAN)"}
    assert "Each prediction is reported as held or not held, whatever the result." in t.parts[0].notes[0]


def test_table11_refuses_missing_section_or_clean_b1():
    with pytest.raises(ValueError, match="B1 outcome"):
        M.build_table11(LOG_FIXTURE, "CLEAN")
    with pytest.raises(ValueError, match="entries start"):
        M.build_table11(LOG_FIXTURE.replace("Plan after D7", "Plan"), "NOT CLEAN")
    with pytest.raises(ValueError, match="C3"):
        M.build_table11(LOG_FIXTURE.replace("3. Predictions (fixed now, before", "3. Other (before"), "NOT CLEAN")


def ic_view(per_query):
    return {"queries": 3, "queries_with_opportunity": 2, "T_obs": 1, "E_T": 0.5, "T_2.5th": 0, "T_97.5th": 2,
            "P_T_ge_obs": 0.4, "P_T_le_obs": 0.9, "outcome": "AGREES", "S_obs": 3, "S_expected": 2.0,
            "agents": {"A1": {"opportunity": 2, "taken_and_opportunity": 1, "p": 0.5}}, "per_query": per_query}


def test_table12_ic_rows():
    pq = [{"query_id": "Q1", "A_q": ["A1"], "takers": [], "K_q": 0, "P_K_ge_3": 0.0, "CF3_Q_H1": 0},
          {"query_id": "Q2", "A_q": ["A1", "A2"], "takers": ["A1", "A2"], "K_q": 2, "P_K_ge_3": 0.0, "CF3_Q_H1": 0},
          {"query_id": "Q3", "A_q": ["A1"], "takers": ["A1"], "K_q": 1, "P_K_ge_3": 0.0, "CF3_Q_H1": 1}]
    ic = {"all_queries": ic_view(pq), "without_source_name_overlap": ic_view(pq[:1]), "provenance": {"commit": "c"}}
    t = M.build_table12(ic)
    assert [r[0] for r in part(t, "c").rows] == ["Q2", "Q3"]
    assert [r[10] for r in part(t, "a").rows] == ["outcome", "descriptive only"]
    assert t.status.startswith("EXPLORATORY") and "2026-11-13" in t.basis[0]


# ------------------------------------------------------------------------------------------ cross-checks

def mini_data():
    qs = [cfq("Q1", question=1, h1=1, rel3=1), cfq("Q2", rt="t2", tag="R2_AMBIGUOUS"), cfq("Q3", rt="t3", tag="R1_AMBIGUOUS")]
    cof = cofailure(qs)
    sha = "s" * 64
    strict = {"CF3^Q": 1, "CF4^Q": 0, "CF3^{Q,H1}": 1, "CF4^{Q,H1}": 0}
    b5_rows = [{"subset": "both", "group": "total", "CF3^Q": 1, "CF4^Q": 0, "CF3^{Q,H1}": 1}]
    prov = {"provenance": {"inputs": {"cofailure": {"sha256": sha}}}}
    return sha, {
        "cofailure": cof, "manifest": MANIFEST,
        "b1": copy.deepcopy(prov), "b6": copy.deepcopy(prov),
        "b2": {**copy.deepcopy(prov), "tables": {v: {"cofailure": {"strict": dict(strict)}} for v, _ in M.VIEWS}},
        "b5": {**copy.deepcopy(prov), "tables": {v: copy.deepcopy(b5_rows) for v, _ in M.VIEWS}},
        "b6_table": [{"view": v, "relation_type": "total", "CF3^BH": "0", "CF3^Q": "1"} for v, _ in M.VIEWS],
        "rp": {"provenance": {"inputs": {"original_cofailure": {"sha256": sha}}},
               "queries": [{"query_id": "Q1", "original_cf3_q": 1, "original_cf4_q": 0, "original_cf3_q_h1": 1}]},
        "ic": {"provenance": {"cofailure": {"sha256": sha}},
               **{v: {"per_query": [{"query_id": "Q1", "CF3_Q_H1": 1}]} for v, _ in M.VIEWS}},
        "s36": {"cases": [s36_case("Q1", {"CF3^Q", "CF3^Q grounded", "CF3^{Q,H1}", "PCF_REL3"})]},
        "candidates": [{"query_id": "Q1"}],
    }


def test_cross_check_passes_on_consistent_inputs():
    sha, data = mini_data()
    assert len(M.cross_check(data, sha)) == 6


@pytest.mark.parametrize("mutate, match", [
    (lambda d: d["b2"]["provenance"]["inputs"]["cofailure"].update(sha256="x"), "b2"),
    (lambda d: d["b2"]["tables"]["all_queries"]["cofailure"]["strict"].update({"CF3^Q": 2}), "B2 strict"),
    (lambda d: d["b6_table"][0].update({"CF3^Q": "0"}), "B6 total"),
    (lambda d: d["rp"]["queries"][0].update(original_cf3_q=0), "RP"),
    (lambda d: d["ic"]["all_queries"]["per_query"][0].update(CF3_Q_H1=0), "IC"),
    (lambda d: d["s36"]["cases"][0]["cf"]["CF3^Q"].update(before=0), "S36"),
    (lambda d: d["candidates"].append({"query_id": "Q2"}), "candidates"),
    (lambda d: d["manifest"].__setitem__("Q1", {**d["manifest"]["Q1"], "ambiguity_tag": "R1_AMBIGUOUS"}), "ambiguity"),
])
def test_cross_check_refuses_disagreement(mutate, match):
    sha, data = mini_data()
    data["manifest"] = copy.deepcopy(data["manifest"])
    mutate(data)
    with pytest.raises(ValueError, match=match):
        M.cross_check(data, sha)


# -------------------------------------------------------------------------------------- causal-word scan

def test_causal_scan_checks_wording_of_tables_1_to_5_only():
    data_cell = M.Table(4, "x", "X", "s", [], [], [M.Part("a", "p", "title", ["h"], [["arthritis due to LACC1"]])])
    M.scan_causal([data_cell])                                   # data cells are not scanned
    field_name = M.Table(2, "x", "X", "s", [], [], [M.Part("a", "p", "t", ["ERROR by §9.5 `cause` field"], [])])
    M.scan_causal([field_name])                                  # the §9.5 field name is exempt
    later = M.Table(12, "x", "X", "s", [], [], [M.Part("a", "p", "t", ["h"], [])], ["the rate explains it"])
    M.scan_causal([later])                                       # exploratory tables are not scanned
    bad = M.Table(5, "x", "X", "s", [], [], [M.Part("a", "p", "t", ["h"], [])], ["hiding led to recovery"])
    with pytest.raises(ValueError, match="causal"):
        M.scan_causal([bad])


# ------------------------------------------------------------------------------- provenance and writing

def git(repo, *args):
    subprocess.run(["git", "-c", "user.name=t", "-c", "user.email=t@example.invalid", "-c", "commit.gpgsign=false",
                    *args], cwd=repo, check=True, capture_output=True)


def test_provenance_tracks_code_commit_state(tmp_path):
    git(tmp_path, "init", "-q")
    (tmp_path / "scripts").mkdir()
    (tmp_path / "data").mkdir()
    (tmp_path / M.REPORT_SCRIPT).write_bytes(b"r\n")
    (tmp_path / "data/in.csv").write_bytes(b"a\n")           # bytes: write_text would add \r on Windows
    git(tmp_path, "add", ".")
    git(tmp_path, "commit", "-q", "-m", "one")
    (tmp_path / M.SCRIPT).write_bytes(b"s\n")                # untracked
    p = M.provenance(tmp_path, ["data/in.csv", "data"])
    assert p["code_committed"] is False and p["code"][M.SCRIPT]["tracked"] is False
    assert p["tracked_clean"] is True
    head = M.git(tmp_path, "rev-parse", "HEAD")
    assert p["inputs"]["data/in.csv"]["last_commit"] == head
    assert p["inputs"]["data/in.csv"]["sha256"] == M.sha256_bytes(b"a\n")
    assert p["inputs"]["data"]["sha256"] == M.sha256_bytes(f"data/in.csv\t{M.sha256_bytes(b'a\n')}\n".encode())
    git(tmp_path, "add", ".")
    git(tmp_path, "commit", "-q", "-m", "two")
    assert M.provenance(tmp_path, [])["code_committed"] is True
    (tmp_path / M.SCRIPT).write_bytes(b"changed\n")
    p = M.provenance(tmp_path, [])
    assert p["code_committed"] is False and p["tracked_clean"] is False


def test_write_outputs_files_idempotent_and_refuses_strangers(tmp_path):
    t = M.Table(1, "demo", "Demo", "Dataset description. Descriptive.", ["§7"], ["data/in.csv"],
                [M.Part("a", "one", "One", ["x", "y"], [[1, None]], ["note"]),
                 M.Part("b", "two", "Two", ["z"], [[0.25]])])
    prov = {"commit": "c" * 40, "tracked_clean": True, "code_committed": False,
            "code": {M.SCRIPT: {"unchanged_at_HEAD": False}, M.REPORT_SCRIPT: {"unchanged_at_HEAD": True}},
            "inputs": {"data/in.csv": {"sha256": "h", "last_commit": "c" * 40}}}
    out = tmp_path / "final"
    files = M.write_outputs(out, [t], prov, ["check"])
    assert sorted(p.name for p in out.iterdir()) == sorted([*files, "provenance.json"])
    assert (out / "table01a_one.csv").read_text(encoding="utf-8") == "x,y\n1,\n"
    md = (out / "table01_demo.md").read_text(encoding="utf-8")
    assert "PROVISIONAL" in md and "`scripts/38_final_tables.py`" in md and "c" * 40 in md
    first = {p.name: p.read_bytes() for p in out.iterdir()}
    M.write_outputs(out, [t], prov, ["check"])
    assert {p.name: p.read_bytes() for p in out.iterdir()} == first
    record = json.loads((out / "provenance.json").read_text(encoding="utf-8"))
    assert record["outputs"]["table01b_two.csv"] == M.sha256_bytes(b"z\n0.250000\n")
    (out / "stray.txt").write_text("x", encoding="utf-8")
    with pytest.raises(FileExistsError, match="stray.txt"):
        M.write_outputs(out, [t], prov, ["check"])
