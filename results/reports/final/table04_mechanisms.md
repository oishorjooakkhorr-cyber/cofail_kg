# Table 4 — Mechanisms

**Status:** Results of record: pilot_v1 + expansion_v1, 500 queries × 4 agents, latest attempts (protocol §19); Gate D7 DESCRIPTIVE (decision log 2026-11-12). Descriptive.

**Basis:** protocol §14.2, §15, §16.3, §21; strata §5.2, §5.3, §7.1

Produced by `scripts/38_final_tables.py` at commit `d6a00137dc22cbec6f9d537432a0166f5d0f9c6b` (tracked files clean: True; producing code committed at this commit: True).

Inputs (SHA256 in `provenance.json`; last commit that touched each):

- `results/combined/pilot_expansion_v1/components.json` — 02e0182f404610727741a6407169dbbe201671e7
- `data/processed/manifests/expansion.jsonl` — a0c586781ba30484b9589fd2cc96b79d4e2a5afc
- `results/runs/expansion_v1/analysis/metrics` — 02e0182f404610727741a6407169dbbe201671e7
- `data/processed/manifests/pilot.jsonl` — a0c586781ba30484b9589fd2cc96b79d4e2a5afc
- `results/runs/pilot_v1/analysis/metrics` — d43af3085a82a5d3706b97f6ad5de6441d5d0b69
- `results/combined/pilot_expansion_v1/cofailure.json` — 02e0182f404610727741a6407169dbbe201671e7
- `results/interventions/candidates.csv` — 52d5c885699a4827078f1bc504fcf05f2a902830

## 4a. Answer-level path reason codes (§14.2, primary path) and early stop (§15) by stratum, all agents pooled

CSV: `table04a_reason_codes_by_stratum.csv`

| View | Stratum | Value | Queries | SUCCESS episodes | PATH_INVALID answers | SHORTCUT | WRONG_RELATION_HOP1 | WRONG_RELATION_HOP2 | WRONG_BRIDGE_TYPE | WRONG_TARGET_TYPE | WRONG_HOP_COUNT | Early-stop episodes | Early stop defined | Early-stop share |
|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|
| All queries | All | All | 500 | 1892 | 1999 | 977 | 264 | 398 | 6 | 133 | 360 | 670 | 1892 | 0.3541 |
| All queries | Relation type | disease:drug:effect/phenotype | 336 | 1266 | 570 | 165 | 258 | 0 | 0 | 126 | 147 | 666 | 1266 | 0.5261 |
| All queries | Relation type | disease:drug:gene/protein | 8 | 30 | 64 | 57 | 6 | 0 | 6 | 7 | 1 | 0 | 30 | 0.0000 |
| All queries | Relation type | disease:gene/protein:drug | 16 | 63 | 22 | 22 | 0 | 0 | 0 | 0 | 0 | 0 | 63 | 0.0000 |
| All queries | Relation type | drug:disease:effect/phenotype | 6 | 23 | 340 | 340 | 0 | 0 | 0 | 0 | 0 | 0 | 23 | 0.0000 |
| All queries | Relation type | drug:disease:gene/protein | 8 | 29 | 65 | 65 | 0 | 0 | 0 | 0 | 0 | 0 | 29 | 0.0000 |
| All queries | Relation type | drug:gene/protein:disease | 51 | 191 | 28 | 28 | 0 | 0 | 0 | 0 | 0 | 0 | 191 | 0.0000 |
| All queries | Relation type | effect/phenotype:disease:drug | 55 | 215 | 710 | 176 | 0 | 322 | 0 | 0 | 212 | 4 | 215 | 0.0186 |
| All queries | Relation type | gene/protein:disease:drug | 11 | 41 | 176 | 106 | 0 | 70 | 0 | 0 | 0 | 0 | 41 | 0.0000 |
| All queries | Relation type | gene/protein:drug:disease | 9 | 34 | 24 | 18 | 0 | 6 | 0 | 0 | 0 | 0 | 34 | 0.0000 |
| All queries | Ambiguity tag | BOTH_AMBIGUOUS | 61 | 238 | 1050 | 516 | 0 | 322 | 0 | 0 | 212 | 4 | 238 | 0.0168 |
| All queries | Ambiguity tag | NONE | 67 | 254 | 50 | 50 | 0 | 0 | 0 | 0 | 0 | 0 | 254 | 0.0000 |
| All queries | Ambiguity tag | R1_AMBIGUOUS | 352 | 1325 | 699 | 287 | 264 | 0 | 6 | 133 | 148 | 666 | 1325 | 0.5026 |
| All queries | Ambiguity tag | R2_AMBIGUOUS | 20 | 75 | 200 | 124 | 0 | 76 | 0 | 0 | 0 | 0 | 75 | 0.0000 |
| All queries | Construction | BRIDGE | 164 | 626 | 1429 | 812 | 6 | 398 | 6 | 7 | 213 | 4 | 626 | 0.0064 |
| All queries | Construction | UNION | 336 | 1266 | 570 | 165 | 258 | 0 | 0 | 126 | 147 | 666 | 1266 | 0.5261 |
| All queries | Bridge multiplicity | MULTI_BRIDGE | 375 | 1420 | 989 | 341 | 146 | 241 | 0 | 126 | 261 | 665 | 1420 | 0.4683 |
| All queries | Bridge multiplicity | SINGLE_BRIDGE | 125 | 472 | 1010 | 636 | 118 | 157 | 6 | 7 | 99 | 5 | 472 | 0.0106 |
| Without SOURCE_NAME_OVERLAP | All | All | 497 | 1880 | 1956 | 977 | 264 | 355 | 6 | 133 | 360 | 670 | 1880 | 0.3564 |
| Without SOURCE_NAME_OVERLAP | Relation type | disease:drug:effect/phenotype | 336 | 1266 | 570 | 165 | 258 | 0 | 0 | 126 | 147 | 666 | 1266 | 0.5261 |
| Without SOURCE_NAME_OVERLAP | Relation type | disease:drug:gene/protein | 8 | 30 | 64 | 57 | 6 | 0 | 6 | 7 | 1 | 0 | 30 | 0.0000 |
| Without SOURCE_NAME_OVERLAP | Relation type | disease:gene/protein:drug | 16 | 63 | 22 | 22 | 0 | 0 | 0 | 0 | 0 | 0 | 63 | 0.0000 |
| Without SOURCE_NAME_OVERLAP | Relation type | drug:disease:effect/phenotype | 6 | 23 | 340 | 340 | 0 | 0 | 0 | 0 | 0 | 0 | 23 | 0.0000 |
| Without SOURCE_NAME_OVERLAP | Relation type | drug:disease:gene/protein | 8 | 29 | 65 | 65 | 0 | 0 | 0 | 0 | 0 | 0 | 29 | 0.0000 |
| Without SOURCE_NAME_OVERLAP | Relation type | drug:gene/protein:disease | 51 | 191 | 28 | 28 | 0 | 0 | 0 | 0 | 0 | 0 | 191 | 0.0000 |
| Without SOURCE_NAME_OVERLAP | Relation type | effect/phenotype:disease:drug | 52 | 203 | 667 | 176 | 0 | 279 | 0 | 0 | 212 | 4 | 203 | 0.0197 |
| Without SOURCE_NAME_OVERLAP | Relation type | gene/protein:disease:drug | 11 | 41 | 176 | 106 | 0 | 70 | 0 | 0 | 0 | 0 | 41 | 0.0000 |
| Without SOURCE_NAME_OVERLAP | Relation type | gene/protein:drug:disease | 9 | 34 | 24 | 18 | 0 | 6 | 0 | 0 | 0 | 0 | 34 | 0.0000 |
| Without SOURCE_NAME_OVERLAP | Ambiguity tag | BOTH_AMBIGUOUS | 58 | 226 | 1007 | 516 | 0 | 279 | 0 | 0 | 212 | 4 | 226 | 0.0177 |
| Without SOURCE_NAME_OVERLAP | Ambiguity tag | NONE | 67 | 254 | 50 | 50 | 0 | 0 | 0 | 0 | 0 | 0 | 254 | 0.0000 |
| Without SOURCE_NAME_OVERLAP | Ambiguity tag | R1_AMBIGUOUS | 352 | 1325 | 699 | 287 | 264 | 0 | 6 | 133 | 148 | 666 | 1325 | 0.5026 |
| Without SOURCE_NAME_OVERLAP | Ambiguity tag | R2_AMBIGUOUS | 20 | 75 | 200 | 124 | 0 | 76 | 0 | 0 | 0 | 0 | 75 | 0.0000 |
| Without SOURCE_NAME_OVERLAP | Construction | BRIDGE | 161 | 614 | 1386 | 812 | 6 | 355 | 6 | 7 | 213 | 4 | 614 | 0.0065 |
| Without SOURCE_NAME_OVERLAP | Construction | UNION | 336 | 1266 | 570 | 165 | 258 | 0 | 0 | 126 | 147 | 666 | 1266 | 0.5261 |
| Without SOURCE_NAME_OVERLAP | Bridge multiplicity | MULTI_BRIDGE | 372 | 1408 | 946 | 341 | 146 | 198 | 0 | 126 | 261 | 665 | 1408 | 0.4723 |
| Without SOURCE_NAME_OVERLAP | Bridge multiplicity | SINGLE_BRIDGE | 125 | 472 | 1010 | 636 | 118 | 157 | 6 | 7 | 99 | 5 | 472 | 0.0106 |

Reason codes are counted over PATH_INVALID answers of SUCCESS episodes (primary path, §14.2). An answer can carry more than one code (for example WRONG_TARGET_TYPE and WRONG_HOP_COUNT), so the code columns can add up to more than the PATH_INVALID answers. WRONG_RELATION is reported as its two §14.2 codes, WRONG_RELATION_HOP1 and WRONG_RELATION_HOP2. Early stop is defined for SUCCESS episodes only (§15).

## 4b. Path reason codes per agent (§14.2: primary path and union over simple paths ≤ 3) and early stop (§15), all queries

CSV: `table04b_reason_codes_by_agent.csv`

| Agent | PATH_INVALID answers | SHORTCUT (primary) | SHORTCUT (all paths ≤ 3) | WRONG_RELATION_HOP1 (primary) | WRONG_RELATION_HOP1 (all paths ≤ 3) | WRONG_RELATION_HOP2 (primary) | WRONG_RELATION_HOP2 (all paths ≤ 3) | WRONG_BRIDGE_TYPE (primary) | WRONG_BRIDGE_TYPE (all paths ≤ 3) | WRONG_TARGET_TYPE (primary) | WRONG_TARGET_TYPE (all paths ≤ 3) | WRONG_HOP_COUNT (primary) | WRONG_HOP_COUNT (all paths ≤ 3) | Early-stop episodes | Early stop defined | Early stop NA | Early-stop share |
|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|
| Gemma4-12B | 108 | 0 | 0 | 77 | 77 | 31 | 31 | 0 | 0 | 0 | 0 | 0 | 0 | 77 | 498 | 2 | 0.1546 |
| Granite41-8B | 1149 | 702 | 702 | 0 | 0 | 97 | 97 | 0 | 0 | 126 | 126 | 350 | 247 | 244 | 486 | 14 | 0.5021 |
| Ministral3-14B | 385 | 96 | 96 | 176 | 176 | 113 | 113 | 0 | 0 | 0 | 0 | 0 | 0 | 193 | 446 | 54 | 0.4327 |
| Cogito-14B | 357 | 179 | 179 | 11 | 11 | 157 | 157 | 6 | 6 | 7 | 7 | 10 | 10 | 156 | 462 | 38 | 0.3377 |

## 4c. Path-level co-failure by stratum (§16.3): shortcut, wrong relation (REL) and off-path node (NODE); queries with the flag = 1

CSV: `table04c_path_cofailure_by_stratum.csv`

| View | Stratum | Value | Queries | PCF_SHORTCUT3 | PCF_REL3 | PCF_REL4 | PCF_NODE3 | PCF_NODE4 |
|---|---|---|---|---|---|---|---|---|
| All queries | Relation type | disease:drug:effect/phenotype | 336 | 0 | 0 | 0 | 0 | 0 |
| All queries | Relation type | disease:drug:gene/protein | 8 | 0 | 0 | 0 | 0 | 0 |
| All queries | Relation type | disease:gene/protein:drug | 16 | 0 | 0 | 0 | 0 | 0 |
| All queries | Relation type | drug:disease:effect/phenotype | 6 | 0 | 0 | 0 | 0 | 0 |
| All queries | Relation type | drug:disease:gene/protein | 8 | 2 | 2 | 0 | 0 | 0 |
| All queries | Relation type | drug:gene/protein:disease | 51 | 0 | 0 | 0 | 0 | 0 |
| All queries | Relation type | effect/phenotype:disease:drug | 55 | 0 | 4 | 2 | 0 | 0 |
| All queries | Relation type | gene/protein:disease:drug | 11 | 0 | 1 | 0 | 0 | 0 |
| All queries | Relation type | gene/protein:drug:disease | 9 | 0 | 1 | 0 | 0 | 0 |
| All queries | Ambiguity tag | BOTH_AMBIGUOUS | 61 | 0 | 4 | 2 | 0 | 0 |
| All queries | Ambiguity tag | NONE | 67 | 0 | 0 | 0 | 0 | 0 |
| All queries | Ambiguity tag | R1_AMBIGUOUS | 352 | 2 | 2 | 0 | 0 | 0 |
| All queries | Ambiguity tag | R2_AMBIGUOUS | 20 | 0 | 2 | 0 | 0 | 0 |
| All queries | Construction | BRIDGE | 164 | 2 | 8 | 2 | 0 | 0 |
| All queries | Construction | UNION | 336 | 0 | 0 | 0 | 0 | 0 |
| All queries | Bridge multiplicity | MULTI_BRIDGE | 375 | 0 | 3 | 1 | 0 | 0 |
| All queries | Bridge multiplicity | SINGLE_BRIDGE | 125 | 2 | 5 | 1 | 0 | 0 |
| Without SOURCE_NAME_OVERLAP | Relation type | disease:drug:effect/phenotype | 336 | 0 | 0 | 0 | 0 | 0 |
| Without SOURCE_NAME_OVERLAP | Relation type | disease:drug:gene/protein | 8 | 0 | 0 | 0 | 0 | 0 |
| Without SOURCE_NAME_OVERLAP | Relation type | disease:gene/protein:drug | 16 | 0 | 0 | 0 | 0 | 0 |
| Without SOURCE_NAME_OVERLAP | Relation type | drug:disease:effect/phenotype | 6 | 0 | 0 | 0 | 0 | 0 |
| Without SOURCE_NAME_OVERLAP | Relation type | drug:disease:gene/protein | 8 | 2 | 2 | 0 | 0 | 0 |
| Without SOURCE_NAME_OVERLAP | Relation type | drug:gene/protein:disease | 51 | 0 | 0 | 0 | 0 | 0 |
| Without SOURCE_NAME_OVERLAP | Relation type | effect/phenotype:disease:drug | 52 | 0 | 3 | 1 | 0 | 0 |
| Without SOURCE_NAME_OVERLAP | Relation type | gene/protein:disease:drug | 11 | 0 | 1 | 0 | 0 | 0 |
| Without SOURCE_NAME_OVERLAP | Relation type | gene/protein:drug:disease | 9 | 0 | 1 | 0 | 0 | 0 |
| Without SOURCE_NAME_OVERLAP | Ambiguity tag | BOTH_AMBIGUOUS | 58 | 0 | 3 | 1 | 0 | 0 |
| Without SOURCE_NAME_OVERLAP | Ambiguity tag | NONE | 67 | 0 | 0 | 0 | 0 | 0 |
| Without SOURCE_NAME_OVERLAP | Ambiguity tag | R1_AMBIGUOUS | 352 | 2 | 2 | 0 | 0 | 0 |
| Without SOURCE_NAME_OVERLAP | Ambiguity tag | R2_AMBIGUOUS | 20 | 0 | 2 | 0 | 0 | 0 |
| Without SOURCE_NAME_OVERLAP | Construction | BRIDGE | 161 | 2 | 7 | 1 | 0 | 0 |
| Without SOURCE_NAME_OVERLAP | Construction | UNION | 336 | 0 | 0 | 0 | 0 | 0 |
| Without SOURCE_NAME_OVERLAP | Bridge multiplicity | MULTI_BRIDGE | 372 | 0 | 2 | 0 | 0 | 0 |
| Without SOURCE_NAME_OVERLAP | Bridge multiplicity | SINGLE_BRIDGE | 125 | 2 | 5 | 1 | 0 | 0 |

Off-path node is defined by the protocol only at the path co-failure level (§16.3 PCF_NODE: an intermediate node not in B_q ∪ T_q on the primary path of an OFF_QUESTION answer for ≥ 3 / all 4 agents). No answer-level off-path-node count is defined, so none is computed.

## 4d. §21 mechanism of the shared feature, queries meeting the flag part of the §21 candidate rule (S31, results/interventions/candidates.csv)

CSV: `table04d_flagged_query_mechanisms.csv`

| Query | Relation type | Ambiguity tag | SOURCE_NAME_OVERLAP | CF3^Q | CF3^{Q,H1} | Mechanism | u | u name | r | Step | Holders | Holder agents | Valid route after block | Matched control |
|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|
| BH2_03356 | gene/protein:disease:drug | R2_AMBIGUOUS | no | 1 | 1 | WRONG_TURN_HOP2 | 33618 | atrial fibrillation (disease) | off-label use | 2 | 3 | Cogito-14B, Granite41-8B, Ministral3-14B | yes | no |
| BH2_04650 | drug:disease:gene/protein | R1_AMBIGUOUS | no | 1 | 0 | SHORTCUT | 16843 | Dipivefrin | drug_protein | 1 | 3 | Cogito-14B, Granite41-8B, Ministral3-14B | yes | no |
| BH2_04856 | drug:disease:gene/protein | R1_AMBIGUOUS | no | 1 | 0 | SHORTCUT | 17226 | Tirofiban | drug_protein | 1 | 3 | Cogito-14B, Granite41-8B, Ministral3-14B | yes | no |
| BH2_05290 | gene/protein:drug:disease | R2_AMBIGUOUS | no | 1 | 1 | WRONG_TURN_HOP2 | 14052 | Vitamin A | off-label use | 2 | 3 | Cogito-14B, Gemma4-12B, Granite41-8B | yes | no |
| BH2_05778 | effect/phenotype:disease:drug | BOTH_AMBIGUOUS | yes | 1 | 1 | WRONG_TURN_HOP2 | 29749 | Ewing sarcoma | off-label use | 2 | 4 | Cogito-14B, Gemma4-12B, Granite41-8B, Ministral3-14B | yes | no |
| BH2_05890 | effect/phenotype:disease:drug | BOTH_AMBIGUOUS | no | 1 | 1 | WRONG_TURN_HOP2 | 32520 | graft versus host disease | off-label use | 2 | 3 | Cogito-14B, Gemma4-12B, Ministral3-14B | yes | no |
| BH2_05997 | effect/phenotype:disease:drug | BOTH_AMBIGUOUS | no | 1 | 1 | WRONG_TURN_HOP2 | 33228 | localized scleroderma | off-label use | 2 | 3 | Cogito-14B, Granite41-8B, Ministral3-14B | yes | no |
| BH2_06016 | effect/phenotype:disease:drug | BOTH_AMBIGUOUS | no | 1 | 1 | WRONG_TURN_HOP2 | 30800 | juvenile arthritis due to defect in LACC1 | off-label use | 2 | 4 | Cogito-14B, Gemma4-12B, Granite41-8B, Ministral3-14B | yes | no |

Mechanism counts: SHORTCUT 2, WRONG_TURN_HOP2 6 (of 8 queries). C = 0: no query has a matched control (decision log 2026-11-11).
