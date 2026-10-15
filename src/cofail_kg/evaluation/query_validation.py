"""S8 query labels and S9 evidence, protocol §6–§7.1; no inclusion decisions."""

import re
from collections import Counter

REASONS = ("QUERY_NOT_FOUND", "QUESTION_TEXT_MISMATCH", "BRIDGE_NOT_FOUND",
           "GOLD_BRIDGE_NOT_VALID", "GOLD_UNMAPPED", "GOLD_MISSING_FROM_KG", "EXTRA_TARGETS")


def validate_queries(queries, target_counts, sample_ids, ambiguity_tags):
    records = []
    for q in sorted(queries, key=lambda q: q["query_id"]):
        denominator = target_counts.get(q["Type_T"], 0)
        if denominator <= 0:
            raise ValueError(f"Missing or zero target type count: {q['Type_T']}")
        roles = {r["role"] for r in q["unresolved_names"]}
        gold, reference = set(q["A_star_q"]), set(q["G_q"])
        source_missing = q["s"] is None
        flags = dict(zip(REASONS, (
            source_missing, len(set(q["question_texts"])) != 1, "bridge" in roles,
            "NA" if source_missing else bool(set(q["gold_bridges"]) - set(q["B_q"])),
            "answer" in roles,
            "NA" if source_missing else bool(gold - reference),
            "NA" if source_missing else bool(reference - gold))))
        reasons = [k for k in REASONS if flags[k] is True]
        names = sorted(set(q["gold_bridge_names"] + q["gold_answer_names"]))
        leaked = [name for name in names if len(name) >= 4 and any(
            re.search(r"(?<!\w)" + re.escape(name) + r"(?!\w)", text, re.IGNORECASE)
            for text in q["question_texts"])]
        bridges = len(q["B_q"])
        overlap = sorted(set(q["row_ids"]) & sample_ids)
        records.append({
            "query_id": q["query_id"], "relation_type": q["relation_type"],
            "construction": q["construction"], "ambiguity_tag": ambiguity_tags[q["relation_type"]],
            "status": "INCONSISTENT" if reasons else "CONSISTENT",
            "primary_reason": reasons[0] if reasons else "NONE", "reason_codes": reasons, **flags,
            "bridge_multiplicity": "NO_BRIDGE" if bridges == 0 else "SINGLE_BRIDGE" if bridges == 1 else "MULTI_BRIDGE",
            "bridge_count": bridges, "dead_end_bridge_count": len(q["dead_end_bridges"]),
            "leaky_question": bool(leaked), "leaked_names": leaked,
            "target_count": len(q["T_q"]), "target_type": q["Type_T"], "target_type_nodes": denominator,
            "saturation_share": len(q["T_q"]) / denominator,
            "contains_s6_validation_row": bool(overlap), "s6_validation_row_ids": overlap,
            "row_ids": q["row_ids"],
            "gold_missing_ids": sorted(gold - reference, key=int) if not source_missing else [],
            "extra_target_ids": sorted(reference - gold, key=int) if not source_missing else [],
        })
    return records


def summarize(records):
    def counts(group):
        return {"queries": len(group), **{key: dict(sorted(Counter(r[key] for r in group).items()))
                for key in ("status", "primary_reason", "bridge_multiplicity")},
                "leaky_questions": sum(r["leaky_question"] for r in group),
                "s6_validation_queries": sum(r["contains_s6_validation_row"] for r in group),
                "reason_codes": {code: sum(r[code] is True for r in group) for code in REASONS}}
    return {"overall": counts(records), **{
        "by_" + field: {value: counts([r for r in records if r[field] == value])
                        for value in sorted({r[field] for r in records})}
        for field in ("relation_type", "construction", "ambiguity_tag", "bridge_multiplicity")}}
