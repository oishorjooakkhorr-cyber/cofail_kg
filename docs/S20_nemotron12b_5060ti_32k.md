# Nemotron-Nano-12B-v2 (derived no-think) RTX 5060 Ti 32K S20 block — 2026-11-06

**D3 FAIL on competence: 20/20 SUCCESS, 0/20 competent.** Run ID
`nemotron12b-5060ti-32k-20261106`, tag `cofailkg/nemotron-nano-12b-v2-nothink:q4_k_m`
(digest `1e01b4a7…8eae`), derived from `hf.co/MaziyarPanahi/NVIDIA-Nemotron-Nano-12B-v2-GGUF:Q4_K_M`
(12.3B, Q4_K_M). Researcher-authorized candidate block; no panel change.

## Setup
num_ctx 32768, num_predict 8192, f16 KV, request 240 s, episode 600 s, budget 30, page size 50,
temperature 0, seed 42, think=false, Flash Attention on, Ollama 0.40.12. Unchanged P1, tools,
runner, parser, re-prompt, evaluators and D3. The source tag ignores think=false, so the 9B method
was reused (researcher approval): one edit to the embedded chat template default
(`enable_thinking=true` → `false`); 369 tensors and all other metadata verified identical
(`derive_model.py`). The derived file is 32 bytes larger than the source (one GGUF alignment step;
the 9B copy happened to stay the same size). Manifest mirrors the source tag (`make_manifest.py`),
so llama-server uses the embedded template. Runtime guards passed before every episode
(32768, f16 KV, 63/63 GPU, embedded template). Driver tests 13 passed.

## D3
|Criterion|Observed|Required|Verdict|
|---|---:|---:|---|
|Well-formed calls|50/50|>=90%|PASS|
|SUCCESS|20/20|>=90%|PASS|
|Competence|0/20|>=40%|FAIL|
|Median wall time|5.29 s|<=300 s|PASS|
|ERROR/OUT_OF_MEMORY|0|0|PASS|

Largest prompt 3109 of 32768; median tool calls 2; no budget hits; mean 6.9 s per query.

## What the traces show
- 13 episodes return `no_answer`; 99 submitted items: 1 GOLD, 98 OFF_QUESTION; none SUPPORTED.
- 6 of 50 calls failed (invented relations such as `side_effect`, `drug_side_effect`);
  4 episodes end right after a failed call.
- Hop 1 wrong in 6 episodes (H1_WRONG).

Same pattern as Nemotron-Nano-9B-v2 (0/20 competent, 3 median calls).

## Exploratory S23 (Qwen35-9B slot; `scripts/23_nemotron12b_substitution_example.py`)
Benchmark CF3 2 (BH2_05686, BH2_05843), CF4 0 (frozen panel: 2/2); all other totals 0.
