"""Tests for scripts/33_overlays.py (S33 treatment overlays) on the tiny S4 graph.

Tiny graph (tests/test_primekg_prepare.py): 10 –drug_protein– 2 (target, enzyme), 30 –drug_protein– 10
(carrier), 10 –drug_effect– 40 (side effect), 2 –protein_protein– 2 (self loop), 99 isolated.
Synthetic query: s = 10, R1 = {drug_protein}, B_q = {2}, R2 = {protein_protein}, T_q = {2};
the wrong turn to block is drug_effect at 10.
"""
import importlib.util
import json
from pathlib import Path

import pytest

from test_primekg_index import cache, index
from test_primekg_prepare import raw_graph
from cofail_kg.agents.kg_env import Overlay, load_overlays

ROOT = Path(__file__).resolve().parents[1]
spec = importlib.util.spec_from_file_location("s33_overlays", ROOT / "scripts/33_overlays.py")
M = importlib.util.module_from_spec(spec)
spec.loader.exec_module(M)

REF = {"query_id": "Q1", "s": "10", "B_q": ["2"], "T_q": ["2"]}
CASE = ("Q1", "10", "drug_effect", "WRONG_TURN_HOP1")


def candidate(**over):
    base = {"query_id": "Q1", "candidate": True, "feature_u": "10", "feature_r": "drug_effect",
            "mechanism": "WRONG_TURN_HOP1", "R1": ["drug_protein"], "R2": ["protein_protein"],
            "shared_entity_ids": {"40"}}
    return base | over


def test_build_case_hides_only_the_feature_and_keeps_a_route(index):
    entry, overlay = M.build_case(CASE, REF, candidate(), index)
    assert overlay == {"query_id": "Q1", "hide_labels": [["10", "drug_effect"]], "hide_edges": []}
    assert entry["hidden_edges"] == [["10", "drug_effect", "40"]] and entry["hidden_edge_count"] == 1
    assert entry["valid_bridges_before"] == entry["valid_bridges_after"] == ["2"]
    assert entry["valid_route_after"] and entry["only_intended_edges_hidden"]
    assert entry["arm"] == "treatment" and entry["control"] is None
    assert entry["checked_nodes"] == 3  # u = s = 10, its drug_effect neighbour 40, bridge 2 (40 again shared)


def test_no_valid_route_after_block_stops(index):
    case = ("Q1", "10", "drug_protein", "WRONG_TURN_HOP1")
    with pytest.raises(ValueError, match="no valid route remains"):
        M.build_case(case, REF, candidate(feature_r="drug_protein"), index)


def test_case_must_equal_the_s31_feature(index):
    with pytest.raises(ValueError, match="S31 feature"):
        M.build_case(CASE, REF, candidate(feature_u="2"), index)
    with pytest.raises(ValueError, match="not a candidate"):
        M.build_case(CASE, REF, candidate(candidate=False), index)


def test_no_route_in_unmodified_graph_stops(index):
    with pytest.raises(ValueError, match="unmodified"):
        M.build_case(CASE, {**REF, "T_q": ["30"]}, candidate(), index)


def test_valid_bridges(index):
    assert M.valid_bridges(index, REF, ["drug_protein"], ["protein_protein"], None) == ["2"]
    blocked = Overlay("Q1", hide_edges=(("2", "protein_protein", "2"),))
    assert M.valid_bridges(index, REF, ["drug_protein"], ["protein_protein"], blocked) == []


def test_expected_hidden():
    n_r = {"40", "41"}
    assert M.expected_hidden("10", "x", "10", "x", n_r) == n_r
    assert M.expected_hidden("40", "x", "10", "x", n_r) == {"10"}
    assert M.expected_hidden("40", "y", "10", "x", n_r) == set()
    assert M.expected_hidden("50", "x", "10", "x", n_r) == set()


def test_check_catches_an_overlay_that_hides_something_else(index):
    wrong = Overlay("Q1", hide_labels=(("10", "drug_effect"), ("2", "protein_protein")))
    with pytest.raises(ValueError, match="2/protein_protein (hides|unexpectedly unavailable)"):
        M.check_only_intended(index, wrong, "10", "drug_effect", ["10", "40", "2"])


def test_check_handles_partial_hiding_and_mirrors(index):
    result = M.check_only_intended(index, Overlay("Q1", hide_labels=(("30", "drug_protein"),)),
                                   "30", "drug_protein", ["30", "10", "2"])
    assert result["hidden_edges"] == [["30", "drug_protein", "10"]]


def test_agent_side_overlay_file_has_only_overlay_keys(tmp_path, index):
    _, overlay = M.build_case(CASE, REF, candidate(), index)
    path = tmp_path / "overlays.jsonl"
    M.write_once(path, M.jsonl([overlay]))
    assert set(json.loads(path.read_text(encoding="utf-8").splitlines()[0])) == {"query_id", "hide_labels",
                                                                                 "hide_edges"}
    assert load_overlays(path)["Q1"].hide_labels == (("10", "drug_effect"),)
    M.write_once(path, M.jsonl([overlay]))  # identical re-run allowed
    with pytest.raises(FileExistsError):
        M.write_once(path, "other\n")


def test_markdown_row_per_case(index):
    entry, _ = M.build_case(CASE, REF, candidate(), index)
    md = M.to_markdown([entry], {"git_commit": "abc", "git_tracked_clean": True,
                                 "overlay_file": {"path": "data/agent_inputs/x.jsonl", "sha256": "f" * 64}})
    assert "| Q1 | WRONG_TURN_HOP1 | drug_effect at 10 | 1 | 2 → 2 |" in md
