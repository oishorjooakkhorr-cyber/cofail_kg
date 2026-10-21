# S20 Command R7B screening — 2026-10-21

**All twenty frozen queries completed at the original 8K settings. D3 FAIL:
no tool attempts and zero competent queries.** Nineteen episodes parsed valid
final JSON; one retained PARSE_FAIL. Valid JSON is not evidence of correctness.

## 1. Files created or changed

- `results/runs/screening/command-r7b-3060ti-20261021/`: one immutable model
  configuration and twenty unique attempt-1 episode records.
- `results/diagnostics/screening/command-r7b-3060ti-20261021/`: twenty evaluator
  metric files; the cumulative `screening_table.csv` now includes this candidate.
- `results/diagnostics/s20/command-r7b-20261021/`: execution policy, baseline
  hashes, focused tests, synthetic response and failed-check log, identity and
  runtime evidence, official/offline console and exit codes, per-query CSV,
  summary, manual-inspection extracts and final integrity proof.
- This report, shared screening status, progress, plan, checklist and decision log.

Production scripts/source, tests, configs, frozen rules, prompts, tools, inputs
and existing episode/metric evidence were preserved. No commit or push.

## 2. Tests, execution and results

The researcher explicitly requested the whole S20 test, all twenty queries,
for the newly downloaded `command-r7b:7b`. The unchanged
`scripts/20_screen_models.py --max-new 20` ran the complete block sequentially,
checkpointing every final status without retrying completed failures.

Installed identity: Cohere, Q4_K_M, metadata parameter size **8.0B** despite
the `7b` tag; digest
`ff4e9696ef9f19b62e3f7d7261c95dcc9bb15a7c0398493366d851119fe2e1ef`.
The recorded agent ID is `CommandR7B-7B`; it does not replace parameter metadata.
Ollama advertises completion and native tools. The synthetic add-tool check
failed behaviorally: the model stated the result without emitting a tool call.
The valid HTTP response and failed assertion are retained. The full requested
block proceeded unchanged to measure this behavior; no extra synthetic-use
acceptance threshold was added to D3 and no prompt/template repair was attempted.

Settings: think=false, temperature=0, seed=42, num_ctx=8192, num_predict=4096,
page_size=50, budget=30, episode timeout=600 s, request timeout=120 s.
Preflight and during-run samples verify the digest and actual context=8192
on RTX 3060 Ti 8 GB; size=size_vram=5,642,230,169 bytes. Sampled total GPU
usage was 6882/6887 MiB; these are samples, not a peak-memory measurement.

Inference ran 12:09:29–12:10:43 Asia/Dhaka on 2026-10-21 (about 74.3 seconds
from first episode start to last finish, including inter-episode work).

| D3 criterion | Required | Observed | Result |
|---|---:|---:|---|
| Well-formed / attempted calls | >=90% | 0/0, undefined | FAIL |
| SUCCESS | >=90% | 19/20 = 95% | PASS |
| Competent queries | >=40% | 0/20 = 0% | FAIL |
| Median episode wall time | <=300 s | 2.889849 s | PASS |
| ERROR/OUT_OF_MEMORY | 0 | 0 | PASS |
| **Overall** | All five pass | | **FAIL** |

Zero attempts does not count as 100% call validity. There were zero native
calls, TEXT_TOOL_CALL events, charged KG calls, budget hits or nonempty thinking
messages. No ERROR or TIMEOUT occurred. Largest prompt_eval_count=2292.
Sixteen parsed outputs were `no_answer`; one was `answered` with an empty
answer list; the other two submitted one item each. One was
OFF_QUESTION/UNGROUNDED; the other UNRESOLVED/NOT_APPLICABLE.
Neither supplied a question-valid SUPPORTED answer.

Verification: **42 screening tests passed in 2.31 s**. Official and offline
report-only invocations exited zero; offline reporting reproduced the same
row without inference. All 512 baseline source/input/test/configuration and
historical evidence hashes match, including all 43 pinned source/input files.
All 21 new configuration/episode hashes match across offline reporting;
all eight prior screening rows remain identical. Query IDs are exactly the
twenty manifest IDs in order, with sequential timestamps and attempt=1.
Before the researcher-requested commit/push, the unchanged full suite also
passed: **598 tests in 47.92 s**, with output in `precommit-tests.txt`.

## 3. One small real example and output

BH2_02033 completed SUCCESS in 2.690555 seconds, without any KG calls:

```json
{"status":"answered","answers":[{"id":"19601","name":"MYO-029"}]}
```

The evaluator labels this item OFF_QUESTION/UNGROUNDED; competence remains zero.
BH2_00461 instead returned an array containing a no_answer object, which the
unchanged parser rejected. Its PARSE_FAIL remains in the denominator.

## 4. Assumptions

The explicit request authorizes this candidate's full original S20 block.
The original protocol section 9.1 8K settings apply: earlier 16K amendments
were candidate-specific reassessments. No new context amendment was inferred.
Existing frozen queries, P1/T1, evaluators and D3 thresholds apply unchanged.

## 5. Design choices beyond the specification

Routine engineering: an isolated dated run ID and diagnostics directory,
explicit Cohere family label, reuse of existing launcher/preflight/summary
code, baseline and post-report hash checks, and sampled runtime evidence.
No new scientific method or threshold was introduced. D3 round accounting
remains a researcher decision; this report does not assign a round or select
the S21 panel. Three candidates currently pass; a fourth is still required.

## 6. Manual inspection

Inspect `official-summary.json`, `official-per-query.csv` and
`official-manual-inspection.json` in the diagnostic directory. In the raw
records, inspect BH2_00461's array-shaped final output, BH2_02033's ungrounded
answer and BH2_05843's unresolved Ristocetin item. The synthetic response and
all twenty traces document absence of native tool use under these settings;
they do not establish inability under every possible prompt or runtime.
