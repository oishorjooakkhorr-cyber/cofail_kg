"""Tests for scripts/28_pilot_report.py on tiny synthetic fixtures (no PrimeKG, no real run)."""
import importlib.util
import json
from pathlib import Path

import pytest

ROOT = Path(__file__).resolve().parents[1]
spec = importlib.util.spec_from_file_location("pilot_report", ROOT / "scripts/28_pilot_report.py")
R = importlib.util.module_from_spec(spec)
spec.loader.exec_module(R)

AGENTS = ["A1", "A2", "A3", "A4"]


def row(agent, q, status="SUCCESS", answers=(), found=True, attempt=1, **extra):
    base = {"agent_id": agent, "query_id": q, "attempt": attempt, "run_id": "t", "episode_status": status,
            "cause": "CONNECTION" if status == "ERROR" else None, "construction": "BRIDGE",
            "found_r1": found, "hop1_status": "H1_CLEAN" if found else "H1_NONE",
            "answers": list(answers), "bridge_rank": {}, "early_stop": False if status == "SUCCESS" else None,
            "budget_exhausted": False}
    base.update(extra)
    return base


def test_technical_counts_and_E():
    rows = {("A1", "q1"): row("A1", "q1"), ("A1", "q2"): row("A1", "q2", "ERROR"),
            ("A2", "q1"): row("A2", "q1", "PARSE_FAIL"), ("A2", "q2"): row("A2", "q2")}
    t = R.technical(rows, ["A1", "A2"])
    assert t["per_agent"]["A1"]["ERROR"] == 1 and t["per_agent"]["A1"]["error_causes"] == {"CONNECTION": 1}
    assert t["per_agent"]["A2"]["PARSE_FAIL"] == 1
    assert (t["technical_failures"], t["episodes"], t["E"]) == (2, 4, 0.5)


def test_unknown_status_is_an_error():
    with pytest.raises(ValueError):
        R.technical({("A1", "q1"): row("A1", "q1", "WEIRD")}, ["A1"])


def test_latest_attempt_selected_and_duplicate_rejected(tmp_path):
    d = tmp_path / "A1"
    d.mkdir()
    (d / "q1_a1.json").write_text(json.dumps(row("A1", "q1", attempt=1)))
    (d / "q1_a2.json").write_text(json.dumps(row("A1", "q1", attempt=2, status="ERROR")))
    rows = R.latest_rows(tmp_path, ["A1"])
    assert rows[("A1", "q1")]["attempt"] == 2
    (d / "q1_dup.json").write_text(json.dumps(row("A1", "q1", attempt=2)))
    with pytest.raises(ValueError):
        R.latest_rows(tmp_path, ["A1"])


@pytest.mark.parametrize("rank,expected", [(None, "NA"), (1, "1"), (2, "2–10"), (10, "2–10"), (50, "11–50"),
                                           (51, "51–100"), (101, ">100")])
def test_rank_bins(rank, expected):
    assert R.rank_bin(rank) == expected


def test_rank_below_one_is_error():
    with pytest.raises(ValueError):
        R.rank_bin(0)


def test_comparison_key_folds_case_whitespace_and_id_type():
    assert R.comparison_key(12, "  Foo   Bar ") == R.comparison_key(" 12", "foo bar")
    assert R.comparison_key("12", "foo") != R.comparison_key("13", "foo")
    assert R.comparison_key("x", "ﬁne") == R.comparison_key("x", "fine")  # NFKC ligature


def test_unresolved_diagnostic_reports_only_would_merge_groups():
    answers = [{"node_id": None, "submitted_index": i} for i in range(3)] + [{"node_id": "5", "submitted_index": 3}]
    rows = {("A1", "q1"): row("A1", "q1", answers=answers)}
    submitted = [{"id": 7, "name": "Foo"}, {"id": "7", "name": "foo "}, {"id": "8", "name": "Foo"},
                 {"id": "5", "name": "x"}]
    records = {("A1", "q1"): {"log_events": [{"event": "FINAL_PARSED", "parsed": {"answers": submitted}}]}}
    d = R.unresolved_diagnostic(rows, records, ["A1"])
    assert d["per_agent"]["A1"] == {"unresolved_retained": 3, "episodes_with_unresolved": 1}
    assert len(d["merge_groups"]) == 1
    assert [i["submitted_index"] for i in d["merge_groups"][0]["items"]] == [0, 1]


def _query(qid, rel="t1", tag="NONE", h1=0, q=0, pcf=0):
    flag = lambda v: {"cf3": v, "cf4": 0, "shared_entities": []}
    return {"query_id": qid, "relation_type": rel, "ambiguity_tag": tag, "question": flag(q),
            "grounded": flag(q), "hop1_clean": flag(h1), "benchmark": flag(q), "pcf_rel3": pcf, "pcf_rel4": 0,
            "pcf_node3": 0, "pcf_node4": 0, "pcf_shortcut3": 0}


def test_cf_counts_strata_and_total_check():
    qs = [_query("q1", h1=1, q=1, pcf=1), _query("q2", tag="R1_AMBIGUOUS"), _query("q3", h1=1, q=1)]
    man = {"q1": {"ambiguity_tag": "NONE"}, "q2": {"ambiguity_tag": "R1_AMBIGUOUS"}, "q3": {"ambiguity_tag": "NONE"}}
    c = R.cf_counts(qs)
    assert c["CF3^{Q,H1}"] == 2 and c["PCF_REL3"] == 1 and c["CF4^Q"] == 0
    s = {k: (n, v["CF3^Q"]) for k, n, v in R.strata(qs, man, "ambiguity_tag")}
    assert s == {"NONE": (2, 2), "R1_AMBIGUOUS": (1, 0)}
    totals = {k: c[name] for name, k in R.TOTAL_KEYS.items()}
    cof = {"queries": qs, "source_name_overlap_queries": ["q3"], "totals_all_queries": totals,
           "totals_without_source_name_overlap": {k: R.cf_counts(qs[:2])[n] for n, k in R.TOTAL_KEYS.items()}}
    R.check_totals(cof)
    cof["totals_all_queries"] = {**totals, "hop1_clean_cf3": 99}
    with pytest.raises(ValueError):
        R.check_totals(cof)


def _null(obs, p95):
    return {"cf3": {"observed_total": obs, "null_p95": p95, "null_mean": 0.5, "p": 0.01,
                    "observed_exceeds_null": obs > p95}}


def test_d6_quantities_and_flags():
    qs = [_query("q1", rel="t1", tag="R1_AMBIGUOUS", h1=1), _query("q2", rel="t2", tag="NONE", h1=1),
          _query("q3", rel="t1", tag="NONE")]
    rows = {}
    for q in ("q1", "q2", "q3"):
        for i, a in enumerate(AGENTS):
            # q3: only 2 agents found R1; q2: one agent found R1 only in an ERROR episode.
            found = not (q == "q3" and i >= 2)
            status = "ERROR" if (q == "q2" and i == 0) else "SUCCESS"
            rows[(a, q)] = row(a, q, status=status, found=found)
    data = {"cofailure": {"queries": qs}, "agents": AGENTS, "rows": rows,
            "nulls": {"aggregate_all_queries": {"N1-H1": _null(2, 1), "N1": _null(2, 1), "N2": _null(2, 2)}}}
    tech = R.technical(rows, AGENTS)
    d = R.d6_quantities(data, tech)
    assert d["E"] == (1, 12)
    assert d["H"] == (2, 3)
    assert d["H_success_only"] == (2, 3)
    assert d["N"] == 2 and d["P"] == 2
    assert d["O_H1"]["exceeds"] is True
    assert d["ordering_flag"] is True          # O_N1 above p95, O_N2 not above
    assert d["ambiguity_share"] == (1, 2) and d["ambiguity_flag"] is False


def test_d6_rejects_inconsistent_stored_comparison():
    bad = _null(2, 1)
    bad["cf3"]["observed_exceeds_null"] = False
    data = {"cofailure": {"queries": [_query("q1")]}, "agents": AGENTS,
            "rows": {(a, "q1"): row(a, "q1") for a in AGENTS},
            "nulls": {"aggregate_all_queries": {"N1-H1": bad, "N1": _null(0, 0), "N2": _null(0, 0)}}}
    with pytest.raises(ValueError):
        R.d6_quantities(data, R.technical(data["rows"], AGENTS))


def test_entity_names_and_path_rendering():
    rec = {"call_log": [
        {"success": True, "result": {"id": "1", "name": "S", "relations": []}},
        {"success": True, "result": {"items": [{"id": "2", "name": "B"}], "has_more": False}},
        {"success": False, "result": "Error: unknown entity ID 9."}]}
    names = R.entity_names([rec])
    assert names == {"1": "S", "2": "B"}
    path = [{"u": "1", "label": "r1", "v": "2"}, {"u": "2", "label": "r2", "v": "3"}]
    assert R.render_path(path, names) == "S [1] —r1→ B [2] —r2→ ? [3]"
    assert R.render_path([], names).startswith("(length 0")
    assert R.render_path(None, names).startswith("(no path")


@pytest.mark.parametrize("text", ["shared answers because of hubs", "this caused it", "due to fan-out",
                                  "hub drives errors", "the effect of order", "explains co-failure"])
def test_causal_pattern_hits(text):
    assert R.CAUSAL.search(text)


@pytest.mark.parametrize("text", ["drug:effect/phenotype:disease", "drug_effect label", "observed total"])
def test_causal_pattern_allows_node_types_and_labels(text):
    assert not R.CAUSAL.search(text)


def test_pairwise_matrix_symmetry_and_na():
    pairs = [{"agent_i": "A1", "agent_j": "A2", "numerator": 1, "denominator": 2},
             {"agent_i": "A1", "agent_j": "A3", "numerator": 0, "denominator": 0},
             {"agent_i": "A2", "agent_j": "A3", "numerator": 3, "denominator": 3}]
    m = R.pairwise_matrix(pairs, ["A1", "A2", "A3"])
    assert m[0] == ["A1", "—", "0.500 (1/2)", "NA (0/0)"]
    assert m[1][1] == "0.500 (1/2)"
