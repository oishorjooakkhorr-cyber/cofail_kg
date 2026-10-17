"""Evaluator-only per-agent metrics, frozen protocol §15; no model calls."""

import pandas as pd

from cofail_kg.agents.kg_env import BUDGET_EXHAUSTED
from cofail_kg.agents.run_agent import parse_final
from cofail_kg.agents.trace import appeared_entities, verify_reconstruction
from cofail_kg.evaluation.answer_labels import label_answers
from cofail_kg.evaluation.normalize import normalize_agent_answers
from cofail_kg.evaluation.path_labels import label_paths


LABEL_A = ("GOLD", "GOLD_BRIDGE_EXTRA", "ALT_VALID", "OFF_QUESTION", "UNRESOLVED")
LABEL_B = ("SUPPORTED", "PATH_INVALID", "KG_UNSUPPORTED", "UNGROUNDED", "NOT_APPLICABLE")
REASONS = ("SHORTCUT", "WRONG_RELATION_HOP1", "WRONG_RELATION_HOP2", "WRONG_BRIDGE_TYPE",
           "WRONG_TARGET_TYPE", "WRONG_HOP_COUNT")


def degree_statistics(nodes: pd.DataFrame, edges: pd.DataFrame) -> dict:
    """§3.2/§15 unique either-direction degrees and same-type inclusive percentiles.

    Caller supplies checksum-verified S4 node/edge tables, once per frozen KG.
    Include isolates; duplicate labels, reverse rows and self-loops count once.
    """
    ids = nodes["node_index"]
    if ids.duplicated().any():
        raise ValueError("duplicate node IDs in degree population")
    pairs = edges[["x_index", "y_index"]]
    if not pairs.isin(ids.to_numpy()).all().all():
        raise ValueError("degree edge endpoint absent from node population")
    pairs = pd.concat([pairs, pairs.rename(columns={"x_index": "y_index", "y_index": "x_index"})],
                      ignore_index=True).drop_duplicates()
    degree = pairs.groupby("x_index").size().reindex(ids, fill_value=0)
    table = nodes[["node_index", "node_type"]].set_index("node_index").copy()
    table["degree"] = degree
    table["degree_percentile"] = table.groupby("node_type")["degree"].rank(method="max", pct=True) * 100
    return {str(node): {"degree": int(d), "degree_percentile": float(p)}
            for node, d, p in table[["degree", "degree_percentile"]].itertuples(name=None)}


def agent_metrics(record: dict, reference: dict, mapping: dict, bridge_targets: dict,
                  kg, degrees: dict, *, consistent: bool) -> dict:
    """One §15 row, including answer/bridge diagnostics, from an S12 saved record.

    Inputs: the matching S7 primary-population row, frozen mapping, complete S7
    {bridge: targets} for this query, verified KG and reusable degree_statistics.
    S16-S18 own normalization and labels. JSON null means NA; denominators and
    undefined_counts allow later aggregation to exclude/count undefined values.
    Benchmark and technical-failure conventions: researcher, 2026-10-17.
    """
    verify_reconstruction(record)
    if record["query_id"] != reference["query_id"]:
        raise ValueError("episode and reference query IDs differ")
    bridges = set(reference["B_q"])
    targets = {b: set(xs) for b, xs in bridge_targets.items()}
    if (set(targets) != bridges or any(not xs for xs in targets.values())
            or set().union(*targets.values()) != set(reference["T_q"])):
        raise ValueError("bridge targets disagree with complete S7 B_q/T_q")
    success = record["status"] == "SUCCESS"
    normalized = normalize_agent_answers(kg, parse_final(record["raw_final_output"], [])["answers"],
                                         reference["Type_T"]) if success else None
    answers = normalized.answers if success else []
    ids = {a.node_id for a in answers if a.node_id is not None}
    labels_a = label_answers(answers, reference, consistent=consistent)
    paths = label_paths(answers, record, reference, mapping, kg)
    if any(a == "OFF_QUESTION" and b["label_b"] == "SUPPORTED"
           for a, b in zip(labels_a, paths["answers"])):
        raise ValueError("OFF_QUESTION/SUPPORTED invariant violated")
    calls = record["call_log"]
    neighbor_calls = [c for c in calls if c["tool"] == "get_neighbors"]
    pages = []
    for i, call in enumerate(calls):
        if not call["success"] or call["tool"] != "get_neighbors":
            continue
        result = call["result"]
        if (any(type(result.get(k)) is not int or result[k] < minimum
                for k, minimum in (("page", 1), ("page_size", 1), ("total_count", 0)))
                or type(result.get("has_more")) is not bool
                or result["page"] != call["arguments"].get("page", 1)
                or len(result["items"]) > result["page_size"]
                or len(result["items"]) > result["total_count"]):
            raise ValueError(f"call_log[{i}]: invalid pagination metadata")
        pages.append((i, call))

    def list_key(call):
        args = call["arguments"]
        return (str(args.get("entity_id")), args.get("relation"), args.get("neighbor_type"))

    requested_page2 = {list_key(c) for c in neighbor_calls if c["arguments"].get("page", 1) == 2}
    first_list, ranks = {}, {}
    explored = sorted({str(c["arguments"]["entity_id"]) for _, c in pages} & bridges, key=int)
    for _, call in pages:
        result = call["result"]
        for position, node in enumerate(result["items"], 1):
            x = str(node["id"])
            first_list.setdefault(x, (result["page"], result["total_count"]))
            if str(call["arguments"]["entity_id"]) == reference["s"] and call["arguments"]["relation"] in mapping["R1"]:
                ranks.setdefault(x, (result["page"] - 1) * result["page_size"] + position)
    early_stop = any(c["result"]["page"] == 1 and c["result"]["has_more"]
                     and any(str(n["id"]) in ids for n in c["result"]["items"])
                     and list_key(c) not in requested_page2 for _, c in pages) if success else None
    appeared = set(appeared_entities(record))
    diagnostics = []
    nodes = {reference["s"], *explored, *ids}
    for i, answer, a, b in zip(normalized.kept_indices if success else [], answers, labels_a, paths["answers"]):
        x = answer.node_id
        path = b["primary_path"]
        if path:
            nodes.update(e[k] for e in path for k in ("u", "v"))
        diagnostics.append({"submitted_index": i, "node_id": x, "label_a": a, **b,
                            "first_seen_page": first_list[x][0] if x in first_list else
                            ("INSPECT" if x in appeared else "NEVER"),
                            "list_size": first_list[x][1] if x in first_list else None,
                            "primary_path_max_list_size": max(
                                (calls[e["creation_index"]]["result"]["total_count"] for e in path),
                                default=None) if path is not None else None,
                            "degree": degrees[x]["degree"] if x is not None else None,
                            "degree_percentile": degrees[x]["degree_percentile"] if x is not None else None})
    total, resolved = (len(answers), len(ids)) if success else (None, None)
    correct = len(ids & set(reference["A_star_q"])) if success else None
    gold = len(reference["A_star_q"])
    a_counts = {label: labels_a.count(label) for label in LABEL_A} if success else None
    b_counts = {label: sum(a["label_b"] == label for a in diagnostics) for label in LABEL_B} if success else None
    denominators = {"question_valid_precision": resolved, "off_question_rate": resolved,
                    "unresolved_rate": total, "ungrounded_rate": resolved,
                    "benchmark_precision": resolved, "benchmark_recall": gold,
                    "benchmark_f1": resolved + gold if success else None}
    numerators = {"question_valid_precision": sum(a_counts[k] for k in LABEL_A[:3]) if success else None,
                  "off_question_rate": a_counts["OFF_QUESTION"] if success else None,
                  "unresolved_rate": a_counts["UNRESOLVED"] if success else None,
                  "ungrounded_rate": b_counts["UNGROUNDED"] if success else None,
                  "benchmark_precision": correct, "benchmark_recall": correct,
                  "benchmark_f1": 2 * correct if success else None}
    ratios = {k: numerators[k] / d if d and numerators[k] is not None else None
              for k, d in denominators.items()}
    rank = {b: ranks.get(b) for b in explored}
    recall = {b: len(ids & targets[b]) / len(targets[b]) if success else None for b in explored}
    charged = sum(c.get("result") != BUDGET_EXHAUSTED for c in calls)
    undefined = {k: int(v is None) for k, v in ratios.items()}
    undefined.update({"bridge_rank": sum(v is None for v in rank.values()),
                      "bridge_conditional_recall": sum(v is None for v in recall.values()),
                      **{k: sum(a[k] is None for a in diagnostics) for k in
                         ("list_size", "primary_path_max_list_size", "degree", "degree_percentile")}})
    return {"query_id": record["query_id"], "agent_id": record["agent_id"],
            "run_id": record["run_id"], "attempt": record["attempt"],
            "construction": reference["construction"], "episode_status": record["status"], "cause": record["cause"],
            "answer_count": total, "resolved_count": resolved, "label_a_counts": a_counts, "label_b_counts": b_counts,
            "primary_reason_counts": {k: sum(k in a["primary_reason_codes"] for a in diagnostics) for k in REASONS} if success else None,
            "reason_counts": {k: sum(k in a["reason_codes"] for a in diagnostics) for k in REASONS} if success else None,
            **ratios, "numerators": numerators, "denominators": denominators, "undefined_counts": undefined,
            "hop1_status": paths["hop1_status"], "found_r1": paths["found_r1"],
            "bridges_explored": explored, "bridge_rank": rank, "bridge_conditional_recall": recall,
            "bridge_recall_counts": {b: {"correct": len(ids & targets[b]) if success else None,
                                          "total": len(targets[b])} for b in explored},
            "early_stop": early_stop, "pages_requested": len(neighbor_calls), "tool_calls_used": charged,
            "budget_exhausted": charged >= record["tool_config"]["budget"],
            "text_tool_call_count": sum(e["event"] == "TEXT_TOOL_CALL" for e in record.get("log_events", [])),
            "answers": diagnostics, "node_statistics": {n: dict(degrees[n]) for n in sorted(nodes, key=int)}}
