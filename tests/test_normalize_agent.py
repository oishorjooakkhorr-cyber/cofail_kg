"""Agent normalization against protocol §12; tiny synthetic nodes only."""

import pytest

from cofail_kg.evaluation import normalize
from cofail_kg.evaluation.normalize import resolve_agent
from cofail_kg.kg.primekg_index import PrimeKGIndex, normalize_name


@pytest.fixture
def kg():
    # Use the real lookup methods without loading edges, which §12 never uses.
    index = PrimeKGIndex.__new__(PrimeKGIndex)
    rows = [
        ("1", "drug", "Alpha"), ("2", "disease", "Alpha"),
        ("3", "disease", "Twin"), ("4", "disease", "Twin"),
        ("5", "gene/protein", "Unique protein"),
        ("6", "disease", "Insomnia (disease)"), ("7", "drug", "Insomnia"),
        ("8", "disease", "Flu"), ("9", "disease", "Flu (disease)"),
        ("10", "disease", "Twin (disease)"),
        ("11", "disease", "Split (disease)"),
        ("12", "disease", "Split (disease)"),
        ("13", "effect/phenotype", "Acne (disease)"),
        ("14", "drug", "Cross"), ("15", "gene/protein", "Cross"),
    ]
    index._nodes = {i: {"id": i, "type": kind, "name": name} for i, kind, name in rows}
    index._names = {}
    for i, _, name in rows:
        index._names.setdefault(normalize_name(name), []).append(i)
    return index


@pytest.mark.parametrize("identifier", ["2", 2, " \t2\n"])
def test_canonical_string_integer_and_trimmed_ids(kg, identifier):
    result = resolve_agent(kg, {"id": identifier, "name": "Alpha"}, "disease")
    assert (result.node_id, result.method, result.reason) == ("2", "ID", None)
    assert not result.name_id_mismatch


def test_id_wins_over_name_and_expected_type(kg):
    result = resolve_agent(kg, {"id": "1", "name": "Twin"}, "disease")
    assert (result.node_id, result.method, result.name_id_mismatch) == ("1", "ID", True)


@pytest.mark.parametrize("name", ["alpha", " Alpha ", "Ａlpha", ""])
def test_id_mismatch_compares_the_given_and_canonical_names(kg, name):
    result = resolve_agent(kg, {"id": "2", "name": name}, "disease")
    assert result.node_id == "2" and result.name_id_mismatch


@pytest.mark.parametrize("identifier", ["missing", "", "02", "+2", "2.0", -1])
def test_invalid_id_falls_back_to_unique_target_type(kg, identifier):
    result = resolve_agent(kg, {"id": identifier, "name": "Alpha"}, "disease")
    assert (result.node_id, result.method, result.reason) == ("2", "NAME_TARGET_TYPE", None)
    assert not result.name_id_mismatch


@pytest.mark.parametrize("name", ["Alpha", "  ＡLPHA\t\n"])
def test_exact_normalized_name_prefers_target_type(kg, name):
    result = resolve_agent(kg, {"id": "missing", "name": name}, "drug")
    assert (result.node_id, result.method) == ("1", "NAME_TARGET_TYPE")


def test_ambiguous_target_name_is_unresolved_without_suffix_retry(kg):
    result = resolve_agent(kg, {"id": "missing", "name": "Twin"}, "disease")
    assert (result.node_id, result.method, result.reason) == (None, None, "AMBIGUOUS_NAME")


def test_unique_other_type_is_resolved_for_later_labeling(kg):
    result = resolve_agent(kg, {"id": "missing", "name": "Unique\t protein"}, "disease")
    assert (result.node_id, result.method) == ("5", "NAME_UNIQUE_ANY_TYPE")


def test_ambiguous_any_type_name_is_unresolved(kg):
    result = resolve_agent(kg, {"id": "missing", "name": "Cross"}, "disease")
    assert (result.node_id, result.reason) == (None, "AMBIGUOUS_NAME")


@pytest.mark.parametrize("name", ["missing", "Alph", "Álpha", ""])
def test_no_match_has_no_fuzzy_fallback(kg, name):
    result = resolve_agent(kg, {"id": "missing", "name": name}, "disease")
    assert (result.node_id, result.method, result.reason) == (None, None, "NO_MATCH")


def test_disease_suffix_precedes_unique_wrong_type(kg):
    result = resolve_agent(kg, {"id": "missing", "name": " Insomnia "}, "disease")
    assert (result.node_id, result.method, result.via_suffix) == ("6", "NAME_TARGET_TYPE", True)


def test_direct_target_name_precedes_suffix(kg):
    result = resolve_agent(kg, {"id": "missing", "name": "Flu"}, "disease")
    assert result.node_id == "8" and not result.via_suffix


def test_ambiguous_disease_suffix_is_unresolved(kg):
    result = resolve_agent(kg, {"id": "missing", "name": "Split"}, "disease")
    assert (result.node_id, result.reason) == (None, "AMBIGUOUS_NAME")


def test_failed_disease_suffix_still_allows_unique_original_name(kg):
    kg._nodes["16"] = {"id": "16", "type": "drug", "name": "Split"}
    kg._names["split"] = ["16"]
    result = resolve_agent(kg, {"id": "missing", "name": "Split"}, "disease")
    assert (result.node_id, result.method) == ("16", "NAME_UNIQUE_ANY_TYPE")


def test_other_target_types_never_use_disease_suffix(kg):
    result = resolve_agent(kg, {"id": "missing", "name": "Acne"}, "effect/phenotype")
    assert result.reason == "NO_MATCH"


@pytest.mark.parametrize("item", [
    None, {}, {"id": True, "name": "Alpha"}, {"id": 2.0, "name": "Alpha"},
    {"id": None, "name": "Alpha"}, {"id": "2", "name": None},
])
def test_nonparsed_answer_items_are_rejected(kg, item):
    with pytest.raises(ValueError, match="string/integer id and string name"):
        resolve_agent(kg, item, "disease")


def test_index_failure_is_not_silently_classified_as_no_match(kg, monkeypatch):
    def broken_lookup(name, node_type=None):
        raise OSError("cache failure")

    monkeypatch.setattr(kg, "find_by_name", broken_lookup)
    with pytest.raises(OSError, match="cache failure"):
        resolve_agent(kg, {"id": "missing", "name": "Alpha"}, "disease")


def test_duplicates_are_removed_after_id_and_name_resolution(kg):
    items = [{"id": "2", "name": "Alpha"}, {"id": 2, "name": "wrong"},
             {"id": "missing", "name": "Alpha"}, {"id": "5", "name": "Unique protein"}]
    result = normalize.normalize_agent_answers(kg, items, "disease")
    assert [answer.node_id for answer in result.answers] == ["2", "5"]
    assert result.kept_indices == [0, 3]
    assert result.duplicates_removed == 2
    # Per-item evidence survives removal, including a duplicate's mismatch flag.
    assert [answer.method for answer in result.items] == ["ID", "ID", "NAME_TARGET_TYPE", "ID"]
    assert result.items[1].name_id_mismatch
    assert items[1] == {"id": 2, "name": "wrong"}


def test_identical_unresolved_submissions_are_deduplicated(kg):
    items = [{"id": "missing", "name": "Twin"}, {"id": "missing", "name": "Twin"},
             {"id": "bad", "name": "absent"}, {"id": "bad", "name": "absent"}]
    result = normalize.normalize_agent_answers(kg, items, "disease")
    assert [answer.reason for answer in result.answers] == ["AMBIGUOUS_NAME", "NO_MATCH"]
    assert result.kept_indices == [0, 2] and result.duplicates_removed == 2


def test_distinct_unresolved_submissions_are_kept(kg):
    items = [{"id": "bad", "name": "absent"}, {"id": "other", "name": "absent"},
             {"id": "bad", "name": "ABSENT"}, {"id": "bad", "name": " absent "},
             {"id": -1, "name": "absent"}, {"id": "-1", "name": "absent"}]
    result = normalize.normalize_agent_answers(kg, items, "disease")
    assert result.kept_indices == list(range(6)) and result.duplicates_removed == 0
    assert all(answer.reason == "NO_MATCH" for answer in result.answers)


def test_different_valid_ids_with_the_same_name_are_not_duplicates(kg):
    result = normalize.normalize_agent_answers(
        kg, [{"id": "1", "name": "Alpha"}, {"id": "2", "name": "Alpha"}], "disease")
    assert [answer.node_id for answer in result.answers] == ["1", "2"]
    assert result.duplicates_removed == 0


def test_first_occurrence_order_is_retained(kg):
    items = [{"id": "5", "name": "Unique protein"}, {"id": "bad", "name": "none"},
             {"id": "2", "name": "Alpha"}, {"id": "5", "name": "wrong"},
             {"id": "bad", "name": "none"}]
    result = normalize.normalize_agent_answers(kg, items, "disease")
    assert [answer.node_id for answer in result.answers] == ["5", None, "2"]
    assert result.kept_indices == [0, 1, 2] and result.duplicates_removed == 2


def test_empty_answer_list(kg):
    result = normalize.normalize_agent_answers(kg, [], "disease")
    assert result.items == result.answers == result.kept_indices == []
    assert result.duplicates_removed == 0


def test_batch_rejects_invalid_items(kg):
    with pytest.raises(ValueError, match="string/integer id and string name"):
        normalize.normalize_agent_answers(kg, [{"id": True, "name": "Alpha"}], "disease")
