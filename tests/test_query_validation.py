import pytest

from cofail_kg.evaluation.query_validation import (
    REASON_ORDER, leak_matches, multiplicity, summarize, validate_query)

TYPE = "disease:drug:effect/phenotype"
NAMES = {"1": "Source", "2": "Bridgeol", "3": "Otherol", "10": "Rash", "11": "Fever spike"}


def query(**changes):
    """A CONSISTENT single-bridge BRIDGE-type S7 record; `changes` override fields."""
    q = {"query_id": "BH2_00000", "row_ids": ["BH2_00000"], "s": "1",
         "question_texts": ["Name all effects of drugs for disease Source."],
         "query_names": ["Source"], "gold_bridge_names": ["Bridgeol"], "gold_answer_names": ["Rash"],
         "Type_S": "disease", "Type_B": "drug", "Type_T": "effect/phenotype",
         "relation_type": TYPE, "construction": "BRIDGE",
         "gold_bridges": ["2"], "B_q": ["2"], "dead_end_bridges": [],
         "T_q": ["10"], "T_q_gold_bridges": ["10"], "G_q": ["10"], "A_star_q": ["10"],
         "unresolved_names": [], "suffix_resolutions": []}
    q.update(changes)
    return q


def validate(q, validation_rows=(), count=100):
    return validate_query(q, validation_rows=list(validation_rows), ambiguity_tag="R1_AMBIGUOUS",
                          type_t_node_count=count, node_name=NAMES.__getitem__)


def unresolved(role, name, row_id="BH2_00000"):
    return {"row_id": row_id, "role": role, "name": name, "status": "not_found"}


def true_codes(r):
    return [c for c in REASON_ORDER if r[c] == "TRUE"]


def test_consistent_baseline():
    r = validate(query())
    assert r["status"] == "CONSISTENT" and r["primary_reason"] == "NONE" and r["reason_codes"] == []
    assert all(r[c] == "FALSE" for c in REASON_ORDER)
    assert r["multiplicity"] == "SINGLE_BRIDGE" and r["dead_end_count"] == 0
    assert r["saturation_share"] == 0.01 and r["leaky_question"] is False


@pytest.mark.parametrize("code,changes", [
    ("QUESTION_TEXT_MISMATCH", {"row_ids": ["BH2_00000", "BH2_00001"],
                                "question_texts": ["Name all effects A.", "Name all effects B."]}),
    ("BRIDGE_NOT_FOUND", {"gold_bridge_names": ["Bridgeol", "Ghost"],
                          "unresolved_names": [unresolved("bridge", "Ghost")]}),
    ("GOLD_BRIDGE_NOT_VALID", {"gold_bridges": ["2", "3"], "dead_end_bridges": ["3"]}),
    ("GOLD_UNMAPPED", {"gold_answer_names": ["Rash", "Unknown"],
                       "unresolved_names": [unresolved("answer", "Unknown")]}),
    ("GOLD_MISSING_FROM_KG", {"A_star_q": ["10", "11"], "gold_answer_names": ["Fever spike", "Rash"]}),
    ("EXTRA_TARGETS", {"T_q": ["10", "11"], "T_q_gold_bridges": ["10", "11"], "G_q": ["10", "11"]}),
])
def test_one_case_per_reason_code(code, changes):
    r = validate(query(**changes))
    assert r["status"] == "INCONSISTENT" and r["primary_reason"] == code
    assert true_codes(r) == r["reason_codes"] == [code]


def test_query_not_found_marks_s_dependent_codes_na_and_keeps_the_others():
    r = validate(query(s=None, B_q=[], gold_bridges=[], T_q=[], T_q_gold_bridges=[], G_q=[], A_star_q=[],
                       question_texts=["Name all A.", "Name all B."], row_ids=["BH2_00000"],
                       unresolved_names=[unresolved("query", "Source"), unresolved("answer", "Rash")]))
    assert r["primary_reason"] == "QUERY_NOT_FOUND"
    assert r["reason_codes"] == ["QUERY_NOT_FOUND", "QUESTION_TEXT_MISMATCH", "GOLD_UNMAPPED"]
    assert r["GOLD_BRIDGE_NOT_VALID"] == r["GOLD_MISSING_FROM_KG"] == r["EXTRA_TARGETS"] == "NA"
    assert r["BRIDGE_NOT_FOUND"] == "FALSE"
    assert r["saturation_share"] is None and r["multiplicity"] == "NO_BRIDGE"


def test_several_codes_primary_follows_protocol_order():
    r = validate(query(gold_bridges=["2", "3"], A_star_q=["11"], gold_answer_names=["Fever spike", "Gone"],
                       unresolved_names=[unresolved("answer", "Gone")]))
    assert r["reason_codes"] == ["GOLD_BRIDGE_NOT_VALID", "GOLD_UNMAPPED", "GOLD_MISSING_FROM_KG",
                                 "EXTRA_TARGETS"]
    assert r["primary_reason"] == "GOLD_BRIDGE_NOT_VALID"


@pytest.mark.parametrize("changes", [
    {"dead_end_bridges": ["3"]},  # reached through R1 but T_q(3) is empty
    {},                           # not reached through R1 at all
])
def test_resolved_gold_bridge_outside_b_q(changes):
    r = validate(query(gold_bridges=["2", "3"], gold_bridge_names=["Bridgeol", "Otherol"], **changes))
    assert r["status"] == "INCONSISTENT" and r["reason_codes"] == ["GOLD_BRIDGE_NOT_VALID"]


def test_unmapped_gold_name_with_all_resolved_answers_matching_is_inconsistent():
    r = validate(query(gold_answer_names=["Rash", "Mystery"],
                       unresolved_names=[unresolved("answer", "Mystery")]))
    assert r["gold_size"] == r["gq_size"] == 1  # resolved A*_q equals G_q exactly
    assert r["status"] == "INCONSISTENT" and r["reason_codes"] == ["GOLD_UNMAPPED"]


def test_differing_question_texts_in_a_two_row_query():
    r = validate(query(row_ids=["BH2_00000", "BH2_00007"],
                       question_texts=["Name all effects of X.", "Name all effects of X ."]))
    assert r["reason_codes"] == ["QUESTION_TEXT_MISMATCH"] and r["n_rows"] == 2
    same = validate(query(row_ids=["BH2_00000", "BH2_00007"], question_texts=["Same."] * 2))
    assert same["status"] == "CONSISTENT"


@pytest.mark.parametrize("construction,status,codes", [
    ("BRIDGE", "CONSISTENT", []),
    ("UNION", "INCONSISTENT", ["EXTRA_TARGETS"]),
])
def test_construction_reference_chooses_t_q_gold_bridges_or_t_q(construction, status, codes):
    g_q = ["10"] if construction == "BRIDGE" else ["10", "11"]
    r = validate(query(construction=construction, B_q=["2", "3"], T_q=["10", "11"],
                       T_q_gold_bridges=["10"], G_q=g_q, A_star_q=["10"]))
    assert r["status"] == status and r["reason_codes"] == codes
    assert r["multiplicity"] == "MULTI_BRIDGE" and r["gq_size"] == len(g_q)


def test_union_type_consistent_when_gold_equals_t_q():
    r = validate(query(construction="UNION", B_q=["2", "3"], T_q=["10", "11"], T_q_gold_bridges=["10"],
                       G_q=["10", "11"], A_star_q=["10", "11"]))
    assert r["status"] == "CONSISTENT"


def test_stored_g_q_drift_raises():
    with pytest.raises(ValueError, match="G_q"):
        validate(query(construction="UNION", T_q=["10", "11"], G_q=["10"]))


def test_unresolved_query_record_must_agree_with_s():
    with pytest.raises(ValueError, match="disagree"):
        validate(query(unresolved_names=[unresolved("query", "Source")]))


def test_question_naming_its_bridge_is_leaky():
    r = validate(query(question_texts=["Which effects follow Bridgeol, used for Source?"]))
    assert r["leaky_question"] is True and r["leaky_matches"] == ["BIOHOPR:bridge:Bridgeol",
                                                                  "PRIMEKG:bridge:Bridgeol"]
    assert r["status"] == "CONSISTENT"  # the flag is separate from the status


def test_leak_through_primekg_name_only_and_answer_name():
    r = validate(query(gold_bridge_names=["bridgeol hcl"],
                       question_texts=["Is bridgeol linked to a rash?"]))
    assert r["leaky_matches"] == ["BIOHOPR:answer:Rash", "PRIMEKG:answer:Rash", "PRIMEKG:bridge:Bridgeol"]


def test_leak_rules_length_whole_word_case_and_whitespace():
    text = ["Name  all EFFECTS of fever   spike drugs, for flu, eyes and Rashes."]
    named = [("BIOHOPR", "answer", "flu"),            # 3 characters: ignored
             ("BIOHOPR", "answer", "rash"),           # only inside "Rashes": not a whole word
             ("BIOHOPR", "answer", " Fever spike "),  # case and whitespace normalized: matches
             ("BIOHOPR", "answer", "eyes")]           # exactly 4 characters: matches
    assert leak_matches(text, named) == [("BIOHOPR", "answer", " Fever spike "),
                                         ("BIOHOPR", "answer", "eyes")]
    assert leak_matches(["a-eyes."], [("PRIMEKG", "answer", "eyes")]) == [("PRIMEKG", "answer", "eyes")]
    assert leak_matches(["eyes_x"], [("PRIMEKG", "answer", "eyes")]) == []


def test_leak_checks_every_question_text_of_the_query():
    r = validate(query(row_ids=["BH2_00000", "BH2_00001"],
                       question_texts=["Name all effects.", "Name all effects of Rash."]))
    assert r["leaky_question"] is True and "QUESTION_TEXT_MISMATCH" in r["reason_codes"]


def test_multiplicity_saturation_and_validation_rows():
    assert [multiplicity(n) for n in (0, 1, 2, 9)] == ["NO_BRIDGE", "SINGLE_BRIDGE", "MULTI_BRIDGE",
                                                       "MULTI_BRIDGE"]
    r = validate(query(row_ids=["BH2_00000", "BH2_00004"], question_texts=["Q."] * 2,
                       T_q=["10", "11"], T_q_gold_bridges=["10", "11"], G_q=["10", "11"],
                       A_star_q=["10", "11"], dead_end_bridges=["7", "8"]),
                 validation_rows=["BH2_00004", "BH2_00009"], count=8)
    assert r["saturation_share"] == 0.25 and r["dead_end_count"] == 2
    assert r["contains_validation_row"] is True and r["validation_row_ids"] == ["BH2_00004"]
    assert validate(query(), validation_rows=["BH2_00009"])["contains_validation_row"] is False


def test_summary_counts():
    records = [validate(query()),
               validate(query(query_id="BH2_00001", row_ids=["BH2_00001"], construction="UNION",
                              T_q=["10", "11"], G_q=["10", "11"]), validation_rows=["BH2_00001"]),
               validate(query(query_id="BH2_00002", row_ids=["BH2_00002"], s=None, B_q=[], gold_bridges=[],
                              T_q=[], T_q_gold_bridges=[], G_q=[], A_star_q=[],
                              unresolved_names=[unresolved("query", "Source", "BH2_00002")]))]
    s = summarize(records)
    assert s["queries"] == 3 and s["by_status"] == {"CONSISTENT": 1, "INCONSISTENT": 2}
    assert s["by_primary_reason"] == {"EXTRA_TARGETS": 1, "NONE": 1, "QUERY_NOT_FOUND": 1}
    assert s["by_construction"]["UNION"] == {"queries": 1, "CONSISTENT": 0, "INCONSISTENT": 1}
    assert s["by_multiplicity"]["NO_BRIDGE"]["INCONSISTENT"] == 1
    assert s["reason_code_counts"]["EXTRA_TARGETS"] == {"TRUE": 1, "NA": 1}
    assert s["contains_validation_row"]["queries"] == 1 and s["saturation_na"] == 1
    assert s["by_ambiguity_tag"] == {"R1_AMBIGUOUS": {"queries": 3, "CONSISTENT": 1, "INCONSISTENT": 2}}


def test_accepts_real_s7_records():
    from test_reference_sets import build, row

    queries, _ = build(rows=[row(), row(1, answer=["Target", "Nowhere"])])
    names = {"1": "Source", "2": "Bridge", "10": "Target"}
    r = validate_query(queries[0], validation_rows=["BH2_00001"], ambiguity_tag="NONE",
                       type_t_node_count=4, node_name=names.__getitem__)
    assert r["n_rows"] == 2 and r["reason_codes"] == ["GOLD_UNMAPPED"]
    assert r["contains_validation_row"] is True and r["saturation_share"] == 0.25
