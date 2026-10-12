import importlib.util
from pathlib import Path

_PATH = Path(__file__).resolve().parents[1] / "scripts/explore_suffix_preview.py"
_spec = importlib.util.spec_from_file_location("suffix_preview", _PATH)
sp = importlib.util.module_from_spec(_spec)
_spec.loader.exec_module(sp)

# (type, normalized name) -> ids
NODES = {
    ("disease", "insomnia (disease)"): ["1"],
    ("disease", "flu"): ["2"],
    ("disease", "twin (disease)"): ["3", "4"],  # suffix form ambiguous
    ("drug", "aspirin"): ["5"],
    ("effect/phenotype", "acne (disease)"): ["6"],  # suffix on a non-disease type
}


def find(name, node_type):
    return NODES.get((node_type, " ".join(name.lower().split())), [])


def rows():
    return [
        {"relation_hop2": "drug:effect/phenotype:disease", "hop2": "Aspirin", "hop1": "acne",
         "answer": ["insomnia", "flu", "twin", "nothing", "insomnia"]},
        {"relation_hop2": "drug:effect/phenotype:disease", "hop2": "Unknown", "hop1": "x",
         "answer": ["insomnia"]},
    ]


def by(agg, field):
    return next(a for a in agg if a["field"] == field)


def test_answer_counts():
    agg, detail = sp.preview(rows(), find)
    a = by(agg, "answer")
    assert a["names_checked"] == 5  # row 1: 4 distinct names; row 2: 1
    assert a["unresolved_names"] == 4  # insomnia x2, twin, nothing
    assert a["rows_with_unresolved"] == 2
    assert a["distinct_unresolved_names"] == 3
    assert a["would_resolve_with_suffix"] == 2  # insomnia twice
    assert a["still_unresolved_with_suffix"] == 2  # twin (ambiguous with suffix), nothing
    assert a["rows_fully_resolved_with_suffix"] == 1  # row 2 only
    ins = next(d for d in detail if d["name"] == "insomnia")
    assert (ins["status"], ins["with_suffix"], ins["rows"]) == ("not_found", "resolved", 2)
    twin = next(d for d in detail if d["name"] == "twin")
    assert twin["with_suffix"] == "ambiguous"


def test_entity_fields_use_their_own_type():
    agg, _ = sp.preview(rows(), find)
    h2, h1 = by(agg, "hop2"), by(agg, "hop1")
    assert h2["node_type"] == "drug" and h2["unresolved_names"] == 1  # "Unknown"
    assert h2["would_resolve_with_suffix"] == 0
    assert h1["node_type"] == "effect/phenotype" and h1["unresolved_names"] == 2
    assert h1["would_resolve_with_suffix"] == 1  # "acne" -> "acne (disease)" of type effect/phenotype


def test_ambiguous_counted_separately():
    NODES[("disease", "dup")] = ["7", "8"]
    try:
        r = [{"relation_hop2": "drug:effect/phenotype:disease", "hop2": "Aspirin", "hop1": "acne",
              "answer": ["dup"]}]
        a = by(sp.preview(r, find)[0], "answer")
        assert (a["unresolved_ambiguous"], a["unresolved_not_found"]) == (1, 0)
    finally:
        del NODES[("disease", "dup")]


def test_summary_has_label():
    agg, _ = sp.preview(rows(), find)
    assert "Exploratory, viewed before the §12 suffix decision" in sp.summary(agg)
