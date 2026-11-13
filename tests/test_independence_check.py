"""Tests for scripts/44_independence_check.py (Phase J IC), on tiny synthetic rows."""
import importlib.util
from pathlib import Path

import pytest

ROOT = Path(__file__).resolve().parents[1]
spec = importlib.util.spec_from_file_location("ic", ROOT / "scripts/44_independence_check.py")
ic = importlib.util.module_from_spec(spec)
spec.loader.exec_module(ic)


def row(q, a, opp, taken, overlap=False):
    return {"query_id": q, "agent_id": a, "opportunity": opp, "taken": taken, "overlap": overlap}


def test_poisson_binomial_matches_hand_values():
    dist = ic.poisson_binomial([0.5, 0.5])
    assert dist == pytest.approx([0.25, 0.5, 0.25])
    dist = ic.poisson_binomial([0.2, 0.5, 1.0])
    assert sum(dist) == pytest.approx(1.0)
    assert dist[0] == pytest.approx(0.0)
    assert dist[3] == pytest.approx(0.1)


def test_percentile_smallest_t_reaching_level():
    dist = [0.01, 0.04, 0.9, 0.05]
    assert ic.percentile(dist, 0.025) == 1
    assert ic.percentile(dist, 0.975) == 3


def test_rates_and_counts():
    rows = [row("Q1", "A", True, True), row("Q1", "B", True, True), row("Q1", "C", True, True),
            row("Q2", "A", True, False), row("Q2", "B", True, False), row("Q2", "C", False, False)]
    r = ic.compute(rows, {"Q1": 1, "Q2": 0})
    assert r["agents"]["A"]["p"] == 0.5
    assert r["agents"]["C"]["p"] == 1.0
    assert r["T_obs"] == 1
    q1 = r["per_query"][0]
    assert q1["K_q"] == 3 and q1["A_q"] == ["A", "B", "C"] and q1["CF3_Q_H1"] == 1
    assert q1["P_K_ge_3"] == pytest.approx(0.5 * 0.5 * 1.0)
    assert r["S_obs"] == 3


def test_agent_outside_opportunity_is_not_in_A_q_and_taken_outside_ignored():
    rows = [row("Q1", "A", True, True), row("Q1", "B", False, True)]
    r = ic.compute(rows + [row("Q2", "B", True, False)], {})
    q1 = [q for q in r["per_query"] if q["query_id"] == "Q1"][0]
    assert q1["A_q"] == ["A"] and q1["K_q"] == 1


def test_outcome_more_clustered_when_takers_bunch():
    # Each agent takes on half its opportunities, but always together -> far more K_q >= 3 than independence.
    rows = []
    for i in range(60):
        t = i < 30
        rows += [row(f"Q{i:02d}", a, True, t) for a in ("A", "B", "C", "D")]
    r = ic.compute(rows, {})
    assert r["T_obs"] == 30
    assert r["E_T"] == pytest.approx(60 * (4 * 0.5 ** 4 + 0.5 ** 4))
    assert r["P_T_ge_obs"] < 0.025
    assert r["outcome"] == "MORE CLUSTERED"


def test_outcome_less_clustered_when_takers_never_bunch():
    # Each agent takes on half its opportunities, but never 3 together -> fewer K_q >= 3 than independence.
    rows = []
    for i, p in enumerate(["AB", "CD", "AC", "BD", "AD", "BC"] * 3):
        rows += [row(f"Q{i:02d}", a, True, a in p) for a in ("A", "B", "C", "D")]
    r = ic.compute(rows, {})
    assert r["T_obs"] == 0
    assert r["P_T_le_obs"] == pytest.approx((11 / 16) ** 18)
    assert r["outcome"] == "LESS CLUSTERED"


def test_outcome_agrees_when_every_pattern_appears_once():
    # All 16 take/not-take patterns of 4 agents once: p_i = 0.5, T_obs = 5 = E[T].
    rows = []
    for i in range(16):
        rows += [row(f"Q{i:02d}", a, True, bool(i >> k & 1)) for k, a in enumerate("ABCD")]
    r = ic.compute(rows, {})
    assert r["T_obs"] == 5
    assert r["E_T"] == pytest.approx(5.0)
    assert r["outcome"] == "AGREES"


def test_no_opportunity_agent_raises():
    with pytest.raises(ValueError, match="no opportunity"):
        ic.compute([row("Q1", "A", False, False)], {})


def test_as_bool_rejects_other_values():
    with pytest.raises(ValueError):
        ic.as_bool("yes", "taken", {"query_id": "Q", "agent_id": "A"})
