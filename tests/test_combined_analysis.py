"""Tests for scripts/30_combined_analysis.py and the D7 parts of scripts/28_pilot_report.py
(tiny synthetic fixtures; no PrimeKG, no real run)."""
import importlib.util
import json
from pathlib import Path

import numpy as np
import pytest

from cofail_kg.evaluation.null_models import TRIALS, aggregate

ROOT = Path(__file__).resolve().parents[1]


def _load(name, filename):
    spec = importlib.util.spec_from_file_location(name, ROOT / "scripts" / filename)
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


C = _load("combined_analysis", "30_combined_analysis.py")
R = _load("pilot_report_d7", "28_pilot_report.py")
AGENTS = ["A1", "A2", "A3", "A4"]
NULLS = ("N1", "N1-H1", "N2")


def _flag(v):
    return {"cf3": v, "cf4": 0}


def _cofq(qid, h1=0, pcf_rel3=0, rel_cases=(), shortcut_cases=(), node_cases=(), shortcut3=0):
    return {"query_id": qid, "relation_type": "t", "ambiguity_tag": "NONE", "question": _flag(h1),
            "grounded": _flag(h1), "hop1_clean": _flag(h1), "benchmark": _flag(h1), "pcf_rel3": pcf_rel3,
            "pcf_rel4": 0, "pcf_node3": int(bool(node_cases)), "pcf_node4": 0, "pcf_shortcut3": shortcut3,
            "pcf_rel_cases": list(rel_cases), "pcf_node_cases": list(node_cases),
            "pcf_shortcut_cases": list(shortcut_cases)}


def _component(run_id, queries, overlap=(), agents=AGENTS):
    return {"run_id": run_id, "cofailure": {"agent_order": agents, "queries": queries,
                                            "source_name_overlap_queries": list(overlap)}}


def _pairwise_stub(results, agents):
    return [r["query_id"] for r in results]


# ------------------------------------------------------------------------------- combine_cofailure

def test_parse_component():
    assert C.parse_component("pilot_v1:pilot") == ("pilot_v1", "pilot")
    for bad in ("pilot_v1", ":pilot", "pilot_v1:"):
        with pytest.raises(ValueError):
            C.parse_component(bad)


def test_combine_cofailure_sums_totals_unions_overlap_and_sorts():
    a = _component("r1", [_cofq("q3", h1=1, pcf_rel3=1), _cofq("q1")], overlap=["q3"])
    b = _component("r2", [_cofq("q2", h1=1)], overlap=["q2"])
    cof = C.combine_cofailure([a, b], AGENTS, _pairwise_stub)
    assert [q["query_id"] for q in cof["queries"]] == ["q1", "q2", "q3"]
    assert cof["source_name_overlap_queries"] == ["q2", "q3"]
    assert cof["totals_all_queries"]["hop1_clean_cf3"] == 2 and cof["totals_all_queries"]["pcf_rel3"] == 1
    assert cof["totals_without_source_name_overlap"]["hop1_clean_cf3"] == 0
    assert cof["pairwise_all_queries"] == ["q1", "q2", "q3"]       # over the combined query set
    assert cof["pairwise_without_source_name_overlap"] == ["q1"]
    assert cof["run_id"] == "r1+r2"


def test_combine_cofailure_rejects_query_in_two_components_and_agent_mismatch():
    with pytest.raises(ValueError, match="in both"):
        C.combine_cofailure([_component("r1", [_cofq("q1")]), _component("r2", [_cofq("q1")])], AGENTS,
                            _pairwise_stub)
    with pytest.raises(ValueError, match="agent order"):
        C.combine_cofailure([_component("r1", [_cofq("q1")], agents=AGENTS[::-1])], AGENTS, _pairwise_stub)


# ---------------------------------------------------------------------------------- combine_nulls

def _null_query(qid, ones=slice(0, 0), observed=0, technical=()):
    ind = np.zeros((TRIALS, 2), dtype=np.int64)
    ind[ones, 0] = 1
    result = {"query_id": qid, "technical_failure_agents": list(technical),
              "nulls": {n: {"observed_cf3": observed, "observed_cf4": 0} for n in NULLS}}
    return {"result": result, "indicators": {n: ind.copy() for n in NULLS}}


def test_combined_null_uses_joint_trial_totals_not_sum_of_percentiles():
    # Each query alone: 3% of trials share -> p95 = 0. Jointly (disjoint trials): 6% -> p95 = 1.
    q1 = _null_query("q1", slice(0, 300), observed=1)
    q2 = _null_query("q2", slice(300, 600), observed=1)
    alone = [aggregate([q])["N1-H1"]["cf3"]["null_p95"] for q in (q1, q2)]
    assert alone == [0.0, 0.0]
    out = C.combine_nulls([q2, q1], set(), AGENTS, "r", aggregate)
    s = out["aggregate_all_queries"]["N1-H1"]["cf3"]
    assert s["null_p95"] == 1.0 and s["observed_total"] == 2 and s["query_count"] == 2
    assert [r["query_id"] for r in out["queries"]] == ["q1", "q2"]
    assert out["trials"] == TRIALS


def test_combined_null_subsets():
    qs = [_null_query("q1", observed=1), _null_query("q2", observed=1, technical=["A1"]),
          _null_query("q3", observed=1)]
    out = C.combine_nulls(qs, {"q3"}, AGENTS, "r", aggregate)
    assert out["aggregate_all_queries"]["N1"]["cf3"]["observed_total"] == 3
    assert out["aggregate_without_source_name_overlap"]["N1"]["cf3"]["query_count"] == 2
    assert out["aggregate_excluding_technical_failures"]["N1"]["cf3"]["query_count"] == 2


def test_check_component_nulls_accepts_exact_and_rejects_changed():
    qs = [_null_query("q1", slice(0, 700), observed=1), _null_query("q2")]
    stored = C._roundtrip(C.combine_nulls(qs, {"q2"}, AGENTS, "r1", aggregate))
    comp = {"run_id": "r1", "nulls": stored, "cofailure": {"source_name_overlap_queries": ["q2"]}}
    C.check_component_nulls(comp, qs, aggregate)
    changed = json.loads(json.dumps(stored))
    changed["aggregate_all_queries"]["N1-H1"]["cf3"]["null_p95"] = 99.0
    with pytest.raises(ValueError, match="aggregate_all_queries"):
        C.check_component_nulls({**comp, "nulls": changed}, qs, aggregate)
    # A different overlap list changes the stored subset aggregate -> rejected.
    with pytest.raises(ValueError):
        C.check_component_nulls({**comp, "cofailure": {"source_name_overlap_queries": []}}, qs, aggregate)


# ------------------------------------------------------------------- 28_pilot_report: D7 candidate flags

def _answer(path):
    return {"primary_path": path}


def _edge(u, label, v):
    return {"u": u, "label": label, "v": v}


def test_candidate_flags_lists_flagged_queries_with_mechanism():
    hop2 = {"node_id": "b", "relation": "off", "agent_count": 3,
            "per_agent": {a: [_answer([_edge("s", "r1", "b"), _edge("b", "off", "x")])] for a in AGENTS[:3]}}
    short = {"node_id": "s", "relation": "dp", "agent_count": 3,
             "per_agent": {a: [_answer([_edge("s", "dp", "y")])] for a in AGENTS[:3]}}
    hop1 = {"node_id": "s", "relation": "bad", "agent_count": 4,
            "per_agent": {a: [_answer([_edge("s", "bad", "c"), _edge("c", "r2", "z")])] for a in AGENTS}}
    two = {"node_id": "s", "relation": "x", "agent_count": 2, "per_agent": {}}  # below 3 agents: not listed
    cof = {"queries": [
        _cofq("q4", pcf_rel3=1, rel_cases=[hop1]),
        _cofq("q1", h1=1, pcf_rel3=1, rel_cases=[hop2, two]),
        _cofq("q2", pcf_rel3=1, rel_cases=[short], shortcut_cases=[short], shortcut3=1),
        _cofq("q3"),                                              # no flag: not listed
        _cofq("q5", node_cases=[{"node_id": "n", "agent_count": 3}]),
    ]}
    flags = R.candidate_flags(cof)
    assert [f["query_id"] for f in flags] == ["q1", "q2", "q4", "q5"]
    by = {f["query_id"]: f["events"] for f in flags}
    assert by["q1"] == ["REL (b, off) × 3 [WRONG_TURN_HOP2]"]
    assert by["q2"] == ["REL (s, dp) × 3 [SHORTCUT]", "SHORTCUT (s, dp) × 3 [SHORTCUT]"]
    assert by["q4"] == ["REL (s, bad) × 4 [WRONG_TURN_HOP1]"]
    assert by["q5"] == ["NODE n × 3 [OFF_PATH_NODE]"]


def test_load_combined_rejects_query_in_two_components(tmp_path):
    folder = tmp_path / "results/combined/x"
    folder.mkdir(parents=True)
    (folder / "components.json").write_text(json.dumps(
        {"components": {"r1": {"manifest": "m1"}, "r2": {"manifest": "m2"}}}))
    (folder / "cofailure.json").write_text(json.dumps({"agent_order": AGENTS, "queries": []}))
    (folder / "nulls.json").write_text(json.dumps({"agent_order": AGENTS}))
    line = json.dumps({"query_id": "q1", "ambiguity_tag": "NONE"}) + "\n"
    for m in ("m1", "m2"):
        for sub in ("data/processed/manifests", "data/agent_inputs"):
            (tmp_path / sub).mkdir(parents=True, exist_ok=True)
            (tmp_path / sub / f"{m}.jsonl").write_text(line)
    for run in ("r1", "r2"):
        for a in AGENTS:
            d = tmp_path / "results/runs" / run / "analysis/metrics" / a
            d.mkdir(parents=True)
            (d / "q1.json").write_text(json.dumps({"agent_id": a, "query_id": "q1", "attempt": 1}))
            (tmp_path / "results/runs" / run / f"q1__{a}__a1.json").write_text("{}")
    with pytest.raises(ValueError, match="another component"):
        R.load_combined("x", root=tmp_path)
