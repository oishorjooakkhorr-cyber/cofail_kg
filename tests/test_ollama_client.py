"""S13 HTTP contract and protocol §9.5 error/retry tests; no live model required."""

from copy import deepcopy
from unittest.mock import Mock

import pytest
import requests

from cofail_kg.agents.ollama_client import OllamaClient, OllamaError


OPTIONS = {"temperature": 0, "seed": 42, "num_ctx": 8192, "num_predict": 4096}
MESSAGES = [{"role": "user", "content": "Use add for 2 + 3."}]
TOOLS = [{"type": "function", "function": {"name": "add"}}]
CALL = {"function": {"name": "add", "arguments": {"a": 2, "b": 3}}}


def response(payload, status=200, text=None):
    result = Mock(status_code=status, text=text or str(payload))
    result.json.return_value = payload
    return result


@pytest.fixture
def http(monkeypatch):
    request = Mock()
    monkeypatch.setattr(requests, "request", request)
    return request


def reply(**overrides):
    return {"message": {"role": "assistant", "content": "", "tool_calls": [CALL]},
            "done": True, "prompt_eval_count": 22, "eval_count": 8, **overrides}


@pytest.mark.parametrize("think", [True, False])
def test_chat_preserves_raw_message_native_calls_and_explicit_options(http, monkeypatch, think):
    raw = reply(extra="keep this", message={"role": "assistant", "content": "",
                                           "thinking": "synthetic reasoning", "tool_calls": [CALL]})
    http.return_value = response(raw)
    ticks = iter([10.0, 10.25])
    monkeypatch.setattr("cofail_kg.agents.ollama_client.time.perf_counter", lambda: next(ticks))
    original = deepcopy((MESSAGES, TOOLS, OPTIONS))
    result = OllamaClient(think=think, timeout_seconds=7).chat("tiny:latest", MESSAGES, TOOLS, OPTIONS)
    http.assert_called_once_with(
        "POST", "http://127.0.0.1:11434/api/chat", timeout=7,
        json={"model": "tiny:latest", "messages": MESSAGES, "tools": TOOLS,
              "options": OPTIONS, "stream": False, "think": think})
    assert result == {"raw_response": raw, "message": raw["message"], "tool_calls": [CALL],
                      "prompt_eval_count": 22, "eval_count": 8, "latency_seconds": .25}
    assert (MESSAGES, TOOLS, OPTIONS) == original
    assert result["raw_response"]["message"]["thinking"] == "synthetic reasoning"


def test_think_cannot_be_omitted():
    with pytest.raises(TypeError, match="think"):
        OllamaClient(timeout_seconds=7)


@pytest.mark.parametrize("think", [None, "true", 0, 1])
def test_think_must_be_explicit_boolean(think):
    with pytest.raises(ValueError, match="think"):
        OllamaClient(think=think, timeout_seconds=7)


def test_plain_text_is_never_executed_or_retried(http):
    raw = reply(message={"role": "assistant", "content": 'add(2, 3); out of memory'})
    http.return_value = response(raw)
    result = OllamaClient(think=True, timeout_seconds=7).chat("tiny", MESSAGES, [], OPTIONS)
    assert result["tool_calls"] == []
    assert result["message"] == raw["message"]
    assert http.call_count == 1


@pytest.mark.parametrize("missing", OPTIONS)
def test_all_four_generation_options_required_before_http(http, missing):
    with pytest.raises(ValueError, match=missing):
        OllamaClient(think=True, timeout_seconds=7).chat("tiny", MESSAGES, [],
                                           {k: v for k, v in OPTIONS.items() if k != missing})
    http.assert_not_called()


@pytest.mark.parametrize("timeout", [0, -1, True, float("nan"), float("inf"), "7"])
def test_timeout_must_be_finite_positive_number(timeout):
    with pytest.raises(ValueError, match="timeout"):
        OllamaClient(think=True, timeout_seconds=timeout)


def test_connection_errors_get_exactly_two_logged_retries(http, caplog):
    http.side_effect = requests.ConnectionError("connection refused")
    with pytest.raises(OllamaError) as error:
        OllamaClient(think=True, timeout_seconds=7).chat("tiny", MESSAGES, [], OPTIONS)
    assert error.value.cause == "CONNECTION"
    assert http.call_count == 3
    assert "retry 1/2" in caplog.text and "retry 2/2" in caplog.text
    assert "connection refused" in caplog.text


def test_connection_retry_can_recover(http):
    http.side_effect = [requests.ConnectionError("reset"), response(reply())]
    assert OllamaClient(think=True, timeout_seconds=7).chat("tiny", MESSAGES, [], OPTIONS)["eval_count"] == 8
    assert http.call_count == 2


@pytest.mark.parametrize("exception,cause", [
    (requests.ReadTimeout("read timed out"), "CONNECTION"),
    (requests.ConnectTimeout("connect timed out"), "CONNECTION"),
    (requests.RequestException("bad transport"), "OTHER"),
])
def test_non_connection_exceptions_are_not_retried(http, exception, cause):
    http.side_effect = exception
    with pytest.raises(OllamaError) as error:
        OllamaClient(think=True, timeout_seconds=7).chat("tiny", MESSAGES, [], OPTIONS)
    assert error.value.cause == cause
    assert http.call_count == 1


@pytest.mark.parametrize("message,cause", [
    ("CUDA out of memory", "OUT_OF_MEMORY"),
    ("model requires more system memory (5 GiB) than is available (3 GiB)", "OUT_OF_MEMORY"),
    ("unable to allocate CUDA buffer", "OUT_OF_MEMORY"),
    ("cudaMalloc failed", "OUT_OF_MEMORY"),
    ("model not found", "RUNTIME"),
    ("runner process exited", "RUNTIME"),
    ("busy", "RUNTIME"),
])
def test_server_error_causes_preserve_response_and_never_retry(http, message, cause):
    http.return_value = response({"error": message}, 500)
    with pytest.raises(OllamaError) as error:
        OllamaClient(think=True, timeout_seconds=7).chat("tiny", MESSAGES, [], OPTIONS)
    assert error.value.cause == cause
    assert error.value.status_code == 500
    assert message in error.value.response_text
    assert http.call_count == 1


def test_error_object_even_on_200_is_runtime_failure(http):
    http.return_value = response({"error": "runner failed"})
    with pytest.raises(OllamaError, match="runner failed") as error:
        OllamaClient(think=True, timeout_seconds=7).chat("tiny", MESSAGES, [], OPTIONS)
    assert error.value.cause == "RUNTIME"
    assert http.call_count == 1


@pytest.mark.parametrize("status,cause", [(200, "OTHER"), (502, "RUNTIME")])
def test_non_json_reply_is_not_retried(http, status, cause):
    http.return_value = response(None, status, text="bad gateway")
    http.return_value.json.side_effect = ValueError("invalid JSON")
    with pytest.raises(OllamaError) as error:
        OllamaClient(think=True, timeout_seconds=7).chat("tiny", MESSAGES, [], OPTIONS)
    assert error.value.cause == cause
    assert error.value.response_text == "bad gateway"
    assert http.call_count == 1


@pytest.mark.parametrize("raw", [[], {}, reply(done=False), reply(message="bad"),
                                     reply(message={"role": "user"}),
                                     reply(message={"role": "assistant", "tool_calls": "bad"}),
                                     reply(prompt_eval_count=-1), reply(eval_count=True)])
def test_invalid_envelopes_are_other_not_model_parse_fail(http, raw):
    http.return_value = response(raw)
    with pytest.raises(OllamaError) as error:
        OllamaClient(think=True, timeout_seconds=7).chat("tiny", MESSAGES, [], OPTIONS)
    assert error.value.cause == "OTHER"
    assert http.call_count == 1


def test_absent_token_counts_remain_unknown(http):
    raw = reply()
    del raw["prompt_eval_count"], raw["eval_count"]
    http.return_value = response(raw)
    result = OllamaClient(think=True, timeout_seconds=7).chat("tiny", MESSAGES, [], OPTIONS)
    assert result["prompt_eval_count"] is None and result["eval_count"] is None


def identity_responses():
    return [response({"models": [
        {"name": "unrelated:latest", "digest": "wrong"},
        {"name": "tiny:latest", "digest": "abc123"}]}),
        response({"details": {"quantization_level": "Q4_K_M", "parameter_size": "1B"},
                  "capabilities": ["completion", "tools"]})]


def test_identity_uses_exact_tag_and_show_metadata(http):
    http.side_effect = identity_responses()
    result = OllamaClient(think=True, timeout_seconds=7).get_model_identity("tiny")
    assert result == {"tag": "tiny:latest", "digest": "abc123", "quantization": "Q4_K_M",
                      "parameter_size": "1B", "capabilities": ["completion", "tools"]}
    assert http.call_args_list[0].args == ("GET", "http://127.0.0.1:11434/api/tags")
    assert http.call_args_list[1].kwargs["json"] == {"model": "tiny:latest"}


def test_missing_model_does_not_choose_another(http):
    http.side_effect = identity_responses()
    with pytest.raises(OllamaError) as error:
        OllamaClient(think=True, timeout_seconds=7).get_model_identity("tin")
    assert error.value.cause == "RUNTIME"
    assert http.call_count == 1


def test_missing_identity_metadata_fails_instead_of_inventing_values(http):
    responses = identity_responses()
    responses[1] = response({"details": {}})
    http.side_effect = responses
    with pytest.raises(OllamaError) as error:
        OllamaClient(think=True, timeout_seconds=7).get_model_identity("tiny")
    assert error.value.cause == "OTHER"
