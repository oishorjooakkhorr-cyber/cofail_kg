# Ministral 3 8B: q4_0 KV-cache episode test (diagnostic only, NOT an amendment)

2026-10-20. Exact pinned 16K screening config (`Ministral3-8B.config.json` of run `context16k-3060ti-20261020`), sources hash-checked; only `runs_root`/`run_id` differ. num_ctx 16384, request timeout 120 s, temperature 0, seed 42.
Server: same Ollama 0.40.4 binary; q4 runs used process-scope `OLLAMA_FLASH_ATTENTION=1`, `OLLAMA_KV_CACHE_TYPE=q4_0`. Original server (no KV/FA vars) restored afterwards; User/Machine env never modified.

| query | run | status | tool calls | gen tokens | last-call gen tok/s | wall s | answers | competent | precision | recall |
|---|---|---|---:|---:|---:|---:|---:|---|---:|---:|
| BH2_02033 | official f16 | SUCCESS | 4 | 286 | 14.5 | 20.0 | 3 | yes | 1.00 | 1.00 |
| BH2_02033 | f16 control rerun | SUCCESS | 4 | 284 | 16.3 | 37.3* | 3 | yes | 1.00 | 1.00 |
| BH2_02033 | q4_0 | SUCCESS | 4 | 280 | 43.9 | 18.9 | 3 | yes | 1.00 | 1.00 |
| BH2_03750 | official f16 | ERROR (timeout) | 4 | 283 | 15.9 | 142.1 | 0 | no | – | – |
| BH2_03750 | q4_0 | SUCCESS | 7 | 3048 | 44.3 | 75.6 | 45 | yes | 0.98 | 1.00 |
| BH2_03760 | official f16 | SUCCESS | 11 | 3158 | 9.8 | 286.5 | 22 | yes | 1.00 | 0.17 |
| BH2_03760 | q4_0 | SUCCESS | 12 | 2951 | 40.5 | 79.1 | 39 | yes | 1.00 | 0.31 |

\* includes cold model load after the Codex benchmark restart.

Trajectory identity vs official: BH2_02033 identical tool calls and answers (also for the f16 control). BH2_03750: diverged after tool call 2 (official was cut off by the timeout). BH2_03760: diverged after tool call 1.
q4 `/api/ps`: size 6.14 GB, VRAM 5.62 GB (91.5%), ctx 16384.

Caveats: 3 queries, one run each; the f16 control shows Ministral is not bit-identical across reruns even at f16 (284 vs 286 tokens), so trajectory divergence cannot be attributed to KV quantization from this sample. Not a D3 block; no thresholds applied.
