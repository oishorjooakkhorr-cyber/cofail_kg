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

---

# Re-audit of v1.1 — every item and its resolution in v1.2

"§" = protocol v1.2 · "D" = decision rules v1.2 · "S" = runbook stage. "Same as" = one problem reported in several parts.

## Part 1 (fixes checked from v1.1)

| Item | Resolution in v1.2 |
|---|---|
| 1.1 | §0.1: a `[TBD@Sx]` value is filled at Sx and may be computed by code at Sx; §5.1: procedure FROZEN, result TBD@S6; CLAUDE.md updated |
| 1.2 | §7.1 condition 4: every gold answer name must resolve |
| 1.3 | §8: floor stated per multiplicity group; remainder ties by relation-type name; total shortfall rule |
| 1.4 | §0.4: queries grouped by resolved PrimeKG node + relation type; unresolved entity = own query; row_id defined; §7.1 condition 2 + `QUESTION_TEXT_MISMATCH` |
| 1.5 | §11: edge identity (u, r, v) and creation index; §14.2: total order (length, largest creation index, numeric-ID/label sequence) |
| 1.6 | §10: six error templates; empty list = successful page 1 with total_count 0 |
| 1.7 | §9.5: status precedence; ERROR `cause` field |
| 1.8 | §9.5: TEXT_TOOL_CALL detection rule |
| 1.9 | §19.1: audit selection takes all eligible episodes if fewer than 2; D4 uses 7/8 |
| 1.10 | §3.4: `configs/frozen_hashes.yaml`; metadata file machine-written only; release details in a separate file |
| 1.11 | §9.4: integer or string IDs; fences with language tags; extra keys; empty and contradictory lists |
| 1.12 | §17: each null has its own observed total (O_N1, O_H1, O_N2) |
| 1.13 | §3.2: one edge convention shared by §6, §10 and §11; §14.1 invariant explanation |
| 1.14 | D2 step 1: UNCONFIRMABLE; revision re-applies D1; exclusion allowed before S14 |
| 1.15 | §12: reference policy (type-filtered) versus agent policy |
| 1.16 | §15: degree percentile defined |
| 1.17 | S10: `relation_type` field |
| 1.18 | S11: display labels in tool output |
| 1.19 | §7.1: `LEAKY_QUESTION`; §7.2: excluded from the primary population |

## Part 2 (full audit of v1.1)

| Item | Resolution in v1.2 |
|---|---|
| 2.1 | Same as 1.1 |
| 2.2 | §10: `direction` argument tagged [TBD@S4] |
| 2.3 | §9.3: P1 [TBD@S14]; §10: T1 [TBD@S11] |
| 2.4 | D5: unconfirmed [DEFAULT] items also block |
| 2.5 | §3.2: release chosen at S4, revisited only through D1 STOP |
| 2.6 | §7.1: reason-code table with definitions; NA rule when the entity does not resolve |
| 2.7 | §15: list size (fan-out) metric; §1 wording; §21 note |
| 2.8 | §15: denominator for each rate |
| 2.9 | §17: observed totals defined |
| 2.10 | §14.3: the bridge must differ from the answer |
| 2.11 | §21: mechanism names; candidates counted in queries; D7/D8 aligned |
| 2.12–2.16 | Same as 1.2, 1.4, 1.5, 1.3, 1.11 |
| 2.17 | §17 table |
| 2.18 | §17: random-number scheme (per query and per null; agent order; sorted pools) |
| 2.19, 2.20 | Same as 1.6, 1.15 |
| 2.21 | §5.1 and D1: fewer than 10 validation rows or no candidate label → FAIL |
| 2.22 | §14.2: WRONG_HOP_COUNT for any length other than 2, except SHORTCUT |
| 2.23 | §19: attempts, new run ID, latest attempt used, E on latest attempts; D6 HOLD |
| 2.24 | §19.1: case-insensitive whole-word matching; short names reviewed by hand |
| 2.25 | D6: `O > null` = O_H1 versus N1-H1 |
| 2.26 | D6 ordering flag: O_N1 vs N1 and O_N2 vs N2 |
| 2.27 | Same as 1.7, 1.8 |
| 2.28 | D3: ordered selection table; fewer than 3 families → screen more |
| 2.29 | Same as 1.14 |
| 2.30 | §19.1 audit fallback; leakage test on screening and smoke queries; S25 |
| 2.31 | Same as 2.23 |
| 2.32 | §8 agent-input sheets; §9.3; §19.1(b); CLAUDE.md; S10, S14 |
| 2.33 | §7.1 LEAKY_QUESTION (excluded); §19.1 checks the system prompt and starting-entity line, not the question text |
| 2.34 | §19.1(a): other B_q/T_q members and evaluator label names added |
| 2.35 | Same as 1.2 |
| 2.36 | §9.3: P1 is a template; its hash is the version; filled values recorded with the tool configuration |
| 2.37, 2.38 | Same as 1.13, 1.11 |
| 2.39 | §21: mechanisms SHORTCUT, WRONG_RELATION_HOP1/2, OFF_PATH_NODE; fan-out descriptive only |
| 2.40 | §8: reserve "up to 400" with shortfall; D2 YELLOW and D6 wording aligned |

## Part 3 (runbook)

| Item | Resolution in v1.2 |
|---|---|
| 3.1 | S1: no version number in the decision or commit text |
| 3.2 | S2: row_id as in §0.4 |
| 3.3 | S4 decision matches §3.2/§10 |
| 3.4 | §3.4 and S4: separate release file |
| 3.5 | §3.1: field-role rule moved into the protocol; S5 applies it |
| 3.6 | S6: ties reported as TIE |
| 3.7 | S7: grouping by resolved node; agents no longer read S7 outputs |
| 3.8 | No change: S9's θ advice is guidance for a researcher decision; the binding rule (decide before D2 step 3) is in D2 |
| 3.9 | S9 aligned with D2 step 1 |
| 3.10 | S10: field names; step reference |
| 3.11 | S11: display labels; configuration wording |
| 3.12 | S12: creation index; §14.2 ordering |
| 3.13 | S13: retries marked as engineering; usability decided by D3 |
| 3.14 | Agent-input sheets (S10, S14, S15) |
| 3.15 | S14: P1 as template; TEXT_TOOL_CALL; full screening configuration |
| 3.16 | S15 rewritten from §19.1 |
| 3.17 | S17 notation |
| 3.18 | S18 fixtures for x = s |
| 3.19 | S20 reports the D3 quantities exactly |
| 3.20 | §9.1: final-value rules moved into the protocol, with the 16384 rerun rule; S21 |
| 3.21 | S21 and stage map |
| 3.22 | S22 uses all 20 screening queries; the 90% guard is engineering |
| 3.23 | S24 test wording; N1-H1 named |
| 3.24 | §19: completed = any status; S25 |
| 3.25 | S26 uses `frozen_hashes.yaml` |
| 3.26 | §19 code-change rule; S27 |
| 3.27 | S28: three null comparisons; explored-bridge ranks |
| 3.28 | S30: new run ID `expansion_v1`; hash checks |
| 3.29 | S31 aligned with §21 (frozen at S29); control tie-break logged before runs |
| 3.30 | S33: valid route |
| 3.31 | D8 and S37: new sets drawn with the §8 algorithm |
