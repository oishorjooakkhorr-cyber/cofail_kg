"""S17 evaluator-only answer status, protocol §6/§13; no trace/path labels."""

from cofail_kg.evaluation.normalize import AgentResolution


def label_answers(answers: list[AgentResolution], reference: dict, *, consistent: bool) -> list[str]:
    """First matching §13 rule, in S16 retained-answer order.

    Use the S7 query row unchanged, including G_q and A_star_q. Official evaluation
    calls this only for primary-population queries; consistent is the S8 status.
    False permits synthetic diagnostic coverage of GOLD_BRIDGE_EXTRA, which is
    an error on a CONSISTENT query. No normalization or deduplication occurs here.
    """
    gold, construction, valid = (set(reference[key]) for key in ("A_star_q", "G_q", "T_q"))
    mode = reference["construction"]
    if mode not in ("BRIDGE", "UNION"):
        raise ValueError(f"{reference['query_id']}: invalid construction {mode!r}")
    expected = set(reference["T_q_gold_bridges"]) if mode == "BRIDGE" else valid
    if construction != expected:
        raise ValueError(f"{reference['query_id']}: G_q disagrees with {mode} construction")

    labels = []
    for answer in answers:
        node = answer.node_id
        if node is None:
            label = "UNRESOLVED"
        elif node in gold:
            label = "GOLD"
        elif node in construction:
            if consistent:
                raise ValueError(f"{reference['query_id']}: GOLD_BRIDGE_EXTRA for {node} on CONSISTENT query")
            label = "GOLD_BRIDGE_EXTRA"
        elif node in valid:
            label = "ALT_VALID"
        else:
            label = "OFF_QUESTION"
        labels.append(label)
    return labels
