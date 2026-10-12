"""Read-only PrimeKG index (protocol §3.2, §10, §12, §15; runbook S4).

Canonical IDs are returned as decimal strings and ordered numerically. Duplicate
stored edges are kept in the cache but count once when listing unique neighbours.
"""

from __future__ import annotations

import unicodedata
from collections import defaultdict
from dataclasses import dataclass
from pathlib import Path

import numpy as np
import pandas as pd

from cofail_kg.kg.prepare import load_cache_metadata


def normalize_name(name: str) -> str:
    """Protocol §12: lower-case, NFKC, whitespace collapse; trim approved 2026-10-12."""
    return " ".join(unicodedata.normalize("NFKC", name.lower()).split())


@dataclass(frozen=True)
class EdgeConvention:
    """One traversal policy for neighbours, relation summaries and degree (§3.2)."""

    mode: str = "either"

    def __post_init__(self) -> None:
        if self.mode not in ("either", "outgoing"):
            raise ValueError(f"Unsupported edge convention: {self.mode}")

    def sides(self) -> tuple[tuple[str, str], ...]:
        sides = (("x_index", "y_index"),)
        return sides + (("y_index", "x_index"),) if self.mode == "either" else sides


class PrimeKGIndex:
    """Load and verify the S4 cache; no BioHopR or evaluation files are read.

    Lookups return fresh dictionaries; ambiguous names return all matches. Unknown
    node IDs raise KeyError, while unmatched label/type filters return empty lists.
    Two sorted edge-position arrays avoid a whole-graph scan on every lookup.
    """

    def __init__(self, cache_dir: Path | str = "data/cache", *, convention: EdgeConvention | None = None):
        cache_dir = Path(cache_dir)
        self.metadata = load_cache_metadata(cache_dir)
        self.convention = convention or EdgeConvention(self.metadata["edge_convention"])
        nodes = pd.read_parquet(cache_dir / "primekg_nodes.parquet").sort_values("node_index")
        self._node_ids = nodes.node_index.to_numpy()
        self._nodes = {}
        self._names: dict[str, list[str]] = defaultdict(list)
        for index, identifier, kind, name, source in nodes.itertuples(index=False, name=None):
            node_id = str(index)
            self._nodes[node_id] = {"id": node_id, "source_id": identifier,
                                    "type": kind, "name": name, "source": source}
            self._names[normalize_name(name)].append(node_id)
        self._edges = pd.read_parquet(cache_dir / "primekg_edges.parquet")
        for field in ("relation", "display_relation"):
            self._edges[field] = self._edges[field].astype("category")
        self._adjacency = {}
        for source, _ in self.convention.sides():
            endpoints = self._edges[source].to_numpy()
            order = np.argsort(endpoints, kind="stable")
            sorted_endpoints = endpoints[order]
            starts = np.searchsorted(sorted_endpoints, self._node_ids, side="left")
            stops = np.searchsorted(sorted_endpoints, self._node_ids, side="right")
            self._adjacency[source] = (order, starts, stops)

    def get_node(self, node_id: str | int) -> dict:
        """Return canonical id, source_id, name, type and source (§3.2)."""
        try:
            return self._nodes[str(node_id)].copy()
        except KeyError:
            raise KeyError(f"Unknown node ID: {node_id}") from None

    def find_by_name(self, name: str, node_type: str | None = None) -> list[dict]:
        """Return every exact normalized match, with optional type filter (§12)."""
        return [self.get_node(node_id) for node_id in self._names.get(normalize_name(name), ())
                if node_type is None or self._nodes[node_id]["type"] == node_type]

    def _incident(self, node_id: str | int) -> pd.DataFrame:
        node = self.get_node(node_id)
        position = np.searchsorted(self._node_ids, int(node["id"]))
        frames = []
        for source, target in self.convention.sides():
            order, starts, stops = self._adjacency[source]
            rows = self._edges.iloc[order[starts[position]:stops[position]]]
            frames.append(rows[[target, "relation", "display_relation"]].rename(columns={target: "neighbor_id"}))
        return pd.concat(frames, ignore_index=True)

    def neighbors(self, node_id: str | int, label: str | None = None,
                  neighbor_type: str | None = None) -> list[dict]:
        """Unique neighbours in numeric canonical-ID order (§3.2, §10)."""
        rows = self._incident(node_id)
        if label is not None:
            rows = rows[rows.relation == label]
        result = []
        for index, group in rows.groupby("neighbor_id", sort=True):
            node = self.get_node(int(index))
            if neighbor_type is None or node["type"] == neighbor_type:
                node["display_labels"] = sorted(group.display_relation.unique())
                result.append(node)
        return result

    def relations_of(self, node_id: str | int) -> list[dict]:
        """Labels, display labels, neighbour types and unique counts (§10)."""
        rows = self._incident(node_id)
        result = []
        for label in sorted(rows.relation.unique()):
            related = rows[rows.relation == label]
            neighbors = np.unique(related.neighbor_id)
            result.append({
                "label": label,
                "display_labels": sorted(related.display_relation.unique()),
                "neighbor_types": sorted({self._nodes[str(index)]["type"] for index in neighbors}),
                "neighbor_count": len(neighbors),
            })
        return result

    def degree(self, node_id: str | int) -> int:
        """Number of unique neighbours over all labels (§15)."""
        return self._incident(node_id).neighbor_id.nunique()
