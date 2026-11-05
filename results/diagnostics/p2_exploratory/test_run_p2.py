"""Offline checks for the exploratory P2 runner: template text, process-only swap, frozen P1 untouched."""
import importlib.util
import json
from pathlib import Path

from cofail_kg.agents import prompts, run_agent
from cofail_kg.utils.frozen_hashes import read_frozen_hashes

HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[2]


def load():
    spec = importlib.util.spec_from_file_location("run_p2", HERE / "run_p2.py")
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


def test_p2_differs_from_p1_only_in_rule_3():
    m = load()
    p1, p2 = prompts.P1_TEMPLATE.splitlines(), m.P2_TEMPLATE.splitlines()
    changed = [line for line in p2 if line not in p1]
    assert changed == ["3. When you are finished, your final message must be only this JSON object, with no other text",
                       "   before or after it, and it must list every entity in your answer:"]
    assert [line for line in p1 if line not in p2] == [
        "3. When you are finished, reply with only this JSON object and nothing else:"]
    for forbidden in ("hop", "R1", "R2", "bridge", "start entity", "shortcut"):
        assert forbidden.lower() not in m.P2_TEMPLATE.lower()


def test_swap_is_process_only_and_p1_stays_frozen():
    m = load()
    frozen = read_frozen_hashes(ROOT / "configs/frozen_hashes.yaml")["prompt"]
    assert prompts.prompt_sha256() == frozen
    source = (ROOT / "src/cofail_kg/agents/prompts.py").read_text(encoding="utf-8")

    class Launcher:
        PROMPT_VERSION = "P1"
    launcher = Launcher()
    saved = (run_agent.P1_TEMPLATE, run_agent.PROMPT_VERSION, run_agent.prompt_sha256)
    try:
        m.use_p2(launcher)
        assert run_agent.P1_TEMPLATE == m.P2_TEMPLATE and run_agent.prompt_sha256() == m.P2_SHA256
        assert run_agent.PROMPT_VERSION == launcher.PROMPT_VERSION == "P2-draft"
        assert prompts.P1_TEMPLATE != m.P2_TEMPLATE and prompts.prompt_sha256() == frozen
    finally:
        run_agent.P1_TEMPLATE, run_agent.PROMPT_VERSION, run_agent.prompt_sha256 = saved
    assert (ROOT / "src/cofail_kg/agents/prompts.py").read_text(encoding="utf-8") == source


def test_configs_match_their_s20_evidence_settings():
    m = load()
    assert len(m.ORDER) == 6 and m.SAME_WEIGHTS <= set(m.ORDER)
    pilot = __import__("yaml").safe_load((ROOT / "configs/pilot.yaml").read_text(encoding="utf-8"))["runtime"]
    for agent in ("Ministral3-8B", "Gemma4-E4B", "Granite41-8B"):
        frozen = pilot["agents"][agent]
        s = m.settings_for(agent)
        assert {k: s[k] for k in ("num_ctx", "num_predict", "kv_cache_type", "request_timeout_seconds",
                                  "flash_attention_env")} == {k: frozen[k] for k in
                                  ("num_ctx", "num_predict", "kv_cache_type", "request_timeout_seconds",
                                   "flash_attention_env")}
    q8 = pilot["agents"]["Qwen35-9B"]
    s8 = m.settings_for("Qwen35-9B-8K")
    assert (s8["num_ctx"], s8["num_predict"], s8["kv_cache_type"], s8["request_timeout_seconds"]) == \
        (q8["num_ctx"], q8["num_predict"], q8["kv_cache_type"], q8["request_timeout_seconds"])
    q16 = json.loads((ROOT / "results/diagnostics/s20/qwen35-5060ti-16k-20261029/manifest.json").read_text())["config"]
    s16 = m.settings_for("Qwen35-9B-16K")
    assert (s16["num_ctx"], s16["num_predict"], s16["request_timeout_seconds"]) == \
        (q16["num_ctx"], q16["num_predict"], q16["request_timeout_seconds"])
    orn = json.loads((ROOT / "results/diagnostics/s20/ornith15-5060ti-32k-20261031/manifest.json").read_text())["config"]
    so = m.settings_for("Ornith15-9B")
    assert (so["num_ctx"], so["num_predict"], so["request_timeout_seconds"]) == \
        (orn["num_ctx"], orn["num_predict"], orn["request_timeout_seconds"])
