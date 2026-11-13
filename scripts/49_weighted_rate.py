"""Phase J PW — Population-weighted co-failure rate (EXPLORATORY, descriptive).

Usage (from the repository root; needs only pushed files, no raw records):
    python scripts/49_weighted_rate.py

Rule (docs/decision_log.md, entry 2026-11-14 "PW — Population-weighted co-failure rate", fixed before any
PW output existed):
  Population: data/processed/primary_population.csv (7,176 queries, protocol §7.2).
  Strata: §8 sampling strata, relation type × bridge multiplicity.
  Sample: the 500 queries of record (pilot + expansion manifests); flags from
  results/combined/pilot_expansion_v1/cofailure.json; all queries (§19.1).
  Metrics: primary CF3^{Q,H1}; secondary CF3^Q and CF4^Q.
  - Sample rate y / n with the Wilson 95% interval (z = 1.959964).
  - Weighted rate p_w = Σ_h (N_h / N) · (y_h / n_h).
  - Interval for p_w: 2.5th / 97.5th percentiles of 100,000 draws of Σ_h (N_h / N) · θ_h,
    θ_h ~ Beta(y_h + 0.5, n_h − y_h + 0.5) independently; NumPy Generator(PCG64), seed 42.
  No threshold, no outcome.

Engineering conventions (documented, not protocol):
* Strata and metrics are processed in sorted order. For the Monte Carlo, the draws for each metric
  use a fresh Generator(PCG64(42)), and within a metric the strata are drawn in sorted order, so each
  metric's interval does not depend on which other metrics are computed.
* Percentiles use numpy.quantile with its default (linear) method.
* The script stops if a sampled query is not in the population, a population stratum has no sampled
  query, or a sampled query has no flag in cofailure.json.
"""
from __future__ import annotations

import argparse
import csv
import hashlib
import io
import json
import math
import subprocess
from pathlib import Path

import numpy as np

ROOT = Path(__file__).resolve().parents[1]
Z95 = 1.959964
DRAWS = 100_000
SEED = 42
METRICS = {"CF3^{Q,H1}": ("hop1_clean", "cf3"), "CF3^Q": ("question", "cf3"), "CF4^Q": ("question", "cf4")}
PRIMARY = "CF3^{Q,H1}"


def wilson(y: int, n: int, z: float = Z95) -> tuple[float, float]:
    if n <= 0:
        raise ValueError("Wilson interval needs n > 0")
    p = y / n
    denom = 1 + z * z / n
    centre = (p + z * z / (2 * n)) / denom
    half = z * math.sqrt(p * (1 - p) / n + z * z / (4 * n * n)) / denom
    return max(0.0, centre - half), min(1.0, centre + half)


def strata_table(population: dict[str, tuple[str, str]], sample: list[str],
                 flags: dict[str, dict[str, int]]) -> dict:
    missing = sorted(q for q in sample if q not in population)
    if missing:
        raise ValueError(f"sampled queries not in the population: {missing}")
    no_flag = sorted(q for q in sample if q not in flags)
    if no_flag:
        raise ValueError(f"sampled queries without co-failure flags: {no_flag}")
    strata: dict[tuple[str, str], dict] = {}
    for stratum in population.values():
        strata.setdefault(stratum, {"N": 0, "n": 0, "y": {m: 0 for m in METRICS}})["N"] += 1
    for q in sample:
        s = strata[population[q]]
        s["n"] += 1
        for m in METRICS:
            s["y"][m] += flags[q][m]
    empty = sorted(k for k, v in strata.items() if v["n"] == 0)
    if empty:
        raise ValueError(f"population strata with no sampled query: {empty}")
    return dict(sorted(strata.items()))


def estimate(strata: dict, metric: str, draws: int = DRAWS, seed: int = SEED) -> dict:
    n_pop = sum(s["N"] for s in strata.values())
    n_samp = sum(s["n"] for s in strata.values())
    y_samp = sum(s["y"][metric] for s in strata.values())
    lo, hi = wilson(y_samp, n_samp)
    p_w = sum(s["N"] / n_pop * s["y"][metric] / s["n"] for s in strata.values())
    rng = np.random.Generator(np.random.PCG64(seed))
    total = np.zeros(draws)
    for s in strata.values():
        y, n = s["y"][metric], s["n"]
        total += s["N"] / n_pop * rng.beta(y + 0.5, n - y + 0.5, size=draws)
    q_lo, q_hi = np.quantile(total, [0.025, 0.975])
    return {"sample_y": y_samp, "sample_n": n_samp, "sample_rate": y_samp / n_samp,
            "sample_wilson_95": [lo, hi], "weighted_rate": p_w,
            "weighted_interval_95": [float(q_lo), float(q_hi)], "population_N": n_pop}


def compute(population: dict, sample: list[str], flags: dict) -> dict:
    strata = strata_table(population, sample, flags)
    return {"strata": [{"relation_type": k[0], "bridge_multiplicity": k[1], **v} for k, v in strata.items()],
            "metrics": {m: estimate(strata, m) for m in sorted(METRICS)}}


def pct(x: float) -> str:
    return f"{100 * x:.2f}%"


def report(result: dict, provenance: dict) -> str:
    out = ["# PW — Population-weighted co-failure rate (EXPLORATORY, descriptive)\n",
           "EXPLORATORY (protocol §20) — docs/decision_log.md, entry 2026-11-14 \"PW — Population-weighted "
           "co-failure rate\" (rule fixed before computing). Descriptive: no threshold, no outcome.\n",
           f"Produced by `scripts/49_weighted_rate.py` at commit `{provenance['commit']}` (tracked files clean: "
           f"{provenance['clean']}). Inputs (SHA256): "
           + ", ".join(f"`{k}` `{v}`" for k, v in sorted(provenance["inputs"].items())) + ".\n",
           "Population: the primary population (7,176 queries, protocol §7.2), not all of BioHopR. Strata: "
           "relation type × bridge multiplicity (§8). Sample: the 500 queries of record, all queries (§19.1).\n",
           "## Rates\n",
           "| Metric | Sample | Sample rate (Wilson 95%) | Weighted to primary population (95% interval) |",
           "|---|---|---|---|"]
    for m, e in result["metrics"].items():
        tag = " (primary)" if m == PRIMARY else ""
        out.append(f"| {m}{tag} | {e['sample_y']}/{e['sample_n']} | {pct(e['sample_rate'])} "
                   f"({pct(e['sample_wilson_95'][0])}–{pct(e['sample_wilson_95'][1])}) | "
                   f"{pct(e['weighted_rate'])} ({pct(e['weighted_interval_95'][0])}–"
                   f"{pct(e['weighted_interval_95'][1])}) |")
    out += ["\nWeighted interval: Monte Carlo, 100,000 draws of Σ_h (N_h/N)·θ_h with θ_h ~ Beta(y_h+½, n_h−y_h+½) "
            "per stratum (Jeffreys), seed 42. Strata with no event add width to the interval, nothing to the "
            "point estimate.\n",
            "## Strata\n",
            "| Relation type | Multiplicity | N_h (population) | n_h (sample) | Weight N_h/N | "
            + " | ".join(f"y_h {m}" for m in sorted(METRICS)) + " |",
            "|---|---|---|---|---|" + "---|" * len(METRICS)]
    n_pop = sum(s["N"] for s in result["strata"])
    for s in result["strata"]:
        out.append(f"| {s['relation_type']} | {s['bridge_multiplicity']} | {s['N']} | {s['n']} | "
                   f"{s['N'] / n_pop:.4f} | " + " | ".join(str(s["y"][m]) for m in sorted(METRICS)) + " |")
    out.append("\nLimits (logged with the rule): stratum rates rest on 6 to 51 sampled queries in 10 of 11 "
               "strata; most strata have no event; the interval is wide where strata are thin and large.\n")
    return "\n".join(out)


def strata_csv(result: dict) -> str:
    buf = io.StringIO()
    w = csv.writer(buf, lineterminator="\n")
    w.writerow(["relation_type", "bridge_multiplicity", "N_h", "n_h", "weight"] + [f"y_h {m}" for m in sorted(METRICS)])
    n_pop = sum(s["N"] for s in result["strata"])
    for s in result["strata"]:
        w.writerow([s["relation_type"], s["bridge_multiplicity"], s["N"], s["n"], f"{s['N'] / n_pop:.6f}"]
                   + [s["y"][m] for m in sorted(METRICS)])
    return buf.getvalue()


def sha256(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def main() -> None:
    ap = argparse.ArgumentParser()
    ap.add_argument("--combined", default="pilot_expansion_v1")
    ap.add_argument("--out", default="results/exploratory/pw")
    args = ap.parse_args()
    pop_path = ROOT / "data/processed/primary_population.csv"
    man_paths = [ROOT / f"data/processed/manifests/{m}.jsonl" for m in ("pilot", "expansion")]
    cof_path = ROOT / "results/combined" / args.combined / "cofailure.json"
    with pop_path.open(encoding="utf-8", newline="") as fh:
        population = {r["query_id"]: (r["relation_type"], r["bridge_multiplicity"]) for r in csv.DictReader(fh)}
    sample = sorted(json.loads(line)["query_id"] for p in man_paths
                    for line in p.read_text(encoding="utf-8").splitlines() if line.strip())
    if len(sample) != len(set(sample)):
        raise ValueError("duplicate query IDs across the pilot and expansion manifests")
    cofailure = json.loads(cof_path.read_text(encoding="utf-8"))
    flags = {q["query_id"]: {m: int(q[sec][key]) for m, (sec, key) in METRICS.items()}
             for q in cofailure["queries"]}
    result = compute(population, sample, flags)
    commit = subprocess.check_output(["git", "rev-parse", "HEAD"], cwd=ROOT, text=True).strip()
    clean = not subprocess.check_output(["git", "status", "--porcelain", "--untracked-files=no"],
                                        cwd=ROOT, text=True).strip()
    provenance = {"commit": commit, "clean": clean,
                  "inputs": {p.relative_to(ROOT).as_posix(): sha256(p) for p in [pop_path, *man_paths, cof_path]}}
    out = ROOT / args.out
    out.mkdir(parents=True, exist_ok=True)
    (out / "pw.json").write_text(json.dumps({"provenance": provenance, **result}, indent=2, sort_keys=True) + "\n",
                                 encoding="utf-8")
    (out / "pw_strata.csv").write_text(strata_csv(result), encoding="utf-8")
    (out / "pw_report.md").write_text(report(result, provenance), encoding="utf-8")
    e = result["metrics"][PRIMARY]
    print(f"PW {PRIMARY}: sample {pct(e['sample_rate'])} (Wilson {pct(e['sample_wilson_95'][0])}–"
          f"{pct(e['sample_wilson_95'][1])}); weighted {pct(e['weighted_rate'])} "
          f"({pct(e['weighted_interval_95'][0])}–{pct(e['weighted_interval_95'][1])})")


if __name__ == "__main__":
    main()
