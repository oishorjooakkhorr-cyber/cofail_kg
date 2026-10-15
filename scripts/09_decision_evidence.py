"""S9 part 1 decision tables, D2 steps 1–2. No threshold choice or feasibility calculation."""

import argparse
import csv
import datetime as dt
import json
import subprocess
import tempfile
from collections import Counter
from pathlib import Path

from cofail_kg.data.biohopr_loader import file_sha256
from cofail_kg.evaluation.dataset_evidence import decision_evidence
from cofail_kg.utils.frozen_hashes import read_frozen_hashes

ROOT = Path(__file__).resolve().parents[1]
FILES = ("mapping_confirmation.csv", "saturation_distribution.csv", "saturation_sensitivity.csv",
         "decision_evidence.json", "decision_evidence.md")


def load_records(path):
    with path.open(newline="", encoding="utf-8") as stream:
        records = list(csv.DictReader(stream))
    for r in records:
        if r["status"] not in ("CONSISTENT", "INCONSISTENT"):
            raise ValueError("Invalid S8 status")
        for key in ("contains_s6_validation_row", "leaky_question"):
            if r[key] not in ("True", "False"):
                raise ValueError(f"Invalid S8 boolean: {key}")
            r[key] = r[key] == "True"
        r["saturation_share"] = float(r["saturation_share"])
        if r["saturation_share"] != int(r["target_count"]) / int(r["target_type_nodes"]):
            raise ValueError("S8 saturation arithmetic mismatch")
    return records


def markdown_table(rows):
    fields = list(rows[0])
    def cell(v):
        return "NA" if v is None else f"{v:.6f}" if isinstance(v, float) else str(v)
    return "\n".join(["| " + " | ".join(fields) + " |", "| " + " | ".join(["---"]*len(fields)) + " |",
                       *["| " + " | ".join(cell(r[k]) for k in fields) + " |" for r in rows]])


def write_outputs(out, confirmation, distribution, sensitivity, provenance):
    def check():
        if any((out/name).exists() for name in FILES):
            raise FileExistsError("S9 evidence exists; use a fresh --output-dir")
    check()
    out.mkdir(parents=True, exist_ok=True)
    pending = [r["relation_type"] for r in confirmation if r["confirmation_status"] == "UNCONFIRMED"]
    report = {"mapping_confirmation": confirmation, "saturation_distribution": distribution,
              "saturation_sensitivity": sensitivity, "unconfirmed_types_requiring_decision": pending,
              "theta": None, "d2_step3_computed": False, "provenance": provenance}
    text = ("# S9 part 1 — Decision evidence\n\n"
            "Mapping confirmation uses only queries containing no S6 validation-sample row; ≥80% confirms a type.\n\n"
            "## Mapping confirmation\n\n" + markdown_table(confirmation) + "\n\n"
            "## Saturation distribution\n\n"
            "All CONSISTENT queries in CONFIRMED/UNCONFIRMABLE types, including S6-overlap and leakage flags. "
            "Percentiles use NumPy linear interpolation. Shares are fractions, not percentages.\n\n" +
            markdown_table(distribution) + "\n\n## Threshold sensitivity\n\n"
            "Exclusion means saturation share > θ. Remaining counts reflect saturation alone; "
            "they are not the primary population.\n\n" + markdown_table(sensitivity) + "\n\n"
            "## Required decisions\n\n" +
            ("Revise mapping or exclude these unconfirmed types: " + ", ".join(pending) if pending else
             "No type requires mapping revision or exclusion under the 80% rule.") +
            "\n\nResearcher must choose θ (protocol recommendation: 0.50) and authorize recording it "
            "in protocol §7.2 and the decision log before part 2. No θ was selected, no primary "
            "population was written, and no Gate D2 feasibility outcome was computed.\n")
    with tempfile.TemporaryDirectory(prefix=".s9-", dir=out) as staging:
        stage = Path(staging)
        for name, rows in zip(FILES[:3], (confirmation, distribution, sensitivity)):
            with (stage/name).open("w", newline="", encoding="utf-8") as stream:
                writer = csv.DictWriter(stream, fieldnames=list(rows[0]))
                writer.writeheader()
                writer.writerows(rows)
        (stage/FILES[3]).write_text(json.dumps(report, indent=2, sort_keys=True)+"\n", encoding="utf-8")
        (stage/FILES[4]).write_text(text, encoding="utf-8")
        check()
        for name in FILES:
            (stage/name).rename(out/name)
    return report


def main(argv=None):
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--output-dir", type=Path, default=ROOT/"results/diagnostics/s9_decision_evidence")
    args = parser.parse_args(argv)
    frozen = read_frozen_hashes(ROOT/"configs/frozen_hashes.yaml")
    summary = json.loads((ROOT/"results/diagnostics/query_validation_summary.json").read_text())
    path = ROOT/"results/diagnostics/query_validation.csv"
    if file_sha256(path) != summary["validation_csv_sha256"]:
        raise ValueError("S8 CSV hash mismatch")
    if summary["provenance"]["frozen_inputs"] != frozen:
        raise ValueError("Frozen inputs differ from S8")
    mapping_path = ROOT/"results/semantics/relation_mapping.json"
    if file_sha256(mapping_path) != frozen["relation_mapping"]:
        raise ValueError("Frozen mapping hash mismatch")
    mapping = json.loads(mapping_path.read_text())
    if not mapping["frozen"] or mapping["d1"]["outcome"] != "PROCEED":
        raise ValueError("Frozen D1 PROCEED mapping required")
    records = load_records(path)
    if len(records) != summary["overall"]["queries"] or dict(Counter(r["status"] for r in records)) != summary["overall"]["status"]:
        raise ValueError("S8 counts mismatch")
    types = [t for t,s in mapping["per_type"].items() if s["d1_status"] == "PASS" and not s["excluded"]]
    tables = decision_evidence(records, types)
    paths = ["results/diagnostics/query_validation.csv", "results/diagnostics/query_validation_summary.json",
             "results/semantics/relation_mapping.json", "configs/frozen_hashes.yaml",
             "docs/frozen_pilot_protocol.md", "docs/decision_rules.md", "docs/pipeline_runbook.md",
             "scripts/09_decision_evidence.py", "src/cofail_kg/evaluation/dataset_evidence.py"]
    provenance = {"run_time_utc": dt.datetime.now(dt.timezone.utc).isoformat(timespec="seconds"),
                  "frozen_inputs": frozen, "sha256": {p:file_sha256(ROOT/p) for p in paths},
                  "git_commit": subprocess.run(["git", "rev-parse", "HEAD"], cwd=ROOT, check=True,
                                               text=True, capture_output=True).stdout.strip()}
    write_outputs(args.output_dir, *tables, provenance)
    print(markdown_table(tables[0]))
    print(markdown_table([r for r in tables[2] if r["relation_type"] == "ALL"]))
    print(f"Saved part-1 evidence to {args.output_dir}")


if __name__ == "__main__":
    main()
