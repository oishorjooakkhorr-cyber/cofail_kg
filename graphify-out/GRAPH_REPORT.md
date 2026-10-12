# Graph Report - cofail_kg  (2026-10-12)

## Corpus Check
- cluster-only mode — file stats not available

## Summary
- 527 nodes · 1531 edges · 20 communities (14 shown, 6 thin omitted)
- Extraction: 99% EXTRACTED · 1% INFERRED · 0% AMBIGUOUS · INFERRED: 16 edges (avg confidence: 0.92)
- Token cost: 0 input · 0 output

## Graph Freshness
- Built from commit: `7998bb3b`
- Run `git rev-parse HEAD` and compare to check if the graph is stale.
- Run `graphify update .` after code changes (no API cost).

## Community Hubs (Navigation)
- Community 0
- Community 1
- Community 2
- Community 3
- Community 4
- Community 5
- Community 6
- Community 7
- Community 8
- Community 9
- Community 10
- Community 11
- Community 12
- Community 13

## God Nodes (most connected - your core abstractions)
1. `BioHopR` - 40 edges
2. `Part 1 — Stage map` - 39 edges
3. `PrimeKG` - 39 edges
4. `Underspecified items (now defined)` - 35 edges
5. `CoFail-KG — Frozen Pilot Protocol` - 34 edges
6. `1. Stage-by-stage` - 32 edges
7. `3.2 PrimeKG` - 31 edges
8. `21. Phase 2 — intervention design [PROVISIONAL], frozen at S29` - 28 edges
9. `Part 1 (fixes checked from v1.1)` - 28 edges
10. `Part 2 (full audit of v1.1)` - 27 edges

## Surprising Connections (you probably didn't know these)
- `5. Design choices beyond the specification` --references--> `EdgeConvention`  [INFERRED]
  docs/S4_implementation.md → src/cofail_kg/kg/primekg_index.py
- `EdgeConvention` --references--> `3.2 PrimeKG`  [EXTRACTED]
  src/cofail_kg/kg/primekg_index.py → docs/frozen_pilot_protocol.md
- `test_corrupted_cache_is_rejected()` --uses--> `PrimeKGIndex`  [INFERRED]
  tests/test_primekg_index.py → src/cofail_kg/kg/primekg_index.py
- `Regenerate results` --references--> `main()`  [EXTRACTED]
  README.md → scripts/02_inspect_biohopr.py
- `S3 — BioHopR diagnostics (no PrimeKG needed)` --references--> `main()`  [EXTRACTED]
  docs/pipeline_runbook.md → scripts/03_biohopr_diagnostics.py

## Import Cycles
- None detected.

## Communities (20 total, 6 thin omitted)

### Community 0 - "Community 0"
Cohesion: 0.06
Nodes (110): Code, CLAUDE.md — CoFail-KG, End of every stage — report exactly this, Experimental agents, Integrity, Provenance, Role, Source of truth (+102 more)

### Community 1 - "Community 1"
Cohesion: 0.06
Nodes (80): Data, 2026-10-02 — S2 — BioHopR revision and question-text field fixed, 2026-10-12 — S4 — Correct the release-check interpretation, 2026-10-12 — S4 — PrimeKG fingerprint written, 2026-10-12 — S4 — Release and whitespace wording finalized, 2026-10-12 — S4 — Stage completed, 2026-10-12 — S4 — Surrounding whitespace in name lookup, 2026-10-12 — S4 — Type map finalized (+72 more)

### Community 2 - "Community 2"
Cohesion: 0.06
Nodes (63): argparse, copy, csv, datetime, huggingface_hub, json, pathlib, random (+55 more)

### Community 3 - "Community 3"
Cohesion: 0.09
Nodes (48): Reproducibility, Scope, 2026-10-02 — S1 — Four consistency fixes after the narrow check, D3 — Model selection (S20–S21), D4 — Panel smoke test (S25), Outcomes, 10. KG environment (tools) [FROZEN] design — built at S11, 11. Trace and trace graph [FROZEN] (+40 more)

### Community 4 - "Community 4"
Cohesion: 0.05
Nodes (45): 16.2 Benchmark comparison (secondary), 16.4 Pairwise error agreement, 16. Co-failure metrics [FROZEN], Deterministic stratified sampling, Pairwise error agreement, Part 8 — Phase G: Panel metrics and smoke, S0 — Environment and repository skeleton, S23 — Co-failure metrics (+37 more)

### Community 5 - "Community 5"
Cohesion: 0.10
Nodes (46): pytest, Row, answer_set(), answer_size_table(), _by_size_desc(), duplicate_question_groups(), largest_answers(), list_length() (+38 more)

### Community 6 - "Community 6"
Cohesion: 0.10
Nodes (21): BH2_00204, BH2_00244, BH2_00260, BH2_00712, BH2_00767, BH2_00839, BH2_00912, BH2_01143 (+13 more)

### Community 7 - "Community 7"
Cohesion: 0.16
Nodes (18): FrozenHashConflict, Any, Path, RuntimeError, Write-once store for frozen hashes (protocol §3.4).…, Raised when a frozen key already holds a different value., Return the frozen-hash mapping, or an empty dict if the file does not exist., Write `key: value` to the frozen-hash file unless already present. Returns True… (+10 more)

### Community 8 - "Community 8"
Cohesion: 0.16
Nodes (11): 1. Files created or changed, hashlib, parametrize, subprocess, test_inspection_cli_on_synthetic_cache(), fixture, raw_graph(), test_changed_raw_input_cannot_replace_cache() (+3 more)

### Community 9 - "Community 9"
Cohesion: 0.21
Nodes (8): PrimeKGIndex, DataFrame, Labels, display labels, neighbour types and unique counts (§10)., Number of unique neighbours over all labels (§15)., Load and verify the S4 cache; no BioHopR or evaluation files are read. Lookups…, Return canonical id, source_id, name, type and source (§3.2)., Return every exact normalized match, with optional type filter (§12)., Unique neighbours in numeric canonical-ID order (§3.2, §10).

### Community 10 - "Community 10"
Cohesion: 0.21
Nodes (10): collections, dataclasses, numpy, pandas, pyarrow, pyarrow_parquet, PrimeKG ingestion and inspection (protocol §3.2–§3.4, runbook S4). Raw rows and…, Read-only PrimeKG index (protocol §3.2, §10, §12, §15; runbook S4). Canonical… (+2 more)

### Community 11 - "Community 11"
Cohesion: 0.21
Nodes (12): ndarray, Series, file_hash(), _indices(), load_cache_metadata(), prepare_primekg(), DataFrame, Path (+4 more)

### Community 12 - "Community 12"
Cohesion: 0.18
Nodes (5): cache(), index(), fixture, test_all_traversal_methods_share_the_edge_convention(), test_corrupted_cache_is_rejected()

### Community 13 - "Community 13"
Cohesion: 0.22
Nodes (6): 5. Design choices beyond the specification, EdgeConvention, normalize_name(), Path, Protocol §12: lower-case, NFKC, whitespace collapse; trim approved 2026-10-12., One traversal policy for neighbours, relation summaries and degree (§3.2).

## Knowledge Gaps
- **60 isolated node(s):** `1. Nodes matching "Troglitazone"`, `2. Labels touching it`, `Columns and five example rows`, `Node types`, `Relation and display-label counts` (+55 more)
  These have ≤1 connection - possible missing edges or undocumented components. (Counts symbols only; 149 node(s) total have ≤1 connection when file, concept and rationale nodes are included.)
- **6 thin communities (<3 nodes) omitted from report** — run `graphify query` to explore isolated nodes.

## Suggested Questions
_Questions this graph is uniquely positioned to answer:_

- **Why does `1. Stage-by-stage` connect `Community 4` to `Community 0`, `Community 1`, `Community 3`?**
  _High betweenness centrality (0.109) - this node is a cross-community bridge._
- **Why does `3.1 BioHopR` connect `Community 1` to `Community 0`, `Community 2`, `Community 4`, `Community 5`?**
  _High betweenness centrality (0.101) - this node is a cross-community bridge._
- **Why does `0.4 Terms used throughout` connect `Community 0` to `Community 1`, `Community 2`, `Community 3`, `Community 5`, `Community 11`?**
  _High betweenness centrality (0.097) - this node is a cross-community bridge._
- **What connects `1. Nodes matching "Troglitazone"`, `2. Labels touching it`, `Columns and five example rows` to the rest of the system?**
  _60 weakly-connected nodes found - possible documentation gaps or missing edges._
- **Should `Community 0` be split into smaller, more focused modules?**
  _Cohesion score 0.062385321100917435 - nodes in this community are weakly interconnected._
- **Should `Community 1` be split into smaller, more focused modules?**
  _Cohesion score 0.05730238025271819 - nodes in this community are weakly interconnected._
- **Should `Community 2` be split into smaller, more focused modules?**
  _Cohesion score 0.060041407867494824 - nodes in this community are weakly interconnected._