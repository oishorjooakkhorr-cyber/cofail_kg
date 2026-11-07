# S22 `smoke_single_s21r2`: investigation of the non-SUCCESS episodes

Run: `smoke_single_s21r2`, 80 episodes, commit `16dfa28`. Prepared 2026-11-07 by reading the saved episode
records in `results/runs/smoke_single_s21r2/` and the server logs in
`results/diagnostics/smoke_single_s21r2/<agent>/`. No code, config or result was changed.

Three episodes did not end in SUCCESS, and one SUCCESS episode crossed the 90% context line:

| Agent | Query | Status | What happened |
|---|---|---|---|
| Ministral3-14B | BH2_02033 | PARSE_FAIL | First reply wrote the tool call as plain text instead of a native tool call |
| Cogito-14B | BH2_03953 | ERROR / CONNECTION | One reply went on generating; the request was cut at 240 s |
| Cogito-14B | BH2_04425 | ERROR / CONNECTION | Same as BH2_03953 |
| Ministral3-14B | BH2_04003 | SUCCESS, 91.7% of `num_ctx` | 26 tool calls; the context grew to 30,048 tokens |

The summary file calls the Cogito episodes "CONNECTION" errors. They are **not** connection problems or
parse failures: they are request timeouts (see §2).

---

## 1. Ministral3-14B, BH2_02033: PARSE_FAIL

**Question:** "Name all diseases that are related to a gene/protein that is associated with drug
MYO-029." Starting entity 19601. The episode lasted 2.5 s and made **0 tool calls**.

What the record shows, turn by turn:

1. **Turn 1 (message 2).** The model's reply had no native `tool_calls`. Its text content was the tool
   call in Mistral's own text syntax:
   `inspect_entity[ARGS]{"entity_id": "19601"}`
   Ollama's parser (this agent runs with `--no-jinja --chat-template chatml`, as frozen) did not turn this
   into a tool call, so the harness treated it as the final answer. It isn't JSON, so the harness logged
   `PARSE_ERROR` ("Expecting value: line 1 column 1").
2. **Re-prompt (message 3).** The harness sent its single re-prompt ("Your last message was not valid JSON
   in the required format. Reply with only the JSON object.") and marked the next turn as the final turn
   ([run_agent.py:214-215](../../src/cofail_kg/agents/run_agent.py)).
3. **Turn 2 (message 4).** This time the model made a correct **native** tool call,
   `inspect_entity({"entity_id": "19601"})`, with empty text content. On the final turn the harness doesn't
   run tool calls: it moved this call to `ignored_tool_calls` and parsed the empty content, which failed
   again. Status became PARSE_FAIL.

**Cause:** in its first reply Ministral printed its tool call as text in its own syntax. After the
re-prompt it made the right tool call, but by then only a final JSON answer was accepted. The harness did
what it is written to do. Whether that is the intended reading of §9.5 is your call.

**Note on the `TEXT_TOOL_CALL` event:** the record has no `TEXT_TOOL_CALL` event. This is correct:
§9.5 defines a text tool call as a tool name "immediately followed by `(`", or a JSON object whose
`"name"`/`"function"` is a tool name. `inspect_entity[ARGS]{...}` matches neither. (Corrected
2026-11-07: an earlier version of this report called this a detector miss.)

**How often:** 1 of 20 Ministral episodes. Ministral's screening didn't show this. I haven't searched the
other Ministral episodes for text-form calls that were followed by a working native call.

---

## 2. Cogito-14B, BH2_03953 and BH2_04425: ERROR / CONNECTION (really request timeouts)

Both episodes go the same way:

| | BH2_03953 | BH2_04425 |
|---|---|---|
| Tool calls before the failure | 8 | 6 |
| Normal turns: latency | 1.0–3.4 s | 1.1–2.7 s |
| Normal turns: completion tokens | 25–96 | 25–81 |
| Last saved message | tool result (side-effect phenotypes) | tool result (side-effect phenotypes) |
| Failure | `Read timed out (read timeout=240)` | same |
| Tokens generated when cut (server log) | **5,979** | **6,436** |
| Generation speed (server log) | 25.3 tok/s | 27.3 tok/s |
| Episode wall time | 249 s | 248 s |

**What happened.** After a fairly large tool result, Cogito's next reply didn't stop. The server log
(`server-run-*.stderr.log`, tasks 12514 and 23857) shows the generation running at about 25–27 tokens per
second. When the client's 240 s read timeout ran out, the reply was at about 6,000 tokens, still short of
the `num_predict` cap of 8,192, with no stop token yet. The client gave up, the server cancelled the task
(`srv stop: cancel task`), and the harness recorded an `OllamaError`. Ollama has no separate cause code
for a read timeout, so it was classed as `CONNECTION`.

Normal Cogito replies are short: over 130 replies in this run the median latency was 1.7 s, and the
longest reply that finished took 105 s (1,954 tokens). Replies of about 6,000 tokens are far outside that
range. That pattern suggests the model got stuck in a loop or kept listing items, but **I can't confirm
it**: Ollama returns the text only when the reply finishes, so the text of the cut replies was never
received and isn't in any file. The server log records token counts, not text.

### Would a 300 s timeout have avoided these two failures?

**Almost certainly not.** Two separate limits apply, and both get in the way:

1. **Request timeout (240 s per model reply, `request_timeout_seconds` in `configs/pilot.yaml`).** At
   about 25 tok/s, reaching the 8,192-token `num_predict` cap takes about 300–330 s. At 300 s a reply
   would be at about 7,500–8,000 tokens and probably still running. Even if it finished, it would most
   likely stop at the token cap, which means a cut-off answer. That leads to PARSE_FAIL, not SUCCESS.
2. **Episode timeout (`timeout_seconds: 600` in `configs/pilot.yaml`, not 300).** Both episodes had used
   only about 8–10 s before the long reply, so 600 s isn't the limit here. But if the request timeout were
   raised, a reply of 300–330 s would fit inside 600 s. The episode would then end as TIMEOUT or
   PARSE_FAIL, depending on whether the reply stopped at the cap.

So raising the request timeout would most likely turn these 2 ERRORs into 2 PARSE_FAILs (or TIMEOUTs).
They wouldn't become successes, because the problem is a reply that doesn't stop, not a slow server.
Note also: the episode cap in `configs/pilot.yaml` is **600 s**, not 300 s.

Both timeouts are frozen runtime settings, and changing either is a scientific/protocol decision under
§0.3. I haven't changed anything. The same two-timeout pattern appeared at screening.

---

## 3. Ministral3-14B, BH2_04003: SUCCESS, but 91.7% of `num_ctx`

**Question:** "Name all effect/phenotypes which are side effects of drug that can treat disease fetal
erythroblastosis." Starting entity 83780.

- 26 tool calls (16 `get_neighbors`, 10 `inspect_entity`) over 28 model turns.
- Prompt size in the last turns: 23,057 → 23,354 → 25,250 → 27,033 → 27,287 → **30,048** tokens.
- Tool results add up to about 75,700 characters. Most of the larger ones are 50-item neighbour pages of
  about 5,400 characters each. The whole conversation is re-sent every turn, so the prompt keeps growing.
- It ended with a valid JSON answer listing side-effect phenotypes.

**Same query, other agents:**

| Agent | Status | Peak prompt | Tool calls |
|---|---|---:|---:|
| Gemma4-12B | SUCCESS | 5,032 | 5 |
| Granite41-8B | SUCCESS | 18,192 | 20 |
| Cogito-14B | SUCCESS | 20,914 | 20 |
| Ministral3-14B | SUCCESS | 30,048 | 26 |

**Cause:** the question asks for every side effect of every drug that treats the disease, so it fans out
widely. Ministral explored the most pages, and every page stays in the context. The 30,048 peak is
**identical** to Ministral's screening peak: at temperature 0 with seed 42, the run repeated the same path
exactly. This episode crosses the runbook's 90% line, so §9.1 re-selection applies. That decision is yours.

---

## 4. Record-keeping issues found along the way (no effect on the results above)

1. **`protocol_version` says 1.3.5 in all 80 records.** The protocol is now v1.3.6 (re-freeze commit
   `fcf1c8a`), but `PROTOCOL_VERSION = "1.3.5"` in
   [trace.py:48](../../src/cofail_kg/agents/trace.py) wasn't updated. The protocol file's own hash is
   recorded correctly in each episode's `source_sha256`, so the real version can be recovered. The field
   itself is wrong, though.
2. **`git_commit` is `16dfa28…-dirty` in all 80 records.** The checkout was "dirty" only because of the
   untracked `results/diagnostics/ministral_speed/` folder that was there before the run. No tracked
   source file was changed: the driver checks source hashes before each episode.
3. **The text of the cut Cogito replies wasn't kept** (see §2). Only the server's token counts survive.

---

## 5. Decisions for you

1. Ministral3-14B BH2_04003 crosses 90% of `num_ctx`: apply §9.1 re-selection or not.
2. Ministral3-14B BH2_02033: is PARSE_FAIL the intended §9.5 outcome when the model makes a valid native
   tool call after the re-prompt?
3. Cogito-14B: keep the frozen 240 s request timeout. Changing it is unlikely to turn these into successes
   (§2).
4. Whether to fix `PROTOCOL_VERSION` (and how to mark these 80 records). This is an engineering fix;
   I'll make it only if you ask. (The text-call detector already follows §9.5; see §1.)
