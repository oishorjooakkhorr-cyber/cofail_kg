"""Tests for scripts/45_rp_report.py (Phase J RP report) on tiny synthetic analysis rows."""
import importlib.util
from pathlib import Path

import pytest

ROOT = Path(__file__).resolve().parents[1]
spec = importlib.util.spec_from_file_location("rp", ROOT / "scripts/45_rp_report.py")
M = importlib.util.module_from_spec(spec)
spec.loader.exec_module(M)

AGENTS = ["A1", "A2", "A3", "A4"]


def row(answers, status="SUCCESS"):
    return {"episode_status": status, "answers": [{"node_id": n, "label_a": la} for n, la in answers]}


def cof(flags):
    """flags: query_id -> (cf3, cf4, cf3_h1, shared ids)."""
    return {"agent_order": AGENTS, "queries": [
        {"query_id": q, "relation_type": "t", "question": {"cf3": c3, "cf4": c4,
                                                         "shared_entities": [{"entity_id": e} for e in sh]},
         "hop1_clean": {"cf3": h1}} for q, (c3, c4, h1, sh) in flags.items()]}


def test_answer_sets_and_jaccard():
    ids, off = M.answer_sets(row([("1", "GOLD"), ("2", "OFF_QUESTION"), (None, "UNRESOLVED")]))
    assert ids == {"1", "2"} and off == {"2"}
    assert M.jaccard({"1", "2"}, {"2", "3"}) == {"intersection": 1, "union": 3, "value": pytest.approx(1 / 3)}
    assert M.jaccard(set(), set())["value"] is None


def test_compare_counts_reproduction_and_views():
    original = cof({"Q1": (1, 1, 1, ["9"]), "Q2": (1, 0, 0, ["8"]), "Q3": (1, 0, 1, ["7"])})
    repeat = cof({"Q1": (1, 0, 1, ["9"]), "Q2": (0, 0, 0, []), "Q3": (1, 1, 1, ["7"])})
    rows_o = {(a, q): row([("9", "OFF_QUESTION"), ("1", "GOLD")]) for a in AGENTS for q in ("Q1", "Q2", "Q3")}
    rows_r = {(a, q): row([("9", "OFF_QUESTION")]) for a in AGENTS for q in ("Q1", "Q2", "Q3")}
    rows_r[("A4", "Q2")] = row([], status="TIMEOUT")
    out = M.compare(original, repeat, rows_o, rows_r, AGENTS, overlap={"Q3"})
    assert [q["reproduces_cf3_q"] for q in out["queries"]] == [True, False, True]
    assert out["counts"]["all_queries"]["reproduced"] == 2 and not out["counts"]["all_queries"]["expectation_met"]
    assert out["counts"]["without_source_name_overlap"] == {"queries": 2, "original_cf3_q": 2, "reproduced": 1,
                                                            "repeat_cf3_q": 1, "repeat_cf4_q": 0, "repeat_cf3_q_h1": 1}
    p = next(p for p in out["pairs"] if (p["query_id"], p["agent_id"]) == ("Q1", "A1"))
    assert p["jaccard_answers"]["value"] == pytest.approx(0.5) and p["jaccard_off_question"]["value"] == 1.0
    t = next(p for p in out["pairs"] if (p["query_id"], p["agent_id"]) == ("Q2", "A4"))
    assert t["repeat_status"] == "TIMEOUT" and t["jaccard_answers"]["value"] == 0.0


def test_compare_rejects_unknown_query_or_agent_order():
    with pytest.raises(ValueError, match="not in the original"):
        M.compare(cof({"Q1": (1, 0, 0, [])}), cof({"Q9": (1, 0, 0, [])}), {}, {}, AGENTS, set())
    bad = cof({"Q1": (1, 0, 0, [])})
    bad["agent_order"] = AGENTS[::-1]
    with pytest.raises(ValueError, match="agent orders"):
        M.compare(cof({"Q1": (1, 0, 0, [])}), bad, {}, {}, AGENTS, set())
