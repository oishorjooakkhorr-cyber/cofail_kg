"""Protocol §12 REFERENCE policy (v1.3.3): resolve a reference name to one PrimeKG node.

Used for query entities, gold bridges and gold answers (§4). Evaluation side only; nothing
agent-facing imports this module. The agent policy is implemented at S16.

* Exact match after lower-casing, NFKC, internal whitespace collapse and trimming
  (`normalize_name`), among nodes of the filter type only. Exactly one -> that node; none or
  several -> unresolved.
* Disease-suffix retry (v1.3.3, decision log 2026-10-13): if NO node of the filter type matches
  and the filter type is `disease`, retry once with " (disease)" appended to the normalized name;
  exactly one -> that node, otherwise unresolved. An ambiguous first match is never retried.
"""

from __future__ import annotations

from dataclasses import dataclass
from typing import Callable

from cofail_kg.kg.primekg_index import normalize_name

DISEASE_TYPE = "disease"
DISEASE_SUFFIX = " (disease)"

Find = Callable[[str, str], list[str]]  # (name, node_type) -> ids of nodes of that type with that name


@dataclass(frozen=True)
class Resolution:
    status: str  # "resolved" | "not_found" | "ambiguous"
    node_id: str | None
    via_suffix: bool = False  # resolved only by the disease-suffix retry

    @property
    def resolved(self) -> bool:
        return self.status == "resolved"


def _classify(hits: list[str]) -> tuple[str, str | None]:
    if len(hits) == 1:
        return "resolved", hits[0]
    return ("not_found" if not hits else "ambiguous"), None


def resolve_reference(find: Find, name: str, node_type: str) -> Resolution:
    """§12 reference policy, with the v1.3.3 disease-suffix retry."""
    hits = find(name, node_type)
    if hits or node_type != DISEASE_TYPE:
        status, node = _classify(hits)
        return Resolution(status, node)
    status, node = _classify(find(normalize_name(name) + DISEASE_SUFFIX, node_type))
    return Resolution(status, node, via_suffix=status == "resolved")


def index_finder(kg) -> Find:
    """`find` callable over a PrimeKGIndex (exact normalized name, exact type filter)."""
    return lambda name, node_type: [n["id"] for n in kg.find_by_name(name, node_type)]
