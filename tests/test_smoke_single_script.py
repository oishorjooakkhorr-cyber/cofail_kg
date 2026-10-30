"""Offline checks for the S22 launcher; never starts a server or calls a model."""
import importlib.util
from pathlib import Path

import pytest
import yaml

ROOT = Path(__file__).resolve().parents[1]
spec = importlib.util.spec_from_file_location("smoke", ROOT / "scripts/22_smoke_single.py")
smoke = importlib.util.module_from_spec(spec)
spec.loader.exec_module(smoke)

QWEN = {"num_ctx": 8192, "num_predict": 4096, "kv_cache_type": "f32", "flash_attention_env": "inherited",
        "num_parallel": 1, "request_timeout_seconds": 120}
GRANITE = {**QWEN, "num_ctx": 32768, "kv_cache_type": "f16", "flash_attention_env": "true"}


def qwen_log():
    return ("OLLAMA_FLASH_ATTENTION:false OLLAMA_KV_CACHE_TYPE:f32\n"
            "load_tensors: offloaded 33/33 layers to GPU\n"
            "llama_kv_cache: size =  512.00 MiB (8192 cells), K (f32):  256.00 MiB, V (f32):  256.00 MiB\n"
            "warmup: flash attention is enabled\n")


def ps(digest="d", ctx=8192, size=10, vram=10):
    return {"models": [{"digest": digest, "context_length": ctx, "size": size, "size_vram": vram}]}


def test_guard_accepts_matching_runtime():
    smoke.guard_runtime(ps(), qwen_log(), "Qwen35-9B", "d", QWEN)


@pytest.mark.parametrize("state", [ps(digest="x"), ps(ctx=16384), ps(vram=9),
                                   {"models": []}, {"models": ps()["models"] * 2}])
def test_guard_rejects_ps_differences(state):
    with pytest.raises(AssertionError):
        smoke.guard_runtime(state, qwen_log(), "Qwen35-9B", "d", QWEN)


@pytest.mark.parametrize("old,new", [("K (f32)", "K (f16)"), ("KV_CACHE_TYPE:f32", "KV_CACHE_TYPE:f16"),
                                     ("33/33", "32/33"), ("FLASH_ATTENTION:false", "FLASH_ATTENTION:true"),
                                     ("warmup: flash attention is enabled", "")])
def test_guard_rejects_log_differences(old, new):
    with pytest.raises(AssertionError):
        smoke.guard_runtime(ps(), qwen_log().replace(old, new), "Qwen35-9B", "d", QWEN)


def test_guard_rejects_any_second_cache_of_other_type():
    log = qwen_log() + "llama_kv_cache: size = 1 MiB, K (f16): 1 MiB, V (f16): 1 MiB\n"
    with pytest.raises(AssertionError):
        smoke.guard_runtime(ps(), log, "Qwen35-9B", "d", QWEN)


def test_gemma_requires_speculative_evidence():
    log = ("OLLAMA_FLASH_ATTENTION:true OLLAMA_KV_CACHE_TYPE:f16 --flash-attn on "
           "offloaded 43/43 layers to GPU offloaded 5/5 layers to GPU --spec-type draft-mtp "
           "--spec-draft-n-max 3 --spec-draft-backend-sampling "
           "sha256-05612e54110f8f68bade01dfcc546cdc6914d11dde0b650a65f263f0f87bbbd2\n"
           "llama_kv_cache: size = 1 MiB, K (f16): 1 MiB, V (f16): 1 MiB\n")
    smoke.guard_runtime(ps(ctx=32768), log, "Gemma4-E4B", "d", GRANITE)
    with pytest.raises(AssertionError):
        smoke.guard_runtime(ps(ctx=32768), log.replace("--spec-draft-n-max 3", "--spec-draft-n-max 4"),
                            "Gemma4-E4B", "d", GRANITE)


def test_server_env():
    q = smoke.server_env({"OLLAMA_FLASH_ATTENTION": "true", "PATH": "p"}, QWEN)
    assert "OLLAMA_FLASH_ATTENTION" not in q and q["PATH"] == "p"
    assert (q["OLLAMA_KV_CACHE_TYPE"], q["OLLAMA_CONTEXT_LENGTH"], q["OLLAMA_NUM_PARALLEL"]) == ("f32", "8192", "1")
    assert q["OLLAMA_HOST"] == "127.0.0.1:11435"
    g = smoke.server_env({}, GRANITE)
    assert g["OLLAMA_FLASH_ATTENTION"] == "true" and g["OLLAMA_KV_CACHE_TYPE"] == "f16"
    with pytest.raises(ValueError):
        smoke.server_env({}, {**GRANITE, "flash_attention_env": "maybe"})


def write_configs(root, order=("A", "B"), frozen_digest="dA"):
    (root / "configs").mkdir()
    rows = [{"agent_id": a, "tag": a.lower() + ":1", "digest": "d" + a, "quantization": "Q4_K_M",
             "parameter_size": "8B", "family": "F" + a} for a in ("A", "B")]
    (root / "configs/models.yaml").write_text(yaml.safe_dump({"agents": rows}))
    runtime = {"temperature": 0, "seed": 42, "agent_order": list(order),
               "agents": {"A": {"num_ctx": 8192}, "B": {"num_ctx": 32768}}}
    (root / "configs/pilot.yaml").write_text(yaml.safe_dump({"seed": 42, "runtime": runtime}))
    frozen = {"models": {"A": {"tag": "a:1", "digest": frozen_digest}, "B": {"tag": "b:1", "digest": "dB"}}}
    (root / "configs/frozen_hashes.yaml").write_text(yaml.safe_dump(frozen))


def test_load_panel_merges_shared_and_agent_settings(tmp_path):
    write_configs(tmp_path)
    panel = smoke.load_panel(tmp_path)
    assert [r["agent_id"] for r, _ in panel] == ["A", "B"]
    assert panel[1][1] == {"temperature": 0, "seed": 42, "num_ctx": 32768}


@pytest.mark.parametrize("kwargs", [{"order": ("B", "A")}, {"frozen_digest": "other"}])
def test_load_panel_refuses_inconsistent_configs(tmp_path, kwargs):
    write_configs(tmp_path, **kwargs)
    with pytest.raises(ValueError):
        smoke.load_panel(tmp_path)


def test_real_panel_matches_frozen_protocol_values():
    panel = {r["agent_id"]: s for r, s in smoke.load_panel()}
    assert list(panel) == ["Ministral3-8B", "Gemma4-E4B", "Granite41-8B", "Qwen35-9B"]
    assert set(panel) == set(smoke.EXPECTED_LOG)
    assert panel["Qwen35-9B"]["kv_cache_type"] == "f32" and panel["Gemma4-E4B"]["num_ctx"] == 32768
    assert smoke.RUN_ID == "smoke_single_v135"


def test_report_config_exempts_only_summary_code():
    config = {"num_ctx": 1, "source_sha256": {"src/cofail_kg/agents/run_agent.py": "a",
              "src/cofail_kg/evaluation/smoke_summary.py": "b", "scripts/22_smoke_single.py": "c"}}
    assert smoke.report_config(config)["source_sha256"] == {"src/cofail_kg/agents/run_agent.py": "a"}
    assert len(config["source_sha256"]) == 3
