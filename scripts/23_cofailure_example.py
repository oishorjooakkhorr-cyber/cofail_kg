"""S23 offline implementation example: protocol §16 co-failure metrics on the saved S22 smoke_single_v135 metrics.

Engineering exercise only. It is NOT panel acceptance and carries no scientific weight: S22 is unaccepted
(§9.1 re-selection pending), and these are screening queries, not the pilot. No inference. Reads the
pinned S19 metrics rows (results/diagnostics/smoke_single_v135/<agent>/metrics), the S7 reference rows,
the frozen mapping, the screening manifest's ambiguity tags and §15 degree_statistics; writes only
results/diagnostics/s23/smoke_single_v135_cofailure.json (write-once).
"""
import importlib.util
import json
from pathlib import Path

import yaml

from cofail_kg.evaluation.cofailure import pairwise_agreement, query_cofailure

ROOT = Path(__file__).resolve().parents[1]
METRICS = ROOT / "results/diagnostics/smoke_single_v135"
OUT = ROOT / "results/diagnostics/s23/smoke_single_v135_cofailure.json"


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
    refs, _, mapping, _, _, degrees = launcher.load_evaluator()
    results = []
    for entry in manifest:
        q = entry["query_id"]
        rows = [json.loads((METRICS / a / "metrics" / f"{q}.json").read_text(encoding="utf-8")) for a in agents]
        ref = refs[q]
        if ref["relation_type"] != entry["relation_type"]:
            raise ValueError(f"{q}: manifest and reference relation types differ")
        results.append(query_cofailure(ref, mapping[ref["relation_type"]], entry["ambiguity_tag"], rows,
                                       degrees, agents))
    keys = ("question", "grounded", "hop1_clean", "benchmark")
    totals = {f"{k}_{n}": sum(r[k][n] for r in results) for k in keys for n in ("cf3", "cf4")}
    totals.update({k: sum(r[k] for r in results) for k in
                   ("pcf_rel3", "pcf_rel4", "pcf_node3", "pcf_node4", "pcf_shortcut3")})
    payload = {"run_id": "smoke_single_v135", "note": "S23 implementation example; not accepted, not pilot data",
               "agent_order": agents, "query_count": len(results), "totals": totals,
               "pairwise": pairwise_agreement(results, agents), "queries": results}
    launcher.pin_manifest(OUT, payload)
    print(json.dumps({"totals": totals}, indent=1))
    for r in results:
        flags = {k: r[k]["cf3"] for k in keys} | {k: r[k] for k in ("pcf_rel3", "pcf_node3", "pcf_shortcut3")}
        if any(flags.values()):
            print(r["query_id"], r["relation_type"], r["ambiguity_tag"], flags,
                  "failures:", r["technical_failure_agents"])
    for p in payload["pairwise"]:
        print(p["agent_i"], p["agent_j"], f"{p['numerator']}/{p['denominator']}", p["agreement"])


if __name__ == "__main__":
    main()
