# Granite 4.1 16K reassessment — stopped by researcher, 2026-10-21

The researcher explicitly stopped this test during query 16 after observing
repeated request timeouts. The process was terminated and the model unloaded.
**Fifteen of twenty outcomes are saved: six SUCCESS and nine ERROR/CONNECTION.**
Each saved error records a 120-second read timeout. No PARSE_FAIL, episode
TIMEOUT or OUT_OF_MEMORY outcome is saved. Query 16, BH2_04425, was interrupted
without a final record; the last four queries were not started. No outcome was
invented for the interrupted or unstarted queries. Do not resume without a new
researcher instruction.

This is an incomplete block: final D3 verdict and full-block competence are
unassigned. Even if all five unsaved queries succeeded, at most 11/20 (55%)
SUCCESS would be possible, below D3's 90% threshold. The original complete
[8K PASS](S20_granite41_screening.md) remains unchanged; this stopped block
does not replace it or qualify Granite 4.1 at 16K.

Only the scientific context setting changed: num_ctx 8192 -> 16384. Exact
identity, agent, twenty-query order, initial messages, prompts, tools,
temperature=0, seed=42, num_predict=4096, page_size=50, budget=30,
episode timeout=600 s, request timeout=120 s and think=false were retained.
Run ID: granite41-context16k-3060ti-20261021 under results/runs/screening-16k.
Digest: 444af1c4b2fedd6b54041aca558e7300b0b3d5c0468c44619126240323ba2852.

Preflight: 42 screening tests passed in 2.15 s; the reused driver's actual
context guard passed four assert-based cases; synthetic native add(2,3)
returned 5 with thinking disabled and actual context 16384. Placement reported
size=8,231,499,856 and size_vram=6,249,072,558 bytes, consistent with more CPU
offload than the 8K sample. These samples do not establish peak memory or prove
the cause of slow requests. No timeout adjustment or diagnostic retry was run.

Evidence: [stopped summary and 16 saved run/configuration hashes](../results/diagnostics/s20/granite41-16k-20261021/stopped-summary.json),
[console](../results/diagnostics/s20/granite41-16k-20261021/official-console.txt),
[preflight](../results/diagnostics/s20/granite41-16k-20261021/preflight.json),
and runtime samples in the same diagnostic directory. All fifteen completed
initial system/user message pairs match the 8K block. Stop-time checks matched
all 488 prior evidence-file hashes and 122 protected identities. No completed
record was retried, repaired or overwritten. No final report-only/evaluator run
was performed because the full block was stopped; no S21 decision or commit.
