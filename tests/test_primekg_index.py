import pandas as pd
import pytest

from cofail_kg.kg.prepare import prepare_primekg
from cofail_kg.kg.primekg_index import EdgeConvention, PrimeKGIndex
from test_primekg_prepare import raw_graph


@pytest.fixture
def cache(raw_graph, tmp_path):
    path = tmp_path / "cache"
    prepare_primekg(raw_graph, path)
    return path


@pytest.fixture
def index(cache):
    return PrimeKGIndex(cache)


def test_neighbors_are_unique_numeric_sorted_and_bidirectional(index):
    assert [node["id"] for node in index.neighbors("10")] == ["2", "30", "40"]
    assert [node["id"] for node in index.neighbors("2")] == ["2", "10"]
    assert [node["id"] for node in index.neighbors("40")] == ["10"]
    assert index.degree("10") == 3
    assert index.degree("99") == 0


def test_filters_use_relation_not_display_label(index):
    assert [node["id"] for node in index.neighbors("10", "drug_protein")] == ["2", "30"]
    assert [node["id"] for node in index.neighbors("10", neighbor_type="effect/phenotype")] == ["40"]
    assert index.neighbors("10", "target") == []
    assert index.neighbors("10", "drug_effect", "gene/protein") == []


def test_candidate_labels_cover_both_directions_and_keep_display_information(index):
    assert index.candidate_labels("drug", "gene/protein") == {
        "drug_protein": ["carrier", "enzyme", "target"]}
    assert index.candidate_labels("gene/protein", "drug") == index.candidate_labels("drug", "gene/protein")
    assert index.candidate_labels("drug", "disease") == {}


def test_neighbors_by_label_uses_same_traversal_and_type_filter(index):
    assert index.neighbors_by_label("10", "gene/protein") == {"drug_protein": {"2", "30"}}
    assert index.neighbors_by_label("40", "drug") == {"drug_effect": {"10"}}
    assert index.neighbors_by_label("99", "drug") == {}


def test_neighbor_display_labels_belong_to_that_neighbor(index):
    neighbors = index.neighbors("10", "drug_protein")
    assert neighbors[0]["display_labels"] == ["enzyme", "target"]
    assert neighbors[1]["display_labels"] == ["carrier"]


def test_relation_summaries_merge_display_labels_and_count_unique_neighbors(index):
    assert index.relations_of("10") == [
        {"label": "drug_effect", "display_labels": ["side effect"],
         "neighbor_types": ["effect/phenotype"], "neighbor_count": 1},
        {"label": "drug_protein", "display_labels": ["carrier", "enzyme", "target"],
         "neighbor_types": ["gene/protein"], "neighbor_count": 2},
    ]
    assert index.relations_of("99") == []


def test_name_matching_keeps_ambiguity_and_applies_approved_whitespace_rule(index):
    assert [node["id"] for node in index.find_by_name("  BETA\tprotein\n")] == ["2", "30"]
    assert [node["id"] for node in index.find_by_name("alpha")] == ["10", "99"]
    assert [node["id"] for node in index.find_by_name("alpha", "disease")] == ["99"]
    assert index.find_by_name("Béta protein") == []
    assert index.find_by_name("acne")[0]["name"] == "acne "  # Original stored name retained.


def test_lookup_returns_decimal_id_and_does_not_expose_mutable_state(index):
    node = index.get_node(10)
    assert node == {"id": "10", "name": "Alpha", "type": "drug", "source": "test", "source_id": "D10"}
    node["name"] = "Changed"
    assert index.get_node("10")["name"] == "Alpha"
    with pytest.raises(KeyError, match="Unknown node"):
        index.get_node("12345")


def test_all_traversal_methods_share_the_edge_convention(cache):
    index = PrimeKGIndex(cache, convention=EdgeConvention("outgoing"))
    assert [node["id"] for node in index.neighbors("10")] == ["2", "40"]
    assert index.degree("10") == 2
    assert index.relations_of("10")[1]["neighbor_count"] == 1
    assert index.relations_of("40") == []
    with pytest.raises(ValueError, match="edge convention"):
        EdgeConvention("unknown")


def test_corrupted_cache_is_rejected(cache):
    path = cache / "primekg_nodes.parquet"
    nodes = pd.read_parquet(path)
    nodes.loc[0, "node_name"] = "changed"
    nodes.to_parquet(path, index=False)
    with pytest.raises(ValueError, match="checksum mismatch"):
        PrimeKGIndex(cache)
