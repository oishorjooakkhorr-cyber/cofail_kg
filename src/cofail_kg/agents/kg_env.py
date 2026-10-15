"""Read-only agent tools, budgets and complete call logs (protocol §3.2, §9.1, §10)."""

from __future__ import annotations

from copy import deepcopy
from dataclasses import dataclass
from datetime import datetime, timezone
from time import perf_counter

from cofail_kg.kg.primekg_index import PrimeKGIndex

_MISSING = object()
BUDGET_EXHAUSTED = "Tool budget exhausted. Give your final answer now."


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


class KGEnvironment:
    """One sequential episode on the S4 index (§10), with no file reads of its own.

    `call` accepts a decoded argument object. Only declared arguments are used;
    extra keys remain in the log. Success returns a dict; protocol errors return
    their exact strings. Unexpected index failures are logged and re-raised to
    the runner, never converted into model-visible diagnostic text.
    """

    def __init__(self, index: PrimeKGIndex, config: ToolConfig):
        if index.convention.mode != "either":
            raise ValueError("Agent tools require the frozen either-direction convention")
        self._index = index
        self.config = config
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
        relations = self._index.relations_of(node["id"])
        if name == "inspect_entity":
            return {key: node[key] for key in ("id", "name", "type")} | {"relations": relations}

        relation = args["relation"]
        if not isinstance(relation, str) or relation not in [r["label"] for r in relations]:
            return f"Error: entity {entity_id} has no relation {relation}."
        kind = args.get("neighbor_type")
        if kind is not None and (not isinstance(kind, str) or kind not in self._node_types):
            return f"Error: unknown neighbor_type {kind}."
        neighbors = self._index.neighbors(node["id"], relation, kind)
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
