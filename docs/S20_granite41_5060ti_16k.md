# Granite41-8B fresh RTX 5060 Ti 16K S20 - 2026-10-29

**D3 PASS. All twenty outcomes are SUCCESS; 16/20 queries are competent.**
This is a fresh host/runtime condition, not a resumption or replacement of the
stopped 3060 Ti block. No errors, HTTP read timeouts, episode timeouts, OOM or
PARSE_FAIL occurred. No completed outcome was retried; no extra experiment ran.

## 1. Files created or changed

New diagnostics, launcher/tests/preflight, twenty metrics, paired trace inspection,
runtime logs and hash proof: results/diagnostics/s20/granite41-5060ti-16k-20261029/.
Twenty attempt-1 records and config: results/runs/screening-5060ti/granite41-5060ti-16k-20261029/.
Project report, decision log, progress, screening status, plan/todo and handover updated.
Unrelated Ministral speed scratch work and all historical results are preserved.

## 2. Tests, preflight, execution and D3

Launcher/authorization commit fe0aab2 preceded all inference. Reused the tested
Gemma new-host driver and unchanged production runner/evaluators. 596 tests
passed, with the two existing missing-raw-BioHopR skips; 45 focused tests passed.
Frozen screening inputs, KG nodes/edges, prompt, tools and ordered twenty queries
were pinned. Source relocation checks allow only historical CRLF differences,
then pin actual current bytes. All-status resume preserves the original run commit.

Model ibm/granite4.1:8b, agent Granite41-8B, 8.8B Q4_K_M weights; digest
444af1c4b2fedd6b54041aca558e7300b0b3d5c0468c44619126240323ba2852.
Installed user-PATH Ollama client/server 0.40.12, without version change;
historical runtime was 0.40.4. Server explicitly uses D:\Models, port11435,
f16 KV, Flash Attention on, one sequence. No model experiment/server was running
before preparation; the new model was unloaded and its isolated server stopped
after the block. Host RTX5060Ti 16311MiB, driver610.88, Ryzen7 7700, Windows11.
Full host memory and OS evidence is in host.json.

Settings: think=false, temperature0, seed42, num_ctx16384, num_predict4096,
budget30, page_size50, request timeout120s, episode timeout600s. Prompts, tools,
parsers, evaluator and all five D3 thresholds remained unchanged.
Synthetic native add(2,3) returned5 with no thinking. Actual context16384,
size_vram=size=8055475404 bytes, all41/41 model layers on GPU, and K/V f16
(1280MiB each, 2560MiB cache) are corroborated by runtime logs. All41 during-block
samples passed context/cache/identity/full-residency guards.

| D3 criterion | Observed | Required | Result |
|---|---:|---:|---|
| Well-formed calls |236/236 (100%)|>=90%|PASS|
| SUCCESS |20/20 (100%)|>=90%|PASS|
| Competence |16/20 (80%)|>=40%|PASS|
| Median episode wall |38.870718s|<=300s|PASS|
| ERROR/OUT_OF_MEMORY |0|0|PASS|

One sequential launcher invocation ran 14:41:35.453975-14:54:53.979449 UTC
(20:41:35-20:54:53 Dhaka). Maximum individual response latency69.404479s,
below the120s read deadline. There were no TEXT_TOOL_CALL or thinking messages.
Two queries hit the tool budget. Largest reported prompt16196; runtime token
accounting is retained as reported, not assumed to prove unused headroom.

Of659 scored answer items,593 are GOLD/SUPPORTED,17 ALT_VALID/SUPPORTED and49
OFF_QUESTION/PATH_INVALID:610 supported items across16 competent queries.
Valid final JSON, well-formed native calls and supported answers are distinct.

### Historical comparison

Complete old8K:20/20 SUCCESS,14/20 competent,217/217 well-formed calls,
median61.3250475s, D3 PASS. New full16K:20/20 SUCCESS,16/20 competent,236/236,
median38.870718s, D3 PASS.

Old3060Ti16K remains **incomplete**:15 saved outcomes,6 SUCCESS and9
ERROR/CONNECTION, each explicitly recording Read timed out(read timeout=120).
No episode TIMEOUT or OOM was recorded. The final five have no saved outcome;
no full-block verdict or competence is assigned. Missing responses are not
reconstructed, and CONNECTION is not interpreted as an internet outage.
All nine formerly timed-out queries now complete SUCCESS:
BH2_03619,BH2_03762,BH2_03850,BH2_03856,BH2_03879,BH2_03881,BH2_03953,
BH2_03991,BH2_04003. Some remain noncompetent despite recovering completion.

### All materially changed outcomes versus complete8K

The paired JSON preserves raw final JSON, final-turn token counts/reasons,
failed tools, request latencies, labels and full token sequences for every
query. The stopped block's missing rows are UNSAVED and its competence is
unscored, never fabricated. Nine queries change supported sets or labels:

|Query|Supported8K -> new|New scored items|Charged tools|Final turns(prompt,completion,reason)|
|---|---:|---:|---:|---|
| BH2_03619 | 84 -> 50 | 50 | 16 | [(9761, 1534, 'stop'), (11323, 786, 'stop')] |
| BH2_03750 | 0 -> 44 | 44 | 10 | [(3368, 1085, 'stop'), (4481, 725, 'stop')] |
| BH2_03762 | 50 -> 1 | 2 | 8 | [(6413, 171, 'stop'), (6612, 42, 'stop')] |
| BH2_03850 | 67 -> 67 | 67 | 10 | [(5092, 3647, 'stop'), (8767, 1074, 'stop')] |
| BH2_03856 | 65 -> 66 | 66 | 6 | [(4217, 2831, 'stop'), (7076, 815, 'stop')] |
| BH2_03879 | 0 -> 0 | 11 | 30 | [(10790, 1050, 'stop'), (11868, 145, 'stop')] |
| BH2_03881 | 0 -> 0 | 4 | 12 | [(9304, 1927, 'stop'), (11259, 57, 'stop')] |
| BH2_03953 | 0 -> 99 | 99 | 8 | [(7029, 3873, 'stop'), (10930, 1227, 'stop')] |
| BH2_04003 | 40 -> 64 | 64 | 20 | [(16196, 1301, 'stop'), (14893, 1033, 'stop')] |

BH2_03619 coverage declines84->50; guessed adverse_event fails, as do two
missing drug_effect relations. BH2_03750 gains competence with44 supported
items despite four failed guessed relations. BH2_03762 declines50->1 supported;
its final JSON contains Edema and Vascular skin abnormality, the latter an
OFF_QUESTION shortcut. A drug_side_effect call failed. BH2_03850 retains67
supported items but the supported ID set changes. BH2_03856 grows65->66.
BH2_03953 gains competence with99 supported items and no tool errors.
BH2_04003 grows40->64 supported, with one missing drug_effect relation.

All four noncompetent new queries: BH2_03879 returns11 drug IDs instead of
phenotypes after exhausting30 calls; BH2_03881 returns4 drug IDs after a
missing drug_effect relation; BH2_03991 returns3 drug IDs after repeated
missing/guessed relation errors. Their evaluator reasons are wrong target type
and hop count. BH2_05366 returns30 direct gene-disease shortcut answers after
an invalid page request. All49 off-question items have invalid support.
No formatting or setting adjustment was made to improve these outcomes.

Observed: no timeouts under verified full-GPU16K; faster median than old8K;
completion recovers on all nine old16K timeout queries. This supports feasibility
of this tested host/runtime condition. It does not isolate why: host hardware,
CPU/RAM/driver and Ollama runtime changed together. The old offload samples
alone did not prove causation; there is no replicated hardware-only control.

Offline report ran with server stopped and Ollama API calls replaced by a
failing guard; it exited zero and reproduced all metrics. All1388 historical
hashes,21 new run/config hashes and46 source/input pins match. Exactly20 unique
attempt-1 records, sequential timestamps and identical initial messages versus
old8K and all15 saved old16K episodes were verified. Historical acceptance,
metrics, manifests and failed outcomes were preserved.

## 3. Small real example

BH2_02033 returned IDs31332,36432,37659 (myostatin-related muscle hypertrophy,
congestive heart failure, heart failure); all three are GOLD/SUPPORTED.
Full final JSON is retained in paired-inspection.json and the raw episode.

## 4. Assumptions

Explicit authorization covers this fresh complete block and scoped publication.
The interrupted preparation had not launched inference; no experiment overlapped.
Historical incomplete outcomes remain incomplete. No S21 selection is implied.

## 5. Design choices beyond specification

Routine engineering only: adapt existing tested driver/preflight, new run ID,
isolated server/output paths, immutable source/history pins, per-episode runtime
samples, network-forbidden offline report, paired raw-trace inspection. No new
scientific gate, threshold, evaluator rule or literature method.

## 6. Manual inspection and publication

Inspect four noncompetent valid-JSON episodes, BH2_03762's loss of coverage,
all nine former request-timeout recoveries, and the raw token/context evidence.
Publication and exact Drive checksum status will be recorded after completion.
