"""S14 launcher checks use a mocked model and the real S12 saver."""

import importlib.util
import json
from pathlib import Path
from unittest.mock import Mock

import pytest
import yaml

from cofail_kg.agents.trace import save_episode_record
from cofail_kg.kg.prepare import file_hash
from test_trace import record


@pytest.fixture
def launcher(tmp_path, monkeypatch):
    source = Path(__file__).parents[1] / "scripts/14_run_episode.py"
    spec = importlib.util.spec_from_file_location("s14_launcher", source)
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    monkeypatch.setattr(module, "ROOT", tmp_path)
    files = {
        "data/agent_inputs/screening.jsonl": json.dumps({"query_id": "Q1", "question_text": "q",
                                                       "start_id": "1", "start_name": "one"}) + "\n",
        "data/cache/primekg_metadata.json": "{}",
        "src/cofail_kg/agents/tool_schemas.py": "# synthetic T1\n",
        "scripts/14_run_episode.py": source.read_text(encoding="utf-8"),
        "configs/ollama.yaml": "base_url: http://127.0.0.1:11434\nrequest_timeout_seconds: 120\nthink: true\n",
    }
    for name, content in files.items():
        path = tmp_path / name
        path.parent.mkdir(parents=True, exist_ok=True)
        path.write_text(content, encoding="utf-8")
    frozen = {"kg_fingerprint": file_hash(tmp_path / "data/cache/primekg_metadata.json"),
              "biohopr_revision": "test-revision",
              "tools": file_hash(tmp_path / "src/cofail_kg/agents/tool_schemas.py"),
              "manifests": {"data/agent_inputs/screening.jsonl": file_hash(
                  tmp_path / "data/agent_inputs/screening.jsonl")}}
    (tmp_path / "configs/frozen_hashes.yaml").write_text(yaml.safe_dump(frozen))
    (tmp_path / "results/diagnostics").mkdir(parents=True)
    identity = {"tag": "qwen3:4b", "digest": "test-digest", "quantization": "Q4_K_M",
                "capabilities": ["tools"]}
    client = Mock()
    client.get_model_identity.return_value = identity
    monkeypatch.setattr(module, "OllamaClient", Mock(return_value=client))
    monkeypatch.setattr(module.subprocess, "check_output", Mock(side_effect=["commit-test\n", " M dirty\n"]))

    def run(query_id, agent, config):
        rec = record([], run_id=config["run_id"], query_id=query_id, agent_id=agent["agent_id"])
        return save_episode_record(rec, config["runs_root"])

    monkeypatch.setattr(module, "run_episode", Mock(side_effect=run))
    return module, tmp_path, client


def test_launcher_passes_explicit_settings_and_refuses_completed_run(launcher):
    module, root, _ = launcher
    assert module.main(["--run-id", "s14-test", "--think", "false"]) == 0
    query, agent, config = module.run_episode.call_args.args
    assert query == "Q1" and agent["think"] is False
    assert {key: config[key] for key in ("num_ctx", "num_predict", "page_size", "budget", "timeout_seconds")} == {
        "num_ctx": 8192, "num_predict": 4096, "page_size": 50, "budget": 30, "timeout_seconds": 600}
    assert config["draft_prompt"] is True and config["git_commit"] == "commit-test-dirty"
    assert config["source_sha256"]["src/cofail_kg/agents/tool_schemas.py"] == config["tool_schema_sha256"]
    assert json.loads((root / "results/diagnostics/s14-test_identity.json").read_text())["identity_stable"]
    with pytest.raises(FileExistsError):
        module.main(["--run-id", "s14-test", "--think", "false"])
    assert module.run_episode.call_count == 1


def test_launcher_rejects_changed_sheet_before_model_call(launcher):
    module, root, _ = launcher
    (root / "data/agent_inputs/screening.jsonl").write_text("changed")
    with pytest.raises(ValueError, match="frozen hash"):
        module.main(["--run-id", "s14-test", "--think", "true"])
    module.OllamaClient.assert_not_called()
    module.run_episode.assert_not_called()


@pytest.mark.parametrize("error", [PermissionError("blocked"), OSError("disk full")])
def test_launcher_stops_on_blocked_persistence_before_model_call(launcher, monkeypatch, error):
    module, _, _ = launcher
    monkeypatch.setattr(module, "check_persistence", Mock(side_effect=error))
    with pytest.raises(RuntimeError, match="persistence is blocked"):
        module.main(["--run-id", "s14-test", "--think", "true"])
    module.OllamaClient.assert_not_called()
    module.run_episode.assert_not_called()


def test_preflight_rejects_an_operation_that_overwrites(launcher, monkeypatch):
    module, root, _ = launcher
    monkeypatch.setattr(module, "publish_once", lambda source, target: target.write_bytes(source.read_bytes()))
    with pytest.raises(RuntimeError, match="not refused"):
        module.check_persistence(root / "results/runs")
    assert list((root / "results/runs").iterdir()) == []


def test_launcher_reports_changed_identity_and_keeps_record(launcher):
    module, root, client = launcher
    identity = client.get_model_identity.return_value
    client.get_model_identity.side_effect = [identity, identity | {"digest": "changed"}]
    assert module.main(["--run-id", "s14-test", "--think", "true"]) == 1
    evidence = json.loads((root / "results/diagnostics/s14-test_identity.json").read_text())
    assert evidence["identity_stable"] is False
    assert Path(evidence["record_path"]).is_file()


def test_diagnostic_output_limit_is_explicit_and_passed_to_runner(launcher):
    module, _, _ = launcher
    assert module.main(["--run-id", "s14-output-test", "--think", "false",
                        "--diagnostic-num-predict", "6144"]) == 0
    _, agent, config = module.run_episode.call_args.args
    assert agent["think"] is False
    assert config["num_predict"] == 6144 and config["num_ctx"] == 8192


def test_diagnostic_model_identity_is_used_and_checked_after_run(launcher):
    module, root, client = launcher
    tag = "cofail-qwen3:4b-templatefix"
    identity = client.get_model_identity.return_value | {"tag": tag, "digest": "variant-digest"}
    client.get_model_identity.return_value = identity
    assert module.main(["--run-id", "s14-template-test", "--think", "false",
                        "--diagnostic-model", tag]) == 0
    assert [call.args for call in client.get_model_identity.call_args_list] == [(tag,), (tag,)]
    _, agent, _ = module.run_episode.call_args.args
    assert agent["tag"] == tag and agent["digest"] == "variant-digest"
    evidence = json.loads((root / "results/diagnostics/s14-template-test_identity.json").read_text())
    assert evidence["identity_before"] == evidence["identity_after"] == identity


@pytest.mark.parametrize("value", ["0", "-1"])
def test_diagnostic_output_limit_rejects_nonpositive_values(launcher, value):
    module, _, _ = launcher
    with pytest.raises(SystemExit) as error:
        module.main(["--run-id", "s14-output-test", "--think", "false",
                     "--diagnostic-num-predict", value])
    assert error.value.code == 2
    module.OllamaClient.assert_not_called()
