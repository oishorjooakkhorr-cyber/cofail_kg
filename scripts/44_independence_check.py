"""Phase J IC — Independence check of off-label uptake (EXPLORATORY).

Usage (from the repository root; needs only pushed files, no raw records):
    python scripts/44_independence_check.py

Rule (docs/decision_log.md, entry 2026-11-13 "IC — Independence check of off-label uptake", fixed before
any IC output existed):
  Input: results/exploratory/b1/b1_episodes.csv, rows with group = treat-final (SUCCESS episodes, latest
  attempts, as in B1).
  - p_i: agent i's B1 uptake on all treat-final queries, (Taken and Opportunity) / Opportunity.
  - A_q: agents with Opportunity = True on query q; K_q: agents in A_q with Taken = True.
  - Primary statistic T = number of queries with K_q >= 3.
  - Null: within a query, Taken for i in A_q is an independent Bernoulli(p_i); queries independent.
    P(K_q >= 3) exact (Poisson-binomial); distribution of T exact (convolution over queries).
  - Outcome: AGREES if P(T >= T_obs) > 0.025 and P(T <= T_obs) > 0.025; MORE CLUSTERED if
    P(T >= T_obs) <= 0.025; LESS CLUSTERED if P(T <= T_obs) <= 0.025.
  - Secondary (descriptive): pairs statistic S and its expectation; per-query K_q next to CF3^{Q,H1};
    the same computation without SOURCE_NAME_OVERLAP queries (protocol §19.1), p_i recomputed there.

Engineering conventions (documented, not protocol):
* Probabilities are computed in double precision by exact dynamic programming (no simulation, no seed).
* Percentiles of T: the smallest t with P(T <= t) >= 0.025 (2.5th) and >= 0.975 (97.5th).
* CF3^{Q,H1} is read, not recomputed, from results/combined/<id>/cofailure.json (hop1_clean.cf3).
* Agents and queries are processed in sorted order; outputs use sorted keys.
* The script stops if an agent has no opportunity episode (p_i undefined) or a CSV value is not
  "True"/"False".
"""
from __future__ import annotations

import argparse
import csv
import hashlib
import io
import json
import subprocess
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
ALPHA = 0.025
VIEWS = ("all_queries", "without_source_name_overlap")


def as_bool(value: str, field: str, row: dict) -> bool:
    if value == "True":
        return True
    if value == "False":
        return False
    raise ValueError(f"{field} must be True/False, got {value!r} in row {row.get('query_id')}/{row.get('agent_id')}")


def load_rows(path: Path) -> list[dict]:
    rows = []
    with path.open(encoding="utf-8", newline="") as fh:
        for row in csv.DictReader(fh):
            if row["group"] != "treat-final":
                continue
            rows.append({"query_id": row["query_id"], "agent_id": row["agent_id"],
                         "opportunity": as_bool(row["opportunity"], "opportunity", row),
                         "taken": as_bool(row["taken"], "taken", row),
                         "overlap": as_bool(row["source_name_overlap"], "source_name_overlap", row)})
    return rows


def poisson_binomial(probs: list[float]) -> list[float]:
    """Exact distribution of a sum of independent Bernoulli(p) variables: dist[k] = P(sum = k)."""
    dist = [1.0]
    for p in probs:
        nxt = [0.0] * (len(dist) + 1)
        for k, mass in enumerate(dist):
            nxt[k] += mass * (1.0 - p)
            nxt[k + 1] += mass * p
        dist = nxt
    return dist


def percentile(dist: list[float], level: float) -> int:
    cum = 0.0
    for t, mass in enumerate(dist):
        cum += mass
        if cum >= level - 1e-12:
            return t
    return len(dist) - 1


def compute(rows: list[dict], cf3_h1: dict[str, int]) -> dict:
    agents = sorted({r["agent_id"] for r in rows})
    rate = {}
    for a in agents:
        opp = [r for r in rows if r["agent_id"] == a and r["opportunity"]]
        if not opp:
            raise ValueError(f"agent {a} has no opportunity episode; p_i undefined")
        taken = sum(1 for r in opp if r["taken"])
        rate[a] = {"opportunity": len(opp), "taken_and_opportunity": taken, "p": taken / len(opp)}

    per_query, q_probs = [], []
    s_obs, s_exp = 0, 0.0
    for qid in sorted({r["query_id"] for r in rows}):
        in_q = sorted((r for r in rows if r["query_id"] == qid and r["opportunity"]), key=lambda r: r["agent_id"])
        a_q = [r["agent_id"] for r in in_q]
        takers = [r["agent_id"] for r in in_q if r["taken"]]
        probs = [rate[a]["p"] for a in a_q]
        dist_k = poisson_binomial(probs)
        p_ge3 = sum(dist_k[3:])
        q_probs.append(p_ge3)
        pairs_obs = len(takers) * (len(takers) - 1) // 2
        pairs_exp = sum(probs[i] * probs[j] for i in range(len(probs)) for j in range(i + 1, len(probs)))
        s_obs += pairs_obs
        s_exp += pairs_exp
        per_query.append({"query_id": qid, "A_q": a_q, "takers": takers, "K_q": len(takers),
                          "P_K_ge_3": p_ge3, "CF3_Q_H1": cf3_h1.get(qid)})

    dist_t = poisson_binomial(q_probs)
    t_obs = sum(1 for q in per_query if q["K_q"] >= 3)
    p_ge = sum(dist_t[t_obs:])
    p_le = sum(dist_t[: t_obs + 1])
    if p_ge <= ALPHA:
        outcome = "MORE CLUSTERED"
    elif p_le <= ALPHA:
        outcome = "LESS CLUSTERED"
    else:
        outcome = "AGREES"
    return {"agents": rate, "queries": len(per_query),
            "queries_with_opportunity": sum(1 for q in per_query if q["A_q"]),
            "T_obs": t_obs, "E_T": sum(q_probs),
            "T_2.5th": percentile(dist_t, ALPHA), "T_97.5th": percentile(dist_t, 1 - ALPHA),
            "P_T_ge_obs": p_ge, "P_T_le_obs": p_le, "outcome": outcome,
            "S_obs": s_obs, "S_expected": s_exp, "per_query": per_query}


def report(result: dict, provenance: dict) -> str:
    out = ["# IC — Independence check of off-label uptake (EXPLORATORY)\n",
           "EXPLORATORY (protocol §20) — docs/decision_log.md, entry 2026-11-13 \"IC — Independence check of "
           "off-label uptake\" (rule fixed before computing). Treat-final queries; SUCCESS episodes, latest "
           "attempts, as in B1.\n",
           f"Produced by `scripts/44_independence_check.py` at commit `{provenance['commit']}` (tracked files "
           f"clean: {provenance['clean']}). Inputs: `{provenance['episodes']['path']}` (SHA256 "
           f"`{provenance['episodes']['sha256']}`), `{provenance['cofailure']['path']}` (SHA256 "
           f"`{provenance['cofailure']['sha256']}`).\n"]
    for view in VIEWS:
        r = result[view]
        title = "All queries (primary)" if view == "all_queries" else \
            "Without SOURCE_NAME_OVERLAP queries (protocol §19.1; descriptive, p_i recomputed)"
        out.append(f"## {title}\n")
        if view == "all_queries":
            out.append(f"**Outcome: {r['outcome']}** — T_obs = {r['T_obs']}; under independence E[T] = "
                       f"{r['E_T']:.3f}, central 95% range {r['T_2.5th']}–{r['T_97.5th']}; "
                       f"P(T ≥ {r['T_obs']}) = {r['P_T_ge_obs']:.4f}, P(T ≤ {r['T_obs']}) = {r['P_T_le_obs']:.4f}.\n")
        else:
            out.append(f"Outcome rule applied here (descriptive, not the outcome): {r['outcome']} — T_obs = "
                       f"{r['T_obs']}; E[T] = {r['E_T']:.3f}, range {r['T_2.5th']}–{r['T_97.5th']}; "
                       f"P(T ≥ obs) = {r['P_T_ge_obs']:.4f}, P(T ≤ obs) = {r['P_T_le_obs']:.4f}.\n")
        out.append("| Agent | Opportunity | Taken ∧ Opportunity | p_i |\n|---|---|---|---|")
        for a, v in sorted(r["agents"].items()):
            out.append(f"| {a} | {v['opportunity']} | {v['taken_and_opportunity']} | {v['p']:.3f} |")
        out.append(f"\nQueries: {r['queries']} ({r['queries_with_opportunity']} with ≥ 1 agent in A_q). "
                   f"Pairs statistic (descriptive): S_obs = {r['S_obs']}, expected {r['S_expected']:.2f}.\n")
        if view == "all_queries":
            out.append("Queries with K_q ≥ 2 or CF3^{Q,H1} = 1:\n")
            out.append("| Query | A_q | Takers | K_q | P(K_q ≥ 3) | CF3^{Q,H1} |\n|---|---|---|---|---|---|")
            for q in r["per_query"]:
                if q["K_q"] >= 2 or q["CF3_Q_H1"] == 1:
                    out.append(f"| {q['query_id']} | {', '.join(q['A_q'])} | {', '.join(q['takers'])} | "
                               f"{q['K_q']} | {q['P_K_ge_3']:.4f} | {q['CF3_Q_H1']} |")
            out.append("")
    out.append("Limits (logged with the rule): p_i is estimated from the same episodes; queries whose off-label "
               "lists are more tempting would also appear as MORE CLUSTERED. Agents never share anything "
               "(§9.3); \"independent\" means only that each agent's own rate explains the pattern.\n")
    return "\n".join(out)


def per_query_csv(result: dict) -> str:
    buf = io.StringIO()
    w = csv.writer(buf, lineterminator="\n")
    w.writerow(["query_id", "A_q", "takers", "K_q", "P_K_ge_3", "CF3_Q_H1"])
    for q in result["all_queries"]["per_query"]:
        w.writerow([q["query_id"], ";".join(q["A_q"]), ";".join(q["takers"]), q["K_q"],
                    f"{q['P_K_ge_3']:.6f}", q["CF3_Q_H1"]])
    return buf.getvalue()


def sha256(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def main() -> None:
    ap = argparse.ArgumentParser()
    ap.add_argument("--episodes", default="results/exploratory/b1/b1_episodes.csv")
    ap.add_argument("--combined", default="pilot_expansion_v1")
    ap.add_argument("--out", default="results/exploratory/ic")
    args = ap.parse_args()
    ep_path = ROOT / args.episodes
    cof_path = ROOT / "results/combined" / args.combined / "cofailure.json"
    cofailure = json.loads(cof_path.read_text(encoding="utf-8"))
    cf3_h1 = {q["query_id"]: int(q["hop1_clean"]["cf3"]) for q in cofailure["queries"]}
    rows = load_rows(ep_path)
    result = {"all_queries": compute(rows, cf3_h1),
              "without_source_name_overlap": compute([r for r in rows if not r["overlap"]], cf3_h1)}
    commit = subprocess.check_output(["git", "rev-parse", "HEAD"], cwd=ROOT, text=True).strip()
    clean = not subprocess.check_output(["git", "status", "--porcelain", "--untracked-files=no"],
                                        cwd=ROOT, text=True).strip()
    provenance = {"commit": commit, "clean": clean,
                  "episodes": {"path": ep_path.relative_to(ROOT).as_posix(), "sha256": sha256(ep_path)},
                  "cofailure": {"path": cof_path.relative_to(ROOT).as_posix(), "sha256": sha256(cof_path)}}
    out = ROOT / args.out
    out.mkdir(parents=True, exist_ok=True)
    (out / "ic.json").write_text(json.dumps({"provenance": provenance, **result}, indent=2, sort_keys=True)
                                 + "\n", encoding="utf-8")
    (out / "ic_per_query.csv").write_text(per_query_csv(result), encoding="utf-8")
    (out / "ic_report.md").write_text(report(result, provenance), encoding="utf-8")
    r = result["all_queries"]
    print(f"IC outcome: {r['outcome']} (T_obs={r['T_obs']}, E[T]={r['E_T']:.3f}, "
          f"P(T>=obs)={r['P_T_ge_obs']:.4f}, P(T<=obs)={r['P_T_le_obs']:.4f})")


if __name__ == "__main__":
    main()
