"""S22 single-agent smoke test: four frozen agents x 20 screening queries, run ID smoke_single_v135.

Final configuration only (protocol §9.1 as revised at S21; configs/pilot.yaml `runtime`,
configs/models.yaml, frozen_hashes.yaml `models`). Each agent runs on its own isolated pinned Ollama
0.40.12 server with its frozen context, output cap, KV cache type and request timeout, one model at a
time in agent order (§9.2). The unchanged S14 runner and S20 resume logic are reused; every saved
final status is write-once and never rerun (§19). Evaluation (S16–S19) runs only after inference.
Phases: pin, preflight, run, report.
"""
import argparse
from datetime import datetime, timezone
import importlib.util
import json
import os
from pathlib import Path
import re
import subprocess
import time

import yaml

from cofail_kg.agents.ollama_client import OllamaClient
from cofail_kg.agents.prompts import prompt_sha256
from cofail_kg.evaluation.agent_metrics import agent_metrics
from cofail_kg.evaluation.smoke_summary import (OffQuestionSupported, model_summary, off_question_supported,
                                                render_markdown)
from cofail_kg.kg.prepare import file_hash
from cofail_kg.utils.frozen_hashes import read_frozen_hashes

ROOT = Path(__file__).resolve().parents[1]
RUN_ID = "smoke_single_v135"
RUNS_ROOT = ROOT / "results/runs"
DIAG = ROOT / "results/diagnostics/smoke_single_v135"
SUMMARY = ROOT / "results/diagnostics/smoke_single_summary.md"
BASE = "http://127.0.0.1:11435"
OLLAMA = ROOT / ".venv/ollama-0.40.12/ollama.exe"
OLLAMA_SHA256 = "aa76635f0a54c663093a9d1c307f6abde3fb4fa0b1aebfd42f71b6faeec0a8e5"
# Runtime evidence each agent showed in its S20 D3 evidence block, required again here.
EXPECTED_LOG = {
    "Ministral3-8B": ("offloaded 35/35 layers to GPU", "--flash-attn on"),
    "Gemma4-E4B": ("offloaded 43/43 layers to GPU", "offloaded 5/5 layers to GPU", "--flash-attn on",
                   "--spec-type draft-mtp", "--spec-draft-n-max 3", "--spec-draft-backend-sampling",
                   "sha256-05612e54110f8f68bade01dfcc546cdc6914d11dde0b650a65f263f0f87bbbd2"),
    "Granite41-8B": ("offloaded 41/41 layers to GPU", "--flash-attn on"),
    "Qwen35-9B": ("offloaded 33/33 layers to GPU", "warmup: flash attention is enabled"),
}


def load_launcher():
    spec = importlib.util.spec_from_file_location("screening_launcher", ROOT / "scripts/20_screen_models.py")
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


def load_panel(root=ROOT):
    """Frozen agents in agent order with their runtime; refuses any inconsistency between configs."""
    runtime = yaml.safe_load((root / "configs/pilot.yaml").read_text(encoding="utf-8"))["runtime"]
    rows = yaml.safe_load((root / "configs/models.yaml").read_text(encoding="utf-8"))["agents"]
    frozen = read_frozen_hashes(root / "configs/frozen_hashes.yaml")["models"]
    if [r["agent_id"] for r in rows] != runtime["agent_order"] or set(frozen) != set(runtime["agent_order"]):
        raise ValueError("models.yaml, pilot.yaml runtime and frozen_hashes.yaml disagree on the agents")
    for row in rows:
        if {k: row[k] for k in ("tag", "digest")} != frozen[row["agent_id"]]:
            raise ValueError(f"{row['agent_id']}: models.yaml differs from frozen_hashes.yaml")
    shared = {k: v for k, v in runtime.items() if k not in ("agent_order", "agents")}
    return [(row, {**shared, **runtime["agents"][row["agent_id"]]}) for row in rows]


def server_env(base_env, settings):
    env = dict(base_env)
    env.update(OLLAMA_HOST=BASE.removeprefix("http://"), OLLAMA_MODELS="D:\\Models",
               OLLAMA_CONTEXT_LENGTH=str(settings["num_ctx"]), OLLAMA_NUM_PARALLEL=str(settings["num_parallel"]),
               OLLAMA_KV_CACHE_TYPE=settings["kv_cache_type"])
    if settings["flash_attention_env"] == "true":
        env["OLLAMA_FLASH_ATTENTION"] = "true"
    elif settings["flash_attention_env"] == "inherited":
        env.pop("OLLAMA_FLASH_ATTENTION", None)  # As in the Qwen evidence block; effective state is guarded.
    else:
        raise ValueError(f"Unknown flash_attention_env {settings['flash_attention_env']!r}")
    return env


def guard_runtime(ps, log, agent_id, digest, settings):
    models = ps["models"]
    assert len(models) == 1 and models[0]["digest"] == digest, ps
    model = models[0]
    assert model["context_length"] == settings["num_ctx"], model
    assert model["size"] > 0 and model["size_vram"] == model["size"], model
    kv = settings["kv_cache_type"]
    assert f"OLLAMA_KV_CACHE_TYPE:{kv}" in log, "Server cache setting differs"
    caches = [line for line in log.splitlines() if "llama_kv_cache: size =" in line]
    assert caches and all(f"K ({kv}):" in line and f"V ({kv}):" in line for line in caches), "KV cache type differs"
    layers = re.findall(r"offloaded (\d+)/(\d+) layers to GPU", log)
    assert layers and all(a == b for a, b in layers), "Partial GPU layer residency"
    fa_config = "OLLAMA_FLASH_ATTENTION:" + ("true" if settings["flash_attention_env"] == "true" else "false")
    assert fa_config in log, "Flash Attention configuration differs from evidence block"
    for item in EXPECTED_LOG[agent_id]:
        assert item in log, f"{agent_id} runtime differs from evidence block: {item}"


def build_snapshot(launcher, row, settings, identity):
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
    if len(query_ids) != 20 or len(set(query_ids)) != 20 or query_ids != manifest_ids:
        raise ValueError("Screening must contain the same 20 ordered unique queries")
    if {k: identity[k] for k in ("tag", "digest", "quantization", "parameter_size")} != \
            {k: row[k] for k in ("tag", "digest", "quantization", "parameter_size")} or "tools" not in identity["capabilities"]:
        raise ValueError(f"{row['agent_id']}: installed identity differs from configs/models.yaml")
    sources = sorted({*required, "configs/frozen_hashes.yaml", "configs/pilot.yaml", "configs/models.yaml",
                      "docs/frozen_pilot_protocol.md", "docs/decision_rules.md", "scripts/20_screen_models.py",
                      "scripts/22_smoke_single.py", "data/processed/reference_queries.parquet",
                      "data/processed/reference_targets.parquet", "data/processed/primary_population.csv",
                      "data/processed/reference_summary.json",
                      *[p.relative_to(ROOT).as_posix() for p in (ROOT / "src/cofail_kg").rglob("*.py")]})
    commit = subprocess.check_output(["git", "rev-parse", "HEAD"], cwd=ROOT, text=True).strip()
    dirty = bool(subprocess.check_output(["git", "status", "--porcelain"], cwd=ROOT, text=True))
    config = {k: settings[k] for k in ("temperature", "seed", "num_ctx", "num_predict", "page_size", "budget",
                                       "timeout_seconds", "request_timeout_seconds")}
    config.update(run_id=RUN_ID, runs_root=str(RUNS_ROOT), agent_inputs=str(ROOT / "data/agent_inputs/screening.jsonl"),
                  agent_inputs_sha256=required["data/agent_inputs/screening.jsonl"], cache_dir=str(ROOT / "data/cache"),
                  prompt_sha256=frozen["prompt"], tool_schema_sha256=frozen["tools"],
                  kg_fingerprint=frozen["kg_fingerprint"], biohopr_revision=frozen["biohopr_revision"],
                  git_commit=commit + ("-dirty" if dirty else ""), base_url=BASE,
                  source_sha256={p: file_hash(ROOT / p) for p in sources})
    agent = {**identity, "agent_id": row["agent_id"], "family": row["family"], "think": settings["think"]}
    runtime = {k: settings[k] for k in ("ollama_version", "kv_cache_type", "flash_attention_env", "num_parallel",
                                        "evidence_run_id")}
    runtime["executable_sha256"] = OLLAMA_SHA256
    snapshot = {"identity": identity, "agent": agent, "config": config, "query_ids": query_ids, "runtime": runtime}
    path = RUNS_ROOT / RUN_ID / f"{row['agent_id']}.config.json"
    if path.exists():  # Resume keeps the original commit; anything else that changed stops the run.
        snapshot["config"]["git_commit"] = json.loads(path.read_text(encoding="utf-8"))["config"]["git_commit"]
    launcher.pin_manifest(path, snapshot)
    launcher.pin_manifest(DIAG / row["agent_id"] / "manifest.json", snapshot)
    return snapshot


def system_sample():
    memory = subprocess.check_output(["powershell", "-NoProfile", "-Command",
        "Get-CimInstance Win32_OperatingSystem | Select-Object TotalVisibleMemorySize,FreePhysicalMemory | ConvertTo-Json -Compress"],
        text=True).strip()
    gpu = subprocess.check_output(["nvidia-smi", "--query-gpu=name,driver_version,memory.total,memory.used,memory.free",
                                   "--format=csv,noheader"], text=True).strip()
    return memory, gpu


def synthetic(client, tag, settings, folder, name):
    tools = [{"type": "function", "function": {"name": "add", "description": "Add two integers.",
        "parameters": {"type": "object", "properties": {"a": {"type": "integer"},
        "b": {"type": "integer"}}, "required": ["a", "b"]}}}]
    messages = [{"role": "user", "content": "Use the add tool to calculate 2 + 3, then state the result."}]
    options = {k: settings[k] for k in ("temperature", "seed", "num_ctx", "num_predict")}
    first = client.chat(tag, messages, tools, options)
    (folder / f"{name}-call.json").write_text(json.dumps(first["raw_response"], indent=2), encoding="utf-8")
    assert not first["message"].get("thinking")
    calls = first["tool_calls"]
    assert len(calls) == 1 and calls[0]["function"]["name"] == "add"
    arguments = calls[0]["function"]["arguments"]
    assert arguments == {"a": 2, "b": 3} and all(type(v) is int for v in arguments.values())
    messages.extend([first["message"], {"role": "tool", "tool_name": "add", "content": "5"}])
    second = client.chat(tag, messages, tools, options)
    (folder / f"{name}-result.json").write_text(json.dumps(second["raw_response"], indent=2), encoding="utf-8")
    assert not second["message"].get("thinking") and not second["tool_calls"]
    assert "5" in second["message"].get("content", "")


def complete(row, snapshot):
    from cofail_kg.agents.trace import record_path
    return all(record_path(RUNS_ROOT, RUN_ID, q, row["agent_id"], 1).exists() for q in snapshot["query_ids"])


def execute(launcher, row, settings, phase):
    """Start the agent's isolated server, check runtime, then preflight or run; always stop the server."""
    folder = DIAG / row["agent_id"]
    folder.mkdir(parents=True, exist_ok=True)
    stamp = datetime.now(timezone.utc).strftime("%Y%m%dT%H%M%SZ")
    processes = subprocess.check_output(["powershell", "-NoProfile", "-Command",
        "Get-CimInstance Win32_Process | Where-Object { $_.Name -match 'ollama|python' } | "
        "Select-Object ProcessId,Name,CommandLine | ConvertTo-Json -Compress"], text=True)
    (folder / f"processes-{phase}-{stamp}.json").write_text(processes, encoding="utf-8")
    # The user's idle tray server on 11434 may remain; refuse competing runners or experiments.
    assert "llama-server" not in processes and "11435" not in processes, "Competing model process"
    assert all(s not in processes for s in ("20_screen_models", "20_shared_resources", "run_model.py")), \
        "Another experiment is running"
    client = OllamaClient(think=settings["think"], timeout_seconds=settings["request_timeout_seconds"], base_url=BASE)
    try:
        client._request("GET", "/api/version")
    except Exception:
        pass
    else:
        raise AssertionError("Isolated port is already occupied")
    assert file_hash(OLLAMA) == OLLAMA_SHA256, "Pinned Ollama 0.40.12 executable changed"
    log_path = folder / f"server-{phase}-{stamp}.stderr.log"
    with (folder / f"server-{phase}-{stamp}.stdout.log").open("ab") as stdout, log_path.open("ab") as stderr:
        server = subprocess.Popen([str(OLLAMA), "serve"], env=server_env(os.environ, settings), stdout=stdout,
                                  stderr=stderr, creationflags=subprocess.CREATE_NO_WINDOW)
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
            assert version["version"] == settings["ollama_version"], version
            snapshot = build_snapshot(launcher, row, settings, client.get_model_identity(row["tag"]))
            agent, config = snapshot["agent"], snapshot["config"]
            run_dir = RUNS_ROOT / RUN_ID

            def check():
                launcher.check_sources(config)
                assert client.get_model_identity(agent["tag"]) == snapshot["identity"]
                ps = client._request("GET", "/api/ps")
                guard_runtime(ps, log_path.read_text(encoding="utf-8", errors="replace"), agent["agent_id"],
                              agent["digest"], settings)
                done = len(list(run_dir.glob(f"*__{agent['agent_id']}__a1.json")))
                memory, gpu = system_sample()
                with (folder / "runtime-samples.jsonl").open("a", encoding="utf-8") as handle:
                    handle.write(json.dumps({"time": datetime.now(timezone.utc).isoformat(), "phase": phase,
                                             "completed": done, "ps": ps, "memory": memory, "gpu": gpu}) + "\n")
                print(f"CHECKED {agent['agent_id']} {done}/20; ctx {settings['num_ctx']}; "
                      f"{settings['kv_cache_type']} KV; full GPU", flush=True)

            synthetic(client, agent["tag"], settings, folder, f"synthetic-{phase}-{stamp}")
            check()
            if phase == "preflight":
                launcher.pin_manifest(folder / "preflight-passed.json", {"passed": True, "run_id": RUN_ID})
            else:
                assert json.loads((folder / "preflight-passed.json").read_text())["passed"]
                records = launcher.run_screening(agent, config, snapshot["query_ids"], max_new=20, check_identity=check)
                assert len(records) == 20
        finally:
            if server.poll() is None:
                try:
                    result = client._request("POST", "/api/generate", json={"model": row["tag"], "keep_alive": 0})
                    (folder / f"unload-{phase}-{stamp}.json").write_text(json.dumps(result, indent=2), encoding="utf-8")
                finally:
                    server.terminate()
                    server.wait(timeout=30)


# Summary-only code: never used by inference or S16-S19 labelling, so the report may run after a fix to it.
# Their current hashes are recorded in summary.json; every other pinned source must be unchanged.
REPORT_ONLY = ("scripts/22_smoke_single.py", "src/cofail_kg/evaluation/smoke_summary.py")


def report_config(config):
    return {**config, "source_sha256": {p: h for p, h in config["source_sha256"].items() if p not in REPORT_ONLY}}


def report(launcher, panel):
    """S16–S19 evaluation of all 80 saved episodes, then the descriptive summary and the S22 assertion."""
    refs, targets, mapping, status, kg, degrees = launcher.load_evaluator()
    summaries, all_metrics = {}, []
    for row, settings in panel:
        snapshot = json.loads((RUNS_ROOT / RUN_ID / f"{row['agent_id']}.config.json").read_text(encoding="utf-8"))
        launcher.check_sources(report_config(snapshot["config"]))
        records = launcher.run_screening(snapshot["agent"], snapshot["config"], snapshot["query_ids"], max_new=0,
                                         check_identity=lambda: None)
        if len(records) != 20:
            raise ValueError(f"{row['agent_id']}: {len(records)}/20 episodes saved; run phase incomplete")
        metrics = []
        for record in records:
            query = refs[record["query_id"]]
            metric = agent_metrics(record, query, mapping[query["relation_type"]], targets[record["query_id"]],
                                   kg, degrees, consistent=status[record["query_id"]] == "CONSISTENT")
            launcher.pin_manifest(DIAG / row["agent_id"] / "metrics" / f"{record['query_id']}.json", metric)
            metrics.append(metric)
        launcher.pin_manifest(DIAG / row["agent_id"] / "final-run-hashes.json", {
            p.relative_to(ROOT).as_posix(): file_hash(p)
            for p in sorted((RUNS_ROOT / RUN_ID).glob(f"*__{row['agent_id']}__a1.json"))})
        summaries[row["agent_id"]] = model_summary(records, metrics, settings["num_ctx"])
        all_metrics.extend(metrics)
    violations = off_question_supported(all_metrics)
    report_sources = {p: file_hash(ROOT / p) for p in REPORT_ONLY}
    (DIAG / "summary.json").write_text(json.dumps({"summaries": summaries, "off_question_supported": violations,
                                                   "report_only_source_sha256": report_sources},
                                                  indent=2, sort_keys=True), encoding="utf-8")
    SUMMARY.write_text(render_markdown(RUN_ID, summaries, violations), encoding="utf-8")
    print(SUMMARY.read_text(encoding="utf-8"), flush=True)
    if violations:
        raise OffQuestionSupported(f"Answers both OFF_QUESTION and SUPPORTED: {violations}")


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("phase", choices=("preflight", "run", "report"))
    parser.add_argument("--agent", help="Limit preflight/run to one agent_id")
    args = parser.parse_args()
    launcher = load_launcher()
    panel = load_panel()
    selected = [(r, s) for r, s in panel if args.agent in (None, r["agent_id"])]
    if not selected:
        raise ValueError(f"Unknown agent {args.agent!r}")
    if args.phase in ("preflight", "run"):
        for row, settings in selected:
            snapshot_path = RUNS_ROOT / RUN_ID / f"{row['agent_id']}.config.json"
            if args.phase == "run" and snapshot_path.exists() and complete(row, json.loads(snapshot_path.read_text())):
                print(f"SKIP {row['agent_id']}: 20/20 episodes already saved", flush=True)
                continue
            print(f"PHASE {args.phase}: {row['agent_id']}", flush=True)
            execute(launcher, row, settings, args.phase)
    if args.phase == "run" and args.agent is None or args.phase == "report":
        report(launcher, panel)
    print(f"PHASE {args.phase} COMPLETE", flush=True)


if __name__ == "__main__":
    main()
