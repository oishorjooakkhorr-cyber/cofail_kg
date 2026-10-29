**Separate new-host follow-up (2026-10-29):** Fresh RTX 5060 Ti / Ollama 0.40.12
16K block passes D3: 20 SUCCESS, 16 competent, no read timeouts.
[New-host report](S20_granite41_5060ti_16k.md). All historical outcomes and
the stopped block's incomplete status below remain unchanged.

# S20 Granite 4.1 8B screening complete (2026-10-21)

All twenty frozen screening queries completed for `ibm/granite4.1:8b`.
**Granite41-8B passes all five D3 criteria at the original 8K settings.**
All twenty outcomes are SUCCESS; there were no ERROR, TIMEOUT or PARSE_FAIL
episodes. SUCCESS means valid final JSON, not necessarily a correct answer.

## 1. Files created or changed

- This report.
- `results/runs/screening/primary-3060ti-20261018/`: a pinned
  `Granite41-8B.config.json` and twenty immutable attempt-1 episode records.
- `results/diagnostics/screening/primary-3060ti-20261018/`: twenty new
  Granite41-8B metric files; the cumulative `screening_table.csv` now includes
  this candidate. Its seven earlier rows are unchanged.
- `results/diagnostics/s20/granite41-20261021/`: preflight, execution policy,
  manifest, console, runtime sample, summary, per-query CSV, inspection examples,
  offline report and final integrity proof.

No production source, evaluator, test, prompt, schema, data or frozen setting
changed. No completed episode was rerun or overwritten. No commit or push.

## 2. Tests and execution results

The unchanged screening tests passed: **42 passed in 6.38 seconds**. Synthetic
native `add(2, 3)` produced integer arguments and result 5, with thinking disabled.
The full production suite was not repeated; all 43 pinned source/input hashes
match the earlier tested implementation.

| D3 criterion | Observed | Required | Verdict |
|---|---:|---:|---|
| Well-formed / attempted calls | 217/217 (100%) | >=90% | PASS |
| SUCCESS episodes | 20/20 (100%) | >=90% | PASS |
| Competent queries | 14/20 (70%) | >=40% | PASS |
| Median episode wall time | 61.3250475 s | <=300 s | PASS |
| ERROR with OUT_OF_MEMORY | 0 | 0 | PASS |

All 217 attempts were native; there were no TEXT_TOOL_CALL events or nonempty
thinking messages. Competence means at least one supported, question-valid
answer on a query, with all twenty queries in the denominator. It is not
answer-level accuracy or exhaustive recall. The 568 submitted answer items
include 508 GOLD/SUPPORTED, 17 ALT_VALID/SUPPORTED and 43
OFF_QUESTION/PATH_INVALID. Median charged calls were 9.5; two queries reached
the tool budget. Largest recorded prompt was 8,187 tokens.

Ollama 0.40.4 ran on the primary RTX 3060 Ti 8 GB host. Identity: 8.8B Q4_K_M,
digest `444af1c4b2fedd6b54041aca558e7300b0b3d5c0468c44619126240323ba2852`.
Settings: think=false, temperature=0, seed=42, num_ctx=8192, num_predict=4096,
page_size=50, budget=30, episode timeout=600 s, request timeout=120 s.
Placement samples reported size=6,862,195,914 and size_vram=6,268,114,697 bytes,
consistent with partial CPU/GPU offload; these are samples, not peak memory.

The twenty episodes ran sequentially from 09:33:32 to 09:57:25 Asia/Dhaka on
2026-10-21, about 23.88 minutes. The full invocation and offline `--max-new 0`
report each exited zero. The offline report reproduced the D3 result without
inference. Final checks confirmed exactly twenty unique attempt-1 episodes in
frozen order, sequential timestamps, unchanged hashes for all 21 new run/config
files, 359 existing result/metric files, 43 source/input pins and 122 protected
identities. See `final-integrity.json` in the diagnostic directory.

## 3. Small real example

BH2_02033 returned all three benchmark answers, evaluated GOLD/SUPPORTED:

```json
{"status":"answered","answers":[{"id":"31332","name":"myostatin-related muscle hypertrophy"},{"id":"36432","name":"congestive heart failure"},{"id":"37659","name":"heart failure"}]}
```

## 4. Assumptions

The user's request authorizes this candidate's complete original S20 block and
continuation after any saved query error. The 16K blocks for other candidates
remain separate reassessments. No S21 model selection or configuration freeze
is implied by this passing result.

## 5. Design choices beyond the specification

Routine engineering: reuse the existing launcher with `--max-new 20` and its
all-status checkpoint/resume behavior, bypassing older wrappers' extra
stop-on-error rules; use the established run ID with a distinct agent ID;
isolate new diagnostics; reuse the existing Granite summary helper with the
candidate and output-directory substitutions; retain preflight/hash evidence
and verify reporting offline. No new scientific gate or literature method.

## 6. Manual inspection and limits

Inspect `official-per-query.csv`, `official-manual-inspection.json` and raw
episode traces in the diagnostic/run directories. Six queries did not meet the
competence definition despite valid final JSON, and 43 submitted items were
off-question with invalid support. The largest prompt approaches the 8K cap;
16K behavior and peak memory were not tested. No further model run or S21 work
was performed.
