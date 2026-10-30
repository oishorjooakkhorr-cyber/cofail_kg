import copy

import pytest
import yaml

from cofail_kg.utils import model_freeze as mf


def manifest(agent):
    identity = {"tag": agent["tag"], "digest": "d-" + agent["agent_id"], "quantization": "Q4_K_M",
                "parameter_size": "8B", "capabilities": ["tools"]}
    config = {"run_id": agent["evidence_run_id"], "num_ctx": agent["num_ctx"], "num_predict": agent["num_predict"],
              "request_timeout_seconds": agent["request_timeout_seconds"], "temperature": 0, "seed": 42,
              "budget": 30, "page_size": 50, "timeout_seconds": 600}
    return {"identity": identity, "config": config,
            "agent": {**identity, "agent_id": agent["agent_id"], "family": agent["family"], "think": False}}


@pytest.fixture
def inputs():
    manifests = {a["agent_id"]: manifest(a) for a in mf.PANEL}
    identities = {k: dict(v["identity"]) for k, v in manifests.items()}
    return identities, manifests


def test_panel_matches_revised_protocol():
    assert [a["agent_id"] for a in mf.PANEL] == ["Ministral3-8B", "Gemma4-E4B", "Granite41-8B", "Qwen35-9B"]
    assert len({a["family"] for a in mf.PANEL}) == 4
    qwen = mf.PANEL[-1]
    assert (qwen["num_ctx"], qwen["num_predict"], qwen["kv_cache_type"], qwen["request_timeout_seconds"]) == (8192, 4096, "f32", 120)
    for agent in mf.PANEL[:3]:
        assert (agent["num_ctx"], agent["num_predict"], agent["kv_cache_type"], agent["request_timeout_seconds"]) == (32768, 8192, "f16", 240)


def test_build_models_rows_in_agent_order(inputs):
    rows = mf.build_models(*inputs)
    assert [r["agent_id"] for r in rows] == [a["agent_id"] for a in mf.PANEL]
    assert rows[0] == {"agent_id": "Ministral3-8B", "tag": "ministral-3:8b", "digest": "d-Ministral3-8B",
                       "quantization": "Q4_K_M", "parameter_size": "8B", "family": "Mistral"}
    assert mf.frozen_models_entry(rows)["Qwen35-9B"] == {"tag": "qwen3.5:9b", "digest": "d-Qwen35-9B"}


def test_installed_digest_must_equal_evidence(inputs):
    identities, manifests = inputs
    identities["Gemma4-E4B"]["digest"] = "other"
    with pytest.raises(mf.ModelDigestMismatch):
        mf.build_models(identities, manifests)


@pytest.mark.parametrize("key,value", [("num_ctx", 16384), ("num_predict", 4096), ("budget", 20),
                                       ("run_id", "other"), ("request_timeout_seconds", 120)])
def test_evidence_configuration_must_equal_frozen_values(inputs, key, value):
    identities, manifests = inputs
    manifests = copy.deepcopy(manifests)
    manifests["Granite41-8B"]["config"][key] = value
    with pytest.raises(ValueError):
        mf.build_models(identities, manifests)


def test_evidence_kv_cache_and_thinking_checked(inputs):
    identities, manifests = inputs
    manifests["Qwen35-9B"]["runtime"] = {"kv_cache_type": "f16"}
    with pytest.raises(ValueError):
        mf.build_models(identities, manifests)
    manifests["Qwen35-9B"]["runtime"] = {"kv_cache_type": "f32"}
    manifests["Qwen35-9B"]["agent"]["think"] = True
    with pytest.raises(ValueError):
        mf.build_models(identities, manifests)


def test_runtime_section():
    runtime = mf.runtime_section()
    assert runtime["agent_order"] == [a["agent_id"] for a in mf.PANEL]
    assert {k: runtime[k] for k in ("temperature", "seed", "think", "budget", "page_size", "timeout_seconds")} == \
        {"temperature": 0, "seed": 42, "think": False, "budget": 30, "page_size": 50, "timeout_seconds": 600}
    assert runtime["agents"]["Qwen35-9B"]["kv_cache_type"] == "f32"


class FakeClient:
    def __init__(self, digests):
        self.digests = digests
        self.calls = []

    def get_model_identity(self, tag):
        self.calls.append(tag)
        return {"tag": tag, "digest": self.digests[tag]}


def write_frozen(path, models):
    path.write_text(yaml.safe_dump({"models": models}), encoding="utf-8")


def test_verify_installed_passes_and_fails(tmp_path):
    path = tmp_path / "frozen.yaml"
    write_frozen(path, {"A": {"tag": "a:1", "digest": "x"}, "B": {"tag": "b:1", "digest": "y"}})
    client = FakeClient({"a:1": "x", "b:1": "y"})
    assert mf.verify_installed(client, path) == {"A": "x", "B": "y"}
    assert client.calls == ["a:1", "b:1"]
    with pytest.raises(mf.ModelDigestMismatch, match="B"):
        mf.verify_installed(FakeClient({"a:1": "x", "b:1": "changed"}), path)


def test_verify_installed_requires_models_entry(tmp_path):
    path = tmp_path / "frozen.yaml"
    path.write_text(yaml.safe_dump({"prompt": "p"}), encoding="utf-8")
    with pytest.raises(mf.ModelDigestMismatch):
        mf.verify_installed(FakeClient({}), path)
