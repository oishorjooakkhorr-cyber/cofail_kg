"""S9 part 2: primary population and ordered Gate D2, protocol §7.2."""

import argparse
import csv
import datetime as dt
import importlib.util
import json
import re
import subprocess
import tempfile
from pathlib import Path

from cofail_kg.data.biohopr_loader import file_sha256
from cofail_kg.evaluation.dataset_evidence import decision_evidence
from cofail_kg.evaluation.primary_population import build_population
from cofail_kg.utils.frozen_hashes import read_frozen_hashes

ROOT = Path(__file__).resolve().parents[1]
FILES = ("primary_population.csv", "primary_population_summary.json", "primary_population_report.md")


def frozen_theta(text):
    match = re.search(r"^\| Saturation threshold θ \| ([0-9]+(?:\.[0-9]+)?) \| `\[FROZEN\]`", text, re.MULTILINE)
    if not match:
        raise ValueError("Protocol §7.2 theta is not numeric and FROZEN")
    return float(match[1])


def check_outputs(out):
    if any((out/name).exists() for name in FILES):
        raise FileExistsError("S9 population outputs exist; use a fresh --output-dir")


def write_outputs(out, population, report, input_fields):
    check_outputs(out)
    out.mkdir(parents=True, exist_ok=True)
    fields = list(input_fields) + ["theta", "saturated", "mapping_confirmation"]
    with tempfile.TemporaryDirectory(prefix=".s9-population-", dir=out) as staging:
        stage = Path(staging)
        with (stage/FILES[0]).open("w", newline="", encoding="utf-8") as stream:
            writer = csv.DictWriter(stream, fieldnames=fields)
            writer.writeheader()
            writer.writerows(population)
        report["primary_population_sha256"] = file_sha256(stage/FILES[0])
        (stage/FILES[1]).write_text(json.dumps(report, indent=2, sort_keys=True)+"\n", encoding="utf-8")
        text = (f"# S9 — Primary population and Gate D2\n\n"
                f"θ = {report['theta']:.2f}; N_P = {report['N_P']}; K = {report['K']}; "
                f"Gate D2 = **{report['outcome']}**. K counts types with at least 20 primary queries.\n\n"
                "Gate evaluated in order: RED if N_P < 150; otherwise GREEN if N_P ≥ 650 "
                "and K ≥ 5; otherwise YELLOW.\n\n"
                f"Input queries: {report['input_queries']}; excluded queries: {report['excluded_queries']}. "
                "Exclusion counts may overlap:\n\n" +
                "\n".join(f"- {key}: {value}" for key,value in report['exclusion_counts'].items()) +
                "\n\n| Relation type | Primary queries | Single | Multi |\n| --- | ---: | ---: | ---: |\n" +
                "\n".join(f"| {kind} | {v['queries']} | {v['by_multiplicity'].get('SINGLE_BRIDGE',0)} | "
                          f"{v['by_multiplicity'].get('MULTI_BRIDGE',0)} |" for kind,v in report['by_type'].items()) +
                "\n\nThis evaluator-only CSV retains S8 evidence fields and adds θ, saturation and "
                "mapping confirmation. S6 sample queries may enter the population; they were excluded "
                "only from mapping-confirmation estimation. No S10 sampling was performed.\n")
        (stage/FILES[2]).write_text(text, encoding="utf-8")
        check_outputs(out)
        for name in FILES:
            (stage/name).rename(out/name)


def main(argv=None):
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--output-dir", type=Path, default=ROOT/"data/processed")
    args = parser.parse_args(argv)
    check_outputs(args.output_dir)
    theta = frozen_theta((ROOT/"docs/frozen_pilot_protocol.md").read_text(encoding="utf-8"))
    frozen = read_frozen_hashes(ROOT/"configs/frozen_hashes.yaml")
    summary = json.loads((ROOT/"results/diagnostics/query_validation_summary.json").read_text())
    evidence = json.loads((ROOT/"results/diagnostics/s9_decision_evidence/decision_evidence.json").read_text())
    path = ROOT/"results/diagnostics/query_validation.csv"
    digest = file_sha256(path)
    if digest != summary["validation_csv_sha256"] or digest != evidence["provenance"]["sha256"]["results/diagnostics/query_validation.csv"]:
        raise ValueError("S8 CSV differs from completed S8/S9 part-1 evidence")
    if frozen != summary["provenance"]["frozen_inputs"] or frozen != evidence["provenance"]["frozen_inputs"]:
        raise ValueError("Frozen inputs differ from evidence")
    if file_sha256(ROOT/"results/semantics/relation_mapping.json") != frozen["relation_mapping"]:
        raise ValueError("Frozen mapping changed")
    if file_sha256(ROOT/"docs/decision_rules.md") != evidence["provenance"]["sha256"]["docs/decision_rules.md"]:
        raise ValueError("Decision rules changed since part 1")
    spec = importlib.util.spec_from_file_location("s9_evidence", ROOT/"scripts/09_decision_evidence.py")
    helper = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(helper)
    records = helper.load_records(path)
    mapping = json.loads((ROOT/"results/semantics/relation_mapping.json").read_text())
    if not mapping["frozen"] or mapping["d1"]["outcome"] != "PROCEED":
        raise ValueError("Frozen D1 PROCEED required")
    types = {t for t,s in mapping["per_type"].items() if s["d1_status"] == "PASS" and not s["excluded"]}
    tables = decision_evidence(records, types)
    for name, current in zip(("mapping_confirmation", "saturation_distribution", "saturation_sensitivity"), tables):
        if current != evidence[name]:
            raise ValueError(f"Part-1 evidence mismatch: {name}")
    confirmation = {r["relation_type"]:r["confirmation_status"] for r in tables[0]}
    if "UNCONFIRMED" in confirmation.values():
        raise ValueError("Unconfirmed mappings require researcher disposition before part 2")
    population, report = build_population(records, types, confirmation, theta)
    paths = ["scripts/09_primary_population.py", "src/cofail_kg/evaluation/primary_population.py",
             "scripts/09_decision_evidence.py", "src/cofail_kg/evaluation/dataset_evidence.py",
             "results/diagnostics/query_validation.csv", "results/diagnostics/query_validation_summary.json",
             "results/diagnostics/s9_decision_evidence/decision_evidence.json",
             "results/semantics/relation_mapping.json", "configs/frozen_hashes.yaml",
             "docs/frozen_pilot_protocol.md", "docs/decision_rules.md", "docs/decision_log.md"]
    report["mapping_confirmation"] = confirmation
    report["provenance"] = {"run_time_utc":dt.datetime.now(dt.timezone.utc).isoformat(timespec="seconds"),
                            "frozen_inputs": frozen, "sha256":{p:file_sha256(ROOT/p) for p in paths},
                            "git_commit":subprocess.run(["git", "rev-parse", "HEAD"], cwd=ROOT, check=True,
                                                        text=True, capture_output=True).stdout.strip()}
    write_outputs(args.output_dir, population, report, records[0])
    print(json.dumps({k:v for k,v in report.items() if k not in ("provenance", "mapping_confirmation")}, indent=2))
    print(f"Saved primary population to {args.output_dir}")


if __name__ == "__main__":
    main()
