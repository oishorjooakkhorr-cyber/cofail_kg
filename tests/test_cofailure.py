"""S23 co-failure metrics (protocol §16) on tiny synthetic panels with hand-computed expectations."""

import copy
import random

import pandas as pd
import pytest

from cofail_kg.evaluation.agent_metrics import degree_statistics
from cofail_kg.evaluation.cofailure import pairwise_agreement, query_cofailure

AGENTS = ["A1", "A2", "A3", "A4"]
# s=1; valid bridges B_q={2,5}; question-valid T_q={3,10,11}; benchmark A*_q={3}.
REF = {"query_id": "BH2_00001", "relation_type": "drug:gene/protein:disease", "s": "1",
       "A_star_q": ["3"], "B_q": ["2", "5"], "T_q": ["3", "10", "11"]}
MAP = {"R1": ["r1"], "R2": ["r2"]}
DEGREES = {str(n): {"degree": n, "degree_percentile": float(n)} for n in range(1, 60)}


def edge(u, label, v, i=0):
    return {"creation_index": i, "u": u, "label": label, "v": v}


def ans(x, label_a, label_b="PATH_INVALID", h1=0, path=None, codes=(), max_list=None):
    """One S19 answer row. Default path: the SHORTCUT s -bad-> x."""
    if path is None and label_b in ("SUPPORTED", "PATH_INVALID"):
        path = [edge("1", "bad", x)]
        codes = codes or ("SHORTCUT",)
    if label_a == "UNRESOLVED":
        x, label_b, path = None, "NOT_APPLICABLE", None
    return {"submitted_index": 0, "node_id": x, "label_a": label_a, "label_b": label_b, "h1": h1,
            "primary_path": path, "primary_reason_codes": sorted(codes), "reason_codes": sorted(codes),
            "primary_path_max_list_size": max_list, "list_size": None}


def row(agent, answers, status="SUCCESS", query="BH2_00001"):
    return {"query_id": query, "agent_id": agent, "run_id": "toy", "attempt": 1,
            "episode_status": status, "cause": None, "answers": answers}


def panel(*answer_lists, statuses=None):
    statuses = statuses or ["SUCCESS"] * 4
    return [row(a, list(xs), st) for a, xs, st in zip(AGENTS, answer_lists, statuses)]


def run(rows, reference=REF, mapping=MAP):
    before = copy.deepcopy((rows, reference, mapping))
    out = query_cofailure(reference, mapping, "NONE", rows, DEGREES, AGENTS)
    assert (rows, reference, mapping) == before
    return out


def off(x, **kw):
    return ans(x, "OFF_QUESTION", **kw)


GOLD = ans("3", "GOLD", "SUPPORTED", 1, [edge("1", "r1", "2"), edge("2", "r2", "3")])


# --- §16.1 answer level -------------------------------------------------------------------------

def test_four_share_wrong_entity():
    out = run(panel([off("20")], [off("20")], [off("20")], [off("20")]))
    assert (out["question"]["cf3"], out["question"]["cf4"]) == (1, 1)
    [e] = out["question"]["shared_entities"]
    assert e["entity_id"] == "20" and e["agents"] == AGENTS and e["degree"] == 20


def test_three_share_fourth_correct():
    out = run(panel([off("20")], [off("20")], [off("20")], [GOLD]))
    assert (out["question"]["cf3"], out["question"]["cf4"]) == (1, 0)
    assert out["question"]["shared_entities"][0]["agents"] == ["A1", "A2", "A3"]


def test_x_x_y_z_and_all_different():
    assert run(panel([off("20")], [off("20")], [off("21")], [off("22")]))["question"]["cf3"] == 0
    assert run(panel([off("20")], [off("21")], [off("22")], [off("23")]))["question"]["cf3"] == 0


def test_hop1_filter_uses_per_answer_h1():
    out = run(panel([off("20", h1=1)], [off("20", h1=1)], [off("20", h1=0)], [GOLD]))
    assert out["question"]["cf3"] == 1 and out["hop1_clean"]["cf3"] == 0
    out = run(panel([off("20", h1=1)], [off("20", h1=1)], [off("20", h1=1)], [off("20", h1=0)]))
    assert (out["hop1_clean"]["cf3"], out["hop1_clean"]["cf4"]) == (1, 0)


def test_grounded_filter_three_sharers():
    ungrounded = ans("20", "OFF_QUESTION", "UNGROUNDED")
    out = run(panel([off("20")], [off("20")], [ungrounded], [GOLD]))
    assert out["question"]["cf3"] == 1 and out["grounded"]["cf3"] == 0


def test_grounded_filter_four_sharers():
    ungrounded = ans("20", "OFF_QUESTION", "UNGROUNDED")
    out = run(panel([off("20")], [off("20")], [off("20")], [ungrounded]))
    assert (out["grounded"]["cf3"], out["grounded"]["cf4"]) == (1, 0)
    assert (out["question"]["cf3"], out["question"]["cf4"]) == (1, 1)


def test_kg_unsupported_counts_as_grounded():
    kgu = ans("20", "OFF_QUESTION", "KG_UNSUPPORTED")
    assert run(panel([kgu], [kgu], [kgu], [GOLD]))["grounded"]["cf3"] == 1


def test_alt_valid_benchmark_only():
    alt = ans("10", "ALT_VALID", "SUPPORTED", 1, [edge("1", "r1", "5"), edge("5", "r2", "10")])
    out = run(panel([alt], [alt], [alt], [alt]))
    assert out["question"]["cf3"] == 0 and out["question"]["shared_entities"] == []
    assert (out["benchmark"]["cf3"], out["benchmark"]["cf4"]) == (1, 1)
    assert out["benchmark"]["shared_entities"][0]["per_agent"]["A1"]["label_a"] == "ALT_VALID"


def test_gold_never_benchmark_error():
    assert run(panel([GOLD], [GOLD], [GOLD], [GOLD]))["benchmark"]["cf3"] == 0


def test_unresolved_never_counts():
    u = ans(None, "UNRESOLVED")
    out = run(panel([u], [u], [u], [u]))
    assert all(out[k]["cf3"] == 0 for k in ("question", "grounded", "hop1_clean", "benchmark"))
    assert out["W_Q"] == {a: [] for a in AGENTS} and out["W_BH"] == {a: [] for a in AGENTS}


def test_duplicates_within_one_agent_count_once():
    out = run(panel([off("20"), off("20")], [off("20")], [], []))
    assert out["question"]["cf3"] == 0 and out["W_Q"]["A1"] == ["20"]


def test_filters_recompute_overlap_per_variant():
    # Unfiltered: X shared by A1-A3. Grounded: X is ungrounded for A3, but Y shared by A1, A2, A4.
    ug = ans("20", "OFF_QUESTION", "UNGROUNDED")
    out = run(panel([off("20"), off("21")], [off("20"), off("21")], [ug], [off("21")]))
    assert [e["entity_id"] for e in out["question"]["shared_entities"]] == ["20", "21"]
    assert [e["entity_id"] for e in out["grounded"]["shared_entities"]] == ["21"]


# --- §16.3 path level ---------------------------------------------------------------------------

def two_hop(x, first, mid, second, codes=()):
    return off(x, path=[edge("1", first, mid), edge(mid, second, x)], codes=codes)


def test_same_wrong_relation_at_same_node():
    p = two_hop("20", "bad", "30", "r2", ("WRONG_RELATION_HOP1",))
    out = run(panel([p], [p], [p], [GOLD]))
    assert (out["pcf_rel3"], out["pcf_rel4"]) == (1, 0)
    [case] = out["pcf_rel_cases"]
    assert (case["node_id"], case["relation"], case["agents"]) == ("1", "bad", ["A1", "A2", "A3"])


def test_same_relation_different_source_node_no_match():
    a = two_hop("20", "r1", "2", "bad")
    b = two_hop("21", "r1", "5", "bad")
    out = run(panel([a], [a], [b], [GOLD]))
    assert out["pcf_rel3"] == 0


def test_repeated_events_one_agent_do_not_count():
    a, b = two_hop("20", "bad", "30", "r2"), two_hop("21", "bad", "31", "r2")
    out = run(panel([a, b], [a], [GOLD], [GOLD]))
    assert out["pcf_rel3"] == 0


def test_both_hops_violated_two_events():
    p = two_hop("20", "bad", "30", "worse", ("WRONG_RELATION_HOP1", "WRONG_RELATION_HOP2"))
    out = run(panel([p], [p], [p], [p]))
    assert [(c["node_id"], c["relation"]) for c in out["pcf_rel_cases"]] == [("1", "bad"), ("30", "worse")]
    assert out["pcf_rel4"] == 1


def test_correct_relations_no_events():
    p = two_hop("20", "r1", "2", "r2", ("WRONG_TARGET_TYPE",))
    assert run(panel([p], [p], [p], [p]))["pcf_rel3"] == 0


def test_shared_off_path_intermediate_node():
    p = two_hop("20", "bad", "30", "r2")
    out = run(panel([p], [p], [p], [GOLD]))
    assert (out["pcf_node3"], out["pcf_node4"]) == (1, 0)
    assert [c["node_id"] for c in out["pcf_node_cases"]] == ["30"]
    assert out["pcf_node_cases"][0]["degree"] == 30


def test_pcf_node_excludes_s_answer_bq_tq():
    via_bridge = two_hop("20", "r1", "2", "bad")        # intermediate 2 is in B_q
    via_target = two_hop("21", "bad", "10", "bad")      # intermediate 10 is in T_q
    direct = off("22")                                   # no intermediate; s and answer only
    # walk through s again: intermediates are 2 (B_q) and 1 (= s); the answer 23 is the endpoint
    via_s = off("23", path=[edge("1", "bad", "2"), edge("2", "bad", "1"), edge("1", "bad", "23")])
    every = [via_bridge, via_target, direct, via_s]
    out = run(panel(every, every, every, every))
    assert out["pcf_node3"] == 0 and out["pcf_node_cases"] == []
    assert out["question"]["cf4"] == 1  # the same answers do co-fail at answer level


def test_alternative_paths_do_not_create_events():
    # Primary path is correct (r1, r2 to a wrong-type node); a non-primary path had a wrong relation.
    p = two_hop("20", "r1", "2", "r2", ("WRONG_TARGET_TYPE",))
    p["reason_codes"] = ["WRONG_RELATION_HOP1", "WRONG_TARGET_TYPE"]
    out = run(panel([p], [p], [p], [p]))
    assert (out["pcf_rel3"], out["pcf_node3"], out["pcf_shortcut3"]) == (0, 0, 0)


def test_shortcut_same_label():
    out = run(panel([off("20")], [off("21")], [off("22")], [GOLD]))
    assert out["pcf_shortcut3"] == 1
    [case] = out["pcf_shortcut_cases"]
    assert (case["node_id"], case["relation"], case["agents"]) == ("1", "bad", ["A1", "A2", "A3"])
    # different labels from s: no case
    other = off("23", path=[edge("1", "other", "23")], codes=("SHORTCUT",))
    assert run(panel([off("20")], [off("21")], [other], [GOLD]))["pcf_shortcut3"] == 0


def test_shortcut_with_accepted_label_is_still_an_event():
    sc = off("20", path=[edge("1", "r1", "20")], codes=("SHORTCUT",))
    out = run(panel([sc], [sc], [sc], [GOLD]))
    assert out["pcf_rel3"] == 1 and out["pcf_rel_cases"][0]["relation"] == "r1"


def test_only_off_question_primary_paths():
    # Non-primary (alternative) paths are not inputs at all; GOLD/ALT_VALID primary paths never count.
    bad_gold = ans("3", "GOLD", "PATH_INVALID", 0, [edge("1", "bad", "30"), edge("30", "bad", "3")])
    out = run(panel([bad_gold], [bad_gold], [bad_gold], [bad_gold]))
    assert (out["pcf_rel3"], out["pcf_node3"], out["pcf_shortcut3"]) == (0, 0, 0)


def test_answers_without_primary_path_have_no_events():
    ug, kgu = ans("20", "OFF_QUESTION", "UNGROUNDED"), ans("20", "OFF_QUESTION", "KG_UNSUPPORTED")
    out = run(panel([ug], [kgu], [ug], [kgu]))
    assert (out["pcf_rel3"], out["pcf_node3"], out["pcf_shortcut3"]) == (0, 0, 0)


def test_case_metadata_list_sizes_and_ambiguity():
    p = [two_hop("20", "bad", "30", "r2") for _ in range(3)]
    for size, a in zip((7, 9, 4), p):
        a["primary_path_max_list_size"] = size
    out = run(panel([p[0]], [p[1]], [p[2]], [GOLD]))
    [case] = out["pcf_node_cases"]
    assert {ag: [e["primary_path_max_list_size"] for e in ev] for ag, ev in case["per_agent"].items()} == \
        {"A1": [7], "A2": [9], "A3": [4]}
    assert out["ambiguity_tag"] == "NONE" and out["R1"] == ["r1"]


def test_degree_percentiles_from_degree_statistics_are_inclusive():
    nodes = pd.DataFrame([(1, "drug"), (2, "drug"), (3, "drug"), (4, "disease")], columns=["node_index", "node_type"])
    edges = pd.DataFrame([(1, 2), (1, 3), (2, 4)], columns=["x_index", "y_index"])
    degrees = degree_statistics(nodes, edges)
    # drug degrees 2, 2, 1 -> node 2 has 3/3 drugs with degree <= 2 -> 100; node 3: 1/3.
    assert degrees["2"]["degree_percentile"] == 100.0
    assert degrees["3"]["degree_percentile"] == pytest.approx(100 / 3)
    ref = {**REF, "s": "1", "B_q": [], "T_q": ["4"], "A_star_q": ["4"]}
    sc = off("3", path=[edge("1", "bad", "3")], codes=("SHORTCUT",))
    out = query_cofailure(ref, MAP, "R1_AMBIGUOUS", panel([sc], [sc], [sc], []), degrees, AGENTS)
    e = out["question"]["shared_entities"][0]
    assert (e["degree"], e["degree_percentile"]) == (1, pytest.approx(100 / 3))
    assert out["pcf_shortcut_cases"][0]["degree"] == 2 and out["ambiguity_tag"] == "R1_AMBIGUOUS"


# --- failures, validation, determinism ----------------------------------------------------------

def test_technical_failure_reported_and_contributes_nothing():
    out = run(panel([off("20")], [off("20")], [off("20")], [], statuses=["SUCCESS"] * 3 + ["PARSE_FAIL"]))
    assert out["technical_failure_agents"] == ["A4"]
    assert out["episodes"]["A4"]["episode_status"] == "PARSE_FAIL"
    assert (out["question"]["cf3"], out["question"]["cf4"]) == (1, 0)


@pytest.mark.parametrize("mutate, message", [
    (lambda r: r.pop(), "missing"),
    (lambda r: r.append(copy.deepcopy(r[0])), "duplicate"),
    (lambda r: r[0].update(query_id="BH2_00002"), "panel row"),
    (lambda r: r[0].update(agent_id="X"), "unknown agent"),
    (lambda r: r[0].update(episode_status="PARSE_FAIL"), "scored answers"),
    (lambda r: r[0]["answers"][0].update(label_a="ALT_VALID"), "disagrees with T_q"),
    (lambda r: r[0]["answers"][0].update(label_b="SUPPORTED"), "invariant"),
    (lambda r: r[0]["answers"][0].update(label_b="UNGROUNDED"), "primary path presence"),
    (lambda r: r[0]["answers"][0].update(primary_path=[edge("9", "bad", "20")]), "walk"),
])
def test_invalid_inputs_rejected(mutate, message):
    rows = panel([off("20")], [off("20")], [off("20")], [GOLD])
    mutate(rows)
    with pytest.raises(ValueError, match=message):
        query_cofailure(REF, MAP, "NONE", rows, DEGREES, AGENTS)


def test_missing_degree_rejected():
    with pytest.raises(ValueError, match="degree"):
        query_cofailure(REF, MAP, "NONE", panel([off("20")], [off("20")], [off("20")], []), {}, AGENTS)


def test_deterministic_under_input_order():
    answers = [[off("40"), off("9"), two_hop("21", "bad", "30", "worse")],
               [off("9"), off("40"), two_hop("21", "bad", "30", "worse")],
               [two_hop("21", "bad", "30", "worse"), off("40"), off("9")], [off("9")]]
    base = run(panel(*answers))
    rng = random.Random(42)
    for _ in range(5):
        shuffled = [rng.sample(xs, len(xs)) for xs in answers]
        rows = panel(*shuffled)
        rng.shuffle(rows)
        assert run(rows) == base
    assert [e["entity_id"] for e in base["question"]["shared_entities"]] == ["9", "21", "40"]  # numeric order


# --- §16.4 pairwise ----------------------------------------------------------------------------

def result(qid, w):
    return {"query_id": qid, "W_Q": {a: w.get(a, []) for a in AGENTS}}


def test_pairwise_hand_computed():
    results = [result("q1", {"A1": ["5"], "A2": ["5"], "A3": ["6"]}),   # A1A2 agree; A1A3, A2A3 disagree
               result("q2", {"A1": ["5", "7"], "A2": ["8"], "A3": ["7"]}),  # A1A2 no; A1A3 yes; A2A3 no
               result("q3", {"A1": ["5"]}),                               # only one non-empty: no pair
               result("q4", {})]
    out = {(p["agent_i"], p["agent_j"]): p for p in pairwise_agreement(results, AGENTS)}
    assert len(out) == 6
    assert (out["A1", "A2"]["numerator"], out["A1", "A2"]["denominator"], out["A1", "A2"]["agreement"]) == (1, 2, 0.5)
    assert (out["A1", "A3"]["numerator"], out["A1", "A3"]["denominator"]) == (1, 2)
    assert (out["A2", "A3"]["numerator"], out["A2", "A3"]["denominator"], out["A2", "A3"]["agreement"]) == (0, 2, 0.0)
    assert out["A1", "A2"]["queries_intersecting"] == ["q1"]
    for pair in (("A1", "A4"), ("A2", "A4"), ("A3", "A4")):
        assert (out[pair]["denominator"], out[pair]["agreement"]) == (0, None)


def test_pairwise_uses_question_level_sets_only():
    alt = ans("10", "ALT_VALID", "SUPPORTED", 1, [edge("1", "r1", "5"), edge("5", "r2", "10")])
    r = run(panel([alt], [alt], [off("20")], [off("20")]))
    out = {(p["agent_i"], p["agent_j"]): p for p in pairwise_agreement([r], AGENTS)}
    assert out["A1", "A2"]["denominator"] == 0          # shared ALT_VALID is not a question-level error
    assert out["A3", "A4"]["agreement"] == 1.0


def test_pairwise_rejects_duplicate_queries():
    with pytest.raises(ValueError, match="duplicate"):
        pairwise_agreement([result("q1", {}), result("q1", {})], AGENTS)


# --- compatibility with real S19 output ---------------------------------------------------------

def test_consumes_agent_metrics_rows():
    from test_agent_metrics import evaluate, nb
    log = [nb("1", "r1", ["2", "5"]), nb("2", "r2", ["3", "10"]), nb("1", "bad", ["4"]), nb("4", "bad", ["9"])]
    # 9 is a drug (not Type_T disease): OFF_QUESTION via 1 -bad-> 4 -bad-> 9; 3 is GOLD/SUPPORTED.
    metric = evaluate(log, ids=("3", "9"))
    rows = [{**copy.deepcopy(metric), "agent_id": a} for a in AGENTS]
    ref = {"query_id": "BH2_00001", "relation_type": "toy", "s": "1", "A_star_q": ["3"],
           "B_q": ["2", "5"], "T_q": ["3", "10", "11"]}
    degrees = {**DEGREES, **{n: dict(v) for n, v in metric["node_statistics"].items()}}
    out = query_cofailure(ref, {"R1": ["r1"], "R2": ["r2"]}, "NONE", rows, degrees, AGENTS)
    assert out["W_Q"]["A1"] == ["9"] and out["question"]["cf4"] == 1
    assert [(c["node_id"], c["relation"]) for c in out["pcf_rel_cases"]] == [("1", "bad"), ("4", "bad")]
    assert [c["node_id"] for c in out["pcf_node_cases"]] == ["4"]
