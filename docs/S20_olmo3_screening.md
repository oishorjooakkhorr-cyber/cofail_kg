# S20 OLMo 3 7B Instruct screening complete (2026-10-19)

All 20 frozen queries are saved for `OLMo3-7B` in
`primary-3060ti-20261018`. **This candidate fails D3 on competence (0/20).**
The other four criteria pass. All episode statuses are SUCCESS, which means
valid final JSON, not correct answers. No S21 selection or freeze was made.

## 1. Files created or changed

- This report, `docs/decision_log.md`, `docs/progress.md`, `tasks/plan.md`, `tasks/todo.md`.
- `results/runs/screening/primary-3060ti-20261018/`: one pinned OLMo configuration
  and 20 write-once attempt-1 episode records (ignored by Git).
- `results/diagnostics/screening/`: 20 new metric files and the cumulative table.
- `results/diagnostics/s20/olmo3/`: model metadata, synthetic exchange/placement,
  test log, reused operational helper copies, invocation logs/journal, per-query
  CSV, summary, manual inspections and integrity proofs.
- Graph query memory and reflection sidecars under `graphify-out/`.

No agent, launcher, evaluator, test, prompt, tool schema, frozen configuration,
data or scientific rule changed. No completed outcome was rerun or overwritten.
Existing shortlist/cleanup working changes were preserved. No commit or push.

## 2. Tests and execution results

The unchanged full suite passed **598 tests in 35.69 seconds**, with no skips or
deselections, before official inference. The workspace basetemp was
`.venv/s20-olmo3-pytest-tmp`; host execution avoided the established sandbox
fixture/socket restrictions. The reused helper scripts compile and retain their
identity, order, record-count, status, exit and hash assertions.

Installed model: `olmo-3:7b-instruct`, OLMo developer lineage, 7.3B Q4_K_M,
digest `ea72df8c85d75c6783ab0d00278803c53a634fc9d0fe38d3fd4ab6f35adbdbb2`.
Runtime: Ollama 0.40.4 on the primary RTX 3060 Ti 8 GB host. Capabilities include
completion and tools. Synthetic add(2,3) emitted one native call with exact
integer arguments, then answered 5; neither message contained nonempty thinking.
Identity remained unchanged. The Instruct tag was used, without a Think/default
variant, template alteration or prompt tuning.

Settings (protocol section 9.1): think=false, temperature=0, seed=42,
num_ctx=8192, num_predict=4096, page_size=50, budget=30, episode timeout=600 s,
request timeout=120 s. Every saved record pins source/input identities and
actual timestamps. Experiment ID retains its established date.

Placement: synthetic and all 20 post-invocation samples report
size=6511625501, size_vram=5298192384 bytes and context_length=8192. This is
automatic partial CPU/GPU offload; no placement tuning was applied. Synthetic
GPU usage sampled 7145/8192 MiB. This sample is not a peak measurement or an
exact layer split. The same unchanged placement procedure was used for Ministral.

Executed 20 separate --max-new 1 invocations in frozen order. Every launcher
exited zero and saved exactly one new SUCCESS record. Zero ERROR, TIMEOUT,
PARSE_FAIL or OUT_OF_MEMORY. No identity/hash drift or order discrepancy.
Report-only --max-new 0 then exited zero without inference. All **105** official
run files retained their hashes, including all **84** prior files. All 122
protected identities and 43 pinned source/input hashes match. Proof:
`results/diagnostics/s20/olmo3/official-final-integrity.json`.

| D3 criterion | Observed | Required | Verdict |
|---|---:|---:|---|
| Well-formed / attempted calls | 60/62 (96.7742%) | >=90% | PASS |
| SUCCESS episodes | 20/20 (100%) | >=90% | PASS |
| Competent queries | 0/20 (0%) | >=40% | FAIL |
| Median episode wall time | 8.951106 s | <=300 s | PASS |
| ERROR with OUT_OF_MEMORY | 0 | 0 | PASS |

All 62 attempts were native, with zero TEXT_TOOL_CALL occurrences. There were
61 charged calls, 51 successful KG calls, and six queries with tool use.
BH2_03762 reached the budget (30 charged, 31 emitted) and returned no_answer.
Two calls in that episode omitted required page; they fail well-formedness even
though the existing tool supplies a default. No argument repair was applied.

Eighteen final outputs were no_answer; two answered outputs submitted 12 items.
All 12 evaluate as OFF_QUESTION and PATH_INVALID; there are no SUPPORTED answers.
The earlier progress statement that every final was no_answer was corrected
once final-output inspection identified these two answered records.
Largest prompt_eval_count=8137; no nonempty assistant thinking fields. Median
charged calls=0, budget-hit share=5%, total episode wall=521.773839 s. Individual
values are in `official-per-query.csv`.

## 3. Small real example and output

`BH2_04425` completed SUCCESS in 50.563304 seconds, using five well-formed native
calls and five successful KG lookups. It submitted:

```json
{"status":"answered","answers":[{"id":"22180","name":"Abnormal bleeding"}]}
```

The evaluator labels this item OFF_QUESTION and PATH_INVALID. The stored output
is a model prediction, not an endorsed biomedical answer. Valid JSON and
successful lookups do not establish a supported, question-valid two-hop answer.

## 4. Assumptions

The request authorizes the complete S20 block for this named downloaded candidate
using the established primary-host procedure. It adds a measurement while
preserving original candidate history and all saved outcomes; it does not decide
pool replacements, D3 round assignment or the S21 panel. Automatic offload is
recorded under the prior unchanged procedure, without adding a scientific rule.
No scientific ambiguity required a decision during this block.

## 5. Design choices beyond the specification

Routine engineering only: reused the preceding candidate's preflight, per-query
supervisor and summary helpers with OLMo tag/digest, agent/family and output
paths. Kept agent ID `OLMo3-7B` and the existing experiment ID. Added no library,
new experimental setting, threshold, heuristic or literature method. Selected
inspection examples to cover immediate abstention, useful tool calls followed
by no_answer, budget exhaustion, and the two invalid answered outputs.

## 6. Items for manual inspection

- `BH2_00461`: immediate no_answer, no tools, 3.081708 s.
- `BH2_03434`: eight well-formed native calls; seven successful lookups,
  a guessed unavailable relation, then no_answer.
- `BH2_03762`: 234.321083 s; 31 emitted calls, two missing page, budget reached,
  largest prompt 8137, then no_answer.
- `BH2_03991`: 11 phenotype items submitted after a first-hop disease lookup;
  all OFF_QUESTION/PATH_INVALID. Inspect the unavailable second-page request.
- `BH2_04425`: the one-item answered example above; inspect the second-hop
  neighbor type and relation choices.

These records, questions, call sequences, outputs and labels are collected in
`official-manual-inspection.json`. Original records remain write-once. This
completes only the requested candidate. No 16K follow-up, other model or S21 work.
