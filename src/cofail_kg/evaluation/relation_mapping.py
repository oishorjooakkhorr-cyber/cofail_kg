"""S6 proposed relation mapping, protocol §5.1–5.3 and decision rules D1.

Only reference data is used. This module never freezes a mapping or selects a
remaining label-set tie. Integer match counts avoid rounded-score decisions.
"""

from __future__ import annotations

from itertools import combinations

from cofail_kg.data.field_roles import order_key, relation_types
from cofail_kg.evaluation.normalize import resolve_reference


def candidate_sets(labels):
    """Every nonempty subset of relation labels, in stable size/lexical order (§5.1)."""
    labels = sorted(set(labels))
    return [subset for size in range(1, len(labels) + 1) for subset in combinations(labels, size)]


def validation_sample(rows, find):
    """First 30 rows with resolved s and bridge; return skipped rows separately (§5.1).

    Skipped means encountered before the sample filled (or input exhausted).
    Answer resolution does not affect admission into this sample.
    """
    sample, skipped = [], []
    for row in sorted(rows, key=lambda r: order_key(r["row_id"])):
        type_s, type_b, type_t = relation_types(row)
        s = resolve_reference(find, row["hop2"], type_s)
        b = resolve_reference(find, row["hop1"], type_b)
        if not s.resolved or not b.resolved:
            skipped.append({"row_id": row["row_id"], "query_status": s.status, "bridge_status": b.status})
            continue
        answers = [(name, resolve_reference(find, name, type_t)) for name in sorted(set(row["answer"]))]
        sample.append({
            "row_id": row["row_id"], "s": s.node_id, "b": b.node_id,
            "gold": {r.node_id for _, r in answers if r.resolved},
            "unresolved_answers": [{"name": name, "status": r.status} for name, r in answers if not r.resolved],
        })
        if len(sample) == 30:
            break
    return sample, skipped


def select_best(scores):
    """Highest match count, then smallest set, preserving any remaining tie (§5.1)."""
    if not scores:
        return {"matches": None, "sets": [], "status": "NO_CANDIDATES"}
    best = max(scores.values())
    size = min(len(labels) for labels, matches in scores.items() if matches == best)
    winners = sorted(labels for labels, matches in scores.items() if matches == best and len(labels) == size)
    return {"matches": best, "sets": [list(labels) for labels in winners],
            "status": "SELECTED" if len(winners) == 1 else "TIE"}


def ambiguity_tag(candidates1, candidates2, r1, r2):
    """Labels outside the accepted sets determine ambiguity (§5.2)."""
    first, second = bool(set(candidates1) - set(r1)), bool(set(candidates2) - set(r2))
    if first and second:
        return "BOTH_AMBIGUOUS"
    if first:
        return "R1_AMBIGUOUS"
    return "R2_AMBIGUOUS" if second else "NONE"


def _neighbors(neighbors, node, kind, labels):
    by_label = neighbors(node, kind)
    return set().union(*(by_label.get(label, set()) for label in labels))


def _passes(matches, sample_size):
    return matches is not None and sample_size > 0 and 10 * matches >= 9 * sample_size


def _hop2_scores(sample, subsets, neighbors, type_b, type_t, r1, construction):
    scores, differences = {}, {}
    for labels in subsets:
        matched, mismatches = 0, []
        for row in sample:
            bridges = ({row["b"]} if construction == "BRIDGE" else
                       _neighbors(neighbors, row["s"], type_b, r1) - {row["s"]})
            targets = set().union(*(_neighbors(neighbors, b, type_t, labels) for b in bridges)) - {row["s"]}
            if not row["unresolved_answers"] and targets == row["gold"]:
                matched += 1
            else:
                mismatches.append({
                    "row_id": row["row_id"], "query_id": row["s"], "bridge_id": row["b"],
                    "gold_count": len(row["gold"]), "reached_count": len(targets),
                    "missing_ids": sorted(row["gold"] - targets, key=int),
                    "extra_ids": sorted(targets - row["gold"], key=int),
                    "unresolved_answers": row["unresolved_answers"],
                })
        scores[labels], differences[labels] = matched, mismatches
    selected = select_best(scores)
    selected["score"] = selected["matches"] / len(sample) if sample and scores else None
    selected["diagnostics"] = [
        {"labels": labels, "mismatch_row_ids": [r["row_id"] for r in differences[tuple(labels)]],
         "examples": differences[tuple(labels)][:2]}
        for labels in selected["sets"]
    ]
    return scores, selected


def score_type(rows, find, neighbors, candidates1, candidates2, *, s5_failed=False):
    """Score one relation type without resolving scientific ties (§5; Gate D1).

    `neighbors(id, type)` returns sets of IDs keyed by relation label. Candidate
    dictionaries map relation labels to informational display-label lists.
    PENDING/NEEDS_DECISION describe incomplete calculations, not new D1 outcomes.
    """
    if not rows or len({r["relation_hop2"] for r in rows}) != 1:
        raise ValueError("score_type needs nonempty rows from exactly one relation type")
    _, type_b, type_t = relation_types(rows[0])
    sample, skipped = validation_sample(rows, find)
    n = len(sample)
    subsets1, subsets2 = candidate_sets(candidates1), candidate_sets(candidates2)
    scores1 = {labels: sum(r["b"] in _neighbors(neighbors, r["s"], type_b, labels) for r in sample)
               for labels in subsets1}
    hop1 = select_best(scores1)
    hop1["score"] = hop1["matches"] / n if n and scores1 else None
    hop1["diagnostics"] = [
        {"labels": labels, "mismatch_row_ids": [r["row_id"] for r in sample
         if r["b"] not in _neighbors(neighbors, r["s"], type_b, labels)]}
        for labels in hop1["sets"]
    ]
    candidate_scores = [{"hop": 1, "hop1_labels": list(labels), "hop2_labels": None,
                         "sample_size": n, "hop1_matches": matches,
                         "bridge_matches": None, "union_matches": None}
                        for labels, matches in scores1.items()]
    bridge_scores, bridge = _hop2_scores(sample, subsets2, neighbors, type_b, type_t, None, "BRIDGE")
    scenarios = []
    for r1 in hop1["sets"] or [None]:
        if r1 is None:
            union_scores = {}
            union = {"matches": None, "sets": [], "status": "NO_HOP1", "score": None, "diagnostics": []}
        else:
            union_scores, union = _hop2_scores(sample, subsets2, neighbors, type_b, type_t, r1, "UNION")
        bridge_pass, union_pass = _passes(bridge["matches"], n), _passes(union["matches"], n)
        construction = "BRIDGE" if bridge_pass else "UNION" if union_pass else None
        why = ("both reach 90%; BRIDGE tie rule" if bridge_pass and union_pass else
               "only BRIDGE reaches 90%" if bridge_pass else "only UNION reaches 90%" if union_pass else
               "neither construction reaches 90%")
        scenarios.append({"R1": r1, "BRIDGE": bridge, "UNION": union,
                          "construction": construction, "why": why})
        for labels in subsets2:
            candidate_scores.append({"hop": 2, "hop1_labels": r1, "hop2_labels": list(labels),
                                     "sample_size": n, "hop1_matches": hop1["matches"],
                                     "bridge_matches": bridge_scores[labels],
                                     "union_matches": union_scores.get(labels)})

    reasons = []
    if n < 10:
        reasons.append("fewer than 10 validation rows")
    if not candidates1:
        reasons.append("no hop-1 candidate label")
    if not candidates2:
        reasons.append("no hop-2 candidate label")
    if s5_failed:
        reasons.append("failed S5 field-role rule")
    if n and scores1 and not _passes(hop1["matches"], n):
        reasons.append("hop-1 score below 90%")
    if all(s["construction"] is None for s in scenarios):
        reasons.append("hop-2 score below 90% under both constructions")
    r1 = hop1["sets"][0] if hop1["status"] == "SELECTED" else None
    constructions = {s["construction"] for s in scenarios}
    construction = next(iter(constructions)) if len(constructions) == 1 else None
    adopted = scenarios[0][construction] if construction and len(scenarios) == 1 else None
    r2 = adopted["sets"][0] if adopted and adopted["status"] == "SELECTED" else None
    needs_decision = hop1["status"] == "TIE" or any(
        s[s["construction"]]["status"] == "TIE" for s in scenarios if s["construction"])
    status = "FAIL" if reasons else "PENDING" if needs_decision else "PASS"
    return {
        "rows_in_dataset": len(rows), "sample_size": n,
        "sample_row_ids": [r["row_id"] for r in sample], "skipped_unresolved": skipped,
        "sample_unresolved_answers": [{"row_id": r["row_id"], "answers": r["unresolved_answers"]}
                                      for r in sample if r["unresolved_answers"]],
        "candidates": {"hop1": candidates1, "hop2": candidates2},
        "hop1": hop1, "scenarios": scenarios, "R1": r1, "R2": r2,
        "construction": construction, "hop2_score": adopted["score"] if adopted else None,
        "ambiguity_tag": ambiguity_tag(candidates1, candidates2, r1, r2) if r1 and r2 else None,
        "d1_status": status, "fail_reasons": reasons, "needs_decision": needs_decision,
        "candidate_scores": candidate_scores,
    }


def evaluate_d1(per_type):
    """Apply global D1; report counts overall and by proposed construction (§5.3)."""
    passed = [v for v in per_type.values() if v["d1_status"] == "PASS"]
    total_rows = sum(v["rows_in_dataset"] for v in per_type.values())
    pass_rows = sum(v["rows_in_dataset"] for v in passed)
    pending = any(v["needs_decision"] for v in per_type.values())
    splits = {}
    for construction in ("BRIDGE", "UNION", "UNADOPTED"):
        group = [v for v in per_type.values() if (v["construction"] or "UNADOPTED") == construction]
        splits[construction] = {
            "types": len(group), "rows": sum(v["rows_in_dataset"] for v in group),
            "pass_types": sum(v["d1_status"] == "PASS" for v in group),
            "pass_rows": sum(v["rows_in_dataset"] for v in group if v["d1_status"] == "PASS"),
            "fail_types": sum(v["d1_status"] == "FAIL" for v in group),
            "pending_types": sum(v["d1_status"] == "PENDING" for v in group),
        }
    return {
        "status": "NEEDS_DECISION" if pending else "COMPUTED",
        "outcome": None if pending else "STOP" if len(passed) < 6 or 10 * pass_rows < 7 * total_rows else "PROCEED",
        "total_types": len(per_type), "total_rows": total_rows, "pass_types": len(passed),
        "fail_types": sum(v["d1_status"] == "FAIL" for v in per_type.values()),
        "pending_types": sum(v["d1_status"] == "PENDING" for v in per_type.values()),
        "pass_rows": pass_rows, "pass_coverage": pass_rows / total_rows if total_rows else 0,
        "by_construction": splits,
    }
