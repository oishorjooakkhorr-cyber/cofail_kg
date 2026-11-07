"""Evaluator-only chance baselines, frozen protocol §17; no model calls, nothing agent-facing imports this.

Three nulls, each with its own pool, observed set and observed total (protocol §17 table):

* **N1** (uniform): pool `C_iq` = entities that appeared in agent i's tool outputs (§11), with type
  Type_T, not in `T_q`, not `s`. Observed set `W'_iq` = members of `W_iq` (§16.1: resolved answers with
  Label A `OFF_QUESTION`) that appeared and have type Type_T.
* **N1-H1** (hop-1-clean): pool and observed set restricted to entities with `H1(x, i) = 1` (§14.3).
* **N2** (ordering): pool and observed set restricted to entities that appeared on page 1 of any
  successful `get_neighbors` list the agent opened.

Procedure (§17): per query and per null, one `Generator(PCG64(SeedSequence([42, h, v])))` with
`h` = first 8 hex digits of SHA256(query_id) as an integer and `v` = 1, 2, 3 for N1, N1-H1, N2. In
each of 10,000 trials every agent, in ascending (frozen) agent order, draws without replacement
`|observed set|` entities from its pool sorted by numeric ID with `Generator.choice`. A query counts
for the 3-agent version when some drawn entity is shared by at least 3 agents, and for the 4-agent
version when shared by all 4 (n = 4, §9.2). Trial totals sum over queries;
`p = (1 + #{trials with null total >= observed total}) / (1 + trials)`.

Engineering conventions (documented, tested; listed in the S24 report):
* Inputs are the S12 episode record (raw `call_log`) and the S19 `agent_metrics` row per (query,
  agent), plus the S7 reference row, the frozen per-type R1/R2 mapping and a node-type lookup.
* `H1(x, i)` for pool entities uses the §14.3 definition with the same reachability rule as
  `path_labels.label_paths` (simple path, no length cap; a return through `s` is excluded). For every
  observed entity it is cross-checked against the S19 row's stored `h1`.
* An agent whose observed set is empty draws nothing (no `choice` call, so no random numbers used).
* A non-SUCCESS episode has no resolved answers, so its observed sets are empty. Queries with such an
  episode are kept in every total and also reported separately (researcher decision 2026-11-07, §16
  convention), via `technical_failure_agents` and an aggregate that excludes them.
* The 95th percentile is `numpy.percentile(totals, 95)` (NumPy's default linear interpolation).
* Node IDs are ordered numerically; output queries are sorted by query_id.
"""

from __future__ import annotations

import hashlib

import numpy as np

from cofail_kg.agents.trace import appeared_entities, build_trace_graph

N_AGENTS = 4  # protocol §9.2
TRIALS = 10_000  # protocol §17
BASE_SEED = 42  # protocol §17
NULLS = ("N1", "N1-H1", "N2")
NULL_STREAM = {"N1": 1, "N1-H1": 2, "N2": 3}  # protocol §17: v
VERSIONS = ("cf3", "cf4")


def _num(node: str) -> int:
    return int(node)


def query_hash(query_id: str) -> int:
    """§17 `h`: the first 8 hex digits of SHA256(query_id) read as an integer."""
    return int(hashlib.sha256(query_id.encode("utf-8")).hexdigest()[:8], 16)


def generator(query_id: str, null: str) -> np.random.Generator:
    """§17 random numbers: Generator(PCG64) from SeedSequence([42, h, v])."""
    seq = np.random.SeedSequence([BASE_SEED, query_hash(query_id), NULL_STREAM[null]])
    return np.random.Generator(np.random.PCG64(seq))


def _page_one(record: dict) -> set[str]:
    """Entities listed on page 1 of any successful get_neighbors call (N2 restriction)."""
    seen = set()
    for index, entry in enumerate(record["call_log"]):
        if entry.get("tool") != "get_neighbors" or not entry.get("success"):
            continue
        result = entry["result"]
        if result.get("page") != 1:
            continue
        for position, item in enumerate(result.get("items", [])):
            node = item.get("id") if isinstance(item, dict) else None
            if type(node) is int:
                node = str(node)
            if not isinstance(node, str):
                raise ValueError(f"call_log[{index}].result.items[{position}]: missing entity ID")
            seen.add(node)
    return seen


def _h1_function(record: dict, reference: dict, mapping: dict, node_type):
    """H1(x, i) of §14.3 for any appeared entity x, matching path_labels.label_paths."""
    r1 = set(mapping["R1"])
    s, type_b = reference["s"], reference["Type_B"]
    graph = build_trace_graph(record)
    bridges = {e.v for e in graph.edges if e.u == s and e.label in r1 and e.v != s
               and node_type(e.v) == type_b}
    reverse: dict[str, set[str]] = {}
    for e in graph.edges:
        reverse.setdefault(e.v, set()).add(e.u)

    def h1(x: str) -> int:
        if x == s:
            return 0
        reachable, pending = {x}, [x]
        while pending:
            for node in reverse.get(pending.pop(), ()):
                if node != s and node not in reachable:
                    reachable.add(node)
                    pending.append(node)
        return int(bool((bridges - {x}) & reachable))

    return h1


def agent_pools(record: dict, row: dict, reference: dict, mapping: dict, node_type) -> dict:
    """§17 pool and observed set of one agent on one query, for N1, N1-H1 and N2.

    Returns {null: {"pool": [...], "observed": [...]}} with numerically sorted ID lists, and asserts
    that every observed set is a subset of its pool (§17).
    """
    q, agent = reference["query_id"], row["agent_id"]
    if record["query_id"] != q or row["query_id"] != q:
        raise ValueError(f"{q}/{agent}: record, metrics row and reference query IDs differ")
    if record["agent_id"] != agent:
        raise ValueError(f"{q}: record agent {record['agent_id']} != metrics row agent {agent}")
    s, type_t, valid = reference["s"], reference["Type_T"], set(reference["T_q"])
    appeared = set(appeared_entities(record))
    h1 = _h1_function(record, reference, mapping, node_type)
    page_one = _page_one(record)

    pool = {x for x in appeared if x != s and x not in valid and node_type(x) == type_t}
    wrong = {a["node_id"] for a in row["answers"] if a["label_a"] == "OFF_QUESTION"}
    if None in wrong:
        raise ValueError(f"{q}/{agent}: OFF_QUESTION answer without a node ID")
    if wrong & valid:
        raise ValueError(f"{q}/{agent}: OFF_QUESTION answer inside T_q")
    observed = {x for x in wrong if x in appeared and node_type(x) == type_t}
    stored = {}
    for a in row["answers"]:
        if a["node_id"] in observed:
            stored.setdefault(a["node_id"], set()).add(a["h1"])
    for x in sorted(observed, key=_num):
        if stored[x] != {h1(x)}:
            raise ValueError(f"{q}/{agent}: H1 of {x} recomputed {h1(x)} != S19 row {sorted(stored[x])}")

    pool_h1 = {x for x in pool if h1(x) == 1}
    sets = {"N1": (pool, observed),
            "N1-H1": (pool_h1, {x for x in observed if h1(x) == 1}),
            "N2": (pool & page_one, observed & page_one)}
    out = {}
    for null, (p, o) in sets.items():
        if not o <= p:
            raise ValueError(f"{q}/{agent} {null}: observed set is not a subset of the pool: "
                             f"{sorted(o - p, key=_num)}")
        out[null] = {"pool": sorted(p, key=_num), "observed": sorted(o, key=_num)}
    return out


def _shared(sets: list) -> tuple[bool, bool]:
    """(some entity in >= 3 agents' sets, some entity in all 4)."""
    counts: dict = {}
    for entities in sets:
        for x in set(entities):
            counts[x] = counts.get(x, 0) + 1
    top = max(counts.values(), default=0)
    return top >= 3, top >= N_AGENTS


def simulate(query_id: str, null: str, pools: list[dict], trials: int = TRIALS) -> np.ndarray:
    """Trial indicators, shape (trials, 2): column 0 = 3-agent share, column 1 = 4-agent share.

    `pools` lists, in ascending agent order, {"pool": [...], "observed": [...]} for each agent.
    """
    rng = generator(query_id, null)
    arrays = [(np.array([_num(x) for x in p["pool"]], dtype=np.int64), len(p["observed"])) for p in pools]
    if any(k > len(arr) for arr, k in arrays):
        raise ValueError(f"{query_id} {null}: observed set larger than pool")
    out = np.zeros((trials, 2), dtype=bool)
    if sum(1 for _, k in arrays if k) < 3:  # fewer than 3 agents draw: no share possible; no RNG used
        return out
    for t in range(trials):
        draws = [rng.choice(arr, size=k, replace=False) if k else () for arr, k in arrays]
        out[t] = _shared([d.tolist() if len(d) else [] for d in draws])
    return out


def query_nulls(reference: dict, panel: list[dict], agent_order: list[str], trials: int = TRIALS) -> dict:
    """Per-query §17 result. `panel` holds one {"record", "row", "pools"} entry per agent."""
    if len(agent_order) != N_AGENTS or len(set(agent_order)) != N_AGENTS:
        raise ValueError(f"agent_order must list {N_AGENTS} distinct agents (§9.2)")
    q = reference["query_id"]
    by_agent = {entry["row"]["agent_id"]: entry for entry in panel}
    if sorted(by_agent) != sorted(agent_order) or len(panel) != N_AGENTS:
        raise ValueError(f"{q}: panel agents {sorted(by_agent)} != frozen agent order")
    result = {"query_id": q, "relation_type": reference["relation_type"],
              "technical_failure_agents": [a for a in agent_order
                                           if by_agent[a]["row"]["episode_status"] != "SUCCESS"],
              "nulls": {}}
    indicators = {}
    for null in NULLS:
        pools = [by_agent[a]["pools"][null] for a in agent_order]
        observed = _shared([p["observed"] for p in pools])
        sim = simulate(q, null, pools, trials)
        indicators[null] = sim
        result["nulls"][null] = {
            "pool_sizes": {a: len(by_agent[a]["pools"][null]["pool"]) for a in agent_order},
            "observed_sets": {a: by_agent[a]["pools"][null]["observed"] for a in agent_order},
            "observed_cf3": int(observed[0]), "observed_cf4": int(observed[1]),
            "null_probability_cf3": float(sim[:, 0].mean()), "null_probability_cf4": float(sim[:, 1].mean())}
    return {"result": result, "indicators": indicators}


def _summary(observed: int, totals: np.ndarray) -> dict:
    trials = len(totals)
    p95 = float(np.percentile(totals, 95))
    return {"observed_total": observed, "null_mean": float(totals.mean()),
            "null_median": float(np.median(totals)), "null_p95": p95,
            "p": (1 + int((totals >= observed).sum())) / (1 + trials),
            "observed_exceeds_null": observed > p95, "query_count": None}


def aggregate(per_query: list[dict], trials: int = TRIALS, include=None) -> dict:
    """§17 aggregate per null and version over the queries `include` accepts (default: all)."""
    chosen = [r for r in sorted(per_query, key=lambda r: r["result"]["query_id"])
              if include is None or include(r["result"])]
    out = {}
    for null in NULLS:
        out[null] = {}
        for column, version in enumerate(VERSIONS):
            observed = sum(r["result"]["nulls"][null][f"observed_{version}"] for r in chosen)
            totals = np.zeros(trials, dtype=np.int64)
            for r in chosen:
                totals += r["indicators"][null][:, column]
            summary = _summary(observed, totals)
            summary["query_count"] = len(chosen)
            out[null][version] = summary
    return out


def run_nulls(references: dict, panels: dict, agent_order: list[str], trials: int = TRIALS) -> dict:
    """All queries: per-query results (sorted by query_id) and aggregates.

    `panels` maps query_id -> list of {"record", "row", "pools"} (one per agent). The gate comparison
    (D6, D7) is O_H1 against N1-H1 (§17); this function reports, it does not apply gates.
    """
    per_query = [query_nulls(references[q], panels[q], agent_order, trials) for q in sorted(panels)]
    return {"agent_order": list(agent_order), "trials": trials,
            "aggregate": aggregate(per_query, trials),
            "aggregate_excluding_technical_failures":
                aggregate(per_query, trials, include=lambda r: not r["technical_failure_agents"]),
            "queries": [r["result"] for r in per_query]}
