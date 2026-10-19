# S20 Qwen3.5 9B screening complete (2026-10-18)

All 20 frozen screening queries are saved for Qwen35-9B in run
primary-3060ti-20261018. **This candidate passes all five D3 criteria.**
The full S20 pool remains incomplete; no four-model S21 selection/freeze has
been made. Qwen3.5 was added as an extra candidate before its results, retaining
the original eight-model pool. Llama and Qwen3.5 are now screened; seven planned
candidates remain unrun.

## 1. Files and authorization

- `docs/decision_log.md`: extra-candidate decision, memory pause/recheck,
  acceptance of offload, full-block authorization and final evidence.
- `docs/S20_qwen35_preflight.md`: historical synthetic compatibility and memory
  investigation; this report covers the subsequent official block.
- `results/runs/screening/primary-3060ti-20261018/`: write-once Qwen35-9B
  configuration and 20 new episode records, attempt 1.
- `results/diagnostics/screening/screening_table.csv`: cumulative Llama/Qwen rows.
- `results/diagnostics/screening/primary-3060ti-20261018/`: 20 new metric files.
- `results/diagnostics/s20/qwen35/`: raw metadata, synthetic checks, memory
  logs, full-suite log, 20 invocation logs, journal, per-query CSV, summary,
  inspection examples, report-only log and integrity proof.
- `docs/progress.md`, `tasks/plan.md`, `tasks/todo.md`: final candidate status.

No agent, launcher, evaluator, prompt, tool schema, test, frozen configuration,
data or scientific rule was changed. No commit or push was performed.

## 2. Verification and execution

The unchanged full suite passed **598 tests in 41.73 seconds**, with no skips
or deselections, before official inference. Synthetic native add(2,3) succeeded
with integer arguments and no nonempty thinking field. Exact installed identity
was checked before/after that test and before/after every official episode.

The researcher accepted the observed offload and authorized all 20 official
queries. Executed 20 separate `--max-new 1` host invocations. Each launcher
exited zero and saved exactly one new record in frozen order. Between
invocations, checked status, query/model identity, prior-file/config hashes,
122 protected-file hashes and 43 pinned source/input hashes. No ERROR, nonzero
exit, drift or order discrepancy occurred. Two PARSE_FAIL records are completed
outcomes under the frozen rules and were not rerun.

After completion, `--max-new 0` exited zero without model inference. All 42 run
files (20 Llama records/configuration plus 20 Qwen records/configuration) retained
their hashes. The original 21 Llama files remain unchanged. Final proof:
`results/diagnostics/s20/qwen35/official-final-integrity.json`.

Model: `qwen3.5:9b`, Qwen lineage, 9.0B, Q4_K_M, digest
`56671c2ab9385f9cfcb404638e32cd62d88e3501d44822208363c010179a3c90`.
Runtime: Ollama 0.40.4, RTX 3060 Ti 8 GB. Settings: think=false,
temperature=0, seed=42, num_ctx=8192, num_predict=4096, page_size=50,
budget=30, episode timeout=600 seconds, request timeout=120 seconds.

The preflight load log confirmed **32/33 layers on GPU**, with one repeating
layer on CPU. Closing unused apps and rechecking did not change placement;
the researcher accepted it explicitly. All 20 post-invocation `/api/ps` samples
are retained. Their loaded-size/VRAM values match the accepted placement:
6,402,196,107 / 5,614,044,445 bytes, at context 8192. This records actual
placement; latency is not a fully GPU-resident measurement.

## 3. D3 results and per-query outcomes

| D3 criterion | Observed | Required | Verdict |
|---|---:|---:|---|
| Well-formed / attempted calls | 210/210 (100%) | >=90% | PASS |
| SUCCESS episodes | 18/20 (90%) | >=90% | PASS |
| Competent queries | 15/20 (75%) | >=40% | PASS |
| Median episode wall time | 26.383874 s | <=300 s | PASS |
| ERROR with OUT_OF_MEMORY | 0 | 0 | PASS |

Competence means at least one question-valid, SUPPORTED answer in a query; it
is not answer-level accuracy or completeness. SUCCESS means the final answer
parsed, including valid no_answer outputs. The SUCCESS threshold is met exactly.

There were 210 native calls, zero TEXT_TOOL_CALL occurrences, a median of nine
charged calls, and no budget-hit episode. Largest prompt_eval_count: **8189**.
No recorded assistant message contained a nonempty thinking field. Across
SUCCESS records, 362 submitted answers comprise 341 GOLD, 17 ALT_VALID and
four OFF_QUESTION; 358 are SUPPORTED and four PATH_INVALID. This does not imply
complete retrieval: several competent queries have very low benchmark recall.

| Query | Status | Wall s | Charged calls | Answers | Question-valid + supported |
|---|---|---:|---:|---:|---:|
| BH2_00461 | SUCCESS | 24.513593 | 4 | 21 | 21 |
| BH2_02033 | SUCCESS | 8.253073 | 4 | 3 | 3 |
| BH2_03434 | SUCCESS | 21.350715 | 4 | 33 | 33 |
| BH2_03619 | SUCCESS | 24.786116 | 16 | 0 | 0 |
| BH2_03750 | SUCCESS | 28.317935 | 6 | 44 | 44 |
| BH2_03760 | SUCCESS | 24.349870 | 13 | 3 | 0 |
| BH2_03762 | SUCCESS | 22.631905 | 10 | 1 | 1 |
| BH2_03850 | SUCCESS | 41.595977 | 8 | 69 | 69 |
| BH2_03856 | PARSE_FAIL | 57.024230 | 27 | 0 | 0 |
| BH2_03879 | SUCCESS | 27.981632 | 13 | 1 | 0 |
| BH2_03881 | PARSE_FAIL | 102.048926 | 15 | 0 | 0 |
| BH2_03953 | SUCCESS | 54.805817 | 12 | 57 | 57 |
| BH2_03991 | SUCCESS | 29.641319 | 16 | 1 | 1 |
| BH2_04003 | SUCCESS | 30.111957 | 20 | 1 | 1 |
| BH2_04007 | SUCCESS | 72.178011 | 12 | 30 | 30 |
| BH2_04425 | SUCCESS | 43.585062 | 7 | 75 | 75 |
| BH2_05366 | SUCCESS | 7.394182 | 4 | 1 | 1 |
| BH2_05686 | SUCCESS | 18.111884 | 8 | 15 | 15 |
| BH2_05843 | SUCCESS | 11.390900 | 7 | 4 | 4 |
| BH2_06427 | SUCCESS | 8.021286 | 4 | 3 | 3 |

## 4. Observed behavior and limitations

- BH2_00461: inspected the start drug, traversed drug_protein to TTR, inspected
  TTR and traversed disease_protein. Four successful calls produced 21 GOLD,
  SUPPORTED answers; benchmark precision/recall both 1.
- BH2_03760: correctly explored disease-to-drug and drug-to-side-effect edges,
  including integer pages 2 and 3, but submitted three drug bridge IDs instead
  of the requested effect/phenotype IDs. All three are OFF_QUESTION and
  PATH_INVALID. This remains SUCCESS for parsing but is not competent.
- BH2_03856: explored many valid drug-effect edges, then reversed direction
  from the Anxiety phenotype into drug neighbors. Final replies were empty,
  with done_reason=length and prompt/output counts 8140+52 and 8169+23,
  each totaling 8192. The existing re-prompt also failed; final PARSE_FAIL
  was retained without an episode rerun.
- BH2_03881: both final attempts ended with done_reason=length and truncated
  JSON. Prompt/output counts 6994+1198 and 6325+1867 each total 8192.
- BH2_03762, BH2_03991 and BH2_04003 each submitted one supported GOLD answer
  but benchmark recall was about 0.57%, 0.75% and 0.70%, respectively. Passing
  the D3 presence-based competence criterion does not guarantee exhaustive
  answers to "all" questions.

The context observations explain a concrete limitation of this 8K screening
run without changing its settings or judging a counterfactual larger-context run.
Because 8189 exceeds 0.8 * 8192, **if Qwen3.5 is chosen at S21**, protocol
section 9.1 requires five screening queries at context 16384 for final context
selection. That check is not yet run or authorized, and no S21 values are frozen.

## 5. Decisions and scope

All scientific settings, exact-type/no-coercion D3 accounting and all-status
write-once persistence were retained. No candidate was dropped based on early
performance. The extra-candidate decision and offload acceptance preceded
official Qwen results. Temporary local memory servers were used only for
diagnostics and stopped before official inference. No model-memory setting,
template, precision, GPU layer override or protocol threshold was tuned.

This completes the authorized Qwen candidate block. No other candidate,
S21 selection/freeze, 16K follow-up, commit or push was performed.

## 6. Manual inspection

Inspect BH2_00461 for a correct two-hop answer, BH2_03760 for wrong target type
despite valid traversal, and BH2_03856/BH2_03881 for context-bound parse failures.
The first three examples' full call/results, outputs and evaluated paths are
collected in `official-manual-inspection.json`; the complete original records
remain in the run directory. Per-query values are also in
`official-per-query.csv`, and the cumulative candidate verdict is in
`screening_table.csv`.
