"""S25 panel runner: the four frozen agents on one manifest, one model at a time, then evaluation.

Usage (from the repository root):
    python scripts/25_run_panel.py run --manifest smoke --run-id smoke_panel
    python scripts/25_run_panel.py analyze --manifest smoke --run-id smoke_panel

`run` executes every (agent, query) in agent-major order (protocol §9.2): for each agent it starts the
agent's own isolated pinned Ollama 0.40.12 server with its frozen runtime (§9.1, configs/pilot.yaml),
checks the installed digest against frozen_hashes `models_s21r2` and every pinned input hash, guards
the runtime against the agent's S20 evidence block, runs the synthetic tool-call probe, then runs the
agent's episodes through `cofail_kg.agents.panel_runner`. Completed episodes (any §9.5 status) are
skipped, never rerun; records are write-once (§19). A progress file is rewritten after every episode.
When all episodes exist, `run` continues with `analyze`.

`analyze` (evaluation only, no inference) writes results/runs/<run_id>/analysis/: S16-S19 metrics,
S23 co-failure (§16) and S24 chance baselines (§17), each on all queries and again without
SOURCE_NAME_OVERLAP queries (§19.1), the reconstruction and kill-and-resume checks (§19.1), the
OFF_QUESTION-and-SUPPORTED check, and the §19.1 audit sheet results/runs/<run_id>/audit_sheet.csv.
"""
import argparse
import csv
from datetime import datetime, timezone
import importlib.util
import io
import json
import os
from pathlib import Path
import subprocess
import sys
import time

from cofail_kg.agents.kg_env import load_overlays
from cofail_kg.agents.ollama_client import OllamaClient
from cofail_kg.agents.panel_runner import (check_hashes, check_identity, episode_plan, manifest_query_ids,
                                           progress, run_agent_block, write_progress)
from cofail_kg.agents.prompts import prompt_sha256
from cofail_kg.agents.trace import load_episode_record, record_path, verify_reconstruction
from cofail_kg.kg.prepare import file_hash
from cofail_kg.utils.frozen_hashes import read_frozen_hashes

ROOT = Path(__file__).resolve().parents[1]
RUNS_ROOT = ROOT / "results/runs"
MANIFESTS = ("smoke", "pilot", "expansion", "repeat8", "intervention_smoke", "intervention5")
# Phase J RP (decision log 2026-11-12, section D) and Phase 2 (section A): these manifests' hashes live in
# their own write-once keys, because the `manifests` key is itself write-once (scripts/44_make_repeat8.py,
# scripts/46_intervention_inputs.py).
EXTRA_MANIFEST_KEYS = ("manifests_repeat8", "manifests_intervention")
# Phase 2 runs (S34/S35): every episode uses the S33 overlay file, pinned by its frozen hash (§10, §21).
OVERLAY_MANIFESTS = ("intervention_smoke", "intervention5")
OVERLAY_FILE = "data/agent_inputs/intervention_overlays.jsonl"
OTHER_EXPERIMENTS = ("20_screen_models", "20_shared_resources", "run_model.py", "22_smoke_single")


def load_script(name, filename):
    spec = importlib.util.spec_from_file_location(name, ROOT / "scripts" / filename)
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


S22 = load_script("s22_driver", "22_smoke_single_s21r2.py")  # frozen runtime guards and server setup
LAUNCHER = load_script("screening_launcher", "20_screen_models.py")  # pin_manifest, load_evaluator


def pinned_inputs(manifest):
    """Frozen hashes this manifest's run depends on (configs/frozen_hashes.yaml)."""
    frozen = read_frozen_hashes(ROOT / "configs/frozen_hashes.yaml")
    sheet, processed = f"data/agent_inputs/{manifest}.jsonl", f"data/processed/manifests/{manifest}.jsonl"
    entries = dict(frozen["manifests"])
    for key in EXTRA_MANIFEST_KEYS:
        clash = set(entries) & set(frozen.get(key, {}))
        if clash:
            raise ValueError(f"configs/frozen_hashes.yaml: {sorted(clash)} in both `manifests` and `{key}`")
        entries.update(frozen.get(key, {}))
    required = {sheet: entries[sheet], processed: entries[processed],
                "data/cache/primekg_metadata.json": frozen["kg_fingerprint"],
                "src/cofail_kg/agents/tool_schemas.py": frozen["tools"],
                "results/semantics/relation_mapping.json": frozen["relation_mapping"]}
    if manifest in OVERLAY_MANIFESTS:
        required[OVERLAY_FILE] = frozen["intervention_overlays"][OVERLAY_FILE]
    return frozen, required


def build_config(manifest, run_id, row, settings, identity):
    """Pin this agent's run configuration once; a resume must reproduce it exactly."""
    frozen, required = pinned_inputs(manifest)
    check_hashes(required, ROOT)
    if prompt_sha256() != frozen["prompt"]:
        raise ValueError("Prompt template differs from frozen_hashes `prompt`")
    sheet = ROOT / f"data/agent_inputs/{manifest}.jsonl"
    query_ids = manifest_query_ids(sheet)
    processed = [json.loads(line)["query_id"] for line in
                 (ROOT / f"data/processed/manifests/{manifest}.jsonl").read_text(encoding="utf-8").splitlines()]
    if query_ids != processed:
        raise ValueError(f"{manifest}: agent-input sheet and manifest list different queries")
    check_identity(row | {"think": settings["think"]}, identity)
    sources = sorted({*required, "configs/frozen_hashes.yaml", "configs/pilot.yaml", "configs/models.yaml",
                      "docs/frozen_pilot_protocol.md", "docs/decision_rules.md", "scripts/25_run_panel.py",
                      "scripts/22_smoke_single_s21r2.py", "scripts/20_screen_models.py",
                      *[p.relative_to(ROOT).as_posix() for p in (ROOT / "src/cofail_kg").rglob("*.py")]})
    commit = subprocess.check_output(["git", "rev-parse", "HEAD"], cwd=ROOT, text=True).strip()
    dirty = bool(subprocess.check_output(["git", "status", "--porcelain", "--untracked-files=no"],
                                         cwd=ROOT, text=True))
    config = {k: settings[k] for k in ("temperature", "seed", "num_ctx", "num_predict", "page_size", "budget",
                                       "timeout_seconds", "request_timeout_seconds")}
    config.update(run_id=run_id, manifest=manifest, runs_root=str(RUNS_ROOT), agent_inputs=str(sheet),
                  agent_inputs_sha256=required[f"data/agent_inputs/{manifest}.jsonl"],
                  cache_dir=str(ROOT / "data/cache"), prompt_sha256=frozen["prompt"],
                  tool_schema_sha256=frozen["tools"], kg_fingerprint=frozen["kg_fingerprint"],
                  biohopr_revision=frozen["biohopr_revision"], git_commit=commit + ("-dirty" if dirty else ""),
                  base_url=S22.BASE, source_sha256={p: file_hash(ROOT / p) for p in sources})
    if manifest in OVERLAY_MANIFESTS:
        overlays = load_overlays(ROOT / OVERLAY_FILE)
        missing = [q for q in query_ids if q not in overlays]
        if missing:
            raise ValueError(f"{manifest}: no overlay for {missing}")
        config.update(overlay_path=str(ROOT / OVERLAY_FILE), overlay_sha256=required[OVERLAY_FILE])
    agent = {**identity, "agent_id": row["agent_id"], "family": row["family"], "think": settings["think"]}
    runtime = {k: settings[k] for k in ("ollama_version", "kv_cache_type", "flash_attention_env", "num_parallel",
                                        "evidence_run_id", "gpu_layers")}
    runtime["executable_sha256"] = S22.OLLAMA_SHA256
    snapshot = {"identity": identity, "agent": agent, "config": config, "query_ids": query_ids, "runtime": runtime}
    path = RUNS_ROOT / run_id / "configs" / f"{row['agent_id']}.config.json"
    if path.exists():
        pinned = json.loads(path.read_text(encoding="utf-8"))
        if pinned["config"]["git_commit"] != config["git_commit"]:
            # §19 code-change rule: stop; a different commit needs a decision-log entry and a new run ID.
            raise ValueError(f"Commit changed during run {run_id}: pinned {pinned['config']['git_commit']}, "
                             f"now {config['git_commit']}. Stop (protocol §19 code-change rule).")
    LAUNCHER.pin_manifest(path, snapshot)
    return snapshot


def competing_processes(folder, phase, stamp):
    processes = subprocess.check_output(["powershell", "-NoProfile", "-Command",
        "Get-CimInstance Win32_Process | Where-Object { $_.Name -match 'ollama|python' } | "
        "Select-Object ProcessId,Name,CommandLine | ConvertTo-Json -Compress"], text=True)
    (folder / f"processes-{phase}-{stamp}.json").write_text(processes, encoding="utf-8")
    if "llama-server" in processes or "11435" in processes:
        raise RuntimeError("Competing model process (llama-server or port 11435) is running")
    for name in OTHER_EXPERIMENTS:
        if name in processes:
            raise RuntimeError(f"Another experiment is running: {name}")


def run_agent(manifest, run_id, row, settings, plan, progress_path, total_halfway):
    """One agent: isolated server, guards, probe, episodes; the server is always stopped."""
    folder = RUNS_ROOT / run_id / "runtime" / row["agent_id"]
    folder.mkdir(parents=True, exist_ok=True)
    stamp = datetime.now(timezone.utc).strftime("%Y%m%dT%H%M%SZ")
    competing_processes(folder, "run", stamp)
    client = OllamaClient(think=settings["think"], timeout_seconds=settings["request_timeout_seconds"],
                          base_url=S22.BASE)
    if file_hash(S22.OLLAMA) != S22.OLLAMA_SHA256:
        raise RuntimeError("Pinned Ollama 0.40.12 executable changed")
    log_path = folder / f"server-{stamp}.stderr.log"
    with (folder / f"server-{stamp}.stdout.log").open("ab") as stdout, log_path.open("ab") as stderr:
        server = subprocess.Popen([str(S22.OLLAMA), "serve"], env=S22.server_env(os.environ, settings),
                                  stdout=stdout, stderr=stderr, creationflags=subprocess.CREATE_NO_WINDOW)
        try:
            version = None
            for _ in range(60):
                if server.poll() is not None:
                    raise RuntimeError("Isolated Ollama exited during startup")
                try:
                    version = client._request("GET", "/api/version")
                    break
                except Exception as error:  # noqa: BLE001 — startup polling; logged below if it never comes up
                    last = error
                    time.sleep(1)
            if version is None:
                raise RuntimeError(f"Isolated server did not become ready: {last}")
            if version["version"] != settings["ollama_version"]:
                raise RuntimeError(f"Ollama version {version} != {settings['ollama_version']}")
            snapshot = build_config(manifest, run_id, row, settings, client.get_model_identity(row["tag"]))
            agent, config = snapshot["agent"], snapshot["config"]

            def check():
                LAUNCHER.check_sources(config)
                check_identity(agent, client.get_model_identity(agent["tag"]))
                ps = client._request("GET", "/api/ps")
                S22.guard_runtime(ps, log_path.read_text(encoding="utf-8", errors="replace"),
                                  agent["agent_id"], agent["digest"], settings)
                memory, gpu = S22.system_sample()
                with (folder / "runtime-samples.jsonl").open("a", encoding="utf-8") as handle:
                    handle.write(json.dumps({"time": datetime.now(timezone.utc).isoformat(), "ps": ps,
                                             "memory": memory, "gpu": gpu}) + "\n")

            def on_episode(query_id, record, new):
                state = progress(RUNS_ROOT, run_id, plan)
                write_progress(progress_path, state)
                tag = "DONE" if new else "SKIP (already completed)"
                print(f"{tag} {agent['agent_id']} {query_id} status={record['status']} | PROGRESS "
                      f"{state['episodes_done']}/{state['episodes_total']} episodes, "
                      f"{state['failures_so_far']} failures", flush=True)
                if new and state["episodes_done"] == total_halfway:
                    print("=" * 72 + f"\nHALFWAY: {total_halfway}/{state['episodes_total']} episodes saved. "
                          "Press Ctrl+C now for the kill-and-resume test.\n" + "=" * 72, flush=True)

            S22.synthetic(client, agent["tag"], settings, folder, f"synthetic-{stamp}")
            check()
            run_agent_block(agent, config, snapshot["query_ids"], check=check, on_episode=on_episode)
        finally:
            if server.poll() is None:
                try:
                    result = client._request("POST", "/api/generate", json={"model": row["tag"], "keep_alive": 0})
                    (folder / f"unload-{stamp}.json").write_text(json.dumps(result, indent=2), encoding="utf-8")
                finally:
                    server.terminate()
                    server.wait(timeout=30)


def report_only(path):
    """Evaluation-only code: never used by inference, so analysis may run after a fix to it."""
    return path == "scripts/25_run_panel.py" or path.startswith("src/cofail_kg/evaluation/")


def check_inference_sources(config):
    """Every pinned source that inference used must be unchanged before analysis."""
    LAUNCHER.check_sources({**config, "source_sha256": {p: h for p, h in config["source_sha256"].items()
                                                        if not report_only(p)}})


def run(manifest, run_id):
    panel = S22.load_panel()
    agent_ids = [row["agent_id"] for row, _ in panel]
    query_ids = manifest_query_ids(ROOT / f"data/agent_inputs/{manifest}.jsonl")
    plan = episode_plan(agent_ids, query_ids)
    progress_path = RUNS_ROOT / run_id / "progress.json"
    state = progress(RUNS_ROOT, run_id, plan)
    write_progress(progress_path, state)
    print(f"RUN {run_id}: manifest {manifest}, {len(query_ids)} queries x {len(agent_ids)} agents = "
          f"{len(plan)} episodes; {state['episodes_done']} already completed", flush=True)
    for row, settings in panel:
        mine = [q for a, q in plan if a == row["agent_id"]]
        if all(record_path(RUNS_ROOT, run_id, q, row["agent_id"], 1).exists() for q in mine):
            print(f"SKIP agent {row['agent_id']}: all {len(mine)} episodes already completed", flush=True)
            continue
        print(f"AGENT {row['agent_id']}: starting isolated server", flush=True)
        run_agent(manifest, run_id, row, settings, plan, progress_path, len(plan) // 2)
    state = progress(RUNS_ROOT, run_id, plan)
    write_progress(progress_path, state)
    if state["episodes_done"] != len(plan):
        raise RuntimeError(f"Run incomplete: {state['episodes_done']}/{len(plan)}")
    print(f"RUN COMPLETE: {state['episodes_done']}/{len(plan)} episodes, {state['failures_so_far']} failures",
          flush=True)


def analyze(manifest, run_id):
    from cofail_kg.evaluation.agent_metrics import agent_metrics
    from cofail_kg.evaluation.cofailure import pairwise_agreement, query_cofailure
    from cofail_kg.evaluation.null_models import aggregate, agent_pools, query_nulls
    from cofail_kg.evaluation.panel_analysis import AUDIT_COLUMNS, audit_rows, audit_selection, completeness
    from cofail_kg.evaluation.smoke_summary import off_question_supported

    panel = S22.load_panel()
    agents = [row["agent_id"] for row, _ in panel]
    query_ids = manifest_query_ids(ROOT / f"data/agent_inputs/{manifest}.jsonl")
    plan = episode_plan(agents, query_ids)
    run_dir = RUNS_ROOT / run_id
    out = run_dir / "analysis"
    files = sorted(p.name for p in run_dir.glob("*__*__a*.json"))
    complete = completeness(plan, files)
    if not complete["pass"]:
        raise RuntimeError(f"Kill-and-resume check failed: {complete}")
    for row, _ in panel:
        pinned = json.loads((run_dir / "configs" / f"{row['agent_id']}.config.json").read_text(encoding="utf-8"))
        check_inference_sources(pinned["config"])
    refs, targets, mapping, status, kg, degrees = LAUNCHER.load_evaluator()
    entries = {json.loads(line)["query_id"]: json.loads(line) for line in
               (ROOT / f"data/processed/manifests/{manifest}.jsonl").read_text(encoding="utf-8").splitlines()}
    overlap = {q["query_id"] for q in json.loads((ROOT / "results/diagnostics/s15/source_name_overlap.json")
                                                 .read_text(encoding="utf-8"))["flagged_queries"]}
    records, rows, reconstruction = {}, {}, []
    for agent, q in plan:
        path = record_path(RUNS_ROOT, run_id, q, agent, 1)
        record = load_episode_record(path)  # includes the §19.1 reconstruction check
        verify_reconstruction(record)
        reconstruction.append({"episode": path.name, "pass": True})
        ref = refs[q]
        metric = agent_metrics(record, ref, mapping[ref["relation_type"]], targets[q], kg, degrees,
                               consistent=status[q] == "CONSISTENT")
        LAUNCHER.pin_manifest(out / "metrics" / agent / f"{q}.json", metric)
        records[(agent, q)], rows[(agent, q)] = record, metric
    types = {}

    def node_type(x):
        if x not in types:
            types[x] = kg.get_node(x)["type"]
        return types[x]

    cof, nulls = [], []
    for q in sorted(query_ids):
        ref = refs[q]
        qrows = [rows[(a, q)] for a in agents]
        cof.append(query_cofailure(ref, mapping[ref["relation_type"]], entries[q]["ambiguity_tag"], qrows,
                                   degrees, agents))
        nulls.append(query_nulls(ref, [{"record": records[(a, q)], "row": rows[(a, q)],
                                        "pools": agent_pools(records[(a, q)], rows[(a, q)], ref,
                                                             mapping[ref["relation_type"]], node_type)}
                                       for a in agents], agents))
    keys = ("question", "grounded", "hop1_clean", "benchmark")

    def totals(results):
        t = {f"{k}_{n}": sum(r[k][n] for r in results) for k in keys for n in ("cf3", "cf4")}
        t.update({k: sum(r[k] for r in results) for k in
                  ("pcf_rel3", "pcf_rel4", "pcf_node3", "pcf_node4", "pcf_shortcut3")})
        return t

    no_overlap = [r for r in cof if r["query_id"] not in overlap]
    LAUNCHER.pin_manifest(out / "cofailure.json", {
        "run_id": run_id, "agent_order": agents, "source_name_overlap_queries": sorted(overlap & set(query_ids)),
        "totals_all_queries": totals(cof), "totals_without_source_name_overlap": totals(no_overlap),
        "pairwise_all_queries": pairwise_agreement(cof, agents),
        "pairwise_without_source_name_overlap": pairwise_agreement(no_overlap, agents), "queries": cof})
    LAUNCHER.pin_manifest(out / "nulls.json", {
        "run_id": run_id, "agent_order": agents, "trials": len(nulls[0]["indicators"]["N1"]),
        "aggregate_all_queries": aggregate(nulls),
        "aggregate_without_source_name_overlap": aggregate(nulls, include=lambda r: r["query_id"] not in overlap),
        "aggregate_excluding_technical_failures": aggregate(nulls, include=lambda r: not r["technical_failure_agents"]),
        "queries": [n["result"] for n in nulls]})
    violations = off_question_supported(list(rows.values()))
    statuses = {}
    for record in records.values():
        statuses[record["status"]] = statuses.get(record["status"], 0) + 1
    selection = audit_selection(list(rows.values()), agents)
    sheet = audit_rows(selection, rows, records)
    audit_path = run_dir / "audit_sheet.csv"
    buffer = io.StringIO(newline="")
    writer = csv.DictWriter(buffer, fieldnames=AUDIT_COLUMNS, lineterminator="\n")
    writer.writeheader()
    writer.writerows(sheet)
    if audit_path.exists():  # write-once; the researcher fills the my_* columns in place
        existing = list(csv.DictReader(audit_path.open(encoding="utf-8", newline="")))
        machine = [{k: r[k] for k in AUDIT_COLUMNS if not k.startswith("my_") and k != "notes"} for r in existing]
        if machine != [{k: r[k] for k in AUDIT_COLUMNS if not k.startswith("my_") and k != "notes"} for r in sheet]:
            raise ValueError(f"Existing audit sheet differs from this analysis: {audit_path}")
    else:
        with audit_path.open("x", encoding="utf-8", newline="") as handle:
            handle.write(buffer.getvalue())
    success = statuses.get("SUCCESS", 0)
    verification = {
        "run_id": run_id, "episodes": len(plan), "status_counts": dict(sorted(statuses.items())),
        "kill_and_resume": complete, "reconstruction": {"checked": len(reconstruction),
                                                        "pass": all(r["pass"] for r in reconstruction)},
        "off_question_supported": violations,
        "every_episode_has_status": all(r["status"] in ("TIMEOUT", "ERROR", "PARSE_FAIL", "SUCCESS")
                                        for r in records.values()),
        "success_share": success / len(plan), "success_at_least_7_of_8": success * 8 >= 7 * len(plan),
        "audit_selection": [f"{q}__{a}__a1" for a, q in selection], "audit_answer_rows": len(sheet),
        "leakage_test": "run separately: pytest tests/test_leakage.py (see analysis/leakage_test.txt)",
        "manual_audit": "pending: researcher fills my_label_A / my_label_B in audit_sheet.csv"}
    LAUNCHER.pin_manifest(out / "verification.json", verification)
    print(json.dumps(verification, indent=2), flush=True)
    print("CO-FAILURE TOTALS (all queries):", json.dumps(totals(cof)), flush=True)
    for null, versions in aggregate(nulls).items():
        for version, s in versions.items():
            print(f"NULL {null} {version}: observed {s['observed_total']}, mean {s['null_mean']:.4f}, "
                  f"p95 {s['null_p95']}, p {s['p']:.4f}", flush=True)
    print(f"AUDIT SHEET: {audit_path} ({len(sheet)} answer rows from {len(selection)} episodes)", flush=True)
    if violations:
        raise RuntimeError(f"Answers both OFF_QUESTION and SUPPORTED: {violations}")


def main(argv=None):
    parser = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    parser.add_argument("phase", choices=("run", "analyze"))
    parser.add_argument("--manifest", required=True, choices=MANIFESTS)
    parser.add_argument("--run-id", required=True)
    args = parser.parse_args(argv)
    if args.phase == "run":
        run(args.manifest, args.run_id)
    analyze(args.manifest, args.run_id)
    print(f"PHASE {args.phase} COMPLETE", flush=True)


if __name__ == "__main__":
    sys.exit(main())
