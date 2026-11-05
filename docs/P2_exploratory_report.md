# EXPLORATORY — P2-draft prompt on six configurations, with §16 co-failure

**Status: exploratory side experiment.** Not a panel change, not a prompt change, not a gate
input. P1 remains the frozen prompt (`configs/frozen_hashes.yaml` unchanged; `prompts.py`
unchanged). Run ID `p2-explore-20261105`, date 2026-11-05. Researcher request: "use this p2 and
run the s23 again use 6 models — ministral, ornith, gemma, qwen 8k, qwen 16k and granite".

## 1. What was run
- **Prompt.** P2-draft = P1 with one rule changed (rule 3); every other line is byte-identical.
  P1: `3. When you are finished, reply with only this JSON object and nothing else:`
  P2: `3. When you are finished, your final message must be only this JSON object, with no other text`
  `   before or after it, and it must list every entity in your answer:`
  P2 template SHA-256 `8413d17eb3bd8302d0822163bdf7c4395f37c668374d95f4e2138c56ab611a35`.
  The swap is in-process only (`run_p2.py::use_p2`); every saved record has
  `prompt_version = "P2-draft:<sha>"` and its system message contains the P2 rule 3 (checked for 120/120).
- **Queries.** The same 20 screening queries as S20/S22 (`data/agent_inputs/screening.jsonl`).
- **Settings.** Each configuration uses its own earlier settings (researcher choice): temp 0,
  seed 42, think=false, budget 30, page 50, episode 600 s, Ollama 0.40.12 on port 11435.

  |Config|Model|num_ctx|num_predict|KV|request timeout|P1 baseline used below|
  |---|---|---:|---:|---|---:|---|
  |Ministral3-8B|frozen digest|32768|8192|f16|240 s|S22 (`smoke_single_v135`)|
  |Gemma4-E4B|frozen digest|32768|8192|f16|240 s|S22|
  |Granite41-8B|frozen digest|32768|8192|f16|240 s|S22|
  |Qwen35-9B-8K|frozen digest|8192|4096|f32|120 s|S22 (pilot config)|
  |Qwen35-9B-16K|frozen digest|16384|4096|f16|120 s|S20 `qwen35-5060ti-16k-20261029`|
  |Ornith15-9B|`ornith-1.5:9b` e5df7dcd…575e|32768|8192|f16|240 s|S20 `ornith15-5060ti-32k-20261031`|

- **Integrity.** 120/120 episodes saved, none overwritten, exit 0. Before every episode the run
  checked the hashes of all earlier records (`historical-hashes.json`) and the GPU (full
  offload, no other model loaded). The connection-refused lines in `run-console.txt` come from
  the free-port probe before each server start. Evaluators (S16–S19) and §16 code unchanged.

## 2. P1 vs P2 per configuration (same 20 queries)
"Competent" = SUCCESS with ≥1 valid SUPPORTED answer (D3 definition; denominator 20).
"D3 row" = the numerical D3 criteria computed by `aggregate_model`. This is not a D3 decision.

|Config|Competent P1→P2|SUCCESS P1→P2|D3 row P1→P2|Re-prompted P1→P2|Start-entity-only P1→P2|Hit ctx/output limit P1→P2|Median tool calls P1→P2|Budget hit P1→P2|Median answers (SUCCESS) P1→P2|
|---|---|---|---|---|---|---|---|---|---|
|Ministral3-8B|19→17|20→18|pass→pass|17→17|0→0|0→1|8→7.5|0%→5%|30→65|
|Gemma4-E4B|16→17|20→20|pass→pass|16→16|0→0|0→0|8→8|5%→5%|44→44|
|Granite41-8B|16→17|20→19|pass→pass|15→13|0→0|0→0|10→10.5|10%→5%|30→44|
|Qwen35-9B-8K|14→**6**|18→**9**|pass→**fail**|4→15|0→0|4→**14**|9→16|5%→35%|3→3|
|Qwen35-9B-16K|12→10|16→11|fail→fail|5→13|0→0|6→9|9.5→21.5|5%→40%|15→15|
|Ornith15-9B|11→12|18→**13**|pass→**fail**|20→20|**7→0**|2→4|12.5→29.5|15%→50%|3→33|

Failing D3 criteria under P2: Qwen35-9B-8K success 9/20 and competence 6/20; Qwen35-9B-16K
success 11/20; Ornith15-9B success 13/20 (needs ≥ 18/20).

### What changed, from the records
1. **Ornith: the start-entity collapse is gone (7 → 0), but it is replaced by parse failures
   (1 → 6).** Ornith still gets the re-prompt in 20/20 episodes. Its six P2 PARSE_FAILs are
   2 context-full final turns (BH2_03881, BH2_04003), 2 prose finals (BH2_03762 "I've exhausted
   my tool budget…"; BH2_03953 "I need to continue fetching page 4…") and 2 empty finals.
   Competence is 11 → 12, so the format gain does not turn into more correct answers.
2. **Qwen and Ornith explore much more under P2.** Median tool calls roughly double (Qwen 8K
   9 → 16, Qwen 16K 9.5 → 21.5, Ornith 12.5 → 29.5) and budget exhaustion rises to 35–50%.
   The records are consistent with these models reading "list every entity" as "fetch every
   page before answering". That reading is an inference from call counts, not something the
   models state.
3. **Qwen 8K fails because its context fills.** All 11 Qwen 8K PARSE_FAILs end with
   prompt + output = 8192 on the final turn (e.g. BH2_03619 prompt 8161 + 31 output tokens;
   the JSON breaks off inside its second answer). Under P1 in S22 the same configuration had 2 PARSE_FAILs,
   both empty finals. Qwen 16K: 3 of its 9 PARSE_FAILs are context-full and 6 are empty finals.
4. **The three 32K models are about the same.** Ministral and Granite list more entities per
   answer (median 30 → 65 and 30 → 44) without more tool calls. Ministral's largest prompt
   reached 32744/32768 (BH2_03881, PARSE_FAIL, context full).

### Per-query outcome (P1 → P2)
`correct v/n` = competent, v valid of n listed; `wrong` = SUCCESS but no valid SUPPORTED answer.
Full data: `results/diagnostics/p2_exploratory/p1_vs_p2.json` and `compare-console.txt`.

|Query|Ministral3-8B|Gemma4-E4B|Granite41-8B|Qwen35-9B-8K|Qwen35-9B-16K|Ornith15-9B|
|---|---|---|---|---|---|---|
|BH2_00461|correct → correct|correct → correct|correct → correct|correct → correct|correct → correct|correct → correct|
|BH2_02033|correct → correct|correct → correct|correct → correct|correct → correct|correct → correct|correct → PARSE_FAIL|
|BH2_03434|correct → correct|correct → correct|correct → correct|correct → PARSE_FAIL|correct → correct|correct → correct|
|BH2_03619|correct → correct|correct → correct|correct → correct|no answer → PARSE_FAIL|no answer → PARSE_FAIL|correct → correct|
|BH2_03750|no answer → PARSE_FAIL|correct → correct|correct → correct|correct → PARSE_FAIL|correct → correct|correct → correct|
|BH2_03760|correct → correct|correct → correct|correct → correct|wrong → PARSE_FAIL|correct → PARSE_FAIL|start only → correct|
|BH2_03762|correct → correct|no answer → no answer|correct → correct|correct → no answer|no answer → PARSE_FAIL|start only → PARSE_FAIL|
|BH2_03850|correct → correct|correct → correct|correct → correct|correct → correct|correct → correct|correct → correct|
|BH2_03856|correct → correct|correct → correct|correct → PARSE_FAIL|correct → PARSE_FAIL|PARSE_FAIL → no answer|start only → correct|
|BH2_03879|correct → correct|correct → correct|wrong → correct|PARSE_FAIL → PARSE_FAIL|PARSE_FAIL → PARSE_FAIL|ERROR → ERROR|
|BH2_03881|correct → PARSE_FAIL|wrong → correct|wrong → wrong|correct → PARSE_FAIL|no answer → PARSE_FAIL|PARSE_FAIL → PARSE_FAIL|
|BH2_03953|correct → correct|correct → correct|correct → correct|no answer → PARSE_FAIL|PARSE_FAIL → PARSE_FAIL|correct → PARSE_FAIL|
|BH2_03991|correct → correct|no answer → no answer|wrong → correct|PARSE_FAIL → no answer|PARSE_FAIL → PARSE_FAIL|start only → correct|
|BH2_04003|correct → correct|correct → correct|correct → correct|no answer → PARSE_FAIL|no answer → PARSE_FAIL|start only → PARSE_FAIL|
|BH2_04007|correct → correct|correct → correct|correct → correct|correct → PARSE_FAIL|correct → correct|start only → correct|
|BH2_04425|correct → correct|correct → correct|correct → correct|correct → PARSE_FAIL|correct → PARSE_FAIL|correct → wrong|
|BH2_05366|correct → wrong|wrong → wrong|wrong → correct|correct → correct|correct → correct|correct → correct|
|BH2_05686|correct → correct|correct → correct|correct → correct|correct → correct|correct → correct|start only → PARSE_FAIL|
|BH2_05843|correct → correct|correct → correct|correct → correct|correct → no answer|correct → correct|correct → correct|
|BH2_06427|correct → correct|correct → correct|correct → wrong|correct → correct|correct → correct|correct → correct|

## 3. §16 co-failure under P2 (all 15 four-of-six panels)
Frozen §16 code (`src/cofail_kg/evaluation/cofailure.py`), unchanged and applied as is. Panels
holding both Qwen configurations are flagged `same_weights_in_panel` (5 of 15). Those two
agents are not independent, because they are the same weights at two context sizes.

- **Question-level, grounded and hop-1-clean CF3/CF4 = 0 in all 15 panels.** No query has
  three agents sharing an OFF_QUESTION answer.
- **Benchmark CF^BH3 = 2 in all 15 panels; CF^BH4 = 0–2.** Both come from BH2_05686 and
  BH2_05843 (tag BOTH_AMBIGUOUS). The shared entities are ALT_VALID + SUPPORTED answers outside
  A*_q, i.e. a benchmark-ambiguity effect, as in the P1 S22 example.
- **Pairwise (§16.4), 15 pairs:** only Ministral3-8B–Gemma4-E4B is defined: 1/1, on BH2_05366
  (Ministral 29 and Gemma 30 OFF_QUESTION answers, intersecting). The other 14 pairs are NA
  (0/0), Qwen 8K–Qwen 16K included.
- **Caveat that dominates these numbers:** 9–15 of the 20 queries per panel have at least one
  technical failure (PARSE_FAIL/ERROR). Under the literal convention in the S23 report, a
  failed episode has an empty answer set, so it can never co-fail. Panels with Qwen 8K or
  Ornith therefore have fewer chances to show co-failure. The convention is still an open
  researcher question (`docs/S23_cofailure_report.md`).
- n = 20 screening queries. These counts say nothing about the 100-query pilot rates.

Output: `results/diagnostics/p2_exploratory/cofailure.json` (per panel, per query, with the
technical-failure agents listed).

## 4. For the researcher (no decision taken here)
1. P2 removes Ornith's start-entity collapse, but under P2 Ornith (13/20 SUCCESS) and both
   Qwen configurations fail the numerical D3 success criterion. Qwen 8K drops from 14 to 6 competent.
2. The extra exploration under P2 interacts with num_ctx: the smaller the context, the more
   P2 hurts (8K worst, 16K next, the 32K models are about the same). This bears on the Qwen §9.1
   decision and on any wording change to rule 3.
3. If a further prompt draft is wanted, "list every entity in your answer" is the phrase whose
   effect shows in the records. The format sentence alone ("only this JSON object, with no other
   text before or after it") was not tested separately. The prompt wording is your decision.
4. Earlier note, for the record: Ornith's P1 S20 D3 row was numerically a pass (18/20 SUCCESS,
   11/20 competent; `docs/S20_ornith15_5060ti_32k.md` line 3). Its open issue was the family
   (UNVERIFIED-qwen35-architecture) against D3's ≥3-families rule, not the D3 numbers.

## 5. Design choices beyond the specification (all routine engineering)
- Process-only prompt swap by patching `run_agent.P1_TEMPLATE/PROMPT_VERSION/prompt_sha256`
  inside `run_p2.py`, then passing the P2 hash as the approved hash. `prompts.py` is never written.
- One run ID for all six configurations; separate `<cfg>.config.json` snapshots; agent IDs
  `Qwen35-9B-8K` / `Qwen35-9B-16K` to keep the two Qwen runs apart.
- P1 baseline per configuration: S22 for the four frozen-panel configurations, the S20 block
  for Qwen 16K and Ornith (the only P1 runs of those settings).
- "Hit ctx/output limit" = any turn with prompt + completion ≥ num_ctx or completion ≥ num_predict.
- "Start-entity-only" = SUCCESS with exactly one answer equal to the start ID.
- Pairwise W_Q per agent taken from any panel containing it (W_Q does not depend on the panel).

## 6. Files
- `results/diagnostics/p2_exploratory/run_p2.py`, `test_run_p2.py` (3 tests),
  `compare_p1_p2.py`; consoles `preflight-`, `run-`, `report-`, `cofailure-`, `compare-console.txt`;
  `summary.json`, `cofailure.json`, `p1_vs_p2.json`, `historical-hashes.json`, `<cfg>/metrics/`,
  `<cfg>/final-run-hashes.json`, per-config server logs.
- Records: `results/runs/p2-exploratory/p2-explore-20261105/` (120 `__a1.json` + 6 config snapshots).
- Tests: `test_run_p2.py` + `tests/test_cofailure.py`: 45 passed.
