# Graph Report - cofail_kg  (2026-10-13)

## Corpus Check
- cluster-only mode — file stats not available

## Summary
- 888 nodes · 2652 edges · 42 communities (30 shown, 12 thin omitted)
- Extraction: 97% EXTRACTED · 3% INFERRED · 0% AMBIGUOUS · INFERRED: 84 edges (avg confidence: 0.87)
- Token cost: 0 input · 0 output

## Graph Freshness
- Built from commit: `5fd5776f`
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
- Community 14
- Community 15
- Community 16
- Community 17
- Community 18
- Community 19
- Community 20
- Community 21
- Community 22
- Community 23
- Community 24
- Community 25
- Community 27
- Community 28
- Community 29
- Community 30
- Community 32

## God Nodes (most connected - your core abstractions)
1. `D1 — Relation-mapping gate (end of S6)` - 85 edges
2. `BioHopR` - 65 edges
3. `PrimeKG` - 55 edges
4. `Accepted relation sets R1 and R2` - 47 edges
5. `12. Normalization [FROZEN]` - 44 edges
6. `Part 1 — Stage map` - 39 edges
7. `Decision Log — CoFail-KG` - 38 edges
8. `3.1 BioHopR` - 38 edges
9. `CoFail-KG — Frozen Pilot Protocol` - 36 edges
10. `3.2 PrimeKG` - 36 edges

## Surprising Connections (you probably didn't know these)
- `S2 — BioHopR loader` --references--> `main()`  [EXTRACTED]
  docs/pipeline_runbook.md → scripts/02_download_biohopr.py
- `Regenerate results` --references--> `main()`  [EXTRACTED]
  README.md → scripts/02_inspect_biohopr.py
- `S3 — BioHopR diagnostics (no PrimeKG needed)` --references--> `main()`  [EXTRACTED]
  docs/pipeline_runbook.md → scripts/03_biohopr_diagnostics.py
- `Regenerate results` --references--> `main()`  [EXTRACTED]
  README.md → scripts/03_biohopr_diagnostics.py
- `1. Files created or changed` --references--> `main()`  [EXTRACTED]
  docs/S4_implementation.md → scripts/04_prepare_primekg.py

## Import Cycles
- None detected.

## Communities (42 total, 12 thin omitted)

### Community 0 - "Community 0"
Cohesion: 0.05
Nodes (131): CLAUDE.md — CoFail-KG, End of every stage — report exactly this, Experimental agents, Integrity, Provenance, Reproducibility, Role, Scope (+123 more)

### Community 1 - "Community 1"
Cohesion: 0.10
Nodes (45): Row, answer_set(), answer_size_table(), _by_size_desc(), duplicate_question_groups(), largest_answers(), list_length(), Any (+37 more)

### Community 2 - "Community 2"
Cohesion: 0.12
Nodes (21): argparse, datetime, huggingface_hub, json, numpy, pandas, pathlib, pyarrow (+13 more)

### Community 3 - "Community 3"
Cohesion: 0.06
Nodes (56): itertools, LabelsBetween, Nbrs, category(), difference(), main(), labels_between(), neighbors() (+48 more)

### Community 4 - "Community 4"
Cohesion: 0.16
Nodes (20): 2026-10-12 — S4 — Correct the release-check interpretation, 2026-10-12 — S4 — PrimeKG fingerprint written, 2026-10-12 — S4 — Type map finalized, 3.2 PrimeKG, 3.3 Type map [FROZEN] at S4, 3. Data, S4 — PrimeKG ingestion and index, S4 findings — PrimeKG release verification and BioHopR answer construction (+12 more)

### Community 5 - "Community 5"
Cohesion: 0.12
Nodes (32): importlib_util, pytest, build_reference_sets(), bridge_targets(), reached(), S7 counts overall and split by frozen answer construction (§5.3, §6)., Return query records and (query, bridge, target) records, using only D1 PASS…, summarize() (+24 more)

### Community 6 - "Community 6"
Cohesion: 0.06
Nodes (20): EdgeConvention, PrimeKGIndex, DataFrame, Path, Labels, display labels, neighbour types and unique counts (§10)., All labels between two node types, with informational display labels (§5.1).…, Typed neighbour IDs grouped by relation under the shared edge convention (§5.1)., Number of unique neighbours over all labels (§15). (+12 more)

### Community 7 - "Community 7"
Cohesion: 0.19
Nodes (16): FrozenHashConflict, Any, Path, RuntimeError, Write-once store for frozen hashes (protocol §3.4).…, Raised when a frozen key already holds a different value., Return the frozen-hash mapping, or an empty dict if the file does not exist., Write `key: value` to the frozen-hash file unless already present. Returns True… (+8 more)

### Community 8 - "Community 8"
Cohesion: 0.21
Nodes (11): collections, fractions, functools, hashlib, Investigate two S6 failures and describe construction mixtures, without rule…, order_key(), S5: field-role verification of BioHopR against PrimeKG (protocol §3.1; runbook…, Per relation type (sorted): [(1-based position, row)] for the first `size` rows. (+3 more)

### Community 9 - "Community 9"
Cohesion: 0.05
Nodes (39): Deterministic stratified sampling, Query grouping, S16 — Answer normalization, Provenance Tracker — CoFail-KG, 1. Stage-by-stage, 2. Phase 2 (after the pilot), 3. Related work only, 5. External code log (+31 more)

### Community 10 - "Community 10"
Cohesion: 0.16
Nodes (21): dataclasses, _classify(), index_finder(), Find, Protocol §12 REFERENCE policy (v1.3.3): resolve a reference name to one PrimeKG…, §12 reference policy, with the v1.3.3 disease-suffix retry., `find` callable over a PrimeKGIndex (exact normalized name, exact type filter)., Resolution (+13 more)

### Community 11 - "Community 11"
Cohesion: 0.11
Nodes (38): Code, Data, Changes that are useful to understand, 2026-10-02 — S2 — BioHopR revision and question-text field fixed, 2026-10-13 — S6 — Approved mapping, constructions and ambiguity tags frozen, BioHopR, Frozen hashes, PrimeKG (+30 more)

### Community 12 - "Community 12"
Cohesion: 0.21
Nodes (28): Amendment 2026-10-12 (S4) — answer construction per relation type (protocol v1.3), 2026-10-12 — S4 — Answer construction: option C, per relation type, 13. Label A — answer status [FROZEN], 4. Query specification (hidden from agents) [FROZEN], 5.1 Relation mapping — procedure [FROZEN], result [TBD@S6], 5.3 Answer construction [FROZEN] rule, result [TBD@S6], 6. Reference sets [FROZEN] — computed at S7, 7.1 Status labels [FROZEN] (+20 more)

### Community 13 - "Community 13"
Cohesion: 0.11
Nodes (28): What changed since v1.0 — one page, Amendment 2026-10-13 (S4) — field-role failure handling (protocol v1.3.2), Amendment 2026-10-13 (S4) — field-role support defined (protocol v1.3.1), Amendment 2026-10-13 (S5) — disease-suffix name fallback (protocol v1.3.3), New ground rule, Precision-only changes (no need to study), 2026-10-12 — S4 — Release and whitespace wording finalized, 2026-10-12 — S4 — Surrounding whitespace in name lookup (+20 more)

### Community 14 - "Community 14"
Cohesion: 0.15
Nodes (25): evaluate(), Per-type pass/fail and the §3.1 failure rule. `records` carry `relation_type`., find(), go(), labels_between(), nbrs(), parametrize, rec() (+17 more)

### Community 15 - "Community 15"
Cohesion: 0.10
Nodes (21): BioHopR inspection — 20 rows, BH2_00204, BH2_00244, BH2_00260, BH2_00712, BH2_00767, BH2_00839, BH2_00912 (+13 more)

### Community 16 - "Community 16"
Cohesion: 0.09
Nodes (49): copy, 0.4 Terms used throughout, S5 field-role preview — per-type summary, main(), S3: BioHopR 2-hop dataset diagnostics (runbook S3; protocol §0.4, §3.1). No…, main(), check_outputs(), load_mapping() (+41 more)

### Community 17 - "Community 17"
Cohesion: 0.14
Nodes (19): ndarray, Series, file_hash(), _indices(), load_cache_metadata(), prepare_primekg(), DataFrame, Path (+11 more)

### Community 18 - "Community 18"
Cohesion: 0.15
Nodes (13): Decision Log — CoFail-KG, 2026-10-02 — S3 — Answer lists compared as sets, 2026-10-12 — S4 — Canonical node ID confirmed, 2026-10-12 — S4 — Edge storage and traversal finalized, 2026-10-12 — S4 — Stage completed, 2026-10-13 — S5 — Field roles verified, 2026-10-13 — S6 — Retain the failed type's unresolved tie, YYYY-MM-DD — Sx — Title (+5 more)

### Community 19 - "Community 19"
Cohesion: 0.24
Nodes (12): analyse_row(), main(), find(), nbrs(), order_key(), preview_rows(), EXPLORATORY, read-only: field-role preview for protocol §3.1, disjoint from the…, Per relation type: [(1-based position, row)] for positions 6-10 only. S5 rows… (+4 more)

### Community 20 - "Community 20"
Cohesion: 0.06
Nodes (80): 2026-10-13 — S6 — Authorize the two remaining exclusions for the time being, 2026-10-13 — S6 — Exclude drug:effect/phenotype:disease after D1 investigation, 2026-10-13 — S6 — First-prompt computation (not a mapping approval), 2026-10-13 — S6 — Remaining failures investigated; mixtures exploratory, D1 — Relation-mapping gate (end of S6), Interpretation flags (reported, not gates), 5.2 Relation-ambiguity tags [FROZEN] rule, computed at S6, 5. Relation mapping and ambiguity tags (+72 more)

### Community 21 - "Community 21"
Cohesion: 0.42
Nodes (11): find(), nbrs(), parametrize, row(), test_ambiguous_status(), test_answer_names_are_a_set(), test_non_adjacent_bridge_is_structural_not_unresolved(), test_partition_and_counts() (+3 more)

### Community 22 - "Community 22"
Cohesion: 0.24
Nodes (10): 3.4 Frozen hashes [FROZEN], check_outputs(), S6 first prompt: propose mappings and report D1 without freezing (protocol §5).…, Reject stale field-role evidence before computing S6 (§3.1, §3.4)., report_md(), describe(), _score(), validate_s5() (+2 more)

### Community 24 - "Community 24"
Cohesion: 0.32
Nodes (4): cell(), git_commit(), main(), S5: field-role verification (protocol §3.1; runbook S5). Reads the pinned…

### Community 25 - "Community 25"
Cohesion: 0.36
Nodes (7): main(), preview(), EXPLORATORY, read-only: " (disease)" suffix preview over all 2-hop rows.…, Return (per type x field counts, per distinct unresolved name details)., status(), summary(), time

### Community 27 - "Community 27"
Cohesion: 0.61
Nodes (7): by(), find(), rows(), test_ambiguous_counted_separately(), test_answer_counts(), test_entity_fields_use_their_own_type(), test_summary_has_label()

### Community 28 - "Community 28"
Cohesion: 0.29
Nodes (7): 0.1 The files and where they go, 0.2 The loop you repeat for every stage, 0.4 When a gate fails, 0.5 Decision-log entry format, 0.6 Time budget (rough, part-time, beginner), 2026-10-14 — S6 — Relation mapping frozen, Part 0 — How to use this runbook

### Community 29 - "Community 29"
Cohesion: 0.29
Nodes (7): BH2_04897 — effect/phenotype:drug:disease, BH2_04907 — effect/phenotype:drug:disease, BH2_05027 — effect/phenotype:drug:disease, BH2_05081 — effect/phenotype:drug:disease, BH2_06120 — disease:effect/phenotype:drug, BH2_06128 — disease:effect/phenotype:drug, Named validation examples

### Community 30 - "Community 30"
Cohesion: 0.50
Nodes (4): cofail_kg, Python, Reproduce, Setup

### Community 32 - "Community 32"
Cohesion: 0.22
Nodes (12): csv, random, re, fmt(), main(), Path, S2: write BioHopR inspection files (protocol §3.1; LEAKY_QUESTION input, §7.1).…, Case-insensitive match not preceded or followed by a word character (\\w). (+4 more)

## Knowledge Gaps
- **77 isolated node(s):** `" (disease)" suffix preview — per-type summary`, `Setup`, `Windows (PowerShell):  venv\Scripts\Activate.ps1`, `Role`, `Integrity` (+72 more)
  These have ≤1 connection - possible missing edges or undocumented components. (Counts symbols only; 215 node(s) total have ≤1 connection when file, concept and rationale nodes are included.)
- **12 thin communities (<3 nodes) omitted from report** — run `graphify query` to explore isolated nodes.

## Suggested Questions
_Questions this graph is uniquely positioned to answer:_

- **Why does `D1 — Relation-mapping gate (end of S6)` connect `Community 20` to `Community 0`, `Community 4`, `Community 9`, `Community 11`, `Community 12`, `Community 13`, `Community 18`?**
  _High betweenness centrality (0.112) - this node is a cross-community bridge._
- **Why does `3.1 BioHopR` connect `Community 13` to `Community 0`, `Community 32`, `Community 2`, `Community 1`, `Community 4`, `Community 8`, `Community 9`, `Community 11`, `Community 12`, `Community 14`, `Community 16`, `Community 18`, `Community 19`, `Community 20`, `Community 22`, `Community 24`?**
  _High betweenness centrality (0.100) - this node is a cross-community bridge._
- **Why does `BioHopR` connect `Community 11` to `Community 0`, `Community 4`, `Community 9`, `Community 12`, `Community 13`, `Community 15`, `Community 18`, `Community 20`, `Community 23`?**
  _High betweenness centrality (0.081) - this node is a cross-community bridge._
- **What connects `" (disease)" suffix preview — per-type summary`, `Setup`, `Windows (PowerShell):  venv\Scripts\Activate.ps1` to the rest of the system?**
  _77 weakly-connected nodes found - possible documentation gaps or missing edges._
- **Should `Community 0` be split into smaller, more focused modules?**
  _Cohesion score 0.05115060378218273 - nodes in this community are weakly interconnected._
- **Should `Community 1` be split into smaller, more focused modules?**
  _Cohesion score 0.10083256244218317 - nodes in this community are weakly interconnected._
- **Should `Community 2` be split into smaller, more focused modules?**
  _Cohesion score 0.12315270935960591 - nodes in this community are weakly interconnected._