"""Offline checks for the new-host runtime guard; never calls a model."""
import importlib.util
import hashlib
from pathlib import Path
import pytest

spec = importlib.util.spec_from_file_location("driver", Path(__file__).with_name("run_model.py"))
driver = importlib.util.module_from_spec(spec)
spec.loader.exec_module(driver)


def test_runtime_guard():
    model = {"digest": driver.DIGEST, "context_length": 16384, "size": 10, "size_vram": 10}
    log = "OLLAMA_KV_CACHE_TYPE:f16 K (f16): 1088 MiB, V (f16): 1088 MiB offloaded 43/43 layers to GPU"
    driver.guard_runtime({"models": [model]}, log)
    for key, value in (("digest", "wrong"), ("context_length", 8192), ("size_vram", 9)):
        with pytest.raises(AssertionError):
            driver.guard_runtime({"models": [{**model, key: value}]}, log)
    with pytest.raises(AssertionError):
        driver.guard_runtime({"models": [model]}, "OLLAMA_KV_CACHE_TYPE:q4_0")
    with pytest.raises(AssertionError):
        driver.guard_runtime({"models": []}, log)
    with pytest.raises(AssertionError):
        driver.guard_runtime({"models": [model]}, log.replace("43/43", "42/43"))


def test_source_relocation(tmp_path):
    path = tmp_path / "source.py"
    expected = hashlib.sha256(b"x = 1\n").hexdigest()
    path.write_bytes(b"x = 1\r\n")
    driver.guard_source(path, expected)
    path.write_bytes(b"x = 2\r\n")
    with pytest.raises(AssertionError):
        driver.guard_source(path, expected)


def test_resume_keeps_original_commit_but_rejects_other_changes(tmp_path):
    import json
    path = tmp_path / "manifest.json"
    path.write_text(json.dumps({"config": {"git_commit": "original", "num_ctx": 16384}}))
    assert driver.resume_snapshot({"config": {"git_commit": "later", "num_ctx": 16384}}, path)["config"]["git_commit"] == "original"
    with pytest.raises(AssertionError):
        driver.resume_snapshot({"config": {"git_commit": "later", "num_ctx": 8192}}, path)
