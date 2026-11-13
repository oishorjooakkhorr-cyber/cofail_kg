# RP — Repeat run `repeat_v1` (EXPLORATORY)

EXPLORATORY (protocol §20) — docs/decision_log.md, entry 2026-11-12 "Plan after D7", section D. repeat_v1 never replaces pilot_v1/expansion_v1, which remain the results of record.

Produced by `scripts/45_rp_report.py` at commit `1b36d37aed6c20b1d272575c3322bb36eefff672` (tracked files clean: True). repeat_v1 inference commit(s): `1b36d37aed6c20b1d272575c3322bb36eefff672`.

**CF3^Q = 1 reproduced in 5 of 8 queries** (expectation, descriptive: at least 6 of 8; met: no). Without SOURCE_NAME_OVERLAP queries: 4 of 7.

## Table 1 — Per query

| Query | Relation type | SNO | CF3^Q orig → repeat | Reproduces | CF4^Q orig → repeat | CF3^{Q,H1} orig → repeat | Shared W^Q entities orig | repeat |
|---|---|---|---|---|---|---|---|---|
| BH2_03356 | gene/protein:disease:drug |  | 1 → 0 | no | 0 → 0 | 1 → 0 | 14142, 14162, 14215, 14255, 14302, 14308, 14317, 14369, 14605, 14835, 14836, 14846, 15451, 15762, 15769, 15836, 16210, 16687, 16689, 16690 | — |
| BH2_04650 | drug:disease:gene/protein |  | 1 → 1 | yes | 0 → 0 | 0 → 0 | 341, 1494, 1659, 2472, 8038 | 341, 1494, 1659, 2472, 8038 |
| BH2_04856 | drug:disease:gene/protein |  | 1 → 0 | no | 0 → 0 | 0 → 0 | 11356 | — |
| BH2_05290 | gene/protein:drug:disease |  | 1 → 1 | yes | 0 → 0 | 1 → 1 | 31820, 36924 | 31820, 36924 |
| BH2_05778 | effect/phenotype:disease:drug | yes | 1 → 1 | yes | 1 → 1 | 1 → 1 | 14231, 14275, 14604, 14608, 14715, 14737, 14793, 14955, 15413, 15481, 20336 | 14231, 14275, 14604, 14608, 14715, 14737, 14793, 14955, 15413, 15481, 20336 |
| BH2_05890 | effect/phenotype:disease:drug |  | 1 → 0 | no | 0 → 0 | 1 → 0 | 14606 | — |
| BH2_05997 | effect/phenotype:disease:drug |  | 1 → 1 | yes | 0 → 0 | 1 → 1 | 15438, 15982 | 15438, 15982 |
| BH2_06016 | effect/phenotype:disease:drug |  | 1 → 1 | yes | 1 → 1 | 1 → 1 | 14175, 14191, 14206, 14262, 14274, 14340, 14347, 15438 | 14175, 14191, 14206, 14262, 14274, 14340, 14347, 15438 |

## Table 2 — Per agent and query: Jaccard overlap (original vs repeat)

| Query | Agent | Status orig / repeat | Answers orig / repeat | Jaccard answer IDs | Jaccard OFF_QUESTION |
|---|---|---|---|---|---|
| BH2_03356 | Gemma4-12B | SUCCESS / SUCCESS | 14 / 14 | 1.000 (14/14) | NA (0/0) |
| BH2_03356 | Granite41-8B | SUCCESS / SUCCESS | 35 / 35 | 1.000 (35/35) | 1.000 (21/21) |
| BH2_03356 | Ministral3-14B | SUCCESS / PARSE_FAIL | 34 / 0 | 0.000 (0/34) | 0.000 (0/20) |
| BH2_03356 | Cogito-14B | SUCCESS / SUCCESS | 35 / 35 | 1.000 (35/35) | 1.000 (21/21) |
| BH2_04650 | Gemma4-12B | SUCCESS / SUCCESS | 13 / 13 | 1.000 (13/13) | NA (0/0) |
| BH2_04650 | Granite41-8B | SUCCESS / SUCCESS | 5 / 5 | 1.000 (5/5) | 1.000 (5/5) |
| BH2_04650 | Ministral3-14B | SUCCESS / SUCCESS | 5 / 5 | 1.000 (5/5) | 1.000 (5/5) |
| BH2_04650 | Cogito-14B | SUCCESS / SUCCESS | 5 / 5 | 1.000 (5/5) | 1.000 (5/5) |
| BH2_04856 | Gemma4-12B | SUCCESS / SUCCESS | 33 / 33 | 1.000 (33/33) | NA (0/0) |
| BH2_04856 | Granite41-8B | SUCCESS / SUCCESS | 2 / 2 | 1.000 (2/2) | 1.000 (1/1) |
| BH2_04856 | Ministral3-14B | SUCCESS / SUCCESS | 2 / 33 | 0.029 (1/34) | 0.000 (0/1) |
| BH2_04856 | Cogito-14B | SUCCESS / SUCCESS | 2 / 2 | 1.000 (2/2) | 1.000 (1/1) |
| BH2_05290 | Gemma4-12B | SUCCESS / SUCCESS | 4 / 4 | 1.000 (4/4) | 1.000 (2/2) |
| BH2_05290 | Granite41-8B | SUCCESS / SUCCESS | 4 / 4 | 1.000 (4/4) | 1.000 (2/2) |
| BH2_05290 | Ministral3-14B | SUCCESS / SUCCESS | 2 / 2 | 1.000 (2/2) | NA (0/0) |
| BH2_05290 | Cogito-14B | SUCCESS / SUCCESS | 4 / 4 | 1.000 (4/4) | 1.000 (2/2) |
| BH2_05778 | Gemma4-12B | SUCCESS / SUCCESS | 13 / 13 | 1.000 (13/13) | 1.000 (11/11) |
| BH2_05778 | Granite41-8B | SUCCESS / SUCCESS | 12 / 12 | 1.000 (12/12) | 1.000 (11/11) |
| BH2_05778 | Ministral3-14B | SUCCESS / SUCCESS | 11 / 11 | 1.000 (11/11) | 1.000 (10/10) |
| BH2_05778 | Cogito-14B | SUCCESS / SUCCESS | 13 / 13 | 1.000 (13/13) | 1.000 (11/11) |
| BH2_05890 | Gemma4-12B | SUCCESS / SUCCESS | 4 / 4 | 1.000 (4/4) | 1.000 (1/1) |
| BH2_05890 | Granite41-8B | SUCCESS / SUCCESS | 13 / 11 | 0.846 (11/13) | 0.800 (8/10) |
| BH2_05890 | Ministral3-14B | SUCCESS / SUCCESS | 4 / 4 | 1.000 (4/4) | 1.000 (1/1) |
| BH2_05890 | Cogito-14B | SUCCESS / SUCCESS | 19 / 3 | 0.158 (3/19) | 0.000 (0/16) |
| BH2_05997 | Gemma4-12B | SUCCESS / SUCCESS | 4 / 4 | 1.000 (4/4) | NA (0/0) |
| BH2_05997 | Granite41-8B | SUCCESS / SUCCESS | 8 / 8 | 1.000 (8/8) | 1.000 (4/4) |
| BH2_05997 | Ministral3-14B | SUCCESS / SUCCESS | 6 / 6 | 1.000 (6/6) | 1.000 (2/2) |
| BH2_05997 | Cogito-14B | SUCCESS / SUCCESS | 6 / 6 | 1.000 (6/6) | 1.000 (2/2) |
| BH2_06016 | Gemma4-12B | SUCCESS / SUCCESS | 32 / 32 | 1.000 (32/32) | 1.000 (8/8) |
| BH2_06016 | Granite41-8B | SUCCESS / SUCCESS | 32 / 32 | 1.000 (32/32) | 1.000 (8/8) |
| BH2_06016 | Ministral3-14B | SUCCESS / SUCCESS | 32 / 32 | 1.000 (32/32) | 1.000 (8/8) |
| BH2_06016 | Cogito-14B | SUCCESS / SUCCESS | 32 / 32 | 1.000 (32/32) | 1.000 (8/8) |

Jaccard = |A ∩ B| / |A ∪ B| over resolved answer IDs (and over OFF_QUESTION IDs); NA when both sets are empty.
