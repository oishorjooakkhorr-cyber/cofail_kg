"""S21: freeze the four agents and their runtime (protocol §9.1 as revised at S21, §3.4).

`freeze` writes configs/models.yaml, the `models` entry of configs/frozen_hashes.yaml (write-once)
and the `runtime` section of configs/pilot.yaml. `check` fails if any installed model's digest
differs from frozen_hashes.yaml. Neither selects a model.
"""
import argparse
import json
from pathlib import Path

import yaml

from cofail_kg.utils.model_freeze import (PANEL, build_models, dump_yaml, frozen_models_entry,
                                           runtime_section, verify_installed)
from cofail_kg.agents.ollama_client import OllamaClient
from cofail_kg.utils.frozen_hashes import write_once

ROOT = Path(__file__).resolve().parents[1]
FROZEN = ROOT / "configs/frozen_hashes.yaml"


def client():
    transport = yaml.safe_load((ROOT / "configs/ollama.yaml").read_text(encoding="utf-8"))
    # Identity lookups only; no generation request is sent.
    return OllamaClient(think=False, timeout_seconds=transport["request_timeout_seconds"],
                        base_url=transport["base_url"])


def freeze():
    ollama = client()
    identities = {a["agent_id"]: ollama.get_model_identity(a["tag"]) for a in PANEL}
    manifests = {a["agent_id"]: json.loads((ROOT / a["evidence_manifest"]).read_text(encoding="utf-8"))
                 for a in PANEL}
    rows = build_models(identities, manifests)
    models_path = ROOT / "configs/models.yaml"
    body = ("# S21 frozen agents — protocol §9.1 (revised at S21) and Gate D3. Written by\n"
            "# scripts/21_freeze_models.py from get_model_identity(); never edit by hand.\n"
            + dump_yaml({"agents": rows}))
    if models_path.read_text(encoding="utf-8").strip().startswith("# filled in at a later stage"):
        models_path.write_text(body, encoding="utf-8")
    elif models_path.read_text(encoding="utf-8") != body:
        raise RuntimeError(f"{models_path} already frozen with different content")
    write_once(FROZEN, "models", frozen_models_entry(rows))
    pilot_path = ROOT / "configs/pilot.yaml"
    pilot = yaml.safe_load(pilot_path.read_text(encoding="utf-8"))
    runtime = runtime_section()
    if "runtime" in pilot and pilot["runtime"] != runtime:
        raise RuntimeError(f"{pilot_path} already holds a different runtime section")
    pilot["runtime"] = runtime
    pilot_path.write_text(dump_yaml(pilot), encoding="utf-8")
    print(json.dumps({"models": rows, "runtime": runtime}, indent=2))


def check():
    observed = verify_installed(client(), FROZEN)
    for agent_id, digest in observed.items():
        print(f"OK {agent_id} {digest}")


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("phase", choices=("freeze", "check"))
    args = parser.parse_args()
    freeze() if args.phase == "freeze" else check()


if __name__ == "__main__":
    main()
