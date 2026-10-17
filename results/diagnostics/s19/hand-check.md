# S19 real-episode inspection

Source: unchanged S14 BH2_00461, agent S14-qwen3-4b, SUCCESS, CONSISTENT, BRIDGE.
Raw call indices are zero-based. The saved replay checks all returned IDs against S18.

| Call index | Tool/source | Returned evidence |
|---|---|---|
| 0 | inspect_entity(14097) | Source identity; no page |
| 1 | get_neighbors(14097, drug_protein, gene/protein, page 1) | TTR 111 only; total_count=1, page_size=50, has_more=false |
| 2 | inspect_entity(111) | TTR identity; no page |
| 3 | get_neighbors(111, disease_protein, disease, page 1) | All 21 submitted disease IDs; total_count=21, page_size=50, has_more=false |

**Bridge rank:** TTR 111 is the only explored B_q member. Its first accepted-source
return is call 1, page 1, position 1: `(1 - 1) * 50 + 1 = 1`.
Call 3 is a successful neighbor call on TTR, so it is explored. All 21 of its
S7 targets were submitted: bridge-conditional recall = 21/21 = 1.

**Early stop:** false. Neither returned page 1 had has_more=true; there is no
qualifying unfinished list, even though page 2 was never requested.

**Effort:** 2 neighbor-page requests, 4 charged calls, budget 30, not exhausted;
0 TEXT_TOOL_CALL events. Inspect calls count toward calls, not pages.

**Quality:** 21 resolved answers, all GOLD/SUPPORTED; P=R=F1=1, question-valid
precision=1; OFF_QUESTION, UNRESOLVED and UNGROUNDED rates=0. H1_CLEAN, found R1=true.

| Answer ID | FIRST_SEEN_PAGE | First list size | Primary-path max list size | Degree | Degree percentile |
|---|---|---|---|---|---|
| 27413 | 1 | 21 | 21 | 50 | 90.87236533957845 |
| 27710 | 1 | 21 | 21 | 68 | 94.26814988290398 |
| 27933 | 1 | 21 | 21 | 782 | 99.94730679156909 |
| 28275 | 1 | 21 | 21 | 53 | 91.63348946135831 |
| 28831 | 1 | 21 | 21 | 10 | 62.36533957845434 |
| 29041 | 1 | 21 | 21 | 52 | 91.38173302107728 |
| 29695 | 1 | 21 | 21 | 5 | 49.133489461358316 |
| 30929 | 1 | 21 | 21 | 12 | 65.46838407494145 |
| 31116 | 1 | 21 | 21 | 605 | 99.86533957845434 |
| 32117 | 1 | 21 | 21 | 40 | 87.3887587822014 |
| 33591 | 1 | 21 | 21 | 37 | 86.15339578454333 |
| 36544 | 1 | 21 | 21 | 456 | 99.75409836065575 |
| 36812 | 1 | 21 | 21 | 327 | 99.6135831381733 |
| 37703 | 1 | 21 | 21 | 499 | 99.77751756440281 |
| 37798 | 1 | 21 | 21 | 13 | 67.02576112412177 |
| 37871 | 1 | 21 | 21 | 24 | 78.13231850117096 |
| 38035 | 1 | 21 | 21 | 104 | 97.11943793911007 |
| 83760 | 1 | 21 | 21 | 488 | 99.77166276346604 |
| 83840 | 1 | 21 | 21 | 466 | 99.7599531615925 |
| 84174 | 1 | 21 | 21 | 16 | 70.63231850117097 |
| 84193 | 1 | 21 | 21 | 4 | 44.47306791569087 |

All 21 first listings are call 3. Every primary path uses calls 1 and 3,
so its largest list size is max(1,21)=21. Source, bridge and target degrees
were independently checked with the S4 unique-neighbor lookup; inclusive
same-type percentile shares were recomputed from the full frozen KG table.

Engineering inspection complete. The researcher explicitly accepted S19 and its
verification evidence on 2026-10-17; see `docs/decision_log.md`.
