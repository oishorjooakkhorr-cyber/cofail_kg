"""Evaluator-only co-failure metrics, frozen protocol §16; no model calls, nothing agent-facing imports this.

Inputs are the existing evaluator outputs: one S19 `agent_metrics` row per (query, agent), which already
carry §12 normalization, §13 Label A, §14 Label B, per-answer H1 and §14.2 primary paths, plus the S7
reference row, the frozen per-type R1/R2 mapping, the manifest ambiguity tag and §15 `degree_statistics`.
No label, path or degree is recomputed here.

Conventions (engineering, documented; see docs/S23_cofailure_report.md):
* An agent "has" an entity once, whatever how many retained answers name it (sets; §16.1).
* A non-SUCCESS episode has no resolved answers (S19 rows carry `answers == []`), so it contributes no
  entity, event or node. Its status is never changed and is reported per query in `episodes`.
* Thresholds count distinct agents: "3" means at least 3 of the 4, "4" means all 4 (n = 4, §9.2).
* JSON null means NA (§15 convention); denominators are always reported (§16.4).
* Node IDs are ordered numerically; agents in the frozen agent order.
"""

from __future__ import annotations

from itertools import combinations

N_AGENTS = 4  # protocol §9.2
LABEL_A = ("GOLD", "GOLD_BRIDGE_EXTRA", "ALT_VALID", "OFF_QUESTION", "UNRESOLVED")
LABEL_B = ("SUPPORTED", "PATH_INVALID", "KG_UNSUPPORTED", "UNGROUNDED", "NOT_APPLICABLE")


def _num(node: str) -> int:
    return int(node)


def _validate_panel(reference: dict, rows: list[dict], agent_order: list[str]) -> dict[str, dict]:
    """One row per frozen agent for this query; labels consistent with the S7 reference sets."""
    if len(agent_order) != N_AGENTS or len(set(agent_order)) != N_AGENTS:
        raise ValueError(f"agent_order must list {N_AGENTS} distinct agents (§9.2)")
    q = reference["query_id"]
    by_agent: dict[str, dict] = {}
    for row in rows:
        if row["query_id"] != q:
            raise ValueError(f"{q}: panel row for query {row['query_id']}")
        agent = row["agent_id"]
        if agent not in agent_order:
            raise ValueError(f"{q}: unknown agent {agent!r}")
        if agent in by_agent:
            raise ValueError(f"{q}: duplicate panel row for {agent} (select the latest attempt first, §19)")
        by_agent[agent] = row
    missing = [a for a in agent_order if a not in by_agent]
    if missing:
        raise ValueError(f"{q}: missing panel rows for {missing}")
    s, valid = reference["s"], set(reference["T_q"])
    for agent, row in by_agent.items():
        where = f"{q}/{agent}"
        if row["episode_status"] != "SUCCESS" and row["answers"]:
            raise ValueError(f"{where}: {row['episode_status']} episode has scored answers")
        for a in row["answers"]:
            x, la, lb = a["node_id"], a["label_a"], a["label_b"]
            if la not in LABEL_A or lb not in LABEL_B or a["h1"] not in (0, 1):
                raise ValueError(f"{where}: invalid labels {la!r}/{lb!r}/h1={a['h1']!r}")
            if (x is None) != (la == "UNRESOLVED") or (x is None) != (lb == "NOT_APPLICABLE"):
                raise ValueError(f"{where}: resolution and labels disagree for {x!r}")
            if x is not None and (la == "OFF_QUESTION") == (x in valid):
                raise ValueError(f"{where}: Label A of {x} disagrees with T_q")
            if la == "OFF_QUESTION" and lb == "SUPPORTED":
                raise ValueError(f"{where}: OFF_QUESTION/SUPPORTED invariant violated for {x}")
            if a["h1"] and lb not in ("SUPPORTED", "PATH_INVALID"):
                raise ValueError(f"{where}: h1=1 on {lb} answer {x}")
            path = a["primary_path"]
            if (path is None) == (lb in ("SUPPORTED", "PATH_INVALID")):
                raise ValueError(f"{where}: primary path presence disagrees with {lb} for {x}")
            if path:
                if path[0]["u"] != s or path[-1]["v"] != x or any(
                        e["v"] != f["u"] for e, f in zip(path, path[1:])):
                    raise ValueError(f"{where}: primary path of {x} is not a walk from s to x")
            elif path == [] and x != s:
                raise ValueError(f"{where}: empty primary path for {x} != s")
    return by_agent


def _stats(degrees: dict, node: str) -> dict:
    if node not in degrees:
        raise ValueError(f"no degree statistics for node {node}")
    return {"degree": degrees[node]["degree"], "degree_percentile": degrees[node]["degree_percentile"]}


def _shared(sets: dict[str, set], agent_order: list[str]) -> dict:
    """Entities in >= 3 agents' sets, each with its agents, and the CF3/CF4 flags (§16.1)."""
    holders: dict[str, list[str]] = {}
    for agent in agent_order:
        for x in sets[agent]:
            holders.setdefault(x, []).append(agent)
    shared = {x: agents for x, agents in holders.items() if len(agents) >= 3}
    return {"cf3": int(bool(shared)), "cf4": int(any(len(a) == N_AGENTS for a in shared.values())),
            "shared": shared}


def _answer_sets(by_agent: dict, agent_order: list[str], reference: dict) -> dict[str, dict[str, set]]:
    gold = set(reference["A_star_q"])
    out = {k: {} for k in ("question", "grounded", "hop1_clean", "benchmark")}
    for agent in agent_order:
        answers = [a for a in by_agent[agent]["answers"] if a["node_id"] is not None]
        off = [a for a in answers if a["label_a"] == "OFF_QUESTION"]
        out["question"][agent] = {a["node_id"] for a in off}
        out["grounded"][agent] = {a["node_id"] for a in off if a["label_b"] != "UNGROUNDED"}
        out["hop1_clean"][agent] = {a["node_id"] for a in off if a["h1"] == 1}
        out["benchmark"][agent] = {a["node_id"] for a in answers} - gold
    return out


def _wrong_turns(path: list[dict], shortcut: bool, r1: set, r2: set) -> list[tuple[str, str]]:
    """§16.3 wrong-turn events on one primary path: step 1 ∉ R1, step 2 ∉ R2, or a SHORTCUT's single step.

    A SHORTCUT step whose label is also outside R1 is the same step, so it is one event.
    """
    events = []
    if path and (path[0]["label"] not in r1 or shortcut):
        events.append((path[0]["u"], path[0]["label"]))
    if len(path) >= 2 and path[1]["label"] not in r2:
        events.append((path[1]["u"], path[1]["label"]))
    return events


def _answer_evidence(a: dict) -> dict:
    return {"answer_id": a["node_id"], "label_b": a["label_b"], "h1": a["h1"],
            "primary_path": a["primary_path"], "primary_reason_codes": a["primary_reason_codes"],
            "primary_path_max_list_size": a["primary_path_max_list_size"], "list_size": a["list_size"]}


def query_cofailure(reference: dict, mapping: dict, ambiguity_tag: str, rows: list[dict],
                    degrees: dict, agent_order: list[str]) -> dict:
    """All §16.1–§16.3 per-query metrics with inspectable evidence for every positive case.

    `rows` are the S19 `agent_metrics` rows (latest attempt) of this query for every frozen agent;
    `mapping` is the query relation type's frozen {"R1", "R2"}; `degrees` is §15 `degree_statistics`.
    Inputs are not modified.
    """
    by_agent = _validate_panel(reference, rows, agent_order)
    order = {a: i for i, a in enumerate(agent_order)}
    r1, r2 = set(mapping["R1"]), set(mapping["R2"])
    s, excluded = reference["s"], set(reference["B_q"]) | set(reference["T_q"])
    sets = _answer_sets(by_agent, agent_order, reference)

    def entity_block(variant):
        result = _shared(sets[variant], agent_order)
        entities = []
        for x in sorted(result["shared"], key=_num):
            per_agent = {}
            for agent in result["shared"][x]:
                a = next(a for a in by_agent[agent]["answers"] if a["node_id"] == x)
                per_agent[agent] = {"label_a": a["label_a"], **_answer_evidence(a)}
            entities.append({"entity_id": x, "agents": result["shared"][x],
                             "agent_count": len(result["shared"][x]), **_stats(degrees, x),
                             "per_agent": per_agent})
        return {"cf3": result["cf3"], "cf4": result["cf4"], "shared_entities": entities}

    # §16.3: primary paths of OFF_QUESTION answers only.
    events: dict[tuple[str, str], dict[str, list]] = {}
    nodes: dict[str, dict[str, list]] = {}
    shortcuts: dict[str, dict[str, list]] = {}
    for agent in agent_order:
        for a in by_agent[agent]["answers"]:
            if a["label_a"] != "OFF_QUESTION" or not a["primary_path"]:
                continue
            path, x = a["primary_path"], a["node_id"]
            shortcut = "SHORTCUT" in a["primary_reason_codes"]
            for event in _wrong_turns(path, shortcut, r1, r2):
                events.setdefault(event, {}).setdefault(agent, []).append(_answer_evidence(a))
            for e in path[:-1]:
                v = e["v"]
                if v not in (s, x) and v not in excluded:
                    nodes.setdefault(v, {}).setdefault(agent, []).append(_answer_evidence(a))
            if shortcut:
                shortcuts.setdefault(path[0]["label"], {}).setdefault(agent, []).append(_answer_evidence(a))

    def cases(found, key, describe):
        out = []
        for k in sorted(found, key=key):
            agents = sorted(found[k], key=order.__getitem__)
            if len(agents) >= 3:
                evidence = {ag: sorted(found[k][ag], key=lambda e: _num(e["answer_id"])) for ag in agents}
                out.append({**describe(k), "agents": agents, "agent_count": len(agents), "per_agent": evidence})
        return out

    rel = cases(events, lambda k: (_num(k[0]), k[1]),
                lambda k: {"node_id": k[0], "relation": k[1], **_stats(degrees, k[0])})
    node = cases(nodes, _num, lambda k: {"node_id": k, **_stats(degrees, k)})
    short = cases(shortcuts, lambda k: k, lambda k: {"node_id": s, "relation": k, **_stats(degrees, s)})
    return {
        "query_id": reference["query_id"], "relation_type": reference["relation_type"],
        "ambiguity_tag": ambiguity_tag, "s": s, "R1": sorted(r1), "R2": sorted(r2),
        "episodes": {a: {"run_id": by_agent[a]["run_id"], "attempt": by_agent[a]["attempt"],
                         "episode_status": by_agent[a]["episode_status"], "cause": by_agent[a]["cause"]}
                     for a in agent_order},
        "technical_failure_agents": [a for a in agent_order if by_agent[a]["episode_status"] != "SUCCESS"],
        "W_Q": {a: sorted(sets["question"][a], key=_num) for a in agent_order},
        "W_BH": {a: sorted(sets["benchmark"][a], key=_num) for a in agent_order},
        "question": entity_block("question"),
        "grounded": entity_block("grounded"),
        "hop1_clean": entity_block("hop1_clean"),
        "benchmark": entity_block("benchmark"),
        "pcf_rel3": int(bool(rel)), "pcf_rel4": int(any(c["agent_count"] == N_AGENTS for c in rel)),
        "pcf_node3": int(bool(node)), "pcf_node4": int(any(c["agent_count"] == N_AGENTS for c in node)),
        "pcf_shortcut3": int(bool(short)),
        "pcf_rel_cases": rel, "pcf_node_cases": node, "pcf_shortcut_cases": short,
    }


def pairwise_agreement(results: list[dict], agent_order: list[str]) -> list[dict]:
    """§16.4 per unordered pair over the question-level W sets of `query_cofailure` results.

    Denominator: queries where both W_iq and W_jq are non-empty; numerator: those where they intersect.
    Kim et al. (2025) "agreement when both are wrong", adapted to answer sets (protocol §16.4).
    """
    ids = [r["query_id"] for r in results]
    if len(ids) != len(set(ids)):
        raise ValueError("duplicate query in pairwise agreement input")
    out = []
    for i, j in combinations(agent_order, 2):
        both, agree = [], []
        for r in sorted(results, key=lambda r: r["query_id"]):
            wi, wj = set(r["W_Q"][i]), set(r["W_Q"][j])
            if wi and wj:
                both.append(r["query_id"])
                if wi & wj:
                    agree.append(r["query_id"])
        out.append({"agent_i": i, "agent_j": j, "numerator": len(agree), "denominator": len(both),
                    "agreement": len(agree) / len(both) if both else None,
                    "queries_both_wrong": both, "queries_intersecting": agree})
    return out
