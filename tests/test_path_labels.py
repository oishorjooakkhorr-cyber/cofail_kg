"""S18 protocol §14 cases use raw synthetic calls and the real S12 utilities."""

import copy
import random

import pytest

from cofail_kg.evaluation.answer_labels import label_answers
from cofail_kg.evaluation.normalize import AgentResolution
from cofail_kg.evaluation.path_labels import label_paths


TYPES = {"1": "drug", "2": "gene/protein", "3": "disease", "4": "drug",
         "5": "gene/protein", "6": "drug", "7": "drug", "8": "drug",
         "9": "drug", "10": "disease"}
SPEC = {"R1": ["r1"], "R2": ["r2"]}


class KG:
    def get_node(self, node):
        return {"id": node, "name": f"N{node}", "type": TYPES[node]}


def nb(u, relation, ids, *, success=True, **arguments):
    return {"tool": "get_neighbors", "success": success,
            "arguments": {"entity_id": u, "relation": relation, "page": 1, **arguments},
            "result": {"items": [KG().get_node(i) for i in ids],
                       "has_more": False, "total_count": len(ids)} if success else "Error"}


def inspect(node):
    return {"tool": "inspect_entity", "success": True,
            "arguments": {"entity_id": node}, "result": KG().get_node(node)}


def evaluate(log, ids=("3",), **changes):
    # The full synthetic KG includes both gold and alternative valid targets,
    # including items on pages the agent has not requested.
    q = {"query_id": "q", "s": "1", "Type_B": "gene/protein", "Type_T": "disease",
         "construction": "BRIDGE", "A_star_q": ["3"], "G_q": ["3"],
         "T_q_gold_bridges": ["3"], "T_q": ["3", "10"], **changes}
    answers = [AgentResolution(node) for node in ids]
    record = {"query_id": "q", "call_log": log, "ignored_tool_calls": []}
    before = copy.deepcopy((record, q, SPEC, answers))
    result = label_paths(answers, record, q, SPEC, KG())
    assert (record, q, SPEC, answers) == before
    assert len(result["answers"]) == len(ids)
    labels_a = label_answers(answers, q, consistent=True)
    assert all(not (a == "OFF_QUESTION" and b["label_b"] == "SUPPORTED")
               for a, b in zip(labels_a, result["answers"]))
    result["labels_a"] = labels_a
    return result


@pytest.mark.parametrize("bridge,target,label_a", [("2", "3", "GOLD"), ("5", "10", "ALT_VALID")])
def test_supported_including_non_gold_bridge(bridge, target, label_a):
    result = evaluate([nb("1", "r1", [bridge]), nb(bridge, "r2", [target])], [target])
    item = result["answers"][0]
    assert item["label_b"] == "SUPPORTED"
    assert item["reason_codes"] == item["primary_reason_codes"] == []
    assert [(e["u"], e["label"], e["v"]) for e in item["primary_path"]] == [
        ("1", "r1", bridge), (bridge, "r2", target)]
    assert result["labels_a"] == [label_a]


@pytest.mark.parametrize("log,target,codes", [
    ([nb("1", "r1", ["3"])], "3", ["SHORTCUT"]),
    ([nb("1", "bad", ["2"]), nb("2", "r2", ["3"])], "3", ["WRONG_RELATION_HOP1"]),
    ([nb("1", "r1", ["2"]), nb("2", "bad", ["3"])], "3", ["WRONG_RELATION_HOP2"]),
    ([nb("1", "r1", ["4"]), nb("4", "r2", ["3"])], "3", ["WRONG_BRIDGE_TYPE"]),
    ([nb("1", "r1", ["2"]), nb("2", "r2", ["4"])], "4", ["WRONG_TARGET_TYPE"]),
    ([nb("1", "r1", ["2"]), nb("2", "r2", ["4"]), nb("4", "r2", ["3"])],
     "3", ["WRONG_HOP_COUNT"]),
    ([inspect("1")], "1", ["WRONG_HOP_COUNT"]),
    ([nb("1", "r1", ["4"])], "4", ["WRONG_HOP_COUNT", "WRONG_TARGET_TYPE"]),
])
def test_invalid_paths_each_reason(log, target, codes):
    item = evaluate(log, [target])["answers"][0]
    assert item["label_b"] == "PATH_INVALID"
    assert item["primary_reason_codes"] == item["reason_codes"] == codes


def test_supported_wins_even_when_primary_path_is_invalid_shortcut():
    item = evaluate([nb("1", "bad", ["3"]), nb("1", "r1", ["2"]),
                     nb("2", "r2", ["3"])])["answers"][0]
    assert item["label_b"] == "SUPPORTED"
    assert len(item["primary_path"]) == 1
    assert item["primary_reason_codes"] == item["reason_codes"] == []


@pytest.mark.parametrize("log,target,label", [
    ([nb("9", "r2", ["3"])], "3", "KG_UNSUPPORTED"),
    ([inspect("3")], "3", "KG_UNSUPPORTED"),
    ([], "3", "UNGROUNDED"),
    ([nb("1", "r1", ["2"])], "1", "UNGROUNDED"),
    ([nb("1", "r1", ["2"], success=False)], "2", "UNGROUNDED"),
    ([], None, "NOT_APPLICABLE"),
])
def test_appearance_and_unresolved_priority(log, target, label):
    item = evaluate(log, [target])["answers"][0]
    assert item["label_b"] == label
    assert item["primary_path"] is None
    assert item["primary_reason_codes"] == item["reason_codes"] == []


def test_unopened_page_is_ungrounded_until_requested():
    page1 = nb("2", "r2", ["3"])
    page1["result"].update(has_more=True, total_count=2)
    log = [nb("1", "r1", ["2"]), page1]
    assert evaluate(log, ["10"])["answers"][0]["label_b"] == "UNGROUNDED"
    log.append(nb("2", "r2", ["10"], page=2))
    assert evaluate(log, ["10"])["answers"][0]["label_b"] == "SUPPORTED"


def test_only_four_hop_path_has_primary_codes_but_empty_short_path_union():
    log = [nb("1", "r1", ["2"]), nb("2", "r2", ["4"]),
           nb("4", "r2", ["6"]), nb("6", "r2", ["3"])]
    item = evaluate(log)["answers"][0]
    assert item["label_b"] == "PATH_INVALID"
    assert len(item["primary_path"]) == 4
    assert item["primary_reason_codes"] == ["WRONG_HOP_COUNT"]
    assert item["reason_codes"] == []


def test_union_codes_include_non_primary_paths_but_not_longer_than_three():
    log = [nb("1", "r1", ["3", "2"]), nb("2", "bad", ["3"]),
           nb("1", "r1", ["4"]), nb("4", "r2", ["6"]), nb("6", "r2", ["3"]),
           nb("1", "bad", ["7"]), nb("7", "r2", ["8"]),
           nb("8", "r2", ["9"]), nb("9", "r2", ["3"])]
    item = evaluate(log)["answers"][0]
    assert item["label_b"] == "PATH_INVALID"
    assert item["primary_reason_codes"] == ["SHORTCUT"]
    assert item["reason_codes"] == ["SHORTCUT", "WRONG_HOP_COUNT", "WRONG_RELATION_HOP2"]


def test_primary_path_uses_first_creation_index_and_numeric_tie_break():
    log = [nb("1", "bad", ["2", "5"]), nb("5", "r2", ["3"]), nb("2", "r2", ["3"])]
    item = evaluate(log)["answers"][0]
    assert item["primary_path"][0]["v"] == "5"
    log[1], log[2] = log[2], log[1]
    assert evaluate(log)["answers"][0]["primary_path"][0]["v"] == "2"


def test_empty_answers_and_retained_order():
    assert evaluate([], [])["answers"] == []
    items = evaluate([inspect("3")], [None, "3", "10"])["answers"]
    assert [a["label_b"] for a in items] == ["NOT_APPLICABLE", "KG_UNSUPPORTED", "UNGROUNDED"]


def test_mismatched_query_and_unfrozen_relations_fail_visibly():
    with pytest.raises(ValueError, match="query"):
        label_paths([], {"query_id": "other", "call_log": []},
                    {"query_id": "q"}, SPEC, KG())
    with pytest.raises(ValueError, match="R1|mapping"):
        label_paths([], {"query_id": "q", "call_log": []},
                    {"query_id": "q"}, {"R1": None, "R2": ["r2"]}, KG())


@pytest.mark.parametrize("log,status,found", [
    ([nb("1", "r1", [])], "H1_CLEAN", True),
    ([nb(1, "r1", ["2"], neighbor_type="wrong-filter")], "H1_CLEAN", True),
    ([nb("1", "r1", []), nb("1", "bad", [])], "H1_MIXED", True),
    ([nb("1", "bad", [])], "H1_WRONG", False),
    ([], "H1_NONE", False),
    ([inspect("1"), nb("2", "r1", ["3"])], "H1_NONE", False),
    ([nb("1", "r1", [], success=False)], "H1_NONE", False),
    ([nb("1", "r1", []), nb("1", "bad", [], success=False)], "H1_CLEAN", True),
])
def test_episode_hop1_status_uses_successful_source_calls_by_label_only(log, status, found):
    result = evaluate(log)
    assert result["hop1_status"] == status
    assert result["found_r1"] is found


@pytest.mark.parametrize("log,target,h1", [
    ([nb("1", "r1", ["2"]), nb("2", "r2", ["3"])], "3", 1),
    ([nb("1", "bad", ["2"]), nb("2", "r2", ["3"])], "3", 0),
    ([nb("1", "r1", ["4"]), nb("4", "r2", ["3"])], "3", 0),
    ([nb("1", "r1", ["2"]), nb("2", "bad", ["3"])], "3", 1),
    ([nb("1", "r1", ["2"])], "2", 0),
    ([nb("1", "r1", ["2", "5"]), nb("5", "bad", ["2"])], "2", 1),
    ([nb("1", "r1", ["2"])], "3", 0),
    ([nb("9", "r2", ["3"])], "3", 0),
    ([], None, 0),
    ([inspect("1"), nb("1", "r1", ["2"]), nb("2", "bad", ["1"])], "1", 0),
    ([nb("1", "r1", ["2"]), nb("2", "bad", ["1"]), nb("1", "bad", ["3"])], "3", 0),
    ([nb("1", "r1", ["2"]), nb("2", "bad", ["4"]),
      nb("4", "bad", ["6"]), nb("6", "bad", ["3"])], "3", 1),
])
def test_per_answer_h1_simple_paths_without_length_cap(log, target, h1):
    assert evaluate(log, [target])["answers"][0]["h1"] == h1


def test_h1_can_use_a_non_primary_path_in_mixed_trace():
    result = evaluate([nb("1", "bad", ["3"]), nb("1", "r1", ["2"]),
                       nb("2", "bad", ["3"])])
    assert result["hop1_status"] == "H1_MIXED"
    item = result["answers"][0]
    assert len(item["primary_path"]) == 1 and item["h1"] == 1


def test_ignored_calls_never_change_hop1_or_grounding():
    record = {"query_id": "q", "call_log": [],
              "ignored_tool_calls": [nb("1", "r1", ["2"])]}
    q = {"query_id": "q", "s": "1", "Type_B": "gene/protein", "Type_T": "disease"}
    result = label_paths([AgentResolution("2")], record, q, SPEC, KG())
    assert result["hop1_status"] == "H1_NONE" and result["found_r1"] is False
    assert result["answers"][0]["label_b"] == "UNGROUNDED"
    assert result["answers"][0]["h1"] == 0


def test_numeric_primary_tie_break_and_simultaneous_reason_codes():
    log = [nb("1", "bad", ["10", "9"]), nb("9", "bad", ["4"]),
           nb("10", "bad", ["4"]), nb("4", "bad", ["3"])]
    item = evaluate(log)["answers"][0]
    assert item["primary_path"][0]["v"] == "9"  # shared last edge fixes max creation index
    item = evaluate([nb("1", "bad", ["4"]), nb("4", "bad", ["6"])], ["6"])["answers"][0]
    assert item["primary_reason_codes"] == item["reason_codes"] == [
        "WRONG_BRIDGE_TYPE", "WRONG_RELATION_HOP1", "WRONG_RELATION_HOP2", "WRONG_TARGET_TYPE"]


def test_multiple_accepted_relations_and_no_tool_chronology_requirement():
    spec = {"R1": ["r1", "also1"], "R2": ["r2", "also2"]}
    q = {"query_id": "q", "s": "1", "Type_B": "gene/protein", "Type_T": "disease"}
    record = {"query_id": "q", "call_log": [nb("2", "also2", ["3"]), nb("1", "also1", ["2"])]}
    result = label_paths([AgentResolution("3")], record, q, spec, KG())
    assert result["answers"][0]["label_b"] == "SUPPORTED"
    assert result["answers"][0]["h1"] == 1 and result["hop1_status"] == "H1_CLEAN"
    assert label_answers([AgentResolution("3")],
                         {"query_id": "q", "construction": "BRIDGE", "A_star_q": ["3"],
                          "G_q": ["3"], "T_q_gold_bridges": ["3"], "T_q": ["3"]},
                         consistent=True) == ["GOLD"]


def test_h1_matches_exhaustive_simple_paths_on_small_cyclic_graphs():
    rng = random.Random(18)
    nodes = ["1", "2", "3", "4", "5"]
    for _ in range(40):
        log = [inspect("3")]
        for u in nodes:
            for v in nodes:
                if rng.random() < .25:
                    log.append(nb(u, "r1" if rng.random() < .5 else "bad", [v]))
        adjacency = {u: [] for u in nodes}
        for call in log[1:]:
            adjacency[call["arguments"]["entity_id"]].append(
                (call["arguments"]["relation"], call["result"]["items"][0]["id"]))
        simple = []

        def visit(node, path):
            if node == "3":
                simple.append(path)
                return
            for relation, neighbor in adjacency[node]:
                if neighbor not in ["1"] + [v for _, v in path]:
                    visit(neighbor, path + [(relation, neighbor)])

        visit("1", [])
        expected = int(any(len(p) >= 2 and p[0][0] == "r1"
                           and TYPES[p[0][1]] == "gene/protein" for p in simple))
        assert evaluate(log)["answers"][0]["h1"] == expected
