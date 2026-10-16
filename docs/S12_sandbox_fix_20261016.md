# S12 sandbox persistence fix — 2026-10-16

The four original S12 persistence failures now pass in the restricted Windows
sandbox. Complete sandbox suite: **358 passed in 13.56 s**, no skips/exclusions.
The actual results/runs synthetic probe also passes. No host execution or model
calls were used for this fix's verification.

## 1. Files and implementation

- `src/cofail_kg/agents/trace.py`: shared `publish_once` uses `os.rename` on Windows
  and retains `os.link` elsewhere. Saver still validates/reconstructs, serializes
  completely, flushes/fsyncs a same-directory temporary file, refuses overwrites
  even with competing writers, and cleans temporary files.
- `scripts/14_run_episode.py`: preflight uses the same publisher, verifies flushed
  publication and collision refusal with original-content preservation, and stops
  before model construction on filesystem errors. It unlinks the source name
  before creating the collision candidate, avoiding mutation of a linked target
  on POSIX. Permission and disk errors retain their chained cause.
- `tests/test_trace.py`, `tests/test_run_episode_script.py`: retain prior checks;
  make fault injection target publication rather than a particular OS primitive;
  add platform dispatch, unavailable-hard-link, concurrent-writer, unsafe-preflight
  and generic-filesystem-error cases. Prior persistence tests still perform real
  saving; no tests were skipped or removed.
- README, progress, tasks/plan.md and tasks/todo.md document the supported procedure.
- Diagnostic transcripts and JSON below preserve the red/green evidence.

Protocol, frozen configuration, prompts, record format, filenames and existing
episode records were not changed. No commit or push was made.

## 2. Plan and test evidence

Plan: probe safe Windows rename; add failing checks; change the shared publisher
and preflight; run focused and complete sandbox tests; probe actual results/runs.
The completed plan/checklist are in `tasks/`.

Evidence files under `results/diagnostics/`:

| Run | Result | File |
| --- | --- | --- |
| Tests first, old production code | 13 failed, 20 passed; original hard-link failures reproduced and new checks not yet implemented | s12_sandbox_fix_20261016_red.txt |
| First implementation, S12 + launcher | 33 passed in 2.08 s | s12_sandbox_fix_20261016_focused.txt |
| Final implementation, entire suite | 358 passed in 13.56 s, exit 0 | s12_sandbox_fix_20261016_suite.txt |
| Final actual-output-folder probe | All assertions passed, exit 0 | s12_sandbox_fix_20261016_probe.json |

The full suite includes six additional cases over the prior 352-pass host suite.
It includes all original four failures, path/reconstruction checks, fsync and
publication error cleanup, refusal despite a bypassed existence precheck, and
two savers synchronized immediately before real OS publication: exactly one
succeeds, one receives FileExistsError, only one complete valid record remains.

All pytest commands used `.venv/Scripts/python.exe -m pytest` with `-q --tb=short`
and distinct workspace `--basetemp=.pytest_cache/s12-fix-...-20261016` paths. The
default sandbox temp-directory restriction is independent of publication; the
workspace temp root resolves that fixture obstacle without skipping tests.

Final full-suite command:

```powershell
.\.venv\Scripts\python.exe -m pytest -q --tb=short --basetemp=.pytest_cache/s12-fix-suite-20261016
```

Use a new basetemp directory for later runs; pytest clears an existing one.

## 3. Actual-folder example

In a disposable subdirectory under actual `results/runs`, a synthetic tool result
`1 -r-> 2` was saved, loaded and reconstructed exactly. A repeated save was
refused and original bytes preserved. No temporary files remained; the disposable
directory was cleaned. Existing records were not modified. The actual launcher
preflight also passed, without invoking its main/model execution.

## 4. Assumptions and scope

This is an engineering fix preserving protocol §19 behavior, not a scientific
change. Tests run only in the current Windows sandbox as requested. No real model
episode, Ollama connectivity check, Linux/macOS live execution, power-cut test,
network-filesystem test or administrator/sandbox-policy change was performed.

## 5. Engineering choices and sources

Windows rename removes the hard-link requirement. Python documents refusal of
existing destinations on Windows, but permits replacement on Unix; the latter
therefore retains the existing safe link operation. The temporary and final files
stay in the same directory. There is no copy-to-final or overwrite-capable replace
fallback. The non-Windows dispatcher is unit-tested; live POSIX behavior was not
verified in this Windows environment.

Primary source: [Python os.rename](https://docs.python.org/3/library/os.html#os.rename).
Same-directory Windows rename is an OS namespace operation, not a staged content
copy. Unsupported operations remain visible failures, caught by preflight before
inference when present at preflight time. No new dependency or literature method.

## 6. Manual inspection and future runs

Review the small production diff, concurrency/error checks and raw evidence.
Retain the preflight in later launchers: changing output folders/filesystems or
permissions requires testing that environment. Other platforms still need hard-link
support. This removes the verified Windows hard-link failure, not every possible
future disk, permission, hardware or power-loss failure. A preflight cannot ensure
the disk stays writable or has enough space for an entire subsequent experiment.

Earlier host-only recommendations and hard-link-only descriptions in dated reports
describe the pre-fix implementation; this report and README supersede that advice.
