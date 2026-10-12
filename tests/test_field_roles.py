import hashlib

import pytest

from cofail_kg.data.field_roles import (
    analyse_row,
    evaluate,
    order_key,
    s5_sample,
    type_row_counts,
)

# id: (type, name)
NODES = {
    "1": ("disease", "Diabetes"),
    "2": ("drug", "DrugA"),  # stored bridge
    "3": ("drug", "DrugB"),  # other bridge of s
    "4": ("drug", "DrugC"),  # drug not adjacent to s
    "10": ("effect/phenotype", "Nausea"),  # via A and B
    "11": ("effect/phenotype", "Rash"),  # via B only
    "12": ("effect/phenotype", "Fever"),  # via C only -> neither
    "13": ("effect/phenotype", "Twin"),
    "14": ("effect/phenotype", "Twin"),  # ambiguous
    "20": ("gene/protein", "Diabetes"),  # same name, other type
}
EDGES = [("1", "2", "indication"), ("2", "1", "contraindication"), ("1", "3", "indication"),
         ("2", "10", "drug_effect"), ("3", "10", "drug_effect"), ("3", "11", "drug_effect"),
         ("4", "12", "drug_effect"), ("2", "1", "indication")]


def find(name, node_type):
    key = " ".join(name.lower().split())
    return sorted((i for i, (t, n) in NODES.items() if t == node_type and n.lower() == key), key=int)


def nbrs(node_id, node_type):
    out = {b for a, b, _ in EDGES if a == node_id} | {a for a, b, _ in EDGES if b == node_id}
    return {n for n in out if NODES[n][0] == node_type}


def labels_between(u, v):
    return sorted({lab for a, b, lab in EDGES if {a, b} == {u, v}})


def row(hop2="Diabetes", hop1="DrugA", answer=("Nausea",), rtype="disease:drug:effect/phenotype", rid="BH2_00000"):
    s, b, t = rtype.split(":")
    return {"row_id": rid, "relation_hop2": rtype, "hop2": hop2, "hop1": hop1, "answer": list(answer),
            "hop2_type": s, "hop1_type": b, "target_type": t}


def go(**kw):
    return analyse_row(row(**kw), find, nbrs, labels_between)


def test_bridge_row_supports():
    r = go()
    assert r["resolvable"] and r["supports"] and r["row_status"] == "supports"
    assert r["labels_hop2_hop1"] == ["contraindication", "indication"]
    assert (r["reach_via_stored_bridge"], r["reach_only_via_other_bridge"], r["reach_via_neither"]) == (1, 0, 0)
    assert r["type_fields_agree"] is True


def test_union_row_supports():
    r = go(answer=("Nausea", "Rash"))
    assert r["supports"] is True
    assert (r["reach_via_stored_bridge"], r["reach_only_via_other_bridge"]) == (1, 1)


def test_answer_via_neither_conflicts():
    r = go(answer=("Nausea", "Fever"))
    assert r["resolvable"] and r["supports"] is False and r["row_status"] == "conflict"
    assert r["c3_every_answer_reachable"] is False and r["reach_via_neither"] == 1


def test_no_answer_via_stored_bridge_conflicts():
    r = go(answer=("Rash",))
    assert r["c2_some_answer_via_hop1"] is False and r["supports"] is False


def test_non_adjacent_bridge_conflicts():
    r = go(hop1="DrugC", answer=("Fever",))
    assert r["c1_adjacent"] is False and r["supports"] is False


@pytest.mark.parametrize("answer,resolvable", [
    (("Nausea", "Missing"), True),  # 1 of 2: exactly half
    (("Nausea", "Missing", "Twin"), False),  # 1 of 3 (Twin ambiguous)
    (("Missing",), False),  # none resolved
])
def test_at_least_half_rule(answer, resolvable):
    r = go(answer=answer)
    assert r["resolvable"] is resolvable
    if not resolvable:
        assert r["row_status"] == "unresolved_answers" and r["supports"] is None
        assert r["c1_adjacent"] is True  # evidence still reported


def test_unresolved_entities_are_not_conflicts():
    assert go(hop2="Nobody")["row_status"] == "unresolved_hop2"
    assert go(hop1="Nobody")["row_status"] == "unresolved_hop1"
    r = go(hop1="Twin", rtype="disease:effect/phenotype:effect/phenotype")
    assert r["hop1_status"] == "ambiguous" and r["resolvable"] is False and r["supports"] is None


def test_type_filter_and_distinct_names():
    assert go()["hop2_node_id"] == "1"  # gene/protein "Diabetes" ignored
    r = go(answer=("Nausea", "Nausea", "Unresolved"))
    assert r["answers_total"] == 2 and r["answers_unresolved"] == 1
    assert r["unresolved_answers"] == ["Unresolved [not_found]"]


def test_s_never_reachable():
    r = go(answer=("Diabetes",), rtype="disease:drug:disease")
    assert r["answers_resolving_to_s"] == 1
    assert r["reach_via_neither"] == 1 and r["supports"] is False


def test_sample_order_and_size():
    rows = [{"row_id": f"BH2_{i:05d}", "relation_hop2": "a:b:c"} for i in range(9)]
    rows += [{"row_id": f"BH2_{i:05d}", "relation_hop2": "x:y:z"} for i in range(100, 103)]
    out = s5_sample(rows)
    expected = sorted((r for r in rows if r["relation_hop2"] == "a:b:c"), key=lambda r: order_key(r["row_id"]))[:5]
    assert [r for _, r in out["a:b:c"]] == expected
    assert [p for p, _ in out["a:b:c"]] == [1, 2, 3, 4, 5]
    assert len(out["x:y:z"]) == 3  # all if fewer
    assert order_key("BH2_00001") == hashlib.sha256(b"42BH2_00001").hexdigest()


def rec(t, rid, resolvable=True, supports=True):
    return {"relation_type": t, "row_id": rid, "resolvable": resolvable, "supports": supports if resolvable else None}


COUNTS = {"big": 9_000, "small": 50, "tiny": 5}


def test_evaluate_all_pass():
    recs = [rec(t, f"{t}{i}") for t in COUNTS for i in range(5)]
    assert evaluate(recs, COUNTS)["rule_outcome"] == "ROLES_SUPPORTED"


def test_evaluate_one_small_failure_excluded():
    recs = [rec(t, f"{t}{i}") for t in ("big", "small") for i in range(5)]
    recs += [rec("tiny", f"tiny{i}", supports=i != 0) for i in range(5)]  # 4/5 = 80%
    ev = evaluate(recs, COUNTS)
    assert ev["failing_types"] == ["tiny"] and ev["rule_outcome"] == "EXCLUDE_FAILING_TYPE"
    assert ev["per_type"]["tiny"]["conflicting_rows"] == ["tiny0"]


def test_evaluate_unresolved_rows_leave_denominator():
    recs = [rec("big", f"b{i}") for i in range(4)] + [rec("big", "b4", resolvable=False)]
    recs += [rec(t, f"{t}{i}") for t in ("small", "tiny") for i in range(5)]
    ev = evaluate(recs, COUNTS)
    assert ev["per_type"]["big"]["support_share"] == 1.0
    assert ev["per_type"]["big"]["unresolved_rows"] == ["b4"]


def test_evaluate_no_resolvable_row_fails():
    recs = [rec("tiny", f"t{i}", resolvable=False) for i in range(5)]
    recs += [rec(t, f"{t}{i}") for t in ("big", "small") for i in range(5)]
    ev = evaluate(recs, COUNTS)
    assert ev["per_type"]["tiny"]["fail_reason"] == "no resolvable sampled row"


@pytest.mark.parametrize("failing,outcome", [
    (["big"], "STOP"),  # covers > 1%
    (["small", "tiny"], "STOP"),  # more than one type
])
def test_evaluate_stop(failing, outcome):
    recs = [rec(t, f"{t}{i}", supports=not (t in failing and i == 0)) for t in COUNTS for i in range(5)]
    assert evaluate(recs, COUNTS)["rule_outcome"] == outcome


def test_threshold_is_exact():
    # 19/20 = 95% passes; boundary handled with exact fractions
    recs = [rec("big", f"b{i}", supports=i != 0) for i in range(20)]
    recs += [rec(t, f"{t}{i}") for t in ("small", "tiny") for i in range(5)]
    assert evaluate(recs, COUNTS)["per_type"]["big"]["outcome"] == "PASS"


def test_type_row_counts():
    assert type_row_counts([{"relation_hop2": "b"}, {"relation_hop2": "a"}, {"relation_hop2": "b"}]) == {"a": 1, "b": 2}
