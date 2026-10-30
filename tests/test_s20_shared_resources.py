"""Resource amendment and immutable resume checks; never send model requests."""
import importlib.util
from pathlib import Path

import pytest

spec = importlib.util.spec_from_file_location(
    "shared", Path(__file__).resolve().parents[1] / "scripts/20_shared_resources.py")
shared = importlib.util.module_from_spec(spec)
spec.loader.exec_module(shared)


def test_amendment_changes_only_two_resources():
    baseline = {"num_ctx": 32768, "num_predict": 4096,
                "request_timeout_seconds": 120, "timeout_seconds": 600,
                "seed": 42, "budget": 30, "page_size": 50}
    assert shared.amend(baseline) == {
        **baseline, "num_predict": 8192, "request_timeout_seconds": 240}
    assert baseline["num_predict"] == 4096
    for key, value in (("num_ctx", 16384), ("num_predict", 8192),
                       ("request_timeout_seconds", 240)):
        with pytest.raises(AssertionError):
            shared.amend({**baseline, key: value})


def test_four_distinct_models_and_new_runs():
    assert list(shared.MODELS) == ["gemma4", "ministral3", "granite41", "qwen35"]
    for model, baseline in shared.MODELS.items():
        assert shared.run_id(model) != baseline
        assert "resources" in shared.run_id(model)


def test_resume_retains_commit_and_rejects_resource_change(tmp_path):
    import json
    path = tmp_path / "manifest.json"
    path.write_text(json.dumps({"config": {"git_commit": "old", "num_predict": 8192}}))
    assert shared.resume({"config": {"git_commit": "new", "num_predict": 8192}}, path)["config"]["git_commit"] == "old"
    with pytest.raises(AssertionError):
        shared.resume({"config": {"git_commit": "new", "num_predict": 4096}}, path)
