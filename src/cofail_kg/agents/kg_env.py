"""Read-only agent tools, budgets and complete call logs (protocol §3.2, §9.1, §10).

Phase 2 (protocol §10, §21): an optional query-local overlay hides edges. Counts and lists are then
computed after hiding, so the agent sees a consistent graph; without an overlay every result is the
unmodified index output.
"""

from __future__ import annotations

from copy import deepcopy
from dataclasses import dataclass
from datetime import datetime, timezone
import json
from pathlib import Path
from time import perf_counter

from cofail_kg.kg.primekg_index import PrimeKGIndex

_MISSING = object()
BUDGET_EXHAUSTED = "Tool budget exhausted. Give your final answer now."
OVERLAY_KEYS = {"query_id", "hide_labels", "hide_edges"}


@dataclass(frozen=True)
class ToolConfig:
    """Explicit episode configuration (§9.1); screening uses page_size=50, budget=30."""

    page_size: int
    budget: int

    def __post_init__(self) -> None:
        if type(self.page_size) is not int or self.page_size < 1:
            raise ValueError("page_size must be a positive integer")
        if type(self.budget) is not int or self.budget < 0:
            raise ValueError("budget must be a nonnegative integer")


def _node_id(value, where: str) -> str:
    if not isinstance(value, str) or not value.isdigit() or value != str(int(value)):
        raise ValueError(f"{where}: node ID must be a canonical decimal string, got {value!r}")
    return value


@dataclass(frozen=True)
class Overlay:
    """Edges hidden for one query (§21 surgery): label r at node u, and/or single edges (u, r, v).

    Under the frozen either-direction convention (§3.2) a hidden edge is hidden from both endpoints, and
    hiding label r at u hides every edge with label r that has u as an endpoint.
    """

    query_id: str
    hide_labels: tuple[tuple[str, str], ...] = ()
    hide_edges: tuple[tuple[str, str, str], ...] = ()

    def __post_init__(self) -> None:
        if not isinstance(self.query_id, str) or not self.query_id:
            raise ValueError("overlay query_id must be a nonempty string")
        where = f"overlay {self.query_id}"
        labels = tuple((_node_id(u, where), r) for u, r in self.hide_labels)
        edges = tuple((_node_id(u, where), r, _node_id(v, where)) for u, r, v in self.hide_edges)
        if any(not isinstance(r, str) or not r for _, r in labels) or any(
                not isinstance(r, str) or not r for _, r, _ in edges):
            raise ValueError(f"{where}: relation labels must be nonempty strings")
        if not labels and not edges:
            raise ValueError(f"{where}: hides nothing")
        if len(set(labels)) != len(labels) or len(set(edges)) != len(edges):
            raise ValueError(f"{where}: duplicate entries")
        object.__setattr__(self, "hide_labels", tuple(sorted(labels, key=lambda p: (int(p[0]), p[1]))))
        object.__setattr__(self, "hide_edges",
                           tuple(sorted(edges, key=lambda e: (int(e[0]), e[1], int(e[2])))))

    def hides(self, u: str, label: str, v: str) -> bool:
        """True if the edge u –label– v (either direction) is hidden."""
        return (any(r == label and w in (u, v) for w, r in self.hide_labels)
                or any(r == label and {a, b} == {u, v} for a, r, b in self.hide_edges))

    def to_json(self) -> dict:
        return {"query_id": self.query_id, "hide_labels": [list(p) for p in self.hide_labels],
                "hide_edges": [list(e) for e in self.hide_edges]}


def load_overlays(path) -> dict[str, Overlay]:
    """Read an overlay file: one JSON object per line with exactly `OVERLAY_KEYS` (protocol §10).

    Nothing but edge identities to hide is accepted, so no evaluation field can reach agent-facing
    code. One line per query; duplicates and malformed lines are refused.
    """
    overlays: dict[str, Overlay] = {}
    for number, line in enumerate(Path(path).read_text(encoding="utf-8").splitlines(), 1):
        if not line.strip():
            continue
        row = json.loads(line)
        if not isinstance(row, dict) or set(row) != OVERLAY_KEYS:
            raise ValueError(f"{path}:{number}: an overlay line has exactly the keys {sorted(OVERLAY_KEYS)}")
        if (not isinstance(row["hide_labels"], list) or not isinstance(row["hide_edges"], list)
                or any(not isinstance(p, list) or len(p) != 2 for p in row["hide_labels"])
                or any(not isinstance(e, list) or len(e) != 3 for e in row["hide_edges"])):
            raise ValueError(f"{path}:{number}: hide_labels holds [u, r] pairs, hide_edges [u, r, v] triples")
        overlay = Overlay(row["query_id"], tuple(map(tuple, row["hide_labels"])),
                          tuple(map(tuple, row["hide_edges"])))
        if overlay.query_id in overlays:
            raise ValueError(f"{path}:{number}: duplicate overlay for {overlay.query_id}")
        overlays[overlay.query_id] = overlay
    if not overlays:
        raise ValueError(f"{path}: no overlay")
    return overlays


class KGEnvironment:
    """One sequential episode on the S4 index (§10), with no file reads of its own.

    `call` accepts a decoded argument object. Only declared arguments are used;
    extra keys remain in the log. Success returns a dict; protocol errors return
    their exact strings. Unexpected index failures are logged and re-raised to
    the runner, never converted into model-visible diagnostic text.

    `overlay` (Phase 2) must belong to this episode's `query_id`; its hidden edges are removed from
    every count and list before anything is returned (§10).
    """

    def __init__(self, index: PrimeKGIndex, config: ToolConfig, *, overlay: Overlay | None = None,
                 query_id: str | None = None):
        if index.convention.mode != "either":
            raise ValueError("Agent tools require the frozen either-direction convention")
        if overlay is not None and overlay.query_id != query_id:
            raise ValueError(f"overlay for {overlay.query_id} cannot be used in an episode of {query_id}")
        self._index = index
        self.config = config
        self.overlay = overlay
        self._node_types = frozenset(index.metadata["node_type_counts"])
        self._calls_used = 0
        self.call_log: list[dict] = []

    @property
    def calls_used(self) -> int:
        """Calls charged to the budget, including errors but excluding exhausted replies."""
        return self._calls_used

    def inspect_entity(self, entity_id=_MISSING) -> dict | str:
        """Return node identity and sorted incident-relation summaries (§10)."""
        args = {} if entity_id is _MISSING else {"entity_id": entity_id}
        return self.call("inspect_entity", args)

    def get_neighbors(self, entity_id=_MISSING, relation=_MISSING,
                      neighbor_type=None, page=1) -> dict | str:
        """Return a complete, explicitly paginated slice of unique neighbors (§10)."""
        args = {"neighbor_type": neighbor_type, "page": page}
        if entity_id is not _MISSING:
            args["entity_id"] = entity_id
        if relation is not _MISSING:
            args["relation"] = relation
        return self.call("get_neighbors", args)

    def call(self, name: str, arguments: dict) -> dict | str:
        """Dispatch only the two tools; every attempt is logged and budgeted (§10)."""
        entry = {"tool": name, "arguments": deepcopy(arguments),
                 "timestamp": datetime.now(timezone.utc).isoformat(), "success": False}
        started = perf_counter()
        try:
            if self._calls_used >= self.config.budget:
                result = BUDGET_EXHAUSTED
            else:
                self._calls_used += 1
                result = self._execute(name, arguments)
            entry["result"] = deepcopy(result)
            entry["success"] = isinstance(result, dict)
            return result
        except Exception as error:
            entry["internal_error"] = f"{type(error).__name__}: {error}"
            raise
        finally:
            entry["elapsed_seconds"] = perf_counter() - started
            self.call_log.append(entry)

    def _execute(self, name: str, args: dict) -> dict | str:
        if name not in ("inspect_entity", "get_neighbors"):
            return f"Error: unknown tool {name}."
        required = ("entity_id",) if name == "inspect_entity" else ("entity_id", "relation")
        for key in required:
            if key not in args:
                return f"Error: missing argument {key}."
        entity_id = args["entity_id"]
        try:
            node = self._index.get_node(entity_id)
        except KeyError:
            return f"Error: unknown entity ID {entity_id}."
        relations = self._relations(node["id"])
        if name == "inspect_entity":
            return {key: node[key] for key in ("id", "name", "type")} | {"relations": relations}

        relation = args["relation"]
        if not isinstance(relation, str) or relation not in [r["label"] for r in relations]:
            return f"Error: entity {entity_id} has no relation {relation}."
        kind = args.get("neighbor_type")
        if kind is not None and (not isinstance(kind, str) or kind not in self._node_types):
            return f"Error: unknown neighbor_type {kind}."
        neighbors = self._neighbors(node["id"], relation, kind)
        total = len(neighbors)
        page_size = self.config.page_size
        last_page = max(1, (total + page_size - 1) // page_size)
        page = args.get("page", 1)
        if type(page) is not int or not 1 <= page <= last_page:
            return f"Error: page must be an integer from 1 to {last_page}."
        items = [{key: n[key] for key in ("id", "name", "type", "display_labels")}
                 for n in neighbors[(page - 1) * page_size:page * page_size]]
        return {"items": items, "total_count": total, "page": page,
                "page_size": page_size, "has_more": page < last_page}

    def _neighbors(self, node_id: str, label: str, kind: str | None) -> list[dict]:
        neighbors = self._index.neighbors(node_id, label, kind)
        if self.overlay is None:
            return neighbors
        return [n for n in neighbors if not self.overlay.hides(node_id, label, n["id"])]

    def _relations(self, node_id: str) -> list[dict]:
        """§10 relation summaries; with an overlay, recomputed from the neighbours left visible.

        A label whose edges at this node are all hidden is not listed.
        """
        relations = self._index.relations_of(node_id)
        if self.overlay is None:
            return relations
        out = []
        for relation in relations:
            visible = self._neighbors(node_id, relation["label"], None)
            if len(visible) == relation["neighbor_count"]:
                out.append(relation)
            elif visible:
                out.append({"label": relation["label"],
                            "display_labels": sorted({d for n in visible for d in n["display_labels"]}),
                            "neighbor_types": sorted({n["type"] for n in visible}),
                            "neighbor_count": len(visible)})
        return out
