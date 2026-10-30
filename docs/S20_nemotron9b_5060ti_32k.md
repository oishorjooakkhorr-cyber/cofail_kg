# Nemotron-Nano-9B-v2 (derived no-think) RTX 5060 Ti 32K S20 block — 2026-10-30

**D3 FAIL on competence: 20/20 SUCCESS, 0/20 competent.** Run ID
`nemotron9b-5060ti-32k-20261030`, tag `cofailkg/nemotron-nano-9b-v2-nothink:q4_k_m`
(digest `c0c59955…bb13d`). Researcher-authorized candidate block; no panel change.

## Setup
num_ctx 32768, num_predict 8192, f16 KV, request 240 s, episode 600 s, budget 30,
page size 50, temperature 0, seed 42, think=false, Flash Attention on, Ollama 0.40.12.
Unchanged P1, tools, runner, parser, re-prompt, evaluators and D3. The shipped template
ignores think=false, so the model is an edited GGUF copy: only the embedded chat
template's default `enable_thinking=true` → `false`; 341 tensors and all other metadata
verified identical (`derive_model.py`). `ollama create` assigned the built-in
`nemotron-3-nano` (ChatML) renderer, so the manifest mirrors the source tag
(`make_manifest.py`); the two failed import attempts are kept in `attempt1-*`/`attempt2-*`.
All runtime guards passed before every episode (32768, f16 KV, 57/57 GPU, embedded
template in use, no thinking). Driver tests 13 passed; full suite 634 passed, 2 skipped.

## D3
|Criterion|Observed|Required|Verdict|
|---|---:|---:|---|
|Well-formed calls|60/60|>=90%|PASS|
|SUCCESS|20/20|>=90%|PASS|
|Competence|0/20|>=40%|FAIL|
|Median wall time|5.64 s|<=300 s|PASS|
|ERROR/OUT_OF_MEMORY|0|0|PASS|

Largest prompt 3019 of 32768; median tool calls 3.0 (Qwen 8K f32: 9.0); no budget hits.

## What the traces show
- 14 episodes return `no_answer`; 6 return answers (61 items): 8 GOLD, 53 OFF_QUESTION,
  all PATH_INVALID — none SUPPORTED.
- 20 failed tool calls (invented relation names such as `gene_protein_disease`);
  13 episodes end immediately after a failed call with `no_answer`.
- 7 episodes expand only the start entity: e.g. BH2_04425 lists the disease's own
  phenotypes (`disease_phenotype_positive`) instead of drug side effects (SHORTCUT).

Same 20 queries, Qwen35-9B (8K f32 block): 18 SUCCESS, 14 competent, D3 PASS.

## Engineering choices (routine)
Edited GGUF copy at `.venv/nemotron-nothink/` (6.5 GB); hand-written manifest mirroring
the source; history pin excludes `ministral_speed`; synthetic probes before the block.
