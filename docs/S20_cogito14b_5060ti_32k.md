# cogito:14b RTX 5060 Ti 32K S20 block (partial GPU offload) — 2026-11-06

**D3 PASS: 18/20 SUCCESS, 16/20 competent.** Run ID `cogito14b-5060ti-32k-20261106`,
tag `cogito:14b` (digest `d0cac86a…16e0`, Q4_K_M, 14.8B, architecture qwen2).
Researcher-authorized candidate block; no panel change.

## Setup
num_ctx 32768, num_predict 8192, f16 KV, request 240 s, episode 600 s, budget 30, page size 50,
temperature 0, seed 42, think=false, Flash Attention on, Ollama 0.40.12. Unchanged P1, tools,
runner, parser, re-prompt, evaluators and D3. Probe: no thinking capability, native tool calls,
Ollama Go template; used unmodified.

**Partial offload (researcher choice).** At 32K with f16 KV the model does not fit the 16 GB GPU;
Ollama places 47 of 49 layers on GPU (about 14.6 of 15.7 GB). Every other candidate ran fully on
GPU. The driver pins the 47/49 split; it held before every episode. Driver tests 16 passed.

## D3
|Criterion|Observed|Required|Verdict|
|---|---:|---:|---|
|Well-formed calls|228/228|>=90%|PASS|
|SUCCESS|18/20 (90%)|>=90%|PASS (at threshold)|
|Competence|16/20 (80%)|>=40%|PASS|
|Median wall time|51.20 s|<=300 s|PASS|
|ERROR/OUT_OF_MEMORY|0 OOM (2 ERROR, cause CONNECTION)|0 OOM|PASS|

Mean 72.7 s per query (24.2 min in total); median tool calls 10; no budget hits.
Largest prompt 20914 of 32768. Answers: 632 correct (615 GOLD, 17 ALT_VALID), 0 OFF_QUESTION.

Not competent: BH2_03953 and BH2_04425 ERROR/CONNECTION; BH2_03856 and BH2_03881 `no_answer`.

## The two ERROR episodes
Both are the 240 s request timeout firing during one long generation: the server log shows the
generation cancelled after about 5800 (BH2_03953) and 6100 (BH2_04425) tokens at about 27 tok/s.
Fully on GPU the model would generate faster and would likely reach the 8192-token output cap
before 240 s instead; the episode would then end differently (most likely PARSE_FAIL), which is
also not SUCCESS. Not verified. SUCCESS sits exactly at the 90% threshold, so this matters for
any later decision.

## Notes
Family not verified from a model card; Ollama reports architecture qwen2. If it is a Qwen
derivative it shares a family with the panel's Qwen slot (three-family D3 rule).

## Exploratory S23 (Qwen35-9B slot; `scripts/23_cogito14b_substitution_example.py`)
Benchmark CF3 2, CF4 2 (BH2_05686, BH2_05843; same as the frozen panel); all other totals 0.
