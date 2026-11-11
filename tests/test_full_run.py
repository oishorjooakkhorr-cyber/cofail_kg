"""S39 full-run manifest builder and single-agent launcher. Synthetic fixtures; no model, no real KG."""
import hashlib
import importlib.util
import json
from pathlib import Path

import pytest

from cofail_kg.agents.panel_runner import episode_plan, progress
from cofail_kg.agents.trace import record_path
from cofail_kg.utils.frozen_hashes import read_frozen_hashes, write_once

ROOT = Path(__file__).resolve().parents[1]


def load(name):
    spec = importlib.util.spec_from_file_location(name.replace(".py", ""), ROOT / "scripts" / name)
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


MAKE = load("39_make_full_manifest.py")


def population(n=12):
    return [dict(query_id=f"q{i:02d}", relation_type="a:b:c", bridge_multiplicity="SINGLE_BRIDGE" if i % 3 else "MULTI_BRIDGE",
                 ambiguity_tag="NONE", target_count="5") for i in range(n)]


def references(rows):
    refs, nodes = {}, {}
    for i, r in enumerate(rows):
        bridges = ["900"] if r["bridge_multiplicity"] == "SINGLE_BRIDGE" else ["900", "901"]
        refs[r["query_id"]] = dict(query_id=r["query_id"], s=str(i), Type_S="drug", relation_type="a:b:c",
                                   question_texts=[f"Name all things for {i}."], B_q=bridges,
                                   T_q=[str(100 + k) for k in range(5)])
        nodes[str(i)] = dict(node_index=i, node_name=f"node {i}", node_type="drug")
    return refs, nodes


def test_remaining_excludes_drawn_and_uses_hash_order():
    rows = population()
    rest = MAKE.remaining_queries(rows, {"q00": "pilot", "q05": "smoke"})
    ids = [r["query_id"] for r in rest]
    assert set(ids) == {r["query_id"] for r in rows} - {"q00", "q05"} and len(ids) == 10
    assert ids == sorted(ids, key=lambda q: (hashlib.sha256(("42" + q).encode()).hexdigest(), q))
    assert ids != sorted(ids)  # not query-ID order
    assert rest == MAKE.remaining_queries(list(reversed(rows)), {"q05": "smoke", "q00": "pilot"})
    fewer = MAKE.remaining_queries(rows, {"q00": "pilot", "q05": "smoke"}, ["q03", "q07"])
    assert [r["query_id"] for r in fewer] == [q for q in ids if q not in ("q03", "q07")]


def test_remaining_refuses_duplicates_and_unknown_drawn_queries():
    rows = population(3)
    with pytest.raises(ValueError, match="Duplicate"):
        MAKE.remaining_queries(rows + rows[:1], {})
    with pytest.raises(ValueError, match="absent"):
        MAKE.remaining_queries(rows, {"zz": "pilot"})
    with pytest.raises(ValueError, match="Excluded"):
        MAKE.remaining_queries(rows, {"q00": "pilot"}, ["q00"])  # already drawn
    with pytest.raises(ValueError, match="Excluded"):
        MAKE.remaining_queries(rows, {}, ["zz"])


def test_lines_have_s10_fields_and_sheet_has_exactly_four():
    rows = population(4)
    refs, nodes = references(rows)
    manifest, sheet = MAKE.build_lines(rows, refs, nodes)
    assert [m["query_id"] for m in manifest] == [s["query_id"] for s in sheet] == [r["query_id"] for r in rows]
    assert all(set(s) == {"query_id", "question_text", "start_name", "start_id"} for s in sheet)
    assert all(set(m) == {"query_id", "relation_type", "multiplicity", "ambiguity_tag", "tq_size_bin"} for m in manifest)
    assert manifest[0]["multiplicity"] == "MULTI_BRIDGE" and manifest[1]["multiplicity"] == "SINGLE_BRIDGE"
    assert sheet[2] == dict(query_id="q02", question_text="Name all things for 2.", start_name="node 2", start_id="2")


def test_lines_refuse_reference_mismatch():
    rows = population(2)
    refs, nodes = references(rows)
    rows[1]["target_count"] = "6"
    with pytest.raises(ValueError, match="mismatch"):
        MAKE.build_lines(rows, refs, nodes)


def test_publish_is_write_once_and_keeps_existing_frozen_entries(tmp_path):
    (tmp_path / "configs").mkdir()
    frozen = tmp_path / "configs/frozen_hashes.yaml"
    write_once(frozen, "manifests", {"data/agent_inputs/pilot.jsonl": "abc"})
    artifacts = {"data/agent_inputs/full.jsonl": b'{"query_id":"q1"}\n', "data/processed/manifests/full.jsonl": b"x\n"}
    hashes = {p: hashlib.sha256(d).hexdigest() for p, d in artifacts.items()}
    MAKE.publish(tmp_path, artifacts, hashes)
    MAKE.publish(tmp_path, artifacts, hashes)  # identical rerun accepted
    assert read_frozen_hashes(frozen) == {"manifests": {"data/agent_inputs/pilot.jsonl": "abc"}}  # untouched
    assert read_frozen_hashes(tmp_path / "configs/frozen_hashes_full.yaml") == {"manifests_full": hashes}
    changed = dict(artifacts, **{"data/agent_inputs/full.jsonl": b'{"query_id":"q2"}\n'})
    with pytest.raises(ValueError, match="refusing"):
        MAKE.publish(tmp_path, changed, {p: hashlib.sha256(d).hexdigest() for p, d in changed.items()})
    with pytest.raises(FileExistsError):
        MAKE.publish(tmp_path, changed, hashes)
    assert (tmp_path / "data/agent_inputs/full.jsonl").read_bytes() == artifacts["data/agent_inputs/full.jsonl"]


@pytest.fixture(scope="module")
def launcher():
    return load("39_run_full.py")


def save(runs_root, run_id, query_id, agent_id, status, cause=None):
    path = record_path(runs_root, run_id, query_id, agent_id, 1)
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps({"status": status, "cause": cause}), encoding="utf-8")


def test_incremental_progress_equals_panel_runner_progress(launcher, tmp_path):
    plan = episode_plan(["A", "B"], ["q1", "q2", "q3"])
    fast = launcher.IncrementalProgress()

    def same():
        a, b = fast(tmp_path, "r", plan), progress(tmp_path, "r", plan)
        a.pop("updated_at"), b.pop("updated_at")
        assert a == b
        return a

    assert same()["episodes_done"] == 0  # the run folder does not exist yet
    save(tmp_path, "r", "q1", "A", "SUCCESS")
    save(tmp_path, "r", "q2", "A", "ERROR", "CONNECTION")
    save(tmp_path, "other", "q3", "A", "SUCCESS")  # another run is never counted
    (tmp_path / "r" / "q3__A__a1.json.tmp").write_text("{}", encoding="utf-8")  # leftovers are ignored
    state = same()
    assert (state["episodes_done"], state["failures_so_far"]) == (2, 1)
    save(tmp_path, "r", "q1", "B", "PARSE_FAIL")
    state = same()
    assert (state["episodes_done"], state["failures_so_far"]) == (3, 2)
    assert launcher.agent_counts(tmp_path, "r", ["A", "B"], ["q1", "q2", "q3"], fast) == {
        "A": {"done": 2, "total": 3, "failures": 1}, "B": {"done": 1, "total": 3, "failures": 1}}
    with pytest.raises(ValueError, match="first attempts"):
        fast(tmp_path, "r", plan, {("A", "q1"): 2})


def test_pinned_inputs_use_manifests_full_and_pin_the_launcher(launcher, tmp_path):
    (tmp_path / "configs").mkdir()
    (tmp_path / "scripts").mkdir()
    (tmp_path / "scripts/39_run_full.py").write_text("launcher", encoding="utf-8")
    frozen = tmp_path / "configs/frozen_hashes.yaml"
    write_once(frozen, "manifests", {"data/agent_inputs/full.jsonl": "WRONG-KEY"})
    write_once(tmp_path / "configs/frozen_hashes_full.yaml", "manifests_full",
               {"data/agent_inputs/full.jsonl": "sheet", "data/processed/manifests/full.jsonl": "manifest"})
    for key in ("kg_fingerprint", "tools", "relation_mapping"):
        write_once(frozen, key, key)
    _, required = launcher.pinned_inputs("full", tmp_path)
    assert required["data/agent_inputs/full.jsonl"] == "sheet"
    assert required["data/processed/manifests/full.jsonl"] == "manifest"
    assert required["scripts/39_run_full.py"] == hashlib.sha256(b"launcher").hexdigest()
    assert required["data/cache/primekg_metadata.json"] == "kg_fingerprint"
    assert required["configs/frozen_hashes_full.yaml"] == hashlib.sha256(
        (tmp_path / "configs/frozen_hashes_full.yaml").read_bytes()).hexdigest()
    with pytest.raises(ValueError, match="only the `full` manifest"):
        launcher.pinned_inputs("pilot", tmp_path)


def test_unknown_agent_is_refused_before_anything_runs(launcher, monkeypatch):
    monkeypatch.setattr(launcher, "setup", lambda: ([({"agent_id": "A"}, {}), ({"agent_id": "B"}, {})], ["q1"]))
    monkeypatch.setattr(launcher.PANEL, "run_agent", lambda *a: pytest.fail("must not start"))
    with pytest.raises(ValueError, match="not a frozen agent"):
        launcher.run("C")


def test_run_starts_only_the_named_agent_and_stops(launcher, monkeypatch, tmp_path, capsys):
    started = []
    monkeypatch.setattr(launcher, "setup", lambda: ([({"agent_id": "A"}, {"k": 1}), ({"agent_id": "B"}, {"k": 2})], ["q1", "q2"]))
    monkeypatch.setattr(launcher.PANEL, "RUNS_ROOT", tmp_path)
    monkeypatch.setattr(launcher.PANEL, "progress", launcher.IncrementalProgress())

    def fake_run_agent(manifest, run_id, row, settings, plan, progress_path, halfway):
        started.append((manifest, run_id, row["agent_id"], settings, len(plan), halfway))
        for q in ("q1", "q2"):
            save(tmp_path, run_id, q, row["agent_id"], "SUCCESS")

    monkeypatch.setattr(launcher.PANEL, "run_agent", fake_run_agent)
    launcher.run("B")
    assert started == [("full", "full_v1", "B", {"k": 2}, 4, -1)]
    assert "AGENT COMPLETE: B" in capsys.readouterr().out
    state = json.loads((tmp_path / "full_v1/progress.json").read_text(encoding="utf-8"))
    assert (state["episodes_done"], state["episodes_total"]) == (2, 4)
