"""Tests for scripts/31_candidates.py (S31 candidate list) on a tiny synthetic graph."""
import csv
import importlib.util
import io
from pathlib import Path

import pytest

ROOT = Path(__file__).resolve().parents[1]
spec = importlib.util.spec_from_file_location("s31_candidates", ROOT / "scripts/31_candidates.py")
M = importlib.util.module_from_spec(spec)
spec.loader.exec_module(M)

TYPES = {"1": "gene", "2": "disease", "3": "disease", "4": "disease",
         "10": "drug", "11": "drug", "12": "drug", "13": "drug"}
# s=1 -dp-> 2,3,4 ; 2 -ind-> 10 (valid), 3 -ind-> 10 (valid) ; 2 -off-> 11,12 (wrong turn) ; 4 -off-> 13
EDGES = [("1", "dp", "2"), ("1", "dp", "3"), ("1", "dp", "4"),
         ("2", "ind", "10"), ("3", "ind", "10"), ("2", "off", "11"), ("2", "off", "12"), ("4", "off", "13")]
NAMES = {n: f"N{n}" for n in TYPES}


class FakeKG:
    def neighbors(self, node, label=None):
        out = set()
        for x, l, y in EDGES:
            if label is not None and l != label:
                continue
            if x == node:
                out.add(y)
            elif y == node:
                out.add(x)
        return [{"id": n} for n in sorted(out, key=int)]

    def relations_of(self, node):
        return [{"label": l} for l in sorted({l for x, l, y in EDGES if node in (x, y)})]

    def get_node(self, node):
        return {"type": TYPES[node], "name": NAMES[node]}


REF = {"query_id": "q", "s": "1", "B_q": ["2", "3"], "T_q": ["10"], "Type_T": "drug"}
PATH = [{"u": "1", "label": "dp", "v": "2"}, {"u": "2", "label": "off", "v": "11"}]
AGENTS = ["A0", "A1", "A2"]
FEATURE = {"u": "2", "r": "off", "agent_count": 3, "agents": AGENTS, "mechanism": "WRONG_TURN_HOP2",
           "earliest_step": 2}


def _query(qid="q", h1=1, pcf=1, node=0, shared=("11",)):
    case = {"node_id": "2", "relation": "off", "agent_count": 3, "agents": AGENTS,
            "per_agent": {a: [{"primary_path": PATH}] for a in AGENTS}}
    block = {"cf3": 1, "shared_entities": [{"entity_id": e, "agent_count": 3} for e in shared]}
    return {"query_id": qid, "relation_type": "t", "ambiguity_tag": "R2_AMBIGUOUS", "s": "1",
            "R1": ["dp"], "R2": ["ind"], "question": block, "hop1_clean": {**block, "cf3": h1},
            "pcf_rel3": pcf, "pcf_node3": node, "pcf_shortcut3": 0,
            "pcf_rel_cases": [case] if pcf else [], "pcf_shortcut_cases": []}


def _d7(**over):
    row = {"query_id": "q", "status": "CONSISTENT", "candidate": True, "feature": dict(FEATURE),
           "has_matched_control": False,
           # the graph has one same-label hop-1 slot (node 4, label off); here an agent opened it
           "controls": {"treatment_branch_degree": 2, "slots": 1, "slots_opened_by_an_agent": 1,
                        "eligible": 0, "within_25pct": 0, "closest": []}}
    row.update(over)
    return row


def _build(q=None, ref=REF, status="CONSISTENT", d7=None, overlap=()):
    g = M.C30.Graph(FakeKG())
    return M.build_row(q or _query(), ref, status, d7 or _d7(), g, set(overlap), lambda n: NAMES[n])


def test_flagged_selects_h1_or_pcf_and_refuses_node_cases():
    qs = [_query("b", h1=0, pcf=1), _query("a", h1=1, pcf=0), _query("c", h1=0, pcf=0)]
    assert [q["query_id"] for q in M.flagged(qs)] == ["a", "b"]
    with pytest.raises(NotImplementedError):
        M.flagged([_query(node=1)])


def test_row_for_candidate_without_control():
    row = _build()
    assert row["candidate"] is True and row["valid_route_after_block"] is True
    assert (row["mechanism"], row["feature_u"], row["feature_r"], row["feature_step"]) == ("WRONG_TURN_HOP2", "2", "off", 2)
    assert row["treatment_branch_degree"] == 2 and row["valid_bridges_after_block"] == 2
    assert row["has_matched_control"] is False and row["control_1"] == row["control_3"] == ""
    assert row["shared_entities_q"] == "11 N11 (3)" and row["s_name"] == "N1"


def test_valid_bridges_drop_when_the_only_route_label_is_hidden():
    g = M.C30.Graph(FakeKG())
    assert M.valid_bridges(g, REF, ["dp"], ["ind"], None) == ["2", "3"]
    assert M.valid_bridges(g, REF, ["dp"], ["ind"], ("2", "ind")) == ["3"]
    assert M.valid_bridges(g, REF, ["dp"], ["ind"], ("1", "dp")) == []


def test_controls_carried_over_up_to_three():
    closest = [{"node": n, "label": "off", "branch_degree": 1} for n in ("3", "4", "10", "11")]
    d7 = _d7(has_matched_control=True,
             controls={"treatment_branch_degree": 2, "slots": 1, "slots_opened_by_an_agent": 0,
                       "eligible": 4, "within_25pct": 0, "closest": closest})
    # graph has exactly one same-label slot at hop 1 (node 4); d7 slot count must agree
    row = _build(d7=d7)
    assert row["control_1"] == "(3 N3, off) bd=1" and row["control_3"] == "(10 N10, off) bd=1"
    assert row["has_matched_control"] is True and row["eligible_controls"] == 4


def test_disagreements_with_d7_stop():
    with pytest.raises(ValueError, match="feature"):
        _build(d7=_d7(feature={**FEATURE, "r": "other"}))
    with pytest.raises(ValueError, match="valid route"):
        _build(d7=_d7(candidate=False))
    with pytest.raises(ValueError, match="slots"):
        _build(d7=_d7(controls={"treatment_branch_degree": 2, "slots": 5, "slots_opened_by_an_agent": 0,
                                "eligible": 0, "within_25pct": 0, "closest": []}))
    with pytest.raises(ValueError, match="status"):
        _build(status="INCONSISTENT")
    with pytest.raises(ValueError, match="do not match"):
        _build(ref={**REF, "s": "2"})


def test_not_consistent_query_is_listed_without_feature():
    row = _build(status="INCONSISTENT", d7={"query_id": "q", "status": "INCONSISTENT", "candidate": False,
                                            "reason": "NOT_CONSISTENT"})
    assert row["candidate"] is False and row["reason"] == "NOT_CONSISTENT" and row["mechanism"] == ""


def test_no_valid_route_in_unmodified_graph_stops():
    with pytest.raises(ValueError, match="unmodified"):
        _build(ref={**REF, "T_q": ["13"]})


def test_source_name_overlap_flag_and_csv_columns():
    row = _build(overlap=["q"])
    assert row["source_name_overlap"] is True
    parsed = list(csv.DictReader(io.StringIO(M.csv_text([row]))))
    assert list(parsed[0]) == M.FIELDS and parsed[0]["query_id"] == "q"


def test_write_once(tmp_path):
    p = tmp_path / "x" / "a.csv"
    M.write_once(p, "one\n")
    M.write_once(p, "one\n")  # identical re-run allowed
    with pytest.raises(FileExistsError):
        M.write_once(p, "two\n")


def test_markdown_lists_every_row_and_counts():
    rows = [_build(), {**_build(), "query_id": "r", "candidate": False, "has_matched_control": False}]
    md = M.to_markdown(rows, {"git_commit": "abc", "git_tracked_clean": True})
    assert "| q |" in md and "| r |" in md and "Candidates: 1 of 2" in md and "(C): 0" in md
