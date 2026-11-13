# Table 1 — Dataset

**Status:** Dataset description (S6, S8, S9 outputs). Descriptive.

**Basis:** protocol §5.1–§5.3, §7.1, §7.2, §8

Produced by `scripts/38_final_tables.py` at commit `d6a00137dc22cbec6f9d537432a0166f5d0f9c6b` (tracked files clean: True; producing code committed at this commit: True).

Inputs (SHA256 in `provenance.json`; last commit that touched each):

- `results/semantics/relation_mapping.json` — ab67cf1593bd6068b60ee2842909d089a31836f1
- `results/diagnostics/biohopr/relation_types.csv` — c2c6ffd07cda1f7da8c9995462d32a513e1426f2
- `results/diagnostics/query_validation.csv` — 58c113dff59dbbd5b30c75612c47e9f39aeb49f7
- `data/processed/primary_population.csv` — ef113fb54bf2150f9694cf315e8aff4b4a9136a7
- `data/processed/primary_population_summary.json` — ef113fb54bf2150f9694cf315e8aff4b4a9136a7

## 1a. Relation types (§5.1–§5.3, Gate D1) and query counts (§7.1, §7.2, §8)

CSV: `table01a_relation_types.csv`

| Relation type | BioHopR rows | Gate D1 | Construction | R1 | R2 | Ambiguity tag | Queries validated | CONSISTENT | INCONSISTENT | LEAKY_QUESTION | SATURATED | Primary population | Primary SINGLE_BRIDGE | Primary MULTI_BRIDGE | Pilot | Expansion |
|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|
| disease:drug:effect/phenotype | 949 | PASS | UNION | indication | drug_effect | R1_AMBIGUOUS | 949 | 949 | 0 | 102 | 0 | 847 | 319 | 528 | 67 | 269 |
| disease:drug:gene/protein | 381 | PASS | BRIDGE | indication | drug_protein | R1_AMBIGUOUS | 381 | 381 | 0 | 5 | 0 | 376 | 376 | 0 | 2 | 6 |
| disease:effect/phenotype:drug | 36 | FAIL | — | — | — | — | — | — | — | — | — | — | — | — | — | — |
| disease:gene/protein:drug | 899 | PASS | BRIDGE | disease_protein | drug_protein | NONE | 899 | 899 | 0 | 47 | 0 | 852 | 852 | 0 | 3 | 13 |
| drug:disease:effect/phenotype | 213 | PASS | BRIDGE | indication | disease_phenotype_positive | BOTH_AMBIGUOUS | 213 | 213 | 0 | 0 | 0 | 213 | 213 | 0 | 2 | 4 |
| drug:disease:gene/protein | 321 | PASS | BRIDGE | indication | disease_protein | R1_AMBIGUOUS | 321 | 321 | 0 | 0 | 0 | 321 | 321 | 0 | 2 | 6 |
| drug:effect/phenotype:disease | 5 | FAIL | — | — | — | — | — | — | — | — | — | — | — | — | — | — |
| drug:gene/protein:disease | 3029 | PASS | BRIDGE | drug_protein | disease_protein | NONE | 3029 | 3029 | 0 | 1 | 0 | 3028 | 3028 | 0 | 8 | 43 |
| effect/phenotype:disease:drug | 546 | PASS | BRIDGE | disease_phenotype_positive | indication | BOTH_AMBIGUOUS | 546 | 534 | 12 | 31 | 0 | 503 | 430 | 73 | 12 | 43 |
| effect/phenotype:drug:disease | 215 | FAIL | — | — | — | — | — | — | — | — | — | — | — | — | — | — |
| gene/protein:disease:drug | 577 | PASS | BRIDGE | disease_protein | indication | R2_AMBIGUOUS | 577 | 577 | 0 | 0 | 0 | 577 | 577 | 0 | 2 | 9 |
| gene/protein:drug:disease | 462 | PASS | BRIDGE | drug_protein | indication | R2_AMBIGUOUS | 462 | 459 | 3 | 0 | 0 | 459 | 459 | 0 | 2 | 7 |
| Total | 7633 | 9 PASS / 3 FAIL | — | — | — | — | 7377 | 7362 | 15 | 186 | 0 | 7176 | 6575 | 601 | 100 | 400 |

Relation types that failed Gate D1 were excluded at S6 and never validated (—). LEAKY_QUESTION and SATURATED are counted over all validated queries, whatever their status.

## 1b. INCONSISTENT queries by reason code (§7.1)

CSV: `table01b_inconsistent_reasons.csv`

| Reason code | Primary reason (queries) | Recorded (queries) | Recorded as NA | Relation types where recorded |
|---|---|---|---|---|
| QUERY_NOT_FOUND | 0 | 0 | 0 | — |
| QUESTION_TEXT_MISMATCH | 0 | 0 | 0 | — |
| BRIDGE_NOT_FOUND | 0 | 0 | 0 | — |
| GOLD_BRIDGE_NOT_VALID | 0 | 0 | 0 | — |
| GOLD_UNMAPPED | 0 | 0 | 0 | — |
| GOLD_MISSING_FROM_KG | 15 | 15 | 0 | effect/phenotype:disease:drug, gene/protein:drug:disease |
| EXTRA_TARGETS | 0 | 3 | 0 | gene/protein:drug:disease |
| Queries INCONSISTENT | 15 | — | — | effect/phenotype:disease:drug, gene/protein:drug:disease |

Primary reason = the first applicable code in the §7.1 order; every applicable code is recorded.

## 1c. Bridge multiplicity (§7.1)

CSV: `table01c_bridge_multiplicity.csv`

| Bridge multiplicity | Queries validated | CONSISTENT | INCONSISTENT | Primary population | Pilot | Expansion |
|---|---|---|---|---|---|---|
| NO_BRIDGE | 0 | 0 | 0 | 0 | 0 | 0 |
| SINGLE_BRIDGE | 6673 | 6670 | 3 | 6575 | 25 | 100 |
| MULTI_BRIDGE | 704 | 692 | 12 | 601 | 75 | 300 |

## 1d. Relation-ambiguity tags (§5.2), D1-PASS relation types

CSV: `table01d_ambiguity_tags.csv`

| Ambiguity tag | Relation types | Relation type names | Queries validated | CONSISTENT | INCONSISTENT | Primary population | Pilot | Expansion |
|---|---|---|---|---|---|---|---|---|
| NONE | 2 | disease:gene/protein:drug, drug:gene/protein:disease | 3928 | 3928 | 0 | 3880 | 11 | 56 |
| R1_AMBIGUOUS | 3 | disease:drug:effect/phenotype, disease:drug:gene/protein, drug:disease:gene/protein | 1651 | 1651 | 0 | 1544 | 71 | 281 |
| R2_AMBIGUOUS | 2 | gene/protein:disease:drug, gene/protein:drug:disease | 1039 | 1036 | 3 | 1036 | 4 | 16 |
| BOTH_AMBIGUOUS | 2 | drug:disease:effect/phenotype, effect/phenotype:disease:drug | 759 | 747 | 12 | 716 | 14 | 47 |

## 1e. Answer construction (§5.3), D1-PASS relation types

CSV: `table01e_construction.csv`

| Construction | Relation types | Relation type names | Queries validated | CONSISTENT | INCONSISTENT | Primary population | Pilot | Expansion |
|---|---|---|---|---|---|---|---|---|
| BRIDGE | 8 | disease:drug:gene/protein, disease:gene/protein:drug, drug:disease:effect/phenotype, drug:disease:gene/protein, drug:gene/protein:disease, effect/phenotype:disease:drug, gene/protein:disease:drug, gene/protein:drug:disease | 6428 | 6413 | 15 | 6329 | 33 | 131 |
| UNION | 1 | disease:drug:effect/phenotype | 949 | 949 | 0 | 847 | 67 | 269 |

## 1f. Saturation share = |T_q| / PrimeKG nodes of Type_T (§7.1); θ = 0.5

CSV: `table01f_saturation.csv`

| Relation type | Type_T | Type_T nodes | Queries validated | Share min | Share median | Share max | SATURATED (share > 0.5) |
|---|---|---|---|---|---|---|---|
| disease:drug:effect/phenotype | effect/phenotype | 15311 | 949 | 0.0001 | 0.0081 | 0.0298 | 0 |
| disease:drug:gene/protein | gene/protein | 27671 | 381 | 0.0000 | 0.0002 | 0.0111 | 0 |
| disease:gene/protein:drug | drug | 7957 | 899 | 0.0001 | 0.0004 | 0.0515 | 0 |
| drug:disease:effect/phenotype | effect/phenotype | 15311 | 213 | 0.0001 | 0.0006 | 0.0179 | 0 |
| drug:disease:gene/protein | gene/protein | 27671 | 321 | 0.0000 | 0.0003 | 0.0322 | 0 |
| drug:gene/protein:disease | disease | 17080 | 3029 | 0.0001 | 0.0009 | 0.0160 | 0 |
| effect/phenotype:disease:drug | drug | 7957 | 546 | 0.0001 | 0.0004 | 0.0133 | 0 |
| gene/protein:disease:drug | drug | 7957 | 577 | 0.0001 | 0.0018 | 0.0085 | 0 |
| gene/protein:drug:disease | disease | 17080 | 462 | 0.0001 | 0.0001 | 0.0050 | 0 |
| All validated queries | — | — | 7377 | 0.0000 | 0.0008 | 0.0515 | 0 |

Saturation share is read as stored (results/diagnostics/query_validation.csv). Shares are small numbers: the Markdown shows 4 decimals, the CSV 6.

## 1g. Primary population (§7.2) and the 500 sampled queries (§8)

CSV: `table01g_inclusion.csv`

| Item | Queries |
|---|---|
| INCONSISTENT | 15 |
| LEAKY_QUESTION | 186 |
| SATURATED | 0 |
| Relation type neither CONFIRMED nor UNCONFIRMABLE in Gate D2 step 1 | 0 |
| Excluded (any of the above; counts above may overlap) | 201 |
| Primary population | 7176 |
| Sampled: pilot | 100 |
| Sampled: expansion | 400 |

Validated queries: 7377 of the D1-PASS relation types. The recount of the §7.2 rule from the validation file equals data/processed/primary_population.csv (checked).
