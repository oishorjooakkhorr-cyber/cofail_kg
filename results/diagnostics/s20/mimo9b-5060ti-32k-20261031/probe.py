"""Synthetic think=false/native-tools probe for hf.co/bartowski/MiMo-V2.6-Distill-Qwen-9B-GGUF:Q4_K_M on an isolated pinned server; no screening query."""
import json, os, subprocess, time
from pathlib import Path
from cofail_kg.agents.ollama_client import OllamaClient

OUT = Path(__file__).resolve().parent
TAG = "hf.co/bartowski/MiMo-V2.6-Distill-Qwen-9B-GGUF:Q4_K_M"
env = dict(os.environ, OLLAMA_HOST="127.0.0.1:11436", OLLAMA_MODELS=r"D:\Models", OLLAMA_CONTEXT_LENGTH="32768",
           OLLAMA_NUM_PARALLEL="1", OLLAMA_KV_CACHE_TYPE="f16", OLLAMA_FLASH_ATTENTION="true")
with (OUT / "probe-server.stderr.log").open("wb") as e, (OUT / "probe-server.stdout.log").open("wb") as o:
    srv = subprocess.Popen([r"D:\cofailKG\.venv\ollama-0.40.12\ollama.exe", "serve"], env=env, stdout=o, stderr=e)
    try:
        c = OllamaClient(think=False, timeout_seconds=240, base_url="http://127.0.0.1:11436")
        for _ in range(60):
            try:
                assert c._request("GET", "/api/version")["version"] == "0.40.12"; break
            except Exception:
                time.sleep(1)
        identity = c.get_model_identity(TAG)
        (OUT / "probe-identity.json").write_text(json.dumps(identity, indent=2), encoding="utf-8")
        print("IDENTITY", identity)
        tools = [{"type": "function", "function": {"name": "add", "description": "Add two integers.",
                  "parameters": {"type": "object", "properties": {"a": {"type": "integer"}, "b": {"type": "integer"}}, "required": ["a", "b"]}}}]
        msgs = [{"role": "user", "content": "Use the add tool to calculate 2 + 3, then state the result."}]
        opts = dict(temperature=0, seed=42, num_ctx=32768, num_predict=8192)
        r1 = c.chat(TAG, msgs, tools, opts)
        (OUT / "probe-call.json").write_text(json.dumps(r1["raw_response"], indent=2), encoding="utf-8")
        print("FIRST thinking:", repr(r1["message"].get("thinking")), "content:", repr(r1["message"].get("content")), "calls:", r1["tool_calls"])
        if r1["tool_calls"]:
            msgs += [r1["message"], {"role": "tool", "tool_name": "add", "content": "5"}]
            r2 = c.chat(TAG, msgs, tools, opts)
            (OUT / "probe-result.json").write_text(json.dumps(r2["raw_response"], indent=2), encoding="utf-8")
            print("SECOND thinking:", repr(r2["message"].get("thinking")), "content:", repr(r2["message"].get("content")), r2["tool_calls"])
        print("PS", json.dumps(c._request("GET", "/api/ps")["models"]))
    finally:
        try:
            c._request("POST", "/api/generate", json={"model": TAG, "keep_alive": 0})
        finally:
            srv.terminate(); srv.wait(30)
