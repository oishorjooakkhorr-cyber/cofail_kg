"""S21: freeze the four agents and their runtime (protocol §9.1 v1.3.6, S21 re-freeze; §3.4).

`freeze` writes configs/models.yaml, the `models_s21r2` entry of configs/frozen_hashes.yaml
(write-once) and the `runtime` section of configs/pilot.yaml. The superseded 2026-10-30 panel is kept:
its `models` entry in frozen_hashes.yaml is untouched, and its models.yaml and pilot.yaml runtime are
copied to configs/superseded/s21r1/ before being replaced (never overwritten afterwards).

Identities come from the live Ollama server (`--identities live`, default) or from the
get_model_identity() result recorded in each D3 evidence manifest (`--identities evidence`, for a
machine without the models). `check` fails if any installed model's digest differs from the
`models_s21r2` entry; run it on the inference host before S22. Neither selects a model.
"""
import argparse
import json
from pathlib import Path

import yaml

from cofail_kg.utils.model_freeze import (MODELS_KEY, PANEL, build_models, dump_yaml, frozen_models_entry,
                                           replace_superseded, runtime_section, verify_installed)
from cofail_kg.agents.ollama_client import OllamaClient
from cofail_kg.utils.frozen_hashes import write_once

ROOT = Path(__file__).resolve().parents[1]
FROZEN = ROOT / "configs/frozen_hashes.yaml"
SUPERSEDED = ROOT / "configs/superseded/s21r1"


def client():
    transport = yaml.safe_load((ROOT / "configs/ollama.yaml").read_text(encoding="utf-8"))
    # Identity lookups only; no generation request is sent.
    return OllamaClient(think=False, timeout_seconds=transport["request_timeout_seconds"],
                        base_url=transport["base_url"])


def freeze(identity_source):
    manifests = {a["agent_id"]: json.loads((ROOT / a["evidence_manifest"]).read_text(encoding="utf-8"))
                 for a in PANEL}
    if identity_source == "live":
        ollama = client()
        identities = {a["agent_id"]: ollama.get_model_identity(a["tag"]) for a in PANEL}
    else:
        identities = {agent_id: manifest["identity"] for agent_id, manifest in manifests.items()}
    rows = build_models(identities, manifests)
    body = ("# S21 frozen agents — protocol §9.1 (v1.3.6, S21 re-freeze 2026-11-07) and Gate D3.\n"
            f"# Written by scripts/21_freeze_models.py (identities: {identity_source}); never edit by hand.\n"
            "# Superseded 2026-10-30 panel: configs/superseded/s21r1/models.yaml.\n"
            + dump_yaml({"agents": rows}))
    replace_superseded(ROOT / "configs/models.yaml", body, SUPERSEDED / "models.yaml")
    write_once(FROZEN, MODELS_KEY, frozen_models_entry(rows))
    pilot_path = ROOT / "configs/pilot.yaml"
    pilot = yaml.safe_load(pilot_path.read_text(encoding="utf-8"))
    runtime = runtime_section()
    if pilot.get("runtime") != runtime:
        archive = SUPERSEDED / "pilot_runtime.yaml"
        previous = dump_yaml({"runtime": pilot.get("runtime")})
        if archive.exists():
            if archive.read_text(encoding="utf-8") != previous:
                raise RuntimeError(f"{pilot_path} runtime differs from both the new panel and {archive}")
        else:
            archive.parent.mkdir(parents=True, exist_ok=True)
            archive.write_text(previous, encoding="utf-8")
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
    parser.add_argument("--identities", choices=("live", "evidence"), default="live")
    args = parser.parse_args()
    freeze(args.identities) if args.phase == "freeze" else check()


if __name__ == "__main__":
    main()
