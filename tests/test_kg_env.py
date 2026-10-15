import json
import subprocess
import sys
from datetime import datetime

import pytest

from cofail_kg.agents.kg_env import KGEnvironment, ToolConfig
from cofail_kg.kg.primekg_index import EdgeConvention, PrimeKGIndex
from test_primekg_index import cache, index
from test_primekg_prepare import raw_graph


@pytest.fixture
def env(index):
    return KGEnvironment(index, ToolConfig(page_size=1, budget=30))


def test_inspection_lists_sorted_relations_and_unique_counts(env):
    assert env.inspect_entity("10") == {
        "id": "10", "name": "Alpha", "type": "drug", "relations": [
            {"label": "drug_effect", "display_labels": ["side effect"],
             "neighbor_types": ["effect/phenotype"], "neighbor_count": 1},
            {"label": "drug_protein", "display_labels": ["carrier", "enzyme", "target"],
             "neighbor_types": ["gene/protein"], "neighbor_count": 2},
        ]}
    assert env.inspect_entity("99")["relations"] == []


def test_pagination_is_unique_numeric_sorted_and_complete(env):
    first = env.get_neighbors("10", "drug_protein")
    last = env.get_neighbors("10", "drug_protein", page=2)
    assert first == {
        "items": [{"id": "2", "name": "Ｂeta  protein", "type": "gene/protein",
                   "display_labels": ["enzyme", "target"]}],
        "total_count": 2, "page": 1, "page_size": 1, "has_more": True}
    assert last["items"][0]["id"] == "30"
    assert last["items"][0]["display_labels"] == ["carrier"]
    assert last["total_count"] == 2 and last["page"] == 2 and not last["has_more"]
    assert [n["id"] for p in (first, last) for n in p["items"]] == ["2", "30"]
    assert env.get_neighbors("30", "drug_protein")["items"][0]["id"] == "10"
    assert env.get_neighbors("2", "protein_protein")["total_count"] == 1


def test_type_filter_and_empty_page(env):
    assert env.get_neighbors("10", "drug_protein", "gene/protein")["total_count"] == 2
    assert env.get_neighbors("10", "drug_protein", "disease") == {
        "items": [], "total_count": 0, "page": 1, "page_size": 1, "has_more": False}
    assert env.call_log[-1]["success"] is True
    assert env.get_neighbors("10", "drug_protein", "disease", page=2) == (
        "Error: page must be an integer from 1 to 1.")


@pytest.mark.parametrize("name,args,error", [
    ("inspect_entity", {"entity_id": "404"}, "Error: unknown entity ID 404."),
    ("get_neighbors", {"entity_id": "404", "relation": "x"}, "Error: unknown entity ID 404."),
    ("get_neighbors", {"entity_id": "10", "relation": "target"},
     "Error: entity 10 has no relation target."),
    ("get_neighbors", {"entity_id": "10", "relation": "drug_protein", "neighbor_type": "x"},
     "Error: unknown neighbor_type x."),
    ("inspect_entity", {}, "Error: missing argument entity_id."),
    ("get_neighbors", {"entity_id": "10"}, "Error: missing argument relation."),
    ("search", {}, "Error: unknown tool search."),
])
def test_exact_errors_are_logged_and_count_toward_budget(env, name, args, error):
    assert env.call(name, args) == error
    assert env.calls_used == 1
    assert env.call_log[0]["result"] == error
    assert env.call_log[0]["success"] is False


@pytest.mark.parametrize("page", [0, -1, 3, 1.0, "1", True, None, [], {}])
def test_invalid_pages_do_not_get_coerced(env, page):
    assert env.get_neighbors("10", "drug_protein", page=page) == (
        "Error: page must be an integer from 1 to 2.")


def test_budget_counts_errors_and_exhaustion_has_priority(index):
    env = KGEnvironment(index, ToolConfig(page_size=50, budget=2))
    env.inspect_entity("10")
    env.call("get_neighbors", {})
    for name in ("inspect_entity", "get_neighbors", "unknown"):
        assert env.call(name, {}) == "Tool budget exhausted. Give your final answer now."
    assert env.calls_used == 2
    assert len(env.call_log) == 5
    assert [entry["success"] for entry in env.call_log] == [True, False, False, False, False]


def test_log_preserves_full_arguments_results_and_timing(env):
    args = {"entity_id": "10", "relation": "drug_protein", "page": 2}
    result = env.call("get_neighbors", args)
    entry = env.call_log[0]
    assert entry["tool"] == "get_neighbors" and entry["arguments"] == args
    assert entry["result"] == result
    assert datetime.fromisoformat(entry["timestamp"]).utcoffset().total_seconds() == 0
    assert entry["elapsed_seconds"] >= 0
    json.dumps(entry, allow_nan=False)
    args["page"] = 999
    result["items"].clear()
    assert env.call_log[0]["arguments"]["page"] == 2
    assert env.call_log[0]["result"]["items"][0]["id"] == "30"


@pytest.mark.parametrize("page_size,budget", [(0, 30), (-1, 30), (True, 30),
                                                (1.5, 30), (50, -1), (50, True)])
def test_invalid_configuration_fails_before_any_call(page_size, budget):
    with pytest.raises(ValueError):
        ToolConfig(page_size=page_size, budget=budget)


def test_zero_budget_is_already_exhausted(index):
    env = KGEnvironment(index, ToolConfig(page_size=50, budget=0))
    assert env.inspect_entity("10") == "Tool budget exhausted. Give your final answer now."


def test_rejects_an_unfrozen_traversal_convention(cache):
    index = PrimeKGIndex(cache, convention=EdgeConvention("outgoing"))
    with pytest.raises(ValueError, match="either-direction"):
        KGEnvironment(index, ToolConfig(page_size=50, budget=30))


def test_direct_calls_report_missing_arguments(env):
    assert env.inspect_entity() == "Error: missing argument entity_id."
    assert env.get_neighbors() == "Error: missing argument entity_id."
    assert env.get_neighbors("10") == "Error: missing argument relation."


@pytest.mark.parametrize("field,value,error", [
    ("entity_id", None, "Error: unknown entity ID None."),
    ("entity_id", [], "Error: unknown entity ID []."),
    ("entity_id", {}, "Error: unknown entity ID {}."),
    ("relation", [], "Error: entity 10 has no relation []."),
    ("relation", None, "Error: entity 10 has no relation None."),
    ("neighbor_type", [], "Error: unknown neighbor_type []."),
    ("neighbor_type", {}, "Error: unknown neighbor_type {}."),
])
def test_malformed_field_values_use_protocol_errors(env, field, value, error):
    args = {"entity_id": "10", "relation": "drug_protein", field: value}
    assert env.call("get_neighbors", args) == error


def test_unused_argument_keys_are_logged_but_do_not_change_results(env):
    args = {"entity_id": "10", "unused": {"value": 1}}
    assert env.call("inspect_entity", args) == env.inspect_entity("10")
    assert env.call_log[0]["arguments"] == args


def test_unexpected_index_failure_is_logged_and_reraised(env, monkeypatch):
    def broken(_):
        raise RuntimeError("index failure")

    monkeypatch.setattr(env._index, "relations_of", broken)
    with pytest.raises(RuntimeError, match="index failure"):
        env.inspect_entity("10")
    assert env.calls_used == 1
    assert env.call_log[0]["success"] is False
    assert env.call_log[0]["internal_error"] == "RuntimeError: index failure"


def test_agent_modules_are_isolated_from_evaluation_imports_and_files(cache):
    # A fresh interpreter also catches transitive imports hidden by pytest's module cache.
    script = r'''
import sys

def audit(event, args):
    if event == "import" and args[0].startswith("cofail_kg.evaluation"):
        raise AssertionError("evaluation import")
    if event == "open" and isinstance(args[0], str):
        path = "/" + args[0].replace("\\", "/").lower().lstrip("/")
        if "/data/processed/" in path or "/results/" in path:
            raise AssertionError("evaluation file read: " + path)

sys.addaudithook(audit)
from cofail_kg.agents.kg_env import KGEnvironment, ToolConfig
from cofail_kg.agents.tool_schemas import TOOL_SCHEMAS
from cofail_kg.kg.primekg_index import PrimeKGIndex
env = KGEnvironment(PrimeKGIndex(sys.argv[1]), ToolConfig(page_size=1, budget=30))
assert env.inspect_entity("10")["id"] == "10"
assert env.get_neighbors("10", "drug_protein")["total_count"] == 2
assert env.get_neighbors("10", "drug_protein", page=2)["has_more"] is False
assert env.get_neighbors("10", "drug_protein", "disease")["total_count"] == 0
assert env.get_neighbors("10", "drug_protein", "unknown").startswith("Error:")
assert not any(n.startswith("cofail_kg.evaluation") for n in sys.modules)
'''
    subprocess.run([sys.executable, "-c", script, str(cache)],
                   capture_output=True, text=True, check=True)
