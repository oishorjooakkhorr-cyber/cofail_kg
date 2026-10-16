"""Thin local HTTP client (protocol §9.1, §9.5, §19).

Uses Ollama /api/chat (stream=false), /api/tags and /api/show. Preserves the
complete parsed JSON and assistant message, including thinking/native calls.
No final-answer parsing, text-tool execution or content-based retries occur here.

§9.5 OUT_OF_MEMORY detection: case-insensitive matching of the explicit memory
failure phrases below against server errors/failed HTTP bodies only. Unknown
runner failures remain RUNTIME; successful assistant text is never inspected.
Transport timeouts are CONNECTION errors without retries. Episode-wall-clock
TIMEOUT precedence belongs to the S14 runner, not this per-request client.
"""

import logging
import math
import time

import requests


logger = logging.getLogger(__name__)
# shortcut: OOM uses explicit error phrases, extend when a verified runtime reports new wording.
_OOM_PHRASES = (
    "out of memory", "requires more system memory", "not enough memory",
    "insufficient memory", "unable to allocate", "failed to allocate",
    "cudamalloc failed", "cuda error: memory allocation",
)
_REQUIRED_OPTIONS = ("temperature", "seed", "num_ctx", "num_predict")


class OllamaError(RuntimeError):
    """Protocol §9.5 ERROR cause plus the original HTTP evidence when available."""

    def __init__(self, cause, message, *, status_code=None, response_text=None):
        super().__init__(message)
        self.cause = cause
        self.status_code = status_code
        self.response_text = response_text


class OllamaClient:
    """Caller supplies configured timeout and think; no implicit generation settings."""

    def __init__(self, *, timeout_seconds, think, base_url="http://127.0.0.1:11434"):
        if (type(timeout_seconds) not in (int, float) or not math.isfinite(timeout_seconds)
                or timeout_seconds <= 0):
            raise ValueError("timeout_seconds must be a finite positive number")
        if type(think) is not bool:
            raise ValueError("think must be an explicit boolean, never None or a runtime default")
        self.timeout_seconds = timeout_seconds
        self.think = think
        self.base_url = base_url.rstrip("/")

    def _request(self, method, endpoint, **kwargs):
        url = self.base_url + endpoint
        for attempt in range(3):
            try:
                response = requests.request(method, url, timeout=self.timeout_seconds, **kwargs)
                break
            except requests.Timeout as exc:
                # ConnectTimeout also inherits ConnectionError; never retry an ambiguous timeout.
                logger.error("Ollama %s %s timed out: %s", method, url, exc)
                raise OllamaError("CONNECTION", str(exc)) from exc
            except requests.ConnectionError as exc:
                if attempt == 2:
                    logger.error("Ollama %s %s failed after 3 attempts: %s", method, url, exc)
                    raise OllamaError("CONNECTION", str(exc)) from exc
                logger.warning("Ollama %s %s connection error; retry %s/2: %s",
                               method, url, attempt + 1, exc)
            except requests.RequestException as exc:
                logger.error("Ollama %s %s transport failure: %s", method, url, exc)
                raise OllamaError("OTHER", str(exc)) from exc

        try:
            data = response.json()
        except ValueError:
            if 200 <= response.status_code < 300:
                self._fail("OTHER", "Ollama returned invalid JSON", response)
            self._server_failure(response.text, response)

        if not 200 <= response.status_code < 300 or (isinstance(data, dict) and "error" in data):
            message = str(data.get("error", response.text)) if isinstance(data, dict) else response.text
            self._server_failure(message, response)
        if not isinstance(data, dict):
            self._fail("OTHER", "Ollama response must be a JSON object", response)
        return data

    @staticmethod
    def _fail(cause, message, response=None):
        logger.error("Ollama %s: %s", cause, message)
        raise OllamaError(cause, message,
                          status_code=response.status_code if response is not None else None,
                          response_text=response.text if response is not None else None)

    def _server_failure(self, message, response):
        cause = "OUT_OF_MEMORY" if any(p in message.lower() for p in _OOM_PHRASES) else "RUNTIME"
        self._fail(cause, message, response)

    def chat(self, model, messages, tools, options):
        """Return raw_response, message, native tool_calls, token counts and wall latency.

        All four §9.1 generation settings are mandatory; other supplied options
        pass through unchanged. Missing token counts stay None, never zero.
        latency_seconds includes HTTP time and any connection retries.
        """
        missing = [name for name in _REQUIRED_OPTIONS if name not in options or options[name] is None]
        if missing:
            raise ValueError(f"Explicit generation options required: {', '.join(missing)}")
        started = time.perf_counter()
        raw = self._request("POST", "/api/chat", json={
            "model": model, "messages": messages, "tools": tools,
            "options": options, "stream": False, "think": self.think})
        latency = time.perf_counter() - started
        message = raw.get("message")
        if (raw.get("done") is not True or not isinstance(message, dict)
                or message.get("role") != "assistant"
                or not isinstance(message.get("tool_calls", []), list)):
            self._fail("OTHER", f"Invalid Ollama chat envelope: {raw!r}")
        for field in ("prompt_eval_count", "eval_count"):
            value = raw.get(field)
            if value is not None and (type(value) is not int or value < 0):
                self._fail("OTHER", f"Invalid Ollama {field}: {raw!r}")
        return {"raw_response": raw, "message": message,
                "tool_calls": message.get("tool_calls", []),
                "prompt_eval_count": raw.get("prompt_eval_count"),
                "eval_count": raw.get("eval_count"), "latency_seconds": latency}

    def get_model_identity(self, model):
        """Exact installed tag/digest plus /api/show metadata; never selects another model."""
        tag = model if ":" in model.rsplit("/", 1)[-1] else model + ":latest"
        models = self._request("GET", "/api/tags").get("models")
        if not isinstance(models, list) or any(not isinstance(item, dict) for item in models):
            self._fail("OTHER", "Invalid Ollama model list")
        matches = [item for item in models if tag in (item.get("name"), item.get("model"))]
        if not matches:
            self._fail("RUNTIME", f"Model {tag!r} is not installed")
        if len(matches) != 1:
            self._fail("OTHER", f"Ambiguous Ollama identity for {tag!r}")
        info = self._request("POST", "/api/show", json={"model": tag})
        details = info.get("details")
        if not isinstance(details, dict):
            self._fail("OTHER", f"Missing model details for {tag!r}")
        identity = {"tag": tag, "digest": matches[0].get("digest"),
                    "quantization": details.get("quantization_level"),
                    "parameter_size": details.get("parameter_size")}
        if any(not isinstance(value, str) or not value.strip() for value in identity.values()):
            self._fail("OTHER", f"Incomplete model identity: {identity!r}")
        identity["capabilities"] = info.get("capabilities", [])
        return identity
