"""Offline checks for the 8K f32-KV driver; never calls a model."""
import hashlib
import importlib.util
import json
from pathlib import Path
import pytest

spec = importlib.util.spec_from_file_location("driver", Path(__file__).with_name("run_model.py"))
driver = importlib.util.module_from_spec(spec)
spec.loader.exec_module(driver)

LOG = ("OLLAMA_KV_CACHE_TYPE:f32 offloaded 33/33 layers to GPU K (f32):  256.00 MiB, V (f32):  256.00 MiB "
       "warmup: flash attention is enabled")


def test_runtime_guard():
    model = {"digest": driver.DIGEST, "context_length": 8192, "size": 10, "size_vram": 10}
    driver.guard_runtime({"models": [model]}, LOG)
    for key, value in (("digest", "wrong"), ("context_length", 16384), ("size_vram", 9)):
        with pytest.raises(AssertionError):
            driver.guard_runtime({"models": [{**model, key: value}]}, LOG)
    with pytest.raises(AssertionError):
        driver.guard_runtime({"models": []}, LOG)
    for old, new in (("33/33", "32/33"), ("KV_CACHE_TYPE:f32", "KV_CACHE_TYPE:f16"),
                     ("K (f32)", "K (f16)"), ("flash attention is enabled", "")):
        with pytest.raises(AssertionError):
            driver.guard_runtime({"models": [model]}, LOG.replace(old, new))
    with pytest.raises(AssertionError):
        driver.guard_runtime({"models": [model]}, LOG + " K (f16): 128 MiB, V (f16): 128 MiB")


def test_source_relocation(tmp_path):
    path = tmp_path / "source.py"
    expected = hashlib.sha256(b"x = 1\n").hexdigest()
    path.write_bytes(b"x = 1\r\n")
    driver.guard_source(path, expected)
    path.write_bytes(b"x = 2\r\n")
    with pytest.raises(AssertionError):
        driver.guard_source(path, expected)


def test_resume_keeps_original_commit_but_rejects_other_changes(tmp_path):
    path = tmp_path / "manifest.json"
    path.write_text(json.dumps({"config": {"git_commit": "original", "num_ctx": 8192}}))
    assert driver.resume_snapshot({"config": {"git_commit": "later", "num_ctx": 8192}}, path)["config"]["git_commit"] == "original"
    with pytest.raises(AssertionError):
        driver.resume_snapshot({"config": {"git_commit": "later", "num_ctx": 16384}}, path)


def test_context_amendment_restores_frozen_screening_context():
    baseline = {"num_ctx": 16384, "num_predict": 4096, "seed": 42}
    assert driver.context_amendment(baseline) == {**baseline, "num_ctx": 8192}
    assert baseline["num_ctx"] == 16384
    with pytest.raises(AssertionError):
        driver.context_amendment({**baseline, "num_ctx": 32768})


def test_server_env_sets_f32_and_inherits_flash_attention():
    env = driver.server_env({"OLLAMA_FLASH_ATTENTION": "false", "PATH": "x"})
    assert env["OLLAMA_KV_CACHE_TYPE"] == "f32" and env["OLLAMA_CONTEXT_LENGTH"] == "8192"
    assert env["OLLAMA_HOST"] == "127.0.0.1:11435" and env["OLLAMA_NUM_PARALLEL"] == "1"
    assert "OLLAMA_FLASH_ATTENTION" not in env and env["PATH"] == "x"


def test_run_is_isolated():
    assert driver.RUN_ID == "qwen35-5060ti-8k-f32-20261030" == driver.OUT.name
    manifest = driver.OUT / "manifest.json"
    if manifest.exists():
        saved = json.loads(manifest.read_text())
        assert saved["config"]["num_ctx"] == 8192 and saved["runtime"]["kv_cache_type"] == "f32"
