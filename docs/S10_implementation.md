# S10 — Sampling manifests and agent-input sheets

Completed 2026-10-15 under protocol §8, §9.3 and §3.4, after Gate D2 GREEN.

## 1. Files created or changed

- `src/cofail_kg/data/sampling.py`: deterministic quotas, per-type floors, largest-remainder
  allocation, SHA256 selection, disjoint draws and descriptive T_q size bins.
- `scripts/10_make_samples.py`: verified input loading, artifact generation, idempotent
  publication and write-once sampling hashes.
- `tests/test_sampling.py`: 13 synthetic and artifact tests.
- `data/processed/manifests/{screening,smoke,pilot,expansion}.jsonl`: evaluator manifests,
  each with exactly query_id, relation_type, multiplicity, ambiguity_tag, tq_size_bin.
- `data/agent_inputs/{screening,smoke,pilot,expansion}.jsonl`: agent sheets, each with exactly
  query_id, question_text, start_name, start_id.
- `data/processed/manifests/sampling_report.md`: counts by stratum and shortfalls.
- `data/processed/manifests/sampling_provenance.json`: input/source SHA256s, source commit,
  seed, allocation report and eight output hashes.
- `configs/pilot.yaml`: seed, target/actual sizes, single/multi counts, floors and file paths.
- `configs/frozen_hashes.yaml`: eight SHA256 entries under `manifests`; earlier identity
  values are preserved.
- `.gitattributes`: disable Git text conversion for the eight JSONL artifacts so their
  frozen byte hashes survive Windows checkout.
- `docs/decision_log.md` and `docs/progress.md`: default confirmation and completion.

Run from the repository root:

```powershell
.\venv\Scripts\python.exe scripts/10_make_samples.py
```

## 2. Tests and results

Full suite: **183 passed** (170 existing plus 13 new). Tests cover floors and capacity,
largest-remainder ties, quota transfer, total shortfalls, deterministic SHA256 ordering,
reversed input order, disjoint draws, bin boundaries, invalid population data, exact
artifact field sets, byte-identical reruns, preserved frozen values, and refusal to change
completed artifacts or sampling hashes.

| Set | Queries | Single | Multi | Shortfall | Relation types |
|---|---:|---:|---:|---:|---:|
| Screening | 20 | 5 | 15 | 0 | 6 |
| Smoke | 4 | 1 | 3 | 0 | 2 |
| Pilot | 100 | 25 | 75 | 0 | 9 |
| Expansion reserve | 400 | 100 | 300 | 0 | 9 |

Total: 524 distinct queries (131 single, 393 multi); 6,652 primary-population queries
remain outside these four sets. All six pairwise intersections are empty. Pilot and
expansion each represent all nine passing types; screening/smoke have no per-type floor.

The actual script was run twice. All eight JSONL files, config, report, provenance and
the entire frozen-hash file were byte-identical after the second run. A separate
Fraction-based allocation calculation reproduced every selected query ID; independent
readback checked all agent/manifest schemas, source names/IDs and question text against
the S7 data and KG nodes, all six pairwise overlaps, and all eight frozen hashes.

## 3. Small real example

Pilot query `BH2_00341` appears in the agent sheet as:

```json
{"query_id":"BH2_00341","question_text":"Name all diseases that are related to a gene/protein that is associated with drug 1-Deaza-Adenosine.","start_id":"19259","start_name":"1-Deaza-Adenosine"}
```

It is one of the 25 single-bridge pilot queries. Its evaluator metadata is kept in the
separate pilot manifest. The first ten saved pilot questions were inspected as part of
the required runbook check; question text is copied unchanged.

## 4. Assumptions

The researcher's request to carry out S10 uses the existing 25/75 pilot DEFAULT.
No alternative quota was requested, so that default is retained and confirmed in the
decision log; no scientific rule or protocol text was changed. Gate D2's 7,176-query
primary population and prior type exclusions remain authoritative. Expansion uses the
protocol's reserve target of 400 because enough queries remain.

## 5. Engineering choices beyond the specification

- Use integer divmod remainders for exact allocation and lexical relation-type tie breaks.
  After the floor, quota is no larger than total remaining capacity, so proportional
  shares and remainder seats do not exceed caps. If a hypothetical group quota cannot
  accommodate the required type floors, fail explicitly rather than weaken a floor;
  this case does not occur in the real population.
- Sort saved lines by query ID after selection; membership within each stratum is determined
  solely by SHA256("42" + query_id). A query-ID fallback resolves a hypothetical hash collision.
- Use compact, sorted-key UTF-8 JSONL with LF bytes. Protect these frozen bytes with narrowly
  scoped Git attributes. Report/config layout and human-readable bin strings are descriptive.
- Read canonical starting names directly from the KG node cache. Validate the primary
  CSV hash, S9 gate status, protocol/rule hashes, frozen identity values and S7/node hashes
  before sampling; check target sizes and multiplicity against S7 while building sheets.
- Stage all files before publication; identical existing artifacts are verified without
  rewriting. Mismatching completed artifacts/frozen hashes stop the run. A partial first
  publication can resume with matching bytes. Fill only the empty pilot config placeholder.
- Freeze all eight artifact hashes together using the existing write_once helper. Provenance
  includes current source hashes because the implementation is uncommitted. Rerun verification
  is against the same source/input checkpoint; changed provenance is not silently overwritten.

These are routine engineering choices. No new literature method or scientific threshold
was introduced. Historical S8/S9 outputs remain unchanged. Their recorded frozen-input
dictionaries predate the newly added S10 manifests key.

## 6. Hand inspection and next stage

Review `sampling_report.md` and the first ten lines of `data/agent_inputs/pilot.jsonl`.
The pilot exactly meets 25/75, all nine types are represented, and all agent lines have
only the four allowed fields. No model has been run. S11 (KG tools) is next, when requested.
