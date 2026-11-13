# Table 12 — IC — Independence check of off-label uptake

**Status:** EXPLORATORY (protocol §20)

**Basis:** docs/decision_log.md, entry 2026-11-13 "IC — Independence check of off-label uptake (rule fixed before computing)"; docs/decision_log.md, entry 2026-11-12 "S30 — Plan after D7" (B1 inputs)

Produced by `scripts/38_final_tables.py` at commit `d6a00137dc22cbec6f9d537432a0166f5d0f9c6b` (tracked files clean: True; producing code committed at this commit: True).

Inputs (SHA256 in `provenance.json`; last commit that touched each):

- `results/exploratory/ic/ic.json` — afdc00c2da1c8f06b3298b120c83a4eab4d4a984

Limits (logged with the rule): p_i is estimated from the same episodes; queries whose off-label lists are more tempting would also appear as MORE CLUSTERED. Agents never share anything (§9.3); "independent" means only that each agent's own rate accounts for the pattern.

Produced by scripts/44_independence_check.py at commit 8131d088cc0ea937071cdca990a2d9c26ff7831b.

## 12a. T = number of treat-final queries with K_q ≥ 3, against independence with each agent's own B1 uptake rate (exact Poisson-binomial)

CSV: `table12a_summary.csv`

| View | Queries | Queries with ≥ 1 agent in A_q | T_obs | E[T] | T 2.5th | T 97.5th | P(T ≥ T_obs) | P(T ≤ T_obs) | Outcome | Use | Pairs S_obs | Pairs expected |
|---|---|---|---|---|---|---|---|---|---|---|---|---|
| All queries | 75 | 35 | 6 | 5.5102 | 2 | 10 | 0.4820 | 0.6940 | AGREES | outcome | 40 | 32.0545 |
| Without SOURCE_NAME_OVERLAP | 72 | 34 | 5 | 4.5552 | 1 | 9 | 0.4878 | 0.7014 | AGREES | descriptive only | 34 | 28.0722 |

Outcome rule (fixed before computing): AGREES if both tail probabilities > 0.025; MORE CLUSTERED if P(T ≥ T_obs) ≤ 0.025; LESS CLUSTERED if P(T ≤ T_obs) ≤ 0.025.

## 12b. p_i = (Taken ∧ Opportunity) / Opportunity per agent (B1)

CSV: `table12b_rates.csv`

| View | Agent | Opportunity | Taken ∧ Opportunity | p_i |
|---|---|---|---|---|
| All queries | Cogito-14B | 33 | 25 | 0.7576 |
| All queries | Gemma4-12B | 35 | 6 | 0.1714 |
| All queries | Granite41-8B | 28 | 8 | 0.2857 |
| All queries | Ministral3-14B | 30 | 18 | 0.6000 |
| Without SOURCE_NAME_OVERLAP | Cogito-14B | 32 | 24 | 0.7500 |
| Without SOURCE_NAME_OVERLAP | Gemma4-12B | 34 | 5 | 0.1471 |
| Without SOURCE_NAME_OVERLAP | Granite41-8B | 27 | 7 | 0.2593 |
| Without SOURCE_NAME_OVERLAP | Ministral3-14B | 29 | 17 | 0.5862 |

## 12c. Queries with K_q ≥ 2 or CF3^{Q,H1} = 1 (all queries)

CSV: `table12c_per_query.csv`

| Query | A_q | Takers | K_q | P(K_q ≥ 3) | CF3^{Q,H1} |
|---|---|---|---|---|---|
| BH2_03356 | Cogito-14B, Gemma4-12B, Granite41-8B, Ministral3-14B | Cogito-14B, Granite41-8B, Ministral3-14B | 3 | 0.2075 | 1 |
| BH2_05290 | Cogito-14B, Gemma4-12B, Granite41-8B, Ministral3-14B | Cogito-14B, Gemma4-12B, Granite41-8B | 3 | 0.2075 | 1 |
| BH2_05576 | Cogito-14B, Gemma4-12B, Granite41-8B, Ministral3-14B | Cogito-14B, Ministral3-14B | 2 | 0.2075 | 0 |
| BH2_05595 | Cogito-14B, Gemma4-12B, Granite41-8B, Ministral3-14B | Cogito-14B, Gemma4-12B | 2 | 0.2075 | 0 |
| BH2_05609 | Cogito-14B, Gemma4-12B, Granite41-8B, Ministral3-14B | Cogito-14B, Ministral3-14B | 2 | 0.2075 | 0 |
| BH2_05627 | Cogito-14B, Gemma4-12B, Ministral3-14B | Cogito-14B, Ministral3-14B | 2 | 0.0779 | 0 |
| BH2_05647 | Cogito-14B, Gemma4-12B, Granite41-8B, Ministral3-14B | Granite41-8B, Ministral3-14B | 2 | 0.2075 | 0 |
| BH2_05680 | Cogito-14B, Gemma4-12B, Granite41-8B, Ministral3-14B | Cogito-14B, Ministral3-14B | 2 | 0.2075 | 0 |
| BH2_05778 | Cogito-14B, Gemma4-12B, Granite41-8B, Ministral3-14B | Cogito-14B, Gemma4-12B, Granite41-8B, Ministral3-14B | 4 | 0.2075 | 1 |
| BH2_05793 | Cogito-14B, Gemma4-12B, Ministral3-14B | Cogito-14B, Ministral3-14B | 2 | 0.0779 | 0 |
| BH2_05812 | Cogito-14B, Gemma4-12B | Cogito-14B, Gemma4-12B | 2 | 0 | 0 |
| BH2_05838 | Cogito-14B, Gemma4-12B, Granite41-8B, Ministral3-14B | Cogito-14B, Ministral3-14B | 2 | 0.2075 | 0 |
| BH2_05852 | Cogito-14B, Gemma4-12B, Granite41-8B, Ministral3-14B | Cogito-14B, Ministral3-14B | 2 | 0.2075 | 0 |
| BH2_05856 | Cogito-14B, Gemma4-12B, Granite41-8B, Ministral3-14B | Cogito-14B, Ministral3-14B | 2 | 0.2075 | 0 |
| BH2_05890 | Cogito-14B, Gemma4-12B, Granite41-8B, Ministral3-14B | Cogito-14B, Gemma4-12B, Granite41-8B, Ministral3-14B | 4 | 0.2075 | 1 |
| BH2_05989 | Cogito-14B, Gemma4-12B, Granite41-8B, Ministral3-14B | Cogito-14B, Ministral3-14B | 2 | 0.2075 | 0 |
| BH2_05997 | Cogito-14B, Gemma4-12B, Granite41-8B, Ministral3-14B | Cogito-14B, Granite41-8B, Ministral3-14B | 3 | 0.2075 | 1 |
| BH2_06016 | Cogito-14B, Gemma4-12B, Granite41-8B, Ministral3-14B | Cogito-14B, Gemma4-12B, Granite41-8B, Ministral3-14B | 4 | 0.2075 | 1 |
| BH2_06034 | Cogito-14B, Gemma4-12B, Granite41-8B, Ministral3-14B | Cogito-14B, Ministral3-14B | 2 | 0.2075 | 0 |

All 75 per-query rows: results/exploratory/ic/ic_per_query.csv.
