# B1 — Off-label opportunity and uptake (EXPLORATORY)

EXPLORATORY (protocol §20) — docs/decision_log.md, entry 2026-11-12 "Plan after D7", section B1, with the readings of the entry 2026-11-12 "B1 — Readings of the B1 definitions". Treat-final is primary; treat-first is descriptive only.

Produced by `scripts/40_b1_uptake.py` at commit `347363f562b699c5db7aec0a9c188ffaa41c7228` (tracked files clean: True). Runs: `expansion_v1`, `pilot_v1`. Latest attempts, SUCCESS episodes only.

**B1 (treat-final, all queries): NOT CLEAN** — 2 of 4 agents meet the rule (at least 3 of the 4 agents have >= 5 opportunity episodes and uptake >= 0.50): Ministral3-14B, Cogito-14B.

## Table 1 — treat-final, All queries (primary)

| Agent | Episodes | Opportunity | Opened | Taken | Taken outside Opportunity | Uptake = Taken∧Opp / Opp | Opened / Opp | Taken∧Opened / Opened |
|---|---|---|---|---|---|---|---|---|
| Gemma4-12B | 75 | 35 | 6 | 6 | 0 | 0.171 (6/35) | 0.171 (6/35) | 1.000 (6/6) |
| Granite41-8B | 75 | 28 | 11 | 8 | 0 | 0.286 (8/28) | 0.393 (11/28) | 0.727 (8/11) |
| Ministral3-14B | 66 | 30 | 19 | 18 | 0 | 0.600 (18/30) | 0.633 (19/30) | 0.947 (18/19) |
| Cogito-14B | 74 | 33 | 29 | 25 | 0 | 0.758 (25/33) | 0.879 (29/33) | 0.862 (25/29) |

## Table 2 — treat-first, All queries (descriptive)

| Agent | Episodes | Opportunity | Opened | Taken | Taken outside Opportunity | Uptake = Taken∧Opp / Opp | Opened / Opp | Taken∧Opened / Opened |
|---|---|---|---|---|---|---|---|---|
| Gemma4-12B | 356 | 192 | 1 | 1 | 0 | 0.005 (1/192) | 0.005 (1/192) | 1.000 (1/1) |
| Granite41-8B | 345 | 185 | 1 | 0 | 0 | 0.000 (0/185) | 0.005 (1/185) | 0.000 (0/1) |
| Ministral3-14B | 324 | 168 | 6 | 4 | 0 | 0.024 (4/168) | 0.036 (6/168) | 0.667 (4/6) |
| Cogito-14B | 323 | 166 | 17 | 3 | 0 | 0.018 (3/166) | 0.102 (17/166) | 0.176 (3/17) |

## Table 3 — treat-final, Without SOURCE_NAME_OVERLAP queries (BH2_05778, BH2_05971, BH2_06099; protocol §19.1; descriptive) (descriptive)

| Agent | Episodes | Opportunity | Opened | Taken | Taken outside Opportunity | Uptake = Taken∧Opp / Opp | Opened / Opp | Taken∧Opened / Opened |
|---|---|---|---|---|---|---|---|---|
| Gemma4-12B | 72 | 34 | 5 | 5 | 0 | 0.147 (5/34) | 0.147 (5/34) | 1.000 (5/5) |
| Granite41-8B | 72 | 27 | 10 | 7 | 0 | 0.259 (7/27) | 0.370 (10/27) | 0.700 (7/10) |
| Ministral3-14B | 63 | 29 | 18 | 17 | 0 | 0.586 (17/29) | 0.621 (18/29) | 0.944 (17/18) |
| Cogito-14B | 71 | 32 | 28 | 24 | 0 | 0.750 (24/32) | 0.875 (28/32) | 0.857 (24/28) |

## Table 4 — treat-first, Without SOURCE_NAME_OVERLAP queries (BH2_05778, BH2_05971, BH2_06099; protocol §19.1; descriptive) (descriptive)

| Agent | Episodes | Opportunity | Opened | Taken | Taken outside Opportunity | Uptake = Taken∧Opp / Opp | Opened / Opp | Taken∧Opened / Opened |
|---|---|---|---|---|---|---|---|---|
| Gemma4-12B | 356 | 192 | 1 | 1 | 0 | 0.005 (1/192) | 0.005 (1/192) | 1.000 (1/1) |
| Granite41-8B | 345 | 185 | 1 | 0 | 0 | 0.000 (0/185) | 0.005 (1/185) | 0.000 (0/1) |
| Ministral3-14B | 324 | 168 | 6 | 4 | 0 | 0.024 (4/168) | 0.036 (6/168) | 0.667 (4/6) |
| Cogito-14B | 323 | 166 | 17 | 3 | 0 | 0.018 (3/166) | 0.102 (17/166) | 0.176 (3/17) |

Rule applied to the view without SOURCE_NAME_OVERLAP queries (descriptive, not the outcome): NOT CLEAN (2 of 4 agents).

Non-SUCCESS episodes excluded (latest attempts): treat-final: Gemma4-12B 0, Granite41-8B 0, Ministral3-14B 9, Cogito-14B 1; treat-first: Gemma4-12B 2, Granite41-8B 13, Ministral3-14B 34, Cogito-14B 35.

Per-episode detail: `b1_episodes.csv`. Definitions: see the docstring of the script and the two decision-log entries named above.
