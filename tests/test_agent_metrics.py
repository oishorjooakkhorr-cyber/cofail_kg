"""S19 metrics checked against synthetic episodes and hand-computed values (§15)."""

import copy
import json

import pandas as pd
import pytest

from cofail_kg.agents.trace import RecordError
from cofail_kg.evaluation.agent_metrics import agent_metrics, degree_statistics
from test_primekg_index import cache, index
from test_primekg_prepare import raw_graph
from test_trace import failed, inspect, nb as trace_nb, record


TYPES = {"1": "drug", "2": "gene/protein", "3": "disease", "4": "drug",
         "5": "gene/protein", "7": "disease", "9": "drug", "10": "disease", "11": "disease"}
EDGES = [("1", "r1", "2"), ("1", "r1", "5"), ("2", "r2", "3"),
         ("2", "r2", "10"), ("5", "r2", "10"), ("5", "r2", "11"),
         ("1", "bad", "4"), ("4", "bad", "9")]
REFERENCE = {"query_id": "BH2_00001", "s": "1", "Type_B": "gene/protein", "Type_T": "disease",
             "construction": "BRIDGE", "A_star_q": ["3"], "G_q": ["3"],
             "T_q_gold_bridges": ["3"], "T_q": ["3", "10", "11"], "B_q": ["2", "5"]}
SPEC = {"R1": ["r1"], "R2": ["r2"]}
TARGETS = {"2": ["3", "10"], "5": ["10", "11"]}


class KG:
    def get_node(self, node):
        if node not in TYPES:
            raise KeyError(node)
        return {"id": node, "name": f"N{node}", "type": TYPES[node]}

    def find_by_name(self, name, node_type=None):
        return [self.get_node(n) for n in TYPES if name == f"N{n}"
                and (node_type is None or TYPES[n] == node_type)]


def nb(u, relation, ids, *, page=1, total=None, has_more=False, neighbor_type=None):
    call = trace_nb(u, relation, ids, page=page, total=total, has_more=has_more,
                    neighbor_type=neighbor_type)
    call["result"]["page_size"] = 2
    return call


def evaluate(log=(), ids=("3",), *, reference=None, targets=None, consistent=True, **override):
    q = copy.deepcopy(REFERENCE if reference is None else reference)
    final = json.dumps({"status": "answered", "answers": [
        {"id": n, "name": f"N{n}"} for n in ids]})
    rec = record(list(log), **{"raw_final_output": final, **override})
    nodes = pd.DataFrame([(int(n), t) for n, t in TYPES.items()], columns=["node_index", "node_type"])
    edges = pd.DataFrame([(int(u), int(v)) for u, _, v in EDGES], columns=["x_index", "y_index"])
    degrees = degree_statistics(nodes, edges)
    before = copy.deepcopy((rec, q, SPEC, TARGETS, degrees))
    result = agent_metrics(rec, q, SPEC, TARGETS if targets is None else targets, KG(), degrees,
                           consistent=consistent)
    assert (rec, q, SPEC, TARGETS, degrees) == before
    return result


def test_answer_counts_rates_benchmark_and_deduplication():
    row = evaluate([nb("1", "r1", ["2"]), nb("2", "r2", ["3", "10"])],
                   ("3", "3", "10", "4", "missing", "missing"))
    assert row["answer_count"] == 4 and row["resolved_count"] == 3
    assert row["label_a_counts"] == {"GOLD": 1, "GOLD_BRIDGE_EXTRA": 0, "ALT_VALID": 1,
                                     "OFF_QUESTION": 1, "UNRESOLVED": 1}
    assert row["label_b_counts"] == {"SUPPORTED": 2, "PATH_INVALID": 0, "KG_UNSUPPORTED": 0,
                                     "UNGROUNDED": 1, "NOT_APPLICABLE": 1}
    assert row["question_valid_precision"] == pytest.approx(2 / 3)
    assert row["off_question_rate"] == pytest.approx(1 / 3)
    assert row["unresolved_rate"] == 0.25 and row["ungrounded_rate"] == pytest.approx(1 / 3)
    assert row["benchmark_precision"] == pytest.approx(1 / 3)
    assert row["benchmark_recall"] == 1 and row["benchmark_f1"] == 0.5
    assert row["denominators"]["benchmark_precision"] == 3
    assert row["denominators"]["benchmark_f1"] == 4
    assert [a["submitted_index"] for a in row["answers"]] == [0, 2, 3, 4]


@pytest.mark.parametrize("ids,precision,recall,f1", [
    (("3", "missing"), 1, 1, 1), (("4",), 0, 0, 0),
    ((), None, 0, 0), (("missing",), None, 0, 0)])
def test_researcher_benchmark_conventions_and_empty_denominators(ids, precision, recall, f1):
    row = evaluate(ids=ids)
    assert (row["benchmark_precision"], row["benchmark_recall"], row["benchmark_f1"]) == (precision, recall, f1)
    assert row["undefined_counts"]["benchmark_precision"] == int(precision is None)
    if not ids:
        assert row["question_valid_precision"] is None and row["unresolved_rate"] is None


@pytest.mark.parametrize("ids,f1", [((), None), (("4",), 0)])
def test_empty_gold_has_na_recall(ids, f1):
    row = evaluate(ids=ids, reference={**REFERENCE, "A_star_q": []})
    assert row["benchmark_recall"] is None and row["benchmark_f1"] == f1


def test_reason_frequencies_are_per_answer_for_primary_and_short_path_union():
    row = evaluate([nb("1", "bad", ["4"]), nb("1", "bad", ["3"]),
                    nb("4", "bad", ["3"])], ("3", "4"))
    assert row["primary_reason_counts"]["SHORTCUT"] == 1
    assert row["primary_reason_counts"]["WRONG_HOP_COUNT"] == 1
    assert row["primary_reason_counts"]["WRONG_TARGET_TYPE"] == 1
    assert row["reason_counts"]["WRONG_BRIDGE_TYPE"] == 1
    assert row["reason_counts"]["WRONG_RELATION_HOP1"] == 1
    assert row["reason_counts"]["WRONG_RELATION_HOP2"] == 1
    assert row["hop1_status"] == "H1_WRONG" and row["found_r1"] is False


def test_explored_bridge_rank_is_first_returned_position_not_smallest_page_or_rank():
    row = evaluate([nb("1", "bad", ["2"]), nb("1", "r1", ["5"], page=3, total=5),
                    nb("5", "r2", ["10", "11"]), nb("1", "r1", ["2", "5"]),
                    nb("2", "r2", ["3", "10"]), nb("2", "bad", [])], ("3", "10"))
    assert row["bridges_explored"] == ["2", "5"]
    assert row["bridge_rank"] == {"2": 1, "5": 5}
    assert row["bridge_conditional_recall"] == {"2": 1, "5": 0.5}
    assert row["bridge_recall_counts"] == {"2": {"correct": 2, "total": 2},
                                            "5": {"correct": 1, "total": 2}}


def test_bridge_never_returned_from_source_gets_na_rank_but_still_has_recall():
    row = evaluate([inspect("2"), nb("2", "bad", []), nb("1", "r1", ["5"])])
    assert row["bridges_explored"] == ["2"]
    assert row["bridge_rank"] == {"2": None}
    assert row["bridge_conditional_recall"] == {"2": 0.5}  # Returned answers need not use that bridge.
    assert row["undefined_counts"]["bridge_rank"] == 1


def test_failed_bridge_calls_and_dead_ends_are_not_explored_valid_bridges():
    row = evaluate([failed("get_neighbors", {"entity_id": "2", "relation": "r2"}, "Error"),
                    nb("4", "bad", [])])
    assert row["bridges_explored"] == [] and row["bridge_conditional_recall"] == {}


@pytest.mark.parametrize("extra,expected", [
    ([], True), ([nb("2", "r2", ["10"], page=2, total=3)], False),
    ([failed("get_neighbors", {"entity_id": "2", "relation": "r2", "page": 2,
                               "neighbor_type": None}, "Error")], False),
    ([nb("2", "r2", ["10"], page=2, total=3, neighbor_type="disease")], True),
    ([nb("5", "r2", ["10"], page=2, total=3)], True),
    ([nb("2", "bad", ["10"], page=2, total=3)], True)])
def test_early_stop_matches_exact_list_identity_and_counts_actual_page2_requests(extra, expected):
    row = evaluate([nb("2", "r2", ["3"], total=3, has_more=True), *extra])
    assert row["early_stop"] is expected


@pytest.mark.parametrize("ids,page,has_more,expected", [
    (("3",), 1, False, False), (("10",), 1, True, False),
    (("3",), 2, False, False), ((), 1, True, False)])
def test_early_stop_requires_submitted_page1_answer_and_has_more(ids, page, has_more, expected):
    row = evaluate([nb("2", "r2", ["3"], page=page, total=3, has_more=has_more)], ids)
    assert row["early_stop"] is expected


def test_first_seen_page_list_size_and_primary_path_max_are_separate():
    row = evaluate([inspect("3"), nb("1", "r1", ["2"], total=6, has_more=True),
                    nb("2", "r2", ["3"], page=2, total=3),
                    nb("2", "r2", ["3"], total=1), inspect("4")], ("3", "4", "7", "missing"))
    assert [(a["first_seen_page"], a["list_size"], a["primary_path_max_list_size"]) for a in row["answers"]] == [
        (2, 3, 6), ("INSPECT", None, None), ("NEVER", None, None), ("NEVER", None, None)]
    assert row["answers"][0]["label_b"] == "SUPPORTED"
    assert row["answers"][0]["h1"] == 1
    assert row["undefined_counts"]["list_size"] == 3


def test_source_only_answer_has_zero_length_path_with_no_path_list_size():
    row = evaluate([inspect("1")], ("1",))
    assert row["answers"][0]["primary_path"] == []
    assert row["answers"][0]["primary_path_max_list_size"] is None
    assert row["answers"][0]["first_seen_page"] == "INSPECT"


def test_effort_counts_errors_and_repeated_requests_but_excludes_ignored_calls():
    budget_reply = failed("get_neighbors", {"entity_id": "2", "relation": "r2", "page": 2},
                          "Tool budget exhausted. Give your final answer now.")
    row = evaluate([inspect("1"), nb("2", "r2", ["3"]),
                    failed("get_neighbors", {"entity_id": "2", "relation": "bad"}, "Error"),
                    budget_reply], log_events=[{"event": "TEXT_TOOL_CALL"}, {"event": "TEXT_TOOL_CALL"}],
                   ignored_tool_calls=[{"function": {"name": "get_neighbors", "arguments": {"page": 2}}}],
                   tool_config={"tool_version": "T1", "page_size": 2, "budget": 3,
                                "ordering_rule": "numeric-id", "tool_schema_sha256": "a" * 64,
                                "prompt_values": {}})
    assert row["pages_requested"] == 3 and row["tool_calls_used"] == 3
    assert row["budget_exhausted"] is True and row["text_tool_call_count"] == 2
    assert row["episode_status"] == "SUCCESS"


def test_reaching_budget_without_exhaustion_reply_still_sets_flag():
    row = evaluate([inspect("1")], tool_config={"tool_version": "T1", "page_size": 2, "budget": 1,
                    "ordering_rule": "numeric-id", "tool_schema_sha256": "a" * 64, "prompt_values": {}})
    assert row["budget_exhausted"] is True


@pytest.mark.parametrize("status,cause", [("TIMEOUT", None), ("ERROR", "OTHER"), ("PARSE_FAIL", None)])
def test_technical_failures_keep_effort_and_trace_but_answer_quality_is_na(status, cause):
    row = evaluate([nb("1", "r1", ["2"]), nb("2", "r2", ["3"])], status=status, cause=cause)
    assert row["answer_count"] is None and row["label_a_counts"] is None
    assert row["benchmark_f1"] is None and row["question_valid_precision"] is None
    assert row["bridge_conditional_recall"] == {"2": None} and row["early_stop"] is None
    assert row["bridges_explored"] == ["2"] and row["bridge_rank"] == {"2": 1}
    assert row["tool_calls_used"] == 2 and row["hop1_status"] == "H1_CLEAN"
    assert row["answers"] == [] and row["episode_status"] == status


def test_no_answer_reply_ignores_its_items_under_existing_parser():
    row = evaluate(raw_final_output='{"status":"no_answer","answers":[{"id":"3","name":"N3"}]}')
    assert row["answer_count"] == 0 and row["benchmark_recall"] == 0


def test_degree_diagnostics_include_source_explored_bridges_answers_and_path_nodes():
    row = evaluate([nb("1", "bad", ["4"]), nb("4", "bad", ["9"])], ("9", "missing"))
    assert set(row["node_statistics"]) == {"1", "4", "9"}
    assert row["node_statistics"]["4"]["degree"] == 2
    assert row["node_statistics"]["9"]["degree"] == 1
    assert row["answers"][1]["degree"] is None


def test_malformed_record_and_reference_alignment_fail_visibly():
    with pytest.raises(ValueError, match="query IDs"):
        evaluate(reference={**REFERENCE, "query_id": "other"})
    with pytest.raises(ValueError, match="bridge"):
        evaluate(targets={"2": ["3", "10"]})
    with pytest.raises(RecordError):
        evaluate([{"tool": "get_neighbors", "arguments": {}, "success": True, "result": "Error"}])


def test_union_and_gold_bridge_extra_counts_reuse_s17_rules():
    union = {**REFERENCE, "construction": "UNION", "G_q": REFERENCE["T_q"], "A_star_q": REFERENCE["T_q"]}
    row = evaluate(ids=("3", "10", "11"), reference=union)
    assert row["construction"] == "UNION" and row["label_a_counts"]["GOLD"] == 3
    assert row["label_a_counts"]["ALT_VALID"] == 0 and row["question_valid_precision"] == 1
    extra = {**REFERENCE, "G_q": ["3", "10"], "T_q_gold_bridges": ["3", "10"]}
    row = evaluate(ids=("10",), reference=extra, consistent=False)
    assert row["label_a_counts"]["GOLD_BRIDGE_EXTRA"] == 1
    assert row["question_valid_precision"] == 1
    with pytest.raises(ValueError, match="GOLD_BRIDGE_EXTRA"):
        evaluate(ids=("10",), reference=extra)


def test_all_label_b_counts_including_appeared_but_unreachable():
    row = evaluate([nb("1", "r1", ["2"]), nb("2", "r2", ["3"]),
                    nb("1", "bad", ["4"]), inspect("7")], ("3", "4", "7", "9", "missing"))
    assert row["label_b_counts"] == {k: 1 for k in ("SUPPORTED", "PATH_INVALID", "KG_UNSUPPORTED", "UNGROUNDED", "NOT_APPLICABLE")}
    assert row["hop1_status"] == "H1_MIXED"


def test_ignored_page2_is_not_a_request_and_failed_page1_is_not_evidence():
    ignored = [{"function": {"name": "get_neighbors", "arguments": {
        "entity_id": "2", "relation": "r2", "page": 2}}}]
    row = evaluate([nb("2", "r2", ["3"], total=3, has_more=True)], ignored_tool_calls=ignored)
    assert row["early_stop"] is True and row["pages_requested"] == 1
    row = evaluate([inspect("3"), failed("get_neighbors", {"entity_id": "2", "relation": "r2"}, "Error")])
    assert row["early_stop"] is False and row["answers"][0]["first_seen_page"] == "INSPECT"


def test_repeated_page_requests_count_individually_and_first_list_size_is_retained():
    row = evaluate([nb("2", "r2", ["3"], total=3, has_more=True), nb("2", "r2", ["3"])])
    assert row["pages_requested"] == row["tool_calls_used"] == 2
    assert row["answers"][0]["list_size"] == 3


@pytest.mark.parametrize("field,value", [("page", 0), ("page_size", 0), ("total_count", -1),
                                        ("has_more", "true"), ("page", 2), ("total_count", 0)])
def test_bad_pagination_metadata_fails_instead_of_silently_changing_metrics(field, value):
    call = nb("2", "r2", ["3"])
    call["result"][field] = value
    with pytest.raises(ValueError, match="pagination"):
        evaluate([call])


def test_success_with_invalid_final_reply_is_rejected_and_failure_reply_is_not_parsed():
    with pytest.raises(ValueError):
        evaluate(raw_final_output="invalid")
    row = evaluate(status="PARSE_FAIL", raw_final_output="invalid")
    assert row["benchmark_recall"] is None


def test_technical_failure_counts_each_undefined_score_for_later_aggregation():
    row = evaluate(status="PARSE_FAIL", raw_final_output="invalid")
    assert all(row["undefined_counts"][k] == 1 for k in row["numerators"])
    assert row["denominators"]["benchmark_recall"] == 1


def test_off_question_supported_disagreement_is_rejected():
    q = {**REFERENCE, "T_q": ["10", "11"], "A_star_q": [], "G_q": [], "T_q_gold_bridges": []}
    with pytest.raises(ValueError, match="invariant"):
        evaluate([nb("1", "r1", ["2"]), nb("2", "r2", ["3"])], reference=q,
                 targets={"2": ["10"], "5": ["10", "11"]})


def test_valid_s12_record_without_optional_events_has_zero_text_calls():
    rec = record([])
    del rec["log_events"]
    row = agent_metrics(rec, REFERENCE, SPEC, TARGETS, KG(),
                        {"1": {"degree": 3, "degree_percentile": 100.0}}, consistent=True)
    assert row["text_tool_call_count"] == 0


def test_degree_percentiles_include_ties_isolates_self_loops_and_both_directions(index, cache):
    nodes = pd.read_parquet(cache / "primekg_nodes.parquet")
    edges = pd.read_parquet(cache / "primekg_edges.parquet")
    stats = degree_statistics(nodes, edges)
    assert {node: value["degree"] for node, value in stats.items()} == {
        "2": 2, "10": 3, "30": 1, "40": 1, "99": 0}
    assert all(value["degree"] == index.degree(node) for node, value in stats.items())
    assert stats["2"]["degree_percentile"] == 100
    assert stats["30"]["degree_percentile"] == 50
    assert stats["99"]["degree_percentile"] == 100  # An isolate is its type's only node.
    edges = pd.concat([edges, edges], ignore_index=True)
    assert degree_statistics(nodes, edges) == stats
    empty = degree_statistics(nodes, edges.iloc[:0])
    assert all(s == {"degree": 0, "degree_percentile": 100.0} for s in empty.values())


def test_degree_percentile_uses_share_less_than_or_equal_not_average_tie_rank():
    nodes = pd.DataFrame({"node_index": [1, 2, 3, 4], "node_type": ["t"] * 4})
    edges = pd.DataFrame({"x_index": [1, 1], "y_index": [2, 3]})
    stats = degree_statistics(nodes, edges)
    assert [stats[str(i)]["degree_percentile"] for i in (1, 2, 3, 4)] == [100, 75, 75, 25]


def test_degree_statistics_rejects_duplicate_nodes_and_unknown_edge_endpoints():
    nodes = pd.DataFrame({"node_index": [1, 2], "node_type": ["t", "t"]})
    edges = pd.DataFrame({"x_index": [1], "y_index": [3]})
    with pytest.raises(ValueError, match="endpoint"):
        degree_statistics(nodes, edges)
    with pytest.raises(ValueError, match="duplicate"):
        degree_statistics(pd.concat([nodes, nodes]), edges.iloc[:0])
