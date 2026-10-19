"""S20 D3 aggregation: synthetic episodes, no network or model calls."""

import importlib.util
import json
from pathlib import Path
from types import SimpleNamespace
from unittest.mock import Mock

import pytest
import yaml

from cofail_kg.agents.trace import save_episode_record
from cofail_kg.evaluation.screening import aggregate_model, call_counts
from cofail_kg.kg.prepare import file_hash
from test_trace import record


IDENTITY = {"tag": "llama3.1:8b", "digest": "a" * 64, "quantization": "Q4_K_M",
            "parameter_size": "8.0B", "family": "Llama"}


def episode(i=0, **changes):
    return record([], query_id=f"Q{i}", model={k: IDENTITY[k] for k in
                  ("tag", "digest", "quantization")}, **changes)


def metrics(valid=True, used=4):
    return {"answers": [{"label_a": "GOLD", "label_b": "SUPPORTED"}] if valid else [],
            "tool_calls_used": used, "budget_exhausted": used >= 30}


def native(name="inspect_entity", arguments=None):
    return {"function": {"name": name, "arguments": {"entity_id": "1"}
                        if arguments is None else arguments}}


def test_call_count_uses_native_messages_even_when_not_executed_and_includes_text():
    calls = [native(), native("missing"), native(arguments={"entity_id": 1}),
             native("get_neighbors", {"entity_id": "1", "relation": "r", "page": True}),
             native("get_neighbors", '{"entity_id":"1","relation":"r","page":2}'),
             native("get_neighbors", {"entity_id": "1", "relation": "r", "neighbor_type": None}),
             native(arguments="broken"), native(arguments={"extra": "missing required"})]
    rec = episode(messages=[{"role": "assistant", "tool_calls": calls}],
                  ignored_tool_calls=[calls[0]], log_events=[{"event": "TEXT_TOOL_CALL"}])
    assert call_counts(rec) == {"native_calls": 8, "text_tool_calls": 1,
                                "attempted_calls": 9, "well_formed_calls": 2}


def test_argument_extras_do_not_invent_additional_properties_restriction():
    rec = episode(messages=[{"role": "assistant", "tool_calls": [
        native(arguments={"entity_id": "1", "extra": 5})]}])
    assert call_counts(rec)["well_formed_calls"] == 1


@pytest.mark.parametrize("function", [None, [], {"name": []}, {"name": {}}, {}])
def test_malformed_native_functions_are_attempts_not_well_formed_calls(function):
    rec = episode(messages=[{"role": "assistant", "tool_calls": [{"function": function}]}])
    assert call_counts(rec)["attempted_calls"] == 1
    assert call_counts(rec)["well_formed_calls"] == 0


def sample(n=20):
    records = [episode(i, messages=[{"role": "assistant", "tool_calls": [native()]}])
               for i in range(n)]
    rows = [metrics(i < 8) for i in range(n)]
    return records, rows


def test_d3_exact_boundaries_and_final_status_denominator():
    records, rows = sample()
    for i in (18, 19):
        records[i] = episode(i, status="PARSE_FAIL", messages=[
            {"role": "assistant", "tool_calls": [native("missing")]}])
        rows[i] = metrics(False)
    for rec in records:
        rec["timestamps"]["finished_at"] = "2026-10-15T00:05:00+00:00"
    result = aggregate_model(records, rows, IDENTITY)
    assert result["success_rate"] == .9
    assert result["competence"] == .4
    assert result["well_formed_rate"] == .9
    assert result["median_wall_seconds"] == 300
    assert result["d3_pass"] is True


@pytest.mark.parametrize("criterion", ["calls", "success", "competence", "time", "oom"])
def test_each_d3_criterion_can_fail_independently(criterion):
    records, rows = sample()
    if criterion == "calls":
        for rec in records[:3]:
            rec["messages"][0]["tool_calls"] = [native("missing")]
    elif criterion == "success":
        for rec in records[-3:]:
            rec["status"] = "PARSE_FAIL"
    elif criterion == "competence":
        rows[7] = metrics(False)
    elif criterion == "time":
        for rec in records:
            rec["timestamps"]["finished_at"] = "2026-10-15T00:05:01+00:00"
    else:
        records[-1].update(status="ERROR", cause="OUT_OF_MEMORY")
    assert aggregate_model(records, rows, IDENTITY)["d3_pass"] is False


def test_competence_requires_valid_supported_answer_and_success():
    records, rows = sample(4)
    rows[0]["answers"][0].update(label_a="OFF_QUESTION")
    rows[1]["answers"][0].update(label_b="UNGROUNDED")
    records[2].update(status="ERROR", cause="RUNTIME")
    result = aggregate_model(records, rows, IDENTITY)
    assert result["competent_episodes"] == 1 and result["competence"] == .25


def test_partial_table_reports_observations_without_gate_verdict():
    records, rows = sample(1)
    result = aggregate_model(records, rows, IDENTITY)
    assert result["episodes_completed"] == 1 and result["episodes_expected"] == 20
    assert result["complete"] is False and result["d3_pass"] is None
    assert result["pass_success"] is None


def test_missing_counts_remain_undefined_and_budget_stats_use_all_episodes():
    records, rows = sample(2)
    records[0]["token_counts"] = {"prompt": [None], "completion": []}
    records[1]["token_counts"] = {"prompt": [], "completion": []}
    for rec in records:
        rec["messages"] = []
    rows[0] = metrics(used=30)
    result = aggregate_model(records, rows, IDENTITY)
    assert result["largest_prompt_eval_count"] is None
    assert result["well_formed_rate"] is None
    assert result["budget_hit_share"] == .5 and result["median_tool_calls"] == 17


def test_call_rate_is_ratio_of_pooled_counts_not_mean_episode_ratio():
    records, rows = sample(2)
    records[0]["messages"][0]["tool_calls"] = [native()] * 10
    records[1]["messages"][0]["tool_calls"] = [native("missing")]
    assert aggregate_model(records, rows, IDENTITY)["well_formed_rate"] == 10 / 11


def test_complete_set_with_no_attempts_does_not_pass_vacuously():
    records, rows = sample()
    for rec in records:
        rec["messages"] = []
    result = aggregate_model(records, rows, IDENTITY)
    assert result["well_formed_rate"] is None and result["d3_pass"] is False


@pytest.mark.parametrize("problem", ["duplicate", "identity", "length", "negative_time"])
def test_bad_aggregation_inputs_fail_visibly(problem):
    records, rows = sample(2)
    if problem == "duplicate":
        records[1]["query_id"] = records[0]["query_id"]
    elif problem == "identity":
        records[1]["model"]["digest"] = "different"
    elif problem == "length":
        rows.pop()
    else:
        records[0]["timestamps"]["finished_at"] = "2026-10-14T00:00:00+00:00"
    with pytest.raises(ValueError):
        aggregate_model(records, rows, IDENTITY)


@pytest.fixture
def launcher():
    path = Path(__file__).parents[1] / "scripts/20_screen_models.py"
    spec = importlib.util.spec_from_file_location("s20_launcher", path)
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


@pytest.mark.parametrize("status,cause", [("SUCCESS", None), ("PARSE_FAIL", None),
                                        ("TIMEOUT", None), ("ERROR", "CONNECTION")])
def test_resume_skips_every_final_status_and_preserves_manifest_order(launcher, tmp_path, status, cause):
    agent = IDENTITY | {"agent_id": "A1", "think": False}
    config = {"runs_root": str(tmp_path), "run_id": "run-test", "temperature": 0, "seed": 42,
              "num_ctx": 8192, "num_predict": 4096, "page_size": 50, "budget": 30,
              "git_commit": "commit-test", "source_sha256": {}, "agent_inputs_sha256": "b" * 64,
              "prompt_sha256": "a" * 64, "tool_schema_sha256": "a" * 64,
              "kg_fingerprint": "b" * 64, "biohopr_revision": "rev-test",
              "timeout_seconds": 600, "request_timeout_seconds": 120}

    def saved(query_id, status="SUCCESS", cause=None):
        return save_episode_record(record([], query_id=query_id, agent_id="A1",
            model={k: agent[k] for k in ("tag", "digest", "quantization")}, status=status, cause=cause,
            prompt_version="P1:" + "a" * 64, log_events=[{"event": "EPISODE_CONFIG", "think": False,
                "agent_inputs_sha256": "b" * 64, "source_sha256": {},
                "timeout_seconds": 600, "request_timeout_seconds": 120}]), tmp_path)

    first = saved("Q0", status, cause)
    original = first.read_bytes()
    launcher.run_episode = Mock(side_effect=lambda q, a, c: saved(q))
    check = Mock()
    launcher.run_screening(agent, config, ["Q0", "Q1", "Q2"], max_new=1, check_identity=check)
    assert [c.args[0] for c in launcher.run_episode.call_args_list] == ["Q1"]
    assert first.read_bytes() == original
    launcher.run_episode.reset_mock()
    launcher.run_screening(agent, config, ["Q0", "Q1", "Q2"], max_new=0, check_identity=check)
    launcher.run_episode.assert_not_called()


def test_write_once_manifest_refuses_changed_configuration(launcher, tmp_path):
    path = tmp_path / "manifest.json"
    launcher.pin_manifest(path, {"num_ctx": 8192})
    original = path.read_bytes()
    launcher.pin_manifest(path, {"num_ctx": 8192})
    with pytest.raises(ValueError, match="manifest"):
        launcher.pin_manifest(path, {"num_ctx": 16384})
    assert path.read_bytes() == original


@pytest.fixture
def prepared(launcher, tmp_path, monkeypatch):
    monkeypatch.setattr(launcher, "ROOT", tmp_path)
    sheet = "".join(json.dumps({"query_id": f"Q{i}", "question_text": "q",
                   "start_id": "1", "start_name": "one"}) + "\n" for i in range(20))
    files = {"data/agent_inputs/screening.jsonl": sheet,
             "data/processed/manifests/screening.jsonl": sheet,
             "data/cache/primekg_metadata.json": "{}",
             "src/cofail_kg/agents/tool_schemas.py": "# synthetic T1\n",
             "results/semantics/relation_mapping.json": "{}",
             "scripts/20_screen_models.py": "# fixture launcher\n",
             "docs/frozen_pilot_protocol.md": "# fixture protocol\n",
             "docs/decision_rules.md": "# fixture gates\n",
             "data/processed/reference_queries.parquet": "fixture queries",
             "data/processed/reference_targets.parquet": "fixture targets",
             "data/processed/primary_population.csv": "query_id,status\n",
             "data/processed/reference_summary.json": "{}",
             "configs/ollama.yaml": "base_url: http://127.0.0.1:11434\nrequest_timeout_seconds: 120\nthink: true\n"}
    for name, text in files.items():
        path = tmp_path / name
        path.parent.mkdir(parents=True, exist_ok=True)
        path.write_text(text, encoding="utf-8")
    frozen = {"manifests": {p: file_hash(tmp_path / p) for p in files if p.endswith(".jsonl")},
              "kg_fingerprint": file_hash(tmp_path / "data/cache/primekg_metadata.json"),
              "tools": file_hash(tmp_path / "src/cofail_kg/agents/tool_schemas.py"),
              "relation_mapping": file_hash(tmp_path / "results/semantics/relation_mapping.json"),
              "biohopr_revision": "fixture-revision", "prompt": launcher.prompt_sha256()}
    (tmp_path / "configs/frozen_hashes.yaml").write_text(yaml.safe_dump(frozen), encoding="utf-8")
    identity = {k: v for k, v in IDENTITY.items() if k != "family"} | {"capabilities": ["tools"]}
    client = Mock()
    client.get_model_identity.return_value = identity
    monkeypatch.setattr(launcher, "OllamaClient", Mock(return_value=client))
    monkeypatch.setattr(launcher.subprocess, "check_output", Mock(side_effect=lambda command, **kw:
                        "fixture-commit\n" if "rev-parse" in command else " M dirty\n"))
    args = SimpleNamespace(run_id="s20-fixture", model=IDENTITY["tag"], agent_id="Llama",
                           family="Llama", expected_digest=IDENTITY["digest"], max_new=1)
    return launcher, tmp_path, args, client


def test_preparation_ignores_old_diagnostic_thinking_and_pins_frozen_settings(prepared):
    module, root, args, _ = prepared
    agent, config, queries, _ = module.prepare_run(args)
    assert agent["think"] is False
    assert {k: config[k] for k in module.SETTINGS} == module.SETTINGS
    assert len(queries) == 20 and queries[:2] == ["Q0", "Q1"]
    assert config["prompt_sha256"] == module.prompt_sha256()
    assert config["source_sha256"]["scripts/20_screen_models.py"] == file_hash(root / "scripts/20_screen_models.py")
    assert "S14" not in agent["agent_id"]


@pytest.mark.parametrize("input_path", ["data/agent_inputs/screening.jsonl",
    "data/processed/manifests/screening.jsonl", "data/cache/primekg_metadata.json",
    "src/cofail_kg/agents/tool_schemas.py", "results/semantics/relation_mapping.json"])
def test_changed_frozen_input_stops_before_model_contact(prepared, input_path):
    module, root, args, client = prepared
    (root / input_path).write_text("changed", encoding="utf-8")
    with pytest.raises(ValueError, match="Frozen"):
        module.prepare_run(args)
    client.get_model_identity.assert_not_called()


def test_wrong_digest_stops_before_creating_run_manifest(prepared):
    module, root, args, _ = prepared
    args.expected_digest = "wrong"
    with pytest.raises(ValueError, match="tag/digest"):
        module.prepare_run(args)
    assert not (root / "results/runs/screening").exists()


def test_changed_source_cannot_silently_resume_existing_run(prepared):
    module, root, args, _ = prepared
    module.prepare_run(args)
    (root / "scripts/20_screen_models.py").write_text("changed", encoding="utf-8")
    with pytest.raises(ValueError, match="manifest"):
        module.prepare_run(args)


def test_report_only_preparation_works_without_contacting_ollama(prepared):
    module, _, args, client = prepared
    module.prepare_run(args)
    client.get_model_identity.reset_mock()
    args.max_new = 0
    module.prepare_run(args)
    client.get_model_identity.assert_not_called()


def test_failed_manifest_serialization_leaves_no_partial_file(launcher, tmp_path):
    with pytest.raises(ValueError):
        launcher.pin_manifest(tmp_path / "manifest.json", {"bad": float("nan")})
    assert list(tmp_path.iterdir()) == []


def test_report_rejects_source_drift_before_loading_evaluator(prepared, monkeypatch):
    module, root, args, _ = prepared
    module.prepare_run(args)
    monkeypatch.setattr(module, "load_evaluator", Mock())
    (root / "data/processed/reference_queries.parquet").write_text("changed", encoding="utf-8")
    with pytest.raises(ValueError, match="Pinned"):
        module.report_screening()
    module.load_evaluator.assert_not_called()


@pytest.mark.parametrize("field,value", [("num_ctx", 16384), ("git_commit", "other"),
                                       ("agent_id", "S14-qwen3-4b"), ("query_id", "Q9")])
def test_mismatched_saved_record_stops_before_any_new_inference(prepared, monkeypatch, field, value):
    module, _, args, _ = prepared
    agent, config, queries, _ = module.prepare_run(args)
    override = {k: config[k] for k in ("run_id", "temperature", "seed", "num_ctx", "num_predict",
                                     "git_commit", "kg_fingerprint", "biohopr_revision")}
    rec = record([], **override, query_id="Q1", agent_id=agent["agent_id"],
                 model={k: agent[k] for k in ("tag", "digest", "quantization")},
                 tool_config={"tool_version": "T1", "page_size": 50, "budget": 30,
                              "ordering_rule": "numeric-id", "tool_schema_sha256": config["tool_schema_sha256"],
                              "prompt_values": {"PAGE_SIZE": 50, "BUDGET": 30}},
                 prompt_version="P1:" + config["prompt_sha256"], log_events=[{
                     "event": "EPISODE_CONFIG", "think": False, **{k: config[k] for k in
                     ("source_sha256", "agent_inputs_sha256", "timeout_seconds", "request_timeout_seconds")}}])
    path = save_episode_record(rec, config["runs_root"])
    tampered = json.loads(path.read_text(encoding="utf-8"))
    tampered[field] = value
    path.write_text(json.dumps(tampered), encoding="utf-8")
    monkeypatch.setattr(module, "run_episode", Mock())
    with pytest.raises(ValueError):
        module.run_screening(agent, config, queries, max_new=1, check_identity=Mock())
    module.run_episode.assert_not_called()
