"""Authorized context diagnostic; reuse protocol sections 9/19 episode machinery."""

from datetime import datetime, timezone
import hashlib
import importlib.util
import json
from pathlib import Path
import subprocess

from cofail_kg.agents.ollama_client import OllamaClient


ROOT = Path(__file__).resolve().parents[4]
OUT = Path(__file__).resolve().parent


def main():
    spec = importlib.util.spec_from_file_location("screening_launcher", ROOT / "scripts/20_screen_models.py")
    launcher = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(launcher)
    snapshot = json.loads((OUT / "manifest.json").read_text(encoding="utf-8"))
    agent, config = snapshot["agent"], snapshot["config"]
    queries = snapshot["query_ids"]
    original = json.loads((ROOT / snapshot["original_manifest"]).read_text(encoding="utf-8"))
    assert {k for k in config if config[k] != original["config"][k]} == {"num_ctx", "run_id", "runs_root"}
    assert config["num_ctx"] == 16384 and agent == original["agent"]
    assert queries == ["BH2_03619", "BH2_03762", "BH2_03850", "BH2_03953"]
    assert Path(config["runs_root"]).resolve() != Path(original["config"]["runs_root"]).resolve()
    launcher.pin_manifest(OUT / "driver-identity.json", {
        "sha256": hashlib.sha256(Path(__file__).read_bytes()).hexdigest()})
    run_dir = Path(config["runs_root"]) / config["run_id"]
    launcher.pin_manifest(run_dir / "diagnostic.config.json", snapshot)
    client = OllamaClient(think=False, timeout_seconds=config["request_timeout_seconds"],
                          base_url=config["base_url"])

    def check():
        launcher.check_sources(config)
        for group in snapshot["integrity_groups"].values():
            for path, digest in group.items():
                assert hashlib.sha256((ROOT / path).read_bytes()).hexdigest() == digest, path
        assert client.get_model_identity(agent["tag"]) == snapshot["identity"]
        completed = len(list(run_dir.glob("*__Gemma4-E4B__a1.json")))
        ps = client._request("GET", "/api/ps")
        sample = {"timestamp": datetime.now(timezone.utc).isoformat(),
                  "completed": completed, "ps": ps,
                  "gpu": subprocess.check_output([
                      "nvidia-smi", "--query-gpu=name,memory.total,memory.used",
                      "--format=csv,noheader"], text=True).strip()}
        with (OUT / "runtime-samples.jsonl").open("a", encoding="utf-8") as handle:
            handle.write(json.dumps(sample) + "\n")
        if completed:
            assert any(m["digest"] == agent["digest"] and m["context_length"] == 16384
                       for m in ps["models"]), ps

    records = launcher.run_screening(agent, config, queries, max_new=4, check_identity=check)
    assert len(records) == 4
    print(json.dumps({"saved": len(records), "status_by_query": {
        r["query_id"]: r["status"] for r in records}}, indent=2), flush=True)
    print("COMPLETE: four diagnostic outcomes saved; official results unchanged.", flush=True)


if __name__ == "__main__":
    main()
