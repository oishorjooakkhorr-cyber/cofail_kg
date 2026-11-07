"""Offline checks for the S22 driver of the re-frozen panel; never starts a server or calls a model."""
import importlib.util
from pathlib import Path

import pytest
import yaml

ROOT = Path(__file__).resolve().parents[1]
spec = importlib.util.spec_from_file_location("smoke_r2", ROOT / "scripts/22_smoke_single_s21r2.py")
smoke = importlib.util.module_from_spec(spec)
spec.loader.exec_module(smoke)

BASE = {"num_ctx": 32768, "num_predict": 8192, "kv_cache_type": "f16", "flash_attention_env": "true",
        "num_parallel": 1, "request_timeout_seconds": 240}
GEMMA = {**BASE, "gpu_layers": ["49/49", "5/5"]}
MINISTRAL = {**BASE, "gpu_layers": ["41/41"]}
COGITO = {**BASE, "gpu_layers": ["47/49"]}
GEMMA_FLAGS = ("--no-jinja --chat-template chatml --spec-type draft-mtp --spec-draft-n-max 3 "
               "--spec-draft-backend-sampling sha256-7008a656050bed18f6741406a631e83fa75ee1a02308f2e4f40d978cfbb3ce4b")


def log(layers, server="--no-jinja --chat-template chatml"):
    offloads = "".join(f"load_tensors: offloaded {layer} layers to GPU\n" for layer in layers)
    return ("OLLAMA_FLASH_ATTENTION:true OLLAMA_KV_CACHE_TYPE:f16\n"
            f"msg=\"starting llama-server\" cmd=\"llama-server --flash-attn on {server}\"\n" + offloads +
            "llama_kv_cache: size = 1 MiB, K (f16): 1 MiB, V (f16): 1 MiB\n")


def ps(digest="d", ctx=32768, size=10, vram=10):
    return {"models": [{"digest": digest, "context_length": ctx, "size": size, "size_vram": vram}]}


def test_identifiers_do_not_reuse_completed_run():
    assert smoke.RUN_ID == "smoke_single_s21r2"
    assert smoke.DIAG.name == "smoke_single_s21r2"
    assert smoke.SUMMARY.name == "smoke_single_s21r2_summary.md"
    assert smoke.REPORT_ONLY[0] == "scripts/22_smoke_single_s21r2.py"


def test_guard_accepts_each_evidence_runtime():
    smoke.guard_runtime(ps(), log(["49/49", "5/5"], GEMMA_FLAGS), "Gemma4-12B", "d", GEMMA)
    smoke.guard_runtime(ps(), log(["41/41"]), "Ministral3-14B", "d", MINISTRAL)
    smoke.guard_runtime(ps(vram=9), log(["47/49"]), "Cogito-14B", "d", COGITO)
    smoke.guard_runtime(ps(), log(["41/41"], ""), "Granite41-8B", "d", MINISTRAL)


@pytest.mark.parametrize("state", [ps(digest="x"), ps(ctx=8192), ps(vram=9), {"models": []},
                                   {"models": ps()["models"] * 2}])
def test_guard_rejects_ps_differences(state):
    with pytest.raises(AssertionError):
        smoke.guard_runtime(state, log(["41/41"]), "Ministral3-14B", "d", MINISTRAL)


@pytest.mark.parametrize("vram", [10, 0])
def test_cogito_requires_partial_offload(vram):
    with pytest.raises(AssertionError):
        smoke.guard_runtime(ps(vram=vram), log(["47/49"]), "Cogito-14B", "d", COGITO)


@pytest.mark.parametrize("agent,settings,layers,bad", [
    ("Cogito-14B", COGITO, ["47/49"], ["48/49"]),
    ("Cogito-14B", COGITO, ["47/49"], ["49/49"]),
    ("Ministral3-14B", MINISTRAL, ["41/41"], ["40/41"]),
    ("Gemma4-12B", GEMMA, ["49/49", "5/5"], ["49/49"]),
])
def test_guard_rejects_layer_residency_differences(agent, settings, layers, bad):
    server = GEMMA_FLAGS if agent == "Gemma4-12B" else "--no-jinja --chat-template chatml"
    state = ps(vram=9) if agent == "Cogito-14B" else ps()
    smoke.guard_runtime(state, log(layers, server), agent, "d", settings)
    with pytest.raises(AssertionError, match="GPU layer"):
        smoke.guard_runtime(state, log(bad, server), agent, "d", settings)


@pytest.mark.parametrize("old,new", [("K (f16)", "K (q8_0)"), ("KV_CACHE_TYPE:f16", "KV_CACHE_TYPE:q8_0"),
                                     ("FLASH_ATTENTION:true", "FLASH_ATTENTION:false"), ("--flash-attn on", ""),
                                     ("--no-jinja --chat-template chatml", "--jinja")])
def test_guard_rejects_log_differences(old, new):
    with pytest.raises(AssertionError):
        smoke.guard_runtime(ps(), log(["41/41"]).replace(old, new), "Ministral3-14B", "d", MINISTRAL)


def test_gemma_requires_speculative_flags_and_others_refuse_them():
    with pytest.raises(AssertionError, match="spec-draft-n-max"):
        smoke.guard_runtime(ps(), log(["49/49", "5/5"], GEMMA_FLAGS.replace("n-max 3", "n-max 4")),
                            "Gemma4-12B", "d", GEMMA)
    with pytest.raises(AssertionError, match="spec-type"):
        smoke.guard_runtime(ps(), log(["41/41"], "--no-jinja --chat-template chatml --spec-type draft-mtp"),
                            "Ministral3-14B", "d", MINISTRAL)


def test_real_panel_matches_frozen_protocol_values():
    panel = {r["agent_id"]: s for r, s in smoke.load_panel()}
    assert list(panel) == ["Gemma4-12B", "Granite41-8B", "Ministral3-14B", "Cogito-14B"]
    assert set(panel) == set(smoke.SERVER_GUARDS)
    for settings in panel.values():
        assert (settings["num_ctx"], settings["num_predict"], settings["kv_cache_type"],
                settings["request_timeout_seconds"], settings["think"]) == (32768, 8192, "f16", 240, False)
    assert panel["Cogito-14B"]["gpu_layers"] == ["47/49"] and not smoke.full_gpu(panel["Cogito-14B"])
    assert smoke.full_gpu(panel["Gemma4-12B"])


def test_load_panel_refuses_superseded_models_entry(tmp_path):
    (tmp_path / "configs").mkdir()
    for name in ("models.yaml", "pilot.yaml"):
        (tmp_path / "configs" / name).write_text((ROOT / "configs" / name).read_text(encoding="utf-8"), encoding="utf-8")
    frozen = yaml.safe_load((ROOT / "configs/frozen_hashes.yaml").read_text(encoding="utf-8"))
    frozen["models_s21r2"] = frozen["models"]
    (tmp_path / "configs/frozen_hashes.yaml").write_text(yaml.safe_dump(frozen), encoding="utf-8")
    with pytest.raises(ValueError):
        smoke.load_panel(tmp_path)


def test_report_config_exempts_only_summary_code():
    config = {"num_ctx": 1, "source_sha256": {"src/cofail_kg/agents/run_agent.py": "a",
              "src/cofail_kg/evaluation/smoke_summary.py": "b", "scripts/22_smoke_single_s21r2.py": "c"}}
    assert smoke.report_config(config)["source_sha256"] == {"src/cofail_kg/agents/run_agent.py": "a"}
