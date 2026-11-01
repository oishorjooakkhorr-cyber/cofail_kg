# Qwen35-9B context-window comparison (8K / 16K / 32K)

Purpose: give the evidence for why Qwen35-9B runs at `num_ctx = 8192` while the other three agents
run at 32768 (protocol §9.1). This is a **descriptive side report**. It changes no gate outcome or
frozen value, and it adds no agent (protocol §9.2, n = 4). No new runs were made; every number
below is copied from existing S20 records.

## Sources

| Block | Run ID / file | Host | `num_ctx` | KV cache |
|---|---|---|---|---|
| A | `primary-3060ti-20261018` (`results/diagnostics/s20/qwen35/official-summary.json`) | RTX 3060 Ti | 8192 | f16 |
| B | `context16k-3060ti-20261020` (`results/diagnostics/s20/full-16k-20261020/acceptance.json`) | RTX 3060 Ti | 16384 | f16 |
| C | `qwen35-5060ti-16k-20261029` (`.../qwen35-5060ti-16k-20261029/summary.json`) | RTX 5060 Ti | 16384 | f16 |
| D | `qwen35-5060ti-32k-20261029` (`.../qwen35-5060ti-32k-20261029/summary.json`) | RTX 5060 Ti | 32768 | f16 |
| E | `qwen35-5060ti-8k-f32-20261030` (`.../qwen35-5060ti-8k-f32-20261030/summary.json`) — **evidence of record** | RTX 5060 Ti | 8192 | f32 |

Every block uses the same model (`qwen3.5:9b`, digest `56671c2a…3c90`, Q4_K_M), the same 20
screening queries, temperature 0, seed 42 and think=false. The per-query table is
`results/diagnostics/s20/qwen35-5060ti-8k-f32-20261030/paired-comparison.csv`, which covers blocks A, C, D and E.

## D3 metrics (thresholds from `docs/decision_rules.md` D3)

| Metric (threshold) | A 8K 3060Ti | B 16K 3060Ti | C 16K 5060Ti | D 32K 5060Ti | E 8K-f32 5060Ti |
|---|---|---|---|---|---|
| Well-formed calls (≥ 90%) | 100% | 100% | 100% (259/259) | 100% (294/294) | 100% (232/232) |
| SUCCESS (≥ 90%) | 18/20 = 90% | 19/20 = 95% | **16/20 = 80%** | **13/20 = 65%** | 18/20 = 90% |
| Competence (≥ 40%) | 15/20 = 75% | 13/20 = 65% | 12/20 = 60% | 12/20 = 60% | 14/20 = 70% |
| Median wall time (≤ 5 min) | 26.4 s | 56.8 s | 30.6 s | 28.6 s | 18.5 s |
| OOM episodes (0) | 0 | 0 | 0 | 0 | 0 |
| PARSE_FAIL episodes | 2 | 1 | 4 | 7 | 2 |
| Budget-hit share | 0.00 | 0.10 | 0.05 | 0.15 | 0.05 |
| Largest prompt (tokens) | 8189 | 16379 | 16368 | 32750 | 8189 |
| **D3 pass** | yes | yes | **no** | **no** | yes |

## Main observations

1. On the host used for the pilot (RTX 5060 Ti), 8K is the only Qwen context that passes D3
   (block E). At 16K and 32K, the SUCCESS rate falls below the 90% threshold.
2. A larger context means more PARSE_FAIL on this host (2 → 4 → 7), not fewer. Competence also
   does not improve (70% → 60% → 60%).
3. Several failures at larger contexts come from episodes that use up the whole window. In block D,
   the last prompts were 32750 and 32749 tokens for BH2_03879 and BH2_04003. In block C,
   BH2_03879 reached 16334 and BH2_03991 reached 16306. More room lets these episodes run longer;
   it does not make them finish.
4. Only one query gains supported answers at a larger context: BH2_03760 has 0 supported answers at
   8K and 124 at both 16K and 32K. BH2_03953 shows the reverse: it succeeds at 8K and is a
   PARSE_FAIL at 16K and 32K.

## Confounds — read before citing

- **KV cache precision differs.** Block E uses an f32 KV cache. Blocks C and D use f16. On the
  5060 Ti host, the comparison therefore mixes context size with cache precision. No 5060 Ti block
  exists at 8K with f16, or at 16K/32K with f32.
- **Host differs.** Blocks A and B ran on the RTX 3060 Ti. At 16K, Qwen passed on the old host
  (B) and failed on the new host (C), with the same digest and the same queries.
- **n = 20 per block.** One episode is 5 percentage points. The 90% threshold is reached at 18/20,
  so A, E (18) and C (16) are only two episodes apart.

The defensible claim is: "Under the screening protocol on the pilot host, Qwen35-9B met Gate D3
only at 8K; increasing the context to 16K or 32K lowered the SUCCESS rate below threshold and
raised parse failures." The claim "8K is intrinsically better for Qwen" is **not** supported,
because of the confounds above.
