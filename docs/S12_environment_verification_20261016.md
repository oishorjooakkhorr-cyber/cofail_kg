# S12 execution environment verification — 2026-10-16

Historical pre-fix comparison. The subsequent Windows publication fix and sandbox
verification in `S12_sandbox_fix_20261016.md` supersede the host-only recommendation
below. Original evidence is preserved.

Fresh verification confirms that the unchanged S12 saver works on the Windows
host and remains blocked by the restricted sandbox. Use approved host execution
for persistence tests and experiments. This does not change sandbox permissions.

## Plan and outcome

| Check | Result | Evidence in results/diagnostics/ |
| --- | --- | --- |
| Sandbox S12 with fresh workspace temp root | 17 passed, 4 failed, exit 1 | s12_environment_20261016b_sandbox.txt |
| Host S12, normal pytest temporary paths | 21 passed in 0.38 s, exit 0 | s12_environment_20261016b_host_trace.txt |
| Actual results/runs synthetic persistence probe | All assertions passed, exit 0 | s12_environment_20261016b_host_probe.json |
| Complete host suite, no skips/exclusions | 352 passed in 12.47 s, exit 0 | s12_environment_20261016b_host_suite.txt |

All commands used the project's `.venv/Scripts/python.exe`. Host commands ran
through approved execution outside the sandbox, without administrator-specific
configuration changes. No application code, test, frozen configuration or
protocol was changed. No model call, commit or push was made.

## Failure localized

The sandbox still denies `os.link(temporary, final)` in trace.py with WinError 5.
The four failures are saving/overwrite refusal, competing-writer refusal,
reconstruction round trip, and the isolation subprocess (which also saves).
Moving pytest temporary files into the workspace does not resolve hard-link
permissions. The same tests all pass outside the sandbox.

The unchanged trace.py SHA256 is
`5d71e12a2b68cc18390448e0072ab61935acfb5bee9872096a8a724eee9b45fd`.
The saver must continue to publish complete records and refuse overwrites
(protocol §19); no fallback or weaker write behavior was introduced.

## Actual output-directory example

The existing `scripts/14_run_episode.py` `check_persistence` function passed under
actual `results/runs`: hard-link identity was verified and an existing target
was refused. The script's main/model execution was not invoked.

Using the existing test fixture, a synthetic record with `1 -r-> 2` was saved in
a disposable subdirectory of `results/runs`, loaded and reconstructed, and checked
for exact equality. A second save raised FileExistsError and original bytes were
unchanged. The disposable directory was cleaned up. Existing episode records
were not modified. Evidence JSON retains the synthetic record hash and outcomes;
the temporary record is not an experimental episode.

## Procedure for subsequent runs

In a normal PowerShell terminal, from the project directory:

```powershell
.\.venv\Scripts\python.exe -m pytest tests/test_trace.py -q --tb=short
.\.venv\Scripts\python.exe -m pytest -q --tb=short
```

Within Codex, use approved execution outside the sandbox for these commands.
An approval applies to the requested execution; it does not permanently remove
sandbox restrictions or establish that future default commands are on the host.

Before inference, run persistence checks in the actual output directory and
execution environment. The existing S14 launcher already does this before
constructing the model client. Future experimental launchers should retain an
equivalent guard; those later stages were not implemented here. Changing folders,
drives or execution environments requires rechecking persistence.

## Scope and manual inspection

Created plan/checklist, raw diagnostic evidence and this report; added a progress
note. No scientific decisions or literature methods were selected. Routine
engineering choices: workspace temp root to isolate sandbox failure, existing
synthetic fixtures for the real-directory probe, and ordinary host pytest runs.

Inspect the report/evidence and use host execution for future runs. The sandbox
failure is a known remaining environment limitation, not a newly passing check.
S15 and later stages were not started; no real model episode was rerun.
