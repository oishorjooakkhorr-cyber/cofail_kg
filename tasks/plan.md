# Gemma RTX 5060 Ti S20 — 2026-10-29 investigation

Completed the authorized fresh 2026-10-28 block: D3 PASS, 19 SUCCESS,
one retained PARSE_FAIL, 14 competent. Tested/committed launcher before
inference; exact digest/frozen order/f16 KV/full GPU checks passed.
Investigated all six material changes against historical 8K/full 16K traces;
offline reporting and 1315 historical/21 new/46 source hashes verified.
Scoped report/evidence pushed to GitHub main as 8c53402 (launcher b49ac91).
Drive upload recovered using the researcher-selected university account:
exact checksum check verified all 69 Gemma scientific files, zero differences.
Nine older S13-S15 archival move errors remain outside this run; global backup
success is not claimed. No additional inference is needed.
[Report](../docs/S20_gemma4_5060ti_16k.md). Stop after publication; no new model,
experimental retries or S21. Older plans below retain their dated history.

# Current S20 plan/status — 2026-10-21

**Command R7B full 8K block completed: D3 FAIL.** Twenty saved outcomes,
nineteen SUCCESS, one PARSE_FAIL, zero tool attempts, zero competent queries,
median 2.889849 s and zero OOM. Forty-two screening tests and offline/integrity
checks passed. Nine original 8K blocks and three complete 16K reassessments
now exist. Three passing candidates remain; researcher round accounting and
S21 selection remain pending. [Report](../docs/S20_command_r7b_screening.md).
The counts below retain the previous checkpoint.

**Granite 4.1 16K reassessment stopped by researcher during query 16.**
Preserve fifteen final records (six SUCCESS, nine request-timeout errors);
five queries have no final record. No completed 16K verdict or automatic resume.
At most 11/20 SUCCESS remains possible, below D3. Keep the original 8K PASS.
[Stopped report](../docs/S20_granite41_16k_stopped.md).

Completed: eight original twenty-query 8K candidate blocks and three separate
full 16K reassessments. See [all results and failure reasons](../docs/S20_screening_status.md).

- **Passing at recorded settings:** Granite41-8B at 8K; Gemma4-E4B and
  Qwen35-9B at 16K. Original 8K verdicts remain preserved.
- **Still failing:** Llama31-8B and Granite33-8B (call validity/competence),
  Granite42-8B (SUCCESS/competence), OLMo3-7B (competence), Ministral3-8B
  (SUCCESS at both contexts). These failures are completed measurements.
- **Granite 4.1:** 20/20 SUCCESS, 14/20 competent, 217/217 well-formed calls,
  median 61.3250475 s, OOM 0; all five D3 criteria PASS. Its previous deferred
  status is superseded. [Report](../docs/S20_granite41_screening.md).
- **Remaining:** a fourth passing model is needed under D3. Researcher decides
  additional-candidate membership/round accounting and later S21 selection;
  no further inference or final configuration freeze is authorized here.

Older sections below retain their dated history. Their previous next-candidate,
unrun and untested statements are superseded where this current status differs.

**Full 16K D3 reassessment complete (2026-10-20): Gemma PASS, Qwen PASS,
Ministral FAIL.** All sixty fresh queries completed, twenty per model, without
stitching selected diagnostic outputs into old results. Current researcher-
authorized acceptance: Gemma4-E4B and Qwen35-9B pass at 16K; Ministral3-8B does not.
Gemma: SUCCESS 19/20, competence 14/20, calls 181/181, median 16.2779325 s, OOM 0.
Qwen: SUCCESS 19/20, competence 13/20, calls 263/263, median 56.839506 s, OOM 0.
Ministral: SUCCESS 12/20, competence 12/20, calls 167/167, median 168.0803425 s,
OOM 0; eight preserved request-timeout errors cause its SUCCESS-criterion FAIL.
42 focused tests passed; all three offline reports reproduced. All 63 new run
hashes, 147 old run hashes, 140 old metrics, old table, 43 pinned sources, 122
protected identities and prior diagnostic evidence are unchanged. All starting
prompts match their 8K counterparts; only configured scientific change is context.
Historical 8K verdicts remain preserved. No S21 selection/freeze.
Report: docs/S20_full_16k_reassessment.md.
Acceptance: results/diagnostics/s20/full-16k-20261020/acceptance.json.

**S20 context-window audit complete (2026-10-20; offline).** Across all 140
saved official episodes, earlier context-related parse failures occur in Qwen3.5
9B (two direct cases) and Ministral 3 8B (three direct cases plus one mixed
context/schema failure). Five earlier final responses end exactly at 8192 tokens
with length termination and output below the 4096 cap. Ministral BH2_03619 first
hits context but its final normal-stop reply omits answers. Qwen/Ministral 16K
recovery remains untested. Gemma's existing 4/4 parsing recovery and 3/4 competent
16K diagnostic is documented separately. Twenty saved parser errors reproduced;
all original/diagnostic/source hashes unchanged; no model call or D3 change.
Report: docs/S20_context_window_audit.md.

**Gemma 4 E4B 16K diagnostic complete (2026-10-20).** The four original
8K PARSE_FAIL queries all completed SUCCESS at 16K in one continuous process.
Three recovered supported answers (85, 66, 90 GOLD/SUPPORTED items); BH2_03762
parsed but all six answers were OFF_QUESTION/PATH_INVALID. Only num_ctx changed
scientifically; 51/51 native calls well formed; no thinking, errors or OOM.
Actual context 16384 verified. All 147 official runs, 140 metrics, official table,
43 pinned and 122 protected hashes unchanged. Original S20 D3 remains FAIL;
this selected diagnostic does not establish a full 16K D3 result.
Report: docs/S20_gemma4_16k_diagnostic.md.

**S20 Gemma 4 E4B complete (2026-10-20): candidate fails D3 on SUCCESS rate.**
All 20 frozen queries ran uninterrupted in one --max-new 20 invocation: 16 SUCCESS,
four preserved PARSE_FAIL, no ERROR/TIMEOUT/OOM. D3: 149/149 well-formed calls
(PASS), SUCCESS 80% (FAIL), competence 11/20=55% (PASS), median wall
11.9732305 s (PASS), OOM 0 (PASS). No thinking; largest prompt 8190.
598 tests passed; synthetic native tools/think=false passed. Offline report-only,
147 run hashes (126 prior), 120 prior metrics, 122 protected, 43 pinned sources
and six prior table rows verified. No source/scientific change, retries or S21.
Report: docs/S20_gemma4_screening.md.

**S20 Granite 4.2 8B complete (2026-10-19): candidate fails D3.** All twenty
frozen outcomes saved: 17 SUCCESS and three preserved ERROR/CONNECTION timeouts.
D3: 327/327 well-formed calls (PASS), SUCCESS 17/20=85% (FAIL), competence
6/20=30% (FAIL), median wall 120.247903 s (PASS), OOM 0 (PASS). Largest prompt
8190, median charged calls 12.5, budget-hit share 35%, no thinking messages.
Final four all SUCCESS under the researcher-approved timeout continuation policy.
598 tests passed before inference; final report-only, all 126 run hashes
(122 last checkpoint, 105 prior), 122 protected, 43 pinned and 116 existing metrics
verified; prior table rows unchanged. No rerun, source/scientific change, S21,
commit or push. Report: docs/S20_granite42_screening.md.

# S20 - OLMo 3 7B Instruct (2026-10-19; complete)

**S20 OLMo 3 7B Instruct complete (2026-10-19): candidate fails D3.** All 20
frozen queries saved in primary-3060ti-20261018. D3: 60/62 well-formed calls
(96.7742%, PASS), SUCCESS 20/20 (PASS), competence 0/20 (FAIL), median wall
8.951106 s (PASS), OOM 0 (PASS). Eighteen no_answer outputs; two answered
outputs contain 12 OFF_QUESTION/PATH_INVALID items. No supported answers.
598 tests passed; report-only and all 105 run-file hashes (84 prior), 122
protected and 43 pinned identities verified. Context 8192, partial CPU/GPU
offload recorded without tuning, largest prompt 8137, no nonempty thinking.
No errors, reruns, source/config/scientific changes, S21 work, commit or push.
Report: `docs/S20_olmo3_screening.md`.

# S20 - Ministral 3 8B (2026-10-19; authorized block complete)

Completed all 20 frozen queries. The researcher explicitly authorized the four
remaining queries after the saved ERROR/CONNECTION at query 16; all four completed
SUCCESS. All prior records, including the error and four PARSE_FAILs, are unchanged.
D3 FAIL on SUCCESS (15/20=75%). Other criteria pass: 197/197 well-formed calls,
10/20 competent, median wall 62.850686 s, zero OOM. Synthetic native tools and
think=false passed; automatic 16%/84% CPU/GPU placement recorded at context 8192.
598 tests passed before inference; final report-only and all 84 run-file hashes,
122 protected and 43 pinned identities match. No scientific/source/config change,
rerun, 16K follow-up, S21 choice, other model, commit or push. Stop after this
candidate. Report: docs/S20_ministral3_screening.md.

# S20 - Updated model shortlist (2026-10-19; proposal)

Researcher requests newer models at the existing 7B-9B scale. Source-checked
proposal: docs/S20_updated_model_pool_proposal.md. Recommend next preflight of
ministral-3:8b, then olmo-3:7b-instruct. granite4.2:8b is conditional on native
tools/disabled thinking support; ibm/granite4.1:8b remains a later fallback or
additional candidate. Retain the exact completed Qwen3.5 identity and all three
historical candidate blocks. No downloads or new inference in this update.
Exact pool membership, old-candidate disposition and D3 round accounting remain
researcher decisions. Frozen rules/settings and prior results stay unchanged.

# S20 - Granite 3.3 8B (2026-10-19; authorized block complete)

Researcher requested S20 for the downloaded granite3.3:8b, an original planned
candidate. Exact identity/native tools checked, synthetic add passed, 598 tests
passed, prior records and protected/pinned inputs verified. Ran 20 separate
--max-new 1 invocations with exit/status/order/identity/hash checks. All completed;
no stop condition. Report-only resume retained all 63 official run files.

D3 FAIL: well-formed 0/8, competence 0/20; SUCCESS 20/20, median wall 13.597764 s,
zero OOM. Zero native KG calls, eight logged text tool calls; no supported answers.
Full GPU residency (41/41 layers, context 8192). No source/config/scientific
changes, reruns, other candidate, S21 selection, commit or push. Three candidates
screened, six planned candidates remain. Report: docs/S20_granite33_screening.md.

# S20 - Qwen3.5 9B (2026-10-18; authorized block complete)

Researcher added qwen3.5:9b as an extra candidate, retaining the original eight,
then paused official screening to investigate GPU memory. Compatibility passed
and 598 tests passed. Reproduced load: 32/33 layers on GPU, about 70 MiB short
of Ollama's all-layer fitting target. Report: docs/S20_qwen35_preflight.md.

Researcher subsequently accepted the recorded offload and authorized all 20
official queries. Completed 20 separate --max-new 1 invocations with checks of
exits, status, frozen order, hashes and sources between queries. No stop
condition occurred. D3 passes: 210/210 well-formed; 18/20 SUCCESS; 15/20
competent; median wall 26.383874 s; zero OOM. Two PARSE_FAIL records retained.
Report-only resume and all 42 run-file hashes verified; protected/pinned hashes
unchanged. Inspected correct, wrong-target and parse-failure examples.
Report: docs/S20_qwen35_screening.md. Stop after this candidate: no other
model, S21 selection, 16K follow-up, source/config edits, commit or push.

# S20 - Remaining Llama screening block (authorized 2026-10-18)

Researcher accepted the first checkpoint, fixed D3 argument typing without
coercion and resolved the stop-policy conflict through nineteen separate
--max-new 1 host invocations with exit/status/order/hash checks between calls.
This supersedes the historical first-episode-only stop below.

Completed: all 20 Llama episodes saved in frozen order; no ERROR, non-zero Python
exit or drift. Original record unchanged. D3 fails on well-formedness (0/620) and
competence (0/20); SUCCESS, median wall-time and OOM criteria pass. Full suite
598 passed; report-only resume preserves all 21 run files, with 20 unique
episodes. All 43 pinned hashes and 122 protected identities remain unchanged.
Report: docs/S20_llama_screening.md. Stop here: no other candidate, S21 decision,
source/config/data/test changes, commit or push.

# S20 - Screening launcher and first Llama episode (authorized 2026-10-18)

The researcher authorized implementation and the first official screening episode
after reviewing Llama 3.1 8B identity, synthetic tool use, and 100% GPU residency
at context 8192. This supersedes historical instructions below not to start S20.
Stop after inspecting this first episode; do not run the remaining 19, select
models at S21, commit, or push in this turn.

1. Preserve existing code/tests/science/config/data/episodes with a hash baseline;
   record the thinking, hardware, candidate-pool and sequential-run decisions.
2. Write failing synthetic tests for D3 counting, incomplete tables, immutable
   provenance and resume of all final statuses, then implement the S20 launcher
   using the unchanged S14 runner and S16-S19 evaluation.
3. Pass focused and full suites; review the change and verify protected hashes.
4. Verify installed Llama digest and native-tools metadata. Test sandbox access
   before creating an episode; if transport is blocked, use the host explicitly.
5. Run exactly the first screening query with the frozen settings, save the
   complete record, evaluate it, and demonstrate a no-inference resume/report.
6. Record the first result, engineering decisions and next checkpoint. The
   screening table stays explicitly incomplete until all 20 queries are saved.

# S19 - Per-agent metrics (authorized 2026-10-17)

Implement protocol §15 using S12 and S16-S18 unchanged. Researcher clarified
resolved-only benchmark precision, count-form F1, and NA answer-quality scores
for technical failures; see the decision log.

1. Save protected identities and inspect callers, raw logs and S7 reference tables.
2. RED/GREEN degree statistics against unique-neighbor counts and inclusive ranks.
3. RED/GREEN answer metrics, bridge recall/rank, pagination and effort cases.
4. Replay saved S14; hand-check bridge rank and early stop against raw calls.
5. Review, mutation-check, run the full suite and compare protected identities;
   record complete evidence and the stage report. No S20 or new inference.

Implementation/automated verification complete: 48 new synthetic cases, 148
focused checks and 556 full-suite tests passed without skips. Both deliberate
mutations caught/restored; all 112 protected files unchanged. Final saved S14
replay matches retained metrics exactly: TTR rank 1, early_stop=false, bridge
recall and benchmark P/R/F1 all 1, 2 page requests/4 calls, budget not exhausted.
Report: docs/S19_implementation.md. Researcher accepted S19 and its verification
evidence on 2026-10-17. Record the §16 requirement that technical failures must
not count as answer failures, then commit as `S19: per-agent metrics`.
Stop at S19. Do not push or start S20.

# S18 - Label B, reason codes and hop-1 status (authorized 2026-10-17)

Researcher explicitly requested S18 implementation and questions for any needed
scientific decisions. Use frozen protocol §14 and runbook S18. Preserve S12,
S16/S17, data, settings and saved episodes; no inference or S19 work.

1. Save protected identities and inspect S12 paths, normalization and all callers.
2. Write failing synthetic Label B/reason-code tests, then implement the evaluator.
3. Resolve H1 path/cycle interpretation with the researcher; test and implement H1.
4. Verify every saved S14 answer against raw returned items and its primary path.
5. Review, run focused/full tests and a deliberate mutation, compare protected
   hashes, and record evidence, engineering choices and manual review items.

Implementation/automated verification complete: 48 new synthetic cases, 142
focused checks and 508 full-suite tests pass. Both deliberate mutations caught
and restored; all 71 protected hashes unchanged. All 21 saved S14 answers are
GOLD/SUPPORTED with H1=1, codes empty and H1_CLEAN; every primary path checked
against raw returned items and KG edges. Report: docs/S18_implementation.md.
S18 accepted under the researcher's explicit delegated-review authorization
(2026-10-17): replay matches saved output and all 21 inspection-table rows;
48 S18 cases pass again. Implementation commit: `efee848`.
Commit/push the acceptance record, then stop. No S19 work.

# S17 - Label A (authorized 2026-10-17)

Implement protocol §6/§13 using S7's saved G_q: BRIDGE uses gold-bridge
targets; UNION uses all valid targets. Preserve S16 normalization and all
scientific rules, frozen settings, data and episodes.

Implementation/automated verification complete: 76 focused checks and 460 full-suite
tests passed; saved S14 BRIDGE query has 21 GOLD answers, two checked through gold
bridge TTR (111); all 53 protected files unchanged. Report: docs/S17_implementation.md.
Researcher accepted S17 and its evidence on 2026-10-17, and explicitly authorized
commit `S17: Label A` and push. Acceptance recorded in the decision log. Completed plan:

1. Save protected-file hashes; inspect S7/S16 structures and existing callers.
2. Write failing synthetic tests for priority, shared targets, both construction
   modes, the UNION prohibition on ALT_VALID, and CONSISTENT extra-target errors.
3. Implement the evaluator-only labeler with one ordered label per retained answer.
4. Replay the saved S14 episode without inference, print every label, confirm
   primary-population membership and state its construction mode in two hand checks.
5. Run focused/full tests, mutation check and protected-file comparison; save
   evidence and report engineering choices and manual inspection items.

S17 implementation/verification and researcher acceptance are complete; perform
the explicitly authorized commit/push, then stop. Do not start S18.

# S16 - answer normalization (authorized 2026-10-17)

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
