"""Tests for scripts/41_b2_lenient.py (Phase J B2) on tiny synthetic fixtures."""
import importlib.util
from pathlib import Path
from types import SimpleNamespace

import pytest

ROOT = Path(__file__).resolve().parents[1]
spec = importlib.util.spec_from_file_location("b2", ROOT / "scripts/41_b2_lenient.py")
M = importlib.util.module_from_spec(spec)
spec.loader.exec_module(M)

OFF, IND, DPP, CONTRA = "off-label use", "indication", "disease_phenotype_positive", "contraindication"
AGENTS = ["A1", "A2", "A3", "A4"]


# ------------------------------------------------------------------------------------- the key

def test_lenient_labels_and_indication_step():
    assert M.lenient_labels([IND]) == [IND, OFF]
    assert M.lenient_labels(["drug_protein"]) == ["drug_protein"]
    with pytest.raises(ValueError):
        M.lenient_labels([IND, CONTRA])
    assert M.indication_step([DPP], [IND]) == 1
    assert M.indication_step([IND], ["drug_effect"]) == 0
    assert M.indication_step(["drug_protein"], ["disease_protein"]) is None


GRAPH = {  # node -> (type, {label: [neighbours]}); either direction already resolved
    "1": ("effect/phenotype", {DPP: ["2", "5"]}),
    "2": ("disease", {DPP: ["1"], IND: ["3"], OFF: ["4"], CONTRA: ["6"]}),
    "5": ("disease", {DPP: ["1"], OFF: ["7"]}),
    "3": ("drug", {IND: ["2"]}), "4": ("drug", {OFF: ["2"]}), "6": ("drug", {CONTRA: ["2"]}),
    "7": ("drug", {OFF: ["5"]}),
}


class FakeKG:
    def get_node(self, n):
        return {"id": n, "type": GRAPH[n][0]}

    def neighbors_by_label(self, node, kind):
        return {lab: {v for v in vs if GRAPH[v][0] == kind} for lab, vs in GRAPH[node][1].items()}


def test_reference_sets_strict_and_lenient():
    kg = FakeKG()
    assert M.reference_sets("1", "disease", "drug", [DPP], [IND], kg.neighbors_by_label) == (["2"], ["3"])
    # 5 is a dead end under the strict key and a valid bridge under the lenient one; contraindication never
    assert M.reference_sets("1", "disease", "drug", [DPP], [IND, OFF], kg.neighbors_by_label) == (
        ["2", "5"], ["3", "4", "7"])


# ------------------------------------------------------------------------------------- per episode

def edge(i, u, label, v):
    return {"creation_index": i, "u": u, "label": label, "v": v}


def test_precision_and_contraindication_positions():
    row = {"episode_status": "SUCCESS", "answers": [
        {"node_id": "3", "label_a": "GOLD", "primary_path": [edge(0, "1", DPP, "2"), edge(1, "2", IND, "3")]},
        {"node_id": "6", "label_a": "OFF_QUESTION", "primary_path": [edge(0, "1", DPP, "2"), edge(2, "2", CONTRA, "6")]},
        {"node_id": "8", "label_a": "OFF_QUESTION", "primary_path": [edge(0, "1", CONTRA, "8")]},
        {"node_id": None, "label_a": "UNRESOLVED", "primary_path": None}]}
    assert M.precision(row) == (1, 3)
    assert M.precision({"episode_status": "TIMEOUT", "answers": []}) is None
    hits = M.contra_answers(row, 1, {"3"}, {"3", "6"})
    assert hits == [{"node_id": "6", "in_T_q": False, "in_T_q_plus": True}]
    assert [h["node_id"] for h in M.contra_answers(row, 0, set(), set())] == ["8"]
    assert M.contra_answers(row, None, set(), set()) == []


def test_contra_table_counts_answers_and_queries():
    contra = [{"query_id": "Q1", "agent_id": "A1", "answers": [{"in_T_q": False, "in_T_q_plus": True}] * 2},
              {"query_id": "Q2", "agent_id": "A1", "answers": [{"in_T_q": True, "in_T_q_plus": True}]}]
    a1, a2 = M.contra_table(contra, ["A1", "A2"])
    assert (a1["answers"], a1["queries"], a1["answers_in_T_q"], a1["answers_in_T_q_plus"]) == (3, 2, 1, 3)
    assert a2["answers"] == 0


# ------------------------------------------------------------------------------------- end to end

def nb(entity, relation, ids):
    return {"tool": "get_neighbors", "arguments": {"entity_id": entity, "relation": relation}, "success": True,
            "result": {"items": [{"id": i} for i in ids], "total_count": len(ids), "page": 1, "page_size": 50,
                       "has_more": False}}


OFF_PATH = [edge(0, "1", DPP, "2"), edge(1, "2", OFF, "4")]


def stored_answer(node, label_a, label_b, h1, path, codes):
    return {"node_id": node, "label_a": label_a, "label_b": label_b, "h1": h1, "primary_path": path,
            "primary_reason_codes": codes, "primary_path_max_list_size": 1, "list_size": 1}


def build(agent_answers):
    """One effect/phenotype:disease:drug query; every agent opens 2 with off-label use and answers ``agent_answers``."""
    ref = {"query_id": "Q1", "s": "1", "Type_B": "disease", "Type_T": "drug", "B_q": ["2"], "T_q": ["3"],
           "A_star_q": ["3"], "G_q": ["3"], "T_q_gold_bridges": ["3"], "construction": "UNION",
           "relation_type": "effect/phenotype:disease:drug"}
    calls = [nb("1", DPP, ["2"]), nb("2", OFF, ["4"]), nb("2", IND, ["3"])]
    records, rows = {}, {}
    for agent in AGENTS:
        records[(agent, "Q1")] = {"query_id": "Q1", "agent_id": agent, "call_log": calls,
                                  "raw_final_output": ",".join(agent_answers)}
        answers = []
        for x in agent_answers:
            if x == "4":
                answers.append(stored_answer("4", "OFF_QUESTION", "PATH_INVALID", 1, OFF_PATH,
                                             ["WRONG_RELATION_HOP2"]))
            else:
                answers.append(stored_answer("3", "GOLD", "SUPPORTED", 1,
                                             [edge(0, "1", DPP, "2"), edge(2, "2", IND, "3")], []))
        valid = sum(a["label_a"] != "OFF_QUESTION" for a in answers)
        rows[(agent, "Q1")] = {"query_id": "Q1", "agent_id": agent, "run_id": "r", "attempt": 1, "cause": None,
                               "episode_status": "SUCCESS", "hop1_status": "H1_CLEAN", "answers": answers,
                               "numerators": {"question_valid_precision": valid},
                               "denominators": {"question_valid_precision": len(answers)}}
    shared = int("4" in agent_answers)
    cof = {"queries": [{"query_id": "Q1", "ambiguity_tag": "t", "question": {"cf3": shared, "cf4": shared},
                        "hop1_clean": {"cf3": shared, "cf4": shared}}], "source_name_overlap_queries": []}
    data = {"agents": AGENTS, "rows": rows, "records": records, "cofailure": cof}
    mapping = {ref["relation_type"]: {"R1": [DPP], "R2": [IND]}}
    degrees = {n: {"degree": 1, "degree_percentile": 50.0} for n in GRAPH}
    return data, {"Q1": ref}, mapping, degrees


@pytest.fixture
def fake_parse(monkeypatch):
    monkeypatch.setattr(M, "parse_final", lambda raw, _: {"answers": raw.split(",") if raw else []})
    monkeypatch.setattr(M, "normalize_agent_answers", lambda kg, answers, t: SimpleNamespace(
        answers=[SimpleNamespace(node_id=a) for a in answers]))


def test_shared_off_label_answer_is_a_cofailure_only_under_the_strict_key(fake_parse):
    data, refs, mapping, degrees = build(["3", "4"])
    out = M.compute(data, refs, mapping, FakeKG(), degrees)
    t = out["tables"]["all_queries"]
    assert t["cofailure"]["strict"] == {"CF3^Q": 1, "CF4^Q": 1, "CF3^{Q,H1}": 1, "CF4^{Q,H1}": 1}
    assert t["cofailure"]["lenient"] == {"CF3^Q": 0, "CF4^Q": 0, "CF3^{Q,H1}": 0, "CF4^{Q,H1}": 0}
    strict_a1, lenient_a1 = t["per_agent"]["strict"][0], t["per_agent"]["lenient"][0]
    assert (strict_a1["qv_pooled_num"], strict_a1["qv_pooled_den"]) == (1, 2)
    assert (lenient_a1["qv_pooled_num"], lenient_a1["qv_pooled_den"]) == (2, 2)
    assert lenient_a1["H1_CLEAN"] == 1
    assert out["reference_sets"]["Q1"] == {"tq_size": 1, "tq_plus_size": 3, "bq_size": 1, "bq_plus_size": 2,
                                           "changed": True}


def test_strict_reproduction_is_checked(fake_parse):
    data, refs, mapping, degrees = build(["4"])
    data["rows"][("A2", "Q1")]["answers"][0]["h1"] = 0   # stored h1 that the trace does not give
    with pytest.raises(ValueError, match="strict path labels not reproduced"):
        M.compute(data, refs, mapping, FakeKG(), degrees)
    data, refs, mapping, degrees = build(["4"])
    data["cofailure"]["queries"][0]["question"]["cf4"] = 0
    with pytest.raises(ValueError, match="not reproduced from cofailure.json"):
        M.compute(data, refs, mapping, FakeKG(), degrees)
    data, refs, mapping, degrees = build(["4"])
    data["rows"][("A3", "Q1")]["numerators"]["question_valid_precision"] = 1
    with pytest.raises(ValueError, match="precision not reproduced"):
        M.compute(data, refs, mapping, FakeKG(), degrees)
    data, refs, mapping, degrees = build(["4"])
    refs["Q1"]["T_q"] = ["3", "4"]
    with pytest.raises(ValueError, match="does not reproduce the frozen"):
        M.compute(data, refs, mapping, FakeKG(), degrees)


def test_answers_must_match_the_metrics_row(fake_parse):
    data, refs, mapping, degrees = build(["4"])
    data["records"][("A1", "Q1")]["raw_final_output"] = "3"
    with pytest.raises(ValueError, match="re-derived answers differ"):
        M.compute(data, refs, mapping, FakeKG(), degrees)
