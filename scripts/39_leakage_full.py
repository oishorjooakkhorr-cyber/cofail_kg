"""S39 (EXPLORATORY): protocol §19.1 leakage checks (a) and (c) on the `full` agent-input sheet.

Evaluator-side audit, no model calls. It reuses the S15 scan functions of tests/test_leakage.py
unchanged, exactly as that file's all-rows test does for the 524 S10 queries:
  (a) the system prompt and the starting-entity line of every query are scanned for the forbidden
      terms of protocol §19.1(a); the 2026-10-16 source-name overlap exemption applies and flags
      SOURCE_NAME_OVERLAP; names shorter than 4 characters are listed for manual review;
  (c) every sheet line has exactly the four fields of protocol §8.
Checks (b) and (d) do not depend on the manifest and stay in the test suite.

Output: results/diagnostics/s39/leakage_full.json (written once; an identical rerun is accepted).
The scan of the 6,652 candidates, made before the researcher excluded 24 of them (decision log
2026-11-11, configs/full_run_exclusions.json), is kept as leakage_candidates_6652.json.
Exit code 1 if any row fails. Failing rows are reported, never dropped or changed.

Usage:  python scripts/39_leakage_full.py
"""
import hashlib
import importlib.util
import json
from pathlib import Path
import sys

import pyarrow.parquet as pq

from cofail_kg.agents.prompts import P1_TEMPLATE, prompt_sha256
from cofail_kg.kg.primekg_index import PrimeKGIndex
from cofail_kg.utils.frozen_hashes import read_frozen_hashes

ROOT = Path(__file__).resolve().parents[1]
OUT = ROOT / "results/diagnostics/s39/leakage_full.json"

spec = importlib.util.spec_from_file_location("s15_leakage", ROOT / "tests/test_leakage.py")
S15 = importlib.util.module_from_spec(spec)
spec.loader.exec_module(S15)


def scan(rows, references, per_type, index, system):
    """Failures, SOURCE_NAME_OVERLAP records and short names for the sheet rows (S15 rules)."""
    failures, overlaps, short_names = [], [], []
    for row in rows:
        q = references[row["query_id"]]
        spec_ = per_type[q["relation_type"]]
        if spec_["d1_status"] != "PASS" or spec_["excluded"]:
            raise ValueError(f"{row['query_id']}: relation type did not pass D1")
        if index.get_node(row["start_id"])["name"] != row["start_name"] or q["s"] != row["start_id"]:
            raise ValueError(f"{row['query_id']}: sheet start entity differs from the reference")
        line = f"Starting entity: {row['start_name']} (PrimeKG ID: {row['start_id']})"
        hits, matches, short = S15.scan_starting_line(line, row, q, spec_, index)
        failures.extend(dict(query_id=row["query_id"], surface="starting_entity", **f) for f in hits)
        system_hits, _ = S15.scan_surface(system, S15.forbidden_terms(q, spec_, index))
        failures.extend(dict(query_id=row["query_id"], surface="system", kind=k, term=t) for k, t in system_hits)
        if matches:
            overlaps.append(S15.overlap_record("full", row, q, matches, index))
        short_names.extend(dict(query_id=row["query_id"], name=n,
                                present_in_system=bool(S15.scan_surface(system, [("id", n)])[0]),
                                present_in_starting_line=bool(S15.scan_surface(line, [("id", n)])[0]))
                           for n in short)
    return failures, overlaps, short_names


def main():
    frozen = read_frozen_hashes(ROOT / "configs/frozen_hashes.yaml")
    sheet = ROOT / "data/agent_inputs/full.jsonl"
    digest = hashlib.sha256(sheet.read_bytes()).hexdigest()
    full = read_frozen_hashes(ROOT / "configs/frozen_hashes_full.yaml")["manifests_full"]
    if digest != full["data/agent_inputs/full.jsonl"]:
        raise ValueError("full agent-input sheet differs from frozen_hashes_full `manifests_full`")
    if prompt_sha256() != frozen["prompt"]:
        raise ValueError("Prompt template differs from frozen_hashes `prompt`")
    rows = S15.read_sheet(sheet)  # check (c): exactly four non-empty string fields, no duplicates
    mapping = json.loads((ROOT / "results/semantics/relation_mapping.json").read_text(encoding="utf-8"))
    references = {q["query_id"]: q for q in pq.read_table(ROOT / "data/processed/reference_queries.parquet").to_pylist()}
    index = PrimeKGIndex(ROOT / "data/cache")
    system = P1_TEMPLATE.replace("{PAGE_SIZE}", "50").replace("{BUDGET}", "30")
    failures, overlaps, short_names = scan(rows, references, mapping["per_type"], index, system)
    report = {"status": "EXPLORATORY (decision log 2026-11-11, S39)", "sheet": "data/agent_inputs/full.jsonl",
              "sheet_sha256": digest, "rows": len(rows), "check_c_four_fields": "PASS",
              "failures": failures, "flagged_queries": overlaps,
              "short_names": short_names,
              "short_names_present_in_a_scanned_surface": [s for s in short_names
                                                           if s["present_in_system"] or s["present_in_starting_line"]]}
    text = json.dumps(report, indent=2, sort_keys=True, ensure_ascii=False) + "\n"
    if OUT.exists():
        if OUT.read_text(encoding="utf-8") != text:
            raise ValueError(f"Existing leakage report differs: {OUT}")
    else:
        OUT.parent.mkdir(parents=True, exist_ok=True)
        with OUT.open("x", encoding="utf-8", newline="\n") as handle:
            handle.write(text)
    print(json.dumps({"rows": len(rows), "failures": len(failures), "source_name_overlap_queries": len(overlaps),
                      "short_name_entries": len(short_names),
                      "short_names_present_in_a_scanned_surface": len(report["short_names_present_in_a_scanned_surface"])},
                     indent=2))
    if failures:
        print("LEAKAGE FAILURES:\n" + json.dumps(failures, indent=2, ensure_ascii=False))
        return 1
    return 0


if __name__ == "__main__":
    sys.exit(main())
