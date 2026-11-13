# IC — Independence check of off-label uptake (EXPLORATORY)

EXPLORATORY (protocol §20) — docs/decision_log.md, entry 2026-11-13 "IC — Independence check of off-label uptake" (rule fixed before computing). Treat-final queries; SUCCESS episodes, latest attempts, as in B1.

Produced by `scripts/44_independence_check.py` at commit `8131d088cc0ea937071cdca990a2d9c26ff7831b` (tracked files clean: True). Inputs: `results/exploratory/b1/b1_episodes.csv` (SHA256 `8d87f8de6c54f6c33176746cd066722162000b0c3fb4561b58fbae3aeed883de`), `results/combined/pilot_expansion_v1/cofailure.json` (SHA256 `198b9aa18770d1a815429361be8f79601330276642665feb025783dd5560f87d`).

## All queries (primary)

**Outcome: AGREES** — T_obs = 6; under independence E[T] = 5.510, central 95% range 2–10; P(T ≥ 6) = 0.4820, P(T ≤ 6) = 0.6940.

| Agent | Opportunity | Taken ∧ Opportunity | p_i |
|---|---|---|---|
| Cogito-14B | 33 | 25 | 0.758 |
| Gemma4-12B | 35 | 6 | 0.171 |
| Granite41-8B | 28 | 8 | 0.286 |
| Ministral3-14B | 30 | 18 | 0.600 |

Queries: 75 (35 with ≥ 1 agent in A_q). Pairs statistic (descriptive): S_obs = 40, expected 32.05.

Queries with K_q ≥ 2 or CF3^{Q,H1} = 1:

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
| BH2_05812 | Cogito-14B, Gemma4-12B | Cogito-14B, Gemma4-12B | 2 | 0.0000 | 0 |
| BH2_05838 | Cogito-14B, Gemma4-12B, Granite41-8B, Ministral3-14B | Cogito-14B, Ministral3-14B | 2 | 0.2075 | 0 |
| BH2_05852 | Cogito-14B, Gemma4-12B, Granite41-8B, Ministral3-14B | Cogito-14B, Ministral3-14B | 2 | 0.2075 | 0 |
| BH2_05856 | Cogito-14B, Gemma4-12B, Granite41-8B, Ministral3-14B | Cogito-14B, Ministral3-14B | 2 | 0.2075 | 0 |
| BH2_05890 | Cogito-14B, Gemma4-12B, Granite41-8B, Ministral3-14B | Cogito-14B, Gemma4-12B, Granite41-8B, Ministral3-14B | 4 | 0.2075 | 1 |
| BH2_05989 | Cogito-14B, Gemma4-12B, Granite41-8B, Ministral3-14B | Cogito-14B, Ministral3-14B | 2 | 0.2075 | 0 |
| BH2_05997 | Cogito-14B, Gemma4-12B, Granite41-8B, Ministral3-14B | Cogito-14B, Granite41-8B, Ministral3-14B | 3 | 0.2075 | 1 |
| BH2_06016 | Cogito-14B, Gemma4-12B, Granite41-8B, Ministral3-14B | Cogito-14B, Gemma4-12B, Granite41-8B, Ministral3-14B | 4 | 0.2075 | 1 |
| BH2_06034 | Cogito-14B, Gemma4-12B, Granite41-8B, Ministral3-14B | Cogito-14B, Ministral3-14B | 2 | 0.2075 | 0 |

## Without SOURCE_NAME_OVERLAP queries (protocol §19.1; descriptive, p_i recomputed)

Outcome rule applied here (descriptive, not the outcome): AGREES — T_obs = 5; E[T] = 4.555, range 1–9; P(T ≥ obs) = 0.4878, P(T ≤ obs) = 0.7014.

| Agent | Opportunity | Taken ∧ Opportunity | p_i |
|---|---|---|---|
| Cogito-14B | 32 | 24 | 0.750 |
| Gemma4-12B | 34 | 5 | 0.147 |
| Granite41-8B | 27 | 7 | 0.259 |
| Ministral3-14B | 29 | 17 | 0.586 |

Queries: 72 (34 with ≥ 1 agent in A_q). Pairs statistic (descriptive): S_obs = 34, expected 28.07.

Limits (logged with the rule): p_i is estimated from the same episodes; queries whose off-label lists are more tempting would also appear as MORE CLUSTERED. Agents never share anything (§9.3); "independent" means only that each agent's own rate explains the pattern.
