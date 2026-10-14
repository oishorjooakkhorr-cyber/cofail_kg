"""S8 evaluator-only query validation (protocol §7.1, §6, §5.3; decision rules D2 step 1).

Input is one S7 query record (`reference_sets.build_reference_sets`). Reason codes are
recorded as "TRUE", "FALSE" or "NA"; nothing is excluded and no saturation threshold is
applied here (θ is [TBD@S9], protocol §7.2).

LEAKY_QUESTION interpretation (researcher decision, 2026-10-15, S8 session): a query is leaky
if any of its question texts contains, as a whole word or phrase, a name of at least 4
characters drawn from (a) the BioHopR bridge (`hop1`) and answer strings of any of its rows,
resolved or not, or (b) the PrimeKG node names of its resolved gold bridges and gold answers.
Both name and question text are normalized with the §12 reference normalization
(`normalize_name`); length is measured after normalization; a match must not be preceded or
followed by a Unicode word character (`\\w`).
"""

import re
from collections import Counter

from cofail_kg.kg.primekg_index import normalize_name

QUERY_NOT_FOUND = "QUERY_NOT_FOUND"
QUESTION_TEXT_MISMATCH = "QUESTION_TEXT_MISMATCH"
BRIDGE_NOT_FOUND = "BRIDGE_NOT_FOUND"
GOLD_BRIDGE_NOT_VALID = "GOLD_BRIDGE_NOT_VALID"
GOLD_UNMAPPED = "GOLD_UNMAPPED"
GOLD_MISSING_FROM_KG = "GOLD_MISSING_FROM_KG"
EXTRA_TARGETS = "EXTRA_TARGETS"
# §7.1 order for the primary reason.
REASON_ORDER = (QUERY_NOT_FOUND, QUESTION_TEXT_MISMATCH, BRIDGE_NOT_FOUND, GOLD_BRIDGE_NOT_VALID,
                GOLD_UNMAPPED, GOLD_MISSING_FROM_KG, EXTRA_TARGETS)
# §7.1: recorded as NA when QUERY_NOT_FOUND applies.
NEEDS_S = frozenset({GOLD_BRIDGE_NOT_VALID, GOLD_MISSING_FROM_KG, EXTRA_TARGETS})
LEAK_MIN_LENGTH = 4
STATUSES = ("CONSISTENT", "INCONSISTENT")
MULTIPLICITIES = ("NO_BRIDGE", "SINGLE_BRIDGE", "MULTI_BRIDGE")
CONSTRUCTIONS = ("BRIDGE", "UNION")


def multiplicity(bq_size):
    """§7.1 bridge multiplicity from |B_q|."""
    return MULTIPLICITIES[min(bq_size, 2)]


def construction_reference(q):
    """§6 G_q recomputed from the stored S7 sets: T_q^{B*} for BRIDGE, T_q for UNION (§5.3)."""
    if q["construction"] == "BRIDGE":
        return set(q["T_q_gold_bridges"])
    if q["construction"] == "UNION":
        return set(q["T_q"])
    raise ValueError(f"{q['query_id']}: invalid construction {q['construction']!r}")


def leak_matches(question_texts, named, min_length=LEAK_MIN_LENGTH):
    """§7.1 LEAKY_QUESTION matches (interpretation in the module docstring).

    `named` holds (source, role, name) triples. Returns the sorted distinct triples whose
    normalized name has at least `min_length` characters and occurs as a whole word or phrase
    in any normalized question text.
    """
    texts = sorted({normalize_name(text) for text in question_texts})
    found = set()
    for source, role, name in named:
        needle = normalize_name(name)
        if len(needle) < min_length:
            continue
        pattern = re.compile(r"(?<!\w)" + re.escape(needle) + r"(?!\w)")
        if any(pattern.search(text) for text in texts):
            found.add((source, role, name))
    return sorted(found)


def validate_query(q, *, validation_rows, ambiguity_tag, type_t_node_count, node_name):
    """Return the §7.1 record for one S7 query.

    `validation_rows` is the S6 validation sample (row IDs) of the query's relation type (§5.1);
    `type_t_node_count` is the number of PrimeKG nodes of Type_T (saturation denominator);
    `node_name(node_id)` returns a PrimeKG node name (LEAKY_QUESTION source b).
    """
    query_id = q["query_id"]
    s_found = q["s"] is not None
    gold_bridges, b_q = set(q["gold_bridges"]), set(q["B_q"])
    a_star, g_q = set(q["A_star_q"]), construction_reference(q)
    if g_q != set(q["G_q"]):
        raise ValueError(f"{query_id}: stored G_q differs from the {q['construction']} reference (§6)")
    unresolved_roles = {entry["role"] for entry in q["unresolved_names"]}
    if s_found == ("query" in unresolved_roles):
        raise ValueError(f"{query_id}: s and the unresolved query-name record disagree")

    applies = {
        QUERY_NOT_FOUND: not s_found,
        QUESTION_TEXT_MISMATCH: len(set(q["question_texts"])) > 1,
        BRIDGE_NOT_FOUND: "bridge" in unresolved_roles,
        GOLD_BRIDGE_NOT_VALID: bool(gold_bridges - b_q),
        GOLD_UNMAPPED: "answer" in unresolved_roles,
        GOLD_MISSING_FROM_KG: bool(a_star - g_q),
        EXTRA_TARGETS: bool(g_q - a_star),
    }
    codes = {code: "NA" if code in NEEDS_S and not s_found else str(applies[code]).upper()
             for code in REASON_ORDER}
    reasons = [code for code in REASON_ORDER if codes[code] == "TRUE"]

    # The five §7.1 conditions, computed directly as a guard on the code table.
    conditions = (s_found, len(set(q["question_texts"])) == 1,
                  "bridge" not in unresolved_roles and gold_bridges <= b_q,
                  "answer" not in unresolved_roles, a_star == g_q)
    consistent = all(conditions)
    if consistent != (not reasons):
        raise ValueError(f"{query_id}: §7.1 conditions {conditions} disagree with codes {reasons}")
    if consistent and not a_star <= set(q["T_q"]):
        raise ValueError(f"{query_id}: CONSISTENT query with A*_q not a subset of T_q (§7.1)")

    named = ([("BIOHOPR", "bridge", name) for name in q["gold_bridge_names"]]
             + [("BIOHOPR", "answer", name) for name in q["gold_answer_names"]]
             + [("PRIMEKG", "bridge", node_name(b)) for b in q["gold_bridges"]]
             + [("PRIMEKG", "answer", node_name(t)) for t in q["A_star_q"]])
    matches = leak_matches(q["question_texts"], named)
    in_sample = sorted(set(q["row_ids"]) & set(validation_rows))
    return {
        "query_id": query_id, "relation_type": q["relation_type"], "construction": q["construction"],
        "ambiguity_tag": ambiguity_tag, "Type_S": q["Type_S"], "Type_B": q["Type_B"],
        "Type_T": q["Type_T"], "n_rows": len(q["row_ids"]), "row_ids": list(q["row_ids"]),
        "status": STATUSES[not consistent], "primary_reason": reasons[0] if reasons else "NONE",
        "reason_codes": reasons, **codes,
        "bq_size": len(b_q), "multiplicity": multiplicity(len(b_q)),
        "dead_end_count": len(q["dead_end_bridges"]), "tq_size": len(q["T_q"]),
        "gq_size": len(g_q), "gold_size": len(a_star), "type_t_node_count": type_t_node_count,
        "saturation_share": len(q["T_q"]) / type_t_node_count if s_found else None,
        "leaky_question": bool(matches),
        "leaky_matches": [f"{source}:{role}:{name}" for source, role, name in matches],
        "contains_validation_row": bool(in_sample), "validation_row_ids": in_sample,
    }


def summarize(records):
    """S8 counts: by status, primary reason, relation type, multiplicity, ambiguity tag and
    construction, each with its CONSISTENT/INCONSISTENT split. No D2 share, θ or exclusion."""
    def split(field):
        out = {}
        for value in sorted({r[field] for r in records}):
            group = [r for r in records if r[field] == value]
            out[value] = {"queries": len(group), **{s: sum(r["status"] == s for r in group)
                                                   for s in STATUSES}}
        return out

    return {
        "queries": len(records), "dataset_rows": sum(r["n_rows"] for r in records),
        "by_status": {s: sum(r["status"] == s for r in records) for s in STATUSES},
        "by_primary_reason": dict(sorted(Counter(r["primary_reason"] for r in records).items())),
        "reason_code_counts": {code: {v: sum(r[code] == v for r in records) for v in ("TRUE", "NA")}
                               for code in REASON_ORDER},
        "by_relation_type": split("relation_type"), "by_multiplicity": split("multiplicity"),
        "by_ambiguity_tag": split("ambiguity_tag"), "by_construction": split("construction"),
        "leaky_question": {"queries": sum(r["leaky_question"] for r in records),
                           **{s: sum(r["leaky_question"] and r["status"] == s for r in records)
                              for s in STATUSES}},
        "contains_validation_row": {
            "queries": sum(r["contains_validation_row"] for r in records),
            "validation_rows": sum(len(r["validation_row_ids"]) for r in records),
            "by_relation_type": {t: sum(r["contains_validation_row"] for r in records
                                        if r["relation_type"] == t)
                                 for t in sorted({r["relation_type"] for r in records})}},
        "saturation_na": sum(r["saturation_share"] is None for r in records),
    }
