# Ministral 3 8B: final Ollama speed diagnostics

2026-10-20, Windows 11, RTX 3060 Ti (8 GiB VRAM), approximately 16 GiB system RAM.

**At approximately 14K prompt tokens: baseline 6.02, FA-only 5.93, q8_0 11.97, q4_0 32.12 generated tokens/s.** This comparison completed 17/17 requests successfully after correcting runner cleanup.

Final files are in `results/diagnostics/ministral_speed/clean/`. Earlier parent-folder reports and all trial outputs are preserved as preliminary evidence; nothing was overwritten.

## Baseline and model

Ollama **0.40.4**; NVIDIA driver **610.88**. Original executable: `E:\Phitron Thesis\cofail_kg\.venv\ollama\ollama.exe serve`; model store: `D:\Models`. No tray app was running.

| Variable | User | Machine | Original server |
|---|---|---|---|
| `OLLAMA_FLASH_ATTENTION` | unset | unset | unset |
| `OLLAMA_KV_CACHE_TYPE` | unset | unset | unset |
| `OLLAMA_NUM_PARALLEL` | unset | unset | unset |
| `OLLAMA_GPU_OVERHEAD` | unset | unset | unset |

Effective defaults observed in logs: one sequence, GPU overhead 0, f16 KV. Baseline already enabled Flash Attention automatically (`flash_attn=auto`, `Flash Attention enabled`), explaining why forcing it alone changes little. See the [Ollama FAQ](https://docs.ollama.com/faq).

`/api/show`: architecture **mistral3**, **8,918,026,240 parameters**, Q4_K_M weights, **34 blocks**, **32 attention heads**, **8 KV heads**, **128 key dimensions** and **128 value dimensions per head**. Advertised model context: 262,144; every successful benchmark loaded **16,384**.

**Vision encoder/projector included:** metadata reports 24 vision blocks; the GGUF directory contains 218 vision tensors plus `mm.linear_1.weight`, `mm.linear_2.weight`, `mm.norm.weight`, and `mm.patch_merger.merging_layer.weight`. No images were used. The complete show output and projector tensor evidence are preserved in the parent folder.

KV per token: `34 * 8 * (128 + 128) = 69,632` scalar values. f16 uses 2 bytes/value; q8_0 uses 34/32 and q4_0 uses 18/32 including block scales, per the [ggml definitions](https://github.com/ggml-org/llama.cpp/blob/master/ggml/src/ggml-common.h).

| KV type | Bytes/token | KiB/token | Bytes at 16K | GiB at 16K |
|---|---:|---:|---:|---:|
| f16 | 139,264 | 136.00 | 2,281,701,376 | 2.125000 |
| q8_0 | 73,984 | 72.25 | 1,212,153,856 | 1.128906 |
| q4_0 | 39,168 | 38.25 | 641,728,512 | 0.597656 |

These are text KV estimates for one sequence, excluding weights, projector/vision memory, compute buffers and runtime overhead. Actual cache allocations matched them exactly.

## Benchmark results

`clean/bench.py` reuses the parent API/metrics script with deterministic varied-word synthetic context and a long prose output instruction. Requests use `/api/generate`, `stream=false`, `think=false`, options `{num_ctx:16384, temperature:0, seed:42, num_predict:256}`, `keep_alive=5m`, and **900 seconds** timeout. Early case prefixes differ to reduce cache reuse. Every successful response contains 256 generated tokens; actual prompt lengths are within 5% of target.

A = original; B = User FA=1; C = FA=1 + KV=q8_0; D = FA=1 + KV=q4_0. All Ollama-owned `ollama*` and `llama-server.exe` processes were stopped and absence verified before each restart. The exact original executable was relaunched. NUM_PARALLEL/GPU_OVERHEAD retained original settings. Benchmark temporary files and CUDA cache stayed inside this output tree.

GB = 10^9 bytes. `%on_GPU = 100 * /api/ps.size_vram / size`, a memory-residency ratio; GPU utilization is a separate quantity. Prompt/gen rates use returned counts divided by their API durations. `/api/ps` was the first API call after each successful response.

| config | prompt_tokens | size_GB | vram_GB | %on_GPU | prompt tok/s | gen tok/s |
|---|---:|---:|---:|---:|---:|---:|
| A | 487 | 7.772 | 5.619 | 72.30% | 30.94 | 18.63 |
| A | 3,988 | 7.772 | 5.619 | 72.30% | 1752.87 | 13.30 |
| A | 7,988 | 7.772 | 5.619 | 72.30% | 1620.47 | 9.53 |
| A | 13,989 | 7.772 | 5.619 | 72.30% | 1502.91 | 6.02 |
| B | 487 | 7.772 | 5.619 | 72.30% | 1525.04 | 18.68 |
| B | 3,988 | 7.772 | 5.619 | 72.30% | 1806.57 | 12.70 |
| B | 7,988 | 7.772 | 5.619 | 72.30% | 1647.12 | 9.45 |
| B | 13,989 | 7.772 | 5.619 | 72.30% | 1476.32 | 5.93 |
| C | 487 | 6.707 | 5.488 | 81.82% | 1629.61 | 18.26 |
| C | 3,988 | 6.707 | 5.488 | 81.82% | 1983.82 | 21.42 |
| C | 7,988 | 6.707 | 5.488 | 81.82% | 1853.61 | 17.14 |
| C | 13,989 | 6.707 | 5.488 | 81.82% | 1681.04 | 11.97 |
| D | 487 | 6.136 | 5.617 | 91.54% | 1704.35 | 31.46 |
| D | 3,988 | 6.136 | 5.617 | 91.54% | 2190.70 | 43.96 |
| D | 7,988 | 6.136 | 5.617 | 91.54% | 2082.45 | 38.45 |
| D | 13,989 | 6.136 | 5.617 | 91.54% | 1882.71 | 32.12 |
| C: Qwen control | 8,000 | 6.486 | 5.543 | 85.45% | 993.42 | 35.90 |

`results.json` includes total_duration, load/prompt/eval durations, wall times, counts, cached counts, bytes and exact unrounded rates for every call. Raw requests/responses and post-call model snapshots are retained. First prompts are cold observations; later prompts generally reused 15 tokens. Uncached-only prompt rates are also saved. No statistical replicates were run.

| config | Actual KV | GPU text/output layers | CPU KV MiB | GPU KV MiB |
|---|---|---:|---:|---:|
| A | f16 | 26/35 | 576 | 1,600 |
| B | f16 | 26/35 | 576 | 1,600 |
| C | q8_0 | 30/35 | 170 | 986 |
| D | q4_0 | 34/35 | 18 | 594 |

## 120-second budget at approximately 14K

Estimated generation time is `1200 / gen tok/s`. Warm total adds measured prompt prefill and excludes model loading. These are extrapolations from 256-token samples.

| config | gen tok/s | 1,200-token generation s | Prefill + generation s | Within 120 s, estimated |
|---|---:|---:|---:|---|
| A | 6.02 | 199.3 | 208.6 | No |
| B | 5.93 | 202.4 | 211.9 | No |
| C | 11.97 | 100.3 | 108.6 | Yes |
| D | 32.12 | 37.4 | 44.8 | Yes |

**Conclusion:** None of A-D achieved 100% GPU residency. q4_0 came closest at **91.54%**, with **34/35 GPU layers**. It measured **32.12 tok/s at 13,989 prompt tokens**, versus baseline **6.02**, a **5.33x** speedup. Its 1,200-token answer projects to **37.4 seconds** of generation or **44.8 seconds including warm prefill**, within 120 seconds under these benchmark conditions. q8_0 projects to **108.6 seconds including prefill**, leaving a narrow margin. Baseline and FA-only exceed 120 seconds. Reduced KV storage and fewer CPU layers materially improved long-context throughput; forcing FA alone provided little benefit because baseline already enabled it. Actual 1,200-token completion reliability remains untested.

## Errors, anomalies and restoration

- The final comparison completed **17/17 requests**. No requested configuration or prompt length was skipped. Earlier trial errors below are preserved separately.
- Earlier repeated-letter/integer trials hit HTTP 500 `token repeat limit reached` at B/8K and C/8K/14K. The final matrix uses varied context and prose output; earlier failures were preserved and excluded from its table.
- Earlier CUDA warm-up failed with `shared object initialization failed`; the first C attempt was interrupted by an unclean Windows reboot (boot 16:14:33 Asia/Dhaka; Kernel-Power 41/EventLog 6008). A later A startup also failed with `0xc0000409` amid 1.1 GiB free RAM, 1.4 GiB free swap and 3.4 GiB free VRAM. The reboot's exact cause was not established.
- The restart procedure initially checked only `ollama*`. This build also launches `llama-server.exe`, and three orphan runners survived; one retained about 3.5 GiB RAM. Their lingering allocations plausibly contributed to resource pressure. Cleanup was corrected before the final comparison and verified at every transition. Earlier parent-folder reports are preliminary and superseded by this `clean/` report.
- PowerShell initially converted null environment properties to empty strings. Explicit `NullString` deletion corrected restoration. Final verification checked actual registry absence and the live server environment.
- **Restoration verified:** all four User/Machine variables are unset; the live server environment matches the original, including `OLLAMA_MODELS=D:\Models`, original TEMP/TMP and unset CUDA_CACHE_PATH. Ollama 0.40.4 was restarted, `/api/ps` responds with an empty list, and only the restored server remains among Ollama-owned server/runner processes (PID 24384).
- **Integrity verified:** 399 protected-tree files have unchanged sizes/timestamps with no additions/deletions; all 500 protected/prior-result SHA-256 values match. All new output is inside `ministral_speed/`. Existing results were preserved.

Not checked: D3, answer quality, or an actual 1,200-token answer. Risk: cache quantization accuracy and long-answer reliability remain untested; earlier CUDA instability requires care with runner cleanup.
