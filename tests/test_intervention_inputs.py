"""Tests for scripts/46_intervention_inputs.py and the Phase 2 overlay wiring of scripts/25_run_panel.py."""
import importlib.util
import json
import sys
from pathlib import Path

import pytest

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "src"))
from cofail_kg.agents.kg_env import Overlay  # noqa: E402


def load(name, filename):
    spec = importlib.util.spec_from_file_location(name, ROOT / "scripts" / filename)
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


M = load("intervention_inputs", "46_intervention_inputs.py")


def jsonl(rows):
    return b"".join(json.dumps(r, separators=(",", ":")).encode() + b"\n" for r in rows)


def files(pilot, expansion):
    def m(ids):
        return {"manifest": jsonl({"query_id": q, "k": 1} for q in ids),
                "sheet": jsonl({"query_id": q, "question_text": q} for q in ids)}
    return {"pilot": m(pilot), "expansion": m(expansion)}


def test_copy_lines_sorted_byte_copies():
    out = M.copy_lines(("B", "A"), files(["B", "X"], ["A"]))
    assert out["sheet"] == jsonl([{"query_id": "A", "question_text": "A"}, {"query_id": "B", "question_text": "B"}])
    with pytest.raises(ValueError, match="not found"):
        M.copy_lines(("Z",), files(["B"], ["A"]))
    with pytest.raises(ValueError, match="more than one"):
        M.copy_lines(("A",), files(["A"], ["A"]))


def s33_row(qid, u, r, ok=True):
    return {"query_id": qid, "overlay": {"query_id": qid, "hide_labels": [[u, r]], "hide_edges": []},
            "valid_route_after": ok, "only_intended_edges_hidden": True}


def test_check_overlays():
    rows = [s33_row(q, "1", "off-label use") for q in M.CASES]
    good = {q: Overlay(q, (("1", "off-label use"),)) for q in M.CASES}
    M.check_overlays(good, rows)
    with pytest.raises(ValueError, match="covers"):
        M.check_overlays({q: good[q] for q in M.CASES[:4]}, rows)
    with pytest.raises(ValueError, match="differs from the S33"):
        M.check_overlays({**good, M.CASES[0]: Overlay(M.CASES[0], (("2", "off-label use"),))}, rows)
    rows[1]["valid_route_after"] = False
    with pytest.raises(ValueError, match="S33 checks"):
        M.check_overlays(good, rows)


# ------------------------------------------------------------------- runner wiring (real frozen hashes)

@pytest.fixture(scope="module")
def runner():
    return load("run_panel", "25_run_panel.py")


def test_pinned_inputs_pin_the_overlay_only_for_intervention_runs(runner):
    _, smoke = runner.pinned_inputs("intervention_smoke")
    _, five = runner.pinned_inputs("intervention5")
    _, pilot = runner.pinned_inputs("pilot")
    _, repeat = runner.pinned_inputs("repeat8")
    assert smoke[runner.OVERLAY_FILE] == five[runner.OVERLAY_FILE]
    assert runner.OVERLAY_FILE not in pilot and runner.OVERLAY_FILE not in repeat
    assert smoke["data/agent_inputs/intervention_smoke.jsonl"] != pilot["data/agent_inputs/pilot.jsonl"]
    assert set(runner.OVERLAY_MANIFESTS) <= set(runner.MANIFESTS)
