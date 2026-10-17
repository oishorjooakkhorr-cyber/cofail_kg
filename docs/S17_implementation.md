# S17 - Label A (2026-10-17)

Implementation and automated verification complete; researcher accepted S17 and
its verification evidence on 2026-10-17. Acceptance is recorded in the decision
log, with explicit authorization to commit `S17: Label A` and push.
Authority: the researcher's explicit S17 request, including G_q by construction,
UNION coverage, CONSISTENT-query extra-target errors and construction in the hand
check; frozen protocol §6/§13 and runbook S17. No scientific rule was changed.

## 1. Files created or changed

- `src/cofail_kg/evaluation/answer_labels.py`: evaluator-only `label_answers`.
- `tests/test_answer_labels.py`: 17 synthetic cases, including S7 integration.
- `results/diagnostics/s17/check_s14.py`: reproducible saved-episode verifier with
  assertions; prints all answers and two hand-check records, without inference.
- `results/diagnostics/s17/`: RED/GREEN/full-suite/mutation logs, before/after
  protected-file hashes, saved `s14_labels.json` and direct `hand-check.txt`.
- `docs/pipeline_runbook.md`: S17 wording aligned with existing §6/§13 and the
  researcher's request. Replaces the older universal gold-bridge comparison with
  G_q, adds UNION/error checks and construction to the hand check.
- `docs/progress.md`, `docs/decision_log.md`, `tasks/plan.md`, `tasks/todo.md` and
  this report: authorization, scope, evidence and current stage status.

Scope inspection: no existing Label A caller or package re-export exists. The new
verifier imports the function directly, matching evaluation-module conventions.
S16's `NormalizedAnswers.answers` supplies retained results. Existing normalization,
reference builders, fixtures, configuration and dependencies need no changes.
There is no new import from experimental agent code into evaluation.

## 2. Tests run and results

Python: existing `.venv/Scripts/python.exe`. All temporary roots are fresh
directories under `.pytest_cache/`; none is a results directory.

| Check | Result | Evidence under `results/diagnostics/s17/` |
|---|---|---|
| RED, new test module | Expected missing-module collection failure | `red.txt` |
| Focused S17 + S16/reference normalization + S7, final tests | **76 passed**, 0.82 s | `green-final.txt` |
| Mutation: reverse `if consistent` | **3 failed, 14 passed**, expected; restored byte-for-byte | `mutation.txt` |
| Mutation: substitute gold-bridge targets for G_q in labeling | **1 failed, 16 passed**, expected; restored byte-for-byte | `mutation-gq.txt` |
| Final full suite after restoration | **460 passed**, 24.89 s, no skips/deselections | `full-suite-final.txt` |
| Saved S14 replay and two hand checks | **21 GOLD**, assertions pass | `s14_labels.json`, `hand-check.txt` |
| Protected identities | **53/53 unchanged** | `protected_before.json`, `protected_after.json` |

The initial passes are retained in `green.txt` and `full-suite.txt`. Review strengthened the
UNION extra-target test to use a node outside gold-bridge targets, then verified
that the universal-gold-bridge mutation fails. The final focused/full runs use
that strengthened test. The production implementation did not change.

Focused command (use a fresh temporary directory when repeating):

```powershell
.\.venv\Scripts\python.exe -m pytest -q tests/test_answer_labels.py tests/test_normalize_agent.py tests/test_normalize_reference.py tests/test_reference_sets.py --basetemp=.pytest_cache/s17-green-final
```

Full-suite command: `python -m pytest -q --basetemp=.pytest_cache/s17-full-final` using
the same virtual environment. Choose a fresh temporary directory when repeating.
`git diff --check` passes. No configured lint, type-check or build gate exists in
`pyproject.toml`; no dependency installation was needed.
Only trailing whitespace in the saved pytest mutation log was trimmed before
commit; its diagnostic content and test outcome are unchanged.

Protocol review: UNRESOLVED precedes all memberships; GOLD precedes construction
and alternative memberships; GOLD_BRIDGE_EXTRA precedes ALT_VALID; OFF_QUESTION
includes the source entity. Shared targets reached through two bridges get one
label per normalized answer. The BRIDGE/UNION integration tests call the real S7
builder, with a valid answer outside the gold-bridge target set: it is ALT_VALID
under BRIDGE and GOLD under UNION. UNION therefore cannot emit ALT_VALID.
Both constructions raise ValueError if a CONSISTENT query would emit
GOLD_BRIDGE_EXTRA. Missing G_q never falls back to gold-bridge targets.

## 3. One real example, with output

Replayed the unchanged saved successful S14 diagnostic episode:
`results/runs/s14-templatefix-20261016/BH2_00461__S14-qwen3-4b__a1.json`.

```text
query_id: BH2_00461
relation_type: drug:gene/protein:disease
construction: BRIDGE
primary_population: yes
status: CONSISTENT
retained answers: 21
labels: GOLD=21; all other labels=0
```

| ID | Answer | Label A |
|---|---|---|
| 27413 | Finnish type amyloidosis | GOLD |
| 27710 | AL amyloidosis | GOLD |
| 27933 | anxiety disorder | GOLD |
| 28275 | corneal dystrophy | GOLD |
| 28831 | carpal tunnel syndrome | GOLD |
| 29041 | familial adenomatous polyposis | GOLD |
| 29695 | hyperthyroxinemia, dystransthyretinemic | GOLD |
| 30929 | ABri amyloidosis | GOLD |
| 31116 | lung cancer | GOLD |
| 32117 | familial amyloid neuropathy | GOLD |
| 33591 | amyloidosis (disease) | GOLD |
| 36544 | drug-induced liver injury | GOLD |
| 36812 | lung neoplasm | GOLD |
| 37703 | neurotic disorder | GOLD |
| 37798 | hereditary amyloidosis | GOLD |
| 37871 | pancreatic neuroendocrine neoplasm | GOLD |
| 38035 | acute kidney failure | GOLD |
| 83760 | dysthymic disorder | GOLD |
| 83840 | unipolar depression | GOLD |
| 84174 | AH amyloidosis | GOLD |
| 84193 | ATTRV122I amyloidosis | GOLD |

Hand checks, inspected directly against the saved parquet rows and membership sets:

| Answer | Exact `reference_targets.parquet` row (query, bridge, target) | Membership and label |
|---|---|---|
| Finnish type amyloidosis | `(BH2_00461, 111, 27413)` | In A*_q and G_q; GOLD |
| AL amyloidosis | `(BH2_00461, 111, 27710)` | In A*_q and G_q; GOLD |

The relation type is **BRIDGE**, so G_q = T_q^{B*}. For both answers the listed
bridge is the gold bridge **111, TTR**, not a different bridge. The checksum-verified
KG confirms source 14097 reaches TTR through frozen R1 `drug_protein`; TTR reaches
each disease through frozen R2 `disease_protein`, using the frozen either-direction
convention. This checks the reference memberships; Label A itself uses no agent
trace/path evidence. The source is drug
`2,6-dimethyl-4-[(E)-2-phenylethenyl]phenol`.

Replay command, which prints JSON and does not write episode records:

```powershell
.\.venv\Scripts\python.exe results/diagnostics/s17/check_s14.py
```

The verifier confirms primary-population membership, the frozen mapping/cache
identities, episode and S7 identities from the saved S16 evidence, and identical
S16 item resolutions and retained indices. Source hashes are saved with the output.

## 4. Assumptions

- Inputs are S16's already-normalized, deduplicated retained answer objects and
  the corresponding S7 query row. Canonical IDs remain strings. A missing node ID
  means UNRESOLVED; mismatch flags and resolution methods do not change Label A.
- Official evaluation calls the helper only for primary-population queries, as
  §13 requires. The helper does not load the population itself; the saved-example
  caller verifies membership and supplies the explicit S8 CONSISTENT status.
- `consistent=False` is used in synthetic diagnostics to test the otherwise
  forbidden GOLD_BRIDGE_EXTRA label. It does not admit inconsistent queries into
  official scoring.

## 5. Design choices beyond the specification

All are routine engineering; no literature method, threshold or matching heuristic:

- One pure batch function returns label strings in input order, converting saved
  membership lists to sets once per call. Time is linear in reference-set sizes
  plus the number of answers. It does not mutate inputs or deduplicate again.
- Require an explicit keyword-only `consistent` flag, with no default. Use
  ValueError containing query and answer ID for forbidden CONSISTENT extra labels;
  do not return partially computed labels after an error.
- Validate saved G_q against the saved construction definition, rather than
  replacing/recomputing G_q for labeling. Missing fields fail visibly.
- Preserve the S7 query dictionary shape and S16 AgentResolution type; introduce
  no new result class, configuration, dependency, command-line framework or export.
- Keep the stage-specific replay and its assert-based self-checks in diagnostics.
  Its fixed input is the existing S14 diagnostic; it makes no new model call.

## 6. Manual inspection and limits

Researcher inspection: review the two hand-check rows above and the UNION
integration test; inspect the complete saved answer list in `s14_labels.json`.
The real example exercises GOLD only; synthetic cases exercise every other label,
both construction modes and forbidden-extra errors. No result-changing discrepancy
was found in review. The runbook wording conflict was corrected to the existing
protocol and the researcher's explicit instruction.

No new inference, experimental episode, metric, Label B or S18 work. No commit or
push occurred during implementation; the researcher subsequently accepted S17
and explicitly authorized committing and pushing it. Earlier pending acceptance
statements are superseded by the decision-log acceptance entry.
