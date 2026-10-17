"""Protocol §12 reference and agent policies: exact PrimeKG ID/name normalization.

Used for query entities, gold bridges and gold answers (§4). Evaluation side only; nothing
agent-facing imports this module. S16's agent-answer policy is evaluator-side too.

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


@dataclass(frozen=True)
class AgentResolution:
    """§12 per-item result; node_id=None means UNRESOLVED with the given reason."""

    node_id: str | None
    method: str | None = None
    reason: str | None = None
    name_id_mismatch: bool = False
    via_suffix: bool = False


def resolve_agent(kg, item: dict, target_type: str) -> AgentResolution:
    """Protocol §12 AGENT policy for one parsed {id, name} answer.

    Canonical IDs win regardless of target type. NAME_ID_MISMATCH compares the
    submitted name literally with the stored name; name lookup uses normalize_name.
    Only an unknown ID (the index's KeyError) triggers name fallback; other errors
    propagate. The S7 resolver supplies the same typed-name and disease-suffix rules.
    """
    if (not isinstance(item, dict) or type(item.get("id")) not in (str, int)
            or not isinstance(item.get("name"), str)):
        raise ValueError("Each answer needs a string/integer id and string name")
    try:
        node = kg.get_node(str(item["id"]).strip())
    except KeyError:
        node = None
    if node is not None:
        return AgentResolution(node["id"], "ID", name_id_mismatch=item["name"] != node["name"])

    target = resolve_reference(index_finder(kg), item["name"], target_type)
    if target.resolved:
        return AgentResolution(target.node_id, "NAME_TARGET_TYPE", via_suffix=target.via_suffix)
    hits = kg.find_by_name(item["name"])
    if len(hits) == 1:
        return AgentResolution(hits[0]["id"], "NAME_UNIQUE_ANY_TYPE")
    reason = "AMBIGUOUS_NAME" if hits or target.status == "ambiguous" else "NO_MATCH"
    return AgentResolution(None, reason=reason)


@dataclass(frozen=True)
class NormalizedAnswers:
    """§12 item-aligned audit results and indices retained after deduplication."""

    items: list[AgentResolution]
    kept_indices: list[int]

    @property
    def answers(self) -> list[AgentResolution]:
        return [self.items[i] for i in self.kept_indices]

    @property
    def duplicates_removed(self) -> int:
        return len(self.items) - len(self.kept_indices)


def normalize_agent_answers(kg, answers: list[dict], target_type: str) -> NormalizedAnswers:
    """Protocol §12: resolve first, then keep the first occurrence of each answer.

    Resolved duplicates share a canonical ID. Unresolved duplicates must have the
    identical submitted (id, name) pair (researcher decision, 2026-10-17).
    All per-item results remain available, including flags on removed duplicates.
    """
    items = [resolve_agent(kg, item, target_type) for item in answers]
    seen = set()
    kept = []
    for i, (item, result) in enumerate(zip(answers, items)):
        key = (("ID", result.node_id) if result.node_id is not None
               else ("UNRESOLVED", item["id"], item["name"]))
        if key not in seen:
            seen.add(key)
            kept.append(i)
    return NormalizedAnswers(items, kept)
