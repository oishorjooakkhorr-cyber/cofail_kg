"""Fresh authorized S20 block on the 5060 Ti; reuse protocol sections 9/19 and D3."""
import argparse
from collections import Counter
from datetime import datetime, timezone
import importlib.util
import hashlib
import json
from pathlib import Path
import subprocess

from cofail_kg.agents.ollama_client import OllamaClient
from cofail_kg.agents.prompts import prompt_sha256
from cofail_kg.evaluation.agent_metrics import agent_metrics
from cofail_kg.evaluation.screening import aggregate_model

ROOT = Path(__file__).resolve().parents[4]
OUT = Path(__file__).resolve().parent
BASE = "http://127.0.0.1:11435"
DIGEST = "dc35e8d9c6061baa6f0fa870975ab6932e2542b579b13ea0f199fa4bb7300c9c"
RUN_ID = "gemma4-5060ti-16k-20261028"


def guard_source(path, expected):
    data = path.read_bytes()
    assert expected in (hashlib.sha256(data).hexdigest(),
                        hashlib.sha256(data.replace(b"\r\n", b"\n")).hexdigest()), str(path)


def guard_runtime(ps, log):
    models = [m for m in ps["models"] if m["digest"] == DIGEST]
    assert len(models) == 1, ps
    model = models[0]
    assert model["context_length"] == 16384, model
    assert model["size"] > 0 and model["size_vram"] == model["size"], model
    assert "OLLAMA_KV_CACHE_TYPE:f16" in log, "Server cache setting differs"
    assert "K (f16):" in log and "V (f16):" in log, "Actual KV cache is not verified f16"
    assert "offloaded 43/43 layers to GPU" in log, "Full model layer residency unverified"


def resume_snapshot(snapshot, path):
    if path.exists():
        saved = json.loads(path.read_text())
        snapshot["config"]["git_commit"] = saved["config"]["git_commit"]
        assert snapshot == saved, "Pinned run configuration changed"
    return snapshot


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--prepare-only", action="store_true")
    parser.add_argument("--report-only", action="store_true")
    args = parser.parse_args()
    spec = importlib.util.spec_from_file_location("screening_launcher", ROOT / "scripts/20_screen_models.py")
    launcher = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(launcher)
    seed = json.loads((OUT.parent / "full-16k-20261020/Gemma4-E4B.manifest.json").read_text())
    agent, config, queries = seed["agent"], seed["config"], seed["query_ids"]
    for path, digest in config["source_sha256"].items():
        guard_source(ROOT / path, digest)
    # Windows checkout line endings differ; the new manifest pins actual bytes.
    config["source_sha256"] = {p: launcher.file_hash(ROOT / p) for p in config["source_sha256"]}
    assert agent["digest"] == DIGEST and agent["quantization"] == "Q4_K_M"
    assert prompt_sha256() == config["prompt_sha256"]
    ids = [json.loads(line)["query_id"] for line in (ROOT / "data/agent_inputs/screening.jsonl").read_text().splitlines()]
    assert queries == ids and len(queries) == len(set(queries)) == 20
    assert {k: config[k] for k in launcher.SETTINGS} == {**launcher.SETTINGS, "num_ctx": 16384}
    assert config["request_timeout_seconds"] == 120
    commit = subprocess.check_output(["git", "rev-parse", "HEAD"], cwd=ROOT, text=True).strip()
    dirty = bool(subprocess.check_output(["git", "status", "--porcelain"], cwd=ROOT, text=True))
    config.update(run_id=RUN_ID, runs_root=str(ROOT / "results/runs/screening-5060ti"),
                  agent_inputs=str(ROOT / "data/agent_inputs/screening.jsonl"),
                  cache_dir=str(ROOT / "data/cache"), base_url=BASE, git_commit=commit + ("-dirty" if dirty else ""))
    for path in [Path(__file__), ROOT / "data/cache/primekg_nodes.parquet", ROOT / "data/cache/primekg_edges.parquet"]:
        config["source_sha256"][path.relative_to(ROOT).as_posix()] = launcher.file_hash(path)
    assert config["source_sha256"]["data/cache/primekg_nodes.parquet"] == "ec43d05e4dd0570d73772a0289166360d90f3e1c79225f4ec840a5fd644dbb17"
    assert config["source_sha256"]["data/cache/primekg_edges.parquet"] == "129f2d881e7aa9a678341e3920e2bba0f2081c5fada1951a545e004fcb25289e"
    run_dir = Path(config["runs_root"]) / RUN_ID
    client = OllamaClient(think=False, timeout_seconds=120, base_url=BASE)
    snapshot = {"identity": seed["identity"], "agent": agent, "config": config, "query_ids": queries}
    baseline_path = OUT / "historical-hashes.json"
    if not baseline_path.exists():
        paths = [p for p in (ROOT / "results/runs").rglob("*") if p.is_file()]
        paths += [p for p in (ROOT / "results/diagnostics").rglob("*")
                  if p.is_file() and OUT not in p.parents and "__pycache__" not in p.parts
                  and "ministral_speed" not in p.parts]
        launcher.pin_manifest(baseline_path, {p.relative_to(ROOT).as_posix(): launcher.file_hash(p) for p in paths})
    baseline = json.loads(baseline_path.read_text())
    snapshot = resume_snapshot(snapshot, OUT / "manifest.json")

    def integrity():
        launcher.check_sources(config)
        for path, digest in baseline.items():
            assert launcher.file_hash(ROOT / path) == digest, path

    def check():
        integrity()
        assert client._request("GET", "/api/version")["version"] == "0.40.12"
        assert client.get_model_identity(agent["tag"]) == seed["identity"]
        ps = client._request("GET", "/api/ps")
        guard_runtime(ps, (OUT / "server.stderr.log").read_text(encoding="utf-8", errors="replace"))
        completed = len(list(run_dir.glob("*__Gemma4-E4B__a1.json")))
        sample = {"time": datetime.now(timezone.utc).isoformat(), "completed": completed, "ps": ps}
        sample["gpu"] = subprocess.check_output(["nvidia-smi", "--query-gpu=name,driver_version,memory.total,memory.used,memory.free", "--format=csv,noheader"], text=True).strip()
        with (OUT / "runtime-samples.jsonl").open("a", encoding="utf-8") as handle:
            handle.write(json.dumps(sample) + "\n")
        print(f"CHECKED {completed}/20; context 16384; f16 KV; full GPU", flush=True)

    integrity()
    if not args.report_only:
        synthetic = json.loads((OUT / "synthetic.json").read_text())
        calls = synthetic["message"]["tool_calls"]
        assert len(calls) == 1 and calls[0]["function"]["name"] == "add"
        assert calls[0]["function"]["arguments"] == {"a": 2, "b": 3}
        assert not synthetic["message"].get("thinking")
        check()
    launcher.pin_manifest(run_dir / "Gemma4-E4B.config.json", snapshot)
    launcher.pin_manifest(OUT / "manifest.json", snapshot)
    if args.prepare_only:
        print("PREPARED: immutable manifest, source/input/history checks and runtime guards passed", flush=True)
        return
    records = launcher.run_screening(agent, config, queries, max_new=0 if args.report_only else 20, check_identity=check)
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
               "historical_files_verified": len(baseline), "runtime": "0.40.12", "kv_cache": "f16"}
    integrity()
    launcher.pin_manifest(OUT / "summary.json", summary)
    launcher.pin_manifest(OUT / "final-run-hashes.json", {p.relative_to(ROOT).as_posix(): launcher.file_hash(p)
                                                           for p in run_dir.glob("*.json")})
    print(json.dumps(summary, indent=2), flush=True)
    print("COMPLETE 20/20", flush=True)


if __name__ == "__main__":
    main()
