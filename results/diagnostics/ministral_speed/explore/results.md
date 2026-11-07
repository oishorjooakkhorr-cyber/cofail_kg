# Ministral 3 8B — f16 vs q4_0 KV cache, exploratory (NOT official, NOT a D3 block)

2026-10-20. 4 full 20-query screening blocks, pinned 16K config (sources hash-checked) except:
separate runs_root/run_id, request timeout 600 s (frozen: 120 s) and episode timeout 1800 s (frozen: 600 s),
so slow f16 replies could finish. q4 blocks: process-scope `OLLAMA_FLASH_ATTENTION=1`, `OLLAMA_KV_CACHE_TYPE=q4_0`.
Order: f16-r1, q4-r1, q4-r2, f16-r2. Original server settings restored; User/Machine env never modified.

## Block summary

| block | SUCCESS | competent | mean precision | mean recall | mean F1 | median wall s | episodes with a reply >120 s | median gen tok/s |
|---|---:|---:|---:|---:|---:|---:|---:|---:|
| f16-r1 | 17 | 15 | 0.949 | 0.653 | 0.674 | 262 | 8 | 15.6 |
| f16-r2 | 17 | 15 | 0.949 | 0.637 | 0.654 | 238 | 7 | 16.1 |
| q4-r1 | 19 | 17 | 0.850 | 0.695 | 0.675 | 66 | 0 | 48.7 |
| q4-r2 | 19 | 17 | 0.850 | 0.695 | 0.675 | 66 | 0 | 48.7 |

## Agreement between blocks (20 queries)

| pair | kind | identical tool paths | identical answer sets | mean answer Jaccard | competence agrees |
|---|---|---:|---:|---:|---:|
| f16-r1 vs f16-r2 | same setting | 19 | 19 | 0.96 | 20 |
| q4-r1 vs q4-r2 | same setting | 20 | 20 | 1.00 | 20 |
| f16 vs q4 (all 4 pairs) | cross | 7 | 5 | 0.45–0.48 | 12 |

Only f16 difference between reruns: BH2_04003 (recall 0.41 vs 0.14).

## Reading

- Rerun noise is tiny (f16 19/20 identical, q4 20/20). The f16-vs-q4 differences (13/20 trajectories differ) are therefore caused by the KV cache type, not chance.
- Aggregate quality is similar: F1 0.65–0.67 (f16) vs 0.675 (q4). q4 has lower precision, higher recall, +2 SUCCESS, +2 competent.
- Per query it is a reshuffle, not a uniform improvement: q4 better on e.g. BH2_03619, 03760, 03856, 03991, 05366, 05686; worse on e.g. BH2_03434 (1.00 -> 0 answers), 03762 (SUCCESS -> PARSE_FAIL), 03850, 03881, 00461.
- Speed: q4 ~3x faster generation, no reply over 120 s; f16 has 7–8 episodes per block that would time out under the frozen 120 s limit, and BH2_03991 exceeds even 600 s.
- Implication for co-failure analysis (researcher to judge): KV cache type changes *which* queries fail, so it behaves like a different model variant, not a pure speed setting.

## Notes / anomalies

- f16-r1 BH2_03991 first attempt was killed by a wrapper bug (PowerShell treated a stderr warning as fatal) while saving; it was rerun after the fix (both attempts timed out at 600 s). Orphan `.tmp` file kept in runs/explore-f16-r1.
- Claude Code session restarted after the run; Ollama was found stopped and restarted with original settings.
- Per-query details: analysis.json. Scripts: run_block.py, run_all.ps1, analyze.py. Console: console.txt.
