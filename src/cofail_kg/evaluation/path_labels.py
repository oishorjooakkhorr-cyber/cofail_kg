"""Evaluator-only Label B and path diagnostics, frozen protocol §11/§14."""

from cofail_kg.agents.trace import appeared_entities, build_trace_graph, paths
from cofail_kg.evaluation.normalize import AgentResolution


def _codes(path, target_type, type_b, type_t, r1, r2, node_type):
    """Protocol §14.2 codes for one invalid path; sorted for stable output."""
    length = len(path)
    codes = set()
    if length == 1 and target_type == type_t:
        codes.add("SHORTCUT")
    elif length != 2:
        codes.add("WRONG_HOP_COUNT")
    if length >= 1 and target_type != type_t:
        codes.add("WRONG_TARGET_TYPE")
    if length == 2:
        if path[0].label not in r1:
            codes.add("WRONG_RELATION_HOP1")
        if node_type(path[0].v) != type_b:
            codes.add("WRONG_BRIDGE_TYPE")
        if path[1].label not in r2:
            codes.add("WRONG_RELATION_HOP2")
    return sorted(codes)


def label_paths(answers: list[AgentResolution], record: dict, reference: dict,
                mapping: dict, kg) -> dict:
    """§14 labels in S16 retained-answer order, using raw S12 tool-call evidence.

    Caller supplies the matching S7 row, frozen per-type R1/R2 mapping and KG
    index. Nothing is normalized/deduplicated here. Primary paths are returned
    for reachable grounded answers; reason codes apply only to PATH_INVALID.
    Unresolved/ungrounded/unreachable answers have primary_path=None; the source
    answer's length-zero path is []. No agent-facing code imports this module.
    H1 uses a simple path without a length cap (researcher, 2026-10-17).
    """
    if record["query_id"] != reference["query_id"]:
        raise ValueError("episode and reference query IDs differ")
    if any(not isinstance(mapping[k], (list, tuple)) or not mapping[k]
           or any(not isinstance(r, str) or not r for r in mapping[k]) for k in ("R1", "R2")):
        raise ValueError("mapping requires nonempty frozen R1 and R2 label lists")
    r1, r2 = set(mapping["R1"]), set(mapping["R2"])
    s, type_b, type_t = (reference[k] for k in ("s", "Type_B", "Type_T"))
    graph, appeared = build_trace_graph(record), set(appeared_entities(record))
    types = {}

    def node_type(node):
        if node not in types:
            types[node] = kg.get_node(node)["type"]
        return types[node]

    bridges = {e.v for e in graph.edges if e.u == s and e.label in r1
               and e.v != s and node_type(e.v) == type_b}
    supported = {e.v for e in graph.edges if e.u in bridges and e.label in r2
                 and e.v != s and node_type(e.v) == type_t}
    reverse = {}
    for e in graph.edges:
        reverse.setdefault(e.v, set()).add(e.u)
    source_calls = [e["arguments"]["relation"] in r1 for e in record["call_log"]
                    if e["success"] and e["tool"] == "get_neighbors"
                    and str(e["arguments"]["entity_id"]) == s]
    if not source_calls:
        hop1_status = "H1_NONE"
    elif all(source_calls):
        hop1_status = "H1_CLEAN"
    elif any(source_calls):
        hop1_status = "H1_MIXED"
    else:
        hop1_status = "H1_WRONG"
    results = []
    for answer in answers:
        x = answer.node_id
        primary, primary_codes, union_codes = None, [], []
        if x is None:
            label = "NOT_APPLICABLE"
        elif x not in appeared:
            label = "UNGROUNDED"
        else:
            found = paths(graph, s, x)
            primary = found.primary
            if x in supported:
                label = "SUPPORTED"
            elif primary is None:
                label = "KG_UNSUPPORTED"
            else:
                label = "PATH_INVALID"
                args = (node_type(x), type_b, type_t, r1, r2, node_type)
                primary_codes = _codes(primary, *args)
                union_codes = sorted({code for path in found.simple for code in _codes(path, *args)})
        h1 = 0
        if label in ("SUPPORTED", "PATH_INVALID") and x != s:
            # Excluding s prevents a return through the source; reachability
            # then guarantees a simple suffix from a distinct bridge to x.
            reachable, pending = {x}, [x]
            while pending:
                for node in reverse.get(pending.pop(), ()):
                    if node != s and node not in reachable:
                        reachable.add(node)
                        pending.append(node)
            h1 = int(bool((bridges - {x}) & reachable))
        results.append({"label_b": label, "h1": h1,
                        "primary_path": None if primary is None else [e.to_json() for e in primary],
                        "primary_reason_codes": primary_codes, "reason_codes": union_codes})
    return {"answers": results, "hop1_status": hop1_status,
            "found_r1": hop1_status in ("H1_CLEAN", "H1_MIXED")}
