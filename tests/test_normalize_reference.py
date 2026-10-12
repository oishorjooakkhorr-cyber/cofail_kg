import pytest

from cofail_kg.evaluation.normalize import Resolution, resolve_reference

# (type, normalized name) -> ids; a tiny synthetic graph
NODES = {
    ("disease", "insomnia (disease)"): ["1"],  # suffix form, unique
    ("disease", "twin (disease)"): ["2", "3"],  # suffix form, ambiguous
    ("disease", "flu"): ["4"],  # plain name exists
    ("disease", "flu (disease)"): ["5"],  # ...and a suffixed one: must not be used
    ("disease", "dup"): ["6", "7"],  # plain name ambiguous: no retry
    ("effect/phenotype", "acne (disease)"): ["8"],  # suffixed node of a non-disease type
    ("drug", "aspirin"): ["9"],
}
calls = []


def find(name, node_type):
    calls.append((name, node_type))
    return NODES.get((node_type, " ".join(name.lower().split())), [])


@pytest.fixture(autouse=True)
def _reset():
    calls.clear()


def test_retry_succeeds_with_trailing_space():
    r = resolve_reference(find, "Insomnia ", "disease")
    assert r == Resolution("resolved", "1", via_suffix=True)
    assert calls[-1] == ("insomnia (disease)", "disease")


def test_retry_with_several_matches_stays_unresolved():
    r = resolve_reference(find, "twin", "disease")
    assert (r.status, r.node_id, r.via_suffix) == ("ambiguous", None, False)
    assert not r.resolved


def test_retry_with_no_match_stays_not_found():
    r = resolve_reference(find, "nothing", "disease")
    assert (r.status, r.node_id) == ("not_found", None)
    assert len(calls) == 2  # one retry only


def test_non_disease_type_never_retries():
    r = resolve_reference(find, "acne", "effect/phenotype")
    assert (r.status, r.node_id, r.via_suffix) == ("not_found", None, False)
    assert len(calls) == 1


def test_name_that_already_matches_is_not_retried():
    r = resolve_reference(find, "Flu", "disease")
    assert r == Resolution("resolved", "4", via_suffix=False)
    assert len(calls) == 1


def test_ambiguous_plain_match_is_not_retried():
    r = resolve_reference(find, "dup", "disease")
    assert r.status == "ambiguous" and len(calls) == 1


def test_type_filter_applies():
    assert resolve_reference(find, "aspirin", "drug").node_id == "9"
    assert resolve_reference(find, "aspirin", "disease").status == "not_found"
