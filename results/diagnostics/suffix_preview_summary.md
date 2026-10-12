# " (disease)" suffix preview — per-type summary

**Exploratory, viewed before the §12 suffix decision.** No hop-2 scores or label sets computed.

Names resolved under §12 as written with the field's type filter; unresolved names re-tried with " (disease)" appended. Answer counts are (row, distinct name) pairs. Full counts: `suffix_preview.csv`; names: `suffix_preview_names.csv`.

| relation type | field (type) | rows | unresolved names (not found / ambiguous) | rows with any | would resolve + suffix | still unresolved | rows fully fixed |
|---|---|---|---|---|---|---|---|
| disease:drug:effect/phenotype | answer (effect/phenotype) | 949 | 0 (0 / 0) | 0 | 0 | 0 | 0 |
| disease:drug:effect/phenotype | hop2 (disease) | 949 | 0 (0 / 0) | 0 | 0 | 0 | 0 |
| disease:drug:effect/phenotype | hop1 (drug) | 949 | 0 (0 / 0) | 0 | 0 | 0 | 0 |
| disease:drug:gene/protein | answer (gene/protein) | 381 | 0 (0 / 0) | 0 | 0 | 0 | 0 |
| disease:drug:gene/protein | hop2 (disease) | 381 | 0 (0 / 0) | 0 | 0 | 0 | 0 |
| disease:drug:gene/protein | hop1 (drug) | 381 | 0 (0 / 0) | 0 | 0 | 0 | 0 |
| disease:effect/phenotype:drug | answer (drug) | 36 | 0 (0 / 0) | 0 | 0 | 0 | 0 |
| disease:effect/phenotype:drug | hop2 (disease) | 36 | 0 (0 / 0) | 0 | 0 | 0 | 0 |
| disease:effect/phenotype:drug | hop1 (effect/phenotype) | 36 | 0 (0 / 0) | 0 | 0 | 0 | 0 |
| disease:gene/protein:drug | answer (drug) | 899 | 0 (0 / 0) | 0 | 0 | 0 | 0 |
| disease:gene/protein:drug | hop2 (disease) | 899 | 0 (0 / 0) | 0 | 0 | 0 | 0 |
| disease:gene/protein:drug | hop1 (gene/protein) | 899 | 0 (0 / 0) | 0 | 0 | 0 | 0 |
| drug:disease:effect/phenotype | answer (effect/phenotype) | 213 | 0 (0 / 0) | 0 | 0 | 0 | 0 |
| drug:disease:effect/phenotype | hop2 (drug) | 213 | 0 (0 / 0) | 0 | 0 | 0 | 0 |
| drug:disease:effect/phenotype | hop1 (disease) | 213 | 0 (0 / 0) | 0 | 0 | 0 | 0 |
| drug:disease:gene/protein | answer (gene/protein) | 321 | 0 (0 / 0) | 0 | 0 | 0 | 0 |
| drug:disease:gene/protein | hop2 (drug) | 321 | 0 (0 / 0) | 0 | 0 | 0 | 0 |
| drug:disease:gene/protein | hop1 (disease) | 321 | 0 (0 / 0) | 0 | 0 | 0 | 0 |
| drug:effect/phenotype:disease | answer (disease) | 5 | 0 (0 / 0) | 0 | 0 | 0 | 0 |
| drug:effect/phenotype:disease | hop2 (drug) | 5 | 0 (0 / 0) | 0 | 0 | 0 | 0 |
| drug:effect/phenotype:disease | hop1 (effect/phenotype) | 5 | 0 (0 / 0) | 0 | 0 | 0 | 0 |
| drug:gene/protein:disease | answer (disease) | 3029 | 0 (0 / 0) | 0 | 0 | 0 | 0 |
| drug:gene/protein:disease | hop2 (drug) | 3029 | 0 (0 / 0) | 0 | 0 | 0 | 0 |
| drug:gene/protein:disease | hop1 (gene/protein) | 3029 | 0 (0 / 0) | 0 | 0 | 0 | 0 |
| effect/phenotype:disease:drug | answer (drug) | 546 | 0 (0 / 0) | 0 | 0 | 0 | 0 |
| effect/phenotype:disease:drug | hop2 (effect/phenotype) | 546 | 0 (0 / 0) | 0 | 0 | 0 | 0 |
| effect/phenotype:disease:drug | hop1 (disease) | 546 | 0 (0 / 0) | 0 | 0 | 0 | 0 |
| effect/phenotype:drug:disease | answer (disease) | 215 | 95 (95 / 0) | 59 | 95 | 0 | 59 |
| effect/phenotype:drug:disease | hop2 (effect/phenotype) | 215 | 0 (0 / 0) | 0 | 0 | 0 | 0 |
| effect/phenotype:drug:disease | hop1 (drug) | 215 | 0 (0 / 0) | 0 | 0 | 0 | 0 |
| gene/protein:disease:drug | answer (drug) | 577 | 0 (0 / 0) | 0 | 0 | 0 | 0 |
| gene/protein:disease:drug | hop2 (gene/protein) | 577 | 0 (0 / 0) | 0 | 0 | 0 | 0 |
| gene/protein:disease:drug | hop1 (disease) | 577 | 0 (0 / 0) | 0 | 0 | 0 | 0 |
| gene/protein:drug:disease | answer (disease) | 462 | 57 (57 / 0) | 56 | 57 | 0 | 56 |
| gene/protein:drug:disease | hop2 (gene/protein) | 462 | 0 (0 / 0) | 0 | 0 | 0 | 0 |
| gene/protein:drug:disease | hop1 (drug) | 462 | 0 (0 / 0) | 0 | 0 | 0 | 0 |

**Totals by field.**
- answer: 152 unresolved in 115 rows; +suffix resolves 152, still unresolved 0; rows fully fixed 115
- hop2: 0 unresolved in 0 rows; +suffix resolves 0, still unresolved 0; rows fully fixed 0
- hop1: 0 unresolved in 0 rows; +suffix resolves 0, still unresolved 0; rows fully fixed 0
