# Full 16K D3 reassessment: Gemma, Qwen and Ministral (2026-10-20)

**Current researcher-authorized acceptance at 16K: Gemma 4 E4B PASS; Qwen3.5 9B PASS; Ministral 3 8B FAIL.** Each verdict uses a complete fresh twenty-query block and all five unchanged D3 thresholds. Gemma now counts as passing on this full-block evidence, not on its earlier selected four-query diagnostic. All original 8K results remain in the historical record.

The researcher explicitly authorized this reassessment after the 8K trace investigation and Gemma diagnostic. This is a dated, outcome-informed scoped amendment to the original section 9.1 screening context, recorded under protocol section 20 before new inference. It is not represented as the original frozen 8K screen or as an S21 panel/configuration freeze. Thresholds, questions, prompts, tools and evaluators were not changed.

## 1. Files created or changed

- `results/runs/screening-16k/context16k-3060ti-20261020/`: three immutable model configurations and sixty fresh attempt-1 episodes, separate from both historical 8K records and the selected four-query diagnostic.
- `results/diagnostics/s20/full-16k-20261020/`: three fixed full-block manifests, baseline hashes, reuse-based driver and its SHA256, focused-test evidence, per-candidate console/exit, runtime samples, sixty metric files, three summaries/per-query CSVs, offline report/exit logs, paired comparison, failed-response inspection, combined reassessment table, acceptance record and final integrity proof.
- This report, current progress/plan/todo and decision log; dated follow-up links in the earlier candidate and diagnostic reports.

Machine-readable current acceptance: `results/diagnostics/s20/full-16k-20261020/acceptance.json`. Complete D3 rows: `reassessment-table.csv`; per-query changes: each candidate's `per-query.csv` and `paired-comparison.json`.

Production source, the original launcher/evaluator, tests, data, prompt, tool schema, frozen protocol/decision-rule files, historical run configurations/episodes/metrics and the original `screening_table.csv` were preserved. No commit or push was performed.

## 2. Tests, execution and D3 results

Pre-inference checks: all three exact installed model identities matched the original digests and native-tool metadata; all original run/source hashes matched; manifests contained the same ordered twenty questions; syntax, workspace-root and context-only scientific-setting assertions passed. Focused unchanged screening tests: **42 passed in 2.43 seconds**. The unchanged full production suite had previously passed **598 tests**; it was not repeated because all 43 pinned source/input byte identities still match.

All sixty initial system/user message pairs are byte-for-byte equivalent as parsed strings to their 8K counterparts. Recorded model identity, temperature, seed, output cap, prompt identity, KG/BioHopR identities and complete tool configuration match. The only configured scientific change is **num_ctx: 8192 -> 16384**. New run IDs/output root isolate results; Git provenance records the current commit/dirty state rather than copying a stale earlier commit.

Runtime settings: think=false, temperature=0, seed=42, num_ctx=16384, num_predict=4096, page_size=50, budget=30, episode timeout=600 s, request read timeout=120 s. Same primary RTX 3060 Ti 8 GB host. Placement was left to Ollama's normal fitting; no layer, template, precision, parser, argument, prompt or timeout tuning. Actual digest/context=16384 was verified in **39 post-load samples per model** (117 samples total), with raw placement/GPU evidence retained. These samples do not constitute peak-memory or exact GPU-layer measurements.

Fixed execution order, registered before these blocks: Gemma, Qwen, Ministral. All twenty questions per model ran sequentially, and the three model blocks did not overlap. Every final status was checkpointed and retained. No completed episode was rerun; the unchanged runner's existing single within-episode JSON re-prompt remained allowed. All three full invocations exited zero.

| D3 criterion | Required | Gemma 4 E4B | Qwen3.5 9B | Ministral 3 8B |
|---|---:|---:|---:|---:|
| Well-formed / attempted calls | >=90% | 181/181 = 100% PASS | 263/263 = 100% PASS | 167/167 = 100% PASS |
| SUCCESS episodes | >=90% | 19/20 = 95% PASS | 19/20 = 95% PASS | 12/20 = 60% FAIL |
| Competent queries | >=40% | 14/20 = 70% PASS | 13/20 = 65% PASS | 12/20 = 60% PASS |
| Median episode wall time | <=300 s | 16.2779325 s PASS | 56.839506 s PASS | 168.0803425 s PASS |
| ERROR with OUT_OF_MEMORY | 0 | 0 PASS | 0 PASS | 0 PASS |
| **Full 16K D3 verdict** | **All five pass** | **PASS — accepted** | **PASS — accepted** | **FAIL — not accepted** |

All 611 attempted calls were native and well formed; there were zero TEXT_TOOL_CALL events and no nonempty thinking messages. Overall statuses: fifty SUCCESS, two PARSE_FAIL and eight ERROR/CONNECTION; no episode TIMEOUT or OOM. SUCCESS means parsed final JSON, including valid no_answer. Competence means at least one question-valid SUPPORTED answer on a query, with all twenty queries in the denominator; it is not answer-level accuracy or exhaustive recall.

Historical and reassessment comparisons:

| Model | 8K SUCCESS -> 16K SUCCESS | 8K competent -> 16K competent | 8K D3 -> 16K D3 |
|---|---:|---:|---|
| Gemma | 16 -> 19 | 11 -> 14 | FAIL -> PASS |
| Qwen | 18 -> 19 | 15 -> 13 | PASS -> PASS |
| Ministral | 15 -> 12 | 10 -> 12 | FAIL -> FAIL |

The increase in context does not improve every metric. Qwen's competence declined while remaining above D3's threshold; Ministral's competence improved but technical completion worsened. No hybrid score combining selected 16K recoveries with old 8K successes was constructed.

### Gemma: accepted on the complete 16K block

Three old parse failures recovered SUCCESS with supported answers: BH2_03619 (77 supported question-valid items), BH2_03850 (66) and BH2_03953 (90). BH2_03762 remains PARSE_FAIL in this fresh full block. Both final attempts ended at the 16384-token boundary: 16314+70 and 16135+249, with length termination and incomplete JSON. All sixteen old 8K SUCCESS queries remained SUCCESS.

The earlier selected four-query diagnostic had parsed BH2_03762 but answered it incorrectly. That separate result remains preserved; it was not reused to replace this full-block failure. The difference between fresh executions is recorded, not repaired or selectively discarded. Gemma passes despite the retained failure because its full SUCCESS rate is 95% and all other thresholds pass. Largest prompt=16314; no budget-hit episodes.

### Qwen: accepted, with parsing recovery distinct from competence

Both old parse failures, BH2_03856 and BH2_03881, now produced valid `{"status":"no_answer","answers":[]}`. They recovered formatting but neither became a competent query. One old 8K SUCCESS, BH2_03991, now has PARSE_FAIL: its first final attempt hit 16379+5=16384 with length termination; after the JSON re-prompt it emitted an extra native get_neighbors call with empty content instead of final JSON. The unchanged final-turn handler retained the parse failure.

Full-block SUCCESS=95%, competence=65%, and all other D3 thresholds pass. Largest prompt=16379, median charged calls=9.5 and budget-hit share=10%. All 562 scored answer items are SUPPORTED (545 GOLD, 17 ALT_VALID), spread across thirteen competent queries; that does not establish exhaustive recall on those queries.

### Ministral: not accepted; request timeouts remain decisive

All twelve completed SUCCESS episodes have at least one supported question-valid answer. There are 228 scored items: 211 GOLD/SUPPORTED and 17 ALT_VALID/SUPPORTED. Nevertheless, eight of the twenty episodes ended ERROR/CONNECTION because an HTTP request exceeded the unchanged 120-second read deadline:

`BH2_03619`, `BH2_03750`, `BH2_03856`, `BH2_03879`, `BH2_03953`, `BH2_03991`, `BH2_04003`, `BH2_04425`.

All eight failed responses are unavailable; their eventual text and token totals were not invented or recovered. No longer-timeout diagnostic was run in this reassessment. CONNECTION is the existing client's broad transport category; the logs specifically record read timeouts, not proof of an internet outage, GPU OOM or a 600-second episode timeout.

Of the four old 8K parse failures, only BH2_03881 completed SUCCESS here, with eleven supported answers. The other three became request-timeout errors, so their final-JSON recovery is unestablished. Four old 8K SUCCESS queries also became request errors (BH2_03750, BH2_03856, BH2_03879, BH2_03953), while the old timeout BH2_04425 remains an error. Thus zero PARSE_FAIL statuses in this block cannot be interpreted as universal formatting recovery: eight episodes ended before final parsing.

Ministral fails only the SUCCESS criterion; competence, call validity, median wall time and zero-OOM criteria pass. Largest recorded prompt=15009, median charged calls=7, no budget-hit episodes. These data establish failure under the tested 16K configuration and read deadline; they do not isolate the causal contribution of CPU offload, context, output verbosity, cache or scheduling to unreturned requests.

### Verification after execution

All three offline `--report-only` invocations exited zero without model calls and reproduced the same summaries/metrics. All **63 new run/configuration hashes** match the pre-report snapshot; there are exactly sixty unique attempt-1 episodes in frozen order, with sequential timestamps and no duplicates. Four saved parse errors from the two new PARSE_FAIL episodes were reproduced through the unchanged parser.

All **147 historical 8K run/configuration hashes**, **140 historical metric hashes**, the historical screening-table hash, **43 pinned source/input hashes**, **122 protected identities**, five existing selected-diagnostic run/configuration hashes, thirteen selected-diagnostic evidence hashes and six existing context-audit artifact hashes match their baseline. Driver SHA256 is pinned. See `final-integrity.json` for the complete proof and new run hashes.

## 3. One small real example and output

Full-block Gemma BH2_02033 completed SUCCESS in **3.601922 seconds**, using four well-formed successful native KG calls. All three items are GOLD/SUPPORTED; benchmark precision and recall are 1.0. Saved final output:

```json
{"status":"answered","answers":[{"id":"31332","name":"myostatin-related muscle hypertrophy"},{"id":"36432","name":"congestive heart failure"},{"id":"37659","name":"heart failure"}]}
```

For a contrasting real output, Qwen's recovered BH2_03881 returns exactly `{"status":"no_answer","answers":[]}`: valid JSON and SUCCESS, but zero competence on that query. Both original traces and their evaluator metrics are retained.

## 4. Assumptions and scope

The researcher explicitly permits these three candidates to count as passing if their full increased-context results meet D3 now. That authorization is implemented as current 16K acceptance, with original 8K history retained. A full fresh block, rather than only the known failures or a stitched result, supplies each denominator. Every saved error remains completed and is never retried.

This reassessment follows observed 8K results and a selected Gemma diagnostic, as recorded before inference. It is a controlled configuration reassessment, not a claim of an unseen preregistered 16K protocol or a replicated causal experiment. Runtime placement/cache state was not separately controlled beyond serial execution and recorded samples. No full pause-versus-continuous comparison was run.

Some Gemma/Qwen prompts still approach the 16K cap, and both retain one parse failure. Passing D3 is not evidence that context pressure is eliminated. Final S21 runtime/headroom rules, four-model/family selection and any later verification remain separate; this task does not freeze final values or choose the panel.

## 5. Design choices beyond the specification

Routine engineering: a separate full-reassessment run root/ID; reuse the existing twenty-query execution, all-status resume, immutable persistence, agent metrics and D3 aggregation; fixed serial model order; current Git provenance plus unchanged byte pins; context/digest/GPU samples; identical-starting-message and configuration comparisons; independent offline reporting; paired status/competence comparison and explicit acceptance JSON. Thresholds are the existing D3 thresholds; no new literature method, scientific gate, answer repair or outcome-dependent parameter change was added.

## 6. Manual inspection

- Inspect `acceptance.json` and `reassessment-table.csv`: only Gemma and Qwen qualify at 16K.
- Inspect Gemma BH2_03762 in both the preserved selected diagnostic and this full block; do not substitute the earlier parsed output for the current failure.
- Inspect Qwen BH2_03856/BH2_03881 no_answer recoveries, and BH2_03991's final-turn native call instead of JSON.
- Inspect the eight Ministral request-timeout records and `failure-inspection.json`; their missing completions were not reconstructed or rerun.
- Inspect the three per-query CSVs, paired comparison, runtime samples and full hash proof. No S21 selection, further context/output/timeout experiment, commit or push was performed.
