# S35 — Intervention run: tool-output check `intervention_v1` (DESCRIPTIVE)

DESCRIPTIVE (D7 DESCRIPTIVE; decision log 2026-11-12 "Plan after D7", section A). Treatment-only smoke test; not used in any gate.

Produced by `scripts/47_s34_smoke_report.py` at commit `8f3b8669e528be4ec8b7d7a39a35f89cb4e1ac8b` (tracked files clean: True); inference commit(s): `c4b854ac946ed8283910120b6670a33cbc6cc89f`.

**Differences from the original run not explained by the overlay: 0.** Every recorded tool output equals the replay with the overlay (checked call by call).

## Per query (S33 checks)

| Query | Hidden edges | Only intended edges hidden | Valid route after | Valid bridges after |
|---|---|---|---|---|
| BH2_03356 | 21 | True | True | 33618 |
| BH2_04650 | 5 | True | True | 36026 |
| BH2_05290 | 2 | True | True | 14052 |
| BH2_05997 | 2 | True | True | 31864, 33228 |
| BH2_06016 | 8 | True | True | 30800 |

## Per episode

| Query | Agent | Status (original → smoke) | Calls | Same calls as original: identical / different | Calls changed by overlay | Reached u via R1 | Asked u for hidden label → result |
|---|---|---|---|---|---|---|---|
| BH2_03356 | Gemma4-12B | SUCCESS → SUCCESS | 4 | 3 / 1 | 1 | True | not asked |
| BH2_04650 | Gemma4-12B | SUCCESS → SUCCESS | 4 | 3 / 1 | 1 | False | not asked |
| BH2_05290 | Gemma4-12B | SUCCESS → SUCCESS | 4 | 3 / 1 | 1 | True | not asked |
| BH2_05997 | Gemma4-12B | SUCCESS → SUCCESS | 7 | 6 / 1 | 1 | True | not asked |
| BH2_06016 | Gemma4-12B | SUCCESS → SUCCESS | 4 | 3 / 1 | 1 | True | not asked |
| BH2_03356 | Granite41-8B | SUCCESS → SUCCESS | 5 | 3 / 1 | 1 | True | not asked |
| BH2_04650 | Granite41-8B | SUCCESS → SUCCESS | 7 | 0 / 1 | 1 | False | not asked |
| BH2_05290 | Granite41-8B | SUCCESS → SUCCESS | 7 | 6 / 1 | 1 | True | not asked |
| BH2_05997 | Granite41-8B | SUCCESS → SUCCESS | 9 | 7 / 1 | 1 | True | not asked |
| BH2_06016 | Granite41-8B | SUCCESS → SUCCESS | 4 | 3 / 1 | 1 | True | not asked |
| BH2_03356 | Ministral3-14B | SUCCESS → PARSE_FAIL | 0 | 0 / 0 | 0 | False | not asked |
| BH2_04650 | Ministral3-14B | SUCCESS → SUCCESS | 4 | 0 / 1 | 1 | False | not asked |
| BH2_05290 | Ministral3-14B | SUCCESS → PARSE_FAIL | 0 | 0 / 0 | 0 | False | not asked |
| BH2_05997 | Ministral3-14B | SUCCESS → SUCCESS | 7 | 6 / 1 | 1 | True | not asked |
| BH2_06016 | Ministral3-14B | SUCCESS → SUCCESS | 4 | 3 / 1 | 1 | True | not asked |
| BH2_03356 | Cogito-14B | SUCCESS → SUCCESS | 8 | 4 / 1 | 1 | True | not asked |
| BH2_04650 | Cogito-14B | SUCCESS → SUCCESS | 17 | 1 / 1 | 1 | False | not asked |
| BH2_05290 | Cogito-14B | SUCCESS → SUCCESS | 30 | 4 / 1 | 1 | True | not asked |
| BH2_05997 | Cogito-14B | SUCCESS → SUCCESS | 15 | 9 / 1 | 1 | True | not asked |
| BH2_06016 | Cogito-14B | SUCCESS → SUCCESS | 8 | 5 / 1 | 1 | True | not asked |

## Every tool output the overlay changed

- Gemma4-12B, call 2: inspect_entity(33618): label `off-label use` removed (21 neighbours)
- Gemma4-12B, call 0: inspect_entity(16843): label `drug_protein` removed (5 neighbours)
- Gemma4-12B, call 2: inspect_entity(14052): label `off-label use` removed (2 neighbours)
- Gemma4-12B, call 5: inspect_entity(33228): label `off-label use` removed (2 neighbours)
- Gemma4-12B, call 2: inspect_entity(30800): label `off-label use` removed (8 neighbours)
- Granite41-8B, call 2: inspect_entity(33618): label `off-label use` removed (21 neighbours)
- Granite41-8B, call 0: inspect_entity(16843): label `drug_protein` removed (5 neighbours)
- Granite41-8B, call 3: inspect_entity(14052): label `off-label use` removed (2 neighbours)
- Granite41-8B, call 6: inspect_entity(33228): label `off-label use` removed (2 neighbours)
- Granite41-8B, call 2: inspect_entity(30800): label `off-label use` removed (8 neighbours)
- Ministral3-14B, call 0: inspect_entity(16843): label `drug_protein` removed (5 neighbours)
- Ministral3-14B, call 4: inspect_entity(33228): label `off-label use` removed (2 neighbours)
- Ministral3-14B, call 2: inspect_entity(30800): label `off-label use` removed (8 neighbours)
- Cogito-14B, call 2: inspect_entity(33618): label `off-label use` removed (21 neighbours)
- Cogito-14B, call 0: inspect_entity(16843): label `drug_protein` removed (5 neighbours)
- Cogito-14B, call 2: inspect_entity(14052): label `off-label use` removed (2 neighbours)
- Cogito-14B, call 3: inspect_entity(33228): label `off-label use` removed (2 neighbours)
- Cogito-14B, call 2: inspect_entity(30800): label `off-label use` removed (8 neighbours)
