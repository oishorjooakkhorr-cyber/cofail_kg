# S20 checkpoint: launcher and first Llama episode (2026-10-18)

This is a first-episode checkpoint, not completed model screening or S20
acceptance. The researcher authorized implementation and exactly one official
episode after reviewing the Llama metadata and synthetic checks. No S21 choice,
remaining screening episode, commit or push was performed.

## 1. Files created or changed

- `scripts/20_screen_models.py`: explicit candidate identity, frozen S20 settings,
  write-once run/source/input manifest, preflight, bounded sequential execution,
  resume and cumulative screening-table output. Defaults to one new episode.
- `src/cofail_kg/evaluation/screening.py`: D3 native/text call accounting and
  per-model aggregation. Scientific answer/path/effort evaluation reuses S16-S19.
- `tests/test_screening.py`: 42 synthetic cases, with mocked inference/transport.
- `docs/decision_log.md`, `docs/progress.md`, `tasks/plan.md`, `tasks/todo.md`:
  pre-screening decisions, authorized scope, evidence and checkpoint status.
- `results/diagnostics/screening/screening_table.csv`: 1/20 Llama episodes;
  complete=false and all D3 criterion/final verdict fields undefined.
- `results/diagnostics/screening/primary-3060ti-20261018/`: complete S19 metric row.
- `results/diagnostics/s20/`: hashes, RED/GREEN/full-suite evidence, unchanged S14
  evaluator replay, live model/GPU evidence, console logs and resume proof.
- `results/runs/screening/primary-3060ti-20261018/`: immutable per-model run
  configuration and the single complete episode (ignored by Git).

Existing agents, prompts, schemas, S16-S19 evaluators, tests, science files,
configs and data were not modified. All 122 protected identities are unchanged.

## 2. Tests and review

- Baseline: 556 passed in 33.69 seconds.
- Initial new-test RED: missing screening module; captured in diagnostics/s20/red.txt.
- Initial GREEN: 20 passed. Added adversarial edge cases exposed two malformed
  function-name failures, then a saved-record/query-name mismatch. These were
  corrected before any official inference; RED evidence retained.
- Final full suite: **598 passed in 30.72 seconds**, no skips/deselections
  (556 existing + 42 new).
- Saved S14 replay through the new evaluator loading path: 21 answers, benchmark
  precision=1 and recall=1; no new model call.
- `git diff --check`: clean. New code reviewed for D3 definitions, JSON/schema
  types, all-status resume, partial-run reporting, source/identity pinning,
  agent/evaluator separation and atomic persistence.

The initial default pytest temporary-directory setup failed in the sandbox
(416 passed, 140 setup errors). The unchanged baseline and final suite pass with
pytest's base temporary directory explicitly inside ignored workspace `.venv/`.
No existing test was removed, weakened or skipped to resolve this environment issue.

## 3. One real example and its output

Run: `primary-3060ti-20261018`; agent: `Llama31-8B`;
query: `BH2_00461` (first frozen screening-sheet row).

Model: `llama3.1:8b`, 8.0B, Q4_K_M, digest
`46e0c10c039e019119339687c3c1757cc81b9da49709a3b3924863ba87ca666e`.
Identity checked before and after inference. Runtime: Ollama 0.40.4 on the same
RTX 3060 Ti 8 GB host. Sandbox socket access is denied; host metadata access was
verified before the official episode, so no known-failing sandbox episode was created.

Settings: think=false; temperature=0; seed=42; num_ctx=8192; num_predict=4096;
page_size=50; budget=30; episode timeout=600 s; existing request timeout=120 s.
Approved frozen P1/T1 and input hashes were checked before inference.

Episode timestamps: 2026-10-18 08:14:22.200085 to 08:14:48.075252 UTC
(14:14:22 to 14:14:48 Asia/Dhaka), **25.875167 seconds**.

Final output:

```json
{"status": "no_answer", "answers": []}
```

Episode status is SUCCESS because valid final JSON was parsed. This does not mean
that the biomedical question was answered correctly.

| Observation | Value |
|---|---|
| Native calls emitted | 31, all get_neighbors |
| Well-formed / attempted calls | 0/31 |
| TEXT_TOOL_CALL occurrences | 0 |
| Charged calls | 30, budget reached |
| KG error replies / exhausted-budget replies | 30 / 1 |
| Successful KG calls / explored valid bridges | 0 / 0 |
| Submitted answers / competent queries | 0 / 0 |
| Largest prompt_eval_count | 2071 |
| OUT_OF_MEMORY episodes | 0 |
| Thinking fields / recorded policy | 0 / false |

Manual inspection: Llama never called inspect_entity. It guessed relation names
such as associated_with, target_of and treats, received explicit unknown-relation
errors, and repeated guesses until the budget was exhausted. All 31 emitted calls
also supplied page as the string "1", which violates T1's integer schema. Unknown
KG relations are tool errors; the wrong page type is why these calls fail D3's
well-formedness definition. Values were neither coerced nor repaired.

During-episode /api/ps sample: context_length=8192, size=size_vram=5821169663
bytes, consistent with 100% GPU residency. nvidia-smi at that sample showed
6687 MiB total GPU usage; this is a sample, not a measured peak. 16K is untested.

Report-only resume (`--max-new 0`) succeeded in the sandbox without contacting
Ollama. Exactly one episode still exists; episode/config hashes are identical
before and after. Episode SHA256:
`36a51907078f857fe75aeb25a0defa71c620d53405fdc138aa95e0f49cdea051`.

## 4. Assumptions

- Today's "go on" authorizes the previously offered launcher and first episode,
  not the other 19 or a final model choice. Stop at this checkpoint.
- The eight-model pool is planned; only Llama has current inference approval.
- Synthetic add-tool success establishes basic integration, not biomedical
  competence or adherence to the two actual KG-tool schemas.
- No result-dependent prompt, template, parameter or candidate changes are allowed.

## 5. Engineering choices beyond the specification

All are routine engineering, not new literature methods or scientific criteria:

- `--max-new` defaults to 1; 0 is offline report-only. The control limits work,
  never changes a query or overwrites a saved final status.
- Run/agent IDs are explicit. Candidate manifests pin identities, all generation
  settings, source/input hashes and the current commit plus dirty marker. The
  working tree remains uncommitted as required; source hashes identify its bytes.
- Identity is checked before/after each new episode; every existing final record
  is validated before any new inference. Source/input drift blocks resume/report
  rather than silently mixing experiments. Later changes require explicit review.
- D3 well-formedness counts emitted native messages, including malformed or
  unexecuted calls, not only successfully dispatched tool calls. Schema required
  fields and declared types are checked without coercion; extra arguments are not
  rejected because the frozen schema does not forbid them. Recorded TEXT_TOOL_CALL
  events contribute to attempted calls. Zero attempts yields an undefined ratio
  and cannot pass the well-formed-call criterion on a complete set.
- Partial tables expose observed quantities with completed/expected counts;
  criterion/final verdicts stay undefined until all 20 queries are saved.
- Per-episode metrics and run configs are write-once; the derived CSV is replaced
  atomically. Evaluator references are loaded after inference and never passed to
  the agent runner. No section 16 co-failure calculation was added.

## 6. Manual inspection and next checkpoint

Read the first three call/result pairs, repeated relation guesses, page argument
types, the exhausted-budget reply and final no_answer JSON in the saved record.
The partial table must not be interpreted as a final D3 failure or used to drop
Llama. The next proposed work is its remaining 19 unchanged screening queries,
after the researcher reviews this checkpoint. No fixes, rerun, candidate swap,
S21 freeze, commit or push has been performed.
