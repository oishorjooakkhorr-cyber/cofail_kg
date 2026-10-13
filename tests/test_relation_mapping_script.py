import importlib.util
import json
from pathlib import Path

import pytest

from test_relation_mapping import run_score

_PATH = Path(__file__).resolve().parents[1] / "scripts/06_relation_mapping.py"
_SPEC = importlib.util.spec_from_file_location("s6_script", _PATH)
script = importlib.util.module_from_spec(_SPEC)
_SPEC.loader.exec_module(script)


def proposal():
    result = run_score(["Target", "Other"])
    candidates = [{"relation_type": "disease:drug:effect/phenotype", **r}
                  for r in result.pop("candidate_scores")]
    per_type = {"disease:drug:effect/phenotype": result}
    return {"frozen": False, "per_type": per_type, "d1": script.evaluate_d1(per_type),
            "provenance": {"test": "synthetic"}}, candidates


def test_reports_include_candidate_scores_and_no_frozen_mapping(tmp_path):
    proposed, candidates = proposal()
    script.write_outputs(tmp_path, proposed, candidates, lambda node: {"name": "test node"})
    assert {p.name for p in tmp_path.iterdir()} == set(script.FILES)
    saved = json.loads((tmp_path / "relation_mapping_proposed.json").read_text())
    assert not saved["frozen"]
    text = (tmp_path / "d1_report.md").read_text(encoding="utf-8")
    assert "UNION" in text and "STOP" in text and "Not frozen" in text
    assert "BH2_" in text and "missing" in text
    assert "bridge_score" in (tmp_path / "relation_mapping_candidates.csv").read_text()
    assert "PROPOSED" in (tmp_path / "relation_ambiguity_tags.csv").read_text()


def test_existing_output_prevents_all_writes(tmp_path):
    existing = tmp_path / "relation_ambiguity_tags.csv"
    existing.write_text("do not overwrite")
    proposed, candidates = proposal()
    with pytest.raises(FileExistsError):
        script.write_outputs(tmp_path, proposed, candidates, lambda node: {})
    assert list(tmp_path.iterdir()) == [existing]
    assert existing.read_text() == "do not overwrite"


def test_input_validation_rejects_stale_s5_counts_and_stop():
    rows = [{"relation_hop2": "t"}]
    s5 = {"rule_outcome": "ROLES_SUPPORTED", "per_type": {"t": {"rows_in_dataset": 1}},
          "provenance": {"biohopr_revision": "a", "kg_fingerprint": "b"}}
    frozen = {"biohopr_revision": "a", "kg_fingerprint": "b"}
    script.validate_s5(rows, s5, frozen)
    s5["per_type"]["t"]["rows_in_dataset"] = 2
    with pytest.raises(ValueError, match="counts"):
        script.validate_s5(rows, s5, frozen)
    s5["per_type"]["t"]["rows_in_dataset"] = 1
    s5["rule_outcome"] = "STOP"
    with pytest.raises(ValueError, match="S5"):
        script.validate_s5(rows, s5, frozen)
