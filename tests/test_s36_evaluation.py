"""Tests for scripts/48_s36_evaluation.py (S36, DESCRIPTIVE) on tiny synthetic metrics rows."""
import importlib.util
from pathlib import Path

import pytest

ROOT = Path(__file__).resolve().parents[1]
spec = importlib.util.spec_from_file_location("s36", ROOT / "scripts/48_s36_evaluation.py")
M = importlib.util.module_from_spec(spec)
spec.loader.exec_module(M)

OFF = "off-label use"
AGENTS = ["A1", "A2", "A3", "A4"]


def e(u, label, v):
    return {"u": u, "label": label, "v": v}


def ans(node, label_a, path=None):
    return {"node_id": node, "label_a": label_a, "primary_path": path}


def row(answers, status="SUCCESS"):
    return {"episode_status": status, "answers": answers if status == "SUCCESS" else []}


# s=1, hop-1 node u=10 (blocked: off-label use at step 2), other hop-1 node 11
SAME = ans("30", "OFF_QUESTION", [e("1", "dpp", "11"), e("11", OFF, "30")])
AT_U = ans("31", "OFF_QUESTION", [e("1", "dpp", "10"), e("10", OFF, "31")])
OTHER = ans("32", "OFF_QUESTION", [e("1", "dpp", "11"), e("11", "contraindication", "32")])
VALID = ans("40", "GOLD", [e("1", "dpp", "10"), e("10", "indication", "40")])


def test_answer_categories():
    assert M.answer_category(SAME, "10", OFF, 2) == "SAME_WRONG_RELATION_OTHER_NEIGHBOR"
    assert M.answer_category(AT_U, "10", OFF, 2) == "OTHER_WRONG"          # same node u, not "other neighbour"
    assert M.answer_category(OTHER, "10", OFF, 2) == "OTHER_WRONG"
    assert M.answer_category(VALID, "10", OFF, 2) == "VALID_RELATION"
    assert M.answer_category(ans("50", "OFF_QUESTION", None), "10", OFF, 2) == "OTHER_WRONG"   # ungrounded
    # SHORTCUT (step 1 at s): a step-1 edge always starts at s = u, so the category cannot occur
    short = ans("60", "OFF_QUESTION", [e("1", "drug_protein", "60")])
    assert M.answer_category(short, "1", "drug_protein", 1) == "OTHER_WRONG"


def test_holder_outcome_precedence_and_failures():
    assert M.holder_outcome(row([VALID, OTHER, SAME]), "10", OFF, 2)["category"] == \
        "SAME_WRONG_RELATION_OTHER_NEIGHBOR"
    o = M.holder_outcome(row([VALID, OTHER]), "10", OFF, 2)
    assert o["category"] == "OTHER_WRONG" and o["recovered"] is False
    assert o["answer_counts"] == {"VALID_RELATION": 1, "SAME_WRONG_RELATION_OTHER_NEIGHBOR": 0, "OTHER_WRONG": 1}
    v = M.holder_outcome(row([VALID, ans(None, "UNRESOLVED")]), "10", OFF, 2)
    assert v["category"] == "VALID_RELATION" and v["recovered"] is True
    n = M.holder_outcome(row([ans(None, "UNRESOLVED")]), "10", OFF, 2)
    assert n["category"] == "NO_ANSWER" and n["recovered"] is False
    f = M.holder_outcome(row([], status="PARSE_FAIL"), "10", OFF, 2)
    assert f == {"status": "PARSE_FAIL", "category": None, "recovered": None, "answer_counts": None, "resolved": None}


def test_column_excludes_technical_failures_from_denominators():
    rows = {("A1", "Q"): row([VALID]), ("A2", "Q"): row([SAME]), ("A3", "Q"): row([], status="PARSE_FAIL"),
            ("A4", "Q"): row([])}
    col = M.column(rows, "Q", ["A1", "A2", "A3", "A4"], "10", OFF, 2)
    assert (col["recovered"], col["denominator"]) == (1, 3)
    assert col["technical_failures"] == {"A3": "PARSE_FAIL"}
    assert col["displacement"] == {"VALID_RELATION": 1, "SAME_WRONG_RELATION_OTHER_NEIGHBOR": 1,
                                   "OTHER_WRONG": 0, "NO_ANSWER": 1}


def test_no_answer_rate_uses_success_episodes_only():
    rows = {("A1", "Q"): row([VALID]), ("A2", "Q"): row([]), ("A3", "Q"): row([], status="TIMEOUT"),
            ("A4", "Q"): row([ans(None, "UNRESOLVED")])}
    assert M.no_answer(rows, "Q", AGENTS) == {"no_answer": 2, "success_episodes": 3, "rate": pytest.approx(2 / 3)}


def cof(qid, cf3, h1):
    blk = lambda c: {"cf3": c, "cf4": 0}  # noqa: E731
    return {"queries": [{"query_id": qid, "question": blk(cf3), "grounded": blk(cf3), "hop1_clean": blk(h1),
                         "pcf_rel3": cf3, "pcf_rel4": 0, "pcf_node3": 0, "pcf_node4": 0, "pcf_shortcut3": 0}]}


def test_evaluate_one_case():
    case = {"query_id": "Q", "mechanism": "WRONG_TURN_HOP2", "u": "10", "r": OFF, "step": 2,
            "holders": ["A1", "A2", "A3"]}
    before = {(a, "Q"): row([VALID, AT_U]) for a in AGENTS}
    after = {("A1", "Q"): row([VALID]), ("A2", "Q"): row([VALID, SAME]), ("A3", "Q"): row([], "PARSE_FAIL"),
             ("A4", "Q"): row([VALID])}
    out = M.evaluate([case], cof("Q", 1, 1), cof("Q", 0, 0),
                     {"before": before, "after": after, "reference": before}, AGENTS)[0]
    assert out["cf"]["CF3^Q"] == {"before": 1, "after": 0} and out["pcf"]["pcf_rel3"] == {"before": 1, "after": 0}
    assert (out["after"]["recovered"], out["after"]["denominator"]) == (1, 2)
    assert out["reference_repeat"]["displacement"]["OTHER_WRONG"] == 3      # before: answers at u itself
    assert out["no_answer"]["after"]["success_episodes"] == 3
    assert out["before_holder_answers"]["A1"]["OTHER_WRONG"] == 1


def test_evaluate_refuses_a_holder_without_an_original_success():
    case = {"query_id": "Q", "mechanism": "WRONG_TURN_HOP2", "u": "10", "r": OFF, "step": 2, "holders": ["A1"]}
    before = {(a, "Q"): row([], "TIMEOUT") for a in AGENTS}
    with pytest.raises(ValueError, match="holder"):
        M.evaluate([case], cof("Q", 1, 1), cof("Q", 0, 0), {"before": before, "after": before,
                                                             "reference": before}, AGENTS)
