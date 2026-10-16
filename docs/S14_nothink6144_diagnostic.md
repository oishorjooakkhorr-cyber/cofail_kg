# S14 diagnostic — think=false, output cap 6144 (2026-10-16)

Follow-up correction: the authorized template repair and repeat are recorded in
`S14_template_repair.md`. The repeat succeeded after one re-prompt, but metadata
also identifies the installed weights as Thinking-2507 (thinking-only). The
earlier inference that a missing false branch was a defect in a switchable model
was incomplete: adding that branch cannot supply a mode those weights lack.
The malformed tool JSON was independently confirmed and repaired. The rest of
this document preserves the earlier diagnostic checkpoint.

The one requested repeat reached the graph and retrieved 21 disease entries, but
ended in PARSE_FAIL because reasoning text preceded the final JSON. GPU capacity
was adequate. Render-only inspection found concrete template problems explaining
why requesting think=false did not actually stop reasoning generation.

## Run and hardware

```powershell
.\.venv\Scripts\python.exe scripts/14_run_episode.py --run-id s14-nothink6144-20261016 --think false --diagnostic-num-predict 6144
```

The explicit diagnostic CLI option is the only runtime-code change. Its default
remains 4096. Three additional tests verify the override and reject nonpositive
values; the full host suite passed **351 tests in 9.31 seconds**, no skips/exclusions.
The researcher authorized this diagnostic deviation before the run; protocol,
frozen hashes, P1 text and the installed model were not modified.

- GPU: RTX 3060 Ti, 8192 MiB. Sampled total GPU usage peaked at **4714 MiB
  (4.60 GiB)** across 168 samples. Sampling is not an exact instantaneous peak.
- Ollama reported the full model resident on GPU, `size_vram == size`, with
  context length 8192. No OOM or CPU-offload indication occurred.
- Output cap: 6144, a 50% increase. Context stayed 8192. Page size 50, tool budget
  30, temperature 0, seed 42, episode timeout 600 s and HTTP timeout 120 s stayed fixed.
- The same qwen3:4b digest was verified before and after; one episode took 174.107482 s.

Record: `results/runs/s14-nothink6144-20261016/BH2_00461__S14-qwen3-4b__a1.json`.
Record SHA256: `a5ba5d4bdcb8ec79dd5e1f778b61426a1b7a6ce582c1d8c99bbfbc4208dd741b`.

## What improved and what failed

| Measure | Previous think=true / 4096 | Requested think=false / 6144 |
| --- | --- | --- |
| Status | PARSE_FAIL | PARSE_FAIL |
| Native tool calls | 0 | 4, all successful |
| Disease entries retrieved | 0 | 21 |
| Assistant turns | 2 | 6 |
| Generated tokens by turn | 4096, 4096 | 4910, 2834, 253, 346, 743, 5747 |
| Finish reasons | length, length | stop on all six turns |
| Maximum prompt tokens | 627 | 7295 |
| Failure | Empty final content | Reasoning text plus JSON, on both final attempts |

The graph route was:

`14097 (drug) --drug_protein--> 111 (TTR) --disease_protein--> 21 disease entries`.

The four calls inspected the drug, retrieved TTR, inspected TTR, and retrieved its
disease neighbors. Each saved result was independently compared with the existing
`scripts/inspect_kg.py` CLI. Both final replies contain a JSON suffix whose 21
ID/name pairs exactly match the retrieved disease list. This confirms graph
grounding of those suffixes; no gold-answer/evaluator scoring was performed.

However, both replies also contain reasoning before `</think>` and the JSON.
Protocol §9.4 requires the entire reply (apart from an optional whole-message
fence) to be JSON. The runner correctly rejected both and preserved PARSE_FAIL
after one fixed re-prompt. Suffix extraction was used only for diagnostic comparison;
neither the parser nor the saved status was relaxed to obtain success.

No turn hit the 6144 output cap. The first turn used 4910 tokens, more than the
earlier 4096 cap, and reached a native call. Since two settings changed together,
this is not a controlled attribution of all improvement to either setting.

## Directly verified template problems

The local `/api/show` template and Ollama 0.40.4 render-only responses were saved.
The `_debug_render_only` endpoint returns the formatted prompt without generation,
as implemented in the pinned [API type](https://raw.githubusercontent.com/ollama/ollama/v0.40.4/api/types.go)
and [server route](https://raw.githubusercontent.com/ollama/ollama/v0.40.4/server/routes.go).
These two diagnostic rendering requests were not additional episodes.

1. **Thinking control:** rendering the same first-turn request with true and false
   produces identical prompt strings, both ending with `<think>\n`. The installed
   template does not branch on `.Think` at that prefix. With false, the observed
   reasoning is delivered in `message.content`, including closing `</think>` text,
   rather than a separate `message.thinking` field. Thus the requested flag did not
   actually prevent reasoning generation in this installation.
2. **Tool schema serialization:** both objects inside the rendered `<tools>` block
   fail JSON parsing. `{{ .Function }}` is rendered as Go struct text, including
   `<nil>`, rather than JSON. Tools still happened to work in this episode, so this
   defect cannot be claimed as the sole cause of previous failures. It is an
   independently demonstrated interface problem that should be repaired.

The runtime source supplies a `json` template function and exposes `.Think` and
`.IsThinkSet`: [Ollama 0.40.4 template implementation](https://raw.githubusercontent.com/ollama/ollama/v0.40.4/template/template.go).

## How to reach the desired outcome

Repair the runtime/model template before increasing memory or token limits again:

- Use `{{ json .Function }}` for each tool definition.
- When `.IsThinkSet` is true and `.Think` is false, close the initial thinking
  block immediately so the model begins its answer/tool-call channel.
- Validate the corrected rendered tool definitions as JSON, and confirm true/false
  produce the intended different assistant prefixes, before another generation.
- Use a separately named diagnostic model variant with the same weights; record
  its new identity. Then verify native calls and a standalone final JSON answer
  under the existing strict parser. This is still an untested next step, not a
  guarantee that the model will always comply.

Prepared proposal: `results/diagnostics/s14_qwen3_template_proposed.Modelfile`.
It changes only those two template expressions. It was **not installed, rendered
by Ollama or used for generation**; its runtime behavior remains to be tested.
The original model and all prior records remain unchanged.

One further issue became visible: the last prompt used 7295/8192 tokens (89.05%),
and server logs record two context shifts during the long re-prompt reply. This
shows why simply raising the output cap is insufficient for long verbose traces.
Fixing the unintended reasoning should reduce this pressure; remeasure afterward
before deciding whether to raise context. No new experimental context setting was chosen.

## Evidence and scope

Under `results/diagnostics/`:
`s14_nothink6144_verification.json`, `s14_nothink6144_gpu.json`,
`s14_nothink6144_model_template.json`, `s14_nothink6144_render_comparison.json`,
`s14_nothink6144_console.txt`, `s14-nothink6144-20261016_identity.json`, and
`s14_nothink6144_suite.txt`. The existing Ollama server stderr contains the context
shift messages. The verification JSON checks reconstruction, four CLI comparisons,
both grounded JSON suffixes, malformed tool JSON and identical rendered prefixes.

Only one new episode was generated. No prompt freeze, model replacement, protocol
change, parser relaxation, gold scoring, additional model selection or commit.
