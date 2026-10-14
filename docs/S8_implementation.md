# S8 — Query validation (protocol §7.1, v1.3.3)

Completed 2026-10-15. Code: `src/cofail_kg/evaluation/query_validation.py`,
`scripts/08_validate_queries.py`. Outputs: `results/diagnostics/query_validation.csv`,
`results/diagnostics/query_validation_summary.json`. Nothing excluded; no θ chosen.

## Inputs and checks
- `results/semantics/relation_mapping.json`: frozen hash, `frozen: true` and D1 PROCEED
  (S7's `load_mapping`).
- `results/semantics/relation_mapping_proposed.json`: SHA256 equal to the mapping's
  `provenance.proposal_sha256`. It is the source of the S6 validation-sample row IDs (§5.1) and the
  ambiguity tags (§5.2). Its R1, R2 and construction must equal the frozen mapping, and its tags must
  equal `relation_ambiguity_tags.csv`.
  The working copy is CRLF (git `core.autocrlf=true`). Its raw SHA256 is `6f92c380…`, but the
  committed blob and the LF-normalized working file both hash to the recorded `29821503…`. The script
  accepts either hash. It prints a note and writes `proposal_sha256_match: lf_normalized` to the
  provenance.
- `data/processed/reference_summary.json` provenance must equal the frozen BioHopR revision,
  kg_fingerprint and mapping hash.
- `data/cache/primekg_metadata.json` SHA256 must equal `kg_fingerprint`. `primekg_nodes.parquet`
  SHA256 must equal the metadata `cache_sha256`. Node-type counts must equal `node_type_counts`; these
  are the saturation denominators. Node names come from this file and feed LEAKY_QUESTION source (b).

## LEAKY_QUESTION interpretation (researcher decision, 2026-10-15)
A query is leaky if any of its question texts contains, as a whole word or phrase, any name of at
least 4 characters from either source:
- (a) the BioHopR `hop1` or `answer` strings of any of its rows, resolved or not;
- (b) the PrimeKG names of its resolved gold bridges or gold answers.

Matching rules:
- Names and question texts are both normalized with the §12 `normalize_name`.
- Length is measured after normalization.
- A match must not be preceded or followed by a Unicode `\w` character.

Recorded in `docs/decision_log.md` (2026-10-15, S8), with a correction entry for the data seen
before deciding.

## Real-run results (7,377 queries, all single-row)
| | Queries | CONSISTENT | INCONSISTENT |
|---|---|---|---|
| Overall | 7,377 | 7,362 | 15 |
| BRIDGE | 6,428 | 6,413 | 15 |
| UNION | 949 | 949 | 0 |
| effect/phenotype:disease:drug | 546 | 534 | 12 |
| gene/protein:drug:disease | 462 | 459 | 3 |
| the other seven types | 6,369 | 6,369 | 0 |

- Primary reason is GOLD_MISSING_FROM_KG for all 15 INCONSISTENT queries; 3 of them also have
  EXTRA_TARGETS.
- No query has QUERY_NOT_FOUND, QUESTION_TEXT_MISMATCH, BRIDGE_NOT_FOUND, GOLD_BRIDGE_NOT_VALID or
  GOLD_UNMAPPED, and no code is NA.
- Multiplicity: 6,673 SINGLE_BRIDGE and 704 MULTI_BRIDGE (0 NO_BRIDGE). 800 queries have at least one
  dead-end bridge.
- Saturation share: p50 0.0008, p90 0.0064, p99 0.0208, max 0.0515. No value is NA.
- LEAKY_QUESTION: 186 queries, all CONSISTENT. 66 match a bridge name and 120 match an answer name.
  Sources (a) and (b) always agree; no query is leaky through only one of them.
- Queries containing an S6 validation-sample row: 270, which is 30 for each of the 9 types.

## Hand checks
- **The 12 effect/phenotype:disease:drug queries** are all MULTI_BRIDGE. A*_q is larger than
  G_q = T_q^{B*}, and every missing gold answer is in T_q, i.e. it is reached through another valid
  bridge. Example: BH2_05881 has |A*| 14 and |G| 1, missing Lovastatin, Fenofibrate, …. These rows
  follow the UNION pattern although the type adopted BRIDGE. This is a real discrepancy under §7.1.
- **The 3 gene/protein:drug:disease queries** (BH2_05099, BH2_05194, BH2_05353):
  - The BioHopR answer "acute lymphoblastic leukemia" resolves by exact match to disease 35852 "acute
    lymphoblastic leukemia".
  - The graph reaches 33621 "acute lymphoblastic leukemia (disease)" instead.
  - §12 retries the suffix only when there is no match, so this cannot be resolved under the frozen
    rule. It is a real discrepancy, not a code bug.
- **CONSISTENT MULTI_BRIDGE queries:** A*_q equals G_q (e.g. BH2_03612, UNION, 23 bridges). Saturation
  equals tq_size / 15,311 effect/phenotype nodes.
- **Leaky queries:** in all 186, every match lies inside the query entity's own name as it appears in
  the question text. Examples: drug "CCR5 mAb" contains its bridge "CCR5"; disease "Japanese spotted
  fever" contains the answer "Fever"; "Burkitt lymphoma" is the query entity and also an answer. Four
  queries did not show this in the automatic check only because the BioHopR query name carries a
  " (disease)" suffix that the question drops (e.g. "vitamin A deficiency" contains "vitamin A").

## Design choices beyond the specification
| Choice | Kind |
|---|---|
| Codes written as TRUE/FALSE/NA; `primary_reason` = `NONE` for CONSISTENT | routine engineering |
| The five conditions computed separately and checked against the code table (raise on disagreement); CONSISTENT ⇒ A*_q ⊆ T_q asserted | routine engineering |
| G_q recomputed from T_q^{B*}/T_q and compared with stored G_q (raise on drift) | routine engineering |
| QUESTION_TEXT_MISMATCH = exact string inequality (no normalization) | routine engineering (literal reading of "identical") |
| Saturation share = NA when `s` does not resolve (T_q undefined); denominators from the fingerprinted `node_type_counts` | routine engineering |
| Validation-sample IDs and tags read from the hash-linked S6 proposal, not recomputed | routine engineering |
| Proposal hash accepted after CRLF→LF normalization only; recorded in provenance | routine engineering |
| LEAKY matching details (normalization, `\w` boundaries, both name sources) | researcher decision this session; whole-word regex test is routine engineering |
| No-overwrite, staged publish, CSV sorted by query_id, `;`-joined lists, `repr` floats | routine engineering |
