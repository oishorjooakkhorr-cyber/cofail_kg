# S9 — Primary population and Gate D2

θ = 0.50; N_P = 7176; K = 9; Gate D2 = **GREEN**. K counts types with at least 20 primary queries.

Gate evaluated in order: RED if N_P < 150; otherwise GREEN if N_P ≥ 650 and K ≥ 5; otherwise YELLOW.

Input queries: 7377; excluded queries: 201. Exclusion counts may overlap:

- inconsistent: 15
- leaky_question: 186
- not_confirmed_or_unconfirmable: 0
- not_d1_pass: 0
- saturated: 0

| Relation type | Primary queries | Single | Multi |
| --- | ---: | ---: | ---: |
| disease:drug:effect/phenotype | 847 | 319 | 528 |
| disease:drug:gene/protein | 376 | 376 | 0 |
| disease:gene/protein:drug | 852 | 852 | 0 |
| drug:disease:effect/phenotype | 213 | 213 | 0 |
| drug:disease:gene/protein | 321 | 321 | 0 |
| drug:gene/protein:disease | 3028 | 3028 | 0 |
| effect/phenotype:disease:drug | 503 | 430 | 73 |
| gene/protein:disease:drug | 577 | 577 | 0 |
| gene/protein:drug:disease | 459 | 459 | 0 |

This evaluator-only CSV retains S8 evidence fields and adds θ, saturation and mapping confirmation. S6 sample queries may enter the population; they were excluded only from mapping-confirmation estimation. No S10 sampling was performed.
