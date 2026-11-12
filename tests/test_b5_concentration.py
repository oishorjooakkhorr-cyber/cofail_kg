"""Tests for scripts/42_b5_concentration.py (Phase J B5) on tiny synthetic fixtures."""
import copy
import importlib.util
import json
from fractions import Fraction
from pathlib import Path

import pytest

ROOT = Path(__file__).resolve().parents[1]
spec = importlib.util.spec_from_file_location("b5", ROOT / "scripts/42_b5_concentration.py")
M = importlib.util.module_from_spec(spec)
spec.loader.exec_module(M)

LABELS = {  # relation type -> (R1, R2)
    "effect/phenotype:disease:drug": (["disease_phenotype_positive"], ["indication"]),
    "gene/protein:drug:disease": (["drug_protein"], ["indication"]),
    "drug:disease:effect/phenotype": (["indication"], ["drug_effect"]),
    "drug:gene/protein:disease": (["drug_protein"], ["disease_protein"]),
}


def q(qid, rel, cf3=0, cf4=0, h1=0):
    r1, r2 = LABELS[rel]
    return {"query_id": qid, "relation_type": rel, "R1": r1, "R2": r2,
            "question": {"cf3": cf3, "cf4": cf4}, "hop1_clean": {"cf3": h1, "cf4": 0}}


TF, TS, OT = "effect/phenotype:disease:drug", "drug:disease:effect/phenotype", "drug:gene/protein:disease"
QUERIES = [
    q("P1", TF, 1, 1, 1), q("P2", TS), q("P3", OT, 1, 0, 0),                      # pilot
    q("E1", TF, 1, 0, 1), q("E2", "gene/protein:drug:disease", 1, 0, 1), q("E3", TF),
    q("E4", TS, 1, 0, 0), q("E5", TS), q("E6", OT), q("E7", OT, 1, 1, 0),          # expansion
]
MANIFESTS = {"pilot": {x["query_id"]: x["relation_type"] for x in QUERIES[:3]},
             "expansion": {x["query_id"]: x["relation_type"] for x in QUERIES[3:]}}


def cof(overlap=()):
    return {"queries": copy.deepcopy(QUERIES), "source_name_overlap_queries": list(overlap)}


def row(rows, subset, group):
    return next(r for r in rows if r["subset"] == subset and r["group"] == group)


# ---------------------------------------------------------------------------------------- groups

def test_group_of_definitions():
    assert M.group_of(TF, *LABELS[TF]) == "treat-final"
    assert M.group_of(TS, *LABELS[TS]) == "treat-first"
    assert M.group_of(OT, *LABELS[OT]) == "other"
    assert len(M.TREAT_FINAL) == 3 and len(M.TREAT_FIRST) == 4


def test_group_of_stops_when_labels_disagree():
    with pytest.raises(ValueError, match="R1="):
        M.group_of(TF, ["indication"], ["drug_effect"])
    with pytest.raises(ValueError):
        M.group_of(OT, ["drug_protein"], ["indication"])


# ------------------------------------------------------------------------------------ manifests

def test_assign_subsets_ok():
    s = M.assign_subsets(cof()["queries"], MANIFESTS)
    assert s["P1"] == "pilot" and s["E7"] == "expansion"


def test_assign_subsets_rejects_overlap_missing_and_type_mismatch():
    both = {"pilot": dict(MANIFESTS["pilot"]), "expansion": {**MANIFESTS["expansion"], "P1": TF}}
    with pytest.raises(ValueError, match="both"):
        M.assign_subsets(cof()["queries"], both)
    short = {"pilot": dict(MANIFESTS["pilot"]), "expansion": {k: v for k, v in MANIFESTS["expansion"].items()
                                                              if k != "E7"}}
    with pytest.raises(ValueError, match="differ"):
        M.assign_subsets(cof()["queries"], short)
    wrong = {"pilot": {**MANIFESTS["pilot"], "P2": OT}, "expansion": dict(MANIFESTS["expansion"])}
    with pytest.raises(ValueError, match="relation type"):
        M.assign_subsets(cof()["queries"], wrong)


def test_read_manifest_rejects_duplicates(tmp_path):
    p = tmp_path / "m.jsonl"
    p.write_text('{"query_id":"A","relation_type":"x"}\n\n{"query_id":"A","relation_type":"x"}\n')
    with pytest.raises(ValueError, match="duplicate"):
        M.read_manifest(p)
    p.write_text('{"query_id":"A","relation_type":"x"}\n{"query_id":"B","relation_type":"y"}\n')
    assert M.read_manifest(p) == {"A": "x", "B": "y"}


# --------------------------------------------------------------------------------------- table

def test_table_counts_by_subset_and_group():
    res = M.compute(cof(), MANIFESTS)
    rows = res["tables"]["all_queries"]
    assert len(rows) == 3 * 4
    r = row(rows, "pilot", "treat-final")
    assert (r["queries"], r["CF3^Q"], r["CF4^Q"], r["CF3^{Q,H1}"]) == (1, 1, 1, 1)
    r = row(rows, "expansion", "treat-final")
    assert (r["queries"], r["CF3^Q"], r["CF4^Q"], r["CF3^{Q,H1}"]) == (3, 2, 0, 2)
    assert r["CF3^{Q,H1} query IDs"] == ["E1", "E2"]
    r = row(rows, "expansion", "other")
    assert (r["queries"], r["CF3^Q"], r["CF4^Q"], r["CF3^{Q,H1}"]) == (2, 1, 1, 0)
    r = row(rows, "both", "total")
    assert (r["queries"], r["CF3^Q"], r["CF4^Q"], r["CF3^{Q,H1}"]) == (10, 6, 2, 3)
    for subset in M.SUBSETS:  # groups sum to total
        tot = row(rows, subset, "total")
        for k in ("queries", "CF3^Q", "CF4^Q", "CF3^{Q,H1}"):
            assert sum(row(rows, subset, g)[k] for g in M.GROUPS) == tot[k]
    for g in M.GROUPS + ("total",):  # pilot + expansion = both
        for k in ("queries", "CF3^Q", "CF4^Q", "CF3^{Q,H1}"):
            assert row(rows, "pilot", g)[k] + row(rows, "expansion", g)[k] == row(rows, "both", g)[k]


def test_source_name_overlap_view_excludes_queries():
    res = M.compute(cof(overlap=["E1"]), MANIFESTS)
    assert row(res["tables"]["all_queries"], "expansion", "treat-final")["queries"] == 3
    r = row(res["tables"]["without_source_name_overlap"], "expansion", "treat-final")
    assert (r["queries"], r["CF3^{Q,H1}"]) == (2, 1)
    h = res["hypergeometric"]["without_source_name_overlap"]
    assert (h["population_N_expansion_queries"], h["successes_K_expansion_treat_final_queries"],
            h["draws_n_expansion_CF3_Q_H1_queries"]) == (6, 2, 1)


def test_unknown_overlap_query_stops():
    with pytest.raises(ValueError, match="SOURCE_NAME_OVERLAP"):
        M.compute(cof(overlap=["ZZ"]), MANIFESTS)


# ------------------------------------------------------------------------------ hypergeometric

def test_hypergeometric_exact_values():
    assert M.hypergeometric_all_in(7, 3, 2) == Fraction(3, 21)          # C(3,2)/C(7,2)
    assert M.hypergeometric_all_in(10, 4, 0) == 1
    assert M.hypergeometric_all_in(10, 2, 3) == 0                        # more draws than successes
    # value quoted in chat before the plan entry (≈ 0.003): C(59,3)/C(400,3)
    p = M.hypergeometric_all_in(400, 59, 3)
    assert p == Fraction(59 * 58 * 57, 400 * 399 * 398)
    assert abs(float(p) - 0.0030707) < 1e-6
    with pytest.raises(ValueError):
        M.hypergeometric_all_in(5, 6, 1)


def test_hypergeometric_sums_to_one():
    N, K, n = 12, 5, 4
    total = sum(Fraction(M.math.comb(K, k) * M.math.comb(N - K, n - k), M.math.comb(N, n)) for k in range(n + 1))
    assert total == 1 and M.hypergeometric_all_in(N, K, n) == Fraction(M.math.comb(K, n), M.math.comb(N, n))


def test_expansion_probability_on_fixture():
    h = M.compute(cof(), MANIFESTS)["hypergeometric"]["all_queries"]
    assert (h["population_N_expansion_queries"], h["successes_K_expansion_treat_final_queries"],
            h["draws_n_expansion_CF3_Q_H1_queries"]) == (7, 3, 2)
    assert h["observed_in_treat_final"] == 2 and h["all_in_treat_final"] is True
    p = h["probability_all_in_treat_final"]
    assert (p["numerator"], p["denominator"], p["fraction_reduced"]) == (3, 21, "1/7")


def test_not_all_in_treat_final_is_reported():
    queries = cof()
    queries["queries"][6]["hop1_clean"]["cf3"] = 1  # E4, treat-first
    h = M.compute(queries, MANIFESTS)["hypergeometric"]["all_queries"]
    assert h["draws_n_expansion_CF3_Q_H1_queries"] == 3
    assert h["observed_in_treat_final"] == 2 and h["all_in_treat_final"] is False
    assert h["probability_all_in_treat_final"]["fraction_reduced"] == "1/35"  # C(3,3)/C(7,3)


# --------------------------------------------------------------------------------------- output

def test_outputs_and_write_once(tmp_path):
    res = M.compute(cof(), MANIFESTS)
    csv_text = M.to_csv(res)
    lines = csv_text.strip().split("\n")
    assert lines[0].startswith("view,subset,group,queries")
    assert len(lines) == 1 + 2 * 12
    assert "expansion,treat-final,3,2,0,2,E1;E2" in csv_text
    prov = {"git_commit": "abc", "git_tracked_clean": True,
            "inputs": {"cofailure": {"path": "x/cofailure.json", "sha256": "0" * 64}}}
    md = M.to_markdown(res, prov)
    assert "EXPLORATORY" in md and "44a2fdd" in md and "1/7" in md
    p = tmp_path / "o" / "a.txt"
    M.write_once(p, "x")
    M.write_once(p, "x")  # identical re-run allowed
    with pytest.raises(FileExistsError):
        M.write_once(p, "y")
    assert json.loads(json.dumps(res, sort_keys=True)) == res  # JSON-serialisable
