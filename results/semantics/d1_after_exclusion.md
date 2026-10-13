# S6 D1 after all three failed-type exclusions

Decision date: 2026-10-13. **D1 remains PROCEED. No mapping is frozen.**

- PASS types: **9/12**.
- Rows belonging to PASS types: **7,377/7,633 (96.65%)**.
- Global thresholds: at least 6 PASS types and at least 70% coverage.
- Eight passing types propose BRIDGE (6,428 rows); one proposes UNION (949 rows).
- Original denominators are retained. All three FAIL types are now EXCLUDED (256 rows).

| Excluded type | Dataset rows | Validation rows | Best BRIDGE | Best UNION | Reason |
|---|---:|---:|---:|---:|---|
| drug:effect/phenotype:disease | 5 | 5 | 0/5 | 0/5 | Fewer than 10 validation rows and hop 2 below 90% |
| disease:effect/phenotype:drug | 36 | 30 | 3/30 | 3/30 | Hop 2 below 90% under both constructions |
| effect/phenotype:drug:disease | 215 | 30 | 26/30 | 20/30 | Hop 2 below 90% under both constructions |

The researcher authorized the two additional exclusions for the time being after reviewing
investigation results. They apply to the current primary analysis, with evidence retained
for possible later review and no automatic re-admission. The original five-row exclusion
is unchanged: positive/negative singleton ties remain unresolved, with neither selected.
No R2 or construction is adopted for the excluded types.

Detailed reasons, permitted checks, examples, alternatives and limits:
[latest exclusion decision](s6_exclusion_decision_02/report.md).
The earlier [five-row investigation](s6_failed_type_investigation/report.md) and
[two-type investigation](s6_remaining_investigation/report.md) remain historical snapshots.
Their earlier pending-disposition wording is superseded by this authorized decision.

Current [exclusion registry](relation_type_exclusions.json) and
[recomputed quantities](d1_after_exclusion.json) agree. Previous versions are preserved in
[s6_exclusion_decision_02/previous](s6_exclusion_decision_02/previous/d1_after_exclusion.md).
No thresholds or normalization rules changed; S7 has not started.
