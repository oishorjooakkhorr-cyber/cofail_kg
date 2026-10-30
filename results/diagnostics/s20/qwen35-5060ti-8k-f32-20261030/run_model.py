"""Researcher-authorized Qwen35-9B S20 block on the 5060 Ti: frozen 8K screening settings with f32 KV.

Reuses the unchanged S14 runner, S16-S19 evaluators and the protocol §9.1 screening configuration;
only the server KV cache type (f16 -> f32) and host differ from the official 8K block. D3 unchanged.
"""
import argparse
from collections import Counter
from datetime import datetime, timezone
import hashlib
import importlib.util
import json
import os
from pathlib import Path
import subprocess
import time

from cofail_kg.agents.ollama_client import OllamaClient
from cofail_kg.agents.prompts import prompt_sha256
from cofail_kg.evaluation.agent_metrics import agent_metrics
from cofail_kg.evaluation.screening import aggregate_model

ROOT = Path(__file__).resolve().parents[4]
OUT = Path(__file__).resolve().parent
BASE = "http://127.0.0.1:11435"
DIGEST = "56671c2ab9385f9cfcb404638e32cd62d88e3501d44822208363c010179a3c90"
RUN_ID = "qwen35-5060ti-8k-f32-20261030"
SEED_MANIFEST = OUT.parent / "qwen35-5060ti-16k-20261029/manifest.json"
OLLAMA = ROOT / ".venv/ollama-0.40.12/ollama.exe"
OLLAMA_SHA256 = "aa76635f0a54c663093a9d1c307f6abde3fb4fa0b1aebfd42f71b6faeec0a8e5"
KV_CACHE = "f32"
# Another workstream's uncommitted evidence; excluded from the history pin so it cannot stop this block.
HISTORY_EXCLUDE = ("__pycache__", "ministral_speed", "shared-resources-32k-20261030")


def guard_source(path, expected):
    data = path.read_bytes()
    assert expected in (hashlib.sha256(data).hexdigest(),
                        hashlib.sha256(data.replace(b"\r\n", b"\n")).hexdigest()), str(path)


def guard_runtime(ps, log):
    models = [m for m in ps["models"] if m["digest"] == DIGEST]
    assert len(models) == 1, ps
    model = models[0]
    assert model["context_length"] == 8192, model
    assert model["size"] > 0 and model["size_vram"] == model["size"], model
    assert "warmup: flash attention is enabled" in log, "Runtime Flash Attention is not enabled"
    assert f"OLLAMA_KV_CACHE_TYPE:{KV_CACHE}" in log, "Server cache setting differs"
    assert "K (f32):" in log and "V (f32):" in log, "Actual KV cache is not verified f32"
    assert "K (f16)" not in log and "V (f16)" not in log, "An f16 KV cache was allocated"
    assert "offloaded 33/33 layers to GPU" in log, "Full model layer residency unverified"


def resume_snapshot(snapshot, path):
    if path.exists():
        saved = json.loads(path.read_text())
        snapshot["config"]["git_commit"] = saved["config"]["git_commit"]
        assert snapshot == saved, "Pinned run configuration changed"
    return snapshot


def context_amendment(config):
    assert config["num_ctx"] == 16384, "Expected the complete same-host 16K configuration"
    return {**config, "num_ctx": 8192}


def server_env(base_env):
    env = dict(base_env)
    env.update(OLLAMA_HOST=BASE.removeprefix("http://"), OLLAMA_MODELS="D:\\Models",
               OLLAMA_CONTEXT_LENGTH="8192", OLLAMA_NUM_PARALLEL="1", OLLAMA_KV_CACHE_TYPE=KV_CACHE)
    # Same inherited Flash Attention configuration as the same-host Qwen blocks; effective state is guarded.
    env.pop("OLLAMA_FLASH_ATTENTION", None)
    return env


def load_launcher():
    spec = importlib.util.spec_from_file_location("screening_launcher", ROOT / "scripts/20_screen_models.py")
    launcher = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(launcher)
    return launcher


def prepare(launcher):
    seed = json.loads(SEED_MANIFEST.read_text())
    agent, config, queries = seed["agent"], context_amendment(seed["config"]), seed["query_ids"]
    for path, digest in config["source_sha256"].items():
        guard_source(ROOT / path, digest)
    # Windows checkout line endings differ; the new manifest pins actual bytes.
    config["source_sha256"] = {p: launcher.file_hash(ROOT / p) for p in config["source_sha256"]}
    assert agent["digest"] == DIGEST and agent["quantization"] == "Q4_K_M" and agent["think"] is False
    assert prompt_sha256() == config["prompt_sha256"]
    ids = [json.loads(line)["query_id"] for line in (ROOT / "data/agent_inputs/screening.jsonl").read_text().splitlines()]
    assert queries == ids and len(queries) == len(set(queries)) == 20
    assert {k: config[k] for k in launcher.SETTINGS} == launcher.SETTINGS
    assert config["request_timeout_seconds"] == 120
    commit = subprocess.check_output(["git", "rev-parse", "HEAD"], cwd=ROOT, text=True).strip()
    dirty = bool(subprocess.check_output(["git", "status", "--porcelain"], cwd=ROOT, text=True))
    config.update(run_id=RUN_ID, runs_root=str(ROOT / "results/runs/screening-5060ti"),
                  agent_inputs=str(ROOT / "data/agent_inputs/screening.jsonl"),
                  cache_dir=str(ROOT / "data/cache"), base_url=BASE, git_commit=commit + ("-dirty" if dirty else ""))
    for path in OUT.glob("*.py"):
        config["source_sha256"][path.relative_to(ROOT).as_posix()] = launcher.file_hash(path)
    assert launcher.file_hash(OLLAMA) == OLLAMA_SHA256, "Pinned Ollama 0.40.12 executable changed"
    snapshot = {"identity": seed["identity"], "agent": agent, "config": config, "query_ids": queries,
                "runtime": {"ollama": "0.40.12", "executable_sha256": OLLAMA_SHA256, "kv_cache_type": KV_CACHE,
                            "num_parallel": 1, "flash_attention_env": "inherited/unset"}}
    history_path = OUT / "historical-hashes.json"
    if not history_path.exists():
        paths = [p for root in (ROOT / "results/runs", ROOT / "results/diagnostics") for p in root.rglob("*")
                 if p.is_file() and OUT not in p.parents and RUN_ID not in p.parts
                 and not any(part in p.parts for part in HISTORY_EXCLUDE)
                 and not any("32k-resources-20261030" in part for part in p.parts)]
        launcher.pin_manifest(history_path, {p.relative_to(ROOT).as_posix(): launcher.file_hash(p) for p in paths})
    snapshot = resume_snapshot(snapshot, OUT / "manifest.json")
    launcher.pin_manifest(OUT / "manifest.json", snapshot)
    launcher.pin_manifest(Path(config["runs_root"]) / RUN_ID / "Qwen35-9B.config.json", snapshot)
    return snapshot


def integrity(launcher, config):
    launcher.check_sources(config)
    for path, digest in json.loads((OUT / "historical-hashes.json").read_text()).items():
        assert launcher.file_hash(ROOT / path) == digest, path


def system_sample():
    memory = subprocess.check_output(["powershell", "-NoProfile", "-Command",
        "Get-CimInstance Win32_OperatingSystem | Select-Object TotalVisibleMemorySize,FreePhysicalMemory | ConvertTo-Json -Compress"], text=True).strip()
    gpu = subprocess.check_output(["nvidia-smi", "--query-gpu=name,driver_version,memory.total,memory.used,memory.free",
                                   "--format=csv,noheader"], text=True).strip()
    return memory, gpu


def synthetic(client, tag, name):
    tools = [{"type": "function", "function": {"name": "add", "description": "Add two integers.",
        "parameters": {"type": "object", "properties": {"a": {"type": "integer"},
        "b": {"type": "integer"}}, "required": ["a", "b"]}}}]
    messages = [{"role": "user", "content": "Use the add tool to calculate 2 + 3, then state the result."}]
    options = dict(temperature=0, seed=42, num_ctx=8192, num_predict=4096)
    first = client.chat(tag, messages, tools, options)
    (OUT / f"{name}-call.json").write_text(json.dumps(first["raw_response"], indent=2))
    assert not first["message"].get("thinking")
    calls = first["tool_calls"]
    assert len(calls) == 1 and calls[0]["function"]["name"] == "add"
    arguments = calls[0]["function"]["arguments"]
    assert arguments == {"a": 2, "b": 3} and all(type(v) is int for v in arguments.values())
    messages.extend([first["message"], {"role": "tool", "tool_name": "add", "content": "5"}])
    second = client.chat(tag, messages, tools, options)
    (OUT / f"{name}-result.json").write_text(json.dumps(second["raw_response"], indent=2))
    assert not second["message"].get("thinking") and not second["tool_calls"]
    assert "5" in second["message"].get("content", "")


def report(launcher, snapshot):
    agent, config = snapshot["agent"], snapshot["config"]
    records = launcher.run_screening(agent, config, snapshot["query_ids"], max_new=0, check_identity=lambda: None)
    assert len(records) == 20
    refs, targets, mapping, status, kg, degrees = launcher.load_evaluator()
    metrics = []
    for record in records:
        query = refs[record["query_id"]]
        metric = agent_metrics(record, query, mapping[query["relation_type"]], targets[record["query_id"]],
                               kg, degrees, consistent=status[record["query_id"]] == "CONSISTENT")
        launcher.pin_manifest(OUT / "metrics" / f"{record['query_id']}.json", metric)
        metrics.append(metric)
    identity = {k: agent[k] for k in ("tag", "digest", "quantization", "parameter_size", "family")}
    summary = {"screening_row": aggregate_model(records, metrics, identity),
               "status_counts": dict(Counter(r["status"] for r in records)),
               "runtime": "0.40.12", "kv_cache": KV_CACHE}
    integrity(launcher, config)
    launcher.pin_manifest(OUT / "summary.json", summary)
    run_dir = Path(config["runs_root"]) / RUN_ID
    launcher.pin_manifest(OUT / "final-run-hashes.json", {p.relative_to(ROOT).as_posix(): launcher.file_hash(p)
                                                           for p in run_dir.glob("*.json")})
    print(json.dumps(summary, indent=2), flush=True)


def execute(launcher, snapshot, phase):
    agent, config = snapshot["agent"], snapshot["config"]
    client = OllamaClient(think=False, timeout_seconds=config["request_timeout_seconds"], base_url=BASE)
    processes = subprocess.check_output(["powershell", "-NoProfile", "-Command",
        "Get-CimInstance Win32_Process | Where-Object { $_.Name -match 'ollama|python' } | Select-Object ProcessId,Name,CommandLine | ConvertTo-Json -Compress"], text=True)
    stamp = datetime.now(timezone.utc).strftime("%Y%m%dT%H%M%SZ")
    (OUT / f"processes-{phase}-{stamp}.json").write_text(processes)
    # The user's idle tray server on 11434 may remain; refuse competing runners or experiments.
    assert "llama-server" not in processes and "11435" not in processes, "Competing model process"
    assert "20_shared_resources" not in processes and "20_screen_models" not in processes, \
        "Another experiment is running"
    try:
        client._request("GET", "/api/version")
    except Exception:
        pass
    else:
        raise AssertionError("Isolated port is already occupied")
    log_path = OUT / f"server-{phase}-{stamp}.stderr.log"
    with (OUT / f"server-{phase}-{stamp}.stdout.log").open("ab") as stdout, log_path.open("ab") as stderr:
        server = subprocess.Popen([str(OLLAMA), "serve"], env=server_env(os.environ), stdout=stdout, stderr=stderr,
                                  creationflags=subprocess.CREATE_NO_WINDOW)
        try:
            for _ in range(60):
                assert server.poll() is None, "Isolated Ollama exited during startup"
                try:
                    version = client._request("GET", "/api/version")
                    break
                except Exception:
                    time.sleep(1)
            else:
                raise AssertionError("Isolated server did not become ready")
            assert version["version"] == "0.40.12", version
            assert client.get_model_identity(agent["tag"]) == snapshot["identity"]
            run_dir = Path(config["runs_root"]) / RUN_ID

            def check():
                integrity(launcher, config)
                assert client.get_model_identity(agent["tag"]) == snapshot["identity"]
                ps = client._request("GET", "/api/ps")
                guard_runtime(ps, log_path.read_text(encoding="utf-8", errors="replace"))
                completed = len(list(run_dir.glob("*__Qwen35-9B__a1.json")))
                memory, gpu = system_sample()
                with (OUT / "runtime-samples.jsonl").open("a", encoding="utf-8") as handle:
                    handle.write(json.dumps({"time": datetime.now(timezone.utc).isoformat(), "phase": phase,
                                             "completed": completed, "ps": ps, "memory": memory, "gpu": gpu}) + "\n")
                print(f"CHECKED {completed}/20; context 8192; f32 KV; full GPU", flush=True)

            synthetic(client, agent["tag"], f"synthetic-{phase}-{stamp}")
            check()
            if phase == "preflight":
                launcher.pin_manifest(OUT / "preflight-passed.json", {"passed": True, "run_id": RUN_ID})
            else:
                assert json.loads((OUT / "preflight-passed.json").read_text())["passed"]
                records = launcher.run_screening(agent, config, snapshot["query_ids"], max_new=20, check_identity=check)
                assert len(records) == 20
        finally:
            if server.poll() is None:
                try:
                    result = client._request("POST", "/api/generate", json={"model": agent["tag"], "keep_alive": 0})
                    (OUT / f"unload-{phase}-{stamp}.json").write_text(json.dumps(result, indent=2))
                finally:
                    server.terminate()
                    server.wait(timeout=30)


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("phase", choices=("pin", "preflight", "run", "report"))
    args = parser.parse_args()
    launcher = load_launcher()
    snapshot = prepare(launcher)
    integrity(launcher, snapshot["config"])
    if args.phase in ("preflight", "run"):
        execute(launcher, snapshot, args.phase)
    if args.phase in ("run", "report"):
        report(launcher, snapshot)
    print(f"PHASE {args.phase} COMPLETE", flush=True)


if __name__ == "__main__":
    main()
