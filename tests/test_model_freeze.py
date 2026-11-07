import copy
import json
from pathlib import Path

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
            "agent": {**identity, "agent_id": agent["agent_id"], "family": agent.get("evidence_family", agent["family"]),
                      "think": False}}


@pytest.fixture
def inputs():
    manifests = {a["agent_id"]: manifest(a) for a in mf.PANEL}
    identities = {k: dict(v["identity"]) for k, v in manifests.items()}
    return identities, manifests


def test_panel_matches_revised_protocol():
    """Protocol §9.1 v1.3.6 table (S21 re-freeze 2026-11-07)."""
    assert [a["agent_id"] for a in mf.PANEL] == ["Gemma4-12B", "Granite41-8B", "Ministral3-14B", "Cogito-14B"]
    assert [a["tag"] for a in mf.PANEL] == ["gemma4:12b", "ibm/granite4.1:8b", "ministral-3:14b", "cogito:14b"]
    assert [a["family"] for a in mf.PANEL] == ["Gemma", "Granite", "Mistral", "Qwen"]
    for agent in mf.PANEL:
        assert (agent["num_ctx"], agent["num_predict"], agent["kv_cache_type"], agent["request_timeout_seconds"],
                agent["flash_attention_env"]) == (32768, 8192, "f16", 240, "true")
    assert mf.PANEL[-1]["gpu_layers"] == ["47/49"]


def test_superseded_panel_is_unchanged():
    assert [a["agent_id"] for a in mf.PANEL_S21R1] == ["Ministral3-8B", "Gemma4-E4B", "Granite41-8B", "Qwen35-9B"]
    qwen = mf.PANEL_S21R1[-1]
    assert (qwen["num_ctx"], qwen["num_predict"], qwen["kv_cache_type"], qwen["request_timeout_seconds"]) == (8192, 4096, "f32", 120)
    assert (mf.MODELS_KEY, mf.SUPERSEDED_MODELS_KEY) == ("models_s21r2", "models")


def test_evidence_manifests_hold_frozen_panel():
    """The committed S20 evidence manifests agree with PANEL (identity used as the live identity)."""
    manifests = {a["agent_id"]: json.loads(Path(a["evidence_manifest"]).read_text(encoding="utf-8")) for a in mf.PANEL}
    rows = mf.build_models({k: m["identity"] for k, m in manifests.items()}, manifests)
    assert [r["family"] for r in rows] == ["Gemma", "Granite", "Mistral", "Qwen"]
    assert rows[-1]["digest"] == "d0cac86a23474d1ed5c455a667879c8fbaf160440f7433e738eab814ae3316e0"


def test_build_models_rows_in_agent_order(inputs):
    rows = mf.build_models(*inputs)
    assert [r["agent_id"] for r in rows] == [a["agent_id"] for a in mf.PANEL]
    assert rows[2] == {"agent_id": "Ministral3-14B", "tag": "ministral-3:14b", "digest": "d-Ministral3-14B",
                       "quantization": "Q4_K_M", "parameter_size": "8B", "family": "Mistral"}
    assert mf.frozen_models_entry(rows)["Cogito-14B"] == {"tag": "cogito:14b", "digest": "d-Cogito-14B"}


def test_frozen_family_is_researcher_label_but_evidence_label_is_checked(inputs):
    identities, manifests = inputs
    assert manifests["Cogito-14B"]["agent"]["family"] == "UNVERIFIED-qwen2-architecture"
    assert mf.build_models(identities, manifests)[-1]["family"] == "Qwen"
    manifests["Cogito-14B"]["agent"]["family"] = "Qwen"
    with pytest.raises(ValueError, match="family"):
        mf.build_models(identities, manifests)


def test_installed_digest_must_equal_evidence(inputs):
    identities, manifests = inputs
    identities["Gemma4-12B"]["digest"] = "other"
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
    manifests["Cogito-14B"]["runtime"] = {"kv_cache_type": "f32"}
    with pytest.raises(ValueError):
        mf.build_models(identities, manifests)
    manifests["Cogito-14B"]["runtime"] = {"kv_cache_type": "f16"}
    manifests["Cogito-14B"]["agent"]["think"] = True
    with pytest.raises(ValueError):
        mf.build_models(identities, manifests)


def test_runtime_section():
    runtime = mf.runtime_section()
    assert runtime["agent_order"] == [a["agent_id"] for a in mf.PANEL]
    assert {k: runtime[k] for k in ("temperature", "seed", "think", "budget", "page_size", "timeout_seconds")} == \
        {"temperature": 0, "seed": 42, "think": False, "budget": 30, "page_size": 50, "timeout_seconds": 600}
    assert runtime["agents"]["Gemma4-12B"]["gpu_layers"] == ["49/49", "5/5"]
    assert runtime["agents"]["Cogito-14B"]["evidence_run_id"] == "cogito14b-5060ti-32k-20261106"


def test_runtime_section_of_superseded_panel_matches_its_archive():
    archived = yaml.safe_load(Path("configs/superseded/s21r1/pilot_runtime.yaml").read_text(encoding="utf-8"))
    assert archived["runtime"] == mf.runtime_section(mf.PANEL_S21R1)


def test_replace_superseded(tmp_path):
    path, archive = tmp_path / "models.yaml", tmp_path / "old/models.yaml"
    path.write_text("old", encoding="utf-8")
    assert mf.replace_superseded(path, "new", archive) is True
    assert (path.read_text(encoding="utf-8"), archive.read_text(encoding="utf-8")) == ("new", "old")
    assert mf.replace_superseded(path, "new", archive) is False
    with pytest.raises(RuntimeError):
        mf.replace_superseded(path, "third", archive)
    assert (path.read_text(encoding="utf-8"), archive.read_text(encoding="utf-8")) == ("new", "old")


class FakeClient:
    def __init__(self, digests):
        self.digests = digests
        self.calls = []

    def get_model_identity(self, tag):
        self.calls.append(tag)
        return {"tag": tag, "digest": self.digests[tag]}


def write_frozen(path, models, key=mf.MODELS_KEY):
    path.write_text(yaml.safe_dump({key: models}), encoding="utf-8")


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


def test_verify_installed_reads_current_key_not_superseded(tmp_path):
    path = tmp_path / "frozen.yaml"
    write_frozen(path, {"A": {"tag": "a:1", "digest": "x"}}, key="models")
    with pytest.raises(mf.ModelDigestMismatch, match="models_s21r2"):
        mf.verify_installed(FakeClient({"a:1": "x"}), path)
    assert mf.verify_installed(FakeClient({"a:1": "x"}), path, key="models") == {"A": "x"}
