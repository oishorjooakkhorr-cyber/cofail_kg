"""Phase J B1 — Off-label opportunity and uptake (EXPLORATORY).

Usage (from the repository root, on the PC that holds the raw run records):
    python scripts/40_b1_uptake.py --combined pilot_expansion_v1

Rule (docs/decision_log.md, entry 2026-11-12 "Plan after D7", section B1):
  Population: SUCCESS episodes of pilot_v1 and expansion_v1 on the 75 treat-final queries (primary);
  treat-first queries reported separately, descriptive only. Per episode:
  - Opportunity: some node u that the agent reached from s through an R1 label, where an inspect_entity(u)
    output listed `off-label use` with a Type_T neighbor type, or the agent called
    get_neighbors(u, "off-label use", …).
  - Opened: the agent called get_neighbors(u, "off-label use", …) on such a u.
  - Taken: the episode has ≥ 1 off-label answer (a retained answer whose primary path, §14.2, uses the
    label `off-label use` at the step whose accepted set is {indication}).
  Per agent: uptake = Taken / Opportunity; also Opened / Opportunity and Taken / Opened.
  CLEAN: at least 3 of the 4 agents have ≥ 5 opportunity episodes and uptake ≥ 0.50. Otherwise NOT CLEAN.

Readings (researcher, 2026-11-12; docs/decision_log.md entry "B1 — Readings of the B1 definitions"):
  1. Reached: u is listed in a successful get_neighbors(s, r1 ∈ R1) result (any page, any neighbor_type) —
     the trace-graph edge s –r1→ u. Any get_neighbors(u, `off-label use`, …) call counts for Opportunity and
     Opened, successful or not. Call order within the episode is ignored.
  2. Taken (treat-final): primary path with ≥ 2 edges whose second edge is `off-label use`.
  3. Treat-first, mirrored at s: Opportunity = inspect_entity(s) listed `off-label use` with a Type_B
     neighbor type, or any get_neighbors(s, `off-label use`, …) call; Opened = that call; Taken = primary
     path whose first edge is `off-label use`.
  4. Nested ratios: uptake = (Taken ∧ Opportunity) / Opportunity; Opened / Opportunity;
     Taken/Opened = (Taken ∧ Opened) / Opened. Taken episodes outside Opportunity get their own column.
  5. CLEAN / NOT CLEAN on all queries, treat-final. The view without SOURCE_NAME_OVERLAP queries (§19.1)
     is written as well, descriptive only.

Inputs: results/combined/<id>/{components,cofailure}.json; per run, the latest-attempt §15 metrics rows
(results/runs/<run>/analysis/metrics/, which hold the frozen primary path of every retained answer) and the
raw episode records (call logs), loaded with scripts/28_pilot_report.py load_combined; the evaluation-side
manifests; data/processed/reference_queries.parquet (Type_B, Type_T); the KG fingerprint.

Engineering conventions (documented, not protocol):
* Taken is read from the stored primary paths of the analysis of record (not recomputed). Each stored
  primary-path edge must exist, with the same creation index, in the trace graph rebuilt from the raw
  record (trace.build_trace_graph); the script stops otherwise. The stored status must equal the record's.
* A tool-call `entity_id` argument is matched as a node ID after str() and strip() (a JSON integer is its
  decimal string), as in scripts/30_candidates_c.py `opened`. inspect_entity is matched by the returned
  `id`, so only successful inspect calls count (a failed one lists no relations).
* Groups come from the relation type (scripts/42_b5_concentration.py group_of, which also checks R1/R2).
  Episodes of "other" queries are not counted.
* Inputs are hash-checked (manifests and KG fingerprint against configs/frozen_hashes.yaml); outputs are
  write-once (an identical re-run is allowed).
* No interpretation is written. CLEAN / NOT CLEAN is stated mechanically.
"""
from __future__ import annotations

import argparse
import csv
import hashlib
import importlib.util
import io
import json
import subprocess
import sys
from pathlib import Path

import pyarrow.parquet as pq
import yaml

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "src"))
from cofail_kg.agents.trace import build_trace_graph  # noqa: E402

OFF_LABEL = "off-label use"
MIN_OPPORTUNITY = 5      # decision log 2026-11-12 B1: "≥ 5 opportunity episodes"
MIN_UPTAKE = 0.50        # "uptake ≥ 0.50"
MIN_AGENTS = 3           # "at least 3 of the 4 agents"
GROUPS = ("treat-final", "treat-first")
VIEWS = ("all_queries", "without_source_name_overlap")
EXPLORATORY_NOTE = ("EXPLORATORY (protocol §20) — docs/decision_log.md, entry 2026-11-12 \"Plan after D7\", "
                    "section B1, with the readings of the entry 2026-11-12 \"B1 — Readings of the B1 "
                    "definitions\". Treat-final is primary; treat-first is descriptive only.")


def load_script(name: str, filename: str):
    spec = importlib.util.spec_from_file_location(name, ROOT / "scripts" / filename)
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


B5 = load_script("b5_concentration", "42_b5_concentration.py")


def sha256_file(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


# ------------------------------------------------------------------------------------- per episode

def node_arg(value) -> str | None:
    """Tool-call entity_id as a node-ID string (str + strip); None if absent."""
    if value is None:
        return None
    return str(value).strip()


def check_paths_in_trace(record: dict, row: dict) -> None:
    """Every stored primary-path edge must be a trace-graph edge of the raw record (same creation index)."""
    edges = {(e.creation_index, e.u, e.label, e.v) for e in build_trace_graph(record).edges}
    for answer in row["answers"]:
        for e in answer.get("primary_path") or []:
            key = (e["creation_index"], e["u"], e["label"], e["v"])
            if key not in edges:
                raise ValueError(f"{row['query_id']}/{row['agent_id']}: stored primary-path edge {key} "
                                 f"is not in the trace graph of the raw record")


def classify_episode(record: dict, row: dict, s: str, r1: list[str], neighbor_type: str,
                     group: str) -> dict:
    """Opportunity / Opened / Taken for one SUCCESS episode (readings 1–3)."""
    calls = record["call_log"]
    if group == "treat-final":
        reached = {e.v for e in build_trace_graph(record).edges if e.u == s and e.label in set(r1)}
        step = 1    # index of the indication step in the primary path (second edge)
    elif group == "treat-first":
        reached = {s}
        step = 0    # first edge
    else:
        raise ValueError(f"no B1 rule for group {group!r}")
    listed, opened = set(), set()
    for call in calls:
        args = call.get("arguments") or {}
        node = node_arg(args.get("entity_id"))
        if call.get("tool") == "get_neighbors" and args.get("relation") == OFF_LABEL and node in reached:
            opened.add(node)
        if call.get("tool") == "inspect_entity" and call.get("success"):
            result = call["result"]
            u = str(result["id"])
            if u in reached and any(rel["label"] == OFF_LABEL and neighbor_type in rel["neighbor_types"]
                                    for rel in result["relations"]):
                listed.add(u)
    off_label_answers = sorted(
        (a["node_id"] for a in row["answers"]
         if a.get("primary_path") and len(a["primary_path"]) > step
         and a["primary_path"][step]["label"] == OFF_LABEL), key=int)
    opportunity_nodes = sorted(listed | opened, key=int)
    return {"opportunity": bool(opportunity_nodes), "opened": bool(opened), "taken": bool(off_label_answers),
            "opportunity_nodes": opportunity_nodes, "opened_nodes": sorted(opened, key=int),
            "listed_nodes": sorted(listed, key=int), "off_label_answers": off_label_answers,
            "reached_count": len(reached)}


# ----------------------------------------------------------------------------------------- per agent

def ratio(num: int, den: int) -> float | None:
    return num / den if den else None


def summarize(episodes: list[dict], agents: list[str]) -> list[dict]:
    """Per agent: counts and the three nested ratios (reading 4)."""
    out = []
    for agent in agents:
        mine = [e for e in episodes if e["agent_id"] == agent]
        opp = [e for e in mine if e["opportunity"]]
        opn = [e for e in mine if e["opened"]]
        taken = [e for e in mine if e["taken"]]
        t_opp = sum(e["taken"] for e in opp)
        t_opn = sum(e["taken"] for e in opn)
        out.append({"agent_id": agent, "episodes": len(mine), "opportunity": len(opp), "opened": len(opn),
                    "taken": len(taken), "taken_and_opportunity": t_opp, "taken_and_opened": t_opn,
                    "taken_outside_opportunity": len(taken) - t_opp,
                    "uptake": ratio(t_opp, len(opp)), "opened_per_opportunity": ratio(len(opn), len(opp)),
                    "taken_per_opened": ratio(t_opn, len(opn))})
    return out


def clean_verdict(rows: list[dict]) -> dict:
    """CLEAN iff ≥ 3 agents have ≥ 5 opportunity episodes and uptake ≥ 0.50 (decision log 2026-11-12 B1)."""
    meeting = [r["agent_id"] for r in rows
               if r["opportunity"] >= MIN_OPPORTUNITY and r["uptake"] is not None and r["uptake"] >= MIN_UPTAKE]
    return {"agents_meeting": meeting, "count": len(meeting),
            "outcome": "CLEAN" if len(meeting) >= MIN_AGENTS else "NOT CLEAN",
            "rule": f"at least {MIN_AGENTS} of the 4 agents have >= {MIN_OPPORTUNITY} opportunity episodes "
                    f"and uptake >= {MIN_UPTAKE:.2f}"}


def compute(data: dict, refs: dict[str, dict], subset_of: dict[str, str]) -> dict:
    cof = data["cofailure"]
    agents = data["agents"]
    overlap = set(cof["source_name_overlap_queries"])
    episodes, excluded = [], {g: {a: {} for a in agents} for g in GROUPS}
    for q in sorted(cof["queries"], key=lambda x: x["query_id"]):
        group = B5.group_of(q["relation_type"], q["R1"], q["R2"])
        if group not in GROUPS:
            continue
        ref = refs[q["query_id"]]
        if ref["s"] != q["s"]:
            raise ValueError(f"{q['query_id']}: s {q['s']} in cofailure.json, {ref['s']} in the references")
        neighbor_type = ref["Type_T"] if group == "treat-final" else ref["Type_B"]
        for agent in agents:
            row, record = data["rows"][(agent, q["query_id"])], data["records"][(agent, q["query_id"])]
            if record["query_id"] != q["query_id"] or record["agent_id"] != agent:
                raise ValueError(f"record identity mismatch for {(agent, q['query_id'])}")
            if row["episode_status"] != record["status"]:
                raise ValueError(f"{q['query_id']}/{agent}: metrics status {row['episode_status']} != "
                                 f"record status {record['status']}")
            if row["episode_status"] != "SUCCESS":
                bucket = excluded[group][agent]
                bucket[row["episode_status"]] = bucket.get(row["episode_status"], 0) + 1
                continue
            check_paths_in_trace(record, row)
            ep = classify_episode(record, row, q["s"], q["R1"], neighbor_type, group)
            episodes.append({"query_id": q["query_id"], "agent_id": agent, "group": group,
                             "relation_type": q["relation_type"], "subset": subset_of[q["query_id"]],
                             "attempt": row["attempt"], "source_name_overlap": q["query_id"] in overlap, **ep})
    tables = {}
    for view in VIEWS:
        sel = [e for e in episodes if view == "all_queries" or not e["source_name_overlap"]]
        tables[view] = {g: summarize([e for e in sel if e["group"] == g], agents) for g in GROUPS}
    queries = {g: sorted({e["query_id"] for e in episodes if e["group"] == g}) for g in GROUPS}
    return {"agent_order": agents, "source_name_overlap_queries": sorted(overlap),
            "queries_with_success_episodes": {g: len(v) for g, v in queries.items()},
            "non_success_episodes_excluded": excluded, "tables": tables,
            "verdict": clean_verdict(tables["all_queries"]["treat-final"]),
            "verdict_without_source_name_overlap_descriptive":
                clean_verdict(tables["without_source_name_overlap"]["treat-final"]),
            "episodes": episodes}


# -------------------------------------------------------------------------------------------- output

SUMMARY_FIELDS = ["view", "group", "agent_id", "episodes", "opportunity", "opened", "taken",
                  "taken_and_opportunity", "taken_and_opened", "taken_outside_opportunity", "uptake",
                  "opened_per_opportunity", "taken_per_opened"]
EPISODE_FIELDS = ["query_id", "agent_id", "group", "relation_type", "subset", "attempt", "source_name_overlap",
                  "opportunity", "opened", "taken", "opportunity_nodes", "opened_nodes", "listed_nodes",
                  "off_label_answers", "reached_count"]


def _cell(v):
    if isinstance(v, list):
        return ";".join(v)
    if isinstance(v, float):
        return f"{v:.6f}"
    return "" if v is None else v


def to_csv(rows: list[dict], fields: list[str]) -> str:
    buf = io.StringIO()
    w = csv.DictWriter(buf, fieldnames=fields, lineterminator="\n")
    w.writeheader()
    for r in rows:
        w.writerow({k: _cell(r[k]) for k in fields})
    return buf.getvalue()


def summary_rows(result: dict) -> list[dict]:
    return [{"view": v, "group": g, **r} for v in VIEWS for g in GROUPS for r in result["tables"][v][g]]


def _fr(num, den) -> str:
    return f"{num / den:.3f} ({num}/{den})" if den else f"NA ({num}/{den})"


def to_markdown(result: dict, provenance: dict) -> str:
    v = result["verdict"]
    out = ["# B1 — Off-label opportunity and uptake (EXPLORATORY)\n", f"{EXPLORATORY_NOTE}\n",
           f"Produced by `scripts/40_b1_uptake.py` at commit `{provenance['git_commit']}` (tracked files clean: "
           f"{provenance['git_tracked_clean']}). Runs: " + ", ".join(
               f"`{r}`" for r in provenance["runs"]) + ". Latest attempts, SUCCESS episodes only.\n",
           f"**B1 (treat-final, all queries): {v['outcome']}** — {v['count']} of 4 agents meet the rule "
           f"({v['rule']}): {', '.join(v['agents_meeting']) or 'none'}.\n"]
    titles = {"all_queries": "All queries",
              "without_source_name_overlap": "Without SOURCE_NAME_OVERLAP queries (" +
              (", ".join(result["source_name_overlap_queries"]) or "none") + "; protocol §19.1; descriptive)"}
    n = 1
    for view in VIEWS:
        for group in GROUPS:
            role = "primary" if group == "treat-final" and view == "all_queries" else "descriptive"
            out.append(f"## Table {n} — {group}, {titles[view]} ({role})\n")
            n += 1
            out.append("| Agent | Episodes | Opportunity | Opened | Taken | Taken outside Opportunity | "
                       "Uptake = Taken∧Opp / Opp | Opened / Opp | Taken∧Opened / Opened |")
            out.append("|---|---|---|---|---|---|---|---|---|")
            for r in result["tables"][view][group]:
                out.append(f"| {r['agent_id']} | {r['episodes']} | {r['opportunity']} | {r['opened']} | "
                           f"{r['taken']} | {r['taken_outside_opportunity']} | "
                           f"{_fr(r['taken_and_opportunity'], r['opportunity'])} | "
                           f"{_fr(r['opened'], r['opportunity'])} | {_fr(r['taken_and_opened'], r['opened'])} |")
            out.append("")
    d = result["verdict_without_source_name_overlap_descriptive"]
    out.append(f"Rule applied to the view without SOURCE_NAME_OVERLAP queries (descriptive, not the outcome): "
               f"{d['outcome']} ({d['count']} of 4 agents).\n")
    out.append("Non-SUCCESS episodes excluded (latest attempts): " + "; ".join(
        f"{g}: " + ", ".join(f"{a} {sum(c.values())}" for a, c in result["non_success_episodes_excluded"][g].items())
        for g in GROUPS) + ".\n")
    out.append("Per-episode detail: `b1_episodes.csv`. Definitions: see the docstring of the script and the "
               "two decision-log entries named above.\n")
    return "\n".join(out)


def write_once(path: Path, text: str) -> None:
    B5.write_once(path, text)


def main(argv=None) -> int:
    ap = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    ap.add_argument("--combined", required=True, help="results/combined/<id> (e.g. pilot_expansion_v1)")
    ap.add_argument("--out", default="results/exploratory/b1")
    args = ap.parse_args(argv)

    frozen = yaml.safe_load((ROOT / "configs/frozen_hashes.yaml").read_text(encoding="utf-8"))
    kg_meta = ROOT / "data/cache/primekg_metadata.json"
    if sha256_file(kg_meta) != frozen["kg_fingerprint"]:
        raise ValueError(f"KG fingerprint {sha256_file(kg_meta)} != frozen {frozen['kg_fingerprint']}")
    comb_dir = ROOT / "results/combined" / args.combined
    components = json.loads((comb_dir / "components.json").read_text(encoding="utf-8"))["components"]
    manifests, manifest_inputs = {}, {}
    for run_id in sorted(components):
        name = components[run_id]["manifest"]
        rel = f"data/processed/manifests/{name}.jsonl"
        digest = sha256_file(ROOT / rel)
        if frozen["manifests"].get(rel) != digest:
            raise ValueError(f"{rel}: SHA256 {digest} != frozen {frozen['manifests'].get(rel)} (protocol §3.4)")
        manifests[name] = B5.read_manifest(ROOT / rel)
        manifest_inputs[name] = {"path": rel, "sha256": digest, "run_id": run_id}
    if set(manifests) != {"pilot", "expansion"}:
        raise ValueError(f"B1 needs exactly the pilot and expansion manifests, got {sorted(manifests)}")

    report = load_script("s28_report", "28_pilot_report.py")
    data = report.load_combined(args.combined)
    subset_of = B5.assign_subsets(data["cofailure"]["queries"], manifests)
    refs_path = ROOT / "data/processed/reference_queries.parquet"
    refs = {r["query_id"]: r for r in pq.read_table(refs_path, columns=["query_id", "s", "Type_B", "Type_T"])
            .to_pylist()}
    result = compute(data, refs, subset_of)

    commit, clean = B5.git_state()
    cof_path = comb_dir / "cofailure.json"
    provenance = {"git_commit": commit, "git_tracked_clean": clean, "combined_id": args.combined,
                  "runs": sorted(components),
                  "inputs": {"cofailure": {"path": cof_path.relative_to(ROOT).as_posix(),
                                           "sha256": sha256_file(cof_path)},
                             "reference_queries": {"path": refs_path.relative_to(ROOT).as_posix(),
                                                   "sha256": sha256_file(refs_path)},
                             "kg_fingerprint": frozen["kg_fingerprint"], "manifests": manifest_inputs}}
    out_dir = ROOT / args.out
    payload = {"stage": "B1", "status": "EXPLORATORY", "note": EXPLORATORY_NOTE, "provenance": provenance,
               **result}
    write_once(out_dir / "b1.json", json.dumps(payload, indent=2, sort_keys=True, ensure_ascii=False) + "\n")
    write_once(out_dir / "b1_table.csv", to_csv(summary_rows(result), SUMMARY_FIELDS))
    write_once(out_dir / "b1_episodes.csv", to_csv(result["episodes"], EPISODE_FIELDS))
    md = to_markdown(result, provenance)
    write_once(out_dir / "b1_report.md", md)
    print(md)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
