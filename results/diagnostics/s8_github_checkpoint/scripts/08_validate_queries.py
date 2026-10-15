"""S8 evaluator-only query validation (protocol §7.1; decision rules D2 step 1 input).

Reads the S7 outputs in data/processed/, the frozen S6 mapping and its hash-linked proposal
(validation-sample row IDs, ambiguity tags), and the fingerprinted PrimeKG node cache (node
names, Type_T node counts). Writes query_validation.csv and query_validation_summary.json.
Nothing is excluded and no saturation threshold is chosen.
"""

from __future__ import annotations

import argparse
import csv
import datetime as dt
import hashlib
import importlib.util
import io
import json
import subprocess
import tempfile
import time
from pathlib import Path

import pandas as pd

from cofail_kg.data.biohopr_loader import file_sha256
from cofail_kg.evaluation.query_validation import REASON_ORDER, summarize, validate_query
from cofail_kg.utils.frozen_hashes import read_frozen_hashes

ROOT = Path(__file__).resolve().parents[1]
FILES = ("query_validation.csv", "query_validation_summary.json")
COLUMNS = ("query_id", "relation_type", "construction", "ambiguity_tag", "Type_S", "Type_B", "Type_T",
           "n_rows", "row_ids", "status", "primary_reason", "reason_codes", *REASON_ORDER,
           "bq_size", "multiplicity", "dead_end_count", "tq_size", "gq_size", "gold_size",
           "type_t_node_count", "saturation_share", "leaky_question", "leaky_matches",
           "contains_validation_row", "validation_row_ids")

_S7_SPEC = importlib.util.spec_from_file_location("s7_script", ROOT / "scripts/07_build_reference_sets.py")
_s7 = importlib.util.module_from_spec(_S7_SPEC)
_S7_SPEC.loader.exec_module(_s7)
load_mapping = _s7.load_mapping  # same frozen-mapping checks as S7 (§3.4, §5)


def check_outputs(out):
    existing = [str(out / name) for name in FILES if (out / name).exists()]
    if existing:
        raise FileExistsError(f"S8 outputs already exist; use a new --output-dir: {existing}")


def text_hash_match(path, expected):
    """Return "raw" or "lf_normalized" if the file's SHA256 equals `expected`, else None.

    A Windows checkout with core.autocrlf=true turns a committed LF text file into CRLF; the
    LF-normalized bytes are then the committed bytes. Only line endings are normalized.
    """
    data = path.read_bytes()
    if hashlib.sha256(data).hexdigest() == expected:
        return "raw"
    if hashlib.sha256(data.replace(b"\r\n", b"\n")).hexdigest() == expected:
        return "lf_normalized"
    return None


def load_proposal(path, mapping, tags_csv):
    """Return ({type: (sample_row_ids, ambiguity_tag)} for PASS types, hash match kind).

    The proposal must be the file the frozen mapping was built from (provenance.proposal_sha256);
    its labels and construction must equal the frozen ones, and its tags must equal the S6 tag CSV.
    """
    match = text_hash_match(path, mapping["provenance"]["proposal_sha256"])
    if match is None:
        raise ValueError("S6 proposal hash differs from the frozen mapping's proposal_sha256")
    if match != "raw":
        print(f"Note: {path.name} matched proposal_sha256 after CRLF->LF normalization.", flush=True)
    proposal = json.loads(path.read_text(encoding="utf-8"))["per_type"]
    with tags_csv.open(encoding="utf-8", newline="") as handle:
        csv_tags = {r["relation_type"]: r["ambiguity_tag"] for r in csv.DictReader(handle)}
    out = {}
    for t, spec in sorted(mapping["per_type"].items()):
        if spec["d1_status"] != "PASS" or spec["excluded"]:
            continue
        p = proposal[t]
        for key in ("R1", "R2", "construction"):
            if p[key] != spec[key]:
                raise ValueError(f"{t}: proposal {key} {p[key]!r} differs from frozen {spec[key]!r}")
        if p["ambiguity_tag"] != csv_tags.get(t):
            raise ValueError(f"{t}: proposal tag {p['ambiguity_tag']!r} differs from tag CSV {csv_tags.get(t)!r}")
        out[t] = (list(p["sample_row_ids"]), p["ambiguity_tag"])
    return out, match


def check_reference_summary(path, frozen):
    """The S7 outputs must come from the frozen inputs (§3.4)."""
    provenance = json.loads(path.read_text(encoding="utf-8"))["provenance"]
    for key, frozen_key in (("biohopr_revision", "biohopr_revision"), ("kg_fingerprint", "kg_fingerprint"),
                            ("relation_mapping_sha256", "relation_mapping")):
        if provenance.get(key) != frozen.get(frozen_key):
            raise ValueError(f"S7 summary {key} differs from frozen {frozen_key}")
    return provenance


def load_nodes(cache, frozen):
    """Node names and per-type node counts from the fingerprinted cache (§3.2, §3.4)."""
    metadata_path = cache / "primekg_metadata.json"
    if file_sha256(metadata_path) != frozen.get("kg_fingerprint"):
        raise ValueError("PrimeKG metadata SHA256 differs from frozen kg_fingerprint")
    metadata = json.loads(metadata_path.read_text(encoding="utf-8"))
    nodes_path = cache / "primekg_nodes.parquet"
    if file_sha256(nodes_path) != metadata["cache_sha256"]["primekg_nodes.parquet"]:
        raise ValueError("PrimeKG node cache SHA256 differs from metadata")
    nodes = pd.read_parquet(nodes_path, columns=["node_index", "node_type", "node_name"])
    counts = {str(k): int(v) for k, v in nodes.groupby("node_type").size().items()}
    if counts != metadata["node_type_counts"]:
        raise ValueError("Node cache type counts differ from metadata node_type_counts")
    return dict(zip(nodes.node_index.astype(str), nodes.node_name)), counts


def to_records(value):
    """Parquet list cells to plain Python lists (deterministic, no truncation)."""
    return [{k: (v.tolist() if hasattr(v, "tolist") else v) for k, v in row.items()} for row in value]


def validate_all(queries, per_type, names, counts):
    def node_name(node_id):
        try:
            return names[node_id]
        except KeyError:
            raise KeyError(f"Node {node_id} missing from PrimeKG node cache") from None

    records = []
    for q in sorted(queries, key=lambda q: q["query_id"]):
        sample, tag = per_type[q["relation_type"]]
        records.append(validate_query(q, validation_rows=sample, ambiguity_tag=tag,
                                      type_t_node_count=counts[q["Type_T"]], node_name=node_name))
    return records


def csv_text(records):
    def cell(value):
        if value is None:
            return "NA"
        if isinstance(value, bool):
            return str(value).upper()
        if isinstance(value, list):
            return ";".join(value)
        if isinstance(value, float):
            return repr(value)
        return value

    buffer = io.StringIO()
    writer = csv.DictWriter(buffer, fieldnames=COLUMNS, lineterminator="\n")
    writer.writeheader()
    for r in records:
        writer.writerow({c: cell(r[c]) for c in COLUMNS})
    return buffer.getvalue()


def write_outputs(out, records, provenance):
    """Stage both files before publishing; never overwrite an artifact."""
    check_outputs(out)
    summary = {**summarize(records), "provenance": provenance}
    out.mkdir(parents=True, exist_ok=True)
    with tempfile.TemporaryDirectory(prefix=".s8-", dir=out) as staging:
        stage = Path(staging)
        (stage / FILES[0]).write_text(csv_text(records), encoding="utf-8", newline="")
        (stage / FILES[1]).write_text(json.dumps(summary, indent=2, sort_keys=True) + "\n", encoding="utf-8")
        check_outputs(out)
        for name in FILES:
            (stage / name).rename(out / name)
    return summary


def main(argv=None):
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--output-dir", type=Path, default=ROOT / "results/diagnostics")
    args = parser.parse_args(argv)
    check_outputs(args.output_dir)
    started = time.perf_counter()
    frozen = read_frozen_hashes(ROOT / "configs/frozen_hashes.yaml")
    mapping = load_mapping(ROOT / "results/semantics/relation_mapping.json", frozen)
    per_type, proposal_match = load_proposal(ROOT / "results/semantics/relation_mapping_proposed.json", mapping,
                             ROOT / "results/semantics/relation_ambiguity_tags.csv")
    processed = ROOT / "data/processed"
    check_reference_summary(processed / "reference_summary.json", frozen)
    names, counts = load_nodes(ROOT / "data/cache", frozen)
    queries = to_records(pd.read_parquet(processed / "reference_queries.parquet").to_dict("records"))
    if {q["relation_type"] for q in queries} - set(per_type):
        raise ValueError("S7 queries contain a relation type that is not a frozen PASS type")
    print(f"Verified frozen inputs; validating {len(queries)} queries.", flush=True)
    records = validate_all(queries, per_type, names, counts)
    inputs = ["data/processed/reference_queries.parquet", "data/processed/reference_summary.json",
              "results/semantics/relation_mapping.json", "results/semantics/relation_mapping_proposed.json",
              "results/semantics/relation_ambiguity_tags.csv", "data/cache/primekg_metadata.json",
              "data/cache/primekg_nodes.parquet", "configs/frozen_hashes.yaml",
              "scripts/08_validate_queries.py", "scripts/07_build_reference_sets.py",
              "src/cofail_kg/evaluation/query_validation.py", "src/cofail_kg/kg/primekg_index.py",
              "docs/frozen_pilot_protocol.md", "docs/decision_rules.md", "requirements.lock"]
    commit = subprocess.run(["git", "-c", f"safe.directory={ROOT.as_posix()}", "rev-parse", "HEAD"],
                            cwd=ROOT, text=True, capture_output=True, check=True).stdout.strip()
    provenance = {
        "biohopr_revision": frozen["biohopr_revision"], "kg_fingerprint": frozen["kg_fingerprint"],
        "relation_mapping_sha256": frozen["relation_mapping"], "protocol_version": "1.3.3",
        "leaky_question_interpretation": "researcher decision 2026-10-15 (S8 session); see "
                                         "src/cofail_kg/evaluation/query_validation.py docstring",
        "proposal_sha256_match": proposal_match, "git_commit": commit, "run_time_utc": dt.datetime.now(dt.timezone.utc).isoformat(timespec="seconds"),
        "elapsed_seconds": round(time.perf_counter() - started, 3),
        "sha256": {p: file_sha256(ROOT / p) for p in sorted(inputs)},
    }
    summary = write_outputs(args.output_dir, records, provenance)
    print(json.dumps({k: v for k, v in summary.items() if k != "provenance"}, indent=2))
    print(f"Saved S8 outputs to {args.output_dir} in {time.perf_counter() - started:.1f}s", flush=True)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
