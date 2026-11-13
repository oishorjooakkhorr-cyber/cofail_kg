# B2 — Strict vs lenient answer key (EXPLORATORY)

EXPLORATORY (protocol §20) — docs/decision_log.md, entry 2026-11-12 "Plan after D7", section B2, with the entry 2026-11-13 "B2 — Inputs and the contraindication step". Strict results remain the results of record.

Produced by `scripts/41_b2_lenient.py` at commit `22923d69088adca357c2e77737701cf7f4a47c0f` (tracked files clean: True). Runs: `expansion_v1`, `pilot_v1`. Latest attempts.

Lenient key: `off-label use` accepted wherever `indication` is (R1⁺, R2⁺); `contraindication` never. 433 of 500 queries have a changed key; 211 of them have T_q⁺ larger than T_q.

## Table 1 — Co-failure, All queries

| Metric | Strict (of record) | Lenient | Strict-only queries | Lenient-only queries |
|---|---|---|---|---|
| CF3^Q | 8 | 2 | BH2_03356, BH2_05290, BH2_05778, BH2_05890, BH2_05997, BH2_06016 | — |
| CF4^Q | 2 | 0 | BH2_05778, BH2_06016 | — |
| CF3^{Q,H1} | 6 | 0 | BH2_03356, BH2_05290, BH2_05778, BH2_05890, BH2_05997, BH2_06016 | — |
| CF4^{Q,H1} | 2 | 0 | BH2_05778, BH2_06016 | — |

CF3^{Q,H1} = N.

## Table 2 — Per-agent question-valid precision and hop-1 status, All queries

| Agent | Key | QV precision: mean (defined / NA) | Pooled | H1_CLEAN | H1_MIXED | H1_WRONG | H1_NONE |
|---|---|---|---|---|---|---|---|
| Gemma4-12B | strict | 0.994 (497 / 3) | 0.996 (27276/27385) | 498 | 2 | 0 | 0 |
| Gemma4-12B | lenient | 1.000 (497 / 3) | 1.000 (27384/27385) | 499 | 1 | 0 | 0 |
| Granite41-8B | strict | 0.866 (481 / 19) | 0.952 (21444/22524) | 463 | 17 | 20 | 0 |
| Granite41-8B | lenient | 0.875 (481 / 19) | 0.956 (21535/22524) | 463 | 17 | 20 | 0 |
| Ministral3-14B | strict | 0.966 (444 / 56) | 0.988 (29179/29543) | 451 | 19 | 0 | 30 |
| Ministral3-14B | lenient | 0.986 (444 / 56) | 0.996 (29433/29543) | 456 | 14 | 0 | 30 |
| Cogito-14B | strict | 0.960 (430 / 70) | 0.979 (21361/21809) | 465 | 34 | 1 | 0 |
| Cogito-14B | lenient | 0.983 (430 / 70) | 0.987 (21527/21809) | 478 | 21 | 1 | 0 |

## Table 3 — `contraindication` at an indication step, All queries

| Agent | Answers | Queries | Of the answers: in T_q | in T_q⁺ |
|---|---|---|---|---|
| Gemma4-12B | 0 | 0 | 0 | 0 |
| Granite41-8B | 34 | 8 | 0 | 0 |
| Ministral3-14B | 1 | 1 | 0 | 0 |
| Cogito-14B | 21 | 4 | 0 | 0 |

## Table 4 — Co-failure, Without SOURCE_NAME_OVERLAP queries (BH2_05778, BH2_05971, BH2_06099; protocol §19.1)

| Metric | Strict (of record) | Lenient | Strict-only queries | Lenient-only queries |
|---|---|---|---|---|
| CF3^Q | 7 | 2 | BH2_03356, BH2_05290, BH2_05890, BH2_05997, BH2_06016 | — |
| CF4^Q | 1 | 0 | BH2_06016 | — |
| CF3^{Q,H1} | 5 | 0 | BH2_03356, BH2_05290, BH2_05890, BH2_05997, BH2_06016 | — |
| CF4^{Q,H1} | 1 | 0 | BH2_06016 | — |

CF3^{Q,H1} = N.

## Table 5 — Per-agent question-valid precision and hop-1 status, Without SOURCE_NAME_OVERLAP queries (BH2_05778, BH2_05971, BH2_06099; protocol §19.1)

| Agent | Key | QV precision: mean (defined / NA) | Pooled | H1_CLEAN | H1_MIXED | H1_WRONG | H1_NONE |
|---|---|---|---|---|---|---|---|
| Gemma4-12B | strict | 0.996 (494 / 3) | 0.996 (27272/27370) | 495 | 2 | 0 | 0 |
| Gemma4-12B | lenient | 1.000 (494 / 3) | 1.000 (27369/27370) | 496 | 1 | 0 | 0 |
| Granite41-8B | strict | 0.868 (478 / 19) | 0.953 (21441/22510) | 460 | 17 | 20 | 0 |
| Granite41-8B | lenient | 0.874 (478 / 19) | 0.956 (21521/22510) | 460 | 17 | 20 | 0 |
| Ministral3-14B | strict | 0.968 (441 / 56) | 0.988 (29176/29530) | 448 | 19 | 0 | 30 |
| Ministral3-14B | lenient | 0.986 (441 / 56) | 0.996 (29420/29530) | 453 | 14 | 0 | 30 |
| Cogito-14B | strict | 0.962 (427 / 70) | 0.980 (21357/21794) | 462 | 34 | 1 | 0 |
| Cogito-14B | lenient | 0.983 (427 / 70) | 0.987 (21512/21794) | 475 | 21 | 1 | 0 |

## Table 6 — `contraindication` at an indication step, Without SOURCE_NAME_OVERLAP queries (BH2_05778, BH2_05971, BH2_06099; protocol §19.1)

| Agent | Answers | Queries | Of the answers: in T_q | in T_q⁺ |
|---|---|---|---|---|
| Gemma4-12B | 0 | 0 | 0 | 0 |
| Granite41-8B | 34 | 8 | 0 | 0 |
| Ministral3-14B | 1 | 1 | 0 | 0 |
| Cogito-14B | 21 | 4 | 0 | 0 |

Indication step: treat-final, the second edge of a primary path with ≥ 2 edges; treat-first, the first edge. Per-episode contraindication detail and per-query T_q / T_q⁺ sizes: `b2.json`.
