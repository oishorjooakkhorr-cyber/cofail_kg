"""S7 evaluator-only query grouping and reference sets (protocol §0.4, §4, §6, §12).

Graph access uses the S4 typed, either-direction index. IDs in saved sets are
decimal strings sorted numerically; row IDs and raw names are sorted lexically.
"""

from collections import defaultdict
from functools import lru_cache

from cofail_kg.data.diagnostics import QUESTION_FIELD
from cofail_kg.data.field_roles import relation_types
from cofail_kg.evaluation.normalize import resolve_reference


def build_reference_sets(rows, per_type, find, neighbors):
    """Return query records and (query, bridge, target) records, using only D1 PASS types.

    `neighbors(node, type)` returns {relation label: typed neighbor IDs}, as in
    PrimeKGIndex.neighbors_by_label. Gold-bridge targets include resolved gold
    bridges even when they are not in B_q; S8 subsequently checks validity (§7.1).
    """
    if len({r["row_id"] for r in rows}) != len(rows):
        raise ValueError("Duplicate row_id in reference input")
    for t, spec in per_type.items():
        if spec["d1_status"] == "PASS" and not spec["excluded"]:
            if spec["construction"] not in ("BRIDGE", "UNION"):
                raise ValueError(f"{t}: missing or invalid construction")
            if not spec["R1"] or not spec["R2"]:
                raise ValueError(f"{t}: accepted labels are empty")

    resolve = lru_cache(maxsize=None)(lambda name, kind: resolve_reference(find, name, kind))

    @lru_cache(maxsize=None)
    def reached(node, kind, labels):
        by_label = neighbors(node, kind)
        return frozenset().union(*(by_label.get(label, ()) for label in labels))

    grouped = defaultdict(list)
    for row in sorted(rows, key=lambda r: r["row_id"]):
        t = row["relation_hop2"]
        spec = per_type[t]
        if spec["d1_status"] != "PASS" or spec["excluded"]:
            continue
        source = resolve(row["hop2"], relation_types(row)[0])
        grouped[(t, source.node_id, None if source.resolved else row["row_id"])].append(row)

    queries, targets = [], []
    for members in sorted(grouped.values(), key=lambda group: group[0]["row_id"]):
        first = members[0]
        query_id, t = first["row_id"], first["relation_hop2"]
        type_s, type_b, type_t = relation_types(first)
        spec = per_type[t]
        s = resolve(first["hop2"], type_s).node_id
        gold_bridges, gold_answers = set(), set()
        unresolved, suffix = [], []
        for row in members:
            entities = [("query", row["hop2"], type_s), ("bridge", row["hop1"], type_b)]
            entities += [("answer", name, type_t) for name in sorted(set(row["answer"]))]
            for role, name, kind in entities:
                result = resolve(name, kind)
                record = {"row_id": row["row_id"], "role": role, "name": name}
                if not result.resolved:
                    unresolved.append({**record, "status": result.status})
                elif result.via_suffix:
                    suffix.append({**record, "node_id": result.node_id})
                if result.resolved and role == "bridge":
                    gold_bridges.add(result.node_id)
                if result.resolved and role == "answer":
                    gold_answers.add(result.node_id)

        def bridge_targets(b):
            return reached(b, type_t, tuple(spec["R2"])) - {s}

        candidate_bridges = reached(s, type_b, tuple(spec["R1"])) - {s} if s is not None else set()
        valid, dead, all_targets = set(), set(), set()
        for b in sorted(candidate_bridges, key=int):
            answers = bridge_targets(b)
            (valid if answers else dead).add(b)
            all_targets.update(answers)
            targets.extend({"query_id": query_id, "bridge": b, "target": target}
                           for target in sorted(answers, key=int))
        gold_targets = set().union(*(bridge_targets(b) for b in gold_bridges))
        construction_targets = gold_targets if spec["construction"] == "BRIDGE" else all_targets
        sets = {"gold_bridges": gold_bridges, "B_q": valid, "dead_end_bridges": dead,
                "T_q": all_targets, "T_q_gold_bridges": gold_targets,
                "G_q": construction_targets, "A_star_q": gold_answers}
        queries.append({
            "query_id": query_id, "row_ids": [r["row_id"] for r in members], "s": s,
            "question_texts": [r[QUESTION_FIELD] for r in members],
            "query_names": sorted({r["hop2"] for r in members}),
            "gold_bridge_names": sorted({r["hop1"] for r in members}),
            "gold_answer_names": sorted({name for r in members for name in r["answer"]}),
            "Type_S": type_s, "Type_B": type_b, "Type_T": type_t,
            "relation_type": t, "construction": spec["construction"],
            **{name: sorted(ids, key=int) for name, ids in sets.items()},
            "bq_size": len(valid), "dead_end_size": len(dead), "tq_size": len(all_targets),
            "gold_bridge_tq_size": len(gold_targets), "gq_size": len(construction_targets),
            "gold_size": len(gold_answers), "unresolved_names": unresolved,
            "suffix_resolutions": suffix,
        })
    return queries, targets


def summarize(queries, targets):
    """S7 counts overall and split by frozen answer construction (§5.3, §6)."""
    def counts(group):
        query_ids = {q["query_id"] for q in group}
        return {
            "queries": len(group), "dataset_rows": sum(len(q["row_ids"]) for q in group),
            "relation_types": len({q["relation_type"] for q in group}),
            "unresolved_queries": sum(q["s"] is None for q in group),
            "no_bridge_queries": sum(q["bq_size"] == 0 for q in group),
            "single_bridge_queries": sum(q["bq_size"] == 1 for q in group),
            "multi_bridge_queries": sum(q["bq_size"] > 1 for q in group),
            **{field: sum(q[field] for q in group) for field in
               ("bq_size", "dead_end_size", "tq_size", "gold_bridge_tq_size", "gq_size", "gold_size")},
            "unresolved_names": sum(len(q["unresolved_names"]) for q in group),
            "suffix_resolutions": sum(len(q["suffix_resolutions"]) for q in group),
            "target_rows": sum(r["query_id"] in query_ids for r in targets),
        }
    return {"overall": counts(queries), "by_construction": {
        c: counts([q for q in queries if q["construction"] == c]) for c in ("BRIDGE", "UNION")}}
