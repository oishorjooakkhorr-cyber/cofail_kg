# CoFail-KG: Final Documentation of the Model Exploration and Engineering Journey

**Evidence cutoff: 1 November 2026 (Asia/Dhaka)**

**Scope: project preparation, integration experiments, S20 screening and reassessments, S21 selection, S22 verification, and the subsequent Qwen replacement trials.**

This report reconstructs how the project arrived at its current model panel, what each tested model actually did, and which engineering changes helped particular stages succeed. It uses the repository's dated Markdown reports, decision log, saved screening tables, per-run summaries, evaluation metrics, configurations, and available episode/server logs. It is a retrospective account of the evidence available at this checkpoint; it does not claim that the pilot or the later co-failure and intervention studies have finished.

The central result is that model suitability emerged from the interaction of model behavior, tool interfaces, context capacity, memory placement, response deadlines, and final-answer formatting. Models that could produce valid JSON sometimes performed no useful graph reasoning. Models that could navigate correctly sometimes failed to finish a parseable answer. Increasing capacity helped Gemma and Ministral substantially, but did not consistently help Qwen. Qwen ultimately entered the frozen panel through its successful 8K/f32-KV block, then remained under review because S22 exposed limited context headroom. Nemotron and MiMo failed the replacement screening; Ornith passed D3 but brought different answer-quality and context-pressure problems. No replacement is recorded as selected.

| Period | Turning point | Why it mattered |
|---|---|---|
| 11–15 October | Graph/benchmark reconciliation, reference construction, population and sample freeze. | Established which answers and paths could legitimately be scored. |
| 15–16 October | Qwen3 4B transport, thinking, template, and persistence diagnostics. | Produced a verified real traversal while exposing mode and finalization limitations. |
| 17 October | Answer/path evaluators and per-agent metrics accepted. | Made grounded correctness distinguishable from parsed JSON. |
| 18–21 October | Original candidate blocks, context audit, and old-host 16K reassessments. | Identified useful models and separated schema, semantic, context, and timeout failures. |
| 28–30 October | New-host 16K/32K tests and shared resource package. | Qualified three strong 32K candidates while exposing Qwen's persistent finalization problem. |
| 30 October | Qwen 8K/f32 pass, S21 freeze, and S22 headroom triggers. | Established the selected panel and the specific reasons selection still required review. |
| 30–31 October | Nemotron, Ornith, and MiMo replacement trials. | Tested both a different developer family and Qwen-based alternatives. |
| 1 November | Ornith offline failure investigation and this synthesis. | Refined the context-limit explanation and recorded unresolved evidence/selection limits. |

## Contents

1. [Research task and meaning of success](#1-research-task-and-meaning-of-success)
2. [Preparing a trustworthy experiment](#2-preparing-a-trustworthy-experiment)
3. [Early integration: Qwen3 4B and the first successful traversal](#3-early-integration-qwen3-4b-and-the-first-successful-traversal)
4. [The original model-screening journey](#4-the-original-model-screening-journey)
5. [Context, timeouts, memory, and the reassessment stages](#5-context-timeouts-memory-and-the-reassessment-stages)
6. [Special section: how Qwen became the choice and why replacements were tested](#6-special-section-how-qwen-became-the-choice-and-why-replacements-were-tested)
7. [Engineering maneuvers and what they established](#7-engineering-maneuvers-and-what-they-established)
8. [The frozen panel, S22 results, and the current checkpoint](#8-the-frozen-panel-s22-results-and-the-current-checkpoint)
9. [What the journey establishes](#9-what-the-journey-establishes)
10. [Evidence inventory, qualifications, and verification](#10-evidence-inventory-qualifications-and-verification)

## 1. Research task and meaning of success

CoFail-KG investigates failures shared by independent local LLM agents answering multi-hop biomedical questions over PrimeKG. BioHopR supplies the questions. Each agent receives the question and starting entity, then explores the graph through two tools: `inspect_entity` and `get_neighbors`. The agents do not communicate, vote, share traces, or receive the evaluator's gold bridge, accepted relations, answer sets, or labels.

The task demands more than recalling biomedical facts. An agent has to discover the available relation labels, select the correct first-hop bridge type, follow the required second hop, handle pagination, retain the results, and submit the requested target entities in the final JSON schema. A correct-looking entity without an observed valid support path is insufficient. Answering with the source or an intermediate drug instead of a requested phenotype is also insufficient, even when the entity was genuinely retrieved.

Three outcomes must therefore remain separate:

| Term | What it means in this project | What it does not establish |
|---|---|---|
| `SUCCESS` | The final reply parses under the frozen JSON/schema rules. A valid `no_answer` also counts. | Correctness, useful tool use, or completeness. |
| Competent query | At least one submitted answer is question-valid and `SUPPORTED` by the observed trace. | An exhaustive answer to an “all” question, or high precision over every submitted item. |
| Well-formed tool call | A native call uses an approved tool and arguments matching the declared schema types. | A real relation name, a useful page, the right traversal, or a successful lookup. |

Gate D3 requires all five criteria: at least 90% well-formed attempted calls, at least 90% `SUCCESS`, competence on at least 40% of the twenty screening questions, median episode wall time at most 300 seconds, and zero `ERROR` episodes caused by `OUT_OF_MEMORY`. Thus a complete twenty-query block needs at least eighteen parsed successes and eight competent queries. Zero tool attempts gives undefined call validity (`0/0`), which does not pass. A non-OOM runtime error is retained in the success denominator but is not automatically a failure of the separate zero-OOM criterion.

Attempted calls include native calls and logged `TEXT_TOOL_CALL` occurrences. Text that merely resembles a tool call is preserved but never executed. The parser accepts a complete JSON object, optionally enclosed in a whole-message code fence. It does not extract a JSON suffix from surrounding prose. A failed final reply receives exactly one fixed JSON re-prompt; a second invalid reply becomes `PARSE_FAIL`.

These definitions explain several otherwise surprising results: Llama could have twenty `SUCCESS` records and zero competence; Granite could submit benchmark-matching but ungrounded entities; Ornith could pass D3 while producing many wrong answers on one query. The protocol and D3 rules, rather than a general impression of model quality, determine the recorded verdicts. [Sources: protocol §§9–15](frozen_pilot_protocol.md), [Gate D3](decision_rules.md#d3--model-selection-s20s21).

## 2. Preparing a trustworthy experiment

### 2.1 Establishing what the benchmark actually asks

Before comparing models, the project had to establish a defensible relationship between BioHopR questions and PrimeKG answers. The dataset contained 7,633 two-hop rows across twelve relation types, with answer-list sizes ranging from one to 890. The original population's median answer-list size was eleven and its p90 was 102. Large answer lists made pagination and final-output capacity practical concerns from the beginning.

The Troglitazone investigation illustrated why this groundwork mattered. A published description associated the drug with 202 side effects, but the local graph contained only seventeen direct side-effect neighbors. Inspection showed that 202 was reproduced by traversing from type 2 diabetes mellitus through all 49 indicated drugs and taking the union of their side effects. Troglitazone was one stored bridge, rather than the owner of all 202 direct neighbors. Treating every answer list as the neighborhood of the stored bridge would have created incorrect reference sets and misleading model scores.

The resulting methodology evaluated both BRIDGE and UNION answer constructions and adopted a construction per relation type. Nine types passed D1, covering 7,377 rows; eight adopted BRIDGE and the `disease:drug:effect/phenotype` type adopted UNION. Three failing types, covering 256 rows, were excluded through the recorded researcher decisions. The choice was not changed separately for each row to maximize agreement. An early bookkeeping error that withheld the global D1 verdict because an already failing type had a label tie was corrected without changing the underlying scientific scores. [Sources: S4 findings](S4_findings.md), [S6 implementation and investigations](S6_implementation.md), [decision log](decision_log.md).

### 2.2 Building the eligible population and frozen samples

S7 constructed evaluator reference sets, and S8 checked consistency, question leakage, saturation, and bridge multiplicity. S9 then used the researcher-selected saturation threshold of 0.50 to define the primary population. Of 7,377 rows in passing relation types, fifteen were excluded as inconsistent and 186 as leaky questions, with no overlap and no saturation exclusions. The resulting population contained 7,176 queries across nine eligible types, and D2 returned GREEN.

S10 created disjoint, deterministic samples and separate evaluator manifests and agent-input sheets. The screening set contained twenty queries, including five single-bridge and fifteen multi-bridge cases; it covered six relation types. The separate smoke set contained four queries, the pilot one hundred, and the expansion reserve four hundred. This matters when interpreting the later S22 report: its eighty episodes are twenty screening questions times four agents, not the sixteen-episode panel smoke test associated with the separate four-question smoke set.

Agents received only four sheet fields: `query_id`, `question_text`, `start_name`, and `start_id`. Evaluator reference fields remained separate. The model comparisons repeatedly reused the same ordered screening questions, making paired inspections possible while also making later tuning outcome-informed. Those repeated blocks are not twenty-eight independent test datasets. [Sources: S9](S9_implementation.md), [S10](S10_implementation.md), [sampling report](../data/processed/manifests/sampling_report.md).

### 2.3 Making the graph tools neutral, deterministic, and inspectable

The T1 tools expose real graph information without handing the agent the accepted solution. `inspect_entity` lists identity and relation summaries; `get_neighbors` returns sorted, paginated neighbors with counts and `has_more`. The default screening page size is fifty and the charged tool-call budget is thirty. Errors consume budget. Neighbor ordering is by numeric canonical ID; the graph follows the frozen either-direction convention.

The tools do not provide a list of evaluator-approved relation choices. Agents must inspect the graph and use the actual labels. Consequently, repeated guesses such as `side_effect`, `treats`, or `gene_protein_disease` can be schema-valid strings yet fail as graph requests. This design allowed the study to distinguish interface compliance from relation discovery and navigation.

S12 added complete call logs, reconstruction of the observed trace graph, deterministic path handling, and write-once episode records. S16–S19 added normalization, answer labels, support-path labels, hop-1 diagnostics, and per-agent metrics. Their separation was essential: the model should not be helped by the same evaluator that later decides whether its route was valid. The saved successful S14 example was repeatedly replayed through these evaluators without generating a fresh answer. [Sources: S11](S11_implementation.md), [S12](S12_environment_verification_20261016.md), [S16](S16_implementation.md), [S17](S17_implementation.md), [S18](S18_implementation.md), [S19](S19_implementation.md).

### 2.4 Resolving an apparent leakage failure without hiding it

S15 initially failed a literal whole-word scan because “Folic acid,” an alternative bridge, appeared inside the canonical starting name “folic acid deficiency anemia.” The researcher later authorized a narrowly defined source-name-overlap exemption. The original strict failure was retained, the affected rows were flagged, and later co-failure reporting was required both with and without the flagged queries. Four overlaps were recorded across all 524 sampled rows.

This was a documented methodological amendment based on lexical inspection, with the earlier S14 diagnostics acknowledged; it was not evidence that those words had no behavioral effect. It also did not inject bridge identities or change the actual question. The amendment and manual review made the leakage stage acceptable while preserving its history. [Source: S15 report and approval](S15_implementation.md).

## 3. Early integration: Qwen3 4B and the first successful traversal

The first Qwen experiments used local `qwen3:4b`, not the later selected `qwen3.5:9b`. They were integration diagnostics, not twenty-question D3 candidate blocks.

### 3.1 Synthetic success did not predict the first biomedical episode

S13 established that the Ollama client could preserve raw responses and thinking, identify the installed model, and receive a native synthetic `add(2,3)` call. The client later made the thinking flag explicit in every request rather than relying on a server default. These checks validated the transport and response envelope; they did not establish biomedical competence.

The first S14 biomedical episode, BH2_00461, ran with thinking enabled, context 8192, and an output cap of 4096. It ended `PARSE_FAIL` after about 90.11 seconds. Both responses used the entire 4096-token allowance for thinking while leaving final content empty. No native tool call was made. Prompt counts were only 598 and 627, so this was an output-budget problem rather than a full context window or GPU OOM.

The distinction was valuable: a test suite and working transport did not mean the model was completing the requested interaction. The runner correctly preserved the failure instead of turning imagined tool interactions inside reasoning text into real graph calls. [Sources: S13](S13_implementation.md), [S14](S14_implementation.md).

### 3.2 More output enabled traversal, but final formatting still failed

The next authorized diagnostic requested `think=false` and raised the per-turn output allowance to 6144 while retaining the 8192 context. Four native calls now followed the route:

```text
14097 (starting drug)
  --drug_protein--> 111 (TTR)
  --disease_protein--> 21 disease entries
```

The tool results were checked independently against the graph-inspection CLI. Both proposed final replies contained a JSON suffix matching the twenty-one retrieved entries. Nevertheless, reasoning text preceded that JSON, so the episode again ended `PARSE_FAIL`, after about 174.11 seconds. The strict parser was not relaxed.

Render-only inspection found two concrete issues. Tool definitions were serialized as Go structure text instead of JSON, and the rendered assistant prefix did not respond to `think=false`. The diagnostic also showed why setting a boolean in the client was insufficient: the template had to translate it correctly into the model's actual prompt. GPU capacity was adequate, with sampled usage around 4.60 GiB and no OOM. [Source: no-think/6144 diagnostic](S14_nothink6144_diagnostic.md).

### 3.3 Template repair produced an accepted integration example

A separate diagnostic tag, `cofail-qwen3:4b-templatefix`, preserved the original model. The template used JSON serialization for each tool definition and closed the initial thinking block when thinking was explicitly disabled. Render-only checks validated the schema text before generation.

The single repeat completed `SUCCESS` in about 101.51 seconds. Four native calls again retrieved twenty-one diseases; the final answer matched those entries. The first final reply still contained reasoning, but the existing one allowed JSON re-prompt produced a standalone valid object. Later evaluator replay classified all twenty-one retained answers as GOLD and SUPPORTED.

This success had an important limit. GGUF metadata identified the installed weights as **Qwen3-4B-Thinking-2507**. Repairing a template could fix serialization, but it could not establish reliable non-thinking behavior for thinking-only weights. The successful variant remained a diagnostic artifact. P1 was subsequently approved and frozen; the result did not justify using these weights as the later non-thinking experimental default. [Source: template repair and corrected interpretation](S14_template_repair.md).

| Early diagnostic | Actual behavior | Result | Engineering lesson |
|---|---|---|---|
| Qwen3 4B, thinking true, output 4096 | Thinking consumed both replies; no native tools. | PARSE_FAIL | A small prompt can still exhaust the output allowance. |
| Same weights, requested false, output 6144 | Four useful graph calls; reasoning mixed with final JSON. | PARSE_FAIL | Traversal and final-schema compliance are separate. |
| Separate repaired-template variant | Four useful calls; fixed re-prompt yielded valid JSON. | SUCCESS | Rendering checks and correct serialization repaired a concrete interface problem, while weight-mode limitations remained. |

## 4. The original model-screening journey

### 4.1 From the planned pool to measured candidates

The original S20 plan targeted roughly 7B–9B local models on an RTX 3060 Ti with 8 GB VRAM, using Ollama 0.40.4 and non-thinking operation. Its initial pool listed Llama 3.1 8B, Qwen3 8B, Granite 3.3 8B, Mistral 7B, Command R7B, Qwen2.5 7B, Aya Expanse 8B, and Granite 3.2 8B. Qwen3.5 9B was added as an extra candidate before its official results. Later, the researcher preferred updated models of a similar scale, leading to the newer Ministral, OLMo, Granite, and Gemma trials.

Being named in the pool or present in a model store is not evidence of a completed test. This report finds complete D3 records for twelve S20 candidates, including the three later replacement trials. It does not assign results to the planned-but-unmeasured tags. The early Qwen3 4B integration work is reported separately.

The original settings were temperature 0, seed 42, `think=false`, context 8192, output cap 4096, thirty charged calls, fifty neighbors per page, a 120-second request timeout, and a 600-second episode limit. Frozen P1/T1, query order, and evaluator definitions remained fixed through these original blocks. [Sources: S20 authorization in decision log](decision_log.md), [updated-pool proposal](S20_updated_model_pool_proposal.md).

### 4.2 Results of every completed original 8K block

Every row below represents twenty questions. Times are median episode wall seconds, rounded for readability; the companion [run inventory](final_model_run_inventory.csv) retains source values and identities.

| Candidate | Well-formed / attempted calls | SUCCESS | Competent | Median seconds | D3 | Decisive failure or strength |
|---|---:|---:|---:|---:|---|---|
| Llama 3.1 8B | 0/620 | 20 | 0 | 22.13 | FAIL | Repeated invalid argument types and guessed relations. |
| Qwen3.5 9B | 210/210 | 18 | 15 | 26.38 | PASS | Useful native traversal; two context-bound parse failures. |
| Granite 3.3 8B | 0/8 | 20 | 0 | 13.60 | FAIL | Textual pseudo-tool calls; no executed KG calls. |
| Ministral 3 8B | 197/197 | 15 | 10 | 62.85 | FAIL | Four parse failures and one request timeout. |
| OLMo 3 7B Instruct | 60/62 | 20 | 0 | 8.95 | FAIL | Some real lookups, but no supported question-valid answers. |
| Granite 4.2 8B | 327/327 | 17 | 6 | 120.25 | FAIL | Three request timeouts and insufficient competence. |
| Gemma 4 E4B | 149/149 | 16 | 11 | 11.97 | FAIL | Four parse failures despite useful graph work. |
| Granite 4.1 8B | 217/217 | 20 | 14 | 61.33 | PASS | Completed all final outputs and supported answers on fourteen queries. |
| Command R7B | 0/0, undefined | 19 | 0 | 2.89 | FAIL | No tool use and no supported answers. |

All original blocks recorded zero OOM episodes. These results show suitability under the recorded harness and settings, not an unrestricted ranking of the model families. [Machine source: original screening table](../results/diagnostics/screening/screening_table.csv).

### 4.3 Llama 3.1: repeated action without successful graph access

Llama produced exactly `{"status":"no_answer","answers":[]}` on every question. Each episode emitted thirty-one `get_neighbors` calls, of which thirty were charged and the last encountered the exhausted budget. Across all twenty questions, all 620 attempts supplied `page` as a string rather than an integer. Llama never called `inspect_entity` and repeatedly guessed relation labels, including unavailable labels.

This was not a memory or parsing failure. Its final JSON parsed, prompts were relatively small, and there were no timeouts or OOM events. The failure lay in argument compliance and failure to learn the graph's actual relation vocabulary from the tools. The project explicitly retained exact-type checking: coercing `"1"` to `1` would have changed the measured interface behavior. No successful graph call or supported answer was produced. [Source: Llama report](S20_llama_screening.md).

### 4.4 Granite 3.3: synthetic tool capability did not transfer to the real task

Granite 3.3 passed the simple native addition probe but produced zero native tool calls in the biomedical episodes. Eight logged textual tool-call occurrences contributed to the attempted-call denominator, but were not executed. All twenty final outputs parsed.

The model submitted 69 answer items: 53 OFF_QUESTION, fifteen UNRESOLVED, and one GOLD. Every resolved item was UNGROUNDED. Even the benchmark-matching item did not qualify as supported competence, because no executed graph trace justified it. Granite 3.3 therefore failed both call validity and competence. This was an example of task-dependent failure to engage the tool channel, rather than proof that the transport could not represent tool calls. [Source: Granite 3.3 report](S20_granite33_screening.md).

### 4.5 OLMo 3: correct envelopes, weak continuation and answer selection

OLMo emitted 62 native attempts, sixty of them schema-well-formed. It made 51 successful KG calls, but tool use occurred on only six questions. Eighteen final outputs were `no_answer`; the other two supplied twelve answer items, all OFF_QUESTION and PATH_INVALID. Competence remained zero.

The model sometimes abstained immediately, sometimes stopped after a failed relation guess, and sometimes returned a first-hop or otherwise invalid answer after genuine graph work. Its passing call-validity rate and twenty parsed successes did not solve the actual two-hop task. Enlarging context alone had no demonstrated remedy for this pattern; no complete 16K reassessment is recorded for OLMo.

One detail in the old prose report requires correction: the two malformed calls in BH2_03762 were not simply missing the optional `page` field. Inspection of the locally available raw messages shows one `get_neighbors` call missing required `relation`, and another using a malformed string-valued `page`. The archived 60/62 count and D3 FAIL are unchanged. [Sources: OLMo report](S20_olmo3_screening.md), [frozen T1 schema](../src/cofail_kg/agents/tool_schemas.py), [saved episode](../results/runs/screening/primary-3060ti-20261018/BH2_03762__OLMo3-7B__a1.json).

### 4.6 Granite 4.2: newer did not mean better in this environment

Granite 4.2 used native tools with 327/327 well-formed calls. Nevertheless, three requests exceeded the 120-second read timeout, and only six questions were competent. Seven episodes hit the call budget. Its seventeen parsed successes and median of about 120.25 seconds were insufficient to overcome the failed success and competence criteria.

The saved timeouts occurred on BH2_03953, BH2_04007, and BH2_04425. The server remained accessible afterward, but the failed generations returned no completion to inspect. The logs therefore do not justify relabeling these requests as context truncation, network loss, or OOM. Automatic partial offload was observed; its individual contribution to those failures was not isolated. Granite 4.1's later stronger result confirms that release-number recency was not a reliable selection rule. [Source: Granite 4.2 report](S20_granite42_screening.md).

### 4.7 Command R7B: fast abstention was not competence

Command R7B emitted no native or textual tool attempts. Nineteen final outputs parsed, while one array-shaped reply failed parsing. Most parsed replies were `no_answer`; the few submitted entities were either off-question and ungrounded or unresolved. The 2.89-second median reflected very short interactions rather than successful graph reasoning.

Its addition probe had also answered directly without calling the tool. The full authorized screening block measured that behavior without inventing an additional synthetic-test gate or altering the prompt. It failed undefined call validity and zero competence. [Source: Command R7B report](S20_command_r7b_screening.md).

### 4.8 Granite 4.1: a usable candidate with persistent semantic mistakes

Granite 4.1 passed at the original 8K settings: twenty successes, fourteen competent queries, and 217/217 well-formed native calls. Of 568 submitted items, 525 were question-valid and supported; 43 were OFF_QUESTION/PATH_INVALID. It could execute useful two-hop traversals and return complete small answers, but did not consistently choose the correct target type or path on every question.

Its later 16K test on the 3060 Ti was stopped during query sixteen. Fifteen final records existed: six successes and nine request-timeout errors. That incomplete block has no final D3 verdict. Even five additional successes could only have reached eleven of twenty, so it could not have passed the success threshold; nevertheless, no results were invented for the interrupted or unstarted queries. The original 8K pass remained valid history. [Sources: Granite 4.1 original report](S20_granite41_screening.md), [stopped 16K report](S20_granite41_16k_stopped.md).

Gemma, Ministral, and Qwen had sufficiently strong useful behavior to justify the more detailed capacity investigations described next. Their original failures were preserved throughout.

## 5. Context, timeouts, memory, and the reassessment stages

### 5.1 Diagnosing context pressure before changing the experiment

The project inspected failed responses rather than treating every `done_reason=length` as the same problem. A completion can hit the per-turn output cap, or it can run out of the context shared by prompt history and generated output. The two require different interpretations. A normal-stop reply can also fail the schema despite remaining capacity.

An offline audit reproduced twenty parser failures across ten failed episodes from the first seven completed candidates. Qwen had two direct context-bound cases; Ministral had three direct cases plus one mixed context/schema case; Gemma had four boundary-related parse failures. Granite 4.2's request errors had no returned completion and were kept separate.

For example, Qwen BH2_03856 ended with 8169 prompt tokens and 23 generated tokens, exactly 8192. By contrast, Ministral BH2_03619 eventually stopped normally with `{"status":"no_answer"}` and no required `answers` list. Earlier boundary pressure existed there, but the final schema failure was not itself a demonstrated forced cutoff. This discipline prevented a single “needs more context” explanation from swallowing distinct failures. [Source: context-window audit](S20_context_window_audit.md).

### 5.2 Gemma: from selected recovery to a full passing block

Gemma's original 8K block had sixteen successes and eleven competent queries. A separate authorized diagnostic reran only its four failed questions at 16K. All four parsed; three recovered supported answers. The fourth returned six wrong answers despite valid JSON. This was evidence that added room could repair particular formatting failures, not a complete D3 result.

The project then ran a fresh full twenty-question 16K block. Gemma reached nineteen successes and fourteen competent queries, passing D3. Three formerly failed questions recovered 77, 66, and ninety supported answers. BH2_03762 still failed parsing in that fresh block, despite having parsed in the selected diagnostic. The earlier diagnostic was not substituted into the denominator.

This is a concrete example of an engineering change making a stage successful: the increased context removed enough observed finalization failures for the complete block to pass. It did not make every run identical or every answer correct. [Sources: selected Gemma diagnostic](S20_gemma4_16k_diagnostic.md), [full 16K reassessment](S20_full_16k_reassessment.md).

### 5.3 Ministral: separating deadline failure from graph-tool failure

Ministral's original 8K block showed useful native graph work but finished only fifteen questions successfully. Four outputs failed parsing and BH2_04425 hit the request timeout. A reconstructed replay of that one failed HTTP request returned after 153.47 seconds; generation alone took 143.57 seconds for 2576 tokens, exceeding the original 120-second read deadline. The preceding KG operation had taken about 0.011 seconds.

The client used buffered, non-streaming responses. An active long generation could therefore exceed the request read limit while remaining well below the 600-second episode limit. `CONNECTION` was the client's broad error category, not evidence that the internet or graph server had failed. The replay returned prose rather than final JSON, so a longer wait alone did not prove full-episode success.

A separately authorized full-query diagnostic with a longer request allowance subsequently completed in about 237 seconds and returned 65 supported answers. It still missed pagination and reached only 65/75 benchmark recall. This supported the deadline explanation while preserving the original failed episode.

The complete official 16K reassessment did not solve Ministral on the 8 GB host: it produced twelve successes, twelve competent queries, and eight request-timeout errors. More context permitted longer trajectories while the same request deadline still cut off generations. Zero `PARSE_FAIL` in that block did not establish universal format recovery, because eight episodes ended before final parsing. [Sources: timeout investigation and separate diagnostic](S20_ministral3_timeout_investigation.md), [full 16K reassessment](S20_full_16k_reassessment.md).

### 5.4 KV-cache exploration: a substantial speed gain with behavioral consequences

The Ministral speed diagnostics tested default f16 KV, forced Flash Attention, q8_0 KV, and q4_0 KV on the 3060 Ti. At approximately fourteen thousand prompt tokens, measured generation rates were 6.02, 5.93, 11.97, and 32.12 tokens/second respectively. Forcing Flash Attention alone added little because the baseline already enabled it. Smaller caches reduced memory demand and allowed more layers onto the GPU: 26/35 with f16, 30/35 with q8_0, and 34/35 with q4_0. None achieved complete residency in that diagnostic.

The clean seventeen-request matrix followed an important operational correction. Earlier cleanup had stopped processes named `ollama*` while leaving `llama-server.exe` runners alive. Three orphan runners survived, retaining memory. The final procedure checked and removed the owned runners before each restart, retained the earlier failures, and verified restoration of the original server environment afterward. Repeated-token benchmark inputs were also replaced with varied context and prose after the earlier trials hit a repetition-limit error.

Three-query episode diagnostics and four exploratory twenty-query blocks then examined whether the speed gain preserved behavior. Under the exploratory longer deadlines, the two f16 blocks each had seventeen successes and fifteen competent queries; the two q4 blocks each had nineteen successes and seventeen competent queries, with much shorter median times. However, cross-cache answer sets and tool trajectories often differed. These were not official D3 blocks: request and episode deadlines had been raised to 600 and 1800 seconds, and one exploratory attempt was rerun after a wrapper interruption.

The defensible lesson is that KV precision can change both practical speed and the observed failure pattern. The small, ordered diagnostic design does not establish that cache precision alone caused every trajectory difference, even though one exploratory report states a stronger causal conclusion. The final official 5060 Ti blocks used f16 for Ministral, Gemma, and Granite rather than silently importing the q4 diagnostic setting. [Sources: clean speed report](../results/diagnostics/ministral_speed/clean/results.md), [selected episode tests](../results/diagnostics/ministral_speed/kv_q4_episodes/results.md), [exploratory blocks](../results/diagnostics/ministral_speed/explore/results.md).

### 5.5 Moving to the RTX 5060 Ti: verifying the environment instead of assuming it

The later host had an RTX 5060 Ti with 16 GB VRAM, Ryzen 7 7700, approximately 31 GiB usable RAM, and Ollama 0.40.12. This was a different host/runtime condition from the original 3060 Ti and Ollama 0.40.4. Weight digests were preserved, but hardware, driver, CPU/RAM, runtime, and placement changed together. Improvements cannot be attributed to the GPU alone.

The new launchers isolated their server on port 11435, used the explicit model store, pinned source/input hashes, recorded actual cache types and context lengths, and checked GPU-layer logs in addition to `/api/ps`. This mattered for Gemma, whose unusually small API size accounting did not represent total GPU use. Logs verified 43/43 main layers; its later 32K setup also recorded 5/5 draft layers and retained the same speculative settings.

Fresh 16K results were:

| Candidate | Calls | SUCCESS | Competent | Median seconds | D3 |
|---|---:|---:|---:|---:|---|
| Ministral 3 | 179/179 | 18 | 17 | 45.31 | PASS |
| Gemma 4 E4B | 185/185 | 19 | 14 | 10.85 | PASS |
| Granite 4.1 | 236/236 | 20 | 16 | 38.87 | PASS |
| Qwen3.5 | 259/259 | 16 | 12 | 30.63 | FAIL |

Ministral no longer had request timeouts, and its competence increased substantially. Granite completed the full block without the timeouts that had dominated its stopped old-host 16K test. Gemma retained the same aggregate success/competence counts as its historical 16K block but changed several individual answers and which query failed. Qwen became fully GPU-resident yet failed the success threshold. Full residency established feasibility and removed an observed placement limitation; it was not a guarantee of reliable final answers. [Sources: Ministral 16K](S20_ministral3_5060ti_16k.md), [Gemma 16K](S20_gemma4_5060ti_16k.md), [Granite 16K](S20_granite41_5060ti_16k.md), [Qwen 16K](S20_qwen35_5060ti_16k.md).

### 5.6 Same-host 32K: clear recoveries for two models, different limits for the others

Separate full 32K blocks retained the 4096 output cap and 120-second request deadline:

| Candidate | Calls | SUCCESS | Competent | Median seconds | D3 |
|---|---:|---:|---:|---:|---|
| Ministral 3 | 180/180 | 20 | 19 | 45.08 | PASS |
| Gemma 4 E4B | 188/188 | 20 | 16 | 11.09 | PASS |
| Granite 4.1 | 233/233 | 20 | 16 | 37.38 | PASS |
| Qwen3.5 | 294/294 | 13 | 12 | 28.63 | FAIL |

For **Ministral**, BH2_03619 and BH2_03879 recovered parsing and competence, contributing fifteen and 113 supported answers. All other eighteen supported-ID sets were unchanged. On BH2_03879 the first final still hit the 4096 output cap, but the larger context left room for the standard JSON retry to finish. This gives a specific explanation for the observed recovery. The model still failed BH2_03750 through incorrect relation guesses despite ample capacity. Its 635 scored items were all supported, but many competent answers had low recall.

For **Gemma**, BH2_03879 recovered 86 supported answers and BH2_04003 changed from wrong-target drug IDs to 74 supported phenotypes. The other eighteen supported sets were unchanged. These two gains increased supported items from 569 to 729. Some failures remained semantic: direct disease–phenotype or gene–disease shortcuts could yield real entities, including benchmark GOLD entities, while violating the question's required route. More context did not repair these below-capacity errors.

For **Granite 4.1**, competence and the total of 610 supported answers did not increase. One query exchanged two supported IDs, and another added 25 invalid shortcut answers while keeping its valid answers. Backend evidence showed that a 16K context shift discarding 8189 tokens was absent at 32K, but removing that measured shift did not improve overall coverage. A capacity improvement can therefore coexist with unchanged competence and worse precision on a particular query.

For **Qwen**, the extra room did not fix finalization. Seven parse failures remained, including cases at the total context boundary, cases hitting the output cap, and a case failing well below either cap. The next section follows this history in detail. [Sources: Ministral 32K](S20_ministral3_5060ti_32k.md), [Gemma 32K](S20_gemma4_5060ti_32k.md), [Granite 32K](S20_granite41_5060ti_32k.md), [Qwen 32K](S20_qwen35_5060ti_32k.md).

### 5.7 A shared resource package did not produce four passing models

The next comparison used 32K context, an 8192 output cap, and a 240-second request deadline for all four candidates. The episode cap remained 600 seconds. Both output cap and request deadline changed, so this was a resource-package reassessment, not an isolated test of either variable.

| Candidate | Calls | SUCCESS | Competent | Median seconds | D3 |
|---|---:|---:|---:|---:|---|
| Gemma 4 E4B | 188/188 | 20 | 16 | 10.78 | PASS |
| Ministral 3 | 180/180 | 19 | 18 | 44.58 | PASS |
| Granite 4.1 | 233/233 | 20 | 16 | 36.90 | PASS |
| Qwen3.5 | 301/301 | 14 | 13 | 28.27 | FAIL |

Gemma gained eight supported items on two questions. Granite's supported sets and labels were unchanged. Qwen recovered 236 supported answers on BH2_03881 but still had six parse failures. Ministral's lower count included a preserved host-sleep timeout: the computer slept for about 84 minutes during BH2_03953. That is infrastructure contamination, not evidence that normal model generation required that elapsed time. A separate two-answer loss on BH2_03879 must not be attributed to the sleep.

Qwen's block was interrupted with thirteen final records saved. Before resuming, a version guard detected that the installed app had advanced from 0.40.12 to 0.40.13 and stopped execution. The pinned 0.40.12 runtime was recovered into an isolated location from a signed installer, verified, and used to resume the seven unsaved queries. Completed records were not retried. This preserved runtime identity without changing the installed application.

Only three candidates passed this common 32K package. The subsequent mixed-runtime panel selection was an explicit researcher decision, documented at S21 rather than inferred from these results. [Source: shared-resource report](S20_shared_resources_32k.md).

## 6. Special section: how Qwen became the choice and why replacements were tested

### 6.1 Why Qwen remained worth investigating

Qwen3.5 was not retained because every run succeeded. It was retained because it repeatedly demonstrated useful native graph reasoning, passed complete screening blocks under specific settings, represented a distinct developer family, and remained stronger on query-level competence than the subsequently tested replacements at their recorded settings.

Its first full 8K block was already a strong contrast to Llama and Granite 3.3: 210/210 well-formed calls, eighteen parsed successes, and fifteen competent queries. The agent could inspect entities, discover relations, traverse two hops, paginate, and produce supported lists. BH2_00461 used four calls through TTR and returned all twenty-one supported answers. The weakness was not a universal inability to use tools.

It also had real semantic errors. BH2_03760 explored the intended disease–drug–side-effect route but submitted drug bridge IDs instead of phenotypes. Some competent queries contained only one valid answer, with recall below 1%. Qwen's early 75% competence should therefore be read as broad presence of some supported answers, not a 75% rate of fully correct, exhaustive responses. [Source: original Qwen screening](S20_qwen35_screening.md).

### 6.2 The first obstacle: fitting the exact model on 8 GB

Before official Qwen screening, the team investigated its partial CPU placement. The primary host reported about 88% of the loaded accounting size in VRAM. Captured loader logs showed 32/33 layers on GPU, including one actual repeating text layer remaining on CPU. This was not merely the multimodal projector being counted on the host.

The fitting calculation recorded a 70 MiB shortfall against its free-memory target and a projector reserve. Closing unused GPU applications and repeating the unchanged load did not eliminate the offload. The researcher accepted that measured placement before authorizing the full block. The resulting 26.38-second median was therefore not presented as a fully GPU-resident speed measurement.

This phase established two habits that persisted: use exact digests rather than a moving tag, and inspect loader/cache evidence rather than trusting a single “GPU percentage.” The Qwen3.5 digest stayed `56671c2ab9385f9cfcb404638e32cd62d88e3501d44822208363c010179a3c90` through the reported comparisons. [Source: Qwen preflight and memory investigation](S20_qwen35_preflight.md).

### 6.3 The six complete Qwen screening conditions

The complete sequence is the clearest explanation of how Qwen became the chosen fourth agent:

| Condition | Context / KV | Output / request cap | Calls | SUCCESS | Competent | Median seconds | D3 |
|---|---|---|---:|---:|---:|---:|---|
| 3060 Ti, original | 8K / f16 | 4096 / 120 s | 210/210 | 18 | 15 | 26.38 | PASS |
| 3060 Ti, full reassessment | 16K / f16 | 4096 / 120 s | 263/263 | 19 | 13 | 56.84 | PASS |
| 5060 Ti, fresh block | 16K / f16 | 4096 / 120 s | 259/259 | 16 | 12 | 30.63 | FAIL |
| 5060 Ti, larger context | 32K / f16 | 4096 / 120 s | 294/294 | 13 | 12 | 28.63 | FAIL |
| 5060 Ti, shared resources | 32K / f16 | 8192 / 240 s | 301/301 | 14 | 13 | 28.27 | FAIL |
| 5060 Ti, restored 8K with f32 KV | 8K / f32 | 4096 / 120 s | 232/232 | 18 | 14 | 18.52 | PASS |

These are six separate twenty-question blocks, not a combined denominator. All used the same pinned model weights and the same screening questions. Later blocks followed inspection of earlier outcomes. [Sources: original 8K](S20_qwen35_screening.md), [old-host 16K](S20_full_16k_reassessment.md), [new-host 16K](S20_qwen35_5060ti_16k.md), [32K](S20_qwen35_5060ti_32k.md), [shared resources](S20_shared_resources_32k.md), [8K/f32](S20_qwen35_5060ti_8k_f32.md).

### 6.4 Why 16K initially looked successful, and why that was incomplete

On the old host, increasing context to 16K raised parsed successes from eighteen to nineteen. Both original parse failures now produced valid `no_answer` objects. This repaired formatting but did not create competent answers on those questions. At the same time, other answer trajectories changed and total competence declined from fifteen to thirteen.

BH2_03991 became the new parse failure. Its first final attempt reached 16379 prompt plus five completion tokens, then the permitted re-prompt emitted a native tool call with empty final content rather than the required JSON. The runner preserved the failure. The result justified a D3 pass at that condition, while already warning that extra context could change trajectories and leave finalization unresolved.

On the 5060 Ti at 16K, all 33 layers were verified on GPU, but four parse failures reduced success to sixteen. BH2_03953 lost the 140 supported answers it had returned in the historical 16K block, reducing competence to twelve. That query hit the 4096 output allowance while compiling prose, then emitted a tool call instead of a valid final reply. Faster hardware and full residency did not repair this interaction pattern.

### 6.5 Why 32K and a larger output allowance were insufficient

At 32K with the 4096 output cap, Qwen retained the same twelve competent supported-answer sets as the same-host 16K run, while three valid `no_answer` outputs became parse failures. The seven failures had several mechanisms:

- BH2_03879 and BH2_04003 reached the total 32768-token boundary on both final attempts.
- BH2_03856, BH2_03881, BH2_03953, and BH2_03991 hit the output allowance during the first proposed final, then failed the single allowed finalization retry.
- BH2_03619 failed below both caps: prose preceded the proposed object and the retry produced an empty-content tool call.

The shared 8192-output/240-second condition rescued BH2_03881, adding 236 supported answers and increasing competence from twelve to thirteen. Yet success rose only from thirteen to fourteen, still far short of eighteen. Some failures now had spare capacity: BH2_03953 generated 5008 tokens and BH2_03991 6147 before their unsuccessful retries. Those observations show that removing the old 4096 cap was not sufficient for valid finalization. Other failures still saturated 32K on the retry.

The practical explanation is that longer histories and longer outputs gave Qwen room to explore or enumerate more, but also allowed lengthy prose and fragile transitions back to final JSON. The evidence identifies concrete boundary and final-turn failures; it does not isolate a single training or architecture cause for them. No parser relaxation, extra retries, final-turn tool execution, or P2 rescue was introduced to manufacture a passing block.

### 6.6 Returning to 8K/f32 produced the evidence used at S21

The researcher next requested one complete Qwen block at 8K context and f32 KV cache on the same 5060 Ti. Runtime guards verified actual f32 K and V allocations, 33/33 GPU layers, context 8192, effective Flash Attention, and the pinned Ollama 0.40.12 executable. A keep-awake mechanism held for the block.

Qwen reached eighteen successes and fourteen competent queries, with 232/232 well-formed calls and a median of 18.52 seconds. Two retained parse failures, BH2_03879 and BH2_03991, had empty final content. Supported question-valid items totaled 301. Compared with the original old-host 8K block, it gained competence on two questions and lost it on others; success remained eighteen while competence moved from fifteen to fourteen.

This block provided an observed passing configuration. It did **not** prove that f32 precision was the cause of the recovery. Context, output allowance, and deadline differed from the shared 32K block, and there was no same-host 8K/f16 control. Against the historical 3060 Ti block, host, GPU, runtime build, placement, and cache precision all differed. The correct conclusion is that the 8K/f32 package passed in the measured block.

The researcher then explicitly chose mixed D3 evidence: Gemma, Ministral, and Granite from the shared 32K package, and Qwen from the 8K/f32 block. Four passing developer families could now be frozen. Qwen was the fourth selected agent, with fourteen competent questions compared with eighteen for Ministral and sixteen each for Gemma and Granite. It was a qualifying complementary family, rather than the top performer on the chosen evidence. [Sources: Qwen 8K/f32 report](S20_qwen35_5060ti_8k_f32.md), [30 October S21 decision](decision_log.md), [frozen runtime configuration](../configs/pilot.yaml).

### 6.7 S22 explained why the search did not end with selection

The frozen Qwen configuration had no margin on the D3 success threshold: eighteen of twenty was exactly the minimum. Its largest prompt was 8189 of 8192 tokens, leaving three tokens of nominal prompt headroom at that observation. Passing D3 therefore did not establish adequate context reserve.

The completed S22 run reproduced eighteen successes and two parse failures for Qwen. Eight episodes exceeded 90% of the configured context, triggering the protocol's return-to-S21 review rule. Gemma also triggered the rule once at 29500/32768, despite twenty parsed successes. Progression paused for researcher review; no automatic runtime increase followed.

The replacement trials were therefore motivated by a concrete unresolved need: retain useful supported graph behavior and family coverage while improving robustness and headroom. The records do not show that Qwen had already been removed. [Sources: S22 summary](../results/diagnostics/smoke_single_summary.md), [protocol §9.1](frozen_pilot_protocol.md), [decision log](decision_log.md).

### 6.8 Why Ornith, MiMo, and NVIDIA Nemotron were relevant candidates

The replacement search explored two Qwen-based alternatives and a separately developed NVIDIA model. Ornith and MiMo offered a way to test whether additional training on Qwen-related weights would change the behavior that made Qwen useful but fragile. Nemotron offered a different developer lineage and model architecture. This is the rationale for testing them, not a claim that the underlying weights guaranteed transfer to biomedical graph reasoning.

For lineage, the local Ornith report records the researcher's confirmation that Ornith 1.5 used Qwen3.5 weights, consistent with its logged `qwen35` architecture. The publisher's model card also describes the Ornith family as extending models built on Qwen3.5 and Gemma4. MiMo's official card explicitly identifies the tested model as supervised fine-tuning of Qwen3.5-9B on MiMo-generated data. Historical run manifests that said lineage was unverified are preserved rather than rewritten. The MiMo lineage attribution here adds later verification to that earlier record. [Primary identity sources, consulted 1 November 2026: Ornith](https://huggingface.co/ornith-ai/Ornith-1.5-9B), [MiMo](https://huggingface.co/XiaomiMiMo/MiMo-V2.6-Distill-Qwen-9B).

NVIDIA's official card identifies Nemotron Nano 9B v2 as its hybrid Mamba–Transformer model. The project tested a Q4_K_M distribution and an explicitly derived no-thinking template variant, described below. It should be treated separately from the two Qwen-weight replacement candidates; using teacher-generated data is not the same as sharing the same base weights. [Primary identity source: NVIDIA](https://huggingface.co/nvidia/NVIDIA-Nemotron-Nano-9B-v2).

All three replacement blocks used twenty original screening questions, 32768 context, 8192 output tokens, f16 KV, a 240-second request deadline, 600-second episode limit, budget thirty, page size fifty, temperature zero, seed 42, thinking disabled, and pinned Ollama 0.40.12. P1, tools, parser, re-prompt, evaluators, and D3 thresholds stayed unchanged. Their settings therefore match the panel's 32K package, while the selected Qwen evidence remains its different 8K/f32 package.

| Candidate / comparison | Well-formed calls | SUCCESS | Competent | Median seconds | Supported question-valid items | D3 |
|---|---:|---:|---:|---:|---:|---|
| Selected Qwen evidence, 8K/f32 | 232/232 | 18 | 14 | 18.52 | 301 | PASS |
| Qwen shared package, 32K/f16 | 301/301 | 14 | 13 | 28.27 | 658 | FAIL |
| NVIDIA Nemotron Nano 9B v2, derived no-think | 60/60 | 20 | 0 | 5.64 | 0 | FAIL |
| Ornith 1.5 9B | 315/315 | 18 | 11 | 47.57 | 572 | PASS |
| MiMo-V2.6-Distill-Qwen-9B | 0/0, undefined | 20 | 0 | 1.97 | 0 | FAIL |

Item totals and query-level competence measure different things. A model returning many supported items on a few questions can have a larger item total but lower competence across questions. [Sources: replacement reports](S20_nemotron9b_5060ti_32k.md), [Ornith](S20_ornith15_5060ti_32k.md), [MiMo](S20_mimo9b_5060ti_32k.md).

### 6.9 NVIDIA Nemotron: compatibility repaired, competence still absent

Nemotron's first obstacle was the thinking-control interface. The shipped template ignored Ollama's `think=false`; the observed disabling mechanism required `/no_think` in a message, while P1 was frozen. The researcher authorized a derived GGUF copy that changed only the embedded template's default `enable_thinking=true` to `false`. The verification checked that all 341 tensors and other metadata were identical.

Importing the derived copy introduced another issue: `ollama create` selected a built-in `nemotron-3-nano` renderer rather than using the intended embedded template. Two unsuccessful import attempts were retained. The final manifest mirrored the source tag structure so the intended renderer path was used. Guards verified no thinking, actual 32K, f16 KV, and 57/57 GPU layers before the official episodes. This was a specific authorized derivation, not an unmodified-model result.

The resulting twenty-question block completed with twenty `SUCCESS` outputs and sixty well-formed native calls, but zero competent questions. Fourteen final outputs were `no_answer`; six contained 61 answer items, including eight benchmark GOLD entities and 53 OFF_QUESTION items. All were PATH_INVALID, so none was SUPPORTED.

The traces show why. Twenty tool calls failed, including invented relation names; thirteen episodes stopped immediately after a failed call and returned `no_answer`. Seven expanded only the starting entity. For example, retrieving a disease's own phenotypes did not answer a question requiring drug-mediated side effects. Median tool use was only three calls, the largest prompt was 3019 of 32768, and no episode exhausted the budget.

The failure therefore occurred with ample context and low latency. The template work solved a compatibility prerequisite, but it did not produce the required exploration, error recovery, or support-path selection. Nemotron failed competence and did not replace Qwen. The result does not establish how the untouched model would behave under a different thinking policy or harness. [Source: Nemotron report](S20_nemotron9b_5060ti_32k.md).

### 6.10 Ornith: a real passing alternative with a different failure distribution

Ornith used its unmodified `ornith-1.5:9b` package. The synthetic probe demonstrated native tools and honored `think=false`; all 33 layers were on GPU. Its full screening block produced eighteen successes, eleven competent queries, and 315/315 well-formed returned attempted calls. Median episode time was 47.57 seconds. One episode ended `ERROR/RUNTIME` and one `PARSE_FAIL`; zero OOM allowed the separate OOM criterion to pass.

Its strengths differed from selected Qwen. Against Qwen's 8K/f32 evidence, BH2_03619 improved from zero to 175 supported items and BH2_03953 from zero to 143; BH2_03850 gained one item. Across the block Ornith returned 572 supported items versus Qwen's 301. Those are meaningful gains in answer coverage on particular questions.

However, competence fell from fourteen questions to eleven. Ornith lost supported answers on BH2_04007, BH2_05686, BH2_03762, and BH2_03856; BH2_03881 became a parse failure. Seven successful episodes returned only the starting entity, with zero-hop evaluated paths, OFF_QUESTION/PATH_INVALID, and WRONG_HOP_COUNT. Five of those seven had clean hop-1 exploration; only one exhausted the budget. The pattern cannot be explained simply by never using tools or always running out of calls.

Wrong items also occurred inside competent episodes. BH2_03750 contained 157 submitted answers: 44 supported and 113 OFF_QUESTION/PATH_INVALID through the wrong first-hop relation. A single supported answer is enough for query-level competence, so this large error cluster did not remove that query's competence flag. Ornith had 124 OFF_QUESTION items in total.

The two technical failures are particularly informative:

**BH2_03879 — context exhaustion during tool-call generation.** Backend tasks showed 31291 prompt plus 1477 generated tokens, then a following request with 32755 prompt tokens and only thirteen generated tokens. The latter returned HTTP 500 for incomplete `inspect_entity` argument JSON. The failure was strongly linked to exhausted 32K headroom, rather than an 8192 output-cap hit, timeout, or OOM. The later offline investigation corrected the earlier report's attribution of the failed request to the preceding 31291-token prompt.

**BH2_03881 — output cap followed by unsuccessful finalization.** A response used 8192 completion tokens from a 24551-token prompt. The retry then had 32723 prompt tokens and generated only 32 tokens. The first output-cap hit and subsequent context pressure are demonstrated. The retry's backend record had `truncated=0`, so a second forced context cutoff is not proved. Without the raw reply, the exact schema or syntax error remains unresolved.

The offline investigation found that raw episode files for this Ornith block were absent locally, and the expected shared archive path was unavailable. Metrics, console, and backend logs support the recorded status and boundary analysis, but cannot supply the exact malformed argument fragment or complete per-turn conversation. That limitation is retained here.

Ornith therefore passed D3 and remained a plausible candidate for researcher review, but the evidence did not make it an automatic upgrade: it covered fewer questions competently, had many wrong-hop/wrong-relation outputs, and three episodes already exceeded the S22 headroom-review threshold. Treating it as Qwen lineage preserves the panel's four-family count if it replaces Qwen; it does not add a fifth family or remove the headroom issue. No replacement freeze is recorded. [Sources: Ornith screening](S20_ornith15_5060ti_32k.md), [offline failure investigation](S20_ornith15_failure_investigation.md).

### 6.11 MiMo: Qwen-based weights did not preserve Qwen's task behavior

MiMo was tested as `hf.co/bartowski/MiMo-V2.6-Distill-Qwen-9B-GGUF:Q4_K_M`. Its synthetic addition probe emitted a native tool call, thinking was disabled, and all 33 layers were on GPU. The package was used unmodified.

In the biomedical block, however, it attempted no tool calls on any question. Eighteen episode finals were `no_answer`, and two answered with the starting entity itself. BH2_03750 first generated invented very large IDs until the 8192-token output cap, after which the single JSON re-prompt returned `no_answer`. Thus the final no-answer tally should not be interpreted as eighteen uniformly clean immediate abstentions: this episode had a long failed first finalization.

All twenty final outputs eventually parsed, giving `SUCCESS=20/20`, but call validity was undefined and competence was zero. The 1.97-second median mostly reflected short abstention rather than efficient graph reasoning. Its Qwen-derived base and successful synthetic tool probe did not guarantee that the trained model would choose to use the tools under the frozen biomedical instructions.

The official MiMo card describes a broader agentic training target and demonstrates thinking-enabled serving. That context can motivate hypotheses about task or interaction mismatch, but the project did not run a controlled thinking-enabled comparison or another official harness. The measured explanation is narrower: under this non-thinking P1/T1 condition, MiMo abstained or selected the source without building support traces. It failed D3 and did not replace Qwen. [Sources: MiMo screening](S20_mimo9b_5060ti_32k.md), [official identity/training card](https://huggingface.co/XiaomiMiMo/MiMo-V2.6-Distill-Qwen-9B).

### 6.12 What the replacement search says about Qwen's selection

The saved configuration shows that Qwen remained selected. The measured case for retaining it is that its passing 8K/f32 block supplied supported answers on more questions than Ornith, while Nemotron and MiMo supplied none. Its useful behavior had also appeared in earlier complete blocks, even though the exact outcomes changed with runtime conditions. This is a retrospective interpretation of the comparative evidence, not a new selection decision. The replacement search did not find a recorded option that simultaneously demonstrated a stronger query-competence result and eliminated headroom concerns under the tested configuration.

That is a conditional experimental conclusion. Qwen's continued selection does not resolve its eight S22 headroom violations or prove it is the best possible model. Ornith's D3 pass remains valid evidence, and a future researcher decision could change the panel. At this cutoff, the records support “Qwen remains frozen, with replacement and capacity review unresolved,” rather than “Qwen was permanently validated” or “Ornith already replaced Qwen.”

## 7. Engineering maneuvers and what they established

The journey repeatedly succeeded by identifying the layer where a failure occurred and preserving the distinction between a software repair, an experimental setting change, and a model limitation.

| Maneuver | Problem addressed | Evidence of improvement | Limit retained |
|---|---|---|---|
| Canonical graph indexing and construction-aware references | Raw benchmark fields did not directly define the right graph targets. | BRIDGE/UNION validation and the 7176-query eligible population. | Excluded types and incomplete benchmark agreement remain documented. |
| Neutral T1 tools with sorted pagination | Need reproducible graph discovery without solution hints. | CLI/tool equality checks and replayable native traces. | Valid schema does not imply valid relation or route. |
| Correct JSON tool serialization | Early Qwen template rendered malformed tool definitions. | Render-only schema checks; successful diagnostic traversal and finalization. | Thinking-only weights still emitted reasoning. |
| Strict parsing plus one fixed re-prompt | Models mixed prose, tools, and final objects. | Recovered valid finals in many runs without suffix extraction. | Some models still failed or returned no_answer. |
| Platform-specific atomic publication | Windows sandbox denied the original hard-link publication. | Same-directory flushed rename on Windows; collision and concurrent-writer checks. | Persistence remains write-once; inference errors are not silently retried. |
| Separate context reassessments | Boundary-limited histories left incomplete answers. | Gemma qualified at 16K; Gemma/Ministral recovered particular answers at 32K. | Qwen regressed in larger-context conditions; semantic errors remained. |
| Request-timeout investigation | Buffered generation exceeded the read deadline before episode expiry. | Reconstructed Ministral request exceeded 120 seconds; separate longer-wait episode completed. | Diagnostic outcomes do not replace official errors. |
| Cache/residency measurements | Larger context increased memory pressure and CPU offload. | KV allocations, layer counts, and synthetic throughput comparisons. | Quantization changed trajectories; sampled memory is not a peak bound. |
| New-host isolated launchers | Needed larger-memory execution while keeping identities explicit. | Full layer placement, actual context/cache guards, offline report reproduction. | Host and runtime changed together, preventing GPU-only attribution. |
| Runtime version and digest guards | Moving tags or automatic app updates could change the experiment. | Qwen 0.40.13 drift stopped before resumed inference; pinned 0.40.12 recovered. | Resume applies only to unsaved episodes, with interruption disclosed. |
| Keep-awake and power-event inspection | A sleeping host contaminated one shared-resource episode. | Sleep mechanism identified; later Qwen 8K block held awake. | The saved TIMEOUT remains in its original denominator. |
| Derived Nemotron template and manifest checks | Shipped thinking control and automatic renderer selection did not match the authorized mode. | No-thinking native-tool operation with tensor identity checks. | Task competence remained zero. |
| Offline evaluation, hashes, and paired inspection | Needed confidence that changes did not rewrite earlier outcomes. | Reports reproduce saved metrics; prior identities checked across stages. | Missing local raw records limit fresh replay of later runs. |

### 7.1 Persistence and resume were part of experimental validity

The saver writes a fully serialized, flushed record to a temporary file, then publishes without overwriting an existing result. Windows uses its non-overwriting rename behavior; other platforms retain hard-link publication. Tests covered real concurrent writers and collision refusal. This resolved the sandbox persistence issue without weakening the promise that a completed failed episode remains completed.

Long runs could resume after interruption by skipping all final statuses, not merely successful ones. Partial tables left final D3 verdicts undefined until the complete block existed. New experiments received new run IDs; selected diagnostic recoveries were not stitched into old successful records. These practices made the eventual “journey” auditable instead of leaving only the final good run. [Sources: persistence repair](S12_sandbox_fix_20261016.md), [S20 launcher](S20_implementation.md).

### 7.2 Verification tested the scientific boundary as well as ordinary code

The repository used synthetic fixtures, real graph spot checks, source hashes, full-suite runs, and mutation checks. Test totals grew with implementation: 352 at the early repaired-template checkpoint, 358 after the persistence repair, 556 at S19 acceptance, and 598 at initial S20 implementation. Later new-host and replacement reports record additional driver tests; Nemotron's report records a full suite of 634 passed with two missing-raw-BioHopR skips.

Those are historical stage results, not tests rerun for this documentation task. Missing-raw-data skips on the new host were disclosed while frozen screening inputs and evaluator references were checked separately. Mutation tests deliberately inverted pagination, support priority, context, or residency conditions to check that verification would catch meaningful faults. Agent/evaluator import and I/O separation was also exercised.

Offline reporting mattered especially after long inference blocks: summaries could be regenerated with model access forbidden, showing that reported outcomes came from saved records rather than a fresh hidden attempt. Where raw files are now absent in this checkout, this report cites the saved summary and historical verification rather than claiming a new complete replay.

### 7.3 Failures that engineering did not solve

Several patterns survived capacity and operational improvements:

- **Relation discovery:** repeated nonexistent labels consumed calls even with ample context.
- **Wrong target type:** agents returned drug bridges or the starting entity instead of requested second-hop phenotypes.
- **Shortcut paths:** a direct graph neighbor could match a benchmark name while failing the required route.
- **Early stopping:** many supported lists omitted later pages or alternative bridges.
- **Finalization:** a useful traversal could still end in prose, incomplete JSON, or a tool call when final JSON was required.
- **Task-dependent abstention:** synthetic native tools did not prevent Granite 3.3, OLMo, or MiMo from failing to engage productively on the biomedical task.

These observations explain why the project needed both transport-level measures and path-aware scientific evaluation. More memory could prevent a cutoff; it could not by itself guarantee correct navigation or answer selection.

## 8. The frozen panel, S22 results, and the current checkpoint

### 8.1 S21 froze the exact accepted evidence packages

On 30 October 2026, the researcher selected mixed runtime evidence and explicitly replaced the earlier formula-based sizing rules with per-agent settings. The old rules would have suggested a larger common context and other derived limits; they were not silently ignored. The decision was recorded, configurations written, and the protocol subsequently versioned as 1.3.5.

| Frozen order | Agent / family | D3 evidence | Context | Output cap | KV | Request cap |
|---:|---|---|---:|---:|---|---:|
| 1 | Ministral 3 / Mistral | Shared 32K block, 19 SUCCESS / 18 competent | 32768 | 8192 | f16 | 240 s |
| 2 | Gemma 4 / Gemma | Shared 32K block, 20 / 16 | 32768 | 8192 | f16 | 240 s |
| 3 | Granite 4.1 / Granite | Shared 32K block, 20 / 16 | 32768 | 8192 | f16 | 240 s |
| 4 | Qwen3.5 / Qwen | 8K/f32 block, 18 / 14 | 8192 | 4096 | f32 | 120 s |

All four retain temperature zero, seed 42, thinking disabled, budget thirty, page size fifty, a 600-second episode cap, and one sequence. Ordering follows competence, then median wall time. The selected evidence for Ministral includes the disclosed host-sleep timeout; the cleaner preceding 20/20 block was not silently substituted. [Sources: frozen models](../configs/models.yaml), [frozen runtime](../configs/pilot.yaml), [protocol §9.1 and decision history](frozen_pilot_protocol.md).

### 8.2 S22 checked a different requirement from D3

The first S22 attempt, `smoke_single`, was stopped during the tenth episode with nine final records preserved. A new eighty-episode run, `smoke_single_v135`, then tested the four agents under the revised protocol. The incomplete first attempt was not resumed or merged into the new one.

| Agent | Final statuses | Largest prompt / context | Episodes above 90% context | S22 implication |
|---|---|---:|---:|---|
| Ministral 3 | 20 SUCCESS | 21298 / 32768 | 0 | No context-trigger event in this run. |
| Gemma 4 | 20 SUCCESS | 29500 / 32768 | 1 | Return to S21 review. |
| Granite 4.1 | 20 SUCCESS | 18192 / 32768 | 0 | No context-trigger event in this run. |
| Qwen3.5 | 18 SUCCESS, 2 PARSE_FAIL | 8189 / 8192 | 8 | Return to S21 review. |

There were no OOM or ERROR episodes, and no answer was both OFF_QUESTION and SUPPORTED. Nevertheless, protocol §9.1 pauses progression when a prompt exceeds 90% of an agent's context. D3 qualification does not waive this check. Both Gemma and Qwen therefore require researcher review; the replacement investigations addressed Qwen without resolving Gemma's separate trigger.

S22 also retained substantive answer failures: Gemma had eighty PATH_INVALID items, Granite 74, and Qwen three. Ministral's 720 scored items were supported in that run, but early stopping was still observed. Parsed completion and absence of OOM did not make the panel universally correct. [Source: S22 summary](../results/diagnostics/smoke_single_summary.md).

### 8.3 State at the evidence cutoff

The frozen model list still contains Ministral 3, Gemma 4, Granite 4.1, and Qwen3.5. Nemotron and MiMo failed their authorized replacement blocks. Ornith passed D3, but the saved decision history does not record its installation into the frozen panel. The 1 November Ornith investigation adds a more precise failure explanation and the Qwen-lineage clarification, without changing the verdict or selection.

The project has therefore completed substantial screening and engineering work, but this documentation must not describe S22 headroom review as resolved or claim later pilot, co-failure significance, or intervention outcomes. The current checkpoint is a selected panel with specific capacity concerns still under review.

## 9. What the journey establishes

The project progressed from an uncertain benchmark interpretation and a thinking-heavy integration model to a reproducible four-agent panel with measured strengths and known limitations. Its main achievement was making failures distinguishable and traceable.

For **Gemma**, increased context converted useful but truncated work into enough valid finals to pass, and later 32K capacity recovered two additional competent questions. For **Ministral**, useful graph reasoning was initially limited by buffered-request deadlines and memory-related execution conditions; the new host removed observed timeouts, and 32K provided room for two previously truncated finalizations. For **Granite 4.1**, the system achieved reliable completion, but extra context did not eliminate wrong-target or shortcut answers. For **Qwen**, repeated tests identified a passing 8K/f32 package while exposing that larger windows and larger output caps did not consistently improve finalization.

The unsuccessful candidates were equally informative. Llama demonstrated repeated schema mistakes despite parsed final output. Granite 3.3 demonstrated textual tool imitation without executed grounding. OLMo demonstrated that valid native envelopes and some useful lookups can coexist with zero competent answers. Granite 4.2 demonstrated that recency does not guarantee better task fit. Command R7B and MiMo demonstrated that short, valid abstention is not success at the research task. Nemotron demonstrated that carefully solving a template/mode problem does not create missing graph competence. Ornith demonstrated that more supported items can coexist with lower coverage across questions, substantial wrong-answer clusters, and renewed context pressure.

The reasons for success are strongest where the evidence follows a specific mechanism: a corrected schema serialization, a longer context allowing a previously cut-off JSON retry to finish, or a generation duration exceeding a measured request deadline. Broader claims about architecture, training, GPU superiority, or KV precision remain hypotheses unless the recorded comparisons isolate them. The report preserves those limits alongside the successful stages.

## 10. Evidence inventory, qualifications, and verification

### 10.1 Coverage of the model record

The companion [complete run inventory](final_model_run_inventory.csv) contains **28 complete twenty-question S20/scoped reassessment blocks, representing 560 documented episode outcomes across twelve S20 candidates**. It also preserves installed parameter metadata, weight quantization, and the family field as originally recorded. Tags are not literal parameter counts: for example, Gemma's E4B package reported 7.5B, Command's 7B tag reported 8.0B, and Nemotron's 9B package reported 8.89B. These metadata values are distinct from active parameters, file size, or loaded VRAM.

The full-block accounting is:

| Block group | Complete blocks | Documented outcomes |
|---|---:|---:|
| Original 3060 Ti 8K screening | 9 | 180 |
| Complete 3060 Ti 16K reassessments | 3 | 60 |
| Fresh 5060 Ti 16K blocks | 4 | 80 |
| Separate 5060 Ti 32K blocks | 4 | 80 |
| Shared 32K resource blocks | 4 | 80 |
| Qwen 5060 Ti 8K/f32 block | 1 | 20 |
| Nemotron, Ornith, and MiMo replacement blocks | 3 | 60 |
| **Total** | **28** | **560** |

This is an accounting of documented runs, not a count of unique questions or independent confirmations. It excludes the incomplete fifteen-record Granite block, the selected four-query Gemma diagnostic, early Qwen3 4B integration episodes, synthetic probes, the isolated Ministral replay/full-query diagnostic, the selected cache tests, eighty exploratory cache-comparison outcomes, and S22's separate verification episodes. Those activities are discussed without adding them to the D3 totals.

### 10.2 Source authority and chronology

The current protocol, frozen model/runtime configurations, and later dated decision entries determine the present selection state. Earlier reports remain evidence of what was known at their own checkpoint. In particular, the shared-resource report's “S21 unselected” statement precedes the later explicit S21 freeze; it must not be presented as the final state. Similarly, old new-host setup proposals are superseded by actual recorded host/runtime identities.

Measured quantities in the tables come from the original screening CSV and per-run `screening_row` summaries. The CSV includes each source path, exact tag/digest, conditions, verdict, and count of raw episode files present locally. Detailed behavioral claims cite the relevant stage reports, paired inspections, metrics, and logs. Model-card links establish lineage only; their vendor benchmark scores are not used as evidence of CoFail-KG performance.

### 10.3 Evidence availability and limits

At documentation time, **400 of the 560 full-block raw episode records are present locally**. The missing 160 correspond to the shared-resource blocks, Qwen's 8K/f32 block, and the three replacement blocks. Their saved summaries, metrics, manifests, and diagnostic evidence remain available. The missing raw records limit fresh end-to-end replays and exact conversational reconstruction; a historical hash list is not a substitute for the missing bytes.

The Ornith investigation explicitly records this limitation and the unavailable expected archive path. Its backend-token analysis is supported, but the exact malformed tool argument and exact parser failure cannot be recovered from a summary alone. This report does not invent them. Historical backup reports also retain unrelated archive errors; they are not evidence of a universally complete current backup.

Other qualifications remain material:

- Later reassessments reused inspected screening questions; they are outcome-informed diagnostics/selection evidence, not an unseen holdout evaluation.
- Cross-host comparisons change multiple variables together. Same-host context comparisons are more focused but usually consist of one paired block, with scheduling and hidden cache behavior not fully controlled.
- Temperature zero and a fixed seed did not make all trajectories identical across runtime, cache, or host conditions.
- Memory and placement samples do not prove instantaneous peaks or complete semantic retention of history.
- Presence-based competence can reward a one-answer subset of a very large expected list; item totals can be dominated by a few large questions.
- A GOLD item can be unsupported or path-invalid, while an ALT_VALID item can be question-valid and supported outside the stored benchmark subset.
- The exploratory KV report's strong causal wording and the OLMo report's malformed-call explanation are treated with the narrower qualifications stated in this report. No historical score was changed.

### 10.4 Verification performed for this documentation

The inventory was assembled from nine original screening-table rows and nineteen complete per-run summary rows, with duplicate run/agent pairs rejected. All 28 were confirmed to contain twenty outcomes. Their five mechanical D3 predicates were recalculated from the saved aggregate quantities and matched every recorded verdict. All 560 saved per-query metric files were also checked: their status totals and presence of question-valid SUPPORTED answers reproduced the recorded success and competence counts. For the 400 locally available raw episodes, final statuses and twenty-query uniqueness were independently counted. This verifies agreement among retained records; it does not regenerate missing conversations or rerun their evaluator pipelines.

The report's original, 16K, 32K, shared-resource, Qwen-history, and replacement tables were checked against their source quantities; the frozen panel/runtime and S22 trigger counts were checked against the current configurations and S22 summary. The OLMo malformed-call clarification was checked directly against its locally available raw messages and frozen T1 schema.

No model inference was performed for this writing task. Production code, scientific rules, frozen configurations, datasets, and existing results were not edited. Verification here is document/source consistency checking, not a fresh replication of the experiments. The historical test counts above are attributed to their stage reports. The new files are this report and its companion run inventory; existing in-progress Ornith investigation edits are preserved.

### 10.5 Suggested source trail for a reader

For the broad history, begin with [decision log](decision_log.md), [protocol](frozen_pilot_protocol.md), and [original screening table](../results/diagnostics/screening/screening_table.csv). For the capacity story, read [context audit](S20_context_window_audit.md), [complete old-host 16K reassessment](S20_full_16k_reassessment.md), and [shared 32K resources](S20_shared_resources_32k.md). For selection, read [Qwen 8K/f32](S20_qwen35_5060ti_8k_f32.md), [frozen runtime](../configs/pilot.yaml), and [S22 summary](../results/diagnostics/smoke_single_summary.md). For the replacement search, read [Nemotron](S20_nemotron9b_5060ti_32k.md), [Ornith](S20_ornith15_5060ti_32k.md), [Ornith failure investigation](S20_ornith15_failure_investigation.md), and [MiMo](S20_mimo9b_5060ti_32k.md).
