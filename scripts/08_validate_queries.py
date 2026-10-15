"""Generate evaluator-only S8 evidence (protocol §7.1), without deciding S9 inclusion."""

import argparse
import csv
import datetime as dt
import hashlib
import importlib.util
import json
import subprocess
import tempfile
from pathlib import Path

import pyarrow.parquet as pq

from cofail_kg.data.biohopr_loader import file_sha256, load_biohopr
from cofail_kg.evaluation.query_validation import validate_queries, summarize
from cofail_kg.evaluation.relation_mapping import validation_sample
from cofail_kg.kg.prepare import load_cache_metadata
from cofail_kg.kg.primekg_index import normalize_name
from cofail_kg.utils.frozen_hashes import read_frozen_hashes

ROOT = Path(__file__).resolve().parents[1]
FILES = ("query_validation.csv", "query_validation_summary.json")


def check_outputs(out):
    if any((out / name).exists() for name in FILES):
        raise FileExistsError("S8 outputs exist; use a new --output-dir")


def write_outputs(out, records, summary):
    check_outputs(out)
    out.mkdir(parents=True, exist_ok=True)
    with tempfile.TemporaryDirectory(prefix=".s8-", dir=out) as staging:
        stage = Path(staging)
        with (stage / FILES[0]).open("w", newline="", encoding="utf-8") as stream:
            writer = csv.DictWriter(stream, fieldnames=list(records[0]))
            writer.writeheader()
            for record in records:
                writer.writerow({k: json.dumps(v, ensure_ascii=False) if isinstance(v, list) else v
                                 for k, v in record.items()})
        summary["validation_csv_sha256"] = file_sha256(stage / FILES[0])
        (stage / FILES[1]).write_text(json.dumps(summary, indent=2, sort_keys=True) + "\n", encoding="utf-8")
        check_outputs(out)
        for name in FILES:
            (stage / name).rename(out / name)


def main(argv=None):
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--output-dir", type=Path, default=ROOT / "results/diagnostics")
    args = parser.parse_args(argv)
    check_outputs(args.output_dir)
    frozen = read_frozen_hashes(ROOT / "configs/frozen_hashes.yaml")
    spec = importlib.util.spec_from_file_location("s7", ROOT / "scripts/07_build_reference_sets.py")
    s7 = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(s7)
    mapping = s7.load_mapping(ROOT / "results/semantics/relation_mapping.json", frozen)
    previous = json.loads((ROOT / "data/processed/reference_summary.json").read_text())
    for key, frozen_key in (("biohopr_revision", "biohopr_revision"),
                            ("kg_fingerprint", "kg_fingerprint"),
                            ("relation_mapping_sha256", "relation_mapping")):
        if previous["provenance"][key] != frozen[frozen_key]:
            raise ValueError(f"S7 provenance differs from frozen {key}")
    # S7 did not hash its output tables; verify its recorded source/input hashes.
    newline_conversions = []
    for name, expected in previous["provenance"]["sha256"].items():
        if file_sha256(ROOT / name) != expected:
            data = (ROOT / name).read_bytes()
            if not name.endswith(".py") or hashlib.sha256(data.replace(b"\r\n", b"\n")).hexdigest() != expected:
                raise ValueError(f"S7 input/source changed: {name}")
            newline_conversions.append(name)
    if file_sha256(ROOT / "data/cache/primekg_metadata.json") != frozen["kg_fingerprint"]:
        raise ValueError("KG fingerprint mismatch")
    load_cache_metadata(ROOT / "data/cache")
    nodes = pq.read_table(ROOT / "data/cache/primekg_nodes.parquet").to_pylist()
    from collections import Counter, defaultdict
    counts, names = Counter(), defaultdict(list)
    for node in nodes:
        counts[node["node_type"]] += 1
        names[(normalize_name(node["node_name"]), node["node_type"])].append(str(node["node_index"]))
    def find(name, kind):
        return names.get((normalize_name(name), kind), [])
    raw = load_biohopr(ROOT / "data/raw/biohopr")
    proposal = json.loads((ROOT / "results/semantics/relation_mapping_proposed.json").read_text())
    sample_ids = set()
    for kind in sorted(mapping["per_type"]):
        sample, _ = validation_sample([r for r in raw if r["relation_hop2"] == kind], find)
        ids = [r["row_id"] for r in sample]
        if ids != proposal["per_type"][kind]["sample_row_ids"]:
            raise ValueError(f"S6 validation sample differs: {kind}")
        sample_ids.update(ids)
    with (ROOT / "results/semantics/relation_ambiguity_tags.csv").open(newline="", encoding="utf-8") as stream:
        tags = {r["relation_type"]: r["ambiguity_tag"] for r in csv.DictReader(stream)}
    queries = pq.read_table(ROOT / "data/processed/reference_queries.parquet").to_pylist()
    expected_rows = {r["row_id"] for r in raw if mapping["per_type"][r["relation_hop2"]]["d1_status"] == "PASS"}
    actual_rows = [row for q in queries for row in q["row_ids"]]
    if len(actual_rows) != len(set(actual_rows)) or set(actual_rows) != expected_rows:
        raise ValueError("S7 rows do not cover D1 PASS rows exactly once")
    records = validate_queries(queries, counts, sample_ids, tags)
    summary = summarize(records)
    paths = ["data/processed/reference_queries.parquet", "data/processed/reference_summary.json",
             "data/cache/primekg_nodes.parquet", "results/semantics/relation_mapping_proposed.json",
             "results/semantics/relation_ambiguity_tags.csv", "scripts/08_validate_queries.py",
             "src/cofail_kg/evaluation/query_validation.py", "src/cofail_kg/evaluation/relation_mapping.py"]
    summary["provenance"] = {
        "frozen_inputs": frozen, "s7_provenance": previous["provenance"],
        "run_time_utc": dt.datetime.now(dt.timezone.utc).isoformat(timespec="seconds"),
        "git_commit": subprocess.run(["git", "rev-parse", "HEAD"], cwd=ROOT,
                                     capture_output=True, text=True, check=True).stdout.strip(),
        "sha256": {name: file_sha256(ROOT / name) for name in paths},
        "target_type_node_counts": dict(sorted(counts.items())),
        "s6_sample_rows": len(sample_ids), "s9_inclusion_computed": False,
        "s7_source_crlf_to_lf_matches": newline_conversions,
    }
    write_outputs(args.output_dir, records, summary)
    print(json.dumps(summary["overall"], indent=2))
    print(f"Saved S8 evidence to {args.output_dir}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
