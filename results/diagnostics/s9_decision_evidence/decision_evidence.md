# S9 part 1 — Decision evidence

Mapping confirmation uses only queries containing no S6 validation-sample row; ≥80% confirms a type.

## Mapping confirmation

| relation_type | total_queries | s6_overlap_queries | confirmation_queries | consistent_queries | inconsistent_queries | consistent_share | confirmation_status |
| --- | --- | --- | --- | --- | --- | --- | --- |
| disease:drug:effect/phenotype | 949 | 30 | 919 | 919 | 0 | 1.000000 | CONFIRMED |
| disease:drug:gene/protein | 381 | 30 | 351 | 351 | 0 | 1.000000 | CONFIRMED |
| disease:gene/protein:drug | 899 | 30 | 869 | 869 | 0 | 1.000000 | CONFIRMED |
| drug:disease:effect/phenotype | 213 | 30 | 183 | 183 | 0 | 1.000000 | CONFIRMED |
| drug:disease:gene/protein | 321 | 30 | 291 | 291 | 0 | 1.000000 | CONFIRMED |
| drug:gene/protein:disease | 3029 | 30 | 2999 | 2999 | 0 | 1.000000 | CONFIRMED |
| effect/phenotype:disease:drug | 546 | 30 | 516 | 506 | 10 | 0.980620 | CONFIRMED |
| gene/protein:disease:drug | 577 | 30 | 547 | 547 | 0 | 1.000000 | CONFIRMED |
| gene/protein:drug:disease | 462 | 30 | 432 | 429 | 3 | 0.993056 | CONFIRMED |

## Saturation distribution

All CONSISTENT queries in CONFIRMED/UNCONFIRMABLE types, including S6-overlap and leakage flags. Percentiles use NumPy linear interpolation. Shares are fractions, not percentages.

| relation_type | queries | p50 | p90 | p95 | p99 | max |
| --- | --- | --- | --- | --- | --- | --- |
| ALL | 7362 | 0.000820 | 0.006440 | 0.011626 | 0.020806 | 0.051527 |
| disease:drug:effect/phenotype | 949 | 0.008099 | 0.019920 | 0.021880 | 0.026922 | 0.029848 |
| disease:drug:gene/protein | 381 | 0.000217 | 0.000867 | 0.000903 | 0.001662 | 0.011059 |
| disease:gene/protein:drug | 899 | 0.000377 | 0.002514 | 0.004587 | 0.012962 | 0.051527 |
| drug:disease:effect/phenotype | 213 | 0.000588 | 0.002090 | 0.007054 | 0.017896 | 0.017896 |
| drug:disease:gene/protein | 321 | 0.000289 | 0.006288 | 0.032164 | 0.032164 | 0.032164 |
| drug:gene/protein:disease | 3029 | 0.000937 | 0.003630 | 0.005972 | 0.010138 | 0.015984 |
| effect/phenotype:disease:drug | 534 | 0.000377 | 0.002312 | 0.003525 | 0.005027 | 0.013322 |
| gene/protein:disease:drug | 577 | 0.001759 | 0.004399 | 0.004399 | 0.008546 | 0.008546 |
| gene/protein:drug:disease | 459 | 0.000059 | 0.000410 | 0.000585 | 0.001639 | 0.001991 |

## Threshold sensitivity

Exclusion means saturation share > θ. Remaining counts reflect saturation alone; they are not the primary population.

| relation_type | theta | queries | excluded_queries | excluded_share | remaining_after_saturation | entire_type_removed |
| --- | --- | --- | --- | --- | --- | --- |
| ALL | 0.300000 | 7362 | 0 | 0.000000 | 7362 | False |
| ALL | 0.500000 | 7362 | 0 | 0.000000 | 7362 | False |
| ALL | 0.700000 | 7362 | 0 | 0.000000 | 7362 | False |
| ALL | 0.900000 | 7362 | 0 | 0.000000 | 7362 | False |
| disease:drug:effect/phenotype | 0.300000 | 949 | 0 | 0.000000 | 949 | False |
| disease:drug:effect/phenotype | 0.500000 | 949 | 0 | 0.000000 | 949 | False |
| disease:drug:effect/phenotype | 0.700000 | 949 | 0 | 0.000000 | 949 | False |
| disease:drug:effect/phenotype | 0.900000 | 949 | 0 | 0.000000 | 949 | False |
| disease:drug:gene/protein | 0.300000 | 381 | 0 | 0.000000 | 381 | False |
| disease:drug:gene/protein | 0.500000 | 381 | 0 | 0.000000 | 381 | False |
| disease:drug:gene/protein | 0.700000 | 381 | 0 | 0.000000 | 381 | False |
| disease:drug:gene/protein | 0.900000 | 381 | 0 | 0.000000 | 381 | False |
| disease:gene/protein:drug | 0.300000 | 899 | 0 | 0.000000 | 899 | False |
| disease:gene/protein:drug | 0.500000 | 899 | 0 | 0.000000 | 899 | False |
| disease:gene/protein:drug | 0.700000 | 899 | 0 | 0.000000 | 899 | False |
| disease:gene/protein:drug | 0.900000 | 899 | 0 | 0.000000 | 899 | False |
| drug:disease:effect/phenotype | 0.300000 | 213 | 0 | 0.000000 | 213 | False |
| drug:disease:effect/phenotype | 0.500000 | 213 | 0 | 0.000000 | 213 | False |
| drug:disease:effect/phenotype | 0.700000 | 213 | 0 | 0.000000 | 213 | False |
| drug:disease:effect/phenotype | 0.900000 | 213 | 0 | 0.000000 | 213 | False |
| drug:disease:gene/protein | 0.300000 | 321 | 0 | 0.000000 | 321 | False |
| drug:disease:gene/protein | 0.500000 | 321 | 0 | 0.000000 | 321 | False |
| drug:disease:gene/protein | 0.700000 | 321 | 0 | 0.000000 | 321 | False |
| drug:disease:gene/protein | 0.900000 | 321 | 0 | 0.000000 | 321 | False |
| drug:gene/protein:disease | 0.300000 | 3029 | 0 | 0.000000 | 3029 | False |
| drug:gene/protein:disease | 0.500000 | 3029 | 0 | 0.000000 | 3029 | False |
| drug:gene/protein:disease | 0.700000 | 3029 | 0 | 0.000000 | 3029 | False |
| drug:gene/protein:disease | 0.900000 | 3029 | 0 | 0.000000 | 3029 | False |
| effect/phenotype:disease:drug | 0.300000 | 534 | 0 | 0.000000 | 534 | False |
| effect/phenotype:disease:drug | 0.500000 | 534 | 0 | 0.000000 | 534 | False |
| effect/phenotype:disease:drug | 0.700000 | 534 | 0 | 0.000000 | 534 | False |
| effect/phenotype:disease:drug | 0.900000 | 534 | 0 | 0.000000 | 534 | False |
| gene/protein:disease:drug | 0.300000 | 577 | 0 | 0.000000 | 577 | False |
| gene/protein:disease:drug | 0.500000 | 577 | 0 | 0.000000 | 577 | False |
| gene/protein:disease:drug | 0.700000 | 577 | 0 | 0.000000 | 577 | False |
| gene/protein:disease:drug | 0.900000 | 577 | 0 | 0.000000 | 577 | False |
| gene/protein:drug:disease | 0.300000 | 459 | 0 | 0.000000 | 459 | False |
| gene/protein:drug:disease | 0.500000 | 459 | 0 | 0.000000 | 459 | False |
| gene/protein:drug:disease | 0.700000 | 459 | 0 | 0.000000 | 459 | False |
| gene/protein:drug:disease | 0.900000 | 459 | 0 | 0.000000 | 459 | False |

## Required decisions

No type requires mapping revision or exclusion under the 80% rule.

Researcher must choose θ (protocol recommendation: 0.50) and authorize recording it in protocol §7.2 and the decision log before part 2. No θ was selected, no primary population was written, and no Gate D2 feasibility outcome was computed.
