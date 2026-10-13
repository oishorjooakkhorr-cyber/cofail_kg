import hashlib

import pytest

from cofail_kg.evaluation.relation_mapping import (
    ambiguity_tag,
    candidate_sets,
    evaluate_d1,
    score_type,
    select_best,
    validation_sample,
)


def row(i, **changes):
    return {
        "row_id": f"BH2_{i:05d}", "relation_hop2": "disease:drug:effect/phenotype",
        "hop2": "Disease", "hop1": "Drug", "answer": ["Target"], **changes,
    }


def find(name, kind):
    return {
        ("Disease", "disease"): ["1"], ("Drug", "drug"): ["2"],
        ("Target", "effect/phenotype"): ["10"],
        ("Insomnia (disease)", "disease"): ["3"],
        ("insomnia (disease)", "disease"): ["3"],
    }.get((name, kind), [])


def test_sample_uses_hash_order_skips_entities_but_not_unresolved_answers():
    rows = [row(i) for i in range(35)]
    ordered = sorted(rows, key=lambda r: hashlib.sha256(("42" + r["row_id"]).encode()).hexdigest())
    ordered[0]["hop2"] = "Missing disease"
    ordered[1]["hop1"] = "Missing drug"
    ordered[2]["answer"] = ["Unknown answer"]
    sample, skipped = validation_sample(list(reversed(rows)), find)
    assert [r["row_id"] for r in sample] == [r["row_id"] for r in ordered[2:32]]
    assert [r["row_id"] for r in skipped] == [r["row_id"] for r in ordered[:2]]
    assert sample[0]["unresolved_answers"] == [{"name": "Unknown answer", "status": "not_found"}]
    assert sample[0]["gold"] == set()


def test_sample_resolves_suffix_and_collapses_answer_ids():
    sample, skipped = validation_sample([row(0, hop2="Insomnia", answer=["Target", "Target"])], find)
    assert not skipped
    assert sample[0]["s"] == "3"
    assert sample[0]["gold"] == {"10"}


def test_candidate_sets_are_all_nonempty_subsets_of_relation_labels():
    assert candidate_sets(["b", "a", "a"]) == [("a",), ("b",), ("a", "b")]
    assert candidate_sets([]) == []


def test_selection_prefers_score_then_smallest_set_and_preserves_ties():
    scores = {("a",): 27, ("b",): 27, ("c",): 26, ("a", "b"): 27}
    assert select_best(scores) == {"matches": 27, "sets": [["a"], ["b"]], "status": "TIE"}
    scores[("a", "b")] = 28
    assert select_best(scores) == {"matches": 28, "sets": [["a", "b"]], "status": "SELECTED"}
    assert select_best({}) == {"matches": None, "sets": [], "status": "NO_CANDIDATES"}


@pytest.mark.parametrize("r1,r2,expected", [
    (["a", "b"], ["x", "y"], "NONE"),
    (["a"], ["x", "y"], "R1_AMBIGUOUS"),
    (["a", "b"], ["x"], "R2_AMBIGUOUS"),
    (["a"], ["x"], "BOTH_AMBIGUOUS"),
])
def test_ambiguity_uses_unselected_labels(r1, r2, expected):
    assert ambiguity_tag(["a", "b"], ["x", "y"], r1, r2) == expected


def neighbors(node, kind):
    return {
        ("1", "drug"): {"a": {"2", "3"}, "b": {"2"}},
        ("2", "effect/phenotype"): {"x": {"10"}, "y": {"11"}},
        ("3", "effect/phenotype"): {"x": {"11"}},
    }.get((node, kind), {})


def run_score(answers, **kwargs):
    def finder(name, kind):
        if (name, kind) == ("Other", "effect/phenotype"):
            return ["11"]
        return find(name, kind)
    return score_type([row(i, answer=answers) for i in range(10)], finder, neighbors,
                      kwargs.pop("candidates1", {"a": ["display a"]}),
                      kwargs.pop("candidates2", {"x": ["display x"]}), **kwargs)


def test_scores_distinguish_bridge_from_union_and_choose_union_when_needed():
    result = run_score(["Target", "Other"])
    assert result["construction"] == "UNION"
    assert result["R1"] == ["a"] and result["R2"] == ["x"]
    assert result["d1_status"] == "PASS"
    scenario = result["scenarios"][0]
    assert scenario["BRIDGE"]["matches"] == 0
    assert scenario["UNION"]["matches"] == 10
    assert scenario["BRIDGE"]["diagnostics"][0]["examples"][0]["missing_ids"] == ["11"]


def test_both_pass_adopts_bridge_and_unselected_labels_only_change_tag():
    result = run_score(["Target"], candidates1={"b": ["info"]}, candidates2={"x": [], "y": []})
    assert result["construction"] == "BRIDGE"
    assert result["scenarios"][0]["UNION"]["matches"] == 10
    assert result["ambiguity_tag"] == "R2_AMBIGUOUS"


def test_any_unresolved_answer_counts_as_mismatch_even_if_resolved_ids_equal():
    result = run_score(["Target", "Missing"], candidates1={"b": []})
    assert result["scenarios"][0]["BRIDGE"]["matches"] == 0
    assert result["construction"] is None and result["d1_status"] == "FAIL"
    assert "hop-2 score below 90% under both constructions" in result["fail_reasons"]


def test_hop1_tie_preserves_every_scenario_and_does_not_choose():
    result = run_score(["Target", "Other"], candidates1={"a": [], "b": []})
    assert result["hop1"]["status"] == "TIE"
    assert result["R1"] is None and result["R2"] is None
    assert result["d1_status"] == "PENDING" and result["needs_decision"]
    assert [s["UNION"]["matches"] for s in result["scenarios"]] == [10, 0]
    assert [c["hop1_labels"] for c in result["candidate_scores"] if c["hop"] == 2] == [["a"], ["b"]]


def test_hop2_tie_is_reported_without_choosing_an_adopted_r2():
    def same_targets(node, kind):
        return {"x": {"10"}, "y": {"10"}} if kind == "effect/phenotype" else {"a": {"2"}}
    result = score_type([row(i) for i in range(10)], find, same_targets, {"a": []}, {"x": [], "y": []})
    assert result["construction"] == "BRIDGE" and result["R2"] is None
    assert result["scenarios"][0]["BRIDGE"]["status"] == "TIE"
    assert result["d1_status"] == "PASS" and result["ambiguity_tag"] is None
    assert result["needs_decision"]


def test_unadopted_construction_tie_is_still_flagged_for_researcher():
    result = run_score(["Target"], candidates2={"x": [], "y": []})
    assert result["construction"] == "BRIDGE" and result["R2"] == ["x"]
    assert result["scenarios"][0]["UNION"]["status"] == "TIE"
    assert result["needs_decision"]


@pytest.mark.parametrize("sample_count,fail_s5,candidates,reason", [
    (5, False, {"a": []}, "fewer than 10 validation rows"),
    (10, True, {"a": []}, "failed S5 field-role rule"),
    (10, False, {}, "no hop-1 candidate label"),
])
def test_d1_independent_failure_rules(sample_count, fail_s5, candidates, reason):
    result = score_type([row(i) for i in range(sample_count)], find, neighbors,
                        candidates, {"x": []}, s5_failed=fail_s5)
    assert result["d1_status"] == "FAIL" and reason in result["fail_reasons"]


def test_threshold_is_inclusive_and_query_entity_is_excluded_from_targets():
    rows = [row(i, relation_hop2="disease:drug:disease", answer=["Insomnia"]) for i in range(10)]
    rows[-1]["answer"] = ["Missing"]
    def disease_neighbors(node, kind):
        return {"a": {"2"}} if kind == "drug" else {"x": {"1", "3"}}
    result = score_type(rows, find, disease_neighbors, {"a": []}, {"x": []})
    assert result["d1_status"] == "PASS" and result["hop2_score"] == 0.9


def test_hop1_below_threshold_and_absent_hop2_labels_fail():
    def disconnected(node, kind):
        return {} if kind == "drug" else neighbors(node, kind)
    result = score_type([row(i) for i in range(10)], find, disconnected, {"a": []}, {"x": []})
    assert result["d1_status"] == "FAIL" and "hop-1 score below 90%" in result["fail_reasons"]
    result = run_score(["Target"], candidates2={})
    assert result["d1_status"] == "FAIL" and "no hop-2 candidate label" in result["fail_reasons"]


@pytest.mark.parametrize("passes,coverage,outcome", [(6, 70, "PROCEED"), (5, 90, "STOP"), (6, 69, "STOP")])
def test_global_d1_thresholds_and_construction_splits(passes, coverage, outcome):
    types = {f"t{i}": {"d1_status": "PASS" if i < passes else "FAIL", "needs_decision": False,
                      "rows_in_dataset": 0, "construction": "BRIDGE" if i % 2 else "UNION"}
             for i in range(12)}
    types["t0"]["rows_in_dataset"] = coverage
    types["t11"]["rows_in_dataset"] = 100 - coverage
    result = evaluate_d1(types)
    assert result["outcome"] == outcome and result["pass_types"] == passes
    assert result["pass_rows"] == coverage
    assert sum(v["pass_types"] for v in result["by_construction"].values()) == passes


def test_global_d1_does_not_issue_a_final_outcome_with_unresolved_ties():
    result = evaluate_d1({"t": {"d1_status": "PENDING", "needs_decision": True,
                                "rows_in_dataset": 100, "construction": None}})
    assert result["outcome"] is None and result["status"] == "NEEDS_DECISION"


def test_tie_in_definitely_failed_type_does_not_change_global_gate():
    types = {f"t{i}": {"d1_status": "PASS" if i < 9 else "FAIL", "needs_decision": i == 11,
                       "rows_in_dataset": 1, "construction": "BRIDGE" if i < 9 else None}
             for i in range(12)}
    result = evaluate_d1(types)
    assert result["outcome"] == "PROCEED" and result["status"] == "NEEDS_DECISION"
