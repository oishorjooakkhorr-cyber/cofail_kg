# S20 Ministral on RTX 5060 Ti — 2026-10-28

Fresh twenty-query run `ministral3-5060ti-16k-20261028`, separate from all
3060 Ti history. Researcher clarified Q4_K_M weights and unquantized f16 KV.
Context 16384; installed Ollama 0.40.12; all 35 layers on GPU. No S21 work.

**Completed: D3 PASS on this host/runtime.** All twenty attempt-1 outcomes saved:
18 SUCCESS, two PARSE_FAIL, zero ERROR/TIMEOUT/OOM. Competence is 17/20 (85%);
native calls 179/179 well-formed; median episode wall time 45.307066 seconds.
SUCCESS reaches the existing 90% threshold exactly. No historical result is
reclassified or combined with this new-host block.

| D3 criterion | Observed | Required | Verdict |
|---|---:|---:|---|
| Well-formed calls | 179/179 (100%) | >=90% | PASS |
| SUCCESS | 18/20 (90%) | >=90% | PASS |
| Competent queries | 17/20 (85%) | >=40% | PASS |
| Median wall time | 45.307066 s | <=300 s | PASS |
| ERROR/OUT_OF_MEMORY | 0 | 0 | PASS |

Preparation: 596 existing tests passed, two skipped for missing raw BioHopR;
restored frozen screening inputs, references, KG, prompt and tools verified.
Two operational driver tests pass. Synthetic native add(2,3) returned integer
arguments without thinking. Server log verifies K (f16), V (f16), 2176 MiB KV;
API reports context 16384 and size=size_vram=7513676184 bytes.

Settings: temperature 0, seed 42, num_predict 4096, think=false, tool budget 30,
page size 50, request timeout 120 s, episode timeout 600 s. Flash Attention on,
one sequence. Store D:\Models, dedicated server http://127.0.0.1:11435.

The operational driver reuses existing agent, screening and evaluation code.
It pins current source bytes after verifying seven CRLF-only checkout changes,
checks historical-output hashes between episodes, preserves every final status,
and writes separate metrics and a summary after all twenty records are saved.
No global screening table or historical manifest is rewritten.

Artifacts: [diagnostics](../results/diagnostics/s20/ministral3-5060ti-16k-20261028/).
Console: `run.stdout.log`, `run.stderr.log`. Final verdict is in
`summary.json`. Raw records live under
`results/runs/screening-5060ti/ministral3-5060ti-16k-20261028/`.

Resume after an interruption with the dedicated server running:

```powershell
& D:\cofailKG\.venv\Scripts\python.exe D:\cofailKG\results\diagnostics\s20\ministral3-5060ti-16k-20261028\run_model.py
```

Already saved final statuses are never retried. Use `--report-only` for offline
evaluation after twenty records; no Ollama access is needed for that mode.

Offline replay exited zero and preserved all 21 new run/configuration hashes;
all 459 historical files and pinned source/input hashes remain unchanged.
The driver guard tests also rejected an intentionally inverted context guard
in an isolated copy. Evidence: `final-validation.json`, `final-run-hashes.json`,
`historical-hashes.json`, `review-mutation.txt` and offline-report logs.
The dedicated model was unloaded and its server stopped after verification;
the original server on port 11434 remains available. See `runtime-cleanup.json`.

Real example: BH2_06427 returned SUCCESS with answer IDs 14782, 15270 and 17559.
Its saved final JSON names Biotin, Lipoic acid and Gabapentin enacarbil. These
are stored benchmark outputs, not independent biomedical recommendations.

Manual inspection: BH2_03619 and BH2_03879 retained incomplete final JSON after
the standard re-prompt. Both final responses report done_reason=length at
prompt_eval_count=16364, leaving only 20 generated tokens in the 16384 window.
Inspect `failure-inspection.json` and raw records. No context, prompt, parser,
timeout or outcome was changed in response to these failures.

Assumptions and routine engineering choices: the request authorizes a fresh
twenty-query S20 block using the installed runtime; the explicit clarification
selects Q4_K_M weights and f16 KV. Isolated server/paths, current-byte source
pinning, runtime guards and separate reporting are engineering choices. Model
selection across hosts and S21 remain researcher decisions. Two missing-raw-data
tests were skipped; the frozen S20 inputs and evaluator references were verified.
