"""Researcher-authorized S20 candidate block: hf.co/bartowski/MiMo-V2.6-Distill-Qwen-9B-GGUF:Q4_K_M on the 5060 Ti at 32K/8192/f16.

Unchanged P1, tools, S14 runner, single JSON re-prompt, S16-S19 evaluators and D3 (protocol §9.1,
§19). Settings match the panel's 32K agents: num_ctx 32768, num_predict 8192, request 240 s, episode
600 s, budget 30, page size 50, temperature 0, seed 42, think=false, f16 KV, Flash Attention on.
The library tag is used unmodified; probe.py showed think=false honoured. Phases: preflight, run, report.
"""
import argparse
from collections import Counter
from datetime import datetime, timezone
import importlib.util
import json
import os
from pathlib import Path
import re
import subprocess
import time

from cofail_kg.agents.ollama_client import OllamaClient
from cofail_kg.agents.prompts import prompt_sha256
from cofail_kg.evaluation.agent_metrics import agent_metrics
from cofail_kg.evaluation.screening import aggregate_model
from cofail_kg.kg.prepare import file_hash
from cofail_kg.utils.frozen_hashes import read_frozen_hashes

ROOT = Path(__file__).resolve().parents[4]
OUT = Path(__file__).resolve().parent
RUN_ID = "mimo9b-5060ti-32k-20261031"
RUNS_ROOT = ROOT / "results/runs/screening-5060ti"
BASE = "http://127.0.0.1:11435"
OLLAMA = ROOT / ".venv/ollama-0.40.12/ollama.exe"
OLLAMA_SHA256 = "aa76635f0a54c663093a9d1c307f6abde3fb4fa0b1aebfd42f71b6faeec0a8e5"
TAG = "hf.co/bartowski/MiMo-V2.6-Distill-Qwen-9B-GGUF:Q4_K_M"
DIGEST = "e2eb00850f5e50b1d49e0456eac740e10d61f47bccd9d8cf29877c97d6897bef"
AGENT_ID = "MiMoV26DistillQwen-9B"
# Lineage not verified from a model card; name says Qwen distill and Ollama reports the qwen35 architecture.
FAMILY = "UNVERIFIED-qwen35-architecture"
SETTINGS = {"temperature": 0, "seed": 42, "num_ctx": 32768, "num_predict": 8192, "page_size": 50,
            "budget": 30, "timeout_seconds": 600, "request_timeout_seconds": 240}
HISTORY_EXCLUDE = ("__pycache__", "ministral_speed")


def guard_runtime(ps, log):
    models = ps["models"]
    assert len(models) == 1 and models[0]["digest"] == DIGEST, ps
    model = models[0]
    assert model["context_length"] == 32768, model
    assert model["size"] > 0 and model["size_vram"] == model["size"], model
    assert "OLLAMA_KV_CACHE_TYPE:f16" in log, "Server cache setting differs"
    caches = [line for line in log.splitlines() if "llama_kv_cache: size =" in line]
    assert caches and all("K (f16):" in line and "V (f16):" in line for line in caches), "KV cache is not f16"
    layers = re.findall(r"offloaded (\d+)/(\d+) layers to GPU", log)
    assert layers and all(a == b == "33" for a, b in layers), "Full 33/33 GPU residency unverified"
    assert "OLLAMA_FLASH_ATTENTION:true" in log and "--flash-attn on" in log, "Flash Attention differs"
    servers = [line for line in log.splitlines() if "starting llama-server" in line]
    assert servers and not any("--no-jinja" in line or "--chat-template" in line for line in servers), \
        "Embedded GGUF chat template is not in use"


def server_env(base_env):
    env = dict(base_env)
    env.update(OLLAMA_HOST=BASE.removeprefix("http://"), OLLAMA_MODELS="D:\\Models", OLLAMA_CONTEXT_LENGTH="32768",
               OLLAMA_NUM_PARALLEL="1", OLLAMA_KV_CACHE_TYPE="f16", OLLAMA_FLASH_ATTENTION="true")
    return env


def load_launcher():
    spec = importlib.util.spec_from_file_location("screening_launcher", ROOT / "scripts/20_screen_models.py")
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


def build_snapshot(launcher, identity):
    frozen = read_frozen_hashes(ROOT / "configs/frozen_hashes.yaml")
    required = {"data/agent_inputs/screening.jsonl": frozen["manifests"]["data/agent_inputs/screening.jsonl"],
                "data/processed/manifests/screening.jsonl": frozen["manifests"]["data/processed/manifests/screening.jsonl"],
                "data/cache/primekg_metadata.json": frozen["kg_fingerprint"],
                "src/cofail_kg/agents/tool_schemas.py": frozen["tools"],
                "results/semantics/relation_mapping.json": frozen["relation_mapping"]}
    if any(file_hash(ROOT / p) != h for p, h in required.items()) or prompt_sha256() != frozen["prompt"]:
        raise ValueError("Frozen screening sheet, KG, tools, mapping or prompt differs")
    query_ids = [json.loads(line)["query_id"] for line in
                 (ROOT / "data/agent_inputs/screening.jsonl").read_text(encoding="utf-8").splitlines()]
    manifest_ids = [json.loads(line)["query_id"] for line in
                    (ROOT / "data/processed/manifests/screening.jsonl").read_text(encoding="utf-8").splitlines()]
    assert query_ids == manifest_ids and len(set(query_ids)) == 20
    assert identity["tag"] == TAG and identity["digest"] == DIGEST and "tools" in identity["capabilities"]
    sources = sorted({*required, "configs/frozen_hashes.yaml", "docs/frozen_pilot_protocol.md",
                      "docs/decision_rules.md", "scripts/20_screen_models.py",
                      "data/processed/reference_queries.parquet", "data/processed/reference_targets.parquet",
                      "data/processed/primary_population.csv", "data/processed/reference_summary.json",
                      *[p.relative_to(ROOT).as_posix() for p in OUT.glob("*.py")],
                      *[p.relative_to(ROOT).as_posix() for p in (ROOT / "src/cofail_kg").rglob("*.py")]})
    commit = subprocess.check_output(["git", "rev-parse", "HEAD"], cwd=ROOT, text=True).strip()
    dirty = bool(subprocess.check_output(["git", "status", "--porcelain"], cwd=ROOT, text=True))
    config = {**SETTINGS, "run_id": RUN_ID, "runs_root": str(RUNS_ROOT),
              "agent_inputs": str(ROOT / "data/agent_inputs/screening.jsonl"),
              "agent_inputs_sha256": required["data/agent_inputs/screening.jsonl"], "cache_dir": str(ROOT / "data/cache"),
              "prompt_sha256": frozen["prompt"], "tool_schema_sha256": frozen["tools"],
              "kg_fingerprint": frozen["kg_fingerprint"], "biohopr_revision": frozen["biohopr_revision"],
              "git_commit": commit + ("-dirty" if dirty else ""), "base_url": BASE,
              "source_sha256": {p: file_hash(ROOT / p) for p in sources}}
    agent = {**identity, "agent_id": AGENT_ID, "family": FAMILY, "think": False}
    runtime = {"ollama": "0.40.12", "executable_sha256": OLLAMA_SHA256, "kv_cache_type": "f16",
               "flash_attention_env": "true", "num_parallel": 1}
    snapshot = {"identity": identity, "agent": agent, "config": config, "query_ids": query_ids, "runtime": runtime}
    path = RUNS_ROOT / RUN_ID / f"{AGENT_ID}.config.json"
    if path.exists():  # Resume keeps the original commit; anything else that changed stops the run.
        snapshot["config"]["git_commit"] = json.loads(path.read_text(encoding="utf-8"))["config"]["git_commit"]
    history = OUT / "historical-hashes.json"
    if not history.exists():
        paths = [p for root in (ROOT / "results/runs", ROOT / "results/diagnostics") for p in root.rglob("*")
                 if p.is_file() and OUT not in p.parents and RUN_ID not in p.parts
                 and not any(part in p.parts for part in HISTORY_EXCLUDE)]
        launcher.pin_manifest(history, {p.relative_to(ROOT).as_posix(): file_hash(p) for p in paths})
    launcher.pin_manifest(path, snapshot)
    launcher.pin_manifest(OUT / "manifest.json", snapshot)
    return snapshot


def integrity(launcher, config):
    launcher.check_sources(config)
    for path, digest in json.loads((OUT / "historical-hashes.json").read_text()).items():
        assert file_hash(ROOT / path) == digest, path


def synthetic(client, name):
    tools = [{"type": "function", "function": {"name": "add", "description": "Add two integers.",
        "parameters": {"type": "object", "properties": {"a": {"type": "integer"},
        "b": {"type": "integer"}}, "required": ["a", "b"]}}}]
    messages = [{"role": "user", "content": "Use the add tool to calculate 2 + 3, then state the result."}]
    options = {k: SETTINGS[k] for k in ("temperature", "seed", "num_ctx", "num_predict")}
    first = client.chat(TAG, messages, tools, options)
    (OUT / f"{name}-call.json").write_text(json.dumps(first["raw_response"], indent=2), encoding="utf-8")
    assert not first["message"].get("thinking")
    calls = first["tool_calls"]
    assert len(calls) == 1 and calls[0]["function"]["name"] == "add"
    assert calls[0]["function"]["arguments"] == {"a": 2, "b": 3}
    messages.extend([first["message"], {"role": "tool", "tool_name": "add", "content": "5"}])
    second = client.chat(TAG, messages, tools, options)
    (OUT / f"{name}-result.json").write_text(json.dumps(second["raw_response"], indent=2), encoding="utf-8")
    assert not second["message"].get("thinking") and not second["tool_calls"]
    assert "5" in second["message"].get("content", "")


def system_sample():
    memory = subprocess.check_output(["powershell", "-NoProfile", "-Command",
        "Get-CimInstance Win32_OperatingSystem | Select-Object TotalVisibleMemorySize,FreePhysicalMemory | ConvertTo-Json -Compress"],
        text=True).strip()
    gpu = subprocess.check_output(["nvidia-smi", "--query-gpu=name,driver_version,memory.total,memory.used,memory.free",
                                   "--format=csv,noheader"], text=True).strip()
    return memory, gpu


def execute(launcher, phase):
    stamp = datetime.now(timezone.utc).strftime("%Y%m%dT%H%M%SZ")
    processes = subprocess.check_output(["powershell", "-NoProfile", "-Command",
        "Get-CimInstance Win32_Process | Where-Object { $_.Name -match 'ollama|python' } | "
        "Select-Object ProcessId,Name,CommandLine | ConvertTo-Json -Compress"], text=True)
    (OUT / f"processes-{phase}-{stamp}.json").write_text(processes, encoding="utf-8")
    assert "llama-server" not in processes and "11435" not in processes, "Competing model process"
    assert all(s not in processes for s in ("20_screen_models", "20_shared_resources", "22_smoke_single")), \
        "Another experiment is running"
    client = OllamaClient(think=False, timeout_seconds=SETTINGS["request_timeout_seconds"], base_url=BASE)
    try:
        client._request("GET", "/api/version")
    except Exception:
        pass
    else:
        raise AssertionError("Isolated port is already occupied")
    assert file_hash(OLLAMA) == OLLAMA_SHA256, "Pinned Ollama 0.40.12 executable changed"
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
            snapshot = build_snapshot(launcher, client.get_model_identity(TAG))
            agent, config = snapshot["agent"], snapshot["config"]

            def check():
                integrity(launcher, config)
                assert client.get_model_identity(TAG) == snapshot["identity"]
                ps = client._request("GET", "/api/ps")
                guard_runtime(ps, log_path.read_text(encoding="utf-8", errors="replace"))
                done = len(list((RUNS_ROOT / RUN_ID).glob(f"*__{AGENT_ID}__a1.json")))
                memory, gpu = system_sample()
                with (OUT / "runtime-samples.jsonl").open("a", encoding="utf-8") as handle:
                    handle.write(json.dumps({"time": datetime.now(timezone.utc).isoformat(), "phase": phase,
                                             "completed": done, "ps": ps, "memory": memory, "gpu": gpu}) + "\n")
                print(f"CHECKED {done}/20; ctx 32768; f16 KV; 33/33 GPU; embedded template", flush=True)

            synthetic(client, f"synthetic-{phase}-{stamp}")
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
                    result = client._request("POST", "/api/generate", json={"model": TAG, "keep_alive": 0})
                    (OUT / f"unload-{phase}-{stamp}.json").write_text(json.dumps(result, indent=2), encoding="utf-8")
                finally:
                    server.terminate()
                    server.wait(timeout=30)


def report(launcher):
    snapshot = json.loads((RUNS_ROOT / RUN_ID / f"{AGENT_ID}.config.json").read_text(encoding="utf-8"))
    agent, config = snapshot["agent"], snapshot["config"]
    integrity(launcher, config)
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
               "error_causes": dict(Counter(r["cause"] for r in records if r["status"] == "ERROR")),
               "runtime": snapshot["runtime"]}
    launcher.pin_manifest(OUT / "summary.json", summary)
    launcher.pin_manifest(OUT / "final-run-hashes.json", {p.relative_to(ROOT).as_posix(): file_hash(p)
                                                           for p in sorted((RUNS_ROOT / RUN_ID).glob("*.json"))})
    print(json.dumps(summary, indent=2), flush=True)


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("phase", choices=("preflight", "run", "report"))
    args = parser.parse_args()
    launcher = load_launcher()
    if args.phase in ("preflight", "run"):
        execute(launcher, args.phase)
    if args.phase in ("run", "report"):
        report(launcher)
    print(f"PHASE {args.phase} COMPLETE", flush=True)


if __name__ == "__main__":
    main()
