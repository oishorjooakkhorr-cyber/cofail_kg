"""Authorized shared S20 resource reassessment; existing P1 runner is unchanged."""
import argparse
from collections import Counter
from datetime import datetime, timezone
import importlib.util
import json
import os
from pathlib import Path
import shutil
import subprocess
import time

from cofail_kg.agents.ollama_client import OllamaClient
from cofail_kg.agents.prompts import prompt_sha256
from cofail_kg.evaluation.agent_metrics import agent_metrics
from cofail_kg.evaluation.screening import aggregate_model

ROOT = Path(__file__).resolve().parents[1]
OUT = ROOT / "results/diagnostics/s20/shared-resources-32k-20261030"
BASE = "http://127.0.0.1:11435"
MODELS = {
    "gemma4": "gemma4-5060ti-32k-20261029",
    "ministral3": "ministral3-5060ti-32k-20261030",
    "granite41": "granite41-5060ti-32k-20261030",
    "qwen35": "qwen35-5060ti-32k-20261029",
}


def load(name, path):
    spec = importlib.util.spec_from_file_location(name, path)
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


def read(path):
    return json.loads(path.read_text(encoding="utf-8"))


def run_id(model):
    return f"{model}-5060ti-32k-resources-20261030"


def amend(config):
    assert config["num_ctx"] == 32768
    assert config["num_predict"] == 4096
    assert config["request_timeout_seconds"] == 120
    return {**config, "num_predict": 8192, "request_timeout_seconds": 240}


def resume(snapshot, path):
    if path.exists():
        saved = read(path)
        snapshot["config"]["git_commit"] = saved["config"]["git_commit"]
        assert saved == snapshot, "Immutable configuration changed"
    return snapshot


def prepare(model):
    launcher = load("screening", ROOT / "scripts/20_screen_models.py")
    baseline_dir = OUT.parent / MODELS[model]
    driver = load("baseline_driver", baseline_dir / "run_model.py")
    seed = read(baseline_dir / "manifest.json")
    config = amend(seed["config"])
    for path, digest in config["source_sha256"].items():
        driver.guard_source(ROOT / path, digest)
    assert prompt_sha256() == config["prompt_sha256"]
    queries = [json.loads(line)["query_id"] for line in
               (ROOT / "data/agent_inputs/screening.jsonl").read_text().splitlines()]
    assert seed["query_ids"] == queries and len(set(queries)) == len(queries) == 20
    expected = {**launcher.SETTINGS, "num_ctx": 32768, "num_predict": 8192}
    assert {k: config[k] for k in launcher.SETTINGS} == expected
    commit = subprocess.check_output(["git", "rev-parse", "HEAD"], cwd=ROOT, text=True).strip()
    dirty = bool(subprocess.check_output(["git", "status", "--porcelain"], cwd=ROOT, text=True))
    config.update(run_id=run_id(model), runs_root=str(ROOT / "results/runs/screening-5060ti"),
                  agent_inputs=str(ROOT / "data/agent_inputs/screening.jsonl"),
                  cache_dir=str(ROOT / "data/cache"), base_url=BASE,
                  git_commit=commit + ("-dirty" if dirty else ""))
    config["source_sha256"] = {p: launcher.file_hash(ROOT / p) for p in config["source_sha256"]}
    for path in (Path(__file__), ROOT / "scripts/20_shared_resources_report.py",
                 ROOT / "tests/test_s20_shared_resources.py"):
        config["source_sha256"][path.relative_to(ROOT).as_posix()] = launcher.file_hash(path)
    snapshot = {"identity": seed["identity"], "agent": seed["agent"],
                "config": config, "query_ids": queries}
    folder = OUT / model
    snapshot = resume(snapshot, folder / "manifest.json")
    launcher.pin_manifest(folder / "manifest.json", snapshot)
    launcher.pin_manifest(Path(config["runs_root"]) / run_id(model) /
                          f"{seed['agent']['agent_id']}.config.json", snapshot)
    # Pin the entire preceding scientific history once, excluding this comparison.
    history_path = OUT / "historical-hashes.json"
    if not history_path.exists():
        paths = [p for root in (ROOT / "results/runs", ROOT / "results/diagnostics")
                 for p in root.rglob("*") if p.is_file() and OUT not in p.parents
                 and run_id(model) not in p.parts and "__pycache__" not in p.parts
                 and "ministral_speed" not in p.parts
                 and not any(run_id(m) in p.parts for m in MODELS)]
        launcher.pin_manifest(history_path, {p.relative_to(ROOT).as_posix(): launcher.file_hash(p)
                                            for p in paths})
    return launcher, driver, snapshot, folder


def integrity(launcher, snapshot):
    launcher.check_sources(snapshot["config"])
    for path, digest in read(OUT / "historical-hashes.json").items():
        assert launcher.file_hash(ROOT / path) == digest, path


def sample(client, driver, folder, phase):
    ps = client._request("GET", "/api/ps")
    driver.guard_runtime(ps, (folder / "server.stderr.log").read_text(errors="replace"))
    memory = subprocess.check_output(["powershell", "-NoProfile", "-Command",
        "Get-CimInstance Win32_OperatingSystem | Select-Object TotalVisibleMemorySize,FreePhysicalMemory | ConvertTo-Json -Compress"], text=True).strip()
    gpu = subprocess.check_output(["nvidia-smi", "--query-gpu=name,driver_version,memory.total,memory.used,memory.free",
                                   "--format=csv,noheader"], text=True).strip()
    with (folder / "runtime-samples.jsonl").open("a", encoding="utf-8") as handle:
        handle.write(json.dumps({"time": datetime.now(timezone.utc).isoformat(), "phase": phase,
                                 "ps": ps, "memory": memory, "gpu": gpu}) + "\n")


def synthetic(client, snapshot, folder, name):
    tools = [{"type": "function", "function": {"name": "add", "description": "Add two integers.",
        "parameters": {"type": "object", "properties": {"a": {"type": "integer"},
        "b": {"type": "integer"}}, "required": ["a", "b"]}}}]
    messages = [{"role": "user", "content": "Use the add tool to calculate 2 + 3, then state the result."}]
    options = {k: snapshot["config"][k] for k in ("temperature", "seed", "num_ctx", "num_predict")}
    first = client.chat(snapshot["agent"]["tag"], messages, tools, options)
    (folder / f"{name}-call.json").write_text(json.dumps(first["raw_response"], indent=2))
    assert not first["message"].get("thinking")
    calls = first["tool_calls"]
    assert len(calls) == 1 and calls[0]["function"]["name"] == "add"
    arguments = calls[0]["function"]["arguments"]
    assert arguments == {"a": 2, "b": 3} and all(type(v) is int for v in arguments.values())
    messages.extend([first["message"], {"role": "tool", "tool_name": "add", "content": "5"}])
    second = client.chat(snapshot["agent"]["tag"], messages, tools, options)
    (folder / f"{name}-result.json").write_text(json.dumps(second["raw_response"], indent=2))
    assert not second["message"].get("thinking") and not second["tool_calls"]
    assert "5" in second["message"].get("content", "")


def report(model, launcher, snapshot, folder):
    config, agent = snapshot["config"], snapshot["agent"]
    records = launcher.run_screening(agent, config, snapshot["query_ids"], max_new=0,
                                     check_identity=lambda: None)
    assert len(records) == 20
    refs, targets, mapping, status, kg, degrees = launcher.load_evaluator()
    metrics = []
    for record in records:
        query = refs[record["query_id"]]
        metric = agent_metrics(record, query, mapping[query["relation_type"]], targets[record["query_id"]],
                               kg, degrees, consistent=status[record["query_id"]] == "CONSISTENT")
        launcher.pin_manifest(folder / "metrics" / f"{record['query_id']}.json", metric)
        metrics.append(metric)
    identity = {k: agent[k] for k in ("tag", "digest", "quantization", "parameter_size", "family")}
    summary = {"screening_row": aggregate_model(records, metrics, identity),
               "status_counts": dict(Counter(r["status"] for r in records))}
    integrity(launcher, snapshot)
    launcher.pin_manifest(folder / "summary.json", summary)
    run_dir = Path(config["runs_root"]) / run_id(model)
    launcher.pin_manifest(folder / "final-run-hashes.json", {
        p.relative_to(ROOT).as_posix(): launcher.file_hash(p) for p in run_dir.glob("*.json")})
    print(json.dumps(summary, indent=2), flush=True)


def execute(model, *, preflight_only=False):
    launcher, driver, snapshot, folder = prepare(model)
    integrity(launcher, snapshot)
    if not preflight_only and (folder / "summary.json").exists():
        report(model, launcher, snapshot, folder)
        return
    client = OllamaClient(think=False, timeout_seconds=240, base_url=BASE)
    env = os.environ.copy()
    env.update(OLLAMA_HOST=BASE, OLLAMA_MODELS="D:\\Models", OLLAMA_CONTEXT_LENGTH="32768",
               OLLAMA_NUM_PARALLEL="1", OLLAMA_KV_CACHE_TYPE="f16")
    # Preserve Qwen's inherited config-string setting from its 32K baseline.
    if model == "qwen35":
        env.pop("OLLAMA_FLASH_ATTENTION", None)
    else:
        env["OLLAMA_FLASH_ATTENTION"] = "true"
    executable = shutil.which("ollama")
    assert executable, "Installed Ollama executable missing"
    processes = subprocess.check_output(["powershell", "-NoProfile", "-Command",
        "Get-CimInstance Win32_Process | Where-Object { $_.Name -match 'ollama' } | Select-Object ProcessId,Name,CommandLine | ConvertTo-Json -Compress"], text=True)
    (folder / "processes-before.json").write_text(processes)
    # A user's idle tray server may remain; refuse competing model runners/experiments.
    assert "llama-server" not in processes and "11435" not in processes, "Competing model process"
    try:
        import requests
        requests.get(BASE + "/api/version", timeout=2)
    except requests.ConnectionError:
        pass
    else:
        raise AssertionError("Isolated port is already occupied")
    with (folder / "server.stdout.log").open("ab") as stdout, (folder / "server.stderr.log").open("ab") as stderr:
        server = subprocess.Popen([executable, "serve"], env=env, stdout=stdout, stderr=stderr,
                                  creationflags=subprocess.CREATE_NO_WINDOW)
        (folder / "server.pid.txt").write_text(str(server.pid))
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
            assert client.get_model_identity(snapshot["agent"]["tag"]) == snapshot["identity"]
            name = "preflight" if preflight_only else "block-preflight"
            if (folder / f"{name}-call.json").exists():
                name += "-resume-" + datetime.now(timezone.utc).strftime("%Y%m%dT%H%M%S%fZ")
            synthetic(client, snapshot, folder, name)
            sample(client, driver, folder, name)
            if preflight_only:
                launcher.pin_manifest(folder / "preflight-passed.json", {"passed": True, "run_id": run_id(model)})
            else:
                assert all(read(OUT / m / "preflight-passed.json")["passed"] for m in MODELS)

                def check():
                    integrity(launcher, snapshot)
                    assert client.get_model_identity(snapshot["agent"]["tag"]) == snapshot["identity"]
                    sample(client, driver, folder, "official")

                records = launcher.run_screening(snapshot["agent"], snapshot["config"],
                    snapshot["query_ids"], max_new=20, check_identity=check)
                assert len(records) == 20
        finally:
            if server.poll() is None:
                try:
                    result = client._request("POST", "/api/generate", json={"model": snapshot["agent"]["tag"], "keep_alive": 0})
                    (folder / f"{name}-unload.json").write_text(json.dumps(result, indent=2))
                finally:
                    server.terminate()
                    server.wait(timeout=30)
    if not preflight_only:
        report(model, launcher, snapshot, folder)


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("phase", choices=("pin", "preflight", "run", "report"))
    parser.add_argument("--model", choices=MODELS)
    args = parser.parse_args()
    selected = [args.model] if args.model else MODELS
    for model in selected:
        print(f"PHASE {args.phase}: {model}", flush=True)
        if args.phase in ("pin", "report"):
            launcher, _, snapshot, folder = prepare(model)
            integrity(launcher, snapshot)
            if args.phase == "report":
                report(model, launcher, snapshot, folder)
        else:
            execute(model, preflight_only=args.phase == "preflight")


if __name__ == "__main__":
    main()
