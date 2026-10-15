import pytest

from cofail_kg.evaluation.dataset_evidence import decision_evidence


def row(i, kind="a", consistent=True, sample=False, share=.5, leaky=False):
    return dict(query_id=str(i), relation_type=kind,
                status="CONSISTENT" if consistent else "INCONSISTENT",
                contains_s6_validation_row=sample, saturation_share=share,
                leaky_question=leaky)


def test_confirmation_excludes_sample_and_uses_inclusive_eighty_percent():
    rows = [row(i, consistent=i < 4) for i in range(5)] + [row(5, consistent=False, sample=True)]
    confirmation, _, _ = decision_evidence(rows, ["a"])
    assert confirmation[0]["confirmation_status"] == "CONFIRMED"
    assert confirmation[0]["confirmation_queries"] == 5
    assert confirmation[0]["consistent_share"] == .8
    assert confirmation[0]["s6_overlap_queries"] == 1


def test_unconfirmable_kept_and_unconfirmed_omitted_from_saturation():
    rows = [row(0, "a", sample=True), row(1, "b", consistent=False)]
    confirmation, saturation, sensitivity = decision_evidence(rows, ["a", "b"])
    assert [r["confirmation_status"] for r in confirmation] == ["UNCONFIRMABLE", "UNCONFIRMED"]
    assert confirmation[0]["consistent_share"] is None
    assert [r["relation_type"] for r in saturation] == ["ALL", "a"]
    assert saturation[0]["queries"] == 1
    assert all(r["relation_type"] != "b" for r in sensitivity)


def test_saturation_strictly_above_threshold_and_includes_leaky_and_sample_queries():
    rows = [row(0, share=.3), row(1, share=.5, leaky=True), row(2, share=.7, sample=True),
            row(3, share=.9), row(4, share=1), row(5, consistent=False, share=1)]
    _, distribution, sensitivity = decision_evidence(rows, ["a"])
    assert distribution[0]["queries"] == 5
    assert distribution[0]["p50"] == .7 and distribution[0]["max"] == 1
    assert distribution[0]["p90"] == pytest.approx(.96)
    assert [r["excluded_queries"] for r in sensitivity if r["relation_type"] == "ALL"] == [4, 3, 2, 1]


def test_empty_distribution_is_explicit_and_input_types_are_checked():
    _, distribution, sensitivity = decision_evidence([row(0, consistent=False)], ["a"])
    assert distribution[0]["queries"] == 0 and distribution[0]["p50"] is None
    assert all(r["excluded_queries"] == 0 for r in sensitivity)
    with pytest.raises(ValueError, match="type"):
        decision_evidence([row(0, "other")], ["a"])


def test_duplicate_ids_rejected():
    with pytest.raises(ValueError, match="Duplicate"):
        decision_evidence([row(0), row(0)], ["a"])


def test_script_artifacts_roundtrip_and_no_overwrite(tmp_path):
    import importlib.util
    import json
    from pathlib import Path
    path = Path(__file__).resolve().parents[1]/"scripts/09_decision_evidence.py"
    spec = importlib.util.spec_from_file_location("s9", path)
    script = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(script)
    tables = decision_evidence([row(0)], ["a"])
    script.write_outputs(tmp_path, *tables, {})
    saved = json.loads((tmp_path/"decision_evidence.json").read_text())
    assert saved["theta"] is None and saved["d2_step3_computed"] is False
    assert saved["mapping_confirmation"][0]["confirmation_status"] == "CONFIRMED"
    assert len(list(tmp_path.iterdir())) == 5
    with pytest.raises(FileExistsError):
        script.write_outputs(tmp_path, *tables, {})
