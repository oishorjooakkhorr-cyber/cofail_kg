import pytest

from cofail_kg.evaluation.query_validation import validate_queries, summarize


def query(**changes):
    return dict(query_id="q1", row_ids=["r1"], s="1", relation_type="a:b:c",
                construction="BRIDGE", Type_T="c", question_texts=["Name all targets"],
                gold_bridge_names=["Bridge"], gold_answer_names=["Target"],
                gold_bridges=["2"], B_q=["2"], dead_end_bridges=["3"],
                T_q=["10", "11"], G_q=["10"], A_star_q=["10"],
                unresolved_names=[], **changes)


def validate(q):
    return validate_queries([q], {"c": 10}, {"r1"}, {"a:b:c": "NONE"})[0]


def test_consistent_bridge_uses_gq_not_union_and_records_s9_fields():
    r = validate(query())
    assert r["status"] == "CONSISTENT" and r["reason_codes"] == []
    assert r["saturation_share"] == .2 and r["target_type_nodes"] == 10
    assert r["contains_s6_validation_row"] and r["s6_validation_row_ids"] == ["r1"]
    assert r["bridge_multiplicity"] == "SINGLE_BRIDGE" and r["dead_end_bridge_count"] == 1


@pytest.mark.parametrize("code,changes", [
    ("QUERY_NOT_FOUND", {"s": None}),
    ("QUESTION_TEXT_MISMATCH", {"question_texts": ["a", "b"]}),
    ("BRIDGE_NOT_FOUND", {"unresolved_names": [{"role": "bridge"}]}),
    ("GOLD_BRIDGE_NOT_VALID", {"gold_bridges": ["9"]}),
    ("GOLD_UNMAPPED", {"unresolved_names": [{"role": "answer"}]}),
    ("GOLD_MISSING_FROM_KG", {"A_star_q": ["10", "12"]}),
    ("EXTRA_TARGETS", {"G_q": ["10", "11"]}),
])
def test_each_reason(code, changes):
    q = query()
    q.update(changes)
    r = validate(q)
    assert r["status"] == "INCONSISTENT" and r["primary_reason"] == code
    assert r[code] is True


def test_multiple_reasons_and_na_when_source_missing():
    q = query()
    q.update(s=None, question_texts=["a", "b"], gold_bridges=["9"],
             A_star_q=["12"], unresolved_names=[{"role": "bridge"}, {"role": "answer"}])
    r = validate(q)
    assert r["reason_codes"] == ["QUERY_NOT_FOUND", "QUESTION_TEXT_MISMATCH", "BRIDGE_NOT_FOUND", "GOLD_UNMAPPED"]
    assert all(r[k] == "NA" for k in ("GOLD_BRIDGE_NOT_VALID", "GOLD_MISSING_FROM_KG", "EXTRA_TARGETS"))


@pytest.mark.parametrize("text,leaky", [("Find BRIDGE.", True), ("Find target!", True),
    ("Find bridges and targeted therapies", False), ("Find (red fox)", True),
    ("Find CAT", False)])
def test_leakage_whole_phrase_case_and_minimum_length(text, leaky):
    q = query()
    q.update(question_texts=[text], gold_answer_names=["Target", "red fox", "cat"])
    assert validate(q)["leaky_question"] is leaky


def test_union_multiplicity_and_summary():
    q = query()
    q.update(construction="UNION", B_q=["2", "4"], G_q=["10", "11"])
    r = validate(q)
    assert r["primary_reason"] == "EXTRA_TARGETS" and r["bridge_multiplicity"] == "MULTI_BRIDGE"
    q.update(B_q=[], gold_bridges=[])
    assert validate(q)["bridge_multiplicity"] == "NO_BRIDGE"
    s = summarize([r])
    assert s["overall"]["queries"] == 1
    assert s["by_relation_type"]["a:b:c"]["status"] == {"INCONSISTENT": 1}


def test_missing_target_denominator_fails():
    with pytest.raises(ValueError, match="target"):
        validate_queries([query()], {"c": 0}, set(), {"a:b:c": "NONE"})


def test_upstream_approved_leakage_checks_graph_names_and_normalizes_both_sides():
    q = query()
    q.update(question_texts=["Find ＲＥＤ   fox."], gold_bridge_names=["unrelated"],
             gold_answer_names=["unrelated"])
    result = validate_queries([q], {"c":10}, set(), {"a:b:c":"NONE"},
                              {"2":"Blue fox", "10":"red fox"})[0]
    assert result["leaky_question"] and result["leaked_names"] == ["red fox"]


def test_leakage_minimum_length_is_measured_after_normalization():
    q = query()
    q.update(question_texts=["cat"], gold_bridge_names=[" cat "], gold_answer_names=[])
    assert validate(q)["leaky_question"] is False


def test_artifact_roundtrip_and_overwrite_protection(tmp_path):
    import csv
    import importlib.util
    import json
    from pathlib import Path
    path = Path(__file__).resolve().parents[1] / "scripts/08_validate_queries.py"
    spec = importlib.util.spec_from_file_location("s8", path)
    script = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(script)
    records = [validate(query())]
    script.write_outputs(tmp_path, records, summarize(records))
    with (tmp_path / script.FILES[0]).open(newline="", encoding="utf-8") as stream:
        saved = list(csv.DictReader(stream))
    assert json.loads(saved[0]["row_ids"]) == ["r1"]
    assert saved[0]["saturation_share"] == "0.2"
    summary = json.loads((tmp_path / script.FILES[1]).read_text())
    assert summary["validation_csv_sha256"] == script.file_sha256(tmp_path / script.FILES[0])
    with pytest.raises(FileExistsError):
        script.write_outputs(tmp_path, records, summary)
