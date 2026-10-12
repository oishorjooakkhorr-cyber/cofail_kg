import hashlib
import pandas as pd
import pytest

from cofail_kg.kg.prepare import prepare_primekg
from cofail_kg.utils.frozen_hashes import read_frozen_hashes


@pytest.fixture
def raw_graph(tmp_path):
    raw = tmp_path / "raw"
    raw.mkdir()
    nodes = pd.DataFrame([
        (10, "D10", "drug", "Alpha", "test"),
        (2, "P2", "gene/protein", "Ｂeta  protein", "test"),
        (30, "P30", "gene/protein", "Beta protein", "test"),
        (40, "E40", "effect/phenotype", "acne ", "test"),
        (99, "D99", "disease", "Alpha", "test"),
    ], columns=["node_index", "node_id", "node_type", "node_name", "node_source"])
    nodes.to_csv(raw / "nodes.csv", index=False)
    lookup = nodes.set_index("node_index").to_dict("index")
    records = []
    for x, y, label, display in [
        (10, 2, "drug_protein", "target"),
        (2, 10, "drug_protein", "target"),
        (10, 2, "drug_protein", "enzyme"),
        (30, 10, "drug_protein", "carrier"),
        (10, 40, "drug_effect", "side effect"),
        (10, 40, "drug_effect", "side effect"),
        (2, 2, "protein_protein", "ppi"),
    ]:
        record = {"relation": label, "display_relation": display}
        for side, index in (("x", x), ("y", y)):
            record[f"{side}_index"] = index
            record.update({f"{side}_{key[5:]}": value for key, value in lookup[index].items()})
        records.append(record)
    pd.DataFrame(records).to_csv(raw / "kg.csv", index=False)
    return raw


def test_prepare_preserves_raw_rows_and_is_deterministic(raw_graph, tmp_path):
    cache = tmp_path / "cache"
    original = {p.name: p.read_bytes() for p in raw_graph.iterdir()}
    metadata = prepare_primekg(raw_graph, cache, chunk_size=2)
    edges = pd.read_parquet(cache / "primekg_edges.parquet")
    nodes = pd.read_parquet(cache / "primekg_nodes.parquet")
    assert len(edges) == 7  # Duplicate and reverse rows remain in the cache.
    assert nodes.node_index.tolist() == [2, 10, 30, 40, 99]
    assert metadata["isolated_node_count"] == 1
    assert metadata["reverse_sample"]["matches"] == 4
    assert metadata["reverse_sample"]["size"] == 7
    assert metadata["raw_files"]["kg.csv"]["sha256"] == hashlib.sha256(original["kg.csv"]).hexdigest()
    before = {p.name: p.read_bytes() for p in cache.iterdir()}
    other_cache = tmp_path / "independent-cache"
    assert prepare_primekg(raw_graph, other_cache, chunk_size=2) == metadata
    assert before == {p.name: p.read_bytes() for p in other_cache.iterdir()}
    assert prepare_primekg(raw_graph, cache) == metadata
    assert before == {p.name: p.read_bytes() for p in cache.iterdir()}
    assert original == {p.name: p.read_bytes() for p in raw_graph.iterdir()}


def test_changed_raw_input_cannot_replace_cache(raw_graph, tmp_path):
    cache = tmp_path / "cache"
    prepare_primekg(raw_graph, cache)
    before = (cache / "primekg_metadata.json").read_bytes()
    with (raw_graph / "kg.csv").open("a") as stream:
        stream.write("\n")
    with pytest.raises(ValueError, match="raw inputs differ"):
        prepare_primekg(raw_graph, cache)
    assert (cache / "primekg_metadata.json").read_bytes() == before


def test_conflicting_node_metadata_is_rejected(raw_graph, tmp_path):
    graph = pd.read_csv(raw_graph / "kg.csv")
    graph.loc[0, "x_name"] = "Different name"
    graph.to_csv(raw_graph / "kg.csv", index=False)
    with pytest.raises(ValueError, match="node metadata"):
        prepare_primekg(raw_graph, tmp_path / "cache")
    assert not (tmp_path / "cache/primekg_metadata.json").exists()


def test_freeze_is_explicit_and_preserves_other_hashes(raw_graph, tmp_path):
    cache = tmp_path / "cache"
    frozen = tmp_path / "frozen.yaml"
    frozen.write_text("biohopr_revision: abc\n")
    prepare_primekg(raw_graph, cache)
    assert read_frozen_hashes(frozen) == {"biohopr_revision": "abc"}
    prepare_primekg(raw_graph, cache, frozen_hashes=frozen)
    assert read_frozen_hashes(frozen) == {
        "biohopr_revision": "abc",
        "kg_fingerprint": hashlib.sha256((cache / "primekg_metadata.json").read_bytes()).hexdigest(),
    }


@pytest.mark.parametrize("problem", ["duplicate_index", "missing_endpoint", "invalid_index"])
def test_invalid_node_identity_is_rejected(raw_graph, tmp_path, problem):
    nodes = pd.read_csv(raw_graph / "nodes.csv", dtype=str)
    if problem == "duplicate_index":
        nodes.loc[1, "node_index"] = "10"
    elif problem == "missing_endpoint":
        nodes = nodes[nodes.node_index != "2"]
    else:
        nodes.loc[0, "node_index"] = "10.0"
    nodes.to_csv(raw_graph / "nodes.csv", index=False)
    with pytest.raises(ValueError):
        prepare_primekg(raw_graph, tmp_path / "cache")
    assert not (tmp_path / "cache/primekg_metadata.json").exists()


def test_frozen_conflict_does_not_publish_cache(raw_graph, tmp_path):
    frozen = tmp_path / "frozen.yaml"
    frozen.write_text("kg_fingerprint: previous\n")
    with pytest.raises(ValueError, match="conflicts with the frozen"):
        prepare_primekg(raw_graph, tmp_path / "cache", frozen_hashes=frozen)
    assert not (tmp_path / "cache/primekg_metadata.json").exists()
    assert read_frozen_hashes(frozen) == {"kg_fingerprint": "previous"}
