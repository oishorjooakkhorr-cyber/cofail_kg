# Table 5 — Counterfactual (illustrative cases)

**Status:** DESCRIPTIVE, TREATMENT-ONLY, EXPLORATORY (D7 DESCRIPTIVE). Per case only.

**Basis:** protocol §21; docs/decision_log.md, entry 2026-11-12 "S30 — Plan after D7", section A4; docs/decision_log.md, entry 2026-11-13 "S36 — Readings of the §21 outcomes"

Produced by `scripts/38_final_tables.py` at commit `d6a00137dc22cbec6f9d537432a0166f5d0f9c6b` (tracked files clean: True; producing code committed at this commit: True).

Inputs (SHA256 in `provenance.json`; last commit that touched each):

- `results/interventions/s36/s36.json` — d4e49446babc6666fdf2cf004328fb13b00206f0

No aggregate ΔCF and no τ_CF are computed: both need a matched control, and none exists (C = 0). Hiding the label removes the answers reached through it by construction (decision log 2026-11-12, A4); these tables state observed counts only.

Run commits (from s36.json): after: intervention_v1 @ c4b854ac946ed8283910120b6670a33cbc6cc89f; before: expansion_v1 @ b8209e6c80a3ee4b1c263bc1479879ca74029110, pilot_v1 @ 46902dccc533fff1e3c617251ce730d996df7e9d (Gemma4-12B); 5e69e2391fb8b3f4c7722a91917200febe59c556 (Cogito-14B, Granite41-8B, Ministral3-14B); reference: repeat_v1 @ 1b36d37aed6c20b1d272575c3322bb36eefff672.

## 5a. CF3/CF4 and PCF per case: before / after treatment / after control

CSV: `table05a_cofailure_before_after.csv`

| Case | Mechanism | Hidden (surgery) | Metric | Before | After treatment | After control |
|---|---|---|---|---|---|---|
| BH2_03356 | WRONG_TURN_HOP2 | `off-label use` at 33618 (step 2) | CF3^Q | 1 | 0 | no control (C = 0) |
| BH2_03356 | WRONG_TURN_HOP2 | `off-label use` at 33618 (step 2) | CF4^Q | 0 | 0 | no control (C = 0) |
| BH2_03356 | WRONG_TURN_HOP2 | `off-label use` at 33618 (step 2) | CF3^Q grounded | 1 | 0 | no control (C = 0) |
| BH2_03356 | WRONG_TURN_HOP2 | `off-label use` at 33618 (step 2) | CF4^Q grounded | 0 | 0 | no control (C = 0) |
| BH2_03356 | WRONG_TURN_HOP2 | `off-label use` at 33618 (step 2) | CF3^{Q,H1} | 1 | 0 | no control (C = 0) |
| BH2_03356 | WRONG_TURN_HOP2 | `off-label use` at 33618 (step 2) | CF4^{Q,H1} | 0 | 0 | no control (C = 0) |
| BH2_03356 | WRONG_TURN_HOP2 | `off-label use` at 33618 (step 2) | PCF_REL3 | 1 | 0 | no control (C = 0) |
| BH2_03356 | WRONG_TURN_HOP2 | `off-label use` at 33618 (step 2) | PCF_REL4 | 0 | 0 | no control (C = 0) |
| BH2_03356 | WRONG_TURN_HOP2 | `off-label use` at 33618 (step 2) | PCF_NODE3 | 0 | 0 | no control (C = 0) |
| BH2_03356 | WRONG_TURN_HOP2 | `off-label use` at 33618 (step 2) | PCF_NODE4 | 0 | 0 | no control (C = 0) |
| BH2_03356 | WRONG_TURN_HOP2 | `off-label use` at 33618 (step 2) | PCF_SHORTCUT3 | 0 | 0 | no control (C = 0) |
| BH2_04650 | SHORTCUT | `drug_protein` at 16843 (step 1) | CF3^Q | 1 | 0 | no control (C = 0) |
| BH2_04650 | SHORTCUT | `drug_protein` at 16843 (step 1) | CF4^Q | 0 | 0 | no control (C = 0) |
| BH2_04650 | SHORTCUT | `drug_protein` at 16843 (step 1) | CF3^Q grounded | 1 | 0 | no control (C = 0) |
| BH2_04650 | SHORTCUT | `drug_protein` at 16843 (step 1) | CF4^Q grounded | 0 | 0 | no control (C = 0) |
| BH2_04650 | SHORTCUT | `drug_protein` at 16843 (step 1) | CF3^{Q,H1} | 0 | 0 | no control (C = 0) |
| BH2_04650 | SHORTCUT | `drug_protein` at 16843 (step 1) | CF4^{Q,H1} | 0 | 0 | no control (C = 0) |
| BH2_04650 | SHORTCUT | `drug_protein` at 16843 (step 1) | PCF_REL3 | 1 | 0 | no control (C = 0) |
| BH2_04650 | SHORTCUT | `drug_protein` at 16843 (step 1) | PCF_REL4 | 0 | 0 | no control (C = 0) |
| BH2_04650 | SHORTCUT | `drug_protein` at 16843 (step 1) | PCF_NODE3 | 0 | 0 | no control (C = 0) |
| BH2_04650 | SHORTCUT | `drug_protein` at 16843 (step 1) | PCF_NODE4 | 0 | 0 | no control (C = 0) |
| BH2_04650 | SHORTCUT | `drug_protein` at 16843 (step 1) | PCF_SHORTCUT3 | 1 | 0 | no control (C = 0) |
| BH2_05290 | WRONG_TURN_HOP2 | `off-label use` at 14052 (step 2) | CF3^Q | 1 | 0 | no control (C = 0) |
| BH2_05290 | WRONG_TURN_HOP2 | `off-label use` at 14052 (step 2) | CF4^Q | 0 | 0 | no control (C = 0) |
| BH2_05290 | WRONG_TURN_HOP2 | `off-label use` at 14052 (step 2) | CF3^Q grounded | 1 | 0 | no control (C = 0) |
| BH2_05290 | WRONG_TURN_HOP2 | `off-label use` at 14052 (step 2) | CF4^Q grounded | 0 | 0 | no control (C = 0) |
| BH2_05290 | WRONG_TURN_HOP2 | `off-label use` at 14052 (step 2) | CF3^{Q,H1} | 1 | 0 | no control (C = 0) |
| BH2_05290 | WRONG_TURN_HOP2 | `off-label use` at 14052 (step 2) | CF4^{Q,H1} | 0 | 0 | no control (C = 0) |
| BH2_05290 | WRONG_TURN_HOP2 | `off-label use` at 14052 (step 2) | PCF_REL3 | 1 | 0 | no control (C = 0) |
| BH2_05290 | WRONG_TURN_HOP2 | `off-label use` at 14052 (step 2) | PCF_REL4 | 0 | 0 | no control (C = 0) |
| BH2_05290 | WRONG_TURN_HOP2 | `off-label use` at 14052 (step 2) | PCF_NODE3 | 0 | 0 | no control (C = 0) |
| BH2_05290 | WRONG_TURN_HOP2 | `off-label use` at 14052 (step 2) | PCF_NODE4 | 0 | 0 | no control (C = 0) |
| BH2_05290 | WRONG_TURN_HOP2 | `off-label use` at 14052 (step 2) | PCF_SHORTCUT3 | 0 | 0 | no control (C = 0) |
| BH2_05997 | WRONG_TURN_HOP2 | `off-label use` at 33228 (step 2) | CF3^Q | 1 | 0 | no control (C = 0) |
| BH2_05997 | WRONG_TURN_HOP2 | `off-label use` at 33228 (step 2) | CF4^Q | 0 | 0 | no control (C = 0) |
| BH2_05997 | WRONG_TURN_HOP2 | `off-label use` at 33228 (step 2) | CF3^Q grounded | 1 | 0 | no control (C = 0) |
| BH2_05997 | WRONG_TURN_HOP2 | `off-label use` at 33228 (step 2) | CF4^Q grounded | 0 | 0 | no control (C = 0) |
| BH2_05997 | WRONG_TURN_HOP2 | `off-label use` at 33228 (step 2) | CF3^{Q,H1} | 1 | 0 | no control (C = 0) |
| BH2_05997 | WRONG_TURN_HOP2 | `off-label use` at 33228 (step 2) | CF4^{Q,H1} | 0 | 0 | no control (C = 0) |
| BH2_05997 | WRONG_TURN_HOP2 | `off-label use` at 33228 (step 2) | PCF_REL3 | 1 | 0 | no control (C = 0) |
| BH2_05997 | WRONG_TURN_HOP2 | `off-label use` at 33228 (step 2) | PCF_REL4 | 0 | 0 | no control (C = 0) |
| BH2_05997 | WRONG_TURN_HOP2 | `off-label use` at 33228 (step 2) | PCF_NODE3 | 0 | 0 | no control (C = 0) |
| BH2_05997 | WRONG_TURN_HOP2 | `off-label use` at 33228 (step 2) | PCF_NODE4 | 0 | 0 | no control (C = 0) |
| BH2_05997 | WRONG_TURN_HOP2 | `off-label use` at 33228 (step 2) | PCF_SHORTCUT3 | 0 | 0 | no control (C = 0) |
| BH2_06016 | WRONG_TURN_HOP2 | `off-label use` at 30800 (step 2) | CF3^Q | 1 | 0 | no control (C = 0) |
| BH2_06016 | WRONG_TURN_HOP2 | `off-label use` at 30800 (step 2) | CF4^Q | 1 | 0 | no control (C = 0) |
| BH2_06016 | WRONG_TURN_HOP2 | `off-label use` at 30800 (step 2) | CF3^Q grounded | 1 | 0 | no control (C = 0) |
| BH2_06016 | WRONG_TURN_HOP2 | `off-label use` at 30800 (step 2) | CF4^Q grounded | 1 | 0 | no control (C = 0) |
| BH2_06016 | WRONG_TURN_HOP2 | `off-label use` at 30800 (step 2) | CF3^{Q,H1} | 1 | 0 | no control (C = 0) |
| BH2_06016 | WRONG_TURN_HOP2 | `off-label use` at 30800 (step 2) | CF4^{Q,H1} | 1 | 0 | no control (C = 0) |
| BH2_06016 | WRONG_TURN_HOP2 | `off-label use` at 30800 (step 2) | PCF_REL3 | 1 | 0 | no control (C = 0) |
| BH2_06016 | WRONG_TURN_HOP2 | `off-label use` at 30800 (step 2) | PCF_REL4 | 1 | 0 | no control (C = 0) |
| BH2_06016 | WRONG_TURN_HOP2 | `off-label use` at 30800 (step 2) | PCF_NODE3 | 0 | 0 | no control (C = 0) |
| BH2_06016 | WRONG_TURN_HOP2 | `off-label use` at 30800 (step 2) | PCF_NODE4 | 0 | 0 | no control (C = 0) |
| BH2_06016 | WRONG_TURN_HOP2 | `off-label use` at 30800 (step 2) | PCF_SHORTCUT3 | 0 | 0 | no control (C = 0) |

Before = pilot_v1/expansion_v1 (results of record); after treatment = intervention_v1. No matched control exists for any case (C = 0, §21: treatment-only exploratory).

## 5b. Recovery and no-answer change per case

CSV: `table05b_recovery_no_answer.csv`

| Case | Holders | Recovered after | Holders with SUCCESS after | Recovery share after | Recovered, repeat_v1 reference | Holders with SUCCESS, repeat_v1 | No-answer before | SUCCESS episodes before | No-answer rate before | No-answer after | SUCCESS episodes after | No-answer rate after | Technical failures after (holders) | Technical failures, repeat_v1 (holders) | Control |
|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|
| BH2_03356 | Granite41-8B, Ministral3-14B, Cogito-14B | 2 | 2 | 1.0000 | 0 | 2 | 0 | 4 | 0.0000 | 0 | 3 | 0.0000 | Ministral3-14B: PARSE_FAIL | Ministral3-14B: PARSE_FAIL | no control (C = 0) |
| BH2_04650 | Granite41-8B, Ministral3-14B, Cogito-14B | 2 | 3 | 0.6667 | 0 | 3 | 0 | 4 | 0.0000 | 0 | 4 | 0.0000 | — | — | no control (C = 0) |
| BH2_05290 | Gemma4-12B, Granite41-8B, Cogito-14B | 3 | 3 | 1.0000 | 0 | 3 | 0 | 4 | 0.0000 | 0 | 3 | 0.0000 | — | — | no control (C = 0) |
| BH2_05997 | Granite41-8B, Ministral3-14B, Cogito-14B | 3 | 3 | 1.0000 | 0 | 3 | 0 | 4 | 0.0000 | 0 | 4 | 0.0000 | — | — | no control (C = 0) |
| BH2_06016 | Gemma4-12B, Granite41-8B, Ministral3-14B, Cogito-14B | 4 | 4 | 1.0000 | 0 | 4 | 0 | 4 | 0.0000 | 0 | 4 | 0.0000 | — | — | no control (C = 0) |

Recovery = holders (SUCCESS after-episodes only) with ≥ 1 resolved answer, all question-valid. No-answer rate = SUCCESS episodes with 0 resolved answers / SUCCESS episodes, all 4 agents. repeat_v1 is a descriptive reference for run-to-run variation; it never replaces 'before'.

## 5c. Displacement per holder (one category = result of record; answer counts descriptive)

CSV: `table05c_displacement_per_holder.csv`

| Case | Holder | Before: VALID_RELATION answers | Before: SAME_WRONG_RELATION_OTHER_NEIGHBOR answers | Before: OTHER_WRONG answers | After: status | After: category | After: VALID_RELATION answers | After: SAME_WRONG_RELATION_OTHER_NEIGHBOR answers | After: OTHER_WRONG answers | repeat_v1: status | repeat_v1: category | repeat_v1: VALID_RELATION answers | repeat_v1: SAME_WRONG_RELATION_OTHER_NEIGHBOR answers | repeat_v1: OTHER_WRONG answers |
|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|
| BH2_03356 | Granite41-8B | 14 | 0 | 21 | SUCCESS | VALID_RELATION | 14 | 0 | 0 | SUCCESS | OTHER_WRONG | 14 | 0 | 21 |
| BH2_03356 | Ministral3-14B | 14 | 0 | 20 | PARSE_FAIL | — | — | — | — | PARSE_FAIL | — | — | — | — |
| BH2_03356 | Cogito-14B | 14 | 0 | 21 | SUCCESS | VALID_RELATION | 14 | 0 | 0 | SUCCESS | OTHER_WRONG | 14 | 0 | 21 |
| BH2_04650 | Granite41-8B | 0 | 0 | 5 | SUCCESS | OTHER_WRONG | 13 | 0 | 7 | SUCCESS | OTHER_WRONG | 0 | 0 | 5 |
| BH2_04650 | Ministral3-14B | 0 | 0 | 5 | SUCCESS | VALID_RELATION | 13 | 0 | 0 | SUCCESS | OTHER_WRONG | 0 | 0 | 5 |
| BH2_04650 | Cogito-14B | 0 | 0 | 5 | SUCCESS | VALID_RELATION | 13 | 0 | 0 | SUCCESS | OTHER_WRONG | 0 | 0 | 5 |
| BH2_05290 | Gemma4-12B | 2 | 0 | 2 | SUCCESS | VALID_RELATION | 2 | 0 | 0 | SUCCESS | OTHER_WRONG | 2 | 0 | 2 |
| BH2_05290 | Granite41-8B | 2 | 0 | 2 | SUCCESS | VALID_RELATION | 2 | 0 | 0 | SUCCESS | OTHER_WRONG | 2 | 0 | 2 |
| BH2_05290 | Cogito-14B | 2 | 0 | 2 | SUCCESS | VALID_RELATION | 2 | 0 | 0 | SUCCESS | OTHER_WRONG | 2 | 0 | 2 |
| BH2_05997 | Granite41-8B | 4 | 0 | 4 | SUCCESS | VALID_RELATION | 4 | 0 | 0 | SUCCESS | OTHER_WRONG | 4 | 0 | 4 |
| BH2_05997 | Ministral3-14B | 4 | 0 | 2 | SUCCESS | VALID_RELATION | 4 | 0 | 0 | SUCCESS | OTHER_WRONG | 4 | 0 | 2 |
| BH2_05997 | Cogito-14B | 4 | 0 | 2 | SUCCESS | VALID_RELATION | 4 | 0 | 0 | SUCCESS | OTHER_WRONG | 4 | 0 | 2 |
| BH2_06016 | Gemma4-12B | 24 | 0 | 8 | SUCCESS | VALID_RELATION | 24 | 0 | 0 | SUCCESS | OTHER_WRONG | 24 | 0 | 8 |
| BH2_06016 | Granite41-8B | 24 | 0 | 8 | SUCCESS | VALID_RELATION | 24 | 0 | 0 | SUCCESS | OTHER_WRONG | 24 | 0 | 8 |
| BH2_06016 | Ministral3-14B | 24 | 0 | 8 | SUCCESS | VALID_RELATION | 24 | 0 | 0 | SUCCESS | OTHER_WRONG | 24 | 0 | 8 |
| BH2_06016 | Cogito-14B | 24 | 0 | 8 | SUCCESS | VALID_RELATION | 24 | 0 | 0 | SUCCESS | OTHER_WRONG | 24 | 0 | 8 |

Category order (decision log 2026-11-13, S36 readings, item 3): NO_ANSWER, SAME_WRONG_RELATION_OTHER_NEIGHBOR, OTHER_WRONG, VALID_RELATION. A holder with a non-SUCCESS episode has no category and is left out of the denominators.

## 5d. Displacement counts per case (holders with a SUCCESS after-episode)

CSV: `table05d_displacement_per_case.csv`

| Case | Mechanism | VALID_RELATION | SAME_WRONG_RELATION_OTHER_NEIGHBOR | OTHER_WRONG | NO_ANSWER | Excluded (technical failure) | SAME_WRONG_RELATION_OTHER_NEIGHBOR possible |
|---|---|---|---|---|---|---|---|
| BH2_03356 | WRONG_TURN_HOP2 | 2 | 0 | 0 | 0 | 1 | yes |
| BH2_04650 | SHORTCUT | 2 | 0 | 1 | 0 | 0 | no |
| BH2_05290 | WRONG_TURN_HOP2 | 3 | 0 | 0 | 0 | 0 | yes |
| BH2_05997 | WRONG_TURN_HOP2 | 3 | 0 | 0 | 0 | 0 | yes |
| BH2_06016 | WRONG_TURN_HOP2 | 4 | 0 | 0 | 0 | 0 | yes |

For the SHORTCUT case (u = s, step 1) SAME_WRONG_RELATION_OTHER_NEIGHBOR cannot occur: step 1 always starts at s.
