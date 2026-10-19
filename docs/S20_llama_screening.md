# S20 Llama screening complete (2026-10-18)

All 20 frozen screening queries are saved for Llama31-8B in run
primary-3060ti-20261018. **Llama fails D3**: 0/620 well-formed attempted calls
and 0/20 competent queries. This completes this candidate's screening block only;
it is not an S21 selection/freeze or acceptance of the full S20 candidate pool.

## 1. Files created or changed

- docs/decision_log.md: researcher acceptance, strict no-coercion decision,
  approved execution method recorded before inference, and final evidence.
- This report, docs/progress.md, tasks/plan.md and tasks/todo.md: continuation
  status and verification. Earlier checkpoint/preflight reports remain historical.
- results/runs/screening/primary-3060ti-20261018/: 19 new write-once episodes;
  the existing BH2_00461 record and Llama31-8B.config.json remain byte-identical.
- results/diagnostics/screening/screening_table.csv: regenerated from all saved
  records; complete=true, five criterion verdicts populated, d3_pass=false.
- results/diagnostics/screening/primary-3060ti-20261018/: 19 new per-episode
  metric files using unchanged S16-S19 evaluation.
- results/diagnostics/s20/llama-*: per-invocation logs/journal, full-suite output,
  report-only output, full summary, per-query CSV and integrity proof.

No agent, launcher, prompt, T1 schema, evaluator, config, dataset, existing test or
frozen scientific rule was changed. No commit or push was performed.

## 2. Tests and pre-run checks

### Three requested checks

1. Read the parser and --help. Exact flags are --run-id, --agent-id and --max-new.
   Used run primary-3060ti-20261018 and agent Llama31-8B. The latest researcher
   instruction replaces the earlier proposed batch size 19 with up to nineteen
   separate invocations using --max-new 1. Other mandatory flags stayed --model
   llama3.1:8b, --family Llama and --expected-digest followed by the approved digest.
2. Read evaluation/screening.py, T1 and decision_rules.md D3 together. The checker
   uses exact declared argument types, required fields and approved tool names,
   without coercion. JSON argument-object parsing is allowed; it does not convert
   string field values to integers. Probes: page="1" fails, page=true fails,
   page=1 passes. Extra fields are allowed by T1; unknown KG relations are a
   separate tool error rather than a schema-type rule. The checker was unchanged.
3. Before continuation, exactly BH2_00461 was saved, with nineteen frozen queries
   remaining in the original manifest order. All 43 pinned source/input hashes
   matched. Live host Ollama 0.40.4 confirmed the approved digest and no competing
   loaded model. The first record and per-model configuration hashes matched the
   accepted checkpoint.

### Execution and verification

Exactly 19 separate host invocations completed. After each, the shell read the
new record and checked native process exit code, ERROR status, reported drift,
expected query order, exactly one new record and unchanged earlier-file hashes
before issuing another invocation. All 19 Python launcher exits were zero; all
new statuses were SUCCESS. No stop condition occurred, no retry was made, and
BH2_00461 was never rerun.

Final full suite: **598 passed in 42.45 seconds**, no skips/deselections, using
--basetemp=.venv/s20-llama-final-tmp. No test was changed.

Report-only resume (--max-new 0) exited zero, regenerated the full table and left
exactly 20 unique episodes. All **21 run files** (20 episodes plus config) had
identical hashes before/after. All **43 pinned source/input hashes** and all
**122 protected identities** match. Original episode SHA256 remains
36a51907078f857fe75aeb25a0defa71c620d53405fdc138aa95e0f49cdea051;
configuration SHA256 remains
8c936436896ca42ef60bbbe617df263fddb61d03e814d954189d4b128923a85b.

Evidence: llama-final-full-suite.txt, llama-final-report-only.txt,
llama-continuation-journal.jsonl and llama-final-integrity-proof.json in
results/diagnostics/s20/.

## 3. Real examples, per-query results and D3

Model: llama3.1:8b, 8.0B Q4_K_M, digest
46e0c10c039e019119339687c3c1757cc81b9da49709a3b3924863ba87ca666e.
Hardware remains the RTX 3060 Ti 8 GB host. Generation is unchanged: think=false,
temperature=0, seed=42, num_ctx=8192, num_predict=4096, page_size=50, budget=30,
episode timeout=600 s, request timeout=120 s; frozen P1/T1 and query order.

Every episode returned exactly:

```json
{"status": "no_answer", "answers": []}
```

SUCCESS means final JSON parsed; it does not establish question competence.

| Query | Status | Wall seconds | Successful KG calls | Submitted answers |
|---|---|---:|---:|---:|
| BH2_00461 (original) | SUCCESS | 25.875 | 0 | 0 |
| BH2_02033 | SUCCESS | 27.330 | 0 | 0 |
| BH2_03434 | SUCCESS | 22.271 | 0 | 0 |
| BH2_03619 | SUCCESS | 22.940 | 0 | 0 |
| BH2_03750 | SUCCESS | 22.897 | 0 | 0 |
| BH2_03760 | SUCCESS | 22.044 | 0 | 0 |
| BH2_03762 | SUCCESS | 21.706 | 0 | 0 |
| BH2_03850 | SUCCESS | 21.514 | 0 | 0 |
| BH2_03856 | SUCCESS | 21.999 | 0 | 0 |
| BH2_03879 | SUCCESS | 21.744 | 0 | 0 |
| BH2_03881 | SUCCESS | 22.646 | 0 | 0 |
| BH2_03953 | SUCCESS | 22.142 | 0 | 0 |
| BH2_03991 | SUCCESS | 23.251 | 0 | 0 |
| BH2_04003 | SUCCESS | 21.005 | 0 | 0 |
| BH2_04007 | SUCCESS | 22.247 | 0 | 0 |
| BH2_04425 | SUCCESS | 21.719 | 0 | 0 |
| BH2_05366 | SUCCESS | 21.653 | 0 | 0 |
| BH2_05686 | SUCCESS | 23.239 | 0 | 0 |
| BH2_05843 | SUCCESS | 20.736 | 0 | 0 |
| BH2_06427 | SUCCESS | 22.123 | 0 | 0 |

All twenty individually emitted 31 get_neighbors calls, made 30 charged calls,
hit the budget, and supplied page as a string in every native call. No
inspect_entity call was emitted. Across the set: 620 native attempts, zero text
tool-call occurrences, zero schema-well-formed calls, 600 charged calls, zero
successful KG calls and zero submitted answers. **No query qualifies for the
requested successful-KG-call or submitted-answer exception list.**

| D3 criterion | Value and denominator | Threshold | Verdict |
|---|---|---|---|
| Well-formed / attempted calls | 0 / (620 native + 0 text) = 0% | >=90% | FAIL |
| SUCCESS episodes | 20/20 = 100% | >=90% | PASS |
| Competence | 0/20 = 0% | >=40% | FAIL |
| Median episode wall time | 22.132269 s, n=20 | <=300 s | PASS |
| ERROR episodes with OUT_OF_MEMORY | 0 among 20 episodes | 0 | PASS |

The median is an order statistic, not a rate: the tenth and eleventh sorted
durations are 22.122784 and 22.141754 s, whose mean is 22.132269 s. Overall
**d3_pass=false**, complete=true. Other statuses: ERROR=0, TIMEOUT=0, PARSE_FAIL=0.
Largest prompt_eval_count=2165; median charged tool calls=30; budget-hit share
20/20=100%. Total episode wall time, including the original checkpoint, is
451.081958 s. All queries remain in D3's official denominator.

## 4. Assumptions

The researcher's latest one-invocation-per-episode instruction is the approved
execution method. Scientific type rules, denominators and thresholds were taken
from D3 and the recorded no-coercion decision. No SUCCESS status was treated as a
correct answer. Candidate screening pass/fail is reported without making an S21
panel selection or choosing final runtime settings.

## 5. Design choices beyond the specification

Routine shell orchestration only: execute the unchanged launcher once per new
episode; retain per-invocation output, status and exit-code evidence; compare
earlier-file hashes before allowing another invocation. No implementation or
literature method was added.

A non-terminating wall-time-display error occurred in the shell: PowerShell
ConvertFrom-Json converted ISO timestamps to date objects, and an additional
DateTimeOffset.Parse call could not parse their locale-formatted strings. This
did not change any Python invocation's exit code, saved status, stop checks or
episode bytes. The original journal is retained without rewriting it. All
reported durations were calculated from the saved JSON's original ISO timestamps
using datetime.fromisoformat, exactly as the unchanged screening evaluator does.
No rerun, source patch or experimental-setting workaround was used.

## 6. Manual inspection

Three suggested records, selected to cover the accepted checkpoint, largest
observed prompt count and final continuation result:

- BH2_00461__Llama31-8B__a1.json: original accepted record, retained unchanged.
  Inspect guessed associated_with, string page="1", explicit unknown-relation
  errors and exhausted-budget no_answer.
- BH2_05686__Llama31-8B__a1.json: largest prompt count (2165); first call uses
  relation TREATS, neighbor_type Drug, page="1". Inspect the exact label/case
  guesses, KG error messages and final no_answer.
- BH2_06427__Llama31-8B__a1.json: last query; compare its frozen settings and
  get_neighbors/error/budget/no_answer sequence with the original checkpoint.

Records live under results/runs/screening/primary-3060ti-20261018/. No other
candidate was run; no S21 selection/freeze, commit or push occurred. Stop here.
