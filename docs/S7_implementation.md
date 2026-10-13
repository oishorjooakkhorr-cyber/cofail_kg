# S7 — Queries and reference sets

Completed 2026-10-13 under the researcher's instruction to start S7 and ask for research
decisions when needed. Implements runbook S7 and protocol §0.4, §4, §6 and §12 v1.3.3.
No research decision was needed. S8 has not started.

## Files and execution

- `src/cofail_kg/evaluation/reference_sets.py`: groups rows by resolved source node and
  relation type; resolves gold bridges/answers; computes B_q, dead ends, T_q, T_q^{B*},
  G_q and A*_q. Unresolved source rows stay separate. Gold-bridge targets follow §6's
  union over B*_q, even when a resolved gold bridge is not in B_q.
- `scripts/07_build_reference_sets.py`: checks frozen mapping/input hashes and the
  either-direction convention, builds reference tables, and writes a summary with provenance.
- `tests/test_reference_sets.py` and `tests/test_reference_sets_script.py`: synthetic
  graph, grouping, construction, resolution, typed-index and output-protection tests.
- `data/processed/reference_queries.parquet`, `reference_targets.parquet`,
  `reference_summary.json`: evaluator-only S7 outputs. Nothing agent-facing imports them.
- `results/reference_sets/verification.json` and three `inspection_*.json` files:
  independent full-table verification and complete inspection CLI spot-check output.
  `mutation_check.json` records the construction-rule mutation test.
- `docs/progress.md`: current S6 freeze and S7 completion recorded; older S6 computation
  snapshots retained. This implementation report records engineering choices.

Command from repository root: `venv/Scripts/python.exe scripts/07_build_reference_sets.py`.
An existing S7 output causes refusal before computation; use a new `--output-dir` for a rerun.
Real build completed in 73.3 seconds. The source commit recorded in the summary is the
pre-S7 HEAD, a7f38e9; SHA256 values identify the actual new source files executed, which
were uncommitted at computation time.

The frozen mapping SHA256 is
`2d609332b6a4ff48423bd7b2f1cb98d8d2d9cafc2fe80c20f7cee8184b8bb8c0`.
BioHopR revision and KG fingerprint match `configs/frozen_hashes.yaml`; loading PrimeKG
also verifies both cached Parquet tables against frozen cache metadata. Raw data,
normalization, mapping, frozen hashes, protocol and gate rules were not changed.

## Results

All counts below are totals across queries; set sizes are summed per query, not globally
deduplicated node counts. Resolution counts are per distinct raw name within each row/role.

| Count | Overall | BRIDGE | UNION |
|---|---:|---:|---:|
| Relation types | 9 | 8 | 1 |
| Dataset rows | 7,377 | 6,428 | 949 |
| Queries | 7,377 | 6,428 | 949 |
| Unresolved query entities | 0 | 0 | 0 |
| NO_BRIDGE queries | 0 | 0 | 0 |
| SINGLE_BRIDGE queries | 6,673 | 6,343 | 330 |
| MULTI_BRIDGE queries | 704 | 85 | 619 |
| Valid bridges, sum of B_q sizes | 11,398 | 6,541 | 4,857 |
| Dead-end bridges | 2,961 | 434 | 2,527 |
| Question-valid answers, sum of T_q sizes | 276,311 | 138,494 | 137,817 |
| Gold-bridge targets, sum of T_q^{B*} sizes | 211,499 | 137,929 | 73,570 |
| Construction references, sum of G_q sizes | 275,746 | 137,929 | 137,817 |
| BioHopR resolved gold, sum of A*_q sizes | 275,827 | 138,010 | 137,817 |
| Unresolved reference names | 0 | 0 | 0 |
| Disease-suffix resolution occurrences | 57 | 57 | 0 |
| Query/bridge/target records | 481,617 | 138,645 | 342,972 |

The input contains 7,633 rows; the three excluded types account for 256. No real query
contains multiple dataset rows, so runbook's merged-row hand check is inapplicable here;
synthetic tests prove the grouping and union rule. Differences between the gold and
graph sets are retained for S8 validation; S7 does not assign consistency or inclusion labels.

## Tests and verification

Test command: `venv/Scripts/python.exe -m pytest -q`. The initial baseline passed all
119 tests. S7 adds 16 tests covering one/several/shared-target/dead-end/no-valid bridges,
numeric set order, merged rows and gold unions, different types sharing a source,
unresolved source isolation, ambiguous names, disease suffix flags, excluded types,
multiple labels, source exclusion, typed reverse traversal, Parquet round trips including
empty/nested lists, empty table schemas, altered/unfrozen/stale mapping rejection, and
refusal to overwrite existing outputs. Final full suite: **135 passed in 10.64 seconds**.
Review mutation check: inverting the BRIDGE/UNION selection made both construction
tests fail (2 failed, 8 passed); the exact original source bytes were restored afterward.
Focused S7 tests passed again after restoration. Review found no required changes;
agent-facing package code has no reference-data imports.

Independent verification rebuilt typed either-direction adjacency directly from cached
edge tables, without calling S7's traversal functions. Assertions verified every query's
valid/dead-end bridges, per-bridge targets, T_q, T_q^{B*}, G_q, stored set sizes, and gold
entity resolution; question text and row membership were checked against raw BioHopR.
All 7,377 retained rows occur exactly once, and all 481,617 target records are unique.
Source/input hashes were checked against the saved summary.

Required real CLI checks (complete JSON saved under `results/reference_sets/`):

1. SINGLE/BRIDGE BH2_00016: source 18365 has one `drug_protein` gene/protein neighbor,
   bridge 4688. The bridge has one `disease_protein` disease neighbor, target 29969.
   T_q = T_q^{B*} = G_q = A*_q = {29969}.
2. MULTI/UNION BH2_04350: potassium deficiency disease (33679) has seven `indication`
   drug neighbors. Two bridges, 16085 and 17987, have nonempty `drug_effect` targets;
   the other five are dead ends. T_q and G_q both contain 22 targets, exactly matching
   BioHopR gold. This example also verifies that dead ends are counted separately.
3. BRIDGE and UNION construction equalities were checked for every query.

Output SHA256 values and complete example sets appear in `verification.json`.

## Assumptions and engineering choices

Assumptions: S5's verified field roles and the §3.3 identity type map apply; the approved
S6 mapping is authoritative; excluded types stay excluded. The existing reference
normalizer is reused unchanged. No extra matching rule, label or threshold was inferred.

Routine engineering choices beyond the specification:

- Inject graph/name callbacks for small tests; cache repeated name and typed label-set
  lookups within the build. Reuse the existing PrimeKG index and normalization module.
- Sort row IDs lexically (fixed-width §0.4 IDs); sort node IDs numerically; retain question
  text per row and distinct raw gold names for later validation. Save actual reference sets
  alongside counts. `T_q_gold_bridges` represents T_q^{B*}; `A_star_q` represents A*_q.
- Use explicit PyArrow schemas, with native list/struct fields, so empty lists have stable
  types. Store unresolved names with row/role/status, and suffix resolutions with row/role/ID.
- Save counts, UTC execution time, elapsed time, source commit and source/input hashes in
  `reference_summary.json`. These are provenance fields, not new frozen values.
- Serialize all three outputs into temporary files before publishing; reject existing
  outputs. A crash during publication may leave a subset of complete files; a subsequent
  run must use a new output directory, preserving those artifacts.
- Verification uses independent cache-table calculations and existing inspection CLI
  commands. No new literature method or dependency was introduced.

Researcher hand inspection: the two example sets and complete CLI JSON; construction
counts; the Parquet column meanings above. No S7 decision remains. Before S8, the runbook's
older gold-bridge-only wording needs alignment with the already frozen G_q rule, as noted
in `docs/progress.md`.
