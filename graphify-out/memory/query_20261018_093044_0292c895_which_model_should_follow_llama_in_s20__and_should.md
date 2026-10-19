---
type: "query"
date: "2026-10-18T09:30:44.997942+00:00"
question: "Which model should follow Llama in S20, and should thinking be on or off?"
contributor: "graphify"
outcome: "useful"
source_nodes: ["S20 — Model screening", "D3 — Model selection (S20–S21)"]
---

# Q: Which model should follow Llama in S20, and should thinking be on or off?

## Answer

Expanded from original query via vocab: model screening think policy tools selection. The graph located S20 and D3, but its snapshot predates the latest decisions. Verified current docs/decision_log.md lines 1207-1221: primary S20 uses think=false, excludes thinking-only weights, and lists qwen3:8b next after llama3.1:8b. Recommend qwen3:8b as the next download, subject to local tools, identity, disabled-thinking and context-8192 GPU preflight. Official Qwen3-8B model card confirms both modes; Ollama tag currently lists Q4_K_M, 5.2GB. docs/S20_llama_screening.md records all 20 Llama episodes complete and D3 failure from string-valued page arguments; this is not evidence that thinking is required. Earlier S14 Qwen results are diagnostics, not matched primary S20 results. No new candidate inference or scientific-policy change performed.

## Outcome

- Signal: useful

## Source Nodes

- S20 — Model screening
- D3 — Model selection (S20–S21)