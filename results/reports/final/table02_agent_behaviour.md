# Table 2 — Agent behaviour

**Status:** Results of record: pilot_v1 + expansion_v1, 500 queries × 4 agents, latest attempts (protocol §19); Gate D7 DESCRIPTIVE (decision log 2026-11-12). Descriptive.

**Basis:** protocol §9.5, §13, §14.1, §14.3, §15; split by construction and ambiguity tag (§5.3)

Produced by `scripts/38_final_tables.py` at commit `d6a00137dc22cbec6f9d537432a0166f5d0f9c6b` (tracked files clean: True; producing code committed at this commit: True).

Inputs (SHA256 in `provenance.json`; last commit that touched each):

- `results/combined/pilot_expansion_v1/components.json` — 02e0182f404610727741a6407169dbbe201671e7
- `data/processed/manifests/expansion.jsonl` — a0c586781ba30484b9589fd2cc96b79d4e2a5afc
- `results/runs/expansion_v1/analysis/metrics` — 02e0182f404610727741a6407169dbbe201671e7
- `data/processed/manifests/pilot.jsonl` — a0c586781ba30484b9589fd2cc96b79d4e2a5afc
- `results/runs/pilot_v1/analysis/metrics` — d43af3085a82a5d3706b97f6ad5de6441d5d0b69
- `results/semantics/relation_mapping.json` — ab67cf1593bd6068b60ee2842909d089a31836f1

Split rows: All; each construction (§5.3); each ambiguity tag (§5.2). A split's rows cover the queries of that split only.

## 2a. Episode status (§9.5), all episodes

CSV: `table02a_episode_status.csv`

| Split | Agent | Episodes | SUCCESS | PARSE_FAIL | ERROR | TIMEOUT | Technical failures | ERROR by §9.5 `cause` field |
|---|---|---|---|---|---|---|---|---|
| All | Gemma4-12B | 500 | 498 | 2 | 0 | 0 | 2 | — |
| All | Granite41-8B | 500 | 486 | 13 | 1 | 0 | 14 | CONNECTION: 1 |
| All | Ministral3-14B | 500 | 446 | 49 | 5 | 0 | 54 | CONNECTION: 5 |
| All | Cogito-14B | 500 | 462 | 2 | 36 | 0 | 38 | CONNECTION: 33, RUNTIME: 3 |
| All | All agents | 2000 | 1892 | 66 | 42 | 0 | 108 | — |
| construction = BRIDGE | Gemma4-12B | 164 | 164 | 0 | 0 | 0 | 0 | — |
| construction = BRIDGE | Granite41-8B | 164 | 163 | 1 | 0 | 0 | 1 | — |
| construction = BRIDGE | Ministral3-14B | 164 | 139 | 25 | 0 | 0 | 25 | — |
| construction = BRIDGE | Cogito-14B | 164 | 160 | 0 | 4 | 0 | 4 | CONNECTION: 4 |
| construction = BRIDGE | All agents | 656 | 626 | 26 | 4 | 0 | 30 | — |
| construction = UNION | Gemma4-12B | 336 | 334 | 2 | 0 | 0 | 2 | — |
| construction = UNION | Granite41-8B | 336 | 323 | 12 | 1 | 0 | 13 | CONNECTION: 1 |
| construction = UNION | Ministral3-14B | 336 | 307 | 24 | 5 | 0 | 29 | CONNECTION: 5 |
| construction = UNION | Cogito-14B | 336 | 302 | 2 | 32 | 0 | 34 | CONNECTION: 29, RUNTIME: 3 |
| construction = UNION | All agents | 1344 | 1266 | 40 | 38 | 0 | 78 | — |
| ambiguity tag = NONE | Gemma4-12B | 67 | 67 | 0 | 0 | 0 | 0 | — |
| ambiguity tag = NONE | Granite41-8B | 67 | 66 | 1 | 0 | 0 | 1 | — |
| ambiguity tag = NONE | Ministral3-14B | 67 | 56 | 11 | 0 | 0 | 11 | — |
| ambiguity tag = NONE | Cogito-14B | 67 | 65 | 0 | 2 | 0 | 2 | CONNECTION: 2 |
| ambiguity tag = NONE | All agents | 268 | 254 | 12 | 2 | 0 | 14 | — |
| ambiguity tag = R1_AMBIGUOUS | Gemma4-12B | 352 | 350 | 2 | 0 | 0 | 2 | — |
| ambiguity tag = R1_AMBIGUOUS | Granite41-8B | 352 | 339 | 12 | 1 | 0 | 13 | CONNECTION: 1 |
| ambiguity tag = R1_AMBIGUOUS | Ministral3-14B | 352 | 319 | 28 | 5 | 0 | 33 | CONNECTION: 5 |
| ambiguity tag = R1_AMBIGUOUS | Cogito-14B | 352 | 317 | 2 | 33 | 0 | 35 | CONNECTION: 30, RUNTIME: 3 |
| ambiguity tag = R1_AMBIGUOUS | All agents | 1408 | 1325 | 44 | 39 | 0 | 83 | — |
| ambiguity tag = R2_AMBIGUOUS | Gemma4-12B | 20 | 20 | 0 | 0 | 0 | 0 | — |
| ambiguity tag = R2_AMBIGUOUS | Granite41-8B | 20 | 20 | 0 | 0 | 0 | 0 | — |
| ambiguity tag = R2_AMBIGUOUS | Ministral3-14B | 20 | 15 | 5 | 0 | 0 | 5 | — |
| ambiguity tag = R2_AMBIGUOUS | Cogito-14B | 20 | 20 | 0 | 0 | 0 | 0 | — |
| ambiguity tag = R2_AMBIGUOUS | All agents | 80 | 75 | 5 | 0 | 0 | 5 | — |
| ambiguity tag = BOTH_AMBIGUOUS | Gemma4-12B | 61 | 61 | 0 | 0 | 0 | 0 | — |
| ambiguity tag = BOTH_AMBIGUOUS | Granite41-8B | 61 | 61 | 0 | 0 | 0 | 0 | — |
| ambiguity tag = BOTH_AMBIGUOUS | Ministral3-14B | 61 | 56 | 5 | 0 | 0 | 5 | — |
| ambiguity tag = BOTH_AMBIGUOUS | Cogito-14B | 61 | 60 | 0 | 1 | 0 | 1 | CONNECTION: 1 |
| ambiguity tag = BOTH_AMBIGUOUS | All agents | 244 | 238 | 5 | 1 | 0 | 6 | — |

E = technical failures / episodes = 108/2000 = 0.0540 (all queries).

## 2b. Hop-1 status per agent (§14.3), every episode whatever its status

CSV: `table02b_hop1_status.csv`

| Split | Agent | Episodes | H1_CLEAN | H1_MIXED | H1_WRONG | H1_NONE | Found R1 (CLEAN + MIXED) |
|---|---|---|---|---|---|---|---|
| All | Gemma4-12B | 500 | 498 | 2 | 0 | 0 | 500 |
| All | Granite41-8B | 500 | 463 | 17 | 20 | 0 | 480 |
| All | Ministral3-14B | 500 | 451 | 19 | 0 | 30 | 470 |
| All | Cogito-14B | 500 | 465 | 34 | 1 | 0 | 499 |
| All | All agents | 2000 | 1877 | 72 | 21 | 30 | 1949 |
| construction = BRIDGE | Gemma4-12B | 164 | 163 | 1 | 0 | 0 | 164 |
| construction = BRIDGE | Granite41-8B | 164 | 137 | 7 | 20 | 0 | 144 |
| construction = BRIDGE | Ministral3-14B | 164 | 125 | 14 | 0 | 25 | 139 |
| construction = BRIDGE | Cogito-14B | 164 | 152 | 11 | 1 | 0 | 163 |
| construction = BRIDGE | All agents | 656 | 577 | 33 | 21 | 25 | 610 |
| construction = UNION | Gemma4-12B | 336 | 335 | 1 | 0 | 0 | 336 |
| construction = UNION | Granite41-8B | 336 | 326 | 10 | 0 | 0 | 336 |
| construction = UNION | Ministral3-14B | 336 | 326 | 5 | 0 | 5 | 331 |
| construction = UNION | Cogito-14B | 336 | 313 | 23 | 0 | 0 | 336 |
| construction = UNION | All agents | 1344 | 1300 | 39 | 0 | 5 | 1339 |
| ambiguity tag = NONE | Gemma4-12B | 67 | 67 | 0 | 0 | 0 | 67 |
| ambiguity tag = NONE | Granite41-8B | 67 | 62 | 3 | 2 | 0 | 65 |
| ambiguity tag = NONE | Ministral3-14B | 67 | 54 | 2 | 0 | 11 | 56 |
| ambiguity tag = NONE | Cogito-14B | 67 | 66 | 1 | 0 | 0 | 67 |
| ambiguity tag = NONE | All agents | 268 | 249 | 6 | 2 | 11 | 255 |
| ambiguity tag = R1_AMBIGUOUS | Gemma4-12B | 352 | 350 | 2 | 0 | 0 | 352 |
| ambiguity tag = R1_AMBIGUOUS | Granite41-8B | 352 | 328 | 12 | 12 | 0 | 340 |
| ambiguity tag = R1_AMBIGUOUS | Ministral3-14B | 352 | 332 | 11 | 0 | 9 | 343 |
| ambiguity tag = R1_AMBIGUOUS | Cogito-14B | 352 | 322 | 30 | 0 | 0 | 352 |
| ambiguity tag = R1_AMBIGUOUS | All agents | 1408 | 1332 | 55 | 12 | 9 | 1387 |
| ambiguity tag = R2_AMBIGUOUS | Gemma4-12B | 20 | 20 | 0 | 0 | 0 | 20 |
| ambiguity tag = R2_AMBIGUOUS | Granite41-8B | 20 | 18 | 0 | 2 | 0 | 18 |
| ambiguity tag = R2_AMBIGUOUS | Ministral3-14B | 20 | 13 | 2 | 0 | 5 | 15 |
| ambiguity tag = R2_AMBIGUOUS | Cogito-14B | 20 | 19 | 1 | 0 | 0 | 20 |
| ambiguity tag = R2_AMBIGUOUS | All agents | 80 | 70 | 3 | 2 | 5 | 73 |
| ambiguity tag = BOTH_AMBIGUOUS | Gemma4-12B | 61 | 61 | 0 | 0 | 0 | 61 |
| ambiguity tag = BOTH_AMBIGUOUS | Granite41-8B | 61 | 55 | 2 | 4 | 0 | 57 |
| ambiguity tag = BOTH_AMBIGUOUS | Ministral3-14B | 61 | 52 | 4 | 0 | 5 | 56 |
| ambiguity tag = BOTH_AMBIGUOUS | Cogito-14B | 61 | 58 | 2 | 1 | 0 | 60 |
| ambiguity tag = BOTH_AMBIGUOUS | All agents | 244 | 226 | 8 | 5 | 5 | 234 |

## 2c. Explored-bridge ranks (§15): position in the first R1 list from s that contained the bridge (page size 50, so ranks 1–50 are page 1)

CSV: `table02c_bridge_ranks.csv`

| Split | Agent | Explored bridges | 1 | 2–10 | 11–50 | 51–100 | >100 | NA | Median | Max |
|---|---|---|---|---|---|---|---|---|---|---|
| All | Gemma4-12B | 844 | 431 | 406 | 7 | 0 | 0 | 0 | 1.0000 | 18 |
| All | Granite41-8B | 1741 | 422 | 1127 | 192 | 0 | 0 | 0 | 3.0000 | 42 |
| All | Ministral3-14B | 1704 | 405 | 1175 | 124 | 0 | 0 | 0 | 3.0000 | 42 |
| All | Cogito-14B | 1646 | 408 | 1128 | 110 | 0 | 0 | 0 | 3.0000 | 21 |
| All | All agents | 5935 | 1666 | 3836 | 433 | 0 | 0 | 0 | 3.0000 | 42 |
| construction = BRIDGE | Gemma4-12B | 224 | 142 | 79 | 3 | 0 | 0 | 0 | 1.0000 | 16 |
| construction = BRIDGE | Granite41-8B | 173 | 116 | 57 | 0 | 0 | 0 | 0 | 1.0000 | 7 |
| construction = BRIDGE | Ministral3-14B | 183 | 111 | 69 | 3 | 0 | 0 | 0 | 1.0000 | 16 |
| construction = BRIDGE | Cogito-14B | 207 | 131 | 74 | 2 | 0 | 0 | 0 | 1.0000 | 16 |
| construction = BRIDGE | All agents | 787 | 500 | 279 | 8 | 0 | 0 | 0 | 1.0000 | 16 |
| construction = UNION | Gemma4-12B | 620 | 289 | 327 | 4 | 0 | 0 | 0 | 2.0000 | 18 |
| construction = UNION | Granite41-8B | 1568 | 306 | 1070 | 192 | 0 | 0 | 0 | 4.0000 | 42 |
| construction = UNION | Ministral3-14B | 1521 | 294 | 1106 | 121 | 0 | 0 | 0 | 3.0000 | 42 |
| construction = UNION | Cogito-14B | 1439 | 277 | 1054 | 108 | 0 | 0 | 0 | 3.0000 | 21 |
| construction = UNION | All agents | 5148 | 1166 | 3557 | 425 | 0 | 0 | 0 | 3.0000 | 42 |
| ambiguity tag = NONE | Gemma4-12B | 67 | 67 | 0 | 0 | 0 | 0 | 0 | 1.0000 | 1 |
| ambiguity tag = NONE | Granite41-8B | 63 | 63 | 0 | 0 | 0 | 0 | 0 | 1.0000 | 1 |
| ambiguity tag = NONE | Ministral3-14B | 56 | 56 | 0 | 0 | 0 | 0 | 0 | 1.0000 | 1 |
| ambiguity tag = NONE | Cogito-14B | 65 | 65 | 0 | 0 | 0 | 0 | 0 | 1.0000 | 1 |
| ambiguity tag = NONE | All agents | 251 | 251 | 0 | 0 | 0 | 0 | 0 | 1.0000 | 1 |
| ambiguity tag = R1_AMBIGUOUS | Gemma4-12B | 636 | 305 | 327 | 4 | 0 | 0 | 0 | 2.0000 | 18 |
| ambiguity tag = R1_AMBIGUOUS | Granite41-8B | 1572 | 310 | 1070 | 192 | 0 | 0 | 0 | 4.0000 | 42 |
| ambiguity tag = R1_AMBIGUOUS | Ministral3-14B | 1531 | 304 | 1106 | 121 | 0 | 0 | 0 | 3.0000 | 42 |
| ambiguity tag = R1_AMBIGUOUS | Cogito-14B | 1451 | 289 | 1054 | 108 | 0 | 0 | 0 | 3.0000 | 21 |
| ambiguity tag = R1_AMBIGUOUS | All agents | 5190 | 1208 | 3557 | 425 | 0 | 0 | 0 | 3.0000 | 42 |
| ambiguity tag = R2_AMBIGUOUS | Gemma4-12B | 20 | 20 | 0 | 0 | 0 | 0 | 0 | 1.0000 | 1 |
| ambiguity tag = R2_AMBIGUOUS | Granite41-8B | 18 | 18 | 0 | 0 | 0 | 0 | 0 | 1.0000 | 1 |
| ambiguity tag = R2_AMBIGUOUS | Ministral3-14B | 14 | 14 | 0 | 0 | 0 | 0 | 0 | 1.0000 | 1 |
| ambiguity tag = R2_AMBIGUOUS | Cogito-14B | 19 | 19 | 0 | 0 | 0 | 0 | 0 | 1.0000 | 1 |
| ambiguity tag = R2_AMBIGUOUS | All agents | 71 | 71 | 0 | 0 | 0 | 0 | 0 | 1.0000 | 1 |
| ambiguity tag = BOTH_AMBIGUOUS | Gemma4-12B | 121 | 39 | 79 | 3 | 0 | 0 | 0 | 2.0000 | 16 |
| ambiguity tag = BOTH_AMBIGUOUS | Granite41-8B | 88 | 31 | 57 | 0 | 0 | 0 | 0 | 2.0000 | 7 |
| ambiguity tag = BOTH_AMBIGUOUS | Ministral3-14B | 103 | 31 | 69 | 3 | 0 | 0 | 0 | 2.0000 | 16 |
| ambiguity tag = BOTH_AMBIGUOUS | Cogito-14B | 111 | 35 | 74 | 2 | 0 | 0 | 0 | 2.0000 | 16 |
| ambiguity tag = BOTH_AMBIGUOUS | All agents | 423 | 136 | 279 | 8 | 0 | 0 | 0 | 2.0000 | 16 |

## 2d. Label A (§13), retained answers of SUCCESS episodes

CSV: `table02d_label_a.csv`

| Split | Agent | SUCCESS episodes | Answers | GOLD | GOLD_BRIDGE_EXTRA | ALT_VALID | OFF_QUESTION | UNRESOLVED |
|---|---|---|---|---|---|---|---|---|
| All | Gemma4-12B | 498 | 27385 | 26968 | 0 | 308 | 109 | 0 |
| All | Granite41-8B | 486 | 22524 | 21224 | 0 | 220 | 1080 | 0 |
| All | Ministral3-14B | 446 | 29543 | 28928 | 0 | 251 | 364 | 0 |
| All | Cogito-14B | 462 | 21809 | 21105 | 0 | 256 | 448 | 0 |
| All | All agents | 1892 | 101261 | 98225 | 0 | 1035 | 2001 | 0 |
| construction = BRIDGE | Gemma4-12B | 164 | 2336 | 1997 | 0 | 308 | 31 | 0 |
| construction = BRIDGE | Granite41-8B | 163 | 2642 | 1606 | 0 | 220 | 816 | 0 |
| construction = BRIDGE | Ministral3-14B | 139 | 2002 | 1544 | 0 | 251 | 207 | 0 |
| construction = BRIDGE | Cogito-14B | 160 | 2264 | 1663 | 0 | 256 | 345 | 0 |
| construction = BRIDGE | All agents | 626 | 9244 | 6810 | 0 | 1035 | 1399 | 0 |
| construction = UNION | Gemma4-12B | 334 | 25049 | 24971 | 0 | 0 | 78 | 0 |
| construction = UNION | Granite41-8B | 323 | 19882 | 19618 | 0 | 0 | 264 | 0 |
| construction = UNION | Ministral3-14B | 307 | 27541 | 27384 | 0 | 0 | 157 | 0 |
| construction = UNION | Cogito-14B | 302 | 19545 | 19442 | 0 | 0 | 103 | 0 |
| construction = UNION | All agents | 1266 | 92017 | 91415 | 0 | 0 | 602 | 0 |
| ambiguity tag = NONE | Gemma4-12B | 67 | 1209 | 1209 | 0 | 0 | 0 | 0 |
| ambiguity tag = NONE | Granite41-8B | 66 | 1095 | 1050 | 0 | 0 | 45 | 0 |
| ambiguity tag = NONE | Ministral3-14B | 56 | 990 | 987 | 0 | 0 | 3 | 0 |
| ambiguity tag = NONE | Cogito-14B | 65 | 1053 | 1053 | 0 | 0 | 0 | 0 |
| ambiguity tag = NONE | All agents | 254 | 4347 | 4299 | 0 | 0 | 48 | 0 |
| ambiguity tag = R1_AMBIGUOUS | Gemma4-12B | 350 | 25202 | 25124 | 0 | 0 | 78 | 0 |
| ambiguity tag = R1_AMBIGUOUS | Granite41-8B | 339 | 19988 | 19638 | 0 | 0 | 350 | 0 |
| ambiguity tag = R1_AMBIGUOUS | Ministral3-14B | 319 | 27652 | 27474 | 0 | 0 | 178 | 0 |
| ambiguity tag = R1_AMBIGUOUS | Cogito-14B | 317 | 19621 | 19503 | 0 | 0 | 118 | 0 |
| ambiguity tag = R1_AMBIGUOUS | All agents | 1325 | 92463 | 91739 | 0 | 0 | 724 | 0 |
| ambiguity tag = R2_AMBIGUOUS | Gemma4-12B | 20 | 310 | 308 | 0 | 0 | 2 | 0 |
| ambiguity tag = R2_AMBIGUOUS | Granite41-8B | 20 | 357 | 272 | 0 | 0 | 85 | 0 |
| ambiguity tag = R2_AMBIGUOUS | Ministral3-14B | 15 | 281 | 199 | 0 | 0 | 82 | 0 |
| ambiguity tag = R2_AMBIGUOUS | Cogito-14B | 20 | 303 | 272 | 0 | 0 | 31 | 0 |
| ambiguity tag = R2_AMBIGUOUS | All agents | 75 | 1251 | 1051 | 0 | 0 | 200 | 0 |
| ambiguity tag = BOTH_AMBIGUOUS | Gemma4-12B | 61 | 664 | 327 | 0 | 308 | 29 | 0 |
| ambiguity tag = BOTH_AMBIGUOUS | Granite41-8B | 61 | 1084 | 264 | 0 | 220 | 600 | 0 |
| ambiguity tag = BOTH_AMBIGUOUS | Ministral3-14B | 56 | 620 | 268 | 0 | 251 | 101 | 0 |
| ambiguity tag = BOTH_AMBIGUOUS | Cogito-14B | 60 | 832 | 277 | 0 | 256 | 299 | 0 |
| ambiguity tag = BOTH_AMBIGUOUS | All agents | 238 | 3200 | 1136 | 0 | 1035 | 1029 | 0 |

## 2e. Label B (§14.1), retained answers of SUCCESS episodes

CSV: `table02e_label_b.csv`

| Split | Agent | SUCCESS episodes | SUPPORTED | PATH_INVALID | KG_UNSUPPORTED | UNGROUNDED | NOT_APPLICABLE |
|---|---|---|---|---|---|---|---|
| All | Gemma4-12B | 498 | 27276 | 108 | 0 | 1 | 0 |
| All | Granite41-8B | 486 | 21374 | 1149 | 0 | 1 | 0 |
| All | Ministral3-14B | 446 | 29143 | 385 | 0 | 15 | 0 |
| All | Cogito-14B | 462 | 21353 | 357 | 0 | 99 | 0 |
| All | All agents | 1892 | 99146 | 1999 | 0 | 116 | 0 |
| construction = BRIDGE | Gemma4-12B | 164 | 2305 | 31 | 0 | 0 | 0 |
| construction = BRIDGE | Granite41-8B | 163 | 1805 | 837 | 0 | 0 | 0 |
| construction = BRIDGE | Ministral3-14B | 139 | 1793 | 209 | 0 | 0 | 0 |
| construction = BRIDGE | Cogito-14B | 160 | 1912 | 352 | 0 | 0 | 0 |
| construction = BRIDGE | All agents | 626 | 7815 | 1429 | 0 | 0 | 0 |
| construction = UNION | Gemma4-12B | 334 | 24971 | 77 | 0 | 1 | 0 |
| construction = UNION | Granite41-8B | 323 | 19569 | 312 | 0 | 1 | 0 |
| construction = UNION | Ministral3-14B | 307 | 27350 | 176 | 0 | 15 | 0 |
| construction = UNION | Cogito-14B | 302 | 19441 | 5 | 0 | 99 | 0 |
| construction = UNION | All agents | 1266 | 91331 | 570 | 0 | 116 | 0 |
| ambiguity tag = NONE | Gemma4-12B | 67 | 1209 | 0 | 0 | 0 | 0 |
| ambiguity tag = NONE | Granite41-8B | 66 | 1048 | 47 | 0 | 0 | 0 |
| ambiguity tag = NONE | Ministral3-14B | 56 | 987 | 3 | 0 | 0 | 0 |
| ambiguity tag = NONE | Cogito-14B | 65 | 1053 | 0 | 0 | 0 | 0 |
| ambiguity tag = NONE | All agents | 254 | 4297 | 50 | 0 | 0 | 0 |
| ambiguity tag = R1_AMBIGUOUS | Gemma4-12B | 350 | 25124 | 77 | 0 | 1 | 0 |
| ambiguity tag = R1_AMBIGUOUS | Granite41-8B | 339 | 19584 | 403 | 0 | 1 | 0 |
| ambiguity tag = R1_AMBIGUOUS | Ministral3-14B | 319 | 27439 | 198 | 0 | 15 | 0 |
| ambiguity tag = R1_AMBIGUOUS | Cogito-14B | 317 | 19501 | 21 | 0 | 99 | 0 |
| ambiguity tag = R1_AMBIGUOUS | All agents | 1325 | 91648 | 699 | 0 | 116 | 0 |
| ambiguity tag = R2_AMBIGUOUS | Gemma4-12B | 20 | 308 | 2 | 0 | 0 | 0 |
| ambiguity tag = R2_AMBIGUOUS | Granite41-8B | 20 | 272 | 85 | 0 | 0 | 0 |
| ambiguity tag = R2_AMBIGUOUS | Ministral3-14B | 15 | 199 | 82 | 0 | 0 | 0 |
| ambiguity tag = R2_AMBIGUOUS | Cogito-14B | 20 | 272 | 31 | 0 | 0 | 0 |
| ambiguity tag = R2_AMBIGUOUS | All agents | 75 | 1051 | 200 | 0 | 0 | 0 |
| ambiguity tag = BOTH_AMBIGUOUS | Gemma4-12B | 61 | 635 | 29 | 0 | 0 | 0 |
| ambiguity tag = BOTH_AMBIGUOUS | Granite41-8B | 61 | 470 | 614 | 0 | 0 | 0 |
| ambiguity tag = BOTH_AMBIGUOUS | Ministral3-14B | 56 | 518 | 102 | 0 | 0 | 0 |
| ambiguity tag = BOTH_AMBIGUOUS | Cogito-14B | 60 | 527 | 305 | 0 | 0 | 0 |
| ambiguity tag = BOTH_AMBIGUOUS | All agents | 238 | 2150 | 1050 | 0 | 0 | 0 |

## 2f. Ratio metrics including benchmark F1 (§15)

CSV: `table02f_ratio_metrics.csv`

| Split | Agent | Metric | Mean of per-episode values | Defined episodes | NA episodes | Pooled numerator | Pooled denominator | Pooled ratio |
|---|---|---|---|---|---|---|---|---|
| All | Gemma4-12B | Question-valid precision | 0.9942 | 497 | 3 | 27276 | 27385 | 0.9960 |
| All | Gemma4-12B | OFF_QUESTION rate | 0.0058 | 497 | 3 | 109 | 27385 | 0.0040 |
| All | Gemma4-12B | UNRESOLVED rate | 0.0000 | 497 | 3 | 0 | 27385 | 0.0000 |
| All | Gemma4-12B | UNGROUNDED rate | 0.0000 | 497 | 3 | 1 | 27385 | 0.0000 |
| All | Gemma4-12B | Benchmark P | 0.9507 | 497 | 3 | 26968 | 27385 | 0.9848 |
| All | Gemma4-12B | Benchmark R | 0.7181 | 498 | 2 | 26968 | 60639 | 0.4447 |
| All | Gemma4-12B | Benchmark F1 | 0.7468 | 498 | 2 | 53936 | 88024 | 0.6127 |
| All | Granite41-8B | Question-valid precision | 0.8665 | 481 | 19 | 21444 | 22524 | 0.9521 |
| All | Granite41-8B | OFF_QUESTION rate | 0.1335 | 481 | 19 | 1080 | 22524 | 0.0479 |
| All | Granite41-8B | UNRESOLVED rate | 0.0000 | 481 | 19 | 0 | 22524 | 0.0000 |
| All | Granite41-8B | UNGROUNDED rate | 0.0000 | 481 | 19 | 1 | 22524 | 0.0000 |
| All | Granite41-8B | Benchmark P | 0.8396 | 481 | 19 | 21224 | 22524 | 0.9423 |
| All | Granite41-8B | Benchmark R | 0.5800 | 486 | 14 | 21224 | 58617 | 0.3621 |
| All | Granite41-8B | Benchmark F1 | 0.6201 | 486 | 14 | 42448 | 81141 | 0.5231 |
| All | Ministral3-14B | Question-valid precision | 0.9662 | 444 | 56 | 29179 | 29543 | 0.9877 |
| All | Ministral3-14B | OFF_QUESTION rate | 0.0338 | 444 | 56 | 364 | 29543 | 0.0123 |
| All | Ministral3-14B | UNRESOLVED rate | 0.0000 | 444 | 56 | 0 | 29543 | 0.0000 |
| All | Ministral3-14B | UNGROUNDED rate | 0.0003 | 444 | 56 | 15 | 29543 | 0.0005 |
| All | Ministral3-14B | Benchmark P | 0.9271 | 444 | 56 | 28928 | 29543 | 0.9792 |
| All | Ministral3-14B | Benchmark R | 0.7427 | 446 | 54 | 28928 | 52675 | 0.5492 |
| All | Ministral3-14B | Benchmark F1 | 0.7709 | 446 | 54 | 57856 | 82218 | 0.7037 |
| All | Cogito-14B | Question-valid precision | 0.9602 | 430 | 70 | 21361 | 21809 | 0.9795 |
| All | Cogito-14B | OFF_QUESTION rate | 0.0398 | 430 | 70 | 448 | 21809 | 0.0205 |
| All | Cogito-14B | UNRESOLVED rate | 0.0000 | 430 | 70 | 0 | 21809 | 0.0000 |
| All | Cogito-14B | UNGROUNDED rate | 0.0012 | 430 | 70 | 99 | 21809 | 0.0045 |
| All | Cogito-14B | Benchmark P | 0.9225 | 430 | 70 | 21105 | 21809 | 0.9677 |
| All | Cogito-14B | Benchmark R | 0.6293 | 462 | 38 | 21105 | 54882 | 0.3846 |
| All | Cogito-14B | Benchmark F1 | 0.6472 | 462 | 38 | 42210 | 76691 | 0.5504 |
| construction = BRIDGE | Gemma4-12B | Question-valid precision | 0.9860 | 164 | 0 | 2305 | 2336 | 0.9867 |
| construction = BRIDGE | Gemma4-12B | OFF_QUESTION rate | 0.0140 | 164 | 0 | 31 | 2336 | 0.0133 |
| construction = BRIDGE | Gemma4-12B | UNRESOLVED rate | 0.0000 | 164 | 0 | 0 | 2336 | 0.0000 |
| construction = BRIDGE | Gemma4-12B | UNGROUNDED rate | 0.0000 | 164 | 0 | 0 | 2336 | 0.0000 |
| construction = BRIDGE | Gemma4-12B | Benchmark P | 0.8543 | 164 | 0 | 1997 | 2336 | 0.8549 |
| construction = BRIDGE | Gemma4-12B | Benchmark R | 1.0000 | 164 | 0 | 1997 | 1997 | 1.0000 |
| construction = BRIDGE | Gemma4-12B | Benchmark F1 | 0.8863 | 164 | 0 | 3994 | 4333 | 0.9218 |
| construction = BRIDGE | Granite41-8B | Question-valid precision | 0.7917 | 161 | 3 | 1826 | 2642 | 0.6911 |
| construction = BRIDGE | Granite41-8B | OFF_QUESTION rate | 0.2083 | 161 | 3 | 816 | 2642 | 0.3089 |
| construction = BRIDGE | Granite41-8B | UNRESOLVED rate | 0.0000 | 161 | 3 | 0 | 2642 | 0.0000 |
| construction = BRIDGE | Granite41-8B | UNGROUNDED rate | 0.0000 | 161 | 3 | 0 | 2642 | 0.0000 |
| construction = BRIDGE | Granite41-8B | Benchmark P | 0.7115 | 161 | 3 | 1606 | 2642 | 0.6079 |
| construction = BRIDGE | Granite41-8B | Benchmark R | 0.8283 | 163 | 1 | 1606 | 1882 | 0.8533 |
| construction = BRIDGE | Granite41-8B | Benchmark F1 | 0.7234 | 163 | 1 | 3212 | 4524 | 0.7100 |
| construction = BRIDGE | Ministral3-14B | Question-valid precision | 0.9017 | 138 | 26 | 1795 | 2002 | 0.8966 |
| construction = BRIDGE | Ministral3-14B | OFF_QUESTION rate | 0.0983 | 138 | 26 | 207 | 2002 | 0.1034 |
| construction = BRIDGE | Ministral3-14B | UNRESOLVED rate | 0.0000 | 138 | 26 | 0 | 2002 | 0.0000 |
| construction = BRIDGE | Ministral3-14B | UNGROUNDED rate | 0.0000 | 138 | 26 | 0 | 2002 | 0.0000 |
| construction = BRIDGE | Ministral3-14B | Benchmark P | 0.7758 | 138 | 26 | 1544 | 2002 | 0.7712 |
| construction = BRIDGE | Ministral3-14B | Benchmark R | 0.9352 | 139 | 25 | 1544 | 1639 | 0.9420 |
| construction = BRIDGE | Ministral3-14B | Benchmark F1 | 0.8022 | 139 | 25 | 3088 | 3641 | 0.8481 |
| construction = BRIDGE | Cogito-14B | Question-valid precision | 0.8937 | 154 | 10 | 1919 | 2264 | 0.8476 |
| construction = BRIDGE | Cogito-14B | OFF_QUESTION rate | 0.1063 | 154 | 10 | 345 | 2264 | 0.1524 |
| construction = BRIDGE | Cogito-14B | UNRESOLVED rate | 0.0000 | 154 | 10 | 0 | 2264 | 0.0000 |
| construction = BRIDGE | Cogito-14B | UNGROUNDED rate | 0.0000 | 154 | 10 | 0 | 2264 | 0.0000 |
| construction = BRIDGE | Cogito-14B | Benchmark P | 0.7885 | 154 | 10 | 1663 | 2264 | 0.7345 |
| construction = BRIDGE | Cogito-14B | Benchmark R | 0.9169 | 160 | 4 | 1663 | 1893 | 0.8785 |
| construction = BRIDGE | Cogito-14B | Benchmark F1 | 0.7829 | 160 | 4 | 3326 | 4157 | 0.8001 |
| construction = UNION | Gemma4-12B | Question-valid precision | 0.9982 | 333 | 3 | 24971 | 25049 | 0.9969 |
| construction = UNION | Gemma4-12B | OFF_QUESTION rate | 0.0018 | 333 | 3 | 78 | 25049 | 0.0031 |
| construction = UNION | Gemma4-12B | UNRESOLVED rate | 0.0000 | 333 | 3 | 0 | 25049 | 0.0000 |
| construction = UNION | Gemma4-12B | UNGROUNDED rate | 0.0000 | 333 | 3 | 1 | 25049 | 0.0000 |
| construction = UNION | Gemma4-12B | Benchmark P | 0.9982 | 333 | 3 | 24971 | 25049 | 0.9969 |
| construction = UNION | Gemma4-12B | Benchmark R | 0.5797 | 334 | 2 | 24971 | 58642 | 0.4258 |
| construction = UNION | Gemma4-12B | Benchmark F1 | 0.6783 | 334 | 2 | 49942 | 83691 | 0.5967 |
| construction = UNION | Granite41-8B | Question-valid precision | 0.9041 | 320 | 16 | 19618 | 19882 | 0.9867 |
| construction = UNION | Granite41-8B | OFF_QUESTION rate | 0.0959 | 320 | 16 | 264 | 19882 | 0.0133 |
| construction = UNION | Granite41-8B | UNRESOLVED rate | 0.0000 | 320 | 16 | 0 | 19882 | 0.0000 |
| construction = UNION | Granite41-8B | UNGROUNDED rate | 0.0000 | 320 | 16 | 1 | 19882 | 0.0001 |
| construction = UNION | Granite41-8B | Benchmark P | 0.9041 | 320 | 16 | 19618 | 19882 | 0.9867 |
| construction = UNION | Granite41-8B | Benchmark R | 0.4547 | 323 | 13 | 19618 | 56735 | 0.3458 |
| construction = UNION | Granite41-8B | Benchmark F1 | 0.5680 | 323 | 13 | 39236 | 76617 | 0.5121 |
| construction = UNION | Ministral3-14B | Question-valid precision | 0.9953 | 306 | 30 | 27384 | 27541 | 0.9943 |
| construction = UNION | Ministral3-14B | OFF_QUESTION rate | 0.0047 | 306 | 30 | 157 | 27541 | 0.0057 |
| construction = UNION | Ministral3-14B | UNRESOLVED rate | 0.0000 | 306 | 30 | 0 | 27541 | 0.0000 |
| construction = UNION | Ministral3-14B | UNGROUNDED rate | 0.0005 | 306 | 30 | 15 | 27541 | 0.0005 |
| construction = UNION | Ministral3-14B | Benchmark P | 0.9953 | 306 | 30 | 27384 | 27541 | 0.9943 |
| construction = UNION | Ministral3-14B | Benchmark R | 0.6555 | 307 | 29 | 27384 | 51036 | 0.5366 |
| construction = UNION | Ministral3-14B | Benchmark F1 | 0.7568 | 307 | 29 | 54768 | 78577 | 0.6970 |
| construction = UNION | Cogito-14B | Question-valid precision | 0.9974 | 276 | 60 | 19442 | 19545 | 0.9947 |
| construction = UNION | Cogito-14B | OFF_QUESTION rate | 0.0026 | 276 | 60 | 103 | 19545 | 0.0053 |
| construction = UNION | Cogito-14B | UNRESOLVED rate | 0.0000 | 276 | 60 | 0 | 19545 | 0.0000 |
| construction = UNION | Cogito-14B | UNGROUNDED rate | 0.0019 | 276 | 60 | 99 | 19545 | 0.0051 |
| construction = UNION | Cogito-14B | Benchmark P | 0.9974 | 276 | 60 | 19442 | 19545 | 0.9947 |
| construction = UNION | Cogito-14B | Benchmark R | 0.4769 | 302 | 34 | 19442 | 52989 | 0.3669 |
| construction = UNION | Cogito-14B | Benchmark F1 | 0.5752 | 302 | 34 | 38884 | 72534 | 0.5361 |
| ambiguity tag = NONE | Gemma4-12B | Question-valid precision | 1.0000 | 67 | 0 | 1209 | 1209 | 1.0000 |
| ambiguity tag = NONE | Gemma4-12B | OFF_QUESTION rate | 0.0000 | 67 | 0 | 0 | 1209 | 0.0000 |
| ambiguity tag = NONE | Gemma4-12B | UNRESOLVED rate | 0.0000 | 67 | 0 | 0 | 1209 | 0.0000 |
| ambiguity tag = NONE | Gemma4-12B | UNGROUNDED rate | 0.0000 | 67 | 0 | 0 | 1209 | 0.0000 |
| ambiguity tag = NONE | Gemma4-12B | Benchmark P | 1.0000 | 67 | 0 | 1209 | 1209 | 1.0000 |
| ambiguity tag = NONE | Gemma4-12B | Benchmark R | 1.0000 | 67 | 0 | 1209 | 1209 | 1.0000 |
| ambiguity tag = NONE | Gemma4-12B | Benchmark F1 | 1.0000 | 67 | 0 | 2418 | 2418 | 1.0000 |
| ambiguity tag = NONE | Granite41-8B | Question-valid precision | 0.9408 | 66 | 1 | 1050 | 1095 | 0.9589 |
| ambiguity tag = NONE | Granite41-8B | OFF_QUESTION rate | 0.0592 | 66 | 1 | 45 | 1095 | 0.0411 |
| ambiguity tag = NONE | Granite41-8B | UNRESOLVED rate | 0.0000 | 66 | 1 | 0 | 1095 | 0.0000 |
| ambiguity tag = NONE | Granite41-8B | UNGROUNDED rate | 0.0000 | 66 | 1 | 0 | 1095 | 0.0000 |
| ambiguity tag = NONE | Granite41-8B | Benchmark P | 0.9408 | 66 | 1 | 1050 | 1095 | 0.9589 |
| ambiguity tag = NONE | Granite41-8B | Benchmark R | 0.9424 | 66 | 1 | 1050 | 1094 | 0.9598 |
| ambiguity tag = NONE | Granite41-8B | Benchmark F1 | 0.9413 | 66 | 1 | 2100 | 2189 | 0.9593 |
| ambiguity tag = NONE | Ministral3-14B | Question-valid precision | 0.9929 | 56 | 11 | 987 | 990 | 0.9970 |
| ambiguity tag = NONE | Ministral3-14B | OFF_QUESTION rate | 0.0071 | 56 | 11 | 3 | 990 | 0.0030 |
| ambiguity tag = NONE | Ministral3-14B | UNRESOLVED rate | 0.0000 | 56 | 11 | 0 | 990 | 0.0000 |
| ambiguity tag = NONE | Ministral3-14B | UNGROUNDED rate | 0.0000 | 56 | 11 | 0 | 990 | 0.0000 |
| ambiguity tag = NONE | Ministral3-14B | Benchmark P | 0.9929 | 56 | 11 | 987 | 990 | 0.9970 |
| ambiguity tag = NONE | Ministral3-14B | Benchmark R | 0.9964 | 56 | 11 | 987 | 989 | 0.9980 |
| ambiguity tag = NONE | Ministral3-14B | Benchmark F1 | 0.9942 | 56 | 11 | 1974 | 1979 | 0.9975 |
| ambiguity tag = NONE | Cogito-14B | Question-valid precision | 1.0000 | 65 | 2 | 1053 | 1053 | 1.0000 |
| ambiguity tag = NONE | Cogito-14B | OFF_QUESTION rate | 0.0000 | 65 | 2 | 0 | 1053 | 0.0000 |
| ambiguity tag = NONE | Cogito-14B | UNRESOLVED rate | 0.0000 | 65 | 2 | 0 | 1053 | 0.0000 |
| ambiguity tag = NONE | Cogito-14B | UNGROUNDED rate | 0.0000 | 65 | 2 | 0 | 1053 | 0.0000 |
| ambiguity tag = NONE | Cogito-14B | Benchmark P | 1.0000 | 65 | 2 | 1053 | 1053 | 1.0000 |
| ambiguity tag = NONE | Cogito-14B | Benchmark R | 0.9768 | 65 | 2 | 1053 | 1114 | 0.9452 |
| ambiguity tag = NONE | Cogito-14B | Benchmark F1 | 0.9816 | 65 | 2 | 2106 | 2167 | 0.9719 |
| ambiguity tag = R1_AMBIGUOUS | Gemma4-12B | Question-valid precision | 0.9983 | 349 | 3 | 25124 | 25202 | 0.9969 |
| ambiguity tag = R1_AMBIGUOUS | Gemma4-12B | OFF_QUESTION rate | 0.0017 | 349 | 3 | 78 | 25202 | 0.0031 |
| ambiguity tag = R1_AMBIGUOUS | Gemma4-12B | UNRESOLVED rate | 0.0000 | 349 | 3 | 0 | 25202 | 0.0000 |
| ambiguity tag = R1_AMBIGUOUS | Gemma4-12B | UNGROUNDED rate | 0.0000 | 349 | 3 | 1 | 25202 | 0.0000 |
| ambiguity tag = R1_AMBIGUOUS | Gemma4-12B | Benchmark P | 0.9983 | 349 | 3 | 25124 | 25202 | 0.9969 |
| ambiguity tag = R1_AMBIGUOUS | Gemma4-12B | Benchmark R | 0.5989 | 350 | 2 | 25124 | 58795 | 0.4273 |
| ambiguity tag = R1_AMBIGUOUS | Gemma4-12B | Benchmark F1 | 0.6930 | 350 | 2 | 50248 | 83997 | 0.5982 |
| ambiguity tag = R1_AMBIGUOUS | Granite41-8B | Question-valid precision | 0.8757 | 336 | 16 | 19638 | 19988 | 0.9825 |
| ambiguity tag = R1_AMBIGUOUS | Granite41-8B | OFF_QUESTION rate | 0.1243 | 336 | 16 | 350 | 19988 | 0.0175 |
| ambiguity tag = R1_AMBIGUOUS | Granite41-8B | UNRESOLVED rate | 0.0000 | 336 | 16 | 0 | 19988 | 0.0000 |
| ambiguity tag = R1_AMBIGUOUS | Granite41-8B | UNGROUNDED rate | 0.0000 | 336 | 16 | 1 | 19988 | 0.0001 |
| ambiguity tag = R1_AMBIGUOUS | Granite41-8B | Benchmark P | 0.8757 | 336 | 16 | 19638 | 19988 | 0.9825 |
| ambiguity tag = R1_AMBIGUOUS | Granite41-8B | Benchmark R | 0.4493 | 339 | 13 | 19638 | 56888 | 0.3452 |
| ambiguity tag = R1_AMBIGUOUS | Granite41-8B | Benchmark F1 | 0.5546 | 339 | 13 | 39276 | 76876 | 0.5109 |
| ambiguity tag = R1_AMBIGUOUS | Ministral3-14B | Question-valid precision | 0.9868 | 318 | 34 | 27474 | 27652 | 0.9936 |
| ambiguity tag = R1_AMBIGUOUS | Ministral3-14B | OFF_QUESTION rate | 0.0132 | 318 | 34 | 178 | 27652 | 0.0064 |
| ambiguity tag = R1_AMBIGUOUS | Ministral3-14B | UNRESOLVED rate | 0.0000 | 318 | 34 | 0 | 27652 | 0.0000 |
| ambiguity tag = R1_AMBIGUOUS | Ministral3-14B | UNGROUNDED rate | 0.0004 | 318 | 34 | 15 | 27652 | 0.0005 |
| ambiguity tag = R1_AMBIGUOUS | Ministral3-14B | Benchmark P | 0.9868 | 318 | 34 | 27474 | 27652 | 0.9936 |
| ambiguity tag = R1_AMBIGUOUS | Ministral3-14B | Benchmark R | 0.6597 | 319 | 33 | 27474 | 51176 | 0.5369 |
| ambiguity tag = R1_AMBIGUOUS | Ministral3-14B | Benchmark F1 | 0.7564 | 319 | 33 | 54948 | 78828 | 0.6971 |
| ambiguity tag = R1_AMBIGUOUS | Cogito-14B | Question-valid precision | 0.9865 | 289 | 63 | 19503 | 19621 | 0.9940 |
| ambiguity tag = R1_AMBIGUOUS | Cogito-14B | OFF_QUESTION rate | 0.0135 | 289 | 63 | 118 | 19621 | 0.0060 |
| ambiguity tag = R1_AMBIGUOUS | Cogito-14B | UNRESOLVED rate | 0.0000 | 289 | 63 | 0 | 19621 | 0.0000 |
| ambiguity tag = R1_AMBIGUOUS | Cogito-14B | UNGROUNDED rate | 0.0018 | 289 | 63 | 99 | 19621 | 0.0050 |
| ambiguity tag = R1_AMBIGUOUS | Cogito-14B | Benchmark P | 0.9865 | 289 | 63 | 19503 | 19621 | 0.9940 |
| ambiguity tag = R1_AMBIGUOUS | Cogito-14B | Benchmark R | 0.4860 | 317 | 35 | 19503 | 53136 | 0.3670 |
| ambiguity tag = R1_AMBIGUOUS | Cogito-14B | Benchmark F1 | 0.5782 | 317 | 35 | 39006 | 72757 | 0.5361 |
| ambiguity tag = R2_AMBIGUOUS | Gemma4-12B | Question-valid precision | 0.9750 | 20 | 0 | 308 | 310 | 0.9935 |
| ambiguity tag = R2_AMBIGUOUS | Gemma4-12B | OFF_QUESTION rate | 0.0250 | 20 | 0 | 2 | 310 | 0.0065 |
| ambiguity tag = R2_AMBIGUOUS | Gemma4-12B | UNRESOLVED rate | 0.0000 | 20 | 0 | 0 | 310 | 0.0000 |
| ambiguity tag = R2_AMBIGUOUS | Gemma4-12B | UNGROUNDED rate | 0.0000 | 20 | 0 | 0 | 310 | 0.0000 |
| ambiguity tag = R2_AMBIGUOUS | Gemma4-12B | Benchmark P | 0.9750 | 20 | 0 | 308 | 310 | 0.9935 |
| ambiguity tag = R2_AMBIGUOUS | Gemma4-12B | Benchmark R | 1.0000 | 20 | 0 | 308 | 308 | 1.0000 |
| ambiguity tag = R2_AMBIGUOUS | Gemma4-12B | Benchmark F1 | 0.9833 | 20 | 0 | 616 | 618 | 0.9968 |
| ambiguity tag = R2_AMBIGUOUS | Granite41-8B | Question-valid precision | 0.8450 | 20 | 0 | 272 | 357 | 0.7619 |
| ambiguity tag = R2_AMBIGUOUS | Granite41-8B | OFF_QUESTION rate | 0.1550 | 20 | 0 | 85 | 357 | 0.2381 |
| ambiguity tag = R2_AMBIGUOUS | Granite41-8B | UNRESOLVED rate | 0.0000 | 20 | 0 | 0 | 357 | 0.0000 |
| ambiguity tag = R2_AMBIGUOUS | Granite41-8B | UNGROUNDED rate | 0.0000 | 20 | 0 | 0 | 357 | 0.0000 |
| ambiguity tag = R2_AMBIGUOUS | Granite41-8B | Benchmark P | 0.8450 | 20 | 0 | 272 | 357 | 0.7619 |
| ambiguity tag = R2_AMBIGUOUS | Granite41-8B | Benchmark R | 0.9000 | 20 | 0 | 272 | 308 | 0.8831 |
| ambiguity tag = R2_AMBIGUOUS | Granite41-8B | Benchmark F1 | 0.8619 | 20 | 0 | 544 | 665 | 0.8180 |
| ambiguity tag = R2_AMBIGUOUS | Ministral3-14B | Question-valid precision | 0.8341 | 15 | 5 | 199 | 281 | 0.7082 |
| ambiguity tag = R2_AMBIGUOUS | Ministral3-14B | OFF_QUESTION rate | 0.1659 | 15 | 5 | 82 | 281 | 0.2918 |
| ambiguity tag = R2_AMBIGUOUS | Ministral3-14B | UNRESOLVED rate | 0.0000 | 15 | 5 | 0 | 281 | 0.0000 |
| ambiguity tag = R2_AMBIGUOUS | Ministral3-14B | UNGROUNDED rate | 0.0000 | 15 | 5 | 0 | 281 | 0.0000 |
| ambiguity tag = R2_AMBIGUOUS | Ministral3-14B | Benchmark P | 0.8341 | 15 | 5 | 199 | 281 | 0.7082 |
| ambiguity tag = R2_AMBIGUOUS | Ministral3-14B | Benchmark R | 0.9333 | 15 | 5 | 199 | 234 | 0.8504 |
| ambiguity tag = R2_AMBIGUOUS | Ministral3-14B | Benchmark F1 | 0.8510 | 15 | 5 | 398 | 515 | 0.7728 |
| ambiguity tag = R2_AMBIGUOUS | Cogito-14B | Question-valid precision | 0.8992 | 19 | 1 | 272 | 303 | 0.8977 |
| ambiguity tag = R2_AMBIGUOUS | Cogito-14B | OFF_QUESTION rate | 0.1008 | 19 | 1 | 31 | 303 | 0.1023 |
| ambiguity tag = R2_AMBIGUOUS | Cogito-14B | UNRESOLVED rate | 0.0000 | 19 | 1 | 0 | 303 | 0.0000 |
| ambiguity tag = R2_AMBIGUOUS | Cogito-14B | UNGROUNDED rate | 0.0000 | 19 | 1 | 0 | 303 | 0.0000 |
| ambiguity tag = R2_AMBIGUOUS | Cogito-14B | Benchmark P | 0.8992 | 19 | 1 | 272 | 303 | 0.8977 |
| ambiguity tag = R2_AMBIGUOUS | Cogito-14B | Benchmark R | 0.9479 | 20 | 0 | 272 | 308 | 0.8831 |
| ambiguity tag = R2_AMBIGUOUS | Cogito-14B | Benchmark F1 | 0.8820 | 20 | 0 | 544 | 611 | 0.8903 |
| ambiguity tag = BOTH_AMBIGUOUS | Gemma4-12B | Question-valid precision | 0.9707 | 61 | 0 | 635 | 664 | 0.9563 |
| ambiguity tag = BOTH_AMBIGUOUS | Gemma4-12B | OFF_QUESTION rate | 0.0293 | 61 | 0 | 29 | 664 | 0.0437 |
| ambiguity tag = BOTH_AMBIGUOUS | Gemma4-12B | UNRESOLVED rate | 0.0000 | 61 | 0 | 0 | 664 | 0.0000 |
| ambiguity tag = BOTH_AMBIGUOUS | Gemma4-12B | UNGROUNDED rate | 0.0000 | 61 | 0 | 0 | 664 | 0.0000 |
| ambiguity tag = BOTH_AMBIGUOUS | Gemma4-12B | Benchmark P | 0.6164 | 61 | 0 | 327 | 664 | 0.4925 |
| ambiguity tag = BOTH_AMBIGUOUS | Gemma4-12B | Benchmark R | 1.0000 | 61 | 0 | 327 | 327 | 1.0000 |
| ambiguity tag = BOTH_AMBIGUOUS | Gemma4-12B | Benchmark F1 | 0.6999 | 61 | 0 | 654 | 991 | 0.6599 |
| ambiguity tag = BOTH_AMBIGUOUS | Granite41-8B | Question-valid precision | 0.7382 | 59 | 2 | 484 | 1084 | 0.4465 |
| ambiguity tag = BOTH_AMBIGUOUS | Granite41-8B | OFF_QUESTION rate | 0.2618 | 59 | 2 | 600 | 1084 | 0.5535 |
| ambiguity tag = BOTH_AMBIGUOUS | Granite41-8B | UNRESOLVED rate | 0.0000 | 59 | 2 | 0 | 1084 | 0.0000 |
| ambiguity tag = BOTH_AMBIGUOUS | Granite41-8B | UNGROUNDED rate | 0.0000 | 59 | 2 | 0 | 1084 | 0.0000 |
| ambiguity tag = BOTH_AMBIGUOUS | Granite41-8B | Benchmark P | 0.5192 | 59 | 2 | 264 | 1084 | 0.2435 |
| ambiguity tag = BOTH_AMBIGUOUS | Granite41-8B | Benchmark R | 0.8092 | 61 | 0 | 264 | 327 | 0.8073 |
| ambiguity tag = BOTH_AMBIGUOUS | Granite41-8B | Benchmark F1 | 0.5573 | 61 | 0 | 528 | 1411 | 0.3742 |
| ambiguity tag = BOTH_AMBIGUOUS | Ministral3-14B | Question-valid precision | 0.8559 | 55 | 6 | 519 | 620 | 0.8371 |
| ambiguity tag = BOTH_AMBIGUOUS | Ministral3-14B | OFF_QUESTION rate | 0.1441 | 55 | 6 | 101 | 620 | 0.1629 |
| ambiguity tag = BOTH_AMBIGUOUS | Ministral3-14B | UNRESOLVED rate | 0.0000 | 55 | 6 | 0 | 620 | 0.0000 |
| ambiguity tag = BOTH_AMBIGUOUS | Ministral3-14B | UNGROUNDED rate | 0.0000 | 55 | 6 | 0 | 620 | 0.0000 |
| ambiguity tag = BOTH_AMBIGUOUS | Ministral3-14B | Benchmark P | 0.5402 | 55 | 6 | 268 | 620 | 0.4323 |
| ambiguity tag = BOTH_AMBIGUOUS | Ministral3-14B | Benchmark R | 0.9107 | 56 | 5 | 268 | 276 | 0.9710 |
| ambiguity tag = BOTH_AMBIGUOUS | Ministral3-14B | Benchmark F1 | 0.6089 | 56 | 5 | 536 | 896 | 0.5982 |
| ambiguity tag = BOTH_AMBIGUOUS | Cogito-14B | Question-valid precision | 0.8020 | 57 | 4 | 533 | 832 | 0.6406 |
| ambiguity tag = BOTH_AMBIGUOUS | Cogito-14B | OFF_QUESTION rate | 0.1980 | 57 | 4 | 299 | 832 | 0.3594 |
| ambiguity tag = BOTH_AMBIGUOUS | Cogito-14B | UNRESOLVED rate | 0.0000 | 57 | 4 | 0 | 832 | 0.0000 |
| ambiguity tag = BOTH_AMBIGUOUS | Cogito-14B | UNGROUNDED rate | 0.0000 | 57 | 4 | 0 | 832 | 0.0000 |
| ambiguity tag = BOTH_AMBIGUOUS | Cogito-14B | Benchmark P | 0.5176 | 57 | 4 | 277 | 832 | 0.3329 |
| ambiguity tag = BOTH_AMBIGUOUS | Cogito-14B | Benchmark R | 0.9038 | 60 | 1 | 277 | 324 | 0.8549 |
| ambiguity tag = BOTH_AMBIGUOUS | Cogito-14B | Benchmark F1 | 0.5711 | 60 | 1 | 554 | 1156 | 0.4792 |

Mean over episodes where the value is defined; NA = undefined (division by zero), excluded and counted (§15). Benchmark F1 pooled = 2·Σcorrect / (Σresolved + Σ|A*_q|).
