"""Phase 2 (DESCRIPTIVE) — intervention run inputs for S34/S35: sheets, manifests and frozen hashes.

Usage (from the repository root, after scripts/33_overlays.py):
    python scripts/46_intervention_inputs.py

Decision log 2026-11-12 "Plan after D7", section A: 5 treatment-only cases (BH2_03356, BH2_05290,
BH2_06016, BH2_05997, BH2_04650); S34 smoke = BH2_05290 × 4 agents, run ID `intervention_smoke`;
S35 = the 5 cases × 4 agents, run ID `intervention_v1`. Runbook S34: connect the overlay file and its
fingerprint to the run configuration and the frozen hashes, and build the input sheet for the cases.

Writes (write-once):
* data/processed/manifests/intervention_smoke.jsonl, data/agent_inputs/intervention_smoke.jsonl (BH2_05290);
* data/processed/manifests/intervention5.jsonl, data/agent_inputs/intervention5.jsonl (the 5 cases).
  Every line is a byte copy of the original pilot/expansion line (the question is never changed, §9.3).
* configs/frozen_hashes.yaml, new write-once keys: `manifests_intervention` (the four files) and
  `intervention_overlays` (data/agent_inputs/intervention_overlays.jsonl, whose SHA256 must equal the one
  S33 recorded in results/interventions/manifest_provenance.json).

Checks: the overlay file loads (kg_env.load_overlays), covers exactly the 5 cases, each overlay equals the
one S33 recorded for its case in results/interventions/manifest.jsonl (one hidden (u, r) label, no single
edges), and S33's checks passed for it (valid route after, only intended edges hidden).

Engineering conventions (documented, not protocol): lines ordered by query_id; both sheets are built here
so that S35 only runs; separate write-once keys because `manifests` is itself write-once.
"""
from __future__ import annotations

import argparse
import hashlib
import importlib.util
import json
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "src"))
from cofail_kg.agents.kg_env import load_overlays  # noqa: E402
from cofail_kg.utils.frozen_hashes import read_frozen_hashes, write_once as write_hash_once  # noqa: E402

CASES = ("BH2_03356", "BH2_04650", "BH2_05290", "BH2_05997", "BH2_06016")   # decision log 2026-11-12, A1
SMOKE = ("BH2_05290",)                                                       # A3
SHEETS = {"intervention_smoke": SMOKE, "intervention5": CASES}
OVERLAY = "data/agent_inputs/intervention_overlays.jsonl"
SOURCES = ("pilot", "expansion")


def _load(name, filename):
    spec = importlib.util.spec_from_file_location(name, ROOT / "scripts" / filename)
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


R8 = _load("make_repeat8", "44_make_repeat8.py")


def sha256_bytes(data: bytes) -> str:
    return hashlib.sha256(data).hexdigest()


def copy_lines(query_ids, files: dict[str, dict[str, bytes]]) -> dict[str, bytes]:
    """{'manifest', 'sheet'} bytes for `query_ids` (sorted), each line copied from the one source holding it."""
    out = {}
    for kind in ("manifest", "sheet"):
        found = {}
        for source in sorted(files):
            for qid, line in R8.lines_by_query(files[source][kind], f"{source} {kind}").items():
                if qid in query_ids:
                    if qid in found:
                        raise ValueError(f"{qid} is in more than one source {kind}")
                    found[qid] = line
        missing = sorted(set(query_ids) - set(found))
        if missing:
            raise ValueError(f"{kind}: not found: {missing}")
        out[kind] = b"".join(found[q] for q in sorted(query_ids))
    return out


def check_overlays(overlays: dict, manifest_rows: list[dict]) -> None:
    """Overlay file = the S33 surgery for exactly the 5 cases (hide label r at node u)."""
    if sorted(overlays) != sorted(CASES):
        raise ValueError(f"overlay file covers {sorted(overlays)}, expected {sorted(CASES)}")
    rows = {r["query_id"]: r for r in manifest_rows}
    for qid, ov in overlays.items():
        r = rows[qid]
        if ov.to_json() != r["overlay"]:
            raise ValueError(f"{qid}: overlay {ov.to_json()} differs from the S33 manifest {r['overlay']}")
        if len(ov.hide_labels) != 1 or ov.hide_edges:
            raise ValueError(f"{qid}: expected one hidden (u, r) label and no single edges")
        if not (r["valid_route_after"] and r["only_intended_edges_hidden"]):
            raise ValueError(f"{qid}: S33 checks did not pass")


def main(argv=None) -> int:
    argparse.ArgumentParser(description=__doc__.splitlines()[0]).parse_args(argv)
    frozen_path = ROOT / "configs/frozen_hashes.yaml"
    frozen = read_frozen_hashes(frozen_path)
    files = {}
    for source in SOURCES:
        files[source] = {}
        for kind, rel in (("manifest", f"data/processed/manifests/{source}.jsonl"),
                          ("sheet", f"data/agent_inputs/{source}.jsonl")):
            data = (ROOT / rel).read_bytes()
            if sha256_bytes(data) != frozen["manifests"][rel]:
                raise ValueError(f"{rel}: SHA256 differs from configs/frozen_hashes.yaml (protocol §3.4)")
            files[source][kind] = data
    overlay_bytes = (ROOT / OVERLAY).read_bytes()
    recorded = json.loads((ROOT / "results/interventions/manifest_provenance.json").read_text(encoding="utf-8"))
    if recorded["overlay_file"] != {"path": OVERLAY, "sha256": sha256_bytes(overlay_bytes)}:
        raise ValueError(f"{OVERLAY}: SHA256 differs from the one S33 recorded")
    s33 = [json.loads(x) for x in (ROOT / "results/interventions/manifest.jsonl").read_text(
        encoding="utf-8").splitlines() if x.strip()]
    check_overlays(load_overlays(ROOT / OVERLAY), s33)
    hashes = {}
    for name, qids in SHEETS.items():
        out = copy_lines(qids, files)
        for kind, rel in (("manifest", f"data/processed/manifests/{name}.jsonl"),
                          ("sheet", f"data/agent_inputs/{name}.jsonl")):
            R8.write_bytes_once(ROOT / rel, out[kind])
            hashes[rel] = sha256_bytes(out[kind])
    written = [write_hash_once(frozen_path, "manifests_intervention", dict(sorted(hashes.items()))),
               write_hash_once(frozen_path, "intervention_overlays", {OVERLAY: sha256_bytes(overlay_bytes)})]
    print(json.dumps({"sheets": {k: list(v) for k, v in SHEETS.items()}, "hashes": hashes,
                      "overlay": {OVERLAY: sha256_bytes(overlay_bytes)}, "written": written}, indent=2))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
