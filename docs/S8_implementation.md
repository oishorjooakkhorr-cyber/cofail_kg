# S8 — Query validation

Completed locally 2026-10-15 using protocol §6, §7.1 and the frozen §12 lookup policy.
No S9 inclusion, mapping revision, saturation threshold or Gate D2 decision was made.

## Files and reproduction

- `src/cofail_kg/evaluation/query_validation.py`: deterministic per-query labels and summaries.
- `scripts/08_validate_queries.py`: frozen-input checks, S6 sample reconstruction, CSV/JSON writer.
- `tests/test_query_validation.py`: 17 synthetic and artifact-writing tests.
- `results/diagnostics/query_validation.csv`: 7,377 query records; list columns are JSON,
  booleans are `True`/`False`, unavailable source-dependent reason flags are `NA`.
- `results/diagnostics/query_validation_summary.json`: counts overall and by relation type,
  construction, ambiguity tag and multiplicity; input/source hashes and CSV hash.
- `results/diagnostics/s8_verification.json`: independent CSV/set checks and ten graph spot-checks.
- `docs/progress.md`: current completion status.

From the repository root in PowerShell:

```powershell
.\venv\Scripts\python.exe scripts/08_validate_queries.py
```

Existing outputs are never overwritten. For a rerun, supply a fresh `--output-dir`.
The default output directory is `results/diagnostics`.

## Results

| Measure | Count |
|---|---:|
| Queries | 7,377 |
| CONSISTENT | 7,362 |
| INCONSISTENT | 15 |
| Primary GOLD_MISSING_FROM_KG | 15 |
| Additional EXTRA_TARGETS | 3 |
| SINGLE_BRIDGE | 6,673 |
| MULTI_BRIDGE | 704 |
| LEAKY_QUESTION flags, across both statuses | 186 |
| Queries overlapping the S6 validation sample | 270 |

All other failure reasons have zero occurrences. Labels and leakage flags are retained;
the script does not filter queries. Saturation share is computed without selecting θ.
S9 can consume status, relation type, construction, ambiguity, S6 overlap, leakage,
bridge multiplicity, target counts and saturation share directly from the CSV.

## Tests and real checks

Full suite: **152 passed** (135 existing plus 17 new). After the final script line-ending
compatibility change, the focused suite passed again: **17 passed**.

An independent readback checked the CSV hash, coverage, answer-set equality and saturation
arithmetic on all 7,377 queries. For the first five inconsistent queries and the first five
consistent MULTI_BRIDGE queries in query-ID order, a separate calculation re-traversed the
cached graph using the frozen relation labels and reproduced B_q, T_q and G_q exactly.
All ten checks passed; their details are in `s8_verification.json`.

Small real example: `BH2_03612`, the AIDS → drug → side-effect question, is CONSISTENT:
23 valid bridges and 347 gold/reference answers. `BH2_05099` is INCONSISTENT despite
both sets having 85 answers: gold node 35852 (`acute lymphoblastic leukemia`) differs
from reachable node 33621 (`acute lymphoblastic leukemia (disease)`). Thus it has both
GOLD_MISSING_FROM_KG and EXTRA_TARGETS, with the former primary under §7.1.

## Assumptions and engineering choices

- Reuse the verified S7 reference tables and frozen mapping; use G_q for both BRIDGE and
  UNION, as required by the protocol. No scientific rule was added.
- Reconstruct the S6 validation samples from raw rows and cached node lookups using the
  existing S6 routine; require exact agreement with recorded S6 sample IDs.
- Count all cached PrimeKG nodes of the target type for the saturation denominator.
- Use escaped names with Unicode word-character boundaries and case-insensitive matching
  for whole-word/phrase leakage. Preserve raw benchmark names and question text.
- Sort records by query ID and serialize lists as JSON within CSV cells. Stage both output
  files in a temporary directory before publishing; reject existing output paths.
- Validate frozen mapping, KG fingerprint/cache hashes and S7 input/source hashes. Four S7
  Python files differ from recorded hashes only by CRLF versus LF; accept that conversion
  for Python sources only and record the affected paths. Data hashes remain byte-exact.
- Record current source/input hashes because these additions are uncommitted at execution.

These are routine engineering choices, not proposed literature methods. S7 did not record
hashes of its own output tables; this run records their current hashes, verifies coverage,
and performs graph spot-checks rather than claiming a historical byte-for-byte output check.

## Hand inspection

Review the ten examples in `s8_verification.json`, particularly the three leukemia-node
differences. The frozen §12 policy first accepts an exact normalized disease name and retries
with the disease suffix only when that lookup has no match. It therefore preserves the two
distinct node identities here. The other two inspected inconsistencies have gold drugs absent
from the adopted BRIDGE reference. No nodes, mappings or answer sets were altered.

Before advancing S9, review the full per-type status counts and leakage flags. S9 still needs
its separate mapping-confirmation analysis and researcher choice of θ before primary-population
calculation. Protocol and decision-rule files were not edited.
