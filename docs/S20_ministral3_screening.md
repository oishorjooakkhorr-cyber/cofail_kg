# S20 Ministral 3 8B screening complete (2026-10-19)

**Follow-up (2026-10-20):** Ministral subsequently failed the complete fresh twenty-query 16K D3 reassessment (12 SUCCESS, eight request-timeout errors, 12 competent). It remains not accepted; the original 8K results below remain historical evidence. See [full 16K reassessment](S20_full_16k_reassessment.md).

All 20 frozen queries are saved for `Ministral3-8B` in
`primary-3060ti-20261018`. **This candidate fails D3** because SUCCESS is
15/20 (75%), below the required 90%. The other four criteria pass. Four
PARSE_FAIL records and the ERROR/CONNECTION at BH2_04425 remain unchanged.
No S21 model selection or final configuration freeze has been made.

## 1. Files created or changed

- This report, `docs/decision_log.md`, `docs/progress.md`, `tasks/plan.md`, `tasks/todo.md`.
- `results/runs/screening/primary-3060ti-20261018/`: one write-once Ministral
  configuration and 20 attempt-1 episode records; only the final four were added
  during the explicitly authorized continuation.
- `results/diagnostics/screening/`: 20 new metric files and the cumulative table.
- `results/diagnostics/s20/ministral3/`: metadata, synthetic exchange, placement,
  test log, operational helpers, invocation logs/journals, integrity proofs,
  per-query CSV, final summary and inspections. The reviewed 16/20 checkpoint
  report and derived summaries are retained as `stopped-report.md`,
  `stopped-summary.json`, `stopped-per-query.csv` and `stopped-manual-inspection.json`.

No agent, launcher, evaluator, test, prompt, tool schema, frozen configuration,
data or scientific rule was changed. No completed episode was rerun or replaced.
No commit or push was performed.

## 2. Tests and execution results

The unchanged full suite passed **598 tests in 28.33 seconds** before official
screening. The initial sandbox run had temporary-directory fixture setup errors
(438 passed, 160 errors). A focused `-x` reproduction identified pytest's inability
to create its numbered temporary directory; host execution with a workspace
basetemp passed without test/code changes, skips or deselections. No full-suite
repeat was needed for continuation: all 43 pinned source/input hashes still match.
The continuation helper compiles and contains explicit identity, frozen-prefix,
record-count, status, exit and hash assertions; all its checks passed.

Installed identity: `ministral-3:8b`, Mistral lineage, 8.9B Q4_K_M, digest
`1922accd5827ebe6829e536369195db25eaf664528dc66206d646ea3bb386b71`.
Runtime: Ollama 0.40.4 on the primary RTX 3060 Ti 8 GB host. Native tools are
advertised. Synthetic add(2,3) used one native call with integer arguments and
returned 5; neither response contained nonempty thinking. The 20 official
records also contain zero nonempty assistant thinking fields.

Frozen screening settings (protocol section 9.1): think=false, temperature=0,
seed=42, num_ctx=8192, num_predict=4096, page_size=50, tool budget=30, episode
timeout=600 seconds, request timeout=120 seconds. Provenance is pinned to
HEAD a7ae7539d705a643b1725114598f075db5846efa-dirty and the recorded source hashes.

Placement: size=6591967394 and size_vram=5549137591 bytes at context 8192;
Ollama CLI reports 16%/84% CPU/GPU. This automatic partial offload is recorded
without tuning. The percentage does not establish the exact text-layer split.
Placement samples are retained before screening, after the stop and after each
successful invocation check, including all four continuation invocations.

Twenty separate --max-new 1 launcher invocations exited zero and each saved one
new final record in frozen order. After episode 16 saved ERROR/CONNECTION, the
between-invocation checker stopped as intended. The researcher then explicitly
chose "Continue the remaining four (Recommended)" while retaining all saved
outcomes. Queries 17-20 completed SUCCESS; no new stop condition occurred.
The continuation preserved every one of the 80 run files at the stopped checkpoint.

| D3 criterion | Observed | Required | Verdict |
|---|---:|---:|---|
| Well-formed / attempted calls | 197/197 (100%) | >=90% | PASS |
| SUCCESS episodes | 15/20 (75%) | >=90% | FAIL |
| Competent queries | 10/20 (50%) | >=40% | PASS |
| Median episode wall time | 62.850686 s | <=300 s | PASS |
| ERROR with OUT_OF_MEMORY | 0 | 0 | PASS |

Final statuses: 15 SUCCESS, four PARSE_FAIL, one ERROR/CONNECTION, zero TIMEOUT
and zero OOM. All 197 attempts were native, with zero TEXT_TOOL_CALL events.
The 266 evaluated answer items comprise 243 GOLD, 17 ALT_VALID and six
OFF_QUESTION; 260 are SUPPORTED and six PATH_INVALID. SUCCESS establishes valid
final parsing, not answer correctness. Median charged calls=8.5; budget-hit
share=0. Largest prompt_eval_count=8184. Per-query values are in official-per-query.csv.

Four parse failures remain: BH2_03619 omitted the required answers list after
its one re-prompt; BH2_03881, BH2_03991 and BH2_04003 left incomplete JSON.
BH2_03991's final response had done_reason=length at prompt_eval_count=8184;
BH2_04003 had done_reason=length at 8095. These observations suggest context
pressure may contribute, without proving the cause of every failure. Frozen
settings, templates, parser and argument types were not altered.

BH2_04425 saved ERROR/CONNECTION after 139.070961 seconds because an /api/chat
request hit `Read timed out. (read timeout=120)` after six completed native KG
calls. This is the existing request-level transport error classification, not
the 600-second episode TIMEOUT or an OOM. A later read-only /api/ps check returned
normally with unchanged identity/placement. The official episode was never retried. A subsequent isolated replay of only
the failed HTTP request returned after 153.47 s, including 143.57 s generating
2,576 tokens, with a diagnostic 300-second read wait. This strongly supports a
long buffered generation exceeding the original 120-second read cap. The replay
returned prose rather than valid final JSON, so it does not establish episode
SUCCESS under a longer wait. Official outputs and D3 are unchanged. Full
follow-up: docs/S20_ministral3_timeout_investigation.md; original error evidence:
failure-inspection.json and official-16-BH2_04425.txt.

Final report-only --max-new 0 exited zero without inference. All **84 official
run-file hashes** match, including all 80 stopped-checkpoint files and all 63
pre-Ministral files. All 122 protected identities and 43 pinned sources/inputs
match. Proof: official-final-integrity.json; the earlier stop proof is retained.
The cumulative table is complete=True and records d3_pass=False for Ministral.
No prior candidate's table row was changed.

## 3. Small real example and output

The final continuation query BH2_06427 completed SUCCESS in 14.131324 seconds
with four well-formed native calls. Its final output was:

```json
{"status": "answered", "answers": [{"id": "14782", "name": "Biotin"}, {"id": "15270", "name": "Lipoic acid"}, {"id": "17559", "name": "Gabapentin enacarbil"}]}
```

All three answers are GOLD/SUPPORTED. Earlier BH2_00461 and BH2_02033 final lists
were independently compared with raw tool results: exact complete lists of 21
and three items, respectively, not a fixed first-five response. See
first-two-inspection-proof.json. These are stored experimental outputs judged
against the frozen benchmark and KG, not independently endorsed biomedical claims.

## 4. Assumptions

The original request authorized this candidate's full block; the continuation
reply explicitly authorized only the four unrun queries with all earlier final
outcomes preserved. The same primary experiment ID and frozen settings apply.
No original candidate is replaced, historical result deleted, D3 round assigned,
or S21 panel selected by this candidate run. Dates in saved records are actual
2026-10-19 timestamps, despite the experiment ID's creation date of 2026-10-18.

## 5. Design choices beyond the specification

Routine engineering: reuse Granite's operational helpers with Ministral identity,
Mistral family and output paths; agent ID Ministral3-8B; one launcher invocation
per episode with status/order/identity/hash checks. The continuation uses the
80-file stopped snapshot and exactly the remaining frozen four-query suffix.
The diagnostic summary was updated from the 16-record checkpoint to all 20;
stopped derivations were retained separately. No new scientific threshold,
method, template, argument coercion or parser repair was introduced.

## 6. Items for manual inspection

- Four preserved parse failures and the 120-second read-timeout event in failure-inspection.json.
- BH2_03760: three OFF_QUESTION/PATH_INVALID answers despite SUCCESS.
- BH2_05686: 14 ALT_VALID/SUPPORTED answers plus one GOLD/SUPPORTED; inspect
  the distinction between benchmark GOLD and a valid supported alternative.
- BH2_05366: SUCCESS with no answers after 24 native calls, hence not competent.
- The CPU/GPU placement and near-ceiling prompt counts when interpreting timing
  and formatting failures. No 16K comparison or S21 work was performed.

This completes the requested Ministral candidate block. No other candidate was run.
