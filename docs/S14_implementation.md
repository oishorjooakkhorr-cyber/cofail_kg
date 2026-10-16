# S14 implementation and S12/S13 fixes — 2026-10-16

The researcher requested fixes, explicitly chose to complete S14 with its tests
active, and enabled thinking for the single S14 example. The implementation and
full host suite pass. The real example ended in PARSE_FAIL, so S14 is **implemented
but awaiting researcher review**, not accepted/frozen as a successful real traversal.

## 1. Files created or changed

- `configs/ollama.yaml`: restored explicit `think: true` for the S13 synthetic
  diagnostic, consistent with the existing 2026-10-15 decision log. This fixes the
  five KeyError failures without selecting the eventual experimental thinking policy.
- `src/cofail_kg/agents/prompts.py`: verbatim runbook P1 and user templates, P1
  version and SHA256. Only PAGE_SIZE/BUDGET are substituted into the system prompt.
- `src/cofail_kg/agents/run_agent.py`: fresh conversation per episode; exact four-field
  sheet validation and hash check; native tools through KGEnvironment; final reply
  parsing; one fixed re-prompt; budget handling; TIMEOUT precedence; full messages,
  raw thinking/responses, token counts and errors; attempt-1 S12 checkpoint.
- `scripts/14_run_episode.py`: first screening query with qwen3:4b and the exact
  screening settings; explicit `--think`; frozen sheet/cache-metadata/T1 checks;
  output-directory hard-link preflight; installed model identity before/after;
  source hashes to identify the uncommitted implementation; printed record path.
- `tests/test_run_agent.py`: retained every original draft test, added edge-case
  checks and a regression for the real thinking-only token-limit responses.
- `tests/test_run_episode_script.py`: launcher configuration, frozen-sheet rejection,
  persistence rejection before any model call, duplicate-run refusal and identity drift.
- `README.md`, `docs/progress.md`, `docs/decision_log.md`, this report and diagnostic
  evidence: reproduction instructions and current results.

S12 saver code was unchanged; its SHA256 still matches the earlier host verification.
No tests were removed, skipped, marked xfail or excluded. Existing S13 uncommitted
work remains intact. No commit, protocol edit or frozen-hash update was made.

## 2. Tests and results

Host commands, outside the Codex restricted sandbox:

```powershell
.\.venv\Scripts\python.exe -m pytest tests/test_ollama_smoke_script.py -q
.\.venv\Scripts\python.exe -m pytest -q
```

S13 focused: **7 passed**. Final full suite: **348 passed in 10.02 s**, including
all 301 earlier cases plus 47 S14 cases (43 runner/parser, 4 launcher).
Evidence: `results/diagnostics/s14_final_suite_20261016.txt`.
Compilation and `git diff --check` passed. The added regression confirms that
empty content with preserved thinking and `done_reason=length` receives exactly
one re-prompt, then PARSE_FAIL, without invented or text-executed tool calls.

The restricted sandbox's OS permissions remain unchanged. Normal host execution
is the verified route. The launcher now checks the actual `results/runs` directory
before spending model inference; a blocked hard link stops with an actionable error.

## 3. One real example and output

```powershell
.\.venv\Scripts\python.exe scripts/14_run_episode.py --run-id s14-review-20261016 --think true
```

The local server was initially stopped. The first launcher attempt failed while
obtaining model identity, before any episode/model generation. Its failure transcript
is preserved in `results/diagnostics/s14_review_20261016_console.txt`. The installed
`.venv/ollama/ollama.exe` server was then started hidden, bound to 127.0.0.1:11434,
using the existing `D:\Models` store. Exactly one episode was subsequently run.

Record:
`results/runs/s14-review-20261016/BH2_00461__S14-qwen3-4b__a1.json`

| Field | Observed |
| --- | --- |
| Query | BH2_00461, first screening row; starting ID 14097 |
| Model | qwen3:4b, 4.0B, Q4_K_M; same digest before/after |
| Think | true, researcher selected for this example only |
| Settings | temperature 0; seed 42; context 8192; output cap 4096; page size 50; tool budget 30; episode timeout 600 s |
| Status | PARSE_FAIL, cause null |
| Episode duration | 90.10505 s |
| Prompt tokens | 598, 627 (maximum 7.65% of context) |
| Generated tokens | 4096, 4096 |
| Stop reasons | length, length |
| Final content | Empty on both replies |
| Native tool calls / trace edges | 0 / 0 |
| Re-prompts | Exactly one, protocol text unchanged |

Both replies generated thinking, including imagined tool interactions, but supplied
no native tool calls and no final JSON. The runner executed none of that text.
The output cap was exhausted; there was no context overflow or episode timeout.
This is an observed model failure under the requested settings, not a persistence
or test-suite failure. No extra content-based retry, alternate model, prompt tuning
or token-budget increase was performed.

The record was read and reconstruction verified. Exact system and user messages,
all raw assistant thinking/messages, two parse errors, the single fixed re-prompt,
counts and source hashes were checked. There are no real tool results to compare
against `inspect_kg.py`, no route to inspect and no final answers to test for grounding.
Those real-example acceptance checks remain unexercised; mocked successful episodes
cover the runner's tool path.

Evidence: `results/diagnostics/s14_review_20261016_verification.json`,
`s14-review-20261016_identity.json`, `s14_review_20261016_console_started.txt` and
`s14_ollama_server_{stdout,stderr}.txt` in the same directory. Record SHA256:
`d43bcebb7c41113694ba1126bfe253042af01522c7812339502671790bca0425`.

## 4. Assumptions

The S14 scope is the supplied runbook stage, now expressly authorized. The S13
test model is qwen3:4b. Researcher-selected think=true applies only to this S14
example. The general experimental thinking policy remains undecided. Launcher
configuration/provenance is trusted input; agent sheet and model replies are validated.

## 5. Engineering choices beyond the specification

All are routine engineering, with no scientific rule or literature method selected:

- A researcher launcher loads configuration/frozen identities and passes values
  to the runner; the runner opens only its sheet/cache data and writes its result.
- P1 identity is `P1:<template SHA256>`. Draft review is explicitly recorded;
  nondraft use requires a matching approved prompt hash supplied by the launcher.
- The entire sheet's bytes are hash-checked, and every row is validated for exactly
  four nonempty string fields, canonical starting IDs and unique query IDs.
- A monotonic clock checks the deadline around model/tool operations and before
  final status assignment. Each HTTP timeout is capped by remaining episode time.
  Synchronous operations are not forcibly killed; late returns are retained and
  classified TIMEOUT, which takes precedence over their other outcome.
- Extra keys and ignored no-answer items are logged; ID types remain unchanged.
  Boolean IDs and nonstandard JSON constants are rejected. Whole fenced JSON
  blocks accept optional language tags and Windows line endings.
- TEXT_TOOL_CALL detection inspects assistant `content`; thinking is preserved in
  the raw message and is never parsed as a final answer or executed as a tool.
- Unexpected operational exceptions become ERROR/OTHER with type and message in
  the episode; Ollama errors preserve their cause and HTTP evidence. Persistence
  failures propagate rather than pretending a record was saved.
- Temporary hard-link preflight files are cleaned up. The final saver retains its
  atomic no-overwrite behavior. Existing final records stop another run; leftover
  temporary files do not count as completed episodes.
- Raw assistant messages and tool responses follow the official
  [Ollama tool-calling format](https://docs.ollama.com/capabilities/tool-calling).
  A separate write-once launcher summary records before/after model identity.

## 6. Researcher inspection and remaining decision

Review the exact template in `src/cofail_kg/agents/prompts.py` and the real record.
P1 template SHA256:
`8f93b7c42ef7a90f64bbcd83e6b77db62e4f3c6b0c08a45f068b435a9c655265`.

Runbook S14 explicitly assigns template approval to the researcher after reviewing
the real episode, and protocol §9.3 says its text is approved by the researcher.
The template is therefore not yet frozen. This example does not establish a
successful real traversal or answer. Review that outcome before accepting S14;
any further episode/settings change needs an explicit decision and a new run ID.
S15 and later stages were not started. Changes remain uncommitted.
