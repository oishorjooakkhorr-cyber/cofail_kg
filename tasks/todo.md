# S15 revision 2 — automated verification complete

- [x] Researcher authorizes the narrow exemption and corrected S14/pilot chronology.
- [x] Confirm no protocol frozen-hash entry and record protected-file identities.
- [x] Amend only protocol §19.1(a); record decision and pre-register split reporting.
- [x] Add synthetic regressions; implement rule-based spans without changing the matcher.
- [x] Pass screening/smoke audit with zero failures and exactly BH2_04007 flagged.
- [x] Pass all-524 scan with zero failures and exactly four specified flags.
- [x] Pass focused 43-test audit and full 401-test sandbox suite; no skips/deselections.
- [x] Preserve old evidence; save versioned results and complete overlap/short-name report.
- [ ] Researcher reviews exact messages, four overlap cases and the 34-entry short-name list.

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
