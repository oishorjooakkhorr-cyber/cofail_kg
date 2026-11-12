"""S31 — Intervention candidates (protocol §21), listed in full; no case is selected here.

Usage (from the repository root, after scripts/30_candidates_c.py):
    python scripts/31_candidates.py --combined pilot_expansion_v1

Runbook S31: using only the frozen 500-query analysis, list every query meeting the protocol §21 candidate
rule (frozen at S29). For each: shared entity, the shared feature chosen by the §21 rule, its mechanism
(SHORTCUT / WRONG_TURN_HOP1 / WRONG_TURN_HOP2 / OFF_PATH_NODE), whether a valid route (§21) remains after
blocking it, and up to 3 matched-control candidates by the §21 matching rule. Do not select cases; list all.
Under D7 DESCRIPTIVE (decision log 2026-11-12) all 8 flagged queries are listed; the control columns show
none (C = 0). The 5 illustrative cases are chosen in the decision log, not here.

Inputs (all pushed, no raw episode record is read):
* results/combined/<id>/cofailure.json — the frozen §16 co-failure analysis (flags, PCF cases, shared
  entities).
* results/combined/<id>/d7_C.json — the S30 §21 evaluation by scripts/30_candidates_c.py under the
  researcher's §21 reading (decision log 2026-11-11). Its control columns depend on which (node, label)
  pairs agents opened in the raw records; they are carried over, not recomputed.
* data/processed/reference_queries.parquet, data/processed/primary_population.csv and the PrimeKG cache.

What is recomputed here from those inputs and must equal d7_C.json (the script stops otherwise): the flagged
set, the feature (scripts/30_candidates_c.py choose_feature), the treatment branch degree, the number of
control slots (control_slots; graph only), and whether a valid route remains after hiding the feature (§21:
s –r1→ b –r2→ t, r1 ∈ R1, b ∈ B_q, r2 ∈ R2, t ∈ T_q). Surgery = hide label r at node u (decision log
2026-11-11, reading 4).

Engineering conventions (documented, not protocol):
* "Shared entity" is reported at two levels: W^Q entities held by ≥ 3 agents (CF3^Q, §16.1) and the H1
  subset (CF3^{Q,H1}). Nothing is chosen between them.
* valid_bridges_after_block counts the bridges b ∈ B_q that still carry a valid route once the feature is
  hidden (context for S33; not a §21 quantity).
* Inputs are hash-checked: the KG fingerprint (SHA256 of data/cache/primekg_metadata.json) must equal
  configs/frozen_hashes.yaml; every input file's SHA256 is recorded.
* Outputs are write-once: an identical re-run is allowed, any difference stops the script.
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

ROOT = Path(__file__).resolve().parents[1]
MAX_CONTROLS = 3  # runbook S31: "up to 3 matched-control candidates"
FIELDS = ["query_id", "relation_type", "ambiguity_tag", "status", "source_name_overlap", "cf3_q", "cf3_h1",
          "s_id", "s_name", "shared_entities_q", "shared_entities_h1", "mechanism", "feature_u",
          "feature_u_name", "feature_r", "feature_holders", "feature_agents", "feature_step",
          "treatment_branch_degree", "valid_route_after_block", "valid_bridges_after_block", "candidate",
          "reason", "control_slots", "slots_opened_by_an_agent", "eligible_controls", "control_1",
          "control_2", "control_3", "has_matched_control"]


def load_script(name: str, filename: str):
    spec = importlib.util.spec_from_file_location(name, ROOT / "scripts" / filename)
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


C30 = load_script("candidates_c", "30_candidates_c.py")


def sha256_file(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def flagged(queries: list[dict]) -> list[dict]:
    """The queries scripts/30_candidates_c.py evaluates: CF3^{Q,H1} = 1 or a PCF event shared by ≥ 3 agents."""
    out = [q for q in sorted(queries, key=lambda q: q["query_id"])
           if q["hop1_clean"]["cf3"] or q["pcf_rel3"] or q["pcf_node3"] or q["pcf_shortcut3"]]
    if any(q["pcf_node3"] for q in out):
        raise NotImplementedError("PCF_NODE3 candidates (OFF_PATH_NODE) need a node-level surgery rule")
    return out


def valid_bridges(g, ref: dict, r1, r2, block) -> list[str]:
    """Bridges b ∈ B_q that carry a §21 valid route with `block` hidden (numeric order)."""
    s, targets, out = ref["s"], set(ref["T_q"]), []
    for b in sorted(ref["B_q"], key=int):
        if not any(b in g.neighbors(s, l1) and not C30.hidden(s, b, l1, block) for l1 in r1):
            continue
        if any(t for l2 in r2 for t in g.neighbors(b, l2) & targets if not C30.hidden(b, t, l2, block)):
            out.append(b)
    return out


def entities(block: dict, name) -> str:
    """'id name (k agents)' for every shared entity held by ≥ 3 agents, numeric order."""
    shared = sorted((e for e in block["shared_entities"] if e["agent_count"] >= 3), key=lambda e: int(e["entity_id"]))
    return "; ".join(f"{e['entity_id']} {name(e['entity_id'])} ({e['agent_count']})" for e in shared)


def build_row(q: dict, ref: dict, status: str, d7: dict, g, overlap: set[str], name) -> dict:
    qid = q["query_id"]
    if d7["query_id"] != qid or str(ref["s"]) != str(q["s"]):
        raise ValueError(f"{qid}: d7_C.json / reference_queries do not match cofailure.json")
    base = {"query_id": qid, "relation_type": q["relation_type"], "ambiguity_tag": q["ambiguity_tag"],
            "status": status, "source_name_overlap": qid in overlap, "cf3_q": int(q["question"]["cf3"]),
            "cf3_h1": int(q["hop1_clean"]["cf3"]), "s_id": str(q["s"]), "s_name": name(str(q["s"])),
            "shared_entities_q": entities(q["question"], name),
            "shared_entities_h1": entities(q["hop1_clean"], name)}
    if status != d7["status"]:
        raise ValueError(f"{qid}: status {status} but d7_C.json has {d7['status']}")
    feature = C30.choose_feature(q) if status == "CONSISTENT" else None
    if (feature or None) != d7.get("feature"):
        raise ValueError(f"{qid}: recomputed feature {feature} != d7_C.json {d7.get('feature')}")
    empty = {k: "" for k in FIELDS if k not in base}
    if feature is None:
        return {**base, **empty, "candidate": False, "reason": d7["reason"], "has_matched_control": False}
    r1, r2 = q["R1"], q["R2"]
    block = (feature["u"], feature["r"])
    if not valid_bridges(g, ref, r1, r2, None):
        raise ValueError(f"{qid}: no valid route even in the unmodified graph")
    after = valid_bridges(g, ref, r1, r2, block)
    if bool(after) != C30.valid_route_remains(g, ref, r1, r2, block) or bool(after) != d7["candidate"]:
        raise ValueError(f"{qid}: valid route after block ({bool(after)}) disagrees with d7_C.json")
    ctl = d7.get("controls") or {}
    bd = g.branch_degree(*block)
    slots = C30.control_slots(g, ref, feature, r1)
    if after and (bd != ctl["treatment_branch_degree"] or len(slots) != ctl["slots"]):
        raise ValueError(f"{qid}: branch degree / slots ({bd}, {len(slots)}) disagree with d7_C.json")
    controls = [f"({c['node']} {name(c['node'])}, {c['label']}) bd={c['branch_degree']}"
                for c in ctl.get("closest", [])[:MAX_CONTROLS]]
    controls += [""] * (MAX_CONTROLS - len(controls))
    return {**base, "mechanism": feature["mechanism"], "feature_u": feature["u"],
            "feature_u_name": name(feature["u"]), "feature_r": feature["r"],
            "feature_holders": feature["agent_count"], "feature_agents": ";".join(feature["agents"]),
            "feature_step": feature["earliest_step"], "treatment_branch_degree": bd,
            "valid_route_after_block": bool(after), "valid_bridges_after_block": len(after),
            "candidate": bool(after), "reason": d7.get("reason", ""),
            "control_slots": ctl.get("slots", ""), "slots_opened_by_an_agent": ctl.get("slots_opened_by_an_agent", ""),
            "eligible_controls": ctl.get("eligible", ""), "control_1": controls[0], "control_2": controls[1],
            "control_3": controls[2], "has_matched_control": bool(d7.get("has_matched_control"))}


def csv_text(rows: list[dict]) -> str:
    buf = io.StringIO()
    w = csv.DictWriter(buf, fieldnames=FIELDS, lineterminator="\n")
    w.writeheader()
    w.writerows(rows)
    return buf.getvalue()


def to_markdown(rows: list[dict], provenance: dict) -> str:
    esc = lambda c: str(c).replace("|", "\\|")
    cols = ["query_id", "relation_type", "mechanism", "feature_u", "feature_u_name", "feature_r",
            "feature_holders", "treatment_branch_degree", "valid_route_after_block", "candidate",
            "control_slots", "slots_opened_by_an_agent", "eligible_controls", "has_matched_control"]
    lines = ["# S31 — Intervention candidates (protocol §21)\n",
             f"Produced by `scripts/31_candidates.py` at commit `{provenance['git_commit']}` (tracked files clean: "
             f"{provenance['git_tracked_clean']}). All flagged queries are listed; no case is selected here "
             "(the 5 illustrative cases are in the decision log, 2026-11-12, section A).\n",
             f"Candidates: {sum(r['candidate'] for r in rows)} of {len(rows)} flagged queries. "
             f"With a matched control (C): {sum(r['has_matched_control'] for r in rows)}.\n",
             "| " + " | ".join(cols) + " |", "|" + "---|" * len(cols)]
    lines += ["| " + " | ".join(esc(r[c]) for c in cols) + " |" for r in rows]
    lines.append("\n## Shared entities (held by ≥ 3 agents)\n")
    for r in rows:
        lines.append(f"- **{r['query_id']}** (s = {r['s_name']} [{r['s_id']}]"
                     f"{', SOURCE_NAME_OVERLAP' if r['source_name_overlap'] else ''}): "
                     f"W^Q: {r['shared_entities_q'] or 'none'}. H1: {r['shared_entities_h1'] or 'none'}.")
    return "\n".join(lines) + "\n"


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
    import pyarrow.parquet as pq
    import yaml
    sys.path.insert(0, str(ROOT / "src"))
    from cofail_kg.kg.primekg_index import PrimeKGIndex

    ap = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    ap.add_argument("--combined", required=True, help="results/combined/<id> (e.g. pilot_expansion_v1)")
    ap.add_argument("--out", default="results/interventions")
    args = ap.parse_args(argv)

    frozen = yaml.safe_load((ROOT / "configs/frozen_hashes.yaml").read_text(encoding="utf-8"))
    meta = ROOT / "data/cache/primekg_metadata.json"
    if sha256_file(meta) != frozen["kg_fingerprint"]:
        raise ValueError(f"KG fingerprint {sha256_file(meta)} != frozen {frozen['kg_fingerprint']} (protocol §3.4)")
    folder = ROOT / "results/combined" / args.combined
    paths = {"cofailure": folder / "cofailure.json", "d7_C": folder / "d7_C.json",
             "reference_queries": ROOT / "data/processed/reference_queries.parquet",
             "primary_population": ROOT / "data/processed/primary_population.csv"}
    cofailure = json.loads(paths["cofailure"].read_text(encoding="utf-8"))
    d7 = {r["query_id"]: r for r in json.loads(paths["d7_C"].read_text(encoding="utf-8"))["queries"]}
    refs = {r["query_id"]: r for r in pq.read_table(paths["reference_queries"]).to_pylist()}
    with paths["primary_population"].open(encoding="utf-8", newline="") as h:
        status = {r["query_id"]: r["status"] for r in csv.DictReader(h)}
    overlap = set(cofailure["source_name_overlap_queries"])

    queries = flagged(cofailure["queries"])
    if [q["query_id"] for q in queries] != sorted(d7):
        raise ValueError(f"flagged queries {[q['query_id'] for q in queries]} != d7_C.json {sorted(d7)}")
    kg = PrimeKGIndex(ROOT / "data/cache")
    g = C30.Graph(kg)
    name = lambda n: kg.get_node(str(n))["name"]
    rows = [build_row(q, refs[q["query_id"]], status[q["query_id"]], d7[q["query_id"]], g, overlap, name)
            for q in queries]

    commit, clean = git_state()
    provenance = {"git_commit": commit, "git_tracked_clean": clean, "combined_id": args.combined,
                  "kg_fingerprint": frozen["kg_fingerprint"],
                  "inputs": {k: {"path": p.relative_to(ROOT).as_posix(), "sha256": sha256_file(p)}
                             for k, p in paths.items()}}
    out = ROOT / args.out
    payload = {"stage": "S31", "provenance": provenance, "flagged_queries": len(rows),
               "candidates": sum(r["candidate"] for r in rows), "C": sum(r["has_matched_control"] for r in rows),
               "queries": rows}
    write_once(out / "candidates.json", json.dumps(payload, indent=2, sort_keys=True, ensure_ascii=False) + "\n")
    write_once(out / "candidates.csv", csv_text(rows))
    md = to_markdown(rows, provenance)
    write_once(out / "candidates_report.md", md)
    print(md)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
