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
