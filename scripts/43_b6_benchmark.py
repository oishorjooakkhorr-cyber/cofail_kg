"""Phase J B6 — Benchmark vs graph labels (EXPLORATORY).

Usage (from the repository root, after scripts/30_combined_analysis.py):
    python scripts/43_b6_benchmark.py --combined pilot_expansion_v1

Rule (docs/decision_log.md, entry 2026-11-12 "Plan after D7", section B6):
  CF3^BH vs CF3^Q by relation type; BH-only queries = CF3^BH = 1 and CF3^Q = 0. Hand-check: 15 BH-only
  queries, the first 15 by SHA256("42" + query_id) ascending; for each, the shared entity with the smallest
  node ID. Claude Code prints its graph path(s) s –r1→ b –r2→ t with r1 ∈ R1, r2 ∈ R2, and the BioHopR gold
  list; the researcher marks each VALID / QUESTIONABLE / NOT_VALID in results/exploratory/b6_handcheck.csv.

Path conflict (reported): the runbook prompt names results/exploratory/b6/b6_handcheck.csv; the entry
names results/exploratory/b6_handcheck.csv. Part 10b: the entry wins, so the hand-check file is written at
the entry's path. The table goes to results/exploratory/b6/ (runbook: outputs in results/exploratory/<stage>/).

Quantities are read, never recomputed, from results/combined/<id>/cofailure.json:
  CF3^Q = question.cf3 (protocol §16.1), CF3^BH = benchmark.cf3 (protocol §16.2: W^BH_iq = resolved answers ∖
  A*_q). The "shared entity" of a BH-only query is an entry of benchmark.shared_entities (an entity in W^BH
  for ≥ 3 agents, as stored by the frozen §16 code).
Graph paths: every (r1, b, r2) with r1 ∈ R1, r2 ∈ R2, an edge (s, r1, b) and an edge (b, r2, t), with
  type(b) = Type_B and b ≠ s (the bridge conditions of protocol §6), edges traversed in either direction (S4
  edge convention). Paths are not truncated. The set of bridges found must equal the bridges b with
  t ∈ T_q(b) in data/processed/reference_targets.parquet when t ∈ T_q; otherwise the script stops.
BioHopR gold list: gold_answer_names of the query in data/processed/reference_queries.parquet (the BioHopR
  answer names; A*_q is their resolution, protocol §4).

Protocol §19.1: every co-failure metric is reported on all queries and again with SOURCE_NAME_OVERLAP queries
excluded. The table is written for both views. The hand-check is drawn from all queries; a
SOURCE_NAME_OVERLAP query, if drawn, is flagged in its row.

Engineering conventions (documented, not protocol):
* SHA256 order: lowercase hex digest of the UTF-8 string "42" + query_id, ascending (as §3.1/§8 code does).
* If fewer than 15 BH-only queries exist, all are listed.
* Table columns add the full 2×2 split (both, BH-only, Q-only) beside CF3^BH and CF3^Q.
* Hand-check context columns (question text, names, holders, gold-bridge tag on paths, T_q membership)
  are added to make the manual mark possible; they change no quantity.
* Inputs are hash-checked: manifests not needed; KG fingerprint (SHA256 of data/cache/primekg_metadata.json)
  must equal configs/frozen_hashes.yaml; input file SHA256s are recorded.
* Outputs are write-once: an existing output is never overwritten (an identical re-run is allowed). The
  hand-check CSV is the researcher's file once marked; the script will refuse to replace it.
"""
from __future__ import annotations

import argparse
import csv
import hashlib
import io
import json
import subprocess
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
HANDCHECK_N = 15
MARKS = ("VALID", "QUESTIONABLE", "NOT_VALID")
VIEWS = ("all_queries", "without_source_name_overlap")
EXPLORATORY_NOTE = ("EXPLORATORY (protocol §20) — docs/decision_log.md, entry 2026-11-12 \"Plan after D7\", "
                    "section B6.")


# ------------------------------------------------------------------------------------------- helpers

def sha256_file(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def order_key(query_id: str) -> str:
    """SHA256("42" + query_id), lowercase hex digest (ascending order = selection order)."""
    return hashlib.sha256(("42" + query_id).encode("utf-8")).hexdigest()


def bh_only(q: dict) -> bool:
    return bool(q["benchmark"]["cf3"]) and not q["question"]["cf3"]


# --------------------------------------------------------------------------------------------- table

def tabulate(queries: list[dict], exclude: set[str]) -> list[dict]:
    """One row per relation type (sorted) plus a total row."""
    sel = [q for q in queries if q["query_id"] not in exclude]
    rows = []
    for rel in sorted({q["relation_type"] for q in sel}) + ["total"]:
        group = [q for q in sel if rel == "total" or q["relation_type"] == rel]
        bh = [bool(q["benchmark"]["cf3"]) for q in group]
        qv = [bool(q["question"]["cf3"]) for q in group]
        rows.append({
            "relation_type": rel, "queries": len(group),
            "CF3^BH": sum(bh), "CF3^Q": sum(qv),
            "both": sum(b and v for b, v in zip(bh, qv)),
            "BH-only": sum(b and not v for b, v in zip(bh, qv)),
            "Q-only": sum(v and not b for b, v in zip(bh, qv)),
        })
    return rows


# ----------------------------------------------------------------------------------------- hand-check

def select_handcheck(queries: list[dict], n: int = HANDCHECK_N) -> list[dict]:
    """The first n BH-only queries (all queries) by SHA256("42" + query_id) ascending."""
    pool = sorted((q for q in queries if bh_only(q)), key=lambda q: (order_key(q["query_id"]), q["query_id"]))
    return pool[:n]


def chosen_entity(q: dict) -> dict:
    """The benchmark shared entity (W^BH for ≥ 3 agents) with the smallest numeric node ID."""
    shared = [e for e in q["benchmark"]["shared_entities"] if e["agent_count"] >= 3]
    if not shared:
        raise ValueError(f"{q['query_id']}: CF3^BH = 1 but no benchmark shared entity with ≥ 3 agents")
    return min(shared, key=lambda e: int(e["entity_id"]))


def graph_paths(kg, s: str, t: str, r1_labels, r2_labels, type_b: str) -> list[tuple[str, str, str]]:
    """Every (r1, b, r2): edge (s, r1, b), edge (b, r2, t), type(b) = Type_B, b ≠ s; either direction (S4).

    Sorted by numeric b, then r1, then r2. Not truncated.
    """
    out = []
    for r1 in sorted(r1_labels):
        hop1 = {n["id"] for n in kg.neighbors(s, r1, neighbor_type=type_b)} - {str(s)}
        for r2 in sorted(r2_labels):
            hop2 = {n["id"] for n in kg.neighbors(t, r2, neighbor_type=type_b)}
            out += [(r1, b, r2) for b in hop1 & hop2]
    return sorted(out, key=lambda p: (int(p[1]), p[0], p[2]))


def handcheck_row(q: dict, ref: dict, targets_by_bridge: dict[str, list[str]], kg, overlap: set[str]) -> dict:
    qid = q["query_id"]
    ent = chosen_entity(q)
    t, s = str(ent["entity_id"]), str(ref["s"])
    if s != str(q["s"]):
        raise ValueError(f"{qid}: s = {q['s']} in cofailure.json but {s} in reference_queries")
    texts = sorted(set(ref["question_texts"]))
    if len(texts) != 1:
        raise ValueError(f"{qid}: question text not identical across rows (§7.1): {texts}")
    paths = graph_paths(kg, s, t, q["R1"], q["R2"], ref["Type_B"])
    in_tq = t in {str(x) for x in ref["T_q"]}
    ref_bridges = sorted((b for b, ts in targets_by_bridge.items() if t in ts), key=int)
    path_bridges = sorted({b for _, b, _ in paths}, key=int)
    if in_tq and path_bridges != ref_bridges:
        raise ValueError(f"{qid}: entity {t} bridges from the graph {path_bridges} != reference_targets {ref_bridges}")
    if not in_tq and ref_bridges:
        raise ValueError(f"{qid}: entity {t} not in T_q but reference_targets lists bridges {ref_bridges}")
    gold_bridges = {str(b) for b in ref["gold_bridges"]}
    name = lambda n: kg.get_node(n)["name"]
    shown = [f"{name(s)} [{s}] -{r1}-> {name(b)} [{b}]{' (gold bridge)' if b in gold_bridges else ''} "
             f"-{r2}-> {name(t)} [{t}]" for r1, b, r2 in paths]
    return {
        "order": "", "query_id": qid, "sha256_42_query_id": order_key(qid),
        "relation_type": q["relation_type"], "question_text": texts[0],
        "source_name_overlap": qid in overlap,
        "s_id": s, "s_name": name(s),
        "entity_id": t, "entity_name": name(t),
        "holders": ent["agent_count"], "holder_agents": ";".join(ent["agents"]),
        "entity_in_T_q": in_tq,
        "n_graph_paths": len(paths), "graph_paths": " | ".join(shown) if shown else "NO_PATH",
        "biohopr_gold_size": len(ref["gold_answer_names"]),
        "biohopr_gold_list": "; ".join(ref["gold_answer_names"]),
        "mark": "",
    }


def build_handcheck(queries, refs, targets, kg, overlap) -> list[dict]:
    rows = []
    for i, q in enumerate(select_handcheck(queries), 1):
        row = handcheck_row(q, refs[q["query_id"]], targets.get(q["query_id"], {}), kg, overlap)
        row["order"] = i
        rows.append(row)
    return rows


# -------------------------------------------------------------------------------------------- output

HANDCHECK_FIELDS = ["order", "query_id", "sha256_42_query_id", "relation_type", "question_text",
                    "source_name_overlap", "s_id", "s_name", "entity_id", "entity_name", "holders",
                    "holder_agents", "entity_in_T_q", "n_graph_paths", "graph_paths", "biohopr_gold_size",
                    "biohopr_gold_list", "mark"]
TABLE_FIELDS = ["view", "relation_type", "queries", "CF3^BH", "CF3^Q", "both", "BH-only", "Q-only"]


def csv_text(fields: list[str], rows: list[dict]) -> str:
    buf = io.StringIO()
    w = csv.DictWriter(buf, fieldnames=fields, lineterminator="\n")
    w.writeheader()
    w.writerows(rows)
    return buf.getvalue()


def _md_table(header, rows) -> str:
    esc = lambda c: str(c).replace("|", "\\|")
    lines = ["| " + " | ".join(header) + " |", "|" + "---|" * len(header)]
    return "\n".join(lines + ["| " + " | ".join(esc(c) for c in r) + " |" for r in rows]) + "\n"


def to_markdown(tables: dict, handcheck: list[dict], overlap: list[str], provenance: dict, n_bh_only: int) -> str:
    out = ["# B6 — Benchmark vs graph labels (EXPLORATORY)\n", f"{EXPLORATORY_NOTE}\n",
           f"Produced by `scripts/43_b6_benchmark.py` at commit `{provenance['git_commit']}` (tracked files "
           f"clean: {provenance['git_tracked_clean']}). Input: `{provenance['inputs']['cofailure']['path']}` "
           f"(SHA256 `{provenance['inputs']['cofailure']['sha256']}`).\n",
           "CF3^Q: protocol §16.1. CF3^BH: protocol §16.2. BH-only = CF3^BH = 1 and CF3^Q = 0; Q-only = CF3^Q = 1 "
           "and CF3^BH = 0.\n"]
    titles = {"all_queries": "All queries", "without_source_name_overlap":
              "Without SOURCE_NAME_OVERLAP queries (" + ", ".join(overlap) + "; protocol §19.1)"}
    for i, view in enumerate(VIEWS, 1):
        out.append(f"## Table {i} — {titles[view]}\n")
        out.append(_md_table(TABLE_FIELDS[1:], [[r[k] for k in TABLE_FIELDS[1:]] for r in tables[view]]))
    out.append(f"## Hand-check — {len(handcheck)} of {n_bh_only} BH-only queries (all queries)\n")
    out.append(f"Selection: first {HANDCHECK_N} BH-only queries by SHA256(\"42\" + query_id) ascending; entity = the "
               "benchmark shared entity with the smallest node ID. The researcher's marks (VALID / QUESTIONABLE / "
               f"NOT_VALID) go in the `mark` column of `{provenance['handcheck_path']}`.\n")
    for r in handcheck:
        out.append(f"### {r['order']}. {r['query_id']} — {r['relation_type']}"
                   f"{' — SOURCE_NAME_OVERLAP' if r['source_name_overlap'] else ''}\n")
        out.append(f"- Question: {r['question_text']}")
        out.append(f"- Entity: {r['entity_name']} [{r['entity_id']}] — held by {r['holders']} agents "
                   f"({r['holder_agents'].replace(';', ', ')}); in T_q: {r['entity_in_T_q']}")
        out.append(f"- Graph paths ({r['n_graph_paths']}):")
        out += [f"  - {p}" for p in (r["graph_paths"].split(" | ") if r["n_graph_paths"] else ["NO_PATH"])]
        out.append(f"- BioHopR gold list ({r['biohopr_gold_size']}): {r['biohopr_gold_list']}\n")
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


def load_references():
    import pyarrow.parquet as pq
    refs = {r["query_id"]: r for r in pq.read_table(ROOT / "data/processed/reference_queries.parquet").to_pylist()}
    targets: dict[str, dict[str, list[str]]] = {}
    for row in pq.read_table(ROOT / "data/processed/reference_targets.parquet").to_pylist():
        targets.setdefault(row["query_id"], {}).setdefault(str(row["bridge"]), []).append(str(row["target"]))
    return refs, targets


def main(argv=None) -> int:
    import yaml
    sys.path.insert(0, str(ROOT / "src"))
    from cofail_kg.kg.primekg_index import PrimeKGIndex

    ap = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    ap.add_argument("--combined", required=True, help="results/combined/<id> (e.g. pilot_expansion_v1)")
    ap.add_argument("--out", default="results/exploratory/b6")
    ap.add_argument("--handcheck", default="results/exploratory/b6_handcheck.csv",
                    help="decision log 2026-11-12 B6 path (the entry wins over the runbook prompt)")
    args = ap.parse_args(argv)

    frozen = yaml.safe_load((ROOT / "configs/frozen_hashes.yaml").read_text(encoding="utf-8"))
    meta = ROOT / "data/cache/primekg_metadata.json"
    if sha256_file(meta) != frozen["kg_fingerprint"]:
        raise ValueError(f"KG fingerprint {sha256_file(meta)} != frozen {frozen['kg_fingerprint']} (protocol §3.4)")
    cof_path = ROOT / "results/combined" / args.combined / "cofailure.json"
    cofailure = json.loads(cof_path.read_text(encoding="utf-8"))
    queries = sorted(cofailure["queries"], key=lambda q: q["query_id"])
    overlap = set(cofailure["source_name_overlap_queries"])
    if overlap - {q["query_id"] for q in queries}:
        raise ValueError(f"SOURCE_NAME_OVERLAP queries not in the query set: {sorted(overlap)}")

    refs, targets = load_references()
    kg = PrimeKGIndex(ROOT / "data/cache")
    tables = {"all_queries": tabulate(queries, set()), "without_source_name_overlap": tabulate(queries, overlap)}
    handcheck = build_handcheck(queries, refs, targets, kg, overlap)
    n_bh_only = sum(bh_only(q) for q in queries)

    commit, clean = git_state()
    inputs = {"cofailure": {"path": cof_path.relative_to(ROOT).as_posix(), "sha256": sha256_file(cof_path)}}
    for rel in ("data/processed/reference_queries.parquet", "data/processed/reference_targets.parquet"):
        inputs[Path(rel).stem] = {"path": rel, "sha256": sha256_file(ROOT / rel)}
    inputs["kg_fingerprint"] = frozen["kg_fingerprint"]
    hc_path = Path(args.handcheck)
    provenance = {"git_commit": commit, "git_tracked_clean": clean, "combined_id": args.combined,
                  "inputs": inputs, "handcheck_path": hc_path.as_posix()}

    out_dir = ROOT / args.out
    payload = {"stage": "B6", "status": "EXPLORATORY", "note": EXPLORATORY_NOTE, "provenance": provenance,
               "source_name_overlap_queries": sorted(overlap), "bh_only_queries": n_bh_only,
               "bh_only_query_ids": [q["query_id"] for q in queries if bh_only(q)],
               "tables": tables, "handcheck": handcheck, "marks_allowed": list(MARKS)}
    write_once(out_dir / "b6.json", json.dumps(payload, indent=2, sort_keys=True, ensure_ascii=False) + "\n")
    write_once(out_dir / "b6_table.csv",
               csv_text(TABLE_FIELDS, [{"view": v, **r} for v in VIEWS for r in tables[v]]))
    md = to_markdown(tables, handcheck, sorted(overlap), provenance, n_bh_only)
    write_once(out_dir / "b6_report.md", md)
    write_once(hc_path if hc_path.is_absolute() else ROOT / hc_path, csv_text(HANDCHECK_FIELDS, handcheck))
    print(md)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
