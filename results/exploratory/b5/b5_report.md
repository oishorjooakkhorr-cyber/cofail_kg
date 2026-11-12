# B5 — Treat concentration (EXPLORATORY)

EXPLORATORY (protocol §20) — docs/decision_log.md, entry 2026-11-12 "Plan after D7", section B5. Reported as a replication of a pattern seen in the pilot: the pilot report was committed (44a2fdd, 2026-11-08) before the expansion run started; no prediction was written before the expansion analysis.

Produced by `scripts/42_b5_concentration.py` at commit `b14370871c0c5cc161ea167e42271aac548aa9e1` (tracked files clean: True). Input: `results/combined/pilot_expansion_v1/cofailure.json` (SHA256 `198b9aa18770d1a815429361be8f79601330276642665feb025783dd5560f87d`).

Groups: treat-final = R2 = {indication} (effect/phenotype:disease:drug, gene/protein:disease:drug, gene/protein:drug:disease); treat-first = R1 = {indication} (disease:drug:effect/phenotype, disease:drug:gene/protein, drug:disease:effect/phenotype, drug:disease:gene/protein); other = disease:gene/protein:drug, drug:gene/protein:disease.

## Table 1 — All queries

| Subset | Group | Queries | CF3^Q | CF4^Q | CF3^{Q,H1} | CF3^{Q,H1} queries |
|---|---|---|---|---|---|---|
| pilot | treat-final | 16 | 3 | 1 | 3 | BH2_03356, BH2_05290, BH2_05778 |
| pilot | treat-first | 73 | 0 | 0 | 0 | — |
| pilot | other | 11 | 0 | 0 | 0 | — |
| pilot | total | 100 | 3 | 1 | 3 | BH2_03356, BH2_05290, BH2_05778 |
| expansion | treat-final | 59 | 3 | 1 | 3 | BH2_05890, BH2_05997, BH2_06016 |
| expansion | treat-first | 285 | 2 | 0 | 0 | — |
| expansion | other | 56 | 0 | 0 | 0 | — |
| expansion | total | 400 | 5 | 1 | 3 | BH2_05890, BH2_05997, BH2_06016 |
| both | treat-final | 75 | 6 | 2 | 6 | BH2_03356, BH2_05290, BH2_05778, BH2_05890, BH2_05997, BH2_06016 |
| both | treat-first | 358 | 2 | 0 | 0 | — |
| both | other | 67 | 0 | 0 | 0 | — |
| both | total | 500 | 8 | 2 | 6 | BH2_03356, BH2_05290, BH2_05778, BH2_05890, BH2_05997, BH2_06016 |

## Table 2 — Without SOURCE_NAME_OVERLAP queries (BH2_05778, BH2_05971, BH2_06099; protocol §19.1)

| Subset | Group | Queries | CF3^Q | CF4^Q | CF3^{Q,H1} | CF3^{Q,H1} queries |
|---|---|---|---|---|---|---|
| pilot | treat-final | 15 | 2 | 0 | 2 | BH2_03356, BH2_05290 |
| pilot | treat-first | 73 | 0 | 0 | 0 | — |
| pilot | other | 11 | 0 | 0 | 0 | — |
| pilot | total | 99 | 2 | 0 | 2 | BH2_03356, BH2_05290 |
| expansion | treat-final | 57 | 3 | 1 | 3 | BH2_05890, BH2_05997, BH2_06016 |
| expansion | treat-first | 285 | 2 | 0 | 0 | — |
| expansion | other | 56 | 0 | 0 | 0 | — |
| expansion | total | 398 | 5 | 1 | 3 | BH2_05890, BH2_05997, BH2_06016 |
| both | treat-final | 72 | 5 | 1 | 5 | BH2_03356, BH2_05290, BH2_05890, BH2_05997, BH2_06016 |
| both | treat-first | 358 | 2 | 0 | 0 | — |
| both | other | 67 | 0 | 0 | 0 | — |
| both | total | 497 | 7 | 1 | 5 | BH2_03356, BH2_05290, BH2_05890, BH2_05997, BH2_06016 |

## Exact hypergeometric probability — expansion's CF3^{Q,H1} queries all in treat-final

| View | N (expansion queries) | K (treat-final) | n (CF3^{Q,H1} = 1) | Observed in treat-final | All in treat-final | Formula | Exact | Decimal |
|---|---|---|---|---|---|---|---|---|
| All queries | 400 | 59 | 3 | 3 | yes | C(59,3) / C(400,3) | 32509/10586800 = 1711/557200 | 0.00307071 |
| Without SOURCE_NAME_OVERLAP queries | 398 | 57 | 3 | 3 | yes | C(57,3) / C(398,3) | 29260/10428396 = 665/237009 | 0.0028058 |


P = C(K, n) / C(N, n): the probability that n queries drawn without replacement from the expansion's N queries all fall among its K treat-final queries.
