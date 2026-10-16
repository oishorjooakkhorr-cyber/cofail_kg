"""S13 diagnostic script checks with a fake client."""

import importlib.util
import json
from pathlib import Path
from unittest.mock import Mock

import pytest

from cofail_kg.agents.ollama_client import OllamaError


@pytest.fixture
def script(monkeypatch):
    path = Path(__file__).parents[1] / "scripts/13_test_ollama.py"
    spec = importlib.util.spec_from_file_location("test_s13_script", path)
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    client = Mock()
    client.get_model_identity.return_value = {"tag": "qwen3:4b", "digest": "abc",
                                             "capabilities": ["tools"]}
    plain = {"raw_response": {}, "message": {"content": "hello"}, "tool_calls": [],
             "prompt_eval_count": 8, "eval_count": 1, "latency_seconds": .1}
    tool = plain | {"tool_calls": [{"function": {"name": "add", "arguments": {"a": 2, "b": 3}}}]}
    client.chat.side_effect = [plain, tool]
    monkeypatch.setattr(module, "OllamaClient", Mock(return_value=client))
    return module, client


def test_script_sends_exactly_two_calls_and_preserves_evidence(script, tmp_path, capsys):
    module, client = script
    output = tmp_path / "evidence.json"
    assert module.main(["--output", str(output)]) == 0
    report = json.loads(capsys.readouterr().out)
    assert json.loads(output.read_text()) == report
    assert report["native_tool_call"] is True
    assert report["identity_before"] == report["identity_after"]
    assert client.chat.call_count == 2
    first, second = client.chat.call_args_list
    assert first.args[2] == []
    assert second.args[2][0]["function"]["name"] == "add"
    assert second.args[3] == {"temperature": 0, "seed": 42, "num_ctx": 8192, "num_predict": 4096}
    assert module.OllamaClient.call_args.kwargs["timeout_seconds"] == 120
    assert module.OllamaClient.call_args.kwargs["think"] is True
    assert report["transport"]["think"] is True


def test_think_false_is_loaded_from_configuration(script, tmp_path, capsys):
    module, _ = script
    config = tmp_path / "ollama.yaml"
    config.write_text("base_url: http://127.0.0.1:11434\nrequest_timeout_seconds: 120\nthink: false\n")
    assert module.main(["--config", str(config)]) == 0
    assert module.OllamaClient.call_args.kwargs["think"] is False
    assert json.loads(capsys.readouterr().out)["transport"]["think"] is False


def test_missing_native_call_is_reported_without_retry(script, capsys):
    module, client = script
    result = {"tool_calls": [], "prompt_eval_count": 1, "eval_count": 2, "latency_seconds": .1}
    client.chat.side_effect = [result, result]
    assert module.main([]) == 1
    assert json.loads(capsys.readouterr().out)["native_tool_call"] is False
    assert client.chat.call_count == 2


def test_failure_keeps_plain_result_and_error_details(script, capsys):
    module, client = script
    client.chat.side_effect = [{"tool_calls": []}, OllamaError(
        "OUT_OF_MEMORY", "out of memory", status_code=500, response_text='{"error":"out of memory"}')]
    assert module.main([]) == 1
    report = json.loads(capsys.readouterr().out)
    assert report["plain"] == {"tool_calls": []}
    assert report["error"]["cause"] == "OUT_OF_MEMORY"
    assert report["error"]["status_code"] == 500


def test_does_not_run_model_without_tools_capability(script, capsys):
    module, client = script
    client.get_model_identity.return_value = {"capabilities": []}
    assert module.main([]) == 1
    assert "tools" in json.loads(capsys.readouterr().out)["error"]["message"]
    client.chat.assert_not_called()


def test_evidence_file_is_never_overwritten(script, tmp_path):
    module, client = script
    output = tmp_path / "exists.json"
    output.write_text("keep")
    with pytest.raises(FileExistsError):
        module.main(["--output", str(output)])
    assert output.read_text() == "keep"
    client.chat.assert_not_called()


def test_model_identity_change_fails_verification(script, capsys):
    module, client = script
    client.get_model_identity.side_effect = [
        {"tag": "qwen3:4b", "digest": "a", "capabilities": ["tools"]},
        {"tag": "qwen3:4b", "digest": "b", "capabilities": ["tools"]}]
    assert module.main([]) == 1
    assert "identity changed" in json.loads(capsys.readouterr().out)["error"]["message"]
