# CoFail-KG — Decision Rules

**Version:** 1.1 (S1 audit fixes) · Frozen before the data each gate judges exists.

These are **feasibility criteria**, not significance tests. They decide whether there is enough of
the phenomenon to continue, and what to do next. "§" refers to `docs/frozen_pilot_protocol.md`.

## Rules for the rules

1. A threshold may change only **before** the gate's input data exists, with a dated
   `docs/decision_log.md` entry.
2. After the data exists, thresholds are fixed. Disagreement and any extra analysis are recorded as
   **exploratory**.
3. Claude Code computes the quantities and applies the rules mechanically, in the stated order. It
   never changes a threshold.
4. Every outcome is logged with the numbers that produced it.
5. Within a gate, outcomes are checked **in the order listed**; the first match wins.

---

## D1 — Relation-mapping gate (end of S6)

**Input.** Per relation type, the hop-1 and hop-2 scores of the selected mapping on the §5.1
validation sample, and the count of unresolved rows.

| Outcome | Rule | Action |
|---|---|---|
| Type PASS | Hop-1 score ≥ 90% **and** hop-2 score ≥ 90% | Type may enter the primary population |
| Type FAIL | Otherwise | Investigate up to 2 working days (field roles, edge storage, labels). If still failing, exclude the type (decision-log entry). |
| **Global STOP** | Fewer than 6 of 12 types PASS, **or** PASS types cover < 70% of 2-hop rows | Do not continue. Re-check PrimeKG release (S4), field roles (S5), edge storage. |
| **Global PROCEED** | Otherwise | Continue to S7 |

Why 90%: BioHopR was generated deterministically from PrimeKG, so the right release and mapping
should reproduce it almost exactly.

---

## D2 — Mapping confirmation and dataset feasibility (S9)

**Step 1 — Mapping confirmation (per PASS type).** Among the type's queries that contain no
validation-sample row, compute the CONSISTENT share.
- ≥ 80% → the type is confirmed.
- < 80% → revisit that type's mapping (decision-log entry) and rerun S7–S8. Allowed only before S14;
  after S14 mappings never change, and an unconfirmed type is excluded.

**Step 2 — Saturation threshold.** Inspect the saturation-share distribution (S9 part 1) and fix θ
(§7.2) **before** computing step 3.

**Step 3 — Feasibility.** `N_P` = size of the primary population (§7.2); `K` = number of relation
types with ≥ 20 primary-population queries.

| Order | Outcome | Rule | Action |
|---|---|---|---|
| 1 | **RED** | `N_P < 150` | Stop before building agents. Revisit release, mapping, θ (decision-log entry for any change). |
| 2 | **GREEN** | `N_P ≥ 650` **and** `K ≥ 5` | Continue as planned |
| 3 | **YELLOW** | Otherwise | Continue; expansion limited to available queries; note reduced coverage |

Why 650: the sets need 20 + 4 + 100 + 400 = 524 queries, plus margin for strata that run out.

---

## D3 — Model selection (S20–S21)

**Input.** Each candidate model run on the 20 screening queries with the **screening
configuration** (§9.1).

**Definitions.**
- *Attempted call:* every native tool call, plus every `TEXT_TOOL_CALL` (tool-call-like text that
  was not executed).
- *Well-formed call:* a native call naming one of the two tools, whose arguments parse and match
  the schema types.
- *Family:* the developer lineage stated on the model card (e.g. Qwen, Llama, Mistral, Granite, Phi).
- *Competence:* share of screening queries with at least one answer that is question-valid and
  `SUPPORTED`.

A model **passes** if all hold:

| Criterion | Threshold |
|---|---|
| Well-formed calls / attempted calls | ≥ 90% |
| Episodes with status SUCCESS | ≥ 90% |
| Competence | ≥ 40% |
| Median episode wall time | ≤ 5 minutes |
| `ERROR` episodes caused by out-of-memory | 0 of 20 |

**Selection.** From passing models, choose four maximizing the number of distinct families (at
least 3; prefer 4); ties by higher competence, then lower median wall time.

| Situation | Action |
|---|---|
| ≥ 4 pass | Freeze four (S21) |
| < 4 pass | Screen more candidates (at most 2 more rounds) |
| Still < 4 | Consult supervisor. The agent count is frozen at 4 (§9.2); changing it requires a protocol revision. |

---

## D4 — Panel smoke test (S25)

**Input.** 4 smoke queries × 4 agents = 16 episodes; the §19.1 verification tests; your manual
audit of the 8 episodes chosen by §19.1 audit selection.

**PASS** requires all:
- every episode ends in one of the §9.5 statuses (no unrecorded failures);
- ≥ 14 of 16 episodes have status SUCCESS;
- the leakage test passes;
- the reconstruction check passes for all 16 episodes;
- the kill-and-resume test passes;
- the manual audit finds zero Label A or Label B errors;
- no answer is both OFF_QUESTION and SUPPORTED.

**FAIL** → fix the implementation (no definition changes), rerun the same 16 episodes, re-audit.

---

## D5 — Pre-run freeze check (S26)

The pilot may start only if all hold:
- no `[TBD@Sx]` with x ≤ 26 remains in the protocol;
- all tests pass on a clean working tree; the commit hash is recorded;
- the KG fingerprint and BioHopR revision equal the recorded values;
- the four model digests equal those frozen at S21;
- the SHA256 of `data/processed/manifests/pilot.jsonl` equals the value in `manifests.sha256`.

---

## D6 — Pilot decision (S29)

### Quantities (100 pilot queries × 4 agents)

| Symbol | Definition |
|---|---|
| `E` | Technical failures (§9.5) / episodes run |
| `H` | Share of queries where ≥ 3 of 4 agents **found R1** (§14.3) |
| `N` | Number of queries with CF3^{Q,H1} = 1 (§16.1) |
| `O > null` | Observed CF3 total exceeds the N1 95th percentile (§17) |
| `P` | Number of distinct relation types among the `N` queries |

### Outcomes

| Order | Outcome | Rule | Action |
|---|---|---|---|
| 1 | **HOLD** | `E > 15%` | Not a scientific outcome. Fix the implementation, rerun only failed episodes with the identical frozen configuration, re-apply D6. |
| 2 | **RED** | `H < 20%` **or** `N < 3` **or** not `O > null` | No intervention work. Descriptive write-up; exploratory follow-ups optional. |
| 3 | **GREEN** | `H ≥ 40%` **and** `N ≥ 10` **and** `O > null` **and** `P ≥ 3` | Freeze §21 (S29); expand to 500 (S30) |
| 4 | **YELLOW** | Otherwise | Freeze §21 (S29); expand to 500 (S30); Phase 2 exploratory unless D7 is CONFIRMATORY |

The pilot **passes** if D6 is GREEN or YELLOW.

Why these numbers: `H ≥ 40%` leaves roughly 40 of 100 queries for structural analysis; `N ≥ 10`
projects to about 50 cases in 500; `N < 3` is too rare to study with this budget.

### Interpretation flags (reported, not gates)
- **Ordering flag:** observed agreement exceeds N1 but not N2.
- **Ambiguity flag:** more than 70% of the `N` queries belong to relation types tagged
  `R1_AMBIGUOUS`, `R2_AMBIGUOUS` or `BOTH_AMBIGUOUS`.

---

## D7 — Expansion and intervention feasibility (after S30)

Same quantities as D6 on all 500 queries (`E` = technical failures / episodes run), plus
`C` = number of candidates meeting the §21 candidate rule (frozen at S29) **with** a matched control.

| Order | Outcome | Rule | Action |
|---|---|---|---|
| 1 | HOLD | `E > 15%` | As in D6 |
| 2 | **DESCRIPTIVE** | `N < 15` **or** not `O > null` **or** `C < 8` | No confirmatory surgery; up to 5 illustrative exploratory cases |
| 3 | **CONFIRMATORY** | `N ≥ 30` **and** `O > null` **and** `P ≥ 4` **and** `C ≥ 20` | Run the intervention study on all eligible candidates |
| 4 | **EXPLORATORY** | Otherwise | Run on available candidates; label results exploratory |

---

## D8 — Final scale decision (S37)

Scale beyond 500 queries only if D7 was CONFIRMATORY or EXPLORATORY **and**
(a) fewer than 10 cases exist for at least one §21 mechanism, **or** (b) intervention cases cover
fewer than 5 relation types — **and** (c) the compute estimate for the larger run, written in the
decision log first, fits the remaining schedule. Otherwise stay at 500.
