import pytest

from cofail_kg.evaluation import smoke_summary as ss


def record(qid, status="SUCCESS", cause=None, prompts=(100, 200)):
    return {"query_id": qid, "status": status, "cause": cause,
            "token_counts": {"prompt": list(prompts), "completion": [1] * len(prompts)}}


def metric(qid, answers=(), early=False, budget=False, hop1="H1_CLEAN", agent="A"):
    return {"agent_id": agent, "query_id": qid, "answers": list(answers),
            "label_a_counts": {"GOLD": 1, "OFF_QUESTION": 0}, "label_b_counts": {"SUPPORTED": 1},
            "reason_counts": {"R1": 1}, "primary_reason_counts": {}, "hop1_status": hop1,
            "early_stop": early, "budget_exhausted": budget}


def test_model_summary_tallies():
    records = [record("q1", prompts=(100, 7400)), record("q2", "ERROR", "OUT_OF_MEMORY", (None,)),
               record("q3", "PARSE_FAIL", prompts=(8189,))]
    metrics = [metric("q1", early=True), metric("q2", budget=True, hop1="H1_NONE"), metric("q3")]
    s = ss.model_summary(records, metrics, 8192)
    assert s["status_counts"] == {"ERROR": 1, "PARSE_FAIL": 1, "SUCCESS": 1}
    assert s["error_causes"] == {"OUT_OF_MEMORY": 1} and s["out_of_memory_episodes"] == 1
    assert s["label_a"] == {"GOLD": 3} and s["label_b"] == {"SUPPORTED": 3}
    assert s["reason_codes"] == {"R1": 3} and s["primary_reason_codes"] == {}
    assert s["hop1_status"] == {"H1_CLEAN": 2, "H1_NONE": 1}
    assert s["early_stop_share"] == pytest.approx(1 / 3) and s["budget_hit_share"] == pytest.approx(1 / 3)
    assert s["largest_prompt_tokens"] == 8189
    assert s["episodes_prompt_over_90pct_num_ctx"] == ["q1", "q3"]


def test_model_summary_requires_pairing():
    with pytest.raises(ValueError):
        ss.model_summary([record("q1")], [metric("q2")], 8192)


def test_off_question_supported_detection_and_render():
    good = {"node_id": 1, "label_a": "OFF_QUESTION", "label_b": "PATH_INVALID"}
    bad = {"node_id": 7, "label_a": "OFF_QUESTION", "label_b": "SUPPORTED"}
    assert ss.off_question_supported([metric("q1", [good])]) == []
    violations = ss.off_question_supported([metric("q1", [good, bad], agent="B")])
    assert violations == [("B", "q1", "7")]
    s = ss.model_summary([record("q1")], [metric("q1")], 32768)
    text = ss.render_markdown("smoke_single", {"B": s}, violations)
    assert "FAIL: B q1 node 7" in text and "|B|1|SUCCESS 1|none|" in text
    assert "PASS: none found." in ss.render_markdown("smoke_single", {"B": s}, [])


def test_episodes_without_label_counts_are_skipped():
    m = metric("q2")
    m.update(label_a_counts=None, label_b_counts=None, reason_counts=None, primary_reason_counts=None)
    s = ss.model_summary([record("q1"), record("q2", "PARSE_FAIL")], [metric("q1"), m], 8192)
    assert s["label_a"] == {"GOLD": 1} and s["reason_codes"] == {"R1": 1}
