# S9 part 1 — Decision evidence

Generated 2026-10-15. Scope: D2 mapping confirmation and saturation evidence only.

## Files created or changed

- `src/cofail_kg/evaluation/dataset_evidence.py`: pure confirmation/distribution/sensitivity calculations.
- `scripts/09_decision_evidence.py`: validates S8 CSV hash and frozen mapping, then writes evidence.
- `tests/test_dataset_evidence.py`: six tests covering confirmation boundaries, sample exclusion,
  UNCONFIRMABLE/UNCONFIRMED handling, strict saturation comparison, percentile behavior,
  leakage/sample inclusion in saturation tables, duplicate IDs and output preservation.
- `results/diagnostics/s9_decision_evidence/`: `mapping_confirmation.csv`,
  `saturation_distribution.csv`, `saturation_sensitivity.csv`, `decision_evidence.json`,
  and a readable `decision_evidence.md` report.
- `docs/progress.md`: records part-1 completion and pending researcher decision.

Reproduce from the repository root:

```powershell
.\venv\Scripts\python.exe scripts/09_decision_evidence.py
```

Reruns require a fresh `--output-dir`; completed outputs are never overwritten.

## Tests and real example

Full suite: **158 passed**, including six new tests. Independent readback verified all
nine confirmation rows, ten distribution rows and forty threshold-sensitivity rows.
Percentiles were independently recalculated by interpolating sorted observations.

Example: `effect/phenotype:disease:drug` has 546 total queries, 30 overlapping S6,
516 confirmation queries, and 506 consistent confirmation queries: 506/516 = 98.0620%,
so CONFIRMED. Its ten inconsistent held-out queries are retained in the evidence.

## Results and pending decision

All nine D1 PASS types are CONFIRMED. Seven have 100% held-out consistency;
`gene/protein:drug:disease` has 429/432 = 99.3056%; the example above has 98.0620%.
No type is UNCONFIRMABLE or UNCONFIRMED. No mapping revision/exclusion decision is required.

Saturation evidence covers all 7,362 consistent queries in those types. Overall shares:
p50 0.0008196721, p90 0.0064402810, p95 0.0116256286, p99 0.0208059565,
maximum 0.0515269574 (5.1527%). At θ = 0.30, 0.50, 0.70 and 0.90, zero queries
are excluded overall or within any relation type. No whole type is removed.

Researcher decision needed: select θ (protocol recommendation: 0.50) and authorize recording
it in protocol §7.2 and the decision log before computing part 2. No primary population,
N_P, K, or Gate D2 step-3 outcome was computed; the protocol/decision log were not changed.

## Assumptions and engineering choices

- Use completed S8 query labels as input; check its CSV checksum against its summary, frozen
  input identity against current hashes, mapping hash, and status totals before calculation.
- Confirmation excludes queries containing any S6 validation-sample row; use integer
  arithmetic for the inclusive 80% threshold. Zero eligible queries are UNCONFIRMABLE.
- Saturation tables include all CONSISTENT queries in CONFIRMED/UNCONFIRMABLE types,
  including leakage flags and S6 sample overlap, as required by S9 part 1. Remaining counts
  after a hypothetical saturation exclusion are not primary-population counts.
- NumPy linear percentile interpolation matches the project's previous diagnostic convention.
  Saved shares are fractions; the readable report explicitly states this.
- Strict `share > θ` follows protocol §7.1. Thresholds are the four specified comparisons,
  not chosen values. Empty distributions have explicit null percentiles.
- Stable ordering, staged CSV/JSON/Markdown publication, overwrite rejection, and source/input
  SHA256 provenance are routine engineering choices. No new literature method was introduced.

## Hand inspection

Read `results/diagnostics/s9_decision_evidence/decision_evidence.md`, particularly the
confirmation denominators and threshold table. Choose θ before requesting part 2.
