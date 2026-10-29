# Ministral3-8B: fresh RTX 5060 Ti 32K S20 reassessment

**2026-10-30: D3 PASS — 20/20 SUCCESS, 19/20 competent.**
This complete block was explicitly authorized after observing the same-host 16K
results. It is an outcome-informed context reassessment, preserving all historical
runs and acceptance. No S21 panel selection, extra condition or other model ran.

## Files and authorization

Run ID: `ministral3-5060ti-32k-20261030`. Diagnostics, launcher, preflight,
tests, metrics, paired CSV/JSON and integrity evidence are under
`results/diagnostics/s20/ministral3-5060ti-32k-20261030/`. Twenty immutable raw
attempt-1 records and configuration are under
`results/runs/screening-5060ti/ministral3-5060ti-32k-20261030/`.
Decision log, progress, plan/todo, screening status and handover are updated.
Unrelated Ministral speed scratch work is untouched and excluded from official evidence.

Commit `5584e3d` recorded executable changes and authorization before synthetic
or official inference. The tested 32K host launcher was adapted for Ministral,
reusing unchanged production runner, prompt, tools, parser and evaluators.
Source validation checks all baseline pins; new operational scripts are separately
pinned. Baseline scientific-source bytes are identical. Full suite: **601 passed,
2 existing missing-raw-BioHopR skips**; focused runner/screening/driver checks:
**90 passed**. Resume covers every final status and immutable run configuration;
identity/hash, isolation, 32K/cache/GPU and offline reporting checks passed.
CRLF-only Git whitespace warnings were retained without rewriting pinned evidence.

## Host, settings and measured placement

Pinned `ministral-3:8b`, agent Ministral3-8B, 8.9B Q4_K_M, digest
`1922accd5827ebe6829e536369195db25eaf664528dc66206d646ea3bb386b71`.
Existing PATH Ollama client/server **0.40.12**, unchanged from same-host 16K;
historical 3060 Ti experiments used 0.40.4. Ryzen 7 7700, Windows 11 Pro,
RTX 5060 Ti 16311 MiB, NVIDIA driver 610.88; Python at
`D:\cofailKG\.venv\Scripts\python.exe`. Before load: GPU used 876 MiB,
free 15175 MiB; system RAM 32626236 KiB, free 19671032 KiB.
No prior experiment/model/server was running, so no preceding model needed unloading.
Isolated localhost port 11435, explicit `OLLAMA_MODELS=D:\Models`, one sequence,
Flash Attention `true` and backend `--flash-attn on`, f16 K/V.

Scientific settings: num_ctx=32768 (baseline 16384), num_predict=4096,
temperature=0, seed=42, think=false, budget=30, page_size=50, request timeout=120s,
episode timeout=600s; standard single JSON re-prompt unchanged. Baseline identity,
ordered queries, input/source hashes, runtime and Flash Attention match. Only
context changes among scientific configuration values; run ID, provenance and
new operational source pins are intentional engineering changes. Evidence:
`baseline-comparison.json`. This is a paired execution, not a randomized or
replicated estimate of context effects.

Synthetic native add(2,3) returned 5 with no thinking. Actual context_length=32768,
API size_vram=size=9828931992 bytes; runtime logs confirm **35/35 layers on GPU**
and **4352 MiB f16 KV** (K=2176, V=2176). Baseline was 2176 MiB total KV,
size_vram=size=7513676184. All **41 runtime samples** pass guards. Sampled free
VRAM ranges 4538–4898 MiB and free RAM 9670944–18868896 KiB; these are samples,
not peak-memory bounds. After reporting, model unloaded and isolated server stopped.

## Execution and all five D3 criteria

One sequential invocation ran 2026-10-29 18:51:21–19:08:05 UTC,
**2026-10-30 00:51:21–01:08:05 Dhaka**. All twenty frozen queries ran in original
order; no crash, duplicate, replacement or experimental retry. Existing within-
episode re-prompts are protocol behavior. No ERROR, request timeout, episode
timeout, OOM or PARSE_FAIL occurred. Maximum response latency **83.584829s**,
below 120s. No thinking fields or TEXT_TOOL_CALL occurrences. Median charged
calls=8, maximum=20; no budget hit. Largest prompt_eval_count=19305.

| D3 criterion | Same-host 16K | New 32K | Required | 32K verdict |
|---|---:|---:|---:|---|
| Well-formed calls |179/179|180/180|>=90%|PASS|
| SUCCESS |18/20|20/20|>=90%|PASS|
| Competence |17/20|19/20|>=40%|PASS|
| Median episode wall |45.307066s|45.076370s|<=300s|PASS|
| ERROR/OUT_OF_MEMORY |0|0|0|PASS|

## Paired investigation

**BH2_03619 recovers parsing and competence.** Baseline first final reports
16278 prompt +106 completion=16384, length, ending in prose; its standard JSON
retry reports16364+20=16384 and leaves an incomplete fenced object. New first
final is prose at16686+764, stop. The same standard retry completes fenced JSON
at17353+304, stop. All **15 answers are GOLD/SUPPORTED**, benchmark precision1,
recall **15/179=8.38%**. Twenty charged tools include one missing drug_effect
relation. Recovery is real but leaves most valid targets unreturned.

**BH2_03879 recovers parsing and competence.** Baseline first final is prose at
15187+1197=16384, length; JSON retry16364+20=16384 is incomplete. New first final
has the same reported prompt15187 but generates4096 tokens, length: an output-
cap hit below the configured32K window, not evidence of32K exhaustion. The
standard JSON retry at19305+2261 ends stop with valid fenced JSON. All **113
answers are GOLD/SUPPORTED**, benchmark precision1, recall **113/271=41.70%**;
18 charged calls, no tool errors. Wall time166.547s is below the episode cap;
its maximum request remains below120s. Added context permits a complete retry
in this observed run while the first final still hits the output cap.

These two gains add **128 supported answers** and account for18->20 parsing
SUCCESS and17->19 competent queries. **All other eighteen supported-ID sets,
statuses, competence and answer labels are unchanged**. No new answer-set or
competence regressions occur; timing and token paths remain available in the
paired evidence, without implying every trace is byte-identical.

There are **635 scored answers:618 GOLD and17 ALT_VALID, all SUPPORTED**.
No OFF_QUESTION or invalid-support items were scored. Parsing SUCCESS remains
separate from competence: **BH2_03750** again returns valid no_answer after
incorrect side_effect relation guesses (eight failed calls of13), hence zero
competence. The correct drug_effect relation was not recovered. Its final
3069+17, stop, is identical to baseline and has ample configured context.

Competence is presence-based, not exhaustive correctness: BH2_03881 returns13
supported answers with5.2% recall; BH2_03619 has8.38%; BH2_03991 has11.28%.
BH2_05686 and BH2_05843 benchmark precision is6.67% and25%, respectively,
because14 and3 supported answers are ALT_VALID rather than benchmark GOLD;
this does not make those supported alternatives question-invalid.
Other retained tool errors: BH2_03434 guesses five nonexistent relations;
BH2_03760 has two missing drug_effect relations; BH2_03850 guesses
 drug_adverse_event; BH2_05366 guesses drug_disease. All count toward budget
and remain schema-well-formed. Full tool errors and supported IDs are preserved.

Only two new responses have done_reason=length: BH2_03879 (15187+4096) and
BH2_03953 (11062+4096). BH2_03953 had the same output-cap hit at16K and its JSON
retry succeeds with the same44 supported answers. Interpretation uses actual
content, output counts and successful retry, not length alone. Runtime logs
contain219 release entries with truncated=0 and no context-shift/n_discard lines;
reported counts and absence of these logs do not prove perfect retention of every
input token. Larger configured context is runtime-verified, not inferred from
completion counts alone.

Historical3060Ti8K/16K request timeouts and off-book longer-timeout diagnostics
remain separate. Their outcomes are never merged into this denominator. The
same-host baseline avoids the previous hardware/runtime change, but single
executions do not isolate every scheduling or cache effect. No hardware-only
claim, longer-timeout replay or tuning was performed. The small median-time
difference is not a robust speed estimate.

## Integrity, example and engineering choices

Offline reporting ran with server stopped and Ollama API calls replaced by a
failing guard; exit0 reproduces all metrics and D3. All **1682 historical files,
21 new config/records and50 source/input pins** retain their hashes. Twenty unique
attempt-1 records are sequential in frozen order, with identical initial messages
versus both same-host16K and3060Ti history. Historical acceptance and failed
records are untouched. Evidence: final-validation.json and final-run-hashes.json.

Small real example: BH2_02033 returns IDs31332,36432,37659; three GOLD/SUPPORTED,
benchmark precision/recall1. Full final JSON and raw trace are retained.

Assumption: explicit user authorization governs this separate32K context
reassessment and scoped publication; it does not choose an S21 panel.
Routine engineering choices: adapt tested launcher, unique roots, isolated server,
all-status resume, immutable hashes, per-episode memory/runtime samples, paired
trace inspection and network-forbidden reporting. No new scientific method,
threshold, prompt, parser, evaluator or extra experiment.
Manual inspection: two recovered finals, remaining BH2_03750 no_answer,
BH2_03881 low recall, BH2_03879/BH2_03953 output-cap hits, and ALT_VALID labels.

## Complete paired table

|Query|16K status/supported|32K status/supported|32K benchmark precision|32K benchmark recall|32K charged calls|32K wall seconds|
|---|---|---|---:|---:|---:|---:|
|BH2_00461|SUCCESS/21|SUCCESS/21|1.0|1.0|4|10.411132|
|BH2_02033|SUCCESS/3|SUCCESS/3|1.0|1.0|4|5.998976|
|BH2_03434|SUCCESS/32|SUCCESS/32|1.0|0.9696969696969697|9|39.838984|
|BH2_03619|PARSE_FAIL/0|SUCCESS/15|1.0|0.08379888268156424|20|72.485853|
|BH2_03750|SUCCESS/0|SUCCESS/0|None|0.0|13|24.022894|
|BH2_03760|SUCCESS/57|SUCCESS/57|1.0|0.4523809523809524|13|70.496368|
|BH2_03762|SUCCESS/47|SUCCESS/47|1.0|0.26857142857142857|8|63.542961|
|BH2_03850|SUCCESS/67|SUCCESS/67|1.0|0.9571428571428572|8|79.411914|
|BH2_03856|SUCCESS/65|SUCCESS/65|1.0|0.8666666666666667|6|57.714521|
|BH2_03879|PARSE_FAIL/0|SUCCESS/113|1.0|0.41697416974169743|18|166.546748|
|BH2_03881|SUCCESS/13|SUCCESS/13|1.0|0.052|11|55.329255|
|BH2_03953|SUCCESS/44|SUCCESS/44|1.0|0.3076923076923077|11|108.648270|
|BH2_03991|SUCCESS/15|SUCCESS/15|1.0|0.11278195488721804|7|30.366490|
|BH2_04003|SUCCESS/40|SUCCESS/40|1.0|0.28169014084507044|8|54.650093|
|BH2_04007|SUCCESS/30|SUCCESS/30|1.0|1.0|11|42.631575|
|BH2_04425|SUCCESS/50|SUCCESS/50|1.0|0.6666666666666666|6|47.521165|
|BH2_05366|SUCCESS/1|SUCCESS/1|1.0|1.0|5|9.500186|
|BH2_05686|SUCCESS/15|SUCCESS/15|0.06666666666666667|1.0|7|25.505755|
|BH2_05843|SUCCESS/4|SUCCESS/4|0.25|1.0|7|15.909287|
|BH2_06427|SUCCESS/3|SUCCESS/3|1.0|1.0|4|6.381499|
