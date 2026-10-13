# Graph Report - cofail_kg  (2026-10-13)

## Corpus Check
- cluster-only mode — file stats not available

## Summary
- 840 nodes · 2451 edges · 55 communities (39 shown, 16 thin omitted)
- Extraction: 97% EXTRACTED · 3% INFERRED · 0% AMBIGUOUS · INFERRED: 71 edges (avg confidence: 0.88)
- Token cost: 0 input · 0 output

## Graph Freshness
- Built from commit: `ab67cf15`
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
- Community 31
- Community 32
- Community 34
- Community 35
- Community 36
- Community 37
- Community 38
- Community 39
- Community 40
- Community 43

## God Nodes (most connected - your core abstractions)
1. `D1 — Relation-mapping gate (end of S6)` - 85 edges
2. `BioHopR` - 62 edges
3. `PrimeKG` - 53 edges
4. `Accepted relation sets R1 and R2` - 47 edges
5. `12. Normalization [FROZEN]` - 41 edges
6. `Part 1 — Stage map` - 39 edges
7. `Decision Log — CoFail-KG` - 38 edges
8. `3.1 BioHopR` - 38 edges
9. `CoFail-KG — Frozen Pilot Protocol` - 36 edges
10. `3.2 PrimeKG` - 36 edges

## Surprising Connections (you probably didn't know these)
- `S2 — BioHopR loader` --references--> `main()`  [EXTRACTED]
  docs/pipeline_runbook.md → scripts/02_download_biohopr.py
- `Regenerate results` --references--> `main()`  [EXTRACTED]
  README.md → scripts/02_download_biohopr.py
- `Regenerate results` --references--> `main()`  [EXTRACTED]
  README.md → scripts/02_inspect_biohopr.py
- `S3 — BioHopR diagnostics (no PrimeKG needed)` --references--> `main()`  [EXTRACTED]
  docs/pipeline_runbook.md → scripts/03_biohopr_diagnostics.py
- `Regenerate results` --references--> `main()`  [EXTRACTED]
  README.md → scripts/03_biohopr_diagnostics.py

## Import Cycles
- None detected.

## Communities (55 total, 16 thin omitted)

### Community 0 - "Community 0"
Cohesion: 0.09
Nodes (50): csv, 0.4 Terms used throughout, S3 — BioHopR diagnostics (no PrimeKG needed), Dataset, templates, relation types, Kim, Abdulle & Wu (2025), BioHopR, Findings of ACL 2025, Row, answer_set(), answer_size_table() (+42 more)

### Community 1 - "Community 1"
Cohesion: 0.11
Nodes (25): What changed since v1.0 — one page, Amendment 2026-10-13 (S4) — field-role failure handling (protocol v1.3.2), Amendment 2026-10-13 (S5) — disease-suffix name fallback (protocol v1.3.3), New ground rule, Precision-only changes (no need to study), Decision Log — CoFail-KG, <2026-10-02> — S1 — Protocol and decision rules revised to v1.2 after re-audit, 2026-10-12 — S4 — Stage completed (+17 more)

### Community 2 - "Community 2"
Cohesion: 0.15
Nodes (14): argparse, datetime, huggingface_hub, json, pathlib, S2: download the pinned BioHopR revision to data/raw/biohopr/ (protocol §3.1,…, main(), S3: BioHopR 2-hop dataset diagnostics (runbook S3; protocol §0.4, §3.1). No… (+6 more)

### Community 3 - "Community 3"
Cohesion: 0.07
Nodes (52): 2026-10-02 — S3 — Answer lists compared as sets, 5.1 Relation mapping — procedure [FROZEN], result [TBD@S6], 5. Relation mapping and ambiguity tags, itertools, order_key(), Per relation type (sorted): [(1-based position, row)] for the first `size` rows., relation_types(), s5_sample() (+44 more)

### Community 4 - "Community 4"
Cohesion: 0.10
Nodes (31): Data, 2026-10-12 — S4 — PrimeKG fingerprint written, 2026-10-13 — S5 — Field roles verified, 2026-10-13 — S6 — Approved mapping, constructions and ambiguity tags frozen, 3.4 Frozen hashes [FROZEN], Frozen hashes, 0.1 The files and where they go, Part 3 — Phase B: Data and graph (+23 more)

### Community 5 - "Community 5"
Cohesion: 0.17
Nodes (22): importlib_util, pytest, find(), nbrs(), parametrize, row(), test_ambiguous_status(), test_answer_names_are_a_set() (+14 more)

### Community 6 - "Community 6"
Cohesion: 0.09
Nodes (34): 2026-10-12 — S4 — Release and whitespace wording finalized, 12. Normalization [FROZEN], 4. Query specification (hidden from agents) [FROZEN], S16 — Answer normalization, S7 — Reference sets, Fix at stage (deferred from the S1 audits), Answer set = execute the question's relation pattern over the KG, Departure from BioHopR's single-bridge answer definition (+26 more)

### Community 7 - "Community 7"
Cohesion: 0.19
Nodes (16): FrozenHashConflict, Any, Path, RuntimeError, Write-once store for frozen hashes (protocol §3.4).…, Raised when a frozen key already holds a different value., Return the frozen-hash mapping, or an empty dict if the file does not exist., Write `key: value` to the frozen-hash file unless already present. Returns True… (+8 more)

### Community 8 - "Community 8"
Cohesion: 0.15
Nodes (16): fractions, functools, hashlib, LabelsBetween, Nbrs, category(), difference(), main() (+8 more)

### Community 9 - "Community 9"
Cohesion: 0.09
Nodes (35): CLAUDE.md — CoFail-KG, End of every stage — report exactly this, Integrity, Provenance, Role, Source of truth, 2026-10-02 — S1 — Protocol v1.0 accepted, CoFail-KG — Decision Rules (+27 more)

### Community 10 - "Community 10"
Cohesion: 0.18
Nodes (12): collections, dataclasses, numpy, pandas, pyarrow, pyarrow_parquet, Series, _indices() (+4 more)

### Community 11 - "Community 11"
Cohesion: 0.15
Nodes (25): Code, BioHopR, PrimeKG, 1. Nodes matching "Troglitazone", 2. Labels touching it, 3. Release, 4. Cross-check with BioHopR, 5. Three other drugs with large answer lists (+17 more)

### Community 12 - "Community 12"
Cohesion: 0.16
Nodes (24): evaluate(), Per-type pass/fail and the §3.1 failure rule. `records` carry `relation_type`., find(), go(), labels_between(), nbrs(), parametrize, rec() (+16 more)

### Community 13 - "Community 13"
Cohesion: 0.26
Nodes (22): Amendment 2026-10-12 (S4) — answer construction per relation type (protocol v1.3), Changes that are useful to understand, 2026-10-12 — S4 — Answer construction: option C, per relation type, 13. Label A — answer status [FROZEN], 5.3 Answer construction [FROZEN] rule, result [TBD@S6], 6. Reference sets [FROZEN] — computed at S7, 7.1 Status labels [FROZEN], CONSISTENT query (+14 more)

### Community 14 - "Community 14"
Cohesion: 0.16
Nodes (21): S2 — BioHopR loader, add_row_ids(), BioHopRLoadError, file_sha256(), load_raw_records(), make_row_id(), Any, Path (+13 more)

### Community 15 - "Community 15"
Cohesion: 0.21
Nodes (21): Experimental agents, Reproducibility, D4 — Panel smoke test (S25), D5 — Pre-run freeze check (S26), 19.1 Verification tests (used by Gate D4), 19. Reproducibility [FROZEN], 9.2 Independence and agent count [FROZEN], 9.3 What the agent receives [FROZEN] (+13 more)

### Community 16 - "Community 16"
Cohesion: 0.21
Nodes (18): copy, load_biohopr(), Load the pinned BioHopR 2-hop rows (protocol §0.4, §3.1), in file order. Checks…, fixture_dir(), fixture, skipif, _rec(), test_added_field_clash_raises() (+10 more)

### Community 17 - "Community 17"
Cohesion: 0.10
Nodes (21): Deterministic stratified sampling, S13 — Ollama client, 1. Stage-by-stage, Coding assistant, Context: panels vs independent-voting null, Frozen protocol and gates before data, Function-based graph tools incl. neighbor listing and neighbor counts, Local model serving (+13 more)

### Community 18 - "Community 18"
Cohesion: 0.10
Nodes (21): BioHopR inspection — 20 rows, BH2_00204, BH2_00244, BH2_00260, BH2_00712, BH2_00767, BH2_00839, BH2_00912 (+13 more)

### Community 19 - "Community 19"
Cohesion: 0.22
Nodes (19): 2026-10-02 — S1 — Four consistency fixes after the narrow check, D2 — Mapping confirmation and dataset feasibility (S9), D8 — Final scale decision (S37), 14.2 Primary path and reason codes (PATH_INVALID only), 14.3 Hop-1 status, 14. Label B — path status, reason codes, hop-1 status [FROZEN], 15. Per-agent metrics [FROZEN], 7.2 Inclusion (+11 more)

### Community 20 - "Community 20"
Cohesion: 0.06
Nodes (81): 2026-10-13 — S6 — Authorize the two remaining exclusions for the time being, 2026-10-13 — S6 — Exclude drug:effect/phenotype:disease after D1 investigation, 2026-10-13 — S6 — First-prompt computation (not a mapping approval), 2026-10-13 — S6 — Remaining failures investigated; mixtures exploratory, D1 — Relation-mapping gate (end of S6), Interpretation flags (reported, not gates), 5.2 Relation-ambiguity tags [FROZEN] rule, computed at S6, Accepted relation sets R1 and R2 (+73 more)

### Community 21 - "Community 21"
Cohesion: 0.22
Nodes (19): Quantities (pilot queries × 4 agents; latest attempts, §19), 16.1 Answer level (primary), 16.2 Benchmark comparison (secondary), 16.3 Path level (secondary), 16.4 Pairwise error agreement, 16. Co-failure metrics [FROZEN], 17. Chance baselines [FROZEN], Answer co-failure CF3 and CF4 (+11 more)

### Community 22 - "Community 22"
Cohesion: 0.32
Nodes (16): Scope, 2026-10-02 — S1 — Protocol and decision rules revised to v1.1 after audit, D6 — Pilot decision (S29), D7 — Expansion and intervention feasibility (after S30), Outcomes, 21. Phase 2 — intervention design [PROVISIONAL], frozen at S29, Phase 2 intervention design, Part 10 — Phase I: After the pilot (provisional) (+8 more)

### Community 23 - "Community 23"
Cohesion: 0.17
Nodes (9): PrimeKGIndex, DataFrame, Labels, display labels, neighbour types and unique counts (§10)., All labels between two node types, with informational display labels (§5.1).…, Typed neighbour IDs grouped by relation under the shared edge convention (§5.1)., Number of unique neighbours over all labels (§15)., Load and verify the S4 cache; no BioHopR or evaluation files are read. Lookups…, Return canonical id, source_id, name, type and source (§3.2). (+1 more)

### Community 24 - "Community 24"
Cohesion: 0.13
Nodes (7): cache(), index(), fixture, test_all_traversal_methods_share_the_edge_convention(), test_corrupted_cache_is_rejected(), fixture, raw_graph()

### Community 25 - "Community 25"
Cohesion: 0.21
Nodes (14): D3 — Model selection (S20–S21), 9.1 Runtime settings, Part 11 — Troubleshooting, Part 6 — Phase E: Evaluation core, Part 7 — Phase F: Models, S18 — Label B, reason codes, hop-1 status, S19 — Per-agent metrics, S20 — Model screening (+6 more)

### Community 27 - "Community 27"
Cohesion: 0.23
Nodes (13): Amendment 2026-10-13 (S4) — field-role support defined (protocol v1.3.1), 2026-10-02 — S2 — BioHopR revision and question-text field fixed, 2026-10-12 — S4 — Canonical node ID confirmed, 2026-10-12 — S4 — Correct the release-check interpretation, 2026-10-12 — S4 — Type map finalized, 3.1 BioHopR, 3.2 PrimeKG, 3.3 Type map [FROZEN] at S4 (+5 more)

### Community 28 - "Community 28"
Cohesion: 0.24
Nodes (12): analyse_row(), main(), find(), nbrs(), order_key(), preview_rows(), EXPLORATORY, read-only: field-role preview for protocol §3.1, disjoint from the…, Per relation type: [(1-based position, row)] for positions 6-10 only. S5 rows… (+4 more)

### Community 29 - "Community 29"
Cohesion: 0.24
Nodes (12): file_hash(), load_cache_metadata(), prepare_primekg(), Path, Verify cached bytes against the machine-written metadata (§3.4)., Build the S4 cache; refuse changed inputs, conflicting nodes, or overwrites.…, parametrize, test_changed_raw_input_cannot_replace_cache() (+4 more)

### Community 30 - "Community 30"
Cohesion: 0.33
Nodes (11): 2026-10-12 — S4 — Edge storage and traversal finalized, 10. KG environment (tools) [FROZEN] design — built at S11, 11. Trace and trace graph [FROZEN], get_neighbors tool, inspect_entity tool, Trace graph TG_i, Part 5 — Phase D: Agent system, S11 — KG tools (+3 more)

### Community 31 - "Community 31"
Cohesion: 0.33
Nodes (9): check_outputs(), main(), S6 first prompt: propose mappings and report D1 without freezing (protocol §5).…, Reject stale field-role evidence before computing S6 (§3.1, §3.4)., report_md(), describe(), _score(), validate_s5() (+1 more)

### Community 32 - "Community 32"
Cohesion: 0.24
Nodes (11): random, re, fmt(), main(), Path, S2: write BioHopR inspection files (protocol §3.1; LEAKY_QUESTION input, §7.1).…, Case-insensitive match not preceded or followed by a word character (\\w)., Show a value as JSON in a code span so whitespace and newlines stay visible. (+3 more)

### Community 35 - "Community 35"
Cohesion: 0.36
Nodes (7): main(), preview(), EXPLORATORY, read-only: " (disease)" suffix preview over all 2-hop rows.…, Return (per type x field counts, per distinct unresolved name details)., status(), summary(), typing

### Community 36 - "Community 36"
Cohesion: 0.29
Nodes (7): Provenance Tracker — CoFail-KG, 2. Phase 2 (after the pilot), 3. Related work only, 5. External code log, 6. AI-assistance log (for the thesis disclosure), Repo URL, License

### Community 37 - "Community 37"
Cohesion: 0.29
Nodes (7): BH2_04897 — effect/phenotype:drug:disease, BH2_04907 — effect/phenotype:drug:disease, BH2_05027 — effect/phenotype:drug:disease, BH2_05081 — effect/phenotype:drug:disease, BH2_06120 — disease:effect/phenotype:drug, BH2_06128 — disease:effect/phenotype:drug, Named validation examples

### Community 38 - "Community 38"
Cohesion: 0.33
Nodes (3): EdgeConvention, Path, One traversal policy for neighbours, relation summaries and degree (§3.2).

### Community 39 - "Community 39"
Cohesion: 0.50
Nodes (4): ndarray, DataFrame, Sample stored rows; reverse identity uses relation, never display label (§0.4)., _reverse_sample()

### Community 40 - "Community 40"
Cohesion: 0.21
Nodes (8): cell(), git_commit(), main(), S5: field-role verification (protocol §3.1; runbook S5). Reads the pinned…, summary_md(), type_row_counts(), subprocess, test_type_row_counts()

### Community 43 - "Community 43"
Cohesion: 0.50
Nodes (4): cofail_kg, Python, Reproduce, Setup

## Knowledge Gaps
- **77 isolated node(s):** `" (disease)" suffix preview — per-type summary`, `Setup`, `Windows (PowerShell):  venv\Scripts\Activate.ps1`, `Role`, `Integrity` (+72 more)
  These have ≤1 connection - possible missing edges or undocumented components. (Counts symbols only; 212 node(s) total have ≤1 connection when file, concept and rationale nodes are included.)
- **16 thin communities (<3 nodes) omitted from report** — run `graphify query` to explore isolated nodes.

## Suggested Questions
_Questions this graph is uniquely positioned to answer:_

- **Why does `D1 — Relation-mapping gate (end of S6)` connect `Community 20` to `Community 1`, `Community 3`, `Community 4`, `Community 6`, `Community 9`, `Community 11`, `Community 13`, `Community 17`, `Community 19`, `Community 21`, `Community 22`, `Community 27`?**
  _High betweenness centrality (0.121) - this node is a cross-community bridge._
- **Why does `3.1 BioHopR` connect `Community 27` to `Community 0`, `Community 1`, `Community 2`, `Community 4`, `Community 6`, `Community 8`, `Community 11`, `Community 12`, `Community 13`, `Community 14`, `Community 16`, `Community 17`, `Community 19`, `Community 20`, `Community 21`, `Community 28`, `Community 31`, `Community 32`, `Community 40`?**
  _High betweenness centrality (0.112) - this node is a cross-community bridge._
- **Why does `BioHopR` connect `Community 11` to `Community 0`, `Community 1`, `Community 34`, `Community 3`, `Community 4`, `Community 6`, `Community 13`, `Community 14`, `Community 15`, `Community 17`, `Community 18`, `Community 20`, `Community 21`, `Community 27`?**
  _High betweenness centrality (0.083) - this node is a cross-community bridge._
- **What connects `" (disease)" suffix preview — per-type summary`, `Setup`, `Windows (PowerShell):  venv\Scripts\Activate.ps1` to the rest of the system?**
  _77 weakly-connected nodes found - possible documentation gaps or missing edges._
- **Should `Community 0` be split into smaller, more focused modules?**
  _Cohesion score 0.0889894419306184 - nodes in this community are weakly interconnected._
- **Should `Community 1` be split into smaller, more focused modules?**
  _Cohesion score 0.10666666666666667 - nodes in this community are weakly interconnected._
- **Should `Community 3` be split into smaller, more focused modules?**
  _Cohesion score 0.07017543859649122 - nodes in this community are weakly interconnected._