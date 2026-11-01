# Ornith 1.5 9B: offline failure investigation — 2026-11-01

Run: `ornith15-5060ti-32k-20261031`. This investigation reads existing logs,
metrics and runner code; it performs no inference and changes no final outcome,
runtime setting, D3 verdict or panel selection.

## Family clarification

The researcher clarified on 2026-11-01 that Ornith 1.5 was trained on Qwen 3.5
weights. Treat its developer lineage as Qwen for this discussion and selection
review; it does not introduce a new family relative to Qwen35-9B. This is
researcher-supplied lineage information, consistent with the logged `qwen35`
architecture, rather than independent model-card verification. Historical run
manifests retain their original `UNVERIFIED-qwen35-architecture` value.

## Evidence and limits

Evidence directory: `results/diagnostics/s20/ornith15-5060ti-32k-20261031/`.
Primary sources are `run-console.txt`, `server-run-20261030T181109Z.stdout.log`,
`server-run-20261030T181109Z.stderr.log`, `runtime-samples.jsonl`, `summary.json`
and all twenty `metrics/*.json` files. Parser behavior was checked in
`src/cofail_kg/agents/run_agent.py`; server error classification was checked in
`src/cofail_kg/agents/ollama_client.py`.

Raw episode JSON files referenced by `final-run-hashes.json` are absent locally.
The configured shared Drive archive's expected `current/results/runs/screening-5060ti/ornith15-5060ti-32k-20261031/`
path also returned directory not found. Consequently the exact assistant text,
tool-argument fragment, parser exception and full per-turn tool sequence cannot
be independently replayed here. Backend requests are associated with episodes
through their sequential order, request durations, and completion checkpoints;
the backend task IDs themselves do not contain query IDs.

## BH2_03879: context exhaustion and invalid tool arguments

Status ERROR/RUNTIME; 29 charged tool calls. Console line 34 reports:
`llama-server returned invalid tool call arguments for "inspect_entity": unexpected end of JSON input`.
The request log records HTTP 500 at 00:21:12 Bangladesh time on October 31,
after 11.16 seconds (stdout line 144). Runtime checks immediately afterward
still pass; this was not loss of the whole Ollama server.

The last two backend tasks before that error show actual context exhaustion:

| Backend task | Full prompt tokens | Generated tokens | Release |
|---|---:|---:|---|
| 31155 | 31,291 | 1,477 | n_tokens=32767, truncated=1 |
| 32634 | 32,755 | 13 | n_tokens=32767, truncated=1 |

See stderr lines 2968–2983 and 3013–3128. The prompt and generated-token counts
reach the 32,768 configured context limit (the backend release index differs
by one). Task 31155 corresponds to the successful HTTP response at 00:21:01;
task 32634 corresponds to the subsequent failed response. Thus the earlier
report's 31,291 prompt figure does not describe the failed backend request's
full prompt; that next request had grown to 32,755.

Conclusion: strong evidence that lack of context headroom cut off generation
and left incomplete tool arguments, which the backend rejected. This is not
an 8,192-token output-cap failure, request timeout, tool-budget exhaustion or
OOM. The exact malformed argument fragment is unavailable without raw traces.
The server also explicitly logs that KV cache shifting is unsupported for this
context and disabled (stderr line 228); a context-shift flag on the command
line therefore does not establish automatic recovery.

## BH2_03881: output-cap exhaustion followed by unsuccessful finalization

Status PARSE_FAIL; 19 charged tool calls. Requests in this episode finish with:

| Backend task | Full prompt tokens | Generated tokens | Release |
|---|---:|---:|---|
| 36232 | 24,551 | 8,192 | n_tokens=32742, truncated=0 |
| 44426 | 32,723 | 32 | n_tokens=32754, truncated=0 |

See stderr lines 3399–3453 and 3483–3585. Corresponding HTTP requests complete
at 00:24:30 and 00:24:41, both with status 200. The first uses the entire output
allowance and leaves little context headroom for the existing single JSON
re-prompt. The next prompt occupies 99.86% of the context, leaving only 45
tokens of nominal space, and generates 32 tokens.

The runner's PARSE_FAIL branch means the first proposed final answer and the
one permitted re-prompt both failed `parse_final`. However, that parser checks
both JSON syntax and required schema. Without raw text, the precise error
(incomplete JSON, prose, missing fields, or another schema issue) is unknown.
In particular the second request has `truncated=0`: it must not be described
as a proven second hard context cutoff. Context pressure and the first output
cap are demonstrated; the exact reason the short re-prompt was invalid remains
unresolved. Neither request exceeded the 240-second deadline.

## Seven additional queries fail on answer selection

The remaining seven noncompetent episodes have SUCCESS status: their final
JSON parses, but their sole answer is the start entity with an empty evaluated
path, zero hops, OFF_QUESTION/PATH_INVALID and WRONG_HOP_COUNT.

| Query | Tool calls | Hop-1 status | Budget exhausted |
|---|---:|---|---|
| BH2_03760 | 14 | H1_MIXED | No |
| BH2_03762 | 30 | H1_CLEAN | Yes |
| BH2_03856 | 7 | H1_CLEAN | No |
| BH2_03991 | 20 | H1_MIXED | No |
| BH2_04003 | 26 | H1_CLEAN | No |
| BH2_04007 | 11 | H1_CLEAN | No |
| BH2_05686 | 7 | H1_CLEAN | No |

These are failures to select a supported answer satisfying the requested hops,
despite actual tool activity. The empty evaluated answer path is not evidence
that the model never explored. Five of these seven even have H1_CLEAN. Only one
hit the call budget, so budget exhaustion cannot explain the pattern as a whole.
Raw conversations are needed to distinguish navigation mistakes from forgetting
or discarding a previously discovered answer during finalization.

## Wrong answers also occur in competent episodes

BH2_03750 contains 157 submitted answers: 44 SUPPORTED and 113 OFF_QUESTION /
PATH_INVALID with WRONG_RELATION_HOP1. It passes query-level competence because
at least one valid answer exists, despite substantial wrong-relation output.
Those 113 items account for most of the run's 124 OFF_QUESTION items.

BH2_03434 adds one WRONG_HOP_COUNT/WRONG_TARGET_TYPE answer. BH2_04425 adds
three invalid answers (one WRONG_HOP_COUNT and two also WRONG_TARGET_TYPE),
while retaining 75 supported answers. These are reasoning/selection failures,
not JSON transport failures.

## Implications

The nine noncompetent queries comprise two execution/finalization failures and
seven wrong-hop answer failures. More capacity might help the two limit-affected
episodes, but the logs do not establish that it would fix the seven start-entity
answers or the wrong-relation output. Any capacity experiment should be separate,
documented, preserve these outcomes, and inspect full raw turns before changing
the selected runtime. Repeating these already inspected questions would be a
diagnostic, not independent confirmation.

Ornith remains D3 PASS: 18/20 SUCCESS, 11/20 competent, 315/315 well-formed
returned attempted calls, median 47.5706245 seconds, zero OOM. The HTTP 500's
malformed generated call was rejected inside the backend, before a normal
native tool call reached the runner; the 315/315 figure should not be read as
proof that every generation attempt formed valid tool arguments. Three episodes
already exceed the S22 context-review level. Using the researcher's Qwen lineage
clarification, replacing Qwen with Ornith would retain four panel families, but
would not resolve context headroom automatically.
