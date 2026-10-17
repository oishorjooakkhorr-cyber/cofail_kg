# S19 - Per-agent metrics (2026-10-17)

Implementation and automated verification complete; full-suite verification is
recorded in `results/diagnostics/s19/full-suite-final.txt`. The researcher accepted
S19 and its verification evidence on 2026-10-17; see the decision log.
Authority: explicit S19 request, protocol §15 and
runbook S19. Benchmark/failure clarifications are in `docs/decision_log.md`.

## 1. Files created or changed

- `src/cofail_kg/evaluation/agent_metrics.py`: evaluator-only metric row and a
  reusable full-KG degree/percentile table.
- `tests/test_agent_metrics.py`: 48 synthetic cases; existing S4/S12 fixtures reused.
- `results/diagnostics/s19/check_s14.py`: saved-episode replay with assertions.
- `results/diagnostics/s19/`: complete real row, inspection table, RED/GREEN,
  mutation/full-suite logs and before/after protected identities.
- This report, `docs/progress.md`, `docs/decision_log.md`, `tasks/plan.md` and
  `tasks/todo.md`: scope, researcher decisions, evidence and status.

Scope/callers: no prior S19 caller, export, config or fixture needs updating.
The verifier imports the helper directly, matching S17/S18. Existing parser,
S12 reconstruction, S16 normalization/deduplication, S17 labels and S18 path
labels are reused unchanged. No dependency or agent-facing import is added.

## 2. Tests run and results

Python: `.venv/Scripts/python.exe`; fresh basetemp directories under
`.pytest_cache/`, never saved-results directories. No test is removed/weakened.

| Check | Result | Evidence in `results/diagnostics/s19/` |
|---|---|---|
| RED degree/module | Expected missing-module collection error | `red-degree.txt` |
| Degree slice + S4 | 13 passed | `green-degree-fixed.txt` |
| RED episode metrics | Expected missing-function import error | `red-metrics.txt` |
| Initial metrics + dependencies | 134 passed | `green-metrics-fixed.txt` |
| Final focused suite | 148 passed, 2.30 s | `green-final-reviewed.txt` |
| Mutation: reverse early-stop page-2 condition | 7 failed, 39 passed, expected | `mutation-early-stop.txt` |
| Mutation: overwrite first returned bridge rank | 1 failed, 45 passed, expected | `mutation-first-bridge-rank.txt` |
| Full suite after restoration/final review | **556 passed**, 31.13 s, no skips/deselections | `full-suite-final.txt` |
| Full suite before accepted S19 commit | **556 passed**, 26.89 s, no skips/deselections | `full-suite-acceptance-20261017.txt` |
| Saved S14 replay | All assertions passed; complete row saved | `s14_metrics.json`, `hand-check.md` |
| Protected identities | **112/112 unchanged** | `protected_before.json`, `protected_after.json` |

Both mutations affected only the new evaluator and were restored byte-for-byte.
Review added UNION/GOLD_BRIDGE_EXTRA, all Label B values, malformed metadata,
missing optional S12 events, ignored page-2 calls and invariant checks.
The initial degree slice exposed pandas Series-aligned `isin`; membership now
uses the node-ID array. An initial test-helper keyword collision was fixed only
in the new test. A missing optional-event list is handled per the S12 schema,
with a reproducing RED case (`red-optional-events.txt`).

Commands:

```powershell
.\.venv\Scripts\python.exe -m pytest -q tests/test_agent_metrics.py tests/test_path_labels.py tests/test_answer_labels.py tests/test_trace.py tests/test_primekg_index.py --basetemp=.pytest_cache/s19-green-final-reviewed
.\.venv\Scripts\python.exe -m pytest -q --basetemp=.pytest_cache/s19-full-final
.\.venv\Scripts\python.exe results/diagnostics/s19/check_s14.py
```

No lint/type/build gate is configured. `git diff --check` and new-file whitespace
checks pass with the final verification. Failed intermediate evidence
is preserved; logs may have only trailing whitespace trimmed.

## 3. One real example, with output

Unchanged episode: `results/runs/s14-templatefix-20261016/BH2_00461__S14-qwen3-4b__a1.json`.

```text
query_id=BH2_00461; agent_id=S14-qwen3-4b; SUCCESS; BRIDGE; CONSISTENT
answers=resolved=GOLD=SUPPORTED=21; benchmark P=R=F1=1
question_valid_precision=1; off_question_rate=unresolved_rate=ungrounded_rate=0
bridges_explored=[111]; bridge_rank={111: 1}; bridge_conditional_recall={111: 1}
early_stop=false; pages_requested=2; tool_calls_used=4; budget_exhausted=false
TEXT_TOOL_CALL=0; H1_CLEAN; found_r1=true
all answers: FIRST_SEEN_PAGE=1; list_size=primary_path_max_list_size=21
```

The complete row includes every zero label/code count, each numerator/denominator,
undefined counts, all answer/path diagnostics, and full-KG degree/percentile values
for source, bridge and targets. The verifier checks all outputs against retained
S18 labels and raw returned items; degree values use an independent S4 lookup.

## 4. Assumptions

- Caller supplies the matching primary-population S7 row, complete S7 bridge
  targets, frozen mapping, verified KG and its degree table. The real replay
  verifies source identities, frozen hashes, saved episode reconstruction and
  consistency. Malformed records, mismatched queries/bridge sets and incomplete
  pagination metadata raise visibly.
- All metrics use S16 retained answers. A valid no_answer reply is a valid empty
  set per the existing parser. Technical failures have unknown answer metrics.
- The three researcher-selected conventions (resolved-only benchmark precision,
  count-form F1, technical-failure NA) are applied exactly as recorded.

## 5. Design choices beyond the specification

All are routine engineering; no literature method, scoring threshold or heuristic.

- JSON null represents NA. Store numerator/denominator and undefined counts for
  ratio metrics, plus undefined counts for bridge/per-answer numeric diagnostics;
  downstream averages must exclude nulls. No aggregate averages are computed here.
- One row has nested answer/bridge diagnostics so no variable-length evidence is
  lost. All known labels/codes have explicit zero counts on successful episodes.
- Pages requested count get_neighbors entries in the actual call log, including
  repeated, erroneous and budget-response requests; ignored calls are excluded.
  Calls used count budget-charged attempts, including errors but not exhausted
  replies. Reaching the configured budget sets the flag even without another call.
- Page-2 requests count even if they failed, because §15 says requested. Matching
  uses exactly (entity, label, neighbor_type); omitted neighbor_type equals None.
- FIRST_SEEN_PAGE and list size use the first successful neighbor listing, even
  if the node was inspected earlier. INSPECT is used only without any listing.
  A zero-edge/absent primary path has no path-list maximum (NA).
- Expose the maximum primary-path list size per answer, for subsequent PCF
  reporting; no co-failure case is computed in S19. Degree diagnostics cover the
  source, explored bridges, resolved answers and all primary-path nodes.
- Compute degrees once from verified S4 tables using distinct either-direction
  pairs, then inclusive same-type ranks, preserving isolates and self-loops.
  Callers reuse that table across episodes. Existing index code stays unchanged.

## 6. Manual inspection and limits

Review `results/diagnostics/s19/hand-check.md` against raw calls 1 and 3:
TTR rank is `(1-1)*50+1=1`, and early_stop is false because neither page has
has_more=true. The table includes every answer's page, fan-out and degree.
Engineering inspection and automated replay assertions are complete. Researcher
acceptance was subsequently explicit and is recorded in the decision log.

The final replay after the focused tests and full-suite run exactly matched the
retained complete metrics JSON. Review found no unresolved result-changing
discrepancy. All 112 protected identities are unchanged, including prior code
and tests, scientific rules, settings, data/cache and saved episodes.

The real example has no errors, unresolved answers or early-stop event. Those
branches are covered by synthetic episodes, not fresh model inference. No S20,
model selection, experiment or frozen-file change was performed. The researcher
subsequently authorized local commit `S19: per-agent metrics`, with no push or S20.
The decision log records the requirement that technical failures must not count
as answer failures in later §16 co-failure metrics; no §16 code is added here.
