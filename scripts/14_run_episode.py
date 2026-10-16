"""Researcher launcher: one S14 example, first screening query, protocol §9.1 settings.

Run outside the restricted sandbox. Prompt approval/freezing is a separate
researcher decision after reviewing the saved episode. No model is downloaded.
"""

import argparse
import json
import os
from pathlib import Path
import subprocess
from tempfile import TemporaryDirectory

import yaml

from cofail_kg.agents.ollama_client import OllamaClient
from cofail_kg.agents.prompts import prompt_sha256
from cofail_kg.agents.run_agent import run_episode
from cofail_kg.agents.trace import load_episode_record, record_path
from cofail_kg.kg.prepare import file_hash
from cofail_kg.utils.frozen_hashes import read_frozen_hashes

ROOT = Path(__file__).resolve().parents[1]


def check_persistence(root):
    """Fail before a model call if this output directory cannot publish hard links."""
    root.mkdir(parents=True, exist_ok=True)
    with TemporaryDirectory(prefix=".s14-check-", dir=root) as temporary:
        source, target = Path(temporary) / "source", Path(temporary) / "target"
        source.write_bytes(b"S14 persistence check\n")
        os.link(source, target)
        if not source.samefile(target):
            raise RuntimeError("Hard-link identity check failed")
        try:
            os.link(source, target)
        except FileExistsError:
            pass
        else:
            raise RuntimeError("Existing hard-link destination was not refused")


def main(argv=None):
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--run-id", required=True, help="New ID; completed results are never overwritten")
    parser.add_argument("--think", choices=("true", "false"), required=True,
                        help="Researcher-selected thinking setting for this single example")
    parser.add_argument("--diagnostic-num-predict", type=int, default=4096,
                        help="Authorized diagnostic output cap; screening default remains 4096")
    parser.add_argument("--diagnostic-model", default="qwen3:4b",
                        help="Installed diagnostic model variant; default remains qwen3:4b")
    args = parser.parse_args(argv)
    if args.diagnostic_num_predict <= 0:
        parser.error("--diagnostic-num-predict must be positive")
    frozen = read_frozen_hashes(ROOT / "configs/frozen_hashes.yaml")
    sheet = ROOT / "data/agent_inputs/screening.jsonl"
    sheet_hash = frozen["manifests"]["data/agent_inputs/screening.jsonl"]
    if file_hash(sheet) != sheet_hash:
        raise ValueError("Screening sheet does not match its frozen hash")
    query_id = json.loads(sheet.read_text(encoding="utf-8").splitlines()[0])["query_id"]
    runs_root = ROOT / "results/runs"
    target = record_path(runs_root, args.run_id, query_id, "S14-qwen3-4b", 1)
    if target.exists():
        raise FileExistsError(f"Completed episode already exists: {target}")
    cache_dir = ROOT / "data/cache"
    if file_hash(cache_dir / "primekg_metadata.json") != frozen["kg_fingerprint"]:
        raise ValueError("PrimeKG metadata does not match its frozen fingerprint")
    if file_hash(ROOT / "src/cofail_kg/agents/tool_schemas.py") != frozen["tools"]:
        raise ValueError("Tool schema source does not match frozen T1")
    if "prompt" in frozen and frozen["prompt"] != prompt_sha256():
        raise ValueError("P1 template does not match its frozen hash")
    try:
        check_persistence(runs_root)
    except PermissionError as error:
        raise RuntimeError("Episode persistence is blocked; run on the host outside the restricted sandbox") from error
    transport = yaml.safe_load((ROOT / "configs/ollama.yaml").read_text(encoding="utf-8"))
    think = args.think == "true"
    client = OllamaClient(think=think, timeout_seconds=transport["request_timeout_seconds"],
                          base_url=transport["base_url"])
    identity = client.get_model_identity(args.diagnostic_model)
    if "tools" not in identity["capabilities"]:
        raise ValueError("The S13 test model must support native tools")
    commit = subprocess.check_output(["git", "rev-parse", "HEAD"], cwd=ROOT, text=True).strip()
    dirty = bool(subprocess.check_output(["git", "status", "--porcelain"], cwd=ROOT, text=True))
    sources = ["scripts/14_run_episode.py", "configs/ollama.yaml"]
    sources += [str(path.relative_to(ROOT)).replace("\\", "/")
                for path in sorted((ROOT / "src/cofail_kg").rglob("*.py"))]
    config = {
        "run_id": args.run_id, "agent_inputs": str(sheet), "agent_inputs_sha256": sheet_hash,
        "cache_dir": str(cache_dir), "runs_root": str(runs_root),
        "temperature": 0, "seed": 42, "num_ctx": 8192, "num_predict": args.diagnostic_num_predict,
        "page_size": 50, "budget": 30, "timeout_seconds": 600,
        "base_url": transport["base_url"], "request_timeout_seconds": transport["request_timeout_seconds"],
        "kg_fingerprint": frozen["kg_fingerprint"], "biohopr_revision": frozen["biohopr_revision"],
        "tool_schema_sha256": frozen["tools"], "git_commit": commit + ("-dirty" if dirty else ""),
        "source_sha256": {path: file_hash(ROOT / path) for path in sources},
        "draft_prompt": "prompt" not in frozen, "prompt_sha256": frozen.get("prompt"),
    }
    agent = {key: identity[key] for key in ("tag", "digest", "quantization")}
    agent.update(agent_id="S14-qwen3-4b", think=think)
    print(f"Starting {query_id} with {identity['tag']}, think={think}; output: {target}", flush=True)
    path = run_episode(query_id, agent, config)
    print(path, flush=True)
    identity_after = client.get_model_identity(identity["tag"])
    summary = {"record_path": str(path), "record_sha256": file_hash(path),
               "identity_before": identity, "identity_after": identity_after,
               "identity_stable": identity == identity_after,
               "status": load_episode_record(path)["status"]}
    evidence = ROOT / "results/diagnostics" / f"{args.run_id}_identity.json"
    with evidence.open("x", encoding="utf-8", newline="\n") as handle:
        json.dump(summary, handle, indent=2)
        handle.write("\n")
    print(json.dumps(summary, indent=2), flush=True)
    return 0 if summary["identity_stable"] and summary["status"] == "SUCCESS" else 1


if __name__ == "__main__":
    raise SystemExit(main())
