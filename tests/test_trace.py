"""S12 tests: episode records, trace graph, paths and write-once saving (protocol §11, §14, §19).

Records are hand-written call logs in the KGEnvironment.call_log shape; no model is run.
"""

import itertools
from concurrent.futures import ThreadPoolExecutor
import json
import os
import random
import subprocess
import sys
from threading import Barrier
from types import SimpleNamespace
from unittest.mock import Mock

import pytest

from cofail_kg.agents import trace
from cofail_kg.agents.trace import (
    Edge, RecordError, TraceGraph, appeared_entities, build_trace_graph, load_episode_record,
    make_episode_record, path_order_key, paths, primary_path, record_path, save_episode_record,
    simple_paths, verify_reconstruction)

BUDGET = "Tool budget exhausted. Give your final answer now."


# --- hand-written call-log entries -------------------------------------------------------------

def nb(u, relation, ids, *, page=1, total=None, has_more=False, neighbor_type=None):
    """A successful get_neighbors entry returning `ids` on one page."""
    items = [{"id": str(i), "name": f"N{i}", "type": "t", "display_labels": [relation]} for i in ids]
    return {"tool": "get_neighbors", "success": True, "timestamp": "2026-10-15T00:00:00+00:00",
            "elapsed_seconds": 0.0,
            "arguments": {"entity_id": u, "relation": relation, "neighbor_type": neighbor_type,
                          "page": page},
            "result": {"items": items, "total_count": len(ids) if total is None else total,
                       "page": page, "page_size": 50, "has_more": has_more}}


def failed(tool, arguments, message):
    return {"tool": tool, "success": False, "timestamp": "2026-10-15T00:00:00+00:00",
            "elapsed_seconds": 0.0, "arguments": arguments, "result": message}


def inspect(entity_id):
    return {"tool": "inspect_entity", "success": True, "timestamp": "2026-10-15T00:00:00+00:00",
            "elapsed_seconds": 0.0, "arguments": {"entity_id": entity_id},
            "result": {"id": str(entity_id), "name": f"N{entity_id}", "type": "t", "relations": []}}


def fields(call_log, **override):
    base = {
        "run_id": "run-test", "query_id": "BH2_00001", "agent_id": "A1", "attempt": 1,
        "model": {"tag": "test:tag", "digest": "sha256:test", "quantization": "Q4_K_M"},
        "temperature": 0, "seed": 42, "num_ctx": 8192, "num_predict": 4096,
        "prompt_version": "P1-test",
        "tool_config": {"tool_version": "T1", "page_size": 50, "budget": 30,
                        "ordering_rule": "numeric-id", "tool_schema_sha256": "a" * 64,
                        "prompt_values": {"PAGE_SIZE": 50, "BUDGET": 30}},
        "kg_fingerprint": "b" * 64, "biohopr_revision": "rev-test", "git_commit": "commit-test",
        "timestamps": {"started_at": "2026-10-15T00:00:00+00:00",
                       "finished_at": "2026-10-15T00:01:00+00:00"},
        "messages": [{"role": "user", "content": "q"}], "call_log": call_log,
        "token_counts": {"prompt": [10], "completion": [5]},
        "raw_final_output": '{"status": "no_answer", "answers": []}',
        "status": "SUCCESS", "cause": None,
    }
    return base | override


def record(call_log, **override):
    return make_episode_record(**fields(call_log, **override))


def triples(graph):
    return {(e.u, e.label, e.v): e.creation_index for e in graph.edges}


def hops(path):
    return [(e.u, e.label, e.v) for e in path]


# --- trace graph (§11) -------------------------------------------------------------------------

def test_only_returned_page_items_become_edges():
    # Page 1 of 3 items; total_count/has_more announce more but only returned items count.
    rec = record([nb("1", "r", [2, 3], total=3, has_more=True)])
    assert triples(build_trace_graph(rec)) == {("1", "r", "2"): 0, ("1", "r", "3"): 0}
    rec = record([nb("1", "r", [2, 3], total=3, has_more=True), nb("1", "r", [4], page=2)])
    assert set(triples(build_trace_graph(rec))) == {("1", "r", "2"), ("1", "r", "3"), ("1", "r", "4")}


def test_creation_index_is_first_successful_call():
    log = [failed("get_neighbors", {"entity_id": "1", "relation": "x"},
                  "Error: entity 1 has no relation x."),          # 0: error, no edge
           nb("1", "r", [2]),                                       # 1
           nb("1", "r", [2, 3], neighbor_type=None),                # 2: (1,r,2) already exists
           nb("2", "q", [1])]                                       # 3: reverse traversal is its own edge
    assert triples(build_trace_graph(record(log))) == {
        ("1", "r", "2"): 1, ("1", "r", "3"): 2, ("2", "q", "1"): 3}


def test_errors_budget_inspect_and_ignored_calls_add_no_edges():
    log = [inspect("1"),
           failed("get_neighbors", {"entity_id": "404", "relation": "r"},
                  "Error: unknown entity ID 404."),
           failed("get_neighbors", {"entity_id": "1", "relation": "r", "page": 9},
                  "Error: page must be an integer from 1 to 1."),
           failed("get_neighbors", {"entity_id": "1", "relation": "r"}, BUDGET)]
    ignored = [{"name": "get_neighbors", "arguments": {"entity_id": "1", "relation": "r"}}]
    rec = record(log, ignored_tool_calls=ignored)
    assert build_trace_graph(rec).edges == ()
    assert rec["trace_graph"] == []
    assert appeared_entities(rec) == ("1",)  # inspect_entity subject appeared


def test_appeared_entities_numeric_order_and_sources():
    rec = record([nb("100", "r", [9, 10]), inspect("2"),
                  failed("inspect_entity", {"entity_id": "7"}, "Error: unknown entity ID 7.")])
    assert appeared_entities(rec) == ("2", "9", "10")  # 100 was only an argument


def test_integer_entity_argument_is_canonicalised_and_bad_logs_are_rejected():
    assert triples(build_trace_graph(record([nb(5, "r", [6])]))) == {("5", "r", "6"): 0}
    with pytest.raises(RecordError, match="contradicts"):
        record([{**nb("1", "r", [2]), "success": False}])
    with pytest.raises(RecordError, match="canonical node ID"):
        record([nb(" 1", "r", [2])])


def test_parallel_edges_both_kept_and_ordered_by_14_2():
    # Paper-drawing case (see S12 report):
    #   call 0: get_neighbors(1, b) -> [5, 20]
    #   call 1: get_neighbors(1, a) -> [5]
    #   call 2: get_neighbors(5, c) -> [9]
    log = [nb("1", "b", [5, 20]), nb("1", "a", [5]), nb("5", "c", [9])]
    graph = build_trace_graph(record(log))
    assert triples(graph) == {("1", "b", "5"): 0, ("1", "b", "20"): 0,
                              ("1", "a", "5"): 1, ("5", "c", "9"): 2}
    # x = 9: both length-2 paths have largest index 2 -> tie broken by (1,a) < (1,b).
    result = paths(graph, "1", "9")
    assert hops(result.primary) == [("1", "a", "5"), ("5", "c", "9")]
    assert [hops(p) for p in result.simple] == [
        [("1", "a", "5"), ("5", "c", "9")], [("1", "b", "5"), ("5", "c", "9")]]
    # x = 5: parallel length-1 edges; creation index (0 < 1) beats label order (a < b).
    assert hops(primary_path(graph, "1", "5")) == [("1", "b", "5")]
    assert [hops(p) for p in simple_paths(graph, "1", "5")] == [[("1", "b", "5")], [("1", "a", "5")]]


def test_numeric_not_string_id_order():
    # Both paths share their largest creation index (call 2), so the sequence decides:
    # (1,a),(9,b) < (1,a),(10,b) numerically, although "10" < "9" as strings.
    log = [nb("10", "b", [50]), nb("9", "b", [50]), nb("1", "a", [9, 10])]
    graph = build_trace_graph(record(log))
    assert hops(primary_path(graph, "1", "50")) == [("1", "a", "9"), ("9", "b", "50")]
    assert [hops(p)[0][2] for p in simple_paths(graph, "1", "50")] == ["9", "10"]


def test_three_edge_tie_break_uses_source_node_label_pairs():
    # Decision log 2026-10-15 (protocol v1.3.4): pairs are (numeric u, label) per edge.
    #   P: 1 -b-> 3 -c-> 7 -d-> 9      Q: 1 -a-> 5 -c-> 7 -d-> 9
    # Shared last edge (call 4) is the largest index in both paths.
    # (u, label) reading:  (1,a) < (1,b)  -> Q through 5.
    # (v, label) reading:  (3,b) < (5,a)  -> P through 3 (rejected reading).
    log = [nb("1", "a", [5]), nb("1", "b", [3]), nb("3", "c", [7]), nb("5", "c", [7]),
           nb("7", "d", [9])]
    graph = build_trace_graph(record(log))
    primary = primary_path(graph, "1", "9")
    assert hops(primary) == [("1", "a", "5"), ("5", "c", "7"), ("7", "d", "9")]
    target_reading = min(simple_paths(graph, "1", "9"),
                         key=lambda p: (len(p), max(e.creation_index for e in p),
                                        tuple((int(e.v), e.label) for e in p)))
    assert hops(target_reading)[0] == ("1", "b", "3")  # the two readings really differ here
    assert [hops(p)[0] for p in simple_paths(graph, "1", "9")] == [("1", "a", "5"), ("1", "b", "3")]
    assert path_order_key(primary) == (3, 4, ((1, "a"), (5, "c"), (7, "d")))


def test_x_equals_s_gives_length_zero_path():
    graph = build_trace_graph(record([nb("1", "r", [2]), nb("2", "r", [1])]))
    result = paths(graph, "1", "1")
    assert result.primary == () and result.simple == ((),)
    assert path_order_key(()) == (0, -1, ())


def test_unreachable_and_reverse_only_targets_have_no_path():
    graph = build_trace_graph(record([nb("1", "r", [2]), nb("3", "r", [1])]))
    assert paths(graph, "1", "3") == trace.PathSet(None, ())  # only 3 -> 1 was traversed
    assert paths(graph, "1", "99") == trace.PathSet(None, ())


def test_simple_paths_limit_and_shortest_wins():
    # 1->2->3->4->5 chain plus a cycle 2->1; also a direct 1->5 added last.
    log = [nb("1", "r", [2]), nb("2", "r", [3, 1]), nb("3", "r", [4]), nb("4", "r", [5]),
           nb("1", "s", [5])]
    graph = build_trace_graph(record(log))
    assert [hops(p) for p in simple_paths(graph, "1", "4")] == [
        [("1", "r", "2"), ("2", "r", "3"), ("3", "r", "4")]]
    assert simple_paths(graph, "1", "5") == (primary_path(graph, "1", "5"),)  # length 4 excluded
    assert hops(primary_path(graph, "1", "5")) == [("1", "s", "5")]  # fewer edges beats index


def _protocol_key(path):
    """§14.2 written out independently of trace.path_order_key: s, r1, n1, r2, ..."""
    flat = []
    for e in path:
        flat += [int(e.u), e.label]
    return (len(path), max(e.creation_index for e in path), flat)


def _brute_force_primary(graph, s, x, limit=6):
    out = {}
    for e in graph.edges:
        out.setdefault(e.u, []).append(e)
    frontier = [((), s)]
    for _ in range(limit):
        frontier = [(p + (e,), e.v) for p, node in frontier for e in out.get(node, ())]
        done = [p for p, node in frontier if node == x]
        if done:
            return min(done, key=_protocol_key)
    return None


def test_primary_path_matches_brute_force_on_seeded_synthetic_graphs():
    rng, ties = random.Random(42), 0
    for _ in range(300):
        nodes = [str(n) for n in rng.sample(range(1, 40), 7)]
        edges = {}
        for _call in range(rng.randint(1, 8)):
            index, u, label = _call, rng.choice(nodes), rng.choice("abc")
            for v in rng.sample(nodes, rng.randint(0, 4)):
                edges.setdefault((u, label, v), index)
        graph = TraceGraph(trace._sorted_edges(Edge(i, u, r, v) for (u, r, v), i in edges.items()))
        for s, x in itertools.permutations(nodes[:4], 2):
            assert primary_path(graph, s, x) == _brute_force_primary(graph, s, x)
            found = simple_paths(graph, s, x)
            assert list(found) == sorted(found, key=_protocol_key)
            ties += sum(len(a) == len(b) and _protocol_key(a)[1] == _protocol_key(b)[1]
                        for a, b in zip(found, found[1:]))
    assert ties > 50  # the tie-break (3) is really exercised


# --- record fields (§19) -----------------------------------------------------------------------

def test_record_requires_every_field_and_derives_graph():
    rec = record([nb("1", "r", [2])])
    assert rec["trace_graph"] == [{"creation_index": 0, "u": "1", "label": "r", "v": "2"}]
    assert rec["protocol_version"] == "1.3.4" and rec["ignored_tool_calls"] == []
    for key in ("model", "num_ctx", "prompt_version", "tool_config", "kg_fingerprint",
                "git_commit", "raw_final_output", "token_counts"):
        with pytest.raises(RecordError, match=key):
            make_episode_record(**{k: v for k, v in fields([]).items() if k != key})
    with pytest.raises(RecordError, match="num_ctx"):
        record([], num_ctx=None)
    with pytest.raises(RecordError, match="digest"):
        record([], model={"tag": "t", "digest": "", "quantization": "q"})
    with pytest.raises(RecordError, match="derived"):
        record([], trace_graph=[])
    with pytest.raises(RecordError, match="unknown"):
        record([], surprise=1)


def test_status_and_cause_rules():
    assert record([], status="ERROR", cause="OUT_OF_MEMORY")["cause"] == "OUT_OF_MEMORY"
    assert record([], status="TIMEOUT", raw_final_output=None)["raw_final_output"] is None
    with pytest.raises(RecordError, match="cause"):
        record([], status="ERROR", cause=None)
    with pytest.raises(RecordError, match="cause"):
        record([], status="SUCCESS", cause="OTHER")
    with pytest.raises(RecordError, match="status"):
        record([], status="DONE")


# --- saving, reconstruction (§19, §19.1) ------------------------------------------------------

def test_save_path_and_refuses_overwrite(tmp_path):
    rec = record([nb("1", "r", [2])])
    path = save_episode_record(rec, tmp_path)
    assert path == tmp_path / "run-test" / "BH2_00001__A1__a1.json"
    assert path == record_path(tmp_path, "run-test", "BH2_00001", "A1", 1)
    before = path.read_bytes()
    changed = record([nb("1", "r", [3])])
    with pytest.raises(FileExistsError, match="refusing to overwrite"):
        save_episode_record(changed, tmp_path)
    assert path.read_bytes() == before
    assert save_episode_record(record([], attempt=2), tmp_path).name == "BH2_00001__A1__a2.json"
    assert sorted(p.name for p in path.parent.iterdir()) == [
        "BH2_00001__A1__a1.json", "BH2_00001__A1__a2.json"]


def test_publication_refuses_existing_target_even_without_the_precheck(tmp_path, monkeypatch):
    rec = record([])
    path = save_episode_record(rec, tmp_path)
    monkeypatch.setattr(trace.Path, "exists", lambda self: False)  # simulate a racing writer
    with pytest.raises(FileExistsError):
        save_episode_record(rec, tmp_path)
    assert json.loads(path.read_text(encoding="utf-8")) == rec
    assert [p.name for p in path.parent.iterdir()] == [path.name]


@pytest.mark.parametrize("target", ["fsync", "publish_once"])
def test_crash_during_save_leaves_no_file(tmp_path, monkeypatch, target):
    def crash(*args, **kwargs):
        raise OSError("simulated crash")
    monkeypatch.setattr(trace.os if target == "fsync" else trace, target, crash)
    with pytest.raises(OSError, match="simulated crash"):
        save_episode_record(record([nb("1", "r", [2])]), tmp_path)
    assert [p for p in tmp_path.rglob("*") if p.is_file()] == []


@pytest.mark.parametrize("platform", ["nt", "posix"])
def test_publication_uses_the_platform_no_overwrite_operation(tmp_path, monkeypatch, platform):
    source, destination = tmp_path / "source", tmp_path / "destination"
    operations = SimpleNamespace(name=platform, rename=Mock(), link=Mock())
    monkeypatch.setattr(trace, "os", operations)
    trace.publish_once(source, destination)
    selected = operations.rename if platform == "nt" else operations.link
    unused = operations.link if platform == "nt" else operations.rename
    selected.assert_called_once_with(source, destination)
    unused.assert_not_called()


def test_saver_when_hard_links_are_unavailable(tmp_path, monkeypatch):
    monkeypatch.setattr(trace.os, "link", Mock(side_effect=PermissionError("hard links blocked")))
    rec = record([nb("1", "r", [2])])
    if os.name == "nt":
        assert load_episode_record(save_episode_record(rec, tmp_path)) == rec
        trace.os.link.assert_not_called()
    else:
        with pytest.raises(PermissionError, match="hard links blocked"):
            save_episode_record(rec, tmp_path)
        assert [p for p in tmp_path.rglob("*") if p.is_file()] == []


def test_competing_savers_publish_one_complete_record(tmp_path, monkeypatch):
    records = [record([nb("1", "r", [target])]) for target in (2, 3)]
    ready = Barrier(2)
    publish = trace.publish_once

    def publish_together(source, destination):
        assert not destination.exists()
        assert json.loads(source.read_text(encoding="utf-8")) in records
        ready.wait(timeout=10)
        publish(source, destination)

    monkeypatch.setattr(trace, "publish_once", publish_together)
    with ThreadPoolExecutor(max_workers=2) as pool:
        futures = [pool.submit(save_episode_record, rec, tmp_path) for rec in records]
        winners, refused = [], 0
        for future in futures:
            try:
                winners.append(future.result(timeout=15))
            except FileExistsError:
                refused += 1
    assert len(winners) == refused == 1
    assert load_episode_record(winners[0]) in records
    assert sorted(p for p in tmp_path.rglob("*") if p.is_file()) == winners


def test_reconstruction_round_trip_and_tamper_detection(tmp_path):
    log = [nb("1", "b", [5, 20]), failed("get_neighbors", {"entity_id": "1", "relation": "z"},
                                         "Error: entity 1 has no relation z."),
           nb("1", "a", [5]), inspect("20"), nb("5", "c", [9])]
    rec = record(log)
    loaded = load_episode_record(save_episode_record(rec, tmp_path))
    assert loaded == rec
    assert build_trace_graph(loaded) == TraceGraph.from_json(loaded["trace_graph"])
    verify_reconstruction(loaded)

    tampered = json.loads(json.dumps(rec))
    tampered["trace_graph"][0]["creation_index"] = 3
    with pytest.raises(RecordError, match="trace graph mismatch"):
        verify_reconstruction(tampered)
    tampered = json.loads(json.dumps(rec))
    tampered["call_log"][0]["result"]["items"].pop()
    with pytest.raises(RecordError, match="mismatch"):
        verify_reconstruction(tampered)
    bad_path = tmp_path / "bad.json"
    bad_path.write_text(json.dumps(tampered), encoding="utf-8")
    with pytest.raises(RecordError):
        load_episode_record(bad_path)


def test_unsafe_file_name_parts_rejected():
    for bad in ("../x", "a__b", "a/b", ""):
        with pytest.raises(RecordError):
            record([], agent_id=bad)


# --- isolation (§9.3, §19.1 b) ----------------------------------------------------------------

def test_trace_module_is_isolated_from_evaluation_imports_and_files(tmp_path):
    # A fresh interpreter also catches transitive imports hidden by pytest's module cache.
    script = r'''
import sys

def audit(event, args):
    if event == "import" and args[0].startswith("cofail_kg.evaluation"):
        raise AssertionError("evaluation import")
    if event == "open" and isinstance(args[0], str):
        path = "/" + args[0].replace("\\", "/").lower().lstrip("/")
        if "/data/processed/" in path:
            raise AssertionError("evaluation file read: " + path)

sys.addaudithook(audit)
import json
from cofail_kg.agents import trace
rec = trace.make_episode_record(**json.loads(sys.argv[2]))
trace.load_episode_record(trace.save_episode_record(rec, sys.argv[1]))
assert not any(n.startswith("cofail_kg.evaluation") for n in sys.modules)
'''
    payload = json.dumps(fields([nb("1", "r", [2])]))
    subprocess.run([sys.executable, "-c", script, str(tmp_path), payload],
                   capture_output=True, text=True, check=True)
    source = trace.__file__
    with open(source, encoding="utf-8") as handle:
        assert "cofail_kg.evaluation" not in handle.read()
