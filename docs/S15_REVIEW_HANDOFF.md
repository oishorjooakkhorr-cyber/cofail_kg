# S15 handoff: finish review and record approval

Status on 2026-10-16: automated verification passes; final S15 acceptance is pending.
The researcher requested publishing this state so other developers can review
the evidence and decide what remains necessary. This file is temporary. **Delete
it only after explicit S15 approval is recorded in the permanent decision log.**
Keep the evidence and permanent completion record; do not delete failed audits.

## Context and decisions already made

S15 audits leakage into experimental-agent inputs. The original strict whole-word
check failed for BH2_04007: Folic acid is a valid non-gold bridge name contained
in the canonical starting name folic acid deficiency anemia. The researcher
initially retained that failure, then authorized an amendment to protocol
§19.1(a). The failed evidence remains in results/diagnostics/s15/.

The amendment exempts a match only when it is a non-gold B_q member name, lies
entirely within start_name, and start_name exactly equals the PrimeKG canonical
name of the starting node. Gold, T_q, ID, label, relation-type and evaluator-term
matches still fail, as do occurrences outside the canonical-name span. There is
no added requirement that the canonical name appear verbatim in the question.
Read the authoritative paragraph in docs/frozen_pilot_protocol.md §19.1(a).

The chronology is **before any pilot model run or co-failure results**. Earlier
real S14 diagnostic episodes existed; do not claim this preceded every model run.
No model calls or episodes were made during S15 verification.

The all-524-row scan found exactly four SOURCE_NAME_OVERLAP queries. Recorded
per-row decisions in results/diagnostics/s15/overlap_review.json are:

| Query | Decision | Classification |
|---|---|---|
| BH2_04007 | Accept | contained-phrase overlap |
| BH2_05778 | Accept | full-name, cross-type overlap |
| BH2_05971 | Accept | contained-phrase overlap |
| BH2_06099 | Accept | contained-phrase overlap |

For BH2_05778, Ewing sarcoma names both starting phenotype node 89218 and bridge
disease node 29749. The researcher authorized acceptance or exclusion; the
assistant selected acceptance under the existing exemption. This provenance is
recorded explicitly. These decisions do not establish absence of model effects.

All four remain flagged and included in official gate populations. Every §16
metric and §17 chance-baseline comparison must later report both all queries and
the population excluding SOURCE_NAME_OVERLAP. No resampling or new exclusion
rule is authorized. This handoff does not authorize starting S16.

## Evidence to read

Paths below are repository-relative.

| File | Purpose |
|---|---|
| results/diagnostics/s15/manual_review_packet.md | Readable remaining review: common system prompt, 34 short-name entries grouped into 26 queries, and all 24 captured screening/smoke user messages |
| results/diagnostics/s15/source_name_overlap.json | Original all-524 scan, four flags, counts and short-name list |
| results/diagnostics/s15/overlap_review.json | Subsequent per-row decisions and their authority |
| results/diagnostics/s15/audit-v2.json | Revised machine-readable audit including exact captured messages |
| results/diagnostics/s15/verification-v2.json | Historical automated verification summary; manual-review status reflects that run |
| docs/S15_implementation.md | Implementation, limits, test results and later overlap decisions |
| docs/decision_log.md | Permanent amendment rationale, chronology and subsequent decisions |
| tasks/todo.md | Current outstanding checklist |

The packet distinguishes actual screening/smoke captures from pilot/expansion
starting lines reconstructed from input sheets. Do not describe the latter as
model-run captures. The common system prompt is identical in all 24 captures.

## Remaining work

1. Review all 34 short-name entries against their corresponding starting lines
   and the common system prompt. The audit reports zero case-insensitive
   whole-word occurrences. Short names are excluded from automatic failure
   classification and require this review. Substrings inside longer words are
   not automatically whole-word matches. Record Accept, Concern or Unsure with
   query IDs and reasons; grouped approval is fine if it explicitly covers all
   34 entries.
2. Review the common system prompt and all 24 captured user messages. Check for
   unintended evaluator information in the scanned surfaces. The original
   question is permitted and outside this leakage scan; the four approved
   canonical-name overlaps remain exceptions under the amendment. Record scope,
   reviewer identity, date, decisions and any unresolved concerns.
3. Save a new dated review record under results/diagnostics/s15/ and append its
   outcome to docs/decision_log.md. Preserve original automated logs and JSON;
   their historical pending status is superseded by the new record, not erased.
   Developers can document findings, but do not invent researcher approval or
   resolve a new scientific ambiguity without researcher direction.
4. If a defect is found, record it and keep S15 pending. Follow CLAUDE.md and the
   protocol; do not silently weaken checks, edit frozen settings, change samples,
   delete failed evidence or launch model experiments. Seek explicit authority
   for any scientific-rule change. Re-run appropriate verification if code or
   inputs change, preserving new results separately.
5. Once both remaining reviews are complete, concerns are resolved and the
   researcher explicitly approves S15, record that approval in the permanent
   decision log. Update docs/progress.md, docs/S15_implementation.md and
   tasks/todo.md to reflect the actual completed review and acceptance.
6. **Only after that approval is recorded**, delete this temporary handoff file
   and remove its active link from tasks/todo.md. Keep manual_review_packet.md,
   review decisions and all historical evidence. Commit the permanent approval
   record, status updates and handoff deletion together. Starting the next stage
   still requires the researcher's instruction.

## Verification already performed

43 focused S15 tests and 401 full-suite tests passed, with no skips/deselections.
The audit found zero remaining leakage failures under the amendment. Original
production code, data, frozen hashes and experimental episodes were preserved.
Later changes add review records and documentation only; no new model calls.

If verification is needed after a relevant change, use the existing environment:

```powershell
.venv/Scripts/python.exe -m pytest tests/test_leakage.py -q -s --basetemp .pytest_tmp_s15_review
.venv/Scripts/python.exe -m pytest -q --basetemp .pytest_tmp_s15_review_full
```

Keep pytest temporary directories outside results/: an existing isolation test
intentionally rejects fixture cache paths under results/. Record fresh output
under new evidence filenames rather than overwriting earlier logs. No additional
test run is required solely to read and record this manual review.
