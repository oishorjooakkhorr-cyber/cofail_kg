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
