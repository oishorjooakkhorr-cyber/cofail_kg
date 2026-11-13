# S34 — Intervention smoke test `intervention_smoke` (DESCRIPTIVE)

DESCRIPTIVE (D7 DESCRIPTIVE; decision log 2026-11-12 "Plan after D7", section A). Treatment-only smoke test; not used in any gate.

Produced by `scripts/47_s34_smoke_report.py` at commit `7a8e082e7b2c95892bd5b2312ed5f4f111e53b56` (tracked files clean: True); inference commit(s): `7a8e082e7b2c95892bd5b2312ed5f4f111e53b56`.

**Differences from the original run not explained by the overlay: 0.** Every recorded tool output equals the replay with the overlay (checked call by call).

## Per query (S33 checks)

| Query | Hidden edges | Only intended edges hidden | Valid route after | Valid bridges after |
|---|---|---|---|---|
| BH2_05290 | 2 | True | True | 14052 |

## Per episode

| Query | Agent | Status (original → smoke) | Calls | Same calls as original: identical / different | Calls changed by overlay | Reached u via R1 | Asked u for hidden label → result |
|---|---|---|---|---|---|---|---|
| BH2_05290 | Gemma4-12B | SUCCESS → SUCCESS | 4 | 3 / 1 | 1 | True | not asked |
| BH2_05290 | Granite41-8B | SUCCESS → SUCCESS | 6 | 4 / 1 | 1 | True | not asked |
| BH2_05290 | Ministral3-14B | SUCCESS → SUCCESS | 5 | 4 / 1 | 1 | True | not asked |
| BH2_05290 | Cogito-14B | SUCCESS → SUCCESS | 9 | 4 / 1 | 1 | True | not asked |

## Every tool output the overlay changed

- Gemma4-12B, call 2: inspect_entity(14052): label `off-label use` removed (2 neighbours)
- Granite41-8B, call 3: inspect_entity(14052): label `off-label use` removed (2 neighbours)
- Ministral3-14B, call 3: inspect_entity(14052): label `off-label use` removed (2 neighbours)
- Cogito-14B, call 2: inspect_entity(14052): label `off-label use` removed (2 neighbours)
