import hashlib
import importlib.util
from pathlib import Path

import pytest

_PATH = Path(__file__).resolve().parents[1] / "scripts/explore_s5_field_role_preview.py"
_spec = importlib.util.spec_from_file_location("field_role_preview", _PATH)
fr = importlib.util.module_from_spec(_spec)
_spec.loader.exec_module(fr)

TYPES = ("disease", "drug", "effect/phenotype")
# id: (type, name)
NODES = {
    "1": ("disease", "Diabetes"),
    "2": ("drug", "DrugA"),  # stored bridge
    "3": ("drug", "DrugB"),  # other bridge
    "4": ("drug", "DrugC"),  # drug NOT adjacent to s
    "10": ("effect/phenotype", "Nausea"),  # via A (and B)
    "11": ("effect/phenotype", "Rash"),  # via B only
    "12": ("effect/phenotype", "Fever"),  # via C only -> neither
    "13": ("effect/phenotype", "Twin"),
    "14": ("effect/phenotype", "Twin"),  # ambiguous name
    "20": ("gene/protein", "Diabetes"),  # same name, other type: must not make s ambiguous
}
EDGES = [("1", "2"), ("1", "3"), ("2", "10"), ("3", "10"), ("3", "11"), ("4", "12"), ("2", "1")]


def find(name, node_type):
    key = " ".join(name.lower().split())
    return sorted((i for i, (t, n) in NODES.items() if t == node_type and n.lower() == key), key=int)


def nbrs(node_id, node_type):
    out = {b for a, b in EDGES if a == node_id} | {a for a, b in EDGES if b == node_id}
    return {n for n in out if NODES[n][0] == node_type}


def row(hop2="Diabetes", hop1="DrugA", answer=("Nausea", "Rash", "Fever", "Twin", "Missing")):
    return {"hop2": hop2, "hop1": hop1, "answer": list(answer), "row_id": "BH2_00000"}


def test_partition_and_counts():
    r = fr.analyse_row(row(), TYPES, find, nbrs)
    assert (r["query_status"], r["query_node_id"]) == ("resolved", "1")
    assert (r["bridge_status"], r["bridge_node_id"]) == ("resolved", "2")
    assert r["answers_total"] == 5
    assert r["answers_resolved"] == 3  # Nausea, Rash, Fever
    assert r["answers_unresolved"] == 2  # Twin (ambiguous), Missing (not found)
    assert r["s_bridge_adjacent"] is True
    assert r["reach_via_stored_bridge"] == 1  # Nausea (also via B, counted once, as bridge)
    assert r["reach_only_via_other_bridge"] == 1  # Rash
    assert r["reach_via_neither"] == 1  # Fever: DrugC is not a neighbour of s
    assert r["other_type_b_neighbours_of_s"] == 1
    assert r["structural_status"] == "computed"


def test_answer_names_are_a_set():
    r = fr.analyse_row(row(answer=("Nausea", "Nausea")), TYPES, find, nbrs)
    assert r["answers_total"] == 1 and r["reach_via_stored_bridge"] == 1


def test_non_adjacent_bridge_is_structural_not_unresolved():
    r = fr.analyse_row(row(hop1="DrugC", answer=("Fever", "Nausea")), TYPES, find, nbrs)
    assert r["bridge_status"] == "resolved"
    assert r["s_bridge_adjacent"] is False
    assert r["reach_via_stored_bridge"] == 1  # Fever via C
    assert r["reach_only_via_other_bridge"] == 1  # Nausea via A or B
    assert r["other_type_b_neighbours_of_s"] == 2  # A and B; C is not a neighbour


@pytest.mark.parametrize("hop2,hop1,status,which", [
    ("Nobody", "DrugA", "not_computed_query_unresolved", "query_status"),
    ("Diabetes", "NoDrug", "not_computed_bridge_unresolved", "bridge_status"),
])
def test_unresolved_kept_separate(hop2, hop1, status, which):
    r = fr.analyse_row(row(hop2=hop2, hop1=hop1), TYPES, find, nbrs)
    assert r[which] == "not_found"
    assert r["structural_status"] == status
    assert r["s_bridge_adjacent"] is None and r["reach_via_neither"] is None
    assert r["answers_resolved"] == 3  # answer resolution still reported


def test_ambiguous_status():
    r = fr.analyse_row(row(hop1="Twin"), ("disease", "effect/phenotype", "effect/phenotype"), find, nbrs)
    assert r["bridge_status"] == "ambiguous"


def test_type_filter_used_for_resolution():
    # "DrugA" exists only as a drug; resolving it as a disease must fail
    r = fr.analyse_row(row(hop2="DrugA"), TYPES, find, nbrs)
    assert r["query_status"] == "not_found"


def test_s_excluded_from_targets():
    types = ("disease", "drug", "disease")  # target type = s's type; s reachable from DrugA
    r = fr.analyse_row(row(answer=("Diabetes",)), types, find, nbrs)
    assert r["answers_resolving_to_s"] == 1
    assert r["reach_via_stored_bridge"] == 0 and r["reach_via_neither"] == 1


def test_preview_rows_skip_s5_sample_and_short_types():
    rows = [{"row_id": f"BH2_{i:05d}", "relation_hop2": "a:b:c"} for i in range(12)]
    rows += [{"row_id": f"BH2_{i:05d}", "relation_hop2": "x:y:z"} for i in range(100, 105)]
    rows += [{"row_id": f"BH2_{i:05d}", "relation_hop2": "p:q:r"} for i in range(200, 207)]
    out = fr.preview_rows(rows)
    key = lambda r: hashlib.sha256(("42" + r["row_id"]).encode()).hexdigest()  # noqa: E731
    abc = sorted((r for r in rows if r["relation_hop2"] == "a:b:c"), key=key)
    assert [r for _, r in out["a:b:c"]] == abc[5:10]
    assert [p for p, _ in out["a:b:c"]] == [6, 7, 8, 9, 10]
    assert out["x:y:z"] == []  # 5 rows: all are S5 sample
    assert [p for p, _ in out["p:q:r"]] == [6, 7]  # 7 rows: positions 6-7 only
    s5 = {r["row_id"] for r in abc[:5]}
    assert not s5 & {r["row_id"] for _, r in out["a:b:c"]}
