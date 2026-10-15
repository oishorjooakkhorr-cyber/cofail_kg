import csv
import importlib.util
import json
from pathlib import Path

import pandas as pd
import pytest

from cofail_kg.data.biohopr_loader import file_sha256
from test_query_validation import NAMES, TYPE, query

_PATH = Path(__file__).resolve().parents[1] / "scripts/08_validate_queries.py"
_SPEC = importlib.util.spec_from_file_location("s8_script", _PATH)
script = importlib.util.module_from_spec(_SPEC)
_SPEC.loader.exec_module(script)

SPEC = {"d1_status": "PASS", "excluded": False, "R1": ["r1"], "R2": ["r2"], "construction": "BRIDGE"}
FAILED = {"d1_status": "FAIL", "excluded": True, "R1": None, "R2": None, "construction": None}


@pytest.fixture
def s6_files(tmp_path):
    proposal = tmp_path / "proposed.json"
    proposal.write_text(json.dumps({"per_type": {TYPE: {**SPEC, "ambiguity_tag": "R1_AMBIGUOUS",
                                                       "sample_row_ids": ["BH2_00000"]}}}))
    tags = tmp_path / "tags.csv"
    tags.write_text("relation_type,ambiguity_tag\n" + f"{TYPE},R1_AMBIGUOUS\nfailed:type:x,\n")
    mapping = {"per_type": {TYPE: SPEC, "failed:type:x": FAILED},
               "provenance": {"proposal_sha256": file_sha256(proposal)}}
    return proposal, tags, mapping


def test_proposal_supplies_samples_and_tags_for_pass_types_only(s6_files):
    proposal, tags, mapping = s6_files
    assert script.load_proposal(proposal, mapping, tags) == ({TYPE: (["BH2_00000"], "R1_AMBIGUOUS")}, "raw")


def test_proposal_hash_accepts_crlf_checkout_of_committed_lf_bytes_only(s6_files):
    proposal, tags, mapping = s6_files
    lf = json.dumps({"per_type": {TYPE: {**SPEC, "ambiguity_tag": "R1_AMBIGUOUS",
                                         "sample_row_ids": ["BH2_00000"]}}}, indent=1).encode()
    proposal.write_bytes(lf)
    mapping["provenance"]["proposal_sha256"] = file_sha256(proposal)
    proposal.write_bytes(lf.replace(b"\n", b"\r\n"))
    assert script.load_proposal(proposal, mapping, tags)[1] == "lf_normalized"
    proposal.write_bytes(lf.replace(b"\n", b"\r\n").replace(b"BH2_00000", b"BH2_00001"))
    with pytest.raises(ValueError, match="proposal_sha256"):
        script.load_proposal(proposal, mapping, tags)


def test_proposal_rejects_hash_label_and_tag_mismatches(s6_files):
    proposal, tags, mapping = s6_files
    with pytest.raises(ValueError, match="proposal_sha256"):
        script.load_proposal(proposal, {**mapping, "provenance": {"proposal_sha256": "x"}}, tags)
    changed = {**mapping, "per_type": {TYPE: {**SPEC, "R2": ["other"]}}}
    with pytest.raises(ValueError, match="R2"):
        script.load_proposal(proposal, changed, tags)
    tags.write_text(f"relation_type,ambiguity_tag\n{TYPE},NONE\n")
    with pytest.raises(ValueError, match="tag CSV"):
        script.load_proposal(proposal, mapping, tags)


def test_reference_summary_must_come_from_frozen_inputs(tmp_path):
    path = tmp_path / "reference_summary.json"
    provenance = {"biohopr_revision": "rev", "kg_fingerprint": "fp", "relation_mapping_sha256": "map"}
    path.write_text(json.dumps({"provenance": provenance}))
    frozen = {"biohopr_revision": "rev", "kg_fingerprint": "fp", "relation_mapping": "map"}
    script.check_reference_summary(path, frozen)
    with pytest.raises(ValueError, match="relation_mapping"):
        script.check_reference_summary(path, {**frozen, "relation_mapping": "other"})


def test_node_cache_checked_against_fingerprint_and_metadata(tmp_path):
    nodes = pd.DataFrame({"node_index": [1, 10], "node_id": ["a", "b"], "node_type": ["disease", "effect/phenotype"],
                          "node_name": ["Source", "Rash"], "node_source": ["t", "t"]})
    nodes.to_parquet(tmp_path / "primekg_nodes.parquet")
    metadata = {"cache_sha256": {"primekg_nodes.parquet": file_sha256(tmp_path / "primekg_nodes.parquet")},
                "node_type_counts": {"disease": 1, "effect/phenotype": 1}}
    (tmp_path / "primekg_metadata.json").write_text(json.dumps(metadata))
    frozen = {"kg_fingerprint": file_sha256(tmp_path / "primekg_metadata.json")}
    names, counts = script.load_nodes(tmp_path, frozen)
    assert names == {"1": "Source", "10": "Rash"} and counts == {"disease": 1, "effect/phenotype": 1}
    with pytest.raises(ValueError, match="kg_fingerprint"):
        script.load_nodes(tmp_path, {"kg_fingerprint": "other"})


def test_end_to_end_outputs_and_no_overwrite(tmp_path):
    queries = [query(), query(query_id="BH2_00003", row_ids=["BH2_00003"], s=None, B_q=[], gold_bridges=[],
                              T_q=[], T_q_gold_bridges=[], G_q=[], A_star_q=[],
                              unresolved_names=[{"row_id": "BH2_00003", "role": "query", "name": "Source",
                                                 "status": "not_found"}])]
    records = script.validate_all(list(reversed(queries)), {TYPE: (["BH2_00000"], "R1_AMBIGUOUS")},
                                  NAMES, {"effect/phenotype": 4})
    summary = script.write_outputs(tmp_path, records, {"test": "synthetic"})
    with (tmp_path / "query_validation.csv").open(encoding="utf-8", newline="") as handle:
        rows = list(csv.DictReader(handle))
    assert [r["query_id"] for r in rows] == ["BH2_00000", "BH2_00003"]
    assert list(rows[0]) == list(script.COLUMNS)
    assert rows[0]["status"] == "CONSISTENT" and rows[0]["saturation_share"] == "0.25"
    assert rows[0]["contains_validation_row"] == "TRUE" and rows[0]["leaky_question"] == "FALSE"
    assert rows[1]["primary_reason"] == "QUERY_NOT_FOUND" and rows[1]["EXTRA_TARGETS"] == "NA"
    assert rows[1]["saturation_share"] == "NA" and rows[1]["reason_codes"] == "QUERY_NOT_FOUND"
    saved = json.loads((tmp_path / "query_validation_summary.json").read_text())
    assert saved == summary and saved["by_status"] == {"CONSISTENT": 1, "INCONSISTENT": 1}
    before = (tmp_path / "query_validation.csv").read_bytes()
    with pytest.raises(FileExistsError):
        script.write_outputs(tmp_path, records, {})
    assert (tmp_path / "query_validation.csv").read_bytes() == before
