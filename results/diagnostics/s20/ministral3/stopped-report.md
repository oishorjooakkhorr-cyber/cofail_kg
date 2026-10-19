# S20 Ministral 3 8B stop checkpoint (2026-10-19)

**Incomplete: 16/20 frozen queries saved.** The between-episode checker stopped at
`BH2_04425` after its saved `ERROR / CONNECTION`. Four queries remain unrun:
BH2_05366, BH2_05686, BH2_05843, BH2_06427.
The exact pinned list is also recorded in `stopped-integrity-proof.json`.
No final D3 verdict is assigned in the incomplete screening table. Even if all
four remaining queries succeed, SUCCESS can reach only 15/20 (75%), below D3's
90% requirement. Preserve every completed outcome; do not rerun the error.

## 1. Files created or changed

- This report, `docs/decision_log.md`, `docs/progress.md`, `tasks/plan.md`, `tasks/todo.md`.
- `results/runs/screening/primary-3060ti-20261018/`: one new write-once
  `Ministral3-8B.config.json` and 16 attempt-1 episode records.
- `results/diagnostics/screening/`: 16 new metric files and the cumulative table.
- `results/diagnostics/s20/ministral3/`: exact metadata, synthetic exchange,
  placement, full-suite log, operational helper copies, per-invocation logs,
  journal, summaries, per-query CSV, inspections and stop/integrity evidence.

No agent/launcher/evaluator source, tests, prompt, schema, frozen config, data or
scientific rule was changed. No prior result was replaced; no commit or push.

## 2. Tests and execution results

The unchanged suite passed **598 tests in 28.33 seconds** on the host. The initial
sandbox run had temporary-directory setup errors (438 passed, 160 errors). An
isolated `-x` reproduction identified pytest's inability to create its numbered
temporary directory; host execution with a workspace basetemp passed completely.
No test, application fix, skip or deselection was introduced.

Exact identity: `ministral-3:8b`, family Mistral, installed 8.9B Q4_K_M, digest
`1922accd5827ebe6829e536369195db25eaf664528dc66206d646ea3bb386b71`.
Ollama 0.40.4, primary RTX 3060 Ti 8 GB. Native tools advertised; synthetic
`add(2,3)` used integer arguments and returned 5, with no nonempty thinking.
No nonempty assistant thinking field appears in the 16 official records.

Screening settings (protocol section 9.1): think=false, temperature=0, seed=42,
num_ctx=8192, num_predict=4096, page_size=50, budget=30, episode timeout=600 s,
request timeout=120 s. Prompt/tool/source/input identities remain pinned.
Provenance: HEAD a7ae7539d705a643b1725114598f075db5846efa-dirty.

Placement: `/api/ps` size=6591967394, size_vram=5549137591 bytes; CLI reports
16%/84% CPU/GPU at context 8192. This is partial offload, and may affect timing;
the exact text-layer split was not established by the CLI percentage. The
post-stop metadata check retained the same placement and exact digest.

Ran 16 separate `--max-new 1` invocations in frozen order, each exiting zero
and saving one final record. The checker then exited nonzero as designed on
record 16's ERROR. No automatic retry, source/config repair or subsequent episode.

| Quantity | Observed in 16 saved episodes | D3 requirement for complete block |
|---|---:|---:|
| Well-formed / attempted calls | 155/155 (100%) | >=90% |
| SUCCESS | 11/16 (68.75%) | >=90% of all 20 |
| Competent queries | 7/16 (43.75%, provisional observed share) | >=40% of all 20 |
| Median episode wall | 70.374565 s | <=300 s |
| ERROR with OUT_OF_MEMORY | 0 | 0 |

Statuses: 11 SUCCESS, 4 PARSE_FAIL, 1 ERROR/CONNECTION, 0 TIMEOUT, 0 OOM.
All 155 attempts were native; zero TEXT_TOOL_CALL events. The 244 evaluated
answer items comprise 238 GOLD/SUPPORTED and six OFF_QUESTION/PATH_INVALID.
SUCCESS means valid final parsing and does not itself establish competence.
Median charged calls=9.5; no episode exhausted the 30-call budget.
Largest prompt_eval_count=8184, close to the frozen context ceiling.

Four parse failures: BH2_03619 omitted the required answers list after its one
re-prompt; BH2_03881, BH2_03991 and BH2_04003 left incomplete JSON. For example,
BH2_03991's last response had done_reason=length with prompt_eval_count=8184;
BH2_04003 had done_reason=length with prompt_eval_count=8095. These observations
support context pressure as a possible contributor, without changing the settings
or claiming it explains every failure. See `failure-inspection.json`.

BH2_04425 saved ERROR/CONNECTION after 139.070961 s: the next `/api/chat` request
hit `Read timed out. (read timeout=120)`. Six native KG calls had completed.
This is an HTTP request error, not the 600-second episode TIMEOUT or an OOM.
A read-only `/api/ps` check subsequently responded normally. The underlying
reason for the generation stall is unresolved; no retry or inference recovery
probe was run.

Report-only `--max-new 0` exited zero. A second report-only invocation with an
explicit before/after snapshot verifies all 80 official run-file hashes, including
all 63 prior files. All 122 protected identities and 43 pinned sources/inputs
match. The 16 journal hashes match saved records in the frozen prefix order;
all four remaining record paths are absent. Proof: `stopped-integrity-proof.json`.
The table remains complete=False with all pass/fail verdict cells blank.

## 3. Small real example and output

BH2_02033 completed SUCCESS in 12.610969 seconds with four well-formed native
calls. Its complete final output was:

```json
{"status": "answered", "answers": [{"id": "31332", "name": "myostatin-related muscle hypertrophy"}, {"id": "36432", "name": "congestive heart failure"}, {"id": "37659", "name": "heart failure"}]}
```

All three answers are GOLD/SUPPORTED. Both this record and BH2_00461 were checked
against raw tool results: final lists exactly match complete returned lists of
three and 21 items, respectively; neither was merely a fixed first-five list.
Proof: `first-two-inspection-proof.json`. These are stored experimental model
outputs evaluated against the frozen KG and benchmark.

## 4. Assumptions

The latest request authorizes this model's full S20 block; it adds a screened
candidate without replacing or erasing historical candidates, assigning D3
rounds or selecting S21 models. The existing experiment ID names the primary
host experiment, while new records retain actual 2026-10-19 timestamps.
The current full-block request was executed with automatic CPU/GPU placement
recorded and all frozen settings unchanged. The stop-on-ERROR checkpoint
prevents automatically proceeding to query 17.

## 5. Design choices beyond the specification

Routine engineering: reuse Granite's operational helpers with Ministral identity,
Mistral family and output-path substitutions; agent ID Ministral3-8B; one launcher
invocation per episode; hash/status/order/identity checks between invocations.
Adapt only the diagnostic summary to the 16-record stop checkpoint. Preserve the
transport failure as the final outcome and use read-only metadata for diagnosis.
No new scientific method, threshold, model template or argument coercion.

## 6. Items for manual inspection

- Inspect BH2_03619 and the three incomplete JSON finals in failure-inspection.json.
- Inspect BH2_04425's raw transport-error event and invocation log.
- Inspect BH2_03760: three OFF_QUESTION/PATH_INVALID answers despite SUCCESS.
- Review automatic 16%/84% CPU/GPU placement and near-ceiling prompt counts.
- Decide whether to continue only the four remaining queries, retaining all 16
  final records, including ERROR. Do not select models or change settings here.
