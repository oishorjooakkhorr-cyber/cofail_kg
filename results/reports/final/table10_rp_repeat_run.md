# Table 10 — RP — Repeat run (repeat_v1)

**Status:** EXPLORATORY (protocol §20)

**Basis:** docs/decision_log.md, entry 2026-11-12 "S30 — Plan after D7", section D; docs/decision_log.md, entries 2026-11-13 "RP — Repeat-run inputs" and "RP — Pre-run checks"

Produced by `scripts/38_final_tables.py` at commit `d6a00137dc22cbec6f9d537432a0166f5d0f9c6b` (tracked files clean: True; producing code committed at this commit: True).

Inputs (SHA256 in `provenance.json`; last commit that touched each):

- `results/exploratory/rp/rp.json` — bf5f57c7dc8e71f175376db052e35f873a3e76c0

repeat_v1 never replaces pilot_v1/expansion_v1, which remain the results of record.

Produced by scripts/45_rp_report.py at commit 1b36d37aed6c20b1d272575c3322bb36eefff672; repeat_v1 inference commit(s): 1b36d37aed6c20b1d272575c3322bb36eefff672.

## 10a. Per query: original (results of record) vs repeat_v1

CSV: `table10a_per_query.csv`

| Query | Relation type | SOURCE_NAME_OVERLAP | CF3^Q original | CF3^Q repeat | CF3^Q reproduces | CF4^Q original | CF4^Q repeat | CF3^{Q,H1} original | CF3^{Q,H1} repeat | Shared W^Q entities original | Shared W^Q entities repeat |
|---|---|---|---|---|---|---|---|---|---|---|---|
| BH2_03356 | gene/protein:disease:drug | no | 1 | 0 | no | 0 | 0 | 1 | 0 | 14142, 14162, 14215, 14255, 14302, 14308, 14317, 14369, 14605, 14835, 14836, 14846, 15451, 15762, 15769, 15836, 16210, 16687, 16689, 16690 | — |
| BH2_04650 | drug:disease:gene/protein | no | 1 | 1 | yes | 0 | 0 | 0 | 0 | 341, 1494, 1659, 2472, 8038 | 341, 1494, 1659, 2472, 8038 |
| BH2_04856 | drug:disease:gene/protein | no | 1 | 0 | no | 0 | 0 | 0 | 0 | 11356 | — |
| BH2_05290 | gene/protein:drug:disease | no | 1 | 1 | yes | 0 | 0 | 1 | 1 | 31820, 36924 | 31820, 36924 |
| BH2_05778 | effect/phenotype:disease:drug | yes | 1 | 1 | yes | 1 | 1 | 1 | 1 | 14231, 14275, 14604, 14608, 14715, 14737, 14793, 14955, 15413, 15481, 20336 | 14231, 14275, 14604, 14608, 14715, 14737, 14793, 14955, 15413, 15481, 20336 |
| BH2_05890 | effect/phenotype:disease:drug | no | 1 | 0 | no | 0 | 0 | 1 | 0 | 14606 | — |
| BH2_05997 | effect/phenotype:disease:drug | no | 1 | 1 | yes | 0 | 0 | 1 | 1 | 15438, 15982 | 15438, 15982 |
| BH2_06016 | effect/phenotype:disease:drug | no | 1 | 1 | yes | 1 | 1 | 1 | 1 | 14175, 14191, 14206, 14262, 14274, 14340, 14347, 15438 | 14175, 14191, 14206, 14262, 14274, 14340, 14347, 15438 |

## 10b. Reproduction counts (expectation, descriptive, not a test: at least 6 of 8)

CSV: `table10b_summary.csv`

| View | Queries | CF3^Q original | CF3^Q repeat | Reproduced | CF4^Q repeat | CF3^{Q,H1} repeat | Expectation (at least) | Expectation met |
|---|---|---|---|---|---|---|---|---|
| All queries | 8 | 8 | 5 | 5 | 2 | 4 | 6 | no |
| Without SOURCE_NAME_OVERLAP | 7 | 7 | 4 | 4 | 1 | 3 | — | — |

## 10c. Per agent and query: Jaccard overlap of answer ID sets and OFF_QUESTION sets

CSV: `table10c_jaccard.csv`

| Query | Agent | Status original | Status repeat | Answers original | Answers repeat | Answers ∩ | Answers ∪ | Jaccard answers | OFF_QUESTION ∩ | OFF_QUESTION ∪ | Jaccard OFF_QUESTION |
|---|---|---|---|---|---|---|---|---|---|---|---|
| BH2_03356 | Cogito-14B | SUCCESS | SUCCESS | 35 | 35 | 35 | 35 | 1.0000 | 21 | 21 | 1.0000 |
| BH2_03356 | Gemma4-12B | SUCCESS | SUCCESS | 14 | 14 | 14 | 14 | 1.0000 | 0 | 0 | — |
| BH2_03356 | Granite41-8B | SUCCESS | SUCCESS | 35 | 35 | 35 | 35 | 1.0000 | 21 | 21 | 1.0000 |
| BH2_03356 | Ministral3-14B | SUCCESS | PARSE_FAIL | 34 | 0 | 0 | 34 | 0.0000 | 0 | 20 | 0.0000 |
| BH2_04650 | Cogito-14B | SUCCESS | SUCCESS | 5 | 5 | 5 | 5 | 1.0000 | 5 | 5 | 1.0000 |
| BH2_04650 | Gemma4-12B | SUCCESS | SUCCESS | 13 | 13 | 13 | 13 | 1.0000 | 0 | 0 | — |
| BH2_04650 | Granite41-8B | SUCCESS | SUCCESS | 5 | 5 | 5 | 5 | 1.0000 | 5 | 5 | 1.0000 |
| BH2_04650 | Ministral3-14B | SUCCESS | SUCCESS | 5 | 5 | 5 | 5 | 1.0000 | 5 | 5 | 1.0000 |
| BH2_04856 | Cogito-14B | SUCCESS | SUCCESS | 2 | 2 | 2 | 2 | 1.0000 | 1 | 1 | 1.0000 |
| BH2_04856 | Gemma4-12B | SUCCESS | SUCCESS | 33 | 33 | 33 | 33 | 1.0000 | 0 | 0 | — |
| BH2_04856 | Granite41-8B | SUCCESS | SUCCESS | 2 | 2 | 2 | 2 | 1.0000 | 1 | 1 | 1.0000 |
| BH2_04856 | Ministral3-14B | SUCCESS | SUCCESS | 2 | 33 | 1 | 34 | 0.0294 | 0 | 1 | 0.0000 |
| BH2_05290 | Cogito-14B | SUCCESS | SUCCESS | 4 | 4 | 4 | 4 | 1.0000 | 2 | 2 | 1.0000 |
| BH2_05290 | Gemma4-12B | SUCCESS | SUCCESS | 4 | 4 | 4 | 4 | 1.0000 | 2 | 2 | 1.0000 |
| BH2_05290 | Granite41-8B | SUCCESS | SUCCESS | 4 | 4 | 4 | 4 | 1.0000 | 2 | 2 | 1.0000 |
| BH2_05290 | Ministral3-14B | SUCCESS | SUCCESS | 2 | 2 | 2 | 2 | 1.0000 | 0 | 0 | — |
| BH2_05778 | Cogito-14B | SUCCESS | SUCCESS | 13 | 13 | 13 | 13 | 1.0000 | 11 | 11 | 1.0000 |
| BH2_05778 | Gemma4-12B | SUCCESS | SUCCESS | 13 | 13 | 13 | 13 | 1.0000 | 11 | 11 | 1.0000 |
| BH2_05778 | Granite41-8B | SUCCESS | SUCCESS | 12 | 12 | 12 | 12 | 1.0000 | 11 | 11 | 1.0000 |
| BH2_05778 | Ministral3-14B | SUCCESS | SUCCESS | 11 | 11 | 11 | 11 | 1.0000 | 10 | 10 | 1.0000 |
| BH2_05890 | Cogito-14B | SUCCESS | SUCCESS | 19 | 3 | 3 | 19 | 0.1579 | 0 | 16 | 0.0000 |
| BH2_05890 | Gemma4-12B | SUCCESS | SUCCESS | 4 | 4 | 4 | 4 | 1.0000 | 1 | 1 | 1.0000 |
| BH2_05890 | Granite41-8B | SUCCESS | SUCCESS | 13 | 11 | 11 | 13 | 0.8462 | 8 | 10 | 0.8000 |
| BH2_05890 | Ministral3-14B | SUCCESS | SUCCESS | 4 | 4 | 4 | 4 | 1.0000 | 1 | 1 | 1.0000 |
| BH2_05997 | Cogito-14B | SUCCESS | SUCCESS | 6 | 6 | 6 | 6 | 1.0000 | 2 | 2 | 1.0000 |
| BH2_05997 | Gemma4-12B | SUCCESS | SUCCESS | 4 | 4 | 4 | 4 | 1.0000 | 0 | 0 | — |
| BH2_05997 | Granite41-8B | SUCCESS | SUCCESS | 8 | 8 | 8 | 8 | 1.0000 | 4 | 4 | 1.0000 |
| BH2_05997 | Ministral3-14B | SUCCESS | SUCCESS | 6 | 6 | 6 | 6 | 1.0000 | 2 | 2 | 1.0000 |
| BH2_06016 | Cogito-14B | SUCCESS | SUCCESS | 32 | 32 | 32 | 32 | 1.0000 | 8 | 8 | 1.0000 |
| BH2_06016 | Gemma4-12B | SUCCESS | SUCCESS | 32 | 32 | 32 | 32 | 1.0000 | 8 | 8 | 1.0000 |
| BH2_06016 | Granite41-8B | SUCCESS | SUCCESS | 32 | 32 | 32 | 32 | 1.0000 | 8 | 8 | 1.0000 |
| BH2_06016 | Ministral3-14B | SUCCESS | SUCCESS | 32 | 32 | 32 | 32 | 1.0000 | 8 | 8 | 1.0000 |

Jaccard is NA (—) when both sets are empty.
