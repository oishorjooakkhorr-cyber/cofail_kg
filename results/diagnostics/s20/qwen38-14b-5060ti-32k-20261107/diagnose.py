"""Diagnostic only (no screening query): does the tag answer coherently with think on/off, with and without tools?"""
import json, os, subprocess, time
from pathlib import Path
from cofail_kg.agents.ollama_client import OllamaClient
OUT = Path(__file__).resolve().parent
TAG = "hf.co/mradermacher/Qwen3.8-14B-Instruct-Turbo-i1-GGUF:Q4_K_M"
env = dict(os.environ, OLLAMA_HOST="127.0.0.1:11436", OLLAMA_MODELS=r"D:\Models", OLLAMA_CONTEXT_LENGTH="32768",
           OLLAMA_NUM_PARALLEL="1", OLLAMA_KV_CACHE_TYPE="f16", OLLAMA_FLASH_ATTENTION="true")
tools = [{"type": "function", "function": {"name": "add", "description": "Add two integers.",
          "parameters": {"type": "object", "properties": {"a": {"type": "integer"}, "b": {"type": "integer"}}, "required": ["a", "b"]}}}]
opts = dict(temperature=0, seed=42, num_ctx=32768, num_predict=1024)
results = {}
with (OUT / "diagnose-server.stderr.log").open("wb") as e, (OUT / "diagnose-server.stdout.log").open("wb") as o:
    srv = subprocess.Popen([r"D:\cofailKG\.venv\ollama-0.40.12\ollama.exe", "serve"], env=env, stdout=o, stderr=e)
    try:
        for think in (False, True):
            c = OllamaClient(think=think, timeout_seconds=240, base_url="http://127.0.0.1:11436")
            for _ in range(60):
                try:
                    c._request("GET", "/api/version"); break
                except Exception:
                    time.sleep(1)
            for name, msgs, t in (("tools", [{"role": "user", "content": "Use the add tool to calculate 2 + 3, then state the result."}], tools),
                                  ("plain", [{"role": "user", "content": "What is the capital of France? Answer in one sentence."}], None)):
                r = c.chat(TAG, msgs, t, opts)
                key = f"think={think}/{name}"
                results[key] = {"content": r["message"].get("content"), "thinking": (r["message"].get("thinking") or "")[:300],
                                "tool_calls": r["tool_calls"], "eval_count": r["raw_response"].get("eval_count")}
                print(key, json.dumps(results[key])[:400], flush=True)
        (OUT / "diagnose-results.json").write_text(json.dumps(results, indent=2), encoding="utf-8")
    finally:
        try:
            c._request("POST", "/api/generate", json={"model": TAG, "keep_alive": 0})
        finally:
            srv.terminate(); srv.wait(30)
