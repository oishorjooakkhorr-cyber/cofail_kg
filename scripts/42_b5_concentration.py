"""Phase J B5 — Treat concentration (EXPLORATORY).

Usage (from the repository root, after scripts/30_combined_analysis.py):
    python scripts/42_b5_concentration.py --combined pilot_expansion_v1

Rule (docs/decision_log.md, entry 2026-11-12 "Plan after D7", section B5, verbatim in substance):
  Table of queries, CF3^Q, CF4^Q and CF3^{Q,H1} by group (treat-final, treat-first, other), for pilot,
  expansion and both. Exact hypergeometric probability that the expansion's CF3^{Q,H1} queries all fall
  in the treat-final group. Reported as a replication of a pattern seen in the pilot: the pilot report was
  committed (44a2fdd, 2026-11-08) before the expansion run started; no prediction was written before the
  expansion analysis.

Groups (same entry, "Definitions used below"):
  treat-final = relation types with R2 = {indication}: effect/phenotype:disease:drug,
                gene/protein:disease:drug, gene/protein:drug:disease (75 of the 500);
  treat-first = relation types with R1 = {indication}: disease:drug:effect/phenotype,
                disease:drug:gene/protein, drug:disease:effect/phenotype, drug:disease:gene/protein (358);
  other       = the remaining queries (67).

Per-query quantities are read, never recomputed, from results/combined/<id>/cofailure.json:
  CF3^Q = question.cf3, CF4^Q = question.cf4, CF3^{Q,H1} = hop1_clean.cf3 (protocol §16; the field names
  used by scripts/28_pilot_report.py and scripts/30_combined_analysis.py).
Pilot vs expansion membership comes from the evaluation-side manifests (data/processed/manifests/), named by
results/combined/<id>/components.json; their SHA256 must equal configs/frozen_hashes.yaml (protocol §3.4).

Protocol §19.1: every co-failure metric is reported on all queries and again with SOURCE_NAME_OVERLAP
queries excluded. Both views are written; "all queries" is listed first.

Hypergeometric probability (exact, as a fraction): population = the expansion's queries (N), successes =
its treat-final queries (K), draws = its queries with CF3^{Q,H1} = 1 (n). P(all n in treat-final) =
C(K, n) / C(N, n).

Engineering conventions (documented, not protocol):
* Group is assigned from the relation-type string; the script stops unless R1/R2 stored for each query
  agree with that group (treat-final ⇔ R2 = [indication]; treat-first ⇔ R1 = [indication]).
* The script stops unless the manifests are disjoint, their union equals the combined query set, and each
  manifest's relation type equals the stored one.
* Outputs are write-once: an existing output is never overwritten (an identical re-run is allowed).
* No interpretation is written; the output states the observed counts and the probability only.
"""
from __future__ import annotations

import argparse
import csv
import hashlib
import io
import json
import math
import subprocess
from fractions import Fraction
from pathlib import Path

import yaml

ROOT = Path(__file__).resolve().parents[1]

TREAT_FINAL = ("effect/phenotype:disease:drug", "gene/protein:disease:drug", "gene/protein:drug:disease")
TREAT_FIRST = ("disease:drug:effect/phenotype", "disease:drug:gene/protein", "drug:disease:effect/phenotype",
               "drug:disease:gene/protein")
GROUPS = ("treat-final", "treat-first", "other")
SUBSETS = ("pilot", "expansion", "both")
VIEWS = ("all_queries", "without_source_name_overlap")
METRICS = (("CF3^Q", "question", "cf3"), ("CF4^Q", "question", "cf4"), ("CF3^{Q,H1}", "hop1_clean", "cf3"))
EXPLORATORY_NOTE = ("EXPLORATORY (protocol §20) — docs/decision_log.md, entry 2026-11-12 \"Plan after D7\", "
                    "section B5. Reported as a replication of a pattern seen in the pilot: the pilot report was "
                    "committed (44a2fdd, 2026-11-08) before the expansion run started; no prediction was "
                    "written before the expansion analysis.")


# ------------------------------------------------------------------------------------------- inputs

def sha256_file(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def group_of(relation_type: str, r1: list[str], r2: list[str]) -> str:
    """Decision log 2026-11-12 definitions; stops if the stored R1/R2 disagree with the relation type."""
    if relation_type in TREAT_FINAL:
        group = "treat-final"
    elif relation_type in TREAT_FIRST:
        group = "treat-first"
    else:
        group = "other"
    by_labels = ("treat-final" if list(r2) == ["indication"]
                 else "treat-first" if list(r1) == ["indication"] else "other")
    if group != by_labels:
        raise ValueError(f"relation type {relation_type!r} gives {group}, but R1={r1} R2={r2} give {by_labels}")
    return group


def read_manifest(path: Path) -> dict[str, str]:
    """query_id -> relation_type from an evaluation-side manifest (JSONL)."""
    out = {}
    with path.open(encoding="utf-8") as h:
        for n, line in enumerate(h, 1):
            if not line.strip():
                continue
            row = json.loads(line)
            if row["query_id"] in out:
                raise ValueError(f"{path}: duplicate query {row['query_id']} at line {n}")
            out[row["query_id"]] = row["relation_type"]
    return out


def assign_subsets(queries: list[dict], manifests: dict[str, dict[str, str]]) -> dict[str, str]:
    """query_id -> 'pilot' | 'expansion'; manifests must be disjoint and cover the query set exactly."""
    subset_of: dict[str, str] = {}
    for name, rows in manifests.items():
        for qid in rows:
            if qid in subset_of:
                raise ValueError(f"{qid} is in both the {subset_of[qid]} and {name} manifests")
            subset_of[qid] = name
    stored = {q["query_id"]: q["relation_type"] for q in queries}
    if set(stored) != set(subset_of):
        missing, extra = sorted(set(subset_of) - set(stored)), sorted(set(stored) - set(subset_of))
        raise ValueError(f"manifests vs combined queries differ: only in manifests {missing[:10]}, "
                         f"only in combined {extra[:10]}")
    for name, rows in manifests.items():
        for qid, rel in rows.items():
            if stored[qid] != rel:
                raise ValueError(f"{qid}: relation type {rel!r} in {name} manifest, {stored[qid]!r} stored")
    return subset_of


# --------------------------------------------------------------------------------------- computation

def tabulate(queries: list[dict], subset_of: dict[str, str], exclude: set[str]) -> list[dict]:
    """Rows: for each subset (pilot, expansion, both) × group (+ total): query count and metric sums."""
    rows = []
    for subset in SUBSETS:
        members = [q for q in queries if q["query_id"] not in exclude
                   and (subset == "both" or subset_of[q["query_id"]] == subset)]
        for group in GROUPS + ("total",):
            sel = [q for q in members if group == "total" or q["_group"] == group]
            row = {"subset": subset, "group": group, "queries": len(sel)}
            for label, key, n in METRICS:
                row[label] = sum(int(q[key][n]) for q in sel)
            row["CF3^{Q,H1} query IDs"] = sorted(q["query_id"] for q in sel if q["hop1_clean"]["cf3"])
            rows.append(row)
    return rows


def hypergeometric_all_in(population: int, successes: int, draws: int) -> Fraction:
    """Exact P(X = draws) for X ~ Hypergeometric(N=population, K=successes, n=draws) = C(K,n)/C(N,n)."""
    if not 0 <= successes <= population or not 0 <= draws <= population:
        raise ValueError(f"invalid hypergeometric arguments N={population} K={successes} n={draws}")
    return Fraction(math.comb(successes, draws), math.comb(population, draws))


def expansion_probability(queries: list[dict], subset_of: dict[str, str], exclude: set[str]) -> dict:
    exp = [q for q in queries if subset_of[q["query_id"]] == "expansion" and q["query_id"] not in exclude]
    flagged = sorted((q for q in exp if q["hop1_clean"]["cf3"]), key=lambda q: q["query_id"])
    population = len(exp)
    successes = sum(q["_group"] == "treat-final" for q in exp)
    draws = len(flagged)
    observed_in = sum(q["_group"] == "treat-final" for q in flagged)
    p = hypergeometric_all_in(population, successes, draws)
    return {
        "population_N_expansion_queries": population,
        "successes_K_expansion_treat_final_queries": successes,
        "draws_n_expansion_CF3_Q_H1_queries": draws,
        "CF3_Q_H1_queries": [{"query_id": q["query_id"], "relation_type": q["relation_type"],
                              "group": q["_group"]} for q in flagged],
        "observed_in_treat_final": observed_in,
        "all_in_treat_final": observed_in == draws,
        "probability_all_in_treat_final": {
            "formula": f"C({successes},{draws}) / C({population},{draws})",
            "numerator": math.comb(successes, draws), "denominator": math.comb(population, draws),
            "fraction_reduced": f"{p.numerator}/{p.denominator}",
            "decimal": float(p),
        },
    }


def compute(cofailure: dict, manifests: dict[str, dict[str, str]]) -> dict:
    queries = [dict(q) for q in cofailure["queries"]]
    subset_of = assign_subsets(queries, manifests)
    for q in queries:
        q["_group"] = group_of(q["relation_type"], q["R1"], q["R2"])
    overlap = set(cofailure["source_name_overlap_queries"])
    unknown = sorted(overlap - set(subset_of))
    if unknown:
        raise ValueError(f"SOURCE_NAME_OVERLAP queries not in the query set: {unknown}")
    excludes = {"all_queries": set(), "without_source_name_overlap": overlap}
    return {
        "source_name_overlap_queries": sorted(overlap),
        "group_relation_types": {"treat-final": list(TREAT_FINAL), "treat-first": list(TREAT_FIRST),
                                 "other": sorted({q["relation_type"] for q in queries if q["_group"] == "other"})},
        "tables": {v: tabulate(queries, subset_of, excludes[v]) for v in VIEWS},
        "hypergeometric": {v: expansion_probability(queries, subset_of, excludes[v]) for v in VIEWS},
    }


# -------------------------------------------------------------------------------------------- output

CSV_FIELDS = ["view", "subset", "group", "queries", "CF3^Q", "CF4^Q", "CF3^{Q,H1}", "CF3^{Q,H1} query IDs"]


def to_csv(result: dict) -> str:
    buf = io.StringIO()
    w = csv.DictWriter(buf, fieldnames=CSV_FIELDS, lineterminator="\n")
    w.writeheader()
    for view in VIEWS:
        for row in result["tables"][view]:
            w.writerow({"view": view, **row, "CF3^{Q,H1} query IDs": ";".join(row["CF3^{Q,H1} query IDs"])})
    return buf.getvalue()


def _md_table(header: list[str], rows: list[list]) -> str:
    lines = ["| " + " | ".join(header) + " |", "|" + "---|" * len(header)]
    lines += ["| " + " | ".join(str(c) for c in r) + " |" for r in rows]
    return "\n".join(lines) + "\n"


def to_markdown(result: dict, provenance: dict) -> str:
    out = ["# B5 — Treat concentration (EXPLORATORY)\n", f"{EXPLORATORY_NOTE}\n",
           f"Produced by `scripts/42_b5_concentration.py` at commit `{provenance['git_commit']}` "
           f"(tracked files clean: {provenance['git_tracked_clean']}). Input: "
           f"`{provenance['inputs']['cofailure']['path']}` (SHA256 `{provenance['inputs']['cofailure']['sha256']}`).\n",
           "Groups: treat-final = R2 = {indication} (" + ", ".join(TREAT_FINAL) + "); treat-first = "
           "R1 = {indication} (" + ", ".join(TREAT_FIRST) + "); other = " +
           ", ".join(result["group_relation_types"]["other"]) + ".\n"]
    titles = {"all_queries": "All queries", "without_source_name_overlap":
              "Without SOURCE_NAME_OVERLAP queries (" + ", ".join(result["source_name_overlap_queries"]) +
              "; protocol §19.1)"}
    for i, view in enumerate(VIEWS, 1):
        out.append(f"## Table {i} — {titles[view]}\n")
        out.append(_md_table(["Subset", "Group", "Queries", "CF3^Q", "CF4^Q", "CF3^{Q,H1}", "CF3^{Q,H1} queries"],
                             [[r["subset"], r["group"], r["queries"], r["CF3^Q"], r["CF4^Q"], r["CF3^{Q,H1}"],
                               ", ".join(r["CF3^{Q,H1} query IDs"]) or "—"] for r in result["tables"][view]]))
    out.append("## Exact hypergeometric probability — expansion's CF3^{Q,H1} queries all in treat-final\n")
    rows = []
    for view in VIEWS:
        h = result["hypergeometric"][view]
        p = h["probability_all_in_treat_final"]
        rows.append([titles[view].split(" (")[0], h["population_N_expansion_queries"],
                     h["successes_K_expansion_treat_final_queries"], h["draws_n_expansion_CF3_Q_H1_queries"],
                     h["observed_in_treat_final"], "yes" if h["all_in_treat_final"] else "no",
                     p["formula"], f"{p['numerator']}/{p['denominator']} = {p['fraction_reduced']}",
                     f"{p['decimal']:.6g}"])
    out.append(_md_table(["View", "N (expansion queries)", "K (treat-final)", "n (CF3^{Q,H1} = 1)",
                          "Observed in treat-final", "All in treat-final", "Formula", "Exact", "Decimal"], rows))
    out.append("\nP = C(K, n) / C(N, n): the probability that n queries drawn without replacement from the "
               "expansion's N queries all fall among its K treat-final queries.\n")
    return "\n".join(out)


def write_once(path: Path, text: str) -> None:
    if path.exists():
        if path.read_text(encoding="utf-8") != text:
            raise FileExistsError(f"{path} exists with different content; not overwritten")
        return
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("x", encoding="utf-8", newline="\n") as h:
        h.write(text)


def git_state() -> tuple[str, bool]:
    commit = subprocess.run(["git", "rev-parse", "HEAD"], cwd=ROOT, capture_output=True, text=True,
                            check=True).stdout.strip()
    dirty = subprocess.run(["git", "status", "--porcelain", "--untracked-files=no"], cwd=ROOT,
                           capture_output=True, text=True, check=True).stdout.strip()
    return commit, not dirty


def main(argv=None) -> int:
    ap = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    ap.add_argument("--combined", required=True, help="results/combined/<id> (e.g. pilot_expansion_v1)")
    ap.add_argument("--out", default="results/exploratory/b5")
    args = ap.parse_args(argv)

    comb_dir = ROOT / "results" / "combined" / args.combined
    cof_path = comb_dir / "cofailure.json"
    cofailure = json.loads(cof_path.read_text(encoding="utf-8"))
    components = json.loads((comb_dir / "components.json").read_text(encoding="utf-8"))["components"]
    frozen = yaml.safe_load((ROOT / "configs" / "frozen_hashes.yaml").read_text(encoding="utf-8"))["manifests"]

    manifests, manifest_inputs = {}, {}
    for run_id in sorted(components):
        name = components[run_id]["manifest"]
        rel = f"data/processed/manifests/{name}.jsonl"
        digest = sha256_file(ROOT / rel)
        if frozen.get(rel) != digest:
            raise ValueError(f"{rel}: SHA256 {digest} != frozen {frozen.get(rel)} (protocol §3.4)")
        manifests[name] = read_manifest(ROOT / rel)
        if len(manifests[name]) != components[run_id]["queries"]:
            raise ValueError(f"{rel}: {len(manifests[name])} queries, components.json says "
                             f"{components[run_id]['queries']}")
        manifest_inputs[name] = {"path": rel, "sha256": digest, "run_id": run_id}
    if set(manifests) != {"pilot", "expansion"}:
        raise ValueError(f"B5 needs exactly the pilot and expansion manifests, got {sorted(manifests)}")

    result = compute(cofailure, manifests)
    commit, clean = git_state()
    provenance = {"git_commit": commit, "git_tracked_clean": clean, "combined_id": args.combined,
                  "inputs": {"cofailure": {"path": cof_path.relative_to(ROOT).as_posix(),
                                           "sha256": sha256_file(cof_path)},
                             "manifests": manifest_inputs}}
    out_dir = ROOT / args.out
    payload = {"stage": "B5", "status": "EXPLORATORY", "note": EXPLORATORY_NOTE, "provenance": provenance,
               **result}
    write_once(out_dir / "b5.json", json.dumps(payload, indent=2, sort_keys=True, ensure_ascii=False) + "\n")
    write_once(out_dir / "b5_table.csv", to_csv(result))
    write_once(out_dir / "b5_report.md", to_markdown(result, provenance))
    print(to_markdown(result, provenance))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
