# Gemma 4 E4B: separate 8K versus 16K context diagnostic (2026-10-20)

**Follow-up (2026-10-20):** The later complete fresh twenty-query Gemma block passed D3 at 16K (19 SUCCESS, 14 competent). This selected four-query diagnostic was preserved and was not stitched into that block. See [full 16K reassessment](S20_full_16k_reassessment.md).

**All four previous PARSE_FAIL queries produced valid final JSON at 16K. Three of the four produced supported, question-valid answers.** All four diagnostic queries ran continuously in one process. This strongly supports the original 8K context limit as the cause of the observed parse failures; a pause-between-queries explanation is not supported by this comparison.

This is a selected four-query diagnostic, not a replacement S20 block or a D3 verdict at 16K. The official 20-query 8K result remains FAIL and every original outcome is unchanged. No full 20-query 16K run or S21 freeze was performed.

## 1. Files created or changed

- `results/runs/context-diagnostics/gemma4-e4b-16k-20261020/`: separate immutable diagnostic configuration and four attempt-1 records.
- `results/diagnostics/s20/gemma4-e4b-16k/`: authorization/configuration/integrity manifest, diagnostic driver and its SHA256, console and exit, runtime/GPU samples, four separate evaluator metric files, comparison CSV/JSON with final outputs and answer labels, and final integrity proof.
- This report, `docs/decision_log.md`, `docs/progress.md`, `tasks/plan.md`, and `tasks/todo.md`.

The production agent, screening launcher, evaluator, prompts, schemas, tests, data, frozen rules, official screening configurations, episodes, metrics and table were unchanged.

## 2. Checks and results

The researcher accepted the proposed separate 16K diagnostic after discussing the four 8K parse failures. Run ID: `gemma4-e4b-16k-20261020`; agent: `Gemma4-E4B`; exact model `gemma4:e4b-it-q4_K_M`, installed metadata 7.5B Q4_K_M; digest `dc35e8d9c6061baa6f0fa870975ab6932e2542b579b13ea0f199fa4bb7300c9c`.

Only the scientific setting **num_ctx changed from 8192 to 16384**. Administrative output root and run ID changed to isolate records. All other generation/episode settings, including think=false, temperature=0, seed=42, num_predict=4096, page_size=50, tool budget=30, episode timeout=600 s and request timeout=120 s, match the original configuration. Every episode still starts with fresh messages and a fresh KG environment.

Offline assertions checked the exact four original PARSE_FAIL records, context-only scientific change, separate output path, frozen sources and prior results. Driver syntax and workspace-root checks passed before inference; an initial path assertion caught an incorrect parent index, which was corrected before any diagnostic model call. Live checks pinned the driver, installed identity and original hashes. Existing `run_screening`, `validate_resume` and immutable persistence were reused; no production behavior changed. The prior unchanged full suite had passed all 598 tests; it was not repeated for this configuration-only experiment. The diagnostic invocation exited zero and saved exactly four records without retries.

| Query | 8K status | 16K status | Supported question-valid answers at 16K | Benchmark precision / recall at 16K | Wall seconds: 8K / 16K |
|---|---|---|---:|---:|---:|
| BH2_03619 | PARSE_FAIL | SUCCESS | 85 | 1.000 / 0.475 | 18.57 / 51.97 |
| BH2_03762 | PARSE_FAIL | SUCCESS | 0 | 0.000 / 0.000 | 21.21 / 38.14 |
| BH2_03850 | PARSE_FAIL | SUCCESS | 66 | 1.000 / 0.943 | 21.41 / 24.75 |
| BH2_03953 | PARSE_FAIL | SUCCESS | 90 | 1.000 / 0.629 | 13.53 / 34.56 |

SUCCESS means valid final JSON, not necessarily correct answers. The first, third and fourth rows have respectively 85, 66 and 90 GOLD/SUPPORTED answer items. BH2_03762 has six OFF_QUESTION/PATH_INVALID items, so its formatting recovered but its biomedical answer did not. These three recovered queries are not necessarily complete answers: recall remains below 1.

All four final response termination reasons changed from `length` at 8K to `stop` at 16K. The largest 16K prompt counts were respectively 13956, 16314, 7636 and 10938. Three therefore used prompt histories larger than 8192. BH2_03850 needed more space for its output despite its prompt remaining below 8192. There were 51/51 well-formed native tool calls, no recorded TEXT_TOOL_CALL occurrences, no thinking messages and no ERROR/TIMEOUT/OOM outcomes.

Ollama `/api/ps` confirmed the pinned digest at context_length=16384 after each completed diagnostic episode. Sampled GPU usage was 5570-5577 MiB of 8192 MiB, not a measured peak. As in the 8K report, `/api/ps` size accounting alone does not establish a GPU layer count or exact residency.

Integrity after evaluation: all **147** official run-file hashes, **140** official metric hashes, the official screening-table hash, **43** pinned source/input hashes and **122** protected identities match the pre-diagnostic baseline. The four diagnostic episodes and separate configuration have their own hashes in `final-integrity.json`. Official 8K D3 metrics were not regenerated or amended.

## 3. One small real example and output

BH2_03762 changed from incomplete JSON at 8K to valid final JSON at 16K, but its six answers all evaluated OFF_QUESTION/PATH_INVALID. This is a useful counterexample to treating JSON recovery as correctness. Its exact final output and all six labels are retained under `manual_inspection` in `comparison.json`.

For a positive example, BH2_03953 changed from the truncated prefix `{"status": "answered", "answers": [{"id": "14` at 8K to a complete JSON object with 90 answer items at 16K. All 90 evaluated GOLD/SUPPORTED, with benchmark precision 1.0 and recall 0.6293706293706294. Its full output is in `comparison.json` and the original diagnostic episode; it is not abbreviated or repaired in those artifacts.

## 4. Assumptions and interpretation

The researcher's "yeah do that with 16K context for this model and see" accepts the previously offered focused diagnostic on the four failures, rather than authorizing a new official twenty-query screening block. Keeping all other settings fixed isolates the configured context change. Longer context can also change the model's later trajectory; the experiment demonstrates recovery under 16K, not that every token would otherwise be identical. There was no replicated 8K diagnostic control, paused-run condition or full 20-query 16K test.

## 5. Design choices beyond the specification

Routine engineering: use a separate diagnostic output root/run ID; select exactly the four prior parse failures in original screening order; reuse existing episode/resume/checkpoint/evaluator functions without calling cumulative official reporting; pin driver/configuration identity; sample actual context and GPU use between episodes; retain all prior hashes; save paired status, token-count, latency and scientific-label comparisons. This is a user-authorized configuration diagnostic, with no new scientific threshold, model-selection rule or literature method.

## 6. Manual inspection

Inspect BH2_03762's valid-but-wrong six-answer output, BH2_03953's complete supported output, the paired termination reasons and prompt counts in `comparison.csv`, and the actual 16K runtime samples. The selected failure subset cannot establish a full 20-query 16K D3 pass. Original S20 evidence remains in `docs/S20_gemma4_screening.md` and its linked artifacts.
