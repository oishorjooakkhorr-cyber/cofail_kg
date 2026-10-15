# S13 — Ollama client

Completed 2026-10-15. Implements the S13 runbook prompt and protocol §9.1,
§9.5 and §19. The real check uses only synthetic greeting/arithmetic messages.
No biomedical episode, Gate D3 model selection, or S14 work occurred.
Protocol, decision rules, frozen hashes and final-model configuration are unchanged.

## 1. Files created or changed

- `src/cofail_kg/agents/ollama_client.py`: thin `OllamaClient`, explicit generation
  options, raw parsed JSON/message/native calls, token counts, elapsed seconds,
  installed-model identity, error causes and bounded connection retries.
- `configs/ollama.yaml`: local API URL and 120-second request timeout.
- `scripts/13_test_ollama.py`: one plain call and one dummy `add(a,b)` call;
  prints complete JSON evidence, optionally saved to a new file with `--output`.
- `tests/test_ollama_client.py`: 39 mocked-HTTP cases.
- `tests/test_ollama_smoke_script.py`: six diagnostic-script cases.
- `results/diagnostics/s13_ollama.json`: real requests, raw responses, identities,
  counts, timings and UTC timestamps.
- `docs/S13_implementation.md`, `docs/progress.md`, `docs/decision_log.md`:
  stage report and completion record.

No dependency was added: `requests` and PyYAML were already installed and declared.
There were no existing client callers to migrate. The diagnostic is its first caller;
the S14 runner will consume this interface when requested.

## 2. Tests run and results

Tests were written first: client tests initially failed on the missing module;
script tests initially failed on the missing script. After implementation:

```powershell
.\.venv\Scripts\python.exe -m pytest tests/test_ollama_client.py tests/test_ollama_smoke_script.py -q --basetemp=.pytest_cache/s13-focused-20261015a
# 45 passed
.\.venv\Scripts\python.exe -m pytest -q --basetemp=.pytest_cache/s13-full-unsandboxed-20261015a
# 294 passed (249 existing + 45 S13)
```

The final full run was outside the execution sandbox. Inside it, 290 passed and
four existing S12 tests failed because Windows hard-link creation was denied.
An earlier focused run also encountered sandbox temp-directory permissions;
using an explicit workspace test directory resolved that. No test was weakened,
skipped or removed, and no S12 implementation was changed.

Coverage includes exact outgoing payload/options and configured timeout; raw
response/message preservation; native versus textual tool calls; missing options;
invalid timeout values; all four ERROR causes; exactly two logged connection
retries and successful recovery; no retries for timeout, server errors, malformed
JSON/envelopes or reply content; absent/invalid token counts; exact model matching;
missing identity metadata; diagnostic success/failure; unsupported tools;
identity changes; partial diagnostic evidence on API failure; overwrite refusal.

Code review covered the client, its diagnostic caller, config and tests. There
are no evaluation imports or biomedical-data reads in either new module. The
dummy native call is recorded, never executed. `git diff --check` passed.

## 3. Small real example and output

Ollama was reachable at `http://127.0.0.1:11434` outside the sandbox, although the
CLI was absent from this shell's PATH. `/api/tags` found the existing model;
`/api/show` advertised `completion`, `tools`, `thinking`. No installation/pull
was needed. Ran:

```powershell
.\.venv\Scripts\python.exe scripts/13_test_ollama.py --output results/diagnostics/s13_ollama.json
# exit 0
```

Identity before and after both calls:

```text
tag: qwen3:4b
digest: 359d7dd4bcdab3d86b87d73ac27966f4dbb9f5efdfcc75d34a8764a09474fae7
quantization: Q4_K_M
parameter_size: 4.0B
```

| Call | Actual output | Prompt tokens | Generated tokens | HTTP wall latency |
|---|---|---:|---:|---:|
| Plain | `Hello!` | 16 | 209 | 46.914 s |
| Dummy tool | native `add`, arguments `{"a":2,"b":3}` | 146 | 295 | 3.111 s |

Both calls explicitly sent temperature 0, seed 42, num_ctx 8192 and num_predict
4096 (protocol §9.1 screening settings). The plain call includes model loading;
generated counts include the model's thinking, preserved in the raw evidence.
An independent assertion checked unchanged identity and the exact native arguments.

## 4. Assumptions

- The installed `qwen3:4b` is a suitable S13 software-check model because it
  advertises native tools; this does not select any experimental model.
- No scientific choice or `[TBD@S14/S21]` value is needed for synthetic S13 calls.
- The local server is kept stable during a diagnostic. Before/after identity
  comparison detects persistent changes, but is not an atomic model pin.

## 5. Design choices beyond the specification

All choices below are routine engineering; none is a proposed literature method.

- **HTTP/interface:** use existing `requests`, non-streaming `/api/chat`, and
  `OllamaClient(timeout_seconds=..., base_url=...)`. Return a dictionary with
  `raw_response`, `message`, `tool_calls`, `prompt_eval_count`, `eval_count`,
  `latency_seconds`. Raw response means the full decoded JSON; no fields are
  discarded and the message's native call objects are passed through unchanged.
  Assistant final-answer parsing stays at S14.
- **Transport config:** separate `configs/ollama.yaml`, URL
  `http://127.0.0.1:11434`, timeout 120 seconds. This is a requests connect/read
  timeout per attempt, not a total wall-clock/episode deadline or an S21 value.
  The client itself opens no config or data files; the caller supplies values.
- **Retries:** fixed maximum of two additional immediate attempts after a
  `requests.ConnectionError`, each logged with endpoint, attempt and error.
  No backoff or content-dependent retry. Request timeouts (including
  `ConnectTimeout`, which also subclasses `ConnectionError`) are checked first
  and never retried. Each call has a fresh retry budget.
- **Failure mapping:** HTTP/nonempty API error objects → RUNTIME unless the
  explicit OOM phrases match; timeout/connection exceptions → CONNECTION;
  other requests failures and malformed API envelopes → OTHER. Errors are
  logged and raised as `OllamaError` with cause and available original HTTP
  status/body. The S14 runner must enforce protocol §9.5 episode TIMEOUT
  precedence independently. A transport timeout alone is not an episode timeout.
- **OOM detection:** case-insensitive substring matching against server error
  text/failed HTTP bodies only: `out of memory`, `requires more system memory`,
  `not enough memory`, `insufficient memory`, `unable to allocate`,
  `failed to allocate`, `cudamalloc failed`, `cuda error: memory allocation`.
  Generic runner termination remains RUNTIME. New runtime wording can require
  an evidence-backed matcher extension; successful assistant content is never used.
- **API validation:** require a completed assistant-message envelope and a list
  for native calls; preserve each call for later dispatch/validation. Token counts
  must be nonnegative integers when supplied; missing values remain `None`.
  All four required generation options must be present and non-null.
- **Identity:** exact installed tag matching through `/api/tags`; omitted suffix
  becomes `:latest`. Digest comes from the matched installed entry; quantization,
  parameter size and capabilities from `/api/show`. Missing identity fields
  fail rather than receiving invented defaults. Capabilities are exposed so the
  diagnostic can check `tools`. The diagnostic compares full before/after identity.
- **Timing:** `time.perf_counter()` elapsed seconds around the chat HTTP operation,
  including connection retries; server nanosecond timings remain in raw JSON.
- **Diagnostic:** defaults to the already installed `qwen3:4b`, accepts `--model`
  and `--config`, and uses two independent synthetic conversations. It checks
  for a native function named `add`; absence makes exit status 1 without another
  generation. `--output` saves the full report with exclusive file creation;
  API failure retains any earlier response and error evidence. This diagnostic
  artifact is separate from protocol §19 completed episode records. No model
  selection is written to `configs/models.yaml`.

API behavior was checked against the official [chat API](https://docs.ollama.com/api/chat),
[model listing](https://docs.ollama.com/api/tags),
[error format](https://docs.ollama.com/api/errors), and
[native tool calling](https://docs.ollama.com/capabilities/tool-calling) documentation,
plus the actual local `/api/show` response.

## 6. Inspect by hand

Inspect `results/diagnostics/s13_ollama.json`: identical full digest before/after,
both token counts/timings, and `tool.raw_response.message.tool_calls` containing
native `add(a=2,b=3)`. The test confirms API plumbing only; model usability is
decided later by Gate D3. S14 remains unstarted.
