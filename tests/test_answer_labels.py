import copy

import pytest

from cofail_kg.evaluation.answer_labels import label_answers
from cofail_kg.evaluation.normalize import AgentResolution
from cofail_kg.evaluation.reference_sets import build_reference_sets


def reference(**changes):
    return {"query_id": "synthetic", "construction": "BRIDGE", "s": "1",
            "A_star_q": ["10"], "G_q": ["10", "11"],
            "T_q_gold_bridges": ["10", "11"], "T_q": ["10", "11", "12"],
            **changes}


@pytest.mark.parametrize("answer,expected", [
    (AgentResolution(None, reason="NO_MATCH"), "UNRESOLVED"),
    (AgentResolution(None, reason="AMBIGUOUS_NAME"), "UNRESOLVED"),
    (AgentResolution("10"), "GOLD"),
    (AgentResolution("11"), "GOLD_BRIDGE_EXTRA"),
    (AgentResolution("12"), "ALT_VALID"),
    (AgentResolution("99"), "OFF_QUESTION"),
    (AgentResolution("1"), "OFF_QUESTION"),
])
def test_protocol_priority(answer, expected):
    assert label_answers([answer], reference(), consistent=False) == [expected]


def test_gold_wins_over_construction_and_alternative_membership():
    q = reference(A_star_q=["10", "12"])
    assert label_answers([AgentResolution("10"), AgentResolution("12")], q,
                         consistent=False) == ["GOLD", "GOLD"]


@pytest.mark.parametrize("construction,node", [("BRIDGE", "11"), ("UNION", "12")])
def test_consistent_extra_is_an_error(construction, node):
    q = reference(construction=construction)
    if construction == "UNION":
        q["G_q"] = q["T_q"]
    with pytest.raises(ValueError, match=f"synthetic.*GOLD_BRIDGE_EXTRA.*{node}"):
        label_answers([AgentResolution("10"), AgentResolution(node)], q, consistent=True)


@pytest.mark.parametrize("construction", ["BRIDGE", "UNION"])
def test_uses_s7_construction_and_labels_shared_target_once(construction):
    kind = "drug:gene/protein:disease"
    rows = [{"row_id": "q", "relation_hop2": kind, "hop2": "source", "hop1": "gold",
             "answer": ["shared"] if construction == "BRIDGE" else ["shared", "other"],
             "hop2_question_multi": "Which diseases?"}]
    mapping = {kind: {"d1_status": "PASS", "excluded": False, "construction": construction,
                      "R1": ["r1"], "R2": ["r2"]}}
    names = {("source", "drug"): ["1"], ("gold", "gene/protein"): ["2"],
             ("shared", "disease"): ["10"], ("other", "disease"): ["12"]}
    edges = {("1", "gene/protein"): {"r1": {"2", "3"}},
             ("2", "disease"): {"r2": {"10"}},
             ("3", "disease"): {"r2": {"10", "12"}}}
    queries, targets = build_reference_sets(
        rows, mapping, lambda name, kind: names.get((name, kind), []),
        lambda node, kind: edges.get((node, kind), {}))
    q = queries[0]
    assert sum(t["target"] == "10" for t in targets) == 2
    answers = [AgentResolution("10"), AgentResolution("12"), AgentResolution("99")]
    labels = label_answers(answers, q, consistent=True)
    assert labels == ["GOLD", "ALT_VALID" if construction == "BRIDGE" else "GOLD",
                      "OFF_QUESTION"]
    if construction == "UNION":
        assert set(q["G_q"]) == set(q["T_q"]) != set(q["T_q_gold_bridges"])
        assert "ALT_VALID" not in labels


@pytest.mark.parametrize("construction", ["BRIDGE", "UNION"])
def test_rejects_gq_that_disagrees_with_s7_construction(construction):
    q = reference(construction=construction, G_q=["10"])
    with pytest.raises(ValueError, match="G_q.*construction"):
        label_answers([AgentResolution("10")], q, consistent=True)


def test_missing_gq_does_not_fall_back_to_gold_bridge_targets():
    q = reference()
    del q["G_q"]
    with pytest.raises(KeyError, match="G_q"):
        label_answers([AgentResolution("10")], q, consistent=False)


def test_invalid_construction_is_an_error():
    with pytest.raises(ValueError, match="construction"):
        label_answers([], reference(construction="UNKNOWN"), consistent=True)


def test_order_empty_input_and_inputs_unchanged():
    q = reference(A_star_q=["10", "11"])
    before = copy.deepcopy(q)
    answers = [AgentResolution("12"), AgentResolution(None, reason="NO_MATCH"),
               AgentResolution("10", name_id_mismatch=True)]
    assert label_answers(answers, q, consistent=True) == ["ALT_VALID", "UNRESOLVED", "GOLD"]
    assert label_answers([], q, consistent=True) == []
    assert q == before and [a.node_id for a in answers] == ["12", None, "10"]
