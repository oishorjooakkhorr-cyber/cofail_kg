import importlib.util
import json
from pathlib import Path

import pandas as pd
import pytest

from cofail_kg.data.biohopr_loader import file_sha256
from test_reference_sets import build, mapping, row, find, graph
from test_primekg_prepare import raw_graph


_PATH = Path(__file__).resolve().parents[1] / "scripts/07_build_reference_sets.py"
_SPEC = importlib.util.spec_from_file_location("s7_script", _PATH)
script = importlib.util.module_from_spec(_SPEC)
_SPEC.loader.exec_module(script)


def test_parquet_round_trip_and_counts_including_empty_nested_lists(tmp_path):
    queries, targets = build()
    summary = script.write_outputs(tmp_path, queries, targets, {"test": "synthetic"})
    q = pd.read_parquet(tmp_path / "reference_queries.parquet").iloc[0]
    assert q["T_q"].tolist() == ["10"] and q["unresolved_names"].tolist() == []
    assert pd.read_parquet(tmp_path / "reference_targets.parquet").to_dict("records") == targets
    saved = json.loads((tmp_path / "reference_summary.json").read_text())
    assert saved == summary and saved["overall"]["dataset_rows"] == 1
    assert saved["provenance"] == {"test": "synthetic"}


def test_empty_outputs_have_schema_and_zero_counts(tmp_path):
    script.write_outputs(tmp_path, [], [], {})
    assert list(pd.read_parquet(tmp_path / "reference_targets.parquet")) == ["query_id", "bridge", "target"]
    assert "query_id" in pd.read_parquet(tmp_path / "reference_queries.parquet")


def test_resolution_flags_survive_parquet_serialization(tmp_path):
    from cofail_kg.evaluation.reference_sets import build_reference_sets

    def finder(name, kind):
        return [] if name == "Source" else find(name, kind)

    queries, targets = build_reference_sets([row(answer=["Unknown"])], mapping(), finder, graph({}))
    script.write_outputs(tmp_path, queries, targets, {})
    q = pd.read_parquet(tmp_path / "reference_queries.parquet").iloc[0]
    assert q["suffix_resolutions"][0]["node_id"] == "1"
    assert q["unresolved_names"][0]["name"] == "Unknown"
    assert q["unresolved_names"][0]["role"] == "answer"


def test_existing_artifact_prevents_any_overwrite(tmp_path):
    existing = tmp_path / "reference_targets.parquet"
    existing.write_bytes(b"preserve")
    with pytest.raises(FileExistsError):
        script.write_outputs(tmp_path, *build(), {})
    assert existing.read_bytes() == b"preserve" and list(tmp_path.iterdir()) == [existing]


def test_mapping_verification_rejects_modified_unfrozen_and_stale_inputs(tmp_path):
    path = tmp_path / "mapping.json"
    value = {"frozen": True, "d1": {"outcome": "PROCEED"}, "per_type": mapping(),
             "provenance": {"biohopr_revision": "revision", "kg_fingerprint": "fingerprint"}}
    path.write_text(json.dumps(value))
    frozen = {"relation_mapping": file_sha256(path), **value["provenance"]}
    assert script.load_mapping(path, frozen)["per_type"] == mapping()
    path.write_text(json.dumps({**value, "frozen": False}))
    with pytest.raises(ValueError, match="hash"):
        script.load_mapping(path, frozen)
    frozen["relation_mapping"] = file_sha256(path)
    with pytest.raises(ValueError, match="frozen"):
        script.load_mapping(path, frozen)
    path.write_text(json.dumps(value))
    frozen["relation_mapping"] = file_sha256(path)
    frozen["kg_fingerprint"] = "changed"
    with pytest.raises(ValueError, match="kg_fingerprint"):
        script.load_mapping(path, frozen)


def test_real_index_applies_type_filters_either_direction_and_no_self_target(raw_graph, tmp_path):
    from cofail_kg.evaluation.normalize import index_finder
    from cofail_kg.evaluation.reference_sets import build_reference_sets
    from cofail_kg.kg.prepare import prepare_primekg
    from cofail_kg.kg.primekg_index import PrimeKGIndex

    nodes = pd.read_csv(raw_graph / "nodes.csv")
    nodes.loc[len(nodes)] = [50, "D50", "drug", "Other drug", "test"]
    nodes.to_csv(raw_graph / "nodes.csv", index=False)
    edges = pd.read_csv(raw_graph / "kg.csv")
    reverse_edge = edges[edges.x_index == 30].iloc[0].to_dict()
    reverse_edge.update(y_index=50, y_id="D50", y_type="drug", y_name="Other drug", y_source="test")
    pd.concat([edges, pd.DataFrame([reverse_edge])], ignore_index=True).to_csv(raw_graph / "kg.csv", index=False)
    cache = tmp_path / "cache"
    prepare_primekg(raw_graph, cache)
    kg = PrimeKGIndex(cache)
    relation = "drug:gene/protein:drug"
    selected = {relation: {"d1_status": "PASS", "excluded": False, "construction": "UNION",
                           "R1": ["drug_protein", "drug_effect"], "R2": ["drug_protein"]}}
    rows = [{"row_id": "BH2_00000", "relation_hop2": relation, "hop2": "Alpha",
             "hop1": "Beta protein", "answer": ["Alpha"], "hop2_question_multi": "question"}]
    queries, targets = build_reference_sets(rows, selected, index_finder(kg), kg.neighbors_by_label)
    # The reverse-only 30 -> 10 edge is traversed; phenotype 40 is filtered out.
    assert queries[0]["dead_end_bridges"] == ["2"]
    assert queries[0]["B_q"] == ["30"] and queries[0]["T_q"] == ["50"]
    assert targets == [{"query_id": "BH2_00000", "bridge": "30", "target": "50"}]
    assert queries[0]["unresolved_names"][0]["status"] == "ambiguous"
