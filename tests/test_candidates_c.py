"""Tests for scripts/30_candidates_c.py (D7 quantity C) on a tiny synthetic graph."""
import importlib.util
from pathlib import Path

import pytest

ROOT = Path(__file__).resolve().parents[1]
spec = importlib.util.spec_from_file_location("candidates_c", ROOT / "scripts/30_candidates_c.py")
M = importlib.util.module_from_spec(spec)
spec.loader.exec_module(M)

TYPES = {"1": "gene", "2": "disease", "3": "disease", "4": "disease", "5": "disease",
         "10": "drug", "11": "drug", "12": "drug", "13": "drug", "14": "drug", "15": "drug", "16": "drug"}
# s=1 (gene) -dp-> diseases 2,3,4,5 ; disease -ind-> drugs (valid) ; disease -off-> drugs (wrong turn)
EDGES = [("1", "dp", "2"), ("1", "dp", "3"), ("1", "dp", "4"), ("1", "pp", "5"),
         ("2", "ind", "10"), ("2", "off", "11"), ("2", "off", "12"), ("2", "off", "13"), ("2", "off", "14"),
         ("3", "off", "11"), ("3", "off", "12"), ("3", "off", "13"),
         ("4", "off", "15"),
         ("5", "off", "11"), ("5", "off", "12"), ("5", "off", "13"), ("5", "off", "16")]


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
        return {"type": TYPES[node]}


REF = {"query_id": "q", "s": "1", "B_q": ["2", "3", "4"], "T_q": ["10"], "Type_T": "drug"}


def _case(node, label, n_agents, path):
    agents = [f"A{i}" for i in range(n_agents)]
    return {"node_id": node, "relation": label, "agent_count": n_agents, "agents": agents,
            "per_agent": {a: [{"primary_path": path}] for a in agents}}


HOP2_PATH = [{"u": "1", "label": "dp", "v": "2"}, {"u": "2", "label": "off", "v": "11"}]


def _query(rel_cases=(), shortcut_cases=(), h1=1):
    return {"query_id": "q", "relation_type": "t", "ambiguity_tag": "NONE", "hop1_clean": {"cf3": h1},
            "R1": ["dp"], "R2": ["ind"], "pcf_rel_cases": list(rel_cases),
            "pcf_shortcut_cases": list(shortcut_cases), "pcf_rel3": 1, "pcf_node3": 0, "pcf_shortcut3": 0}


def _records(*opened_pairs, inspected=()):
    calls = [{"tool": "get_neighbors", "arguments": {"entity_id": n, "relation": l}} for n, l in opened_pairs]
    calls += [{"tool": "inspect_entity", "arguments": {"entity_id": n}} for n in inspected]
    return [{"call_log": calls}]


def test_valid_route_and_hiding():
    g = M.Graph(FakeKG())
    assert M.valid_route_remains(g, REF, ["dp"], ["ind"], None)
    assert M.valid_route_remains(g, REF, ["dp"], ["ind"], ("2", "off"))   # off ∉ R2
    assert not M.valid_route_remains(g, REF, ["dp"], ["ind"], ("2", "ind"))  # only route through 2
    assert not M.valid_route_remains(g, REF, ["dp"], ["ind"], ("1", "dp"))
    assert M.hidden("10", "2", "ind", ("2", "ind")) and not M.hidden("10", "2", "ind", ("3", "ind"))


def test_choose_feature_most_agents_then_earliest():
    q = _query(rel_cases=[_case("2", "off", 3, HOP2_PATH), _case("1", "dp", 4, HOP2_PATH),
                          _case("3", "x", 2, HOP2_PATH)])
    f = M.choose_feature(q)
    assert (f["u"], f["r"], f["agent_count"], f["mechanism"]) == ("1", "dp", 4, "WRONG_TURN_HOP1")
    tie = _query(rel_cases=[_case("2", "off", 3, HOP2_PATH), _case("1", "dp", 3, HOP2_PATH)])
    assert M.choose_feature(tie)["u"] == "1"                     # step 1 is earlier than step 2
    assert M.choose_feature(_query()) is None


def test_hop2_controls_same_label_unused_and_branch_degree():
    g = M.Graph(FakeKG())
    q = _query(rel_cases=[_case("2", "off", 3, HOP2_PATH)])
    # Node 3 (bd 3) was opened with `off` by an agent; node 4 (bd 1) unused; node 5 is hop-1 only via `pp`.
    # inspect_entity on node 4 does not count as opening (4, off) (researcher's reading of "used").
    r = M.evaluate(q, REF, "CONSISTENT", _records(("3", "off"), inspected=["4"]), g)
    assert r["candidate"] and r["feature"]["mechanism"] == "WRONG_TURN_HOP2"
    ctl = r["controls"]
    assert ctl["treatment_branch_degree"] == 4
    assert (ctl["slots"], ctl["slots_opened_by_an_agent"]) == (2, 1)   # node 5 (via `pp`, not R1) excluded
    assert [(c["node"], c["label"]) for c in ctl["closest"]] == [("4", "off")]
    assert ctl["within_25pct"] == 0                        # 1 vs 4: outside ±25%, nearest still counts
    assert r["has_matched_control"] is True


def test_no_control_when_all_used_and_not_consistent():
    g = M.Graph(FakeKG())
    q = _query(rel_cases=[_case("2", "off", 3, HOP2_PATH)])
    r = M.evaluate(q, REF, "CONSISTENT", _records(("3", "off"), ("4", "off")), g)
    assert r["has_matched_control"] is False
    assert M.evaluate(q, REF, "INCONSISTENT", [], g)["reason"] == "NOT_CONSISTENT"
    assert M.evaluate(_query(), REF, "CONSISTENT", [], g)["reason"] == "NO_SHARED_FEATURE"


def test_block_removing_only_route_is_not_candidate():
    g = M.Graph(FakeKG())
    path = [{"u": "1", "label": "dp", "v": "2"}, {"u": "2", "label": "ind", "v": "10"}]
    q = _query(rel_cases=[_case("2", "ind", 3, path)])
    assert M.evaluate(q, REF, "CONSISTENT", [], g)["reason"] == "NO_VALID_ROUTE_AFTER_BLOCK"


def test_shortcut_controls_are_other_labels_at_s_reaching_type_t():
    g = M.Graph(FakeKG())
    ref = {**REF, "Type_T": "disease"}
    path = [{"u": "1", "label": "pp", "v": "5"}]
    q = _query(rel_cases=[_case("1", "pp", 3, path)], shortcut_cases=[_case("1", "pp", 3, path)])
    q["R1"] = ["dp"]
    r = M.evaluate(q, ref, "CONSISTENT", [], g)
    assert r["feature"]["mechanism"] == "SHORTCUT"
    assert r["controls"]["eligible"] == 0                  # the only other label at s is dp ∈ R1
    assert r["has_matched_control"] is False


def test_hop2_same_label_only_no_fallback_to_other_labels():
    g = M.Graph(FakeKG())
    path = [{"u": "1", "label": "dp", "v": "2"}, {"u": "2", "label": "ind2", "v": "10"}]
    # Treatment label `ind2` exists nowhere else at hop 1, so no control even though 3 and 4 have `off`.
    q = _query(rel_cases=[_case("2", "ind2", 3, path)])
    q["R2"] = ["ind"]
    r = M.evaluate(q, REF, "CONSISTENT", [], g)
    assert r["candidate"] and r["controls"]["slots"] == 0 and r["has_matched_control"] is False


def test_opened_reads_get_neighbors_pairs_and_nodes():
    pairs, nodes = M.opened(_records(("7", "a"), inspected=["8"]) +
                            [{"call_log": [{"tool": "get_neighbors", "arguments": {"entity_id": 9}}]}])
    assert pairs == {("7", "a")} and nodes == {"7", "8", "9"}


def test_mixed_mechanism_event_is_an_error():
    case = _case("2", "off", 3, HOP2_PATH)
    case["per_agent"]["A0"] = [{"primary_path": [{"u": "2", "label": "off", "v": "11"}]}]
    with pytest.raises(ValueError, match="mechanisms"):
        M.choose_feature(_query(rel_cases=[case]))
