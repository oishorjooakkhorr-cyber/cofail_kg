import pytest

from cofail_kg.evaluation.reference_sets import build_reference_sets, summarize
from cofail_kg.kg.primekg_index import normalize_name


TYPE = "disease:drug:effect/phenotype"


def row(i=0, **changes):
    return {"row_id": f"BH2_{i:05d}", "relation_hop2": TYPE,
            "hop2": "Source", "hop1": "Bridge", "answer": ["Target"],
            "hop2_question_multi": "Name all targets", **changes}


def mapping(construction="BRIDGE"):
    return {TYPE: {"d1_status": "PASS", "excluded": False,
                   "R1": ["r1"], "R2": ["r2"], "construction": construction}}


def find(name, kind):
    return {("source", "disease"): ["1"], ("source (disease)", "disease"): ["1"],
            ("bridge", "drug"): ["2"], ("other", "drug"): ["3"],
            ("invalid bridge", "drug"): ["5"],
            ("target", "effect/phenotype"): ["10"],
            ("extra", "effect/phenotype"): ["11"]}.get((normalize_name(name), kind), [])


def graph(edges):
    return lambda node, kind: edges.get((node, kind), {})


def build(rows=None, edges=None, construction="BRIDGE"):
    return build_reference_sets(rows or [row()], mapping(construction), find,
                                graph(edges or {("1", "drug"): {"r1": {"2"}},
                                                ("2", "effect/phenotype"): {"r2": {"10"}}}))


def test_single_bridge_and_gold_sets():
    queries, targets = build()
    q = queries[0]
    assert q["B_q"] == ["2"] and q["dead_end_bridges"] == []
    assert q["T_q"] == q["T_q_gold_bridges"] == q["G_q"] == q["A_star_q"] == ["10"]
    assert q["bq_size"] == q["tq_size"] == q["gq_size"] == 1
    assert targets == [{"query_id": "BH2_00000", "bridge": "2", "target": "10"}]


@pytest.mark.parametrize("construction,gold", [("BRIDGE", ["10"]), ("UNION", ["10", "11"])])
def test_multiple_bridges_shared_target_dead_end_and_constructions(construction, gold):
    queries, targets = build(edges={
        ("1", "drug"): {"r1": {"2", "3", "4"}, "wrong_label": {"5"}},
        ("2", "effect/phenotype"): {"r2": {"10"}},
        ("3", "effect/phenotype"): {"r2": {"10", "11"}},
        ("4", "effect/phenotype"): {"wrong_label": {"11"}},
    }, construction=construction)
    q = queries[0]
    assert q["B_q"] == ["2", "3"] and q["dead_end_bridges"] == ["4"]
    assert q["T_q"] == ["10", "11"] and q["T_q_gold_bridges"] == ["10"]
    assert q["G_q"] == gold
    assert [(t["bridge"], t["target"]) for t in targets] == [("2", "10"), ("3", "10"), ("3", "11")]


def test_no_valid_bridge_keeps_gold_bridge_targets_separate():
    queries, targets = build(edges={
        ("1", "drug"): {"r1": {"4"}},
        ("2", "effect/phenotype"): {"r2": {"10"}},
    })
    q = queries[0]
    assert q["B_q"] == q["T_q"] == [] and targets == []
    assert q["dead_end_bridges"] == ["4"]
    assert q["T_q_gold_bridges"] == ["10"]  # §6 unions over B*, even if not valid.


def test_rows_merge_by_resolved_node_and_gold_answers_are_union():
    rows = [row(8, hop2=" SOURCE ", hop1="Other", answer=["Extra", "Extra"],
                hop2_question_multi="Different text"), row(2)]
    queries, _ = build(rows)
    q = queries[0]
    assert len(queries) == 1 and q["query_id"] == "BH2_00002"
    assert q["row_ids"] == ["BH2_00002", "BH2_00008"]
    assert q["question_texts"] == ["Name all targets", "Different text"]
    assert q["gold_bridges"] == ["2", "3"] and q["A_star_q"] == ["10", "11"]
    assert build(list(reversed(rows))) == build(rows)


def test_unresolved_sources_form_individual_queries_and_preserve_unresolved_names():
    queries, targets = build([row(0, hop2="Missing", hop1="Unknown", answer=["Unknown"]),
                              row(1, hop2="Missing")])
    assert len(queries) == 2 and all(q["s"] is None for q in queries)
    assert targets == [] and all(q["B_q"] == q["T_q"] == [] for q in queries)
    assert [(r["role"], r["name"], r["status"]) for r in queries[0]["unresolved_names"]] == [
        ("query", "Missing", "not_found"), ("bridge", "Unknown", "not_found"),
        ("answer", "Unknown", "not_found")]


def test_suffix_retry_is_flagged_and_ambiguous_names_are_unresolved():
    def finder(name, kind):
        if name == "Source":
            return []
        if name == "Target":
            return ["10", "11"]
        return find(name, kind)
    queries, _ = build_reference_sets([row()], mapping(), finder, graph({}))
    assert queries[0]["s"] == "1"
    assert queries[0]["suffix_resolutions"] == [
        {"row_id": "BH2_00000", "role": "query", "name": "Source", "node_id": "1"}]
    assert queries[0]["unresolved_names"][0]["status"] == "ambiguous"


def test_type_filters_multiple_labels_and_source_exclusion():
    selected = mapping()
    selected[TYPE]["R1"] = ["r1", "also_r1"]
    selected[TYPE]["R2"] = ["r2", "also_r2"]
    edges = {("1", "drug"): {"r1": {"1", "2"}, "also_r1": {"3"}},
             ("2", "effect/phenotype"): {"r2": {"1", "10"}, "also_r2": {"11"}},
             ("3", "effect/phenotype"): {"r2": {"11"}},
             ("1", "wrong_type"): {"r1": {"5"}}}
    q = build_reference_sets([row()], selected, find, graph(edges))[0][0]
    assert q["B_q"] == ["2", "3"] and q["T_q"] == ["10", "11"]


def test_excluded_types_are_not_built_and_same_source_different_type_stays_separate():
    selected = mapping()
    other_type = "disease:drug:gene/protein"
    selected[other_type] = {**selected[TYPE]}
    selected["excluded:type:type"] = {"d1_status": "FAIL", "excluded": True}
    queries, _ = build_reference_sets([row(), row(1, relation_hop2=other_type),
                                      row(2, relation_hop2="excluded:type:type")], selected, find, graph({}))
    assert len(queries) == 2
    summary = summarize(queries, [])
    assert summary["overall"]["queries"] == summary["by_construction"]["BRIDGE"]["queries"] == 2
    assert summary["by_construction"]["UNION"]["queries"] == 0


def test_duplicate_row_ids_and_incomplete_mapping_fail_loudly():
    with pytest.raises(ValueError, match="row_id"):
        build([row(), row()])
    selected = mapping()
    selected[TYPE]["construction"] = None
    with pytest.raises(ValueError, match="construction"):
        build_reference_sets([row()], selected, find, graph({}))
