"""Build evaluator-only S7 reference data (protocol §0.4, §4, §6, §12)."""

from __future__ import annotations

import argparse
import datetime as dt
import json
import subprocess
import tempfile
import time
from pathlib import Path

import pyarrow as pa
import pyarrow.parquet as pq

from cofail_kg.data.biohopr_loader import file_sha256, load_biohopr, read_metadata
from cofail_kg.evaluation.normalize import index_finder
from cofail_kg.evaluation.reference_sets import build_reference_sets, summarize
from cofail_kg.kg.primekg_index import PrimeKGIndex
from cofail_kg.utils.frozen_hashes import read_frozen_hashes

ROOT = Path(__file__).resolve().parents[1]
FILES = ("reference_queries.parquet", "reference_targets.parquet", "reference_summary.json")
STRING_FIELDS = ("query_id", "s", "Type_S", "Type_B", "Type_T", "relation_type", "construction")
LIST_FIELDS = ("row_ids", "question_texts", "query_names", "gold_bridge_names", "gold_answer_names",
               "gold_bridges", "B_q", "dead_end_bridges", "T_q", "T_q_gold_bridges", "G_q", "A_star_q")
SIZE_FIELDS = ("bq_size", "dead_end_size", "tq_size", "gold_bridge_tq_size", "gq_size", "gold_size")
QUERY_SCHEMA = pa.schema(
    [(name, pa.string()) for name in STRING_FIELDS]
    + [(name, pa.list_(pa.string())) for name in LIST_FIELDS]
    + [(name, pa.int64()) for name in SIZE_FIELDS]
    + [("unresolved_names", pa.list_(pa.struct([(name, pa.string()) for name in
                                               ("row_id", "role", "name", "status")]))),
       ("suffix_resolutions", pa.list_(pa.struct([(name, pa.string()) for name in
                                                 ("row_id", "role", "name", "node_id")])))]
)
TARGET_SCHEMA = pa.schema([(name, pa.string()) for name in ("query_id", "bridge", "target")])


def check_outputs(out):
    existing = [str(out / name) for name in FILES if (out / name).exists()]
    if existing:
        raise FileExistsError(f"S7 outputs already exist; use a new --output-dir: {existing}")


def load_mapping(path, frozen):
    """Reject changed, proposed or stale S6 mappings before graph computation (§3.4, §5)."""
    if file_sha256(path) != frozen.get("relation_mapping"):
        raise ValueError("S6 relation mapping hash does not match frozen hash")
    value = json.loads(path.read_text(encoding="utf-8"))
    if value.get("frozen") is not True or value["d1"]["outcome"] != "PROCEED":
        raise ValueError("S7 requires a frozen mapping with D1 PROCEED")
    for key in ("biohopr_revision", "kg_fingerprint"):
        if value["provenance"][key] != frozen.get(key):
            raise ValueError(f"S6 mapping {key} differs from frozen inputs")
    return value


def write_outputs(out, queries, targets, provenance):
    """Stage complete typed Parquet tables before publishing; never overwrite an artifact."""
    check_outputs(out)
    summary = {**summarize(queries, targets), "provenance": provenance}
    out.mkdir(parents=True, exist_ok=True)
    with tempfile.TemporaryDirectory(prefix=".s7-", dir=out) as staging:
        stage = Path(staging)
        pq.write_table(pa.Table.from_pylist(queries, schema=QUERY_SCHEMA), stage / FILES[0])
        pq.write_table(pa.Table.from_pylist(targets, schema=TARGET_SCHEMA), stage / FILES[1])
        (stage / FILES[2]).write_text(json.dumps(summary, indent=2, sort_keys=True) + "\n", encoding="utf-8")
        check_outputs(out)
        for name in FILES:
            (stage / name).rename(out / name)
    return summary


def main(argv=None):
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--output-dir", type=Path, default=ROOT / "data/processed")
    args = parser.parse_args(argv)
    check_outputs(args.output_dir)
    started = time.perf_counter()
    frozen = read_frozen_hashes(ROOT / "configs/frozen_hashes.yaml")
    path = ROOT / "results/semantics/relation_mapping.json"
    mapping = load_mapping(path, frozen)
    revision = read_metadata(ROOT / "data/raw/biohopr")["revision"]
    fingerprint = file_sha256(ROOT / "data/cache/primekg_metadata.json")
    if revision != frozen["biohopr_revision"] or fingerprint != frozen["kg_fingerprint"]:
        raise ValueError("S7 inputs differ from frozen BioHopR revision / KG fingerprint")
    rows = load_biohopr(ROOT / "data/raw/biohopr")
    if set(mapping["per_type"]) != {r["relation_hop2"] for r in rows}:
        raise ValueError("BioHopR relation types differ from frozen mapping")
    print("Verified frozen inputs; loading PrimeKG.", flush=True)
    kg = PrimeKGIndex(ROOT / "data/cache")
    if kg.convention.mode != "either":
        raise ValueError("S7 requires the frozen either-direction edge convention")
    print("Building reference queries and targets.", flush=True)
    queries, targets = build_reference_sets(rows, mapping["per_type"], index_finder(kg), kg.neighbors_by_label)
    source_files = ["scripts/07_build_reference_sets.py", "src/cofail_kg/evaluation/reference_sets.py",
                    "src/cofail_kg/evaluation/normalize.py", "src/cofail_kg/kg/primekg_index.py",
                    "src/cofail_kg/data/biohopr_loader.py", "src/cofail_kg/data/field_roles.py",
                    "src/cofail_kg/data/diagnostics.py", "src/cofail_kg/kg/prepare.py",
                    "src/cofail_kg/utils/frozen_hashes.py", "requirements.lock",
                    "docs/frozen_pilot_protocol.md", "docs/decision_rules.md",
                    "configs/frozen_hashes.yaml", "results/semantics/relation_mapping.json",
                    "data/raw/biohopr/metadata.json", "data/raw/biohopr/BioHopR.json"]
    commit = subprocess.run(["git", "-c", f"safe.directory={ROOT.as_posix()}", "rev-parse", "HEAD"],
                            cwd=ROOT, text=True, capture_output=True, check=True).stdout.strip()
    provenance = {
        "biohopr_revision": revision, "kg_fingerprint": fingerprint,
        "relation_mapping_sha256": frozen["relation_mapping"], "protocol_version": "1.3.3",
        "git_commit": commit, "run_time_utc": dt.datetime.now(dt.timezone.utc).isoformat(timespec="seconds"),
        "elapsed_seconds": round(time.perf_counter() - started, 3),
        "input_dataset_rows": len(rows), "excluded_dataset_rows": len(rows) - sum(len(q["row_ids"]) for q in queries),
        "sha256": {p: file_sha256(ROOT / p) for p in sorted(source_files)},
    }
    summary = write_outputs(args.output_dir, queries, targets, provenance)
    print(json.dumps({k: v for k, v in summary.items() if k != "provenance"}, indent=2))
    print(f"Saved S7 outputs to {args.output_dir} in {time.perf_counter() - started:.1f}s", flush=True)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
