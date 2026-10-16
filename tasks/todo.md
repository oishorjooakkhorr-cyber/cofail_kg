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
