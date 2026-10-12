# S4 completion report — 2026-10-12

S4 is complete: ingestion, index, inspection CLI, tests, protocol fields and fingerprint
are finalized. The researcher authorized closure after reviewing the remaining decisions.
The release-check wording was corrected
with researcher authorization on 2026-10-12. The cache was initially prepared without
`--freeze`; the researcher subsequently authorized freezing, and the preparation script
wrote `kg_fingerprint` on 2026-10-12. Its value matches an independent metadata SHA256 check.

## 1. Files created or changed

- `src/cofail_kg/kg/prepare.py`: input hashes, complete endpoint metadata validation,
  Parquet cache, relation counts, seeded reverse-row inspection, write-once metadata.
- `src/cofail_kg/kg/primekg_index.py`: canonical node lookup, normalized name lookup,
  relation summaries, unique neighbours, degree and one configurable edge convention.
- `scripts/04_prepare_primekg.py`, `scripts/inspect_kg.py`: preparation and researcher CLI.
- `tests/test_primekg_prepare.py`, `tests/test_primekg_index.py`, `tests/test_primekg_cli.py`.
- `results/diagnostics/primekg/inspection.md`: columns, five rows, all relation/display-label
  and endpoint-type counts, node-type counts, reverse sample and raw checksums.
- `results/diagnostics/primekg/runtime.json`: real graph verification and measurements.
- `README.md`, `docs/progress.md`, `docs/decision_log.md`, this report.
- `docs/frozen_pilot_protocol.md`, `docs/pipeline_runbook.md`: approved S4 findings and decisions.
- `configs/frozen_hashes.yaml`: machine-written kg_fingerprint.
- Local, gitignored data: extracted `data/raw/primekg/kg.csv` and `nodes.csv`, and generated
  `data/cache/primekg_nodes.parquet`, `primekg_edges.parquet`, `primekg_metadata.json`.

The supplied archive contains `nodes.csv`, rather than the `nodes.tab` mentioned in the
earlier findings. Its 129,375 indices and every parsed ID/name/type/source agree with kg.csv,
including the previously reported quoting case at index 98266. There are no isolated nodes.

## 2. Tests run and their results

- Baseline: 27 passed.
- Final `python -m pytest -q`: **45 passed**, including 18 new S4 tests.
- Closure verification: revalidated raw inputs/cache, independently matched metadata SHA256
  to the frozen fingerprint, preserved the BioHopR revision, and rechecked the 17 direct
  Troglitazone side-effect neighbours. Documentation diff checks passed.
- Tests cover duplicate/reverse/self edges, isolated nodes, ambiguous names, Unicode and
  whitespace normalization, numeric ordering, relation vs display-label filtering, unique
  counts, shared traversal policy, raw preservation, conflicting nodes, cache corruption,
  deterministic independent preparation, repeat preparation, freeze conflicts and both CLIs.
- Mutation check: disabling incoming-edge traversal makes the corresponding test fail.
  The mutation was confined to one Python process; source files were not changed.
- Real validation: all four Troglitazone relation-neighbour sets exactly match an independent
  chunked scan of raw kg.csv.
- Ingestion: 56.13 seconds. Index load: 6.57 seconds in the measured verification run.
  Actual Python process peak working set: 923,447,296 bytes (880.7 MiB), including imports,
  index loading, queries and the independent raw-CSV scan. This is a single-machine observation.

## 3. One small real example run, with its output

```powershell
python scripts/inspect_kg.py neighbors 14813 --relation drug_effect --neighbor-type effect/phenotype
```

The CLI returns all 17 neighbours, sorted numerically. Its first item is node `22262`,
`Edema` (`effect/phenotype`); its last is `85849`, `Poor appetite`.
The output has `count: 17`; no items are truncated. Loading in this CLI run took 5.20 seconds.

Troglitazone is canonical node `14813`, DrugBank ID `DB00197`. Relation summaries:

| Relation | Unique neighbours |
|---|---:|
| drug_drug | 1129 |
| drug_effect | 17 |
| drug_protein | 30 |
| indication | 2 |

## 4. Assumptions made

- Use the supplied archive's kg.csv and distributed nodes.csv as the two raw inputs.
  The archive is retained, and extracted raw bytes are never rewritten by preparation.
- Use the finalized protocol §3.2 convention, traversal in either direction.
  No directional exception has been adopted.
- Keep the existing `data/cache/primekg_release.json`: version 2.1, DOI 10.7910/DVN/IXA7BM,
  download date 2026-10-10. Its date is explicitly recorded as inferred from the archive's
  local timestamps, not independently verified.
- Surrounding-space trimming is a researcher-approved decision, recorded in the decision log.

## 5. Design choices beyond the specification

All of the following are routine engineering choices, with no new literature method:

- Read 250,000 CSV rows per chunk; use pandas/PyArrow and Snappy Parquet compression.
  Preserve every original edge row, including duplicates and both directions.
- Cache canonical indices as 64-bit integers; return decimal strings. Keep source IDs
  separately as `source_id`, and preserve original names exactly.
- Build two sorted edge-position arrays for efficient incident-edge lookup.
  Deduplicate neighbours at query time; all traversals use `EdgeConvention`.
- Return all ambiguous name matches. Apply lower-case, then NFKC, then whitespace collapse
  and the approved trimming. Type filtering is exact.
- Neighbour records include sorted `display_labels` for that specific neighbour and requested
  relation(s). Scientific filtering uses only `relation`, never display labels.
- Unknown node IDs raise `KeyError`; unmatched name/label/type filters yield empty lists.
- Use Python's seeded sampling without replacement for the prescribed 10,000-row check;
  encode dense endpoint positions and relation codes for exact reverse membership checks.
- Exclude timestamps and performance measurements from deterministic metadata; include raw
  hashes and cache-file hashes. Verify cache hashes whenever the index loads.
- Prepare in a temporary directory, refuse differing existing inputs/cache metadata, and use
  explicit `--freeze` for the final write-once fingerprint. A partial publication after an
  interrupted process is reported for inspection rather than silently overwritten.

## 6. Anything the researcher should inspect by hand

1. Review `results/diagnostics/primekg/inspection.md` and the real CLI example above.
2. Canonical IDs were confirmed and frozen in protocol §3.2 with researcher approval on
   2026-10-12: x_index/y_index correspond to node_index, returned as decimal strings and
   ordered numerically. The sampled reverse-storage finding (with its limitation),
   either-direction traversal with no exceptions, and no direction argument in §10 were
   also finalized with researcher approval on 2026-10-12. The v2.1 release choice in §3.2
   is now frozen with researcher approval. The §3.3 identity mapping for drug, disease,
   gene/protein and effect/phenotype was also confirmed and frozen with researcher approval
   on 2026-10-12. The researcher subsequently authorized S4 closure and its local completion
   commit after final verification.
3. Release-check correction completed with researcher authorization on 2026-10-12:
   protocol §3.2 and runbook S4 now use publisher checksums and 17 direct side-effect
   neighbours, explaining 202 as the two-hop answer set. Explicit wording for the approved
   whitespace clarification in §12 was also finalized with authorization on 2026-10-12.
4. Completed with researcher authorization on 2026-10-12:
   `python scripts/04_prepare_primekg.py --freeze` validated the existing raw inputs and cache
   and wrote the fingerprint. Frozen metadata SHA256:
   `bc5d3fd2f12aeb29398fe4684c83d8c65c7bd5c1edf704573322295bdc6b2e95`.
5. Resolved on 2026-10-12: the researcher supplied the full nodes.csv MD5 from the
   publisher's website, `7f9ab4109c54049e819ecd14e15a6038`. A fresh local MD5 calculation
   matches exactly. This is researcher-provided website verification; the automated
   Dataverse metadata request still returned HTTP 403. Local node consistency is fully verified.
6. The prescribed reverse sample covers 28 of the 30 relation labels, all 10,000 matches.
   The rare exposure_cellcomp and exposure_molfunc labels have no sampled rows; the sample
   alone does not prove reverse storage for those labels or for every graph row.
7. The A/B/C answer-construction question remains for before S5. No S5 work was performed.
