# S20 Granite 3.3 8B screening complete (2026-10-19)

All 20 frozen queries are saved for `Granite33-8B` in
`primary-3060ti-20261018`. **This candidate fails D3** on tool well-formedness
and competence. Three candidates have now been screened; six planned candidates
remain unrun. The S20 pool is incomplete and no S21 selection has been made.

## 1. Files created or changed

- `docs/decision_log.md`: authorization, preflight and final evidence.
- This report, `docs/progress.md`, `tasks/plan.md`, and `tasks/todo.md`.
- `results/runs/screening/primary-3060ti-20261018/`: one new pinned Granite
  configuration and 20 write-once episode records, attempt 1.
- `results/diagnostics/screening/`: 20 new Granite metric files and the
  cumulative `screening_table.csv`.
- `results/diagnostics/s20/granite33/`: metadata, synthetic exchange, test log,
  GPU evidence, invocation logs/journal, integrity proofs, per-query CSV,
  summary, inspection examples and copies of the operational helpers.

No agent, launcher, evaluator, prompt, tool schema, test, frozen configuration,
data or scientific rule was changed. No commit or push was performed.

## 2. Tests and execution results

The unchanged full suite passed **598 tests in 43.55 seconds**, with no skips
or deselections, before official inference. Synthetic native `add(2,3)` emitted
one tool call with integer arguments and then answered 5. Neither response
contained a nonempty thinking field; identity stayed unchanged.

Installed model: `granite3.3:8b`, Granite lineage, 8.2B, Q4_K_M, digest
`fd429f23b90980ed1bef53b990894e7b0199331f6ae90c5650240a7d5b70f1f7`.
Runtime: Ollama 0.40.4 on the primary RTX 3060 Ti 8 GB host. The local server
was initially stopped and was started using the installed executable and
`D:\Models`. Its load log confirms **41/41 layers on GPU**. Synthetic `/api/ps`
reports `size=size_vram=6403905289` bytes at context 8192; GPU usage sampled
7404 MiB of 8192 MiB. Post-invocation placement samples are retained.

Settings: think=false, temperature=0, seed=42, num_ctx=8192, num_predict=4096,
page_size=50, budget=30, episode timeout=600 seconds, request timeout=120 seconds.

Executed 20 separate `--max-new 1` invocations in frozen order. Every launcher
exited zero and saved exactly one new episode. Identity, status, prior-file
hashes, 122 protected identities and 43 pinned source/input hashes were checked
between invocations. No ERROR, nonzero exit, drift or order discrepancy occurred.
No outcome was rerun or overwritten. All 20 statuses are SUCCESS; TIMEOUT,
PARSE_FAIL, ERROR and OUT_OF_MEMORY counts are zero.

After completion, `--max-new 0` exited zero without inference. All **63**
official run files retained their hashes, including all 42 prior Llama/Qwen
files. Protected/pinned hashes also match. Proof:
`results/diagnostics/s20/granite33/official-final-integrity.json`.

| D3 criterion | Observed | Required | Verdict |
|---|---:|---:|---|
| Well-formed / attempted calls | 0/8 (0%) | >=90% | FAIL |
| SUCCESS episodes | 20/20 (100%) | >=90% | PASS |
| Competent queries | 0/20 (0%) | >=40% | FAIL |
| Median episode wall time | 13.597764 s | <=300 s | PASS |
| ERROR with OUT_OF_MEMORY | 0 | 0 | PASS |

SUCCESS means final-answer parsing succeeded under the existing parser,
including its code-fence handling; it does not establish answer correctness.
There were **zero native tool calls**, eight logged TEXT_TOOL_CALL occurrences,
zero charged KG calls and zero supported answers. Text tool calls were never
executed. D3's attempted-call count follows those logged occurrences; it is not
a count of every tool-like block within each message.

The model submitted 69 answer items: 53 OFF_QUESTION, 15 UNRESOLVED and one GOLD.
All 54 resolved items are UNGROUNDED; the 15 unresolved items are NOT_APPLICABLE.
The GOLD item therefore does not establish D3 competence. Sixteen final outputs
have status answered, four no_answer; one answered output has an empty list.
Largest prompt_eval_count=3546; no nonempty assistant thinking field was recorded.
Total episode wall time=346.642073 seconds; median charged calls and budget-hit
share are both zero. Per-query values are in `official-per-query.csv`.

## 3. Small real example and output

`BH2_00461` completed in 13.901365 seconds. Granite wrote several `<tool>`
blocks as text, received no KG result, and then submitted these IDs:

```json
{"status":"answered","answers":[{"id":"1783","name":"Phenylketonuria"},{"id":"29497","name":"Tyrosinemia type I"},{"id":"29498","name":"Tyrosinemia type II"},{"id":"29499","name":"Tyrosinemia type III"}]}
```

All four evaluate as OFF_QUESTION and UNGROUNDED. The record's SUCCESS status
reflects the parsed final JSON after the existing re-prompt, with zero native
calls and an empty KG call log. This is a stored model output, not a factual
biomedical answer endorsed by the evaluator.

## 4. Assumptions

The latest request authorizes this planned candidate's complete S20 block using
the established primary-host procedure. The existing experiment ID remains
`primary-3060ti-20261018`; its date names the experiment, while these new records
carry their actual 2026-10-19 timestamps. Scientific rules, strict schema types,
denominators and thresholds remain those already frozen. Model tool behavior
was measured without a template, prompt or argument-coercion adjustment.

## 5. Design choices beyond the specification

Routine engineering: reused the preceding candidate's operational helpers with
Granite identity/output paths; one unchanged launcher invocation per episode;
saved logs, placement samples and hash checks between invocations. Reused the
established agent-ID convention (`Granite33-8B`) and existing experiment ID.
The project agent/launcher/evaluator were not patched. No literature method or
new scientific threshold was introduced.

## 6. Items for manual inspection

- `BH2_00461`: text tool blocks and four ungrounded final answers despite the
  successful synthetic tool preflight.
- `BH2_03762`: fabricated suffixed IDs; name fallback resolves Edema to node
  22262, yielding GOLD but UNGROUNDED without any executed KG call. Inspect the
  difference between a benchmark match and supported competence.
- `BH2_03850`: longest episode and largest prompt; ten placeholder
  `side_effect_*` answers, all UNRESOLVED.

Raw messages, final outputs, call logs and labels for these three records are
collected in `official-focused-inspection.json`. Original records remain in the
screening run directory. No other candidate or S21 work was run.
