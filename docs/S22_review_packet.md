# S22 review packet — run `smoke_single_v135`

**Status: S22 is NOT accepted.** Progression is paused under protocol §9.1 (re-selection rule):
Gemma4-E4B and Qwen35-9B have episodes with prompt tokens above 90% of `num_ctx`, so both return
to S21 for researcher review. This packet is Claude Code's software/evidence review only. It is not a
researcher review, and nothing here records a researcher decision. All work is offline and
read-only: no inference was rerun, and no historical artifact was modified.

Scripts and machine-readable outputs: `results/diagnostics/s22_review/`
(`verify_s22.py` → `verification.json`, `independent_label_check.py` → `label_checks.json`,
`dump_episodes.py` → `episodes/*.md`, `prompt_drops.py` → `prompt_drops.json`,
`prompt_drops_log.py` → `prompt_drops_log.json`).

**Still required from the researcher (runbook S22):** read at least one full episode per model
(`episodes/*.md`); check 6 answers by hand (§5 gives the evidence); record the separate §9.1
decisions for Gemma4-E4B and Qwen35-9B; then decide whether to accept S22. None of this has been
recorded yet.

## 1. Runs

| Run | Episodes | Status | Use |
|---|---|---|---|
| `smoke_single` | 9/80 (Ministral3-8B, BH2_00461–BH2_03856) | Stopped by the researcher, 2026-10-30 (`interruption.json`) | Preserved unchanged. Not resumed, not combined. |
| `smoke_single_v135` | 80/80 | Complete | The S22 run under review |

## 2. Integrity and coverage (`verification.json`)

- The record files are exactly the 20 screening queries × the 4 frozen agents, attempt 1. Nothing
  is extra or missing.
- All 80 record SHA256s match `results/diagnostics/smoke_single_v135/<agent>/final-run-hashes.json`.
  The content of each of the four hash files equals its committed version at HEAD; only the line
  endings differ, because of `core.autocrlf`. The records themselves are git-ignored
  (`results/runs/*`), so the committed hash files are their pin.
- The trace graph rebuilt from the raw tool results equals the stored trace graph
  (`verify_reconstruction`) for all 80 episodes.
- Every saved metrics file pairs with its record (same query, agent and episode status).
- Status: Ministral3-8B 20 SUCCESS; Gemma4-E4B 20 SUCCESS; Granite41-8B 20 SUCCESS; Qwen35-9B
  18 SUCCESS and 2 PARSE_FAIL (BH2_03879, BH2_03991). No ERROR, TIMEOUT or OUT_OF_MEMORY.
- The OFF_QUESTION ∧ SUPPORTED invariant holds (none found; `summary.json`).

## 3. Context-review triggers (§9.1; strict test `max prompt_eval_count > 0.9 × num_ctx` on exact integers)

| Agent | num_ctx | 90% threshold | Episodes above (prompt_eval_count) |
|---|---|---|---|
| Ministral3-8B | 32768 | 29491.2 | none (max 21298) |
| Gemma4-E4B | 32768 | 29491.2 | BH2_04003 (29500 = 90.027%) |
| Granite41-8B | 32768 | 29491.2 | none (max 18192) |
| Qwen35-9B | 8192 | 7372.8 | BH2_03619 (8189), BH2_03760 (8048), BH2_03856 (7470), BH2_03879 (8151), BH2_03881 (8138), BH2_03953 (7972), BH2_03991 (8181), BH2_04003 (7464) |

Further context evidence from the raw Ollama responses (`log_events`). This is reported as data,
not interpreted:

- Five Qwen episodes contain a response with `done_reason = "length"` where prompt + output = 8192
  exactly. The model stopped because the context window was full, not because of `num_predict`:
  - BH2_03619 (msg 22: 8189 + 3)
  - BH2_03879 (msg 36: 8151 + 41)
  - BH2_03953 (msg 20: 7972 + 220)
  - BH2_03991 (msg 20: 8161 + 31; msg 28: 8181 + 11)

  Both PARSE_FAIL episodes are among these. In BH2_03879, the cut-off message ("Now let me get side
  effects for Zonisamide…") had no tool call. It was therefore treated as the final message (§9.4)
  and re-prompted. The reply to the re-prompt was a tool call, which was ignored, so the episode
  ended as PARSE_FAIL.
  The Qwen server log (`server-run-20261030T154436Z.stderr.log`) has exactly five
  `stop processing: n_tokens = 8191, truncated = 1` lines, which matches these five cut-offs. Gemma's
  log has none.
- **Input history reset (Qwen only).** This was inspected offline from the records and the server log
  (scripts `prompt_drops.py` and `prompt_drops_log.py` → `prompt_drops.json` and
  `prompt_drops_log.json`).
  - The stored message history only grows. Even so, `prompt_eval_count` falls between consecutive
    turns 17 times in 8 Qwen episodes. Ministral, Gemma and Granite have no such drops.
  - Each of the 145 Qwen turns was matched to its llama-server request by token count
    (`task.n_tokens = prompt_eval_count`). For every request, the log records `f_keep`: the share of
    the previous cached prompt that the new prompt keeps as a common prefix.
    - On normal later turns, the median `f_keep` is 0.955.
    - On all 12 drop turns that have an `f_keep` line, it is 0.085–0.128. The common prefix is then
      about 680–780 tokens, close to each episode's first-turn prompt (745–759 tokens: system prompt
      plus question).
    - The other 5 drop turns have no `f_keep` line, so they cannot be checked this way.
  - Three further turns show the same reset with **no** drop in the count:
    - BH2_03762 msg 14: 2688 → 6349, `f_keep` 0.236
    - BH2_04003 msg 26: 3782 → 6392, `f_keep` 0.166
    - BH2_03879 msg 20: `f_keep` 0.106, after an earlier reset

    In each of these, a large tool result followed.
  - **Finding:** on these turns, the input Qwen received matched its conversation only up to about
    the system prompt and question. After that, the prompt differed: earlier turns were missing, or
    were not in their stored form. This is consistent with the runtime removing older messages so
    the request fits in 8192 tokens. Trimmed prompts settle at about 6300–6600 tokens.
  - The logs record token counts, not text, so exactly which messages were removed cannot be
    reconstructed. No log line names the mechanism.
  - Episodes affected: BH2_03619, BH2_03762, BH2_03856, BH2_03879, BH2_03881, BH2_03953,
    BH2_03991 and BH2_04003. **BH2_03762 is not a §9.1 trigger**: its maximum prompt is 6562 tokens,
    which is 80.1% of 8192. So the strict 90% test does not catch every episode in which Qwen lost
    history.
  - The stored records and all labels are unaffected: §11–§14 use the stored tool results, not what
    the model saw. What is affected is what the model could read when it chose its next action or
    its final answer.
  - The Granite S20 32K notes in `progress.md` record a "context shift (discard 8189)" in an earlier
  log, so runtime trimming has been seen in this project before.
- Gemma BH2_04003 has no length stop and no decreasing prompt count.

## 4. Complete episodes read (one per model, plus a failure case)

The full transcripts are in `results/diagnostics/s22_review/episodes/`. Each contains every message,
every tool call with its full result, the raw final output and the evaluated answers, with nothing
truncated.

| Episode | Status | Messages / calls | Answers (A / B) | What the software review checked |
|---|---|---|---|---|
| BH2_02033 · Ministral3-8B | SUCCESS | 11 / 4 | 3 GOLD / SUPPORTED | Two hops through R1 then R2; IDs copied from tool output; final JSON parsed |
| BH2_05843 · Gemma4-E4B | SUCCESS | 21 / 8 | 1 GOLD + 3 ALT_VALID, all SUPPORTED | ALT_VALID members are in T_q but not A*_q (BRIDGE construction) |
| BH2_03762 · Granite41-8B | SUCCESS | 21 / 8 | 1 GOLD / SUPPORTED, 1 OFF_QUESTION / PATH_INVALID (SHORTCUT) | H1_MIXED agent; the GOLD answer's *primary* path is the 1-edge shortcut (shorter wins, §14.2), and it is still SUPPORTED through a separate R1→R2 path |
| BH2_05366 · Qwen35-9B | SUCCESS | 11 / 4 | 1 GOLD / SUPPORTED | Normal finish |
| BH2_03879 · Qwen35-9B | PARSE_FAIL | 39 / 19 | none (failed episode) | Context-length cut-off followed by re-prompt, described in §3 |

## 5. Independent Label A / Label B / H1 checks (`label_checks.json`)

The checker deliberately does not import `cofail_kg.evaluation` or the trace module. It rebuilds
appearance and edges from the raw `call_log`, node types from `data/cache/primekg_nodes.parquet`,
and A*_q / G_q / T_q from `data/processed/reference_queries.parquet`. R1 and R2 come from the frozen
mapping. **9 of 9 answers agree** with the recorded labels.

| Query | Agent | Relation type | Canonical answer | Recorded A / B / H1 | Independent A / B / H1 | Evidence | Agree |
|---|---|---|---|---|---|---|---|
| BH2_03762 | Ministral3-8B | disease:drug:effect/phenotype | 22262 Edema (effect/phenotype) | GOLD / SUPPORTED / 1 | GOLD / SUPPORTED / 1 | in A*_q; R1 `indication` → bridges 14024, 14028, 14320 → R2 `drug_effect` → 22262 | yes |
| BH2_05686 | Gemma4-E4B | effect/phenotype:disease:drug | 14557 Turoctocog alfa pegol (drug) | ALT_VALID / SUPPORTED / 1 | ALT_VALID / SUPPORTED / 1 | in T_q, not G_q or A*_q; R1 `disease_phenotype_positive` → 27361 → R2 `indication` → 14557 | yes |
| BH2_03881 | Gemma4-E4B | disease:drug:effect/phenotype | 22304 Hearing impairment | GOLD / PATH_INVALID / 0 | GOLD / PATH_INVALID / 0 | in A*_q, but no R1→R2 path in TG_i; only trace path is 32651 –disease_phenotype_positive→ 22304 (SHORTCUT) | yes |
| BH2_03881 | Gemma4-E4B | disease:drug:effect/phenotype | 22121 Abnormality of the female genitalia | OFF_QUESTION / PATH_INVALID / 0 | same | not in T_q; 32651 –disease_phenotype_positive→ 22121 (SHORTCUT) | yes |
| BH2_05366 | Granite41-8B | gene/protein:drug:disease | 27933 anxiety disorder | OFF_QUESTION / PATH_INVALID / 0 | same | not in T_q; 321 –disease_protein→ 27933 (SHORTCUT; agent H1_WRONG) | yes |
| BH2_03762 | Granite41-8B | disease:drug:effect/phenotype | 22540 Vascular skin abnormality | OFF_QUESTION / PATH_INVALID / 0 | same | not in T_q; 39540 –disease_phenotype_positive→ 22540 (SHORTCUT) | yes |
| BH2_06427 | Granite41-8B | disease:gene/protein:drug | 14143 Dicoumarol (drug) | OFF_QUESTION / PATH_INVALID / 0 | same | not in T_q; 39126 –contraindication→ 14143 (SHORTCUT) | yes |
| BH2_03760 | Qwen35-9B | disease:drug:effect/phenotype | 14208 Testosterone (drug) | OFF_QUESTION / PATH_INVALID / 0 | same | answer is a bridge-type node; 31630 –indication→ 14208 (WRONG_HOP_COUNT, WRONG_TARGET_TYPE) | yes |
| BH2_05843 | Qwen35-9B | effect/phenotype:disease:drug | 14699 Lusutrombopag (drug) | ALT_VALID / SUPPORTED / 1 | same | in T_q, not A*_q; 88994 –disease_phenotype_positive→ 27626 –indication→ 14699 | yes |

Limits of this check: the independent script confirms the primary path's *length* through a BFS
shortest path. It does not re-implement the full §14.2 tie-break order. The S16–S19 test suite
covers that order.

## 6. Researcher decision required (§9.1)

Per §9.1, Gemma4-E4B and Qwen35-9B return to S21 for your review. Passing D3 does not resolve this.
The decision is yours. The options below are only those the protocol text allows, and none has been
taken.

**Gemma4-E4B** (one episode, 29500 / 32768; the threshold is exceeded by 8.8 tokens)
- (a) Review and record that no runtime revision is needed, with your reason. S22 for Gemma then
  stands as run.
- (b) Authorize a documented, frozen runtime revision. Gemma's S22 is then repeated under a new
  run ID, and `smoke_single_v135` is preserved.

**Qwen35-9B** (eight §9.1 trigger episodes, maximum 8189 / 8192; five context-length cut-offs,
both PARSE_FAILs among them; input history reset on at least 15 turns in 8 episodes, one of them
below the 90% trigger; see §3)
- (a) Review and record that no revision is needed, with your reason, keeping the 8K setting.
  `docs/qwen35_context_comparison.md` holds the existing S20 evidence at 8K, 16K and 32K, including
  its confounds.
- (b) Authorize a documented, frozen runtime revision, then repeat S22 for Qwen under a new run ID.
- (c) Any panel replacement would mean re-opening D3 at S21. Nemotron and MiMo failed D3; Ornith
  passed but was not selected.

Constraints for any choice: it must be logged in `docs/decision_log.md`, and changes are allowed
only before S26. Earlier outcomes are preserved, and the `smoke_single` and `smoke_single_v135`
records remain unchanged.
