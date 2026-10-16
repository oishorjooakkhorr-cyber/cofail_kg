"""Episode records, write-once saving, trace graphs and paths (protocol v1.3.4 §11, §14.1–14.2, §19).

Episode record (§11, §19)
    A JSON object holding every §19 reproducibility field, all messages, the full tool-call
    log (``KGEnvironment.call_log`` entries: arguments, complete result, success flag,
    timestamp, timing) and the raw final output. Values fixed only at later stages (model
    digest, prompt version P1, final ``num_ctx`` ...) are required arguments supplied by the
    caller; nothing here invents or defaults them. ``make_episode_record`` validates the
    fields and adds the derived ``trace_graph`` and ``appeared_entities``.

Write-once saving (§19)
    ``results/runs/<run_id>/<query_id>__<agent_id>__a<attempt>.json``. Any existing record
    counts as a completed episode, so a partial record must never exist: the JSON is written
    to a temporary file in the same folder, flushed and fsynced, then published with Windows
    rename or, elsewhere, a hard link. Both refuse an existing target, so an existing
    record is never overwritten, even by a racing writer. The temporary file is removed on
    every exit path; a hard crash can leave only a ``.*.tmp`` file, never a ``*.json`` record.

Trace graph TG_i (§11)
    For every successful ``get_neighbors(u, r, ...)`` call, one directed edge u → v with label
    r for each item v on the returned page, oriented as traversed (the §3.2 either-direction
    convention has no exceptions). Edge identity is (u, r, v); its creation index is the
    0-based position in the call log of the first successful call that returned it. Errors,
    budget messages, ``inspect_entity`` and tool calls ignored after the budget (§9.4, kept in
    ``ignored_tool_calls``) add no edges. Any strictly increasing call numbering gives the
    same §14.2 comparisons, so the 0-based log position is an engineering choice.

Appeared (§11)
    Every entity returned by a successful call: neighbor items and ``inspect_entity`` subjects.

Paths (§14.1–14.2)
    Path order: (1) fewer edges; (2) smaller largest creation index; (3) lexicographically
    smaller sequence of (numeric ID of u, r) per edge u –r→ v, i.e. s, r1, n1, r2, ...
    (decision log 2026-10-15, protocol v1.3.4). When x = s the primary path is the length-0
    path (§14.1).
"""

from __future__ import annotations

import json
import os
import re
import uuid
from collections import deque
from dataclasses import dataclass
from pathlib import Path

PROTOCOL_VERSION = "1.3.4"
RECORD_SCHEMA_VERSION = 1
DEFAULT_RUNS_ROOT = Path("results/runs")

STATUSES = ("TIMEOUT", "ERROR", "PARSE_FAIL", "SUCCESS")  # §9.5 precedence order
ERROR_CAUSES = ("OUT_OF_MEMORY", "CONNECTION", "RUNTIME", "OTHER")  # §9.5

_CANONICAL_ID = re.compile(r"0|[1-9][0-9]*")
_SAFE_PART = re.compile(r"[A-Za-z0-9][A-Za-z0-9._-]*")
_SHA256 = re.compile(r"[0-9a-f]{64}")
_DERIVED = ("appeared_entities", "protocol_version", "record_schema_version", "trace_graph")
_OPTIONAL_LISTS = ("ignored_tool_calls", "log_events")


class RecordError(ValueError):
    """An episode record is missing a field, has an invalid value, or fails reconstruction."""


# ---------------------------------------------------------------------------------------------
# Field validation (§19)
# ---------------------------------------------------------------------------------------------

def _text(value, name):
    if not isinstance(value, str) or not value.strip():
        raise RecordError(f"{name} must be a non-empty string, got {value!r}")


def _safe_part(value, name):
    _text(value, name)
    if not _SAFE_PART.fullmatch(value) or "__" in value or ".." in value:
        raise RecordError(f"{name} {value!r} is not safe as a file-name part")


def _int(value, name, minimum):
    if type(value) is not int or value < minimum:
        raise RecordError(f"{name} must be an integer >= {minimum}, got {value!r}")


def _number(value, name):
    if type(value) not in (int, float):
        raise RecordError(f"{name} must be a number, got {value!r}")


def _sha256(value, name):
    if not isinstance(value, str) or not _SHA256.fullmatch(value):
        raise RecordError(f"{name} must be a lowercase SHA256 hex digest, got {value!r}")


def _mapping(value, name, fields):
    if not isinstance(value, dict):
        raise RecordError(f"{name} must be an object, got {type(value).__name__}")
    if set(value) != set(fields):
        raise RecordError(f"{name} keys {sorted(value)} must be exactly {sorted(fields)}")
    for key, check in fields.items():
        check(value[key], f"{name}.{key}")


def _list(value, name):
    if not isinstance(value, list):
        raise RecordError(f"{name} must be a list, got {type(value).__name__}")


def _container(value, name):
    if not isinstance(value, (dict, list)):
        raise RecordError(f"{name} must be an object or list, got {type(value).__name__}")


def _object(value, name):
    if not isinstance(value, dict):
        raise RecordError(f"{name} must be an object, got {type(value).__name__}")


def _optional_text(value, name):
    if value is not None and not isinstance(value, str):
        raise RecordError(f"{name} must be a string or null, got {type(value).__name__}")


def _status(value, name):
    if value not in STATUSES:
        raise RecordError(f"{name} must be one of {STATUSES}, got {value!r}")


_FIELDS = {
    "run_id": _safe_part,
    "query_id": _safe_part,
    "agent_id": _safe_part,
    "attempt": lambda v, n: _int(v, n, 1),
    "model": lambda v, n: _mapping(v, n, {"tag": _text, "digest": _text, "quantization": _text}),
    "temperature": _number,
    "seed": lambda v, n: _int(v, n, 0),
    "num_ctx": lambda v, n: _int(v, n, 1),
    "num_predict": lambda v, n: _int(v, n, 1),
    "prompt_version": _text,
    "tool_config": lambda v, n: _mapping(v, n, {
        "tool_version": _text, "page_size": lambda w, m: _int(w, m, 1),
        "budget": lambda w, m: _int(w, m, 0), "ordering_rule": _text,
        "tool_schema_sha256": _sha256, "prompt_values": _object}),
    "kg_fingerprint": _sha256,
    "biohopr_revision": _text,
    "git_commit": _text,
    "timestamps": lambda v, n: _mapping(v, n, {"started_at": _text, "finished_at": _text}),
    "messages": _list,
    "call_log": _list,
    "token_counts": _container,
    "raw_final_output": _optional_text,
    "status": _status,
    "cause": lambda v, n: None,  # checked jointly with status in _validate_fields
}


def _validate_fields(record: dict) -> None:
    if not isinstance(record, dict):
        raise RecordError(f"record must be an object, got {type(record).__name__}")
    allowed = set(_FIELDS) | set(_OPTIONAL_LISTS) | set(_DERIVED)
    missing = sorted(set(_FIELDS) - set(record))
    unknown = sorted(set(record) - allowed)
    if missing or unknown:
        raise RecordError(f"record fields: missing {missing}, unknown {unknown}")
    for key, check in _FIELDS.items():
        check(record[key], key)
    for key in _OPTIONAL_LISTS:
        if key in record:
            _list(record[key], key)
    if record["status"] == "ERROR":
        if record["cause"] not in ERROR_CAUSES:
            raise RecordError(f"status ERROR needs cause in {ERROR_CAUSES}, got {record['cause']!r}")
    elif record["cause"] is not None:
        raise RecordError(f"cause must be null for status {record['status']}, got {record['cause']!r}")


# ---------------------------------------------------------------------------------------------
# Trace graph and appeared entities (§11)
# ---------------------------------------------------------------------------------------------

@dataclass(frozen=True, order=True)
class Edge:
    """A trace-graph edge u –label→ v with its creation index (§11)."""

    creation_index: int
    u: str
    label: str
    v: str

    def to_json(self) -> dict:
        return {"creation_index": self.creation_index, "u": self.u, "label": self.label, "v": self.v}


@dataclass(frozen=True)
class TraceGraph:
    """TG_i: edges sorted by (creation index, numeric u, label, numeric v)."""

    edges: tuple[Edge, ...]

    def to_json(self) -> list[dict]:
        return [edge.to_json() for edge in self.edges]

    @classmethod
    def from_json(cls, data: list[dict]) -> "TraceGraph":
        return cls(_sorted_edges(Edge(item["creation_index"], item["u"], item["label"], item["v"])
                                 for item in data))


def _sorted_edges(edges) -> tuple[Edge, ...]:
    return tuple(sorted(edges, key=lambda e: (e.creation_index, int(e.u), e.label, int(e.v))))


def _canonical_id(value, context: str) -> str:
    """Canonical node IDs are decimal strings (§3.2); a JSON integer is accepted as its string."""
    if type(value) is int and value >= 0:
        value = str(value)
    if not isinstance(value, str) or not _CANONICAL_ID.fullmatch(value):
        raise RecordError(f"{context}: {value!r} is not a canonical node ID")
    return value


def _successful_calls(call_log: list):
    """Yield (index, entry) for successful calls; reject logs whose flag contradicts the result."""
    for index, entry in enumerate(call_log):
        where = f"call_log[{index}]"
        if not isinstance(entry, dict) or not isinstance(entry.get("tool"), str):
            raise RecordError(f"{where}: entry must be an object with a string 'tool'")
        if not isinstance(entry.get("arguments"), dict) or type(entry.get("success")) is not bool:
            raise RecordError(f"{where}: entry needs object 'arguments' and boolean 'success'")
        if entry["success"] != isinstance(entry.get("result"), dict):
            raise RecordError(f"{where}: success={entry['success']} contradicts result "
                              f"{type(entry.get('result')).__name__}")
        if entry["success"]:
            yield index, entry


def build_trace_graph(record: dict) -> TraceGraph:
    """Build TG_i from the stored raw tool results in ``record['call_log']`` (§11)."""
    first: dict[tuple[str, str, str], int] = {}
    for index, entry in _successful_calls(record["call_log"]):
        if entry["tool"] != "get_neighbors":
            continue
        where = f"call_log[{index}]"
        u = _canonical_id(entry["arguments"].get("entity_id"), f"{where}.arguments.entity_id")
        label = entry["arguments"].get("relation")
        if not isinstance(label, str):
            raise RecordError(f"{where}: successful get_neighbors without a string relation")
        items = entry["result"].get("items")
        if not isinstance(items, list):
            raise RecordError(f"{where}: successful get_neighbors result has no items list")
        for position, item in enumerate(items):
            v = _canonical_id(item.get("id") if isinstance(item, dict) else None,
                              f"{where}.result.items[{position}].id")
            first.setdefault((u, label, v), index)
    return TraceGraph(_sorted_edges(Edge(i, u, r, v) for (u, r, v), i in first.items()))


def appeared_entities(record: dict) -> tuple[str, ...]:
    """IDs returned by any successful call: neighbor items and inspect_entity subjects (§11)."""
    seen = set()
    for index, entry in _successful_calls(record["call_log"]):
        where = f"call_log[{index}]"
        if entry["tool"] == "inspect_entity":
            seen.add(_canonical_id(entry["result"].get("id"), f"{where}.result.id"))
        elif entry["tool"] == "get_neighbors":
            for position, item in enumerate(entry["result"].get("items", [])):
                seen.add(_canonical_id(item.get("id") if isinstance(item, dict) else None,
                                       f"{where}.result.items[{position}].id"))
    return tuple(sorted(seen, key=int))


# ---------------------------------------------------------------------------------------------
# Paths (§14.1–14.2)
# ---------------------------------------------------------------------------------------------

Path_ = tuple[Edge, ...]


def path_order_key(path: Path_) -> tuple:
    """§14.2 total order: length, largest creation index, then (numeric u, label) per edge."""
    return (len(path), max((e.creation_index for e in path), default=-1),
            tuple((int(e.u), e.label) for e in path))


@dataclass(frozen=True)
class PathSet:
    """``primary`` is None when TG_i has no path from s to x; ``simple`` holds every simple
    path of length ≤ 3, sorted by the §14.2 order (length-0 path included when x = s)."""

    primary: Path_ | None
    simple: tuple[Path_, ...]


def _out_edges(edges) -> dict[str, list[Edge]]:
    out: dict[str, list[Edge]] = {}
    for edge in edges:
        out.setdefault(edge.u, []).append(edge)
    return out


def _distances(out: dict[str, list[Edge]], start: str) -> dict[str, int]:
    dist, queue = {start: 0}, deque([start])
    while queue:
        node = queue.popleft()
        for edge in out.get(node, ()):
            if edge.v not in dist:
                dist[edge.v] = dist[node] + 1
                queue.append(edge.v)
    return dist


def primary_path(graph: TraceGraph, s, x) -> Path_ | None:
    """The first s→x path in the §14.2 order, or None if x is unreachable from s.

    The first path is always a shortest one, so: d = shortest length; c = the smallest
    creation-index threshold under which a length-d path still exists (every length-d path in
    that subgraph then has largest index exactly c); then walk from s choosing, at each step,
    the smallest (label, numeric v) among edges that stay on a length-d path. Under the
    (numeric u, label) sequence, u is already fixed at each step, so this greedy choice is
    the lexicographic minimum. Tests compare it against brute-force enumeration.
    """
    s, x = _canonical_id(s, "s"), _canonical_id(x, "x")
    if s == x:
        return ()
    full = _distances(_out_edges(graph.edges), s)
    if x not in full:
        return None
    d = full[x]
    for c in sorted({e.creation_index for e in graph.edges}):
        allowed = [e for e in graph.edges if e.creation_index <= c]
        if _distances(_out_edges(allowed), s).get(x) == d:
            break
    reverse: dict[str, list[Edge]] = {}
    for edge in allowed:
        reverse.setdefault(edge.v, []).append(Edge(edge.creation_index, edge.v, edge.label, edge.u))
    to_x = _distances(reverse, x)
    out, path, node = _out_edges(allowed), [], s
    for step in range(d):
        remaining = d - step - 1
        node_edge = min((e for e in out[node] if to_x.get(e.v) == remaining),
                        key=lambda e: (e.label, int(e.v)))
        path.append(node_edge)
        node = node_edge.v
    return tuple(path)


def simple_paths(graph: TraceGraph, s, x, max_length: int = 3) -> tuple[Path_, ...]:
    """All simple s→x paths with at most ``max_length`` edges, in §14.2 order."""
    s, x = _canonical_id(s, "s"), _canonical_id(x, "x")
    if s == x:
        return ((),)
    out, found = _out_edges(graph.edges), []

    def extend(node, visited, path):
        for edge in out.get(node, ()):
            if edge.v in visited:
                continue
            if edge.v == x:
                found.append(tuple(path + [edge]))
            elif len(path) + 1 < max_length:
                extend(edge.v, visited | {edge.v}, path + [edge])

    extend(s, {s}, [])
    return tuple(sorted(found, key=path_order_key))


def paths(graph: TraceGraph, s, x) -> PathSet:
    """Primary path and all simple paths of length ≤ 3 from s to x (§14.1–14.2)."""
    return PathSet(primary_path(graph, s, x), simple_paths(graph, s, x))


# ---------------------------------------------------------------------------------------------
# Records: construction, reconstruction, write-once save and load (§19, §19.1)
# ---------------------------------------------------------------------------------------------

def make_episode_record(**fields) -> dict:
    """Validate caller-supplied §19 fields and add the derived trace graph and appeared set."""
    if overlap := sorted(set(fields) & set(_DERIVED)):
        raise RecordError(f"derived fields are computed here, not supplied: {overlap}")
    record = {key: [] for key in _OPTIONAL_LISTS} | dict(fields)
    _validate_fields(record)
    record["trace_graph"] = build_trace_graph(record).to_json()
    record["appeared_entities"] = list(appeared_entities(record))
    record["protocol_version"] = PROTOCOL_VERSION
    record["record_schema_version"] = RECORD_SCHEMA_VERSION
    return record


def verify_reconstruction(record: dict) -> None:
    """§19.1: rebuilding TG_i (and the appeared set) from the raw tool results must equal what
    is stored. Raises RecordError naming the differing edges."""
    _validate_fields(record)
    stored = set(TraceGraph.from_json(record["trace_graph"]).edges)
    rebuilt = set(build_trace_graph(record).edges)
    if stored != rebuilt:
        raise RecordError(f"trace graph mismatch for {record['query_id']}/{record['agent_id']}"
                          f"/a{record['attempt']}: only stored {sorted(stored - rebuilt)}, "
                          f"only rebuilt {sorted(rebuilt - stored)}")
    if record["appeared_entities"] != list(appeared_entities(record)):
        raise RecordError(f"appeared_entities mismatch for {record['query_id']}"
                          f"/{record['agent_id']}/a{record['attempt']}")


def record_path(runs_root, run_id: str, query_id: str, agent_id: str, attempt: int) -> Path:
    """results/runs/<run_id>/<query_id>__<agent_id>__a<attempt>.json (runbook S12)."""
    for value, name in ((run_id, "run_id"), (query_id, "query_id"), (agent_id, "agent_id")):
        _safe_part(value, name)
    _int(attempt, "attempt", 1)
    return Path(runs_root) / run_id / f"{query_id}__{agent_id}__a{attempt}.json"


def publish_once(source: Path, destination: Path) -> None:
    """Publish a complete staged file beside its target without replacing it (protocol §19)."""
    if os.name == "nt":
        os.rename(source, destination)  # Windows refuses existing targets; POSIX rename overwrites.
    else:
        os.link(source, destination)


def save_episode_record(record: dict, runs_root=DEFAULT_RUNS_ROOT) -> Path:
    """Write the record once, atomically; raise FileExistsError if it already exists (§19)."""
    verify_reconstruction(record)
    text = json.dumps(record, ensure_ascii=False, sort_keys=True, indent=2, allow_nan=False) + "\n"
    if json.loads(text) != record:
        raise RecordError("record does not round-trip through JSON (non-JSON value types?)")
    final = record_path(runs_root, record["run_id"], record["query_id"],
                        record["agent_id"], record["attempt"])
    if final.exists():
        raise FileExistsError(f"episode record already exists, refusing to overwrite: {final}")
    final.parent.mkdir(parents=True, exist_ok=True)
    temporary = final.parent / f".{final.name}.{uuid.uuid4().hex}.tmp"
    try:
        with open(temporary, "x", encoding="utf-8", newline="\n") as handle:
            handle.write(text)
            handle.flush()
            os.fsync(handle.fileno())
        publish_once(temporary, final)
    finally:
        temporary.unlink(missing_ok=True)
    return final


def load_episode_record(path) -> dict:
    """Read a saved record and check it (§19.1 reconstruction included)."""
    with open(path, encoding="utf-8") as handle:
        record = json.load(handle)
    verify_reconstruction(record)
    return record
