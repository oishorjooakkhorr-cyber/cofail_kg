# Table 6 — B1 — Off-label opportunity and uptake

**Status:** EXPLORATORY (protocol §20)

**Basis:** docs/decision_log.md, entry 2026-11-12 "S30 — Plan after D7", section B1; docs/decision_log.md, entries 2026-11-12 "B1 — Readings of the B1 definitions" and 2026-11-13 "B1 — Outcome NOT CLEAN; follow-up not run; no full run"

Produced by `scripts/38_final_tables.py` at commit `d6a00137dc22cbec6f9d537432a0166f5d0f9c6b` (tracked files clean: True; producing code committed at this commit: True).

Inputs (SHA256 in `provenance.json`; last commit that touched each):

- `results/exploratory/b1/b1_table.csv` — 5ea1abd32253df9e8d8e4b31ef0d0221bb7b9796
- `results/exploratory/b1/b1.json` — 5ea1abd32253df9e8d8e4b31ef0d0221bb7b9796

Produced by scripts/40_b1_uptake.py at commit 347363f562b699c5db7aec0a9c188ffaa41c7228.

## 6a. Opportunity, opened and taken per agent (SUCCESS episodes, latest attempts); treat-final primary, treat-first descriptive

CSV: `table06a_uptake.csv`

| View | Group | Agent | Episodes | Opportunity | Opened | Taken | Taken ∧ Opportunity | Taken ∧ Opened | Taken outside Opportunity | Uptake = Taken∧Opp / Opp | Opened / Opp | Taken∧Opened / Opened |
|---|---|---|---|---|---|---|---|---|---|---|---|---|
| All queries | treat-final | Gemma4-12B | 75 | 35 | 6 | 6 | 6 | 6 | 0 | 0.1714 | 0.1714 | 1.0000 |
| All queries | treat-final | Granite41-8B | 75 | 28 | 11 | 8 | 8 | 8 | 0 | 0.2857 | 0.3929 | 0.7273 |
| All queries | treat-final | Ministral3-14B | 66 | 30 | 19 | 18 | 18 | 18 | 0 | 0.6000 | 0.6333 | 0.9474 |
| All queries | treat-final | Cogito-14B | 74 | 33 | 29 | 25 | 25 | 25 | 0 | 0.7576 | 0.8788 | 0.8621 |
| All queries | treat-first | Gemma4-12B | 356 | 192 | 1 | 1 | 1 | 1 | 0 | 0.0052 | 0.0052 | 1.0000 |
| All queries | treat-first | Granite41-8B | 345 | 185 | 1 | 0 | 0 | 0 | 0 | 0.0000 | 0.0054 | 0.0000 |
| All queries | treat-first | Ministral3-14B | 324 | 168 | 6 | 4 | 4 | 4 | 0 | 0.0238 | 0.0357 | 0.6667 |
| All queries | treat-first | Cogito-14B | 323 | 166 | 17 | 3 | 3 | 3 | 0 | 0.0181 | 0.1024 | 0.1765 |
| Without SOURCE_NAME_OVERLAP | treat-final | Gemma4-12B | 72 | 34 | 5 | 5 | 5 | 5 | 0 | 0.1471 | 0.1471 | 1.0000 |
| Without SOURCE_NAME_OVERLAP | treat-final | Granite41-8B | 72 | 27 | 10 | 7 | 7 | 7 | 0 | 0.2593 | 0.3704 | 0.7000 |
| Without SOURCE_NAME_OVERLAP | treat-final | Ministral3-14B | 63 | 29 | 18 | 17 | 17 | 17 | 0 | 0.5862 | 0.6207 | 0.9444 |
| Without SOURCE_NAME_OVERLAP | treat-final | Cogito-14B | 71 | 32 | 28 | 24 | 24 | 24 | 0 | 0.7500 | 0.8750 | 0.8571 |
| Without SOURCE_NAME_OVERLAP | treat-first | Gemma4-12B | 356 | 192 | 1 | 1 | 1 | 1 | 0 | 0.0052 | 0.0052 | 1.0000 |
| Without SOURCE_NAME_OVERLAP | treat-first | Granite41-8B | 345 | 185 | 1 | 0 | 0 | 0 | 0 | 0.0000 | 0.0054 | 0.0000 |
| Without SOURCE_NAME_OVERLAP | treat-first | Ministral3-14B | 324 | 168 | 6 | 4 | 4 | 4 | 0 | 0.0238 | 0.0357 | 0.6667 |
| Without SOURCE_NAME_OVERLAP | treat-first | Cogito-14B | 323 | 166 | 17 | 3 | 3 | 3 | 0 | 0.0181 | 0.1024 | 0.1765 |

## 6b. CLEAN / NOT CLEAN (rule fixed 2026-11-12)

CSV: `table06b_outcome.csv`

| View | Group | Rule | Agents meeting | Count | Outcome | Use |
|---|---|---|---|---|---|---|
| All queries | treat-final | at least 3 of the 4 agents have >= 5 opportunity episodes and uptake >= 0.50 | Ministral3-14B, Cogito-14B | 2 | NOT CLEAN | outcome (primary) |
| Without SOURCE_NAME_OVERLAP | treat-final | at least 3 of the 4 agents have >= 5 opportunity episodes and uptake >= 0.50 | Ministral3-14B, Cogito-14B | 2 | NOT CLEAN | descriptive only |

## 6c. Non-SUCCESS episodes excluded (latest attempts)

CSV: `table06c_excluded_episodes.csv`

| Group | Agent | Excluded | By status |
|---|---|---|---|
| treat-final | Gemma4-12B | 0 | — |
| treat-final | Granite41-8B | 0 | — |
| treat-final | Ministral3-14B | 9 | PARSE_FAIL: 9 |
| treat-final | Cogito-14B | 1 | ERROR: 1 |
| treat-first | Gemma4-12B | 2 | PARSE_FAIL: 2 |
| treat-first | Granite41-8B | 13 | ERROR: 1, PARSE_FAIL: 12 |
| treat-first | Ministral3-14B | 34 | ERROR: 5, PARSE_FAIL: 29 |
| treat-first | Cogito-14B | 35 | ERROR: 33, PARSE_FAIL: 2 |
