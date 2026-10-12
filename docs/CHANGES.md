# What changed since v1.0 — one page

The study design is the same as in v1.0: four agents explore PrimeKG; T_q (all bridges) is the
answer key; every answer gets Label A (right answer?) and Label B (right route?); co-failure means
3 or 4 agents share a wrong answer; results are compared with chance; gates decide what's next.

Everything below makes an existing rule precise. Nothing replaces an idea from v1.0.

## Changes that are useful to understand

1. **A query is one question, not one dataset row.** Rows with the same starting entity (same
   PrimeKG node) and the same question type are merged; their gold answers are combined.
2. **The mapping test checks both hops** (hop-1 score and hop-2 score). Both must reach 90%.
3. **Ambiguity tags are computed by code:** a hop is ambiguous if another PrimeKG label connects
   the same two node types. No spreadsheet.
4. **Bridges that lead nowhere don't count as bridges.**
5. **A question is CONSISTENT only if everything matches:** entity found, all gold bridges valid,
   every gold answer found, and the answer lists equal.
6. **Questions that name their own bridge or answers are excluded** (LEAKY_QUESTION).
7. **Agents read a separate question sheet** with only the question and starting entity.
8. **Each chance baseline compares like with like.** The pilot gate compares hop-1-clean shared
   wrong answers with a hop-1-clean random baseline.
9. **Screening uses fixed settings;** the final settings are chosen afterwards by written rules.
10. **All frozen hashes live in one file,** `configs/frozen_hashes.yaml`.

## Precision-only changes (no need to study)

Tie-break rules, error message templates, JSON parsing details, status precedence, reruns and
attempts, random-number details, rate denominators, audit selection, naming ("relation type").

## New ground rule

The protocol fixes only what can change a scientific result or a gate outcome. Engineering details
are decided in code, tested, and reported by Claude Code at the end of each stage. Audits report
only scientific problems.

## Amendment 2026-10-12 (S4) — answer construction per relation type (protocol v1.3)

Protocol version 1.2 → **1.3 (2026-10-12)**. This one changes a rule, not only its wording. S4 found that BioHopR builds most answer lists from
the stored bridge only, but one relation type (disease:drug:effect/phenotype) from the union over
all bridges. Each relation type now adopts one construction at S6: **BRIDGE** (`T_q^{B*}`) or
**UNION** (`T_q`), whichever reaches 90% on the hop-2 score; BRIDGE if both do (§5.1, new §5.3).
CONSISTENT and Label A compare against the adopted one, `G_q` (§6, §7.1, §13). `T_q` stays the
correctness reference for every type. Results are reported split by construction. Decision log:
"S4 — Answer construction: option C, per relation type".

## Amendment 2026-10-13 (S4) — field-role support defined (protocol v1.3.1)

Protocol version 1.3 → **1.3.1 (2026-10-13)**. §3.1 now defines when a sampled row is resolvable
(hop2 and hop1 resolve; at least half, and at least one, of its answer names resolve) and when it
supports the field roles (hop2–hop1 adjacent; at least one answer via hop1; every answer via hop1
or another bridge of hop2). This lets UNION rows pass S5 when their roles are correct. The sample,
ordering, 95% threshold and every-type rule are unchanged; runbook S5 step 3 matches. Decision
log: "S4 — Field-role support defined (§3.1, protocol v1.3.1)".

## Amendment 2026-10-13 (S4) — field-role failure handling (protocol v1.3.2)

Protocol version 1.3.1 → **1.3.2 (2026-10-13)**. A relation type that fails the §3.1 field-role
rule (below 95% support, or no resolvable sampled row) is now excluded and counts as FAIL in Gate
D1, instead of stopping S5. S5 still stops if more than one type fails or the failing types cover
more than 1% of the 7,633 2-hop rows. Sample, ordering, 95% threshold and Support definition are
unchanged; the runbook S5 prompt matches. `decision_rules.md` Gate D1 now lists the §3.1 failure as
a Type FAIL trigger, with no 2-day investigation (re-admission after seeing the S5 sample would be
post hoc). Decision log: "S4 — Field-role failure handling (§3.1, protocol v1.3.2)".
