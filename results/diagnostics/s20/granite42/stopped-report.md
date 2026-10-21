# S20 Granite 4.2 8B stopped checkpoint (2026-10-19)

**12/20 outcomes saved; stopped on BH2_03953 ERROR/CONNECTION.** Eleven SUCCESS records and the error are preserved in primary-3060ti-20261018. Eight queries remain unrun. No complete D3 verdict is assigned. The established stop policy requires an explicit continuation decision; no error retry is proposed.

## 1. Files created or changed

- This report, docs/decision_log.md, docs/progress.md, tasks/plan.md and tasks/todo.md.
- results/runs/screening/primary-3060ti-20261018/: one pinned Granite42-8B configuration and 12 write-once attempt-1 episode records (ignored by Git).
- results/diagnostics/screening/: 12 new metric files and the cumulative screening_table.csv.
- results/diagnostics/s20/granite42/: metadata, synthetic exchange/placement, full-suite log, reused operational helpers, per-invocation logs and journal, stopped summary/per-query CSV/manual inspection, timeout evidence, report-only log and integrity proof.
- Graphify query used to locate the existing stage workflow; existing pending shortlist/cleanup changes preserved.

No production source, launcher, evaluator, test, prompt, tool schema, data, frozen configuration or scientific rule was edited. No episode was rerun or overwritten; no commit or push.

## 2. Tests and execution results

Unchanged full suite: **598 passed in 34.27 seconds**, no skips or deselections. Reused helpers parse and retain explicit identity, source/input hashes, frozen query order, exactly-one-new-record, exit and status assertions. The summary helper also verifies saved records are a frozen-order prefix and partial D3 fields remain undefined.

Installed identity: granite4.2:8b, Granite family, 8.8B Q4_K_M, digest f586c02fdecdf151b656207c339aa003997345774a41768bac1fd6d2fb85913b. Ollama 0.40.4 on RTX 3060 Ti 8 GB. The healthy existing local server was reused after an attempted start found port 11434 occupied; no runtime update was made.

Native add(2,3) synthetic preflight passed with integer arguments, then final result 5, unchanged identity and no nonempty thinking field. Frozen settings: think=false, temperature=0, seed=42, num_ctx=8192, num_predict=4096, page_size=50, budget=30, episode timeout=600 s and request timeout=120 s (protocol section 9.1).

Synthetic and all eleven completed post-invocation samples report size=6862195914, size_vram=6268114697 bytes and context_length=8192. This is automatic partial CPU/GPU offload, without tuning. Synthetic GPU use sampled 7208/8192 MiB; this is not a peak measurement. The read-only check after the error reports the same identity and placement.

| Observed quantity | Partial result (12 saved / 20 expected) |
|---|---:|
| Well-formed / attempted calls | 168/168 (100%) |
| SUCCESS episodes | 11/12 (91.67%) |
| Competent queries | 5/12 (41.67%) |
| Median episode wall time | 86.6405435 s |
| ERROR with OUT_OF_MEMORY | 0 |
| Largest recorded prompt | 8187 tokens |
| Median charged tool calls | 9.5 |
| Budget-hit share | 25% |

These are partial observations, not complete D3 PASS/FAIL results. All 168 attempts are native, with zero TEXT_TOOL_CALL events. There are 131 answer items: 129 GOLD/SUPPORTED and two OFF_QUESTION/PATH_INVALID. No nonempty thinking field was recorded.

All twelve separate --max-new 1 launcher invocations exited zero. Invocation 12 saved ERROR/CONNECTION; the outer checker then exited nonzero and stopped before query 13 as required. BH2_03953 ran 139.565813 seconds and saved eight successful model responses before the next POST /api/chat exceeded the 120-second HTTP read timeout. The error is a timeout classification, not proof of a disconnected network. No completion from that failed request was available to inspect; exact generation-stall cause remains unresolved. No diagnostic inference/replay was performed.

Report-only --max-new 0 exited zero without inference. All **118** current run-file hashes match, including all **105** prior files and all 12 episode hashes in the invocation journal. All **122** protected identities, **43** pinned source/input hashes, **100** prior metric files and five prior candidate table rows are unchanged. Proof: results/diagnostics/s20/granite42/stopped-integrity-proof.json.

## 3. One small real example and output

BH2_02033 completed SUCCESS in 12.574970 seconds, using four well-formed native KG calls. All three answers evaluate GOLD and SUPPORTED. Full final output:

```json
{"status":"answered","answers":[{"id":"31332","name":"myostatin-related muscle hypertrophy"},{"id":"36432","name":"congestive heart failure"},{"id":"37659","name":"heart failure"}]}
```

This is saved experimental output, not independent biomedical advice. Omitting page is valid: the frozen T1 schema requires only entity_id and relation for get_neighbors and defaults page to 1. An intermediate commentary incorrectly called its omission malformed; direct schema/evaluator inspection corrected that statement. No metric or scientific rule changed.

## 4. Assumptions

The latest request authorizes this candidate's full block subject to the established per-invocation ERROR stop policy (decision log, 2026-10-18 continuation policy). The experiment ID retains its original date; all new timestamps record the actual run time. This measurement does not decide revised candidate membership, D3 round accounting or S21 selection. Existing partial CPU/GPU placement procedure remains accepted without tuning.

## 5. Design choices beyond the specification

Routine engineering only: reuse the prior candidate's operational helpers with identity/path substitutions; use agent ID Granite42-8B and the established experiment ID; preserve raw outputs and logs; add a partial-summary prefix/order assertion; check historical metrics/table rows as well as run/source identities. No new scientific threshold, literature method, parser repair or model-specific prompt/template was introduced.

## 6. Items for manual inspection and next decision

- BH2_02033: supported three-answer example and valid omitted optional page argument.
- BH2_00461: four KG calls and 21 GOLD/SUPPORTED answers; inspect completeness rather than infer it from SUCCESS.
- BH2_03953: last successful native responses and the saved read-timeout event, in stopped-timeout-evidence.json and the original record. Do not replace this final ERROR outcome.
- Largest prompt 8187 is close to context 8192. Any protocol-required 16K follow-up belongs to later S21 work, outside this request.

Remaining frozen queries: BH2_03991, BH2_04003, BH2_04007, BH2_04425, BH2_05366, BH2_05686, BH2_05843 and BH2_06427. The concrete continuation option is to run only these eight with unchanged settings, retaining all twelve outcomes including ERROR/CONNECTION. No automatic retry or timeout change.
