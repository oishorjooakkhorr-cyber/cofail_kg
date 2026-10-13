# S6 first prompt — proposed relation mappings

Computed 2026-10-13 from protocol v1.3.3 §5.1–5.3 and decision rules D1.
The researcher requested only the first runbook prompt. No mapping, construction or ambiguity
tag is frozen; no exclusion decision has been made, and S7 has not started.

## Result

**Global D1: PROCEED.** Nine of twelve types PASS, covering 7,377 of 7,633 rows (96.65%).
335 validation rows were selected. No query/bridge row was skipped before the samples filled,
and no sampled answer remained unresolved under the v1.3.3 reference resolver.

Eight passing types propose BRIDGE. `disease:drug:effect/phenotype` proposes UNION (949 rows).
Passing ambiguity tags: NONE 2, R1_AMBIGUOUS 3, R2_AMBIGUOUS 2, BOTH_AMBIGUOUS 2.

| Failing relation type | Sample | Best BRIDGE | Best UNION | Explanation |
|---|---:|---:|---:|---|
| disease:effect/phenotype:drug | 30 | 3/30 | 3/30 | Both below 90%; raw examples contain extra reachable drugs |
| drug:effect/phenotype:disease | 5 | 0/5 | 0/5 | Both below 90%, and fewer than 10 validation rows |
| effect/phenotype:drug:disease | 30 | 26/30 | 20/30 | Both below 90%; different rows reproduce under different constructions |

The five-row type has a hop-2 tie between `disease_phenotype_negative` and
`disease_phenotype_positive` under both constructions. Both score zero; neither is chosen.
The positive label reaches gold diseases plus extras in the inspected examples; the negative
label misses the gold diseases. This cannot change the type's FAIL or global PROCEED.
Researcher disposition (2026-10-13): **keep the failed type's tie unresolved**. Neither label
is selected, including for diagnostics. This leaves the type's FAIL and global PROCEED unchanged.
The generated outputs remain the original computation snapshot; their `NEEDS_DECISION` status
predates this disposition. The decision log records the subsequent human decision.

For `effect/phenotype:drug:disease`, the BRIDGE mismatches are BH2_05081, BH2_04897,
BH2_05027 and BH2_04933. UNION reproduces three of these; BH2_05027 fails both.
This is descriptive evidence only. The protocol fixes one construction per relation type;
using a different construction per row would change the science and was not done.

S5 support and S6 equality are different checks. For BH2_06128, all 44 gold drugs are reachable
via Pleural effusion, but PrimeKG reaches 111 drugs. The 67 extras explain why S5 can pass
while S6 fails; the exhaustive candidate search found no alternative hop-2 label.

## Files and reproduction

- `src/cofail_kg/evaluation/relation_mapping.py`: sampling, subset scores, tie preservation,
  construction choice, ambiguity tags and D1 quantities.
- `src/cofail_kg/kg/primekg_index.py`: candidate-label catalog and typed neighbors grouped by label.
- `scripts/06_relation_mapping.py`: validates frozen inputs and S5 evidence; writes four outputs.
- `tests/test_relation_mapping.py`, `tests/test_relation_mapping_script.py`, and additions to
  `tests/test_primekg_index.py`: focused logic, reporting and graph-access tests.
- `results/semantics/relation_mapping_candidates.csv`: every candidate subset's scores.
- `results/semantics/relation_mapping_proposed.json`: samples, skipped rows, selected sets and
  ties, both constructions, mismatch IDs, two full difference examples per best set, and provenance.
- `results/semantics/relation_ambiguity_tags.csv`: proposed tags, with unadopted mappings left blank.
- `results/semantics/d1_report.md`: readable scores, candidate labels and mismatch examples.
- `results/diagnostics/s6_raw_spot_checks.json`, `s6_union_example.json`: independent verification.
- `docs/progress.md`, `docs/decision_log.md`: stage status and computation record.

Run from the repository root:

```powershell
.\venv\Scripts\python.exe -m pytest -q
.\venv\Scripts\python.exe scripts/06_relation_mapping.py --output-dir results/semantics/s6_reproduction
```

Existing output files are never overwritten. The script has no freeze option.
The outputs record calculation commit `2f2caf1`, source-file SHA256s, protocol/rule/S5 hashes,
the BioHopR revision and raw-file hash, KG metadata fingerprint, and UTC time.

## Verification and reporting correction

- Baseline: 85 tests passed. Final suite: **114 tests passed**, with no skips.
- Tests were first observed failing before the corresponding implementation. A temporary
  mutation from `>= 90%` to `> 90%` was caught by the exact-boundary test; source was restored.
- All raw PrimeKG input hashes match the frozen metadata. An independent scan of all
  8,100,498 raw kg.csv rows reproduced eight BRIDGE mismatch checks: two rows per best label
  set in each failing type, including both tied sets in the five-row type. The check built
  its own adjacency and resolved names against raw nodes.csv, without the S6 scorer/index accessors.
- An independent check using the existing `PrimeKGIndex.neighbors` API reproduced BH2_03879:
  query clear cell renal carcinoma, stored bridge Pazopanib, 11 valid bridges, 271 gold targets;
  stored bridge reaches 86, UNION reaches exactly 271.
- The first run at `a7ffef5` incorrectly withheld global D1 whenever any mapping had a tie,
  including a type already known to FAIL. Two regression tests exposed the bookkeeping error.
  Commit `2f2caf1` separates label approval from mechanically determined gate status.
- The original four outputs are preserved in `results/semantics/s6_attempt_01/`. The corrected
  run's candidate CSV is byte-identical, and its complete `per_type` JSON equals the first run.
  No scientific score, sample, selected set, construction or per-type outcome changed.

## Assumptions and engineering choices

No new scientific rule was introduced. Field roles, identity type map, either-direction edges,
reference normalization, subset search, sample size/order, thresholds and tie rules follow
the frozen protocol. No agent outputs are involved.

Routine engineering choices: deterministic size/lexical ordering of subsets (never a scientific
tie-break); integer match-count comparisons; memoized typed neighbor sets; JSON lists in CSV
cells; explicit nulls for unadopted mappings; first two mismatches in validation-sample order
for diagnostics; complete ID differences in JSON with only a short preview in Markdown;
read-only frozen-input verification and exclusive creation of outputs. No new dependency.

`needs_decision` and `PENDING` describe unresolved computation/review, not additional gate rules.
Equal-score label ties do not change threshold calculations; differing tied hop-1 scenarios
can leave a type's D1 outcome unknown. The current real run has no such unknown type outcome.
Unadopted failed types have no accepted R2, so §5.2 cannot supply a tag for them.

## Researcher review remaining

The five-row type's tie is retained unresolved by researcher decision. Inspect the proposed
labels and failing examples. Apply D1's failure
investigation/exclusion procedure, and record any scientific decision. The second runbook
prompt (approval, exclusions and freezing) remains outside this first-prompt execution.
