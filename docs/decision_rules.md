# CoFail-KG — Decision Rules

**Version:** 1.2 · Frozen before the data each gate judges exists. "§" = `docs/frozen_pilot_protocol.md`.

These are **feasibility criteria**, not significance tests.

## Rules for the rules

1. A threshold may change only **before** the gate's input data exists, with a dated
   `docs/decision_log.md` entry.
2. After the data exists, thresholds are fixed; disagreement and extra analyses are **exploratory**.
3. Claude Code computes the quantities and applies the rules mechanically. It never changes a threshold.
4. Every outcome is logged with the numbers that produced it.
5. Within a gate, outcomes are checked **in the order listed**; the first match wins.

---

## D1 — Relation-mapping gate (end of S6)

**Input.** Per relation type: the hop-1 and hop-2 scores of the selected mapping (§5.1), the
number of validation rows, and unresolved-row counts.

| Outcome | Rule | Action |
|---|---|---|
| Type FAIL | Fewer than 10 validation rows, **or** a hop has no candidate label, **or** hop-1 score < 90%, **or** hop-2 score < 90% | Investigate up to 2 working days (field roles, edge storage, release). If still failing, exclude the type (decision-log entry). |
| Type PASS | Otherwise | Type may enter the primary population |
| **Global STOP** | Fewer than 6 of 12 types PASS, **or** PASS types cover < 70% of 2-hop rows | Do not continue. Re-check release (S4), field roles (S5), edge convention. |
| **Global PROCEED** | Otherwise | Continue to S7 |

---

## D2 — Mapping confirmation and dataset feasibility (S9)

**Step 1 — Mapping confirmation, per PASS type.** Among the type's queries that contain no
validation-sample row, compute the CONSISTENT share.
- If the type has **no** such queries, it is marked `UNCONFIRMABLE` and is kept (its D1 result stands).
- ≥ 80% → confirmed.
- < 80% → before S14: either revise the type's mapping (decision-log entry), then re-apply D1 to
  that type and repeat step 1 after rerunning S7–S8; or exclude the type (decision-log entry).
  From S14 on, mappings never change; an unconfirmed type is excluded.

**Step 2 — Saturation threshold.** Inspect the saturation-share distribution and fix θ (§7.2)
**before** step 3.

**Step 3 — Feasibility.** `N_P` = primary-population size (§7.2); `K` = number of relation types
with ≥ 20 primary-population queries.

| Order | Outcome | Rule | Action |
|---|---|---|---|
| 1 | **RED** | `N_P < 150` | Stop before building agents; revisit release, mapping or θ (decision-log entry). |
| 2 | **GREEN** | `N_P ≥ 650` **and** `K ≥ 5` | Continue as planned |
| 3 | **YELLOW** | Otherwise | Continue; the expansion reserve holds whatever remains (§8 step 1) |

Why 650: 20 + 4 + 100 + 400 = 524 queries, plus margin.

---

## D3 — Model selection (S20–S21)

**Input.** Each candidate on the 20 screening queries, with the screening configuration (§9.1).

**Definitions.** *Attempted calls:* native tool calls plus TEXT_TOOL_CALL occurrences (§9.5).
*Well-formed call:* a native call naming one of the two tools, whose arguments parse and match the
schema types. *Family:* developer lineage on the model card (e.g. Qwen, Llama, Mistral, Granite,
Phi). *Competence:* share of screening queries with at least one answer that is question-valid and
SUPPORTED.

A model **passes** if all hold:

| Criterion | Threshold |
|---|---|
| Well-formed calls / attempted calls | ≥ 90% |
| Episodes with status SUCCESS | ≥ 90% |
| Competence | ≥ 40% |
| Median episode wall time | ≤ 5 minutes |
| ERROR episodes with cause OUT_OF_MEMORY | 0 |

**Selection.** Choose four passing models maximizing the number of distinct families (at least 3);
ties by higher competence, then lower median wall time.

| Order | Situation | Action |
|---|---|---|
| 1 | Four can be chosen covering ≥ 3 families | Freeze them (S21) |
| 2 | Otherwise | Screen more candidates, preferring new families (at most 2 more rounds) |
| 3 | Still not possible | Consult supervisor. n = 4 is frozen (§9.2); any change needs a protocol revision. |

---

## D4 — Panel smoke test (S25)

**Input.** The smoke set × 4 agents; the §19.1 verification tests; your manual audit of the episodes
chosen by §19.1 audit selection.

**PASS** requires all:
- every episode has a §9.5 status;
- at least 7/8 of episodes are SUCCESS (14 of 16 with the full smoke set);
- the leakage, reconstruction and kill-and-resume tests pass;
- the manual audit finds zero Label A or Label B errors;
- no answer is both OFF_QUESTION and SUPPORTED.

**FAIL** → fix the implementation (no definition changes), rerun the smoke episodes as new attempts,
re-audit.

---

## D5 — Pre-run freeze check (S26)

The pilot may start only if all hold:
- no `[TBD@Sx]` with x ≤ 26 remains unfilled, and every `[DEFAULT]` with stage ≤ 26 is confirmed;
- all tests pass on a clean working tree; the commit hash is recorded;
- the KG fingerprint, BioHopR revision, relation mapping, tool schema, prompt template, pilot
  manifest and pilot agent-input sheet all match `configs/frozen_hashes.yaml`;
- the installed model digests match the `models` entry of `configs/frozen_hashes.yaml`.

---

## D6 — Pilot decision (S29)

### Quantities (pilot queries × 4 agents; latest attempts, §19)

| Symbol | Definition |
|---|---|
| `E` | Technical failures (§9.5) / episodes |
| `H` | Share of queries where ≥ 3 of 4 agents **found R1** (§14.3) |
| `N` | Number of queries with CF3^{Q,H1} = 1 (§16.1) |
| `O > null` | `O_H1` exceeds the 95th percentile of null N1-H1 (§17) |
| `P` | Number of distinct relation types among the `N` queries |

### Outcomes

| Order | Outcome | Rule | Action |
|---|---|---|---|
| 1 | **HOLD** | `E > 15%` | Not a scientific outcome. Fix the implementation; rerun failed episodes as new attempts (§19); re-apply D6. |
| 2 | **RED** | `H < 20%` **or** `N < 3` **or** not `O > null` | No intervention work. Descriptive write-up; exploratory follow-ups optional. |
| 3 | **GREEN** | `H ≥ 40%` **and** `N ≥ 10` **and** `O > null` **and** `P ≥ 3` | Freeze §21 (S29); run the expansion reserve (S30) |
| 4 | **YELLOW** | Otherwise | Freeze §21 (S29); run the expansion reserve (S30); Phase 2 exploratory unless D7 is CONFIRMATORY |

The pilot **passes** if D6 is GREEN or YELLOW.

### Interpretation flags (reported, not gates)
- **Ordering flag:** `O_N1` exceeds N1 but `O_N2` does not exceed N2.
- **Ambiguity flag:** more than 70% of the `N` queries belong to relation types tagged
  `R1_AMBIGUOUS`, `R2_AMBIGUOUS` or `BOTH_AMBIGUOUS`.

---

## D7 — Expansion and intervention feasibility (after S30)

Same quantities as D6 over pilot + expansion queries, plus `C` = number of candidate **queries**
meeting the §21 candidate rule (frozen at S29) with a matched control.

| Order | Outcome | Rule | Action |
|---|---|---|---|
| 1 | HOLD | `E > 15%` | As in D6 |
| 2 | **DESCRIPTIVE** | `N < 15` **or** not `O > null` **or** `C < 8` | No confirmatory surgery; up to 5 illustrative exploratory cases |
| 3 | **CONFIRMATORY** | `N ≥ 30` **and** `O > null` **and** `P ≥ 4` **and** `C ≥ 20` | Run the intervention study on all eligible candidates |
| 4 | **EXPLORATORY** | Otherwise | Run on available candidates; label results exploratory |

---

## D8 — Final scale decision (S37)

Scale beyond the expansion only if D7 was CONFIRMATORY or EXPLORATORY **and** (a) fewer than 10
candidate queries exist for at least one §21 mechanism, **or** (b) candidates cover fewer than 5
relation types — **and** (c) a compute estimate, written in the decision log first, fits the
remaining schedule. New sets are drawn with the §8 algorithm from queries not yet drawn.
