# CoFail-KG — Decision Rules

**Version:** 1.0 · Frozen before the data each gate judges is seen.

These are **feasibility criteria**, not significance tests. They decide whether the project has
enough of the phenomenon to continue, and what to do next. Thresholds were chosen from the sample
sizes the later stages need (explained under each gate).

## Rules for the rules

1. A threshold may be changed only **before** the gate's input data exists, with a dated entry in
   `docs/decision_log.md`.
2. After the data exists, thresholds are fixed. If you disagree with the outcome, record the
   disagreement and any follow-up analysis as **exploratory**.
3. Claude Code computes the quantities and applies the rules mechanically. It reports the outcome;
   it never changes a threshold.
4. Every gate outcome is recorded in `docs/decision_log.md` with the numbers that produced it.

---

## D1 — Semantics and relation-mapping gate (end of S6)

**Input.** For each of the 12 BioHopR relation pairs, a validation sample of up to 30 rows
(all rows if fewer; seed 42), and the exact-reproduction rate of the chosen mapping:
the share of rows where `T_q^{b*} = A*_q`.

| Outcome | Rule | Action |
|---|---|---|
| Pair PASS | Reproduction rate ≥ 90% | Pair enters the primary population |
| Pair FAIL | Reproduction rate < 90% | Investigate for up to 2 working days (field roles, direction, alternative labels). If still < 90%, the pair is excluded (decision-log entry). |
| **Global PROCEED** | ≥ 6 of 12 pairs PASS **and** PASS pairs cover ≥ 70% of 2-hop rows | Continue to S7 |
| **Global STOP** | Otherwise | Do not continue. Re-check the PrimeKG release, field roles (S5) and edge direction (S4). A systematic mismatch usually means the wrong PrimeKG release. |

Why 90%: BioHopR's answers were generated from PrimeKG by a deterministic procedure, so the right
release and mapping should reproduce them almost exactly. A lower rate signals a version or
interpretation mismatch, which would contaminate every later measurement.

---

## D2 — Dataset feasibility gate (S9)

**Input.** `N_P` = size of the primary population (CONSISTENT ∧ not SATURATED ∧ PASS pair);
per-pair counts; single/multi-bridge counts.

| Outcome | Rule | Action |
|---|---|---|
| **GREEN** | `N_P ≥ 650` **and** ≥ 5 relation pairs each with ≥ 20 eligible queries | Continue as planned |
| **YELLOW** | `150 ≤ N_P < 650`, **or** fewer than 5 pairs with ≥ 20 eligible | Continue; expansion (D6) limited to what is available; note reduced coverage |
| **RED** | `N_P < 150` | Stop before building agents. Revisit PrimeKG release, mapping, saturation threshold (decision-log entry for any change). |

Why 650: screening (20) + smoke (4) + pilot (100) + expansion reserve (400) = 524 queries, plus
margin for strata that run out.

**Saturation threshold (decided at this gate).** Default: exclude queries where `T_q` covers more
than 50% of all PrimeKG nodes of `Type_T`. Before looking at the D2 outcome, inspect the
distribution of this coverage share and confirm or change the default (decision-log entry).

---

## D3 — Model selection gate (S20–S21)

**Input.** Screening results for each candidate model on the 20 screening queries.

A model **passes** if all of the following hold:

| Criterion | Threshold |
|---|---|
| Tool-call validity (well-formed calls / attempted calls) | ≥ 90% |
| Valid final JSON (after the single allowed re-prompt) | ≥ 90% of episodes |
| Competence floor: at least one `SUPPORTED` question-valid answer | ≥ 40% of screening queries |
| Median episode wall time | ≤ 5 minutes |
| Runs at the chosen `num_ctx` without out-of-memory errors | 20 of 20 episodes |

**Selection.** From passing models, choose four that maximize family diversity (at least 3
distinct model families; prefer 4). Ties: higher competence, then lower latency.

| Situation | Action |
|---|---|
| ≥ 4 pass | Freeze four (S21) |
| < 4 pass | Screen additional candidates (at most 2 more rounds) |
| Still < 4 after 2 rounds | Decision-log entry: either run with 3 agents (CF3 becomes the strict metric; CF4 is not computed) or relax one named criterion with justification |

Why 40%: models below this rarely produce grounded answers, so their "failures" would mostly be
incompetence rather than correlated error.

---

## D4 — Panel smoke-test gate (S25)

**Input.** 4 smoke queries × 4 agents = 16 episodes, plus your manual audit of 8 episodes.

**PASS** requires all of:

- all 16 episodes end in an explicit status (success, `PARSE_FAIL`, timeout, or error) — no silent failures;
- ≥ 14 of 16 episodes produce valid final JSON;
- the leakage test passes;
- trace-graph reconstruction matches the raw tool log for all 16 episodes;
- the manual audit of 8 episodes finds **zero** Label A or Label B errors;
- the kill-and-resume test completes without duplicated or missing episodes.

**FAIL** → fix the implementation (definitions unchanged), rerun the same 16 episodes, re-audit.

---

## D5 — Pre-run freeze check (S26)

The 100-query pilot may start only if:

- neither `frozen_pilot_protocol.md` nor this file contains a `[TBD@Sx]` item with x ≤ 26;
- all tests pass on a clean git working tree, and the commit hash is recorded;
- PrimeKG SHA256 and BioHopR revision match the recorded values;
- the four model digests match those frozen at S21;
- the pilot manifest hash matches the one produced at S10.

---

## D6 — Pilot decision gate (S29)

### Quantities (computed on the 100 pilot queries)

| Symbol | Definition |
|---|---|
| `E` | Technical failure rate: episodes ending in crash, timeout, or `PARSE_FAIL`, divided by 400 |
| `H` | Share of queries where ≥ 3 of 4 agents **found R1** (`H1_CLEAN` or `H1_MIXED`, protocol §14.3) |
| `N` | Number of queries with **CF3^{Q,H1} = 1** (protocol §16.1) |
| `O > null` | Observed restricted CF3 total exceeds the 95th percentile of null N1 (protocol §17) |
| `P` | Number of distinct relation pairs among the `N` queries |

### Outcomes — checked in this order; the first match wins

| Order | Outcome | Rule | Action |
|---|---|---|---|
| 1 | **HOLD** | `E > 15%` | Not a scientific outcome. Fix the implementation, rerun only the failed episodes with the identical frozen configuration, recompute, re-apply D6. |
| 2 | **RED** | `H < 20%` **or** `N < 3` **or** not `O > null` | Do not build intervention machinery. Write up the descriptive results. Possible exploratory follow-ups: closed-book comparison, bridge-preference analysis. |
| 3 | **GREEN** | `H ≥ 40%` **and** `N ≥ 10` **and** `O > null` **and** `P ≥ 3` | Expand to 500 queries (S30); proceed toward Phase 2. |
| 4 | **YELLOW** | Anything else | Expand to 500 queries (S30); Phase 2 remains exploratory unless D7 is CONFIRMATORY. |

Why these numbers: with four agents, `H ≥ 40%` leaves roughly 40 of 100 queries for the structural
analysis; `N ≥ 10` in 100 projects to about 50 cases in 500, enough to form intervention and
control groups; `N < 3` means the phenomenon is too rare to study with this budget.

### Interpretation flags (reported, not gates)

- **Ordering flag:** observed agreement exceeds N1 but not N2 → "consistent with a shared-ordering
  effect"; must be reported with the result.
- **Ambiguity flag:** if more than 70% of the `N` cases come from pairs tagged `R1_AMBIGUOUS`,
  `R2_AMBIGUOUS` or `BOTH_AMBIGUOUS`, report that co-failure is concentrated where wording is
  ambiguous (weaker evidence for a structural effect).

---

## D7 — Expansion and intervention-feasibility gate (after S30)

Same quantities as D6, computed on all 500 queries, plus `C` = number of intervention candidates
meeting the protocol §21 candidate rule **with** an available matched control.

| Order | Outcome | Rule | Action |
|---|---|---|---|
| 1 | HOLD | `E > 15%` | As in D6 |
| 2 | **DESCRIPTIVE** | `N < 15` **or** not `O > null` **or** `C < 8` | No confirmatory surgery. Thesis reports the observational study; up to 5 surgery cases may be run as illustrative exploratory examples. |
| 3 | **CONFIRMATORY** | `N ≥ 30` **and** `O > null` **and** `P ≥ 4` **and** `C ≥ 20` | Freeze the Phase 2 design (protocol §21) and run the intervention study on all eligible candidates. |
| 4 | **EXPLORATORY** | Anything else | Run the intervention study on available candidates; label all intervention results exploratory. |

---

## D8 — Final scale decision (S37)

Scale beyond 500 queries only if D7 was CONFIRMATORY or EXPLORATORY **and** at least one of:

- fewer than 10 cases per intervention mechanism (e.g., `SHORTCUT`, `WRONG_RELATION_HOP2`);
- relation-pair coverage < 5 pairs among intervention cases;
- estimated compute for the larger run fits within the remaining thesis schedule (write the
  estimate in the decision log first).

Otherwise stay at 500.
