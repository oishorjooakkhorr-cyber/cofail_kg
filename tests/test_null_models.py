"""S24 chance baselines (protocol §17) on tiny synthetic episodes."""

import hashlib
import random

import numpy as np
import pytest

from cofail_kg.evaluation.null_models import (TRIALS, agent_pools, aggregate, generator, query_hash,
                                              query_nulls, run_nulls, simulate)

AGENTS = ["A1", "A2", "A3", "A4"]
Q = "BH2_00001"
# s=1 (drug); bridges of Type_B "gene/protein"; targets of Type_T "disease". T_q = {3}.
REF = {"query_id": Q, "relation_type": "drug:gene/protein:disease", "s": "1", "Type_B": "gene/protein",
       "Type_T": "disease", "T_q": ["3"]}
MAP = {"R1": ["r1"], "R2": ["r2"]}
TYPES = {"1": "drug", "2": "gene/protein", "5": "gene/protein", "3": "disease"}


def node_type(x):
    return TYPES.get(x, "disease" if int(x) >= 100 else "drug")


def nb(u, relation, items, page=1):
    return {"tool": "get_neighbors", "success": True,
            "arguments": {"entity_id": u, "relation": relation, "page": page},
            "result": {"items": [{"id": i, "name": i, "type": node_type(i)} for i in items],
                       "page": page, "page_size": 50, "total_count": len(items), "has_more": False}}


def record(agent, calls, query=Q):
    return {"query_id": query, "agent_id": agent, "call_log": calls}


def answer(x, h1, label_a="OFF_QUESTION"):
    return {"node_id": x, "label_a": label_a, "label_b": "PATH_INVALID", "h1": h1}


def row(agent, answers, status="SUCCESS", query=Q):
    return {"query_id": query, "agent_id": agent, "episode_status": status, "answers": answers}


def clean_calls(targets, page=1):
    """s -r1-> 2 -r2-> targets: every target has H1 = 1."""
    return [nb("1", "r1", ["2"]), nb("2", "r2", targets, page=page)]


def entry(agent, calls, answers, ref=REF, status="SUCCESS"):
    rec, r = record(agent, calls, ref["query_id"]), row(agent, answers, status, ref["query_id"])
    return {"record": rec, "row": r, "pools": agent_pools(rec, r, ref, MAP, node_type)}


def test_seed_scheme_matches_protocol():
    h = int(hashlib.sha256(Q.encode()).hexdigest()[:8], 16)
    assert query_hash(Q) == h
    expected = np.random.Generator(np.random.PCG64(np.random.SeedSequence([42, h, 2]))).random(5)
    assert np.array_equal(generator(Q, "N1-H1").random(5), expected)


def test_required_same_single_wrong_answer_with_200_other_candidates_is_unlikely():
    """Protocol §17 required test: N1 probability of a shared answer < 0.01."""
    others = [str(200 + k) for k in range(200)]  # 200 other wrong Type_T candidates
    panel = [entry(a, clean_calls(["150"] + others), [answer("150", 1)]) for a in AGENTS]
    assert all(len(e["pools"]["N1"]["pool"]) == 201 for e in panel)
    out = query_nulls(REF, panel, AGENTS)["result"]["nulls"]["N1"]
    assert out["observed_cf3"] == 1 and out["observed_cf4"] == 1
    assert out["null_probability_cf3"] < 0.01
    assert out["null_probability_cf4"] < 0.01


def test_tiny_pools_single_shared_entity_gives_probability_one():
    panel = [entry(a, clean_calls(["150"]), [answer("150", 1)]) for a in AGENTS]
    nulls = query_nulls(REF, panel, AGENTS)["result"]["nulls"]
    for null in ("N1", "N1-H1", "N2"):
        assert nulls[null]["null_probability_cf3"] == 1.0
        assert nulls[null]["null_probability_cf4"] == 1.0


def test_pools_and_observed_sets_follow_the_table_and_are_subsets():
    calls = [nb("1", "r1", ["2"]),
             nb("2", "r2", ["150", "151", "3"], page=1),   # 3 is in T_q: never in the pool
             nb("2", "r2", ["152"], page=2),               # page 2 only: not in N2
             nb("1", "bad", ["160", "1"]),                 # 160 reached without R1: H1 = 0; s excluded
             nb("5", "r2", ["170"])]                       # 170: 5 is not reached from s; H1 = 0
    answers = [answer("150", 1), answer("152", 1), answer("160", 0), answer("170", 0),
               answer("999", 0),                           # never appeared: not in W'
               answer("3", 1, label_a="GOLD")]
    pools = agent_pools(record("A1", calls), row("A1", answers), REF, MAP, node_type)
    assert pools["N1"] == {"pool": ["150", "151", "152", "160", "170"],
                           "observed": ["150", "152", "160", "170"]}
    assert pools["N1-H1"] == {"pool": ["150", "151", "152"], "observed": ["150", "152"]}
    assert pools["N2"] == {"pool": ["150", "151", "160", "170"], "observed": ["150", "160", "170"]}
    for null in pools.values():
        assert set(null["observed"]) <= set(null["pool"])


def test_h1_disagreeing_with_s19_row_is_rejected():
    with pytest.raises(ValueError, match="H1"):
        agent_pools(record("A1", clean_calls(["150"])), row("A1", [answer("150", 0)]), REF, MAP, node_type)


def test_failed_episode_contributes_empty_observed_sets_and_is_reported():
    panel = [entry(a, clean_calls(["150"]), [answer("150", 1)]) for a in AGENTS[:3]]
    panel.append(entry("A4", clean_calls(["150"]), [], status="ERROR"))
    out = query_nulls(REF, panel, AGENTS)["result"]
    assert out["technical_failure_agents"] == ["A4"]
    assert out["nulls"]["N1"]["observed_cf3"] == 1 and out["nulls"]["N1"]["observed_cf4"] == 0
    assert out["nulls"]["N1"]["null_probability_cf3"] == 1.0
    assert out["nulls"]["N1"]["null_probability_cf4"] == 0.0


def test_draws_follow_ascending_agent_order_on_one_stream():
    pools = [{"pool": [str(100 + k) for k in range(20)], "observed": ["100", "101"]} for _ in AGENTS]
    sim = simulate(Q, "N1", pools, trials=50)
    rng = generator(Q, "N1")
    arr = np.arange(100, 120)
    for t in range(50):
        draws = [rng.choice(arr, size=2, replace=False).tolist() for _ in AGENTS]
        counts = {}
        for d in draws:
            for x in d:
                counts[x] = counts.get(x, 0) + 1
        assert sim[t, 0] == (max(counts.values()) >= 3)
        assert sim[t, 1] == (max(counts.values()) >= 4)


def _two_query_inputs():
    ref2 = dict(REF, query_id="BH2_00002")
    others = [str(100 + k) for k in range(30)]
    panels = {Q: [entry(a, clean_calls(["150"]), [answer("150", 1)]) for a in AGENTS],
              "BH2_00002": [entry(a, clean_calls(["150"] + others), [answer("150", 1)], ref=ref2)
                            for a in AGENTS]}
    return {Q: REF, "BH2_00002": ref2}, panels


def test_determinism_and_query_order_invariance():
    refs, panels = _two_query_inputs()
    first = run_nulls(refs, panels, AGENTS, trials=500)
    assert run_nulls(refs, panels, AGENTS, trials=500) == first
    keys = list(panels)
    random.Random(7).shuffle(keys)
    shuffled = {k: list(reversed(panels[k])) for k in reversed(keys)}
    assert run_nulls(refs, shuffled, AGENTS, trials=500) == first


def test_aggregate_hand_checkable_two_queries():
    """Q1: one-entity pools, always shared (indicator 1). Q2: 31-entity pools, observed shared."""
    refs, panels = _two_query_inputs()
    per_query = [query_nulls(refs[q], panels[q], AGENTS, trials=TRIALS) for q in sorted(panels)]
    agg = aggregate(per_query)["N1"]["cf3"]
    q2 = per_query[1]["indicators"]["N1"][:, 0]
    totals = 1 + q2.astype(int)                    # Q1 always contributes 1
    assert agg["observed_total"] == 2 and agg["query_count"] == 2
    assert agg["null_mean"] == pytest.approx(totals.mean())
    assert agg["null_median"] == 1.0
    assert agg["null_p95"] == float(np.percentile(totals, 95))
    assert agg["p"] == (1 + int((totals >= 2).sum())) / (1 + TRIALS)
    assert agg["observed_exceeds_null"] is (2 > agg["null_p95"])
    # Q2 share probability ~ 4*C(..) small: observed 2 lies above the 95th percentile (1).
    assert agg["null_p95"] == 1.0 and agg["observed_exceeds_null"] is True


def test_aggregate_excluding_technical_failures():
    refs, panels = _two_query_inputs()
    panels[Q][3] = entry("A4", clean_calls(["150"]), [], status="TIMEOUT")
    out = run_nulls(refs, panels, AGENTS, trials=200)
    assert out["aggregate"]["N1"]["cf3"]["query_count"] == 2
    assert out["aggregate_excluding_technical_failures"]["N1"]["cf3"]["query_count"] == 1


def test_panel_must_match_frozen_agents():
    refs, panels = _two_query_inputs()
    with pytest.raises(ValueError, match="agent"):
        query_nulls(REF, panels[Q][:3], AGENTS, trials=10)
