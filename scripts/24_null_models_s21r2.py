"""S24 offline example: protocol §17 chance baselines on the accepted S22 run smoke_single_s21r2.

Engineering example on the 20 screening queries, not pilot data. No inference. Reads the S12 episode
records (results/runs/smoke_single_s21r2), the pinned S19 metrics rows
(results/diagnostics/smoke_single_s21r2/<agent>/metrics), the S7 reference rows and the PrimeKG cache
(node types); writes only results/diagnostics/s24/smoke_single_s21r2_nulls.json (write-once).
"""
import importlib.util
import json
from pathlib import Path

import yaml

from cofail_kg.evaluation.null_models import TRIALS, agent_pools, run_nulls

ROOT = Path(__file__).resolve().parents[1]
RUN_ID = "smoke_single_s21r2"
RUNS = ROOT / "results/runs" / RUN_ID
METRICS = ROOT / "results/diagnostics" / RUN_ID
OUT = ROOT / "results/diagnostics/s24" / f"{RUN_ID}_nulls.json"


def load_launcher():
    spec = importlib.util.spec_from_file_location("screening_launcher", ROOT / "scripts/20_screen_models.py")
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


def main():
    launcher = load_launcher()
    agents = yaml.safe_load((ROOT / "configs/pilot.yaml").read_text(encoding="utf-8"))["runtime"]["agent_order"]
    manifest = [json.loads(line) for line in
                (ROOT / "data/processed/manifests/screening.jsonl").read_text(encoding="utf-8").splitlines()]
    refs, _, mapping, _, kg, _ = launcher.load_evaluator()
    types = {}

    def node_type(x):
        if x not in types:
            types[x] = kg.get_node(x)["type"]
        return types[x]

    panels, references = {}, {}
    for entry in manifest:
        q = entry["query_id"]
        ref = refs[q]
        references[q] = ref
        panel = []
        for a in agents:
            record = json.loads((RUNS / f"{q}__{a}__a1.json").read_text(encoding="utf-8"))
            row = json.loads((METRICS / a / "metrics" / f"{q}.json").read_text(encoding="utf-8"))
            panel.append({"record": record, "row": row,
                          "pools": agent_pools(record, row, ref, mapping[ref["relation_type"]], node_type)})
        panels[q] = panel
    payload = run_nulls(references, panels, agents, TRIALS)
    payload = {"run_id": RUN_ID, "note": "S24 implementation example on screening queries; not pilot data",
               **payload}
    OUT.parent.mkdir(parents=True, exist_ok=True)
    launcher.pin_manifest(OUT, payload)
    for label, agg in (("all queries", payload["aggregate"]),
                       ("excluding technical failures", payload["aggregate_excluding_technical_failures"])):
        print(f"== {label}")
        for null, versions in agg.items():
            for version, s in versions.items():
                print(f"{null:6} {version} n={s['query_count']} observed={s['observed_total']} "
                      f"mean={s['null_mean']:.4f} median={s['null_median']} p95={s['null_p95']} "
                      f"p={s['p']:.4f} exceeds={s['observed_exceeds_null']}")
    print("== per query (pool sizes N1 / N1-H1 / N2; observed CF3 per null)")
    for r in payload["queries"]:
        n = r["nulls"]
        sizes = " | ".join("/".join(str(n[v]["pool_sizes"][a]) for v in ("N1", "N1-H1", "N2")) for a in agents)
        obs = {v: n[v]["observed_cf3"] for v in n}
        print(r["query_id"], sizes, obs, {v: round(n[v]["null_probability_cf3"], 4) for v in n},
              "failed:", r["technical_failure_agents"])


if __name__ == "__main__":
    main()
