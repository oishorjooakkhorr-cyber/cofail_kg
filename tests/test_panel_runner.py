"""S25 panel runner (protocol §9.2, §19) and panel checks (§19.1) on synthetic episodes; no model calls."""

import hashlib
import json

import pytest

from cofail_kg.agents import panel_runner as pr
from cofail_kg.agents.prompts import PROMPT_VERSION
from cofail_kg.agents.run_agent import run_episode as real_run_episode
from cofail_kg.agents.trace import make_episode_record, record_path, save_episode_record
from cofail_kg.evaluation.panel_analysis import audit_key, audit_rows, audit_selection, completeness

AGENTS = ["A1", "A2"]
QUERIES = ["BH2_00001", "BH2_00002", "BH2_00003"]


def agent(agent_id):
    return {"agent_id": agent_id, "tag": f"{agent_id.lower()}:tag", "digest": f"sha256:{agent_id}",
            "quantization": "Q4_K_M", "think": False}


def config(tmp_path, **override):
    base = {"run_id": "smoke_test", "runs_root": str(tmp_path), "temperature": 0, "seed": 42, "num_ctx": 8192,
            "num_predict": 4096, "git_commit": "c0ffee", "kg_fingerprint": "b" * 64, "biohopr_revision": "rev",
            "prompt_sha256": "p" * 64, "page_size": 50, "budget": 30, "tool_schema_sha256": "a" * 64,
            "source_sha256": {"x.py": "1" * 64}, "agent_inputs_sha256": "2" * 64, "timeout_seconds": 600,
            "request_timeout_seconds": 240}
    return base | override


def fake_record(query_id, ag, cfg, attempt=1, status="SUCCESS"):
    return make_episode_record(
        run_id=cfg["run_id"], query_id=query_id, agent_id=ag["agent_id"], attempt=attempt,
        model={k: ag[k] for k in ("tag", "digest", "quantization")}, temperature=cfg["temperature"],
        seed=cfg["seed"], num_ctx=cfg["num_ctx"], num_predict=cfg["num_predict"],
        prompt_version=f"{PROMPT_VERSION}:{cfg['prompt_sha256']}",
        tool_config={"tool_version": "T1", "page_size": cfg["page_size"], "budget": cfg["budget"],
                     "ordering_rule": "numeric-id", "tool_schema_sha256": cfg["tool_schema_sha256"],
                     "prompt_values": {"PAGE_SIZE": cfg["page_size"], "BUDGET": cfg["budget"]}},
        kg_fingerprint=cfg["kg_fingerprint"], biohopr_revision=cfg["biohopr_revision"],
        git_commit=cfg["git_commit"], timestamps={"started_at": "2026-11-07T00:00:00+00:00",
                                                  "finished_at": "2026-11-07T00:00:01+00:00"},
        messages=[{"role": "user", "content": "q"}], call_log=[], token_counts={"prompt": [1], "completion": [1]},
        raw_final_output='{"status": "no_answer", "answers": []}', status=status,
        cause="CONNECTION" if status == "ERROR" else None,
        log_events=[{"event": "EPISODE_CONFIG", "think": ag["think"], "draft_prompt": False,
                     **{k: cfg[k] for k in ("source_sha256", "agent_inputs_sha256", "timeout_seconds",
                                            "request_timeout_seconds")}}])


class FakeRunner:
    """Saves a real write-once record; can 'crash' (KeyboardInterrupt) before saving the Nth episode."""

    def __init__(self, crash_at=None, statuses=None):
        self.calls, self.crash_at, self.statuses = [], crash_at, statuses or {}

    def __call__(self, query_id, ag, cfg, attempt=1):
        self.calls.append((ag["agent_id"], query_id))
        if self.crash_at is not None and len(self.calls) == self.crash_at:
            raise KeyboardInterrupt("simulated Ctrl+C mid-episode")
        status = self.statuses.get((ag["agent_id"], query_id), "SUCCESS")
        save_episode_record(fake_record(query_id, ag, cfg, attempt, status), cfg["runs_root"])


def run_panel(tmp_path, runner, cfg):
    plan = pr.episode_plan(AGENTS, QUERIES)
    for agent_id in AGENTS:
        pr.run_agent_block(agent(agent_id), cfg, QUERIES, check=lambda: None,
                           on_episode=lambda q, r, new: pr.write_progress(
                               tmp_path / "progress.json", pr.progress(tmp_path, cfg["run_id"], plan)),
                           run_episode=runner)
    return plan


def saved_names(tmp_path, cfg):
    return sorted(p.name for p in (tmp_path / cfg["run_id"]).glob("*__*__a*.json"))


def test_plan_is_agent_major():
    assert pr.episode_plan(AGENTS, QUERIES) == [("A1", q) for q in QUERIES] + [("A2", q) for q in QUERIES]


def test_resume_after_simulated_crash_has_no_duplicates_and_nothing_missing(tmp_path):
    cfg = config(tmp_path)
    first = FakeRunner(crash_at=5, statuses={("A1", "BH2_00002"): "ERROR"})
    with pytest.raises(KeyboardInterrupt):
        run_panel(tmp_path, first, cfg)
    assert len(saved_names(tmp_path, cfg)) == 4  # A1 x 3 (one ERROR) + A2 first query
    progress = json.loads((tmp_path / "progress.json").read_text())
    assert progress["episodes_done"] == 4 and progress["episodes_total"] == 6
    assert progress["failures_so_far"] == 1 and progress["failures"][0]["status"] == "ERROR"
    second = FakeRunner()
    plan = run_panel(tmp_path, second, cfg)
    # Only the interrupted and the never-started episodes run; the ERROR episode is never rerun (§19).
    assert second.calls == [("A2", "BH2_00002"), ("A2", "BH2_00003")]
    check = completeness(plan, saved_names(tmp_path, cfg))
    assert check["pass"] and check["saved"] == 6 and not check["duplicates"] and not check["missing"]
    third = FakeRunner()
    run_panel(tmp_path, third, cfg)  # a completed run resumes to a no-op
    assert third.calls == []


def test_resume_refuses_records_from_a_different_configuration(tmp_path):
    cfg = config(tmp_path)
    run_panel(tmp_path, FakeRunner(), cfg)
    with pytest.raises(ValueError, match="git_commit"):
        run_panel(tmp_path, FakeRunner(), config(tmp_path, git_commit="other"))


def test_digest_mismatch_is_refused_before_any_episode(tmp_path):
    ag = agent("A1")
    with pytest.raises(pr.IdentityMismatch, match="digest"):
        pr.check_identity(ag, {**ag, "digest": "sha256:other", "capabilities": ["tools"]})
    with pytest.raises(pr.IdentityMismatch, match="tools"):
        pr.check_identity(ag, {**ag, "capabilities": ["completion"]})
    pr.check_identity(ag, {**ag, "capabilities": ["tools"]})
    runner = FakeRunner()

    def check():
        pr.check_identity(ag, {**ag, "digest": "sha256:other", "capabilities": ["tools"]})

    with pytest.raises(pr.IdentityMismatch):
        pr.run_agent_block(ag, config(tmp_path), QUERIES, check=check, on_episode=lambda *a: None,
                           run_episode=runner)
    assert runner.calls == [] and saved_names(tmp_path, config(tmp_path)) == []


def test_config_hash_mismatch_is_refused(tmp_path):
    (tmp_path / "sheet.jsonl").write_text("abc", encoding="utf-8")
    good = hashlib.sha256(b"abc").hexdigest()
    pr.check_hashes({"sheet.jsonl": good}, tmp_path)
    with pytest.raises(pr.IdentityMismatch, match="sheet.jsonl"):
        pr.check_hashes({"sheet.jsonl": "0" * 64}, tmp_path)


def test_records_are_write_once(tmp_path):
    cfg = config(tmp_path)
    ag = agent("A1")
    save_episode_record(fake_record("BH2_00001", ag, cfg), tmp_path)
    with pytest.raises(FileExistsError):
        save_episode_record(fake_record("BH2_00001", ag, cfg, status="ERROR"), tmp_path)
    with pytest.raises(FileExistsError):  # the real runner refuses before any model call
        real_run_episode("BH2_00001", ag, cfg)
    saved = json.loads(record_path(tmp_path, cfg["run_id"], "BH2_00001", "A1", 1).read_text())
    assert saved["status"] == "SUCCESS"


def test_rerun_plan_follows_section_19_routes():
    cfg = {"run_id": "r", "runs_root": "x"}
    records = [{"agent_id": "A1", "query_id": "BH2_00001", "attempt": 1, "status": "ERROR"},
               {"agent_id": "A1", "query_id": "BH2_00002", "attempt": 1, "status": "SUCCESS"},
               {"agent_id": "A2", "query_id": "BH2_00001", "attempt": 1, "status": "TIMEOUT"},
               {"agent_id": "A2", "query_id": "BH2_00001", "attempt": 2, "status": "SUCCESS"}]
    hold = pr.rerun_plan(records, "D6_HOLD", "2026-11-07 — D6 HOLD")
    assert hold["attempts"] == {("A1", "BH2_00001"): 2}  # A2's latest attempt succeeded
    d4 = pr.rerun_plan(records, "D4_FAIL", "2026-11-07 — D4 FAIL")
    assert d4["attempts"] == {("A1", "BH2_00001"): 2, ("A1", "BH2_00002"): 2, ("A2", "BH2_00001"): 3}
    with pytest.raises(ValueError, match="reason"):
        pr.rerun_plan(records, "LOOKS_BAD", "x")
    with pytest.raises(ValueError, match="decision-log"):
        pr.rerun_plan(records, "D6_HOLD", " ")
    assert cfg  # reruns are planned only; the caller supplies the new run ID


def test_completeness_flags_duplicates_missing_and_extra():
    plan = pr.episode_plan(AGENTS, QUERIES[:2])
    names = ["BH2_00001__A1__a1.json", "BH2_00001__A1__a2.json", "BH2_00002__A1__a1.json",
             "BH2_00001__A2__a1.json", "BH2_00009__A2__a1.json"]
    check = completeness(plan, names)
    assert not check["pass"]
    assert check["duplicates"] == [["A1", "BH2_00001"]]
    assert check["missing"] == [["A2", "BH2_00002"]] and check["extra"] == [["A2", "BH2_00009"]]


def answer(label_a, node="10"):
    return {"submitted_index": 0, "node_id": node, "label_a": label_a, "label_b": "SUPPORTED",
            "primary_path": [{"u": "1", "label": "r1", "v": "2"}, {"u": "2", "label": "r2", "v": node}]}


def mrow(agent_id, query_id, answers, status="SUCCESS"):
    return {"agent_id": agent_id, "query_id": query_id, "episode_status": status, "answers": answers}


def test_audit_selection_rule():
    queries = [f"BH2_{i:05d}" for i in range(1, 7)]
    order = sorted(queries, key=lambda q: audit_key(q, "A1"))
    rows = [mrow("A1", q, [answer("GOLD")]) for q in queries]
    rows[queries.index(order[3])]["answers"].append(answer("OFF_QUESTION", "99"))
    rows[queries.index(order[0])]["episode_status"] = "TIMEOUT"   # not SUCCESS: ineligible
    rows[queries.index(order[1])]["answers"] = []                 # no answer: ineligible
    rows += [mrow("A2", "BH2_00001", [answer("GOLD")]),             # A2: one eligible episode only
             mrow("A2", "BH2_00002", [], status="ERROR")]
    chosen = audit_selection(rows, ["A1", "A2"])
    # A1: first OFF_QUESTION episode in hash order, then the first eligible not already chosen.
    assert chosen == [("A1", order[3]), ("A1", order[2]), ("A2", "BH2_00001")]


def test_audit_selection_without_off_question_takes_first_two():
    queries = ["BH2_00001", "BH2_00002", "BH2_00003"]
    order = sorted(queries, key=lambda q: audit_key(q, "A1"))
    assert audit_selection([mrow("A1", q, [answer("GOLD")]) for q in queries], ["A1"]) == \
        [("A1", order[0]), ("A1", order[1])]


def test_audit_rows_one_per_answer_with_empty_researcher_columns():
    row = mrow("A1", "BH2_00001", [answer("GOLD"), {**answer("UNRESOLVED", None), "submitted_index": 1,
                                                     "label_b": "NOT_APPLICABLE", "primary_path": None}])
    record = {"query_id": "BH2_00001", "agent_id": "A1", "attempt": 1,
              "log_events": [{"event": "FINAL_PARSED", "parsed": {"answers": [{"id": "10"}, {"id": "abc"}]}}]}
    rows = audit_rows([("A1", "BH2_00001")], {("A1", "BH2_00001"): row}, {("A1", "BH2_00001"): record})
    assert [r["answer_id"] for r in rows] == ["10", "unresolved:abc"]
    assert rows[0]["primary_path"] == "1 -r1-> 2 ; 2 -r2-> 10" and rows[1]["primary_path"] == ""
    assert all(r["episode"] == "BH2_00001__A1__a1" and r["my_label_A"] == r["my_label_B"] == r["notes"] == ""
               for r in rows)
