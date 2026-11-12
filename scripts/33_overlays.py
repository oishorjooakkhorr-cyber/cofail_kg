"""S33 (D7 DESCRIPTIVE) — Treatment overlays for the 5 illustrative cases; no controls (C = 0).

Usage (from the repository root, after scripts/31_candidates.py):
    python scripts/33_overlays.py --combined pilot_expansion_v1

Runbook S33 (DESCRIPTIVE form): for the 5 cases in the decision log of 2026-11-12 (section A), build
treatment overlays only (hide label r at node u; there are no controls, C = 0). Verify for each: a valid
route (protocol §21) remains and only the intended edges are hidden. Write results/interventions/manifest.jsonl.

Cases (decision log 2026-11-12, section A; surgery = hide label r at node u, reading of 2026-11-11):
    BH2_03356 (33618, off-label use), BH2_05290 (14052, off-label use), BH2_06016 (30800, off-label use),
    BH2_05997 (33228, off-label use), BH2_04650 (16843, drug_protein).
Each must equal the feature of that query in results/interventions/candidates.json (S31), with
candidate = True; otherwise the script stops.

Verification, per case, through the agent tools themselves (src/cofail_kg/agents/kg_env.py, S32):
1. Valid route (§21): s –r1→ b –r2→ t with r1 ∈ R1, b ∈ B_q, r2 ∈ R2, t ∈ T_q remains in the graph with the
   overlay applied (S32 `Overlay.hides`), and the bridges that keep one are listed.
2. Only the intended edges are hidden: for every checked node x and every label l at x in the unmodified
   graph, the neighbours returned with the overlay equal the unmodified neighbours minus exactly the
   expected set — N_r(u) when (x, l) = (u, r), {u} when x ∈ N_r(u) and l = r, and nothing otherwise. Checked
   nodes: u, every r-neighbour of u, s, every bridge in B_q, and the query's shared entities (S31). inspect_entity
   must agree: unchanged labels are returned unchanged, and label r disappears at x exactly when all its
   neighbours there are hidden.

Outputs:
* results/interventions/manifest.jsonl — evaluator-side: the overlay, the hidden edges (u, r, v), and the
  verification results, one line per case.
* data/agent_inputs/intervention_overlays.jsonl — agent-side overlay file read by run_episode (S32); it holds
  only {query_id, hide_labels, hide_edges}, so no evaluation field reaches agent-facing code (§9.3, §10).
* results/interventions/manifest_report.md — readable summary with provenance and file hashes.

Engineering conventions (documented, not protocol):
* Neighbour lists are compared in full (page size larger than any list), not page by page.
* Inputs are hash-checked: KG fingerprint against configs/frozen_hashes.yaml; input SHA256s recorded.
  The overlay file's SHA256 is reported for the S34 run configuration; configs/frozen_hashes.yaml is not edited.
* Outputs are write-once: an identical re-run is allowed, any difference stops the script.
"""
from __future__ import annotations

import argparse
import hashlib
import json
import subprocess
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "src"))
from cofail_kg.agents.kg_env import KGEnvironment, Overlay, ToolConfig  # noqa: E402

# Decision log 2026-11-12, section A: (query_id, u, r, mechanism).
CASES = (("BH2_03356", "33618", "off-label use", "WRONG_TURN_HOP2"),
         ("BH2_05290", "14052", "off-label use", "WRONG_TURN_HOP2"),
         ("BH2_06016", "30800", "off-label use", "WRONG_TURN_HOP2"),
         ("BH2_05997", "33228", "off-label use", "WRONG_TURN_HOP2"),
         ("BH2_04650", "16843", "drug_protein", "SHORTCUT"))
FULL = ToolConfig(page_size=10**9, budget=10**9)  # one page holds any list; budget never reached


def sha256_file(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def ids(result) -> list[str]:
    if not isinstance(result, dict):
        raise ValueError(f"tool call failed: {result}")
    if result["has_more"]:
        raise ValueError("neighbour list did not fit on one page")
    return [n["id"] for n in result["items"]]


def valid_bridges(index, ref: dict, r1, r2, overlay: Overlay | None) -> list[str]:
    """Bridges b ∈ B_q with a §21 valid route s –r1→ b –r2→ t (t ∈ T_q) left visible by the overlay."""
    s, targets, out = str(ref["s"]), {str(t) for t in ref["T_q"]}, []
    hidden = (lambda u, r, v: overlay is not None and overlay.hides(u, r, v))
    for b in sorted((str(b) for b in ref["B_q"]), key=int):
        if not any(not hidden(s, l1, b) for l1 in r1 if b in {n["id"] for n in index.neighbors(s, l1)}):
            continue
        if any(not hidden(b, l2, n["id"]) for l2 in r2 for n in index.neighbors(b, l2) if n["id"] in targets):
            out.append(b)
    return out


def expected_hidden(x: str, label: str, u: str, r: str, n_r: set[str]) -> set[str]:
    if (x, label) == (u, r):
        return set(n_r)
    if label == r and x in n_r:
        return {u}
    return set()


def check_only_intended(index, overlay: Overlay, u: str, r: str, nodes: list[str]) -> dict:
    """Compare the agent tools with and without the overlay at every checked node (see module docstring)."""
    plain = KGEnvironment(index, FULL)
    surgery = KGEnvironment(index, FULL, overlay=overlay, query_id=overlay.query_id)
    n_r = set(ids(plain.get_neighbors(u, r)))
    hidden_edges, checked = [], 0
    for x in nodes:
        before = {rel["label"]: rel for rel in plain.inspect_entity(x)["relations"]}
        after = {rel["label"]: rel for rel in surgery.inspect_entity(x)["relations"]}
        for label in sorted(before):
            want = expected_hidden(x, label, u, r, n_r)
            old = ids(plain.get_neighbors(x, label))
            new_result = surgery.get_neighbors(x, label)
            new = [] if isinstance(new_result, str) else ids(new_result)
            if isinstance(new_result, str) and set(old) != want:
                raise ValueError(f"{overlay.query_id}: {x}/{label} unexpectedly unavailable: {new_result}")
            if new != [n for n in old if n not in want] or not want <= set(old):
                raise ValueError(f"{overlay.query_id}: {x}/{label} hides {sorted(set(old) - set(new))}, "
                                 f"expected {sorted(want)}")
            if not want and after.get(label) != before[label]:
                raise ValueError(f"{overlay.query_id}: inspect_entity({x}) changed label {label}")
            if want and (label in after) != bool(new):
                raise ValueError(f"{overlay.query_id}: inspect_entity({x}) lists {label} inconsistently")
            if want and new and after[label]["neighbor_count"] != len(new):
                raise ValueError(f"{overlay.query_id}: inspect_entity({x}) count for {label} != {len(new)}")
            hidden_edges += [(x, label, v) for v in sorted(want, key=int)]
            checked += 1
        if set(after) - set(before):
            raise ValueError(f"{overlay.query_id}: inspect_entity({x}) gained labels {sorted(set(after) - set(before))}")
    from_u = sorted((e for e in hidden_edges if e[0] == u), key=lambda e: int(e[2]))
    mirrored = {(v, r, u) for _, _, v in from_u} - {(u, r, u)}
    if {e for e in hidden_edges if e[0] != u} != mirrored:
        raise ValueError(f"{overlay.query_id}: hidden edges seen from the neighbours do not mirror those at u")
    return {"hidden_edges": [list(e) for e in from_u], "hidden_edge_count": len(from_u),
            "checked_nodes": len(nodes), "checked_node_labels": checked}


def build_case(case, ref: dict, candidate: dict, index) -> tuple[dict, dict]:
    qid, u, r, mechanism = case
    if candidate.get("query_id") != qid or not candidate.get("candidate"):
        raise ValueError(f"{qid}: not a candidate in candidates.json")
    if (candidate["feature_u"], candidate["feature_r"], candidate["mechanism"]) != (u, r, mechanism):
        raise ValueError(f"{qid}: decision-log case ({u}, {r}, {mechanism}) != S31 feature "
                         f"({candidate['feature_u']}, {candidate['feature_r']}, {candidate['mechanism']})")
    r1, r2 = candidate["R1"], candidate["R2"]
    overlay = Overlay(qid, hide_labels=((u, r),))
    before = valid_bridges(index, ref, r1, r2, None)
    after = valid_bridges(index, ref, r1, r2, overlay)
    if not before:
        raise ValueError(f"{qid}: no valid route in the unmodified graph")
    if not after:
        raise ValueError(f"{qid}: no valid route remains after hiding ({u}, {r}) (§21)")
    shared = sorted({e for e in candidate["shared_entity_ids"]}, key=int)
    nodes = list(dict.fromkeys([u, *sorted({n["id"] for n in index.neighbors(u, r)}, key=int), str(ref["s"]),
                                *sorted((str(b) for b in ref["B_q"]), key=int), *shared]))
    check = check_only_intended(index, overlay, u, r, nodes)
    entry = {"query_id": qid, "arm": "treatment", "control": None, "mechanism": mechanism,
             "overlay": overlay.to_json(), "s": str(ref["s"]), "R1": r1, "R2": r2,
             "valid_bridges_before": before, "valid_bridges_after": after, "valid_route_after": True,
             **check, "only_intended_edges_hidden": True}
    return entry, overlay.to_json()


def jsonl(rows: list[dict]) -> str:
    return "".join(json.dumps(r, sort_keys=True, ensure_ascii=False) + "\n" for r in rows)


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


def to_markdown(entries: list[dict], provenance: dict) -> str:
    lines = ["# S33 — Treatment overlays (D7 DESCRIPTIVE; no controls)\n",
             f"Produced by `scripts/33_overlays.py` at commit `{provenance['git_commit']}` (tracked files clean: "
             f"{provenance['git_tracked_clean']}). Cases: decision log 2026-11-12, section A. Surgery: hide label r "
             "at node u (reading of 2026-11-11). Treatment-only (C = 0).\n",
             f"Agent-side overlay file: `{provenance['overlay_file']['path']}`, SHA256 "
             f"`{provenance['overlay_file']['sha256']}` (for the S34/S35 run configuration).\n",
             "| query_id | mechanism | hidden label at node | hidden edges | valid bridges before → after | "
             "nodes checked | node-labels checked |", "|---|---|---|---|---|---|---|"]
    for e in entries:
        (u, r), = e["overlay"]["hide_labels"]
        lines.append(f"| {e['query_id']} | {e['mechanism']} | {r} at {u} | {e['hidden_edge_count']} | "
                     f"{', '.join(e['valid_bridges_before'])} → {', '.join(e['valid_bridges_after'])} | "
                     f"{e['checked_nodes']} | {e['checked_node_labels']} |")
    lines.append("\nEvery case: a §21 valid route remains, and only the intended edges are hidden "
                 "(checked through the agent tools with and without the overlay).")
    return "\n".join(lines) + "\n"


def main(argv=None) -> int:
    import pyarrow.parquet as pq
    import yaml
    from cofail_kg.kg.primekg_index import PrimeKGIndex

    ap = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    ap.add_argument("--combined", required=True, help="results/combined/<id> (e.g. pilot_expansion_v1)")
    ap.add_argument("--out", default="results/interventions")
    ap.add_argument("--overlay-file", default="data/agent_inputs/intervention_overlays.jsonl")
    args = ap.parse_args(argv)

    frozen = yaml.safe_load((ROOT / "configs/frozen_hashes.yaml").read_text(encoding="utf-8"))
    meta = ROOT / "data/cache/primekg_metadata.json"
    if sha256_file(meta) != frozen["kg_fingerprint"]:
        raise ValueError(f"KG fingerprint {sha256_file(meta)} != frozen {frozen['kg_fingerprint']} (protocol §3.4)")
    paths = {"candidates": ROOT / args.out / "candidates.json",
             "cofailure": ROOT / "results/combined" / args.combined / "cofailure.json",
             "reference_queries": ROOT / "data/processed/reference_queries.parquet"}
    candidates = {r["query_id"]: r for r in json.loads(paths["candidates"].read_text(encoding="utf-8"))["queries"]}
    cof = {q["query_id"]: q for q in json.loads(paths["cofailure"].read_text(encoding="utf-8"))["queries"]}
    refs = {r["query_id"]: r for r in pq.read_table(paths["reference_queries"]).to_pylist()}
    index = PrimeKGIndex(ROOT / "data/cache")

    entries, overlays = [], []
    for case in CASES:
        qid = case[0]
        q = cof[qid]
        shared = {str(e["entity_id"]) for e in q["question"]["shared_entities"] if e["agent_count"] >= 3}
        cand = {**candidates[qid], "R1": q["R1"], "R2": q["R2"], "shared_entity_ids": shared}
        entry, overlay = build_case(case, refs[qid], cand, index)
        entries.append(entry)
        overlays.append(overlay)
    entries.sort(key=lambda e: e["query_id"])
    overlays.sort(key=lambda o: o["query_id"])

    overlay_path = ROOT / args.overlay_file
    write_once(overlay_path, jsonl(overlays))
    commit, clean = git_state()
    provenance = {"git_commit": commit, "git_tracked_clean": clean, "kg_fingerprint": frozen["kg_fingerprint"],
                  "inputs": {k: {"path": p.relative_to(ROOT).as_posix(), "sha256": sha256_file(p)}
                             for k, p in paths.items()},
                  "overlay_file": {"path": overlay_path.relative_to(ROOT).as_posix(),
                                   "sha256": sha256_file(overlay_path)}}
    out = ROOT / args.out
    write_once(out / "manifest.jsonl", jsonl(entries))
    md = to_markdown(entries, provenance)
    write_once(out / "manifest_provenance.json", json.dumps(provenance, indent=2, sort_keys=True) + "\n")
    write_once(out / "manifest_report.md", md)
    print(md)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
