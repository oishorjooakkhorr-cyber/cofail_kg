"""EXPLORATORY P2 side experiment (researcher request, 2026-11-05). Not a panel change; no gate input.

Researcher choices: P2 stays a draft outside the protocol (P1 remains frozen in prompts.py, §9.3 and
frozen_hashes.yaml); six configurations on the 20 screening queries, each with its own S20 runtime;
co-failure on all 15 four-agent panels with the frozen §16 code; Qwen 8K and 16K may share a panel,
flagged as the same weights (not independent, §9.2).

P2 differs from P1 only in rule 3 (final-message format). It is applied by replacing the template in
this process only; no frozen source file is edited. Records carry prompt_version "P2-draft:<sha256>".
The re-prompt, tools, parser and S16-S19 evaluators are unchanged.
Phases: preflight <cfg>, run <cfg>, report, cofailure. Write-once records, resume without reruns (§19).
"""
import argparse
from collections import Counter
from datetime import datetime, timezone
import hashlib
import importlib.util
from itertools import combinations
import json
import os
from pathlib import Path
import subprocess
import time

from cofail_kg.agents import prompts, run_agent
from cofail_kg.agents.ollama_client import OllamaClient
from cofail_kg.evaluation.agent_metrics import agent_metrics
from cofail_kg.evaluation.cofailure import pairwise_agreement, query_cofailure
from cofail_kg.evaluation.screening import aggregate_model
from cofail_kg.kg.prepare import file_hash
from cofail_kg.utils.frozen_hashes import read_frozen_hashes

ROOT = Path(__file__).resolve().parents[3]
OUT = Path(__file__).resolve().parent
RUN_ID = "p2-explore-20261105"
RUNS_ROOT = ROOT / "results/runs/p2-exploratory"
BASE = "http://127.0.0.1:11435"

P2_VERSION = "P2-draft"
P2_TEMPLATE = prompts.P1_TEMPLATE.replace(
    "3. When you are finished, reply with only this JSON object and nothing else:\n",
    "3. When you are finished, your final message must be only this JSON object, with no other text\n"
    "   before or after it, and it must list every entity in your answer:\n")
assert P2_TEMPLATE != prompts.P1_TEMPLATE, "P1 rule 3 text not found"
P2_SHA256 = hashlib.sha256(P2_TEMPLATE.encode("utf-8")).hexdigest()

SHARED = {"temperature": 0, "seed": 42, "page_size": 50, "budget": 30, "timeout_seconds": 600}
FULL = {"num_ctx": 32768, "num_predict": 8192, "kv_cache_type": "f16", "request_timeout_seconds": 240,
        "flash_attention_env": "true"}
# config id -> (tag, digest, family, guard key in 22_smoke_single.EXPECTED_LOG, runtime, evidence block)
CONFIGS = {
    "Ministral3-8B": ("ministral-3:8b", "1922accd5827ebe6829e536369195db25eaf664528dc66206d646ea3bb386b71",
                      "Mistral", "Ministral3-8B", FULL, "ministral3-5060ti-32k-resources-20261030"),
    "Gemma4-E4B": ("gemma4:e4b-it-q4_K_M", "dc35e8d9c6061baa6f0fa870975ab6932e2542b579b13ea0f199fa4bb7300c9c",
                   "Gemma", "Gemma4-E4B", FULL, "gemma4-5060ti-32k-resources-20261030"),
    "Granite41-8B": ("ibm/granite4.1:8b", "444af1c4b2fedd6b54041aca558e7300b0b3d5c0468c44619126240323ba2852",
                     "Granite", "Granite41-8B", FULL, "granite41-5060ti-32k-resources-20261030"),
    "Qwen35-9B-8K": ("qwen3.5:9b", "56671c2ab9385f9cfcb404638e32cd62d88e3501d44822208363c010179a3c90",
                     "Qwen", "Qwen35-9B", {"num_ctx": 8192, "num_predict": 4096, "kv_cache_type": "f32",
                                          "request_timeout_seconds": 120, "flash_attention_env": "inherited"},
                     "qwen35-5060ti-8k-f32-20261030"),
    "Qwen35-9B-16K": ("qwen3.5:9b", "56671c2ab9385f9cfcb404638e32cd62d88e3501d44822208363c010179a3c90",
                      "Qwen", "Qwen35-9B", {"num_ctx": 16384, "num_predict": 4096, "kv_cache_type": "f16",
                                           "request_timeout_seconds": 120, "flash_attention_env": "inherited"},
                      "qwen35-5060ti-16k-20261029"),
    "Ornith15-9B": ("ornith-1.5:9b", "e5df7dcdd8a263994df62d610317e07be0d6af23f96fcbd8543273058fce575e",
                    "UNVERIFIED-qwen35-architecture", "Ornith15-9B", FULL, "ornith15-5060ti-32k-20261031"),
}
ORDER = list(CONFIGS)
SAME_WEIGHTS = {"Qwen35-9B-8K", "Qwen35-9B-16K"}


def load(name, path):
    spec = importlib.util.spec_from_file_location(name, path)
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


def use_p2(launcher):
    """Swap the system template for this process only; validate_resume then expects P2 provenance."""
    run_agent.P1_TEMPLATE = P2_TEMPLATE
    run_agent.PROMPT_VERSION = P2_VERSION
    run_agent.prompt_sha256 = lambda: P2_SHA256
    launcher.PROMPT_VERSION = P2_VERSION


def settings_for(cfg):
    runtime = CONFIGS[cfg][4]
    return {**SHARED, **runtime, "ollama_version": "0.40.12", "num_parallel": 1, "think": False}


def snapshot_for(launcher, cfg, identity):
    tag, digest, family, _, _, evidence = CONFIGS[cfg]
    frozen = read_frozen_hashes(ROOT / "configs/frozen_hashes.yaml")
    required = {"data/agent_inputs/screening.jsonl": frozen["manifests"]["data/agent_inputs/screening.jsonl"],
                "data/processed/manifests/screening.jsonl": frozen["manifests"]["data/processed/manifests/screening.jsonl"],
                "data/cache/primekg_metadata.json": frozen["kg_fingerprint"],
                "src/cofail_kg/agents/tool_schemas.py": frozen["tools"],
                "results/semantics/relation_mapping.json": frozen["relation_mapping"]}
    if any(file_hash(ROOT / p) != h for p, h in required.items()) or prompts.prompt_sha256() != frozen["prompt"]:
        raise ValueError("Frozen screening sheet, KG, tools, mapping or P1 file differs")
    query_ids = [json.loads(line)["query_id"] for line in
                 (ROOT / "data/agent_inputs/screening.jsonl").read_text(encoding="utf-8").splitlines()]
    if identity["tag"] != tag or identity["digest"] != digest or "tools" not in identity["capabilities"]:
        raise ValueError(f"{cfg}: installed model differs from its S20 evidence identity")
    sources = sorted({*required, "configs/frozen_hashes.yaml", "docs/frozen_pilot_protocol.md",
                      "docs/decision_rules.md", "scripts/20_screen_models.py", "scripts/22_smoke_single.py",
                      "data/processed/reference_queries.parquet", "data/processed/reference_targets.parquet",
                      "data/processed/primary_population.csv", "data/processed/reference_summary.json",
                      *[p.relative_to(ROOT).as_posix() for p in OUT.glob("*.py")],
                      *[p.relative_to(ROOT).as_posix() for p in (ROOT / "src/cofail_kg").rglob("*.py")]})
    commit = subprocess.check_output(["git", "rev-parse", "HEAD"], cwd=ROOT, text=True).strip()
    dirty = bool(subprocess.check_output(["git", "status", "--porcelain"], cwd=ROOT, text=True))
    s = settings_for(cfg)
    config = {k: s[k] for k in ("temperature", "seed", "num_ctx", "num_predict", "page_size", "budget",
                                "timeout_seconds", "request_timeout_seconds")}
    config.update(run_id=RUN_ID, runs_root=str(RUNS_ROOT), agent_inputs=str(ROOT / "data/agent_inputs/screening.jsonl"),
                  agent_inputs_sha256=required["data/agent_inputs/screening.jsonl"], cache_dir=str(ROOT / "data/cache"),
                  prompt_sha256=P2_SHA256, tool_schema_sha256=frozen["tools"], kg_fingerprint=frozen["kg_fingerprint"],
                  biohopr_revision=frozen["biohopr_revision"], git_commit=commit + ("-dirty" if dirty else ""),
                  base_url=BASE, source_sha256={p: file_hash(ROOT / p) for p in sources})
    agent = {**identity, "agent_id": cfg, "family": family, "think": False}
    runtime = {k: s[k] for k in ("ollama_version", "kv_cache_type", "flash_attention_env", "num_parallel")}
    runtime.update(evidence_run_id=evidence, prompt=P2_VERSION, prompt_sha256=P2_SHA256,
                   prompt_text=P2_TEMPLATE, same_weights_as=sorted(SAME_WEIGHTS - {cfg}) if cfg in SAME_WEIGHTS else [])
    snapshot = {"identity": identity, "agent": agent, "config": config, "query_ids": query_ids, "runtime": runtime}
    path = RUNS_ROOT / RUN_ID / f"{cfg}.config.json"
    if path.exists():  # Resume keeps the original commit; anything else that changed stops the run.
        snapshot["config"]["git_commit"] = json.loads(path.read_text(encoding="utf-8"))["config"]["git_commit"]
    launcher.pin_manifest(path, snapshot)
    launcher.pin_manifest(OUT / cfg / "manifest.json", snapshot)
    return snapshot


def pin_history(launcher):
    """Hashes of every earlier result file, checked again before each episode (never overwrite history)."""
    history = OUT / "historical-hashes.json"
    if not history.exists():
        paths = [p for base in (ROOT / "results/runs", ROOT / "results/diagnostics") for p in base.rglob("*")
                 if p.is_file() and OUT not in p.parents and RUN_ID not in p.parts
                 and not any(part in p.parts for part in ("__pycache__", "ministral_speed"))]
        launcher.pin_manifest(history, {p.relative_to(ROOT).as_posix(): file_hash(p) for p in paths})
    return json.loads(history.read_text(encoding="utf-8"))


def execute(launcher, smoke, cfg, phase):
    """Start an isolated pinned server with the config's runtime, verify it, then preflight or run."""
    tag, digest, _, guard_key, _, _ = CONFIGS[cfg]
    settings = settings_for(cfg)
    folder = OUT / cfg
    folder.mkdir(parents=True, exist_ok=True)
    history = pin_history(launcher)
    stamp = datetime.now(timezone.utc).strftime("%Y%m%dT%H%M%SZ")
    processes = subprocess.check_output(["powershell", "-NoProfile", "-Command",
        "Get-CimInstance Win32_Process | Where-Object { $_.Name -match 'ollama|python' } | "
        "Select-Object ProcessId,Name,CommandLine | ConvertTo-Json -Compress"], text=True)
    (folder / f"processes-{phase}-{stamp}.json").write_text(processes, encoding="utf-8")
    assert "llama-server" not in processes and "11435" not in processes, "Competing model process"
    assert all(s not in processes for s in ("20_screen_models", "20_shared_resources", "22_smoke_single",
                                             "run_model.py")), "Another experiment is running"
    client = OllamaClient(think=False, timeout_seconds=settings["request_timeout_seconds"], base_url=BASE)
    try:
        client._request("GET", "/api/version")
    except Exception:
        pass
    else:
        raise AssertionError("Isolated port is already occupied")
    assert file_hash(smoke.OLLAMA) == smoke.OLLAMA_SHA256, "Pinned Ollama 0.40.12 executable changed"
    log_path = folder / f"server-{phase}-{stamp}.stderr.log"
    with (folder / f"server-{phase}-{stamp}.stdout.log").open("ab") as stdout, log_path.open("ab") as stderr:
        server = subprocess.Popen([str(smoke.OLLAMA), "serve"], env=smoke.server_env(os.environ, settings),
                                  stdout=stdout, stderr=stderr, creationflags=subprocess.CREATE_NO_WINDOW)
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
            snapshot = snapshot_for(launcher, cfg, client.get_model_identity(tag))
            agent, config = snapshot["agent"], snapshot["config"]

            def check():
                launcher.check_sources(config)
                for path, h in history.items():
                    assert file_hash(ROOT / path) == h, f"Historical file changed: {path}"
                assert client.get_model_identity(tag) == snapshot["identity"]
                ps = client._request("GET", "/api/ps")
                smoke.guard_runtime(ps, log_path.read_text(encoding="utf-8", errors="replace"), guard_key, digest,
                                    settings)
                done = len(list((RUNS_ROOT / RUN_ID).glob(f"*__{cfg}__a1.json")))
                memory, gpu = smoke.system_sample()
                with (folder / "runtime-samples.jsonl").open("a", encoding="utf-8") as handle:
                    handle.write(json.dumps({"time": datetime.now(timezone.utc).isoformat(), "phase": phase,
                                             "completed": done, "ps": ps, "memory": memory, "gpu": gpu}) + "\n")
                print(f"CHECKED {cfg} {done}/20; ctx {settings['num_ctx']}; {settings['kv_cache_type']} KV; "
                      f"full GPU; {P2_VERSION}", flush=True)

            smoke.synthetic(client, tag, settings, folder, f"synthetic-{phase}-{stamp}")
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
                    result = client._request("POST", "/api/generate", json={"model": tag, "keep_alive": 0})
                    (folder / f"unload-{phase}-{stamp}.json").write_text(json.dumps(result, indent=2), encoding="utf-8")
                finally:
                    server.terminate()
                    server.wait(timeout=30)


def report(launcher):
    """S16-S19 evaluation of every saved episode (unchanged evaluators), per-config D3-style rows."""
    refs, targets, mapping, status, kg, degrees = launcher.load_evaluator()
    rows = {}
    for cfg in ORDER:
        snapshot = json.loads((RUNS_ROOT / RUN_ID / f"{cfg}.config.json").read_text(encoding="utf-8"))
        launcher.check_sources(snapshot["config"])
        records = launcher.run_screening(snapshot["agent"], snapshot["config"], snapshot["query_ids"], max_new=0,
                                         check_identity=lambda: None)
        if len(records) != 20:
            raise ValueError(f"{cfg}: {len(records)}/20 episodes saved; run phase incomplete")
        metrics = []
        for record in records:
            if not record["prompt_version"].startswith(P2_VERSION + ":"):
                raise ValueError(f"{cfg}/{record['query_id']}: not a P2 record")
            query = refs[record["query_id"]]
            metric = agent_metrics(record, query, mapping[query["relation_type"]], targets[record["query_id"]],
                                   kg, degrees, consistent=status[record["query_id"]] == "CONSISTENT")
            launcher.pin_manifest(OUT / cfg / "metrics" / f"{record['query_id']}.json", metric)
            metrics.append(metric)
        agent = snapshot["agent"]
        identity = {k: agent[k] for k in ("tag", "digest", "quantization", "parameter_size", "family")}
        rows[cfg] = {"screening_row": aggregate_model(records, metrics, identity),
                     "status_counts": dict(sorted(Counter(r["status"] for r in records).items())),
                     "error_causes": dict(sorted(Counter(r["cause"] for r in records if r["status"] == "ERROR").items())),
                     "runtime": {k: v for k, v in snapshot["runtime"].items() if k != "prompt_text"}}
        launcher.pin_manifest(OUT / cfg / "final-run-hashes.json", {
            p.relative_to(ROOT).as_posix(): file_hash(p) for p in sorted((RUNS_ROOT / RUN_ID).glob(f"*__{cfg}__a1.json"))})
    launcher.pin_manifest(OUT / "summary.json", rows)
    for cfg, row in rows.items():
        r = row["screening_row"]
        print(cfg, row["status_counts"], f"competent {r['competent_episodes']}/20", f"d3_pass {r['d3_pass']}",
              f"median {r['median_wall_seconds']:.1f}s", f"largest prompt {r['largest_prompt_eval_count']}", flush=True)


def cofailure(launcher):
    """Frozen §16 on all 15 four-of-six panels, plus §16.4 pairwise for all 15 pairs."""
    refs, _, mapping, _, _, degrees = launcher.load_evaluator()
    manifest = [json.loads(line) for line in
                (ROOT / "data/processed/manifests/screening.jsonl").read_text(encoding="utf-8").splitlines()]
    metrics = {(cfg, e["query_id"]): json.loads((OUT / cfg / "metrics" / f"{e['query_id']}.json").read_text(encoding="utf-8"))
               for cfg in ORDER for e in manifest}
    keys = ("question", "grounded", "hop1_clean", "benchmark")
    panels = []
    for panel in combinations(ORDER, 4):
        results = []
        for e in manifest:
            ref = refs[e["query_id"]]
            results.append(query_cofailure(ref, mapping[ref["relation_type"]], e["ambiguity_tag"],
                                           [metrics[(cfg, e["query_id"])] for cfg in panel], degrees, list(panel)))
        totals = {f"{k}_{n}": sum(r[k][n] for r in results) for k in keys for n in ("cf3", "cf4")}
        totals.update({k: sum(r[k] for r in results) for k in
                       ("pcf_rel3", "pcf_rel4", "pcf_node3", "pcf_node4", "pcf_shortcut3")})
        panels.append({"panel": list(panel), "same_weights_in_panel": SAME_WEIGHTS <= set(panel),
                       "totals": totals, "queries": results})
    # W_Q of an agent does not depend on the panel; take it from any panel containing the agent.
    w = {}
    for p in panels:
        for r in p["queries"]:
            for cfg in p["panel"]:
                w.setdefault(r["query_id"], {})[cfg] = r["W_Q"][cfg]
    pairs = pairwise_agreement([{"query_id": q, "W_Q": v} for q, v in sorted(w.items())], ORDER)
    for pair in pairs:
        pair["same_weights"] = {pair["agent_i"], pair["agent_j"]} == SAME_WEIGHTS
    payload = {"note": "EXPLORATORY P2 side experiment; not a panel change, not a gate input; screening queries",
               "run_id": RUN_ID, "prompt": P2_VERSION, "prompt_sha256": P2_SHA256, "configs": ORDER,
               "panels": panels, "pairwise": pairs}
    launcher.pin_manifest(OUT / "cofailure.json", payload)
    for p in panels:
        t = p["totals"]
        print(" + ".join(p["panel"]), "| same-weights" if p["same_weights_in_panel"] else "",
              {k: v for k, v in t.items() if v}, flush=True)
    for x in pairs:
        print(x["agent_i"], x["agent_j"], f"{x['numerator']}/{x['denominator']}", x["agreement"],
              "(same weights)" if x["same_weights"] else "", flush=True)


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("phase", choices=("preflight", "run", "report", "cofailure"))
    parser.add_argument("--config", choices=ORDER)
    args = parser.parse_args()
    launcher = load("screening_launcher", ROOT / "scripts/20_screen_models.py")
    smoke = load("smoke_single", ROOT / "scripts/22_smoke_single.py")
    smoke.EXPECTED_LOG.setdefault("Ornith15-9B", ("offloaded 33/33 layers to GPU", "--flash-attn on"))
    use_p2(launcher)
    if args.phase in ("preflight", "run"):
        for cfg in [args.config] if args.config else ORDER:
            print(f"PHASE {args.phase}: {cfg}", flush=True)
            execute(launcher, smoke, cfg, args.phase)
    elif args.phase == "report":
        report(launcher)
    else:
        cofailure(launcher)
    print(f"PHASE {args.phase} COMPLETE", flush=True)


if __name__ == "__main__":
    main()
