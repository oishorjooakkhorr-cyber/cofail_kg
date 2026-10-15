# S9 — Primary population and Gate D2

Completed 2026-10-15 after the researcher selected θ = 0.50 and authorized part 2.
Part-1 evidence is documented separately in `docs/S9_part1_implementation.md`.

## Files created or changed

- `docs/frozen_pilot_protocol.md`: §7.2 threshold filled as 0.50, FROZEN at S9.
- `docs/decision_log.md`: threshold choice recorded before computation; outcome recorded after.
- `src/cofail_kg/evaluation/primary_population.py`: inclusion and ordered D2 feasibility rules.
- `scripts/09_primary_population.py`: protocol threshold parsing, input checks and output writer.
- `tests/test_primary_population.py`: 12 tests for inclusion predicates, exact threshold boundary,
  overlapping exclusions, zero eligible population, the ≥20 per-type rule, ordered gate
  boundaries, unfilled threshold/missing confirmation, artifact readback and overwrite protection.
- `data/processed/primary_population.csv`: evaluator-only population; retains S8 fields and
  adds `theta`, `saturated` and `mapping_confirmation`.
- `data/processed/primary_population_summary.json`: counts, outcome, population hash and provenance.
- `data/processed/primary_population_report.md`: readable per-type results.
- `docs/progress.md`: S9 complete and S10 next.

Reproduction from the repository root:

```powershell
.\venv\Scripts\python.exe scripts/09_primary_population.py
```

Use a new `--output-dir` for reruns; existing output files are never overwritten.

## Tests and results

Full suite: **170 passed** (158 existing plus 12 part-2 tests).
An independent CSV readback reproduced exact population membership from S8 status, leakage
and saturation, verified every retained type was CONFIRMED, and checked uniqueness, all
per-type counts, multiplicity totals, the saved checksum and the D2 result.

| Quantity | Result |
|---|---:|
| Input queries in nine D1 PASS types | 7,377 |
| INCONSISTENT exclusions | 15 |
| LEAKY_QUESTION exclusions | 186 |
| Overlap of those exclusions | 0 |
| SATURATED exclusions | 0 |
| Primary population N_P | 7,176 |
| SINGLE_BRIDGE | 6,575 |
| MULTI_BRIDGE | 601 |
| Types with ≥20 primary queries, K | 9 |
| Gate D2 | GREEN |

All nine types are CONFIRMED. The three earlier D1 FAIL types remain excluded upstream;
their 256 dataset rows are not included in the 7,377-query input denominator.
The report lists all nine per-type counts and single/multi splits.

Gate evaluation: N_P <150 is false; N_P ≥650 and K ≥5 is true, so GREEN.
No model run, S10 sampling or new mapping decision was performed.

## Small real example

`BH2_00005` (`drug:gene/protein:disease`) is included: CONSISTENT, not leaky,
saturation share 0.0015807963 (about 0.1581%) ≤0.50, D1 PASS and CONFIRMED.
It is SINGLE_BRIDGE. The first retained CSV row contains this example.

## Assumptions and engineering choices

- Researcher authorization fills the scheduled §7.2 threshold and permits this computation;
  existing mapping exclusions and all other scientific rules remain in force.
- Read θ from the numeric FROZEN protocol row; no command-line threshold override.
- Reuse S8 CSV parsing, verify its checksum against both S8 and S9 part-1 evidence,
  verify frozen inputs/mapping and unchanged decision rules, and recompute all three
  part-1 tables before computing the population. Refuse unresolved UNCONFIRMED types.
- S6 sample overlap affects mapping-confirmation estimation only. Such queries remain
  eligible for the primary population if they meet all §7.2 predicates.
- Use conjunction of all five inclusion conditions; count every applicable exclusion
  reason, explicitly allowing overlap, and count excluded queries once.
- Stable query-ID sorting, integer gate comparisons, preserved evaluator fields,
  staged CSV/JSON/Markdown output, exclusive output creation and SHA256 provenance
  are routine engineering choices, not new literature methods.
- The summary records current source hashes because implementation files are uncommitted.
  Its decision-log hash identifies the pre-run threshold-decision checkpoint; the later
  outcome entry is appended after computation and therefore changes the current log hash.
- Historical S8 and S9 part-1 outputs remain unchanged; their prior threshold-pending
  statements and recorded protocol/source hashes describe the earlier checkpoints.

## Hand inspection

Review the frozen θ row, threshold/outcome decision-log entries and the primary-population
report. S10 is next, subject to the researcher's request; no additional S9 decision is needed.
