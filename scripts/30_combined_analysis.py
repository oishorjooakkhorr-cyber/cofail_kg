"""S30 combined analysis: pilot + expansion queries as one query set (decision_rules.md D7).

Usage (from the repository root):
    python scripts/30_combined_analysis.py --component pilot_v1:pilot --component expansion_v1:expansion \
        --out-id pilot_expansion_v1

D7 uses "the same quantities as D6 over pilot + expansion queries". Every per-query quantity was already
computed by `scripts/25_run_panel.py analyze` for each run; this script does not change any of them.
It:
1. loads each component run's stored analysis (cofailure.json, nulls.json, per-episode §15 metrics,
   latest attempt per (query, agent), protocol §19) and its episode records;
2. recomputes every per-query §16 co-failure result (`query_cofailure`) and every per-query §17 null
   result (`query_nulls`, seeded per query ID, so independent of which run a query belongs to) and
   stops unless each equals the stored value exactly; it also stops unless each component's three
   stored §17 aggregates are reproduced exactly;
3. writes results/combined/<out_id>/: cofailure.json (per-query results concatenated, totals as sums,
   §16.4 pairwise agreement over the combined query set) and nulls.json (§17 aggregates over the
   combined query set: all queries, without SOURCE_NAME_OVERLAP (§19.1), without queries that have a
   technical failure), plus components.json naming the inputs and their file hashes.

Outputs are write-once (identical re-runs allowed, any difference stops). No gate outcome is derived.

Engineering conventions (documented, not protocol):
* A query may belong to only one component; a query in two components is an error.
* The SOURCE_NAME_OVERLAP list is the union of the components' stored lists.
* Agent order must be identical in every component.
"""
from __future__ import annotations

import argparse
import importlib.util
import json
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]


def load_script(name, filename):
    spec = importlib.util.spec_from_file_location(name, ROOT / "scripts" / filename)
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


def _roundtrip(value):
    """JSON normal form (tuples → lists, numpy scalars rejected) for exact comparison with stored files."""
    return json.loads(json.dumps(value, sort_keys=True, allow_nan=False))


def parse_component(text: str) -> tuple[str, str]:
    run_id, sep, manifest = text.partition(":")
    if not sep or not run_id or not manifest:
        raise ValueError(f"--component must be RUN_ID:MANIFEST, got {text!r}")
    return run_id, manifest


def totals(results: list[dict]) -> dict:
    """Same totals as scripts/25_run_panel.py analyze (sums of per-query flags)."""
    keys = ("question", "grounded", "hop1_clean", "benchmark")
    t = {f"{k}_{n}": sum(r[k][n] for r in results) for k in keys for n in ("cf3", "cf4")}
    t.update({k: sum(r[k] for r in results) for k in
              ("pcf_rel3", "pcf_rel4", "pcf_node3", "pcf_node4", "pcf_shortcut3")})
    return t


def combine_cofailure(components: list[dict], agents: list[str], pairwise_agreement) -> dict:
    """Concatenate stored per-query §16 results; recompute totals and §16.4 pairwise agreement."""
    seen: dict[str, str] = {}
    queries, overlap = [], set()
    for comp in components:
        cof = comp["cofailure"]
        if cof["agent_order"] != agents:
            raise ValueError(f"{comp['run_id']}: agent order {cof['agent_order']} != {agents}")
        for q in cof["queries"]:
            if q["query_id"] in seen:
                raise ValueError(f"{q['query_id']} is in both {seen[q['query_id']]} and {comp['run_id']}")
            seen[q["query_id"]] = comp["run_id"]
            queries.append(q)
        overlap |= set(cof["source_name_overlap_queries"])
    queries.sort(key=lambda q: q["query_id"])
    no_overlap = [q for q in queries if q["query_id"] not in overlap]
    return {"run_id": "+".join(c["run_id"] for c in components), "agent_order": agents,
            "source_name_overlap_queries": sorted(overlap),
            "totals_all_queries": totals(queries), "totals_without_source_name_overlap": totals(no_overlap),
            "pairwise_all_queries": pairwise_agreement(queries, agents),
            "pairwise_without_source_name_overlap": pairwise_agreement(no_overlap, agents),
            "queries": queries}


def combine_nulls(per_query: list[dict], overlap: set[str], agents: list[str], run_id: str, aggregate) -> dict:
    """§17 aggregates over the combined query set, from recomputed per-query results with indicators."""
    per_query = sorted(per_query, key=lambda r: r["result"]["query_id"])
    return {"run_id": run_id, "agent_order": agents, "trials": len(per_query[0]["indicators"]["N1"]),
            "aggregate_all_queries": aggregate(per_query),
            "aggregate_without_source_name_overlap": aggregate(
                per_query, include=lambda r: r["query_id"] not in overlap),
            "aggregate_excluding_technical_failures": aggregate(
                per_query, include=lambda r: not r["technical_failure_agents"]),
            "queries": [r["result"] for r in per_query]}


def check_component_nulls(comp: dict, per_query: list[dict], aggregate) -> None:
    """Stored per-query results and all three stored aggregates must be reproduced exactly."""
    stored = comp["nulls"]
    overlap = set(comp["cofailure"]["source_name_overlap_queries"])
    recomputed = combine_nulls(per_query, overlap, stored["agent_order"], stored["run_id"], aggregate)
    for key in ("trials", "aggregate_all_queries", "aggregate_without_source_name_overlap",
                "aggregate_excluding_technical_failures", "queries"):
        if _roundtrip(recomputed[key]) != stored[key]:
            raise ValueError(f"{comp['run_id']}: recomputed nulls.json[{key!r}] differs from the stored file")


def main(argv=None):
    parser = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    parser.add_argument("--component", action="append", required=True, help="RUN_ID:MANIFEST (repeatable)")
    parser.add_argument("--out-id", required=True)
    args = parser.parse_args(argv)

    from cofail_kg.agents.trace import load_episode_record, verify_reconstruction
    from cofail_kg.evaluation.cofailure import pairwise_agreement, query_cofailure
    from cofail_kg.evaluation.null_models import aggregate, agent_pools, query_nulls
    from cofail_kg.kg.prepare import file_hash

    report = load_script("s28_report", "28_pilot_report.py")
    launcher = load_script("screening_launcher", "20_screen_models.py")
    refs, _targets, mapping, _status, kg, degrees = launcher.load_evaluator()
    types: dict[str, str] = {}

    def node_type(x):
        if x not in types:
            types[x] = kg.get_node(x)["type"]
        return types[x]

    components, combined_nulls, inputs = [], [], {}
    agents = None
    for run_id, manifest in map(parse_component, args.component):
        data = report.load_run(run_id, manifest)  # stored analysis, latest-attempt rows and records
        agents = agents or data["agents"]
        if data["agents"] != agents:
            raise ValueError(f"{run_id}: agent order {data['agents']} != {agents}")
        entries = {r["query_id"]: r for r in data["manifest_rows"]}
        stored_cof = {q["query_id"]: q for q in data["cofailure"]["queries"]}
        per_query = []
        for q in sorted(entries):
            ref = refs[q]
            qrows = [data["rows"][(a, q)] for a in agents]
            records = []
            for a in agents:
                path = ROOT / "results/runs" / run_id / f"{q}__{a}__a{data['rows'][(a, q)]['attempt']}.json"
                record = load_episode_record(path)
                verify_reconstruction(record)
                records.append(record)
            cof = query_cofailure(ref, mapping[ref["relation_type"]], entries[q]["ambiguity_tag"], qrows,
                                  degrees, agents)
            if _roundtrip(cof) != stored_cof[q]:
                raise ValueError(f"{run_id}/{q}: recomputed co-failure differs from stored cofailure.json")
            per_query.append(query_nulls(ref, [
                {"record": rec, "row": row,
                 "pools": agent_pools(rec, row, ref, mapping[ref["relation_type"]], node_type)}
                for rec, row in zip(records, qrows)], agents))
        check_component_nulls(data, per_query, aggregate)
        components.append({"run_id": run_id, "cofailure": data["cofailure"], "nulls": data["nulls"]})
        combined_nulls += per_query
        analysis = ROOT / "results/runs" / run_id / "analysis"
        inputs[run_id] = {"manifest": manifest, "queries": len(entries),
                          "cofailure.json": file_hash(analysis / "cofailure.json"),
                          "nulls.json": file_hash(analysis / "nulls.json")}
        print(f"{run_id}: {len(entries)} queries; stored co-failure and null results reproduced exactly",
              flush=True)

    cof = combine_cofailure(components, agents, pairwise_agreement)
    nulls = combine_nulls(combined_nulls, set(cof["source_name_overlap_queries"]), agents, cof["run_id"],
                          aggregate)
    out = ROOT / "results/combined" / args.out_id
    launcher.pin_manifest(out / "components.json", {"out_id": args.out_id, "components": inputs,
                                                     "agent_order": agents})
    launcher.pin_manifest(out / "cofailure.json", cof)
    launcher.pin_manifest(out / "nulls.json", nulls)
    print("CO-FAILURE TOTALS (all queries):", json.dumps(cof["totals_all_queries"], sort_keys=True), flush=True)
    for null, versions in nulls["aggregate_all_queries"].items():
        for version, s in versions.items():
            print(f"NULL {null} {version}: observed {s['observed_total']}, mean {s['null_mean']:.4f}, "
                  f"p95 {s['null_p95']}, p {s['p']:.4f}, queries {s['query_count']}", flush=True)
    print(f"wrote {out.relative_to(ROOT)}", flush=True)


if __name__ == "__main__":
    main()
