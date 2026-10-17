# S16 — answer normalization (authorized 2026-10-17)

Implementation/automated verification complete: 49 focused tests, 443 full-suite
tests, 21/21 saved S14 answers by ID, protected files and S7 definitions unchanged.
Report: docs/S16_implementation.md. Researcher inspection/acceptance pending.

The researcher explicitly requested starting S16 and asking about needed
decisions. S15 acceptance is recorded in remote commit 20997df, integrated
before pushing S16. Preserve that approval, its evidence and handoff removal.

Scope: extend evaluation/normalize.py with the protocol §12 agent policy,
synthetic tests, saved S14 example evidence, and stage/status documentation.
Existing S7 definitions and callers remain unchanged. No new dependencies,
experimental calls, data/settings edits, later-stage labels or metrics are needed.

1. Save protected-file identities; inspect all reference-resolver callers.
2. Add failing single-item tests, implement ID precedence and exact-name fallback,
   then pass them alongside the unchanged S7 tests.
3. Ask about unresolved duplicates before implementing list-level deduplication.
   Researcher selected: remove only identical submitted (id, name) pairs; distinct
   unresolved submissions remain separate. Resolved duplicates use canonical ID.
4. Add failing list tests and implement stable deduplication with retained per-item
   audit evidence and duplicate counts.
5. Normalize the saved successful S14 episode without inference; require all 21
   copied tool-output answers to resolve by ID. Save every normalized answer.
6. Run focused/full tests, review against §12, verify protected identities and
   unchanged S7 definitions, and document findings and engineering choices.

Acceptance: all required cases pass, saved example resolves by ID, no regressions
or scientific-rule edits. Human inspection and stage acceptance remain explicit;
no automatic commit/push or continuation to S17.

# S15 revision 2 — authorized and executed (2026-10-16)

The researcher authorized Option 1, a narrow source-name exemption plus a
pre-registered split report, and approved correcting the chronology to before any
pilot model run or co-failure results while acknowledging the S14 diagnostics.
The earlier strict-failure hold is superseded; its record is preserved below.

1. Confirmed no frozen-hash entry covers the protocol; recorded protected-file hashes.
2. Added the authorized paragraph only to §19.1(a) and logged the frozen-item change.
3. Added synthetic regressions first, then implemented per-occurrence character-offset
   checks in tests/test_leakage.py, preserving the literal whole-word matcher.
4. Passed the 24-query audit (one flag) and full 524-row scan (exactly four flags).
5. Passed focused tests (43) and the complete sandbox suite (401), without skips.
6. Saved new versioned evidence and the complete overlap/short-name report; retained
   original evidence and protected production, data, configuration and episode files.

Manual review remains pending. Every §16 metric and §17 baseline comparison must
later report both all queries and the subset excluding SOURCE_NAME_OVERLAP; gates
use all queries. No metric implementation, model call, S16 work or commit in this
revision. Full report: docs/S15_implementation.md, revision 2.

# Original S15 strict audit plan (historical)

Execution update: implementation and audit completed, with one strict failure
retained by the researcher. See docs/S15_implementation.md. Screening BH2_04007's
starting entity contains the name Folic acid, an additional B_q bridge. Checks
(b)-(d) pass; (a) fails. Final full suite: 383 passed, 1 failed. S15 acceptance
and a scientific remedy remain pending; no production/scientific changes made.

Original proposal below, subsequently authorized by the researcher.
Authority: runbook S15 and protocol §§8, 9.3, 10, 19.1. Preserve the completed
S12 plans below. Tasks are appended to tasks/todo.md.

1. Preflight: verify frozen P1/T1, sheet hashes and cache identity. Inventory all
   screening (20) and smoke (4) queries and their evaluator-side reference rows,
   accepted R1/R2 mapping, raw gold names, resolved gold IDs and B_q/T_q names.
   Missing evidence fails explicitly; do not regenerate data or change samples.
2. Add tests/test_leakage.py with small synthetic checks that demonstrate the
   audit detects leaks, handles case-insensitive whole-word punctuation correctly,
   reports names shorter than four characters for manual review, and rejects an
   extra sheet field. IDs and labels are not exempted by the short-name rule.
3. Capture the initial messages produced by the existing runner using a test-only
   fake client stopped at the first chat boundary. No network/model calls or
   saved episodes. Use existing runner fixtures/patterns; do not change production
   message construction or introduce a separate production helper for this audit.
4. Check system content and the starting-entity line for the full query-specific
   prohibited vocabulary. Preserve question text verbatim; do not treat permitted
   question text or tool results as leakage. Print exact system/user messages for
   first screening query BH2_00461, and detailed query/surface/term failures.
5. Audit imports and application-data reads for kg_env, tool_schemas, prompts and
   run_agent, following local dependencies. Combine source inspection with guarded
   reads on exercised paths. Only agent sheets and PrimeKG cache are allowed inputs.
   Evaluator data is read only by the audit harness, outside the guarded agent path.
   Do not confuse result writes or Python/library source loading with experiment
   input reads; inspect any questionable access rather than silently exempting it.
6. Check every line of all four agent-input sheets for exactly query_id,
   question_text, start_name, start_id. For 10 distinct seeded random real
   (entity, label) pairs, compare complete paginated get_neighbors results against
   the index: IDs, names, types, display labels, order and pagination metadata.
   Sort candidates before sampling; record seed 42 and selected pairs. Ensure the
   test budget permits all pages; do not silently truncate.
7. Run focused synthetic/audit tests then the full sandbox suite with a fresh
   workspace --basetemp. Report pass/fail independently for (a)-(d), coverage
   counts, exact messages, short-name review list, commands and results. Save
   docs/S15_implementation.md and results/diagnostics/s15/ evidence; update progress
   and decision log as appropriate. No dependency additions are expected.

Acceptance: all four automated checks pass on complete required evidence; checker
regressions pass; full suite has no regressions; researcher can inspect exact
messages and short-name list. Human review remains explicitly pending until done.
Any real leak or scientific ambiguity is reported, not repaired by changing P1,
data, matching rules or exclusions. No model calls, frozen/protocol changes,
commit/push or S16 work are included in this request.

Expected scope: tests/test_leakage.py, audit evidence/report, progress/decision
documentation and these task files. Existing production modules are audit inputs.
Engineering choices: deterministic seed/order, source plus runtime isolation
checks, test-only interception and report format; none changes scientific rules.

# Plan: remove the Windows hard-link requirement safely

Follow-up requested 2026-10-16 after the completed host/sandbox comparison below.
All follow-up verification must run inside the restricted sandbox. No model calls,
protocol/frozen-setting changes, commits or sandbox-policy changes are planned.

1. Confirm Windows rename can publish a staged file and refuses existing targets
   inside the sandbox (direct probe: PASS).
2. Add regression checks first: Windows operation without hard links, concurrent
   writers, failed publication, and the preflight's refusal of overwrites.
3. Share a small publish-once operation between saver and preflight: os.rename on
   Windows, os.link elsewhere. Never use overwrite-capable os.replace, or Unix
   os.rename. Preserve validation, serialization, flush/fsync, final filenames,
   reconstruction checks and cleanup. Keep the temporary file beside its target.
4. Update the S14 preflight, its error message, README and progress/report.
5. Run S12, launcher checks, actual results/runs synthetic probe and complete suite
   in the sandbox. Use fresh workspace --basetemp paths; no test exclusions or mocks
   replacing real saving in the original persistence tests.

Acceptance: original four sandbox failures pass, concurrent writers have exactly
one winner, existing results stay unchanged, failed publication leaves no final
record, preflight catches unsupported saving before inference, full suite passes.
Windows is tested live; non-Windows dispatch is unit-tested, not claimed as a live
Linux/macOS verification. New filesystem permissions, disk exhaustion and power
failure are not guaranteed away; errors must remain visible and preflight retained.

Scope: trace.py, scripts/14_run_episode.py, their two test files, README,
progress, this plan/checklist, one report and raw diagnostic evidence. Existing
episode records, scientific rules, prompts, settings and failed-run evidence stay
intact. Platform-specific publishing is a routine engineering choice.

Sources: Python os.rename documentation (Windows refuses existing destination;
Unix can overwrite), https://docs.python.org/3/library/os.html#os.rename.

## Prior completed verification plan

Requested 2026-10-16. Preserve protocol, frozen settings, existing records, tests,
and the S12 write-once saver. No model calls or sandbox-policy changes.

1. Reproduce S12 in the restricted sandbox using a fresh workspace temporary root.
2. Run the unchanged S12 suite through approved host execution.
3. Exercise the existing S14 persistence preflight and the S12 save/load/overwrite
   checks with synthetic data in a temporary subdirectory of actual results/runs.
4. Run the complete host test suite without exclusions; preserve raw output.
5. Document outcomes and the supported procedure for subsequent experiments.

Success: S12 and full host tests pass; actual output-directory probe passes;
sandbox limitations are reported explicitly. Do not weaken persistence to make
restricted execution pass. Host execution requires the normal tool approval review.
Future launchers must check persistence before inference, as S14 already does.

Tasks and verification: tasks/todo.md. Engineering choices only; no scientific
decision needed. If host execution is unavailable, retain evidence and report
the blocker rather than treating unrun checks as passed.
