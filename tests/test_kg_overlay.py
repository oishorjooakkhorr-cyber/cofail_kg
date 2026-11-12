"""S32 query-local surgery overlay (protocol §10, §21) on the tiny S4 graph; no Ollama required.

Tiny graph (tests/test_primekg_prepare.py): 10 –drug_protein– 2 (target, enzyme), 30 –drug_protein– 10
(carrier), 10 –drug_effect– 40 (side effect), 2 –protein_protein– 2 (self loop), 99 isolated.
"""

import hashlib
import json
from unittest.mock import Mock

import pytest

from test_primekg_index import cache, index
from test_primekg_prepare import raw_graph
from test_panel_runner import agent as panel_agent, config as panel_config, fake_record
from test_run_agent import call, response
from cofail_kg.agents import panel_runner as pr
from cofail_kg.agents import run_agent as runner
from cofail_kg.agents.kg_env import KGEnvironment, Overlay, ToolConfig, load_overlays
from cofail_kg.agents.trace import load_episode_record, make_episode_record

NODES = ["2", "10", "30", "40", "99"]
LABELS = {"2": ["drug_protein", "protein_protein"], "10": ["drug_effect", "drug_protein"],
          "30": ["drug_protein"], "40": ["drug_effect"], "99": []}


def env(index, overlay=None, query_id="Q1", page_size=50):
    return KGEnvironment(index, ToolConfig(page_size=page_size, budget=100), overlay=overlay, query_id=query_id)


def every_output(environment):
    """All inspect_entity and page-1 get_neighbors outputs of the tiny graph."""
    out = {}
    for node in NODES:
        out[("inspect", node)] = environment.inspect_entity(node)
        for label in LABELS[node]:
            out[("neighbors", node, label)] = environment.get_neighbors(node, label)
    return out


def test_without_overlay_tools_return_the_unmodified_index_output(index):
    plain = every_output(env(index))
    assert plain[("inspect", "10")]["relations"] == index.relations_of("10")
    assert [n["id"] for n in plain[("neighbors", "10", "drug_protein")]["items"]] == ["2", "30"]
    assert plain == every_output(KGEnvironment(index, ToolConfig(page_size=50, budget=100)))


def test_hidden_label_disappears_at_the_node_and_at_its_neighbours(index):
    e = env(index, Overlay("Q1", hide_labels=(("10", "drug_protein"),)))
    assert [r["label"] for r in e.inspect_entity("10")["relations"]] == ["drug_effect"]
    assert e.get_neighbors("10", "drug_protein") == "Error: entity 10 has no relation drug_protein."
    assert [r["label"] for r in e.inspect_entity("2")["relations"]] == ["protein_protein"]
    assert e.inspect_entity("30")["relations"] == []
    assert e.get_neighbors("30", "drug_protein") == "Error: entity 30 has no relation drug_protein."


def test_hidden_edge_updates_counts_display_labels_and_pages(index):
    e = env(index, Overlay("Q1", hide_edges=(("10", "drug_protein", "2"),)), page_size=1)
    rel = next(r for r in e.inspect_entity("10")["relations"] if r["label"] == "drug_protein")
    assert rel == {"label": "drug_protein", "display_labels": ["carrier"],
                   "neighbor_types": ["gene/protein"], "neighbor_count": 1}
    page = e.get_neighbors("10", "drug_protein")
    assert [n["id"] for n in page["items"]] == ["30"] and page["total_count"] == 1 and not page["has_more"]
    assert e.get_neighbors("10", "drug_protein", page=2) == "Error: page must be an integer from 1 to 1."
    # Either direction (§3.2): node 2 no longer sees 10 through drug_protein; 30 still sees 10.
    assert [r["label"] for r in e.inspect_entity("2")["relations"]] == ["protein_protein"]
    assert [n["id"] for n in e.get_neighbors("30", "drug_protein")["items"]] == ["10"]


def test_edge_is_hidden_whichever_way_it_is_written(index):
    forward = every_output(env(index, Overlay("Q1", hide_edges=(("10", "drug_protein", "2"),))))
    backward = every_output(env(index, Overlay("Q1", hide_edges=(("2", "drug_protein", "10"),))))
    assert forward == backward


def test_nothing_else_changes(index):
    plain = every_output(env(index))
    hidden = every_output(env(index, Overlay("Q1", hide_labels=(("10", "drug_effect"),))))
    changed = {k for k in plain if plain[k] != hidden[k]}
    assert changed == {("inspect", "10"), ("inspect", "40"), ("neighbors", "10", "drug_effect"),
                       ("neighbors", "40", "drug_effect")}
    # Every other label at the touched nodes is returned exactly as before.
    keep = lambda n: [r for r in plain[("inspect", n)]["relations"] if r["label"] != "drug_effect"]
    assert hidden[("inspect", "10")]["relations"] == keep("10")
    assert hidden[("inspect", "40")]["relations"] == keep("40") == []


def test_overlay_cannot_be_used_in_another_query(index):
    with pytest.raises(ValueError, match="cannot be used"):
        env(index, Overlay("Q2", hide_labels=(("10", "drug_effect"),)), query_id="Q1")
    with pytest.raises(ValueError, match="cannot be used"):
        env(index, Overlay("Q2", hide_labels=(("10", "drug_effect"),)), query_id=None)


@pytest.mark.parametrize("kwargs,match", [
    ({}, "hides nothing"),
    ({"hide_labels": (("x10", "drug_effect"),)}, "canonical decimal"),
    ({"hide_labels": (("010", "drug_effect"),)}, "canonical decimal"),
    ({"hide_labels": (("10", ""),)}, "nonempty strings"),
    ({"hide_labels": (("10", "a"), ("10", "a"))}, "duplicate"),
])
def test_overlay_values_are_validated(kwargs, match):
    with pytest.raises(ValueError, match=match):
        Overlay("Q1", **kwargs)


def write_overlays(path, rows):
    path.write_text("".join(json.dumps(r) + "\n" for r in rows), encoding="utf-8")
    return path


def test_load_overlays_reads_one_line_per_query(tmp_path):
    path = write_overlays(tmp_path / "o.jsonl", [
        {"query_id": "Q1", "hide_labels": [["10", "drug_effect"]], "hide_edges": []},
        {"query_id": "Q2", "hide_labels": [], "hide_edges": [["30", "drug_protein", "10"]]}])
    overlays = load_overlays(path)
    assert sorted(overlays) == ["Q1", "Q2"] and overlays.get("Q3") is None
    assert overlays["Q2"].to_json() == {"query_id": "Q2", "hide_labels": [],
                                        "hide_edges": [["30", "drug_protein", "10"]]}


@pytest.mark.parametrize("rows,match", [
    ([{"query_id": "Q1", "hide_labels": [["10", "x"]], "hide_edges": [], "T_q": ["1"]}], "exactly the keys"),
    ([{"query_id": "Q1", "hide_labels": [["10", "x"]], "hide_edges": []}] * 2, "duplicate overlay"),
    ([{"query_id": "Q1", "hide_labels": [["10"]], "hide_edges": []}], "pairs"),
    ([], "no overlay"),
])
def test_load_overlays_refuses_anything_else(tmp_path, rows, match):
    with pytest.raises(ValueError, match=match):
        load_overlays(write_overlays(tmp_path / "o.jsonl", rows))


@pytest.fixture
def overlay_episode(tmp_path, index, monkeypatch):
    queries = [{"query_id": q, "question_text": "Find an entity.", "start_id": "10", "start_name": "Alpha"}
               for q in ("Q1", "Q2")]
    sheet = tmp_path / "sheet.jsonl"
    sheet.write_text("".join(json.dumps(q) + "\n" for q in queries), encoding="utf-8")
    overlay_file = write_overlays(tmp_path / "overlay.jsonl", [
        {"query_id": "Q1", "hide_labels": [["10", "drug_protein"]], "hide_edges": []}])
    config = {"run_id": "s32-test", "agent_inputs": str(sheet), "cache_dir": "unused",
              "runs_root": str(tmp_path / "runs"), "temperature": 0, "seed": 42, "num_ctx": 8192,
              "num_predict": 4096, "page_size": 50, "budget": 30, "timeout_seconds": 10,
              "request_timeout_seconds": 7, "base_url": "http://127.0.0.1:11434", "kg_fingerprint": "a" * 64,
              "biohopr_revision": "test-revision", "git_commit": "test-dirty", "tool_schema_sha256": "b" * 64,
              "agent_inputs_sha256": hashlib.sha256(sheet.read_bytes()).hexdigest(), "draft_prompt": True,
              "overlay_path": str(overlay_file),
              "overlay_sha256": hashlib.sha256(overlay_file.read_bytes()).hexdigest()}
    agent = {"agent_id": "A1", "tag": "tiny:test", "digest": "test-digest", "quantization": "Q4_K_M",
             "think": False}
    client = Mock()
    monkeypatch.setattr(runner, "PrimeKGIndex", lambda _: index)
    monkeypatch.setattr(runner, "OllamaClient", Mock(return_value=client))

    def run(query_id, cfg=config):
        client.chat.side_effect = [response(calls=[call(entity_id="10"),
                                                   call("get_neighbors", entity_id="10", relation="drug_protein")]),
                                   response('{"status":"no_answer","answers":[]}')]
        return load_episode_record(runner.run_episode(query_id, agent, cfg))
    return run, client, config


def test_episode_applies_and_saves_only_its_own_overlay(overlay_episode):
    run, _, config = overlay_episode
    q1 = run("Q1")
    cfg_event = q1["log_events"][0]
    assert cfg_event["overlay"] == {"query_id": "Q1", "hide_labels": [["10", "drug_protein"]], "hide_edges": []}
    assert cfg_event["overlay_sha256"] == config["overlay_sha256"]
    assert [r["label"] for r in q1["call_log"][0]["result"]["relations"]] == ["drug_effect"]
    assert q1["call_log"][1]["result"] == "Error: entity 10 has no relation drug_protein."
    q2 = run("Q2")  # no overlay line for Q2: the unmodified graph, and that is recorded
    assert q2["log_events"][0]["overlay"] is None
    assert [n["id"] for n in q2["call_log"][1]["result"]["items"]] == ["2", "30"]


def test_changed_overlay_file_stops_before_any_model_call(overlay_episode):
    run, client, config = overlay_episode
    with pytest.raises(ValueError, match="overlay_sha256"):
        run("Q1", {**config, "overlay_sha256": "0" * 64})
    assert client.chat.call_count == 0


def test_resume_refuses_a_record_from_another_overlay_file(tmp_path):
    ag = panel_agent("A1")
    cfg = panel_config(tmp_path, overlay_path="o.jsonl", overlay_sha256="c" * 64)
    record = fake_record("BH2_00001", ag, cfg)
    record_fields = {k: v for k, v in record.items()
                     if k not in ("trace_graph", "appeared_entities", "protocol_version", "record_schema_version")}
    record_fields["log_events"][0]["overlay_sha256"] = "c" * 64
    good = make_episode_record(**record_fields)
    pr.validate_completed(good, ag, cfg, "BH2_00001", 1)
    with pytest.raises(ValueError, match="episode config"):
        pr.validate_completed(good, ag, {**cfg, "overlay_sha256": "d" * 64}, "BH2_00001", 1)
    with pytest.raises(ValueError, match="episode config"):
        pr.validate_completed(fake_record("BH2_00001", ag, cfg), ag, cfg, "BH2_00001", 1)
