# Ministral 3 8B: Ollama speed diagnostics

2026-10-20, Windows 11, RTX 3060 Ti (8 GiB VRAM), approximately 16 GiB system RAM.

**q4_0 reached 25.07 generated tokens/s at 14,005 prompt tokens, versus 5.85 at baseline. None of the tested configurations achieved 100% GPU residency.** The q8_0 14K request aborted, so its completed-request throughput remains unmeasured.

## Baseline

Ollama **0.40.4**, NVIDIA driver **610.88**. Executable: `E:\Phitron Thesis\cofail_kg\.venv\ollama\ollama.exe`; model store: `D:\Models`. The original server was `ollama.exe serve`; no tray app was running.

| Environment variable | User | Machine | Original server process |
|---|---|---|---|
| `OLLAMA_FLASH_ATTENTION` | unset | unset | unset |
| `OLLAMA_KV_CACHE_TYPE` | unset | unset | unset |
| `OLLAMA_NUM_PARALLEL` | unset | unset | unset |
| `OLLAMA_GPU_OVERHEAD` | unset | unset | unset |

The measured runner used one sequence (`n_seq_max=1`); startup reported GPU overhead 0. Baseline already enabled Flash Attention automatically: its log contains `flash_attn=auto` and `Flash Attention enabled`. Forcing FA therefore did not turn on a previously disabled kernel. Automatic FA and quantized KV settings are described in the [Ollama FAQ](https://docs.ollama.com/faq).

## Model and KV cache

`/api/show` identifies **mistral3**, 8,918,026,240 parameters, Q4_K_M weights, **34 transformer blocks**, 32 attention heads, **8 KV heads**, **128 key dimensions** and **128 value dimensions per head**. Its advertised context limit is 262,144; every successful test loaded 16,384.

**A vision encoder and projector are included in the GGUF.** Metadata reports 24 vision blocks; reading the tensor directory confirmed 218 vision tensors and projector tensors including `mm.linear_1.weight`, `mm.linear_2.weight`, `mm.norm.weight`, and `mm.patch_merger.merging_layer.weight`. No images were supplied. Evidence is in `show-ministral.json` and `projector-tensor-evidence.json`.

Text KV storage per token is `34 × 8 × (128 + 128) = 69,632` scalar values. Estimates include quantization block scales: f16 uses 2 bytes/value, q8_0 uses 34/32, and q4_0 uses 18/32, following the [ggml block definitions](https://github.com/ggml-org/llama.cpp/blob/master/ggml/src/ggml-common.h).

| KV type | Bytes/token | KiB/token | Bytes at 16,384 | GiB at 16,384 |
|---|---:|---:|---:|---:|
| f16 | 139,264 | 136.00 | 2,281,701,376 | 2.125000 |
| q8_0 | 73,984 | 72.25 | 1,212,153,856 | 1.128906 |
| q4_0 | 39,168 | 38.25 | 641,728,512 | 0.597656 |

These are single-sequence text KV estimates. Weights, vision/projector memory, compute buffers and other runtime allocations are additional. Actual runner totals matched all three estimates exactly: 2,176 / 1,156 / 612 MiB.

## Benchmark

`bench.py` uses `/api/generate`, `stream=false`, `num_ctx=16384`, `temperature=0`, `seed=42`, `num_predict=256`, `keep_alive=5m`, and a **900-second request timeout**. Thinking is disabled and a short system instruction is supplied. Synthetic repeated-letter context ends with an instruction to count integers. Early case prefixes differ to limit prompt-cache reuse. All successful calls generated 256 tokens; returned prompt counts confirmed the requested lengths within 5%.

A = original settings; B = User FA=1; C = FA=1 + KV=q8_0; D = FA=1 + KV=q4_0. Other requested variables retained their original effective settings. Ollama processes were fully stopped and the same executable relaunched between configurations. C/D were completed in `resume/` after the interrupted first C attempt. Benchmark temporary files and CUDA cache were redirected inside this diagnostics folder.

GB below means **10^9 bytes**. `%on_GPU = 100 × /api/ps.size_vram / size`; this is memory residency. GPU utilization is a separate measure. The originally reported 7.24/5.23 values correspond approximately to GiB; baseline here is 7.238/5.233 GiB.

| config | prompt_tokens | size_GB | vram_GB | %on_GPU | prompt tok/s | gen tok/s |
|---|---:|---:|---:|---:|---:|---:|
| A | 503 | 7.772 | 5.619 | 72.30% | 31.07 | 18.33 |
| A | 4,004 | 7.772 | 5.619 | 72.30% | 1778.10 | 13.07 |
| A | 8,004 | 7.772 | 5.619 | 72.30% | 1647.22 | 9.35 |
| A | 14,005 | 7.772 | 5.619 | 72.30% | 1475.93 | 5.85 |
| B | 503 | 7.772 | 5.619 | 72.30% | 755.85 | 18.15 |
| B | 4,004 | 7.772 | 5.619 | 72.30% | 1613.14 | 12.96 |
| B ERROR | ~8,000 requested | — | — | — | — | — |
| B | 14,005 | 7.772 | 5.619 | 72.30% | 1268.25 | 5.60 |
| C | 503 | 6.707 | 5.488 | 81.82% | 31.31 | 18.22 |
| C | 4,004 | 6.707 | 5.488 | 81.82% | 2000.01 | 21.74 |
| C ERROR | ~8,000 requested | — | — | — | — | — |
| C ERROR | ~14,000 requested | — | — | — | — | — |
| D | 503 | 6.136 | 5.459 | 88.97% | 1161.14 | 27.53 |
| D | 4,004 | 6.136 | 5.459 | 88.97% | 2140.96 | 35.34 |
| D | 8,004 | 6.136 | 5.459 | 88.97% | 2001.85 | 30.75 |
| D | 14,005 | 6.136 | 5.459 | 88.97% | 1819.24 | 25.07 |
| C: Qwen control | 8,017 | 6.486 | 5.543 | 85.45% | 1018.39 | 36.12 |

Error rows returned HTTP 500, without API token counts/durations. Their prompt lengths and immediate `/api/ps` values could not be confirmed. Raw requests, responses, successful post-call `/api/ps` snapshots, nanosecond durations, cached-token counts and wall times are preserved beside the scripts and aggregated in `results.json`.

Prompt throughput uses `prompt_eval_count / prompt_eval_duration`; later successful calls generally reused 15 prompt tokens. `results.json` also contains uncached-only rates. Initial model loading and warm-up varied considerably; A/C first-prompt prefill was unusually slow, and B's first call included 98.77 seconds of loading. These cold observations are not representative steady-state prefill rates.

| config | Actual KV | GPU text/output layers | CPU KV MiB | GPU KV MiB |
|---|---|---:|---:|---:|
| A | f16 | 26/35 | 576 | 1,600 |
| B | f16 | 26/35 | 576 | 1,600 |
| C | q8_0 | 30/35 | 170 | 986 |
| D | q4_0 | 33/35 | 36 | 576 |

The Qwen C control used 31/33 GPU layers, 272 MiB of attention KV across 8 attention layers, and 50.25 MiB of recurrent state. This smaller attention cache and different architecture help explain its stronger long-context speed; CPU offload alone does not predict identical speed across models.

## 120-second budget at approximately 14K

Extrapolation from each completed 256-token sample: generation time = `1200 / gen_tok_s`; warm total adds measured prompt prefill, excluding cold loading. An actual 1,200-token answer was not tested.

| config | gen tok/s | 1,200-token generation s | Prefill + generation s | Within 120 s, estimated |
|---|---:|---:|---:|---|
| A | 5.85 | 205.2 | 214.7 | No |
| B | 5.60 | 214.4 | 225.5 | No |
| C | Unmeasured: request aborted | — | — | Unconfirmed |
| D | 25.07 | 47.9 | 55.6 | Yes |

**Conclusion:** None of A–D put Ministral entirely on the GPU at 16K. q4_0 came closest at 88.97% residency and 33/35 layers, while reducing text KV from 2.125 to 0.598 GiB. Its measured 14K generation speed was **25.07 tok/s**, about **4.29× baseline**, projecting to **47.9 seconds** for 1,200 generated tokens or **55.6 seconds including warm prefill**. Baseline/FA-only were 5.85/5.60 tok/s and would exceed 120 seconds. q8_0 improved the successful 4K sample to 21.74 tok/s, but its aborted 14K request cannot establish a completed-answer time. The results support KV memory and CPU attention offload as major contributors to the slowdown; forcing FA alone offered no clear improvement because baseline already used FA.

## Errors, anomalies and limits

- B at 8K and C at 8K/14K returned `prediction aborted, token repeat limit reached`. These were explicit HTTP 500 responses, not 120-second connection timeouts. The repetitive synthetic input/output task limits their usefulness. A C/14K backend progress line showed 11.79 tok/s at 100 generated tokens before abort; it is not a completed-request average and was excluded from the main table.
- The first C attempt failed CUDA warm-up with `shared object initialization failed`, returned no benchmark response, and was interrupted by an unclean Windows reboot. Windows reports boot at **16:14:33 Asia/Dhaka** and Kernel-Power 41/EventLog 6008. The evidence does not establish what caused the reboot. The fresh C retry passed warm-up.
- A second matrix using varied common words and prose output was attempted to avoid repetition failures. Its first A/500 call failed with the same CUDA initialization error and exit status `0xc0000409`. At that load, Ollama logged only 1.1 GiB free system RAM, 1.4 GiB free swap, 3.4 GiB free VRAM and 6/35 GPU layers. Resource pressure is a plausible contributor; the exact CUDA failure cause remains unresolved.
- During recovery/stop processing, additional prose A calls completed: 3,988 tokens at 12.45 gen tok/s and 7,988 at 8.92 gen tok/s. A/14K was interrupted when the added controller was stopped. The remaining prose B/C/D/control phases were skipped after the repeated CUDA failure. These partial observations are preserved separately and were not mixed into the main comparison.
- The initial controller was lost during the reboot. Its first restoration attempt also exposed PowerShell converting null property values to empty environment strings. Explicit `NullString` deletion corrected this; final checks confirmed actual absence, including in the live server process.
- Single observations per cell, synthetic prompts, cold-start variation and a reboot between phases limit precision. No successful request exceeded its 900-second timeout. These tests do not measure thesis-answer quality or D3; quantized-cache accuracy and actual 1,200-token completion reliability remain untested.

## Restoration and integrity

**Verified:** all four User/Machine variables are restored to unset; the live server's selected environment matches the original, including `OLLAMA_MODELS=D:\Models`, original TEMP/TMP and unset CUDA_CACHE_PATH. Ollama 0.40.4 was restarted and `/api/ps` responds with an empty model list. No benchmark Python process remains. Final PID: 16916.

**Frozen files unchanged:** 399 files under the six protected trees have identical sizes/timestamps, with no added or missing files; all 500 protected/prior-result SHA-256 values match. All diagnostic outputs are inside `results/diagnostics/ministral_speed/`. Existing results were preserved. Proof: `integrity-after.json`, `final-restoration.json`, and `post-restoration-health.json`.

Not checked: D3, answer quality, or an actual 1,200-token answer. Risk: CUDA startup remains intermittently unstable; the projected timeout margin is not a reliability guarantee.
