"""Offline checks for the new-host runtime guard; never calls a model."""
import importlib.util
import hashlib
from pathlib import Path
import pytest

spec = importlib.util.spec_from_file_location("driver", Path(__file__).with_name("run_model.py"))
driver = importlib.util.module_from_spec(spec)
spec.loader.exec_module(driver)


def test_runtime_guard():
    model = {"digest": driver.DIGEST, "context_length": 32768, "size": 10, "size_vram": 10}
    log = ("OLLAMA_KV_CACHE_TYPE:f16 OLLAMA_FLASH_ATTENTION:true --flash-attn on "
           "offloaded 43/43 layers to GPU offloaded 5/5 layers to GPU "
           "--spec-type draft-mtp --spec-draft-n-max 3 --spec-draft-backend-sampling "
           "sha256-05612e54110f8f68bade01dfcc546cdc6914d11dde0b650a65f263f0f87bbbd2\n" +
           "llama_kv_cache: size = 1 MiB K (f16): 1 V (f16): 1\n" * 4)
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
    for before, after in (("5/5", "4/5"), ("--spec-draft-n-max 3", "--spec-draft-n-max 4"),
                          ("K (f16):", "K (q8_0):"), ("FLASH_ATTENTION:true", "FLASH_ATTENTION:false")):
        with pytest.raises(AssertionError):
            driver.guard_runtime({"models": [model]}, log.replace(before, after))


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
    path.write_text(json.dumps({"config": {"git_commit": "original", "num_ctx": 32768}}))
    assert driver.resume_snapshot({"config": {"git_commit": "later", "num_ctx": 32768}}, path)["config"]["git_commit"] == "original"
    with pytest.raises(AssertionError):
        driver.resume_snapshot({"config": {"git_commit": "later", "num_ctx": 8192}}, path)


def test_context_amendment_requires_16k_and_changes_only_context():
    baseline = {"num_ctx": 16384, "num_predict": 4096, "seed": 42}
    assert driver.context_amendment(baseline) == {**baseline, "num_ctx": 32768}
    assert baseline["num_ctx"] == 16384
    with pytest.raises(AssertionError):
        driver.context_amendment({**baseline, "num_ctx": 8192})


def test_isolated_gemma_32k_run():
    assert driver.RUN_ID == "gemma4-5060ti-32k-20261029"
    assert driver.OUT.name == driver.RUN_ID
