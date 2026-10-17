# S18 - Label B, reason codes and hop-1 status (2026-10-17)

Implementation and automated verification complete. Researcher inspection and
acceptance remain pending. Authority: explicit S18 request, frozen protocol §14
and runbook S18. The researcher clarified that H1 requires a path without repeated
nodes; the decision is recorded in `docs/decision_log.md`.

## 1. Files created or changed

- `src/cofail_kg/evaluation/path_labels.py`: evaluator-only `label_paths`.
- `tests/test_path_labels.py`: 48 synthetic cases, including a deterministic
  comparison against exhaustive simple-path enumeration on 40 small cyclic graphs.
- `results/diagnostics/s18/check_s14.py`: saved-episode replay with assertions;
  checks every answer/path against raw returned items and the checksum-verified KG.
- `results/diagnostics/s18/`: RED/GREEN/full-suite/mutation logs, protected hashes,
  complete `s14_labels.json` and all-answer `hand-check.md` inspection table.
- `docs/progress.md`, `docs/decision_log.md`, `tasks/plan.md`, `tasks/todo.md`
  and this report: authority, H1 decision, evidence and current status.

Scope/callers: no prior Label B caller or package re-export exists. The verifier
imports the helper directly, matching S17. S12's graph/path utilities and S16's
`AgentResolution` are reused unchanged. There is no new agent-side import, config,
fixture file, dependency, model call or episode record.

## 2. Tests run and results

Python: existing `.venv/Scripts/python.exe`. Every pytest run uses a fresh
temporary directory under `.pytest_cache/`, never a saved-results directory.

| Check | Result | Evidence in `results/diagnostics/s18/` |
|---|---|---|
| RED: new Label B/reason module | Expected missing-module collection error | `red.txt` |
| First Label B slice + S12/S17 | 65 passed | `green-labels.txt` |
| RED: H1 output cases | 22 expected failures (missing H1 fields) | `red-h1.txt` |
| H1 slice + S12/S16/S17/S7 | 139 passed | `green-h1.txt` |
| Additional reviewed cases | 141 passed | `green-final.txt` |
| Final focused suite including cyclic-graph oracle | **142 passed**, 1.38 s | `green-reviewed.txt` |
| Mutation: allow H1 suffix to revisit source | **2 failed, 46 passed**, expected | `mutation-h1-source-return.txt` |
| Mutation: disable SUPPORTED priority | **5 failed, 43 passed**, expected | `mutation-supported-priority.txt` |
| Full suite after byte-for-byte restoration | **508 passed**, 24.47 s, no skips/deselections | `full-suite-final.txt` |
| Saved S14 replay/all-answer path checks | **21 GOLD/SUPPORTED**, all H1=1, H1_CLEAN | `s14_labels.json`, `hand-check.md` |
| Protected identities | **71/71 unchanged** | `protected_before.json`, `protected_after.json` |

Focused command (choose a new temporary directory if repeating):

```powershell
.\.venv\Scripts\python.exe -m pytest -q tests/test_path_labels.py tests/test_trace.py tests/test_answer_labels.py tests/test_normalize_agent.py tests/test_reference_sets.py --basetemp=.pytest_cache/s18-green-reviewed
```

Full command: `.\.venv\Scripts\python.exe -m pytest -q
--basetemp=.pytest_cache/s18-full-final`. `git diff --check` passes; new text files
were also checked for trailing whitespace. No lint/type/build gate is configured
in `pyproject.toml`. Logs had trailing whitespace trimmed only.

Both mutations changed only the new evaluator, were caught by behavioral checks,
and were restored byte-for-byte before the full suite. Existing checks were not
removed or weakened. The initial real replay exposed that pandas `set_index`
removes `query_id` from the row dictionary; the verifier now restores that field
before the evaluator's query-identity check. The successful replay verifies the fix.

Review checked all §14 priorities, overlapping paths, all reason codes including
simultaneous codes, primary-path tie ordering, absent/unopened/failed/ignored tool
evidence, source-as-answer, four-hop primary paths, non-gold bridges, H1 without a
length cap, correct/incorrect typed neighbors, every episode H1 status, empty
successful calls and ignored neighbor-type filters. The OFF_QUESTION/SUPPORTED
invariant is checked alongside synthetic evaluation and all 21 real answers.
No result-changing discrepancy remains from review.

## 3. One real example, with output

Replay (stdout JSON; no inference or episode writes):

```powershell
.\.venv\Scripts\python.exe results/diagnostics/s18/check_s14.py
```

Input: `results/runs/s14-templatefix-20261016/BH2_00461__S14-qwen3-4b__a1.json`.
This is the unchanged successful S14 diagnostic, in the primary population and
CONSISTENT, with BRIDGE construction.

```text
query_id: BH2_00461
Label A: GOLD=21
Label B: SUPPORTED=21
H1(x,i): 1 for all 21 answers
agent hop-1 status: H1_CLEAN
found R1: true
primary reason codes: [] for all answers
union reason codes: [] for all answers
```

Direct inspection of the complete raw four-call log:

| Call index (zero-based) | Tool | Returned evidence |
|---|---|---|
| 0 | inspect_entity(14097) | Source appeared; no trace edge |
| 1 | get_neighbors(14097, drug_protein, gene/protein, page 1) | TTR (111) |
| 2 | inspect_entity(111) | Bridge appeared; no new trace edge |
| 3 | get_neighbors(111, disease_protein, disease, page 1) | All 21 submitted disease IDs |

For example, Finnish type amyloidosis (27413) has primary path
`14097 --drug_protein [1]--> 111 --disease_protein [3]--> 27413`.
AL amyloidosis (27710) has the same first edge and final node 27710.
Every other answer has this same first edge and its own call-3 edge; there are
22 graph edges total and no competing path. Each bridge/target type, raw returned
item, creation index, frozen relation and underlying KG edge was verified.
The sole successful neighbor call on the source uses R1, hence H1_CLEAN.

`hand-check.md` lists **every one of the 21 names, IDs, primary paths, labels,
codes and H1 values**. `s14_labels.json` additionally retains the exact raw
returned items and call indices for both edges of each answer.

## 4. Assumptions

- Inputs are retained S16 resolutions, the matching original S7 query dictionary
  and frozen per-type R1/R2 mapping. IDs remain canonical strings. No second
  normalization/deduplication pass occurs here.
- The caller supplies the correct checksum-verified KG/mapping. The real verifier
  checks frozen identities, S17 source hashes, primary membership and consistency.
  Unknown nodes, missing fields and malformed call logs fail visibly.
- `label_paths` rebuilds graph/appearance from raw calls using S12, rather than
  trusting supplied derived fields; saved-record reconstruction is checked on load.
- Per the researcher, an H1 supporting path is simple, without a length cap.
  The ≤3 limit applies only to the §14.2 reason-code union.

## 5. Design choices beyond the specification

All are routine engineering; no literature method, scoring threshold or heuristic:

- One function returns an answer-aligned dictionary list plus episode H1 fields.
  `label_b`, `primary_reason_codes`, `reason_codes` (the union), `primary_path`
  and `h1` are explicit fields. Paths contain S12 edge dictionaries with creation
  indices. Codes are unique and alphabetically sorted.
- An absent path is `None`; a present zero-edge source path is `[]`. Grounded reachable
  answers retain their primary path even when SUPPORTED; **codes are emitted only
  for PATH_INVALID**, as §14.2 says. SUPPORTED can have an invalid shorter primary
  path when another valid two-hop path exists; its code arrays remain empty.
- Precompute valid two-hop support directly from graph edges, independently of
  primary paths. This preserves SUPPORTED priority over invalid alternatives.
- Compute H1 by reverse reachability from x with s excluded, then intersect with
  correct typed R1 neighbors other than x. Reachability guarantees a simple suffix;
  excluding s prevents repeated-source routes. This avoids enumerating arbitrary
  length simple paths. It takes O(V+E) per grounded reachable answer, in addition
  to unchanged S12 primary-path and bounded simple-path costs.
- Cache node types within one call. Rebuild graph and successful-call evidence
  with existing S12 validation; reject mismatched query IDs and absent/empty
  relation mappings. No framework, package re-export or dependency added.

## 6. Manual inspection and limits

Researcher: review **all 21 rows** of `results/diagnostics/s18/hand-check.md`
against the saved episode, including both creation indices and the call-3 returned
items. Review the cyclic-source H1 regression and the SUPPORTED-with-shortcut case.
Engineering inspection and automated assertions are complete; researcher acceptance
has not been inferred.

The real example exercises SUPPORTED only. Other labels, reason codes and H1
statuses are covered by synthetic traces. This verifies evaluation behavior, not
model reliability or pilot outcomes. No new inference, scientific-file edit,
experimental setting change, S19 work, commit or push was performed.
The researcher subsequently explicitly authorized committing and pushing S18;
the publication authorization is recorded in the decision log.
