# Table 8 — B5 — Treat concentration

**Status:** EXPLORATORY (protocol §20)

**Basis:** docs/decision_log.md, entry 2026-11-12 "S30 — Plan after D7", section B5

Produced by `scripts/38_final_tables.py` at commit `d6a00137dc22cbec6f9d537432a0166f5d0f9c6b` (tracked files clean: True; producing code committed at this commit: True).

Inputs (SHA256 in `provenance.json`; last commit that touched each):

- `results/exploratory/b5/b5_table.csv` — 752a078ad00657c12d0a73ac2874f7ce42578019
- `results/exploratory/b5/b5.json` — 752a078ad00657c12d0a73ac2874f7ce42578019

Produced by scripts/42_b5_concentration.py at commit b14370871c0c5cc161ea167e42271aac548aa9e1.

## 8a. Queries and co-failure by group (treat-final, treat-first, other) for pilot, expansion and both

CSV: `table08a_groups.csv`

| View | Subset | Group | Queries | CF3^Q | CF4^Q | CF3^{Q,H1} | CF3^{Q,H1} queries |
|---|---|---|---|---|---|---|---|
| All queries | pilot | treat-final | 16 | 3 | 1 | 3 | BH2_03356, BH2_05290, BH2_05778 |
| All queries | pilot | treat-first | 73 | 0 | 0 | 0 | — |
| All queries | pilot | other | 11 | 0 | 0 | 0 | — |
| All queries | pilot | total | 100 | 3 | 1 | 3 | BH2_03356, BH2_05290, BH2_05778 |
| All queries | expansion | treat-final | 59 | 3 | 1 | 3 | BH2_05890, BH2_05997, BH2_06016 |
| All queries | expansion | treat-first | 285 | 2 | 0 | 0 | — |
| All queries | expansion | other | 56 | 0 | 0 | 0 | — |
| All queries | expansion | total | 400 | 5 | 1 | 3 | BH2_05890, BH2_05997, BH2_06016 |
| All queries | both | treat-final | 75 | 6 | 2 | 6 | BH2_03356, BH2_05290, BH2_05778, BH2_05890, BH2_05997, BH2_06016 |
| All queries | both | treat-first | 358 | 2 | 0 | 0 | — |
| All queries | both | other | 67 | 0 | 0 | 0 | — |
| All queries | both | total | 500 | 8 | 2 | 6 | BH2_03356, BH2_05290, BH2_05778, BH2_05890, BH2_05997, BH2_06016 |
| Without SOURCE_NAME_OVERLAP | pilot | treat-final | 15 | 2 | 0 | 2 | BH2_03356, BH2_05290 |
| Without SOURCE_NAME_OVERLAP | pilot | treat-first | 73 | 0 | 0 | 0 | — |
| Without SOURCE_NAME_OVERLAP | pilot | other | 11 | 0 | 0 | 0 | — |
| Without SOURCE_NAME_OVERLAP | pilot | total | 99 | 2 | 0 | 2 | BH2_03356, BH2_05290 |
| Without SOURCE_NAME_OVERLAP | expansion | treat-final | 57 | 3 | 1 | 3 | BH2_05890, BH2_05997, BH2_06016 |
| Without SOURCE_NAME_OVERLAP | expansion | treat-first | 285 | 2 | 0 | 0 | — |
| Without SOURCE_NAME_OVERLAP | expansion | other | 56 | 0 | 0 | 0 | — |
| Without SOURCE_NAME_OVERLAP | expansion | total | 398 | 5 | 1 | 3 | BH2_05890, BH2_05997, BH2_06016 |
| Without SOURCE_NAME_OVERLAP | both | treat-final | 72 | 5 | 1 | 5 | BH2_03356, BH2_05290, BH2_05890, BH2_05997, BH2_06016 |
| Without SOURCE_NAME_OVERLAP | both | treat-first | 358 | 2 | 0 | 0 | — |
| Without SOURCE_NAME_OVERLAP | both | other | 67 | 0 | 0 | 0 | — |
| Without SOURCE_NAME_OVERLAP | both | total | 497 | 7 | 1 | 5 | BH2_03356, BH2_05290, BH2_05890, BH2_05997, BH2_06016 |

## 8b. Exact hypergeometric probability that the expansion's CF3^{Q,H1} queries all fall in treat-final

CSV: `table08b_hypergeometric.csv`

| View | N (expansion queries) | K (treat-final) | n (CF3^{Q,H1} = 1) | Observed in treat-final | All in treat-final | Formula | Exact | Decimal |
|---|---|---|---|---|---|---|---|---|
| All queries | 400 | 59 | 3 | 3 | yes | C(59,3) / C(400,3) | 32509/10586800 = 1711/557200 | 0.0031 |
| Without SOURCE_NAME_OVERLAP | 398 | 57 | 3 | 3 | yes | C(57,3) / C(398,3) | 29260/10428396 = 665/237009 | 0.0028 |

P = C(K, n) / C(N, n). Reported as a replication of a pattern seen in the pilot: the pilot report was committed (44a2fdd, 2026-11-08) before the expansion run started; no prediction was written before the expansion analysis.
