# S20 Gemma 4 E4B screening complete (2026-10-20)

**Follow-up (2026-10-20):** Gemma subsequently passed a complete fresh twenty-query 16K D3 reassessment (19 SUCCESS, 14 competent). The original 8K FAIL below remains historical evidence. See [full 16K reassessment](S20_full_16k_reassessment.md).

All **20 frozen queries completed uninterrupted in one launcher invocation**, as explicitly requested by the researcher. **Gemma4-E4B fails D3 only on SUCCESS rate: 16/20 (80%), below 90%.** The other four criteria pass. The four PARSE_FAIL outcomes remain in the denominator, with no reruns or replacements.

## 1. Files created or changed

- `results/runs/screening/primary-3060ti-20261018/`: pinned `Gemma4-E4B.config.json` and twenty write-once attempt-1 records (ignored by Git).
- `results/diagnostics/screening/`: twenty new per-query metric files and the cumulative `screening_table.csv`.
- `results/diagnostics/s20/gemma4-e4b/`: baseline hashes, model/show and runtime metadata, reused synthetic preflight and summary helpers, full-suite log, synthetic responses, GPU samples, official console/exit, report-only console/exit, per-query CSV, summary, manual inspection, parse-failure inspection and final integrity proof.
- This report, `docs/decision_log.md`, `docs/progress.md`, `tasks/plan.md` and `tasks/todo.md`.

Existing production source, launcher, evaluator, tests, prompts, tool schemas, data, frozen configurations and scientific rules were unchanged. Prior working-tree changes were preserved.

## 2. Tests and execution results

Unchanged full suite: **598 passed in 38.36 seconds**, with no skips or deselections. The existing OLMo synthetic preflight and summary helpers were reused with candidate/path substitutions; both compile, and their existing assertions passed. Synthetic native `add(2,3)` emitted exact integer arguments and returned 5 after the tool result. No nonempty thinking field appeared in either synthetic response or any official message.

Installed identity: `gemma4:e4b-it-q4_K_M`, family Gemma, installed parameter metadata **7.5B**, Q4_K_M; digest `dc35e8d9c6061baa6f0fa870975ab6932e2542b579b13ea0f199fa4bb7300c9c`. The metadata value is recorded separately from the E4B tag. Ollama 0.40.4; primary NVIDIA RTX 3060 Ti, 8192 MiB.

Frozen protocol section 9.1 settings: think=false, temperature=0, seed=42, num_ctx=8192, num_predict=4096, page_size=50, tool budget=30, episode timeout=600 s, request timeout=120 s. No parameter, template, parser or placement adjustments.

| D3 criterion | Observed | Required | Verdict |
|---|---:|---:|---|
| Well-formed / attempted calls | 149/149 (100%) | >=90% | PASS |
| SUCCESS episodes | 16/20 (80%) | >=90% | FAIL |
| Competent queries | 11/20 (55%) | >=40% | PASS |
| Median episode wall time | 11.9732305 s | <=300 s | PASS |
| ERROR with OUT_OF_MEMORY | 0 | 0 | PASS |

All 149 attempted calls are native; no TEXT_TOOL_CALL occurrences. Median charged calls=7; no query exhausted the tool budget. Largest recorded prompt=8190. Outcomes: 16 SUCCESS and four PARSE_FAIL, with no ERROR, episode TIMEOUT or OOM. SUCCESS denotes valid parsed final JSON, not correctness.

The evaluator scored 346 submitted answer items: 325 GOLD/SUPPORTED, 17 ALT_VALID/SUPPORTED, and four OFF_QUESTION/PATH_INVALID. Eleven queries contain at least one question-valid supported answer. Query-level benchmark precision/recall and competent-query evidence are in `official-per-query.csv` and the original metrics.

The official invocation used existing `--max-new 20` support and exited zero. Console starts match the frozen query order exactly, all episode timestamps are sequential, and each query has exactly one attempt-1 record. Episode window: 2026-10-20 07:08:06.727516 to 07:12:38.122411 UTC (13:08:06 to 13:12:38 Asia/Dhaka), **271.394895 seconds**. The cumulative report completed at 07:12:45 UTC. The original episode runner's existing within-episode parse re-prompt remained unchanged; no completed episode was retried.

The four parse failures are BH2_03619, BH2_03762, BH2_03850 and BH2_03953. Each final response has `done_reason=length` and incomplete JSON. Their final prompt counts are respectively 8173, 8175, 7645 and 8175, with 19, 15, 547 and 15 generated tokens. This is consistent with pressure at the frozen 8192-token context; it is an interpretation of saved evidence, not a separately tested cause. No output was repaired and no context-size experiment was run. Full evidence: `parse-failure-inspection.json`.

Synthetic and during-run GPU usage samples were 5570 and 5596 MiB of 8192 MiB; these are samples, not peaks. `/api/ps` records context 8192 and size=size_vram=346302708 bytes. These unusually small accounting values do not explain total observed GPU usage; an exact GPU layer count/full-residency claim is not established by these samples. Raw values are retained without tuning.

Offline `--max-new 0` report-only execution exited zero. All **147** official run-file hashes remained identical across report-only, including all **126** pre-Gemma files. All **120** prior metric hashes, **122** protected identities, **43** pinned source/input hashes and all **six** prior candidate table rows match the preflight baseline. Twenty episodes plus one manifest were added; no duplicates or drift. See `official-final-integrity.json`.

## 3. One small real example run and output

BH2_02033 completed SUCCESS in 3.69889 seconds using four successful, well-formed native KG calls. All three answers were GOLD/SUPPORTED; benchmark precision and recall are both 1.0. Saved final output:

```json
{"status":"answered","answers":[{"id":"31332","name":"myostatin-related muscle hypertrophy"},{"id":"36432","name":"congestive heart failure"},{"id":"37659","name":"heart failure"}]}
```

The final query BH2_06427 also completed SUCCESS (4.726085 s), with three GOLD/SUPPORTED answers and benchmark precision/recall 1.0. The full trace preserves an intermediate invalid final response and the unchanged runner's successful parse re-prompt.

## 4. Assumptions

The researcher's exact-model request authorizes this candidate's entire S20 block, retaining all final statuses and proceeding without intermediate continuation approval. The established run ID is retained; records contain today's actual timestamps. This request does not select an S21 panel or settle the revised candidate-pool/round accounting.

## 5. Design choices beyond the specification

Routine engineering: use agent ID Gemma4-E4B, candidate diagnostics directory `gemma4-e4b`, reuse existing synthetic/summary helpers, and invoke the already-supported `--max-new 20` once. Preserve per-episode checkpointing and immutable provenance; snapshot prior run/metric hashes and table rows; verify frozen order, sequential timestamps and offline reporting; derive a focused parse-failure evidence file from existing traces. No new scientific threshold, literature method, evaluator rule or result-dependent change was introduced.

## 6. Items for manual inspection

- BH2_02033: compact, fully supported three-answer example in the original episode and metric records.
- The four PARSE_FAIL records and `parse-failure-inspection.json`: inspect incomplete final JSON, length termination and prompt counts.
- BH2_05686 and BH2_05843: supported ALT_VALID answers differ from the benchmark gold set; inspect scientific labels separately from benchmark precision.
- BH2_03879 and BH2_04003: valid final JSON with OFF_QUESTION/PATH_INVALID answers; parsing and competence are different measurements.
- `official-console.txt`, `official-per-query.csv` and `official-final-integrity.json`: complete continuous execution and preservation evidence.

No S21 work, other candidate, commit or push was performed.
