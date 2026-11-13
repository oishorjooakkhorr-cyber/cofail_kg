# S36 — Intervention evaluation (DESCRIPTIVE, treatment-only, exploratory)

DESCRIPTIVE, EXPLORATORY, TREATMENT-ONLY (D7 DESCRIPTIVE; decision log 2026-11-12 "Plan after D7", section A4; readings 2026-11-13 "S36 — Readings of the §21 outcomes"). Per case only; no aggregate ΔCF and no τ_CF (no control exists, C = 0).

Produced by `scripts/48_s36_evaluation.py` at commit `dcf51a84238c5ee491ff31b65387bbf80b729860` (tracked files clean: True). Run columns and their inference commits: before = `expansion_v1` @ `b8209e6c80a3ee4b1c263bc1479879ca74029110`, `pilot_v1` @ `46902dccc533fff1e3c617251ce730d996df7e9d (Gemma4-12B); 5e69e2391fb8b3f4c7722a91917200febe59c556 (Cogito-14B, Granite41-8B, Ministral3-14B)`; after = `intervention_v1` @ `c4b854ac946ed8283910120b6670a33cbc6cc89f`; reference = `repeat_v1` @ `1b36d37aed6c20b1d272575c3322bb36eefff672`.

## Observed facts

### Table 1 — Co-failure before (original run) vs after (intervention_v1), per case

| Case | Mechanism | Hidden | CF3^Q | CF4^Q | CF3^Q grounded | CF4^Q grounded | CF3^{Q,H1} | CF4^{Q,H1} | pcf_rel3 | pcf_rel4 | pcf_node3 | pcf_node4 | pcf_shortcut3 |
|---|---|---|---|---|---|---|---|---|---|---|---|---|---|
| BH2_03356 | WRONG_TURN_HOP2 | `off-label use` at 33618 (step 2) | 1 → 0 | 0 → 0 | 1 → 0 | 0 → 0 | 1 → 0 | 0 → 0 | 1 → 0 | 0 → 0 | 0 → 0 | 0 → 0 | 0 → 0 |
| BH2_04650 | SHORTCUT | `drug_protein` at 16843 (step 1) | 1 → 0 | 0 → 0 | 1 → 0 | 0 → 0 | 0 → 0 | 0 → 0 | 1 → 0 | 0 → 0 | 0 → 0 | 0 → 0 | 1 → 0 |
| BH2_05290 | WRONG_TURN_HOP2 | `off-label use` at 14052 (step 2) | 1 → 0 | 0 → 0 | 1 → 0 | 0 → 0 | 1 → 0 | 0 → 0 | 1 → 0 | 0 → 0 | 0 → 0 | 0 → 0 | 0 → 0 |
| BH2_05997 | WRONG_TURN_HOP2 | `off-label use` at 33228 (step 2) | 1 → 0 | 0 → 0 | 1 → 0 | 0 → 0 | 1 → 0 | 0 → 0 | 1 → 0 | 0 → 0 | 0 → 0 | 0 → 0 | 0 → 0 |
| BH2_06016 | WRONG_TURN_HOP2 | `off-label use` at 30800 (step 2) | 1 → 0 | 1 → 0 | 1 → 0 | 1 → 0 | 1 → 0 | 1 → 0 | 1 → 0 | 1 → 0 | 0 → 0 | 0 → 0 | 0 → 0 |

### Table 2 — Recovery, no-answer rate and technical failures, per case

| Case | Holders | Recovery after | Recovery, repeat_v1 reference | No-answer rate before → after | Technical failures after (holders) | Technical failures, repeat_v1 (holders) |
|---|---|---|---|---|---|---|
| BH2_03356 | Granite41-8B, Ministral3-14B, Cogito-14B | 2/2 | 0/2 | 0.00 (0/4) → 0.00 (0/3) | Ministral3-14B PARSE_FAIL | Ministral3-14B PARSE_FAIL |
| BH2_04650 | Granite41-8B, Ministral3-14B, Cogito-14B | 2/3 | 0/3 | 0.00 (0/4) → 0.00 (0/4) | — | — |
| BH2_05290 | Gemma4-12B, Granite41-8B, Cogito-14B | 3/3 | 0/3 | 0.00 (0/4) → 0.00 (0/3) | — | — |
| BH2_05997 | Granite41-8B, Ministral3-14B, Cogito-14B | 3/3 | 0/3 | 0.00 (0/4) → 0.00 (0/4) | — | — |
| BH2_06016 | Gemma4-12B, Granite41-8B, Ministral3-14B, Cogito-14B | 4/4 | 0/4 | 0.00 (0/4) → 0.00 (0/4) | — | — |

Recovery = holders (SUCCESS episodes only) with ≥ 1 resolved answer, all question-valid.

### Table 3 — Displacement per holder (result of record: one category; descriptive: answer counts VALID / SAME_WRONG_OTHER_NEIGHBOR / OTHER_WRONG)

| Case | Holder | Before: answer counts | After: category | After: answer counts | repeat_v1: category | repeat_v1: answer counts |
|---|---|---|---|---|---|---|
| BH2_03356 | Granite41-8B | 14 / 0 / 21 | VALID_RELATION | 14 / 0 / 0 | OTHER_WRONG | 14 / 0 / 21 |
| BH2_03356 | Ministral3-14B | 14 / 0 / 20 | PARSE_FAIL | — | PARSE_FAIL | — |
| BH2_03356 | Cogito-14B | 14 / 0 / 21 | VALID_RELATION | 14 / 0 / 0 | OTHER_WRONG | 14 / 0 / 21 |
| BH2_04650 | Granite41-8B | 0 / 0 / 5 | OTHER_WRONG | 13 / 0 / 7 | OTHER_WRONG | 0 / 0 / 5 |
| BH2_04650 | Ministral3-14B | 0 / 0 / 5 | VALID_RELATION | 13 / 0 / 0 | OTHER_WRONG | 0 / 0 / 5 |
| BH2_04650 | Cogito-14B | 0 / 0 / 5 | VALID_RELATION | 13 / 0 / 0 | OTHER_WRONG | 0 / 0 / 5 |
| BH2_05290 | Gemma4-12B | 2 / 0 / 2 | VALID_RELATION | 2 / 0 / 0 | OTHER_WRONG | 2 / 0 / 2 |
| BH2_05290 | Granite41-8B | 2 / 0 / 2 | VALID_RELATION | 2 / 0 / 0 | OTHER_WRONG | 2 / 0 / 2 |
| BH2_05290 | Cogito-14B | 2 / 0 / 2 | VALID_RELATION | 2 / 0 / 0 | OTHER_WRONG | 2 / 0 / 2 |
| BH2_05997 | Granite41-8B | 4 / 0 / 4 | VALID_RELATION | 4 / 0 / 0 | OTHER_WRONG | 4 / 0 / 4 |
| BH2_05997 | Ministral3-14B | 4 / 0 / 2 | VALID_RELATION | 4 / 0 / 0 | OTHER_WRONG | 4 / 0 / 2 |
| BH2_05997 | Cogito-14B | 4 / 0 / 2 | VALID_RELATION | 4 / 0 / 0 | OTHER_WRONG | 4 / 0 / 2 |
| BH2_06016 | Gemma4-12B | 24 / 0 / 8 | VALID_RELATION | 24 / 0 / 0 | OTHER_WRONG | 24 / 0 / 8 |
| BH2_06016 | Granite41-8B | 24 / 0 / 8 | VALID_RELATION | 24 / 0 / 0 | OTHER_WRONG | 24 / 0 / 8 |
| BH2_06016 | Ministral3-14B | 24 / 0 / 8 | VALID_RELATION | 24 / 0 / 0 | OTHER_WRONG | 24 / 0 / 8 |
| BH2_06016 | Cogito-14B | 24 / 0 / 8 | VALID_RELATION | 24 / 0 / 0 | OTHER_WRONG | 24 / 0 / 8 |

### Table 4 — Displacement counts per case (SUCCESS after-episodes of holders)

| Case | VALID_RELATION | SAME_WRONG_RELATION_OTHER_NEIGHBOR | OTHER_WRONG | NO_ANSWER | Excluded (technical failure) |
|---|---|---|---|---|---|
| BH2_03356 | 2 | 0 | 0 | 0 | 1 |
| BH2_04650 | 2 | 0 | 1 | 0 | 0 |
| BH2_05290 | 3 | 0 | 0 | 0 | 0 |
| BH2_05997 | 3 | 0 | 0 | 0 | 0 |
| BH2_06016 | 4 | 0 | 0 | 0 | 0 |

## Notes

- For the SHORTCUT case BH2_04650 (u = s, step 1), SAME_WRONG_RELATION_OTHER_NEIGHBOR cannot occur by construction: step 1 always starts at s.
- Hiding the label removes the answers reached through it by construction (decision log 2026-11-12, A4); these tables state observed counts only.
- ΔCF and τ_CF are not computed: both need a matched control, and none exists (C = 0).
