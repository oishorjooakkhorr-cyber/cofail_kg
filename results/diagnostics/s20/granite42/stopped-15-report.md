# S20 Granite 4.2 8B stopped checkpoint: 15/20 (2026-10-19)

**Stopped on a second ERROR/CONNECTION at BH2_04007 (query 15).** The authorized remaining-eight continuation completed query 13 and 14 SUCCESS, then saved query 15 ERROR and stopped before query 16. All earlier outcomes, including the first error, are unchanged. Five queries remain unrun; no complete D3 verdict is assigned.

## 1. Files created or changed

- This report, docs/decision_log.md, docs/progress.md, tasks/plan.md and tasks/todo.md.
- results/runs/screening/primary-3060ti-20261018/: Granite42-8B pinned configuration and 15 write-once attempt-1 episodes (ignored by Git); only three episodes added during continuation.
- results/diagnostics/screening/: 15 Granite metric files and cumulative screening_table.csv.
- results/diagnostics/s20/granite42/: original preflight/test/log evidence, reused continuation helper and journal, continuation invocation logs, two new post-invocation placement samples, stopped-15 summary/per-query CSV/manual inspection, timeout evidence, offline report-only log, integrity proof and report copy.

The reviewed 12/20 checkpoint is retained unchanged in stopped-report.md, stopped-summary.json, stopped-per-query.csv, stopped-manual-inspection.json, stopped-integrity-proof.json and stopped-screening-table.csv. This checkpoint has separately numbered stopped-15 artifacts. Pending shortlist/cleanup edits remain intact. No production source, launcher, evaluator, test, prompt, tool schema, data, frozen configuration or scientific rule changed. No rerun, commit or push.

## 2. Tests and execution results

Before official inference, unchanged full suite: **598 passed in 34.27 seconds**, no skips/deselections. All 43 pinned source/input hashes match before continuation and after this stop, so the suite was not repeated. Reused continuation helper compiles and checks the twelve-record frozen-order prefix, retained error, exact identity, one new record per invocation, exits, statuses and historical hashes. All three launcher invocations exited zero; the outer checker stopped on the newly saved ERROR exactly as required. Partial summary assertions verify prefix/order, record count and undefined final D3 fields.

Identity: granite4.2:8b, Granite family, 8.8B Q4_K_M, digest f586c02fdecdf151b656207c339aa003997345774a41768bac1fd6d2fb85913b. Ollama 0.40.4 on RTX 3060 Ti 8 GB. Synthetic native add(2,3) and result 5 passed with unchanged identity and no nonempty thinking fields.

Protocol section 9.1 settings unchanged: think=false, temperature=0, seed=42, num_ctx=8192, num_predict=4096, page_size=50, budget=30, episode timeout=600 s, request timeout=120 s. Existing local server was reused; an initial attempted start found the port occupied. No runtime update or placement tuning.

Synthetic, all thirteen available post-invocation samples and both read-only post-error samples report size=6862195914, size_vram=6268114697 bytes and context_length=8192: automatic partial CPU/GPU offload. Synthetic GPU use sampled 7208/8192 MiB, not a measured peak. Both post-error identity checks responded unchanged.

| Observed quantity | Partial result (15 saved / 20 expected) |
|---|---:|
| Well-formed / attempted calls | 244/244 (100%) |
| SUCCESS episodes | 13/15 (86.67%) |
| Competent queries | 5/15 (33.33%) |
| Median episode wall time | 108.939291 s |
| ERROR with OUT_OF_MEMORY | 0 |
| Largest recorded prompt | 8190 tokens |
| Median charged tool calls | 14 |
| Budget-hit share | 33.33% |

Partial observations only; all D3 criterion and overall verdict fields remain undefined. All 244 attempts were native; zero TEXT_TOOL_CALL events. There are 132 answer items: 129 GOLD/SUPPORTED and three OFF_QUESTION/PATH_INVALID. No nonempty assistant thinking field was recorded.

First error: BH2_03953, query 12, 139.565813 s, eight successful model responses before a read timeout. Second error: BH2_04007, query 15, 144.983317 s, fourteen successful model responses before the next request exceeded the unchanged 120-second HTTP read timeout. CONNECTION is the existing client's broad timeout classification, not proof of a network disconnect. Neither failed request returned a completion to inspect; the exact slow-generation cause remains unresolved. No inference replay or diagnostic rerun was performed.

Offline --max-new 0 exited zero without inference. All **121** current run-file hashes match, including the entire **118-file** stopped checkpoint and **105** pre-Granite files. The three continuation journal hashes match their records. All **122** protected identities, **43** pinned source/input hashes, **100** prior metric files and five prior candidate table rows are unchanged. Proof: stopped-15-integrity-proof.json.

## 3. One small real example and output

New continuation query BH2_03991 completed SUCCESS in 155.876456 s; BH2_04003 completed SUCCESS in 176.102251 s. Neither adds a competent query. SUCCESS means the final JSON parsed, not that the answer was correct.

The earlier small supported example BH2_02033 remains unchanged: 12.574970 s, four well-formed native calls, all three answers GOLD/SUPPORTED. Full saved output:

```json
{"status":"answered","answers":[{"id":"31332","name":"myostatin-related muscle hypertrophy"},{"id":"36432","name":"congestive heart failure"},{"id":"37659","name":"heart failure"}]}
```

This is experimental output, not independent biomedical advice. Omitting page is valid under frozen T1; the earlier intermediate commentary error was corrected by direct schema/evaluator inspection without any metric change.

## 4. Assumptions

Researcher selected "Continue the remaining eight (Recommended)" after the 12/20 checkpoint. Authorization retained the established stop-on-new-ERROR policy, so only three new queries were executed before the second stop. All saved final statuses remain completed. Experiment ID remains primary-3060ti-20261018; timestamps record actual execution. Revised candidate membership, D3 round accounting and S21 selection remain outside this measurement.

## 5. Design choices beyond the specification

Routine engineering: reuse Ministral's existing continuation helper with Granite identity/path substitutions and the twelve-record prefix; preserve reviewed checkpoint derivations separately; number subsequent stopped summaries to prevent overwriting earlier checkpoints; verify old metrics/table rows as well as run/source hashes. No scientific threshold, literature method, model-specific template, argument repair or timeout change was introduced.

## 6. Items for manual inspection and next decision

- BH2_04007: second read-timeout event and last successful responses in stopped-15-timeout-evidence.json and its original record. The original first error is in stopped-timeout-evidence.json.
- BH2_03991 and BH2_04003: SUCCESS without supported question-valid answers; do not equate parsing with competence.
- BH2_02033: supported three-answer example and valid omitted optional page argument.
- Largest prompt 8190 is near the frozen 8192 context. Any protocol-required 16K follow-up belongs to later S21 work.

Five remaining frozen queries: BH2_04425, BH2_05366, BH2_05686, BH2_05843 and BH2_06427. A continuation would run only those five with unchanged settings while retaining all fifteen outcomes and both errors. No automatic retry or further inference has been performed. The existing stop policy requires the researcher's continuation decision.
