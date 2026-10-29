# Granite41-8B: fresh RTX 5060 Ti 32K S20 reassessment

**2026-10-30: D3 PASS — 20/20 SUCCESS, 16/20 competent.**
This is a separate, outcome-informed context reassessment explicitly authorized
after the complete same-host 16K result. Historical runs and acceptance remain
unchanged. No other model, extra condition or S21 selection was started.

## Files, authorization and checks

Run ID: `granite41-5060ti-32k-20261030`. Diagnostics, committed launcher,
preflight/tests, twenty metrics, paired CSV/JSON, memory/context evidence and hash
proof are under `results/diagnostics/s20/granite41-5060ti-32k-20261030/`.
Twenty raw attempt-1 records and configuration are under the ignored
`results/runs/screening-5060ti/granite41-5060ti-32k-20261030/`.
Decision log, progress, plan/todo, screening status and handover are updated.
Unrelated Ministral speed scratch work is preserved and excluded from this experiment.

Commit **473e92c** records executable changes and authorization before synthetic
or official inference. Reused the tested 32K new-host launcher with Granite
identity, baseline and isolated roots. Production runner, prompt, tools, parser,
evaluators, frozen configs/data and D3 thresholds are unchanged. Full suite:
**601 passed, two existing missing-raw-BioHopR skips**; focused runner/screening/
driver checks: **90 passed**. Identity/hash refusal, isolation, all-final-status
write-once resume, actual32K, cache/GPU and offline reporting checks pass.
All baseline source pins match; new operational scripts are separately pinned.

## Host and scientific configuration

Model `ibm/granite4.1:8b`, agent Granite41-8B, 8.8B Q4_K_M; exact digest
`444af1c4b2fedd6b54041aca558e7300b0b3d5c0468c44619126240323ba2852`.
Existing PATH client/server **Ollama0.40.12**, unchanged from same-host16K;
historical3060Ti runs used0.40.4. Python at
`D:\cofailKG\.venv\Scripts\python.exe`; Ryzen7 7700, Windows11 Pro,
RTX5060Ti16311MiB, NVIDIA610.88. Pre-load GPU used782/free15269MiB;
system RAM32626236KiB/free21393992KiB. No prior experiment/model/server was
running, so no preceding model required unloading. Dedicated localhost11435,
explicit `OLLAMA_MODELS=D:\Models`, one sequence, f16 KV, Flash Attention
`true` and backend `--flash-attn on`; same configuration as baseline.

Only scientific configuration change: **num_ctx16384->32768**.
Retained num_predict4096, temperature0, seed42, think=false, budget30, page_size50,
request timeout120s, episode timeout600s and standard single JSON re-prompt.
Identity, ordered twenty inputs, all baseline source/input hashes, runtime and
Flash Attention match. Intentional engineering changes are run ID, provenance
and added operational pins (`baseline-comparison.json`). The manifest records
473e92c-dirty accurately because scratch/output files are present; executable
changes were committed. This is one paired execution, not a randomized or
replicated estimate of context effects.

## Measured preflight and placement

Native add(2,3) returned5 without thinking. Actual context_length32768,
API **size_vram=size=10773384396 bytes**, runtime **41/41 layers on GPU**.
Actual **5120MiB f16 KV**, K=2560/V=2560, compared with baseline2560MiB total
and API size8055475404. All41 during-block samples passed. Sampled free VRAM
4541–4888MiB and free RAM11186548–20249360KiB; these are samples, not peak bounds.
The model was unloaded and isolated server stopped after the block.

## Complete block and unchanged D3

One sequential invocation ran2026-10-29 19:25:21–19:38:29 UTC,
**2026-10-30 01:25:21–01:38:29 Dhaka**. Twenty unique attempt-1 outcomes in
original frozen order, sequential timestamps, no crash, replacement or retry.
All20 SUCCESS; no ERROR, read timeout, episode TIMEOUT, PARSE_FAIL or OOM.
Maximum response latency67.591140s, below120s. No nonempty thinking or
TEXT_TOOL_CALL. Median charged calls10; two budget hits (BH2_03760,BH2_03879).
Largest prompt18192; largest completion3873, below4096. All recorded responses
stop normally; no length termination or output-cap hit in this block.

|D3 criterion|Same-host16K|New32K|Required|32K verdict|
|---|---:|---:|---:|---|
|Well-formed calls|236/236|233/233|>=90%|PASS|
|SUCCESS|20/20|20/20|>=90%|PASS|
|Competence|16/20|16/20|>=40%|PASS|
|Median episode wall|38.870718s|37.384036s|<=300s|PASS|
|ERROR/OUT_OF_MEMORY|0|0|0|PASS|

## Paired investigation

All20 statuses and competence indicators are unchanged. **Nineteen supported-ID
sets are identical**; BH2_04003 exchanges two IDs without increasing coverage.
BH2_06427 adds25 wrong answers while retaining its three supported answers.
These are the only queries changing supported IDs or evaluator labels.
There are **684 scored items:593 GOLD,17 ALT_VALID and74 OFF_QUESTION**.
**610 are SUPPORTED**, unchanged in count from16K;74 are PATH_INVALID, up from49.
D3 therefore remains PASS while answer-level quality regresses on one query.

**BH2_03879,03881,03991: wrong target type persists.** They return11,4,3 drug
IDs instead of requested phenotypes, respectively. All are OFF_QUESTION/
PATH_INVALID; zero competence despite valid JSON. BH2_03879 again exhausts30
calls and returns the same drug set. BH2_03881 repeats a missing drug_effect
relation; BH2_03991 repeats missing/guessed relation errors. Larger context did
not correct these navigation/target-selection errors. Raw finals, paths and
all tool failures are in paired-inspection.json and individual metrics.

**BH2_05366: shortcut failure persists with fewer calls.** Baseline fetched
page1, requested an invalid page2, then fetched page1 again. New run calls only
inspect_entity and page1 disease_protein. The invalid page request disappears,
but the final thirty direct gene-disease shortcut answers remain exactly the
same, all OFF_QUESTION/PATH_INVALID. Valid JSON and fewer tools do not establish
question-valid support.

**BH2_03619 and BH2_03762: lost historical coverage is not restored.**
BH2_03619 retains the same50 supported IDs as same-host16K, recall27.93%, versus84
at historical8K. It repeats the adverse_event guess and two missing drug_effect
lookups. BH2_03762 retains Edema as its sole supported answer and the same
Vascular skin abnormality shortcut error: benchmark precision50%, recall0.57%.
Historical8K had50 supported answers. Compare the actual same-host IDs, not a
hybrid count that replaces this block's outcomes with older answers.

**BH2_03953: supported coverage retained.** Same99 supported IDs, precision1,
recall99/143=69.23%, same8 charged calls. Longest completion3873 remains below
4096 and ends stop; neither baseline nor new trace establishes an output-cap
failure on this query.

**BH2_04003: context handling changes, coverage does not grow.** Baseline first
final reports16196 prompt+1301 completion, stop. Runtime task30768 explicitly
starts n_ctx_slot16384/task.n_tokens16196, then performs a slot context shift:
**n_keep4,n_left16379,n_discard8189**; release reports n_tokens9307,truncated1.
Thus the API sum alone was not evidence of retained history. Its JSON retry
reported14893+1033, stop,64 supported answers.

New runtime task30768 starts n_ctx_slot32768/task.n_tokens16196; first final
reports16196+1968,stop, and JSON retry18192+772,stop. New log has no context-shift/
n_discard entries and270 release entries with truncated0. These observations
support absence of the measured baseline shift; they do not prove semantic
retention of every token or perfect recall. New final still has64 supported
answers, precision1/recall45.07%, but adds Alopecia23073 and Blindness24423 while
omitting Corneal ulceration24416 and Mydriasis24438. All four are supported GOLD
in their respective traces. See context-handling.json with original log line
numbers/spans. Removing observed context pressure did not increase this count.

**BH2_06427: new answer-quality regression despite continued competence.**
Baseline returned only Biotin,Lipoic acid,Gabapentin enacarbil. New run retains
these three but adds25 OFF_QUESTION/PATH_INVALID shortcut drugs; benchmark
precision falls100%->3/28=10.71%, recall stays100%. After a failed
 gene_protein_drug guess, new run also guesses gene_protein, explores direct
contraindication/off-label-use drug edges from disease39126, then retrieves the
correct drug_protein neighbors from protein7383. The final answer mixes those
direct shortcut drugs with the valid two-hop answers. Example Dicoumarol14143
has primary reason SHORTCUT via contraindication directly from39126. Eight
charged tools versus five at16K. This occurs at short prompts (final2573+455,
stop), not at a measured context boundary or output cap. Single deterministic-
setting executions do not establish a unique causal explanation for divergence.

Other supported sets, including partially recalled lists, are unchanged.
BH2_03760 remains competent with50 supported answers despite repeated failed
relations and exhausting30 calls. BH2_05686/BH2_05843 retain14/3 ALT_VALID items;
low benchmark precision there does not make supported alternatives invalid.
Parsing SUCCESS, competence and exhaustive correctness remain separate.

## Historical stopped evidence and limitations

Historical8K passed20 SUCCESS/14 competent. The3060Ti16K block is explicitly
**incomplete:15 saved outcomes,6 SUCCESS and9 ERROR/CONNECTION**, all nine
recording120s read timeouts. Five queries have no saved outcome; no full-block
D3 or competence is assigned and no response is reconstructed. This task does
not resume it or merge denominators. Historical placement/runtime changed
alongside hardware, so timeout recovery is not attributed solely to GPU hardware.

Same-host16K/32K runtime/settings match apart from the declared context amendment,
but these are single, post-result executions with changing machine/cache state.
A 1.49s median difference is not a replicated speed estimate. Additional context
fits and removes the observed04003 shift but provides no competence gain here;
wrong-target and shortcut failures persist and one answer-quality regression
appears. No setting, parser, prompt, output or failed outcome was repaired.

## Offline integrity, example and engineering choices

Report-only executed with server stopped and Ollama API replaced by a failing
guard: exit0, same metrics and D3. All **1755 historical hashes,21 new config/
records and50 source/input pins** match. Frozen query order and initial messages
match same-host16K and historical8K; old stopped block remains intact. Offline
paired CSV/JSON contains all20 token sequences,reasons,finals,tool errors,
supported IDs,precision/recall and timings.

Small real example: BH2_02033 returns31332,36432,37659, all GOLD/SUPPORTED with
benchmark precision/recall1. Full JSON remains in raw and paired evidence.
Assumption: explicit authorization covers this separate reassessment and scoped
publication, not an S21 panel. Routine engineering choices: adapt tested launcher,
unique roots, isolated server, immutable hashes, all-status resume, runtime/memory
samples and offline paired analysis. No new scientific method or threshold.
Manual inspection:06427 shortcut regression,04003 runtime shift and ID exchange,
four unchanged noncompetent queries,03762 very low recall and03953 retained99.

## All twenty paired outcomes

|Query|16K status/supported|32K status/supported|32K benchmark precision|32K benchmark recall|32K charged calls|32K wall seconds|
|---|---|---|---:|---:|---:|---:|
|BH2_00461|SUCCESS/21|SUCCESS/21|1.0|1.0|4|9.480187|
|BH2_02033|SUCCESS/3|SUCCESS/3|1.0|1.0|4|4.544968|
|BH2_03434|SUCCESS/33|SUCCESS/33|1.0|1.0|4|26.665784|
|BH2_03619|SUCCESS/50|SUCCESS/50|1.0|0.27932960893854747|16|54.284558|
|BH2_03750|SUCCESS/44|SUCCESS/44|1.0|1.0|10|35.716804|
|BH2_03760|SUCCESS/50|SUCCESS/50|1.0|0.3968253968253968|30|34.152488|
|BH2_03762|SUCCESS/1|SUCCESS/1|0.5|0.005714285714285714|8|11.537476|
|BH2_03850|SUCCESS/67|SUCCESS/67|1.0|0.9571428571428572|10|86.362890|
|BH2_03856|SUCCESS/66|SUCCESS/66|1.0|0.88|6|64.287511|
|BH2_03879|SUCCESS/0|SUCCESS/0|0.0|0.0|30|39.750077|
|BH2_03881|SUCCESS/0|SUCCESS/0|0.0|0.0|12|46.362225|
|BH2_03953|SUCCESS/99|SUCCESS/99|1.0|0.6923076923076923|8|96.825170|
|BH2_03991|SUCCESS/0|SUCCESS/0|0.0|0.0|11|40.220664|
|BH2_04003|SUCCESS/64|SUCCESS/64|1.0|0.4507042253521127|20|75.351904|
|BH2_04007|SUCCESS/30|SUCCESS/30|1.0|1.0|11|39.051268|
|BH2_04425|SUCCESS/60|SUCCESS/60|1.0|0.8|9|44.107937|
|BH2_05366|SUCCESS/0|SUCCESS/0|0.0|0.0|2|10.895116|
|BH2_05686|SUCCESS/15|SUCCESS/15|0.06666666666666667|1.0|10|21.725435|
|BH2_05843|SUCCESS/4|SUCCESS/4|0.25|1.0|18|16.477076|
|BH2_06427|SUCCESS/3|SUCCESS/3|0.10714285714285714|1.0|8|13.103137|
