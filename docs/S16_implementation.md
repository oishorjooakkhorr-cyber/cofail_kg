# S16 — Answer normalization (2026-10-17)

Implementation and automated verification are complete. Researcher inspection and
acceptance are pending. Authority: the researcher's explicit request to start S16,
runbook S16, and frozen protocol §12. The latest remote commit, 20997df,
records S15 acceptance and was integrated before the S16 push. Earlier local
references to pending S15 review were stale; that remote approval is preserved.

## 1. Files created or changed

- `src/cofail_kg/evaluation/normalize.py`: adds `AgentResolution`, `resolve_agent`,
  `NormalizedAnswers` and `normalize_agent_answers`; updates the module description.
  All four existing S7 class/function definitions are unchanged.
- `tests/test_normalize_agent.py`: 42 synthetic cases using the actual PrimeKG
  ID/name lookup methods on a tiny in-memory node index. No full KG in unit tests.
- `results/diagnostics/s16/`: protected-file baseline/comparison, RED/GREEN logs,
  deliberate mutation result, full-suite log and saved S14 normalization output.
- `docs/decision_log.md`: direct S16 authorization, the researcher's unresolved
  duplicate decision and verification outcome.
- `docs/progress.md`, `tasks/plan.md`, `tasks/todo.md`: stage status and checklist.
- This report.

No dependency or configuration change. Existing callers of `resolve_reference`
and `index_finder` require no changes. The evaluation package has no re-export
convention to extend; functions are imported directly from `evaluation.normalize`.
The experimental agent runner does not import this evaluator module.

## 2. Tests run and results

All commands used `.venv/Scripts/python.exe` in the restricted Windows sandbox.
Temporary roots are under `.pytest_cache/`, outside `results/`.

| Check | Command after the Python executable | Result |
|---|---|---|
| Item RED | `-m pytest tests/test_normalize_agent.py -q --basetemp .pytest_cache/s16-red-01` | Expected collection failure: `resolve_agent` not implemented |
| Item GREEN + S7 | `-m pytest tests/test_normalize_agent.py tests/test_normalize_reference.py -q --basetemp .pytest_cache/s16-green-item-01` | 42 passed, 0.97 s |
| List RED | `-m pytest tests/test_normalize_agent.py -q --basetemp .pytest_cache/s16-red-list-01` | 7 expected failures for missing list function; 35 passed |
| Complete focused GREEN | `-m pytest tests/test_normalize_agent.py tests/test_normalize_reference.py -q --basetemp .pytest_cache/s16-green-list-01` | 49 passed, 0.76 s |
| Deliberate mutation | `-m pytest tests/test_normalize_agent.py -q --basetemp .pytest_cache/s16-mutation-01` | Incorrectly ignoring submitted ID in unresolved identity was caught: 1 failed, 41 passed |
| Final full suite | `-m pytest -q --basetemp .pytest_cache/s16-full-01` | **443 passed, 27.81 s; no skips/deselections** |

The mutation was restored byte-for-byte in a `finally` block before the full
suite. It is a test-sensitivity check, not a retained implementation failure.
`git diff --check` passes. No configured build, lint or static-type gate exists
in `pyproject.toml`; no dependency installation was needed.

### Protocol review

| §12 requirement | Implementation/coverage |
|---|---|
| String/integer ID; trim whitespace; exact canonical identity | ID lookup before name lookup; tests include noncanonical ID strings and integer IDs |
| Valid ID wins over name and target type | Tested with a wrong name and wrong target type; records `name_id_mismatch` |
| Exact normalized names | Existing `normalize_name` through actual index lookups; lower-case, NFKC, trim and internal whitespace coverage |
| Unique target-type name preferred | Tested with two same-name nodes of different types |
| Disease-suffix retry before any-type fallback | Reuses unchanged S7 resolver; tests unique suffix, ambiguous suffix, no retry on direct ambiguity, and non-disease target |
| Unique any-type match remains resolved | Wrong-type node retained for later labeling; no S17 label assigned |
| Ambiguous/no matches | Distinct `AMBIGUOUS_NAME` and `NO_MATCH` reasons; no fuzzy or embedding matching |
| Post-resolution duplicates removed | Same resolved ID across string/integer/name paths; distinct same-name IDs retained |
| Unresolved duplicates | Exact submitted pair per direct researcher decision; case/whitespace and string/integer differences retained |
| Evidence and errors | Item-aligned results preserve removed duplicates' flags; invalid parsed-item shapes rejected; index failures propagate |

No result-changing discrepancy was found in the final review. The runbook's S16
case list omits the disease-suffix detail present in frozen §12; the implementation
follows the protocol and tests it explicitly.

## 3. One real example, with output

Replayed the saved successful diagnostic episode, without a model call:

`results/runs/s14-templatefix-20261016/BH2_00461__S14-qwen3-4b__a1.json`

The existing episode loader validated trace reconstruction. The existing parser
parsed its final answer. `Type_T=disease` came from this query's evaluator-side
reference row. The loaded cache was checksum-verified by `PrimeKGIndex`, and the
metadata-file hash matched both the episode and frozen KG fingerprint. Every
submitted ID/name pair was verified against a saved successful neighbor result.

```text
query_id: BH2_00461
target_type: disease
input_count: 21
retained_count: 21
resolved_by_id: 21
unresolved_count: 0
name_id_mismatch_count: 0
duplicates_removed: 0
example: {id: "27413", name: "Finnish type amyloidosis"}
      -> {node_id: "27413", method: "ID", reason: null,
          name_id_mismatch: false, via_suffix: false}
```

All 21 per-item results, source hashes and retained indices are in
`results/diagnostics/s16/s14_normalization.json`; the complete printed output is
`real-example-v2.txt`. The initial one-off verifier incorrectly expected a
`kg_fingerprint` key inside metadata and stopped before normalization; its
`KeyError` is retained in `real-example.txt`. The corrected verifier uses the
repository's existing `file_hash` on the metadata file. No production fix was
needed for that verifier mistake.

To reproduce the normalization read-only from the repository root in PowerShell:

```powershell
@'
from dataclasses import asdict
from pathlib import Path
import json
import pandas as pd
from cofail_kg.agents.run_agent import parse_final
from cofail_kg.agents.trace import load_episode_record
from cofail_kg.evaluation.normalize import normalize_agent_answers
from cofail_kg.kg.primekg_index import PrimeKGIndex

record = load_episode_record(Path('results/runs/s14-templatefix-20261016/BH2_00461__S14-qwen3-4b__a1.json'))
parsed = parse_final(record['raw_final_output'], [])
query = pd.read_parquet('data/processed/reference_queries.parquet').set_index('query_id').loc[record['query_id']]
result = normalize_agent_answers(PrimeKGIndex('data/cache'), parsed['answers'], query['Type_T'])
assert len(result.answers) == 21 and result.duplicates_removed == 0
assert all(item.method == 'ID' for item in result.items)
print(json.dumps(asdict(result), indent=2))
print('duplicates_removed:', result.duplicates_removed)
'@ | .\.venv\Scripts\python.exe -
```

## 4. Assumptions and researcher decision

- Input is the parsed answer list, with a string/integer `id` and string `name`,
  as specified by the existing §9.4 parser. S16 also rejects malformed items.
- `target_type` is the query's existing `Type_T`, supplied only to evaluation.
- Under §12's wording "name differs," the ID-path mismatch flag compares the
  submitted and canonical names literally. Name lookup still uses §12's normalized
  equality. ID acceptance is unaffected by either comparison.
- The researcher explicitly selected deduplication of identical unresolved
  submitted `(id, name)` pairs. Distinct unresolved pairs remain separate, including
  integer/string ID differences and name case/whitespace differences. This is a
  researcher decision, not an assistant-selected scientific default.

## 5. Design choices beyond the specification

All are routine engineering; no additional literature method or heuristic:

- Reuse the unchanged S7 resolver for typed-name/suffix lookup and the existing
  index for IDs and unrestricted names; introduce no new matching implementation.
- Represent per-item outcomes with a frozen dataclass. `node_id=None` means
  UNRESOLVED; `reason` distinguishes the two failure categories. Boolean
  `name_id_mismatch` represents the requested `NAME_ID_MISMATCH` flag.
- Retain results for every submitted item plus first-occurrence indices. The
  `answers` and `duplicates_removed` properties derive the deduplicated view and
  count, preserving flags on discarded duplicates without modifying inputs.
- Use a local set of tagged keys for linear-time deduplication. Preserve submitted
  order rather than sorting or selecting a preferred resolution method.
- Record `via_suffix` separately while keeping method `NAME_TARGET_TYPE`, so a
  suffix resolution is auditable without adding a new scientific method category.
- Reuse the existing parser/episode loader for the saved example; no model call,
  experiment launcher, configuration switch or additional dependency.

## 6. Manual inspection and limits

Inspect the saved real-example JSON and the synthetic duplicate cases, especially
`test_distinct_unresolved_submissions_are_kept`, against the recorded decision.
S16 normalization establishes identity only; it does not establish GOLD,
OFF_QUESTION or path support. Those are later stages.

`protected_after.json` confirms all 50 baseline files are byte-identical: protocol,
decision rules, CLAUDE.md, configs/frozen hashes, data, saved episodes, agent code
and KG code. It also confirms the four S7 definitions are unchanged. During
implementation verification, no model calls, new episodes, commits, pushes or S17
work were performed. The researcher subsequently authorized commit/push and an
immediate Drive backup. Remote S15 approval and its handoff removal were integrated;
S16 source/tests and all prior diagnostic evidence remain unchanged.
