# S10 — Sampling report

Seed 42; sets are disjoint and selected in screening → smoke → pilot → expansion order.
Pilot default confirmed: 25 SINGLE_BRIDGE / 75 MULTI_BRIDGE. Bins are descriptive only.

| Set | Target | Sampled | Single | Multi | Shortfall |
| --- | ---: | ---: | ---: | ---: | ---: |
| screening | 20 | 20 | 5 | 15 | 0 |
| smoke | 4 | 4 | 1 | 3 | 0 |
| pilot | 100 | 100 | 25 | 75 | 0 |
| expansion | 400 | 400 | 100 | 300 | 0 |

## screening — strata

| Multiplicity | Relation type | Queries |
| --- | --- | ---: |
| SINGLE_BRIDGE | disease:drug:effect/phenotype | 0 |
| SINGLE_BRIDGE | disease:drug:gene/protein | 0 |
| SINGLE_BRIDGE | disease:gene/protein:drug | 1 |
| SINGLE_BRIDGE | drug:disease:effect/phenotype | 0 |
| SINGLE_BRIDGE | drug:disease:gene/protein | 0 |
| SINGLE_BRIDGE | drug:gene/protein:disease | 2 |
| SINGLE_BRIDGE | effect/phenotype:disease:drug | 0 |
| SINGLE_BRIDGE | gene/protein:disease:drug | 1 |
| SINGLE_BRIDGE | gene/protein:drug:disease | 1 |
| MULTI_BRIDGE | disease:drug:effect/phenotype | 13 |
| MULTI_BRIDGE | effect/phenotype:disease:drug | 2 |

## smoke — strata

| Multiplicity | Relation type | Queries |
| --- | --- | ---: |
| SINGLE_BRIDGE | disease:drug:effect/phenotype | 0 |
| SINGLE_BRIDGE | disease:drug:gene/protein | 0 |
| SINGLE_BRIDGE | disease:gene/protein:drug | 0 |
| SINGLE_BRIDGE | drug:disease:effect/phenotype | 0 |
| SINGLE_BRIDGE | drug:disease:gene/protein | 0 |
| SINGLE_BRIDGE | drug:gene/protein:disease | 1 |
| SINGLE_BRIDGE | effect/phenotype:disease:drug | 0 |
| SINGLE_BRIDGE | gene/protein:disease:drug | 0 |
| SINGLE_BRIDGE | gene/protein:drug:disease | 0 |
| MULTI_BRIDGE | disease:drug:effect/phenotype | 3 |
| MULTI_BRIDGE | effect/phenotype:disease:drug | 0 |

## pilot — strata

| Multiplicity | Relation type | Queries |
| --- | --- | ---: |
| SINGLE_BRIDGE | disease:drug:effect/phenotype | 2 |
| SINGLE_BRIDGE | disease:drug:gene/protein | 2 |
| SINGLE_BRIDGE | disease:gene/protein:drug | 3 |
| SINGLE_BRIDGE | drug:disease:effect/phenotype | 2 |
| SINGLE_BRIDGE | drug:disease:gene/protein | 2 |
| SINGLE_BRIDGE | drug:gene/protein:disease | 8 |
| SINGLE_BRIDGE | effect/phenotype:disease:drug | 2 |
| SINGLE_BRIDGE | gene/protein:disease:drug | 2 |
| SINGLE_BRIDGE | gene/protein:drug:disease | 2 |
| MULTI_BRIDGE | disease:drug:effect/phenotype | 65 |
| MULTI_BRIDGE | effect/phenotype:disease:drug | 10 |

## expansion — strata

| Multiplicity | Relation type | Queries |
| --- | --- | ---: |
| SINGLE_BRIDGE | disease:drug:effect/phenotype | 5 |
| SINGLE_BRIDGE | disease:drug:gene/protein | 6 |
| SINGLE_BRIDGE | disease:gene/protein:drug | 13 |
| SINGLE_BRIDGE | drug:disease:effect/phenotype | 4 |
| SINGLE_BRIDGE | drug:disease:gene/protein | 6 |
| SINGLE_BRIDGE | drug:gene/protein:disease | 43 |
| SINGLE_BRIDGE | effect/phenotype:disease:drug | 7 |
| SINGLE_BRIDGE | gene/protein:disease:drug | 9 |
| SINGLE_BRIDGE | gene/protein:drug:disease | 7 |
| MULTI_BRIDGE | disease:drug:effect/phenotype | 264 |
| MULTI_BRIDGE | effect/phenotype:disease:drug | 36 |

Agent sheets contain exactly query_id, question_text, start_name and start_id.
Manifest and sheet lines are ordered by query ID after selection; selection within strata uses SHA256(42 + query_id).
