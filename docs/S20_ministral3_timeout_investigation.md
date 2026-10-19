# Ministral S20 HTTP timeout investigation (2026-10-19)

**A long buffered generation exceeded the 120-second HTTP read deadline.**
The isolated replay of the saved request returned after **153.47 seconds**,
including **143.57 seconds generating 2,576 tokens** (17.94 tokens/second).
Generation time alone exceeded the original deadline. This reproduces the
failure mechanism; the original request was cancelled before its response could
be saved, so its eventual text and completion duration remain unknown.

## 1. Files created or changed

- This report; a follow-up note in docs/S20_ministral3_screening.md and docs/decision_log.md.
- results/diagnostics/s20/ministral3/timeout-investigation/: the reconstructed
  request, one replay helper, raw response, timing summary, response inspection,
  placement/process evidence, GPU samples, hardware-event window and findings.
- Official episodes, configurations, metrics, screening table and source are unchanged.

## 2. Evidence and verification

The original failure is BH2_04425 / Ministral3-8B / attempt 1. Six native KG calls
completed before the seventh /api/chat request. Last tool call: get_neighbors
for entity 15180, drug_effect, effect/phenotype, page 1; it returned 28 items in
0.0110465 seconds. Its UTC timestamp is 2026-10-19T07:10:33.915069+00:00
(13:10:33 Dhaka). The ERROR was saved at 07:12:33.959775 UTC (13:12:33 Dhaka).
The interval after that tool finished is approximately 120.034 seconds.
Six earlier successful model responses took 16.897459 seconds combined.
Episode wall time was 139.070961 seconds, well below the 600-second episode cap.

The trace records `Read timed out. (read timeout=120)`, with no HTTP status or
response body. Code locations:

- configs/ollama.yaml:3 fixes request_timeout_seconds=120.
- src/cofail_kg/agents/run_agent.py:169 limits each request to min(120, remaining episode time).
- src/cofail_kg/agents/ollama_client.py:112 sends stream=false.
- src/cofail_kg/agents/ollama_client.py:60 catches requests.Timeout and labels it CONNECTION.

CONNECTION is a broad project transport category. This event specifically means
that the client waited too long for response data; it does not establish a
failed TCP connection, internet outage, KG failure or exhausted episode budget.
Ollama's non-streaming response is returned as one JSON object; Requests' read
timeout limits the gap while waiting for response bytes. Primary documentation:
[Ollama API](https://github.com/ollama/ollama/blob/main/docs/api.md#generate-a-chat-completion),
[Requests timeouts](https://requests.readthedocs.io/en/stable/user/advanced/#timeouts).

### One isolated reproduction

Reconstructed the exact request payload from the saved agent messages, pinned
tool schemas and original model/options. No evaluator/reference data was added.
Model tag/digest, temperature=0, seed=42, num_ctx=8192, num_predict=4096,
think=false and stream=false were unchanged. Only the diagnostic client's read
wait was raised to 300 seconds. No episode runner, subsequent turn, KG execution,
re-prompt or scientific evaluation was run for this replay.

| Replay observation | Value |
|---|---:|
| Total HTTP latency | 153.471033 s |
| Token generation | 143.567916 s |
| Output tokens | 2576 |
| Generation rate | 17.94 tokens/s |
| Prompt tokens | 4569 |
| Prompt processing | 2.608029 s |
| Model loading | 7.226668 s |
| Stop reason | stop |
| Content / native tool calls | 2624 characters / 0 calls |

The diagnostic started from an unloaded model (before-ps.json has no models).
Cold loading therefore adds about 7.23 seconds, but generation alone exceeds
120 seconds. During generation the loaded model retained the original exact
digest and size=6591967394, size_vram=5549137591, context=8192: the same 16%/84%
CPU/GPU allocation observed in S20. GPU samples showed activity. Partial CPU
offload may contribute to speed; no controlled full-GPU comparison was performed,
so its individual causal contribution is unmeasured.

The replay returned a verbose prose list of side effects and a statement that it
would now compile them. It is not the required final JSON, and the unchanged
parser rejected it with "Expecting value". Thus a larger read deadline permits
this model turn to return; it does not demonstrate that the whole episode would
be SUCCESS. No re-prompt or full-episode rerun was performed.

The same server process was created at 10:58:09 Dhaka and remained alive after
the original 13:12 timeout. No matching Display/nvlddmkm/WHEA/Kernel-Power warning
or error was found in the System log's 13:09-13:14 window. These observations
provide no evidence of a server restart or recorded GPU-reset/power event; they
cannot exclude every possible original transient. The active server was launched
from an interactive PowerShell process, and a retained server log for the original
request was not found. The older .tool-inspect server logs end on October 18.

Assertions verified the reconstructed payload, original identity/settings, same
loaded placement, all 84 official run-file hashes, 122 protected identities,
43 pinned source/input hashes and the unchanged complete screening-table row.
The existing suite was not rerun: no production code was changed. The replay's
raw response, timings and successful envelope are the runtime reproduction.

## 3. Small real example

The single diagnostic request completed with done_reason=stop after 153.47 s.
Its response begins:

> I have retrieved the side effects/phenotypes for both drugs indicated for scrub typhus:

This is stored model output, not an independently verified medical statement.
The full response is in response.json; the original official record remains
ERROR/CONNECTION and the final D3 row remains unchanged.

## 4. Assumptions and limits

The investigation request authorizes a separate diagnostic replay, not a change
to the completed experiment. Exact request equality does not imply identical
historical latency or generated text: model cache state, loading and machine
load can vary. The historical cause is strongly supported by reproduction of the
same request taking longer than the read limit, with generation alone exceeding
that limit; unavailable original server logs prevent reconstructing every detail.

## 5. Engineering implications

The 120-second request cap can terminate active generation before the frozen
600-second episode budget is exhausted. A future, explicitly declared runtime
revision could use a longer request deadline capped by the episode's remaining
time. It should be validated and applied consistently to affected candidates;
existing screening records must retain their original settings and outcomes.
No timeout, streaming, prompt, parser, model, data, threshold or source change was
made here. Changing the timeout alone would not guarantee schema-valid replies.
These are routine engineering findings, not a new scientific method.

## 6. Items for manual inspection

- replay-summary.json and response.json: generation duration versus the read limit.
- request.json: the saved seventh request, without reference/evaluator leakage.
- response-inspection.json: verbose non-JSON output and parser rejection.
- findings.json: integrity proof and distinction between reproduced mechanism
  and unknown historical completion text/duration.

## Subsequently authorized full-query diagnostic

After the single-request investigation above, the researcher separately requested one fresh full BH2_04425 episode outside official screening. It completed SUCCESS in 237.02 s with six well-formed native calls and 65 GOLD/SUPPORTED answers (precision 100%, recall 65/75=86.67%). Only the diagnostic request cap was 600 rather than 120 seconds, still bounded by the unchanged 600-second episode limit. The prose turn took 135.26 s; the normal single JSON re-prompt then took 74.90 s and parsed successfully. This corroborates the request-deadline mechanism without changing any official record or D3 result. The model omitted pagination after a has_more=true result, so benchmark recall remained incomplete. Full trace, config, metrics and integrity evidence: results/diagnostics/s20/ministral3/offbook-20261019T075024Z/README.md.
