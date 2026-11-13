"""Tests for scripts/47_s34_smoke_report.py on the tiny S4 graph (see tests/test_kg_overlay.py).

Tiny graph: 10 –drug_protein– 2, 30 –drug_protein– 10, 10 –drug_effect– 40, 2 –protein_protein– 2, 99 isolated.
"""
import importlib.util
from pathlib import Path

import pytest

from test_primekg_index import cache, index  # noqa: F401 (fixtures)
from test_primekg_prepare import raw_graph  # noqa: F401 (fixture)
from cofail_kg.agents.kg_env import BUDGET_EXHAUSTED, KGEnvironment, Overlay, ToolConfig

ROOT = Path(__file__).resolve().parents[1]
spec = importlib.util.spec_from_file_location("s34", ROOT / "scripts/47_s34_smoke_report.py")
M = importlib.util.module_from_spec(spec)
spec.loader.exec_module(M)

OV = Overlay("Q1", hide_labels=(("10", "drug_protein"),))


def logged(index, calls, overlay):
    """A call log as KGEnvironment records it."""
    e = KGEnvironment(index, ToolConfig(page_size=50, budget=100), overlay=overlay, query_id="Q1")
    for tool, args in calls:
        e.call(tool, args)
    return {"query_id": "Q1", "agent_id": "A", "call_log": e.call_log}


CALLS = [("inspect_entity", {"entity_id": "10"}),
         ("get_neighbors", {"entity_id": "10", "relation": "drug_protein"}),
         ("get_neighbors", {"entity_id": "10", "relation": "drug_effect"}),
         ("inspect_entity", {"entity_id": "40"})]


def test_differences_from_the_original_are_exactly_the_overlay(index):
    original = logged(index, CALLS, None)
    smoke = logged(index, CALLS, OV)
    out = M.compare_episode(smoke, original, index, 50, OV)
    assert out["calls"] == 4 and out["same_calls_as_original"] == 4
    assert out["identical_to_original"] == 2 and out["different_from_original"] == [0, 1]
    assert out["different_and_not_explained_by_overlay"] == []
    text = [c["description"] for c in out["calls_changed_by_overlay"]]
    assert text[0] == "inspect_entity(10): label `drug_protein` removed (2 neighbours)"
    assert text[1].startswith("get_neighbors(10, 'drug_protein'): 2 → 'Error: entity 10 has no relation")


def test_recorded_output_must_equal_the_overlay_replay(index):
    smoke = logged(index, CALLS[:1], None)    # recorded without the overlay the run claims
    with pytest.raises(ValueError, match="differs from the overlay replay"):
        M.compare_episode(smoke, logged(index, CALLS[:1], None), index, 50, OV)


def test_budget_messages_are_skipped_and_new_calls_are_not_compared(index):
    smoke = logged(index, CALLS[2:], OV)
    smoke["call_log"].append({"tool": "inspect_entity", "arguments": {"entity_id": "2"}, "success": False,
                              "result": BUDGET_EXHAUSTED})
    out = M.compare_episode(smoke, logged(index, CALLS[:1], None), index, 50, OV)
    assert out["calls"] == 2 and out["same_calls_as_original"] == 0


def test_navigation_flags():
    record = {"call_log": [
        {"tool": "get_neighbors", "success": True, "arguments": {"entity_id": "1", "relation": "r1"},
         "result": {"items": [{"id": "10"}]}},
        {"tool": "get_neighbors", "success": False, "arguments": {"entity_id": "10", "relation": "off-label use"},
         "result": "Error: entity 10 has no relation off-label use."}]}
    nav = M.navigation(record, "1", ["r1"], "10", "off-label use")
    assert nav == {"reached_u_from_s_via_R1": True,
                   "asked_u_for_hidden_label": ["Error: entity 10 has no relation off-label use."]}
    assert M.navigation(record, "1", ["other"], "10", "x") == {"reached_u_from_s_via_R1": False,
                                                              "asked_u_for_hidden_label": []}
