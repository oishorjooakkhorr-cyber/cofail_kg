# S20 Llama continuation: preflight stop (2026-10-18)

All three requested pre-run checks pass. No new episode was run because the
unchanged launcher cannot guarantee the newly required immediate stop on ERROR.
The saved set remains one of twenty, with D3 verdicts undefined.

## 1. Files created or changed

- docs/decision_log.md: checkpoint acceptance, continuation authorization, strict
  no-coercion decision and preflight stop recorded before further inference.
- This report and diagnostics/s20 continuation verification logs.
- No agent, launcher, prompt, tool schema, evaluator, configuration, data or test
  source was modified. The original episode and run configuration are unchanged.

## 2. Tests and pre-run checks

1. Read scripts/20_screen_models.py and executed its --help. Exact flags:
   --run-id primary-3060ti-20261018, --agent-id Llama31-8B, --max-new 19.
   The additional required flags remain --model llama3.1:8b, --family Llama and
   --expected-digest 46e0c10c039e019119339687c3c1757cc81b9da49709a3b3924863ba87ca666e.
2. Read evaluation/screening.py, T1 and D3 together. call_counts checks required
   fields and exact declared types without coercion; string page="1" and Boolean
   page=true both fail, integer page=1 passes. JSON argument-object parsing is
   permitted by D3 and does not coerce the argument values. Extra arguments are
   permitted by T1; KG-relation validity is separate from schema-type validity.
3. Exactly one episode is saved: BH2_00461. Nineteen frozen queries remain, in order:

   BH2_02033, BH2_03434, BH2_03619, BH2_03750, BH2_03760, BH2_03762,
   BH2_03850, BH2_03856, BH2_03879, BH2_03881, BH2_03953, BH2_03991,
   BH2_04003, BH2_04007, BH2_04425, BH2_05366, BH2_05686, BH2_05843,
   BH2_06427.

All 43 pinned source/input hashes match. Saved episode SHA256:
36a51907078f857fe75aeb25a0defa71c620d53405fdc138aa95e0f49cdea051.
Saved configuration SHA256:
8c936436896ca42ef60bbbe617df263fddb61d03e814d954189d4b128923a85b.
Full unchanged suite: **598 passed in 32.83 seconds**, no skips/deselections,
using --basetemp=.venv/s20-continuation-tmp. Report-only resume (--max-new 0)
succeeded and regenerated the explicitly incomplete table. Afterwards exactly one
episode remains, the original episode/config hashes are identical, and all 43
pinned source/input hashes still match. Test/resume verification logs and proof
are recorded in results/diagnostics/s20/continuation-*.

Additional finding: run_screening has no ERROR-status stop between loading an
episode and advancing to the next query. The unchanged run_episode catches model
and runner exceptions and returns a saved ERROR record normally. Therefore a
batch of nineteen can continue after ERROR. No assumption that errors are
unlikely was used to bypass the researcher's requested stop policy.

## 3. Real example and output

No new inference. Existing record only:

| Query | Status | Wall time | Successful KG calls | Submitted answers |
|---|---|---|---|---|
| BH2_00461 | SUCCESS | 25.875167 s | 0 | 0 |

Output: {"status":"no_answer","answers":[]}.
SUCCESS refers to final JSON parsing, not question competence. Nineteen queries
are unrun, not failed or missing completed records.

| D3 criterion | Observed quantity | Required | Verdict |
|---|---|---|---|
| Well-formed / attempted calls | 0/31 | >=90% | Undefined: incomplete set |
| SUCCESS share | 1/1 observed; full denominator will be 20 | >=90% | Undefined |
| Competence | 0/1 observed; full denominator will be 20 | >=40% | Undefined |
| Median episode wall time | 25.875167 s, one observation | <=300 s | Undefined |
| ERROR with OUT_OF_MEMORY | 0 among one completed episode | 0 | Undefined |

Complete=false; overall D3 verdict remains undefined. No saved query has a
successful KG call or a submitted answer. These are the previous checkpoint
results; no new inference outcome has been observed.

## 4. Assumptions

None about the probability of ERROR or permission to edit frozen code. The
researcher's strict stop policy is binding even though the three named checks pass.
No model-level pass/fail is inferred from the incomplete set.

## 5. Design choices beyond the specification

No new implementation or scientific method. Routine engineering inspection
identified that an unguarded batch cannot enforce the requested stop rule.
No source patch, in-memory replacement or external supervisor was introduced.

## 6. Manual inspection

Inspect scripts/20_screen_models.py run_screening: after a new run_episode returns,
the code checks identity, loads/validates the record and appends it without a
status==ERROR branch. Inspect agents/run_agent.py's exception handler and normal
return of save_episode_record for why ERROR does not raise to the launcher.

Only one episode exists, so two or three distinct episodes cannot yet be nominated.
The existing BH2_00461 record is the available manual-inspection example: inspect
its guessed relation names, string page arguments and final no_answer output.
The continuation requires researcher resolution of the stop-policy conflict.
