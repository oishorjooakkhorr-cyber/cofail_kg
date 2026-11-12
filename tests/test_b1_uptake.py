"""Tests for scripts/40_b1_uptake.py (Phase J B1) on tiny synthetic traces."""
import importlib.util
from pathlib import Path

import pytest

ROOT = Path(__file__).resolve().parents[1]
spec = importlib.util.spec_from_file_location("b1", ROOT / "scripts/40_b1_uptake.py")
M = importlib.util.module_from_spec(spec)
spec.loader.exec_module(M)

OFF = "off-label use"
S = "10"


def nb(entity, relation, ids, success=True):
    """A get_neighbors call-log entry."""
    entry = {"tool": "get_neighbors", "arguments": {"entity_id": entity, "relation": relation}, "success": success}
    if success:
        entry["result"] = {"items": [{"id": i} for i in ids], "total_count": len(ids), "page": 1,
                           "page_size": 50, "has_more": False}
    else:
        entry["result"] = f"Error: entity {entity} has no relation {relation}."
    return entry


def ins(entity, relations, success=True):
    """An inspect_entity call-log entry; relations = {label: [neighbor types]}."""
    entry = {"tool": "inspect_entity", "arguments": {"entity_id": entity}, "success": success}
    entry["result"] = ({"id": str(entity), "name": "x", "type": "t",
                        "relations": [{"label": k, "neighbor_types": v} for k, v in relations.items()]}
                       if success else f"Error: unknown entity ID {entity}.")
    return entry


def rec(calls, qid="Q1", agent="A", status="SUCCESS"):
    return {"query_id": qid, "agent_id": agent, "status": status, "call_log": calls}


def edge(i, u, label, v):
    return {"creation_index": i, "u": u, "label": label, "v": v}


def row(answers, qid="Q1", agent="A", status="SUCCESS"):
    return {"query_id": qid, "agent_id": agent, "episode_status": status, "attempt": 1,
            "answers": [{"node_id": n, "primary_path": p} for n, p in answers]}


R1 = ["disease_phenotype_positive"]


# ------------------------------------------------------------------------------- treat-final episodes

def test_inspect_listing_with_type_t_is_opportunity_only():
    r = rec([nb(S, R1[0], ["20"]), ins("20", {OFF: ["drug"], "indication": ["drug"]})])
    ep = M.classify_episode(r, row([]), S, R1, "drug", "treat-final")
    assert (ep["opportunity"], ep["opened"], ep["taken"]) == (True, False, False)
    assert ep["listed_nodes"] == ["20"] and ep["opportunity_nodes"] == ["20"]


def test_inspect_listing_without_type_t_is_not_opportunity():
    r = rec([nb(S, R1[0], ["20"]), ins("20", {OFF: ["disease"]})])
    assert not M.classify_episode(r, row([]), S, R1, "drug", "treat-final")["opportunity"]


def test_node_reached_by_non_r1_label_is_not_reached():
    r = rec([nb(S, "other_label", ["20"]), ins("20", {OFF: ["drug"]}), nb("20", OFF, ["30"])])
    ep = M.classify_episode(r, row([]), S, R1, "drug", "treat-final")
    assert (ep["opportunity"], ep["opened"], ep["reached_count"]) == (False, False, 0)


def test_failed_reaching_call_reaches_nothing():
    r = rec([nb(S, R1[0], ["20"], success=False), nb("20", OFF, ["30"])])
    assert not M.classify_episode(r, row([]), S, R1, "drug", "treat-final")["opportunity"]


def test_failed_open_call_counts_and_integer_ids_match():
    r = rec([nb(S, R1[0], ["20"]), nb(20, OFF, [], success=False)])
    ep = M.classify_episode(r, row([]), S, R1, "drug", "treat-final")
    assert (ep["opportunity"], ep["opened"], ep["opened_nodes"]) == (True, True, ["20"])


def test_order_of_calls_is_ignored():
    r = rec([ins("20", {OFF: ["drug"]}), nb(S, R1[0], ["20"])])
    assert M.classify_episode(r, row([]), S, R1, "drug", "treat-final")["opportunity"]


def test_taken_second_edge_any_length_but_not_first_edge():
    two = [edge(0, S, R1[0], "20"), edge(1, "20", OFF, "30")]
    three = [edge(0, S, "x", "21"), edge(1, "21", OFF, "22"), edge(2, "22", "y", "31")]
    one = [edge(0, S, OFF, "32")]
    second_not_off = [edge(0, S, R1[0], "20"), edge(2, "20", "indication", "33")]
    r = rec([])
    ep = M.classify_episode(r, row([("30", two), ("31", three), ("32", one), ("33", second_not_off),
                                    ("34", None)]), S, R1, "drug", "treat-final")
    assert ep["taken"] and ep["off_label_answers"] == ["30", "31"]


# ------------------------------------------------------------------------------- treat-first episodes

def test_treat_first_mirrors_at_s():
    listed = rec([ins(S, {OFF: ["disease"]})])
    ep = M.classify_episode(listed, row([]), S, ["indication"], "disease", "treat-first")
    assert (ep["opportunity"], ep["opened"]) == (True, False)
    wrong_type = rec([ins(S, {OFF: ["drug"]})])
    assert not M.classify_episode(wrong_type, row([]), S, ["indication"], "disease", "treat-first")["opportunity"]
    opened = rec([nb(S, OFF, ["40"])])
    taken_path = [edge(0, S, OFF, "40"), edge(1, "40", "drug_effect", "50")]
    ep = M.classify_episode(opened, row([("50", taken_path)]), S, ["indication"], "disease", "treat-first")
    assert (ep["opportunity"], ep["opened"], ep["taken"], ep["off_label_answers"]) == (True, True, True, ["50"])
    # an off-label second edge is not the indication step for treat-first
    second = [edge(0, S, "indication", "40"), edge(1, "40", OFF, "50")]
    assert not M.classify_episode(opened, row([("50", second)]), S, ["indication"], "disease",
                                  "treat-first")["taken"]


def test_other_group_is_rejected():
    with pytest.raises(ValueError):
        M.classify_episode(rec([]), row([]), S, R1, "drug", "other")


# ------------------------------------------------------------------------------- trace cross-check

def test_stored_path_must_be_in_trace_graph():
    r = rec([nb(S, R1[0], ["20"]), nb("20", OFF, ["30"])])
    M.check_paths_in_trace(r, row([("30", [edge(0, S, R1[0], "20"), edge(1, "20", OFF, "30")])]))
    with pytest.raises(ValueError, match="not in the trace graph"):
        M.check_paths_in_trace(r, row([("30", [edge(0, S, R1[0], "20"), edge(5, "20", OFF, "30")])]))


# ------------------------------------------------------------------------------- summaries and verdict

def ep(agent, opp, opn, taken):
    return {"agent_id": agent, "opportunity": opp, "opened": opn, "taken": taken}


def test_nested_ratios_and_taken_outside():
    eps = [ep("A", True, True, True), ep("A", True, False, False), ep("A", False, False, True),
           ep("A", True, True, False), ep("B", False, False, False)]
    a, b = M.summarize(eps, ["A", "B"])
    assert (a["episodes"], a["opportunity"], a["opened"], a["taken"]) == (4, 3, 2, 2)
    assert (a["taken_and_opportunity"], a["taken_and_opened"], a["taken_outside_opportunity"]) == (1, 1, 1)
    assert a["uptake"] == pytest.approx(1 / 3) and a["opened_per_opportunity"] == pytest.approx(2 / 3)
    assert a["taken_per_opened"] == pytest.approx(0.5)
    assert b["uptake"] is None and b["taken_per_opened"] is None


def vrow(agent, opp, uptake):
    return {"agent_id": agent, "opportunity": opp, "uptake": uptake}


def test_clean_boundaries():
    clean = M.clean_verdict([vrow("A", 5, 0.5), vrow("B", 9, 0.9), vrow("C", 5, 0.5), vrow("D", 0, None)])
    assert clean["outcome"] == "CLEAN" and clean["agents_meeting"] == ["A", "B", "C"]
    not_clean = M.clean_verdict([vrow("A", 4, 1.0), vrow("B", 9, 0.9), vrow("C", 5, 0.49), vrow("D", 6, 0.5)])
    assert not_clean["outcome"] == "NOT CLEAN" and not_clean["count"] == 2


# ------------------------------------------------------------------------------- end to end

TF, TS, OT = "effect/phenotype:disease:drug", "drug:disease:effect/phenotype", "drug:gene/protein:disease"


def test_compute_views_exclusions_and_groups():
    queries = [
        {"query_id": "Q1", "relation_type": TF, "R1": R1, "R2": ["indication"], "s": S},
        {"query_id": "Q2", "relation_type": TF, "R1": R1, "R2": ["indication"], "s": S},
        {"query_id": "Q3", "relation_type": TS, "R1": ["indication"], "R2": ["disease_phenotype_positive"],
         "s": S},
        {"query_id": "Q4", "relation_type": OT, "R1": ["drug_protein"], "R2": ["disease_protein"], "s": S},
    ]
    agents = ["A", "B"]
    taken_path = [edge(0, S, R1[0], "20"), edge(1, "20", OFF, "30")]
    calls = [nb(S, R1[0], ["20"]), nb("20", OFF, ["30"])]
    records, rows = {}, {}
    for q in queries:
        for a in agents:
            status = "TIMEOUT" if (q["query_id"], a) == ("Q2", "B") else "SUCCESS"
            records[(a, q["query_id"])] = rec(calls if q["query_id"] in ("Q1", "Q2") else [], q["query_id"], a,
                                              status)
            answers = [("30", taken_path)] if q["query_id"] == "Q1" else []
            rows[(a, q["query_id"])] = row(answers, q["query_id"], a, status)
    data = {"agents": agents, "rows": rows, "records": records,
            "cofailure": {"queries": queries, "source_name_overlap_queries": ["Q1"]}}
    refs = {q["query_id"]: {"s": S, "Type_B": "disease", "Type_T": "drug"} for q in queries}
    subset_of = {"Q1": "pilot", "Q2": "expansion", "Q3": "expansion", "Q4": "pilot"}
    out = M.compute(data, refs, subset_of)
    tf = {r["agent_id"]: r for r in out["tables"]["all_queries"]["treat-final"]}
    assert (tf["A"]["episodes"], tf["A"]["opportunity"], tf["A"]["taken"]) == (2, 2, 1)
    assert (tf["B"]["episodes"], tf["B"]["opportunity"]) == (1, 1)
    assert out["non_success_episodes_excluded"]["treat-final"]["B"] == {"TIMEOUT": 1}
    no_sno = {r["agent_id"]: r for r in out["tables"]["without_source_name_overlap"]["treat-final"]}
    assert (no_sno["A"]["episodes"], no_sno["A"]["taken"]) == (1, 0)
    assert {e["group"] for e in out["episodes"]} == {"treat-final", "treat-first"}
    assert all(e["query_id"] != "Q4" for e in out["episodes"])
    assert out["verdict"]["outcome"] == "NOT CLEAN"  # 2 agents only, < 5 opportunities each


def test_compute_stops_on_status_mismatch():
    q = {"query_id": "Q1", "relation_type": TF, "R1": R1, "R2": ["indication"], "s": S}
    data = {"agents": ["A"], "rows": {("A", "Q1"): row([], status="SUCCESS")},
            "records": {("A", "Q1"): rec([], status="ERROR")},
            "cofailure": {"queries": [q], "source_name_overlap_queries": []}}
    with pytest.raises(ValueError, match="status"):
        M.compute(data, {"Q1": {"s": S, "Type_B": "disease", "Type_T": "drug"}}, {"Q1": "pilot"})


def test_outputs_are_write_once(tmp_path):
    path = tmp_path / "x.csv"
    M.write_once(path, "a\n")
    M.write_once(path, "a\n")
    with pytest.raises(FileExistsError):
        M.write_once(path, "b\n")
