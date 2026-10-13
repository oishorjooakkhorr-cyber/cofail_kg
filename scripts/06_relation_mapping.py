"""S6 first prompt: propose mappings and report D1 without freezing (protocol §5).

Usage: python scripts/06_relation_mapping.py [--output-dir NEW_DIRECTORY]
Existing outputs are never overwritten. A new directory supports reproducibility
checks or later, explicitly authorized attempts without destroying this evidence.
"""

from __future__ import annotations

import argparse
import csv
import datetime as dt
import json
import subprocess
import time
from collections import defaultdict
from functools import lru_cache
from pathlib import Path

from cofail_kg.data.biohopr_loader import file_sha256, load_biohopr, read_metadata
from cofail_kg.data.field_roles import type_row_counts
from cofail_kg.evaluation.normalize import index_finder
from cofail_kg.evaluation.relation_mapping import evaluate_d1, score_type
from cofail_kg.kg.primekg_index import PrimeKGIndex
from cofail_kg.utils.frozen_hashes import read_frozen_hashes

ROOT = Path(__file__).resolve().parents[1]
FILES = ("relation_mapping_candidates.csv", "relation_mapping_proposed.json",
         "relation_ambiguity_tags.csv", "d1_report.md")


def validate_s5(rows, s5, frozen):
    """Reject stale field-role evidence before computing S6 (§3.1, §3.4)."""
    if s5["rule_outcome"] not in ("ROLES_SUPPORTED", "EXCLUDE_FAILING_TYPE"):
        raise ValueError("S5 has not permitted continuation")
    if type_row_counts(rows) != {t: v["rows_in_dataset"] for t, v in s5["per_type"].items()}:
        raise ValueError("S5 dataset counts differ from loaded BioHopR")
    for key in ("biohopr_revision", "kg_fingerprint"):
        if s5["provenance"][key] != frozen[key]:
            raise ValueError(f"S5 {key} differs from frozen input")


def check_outputs(out):
    existing = [name for name in FILES if (out / name).exists()]
    if existing:
        raise FileExistsError(f"Outputs already exist: {existing}; use a new output directory")


def _score(selection, n):
    return "NA" if selection["matches"] is None or not n else f"{selection['matches']}/{n} ({selection['score']:.1%})"


def report_md(proposed, get_node):
    d1 = proposed["d1"]
    lines = ["# S6 relation mapping — D1 report", "", "**Not frozen. First-prompt proposal only.**", "",
             "Protocol §5.1–5.3, v1.3.3; decision rules D1. All nonempty subsets of actual relation labels "
             "are scored. Display labels never affect scores. Validation uses the first 30 rows with "
             "resolved query and bridge in SHA256(\"42\" + row_id) order. An unresolved answer is a mismatch.", "",
             f"**D1: {d1['outcome'] or 'awaiting researcher tie decision'}.** "
             f"{d1['pass_types']}/{d1['total_types']} types PASS; {d1['fail_types']} FAIL; "
             f"{d1['pending_types']} pending. PASS types cover {d1['pass_rows']}/{d1['total_rows']} rows "
             f"({d1['pass_coverage']:.2%}). Global thresholds: at least 6 types and at least 70% row coverage.", "",
             f"**Mapping review status: {d1['status']}.** A label-set tie can require researcher review "
             "even when it cannot change any type's pass/fail status or the global D1 outcome.", "",
             "| Construction | Types | Dataset rows | PASS types | PASS rows | FAIL types | Pending |",
             "|---|---:|---:|---:|---:|---:|---:|"]
    for construction, v in d1["by_construction"].items():
        lines.append(f"| {construction} | {v['types']} | {v['rows']} | {v['pass_types']} | "
                     f"{v['pass_rows']} | {v['fail_types']} | {v['pending_types']} |")
    lines += ["", "## Per-type scores", "",
              "Skipped counts include unresolved query/bridge rows encountered before the sample fills. "
              "Alternative scenarios are shown for every tied hop-1 set. NA tags have no uniquely adopted mapping.", "",
              "| Relation type | Sample | Skipped | R1 | Hop 1 | BRIDGE hop 2 | UNION hop 2 | Construction | R2 | D1 | Ambiguity |",
              "|---|---:|---:|---|---|---|---|---|---|---|---|"]
    for t, v in proposed["per_type"].items():
        for scenario in v["scenarios"]:
            construction = scenario["construction"]
            r2 = scenario[construction]["sets"] if construction else []
            lines.append(f"| {t} | {v['sample_size']} | {len(v['skipped_unresolved'])} | {scenario['R1']} | "
                         f"{_score(v['hop1'], v['sample_size'])} | {_score(scenario['BRIDGE'], v['sample_size'])} | "
                         f"{_score(scenario['UNION'], v['sample_size'])} | {construction or 'neither'} | {r2} | "
                         f"{v['d1_status']} | {v['ambiguity_tag'] or 'NA'} |")
    lines += ["", "## Candidate labels (display labels are informational)", "",
              "| Relation type | Hop | Relation labels and display labels |", "|---|---|---|"]
    for t, v in proposed["per_type"].items():
        for hop, candidates in v["candidates"].items():
            lines.append(f"| {t} | {hop} | {json.dumps(candidates, ensure_ascii=False)} |")
    lines += ["", "## Decisions and mismatch evidence", "",
              "Examples below use each best-scoring label set, including ties. Complete missing/extra ID lists, "
              "all mismatch row IDs, sample IDs and skipped-row reasons are in `relation_mapping_proposed.json`. "
              "Examples show up to two rows per best set; long ID differences are summarized here only."]

    def describe(ids):
        names = [f"{i} ({get_node(i)['name']})" for i in ids[:8]]
        return "; ".join(names) + (f"; … ({len(ids)} total)" if len(ids) > 8 else "") or "none"

    for t, v in proposed["per_type"].items():
        lines += ["", f"### {t}", "", f"- D1: {v['d1_status']}; reasons: {', '.join(v['fail_reasons']) or 'none'}.",
                  f"- Query/bridge rows skipped: {len(v['skipped_unresolved'])}; sampled rows with unresolved answers: "
                  f"{len(v['sample_unresolved_answers'])}.",
                  f"- Hop-1 selection: {v['hop1']['status']}; sets: {v['hop1']['sets']}."]
        for scenario in v["scenarios"]:
            lines.append(f"- R1 {scenario['R1']}: {scenario['why']}.")
            for construction in ("BRIDGE", "UNION"):
                selected = scenario[construction]
                lines.append(f"- {construction}: {selected['status']}; sets {selected['sets']}; "
                             f"score {_score(selected, v['sample_size'])}.")
                for diagnostic in selected["diagnostics"]:
                    for example in diagnostic["examples"]:
                        lines.append(f"- {construction}, R2 {diagnostic['labels']}, {example['row_id']}: "
                                     f"s={example['query_id']} ({get_node(example['query_id'])['name']}), "
                                     f"bridge={example['bridge_id']} ({get_node(example['bridge_id'])['name']}); "
                                     f"gold {example['gold_count']}, reached {example['reached_count']}; "
                                     f"missing: {describe(example['missing_ids'])}; extra: {describe(example['extra_ids'])}; "
                                     f"unresolved: {example['unresolved_answers']}.")
        if v["d1_status"] == "FAIL" and all(
                not d["examples"] for s in v["scenarios"] for c in ("BRIDGE", "UNION") for d in s[c]["diagnostics"]):
            lines.append("- No answer-mismatch examples exist; this type fails an independent D1 requirement.")
    lines += ["", "## Provenance", "", "```json", json.dumps(proposed["provenance"], indent=2, sort_keys=True), "```", ""]
    return "\n".join(lines)


def write_outputs(out, proposed, candidates, get_node):
    check_outputs(out)
    report = report_md(proposed, get_node)
    out.mkdir(parents=True, exist_ok=True)
    columns = ["relation_type", "hop", "hop1_labels", "hop2_labels", "sample_size", "hop1_matches",
               "bridge_matches", "union_matches", "hop1_score", "bridge_score", "union_score"]
    with (out / FILES[0]).open("x", encoding="utf-8", newline="") as stream:
        writer = csv.DictWriter(stream, fieldnames=columns, lineterminator="\n")
        writer.writeheader()
        for record in candidates:
            record = dict(record)
            for hop in ("hop1", "bridge", "union"):
                count = record[f"{hop}_matches"]
                record[f"{hop}_score"] = count / record["sample_size"] if count is not None and record["sample_size"] else None
            for key in ("hop1_labels", "hop2_labels"):
                record[key] = json.dumps(record[key])
            writer.writerow(record)
    with (out / FILES[1]).open("x", encoding="utf-8", newline="\n") as stream:
        stream.write(json.dumps(proposed, indent=2, sort_keys=True, ensure_ascii=False) + "\n")
    with (out / FILES[2]).open("x", encoding="utf-8", newline="") as stream:
        columns = ["relation_type", "construction", "R1", "R2", "ambiguity_tag", "d1_status", "mapping_status"]
        writer = csv.DictWriter(stream, fieldnames=columns, lineterminator="\n")
        writer.writeheader()
        for t, v in proposed["per_type"].items():
            writer.writerow({"relation_type": t, "construction": v["construction"],
                             "R1": json.dumps(v["R1"]), "R2": json.dumps(v["R2"]),
                             "ambiguity_tag": v["ambiguity_tag"], "d1_status": v["d1_status"],
                             "mapping_status": "PROPOSED" if v["ambiguity_tag"] else "UNDETERMINED"})
    with (out / FILES[3]).open("x", encoding="utf-8", newline="\n") as stream:
        stream.write(report)


def main(argv=None):
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--output-dir", type=Path, default=ROOT / "results/semantics")
    args = parser.parse_args(argv)
    check_outputs(args.output_dir)
    started = time.perf_counter()
    frozen = read_frozen_hashes(ROOT / "configs/frozen_hashes.yaml")
    revision = read_metadata(ROOT / "data/raw/biohopr")["revision"]
    fingerprint = file_sha256(ROOT / "data/cache/primekg_metadata.json")
    if revision != frozen["biohopr_revision"] or fingerprint != frozen["kg_fingerprint"]:
        raise ValueError("S6 inputs do not match frozen BioHopR revision / KG fingerprint")
    rows = load_biohopr(ROOT / "data/raw/biohopr")
    s5 = json.loads((ROOT / "results/semantics/field_roles_summary.json").read_text(encoding="utf-8"))
    validate_s5(rows, s5, frozen)
    print("Verified frozen inputs and S5 evidence; loading PrimeKG.", flush=True)
    kg = PrimeKGIndex(ROOT / "data/cache")
    if kg.convention.mode != "either":
        raise ValueError("S6 requires the frozen either-direction edge convention")
    find = index_finder(kg)
    neighbors = lru_cache(maxsize=None)(kg.neighbors_by_label)
    candidates = lru_cache(maxsize=None)(kg.candidate_labels)
    grouped = defaultdict(list)
    for row in rows:
        grouped[row["relation_hop2"]].append(row)
    per_type, candidate_rows = {}, []
    for t, type_rows in sorted(grouped.items()):
        type_s, type_b, type_t = t.split(":")
        value = score_type(type_rows, find, neighbors, candidates(*sorted((type_s, type_b))),
                           candidates(*sorted((type_b, type_t))), s5_failed=s5["per_type"][t]["outcome"] == "FAIL")
        candidate_rows.extend({"relation_type": t, **c} for c in value.pop("candidate_scores"))
        per_type[t] = value
        print(f"{t}: n={value['sample_size']}, {value['d1_status']}, "
              f"{value['construction']}, {time.perf_counter() - started:.1f}s", flush=True)
    tracked = subprocess.run(["git", "-c", f"safe.directory={ROOT.as_posix()}", "ls-files", "src", "scripts/06_relation_mapping.py"],
                             cwd=ROOT, text=True, capture_output=True, check=True).stdout.splitlines()
    evidence = ["docs/frozen_pilot_protocol.md", "docs/decision_rules.md", "configs/frozen_hashes.yaml",
                "results/semantics/field_roles_summary.json", "data/raw/biohopr/BioHopR.json"]
    commit = subprocess.run(["git", "-c", f"safe.directory={ROOT.as_posix()}", "rev-parse", "HEAD"],
                            cwd=ROOT, text=True, capture_output=True, check=True).stdout.strip()
    proposed = {"frozen": False, "per_type": per_type, "d1": evaluate_d1(per_type), "provenance": {
        "biohopr_revision": revision, "kg_fingerprint": fingerprint, "protocol_version": "1.3.3",
        "git_commit": commit, "run_time_utc": dt.datetime.now(dt.timezone.utc).isoformat(timespec="seconds"),
        "elapsed_seconds": round(time.perf_counter() - started, 3),
        "sha256": {p: file_sha256(ROOT / p) for p in sorted(set(tracked + evidence))},
    }}
    write_outputs(args.output_dir, proposed, candidate_rows, kg.get_node)
    print(json.dumps(proposed["d1"], indent=2))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
