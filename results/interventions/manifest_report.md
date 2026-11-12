# S33 — Treatment overlays (D7 DESCRIPTIVE; no controls)

Produced by `scripts/33_overlays.py` at commit `0647156d738e77d625c3034323c1b5c84911a53b` (tracked files clean: True). Cases: decision log 2026-11-12, section A. Surgery: hide label r at node u (reading of 2026-11-11). Treatment-only (C = 0).

Agent-side overlay file: `data/agent_inputs/intervention_overlays.jsonl`, SHA256 `e7d9a241c73ce5b2703a8844e715e1513954056b8302916f24fee538f83f1a44` (for the S34/S35 run configuration).

| query_id | mechanism | hidden label at node | hidden edges | valid bridges before → after | nodes checked | node-labels checked |
|---|---|---|---|---|---|---|
| BH2_03356 | WRONG_TURN_HOP2 | off-label use at 33618 | 21 | 33618 → 33618 | 23 | 139 |
| BH2_04650 | SHORTCUT | drug_protein at 16843 | 5 | 36026 → 36026 | 7 | 59 |
| BH2_05290 | WRONG_TURN_HOP2 | off-label use at 14052 | 2 | 14052 → 14052 | 4 | 23 |
| BH2_05997 | WRONG_TURN_HOP2 | off-label use at 33228 | 2 | 31864, 33228 → 31864, 33228 | 5 | 25 |
| BH2_06016 | WRONG_TURN_HOP2 | off-label use at 30800 | 8 | 30800 → 30800 | 10 | 53 |

Every case: a §21 valid route remains, and only the intended edges are hidden (checked through the agent tools with and without the overlay).
