# S6 D1 after the failed-type investigation

Decision date: 2026-10-13. **D1 remains PROCEED. No mapping is frozen.**

- PASS types: **9/12**.
- Rows belonging to PASS types: **7,377/7,633 (96.65%)**.
- Global thresholds remain at least 6 PASS types and at least 70% coverage.
- Eight passing types propose BRIDGE (6,428 rows); one proposes UNION (949 rows).
- Original denominators are retained: exclusion does not turn 9/12 into 9/11 or remove five rows from 7,633.

## Excluded after investigation

`drug:effect/phenotype:disease`: five available and resolvable validation rows, below the minimum ten;
all hop-2 subsets reproduce 0/5 gold sets under BRIDGE and UNION, below 90%.
The tied singleton candidates are retained unresolved:

| Candidate | BRIDGE | UNION |
|---|---:|---:|
| disease_phenotype_negative | 0/5 (0%) | 0/5 (0%) |
| disease_phenotype_positive | 0/5 (0%) | 0/5 (0%) |

Field roles, normalization, raw edge orientations and frozen/local release integrity were checked.
No permitted correction was found. The full two-row disease sets were presented before exclusion.
The user's conditional authorization therefore applies. See
[saved investigation](s6_failed_type_investigation/report.md),
[exclusion registry](relation_type_exclusions.json), and [recomputed quantities](d1_after_exclusion.json).
No R2 or construction is adopted for the excluded type, and no frozen mapping/hash was written.

## Still awaiting separate failure review

- `disease:effect/phenotype:drug`: BRIDGE 3/30; UNION 3/30.
- `effect/phenotype:drug:disease`: BRIDGE 26/30; UNION 20/30.

These two remain FAIL and are not marked finally excluded by this decision.
The original calculation outputs are preserved as historical snapshots. This report and the
exclusion registry record the subsequent investigation and researcher-authorized disposition.
