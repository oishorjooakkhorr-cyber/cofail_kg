# S20 - Qwen3.5 9B preflight (2026-10-18)

- [x] Record addition as an extra candidate, preserving the original eight.
- [x] Verify identity, native tools and synthetic disabled-thinking exchange.
- [x] Run full suite: 598 passed; verify 122 protected and 43 pinned hashes.
- [x] Pause official inference at researcher's request; investigate GPU memory.
- [x] Capture isolated Ollama load: 32/33 GPU layers, about 70 MiB fitting shortfall.
- [x] Researcher recheck after closing apps; same placement and 70 MiB shortfall.
- [x] Researcher accepts recorded offload and authorizes all 20 official queries.
- [x] Run full official block with separate invocations and strict stop checks.
- [x] Verify report-only resume/integrity, inspect episodes and report final D3.

Qwen D3 PASS: 210/210 well-formed; 18/20 SUCCESS; 15/20 competent;
median wall 26.383874 s; zero OOM. All 20 outcomes saved, no reruns. All 42 run
files, 122 protected identities and 43 pinned sources/inputs verified unchanged.
Report: docs/S20_qwen35_screening.md. No S21 choice or 16K follow-up yet.

# S20 - Remaining Llama screening block (2026-10-18)

- [x] Record checkpoint acceptance, strict D3 typing and per-invocation execution authorization.
- [x] Confirm CLI flags, strict checker, original record, nineteen remaining queries and pinned hashes.
- [x] Execute nineteen host invocations with --max-new 1; check exit/status/order/hashes between each.
- [x] Save all twenty episodes and complete D3 row; do not rerun the original episode.
- [x] Full suite 598 passed; report-only resume retains twenty unique episodes and all twenty-one run files.
- [x] Verify 43 pinned hashes and 122 protected identities unchanged; report all per-query times and inspect three records.
- [x] Stop after Llama block; no other candidate, S21 selection/freeze, commit or push.

Llama D3 FAIL: well-formed 0/620, competence 0/20; other three criteria pass.
Full report: docs/S20_llama_screening.md. The rest of the S20 pool is unrun.

# S20 - Launcher and first Llama episode (2026-10-18)

- [x] Researcher authorizes S20 implementation and first Llama screening episode.
- [x] Preserve protected-file hashes and record pre-screening decisions.
- [x] RED/GREEN screening counts, D3 boundaries, provenance and resume checks.
- [x] Implement screening launcher and evaluator-only table using existing helpers.
- [x] Review, 598 full-suite tests (42 new), saved S14 replay and 122 unchanged protected identities.
- [x] Run exactly one Llama episode; inspect/evaluate it and verify report-only resume.
- [x] Report first result and stop before further screening or S21 decisions.

First result: valid no_answer JSON, 25.875 s, 30 charged calls, 0/31 well-formed
native calls (all page values are strings), no OOM. Partial table is 1/20 with no
D3 verdict. Full report: docs/S20_implementation.md. Remaining 19 episodes and
all later models await the next researcher instruction; do not silently drop Llama.

# S19 - Per-agent metrics (2026-10-17)

- [x] Researcher authorizes S19; inspect scope/callers and save 112 protected hashes.
- [x] Record benchmark and technical-failure decisions before computing scores.
- [x] RED/GREEN degree and percentile cases using the existing S4 fixture.
- [x] Test/implement all §15 answer, bridge, pagination and effort metrics.
- [x] Replay saved S14 and inspect early stop and bridge rank against raw calls.
- [x] Review/mutation, 148 focused/556 full checks, 112 unchanged hashes and stage report.
- [x] Researcher explicitly accepts S19 and its verification evidence (2026-10-17).
- [x] Record that TIMEOUT/ERROR/PARSE_FAIL must not count as answer failures in §16.

# S18 - Label B, reason codes and hop-1 status (2026-10-17)

- [x] Researcher authorizes S18; inspect dependencies/callers and save protected hashes.
- [x] RED/GREEN synthetic Label B and reason-code cases, using S12 utilities.
- [x] Researcher selects simple H1 paths; test/implement H1 without a length cap.
- [x] Replay saved S14 and verify all 21 primary paths directly against raw calls/KG.
- [x] Review; 2 mutations caught/restored, 142 focused/508 full checks, 71 hashes unchanged.
- [x] Save report and complete all-answer inspection table in diagnostics/s18.
- [x] Researcher explicitly authorizes S18 commit/push after the verification report.
- [x] Complete delegated review of all primary paths/labels/codes; accept S18 under the researcher's explicit authorization (2026-10-17).

# S17 - Label A (2026-10-17)

- [x] Researcher authorizes S17 with G_q, UNION coverage and CONSISTENT extra errors.
- [x] Inspect S7/S16 structures/callers and save protected-file identities.
- [x] Write failing tests; implement §6/§13 labels and pass 76 focused checks.
- [x] Replay saved S14: BRIDGE, primary/CONSISTENT, 21 GOLD; hand-check two via TTR.
- [x] Pass all 460 tests, catch/restore deliberate mutation, verify 53 protected files.
- [x] Align runbook S17 wording; save full report, evidence and design choices.
- [x] Researcher accepts S17 and its verification evidence (2026-10-17), and
  explicitly authorizes commit `S17: Label A` and push; decision log updated.

# S16 - answer normalization (2026-10-17)

- [x] Researcher explicitly authorizes starting S16; remote S15 acceptance is preserved.
- [x] Inventory S7 callers and save protected-file hashes and S7 definitions.
- [x] Add failing item tests; implement §12 agent policy; pass 42 item/reference tests.
- [x] Obtain researcher decision: deduplicate identical unresolved submitted pairs only.
- [x] Add seven failing list tests, then implement stable post-resolution deduplication.
- [x] Pass focused tests (49) and demonstrate all 21 S14 answers resolve by ID.
- [x] Complete full sandbox tests (443), review/mutation check and protected-file verification.
- [x] Save stage report and current status in docs/S16_implementation.md and docs/progress.md.
- [x] Researcher accepts S16 behavior and evidence (2026-10-17); exact unresolved
  pairs and literal diagnostic-only mismatch flag recorded in the decision log.
- [ ] S28 pilot report: report unresolved answers that would merge under normalized
  comparison; state the comparison rule and preserve official exact-pair scoring.

# S15 — accepted 2026-10-16

- [x] Researcher reviews exact messages and the 34-entry short-name list (record:
  `results/diagnostics/s15/manual_review_20261016.json` / `.md`).
- [x] Researcher confirms all four overlap rows and approves S15 (decision log 2026-10-16).
- [x] Temporary review handoff removed after approval was recorded.
- [x] Researcher separately instructs S16 implementation (2026-10-17); see above.

# S15 revision 2 — automated verification complete (historical)

- [x] Researcher authorizes the narrow exemption and corrected S14/pilot chronology.
- [x] Confirm no protocol frozen-hash entry and record protected-file identities.
- [x] Amend only protocol §19.1(a); record decision and pre-register split reporting.
- [x] Add synthetic regressions; implement rule-based spans without changing the matcher.
- [x] Pass screening/smoke audit with zero failures and exactly BH2_04007 flagged.
- [x] Pass all-524 scan with zero failures and exactly four specified flags.
- [x] Pass focused 43-test audit and full 401-test sandbox suite; no skips/deselections.
- [x] Preserve old evidence; save versioned results and complete overlap/short-name report.
- [x] Record four per-row overlap decisions under researcher authorization in `results/diagnostics/s15/overlap_review.json`.
- [x] Researcher reviews exact messages and the 34-entry short-name list (done 2026-10-16; see top).

Later reporting requirement (pre-registered here; not implemented during S15):
every §16 metric and §17 comparison uses both all queries and a report excluding
SOURCE_NAME_OVERLAP; official gates continue to use all queries.

# Original S15 strict audit (historical)

- [x] Verify frozen identities and complete screening/smoke evidence (20 + 4 queries).
- [x] Add synthetic audit-detection checks in tests/test_leakage.py; verify injected leaks fail.
- [x] Capture actual runner initial messages without network/model calls or episode saving; check (a) FAILS at BH2_04007.
- [x] Audit agent imports and data reads with source checks and guarded exercised paths; check (b) PASS.
- [x] Validate every line of all four agent sheets; check (c) PASS, 524 rows.
- [x] Compare 10 reproducible real pairs across all pages against PrimeKG index; check (d) PASS, 12 pages/187 neighbors.
- [x] Run focused (25 passed/1 failed) and complete sandbox suites (383 passed/1 failed); no skips/exclusions.
- [x] Save exact example messages, per-check evidence and short-name review list; update stage report.
- [x] Researcher elects to retain strict BH2_04007 failure and decide a remedy later.
- [x] Resolve the strict failure under researcher direction: revision 2 above.
- [x] Carry manual review forward to the revision-2 checklist above.

Dependencies follow the order above; (b), (c) and (d) depend on preflight and
checker regression checks. Checkpoint after (a)-(c): no production behavior or
frozen identity changed. Final checkpoint: automated checks and full suite pass,
manual review status explicit. Detailed scope and failure handling: tasks/plan.md.

# S12 environment verification

## Sandbox-compatible saver follow-up

- [x] Probe Windows rename and collision refusal inside sandbox.
- [x] Add and run failing regression checks before production changes: red transcript saved.
- [x] Implement shared platform-safe publishing and align launcher preflight.
- [x] Pass S12 and launcher checks inside sandbox, including competing writers.
- [x] Pass synthetic persistence probe under actual results/runs inside sandbox.
- [x] Complete sandbox suite: 358 passed, no skips/exclusions; report in docs/S12_sandbox_fix_20261016.md.

## Prior completed host/sandbox comparison

- [x] Reproduce sandbox S12 result: 17 passed, 4 failed at persistence (exit 1).
- [x] Run all 21 unchanged S12 cases on host: 21 passed in 0.38 s (exit 0).
- [x] Run actual results/runs preflight and synthetic save/load/overwrite probe: PASS.
- [x] Run full host suite without skips/exclusions: 352 passed in 12.47 s (exit 0).
- [x] Document procedure and evidence in docs/S12_environment_verification_20261016.md.
