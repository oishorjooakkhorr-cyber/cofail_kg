"""Synthetic preflight only; no screening question is sent to the model."""
import json
from pathlib import Path
from cofail_kg.agents.ollama_client import OllamaClient
from run_model import BASE, DIGEST, guard_runtime

OUT = Path(__file__).resolve().parent
client = OllamaClient(think=False, timeout_seconds=120, base_url=BASE)
tag = "ibm/granite4.1:8b"
identity = client.get_model_identity(tag)
assert identity["digest"] == DIGEST and identity["quantization"] == "Q4_K_M"
assert "tools" in identity["capabilities"]
assert client._request("GET", "/api/version")["version"] == "0.40.12"
(OUT / "identity.json").write_text(json.dumps(identity, indent=2))
tools = [{"type": "function", "function": {"name": "add", "description": "Add two integers.",
    "parameters": {"type": "object", "properties": {"a": {"type": "integer"},
    "b": {"type": "integer"}}, "required": ["a", "b"]}}}]
messages = [{"role": "user", "content": "Use the add tool to calculate 2 + 3, then state the result."}]
options = dict(temperature=0, seed=42, num_ctx=16384, num_predict=4096)
first = client.chat(tag, messages, tools, options)
(OUT / "synthetic.json").write_text(json.dumps(first["raw_response"], indent=2))
assert not first["message"].get("thinking")
calls = first["tool_calls"]
assert len(calls) == 1 and calls[0]["function"]["name"] == "add"
arguments = calls[0]["function"]["arguments"]
assert arguments == {"a": 2, "b": 3} and all(type(v) is int for v in arguments.values())
messages.extend([first["message"], {"role": "tool", "tool_name": "add", "content": "5"}])
second = client.chat(tag, messages, tools, options)
(OUT / "synthetic-result.json").write_text(json.dumps(second["raw_response"], indent=2))
assert not second["message"].get("thinking") and not second["tool_calls"]
assert "5" in second["message"].get("content", "")
ps = client._request("GET", "/api/ps")
(OUT / "synthetic-ps.json").write_text(json.dumps(ps, indent=2))
guard_runtime(ps, (OUT / "server.stderr.log").read_text(encoding="utf-8", errors="replace"))
print(json.dumps({"identity": identity, "ps": ps, "result": second["message"]}, indent=2))
