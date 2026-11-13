# Table 7 — B2 — Strict vs lenient answer key

**Status:** EXPLORATORY (protocol §20)

**Basis:** docs/decision_log.md, entry 2026-11-12 "S30 — Plan after D7", section B2; docs/decision_log.md, entry 2026-11-13 "B2 — Inputs and the contraindication step"

Produced by `scripts/38_final_tables.py` at commit `d6a00137dc22cbec6f9d537432a0166f5d0f9c6b` (tracked files clean: True; producing code committed at this commit: True).

Inputs (SHA256 in `provenance.json`; last commit that touched each):

- `results/exploratory/b2/b2.json` — dd0e748d1cdd79dd6a7a067eb3a493eb3a6c8dc3

Lenient key: `off-label use` accepted wherever `indication` is (R1⁺, R2⁺); `contraindication` never. 433 of 500 queries have a changed key; 211 of them have T_q⁺ larger than T_q. Strict results remain the results of record.

Produced by scripts/41_b2_lenient.py at commit 22923d69088adca357c2e77737701cf7f4a47c0f.

## 7a. Co-failure under the strict key (of record) and the lenient key

CSV: `table07a_cofailure.csv`

| View | Metric | Strict (of record) | Lenient | Strict-only queries | Lenient-only queries |
|---|---|---|---|---|---|
| All queries | CF3^Q | 8 | 2 | BH2_03356, BH2_05290, BH2_05778, BH2_05890, BH2_05997, BH2_06016 | — |
| All queries | CF4^Q | 2 | 0 | BH2_05778, BH2_06016 | — |
| All queries | CF3^{Q,H1} | 6 | 0 | BH2_03356, BH2_05290, BH2_05778, BH2_05890, BH2_05997, BH2_06016 | — |
| All queries | CF4^{Q,H1} | 2 | 0 | BH2_05778, BH2_06016 | — |
| Without SOURCE_NAME_OVERLAP | CF3^Q | 7 | 2 | BH2_03356, BH2_05290, BH2_05890, BH2_05997, BH2_06016 | — |
| Without SOURCE_NAME_OVERLAP | CF4^Q | 1 | 0 | BH2_06016 | — |
| Without SOURCE_NAME_OVERLAP | CF3^{Q,H1} | 5 | 0 | BH2_03356, BH2_05290, BH2_05890, BH2_05997, BH2_06016 | — |
| Without SOURCE_NAME_OVERLAP | CF4^{Q,H1} | 1 | 0 | BH2_06016 | — |

CF3^{Q,H1} = N.

## 7b. Per-agent question-valid precision and hop-1 status under both keys

CSV: `table07b_precision_hop1.csv`

| View | Agent | Key | Episodes | QV precision mean | Defined | NA | Pooled numerator | Pooled denominator | QV precision pooled | H1_CLEAN | H1_MIXED | H1_WRONG | H1_NONE |
|---|---|---|---|---|---|---|---|---|---|---|---|---|---|
| All queries | Gemma4-12B | strict | 500 | 0.9942 | 497 | 3 | 27276 | 27385 | 0.9960 | 498 | 2 | 0 | 0 |
| All queries | Granite41-8B | strict | 500 | 0.8665 | 481 | 19 | 21444 | 22524 | 0.9521 | 463 | 17 | 20 | 0 |
| All queries | Ministral3-14B | strict | 500 | 0.9662 | 444 | 56 | 29179 | 29543 | 0.9877 | 451 | 19 | 0 | 30 |
| All queries | Cogito-14B | strict | 500 | 0.9602 | 430 | 70 | 21361 | 21809 | 0.9795 | 465 | 34 | 1 | 0 |
| All queries | Gemma4-12B | lenient | 500 | 1.0000 | 497 | 3 | 27384 | 27385 | 1.0000 | 499 | 1 | 0 | 0 |
| All queries | Granite41-8B | lenient | 500 | 0.8746 | 481 | 19 | 21535 | 22524 | 0.9561 | 463 | 17 | 20 | 0 |
| All queries | Ministral3-14B | lenient | 500 | 0.9858 | 444 | 56 | 29433 | 29543 | 0.9963 | 456 | 14 | 0 | 30 |
| All queries | Cogito-14B | lenient | 500 | 0.9829 | 430 | 70 | 21527 | 21809 | 0.9871 | 478 | 21 | 1 | 0 |
| Without SOURCE_NAME_OVERLAP | Gemma4-12B | strict | 497 | 0.9959 | 494 | 3 | 27272 | 27370 | 0.9964 | 495 | 2 | 0 | 0 |
| Without SOURCE_NAME_OVERLAP | Granite41-8B | strict | 497 | 0.8676 | 478 | 19 | 21441 | 22510 | 0.9525 | 460 | 17 | 20 | 0 |
| Without SOURCE_NAME_OVERLAP | Ministral3-14B | strict | 497 | 0.9680 | 441 | 56 | 29176 | 29530 | 0.9880 | 448 | 19 | 0 | 30 |
| Without SOURCE_NAME_OVERLAP | Cogito-14B | strict | 497 | 0.9619 | 427 | 70 | 21357 | 21794 | 0.9799 | 462 | 34 | 1 | 0 |
| Without SOURCE_NAME_OVERLAP | Gemma4-12B | lenient | 497 | 1.0000 | 494 | 3 | 27369 | 27370 | 1.0000 | 496 | 1 | 0 | 0 |
| Without SOURCE_NAME_OVERLAP | Granite41-8B | lenient | 497 | 0.8738 | 478 | 19 | 21521 | 22510 | 0.9561 | 460 | 17 | 20 | 0 |
| Without SOURCE_NAME_OVERLAP | Ministral3-14B | lenient | 497 | 0.9857 | 441 | 56 | 29420 | 29530 | 0.9963 | 453 | 14 | 0 | 30 |
| Without SOURCE_NAME_OVERLAP | Cogito-14B | lenient | 497 | 0.9828 | 427 | 70 | 21512 | 21794 | 0.9871 | 475 | 21 | 1 | 0 |

## 7c. `contraindication` at an indication step (never accepted)

CSV: `table07c_contraindication.csv`

| View | Agent | Answers | Queries | Of the answers: in T_q | in T_q⁺ |
|---|---|---|---|---|---|
| All queries | Gemma4-12B | 0 | 0 | 0 | 0 |
| All queries | Granite41-8B | 34 | 8 | 0 | 0 |
| All queries | Ministral3-14B | 1 | 1 | 0 | 0 |
| All queries | Cogito-14B | 21 | 4 | 0 | 0 |
| Without SOURCE_NAME_OVERLAP | Gemma4-12B | 0 | 0 | 0 | 0 |
| Without SOURCE_NAME_OVERLAP | Granite41-8B | 34 | 8 | 0 | 0 |
| Without SOURCE_NAME_OVERLAP | Ministral3-14B | 1 | 1 | 0 | 0 |
| Without SOURCE_NAME_OVERLAP | Cogito-14B | 21 | 4 | 0 | 0 |

Indication step: treat-final, the second edge of a primary path with ≥ 2 edges; treat-first, the first edge.
