# ministral-3:14b RTX 5060 Ti 32K S20 block — 2026-11-06

**D3 PASS: 19/20 SUCCESS, 16/20 competent.** Run ID `ministral3-14b-5060ti-32k-20261106`,
tag `ministral-3:14b` (digest `4760c35a…dcf7`, Q4_K_M, 13.9B, architecture mistral3).
Researcher-authorized candidate block; no panel change.

## Setup
num_ctx 32768, num_predict 8192, f16 KV, request 240 s, episode 600 s, budget 30, page size 50,
temperature 0, seed 42, think=false, Flash Attention on, Ollama 0.40.12. Unchanged P1, tools,
runner, parser, re-prompt, evaluators and D3. Probe: no thinking capability, native tool calls,
41/41 layers on GPU (about 13.5 GB), Ollama ministral parser (as for Ministral3-8B); used
unmodified. Runtime guards passed before every episode. Driver tests 14 passed.

## D3
|Criterion|Observed|Required|Verdict|
|---|---:|---:|---|
|Well-formed calls|220/220|>=90%|PASS|
|SUCCESS|19/20 (95%)|>=90%|PASS|
|Competence|16/20 (80%)|>=40%|PASS|
|Median wall time|40.54 s|<=300 s|PASS|
|ERROR/OUT_OF_MEMORY|0|0 OOM|PASS|

Mean 77.3 s per query (25.8 min in total); median tool calls 10; no budget hits.
Largest prompt 30048 of 32768 (92%; above the 90% S22 re-selection level).
Answers: 1160 correct (1143 GOLD, 17 ALT_VALID), 11 OFF_QUESTION (all BH2_05366, SHORTCUT).

Not competent: BH2_02033 PARSE_FAIL; BH2_03434 and BH2_03750 `no_answer`; BH2_05366 only
OFF_QUESTION answers.

## Notes for inspection
- BH2_02033: the first assistant turn is a raw-text Mistral-format tool call
  (`inspect_entity[ARGS]{"entity_id": "19601"}`). The runner's TEXT_TOOL_CALL detection does not
  match this format, so it was handled as a malformed final answer; after the single re-prompt
  the model made a native tool call and the episode ended PARSE_FAIL. Counted as attempted,
  well-formed would be 220/221 (still PASS). No runner change made.
- Family Mistral, same as panel agent Ministral3-8B (three-family D3 rule).

## Exploratory S23 (Qwen35-9B slot; `scripts/23_ministral14b_substitution_example.py`)
Question CF3 1, grounded CF3 1, PCF_REL3 1, PCF_SHORTCUT3 1, all on BH2_05366 (R2_AMBIGUOUS):
Ministral3-14B, Gemma4-E4B and Granite41-8B share wrong answers (drug_protein → indication
query). Benchmark CF3 3, CF4 2 (frozen panel: 2/2). Pairwise agreement with Gemma4-E4B and
Granite41-8B: 1/1 each.
