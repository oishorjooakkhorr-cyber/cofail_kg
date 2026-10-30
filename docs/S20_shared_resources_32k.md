# Shared four-model 32K resource reassessment — 2026-10-30

**Tasks 1–3 complete: all 80 final episodes saved and evaluated offline.**
Execution was authorized by the researcher's instruction to complete the ordered
checklist from 914fe42. Gemma, Ministral and Granite pass D3; Qwen fails.
Ministral includes one host-sleep TIMEOUT. Qwen resumed seven unsaved queries
after an execution interruption and recovery of the pinned runtime. These limits
are disclosed below. Historical acceptance remains unchanged; S21 is unselected.

## Fixed comparison

Gemma4-E4B, Ministral3-8B, Granite41-8B, then Qwen35-9B; twenty original screening
queries per model in original order. Same-host 32K baseline weights/digests and
Ollama 0.40.12 retained. Context 32768, output cap 8192, request deadline 240s,
episode deadline 600s, temperature 0, seed 42, think=false, budget 30, page size 50.
P1, tools, finalization, exact single JSON re-prompt, parser and D3 unchanged.
This compares a resource package against each preceding 32K block: both the output
cap (4096→8192) and request deadline (120→240s) change. It is outcome-informed
reassessment on already inspected questions, not independent confirmation.

Executable checkpoint: 61be26f. Four-model preflight/manifest checkpoint: 6d442e0.
Immutable manifests and source/input/history hashes are under
`results/diagnostics/s20/shared-resources-32k-20261030/`.
Raw episodes and configurations are under ignored `results/runs/screening-5060ti/`
with run IDs `<model>-5060ti-32k-resources-20261030`.

Verification: production suite 599 passed, two existing missing-raw-BioHopR skips;
focused launcher/runner/client/trace/leakage and four baseline guards 221 passed.
Python compilation and pip check passed. All four synthetic add(2,3) tool/result
checks passed before official inference, with verified 32K, f16 and full GPU
residency, effective Flash Attention and unchanged Gemma speculative settings.
The idle user's Ollama tray server remains separate from isolated port 11435.
Every saved final status is immutable, including failed outcomes; guard failures
stop execution. Evaluation occurs offline after each isolated server stops.

## All five unchanged D3 criteria

|Model|Valid calls (>=90%)|SUCCESS (>=18/20)|Competence (>=8/20)|Median seconds (<=300)|OOM (0)|D3|
|---|---:|---:|---:|---:|---:|---|
|Gemma4-E4B|188/188|20/20|16/20|10.777069|0|PASS|
|Ministral3-8B|180/180|19/20|18/20|44.5842285|0|PASS|
|Granite41-8B|233/233|20/20|16/20|36.901580|0|PASS|
|Qwen35-9B|301/301|14/20|13/20|28.2654795|0|FAIL: SUCCESS|

Status totals:73 SUCCESS,6 PARSE_FAIL,1 TIMEOUT; no ERROR/OOM. All six parse
failures are Qwen; the timeout is the interrupted Ministral episode described
below. SUCCESS is valid final JSON (including no_answer); competence is at least
one supported question-valid answer. Neither means a complete or fully correct
answer. The same-host preceding32K results were20/16,20/19,20/16,13/12
(SUCCESS/competent) in the same model order. Denominators are never stitched.

## Paired answer quality and persistent failures

|Model|Supported items: baseline → new|OFF_QUESTION: baseline → new|PATH_INVALID: baseline → new|
|---|---:|---:|---:|
|Gemma|729 →737|60 →60|80 →80|
|Ministral|635 →589|0 →0|0 →0|
|Granite|610 →610|74 →74|74 →74|
|Qwen|422 →658|0 →0|0 →0|

Gemma changes only BH2_03879 (86→88 supported answers,+2) and BH2_04003
(74→80,+6); no supported IDs are lost. All20 status/competence indicators are
unchanged. Existing incomplete-answer,wrong-target and shortcut failures remain;
extra output room is not a navigation fix.

Ministral changes BH2_03879 (113→111 supported answers,two lost) and the
sleep-interrupted BH2_03953 (44→0,TIMEOUT). The two-answer loss is separate
from the host interruption; it must not be attributed to sleep. The other18
supported sets and label counts are unchanged. No wrong-target answers appear.
This block does not establish an improvement over its20/20,19-competent baseline.

Granite has identical supported-ID sets,statuses,competence and label counts on
all20 questions. Wrong-target/shortcut failures and74 PATH_INVALID answers persist.
The resource increase produces no observed answer-quality gain for this model.

Qwen changes only BH2_03881: PARSE_FAIL→SUCCESS and0→236 supported question-valid
answers; the other19 supported sets and labels are unchanged. Competence12→13
and SUCCESS13→14 improve, but the model needs18 SUCCESS to pass D3. More output
helps one large answer without resolving all formatting/context failures.

Complete per-query precision,recall,failed tool calls,final outputs and supported
ID gains/losses are preserved in each model's paired-inspection.json. Macro
precision/recall in comparison.json average over20 questions with missing values
treated as zero; they are descriptive query averages,not pooled answer accuracy.
No answer was repaired or selected from an earlier attempt.

## Qwen's six retained parse failures

P/C are reported prompt/completion counts for the first final and the single
allowed re-prompt. These counts do not prove every original input token survived.

|Query|First final P/C|Re-prompt P/C|Observed limit|
|---|---:|---:|---|
|BH2_03619|20108/151|20287/56|Below both caps; finalization/formatting failure persists|
|BH2_03856|23915/8192|32136/632|Output cap,then total32768 on retry|
|BH2_03879|29114/3654|32750/18|Both responses reach total32768|
|BH2_03953|11219/5008|16255/320|Output cap no longer binds; formatting still fails|
|BH2_03991|18802/6147|24977/112|Output cap no longer binds; formatting still fails|
|BH2_04003|32061/707|32749/19|Both responses reach total32768|

The first, fourth and fifth failures have remaining token room: larger capacity
alone does not guarantee valid JSON. Three other failures reach the32K boundary
on the re-prompt. The single existing re-prompt is retained exactly; native calls
on that final turn are ignored/logged by the unchanged runner. There is no extra
retry,format repair or P2 rescue. Stop tuning on these inspected questions and
prepare a separate capacity/interaction decision before further official changes.

## Runtime/context and integrity proof

|Model|Max prompt|Max completion|Length responses|At8192 output cap|Reported P+C>=32768|
|---|---:|---:|---:|---:|---:|
|Gemma|29500|7183|0|0|0|
|Ministral|21298|6090|0|0|0|
|Granite|18192|3873|0|0|0|
|Qwen|32750|8192|6|1|5|

All saved responses have empty/absent thinking. Per-response and final/retry
headroom is in paired-inspection.json; server discard/shift/truncation lines are
in context-events.json and context-pressure-summary.json. The former intentionally
retains all matching lines,including truncated=0; it is not a count of failures.
Qwen logs also retain its canceled in-flight query14 and blocked0.40.13 startup.

Offline checks verify1,829 preceding scientific files unchanged,54/53/53/54
source/input pins respectively,21 raw/configuration files per new model (84 total),
original query order,identical initial P1/user messages and sequential saved
episode timestamps. Runtime samples total42/42/42/44; Qwen's additional samples
include interruption/resume. All ps/cache/GPU guards pass. No runtime/source
guard was weakened. Isolated model/server was unloaded/stopped before each
offline evaluation. Final host check finds only the user's tray app/server;
GPU free14848MiB at that sample. Sampled memory is not a peak-memory guarantee.

Raw server logs retain their native whitespace/line endings. Git whitespace
warnings on those evidence files are preserved rather than rewriting pinned
bytes; source/document whitespace checks are separate. Raw episodes/configs are
ignored by Git and hashed; this execution has not uploaded or published them.

## Host interruption retained

Windows power events confirm sleep during Ministral query BH2_03953 (query12),
from2026-10-30 13:04:55.699 to14:29:04.632 Dhaka, approximately84 minutes.
The unchanged runner saved TIMEOUT, with episode timestamps13:03:21.671908 to
14:29:50.317090. That final record remains in the twenty-query denominator;
there is no retry, replacement or timing correction. Sleep evidence is retained
in `host-suspension.json`. The interruption is infrastructure contamination,
not evidence that the model itself needed this elapsed time. Remaining questions
continue in manifest order after wake with normal runtime/source guards.
Any mechanical D3 result must disclose this interruption; the block cannot be
described as twenty uninterrupted executions under normal host operation.

## Qwen interruption, runtime recovery and identity check

The execution process exited1073807364 during Qwen query14 BH2_04003; only the
first13 final records existed. Original server logs retain the canceled in-flight
request. A later resume found installed Ollama0.40.13 instead of pinned0.40.12:
the version guard stopped before any new screening request. Its cleanup path
also raised UnboundLocalError for the not-yet-assigned synthetic evidence name;
the owned isolated server still terminated. Pinned executable bytes were retained.

The existing Downloads/OllamaSetup.exe is version0.40.12 with a valid Ollama Inc.
Authenticode signature. Extracted and verified its installer checksums without
running setup, selected AMD64 binaries and excluded ARM64, and stored an isolated
runtime under .venv/ollama-0.40.12. No installed app, global PATH, model bytes or
system configuration changed. The resumed shell alone prepends this runtime to
PATH. Evidence: runtime-restoration.json, including installer/executable/library
SHA-256 values. The [extractor release](https://github.com/UserUnknownFactor/innoextract_win/releases/tag/670)
supports the installer's6.7.0 format; its archive SHA-256 matched the published
value. Runtime recovery is a relocation of the pinned0.40.12 distribution, not
permission to continue under0.40.13. New synthetic evidence and runtime guards
passed before resuming the first unsaved query. No completed record was retried.

Researcher also requested a model-identity comparison: original3060Ti saved
show.json and current5060Ti /api/show have identical model_info,details and
capabilities. Original3060Ti tags.json,5060Ti manifest and current /api/tags all
report qwen3.5:9b digest
56671c2ab9385f9cfcb404638e32cd62d88e3501d44822208363c010179a3c90,
9.0B,Q4_K_M. Proof:qwen-model-identity-comparison.json. This read-only check
used the installed0.40.13 API and sent no inference request. Model identity is
unchanged; historical differences in host,context,runtime and GPU placement remain.

## S21 sizing evidence (no final configuration selected)

Original S3 population: all 7,633 BioHopR two-hop rows, twelve relation types.
`results/diagnostics/biohopr/answer_sizes.csv` ALL/list_length p90=102, corroborated
by summary.json. `src/cofail_kg/data/diagnostics.py` defines answer-list length as
len(row['answer']) and uses NumPy's linear percentile method. This is the original
population, not the twenty screening questions or a selected relation subset.
Protocol output floor: max(4096,next_power_of_two(25×102))=4096. The experimental
8192 cap exceeds that floor; it does not establish final S21 sizing by itself.

Final context selection remains separate: protocol §9.1 requires a power of two
at least 1.25 times the applicable largest observed prompt. Earlier Qwen32K
reached 32750: 1.25×32750=40937.5, which rounds up to 65536. The applicability of
reassessment counts and any amendment to the sizing procedure must be resolved
before S21; full-GPU f16 capacity at64K is not established for all four models.
No automatic64K/offload/cache quantization, P2 exploration or S21 freeze follows.
