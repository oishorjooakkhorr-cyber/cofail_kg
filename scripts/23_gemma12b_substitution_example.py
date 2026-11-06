"""EXPLORATORY S23 comparison: §16 co-failure with Gemma4-12B substituted for Qwen35-9B. Not a panel change.

Researcher request (2026-11-06): exploratory S23 with gemma4:12b, keeping Gemma4-E4B (replaces the 9B Qwen slot). Offline only; no inference.
Panels compared on the 20 screening queries:
  frozen:  Ministral3-8B, Gemma4-E4B, Granite41-8B (S22 smoke_single_v135) + Qwen35-9B (S22 smoke_single_v135)
  gemma12b: the same three S22 rows + Gemma4-12B (S20 block gemma4-12b-5060ti-32k-20261106)
Gemma4-12B's episodes come from a separate S20 screening run (same queries, P1, tools, evaluator, 32K f16
runtime as the three 32K agents), not from S22. Both runs' records are hash-checked against their
pinned final-run-hashes.json before use. Writes only results/diagnostics/s23/gemma12b_substitution_example.json.
"""
import importlib.util
import json
from pathlib import Path

import yaml

from cofail_kg.evaluation.cofailure import pairwise_agreement, query_cofailure
from cofail_kg.kg.prepare import file_hash

ROOT = Path(__file__).resolve().parents[1]
S22 = ROOT / "results/diagnostics/smoke_single_v135"
GEMMA12B = ROOT / "results/diagnostics/s20/gemma4-12b-5060ti-32k-20261106"
OUT = ROOT / "results/diagnostics/s23/gemma12b_substitution_example.json"
KEYS = ("question", "grounded", "hop1_clean", "benchmark")
PCF = ("pcf_rel3", "pcf_rel4", "pcf_node3", "pcf_node4", "pcf_shortcut3")


def load_launcher():
    spec = importlib.util.spec_from_file_location("screening_launcher", ROOT / "scripts/20_screen_models.py")
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


def check_hashes(folder):
    hashes = json.loads((folder / "final-run-hashes.json").read_text(encoding="utf-8"))
    # Every pinned file must match; the S20 pin also covers the run's config snapshot, S22's does not.
    bad = sorted(p for p, h in hashes.items() if file_hash(ROOT / p) != h)
    episodes = [p for p in hashes if p.endswith("__a1.json")]
    if len(episodes) != 20 or bad:
        raise ValueError(f"{folder}: {len(episodes)} pinned episode records, mismatches {bad}")


def panel_results(agents, sources, manifest, refs, mapping, degrees):
    results = []
    for entry in manifest:
        q = entry["query_id"]
        rows = [json.loads((sources[a] / "metrics" / f"{q}.json").read_text(encoding="utf-8")) for a in agents]
        ref = refs[q]
        if ref["relation_type"] != entry["relation_type"]:
            raise ValueError(f"{q}: manifest and reference relation types differ")
        results.append(query_cofailure(ref, mapping[ref["relation_type"]], entry["ambiguity_tag"], rows,
                                       degrees, agents))
    totals = {f"{k}_{n}": sum(r[k][n] for r in results) for k in KEYS for n in ("cf3", "cf4")}
    totals.update({k: sum(r[k] for r in results) for k in PCF})
    return {"agent_order": agents, "totals": totals, "pairwise": pairwise_agreement(results, agents),
            "queries": results}


def main():
    launcher = load_launcher()
    frozen = yaml.safe_load((ROOT / "configs/pilot.yaml").read_text(encoding="utf-8"))["runtime"]["agent_order"]
    for agent in frozen:
        check_hashes(S22 / agent)
    check_hashes(GEMMA12B)
    manifest = [json.loads(line) for line in
                (ROOT / "data/processed/manifests/screening.jsonl").read_text(encoding="utf-8").splitlines()]
    refs, _, mapping, _, _, degrees = launcher.load_evaluator()
    sources = {a: S22 / a for a in frozen} | {"Gemma4-12B": GEMMA12B}
    substituted = [a if a != "Qwen35-9B" else "Gemma4-12B" for a in frozen]
    payload = {"note": "EXPLORATORY; not a panel change, not S23 acceptance, screening queries only; "
                       "Gemma4-12B rows from S20 run gemma4-12b-5060ti-32k-20261106, others from S22 smoke_single_v135",
               "frozen_panel": panel_results(frozen, sources, manifest, refs, mapping, degrees),
               "gemma12b_panel": panel_results(substituted, sources, manifest, refs, mapping, degrees)}
    launcher.pin_manifest(OUT, payload)
    for name in ("frozen_panel", "gemma12b_panel"):
        p = payload[name]
        print("==", name, p["agent_order"])
        print(json.dumps(p["totals"]))
        for r in p["queries"]:
            flags = {k: r[k]["cf3"] for k in KEYS} | {k: r[k] for k in ("pcf_rel3", "pcf_node3", "pcf_shortcut3")}
            if any(flags.values()):
                print(" ", r["query_id"], r["ambiguity_tag"], flags, "failures:", r["technical_failure_agents"])
        for x in p["pairwise"]:
            print(" ", x["agent_i"], x["agent_j"], f"{x['numerator']}/{x['denominator']}", x["agreement"])


if __name__ == "__main__":
    main()
