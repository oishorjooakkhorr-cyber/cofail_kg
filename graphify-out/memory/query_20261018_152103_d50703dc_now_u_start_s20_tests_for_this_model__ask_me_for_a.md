---
type: "query"
date: "2026-10-18T15:21:03.134638+00:00"
question: "now u start s20 tests for this model, ask me for any decisions"
contributor: "graphify"
outcome: "useful"
source_nodes: ["S20 — Model screening", "D3 — Model selection (S20–S21)"]
---

# Q: now u start s20 tests for this model, ask me for any decisions

## Answer

Expanded from graph vocab: model screening think tools selection. Current source evidence supersedes the older graph snapshot. Researcher added qwen3.5:9b as a ninth candidate, kept the original eight, investigated GPU memory, then explicitly accepted 32/33 GPU-layer placement and authorized all 20 frozen S20 queries. Completed 20 separate max-new 1 invocations in primary-3060ti-20261018, Qwen35-9B. This candidate passes all D3 criteria: 210/210 well formed, 18/20 SUCCESS, 15/20 competence, median wall 26.383874 s, zero OOM. Two context-bound PARSE_FAIL records preserved, no retries. Full suite 598 passed; all 42 run files and 43 pinned source hashes verified. Largest prompt 8189 triggers five-query 16K check if later selected at S21, which is not performed or frozen. See docs/S20_qwen35_screening.md and docs/decision_log.md. S20 pool incomplete: seven planned candidates remain unrun.

## Outcome

- Signal: useful

## Source Nodes

- S20 — Model screening
- D3 — Model selection (S20–S21)