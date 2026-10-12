"""S5: field-role verification of BioHopR against PrimeKG (protocol §3.1; runbook S5).

Working hypothesis under test (§3.1): `hop2` = query entity s, `hop1` = bridge, `answer` = targets.

* Sample (§3.1): per relation type, rows ordered by SHA256("42" + row_id) (hex digest, ascending),
  first 5 (all if fewer).
* Types: Type_S, Type_B, Type_T from the row's relation type (`relation_hop2`, §0.4), through the
  §3.3 identity type map.
* Resolution (§12 reference policy): exact normalized name among nodes of the filter type; exactly
  one -> resolved, none -> not_found, several -> ambiguous (both unresolved).
* Distinct answer names (§3.1): distinct raw strings of the answer list (§0.4 set semantics:
  order and exact repeats ignored).
* Resolvable / supports: protocol §3.1 "Support", checked with any label under the §3.2 edge
  convention; s never counts as a reachable target (§6).
* Failure rule (§3.1): a type with < 95% supporting resolvable rows, or with no resolvable row,
  fails. One failing type covering <= 1% of all 2-hop rows -> listed for exclusion; more than one
  failing type, or > 1% coverage -> STOP.

Graph access is injected (`find`, `nbrs`, `labels_between`) so the logic is tested on tiny graphs.
"""

from __future__ import annotations

import hashlib
from collections import Counter, defaultdict
from fractions import Fraction
from typing import Callable, Iterable

SAMPLE_SIZE = 5
SUPPORT_THRESHOLD = Fraction(95, 100)
STOP_COVERAGE = Fraction(1, 100)

Find = Callable[[str, str], list[str]]  # (name, node_type) -> node ids
Nbrs = Callable[[str, str], set[str]]  # (node_id, node_type) -> neighbour ids of that type
LabelsBetween = Callable[[str, str], list[str]]  # (u, v) -> sorted labels of edges between them


def order_key(row_id: str) -> str:
    return hashlib.sha256(("42" + row_id).encode("utf-8")).hexdigest()


def relation_types(row: dict) -> tuple[str, str, str]:
    parts = row["relation_hop2"].split(":")
    if len(parts) != 3:
        raise ValueError(f"{row['row_id']}: relation_hop2 {row['relation_hop2']!r} is not S:B:T")
    return parts[0], parts[1], parts[2]


def s5_sample(rows: Iterable[dict], size: int = SAMPLE_SIZE) -> dict[str, list[tuple[int, dict]]]:
    """Per relation type (sorted): [(1-based position, row)] for the first `size` rows."""
    by_type: dict[str, list[dict]] = defaultdict(list)
    for r in rows:
        by_type[r["relation_hop2"]].append(r)
    return {
        t: [(i + 1, r) for i, r in enumerate(sorted(by_type[t], key=lambda r: order_key(r["row_id"]))[:size])]
        for t in sorted(by_type)
    }


def resolve(find: Find, name: str, node_type: str) -> tuple[str, str | None]:
    hits = find(name, node_type)
    if len(hits) == 1:
        return "resolved", hits[0]
    return ("not_found" if not hits else "ambiguous"), None


def analyse_row(row: dict, find: Find, nbrs: Nbrs, labels_between: LabelsBetween) -> dict:
    type_s, type_b, type_t = relation_types(row)
    q_status, s = resolve(find, row["hop2"], type_s)
    b_status, b = resolve(find, row["hop1"], type_b)

    names = sorted(set(row["answer"]))
    resolved: dict[str, str] = {}
    unresolved: list[str] = []
    for name in names:
        status, node = resolve(find, name, type_t)
        if status == "resolved":
            resolved[name] = node
        else:
            unresolved.append(f"{name} [{status}]")

    out = {
        "type_s": type_s, "type_b": type_b, "type_t": type_t,
        "type_fields_agree": row.get("hop2_type") == type_s and row.get("hop1_type") == type_b
                             and row.get("target_type") == type_t,
        "hop2": row["hop2"], "hop2_status": q_status, "hop2_node_id": s,
        "hop1": row["hop1"], "hop1_status": b_status, "hop1_node_id": b,
        "answers_total": len(names), "answers_resolved": len(resolved),
        "answers_unresolved": len(unresolved), "unresolved_answers": unresolved,
        "labels_hop2_hop1": None, "other_type_b_neighbours_of_hop2": None,
        "answers_resolving_to_s": None,
        "reach_via_stored_bridge": None, "reach_only_via_other_bridge": None, "reach_via_neither": None,
        "c1_adjacent": None, "c2_some_answer_via_hop1": None, "c3_every_answer_reachable": None,
        "supports": None,
    }
    enough = len(resolved) >= 1 and 2 * len(resolved) >= len(names)
    out["resolvable"] = s is not None and b is not None and s != b and enough
    if s is None or b is None:
        out["row_status"] = "unresolved_" + ("hop2" if s is None else "hop1")
        return out
    if s == b:
        out["row_status"] = "unresolved_hop1_is_hop2"
        return out

    # graph evidence is reported for every row with both entities resolved
    labels = labels_between(s, b)
    s_type_b = nbrs(s, type_b) - {s}
    others = s_type_b - {b}
    via_b = nbrs(b, type_t) - {s}
    via_other: set[str] = set()
    for o in sorted(others, key=int):
        via_other |= nbrs(o, type_t)
    via_other -= {s}
    targets = list(resolved.values())
    n_b = sum(t in via_b for t in targets)
    n_o = sum(t not in via_b and t in via_other for t in targets)
    out.update({
        "labels_hop2_hop1": labels,
        "other_type_b_neighbours_of_hop2": len(others),
        "answers_resolving_to_s": sum(t == s for t in targets),
        "reach_via_stored_bridge": n_b,
        "reach_only_via_other_bridge": n_o,
        "reach_via_neither": len(targets) - n_b - n_o,
        "c1_adjacent": b in s_type_b,
        "c2_some_answer_via_hop1": n_b >= 1,
        "c3_every_answer_reachable": len(targets) - n_b - n_o == 0,
    })
    if not enough:
        out["row_status"] = "unresolved_answers"
        return out
    out["supports"] = out["c1_adjacent"] and out["c2_some_answer_via_hop1"] and out["c3_every_answer_reachable"]
    out["row_status"] = "supports" if out["supports"] else "conflict"
    return out


def evaluate(records: list[dict], type_row_counts: dict[str, int]) -> dict:
    """Per-type pass/fail and the §3.1 failure rule. `records` carry `relation_type`."""
    total_rows = sum(type_row_counts.values())
    by_type: dict[str, list[dict]] = defaultdict(list)
    for r in records:
        by_type[r["relation_type"]].append(r)
    per_type = {}
    for t in sorted(type_row_counts):
        rs = by_type.get(t, [])
        resolvable = [r for r in rs if r["resolvable"]]
        supporting = [r for r in resolvable if r["supports"]]
        share = Fraction(len(supporting), len(resolvable)) if resolvable else None
        if share is None:
            outcome, reason = "FAIL", "no resolvable sampled row"
        elif share < SUPPORT_THRESHOLD:
            outcome, reason = "FAIL", "support below 95%"
        else:
            outcome, reason = "PASS", ""
        per_type[t] = {
            "rows_in_dataset": type_row_counts[t],
            "sampled": len(rs),
            "resolvable": len(resolvable),
            "unresolved": len(rs) - len(resolvable),
            "supporting": len(supporting),
            "support_share": None if share is None else float(share),
            "outcome": outcome,
            "fail_reason": reason,
            "conflicting_rows": [r["row_id"] for r in resolvable if not r["supports"]],
            "unresolved_rows": [r["row_id"] for r in rs if not r["resolvable"]],
        }
    failing = [t for t, v in per_type.items() if v["outcome"] == "FAIL"]
    coverage = Fraction(sum(type_row_counts[t] for t in failing), total_rows) if total_rows else Fraction(0)
    if not failing:
        decision = "ROLES_SUPPORTED"
    elif len(failing) == 1 and coverage <= STOP_COVERAGE:
        decision = "EXCLUDE_FAILING_TYPE"
    else:
        decision = "STOP"
    return {
        "per_type": per_type,
        "failing_types": failing,
        "failing_rows_in_dataset": sum(type_row_counts[t] for t in failing),
        "total_rows": total_rows,
        "failing_coverage": float(coverage),
        "rule_outcome": decision,
    }


def type_row_counts(rows: Iterable[dict]) -> dict[str, int]:
    return dict(sorted(Counter(r["relation_hop2"] for r in rows).items()))
