"""Frozen agent panel and runtime (protocol §9.1 final configuration, §3.4 `models` entry).

The four agents and their per-agent runtime are fixed by protocol §9.1 as revised at S21. Each
agent's identity comes from `OllamaClient.get_model_identity()` and must equal the identity pinned
in its D3 evidence manifest; nothing here selects or substitutes a model.
"""

from __future__ import annotations

from pathlib import Path
from typing import Any

import yaml

from cofail_kg.utils.frozen_hashes import read_frozen_hashes

S20 = Path("results/diagnostics/s20")
RESOURCES = S20 / "shared-resources-32k-20261030"

# Protocol §9.1 final configuration, in agent order (§9.2).
PANEL: tuple[dict[str, Any], ...] = (
    {"agent_id": "Ministral3-8B", "tag": "ministral-3:8b", "family": "Mistral",
     "evidence_run_id": "ministral3-5060ti-32k-resources-20261030",
     "evidence_manifest": RESOURCES / "ministral3/manifest.json",
     "num_ctx": 32768, "num_predict": 8192, "kv_cache_type": "f16", "request_timeout_seconds": 240,
     "flash_attention_env": "true"},
    {"agent_id": "Gemma4-E4B", "tag": "gemma4:e4b-it-q4_K_M", "family": "Gemma",
     "evidence_run_id": "gemma4-5060ti-32k-resources-20261030",
     "evidence_manifest": RESOURCES / "gemma4/manifest.json",
     "num_ctx": 32768, "num_predict": 8192, "kv_cache_type": "f16", "request_timeout_seconds": 240,
     "flash_attention_env": "true"},
    {"agent_id": "Granite41-8B", "tag": "ibm/granite4.1:8b", "family": "Granite",
     "evidence_run_id": "granite41-5060ti-32k-resources-20261030",
     "evidence_manifest": RESOURCES / "granite41/manifest.json",
     "num_ctx": 32768, "num_predict": 8192, "kv_cache_type": "f16", "request_timeout_seconds": 240,
     "flash_attention_env": "true"},
    {"agent_id": "Qwen35-9B", "tag": "qwen3.5:9b", "family": "Qwen",
     "evidence_run_id": "qwen35-5060ti-8k-f32-20261030",
     "evidence_manifest": S20 / "qwen35-5060ti-8k-f32-20261030/manifest.json",
     "num_ctx": 8192, "num_predict": 4096, "kv_cache_type": "f32", "request_timeout_seconds": 120,
     "flash_attention_env": "inherited"},
)
SHARED = {"ollama_version": "0.40.12", "temperature": 0, "seed": 42, "think": False,
          "budget": 30, "page_size": 50, "timeout_seconds": 600, "num_parallel": 1}
IDENTITY_KEYS = ("tag", "digest", "quantization", "parameter_size")


class ModelDigestMismatch(RuntimeError):
    """An installed model differs from the digest frozen in configs/frozen_hashes.yaml."""


def check_evidence(agent: dict[str, Any], manifest: dict[str, Any]) -> None:
    """The evidence manifest must name this agent and hold exactly its frozen runtime values."""
    config = manifest["config"]
    expected = {"run_id": agent["evidence_run_id"], "num_ctx": agent["num_ctx"],
                "num_predict": agent["num_predict"], "request_timeout_seconds": agent["request_timeout_seconds"],
                **{k: SHARED[k] for k in ("temperature", "seed", "budget", "page_size", "timeout_seconds")}}
    observed = {k: config.get(k) for k in expected}
    if observed != expected:
        raise ValueError(f"{agent['agent_id']}: evidence configuration {observed} != frozen {expected}")
    if manifest["agent"]["agent_id"] != agent["agent_id"] or manifest["agent"]["think"] is not SHARED["think"]:
        raise ValueError(f"{agent['agent_id']}: evidence agent differs: {manifest['agent']}")
    if manifest["agent"]["family"] != agent["family"] or manifest["agent"]["tag"] != agent["tag"]:
        raise ValueError(f"{agent['agent_id']}: evidence tag/family differs: {manifest['agent']}")
    runtime = manifest.get("runtime")
    if runtime is not None and runtime.get("kv_cache_type") != agent["kv_cache_type"]:
        raise ValueError(f"{agent['agent_id']}: evidence KV cache {runtime} != {agent['kv_cache_type']}")


def build_models(identities: dict[str, dict[str, Any]], manifests: dict[str, dict[str, Any]]) -> list[dict[str, Any]]:
    """models.yaml rows from live identities, each equal to its evidence manifest identity."""
    rows = []
    for agent in PANEL:
        identity = {k: identities[agent["agent_id"]][k] for k in IDENTITY_KEYS}
        pinned = {k: manifests[agent["agent_id"]]["identity"][k] for k in IDENTITY_KEYS}
        if identity != pinned:
            raise ModelDigestMismatch(f"{agent['agent_id']}: installed {identity} != evidence {pinned}")
        check_evidence(agent, manifests[agent["agent_id"]])
        rows.append({"agent_id": agent["agent_id"], **identity, "family": agent["family"]})
    return rows


def runtime_section() -> dict[str, Any]:
    agents = {a["agent_id"]: {k: a[k] for k in ("num_ctx", "num_predict", "kv_cache_type",
                                                  "request_timeout_seconds", "flash_attention_env",
                                                  "evidence_run_id")}
              for a in PANEL}
    return {**SHARED, "agent_order": [a["agent_id"] for a in PANEL], "agents": agents}


def frozen_models_entry(rows: list[dict[str, Any]]) -> dict[str, dict[str, str]]:
    return {row["agent_id"]: {"tag": row["tag"], "digest": row["digest"]} for row in rows}


def verify_installed(client: Any, frozen_path: Path | str) -> dict[str, str]:
    """Raise ModelDigestMismatch unless every frozen model is installed with its frozen digest."""
    frozen = read_frozen_hashes(frozen_path).get("models")
    if not frozen:
        raise ModelDigestMismatch(f"{frozen_path}: no frozen `models` entry")
    observed = {}
    for agent_id, pinned in sorted(frozen.items()):
        identity = client.get_model_identity(pinned["tag"])
        if identity["digest"] != pinned["digest"]:
            raise ModelDigestMismatch(f"{agent_id} ({pinned['tag']}): installed digest {identity['digest']} "
                                      f"!= frozen {pinned['digest']}")
        observed[agent_id] = identity["digest"]
    return observed


def dump_yaml(value: Any) -> str:
    return yaml.safe_dump(value, sort_keys=False, default_flow_style=False, allow_unicode=True)
