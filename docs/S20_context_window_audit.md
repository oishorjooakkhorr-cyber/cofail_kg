# S20 context-window parse-failure audit (2026-10-20)

**Follow-up (2026-10-20):** The later full twenty-query 16K reassessment is complete for all three candidates: Gemma and Qwen PASS; Ministral FAIL from eight request timeouts. The offline evidence audit below remains the earlier checkpoint. See [full 16K reassessment](S20_full_16k_reassessment.md).

**Before Gemma, two screened models had context-related parse failures: Qwen3.5 9B and Ministral 3 8B.** Qwen has two direct context-truncation cases. Ministral has three direct cases plus one mixed case in which the initial attempt reaches the context limit but the final attempt stops normally with an invalid answer schema. Larger-context recovery has not been tested for either model.

Gemma's separate diagnostic is already documented in [S20_gemma4_16k_diagnostic.md](S20_gemma4_16k_diagnostic.md): all four original parse failures recovered valid JSON at 16K, and three recovered supported, question-valid answers. These four queries also ran continuously. Original S20 results and D3 verdicts remain unchanged.

## 1. Files created or changed

- This report; follow-up entries in `docs/decision_log.md`, `docs/progress.md`, `tasks/plan.md`, and `tasks/todo.md`.
- `results/diagnostics/s20/context-window-audit-20261020/`: offline audit driver, integrity baseline and proof, full response/parse-error evidence for all non-SUCCESS episodes, per-model summary CSV and console log.

No original episode, configuration, metric, screening table, production source, prompt, schema, dataset or scientific rule changed. No model was loaded or called for this audit.

## 2. Scope, checks and findings

Scope: all **140 official S20 episodes across seven completed candidates**. The earlier-model subset excludes Gemma and contains 120 episodes across six candidates. Pre-S20 S14 integration/template experiments are outside this S20 comparison, as are models never screened. The separate Gemma 16K diagnostic is supporting evidence, not part of the official 140-episode denominator.

| Model | Official parse failures / 20 | Context finding |
|---|---:|---|
| Qwen3.5 9B | 2 | Both final attempts terminate exactly at 8192 tokens; strong direct trace evidence of context truncation. No 16K recovery test. |
| Ministral 3 8B | 4 | Three final responses truncate at 8192; one mixed context/schema case. No 16K recovery test. |
| Llama 3.1 8B | 0 | No official parse failures. |
| Granite 3.3 8B | 0 | No official parse failures. |
| OLMo 3 7B Instruct | 0 | No official parse failures, despite some large prompts. |
| Granite 4.2 8B | 0 | Three ERROR/CONNECTION read timeouts, separate from parse failures; cause of the unreturned generations remains unresolved. |
| Gemma 4 E4B | 4 | All four recovered valid JSON in the existing separate 16K diagnostic; three of four competent. |

Total official outcomes: 126 SUCCESS, ten PARSE_FAIL and four ERROR/CONNECTION. Of the six pre-Gemma parse failures, **five have a final truncated response at the exact context boundary**, and **one has a truncated first attempt followed by a final schema omission**. All four ERROR outcomes are request read timeouts rather than episode TIMEOUT or PARSE_FAIL.

The audit loaded and validated saved episode records. For each recorded PARSE_ERROR, it replayed the original message through the unchanged `parse_final` function and reproduced the exact saved error text: **20/20 parse attempts across ten episodes**. Four assert-based checks verify the descriptive evidence-label precedence (16K recovery, final context truncation, earlier context pressure, unresolved). These are audit labels only, not new scientific gates. All seven model record counts and all aggregate totals reconcile.

Integrity after audit: all **147** official run/configuration files, **140** official metric files, the official screening-table hash, **43** pinned source/input hashes, **122** protected identities, **five** separate Gemma diagnostic run/configuration files and **13** existing Gemma diagnostic evidence files match the pre-audit baseline. No drift. Production code is unchanged, so the previously passing 598-test suite was not repeated; this investigation uses parser replays and provenance/count assertions.

### Qwen3.5 9B: two direct context-truncation cases

| Query | First failed attempt: prompt + output | Final failed attempt: prompt + output | Final text |
|---|---:|---:|---|
| BH2_03856 | 8140 + 52 = 8192 | 8169 + 23 = 8192 | Empty content. |
| BH2_03881 | 6994 + 1198 = 8192 | 6325 + 1867 = 8192 | Incomplete JSON ending inside an answer item. |

All four responses have `done_reason=length`. Generated output is below the separate 4096-token `num_predict` cap, while prompt-plus-output reaches the configured 8192 context exactly. Thus the trace specifically implicates the shared context budget rather than exhausting a 4096-token output allocation. A prompt need not itself approach 8192: BH2_03881 runs out of remaining space while producing the answer.

Qwen's existing official D3 result is PASS (18/20 SUCCESS, 15/20 competent); these two failures do not overturn that verdict. The audit does not demonstrate that a 16K rerun would produce correct answers or an improved full-block result.

### Ministral 3 8B: three direct cases and one mixed case

| Query | First failed attempt: prompt + output | Final failed attempt: prompt + output | Interpretation |
|---|---:|---:|---|
| BH2_03881 | 8050 + 142 = 8192 | 8076 + 116 = 8192 | Both terminate with length; final fenced JSON is incomplete. |
| BH2_03991 | 7142 + 1050 = 8192 | 8184 + 8 = 8192 | Both terminate with length; final output stops immediately after the status key. |
| BH2_04003 | 8033 + 159 = 8192 | 8095 + 97 = 8192 | Both terminate with length; final fenced JSON stops inside an answer item. |
| BH2_03619 | 8073 + 119 = 8192 | 8155 + 15 = 8170 | First response has length termination; final response has stop termination and omits required answers. |

In the first three rows, both attempts have `done_reason=length`, exact context saturation and fewer than 4096 output tokens. Their final incomplete JSON gives strong direct context-truncation evidence.

**BH2_03619 is different.** The final text is syntactically valid fenced JSON:

```json
{"status":"no_answer"}
```

It omits the required `answers` list, so the unchanged parser reports `Expected status and answers list`. The final response stops normally and does not exactly fill the context. Earlier context exhaustion is observed, but this final failure cannot be attributed solely to forced truncation. A larger context might alter the trajectory; recovery is untested.

Ministral's other failed episode, BH2_04425, is ERROR/CONNECTION from the unchanged 120-second request read deadline. The earlier isolated replay, with a longer diagnostic read wait, returned after 153.47 seconds with normal stop termination and 4569 prompt + 2576 output tokens (7145 total). That existing evidence supports slow buffered generation as the timeout mechanism, not an observed 8192-token cutoff. It is not a parse-failure episode or proof of full-episode success. See [S20_ministral3_timeout_investigation.md](S20_ministral3_timeout_investigation.md).

Ministral's official D3 FAIL remains based on SUCCESS 15/20=75%; competence 10/20=50% and its other D3 criteria pass. Context truncation plausibly contributes to its technical failures, but no hybrid or counterfactual D3 score was computed.

### Models without official parse failures

Llama 3.1, Granite 3.3 and OLMo 3 each saved twenty SUCCESS outcomes. Their competence/tool-use shortcomings are distinct from final-JSON parsing. Granite 4.2 saved seventeen SUCCESS outcomes and three ERROR/CONNECTION request timeouts (BH2_03953, BH2_04007 and BH2_04425). Their missing HTTP responses provide no final completion reason or token total, so this audit does not relabel those errors as context failures. High maximum prompt counts elsewhere in a model's run are insufficient to assign causality to a particular failed request.

## 3. One small real example and output

Offline parser replay for Ministral BH2_04003: final response has prompt_eval_count=8095, eval_count=97, total=8192, done_reason=length, and incomplete final JSON. The unchanged parser again raises `Expecting value: line 1 column 1 (char 0)` because the incomplete JSON code fence cannot be stripped as a complete fenced object. This is the saved parser behavior, not a new repair or altered parser. The full raw response is retained in `evidence.json` and the original episode.

For the contrasting schema case, Ministral BH2_03619's complete fenced `{"status":"no_answer"}` reproduces `Expected status and answers list`. This distinction is why the report identifies three direct Ministral cases and one mixed case rather than treating all four identically.

## 4. Assumptions and limits

"Previous models" means completed official S20 candidates before Gemma. Gemma is included as the already-tested comparison. This request authorizes saved-evidence investigation and documentation; no further inference is needed to identify the observed failure mechanisms. Larger-context recovery for Qwen/Ministral and any full-block 16K performance remain untested. An exact token-boundary observation is strong trace evidence, while changing the context and observing recovery is a separate experimental result. The audit makes that distinction explicit.

The repository graph was used for orientation; it lacks the later saved response-level evidence, so conclusions were verified against immutable episode records and the existing Gemma diagnostic. No new literature claim or external API behavior was assumed.

## 5. Design choices beyond the specification

Routine engineering: audit all seven complete S20 manifests, retain the fourteen non-SUCCESS episode records as evidence, replay every recorded parse error, distinguish exact final context truncation from earlier pressure plus final schema failure, and link the existing four-query Gemma 16K comparison. An exact-boundary check uses observed `prompt_eval_count + eval_count == num_ctx`, `done_reason=length` and output below `num_predict`; it does not introduce a new scientific threshold. Evidence labels do not modify statuses, competence, denominators, D3 or selection rules.

## 6. Manual inspection

Inspect Qwen BH2_03881 for answer-generation exhaustion despite a prompt well below 8192, Ministral BH2_03991 for only eight final output tokens, and Ministral BH2_03619 for the normal-stop schema omission. Inspect the four request-timeout records separately; no missing completion was invented. `model-summary.csv`, `evidence.json` and `integrity-after.json` contain the inventory, full raw-response evidence and verification.

No new model call, official rerun, context/configuration change, S21 selection, commit or push was performed during this audit.
