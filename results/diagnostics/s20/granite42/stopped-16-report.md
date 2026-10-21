# S20 Granite 4.2 8B checkpoint: 16/20 (2026-10-19)

**Stopped on a third ERROR/CONNECTION at BH2_04425 (query 16).** The approved remaining-five continuation saved this final error and stopped before query 17. All fifteen prior outcomes and both earlier errors are unchanged. Four queries remain unrun. Even four SUCCESS outcomes would yield only 17/20 (85%), below D3's 90% SUCCESS threshold; complete-set verdict fields remain undefined until all twenty outcomes are saved.

## 1. Files created or changed

- This report, docs/decision_log.md, docs/progress.md, tasks/plan.md and tasks/todo.md.
- results/runs/screening/primary-3060ti-20261018/: Granite42-8B configuration and sixteen write-once attempt-1 records (ignored by Git), only one added in this continuation.
- results/diagnostics/screening/: sixteen Granite metric files and cumulative screening_table.csv.
- results/diagnostics/s20/granite42/: continuation2 helper/log/journal, baseline of all 115 existing metrics, stopped-16 summary/per-query CSV/manual inspection, timeout evidence, read-only placement sample, offline report-only log, integrity proof and report copy.

Earlier reviewed checkpoints remain in stopped-report.md (12/20), stopped-15-report.md and their separate summaries/proofs/tables. Pending shortlist/cleanup edits remain intact. No production source, launcher, evaluator, test, prompt, tool schema, data, frozen configuration or scientific rule changed. No completed outcome was rerun or overwritten; no commit or push.

## 2. Tests and execution results

Unchanged full suite before inference: **598 passed in 34.27 seconds**, no skips/deselections. The 43 pinned source/input hashes still match; no suite repeat was required. The reused continuation helper parses and verifies the fifteen-record prefix, saved error, exact identity, order, record count, source/run hashes, exit and status. The launcher exited zero and saved the error; the outer checker then stopped on ERROR as required. The partial-summary helper validates the saved frozen-order prefix and undefined final D3 fields.

Identity: granite4.2:8b, Granite lineage, 8.8B Q4_K_M, digest f586c02fdecdf151b656207c339aa003997345774a41768bac1fd6d2fb85913b. Runtime: Ollama 0.40.4, RTX 3060 Ti 8 GB. Synthetic native add(2,3) and result 5 passed before official inference; no thinking field or identity drift.

Protocol section 9.1 settings unchanged: think=false, temperature=0, seed=42, num_ctx=8192, num_predict=4096, page_size=50, budget=30, episode timeout=600 s, request timeout=120 s. No template/parser/argument repair or placement tuning. Synthetic and available post-invocation/post-error samples retain size=6862195914, size_vram=6268114697 bytes and context_length=8192 (automatic partial CPU/GPU offload). Synthetic GPU usage sampled 7208/8192 MiB, not a peak measurement. Existing healthy server was reused; the initial attempted start found the port occupied.

| Observed quantity | Partial result (16 saved / 20 expected) |
|---|---:|
| Well-formed / attempted calls | 251/251 (100%) |
| SUCCESS episodes | 13/16 (81.25%) |
| Competent queries | 5/16 (31.25%) |
| Median episode wall time | 124.252552 s |
| ERROR with OUT_OF_MEMORY | 0 |
| Largest recorded prompt | 8190 tokens |
| Median charged tool calls | 12.5 |
| Budget-hit share | 31.25% |

All 251 attempts native; zero TEXT_TOOL_CALL occurrences and no nonempty assistant thinking fields. There are 132 answer items: 129 GOLD/SUPPORTED and three OFF_QUESTION/PATH_INVALID. All complete D3 pass/fail fields remain undefined in the partial table. The fixed SUCCESS threshold is already mathematically unreachable; no new stopping/selection criterion is inferred from this observation.

Errors preserved: BH2_03953 (query 12, 139.565813 s), BH2_04007 (query 15, 144.983317 s), BH2_04425 (query 16, 142.561278 s). Each failed a POST /api/chat at the unchanged 120-second HTTP read timeout. Latest episode retained seven successful model responses before the failed request. CONNECTION is the client's broad timeout classification, not proof of a disconnected network. Read-only post-error metadata/placement responded with unchanged identity. No failed-request completion is available; exact slow-generation cause unresolved. No diagnostic inference or replay performed.

Offline --max-new 0 exited zero without inference. All **122** run-file hashes match, including the **121-file** previous checkpoint and **105** pre-Granite files. Latest journal hash matches its episode. All **122** protected identities, **43** pinned source/input hashes, **115** existing metric hashes and five prior candidate table rows are unchanged. Proof: stopped-16-integrity-proof.json.

## 3. One small real example run and output

Exactly one new episode was run during this approved continuation: BH2_04425, wall 142.561278 seconds. Recorded outcome (selected fields):

```json
{"query_id":"BH2_04425","status":"ERROR","cause":"CONNECTION"}
```

Error text: `HTTPConnectionPool(host='127.0.0.1', port=11434): Read timed out. (read timeout=120)`.

The earlier BH2_02033 example remains unchanged: SUCCESS in 12.574970 s, four well-formed native calls, three GOLD/SUPPORTED answers. Omitting page is valid under frozen T1; an earlier commentary mistake was corrected by direct schema/evaluator inspection without changing any metric.

## 4. Assumptions

Researcher selected "Continue the remaining five (Recommended)" while retaining the stop-on-each-new-ERROR policy. That authorizes the five-query suffix subject to this stop condition, so execution stopped after its first new error. All saved final statuses remain completed and both earlier checkpoints retain their reviewed evidence. Revised pool membership, round accounting and S21 selection remain outside this measurement.

## 5. Design choices beyond the specification

Routine engineering only: reuse the continuation helper with the fifteen-record prefix and a separate journal/log name; preserve numbered checkpoints; snapshot all 115 existing metrics before continuation; retain the established experiment ID and pinned source. No new scientific threshold, literature method or result-dependent setting change.

## 6. Items for manual inspection and continuation decision

- BH2_04425: stopped-16-timeout-evidence.json and original record, seven successful responses followed by the saved read timeout.
- Earlier errors remain in stopped-timeout-evidence.json and stopped-15-timeout-evidence.json. No error is replaced.
- Largest prompt 8190 is near context 8192. Any protocol-required 16K follow-up belongs to later S21 work, outside this request.

Remaining frozen queries: BH2_05366, BH2_05686, BH2_05843 and BH2_06427. The retained operational policy currently requires another explicit continuation decision. A possible researcher-approved alternative is to finish only these four despite further ERROR/CONNECTION outcomes, keeping every timeout in the official denominator and retaining stops for other ERROR causes, nonzero exits, identity/hash drift and order discrepancies. This would change only the between-invocation stop policy, not the request timeout, generation settings, metrics, thresholds or saved outcomes. It has not been implemented or executed without approval.
