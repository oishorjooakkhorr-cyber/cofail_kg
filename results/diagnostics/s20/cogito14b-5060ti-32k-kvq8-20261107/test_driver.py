"""Offline checks for the exploratory cogito:14b 32K q8_0 driver; never calls a model."""
import importlib.util
from pathlib import Path

import pytest


def load(name):
    spec = importlib.util.spec_from_file_location(name, Path(__file__).with_name(f"{name}.py"))
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


driver = load("run_model")

LOG = ("OLLAMA_FLASH_ATTENTION:true OLLAMA_KV_CACHE_TYPE:q8_0\n"
       'msg="starting llama-server" cmd="llama-server.exe -c 32768 --no-jinja --chat-template chatml '
       '--cache-type-k q8_0 --cache-type-v q8_0 --flash-attn on"\n'
       "load_tensors: offloaded 49/49 layers to GPU\n"
       "llama_kv_cache: size = 5120.00 MiB ( 32768 cells,  40 layers,  1/1 seqs), K (q8_0): 1632.00 MiB, V (q8_0): 1632.00 MiB\n")


def ps(**changes):
    model = {"digest": driver.DIGEST, "context_length": 32768, "size": 10, "size_vram": 10, **changes}
    return {"models": [model]}


def test_guard_accepts_expected_runtime():
    driver.guard_runtime(ps(), LOG)


@pytest.mark.parametrize("state", [ps(digest="x"), ps(context_length=8192), ps(size_vram=9), ps(size_vram=0), {"models": []}])
def test_guard_rejects_ps_differences(state):
    with pytest.raises(AssertionError):
        driver.guard_runtime(state, LOG)


@pytest.mark.parametrize("old,new", [("49/49", "47/49"), ("49/49", "48/49"), ("K (q8_0)", "K (f16)"),
                                     ("FLASH_ATTENTION:true", "FLASH_ATTENTION:false"),
                                     ("--flash-attn on", "--flash-attn auto"),
                                     ("--no-jinja --chat-template chatml ", ""),
                                     ('--flash-attn on"', '--flash-attn on --spec-type draft-mtp"')])
def test_guard_rejects_log_differences(old, new):
    with pytest.raises(AssertionError):
        driver.guard_runtime(ps(), LOG.replace(old, new))


def test_server_env():
    env = driver.server_env({"PATH": "p", "OLLAMA_FLASH_ATTENTION": "false"})
    assert (env["OLLAMA_CONTEXT_LENGTH"], env["OLLAMA_KV_CACHE_TYPE"], env["OLLAMA_FLASH_ATTENTION"]) == ("32768", "q8_0", "true")
    assert env["OLLAMA_HOST"] == "127.0.0.1:11435" and env["PATH"] == "p"


def test_settings_match_panel_32k_agents():
    assert driver.SETTINGS == {"temperature": 0, "seed": 42, "num_ctx": 32768, "num_predict": 8192, "page_size": 50,
                               "budget": 30, "timeout_seconds": 600, "request_timeout_seconds": 240}


def test_identity_constants():
    assert driver.TAG == "cogito:14b" and driver.RUN_ID == driver.OUT.name == "cogito14b-5060ti-32k-kvq8-20261107"
    assert driver.AGENT_ID == "Cogito-14B" and driver.FAMILY == "UNVERIFIED-qwen2-architecture"
