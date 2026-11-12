"""Tests for scripts/43_b6_benchmark.py (Phase J B6) on tiny synthetic fixtures."""
import copy
import csv
import hashlib
import importlib.util
import io
from pathlib import Path

import pytest

ROOT = Path(__file__).resolve().parents[1]
spec = importlib.util.spec_from_file_location("b6", ROOT / "scripts/43_b6_benchmark.py")
M = importlib.util.module_from_spec(spec)
spec.loader.exec_module(M)

# s=1 (phenotype) -dpp-> diseases 2,3 ; 4 is a disease linked to s by another label ; 9 is a gene linked by dpp
# diseases -ind-> drugs 10, 11 ; drug 12 reached only from 4
NODES = {"1": ("pheno", "effect/phenotype"), "2": ("dis A", "disease"), "3": ("dis B", "disease"),
         "4": ("dis C", "disease"), "9": ("gene X", "gene/protein"),
         "10": ("drug P", "drug"), "11": ("drug Q", "drug"), "12": ("drug R", "drug")}
EDGES = [("1", "dpp", "2"), ("1", "dpp", "3"), ("1", "other", "4"), ("1", "dpp", "9"),
         ("2", "ind", "10"), ("3", "ind", "10"), ("3", "ind", "11"), ("4", "ind", "12"), ("9", "ind", "11"),
         ("2", "off", "11")]


class FakeKG:
    def neighbors(self, node, label=None, neighbor_type=None):
        out = set()
        for x, l, y in EDGES:
            if label is not None and l != label:
                continue
            if x == str(node):
                out.add(y)
            elif y == str(node):
                out.add(x)
        return [{"id": n} for n in sorted(out, key=int) if neighbor_type is None or NODES[n][1] == neighbor_type]

    def get_node(self, node):
        return {"id": str(node), "name": NODES[str(node)][0], "type": NODES[str(node)][1]}


def ent(eid, n=3):
    agents = ["A", "B", "C", "D"][:n]
    return {"entity_id": eid, "agent_count": n, "agents": agents}


def q(qid, rel="effect/phenotype:disease:drug", bh=0, qv=0, shared=()):
    return {"query_id": qid, "relation_type": rel, "s": "1", "R1": ["dpp"], "R2": ["ind"],
            "benchmark": {"cf3": bh, "cf4": 0, "shared_entities": list(shared)},
            "question": {"cf3": qv, "cf4": 0, "shared_entities": []}}


REF = {"s": "1", "Type_B": "disease", "T_q": ["10", "11"], "gold_bridges": ["2"],
       "question_texts": ["Name all drugs that can treat a disease that has phenotype pheno."] * 2,
       "gold_answer_names": ["drug P"]}
TARGETS = {"2": ["10"], "3": ["10", "11"]}


# --------------------------------------------------------------------------------------------- table

def test_tabulate_two_by_two_and_views():
    qs = [q("a", bh=1, qv=0), q("b", bh=1, qv=1), q("c", bh=0, qv=1), q("d"),
          q("e", rel="drug:disease:gene/protein", bh=1)]
    rows = M.tabulate(qs, set())
    r = next(x for x in rows if x["relation_type"] == "effect/phenotype:disease:drug")
    assert (r["queries"], r["CF3^BH"], r["CF3^Q"], r["both"], r["BH-only"], r["Q-only"]) == (4, 2, 2, 1, 1, 1)
    tot = rows[-1]
    assert tot["relation_type"] == "total" and (tot["queries"], tot["BH-only"]) == (5, 2)
    assert [x["relation_type"] for x in rows[:-1]] == sorted(x["relation_type"] for x in rows[:-1])
    for k in ("queries", "CF3^BH", "CF3^Q", "both", "BH-only", "Q-only"):
        assert sum(x[k] for x in rows[:-1]) == tot[k]
    without = M.tabulate(qs, {"a"})
    assert without[-1]["queries"] == 4 and without[-1]["BH-only"] == 1


# ------------------------------------------------------------------------------------------ selection

def test_order_key_is_sha256_of_42_plus_id():
    assert M.order_key("BH2_00001") == hashlib.sha256(b"42BH2_00001").hexdigest()


def test_select_handcheck_takes_first_n_bh_only_by_hash():
    qs = [q(f"Q{i:02d}", bh=1, qv=(i % 5 == 0)) for i in range(40)]
    picked = M.select_handcheck(qs, 15)
    pool = [x for x in qs if x["benchmark"]["cf3"] and not x["question"]["cf3"]]
    expected = sorted(pool, key=lambda x: hashlib.sha256(("42" + x["query_id"]).encode()).hexdigest())[:15]
    assert [x["query_id"] for x in picked] == [x["query_id"] for x in expected]
    assert all(not x["question"]["cf3"] for x in picked)
    assert len(M.select_handcheck(qs[:6], 15)) == sum(1 for x in qs[:6] if not x["question"]["cf3"])


def test_chosen_entity_smallest_numeric_id():
    qq = q("a", bh=1, shared=[ent("100"), ent("11", 4), ent("9")])
    assert M.chosen_entity(qq)["entity_id"] == "9"          # numeric, not string order
    with pytest.raises(ValueError, match="no benchmark shared entity"):
        M.chosen_entity(q("b", bh=1, shared=[ent("5", 2)]))


# ------------------------------------------------------------------------------------------- paths

def test_graph_paths_all_bridges_typed_and_sorted():
    kg = FakeKG()
    assert M.graph_paths(kg, "1", "10", ["dpp"], ["ind"], "disease") == [("dpp", "2", "ind"), ("dpp", "3", "ind")]
    # 9 is a gene (wrong Type_B) and 4 is reached by a non-R1 label: neither is a bridge
    assert M.graph_paths(kg, "1", "11", ["dpp"], ["ind"], "disease") == [("dpp", "3", "ind")]
    assert M.graph_paths(kg, "1", "12", ["dpp"], ["ind"], "disease") == []
    # R2 with two labels: off-label edge 2-11 adds a path only when "off" is accepted
    assert M.graph_paths(kg, "1", "11", ["dpp"], ["ind", "off"], "disease") == [("dpp", "2", "off"),
                                                                                 ("dpp", "3", "ind")]


def test_handcheck_row_contents():
    qq = q("a", bh=1, shared=[ent("11"), ent("10", 4)])
    row = M.handcheck_row(qq, REF, TARGETS, FakeKG(), set())
    assert row["entity_id"] == "10" and row["entity_name"] == "drug P" and row["holders"] == 4
    assert row["n_graph_paths"] == 2 and row["entity_in_T_q"] is True
    assert row["graph_paths"] == ("pheno [1] -dpp-> dis A [2] (gold bridge) -ind-> drug P [10] | "
                                  "pheno [1] -dpp-> dis B [3] -ind-> drug P [10]")
    assert row["biohopr_gold_list"] == "drug P" and row["mark"] == ""
    assert row["question_text"].startswith("Name all drugs")


def test_handcheck_row_no_path_and_overlap_flag():
    qq = q("a", bh=1, shared=[ent("12")])
    ref = {**REF, "T_q": ["10", "11"]}
    row = M.handcheck_row(qq, ref, TARGETS, FakeKG(), {"a"})
    assert row["graph_paths"] == "NO_PATH" and row["n_graph_paths"] == 0
    assert row["entity_in_T_q"] is False and row["source_name_overlap"] is True


def test_handcheck_row_stops_on_reference_mismatch():
    qq = q("a", bh=1, shared=[ent("10")])
    with pytest.raises(ValueError, match="reference_targets"):
        M.handcheck_row(qq, REF, {"2": ["10"]}, FakeKG(), set())     # graph finds bridges 2 and 3
    with pytest.raises(ValueError, match="question text"):
        M.handcheck_row(qq, {**REF, "question_texts": ["x", "y"]}, TARGETS, FakeKG(), set())
    with pytest.raises(ValueError, match="s ="):
        M.handcheck_row({**qq, "s": "2"}, REF, TARGETS, FakeKG(), set())


def test_build_handcheck_orders_rows():
    qs = [q(f"Q{i}", bh=1, shared=[ent("10")]) for i in range(5)]
    rows = M.build_handcheck(qs, {x["query_id"]: REF for x in qs}, {x["query_id"]: TARGETS for x in qs},
                             FakeKG(), set())
    assert [r["order"] for r in rows] == [1, 2, 3, 4, 5]
    assert [r["query_id"] for r in rows] == [x["query_id"] for x in M.select_handcheck(qs)]


# ------------------------------------------------------------------------------------------ output

def test_csv_and_markdown_and_write_once(tmp_path):
    qq = q("a", bh=1, shared=[ent("10")])
    hc = M.build_handcheck([qq], {"a": REF}, {"a": TARGETS}, FakeKG(), set())
    text = M.csv_text(M.HANDCHECK_FIELDS, hc)
    rows = list(csv.DictReader(io.StringIO(text)))
    assert rows[0]["mark"] == "" and list(rows[0])[-1] == "mark" and rows[0]["query_id"] == "a"
    tables = {v: M.tabulate([qq], set()) for v in M.VIEWS}
    prov = {"git_commit": "abc", "git_tracked_clean": True, "handcheck_path": "x.csv",
            "inputs": {"cofailure": {"path": "c.json", "sha256": "0" * 64}}}
    md = M.to_markdown(tables, hc, [], prov, 1)
    assert "EXPLORATORY" in md and "dis A [2] (gold bridge)" in md and "VALID / QUESTIONABLE / NOT_VALID" in md
    p = tmp_path / "d" / "f.csv"
    M.write_once(p, text)
    M.write_once(p, text)
    with pytest.raises(FileExistsError):
        M.write_once(p, text + "marked")


def test_fixture_not_mutated():
    before = copy.deepcopy(REF)
    M.handcheck_row(q("a", bh=1, shared=[ent("10")]), REF, TARGETS, FakeKG(), set())
    assert REF == before
