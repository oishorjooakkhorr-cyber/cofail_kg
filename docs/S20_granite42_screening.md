# S20 Granite 4.2 8B screening complete (2026-10-19)

All **20 frozen queries** are saved for Granite42-8B in primary-3060ti-20261018. **This candidate fails D3 on SUCCESS rate and competence.** The other three criteria pass. All three ERROR/CONNECTION timeout outcomes remain in the official denominators; none was retried or replaced. No S21 selection or final configuration freeze was made.

## 1. Files created or changed

- This report, docs/decision_log.md, docs/progress.md, tasks/plan.md and tasks/todo.md.
- results/runs/screening/primary-3060ti-20261018/: one pinned Granite42-8B configuration and twenty write-once attempt-1 episode records, ignored by Git.
- results/diagnostics/screening/: twenty new metric files and the cumulative screening_table.csv.
- results/diagnostics/s20/granite42/: exact model metadata, synthetic exchange/placement, full-suite log, reused operational helpers, invocation logs/journals, per-query CSV, official summary/manual inspection, report-only log, final integrity proof and validation.

The reviewed 12/20, 15/20 and 16/20 reports and their derivations/proofs are retained separately as stopped-report.md, stopped-15-report.md and stopped-16-report.md with corresponding checkpoint artifacts. Pending shortlist/cleanup/other graph changes were preserved.

No production source, launcher, evaluator, test, prompt, tool schema, data, frozen configuration or scientific rule changed. No completed outcome was rerun, repaired or overwritten. No commit or push was performed.

## 2. Tests and execution results

Unchanged full suite before official inference: **598 passed in 34.27 seconds**, no skips/deselections. All 43 pinned source/input hashes match across continuations; the full suite was not repeated. Reused helpers parse and retain identity, frozen-prefix/order, exactly-one-new-record, exit, status and hash checks. The final operational stop-policy guard passed six synthetic assert-based checks: SUCCESS, PARSE_FAIL and logged CONNECTION timeout may continue; refused CONNECTION, OUT_OF_MEMORY and RUNTIME stop. These checks exercise the actual guard expression, saved in continuation3-stop-policy-selfcheck.json.

Installed identity: granite4.2:8b, Granite family, 8.8B Q4_K_M, digest f586c02fdecdf151b656207c339aa003997345774a41768bac1fd6d2fb85913b. Runtime: Ollama 0.40.4 on the primary RTX 3060 Ti 8 GB host. Native synthetic add(2,3) emitted exact integer arguments, followed by result 5, with unchanged identity and no nonempty thinking field. The existing healthy local server was used after an attempted start found port 11434 occupied.

Frozen protocol section 9.1 settings: think=false, temperature=0, seed=42, num_ctx=8192, num_predict=4096, page_size=50, budget=30, episode timeout=600 s and request timeout=120 s. No template adjustment, parser/argument repair or placement tuning.

Synthetic, all **17** available post-invocation placement samples and the three read-only post-error samples retain context 8192 and size=6862195914, size_vram=6268114697 bytes. This is automatic partial CPU/GPU offload. Synthetic GPU use sampled 7208/8192 MiB; this is not a peak measurement or an exact layer count. No new placement eligibility threshold was introduced.

| D3 criterion | Observed | Required | Verdict |
|---|---:|---:|---|
| Well-formed / attempted calls | 327/327 (100%) | >=90% | PASS |
| SUCCESS episodes | 17/20 (85%) | >=90% | FAIL |
| Competent queries | 6/20 (30%) | >=40% | FAIL |
| Median episode wall time | 120.247903 s | <=300 s | PASS |
| ERROR with OUT_OF_MEMORY | 0 | 0 | PASS |

All 327 attempts are native; zero TEXT_TOOL_CALL occurrences. Median charged tool calls=12.5; seven queries reached the budget (35%). Largest recorded prompt=8190. No nonempty assistant thinking field. The twenty outcomes are 17 SUCCESS and three ERROR/CONNECTION; zero PARSE_FAIL, episode TIMEOUT or OUT_OF_MEMORY. SUCCESS means a final JSON answer parsed, not necessarily a correct answer.

There are 135 submitted answer items: 132 GOLD/SUPPORTED and three OFF_QUESTION/PATH_INVALID, spread over nine queries with answer items. Six queries have at least one question-valid supported answer. Per-query counts and benchmark scores are in official-per-query.csv.

All twenty separate --max-new 1 launcher invocations exited zero and each saved exactly one new record in frozen order. Three saved errors caused the outer checker to stop at the established checkpoints; the researcher explicitly authorized each continuation. For the final four, the researcher amended only the operational policy to continue past further logged CONNECTION timeouts while retaining other stops. **All four final queries completed SUCCESS**, so that exception was not triggered in live continuation.

Preserved request-timeout records:

| Query | Frozen position | Episode wall time | Successful model responses before failed request |
|---|---:|---:|---:|
| BH2_03953 | 12 | 139.565813 s | 8 |
| BH2_04007 | 15 | 144.983317 s | 14 |
| BH2_04425 | 16 | 142.561278 s | 7 |

Each next POST /api/chat exceeded the unchanged 120-second HTTP read timeout. CONNECTION is the existing client's broad timeout classification, not proof of a network disconnect. Read-only endpoint checks responded with unchanged identity/placement. The failed requests returned no completion to inspect; exact slow-generation cause remains unresolved. No off-book inference, replay or diagnostic rerun was performed.

Final --max-new 0 exited zero without inference. All **126** official run-file hashes match, including all **122** files at the last checkpoint and **105** pre-Granite files. All twenty episode hashes match the combined invocation journals. All **122** protected identities, **43** pinned source/input hashes, **116** existing metric hashes captured before the final four, and the five prior candidate table rows are unchanged. Final proofs: official-final-integrity.json and official-validation.json. Seventeen post-invocation placement samples were checked against the pinned model and unchanged context/size values.

## 3. One small real example run and output

The final query, BH2_06427, completed SUCCESS in 44.859084 seconds. Seven well-formed native calls were emitted, six successful; one later query used an invalid KG relation for its entity. The earlier valid two-hop calls support all three submitted answers. Benchmark precision and recall are both 1.0; all three evaluate GOLD/SUPPORTED. Full saved final output:

```json
{"status":"answered","answers":[{"id":"14782","name":"Biotin"},{"id":"15270","name":"Lipoic acid"},{"id":"17559","name":"Gabapentin enacarbil"}]}
```

This is experimental model output, not independent biomedical advice. The original record and official-manual-inspection.json contain the raw messages, tool calls/results and labels. The earlier supported BH2_02033 example is also retained unchanged.

## 4. Assumptions

The initial request authorized this candidate's unchanged full block subject to established stop conditions. The researcher separately approved the remaining-eight and remaining-five continuations, and finally the last four with a narrow logged-CONNECTION-timeout exception. Every saved final status remained completed, including all three errors. The run ID retains the existing experiment date while records carry actual timestamps. This measurement does not settle revised pool membership, D3 round accounting or S21 panel selection.

## 5. Design choices beyond the specification

Routine engineering: reuse prior candidates' preflight/run/summary/continuation helpers with candidate identity/path and saved-prefix substitutions; use Granite42-8B in the established experiment; number stopped checkpoint artifacts to preserve reviewed evidence; verify prior metrics/table rows in addition to run/source hashes; test the explicitly approved narrow timeout stop-policy exception. No new scientific threshold, literature method or result-dependent prompt/template/parameter change was introduced.

An early intermediate commentary incorrectly called omitted page arguments malformed. Direct inspection confirmed page is optional in frozen T1, and the unchanged evaluator correctly counts those calls as well formed. The commentary was corrected; no metric, schema or scientific rule was changed.

## 6. Items for manual inspection

- BH2_06427: final supported three-answer example; inspect the seven-call sequence and later failed relation separately from support for the submitted answers.
- BH2_02033: compact four-call supported example; page omission is valid under T1.
- BH2_03991 and BH2_04003: SUCCESS after budget exhaustion without competent answers; parsing is distinct from competence.
- BH2_03953, BH2_04007 and BH2_04425: saved error traces and timeout evidence in the retained checkpoint artifacts. No timeout was rerun or removed from the denominator.
- Largest prompt 8190 is close to context 8192. Any protocol-required 16K follow-up belongs to later S21 work; none was run here.

Stop after this completed candidate report. No other model, S21 work, commit or push.
