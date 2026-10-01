# S1 Audit — Response and Fixes (protocol and decision rules v1.0 → v1.1)

Each audit item, what kind of problem it was, and where v1.1 fixes it. "§" = protocol, "D" = decision rules.

## Real errors in v1.0

| Audit item | Problem | Fix in v1.1 |
|---|---|---|
| 3a / 4a / contradiction 3 | Mapping score ignored hop 1, so R1 could not be chosen or validated | §5.1: separate hop-1 score (edge s–bridge exists with the label) and hop-2 score; D1 requires both ≥ 90% |
| 3b / contradiction 2 | A query could be CONSISTENT with its gold bridge outside B_q, making GOLD answers fall outside T_q | §7.1: CONSISTENT requires every gold bridge ∈ B_q; new reason GOLD_BRIDGE_NOT_VALID; §13 notes A*_q ⊆ T_q for primary queries |
| 3e, 3f / contradiction 4 | Sampling floors impossible for screening/smoke; allocation steps unspecified | §8: per-set quotas and floors (0 for screening/smoke, 1 for pilot/reserve); full algorithm with shortfall and cap handling |
| 4c / contradiction 5 | Screening needed runtime values that are chosen from screening | §9.1: a frozen screening configuration; final values at S21 |
| 4f / contradiction 8 | D7 needed §21, frozen only after D7 | §21 frozen at S29 (after D6, before S30); runbook S29 updated |
| 4f / contradiction 9 | E "divided by 400" for 500 queries | D6/D7: E = technical failures / episodes run |
| 5a / contradiction 6 | Type_B forbidden although the question text must state it | §9.3: question text (with node types) explicitly allowed; forbidden list corrected; check that no question contains its bridge's name |
| 3r / contradiction 15 | D2 outcomes overlapped | D2: ordered RED → GREEN → YELLOW |
| 3s | D8 scaled whenever compute fit | D8: (a or b) and c |
| 3q | N2 draw could be impossible | §17 N2: pool and observed set both restricted to page-1 entities |
| contradiction 11 / 4h | 4 agents frozen but D3 allowed 3 | D3: no 3-agent fallback; changing n needs a protocol revision |

## Underspecified items (now defined)

| Audit item | Fix in v1.1 |
|---|---|
| Query identity, query_id, duplicate question texts | §0.3: query = unique (query entity, relation type); rows merged; query_id = lowest row_id; row_id defined |
| Type_S, type map, starting-entity name | §0.3, §3.3 type map `[TBD@S4]`, §4 normalization filters, §9.3 PrimeKG node name |
| Label vs display label | §0.3: all rules use `relation`; display label informational only |
| Candidate sets, "smallest", validation sample, denominators | §5.1 |
| T_q size bins | §8 step 4 |
| Successful call, error message format | §10 |
| Tie-break for primary path, long paths, x = s, UNRESOLVED | §14.1–14.2 (BFS primary path; NOT_APPLICABLE; WRONG_HOP_COUNT for length 0 and ≥ 3) |
| Hop-1 status details | §14.3 (successful calls on s, by label only) |
| Bridge rank, FIRST_SEEN_PAGE, early stop, division by zero | §15 (NA rule; INSPECT / NEVER) |
| Degree and percentile | §15 |
| Wrong-turn events, PCF_NODE endpoint | §16.3 |
| Grounded variant per agent | §16.1 |
| Pairwise agreement with no data | §16.4 (NA, denominator reported) |
| Hop-1-clean null | §17 N1-H1 |
| Random number generator | §17 (NumPy PCG64, per-query seed) |
| Tool configuration, prompt version, KG hash | §19 (KG fingerprint = SHA256 of metadata file) |
| Episode statuses; "crash" | §9.5 (SUCCESS, PARSE_FAIL, TIMEOUT, ERROR) |
| D3 terms (attempted, well-formed, family, competence) | D3 definitions |
| D4 tests and audit selection | §19.1 |
| Pilot manifest | §8 table; D5 |
| "Passes" | D6: GREEN or YELLOW; §1 and CLAUDE.md updated |
| "Relation pair" naming | Renamed "relation type" everywhere |
| Tag conflict on saturation threshold | §7.2: `[TBD@S9]` with a recommended value |
| JSON parsing details; tool calls after budget | §9.4 |
| Numeric vs string IDs | §12 |
| D7 terms ("valid route", branch degree, mechanism) | §21 |
| Phase 2 overlays vs "never reads evaluation files" | §10: the environment may read an overlay file of edge identities only |

## Expected items (not errors)

The `[TBD@Sx]` list is intentional: each item is decided from data at its stage.

## Also added (agreed in planning after v1.0)

- Mechanical ambiguity rule (§5.2), replacing manual judgments.
- Mapping confirmation on non-validation queries (D2 step 1).
- Invariant: no answer is both OFF_QUESTION and SUPPORTED (§14.1, D4, runbook S18).
- Bridges with no targets are dead ends, not valid bridges (§6).
