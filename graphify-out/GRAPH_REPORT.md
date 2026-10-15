# Graph Report - cofail_kg  (2026-10-15)

## Corpus Check
- cluster-only mode — file stats not available

## Summary
- 1142 nodes · 3527 edges · 64 communities (43 shown, 21 thin omitted)
- Extraction: 97% EXTRACTED · 3% INFERRED · 0% AMBIGUOUS · INFERRED: 97 edges (avg confidence: 0.87)
- Token cost: 0 input · 0 output

## Graph Freshness
- Built from commit: `e7c8d669`
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
- Community 33
- Community 34
- Community 35
- Community 36
- Community 37
- Community 38
- Community 39
- Community 40
- Community 43
- Community 49
- Community 50
- Community 51
- Community 52

## God Nodes (most connected - your core abstractions)
1. `D1 — Relation-mapping gate (end of S6)` - 105 edges
2. `BioHopR` - 86 edges
3. `PrimeKG` - 68 edges
4. `12. Normalization [FROZEN]` - 59 edges
5. `Accepted relation sets R1 and R2` - 51 edges
6. `Decision Log — CoFail-KG` - 47 edges
7. `3.1 BioHopR` - 45 edges
8. `CONSISTENT query` - 45 edges
9. `Agent independence` - 43 edges
10. `3.2 PrimeKG` - 42 edges

## Surprising Connections (you probably didn't know these)
- `Inputs and checks` --references--> `load_mapping()`  [INFERRED]
  results/diagnostics/s8_github_checkpoint/docs/S8_implementation.md → scripts/07_build_reference_sets.py
- `check()` --references--> `7.2 Inclusion`  [EXTRACTED]
  scripts/09_decision_evidence.py → docs/frozen_pilot_protocol.md
- `3. One small real example run, with its output` --references--> `main()`  [EXTRACTED]
  docs/S4_implementation.md → scripts/inspect_kg.py
- `LEAKY_QUESTION interpretation (researcher decision, 2026-10-15)` --references--> `normalize_name()`  [INFERRED]
  results/diagnostics/s8_github_checkpoint/docs/S8_implementation.md → src/cofail_kg/kg/primekg_index.py
- `load_nodes()` --references--> `3.2 PrimeKG`  [EXTRACTED]
  results/diagnostics/s8_github_checkpoint/scripts/08_validate_queries.py → docs/frozen_pilot_protocol.md

## Import Cycles
- None detected.

## Communities (64 total, 21 thin omitted)

### Community 0 - "Community 0"
Cohesion: 0.09
Nodes (32): collections, math, analyse_row(), main(), find(), nbrs(), order_key(), preview_rows() (+24 more)

### Community 1 - "Community 1"
Cohesion: 0.10
Nodes (51): Amendment 2026-10-12 (S4) — answer construction per relation type (protocol v1.3), 2026-10-12 — S4 — Answer construction: option C, per relation type, 13. Label A — answer status [FROZEN], 4. Query specification (hidden from agents) [FROZEN], 5.1 Relation mapping — procedure [FROZEN], result [TBD@S6], 5.3 Answer construction [FROZEN] rule, result [TBD@S6], 6. Reference sets [FROZEN] — computed at S7, 7.1 Status labels [FROZEN] (+43 more)

### Community 2 - "Community 2"
Cohesion: 0.14
Nodes (15): argparse, huggingface_hub, json, pathlib, S2: download the pinned BioHopR revision to data/raw/biohopr/ (protocol §3.1,…, S3: BioHopR 2-hop dataset diagnostics (runbook S3; protocol §0.4, §3.1). No…, S4 cache preparation (protocol §3.2–§3.4). Run without --freeze while S4…, cell() (+7 more)

### Community 3 - "Community 3"
Cohesion: 0.17
Nodes (18): 5.2 Relation-ambiguity tags [FROZEN] rule, computed at S6, 5. Relation mapping and ambiguity tags, Assumptions and engineering choices, itertools, relation_types(), ambiguity_tag(), _hop2_scores(), _neighbors() (+10 more)

### Community 4 - "Community 4"
Cohesion: 0.09
Nodes (24): 2026-10-12 — S4 — Stage completed, 2026-10-15 — Publishing through S10 — Reconcile upstream S8 checkpoint, Agent independence, 2. Tests run and their results, 3. One small real example run, with its output, 4. Assumptions made, 5. Design choices beyond the specification, 6. Anything the researcher should inspect by hand (+16 more)

### Community 5 - "Community 5"
Cohesion: 0.18
Nodes (27): pytest, build_reference_sets(), bridge_targets(), reached(), Return query records and (query, bridge, target) records, using only D1 PASS…, build(), find(), graph() (+19 more)

### Community 6 - "Community 6"
Cohesion: 0.09
Nodes (49): Code, Data, Amendment 2026-10-13 (S5) — disease-suffix name fallback (protocol v1.3.3), Changes that are useful to understand, 2026-10-02 — S2 — BioHopR revision and question-text field fixed, 2026-10-12 — S4 — PrimeKG fingerprint written, 2026-10-12 — S4 — Type map finalized, 2026-10-13 — S6 — Approved mapping, constructions and ambiguity tags frozen (+41 more)

### Community 7 - "Community 7"
Cohesion: 0.16
Nodes (20): jsonl(), main(), make_artifacts(), publish(), S10 manifests and isolated agent sheets, protocol §8, §9.3 and §3.4., FrozenHashConflict, Any, Path (+12 more)

### Community 8 - "Community 8"
Cohesion: 0.15
Nodes (26): hashlib, allocate_types(), draw_samples(), Deterministic disjoint query sampling, protocol §8; evaluator-only metadata., Apply per-type floors then largest remainders on remaining availability (§8.2)., size_bin(), find(), nbrs() (+18 more)

### Community 9 - "Community 9"
Cohesion: 0.09
Nodes (47): expansion — strata, pilot — strata, S10 — Sampling report, screening — strata, smoke — strata, S9 — Primary population and Gate D2, 2026-10-15 — S8 — Correction: data seen before the LEAKY_QUESTION interpretation, 2026-10-15 — S9 — Primary population and Gate D2 GREEN (+39 more)

### Community 10 - "Community 10"
Cohesion: 0.17
Nodes (19): dataclasses, _classify(), index_finder(), Find, Protocol §12 REFERENCE policy (v1.3.3): resolve a reference name to one PrimeKG…, §12 reference policy, with the v1.3.3 disease-suffix retry., `find` callable over a PrimeKGIndex (exact normalized name, exact type filter)., Resolution (+11 more)

### Community 11 - "Community 11"
Cohesion: 0.10
Nodes (45): Row, answer_set(), answer_size_table(), _by_size_desc(), duplicate_question_groups(), largest_answers(), list_length(), Any (+37 more)

### Community 12 - "Community 12"
Cohesion: 0.08
Nodes (43): Decision Log — CoFail-KG, 2026-10-12 — S4 — Release and whitespace wording finalized, 2026-10-12 — S4 — Surrounding whitespace in name lookup, 2026-10-13 — S5 — Field roles verified, 2026-10-13 — S6 — Authorize the two remaining exclusions for the time being, 2026-10-13 — S6 — Exclude drug:effect/phenotype:disease after D1 investigation, 2026-10-13 — S6 — Remaining failures investigated; mixtures exploratory, 2026-10-15 — S8 — LEAKY_QUESTION interpretation of §7.1 (+35 more)

### Community 13 - "Community 13"
Cohesion: 0.05
Nodes (43): Files and reproduction, check_outputs(), main(), find(), Generate evaluator-only S8 evidence (protocol §7.1), without deciding S9…, write_outputs(), S8 query labels and S9 evidence, protocol §6–§7.1; no inclusion decisions., summarize() (+35 more)

### Community 14 - "Community 14"
Cohesion: 0.17
Nodes (22): What changed since v1.0 — one page, Amendment 2026-10-13 (S4) — field-role failure handling (protocol v1.3.2), Amendment 2026-10-13 (S4) — field-role support defined (protocol v1.3.1), New ground rule, Precision-only changes (no need to study), 2026-10-12 — S4 — Canonical node ID confirmed, 2026-10-12 — S4 — Correct the release-check interpretation, 2026-10-12 — S4 — Edge storage and traversal finalized (+14 more)

### Community 15 - "Community 15"
Cohesion: 0.07
Nodes (42): 16.1 Answer level (primary), 16.2 Benchmark comparison (secondary), 16.3 Path level (secondary), 16.4 Pairwise error agreement, 16. Co-failure metrics [FROZEN], Answer co-failure CF3 and CF4, Deterministic stratified sampling, Episode status (+34 more)

### Community 16 - "Community 16"
Cohesion: 0.11
Nodes (38): copy, main(), add_row_ids(), BioHopRLoadError, load_biohopr(), load_raw_records(), make_row_id(), Any (+30 more)

### Community 17 - "Community 17"
Cohesion: 0.10
Nodes (34): CLAUDE.md — CoFail-KG, End of every stage — report exactly this, Integrity, Provenance, Role, Source of truth, 2026-10-02 — S1 — Protocol v1.0 accepted, CoFail-KG — Decision Rules (+26 more)

### Community 18 - "Community 18"
Cohesion: 0.13
Nodes (30): pandas, parametrize, query(), A CONSISTENT single-bridge BRIDGE-type S7 record; `changes` override fields., fixture, s6_files(), test_end_to_end_outputs_and_no_overwrite(), test_node_cache_checked_against_fingerprint_and_metadata() (+22 more)

### Community 19 - "Community 19"
Cohesion: 0.11
Nodes (24): ndarray, Series, file_hash(), _indices(), load_cache_metadata(), prepare_primekg(), DataFrame, Path (+16 more)

### Community 20 - "Community 20"
Cohesion: 0.05
Nodes (78): 2026-10-13 — S6 — First-prompt computation (not a mapping approval), 2026-10-13 — S6 — Retain the failed type's unresolved tie, D1 — Relation-mapping gate (end of S6), Interpretation flags (reported, not gates), Accepted relation sets R1 and R2, S6 first prompt — computed, not frozen, Researcher review remaining, Result (+70 more)

### Community 21 - "Community 21"
Cohesion: 0.13
Nodes (22): 3.4 Frozen hashes [FROZEN], io, check_outputs(), check_reference_summary(), csv_text(), load_nodes(), load_proposal(), main() (+14 more)

### Community 22 - "Community 22"
Cohesion: 0.16
Nodes (24): evaluate(), Per-type pass/fail and the §3.1 failure rule. `records` carry `relation_type`., find(), go(), labels_between(), nbrs(), parametrize, rec() (+16 more)

### Community 23 - "Community 23"
Cohesion: 0.12
Nodes (21): 2026-10-02 — S3 — Answer lists compared as sets, 0.4 Terms used throughout, 3.3 Type map [FROZEN] at S4, Part 3 — Phase B: Data and graph, S2 — BioHopR loader, S3 — BioHopR diagnostics (no PrimeKG needed), Fix at stage (deferred from the S1 audits), Next action (+13 more)

### Community 24 - "Community 24"
Cohesion: 0.20
Nodes (22): Experimental agents, D8 — Final scale decision (S37), 0.1 Status tags, 14.1 Label B, 14.2 Primary path and reason codes (PATH_INVALID only), 14.3 Hop-1 status, 14. Label B — path status, reason codes, hop-1 status [FROZEN], 15. Per-agent metrics [FROZEN] (+14 more)

### Community 25 - "Community 25"
Cohesion: 0.10
Nodes (21): BioHopR inspection — 20 rows, BH2_00204, BH2_00244, BH2_00260, BH2_00712, BH2_00767, BH2_00839, BH2_00912 (+13 more)

### Community 27 - "Community 27"
Cohesion: 0.22
Nodes (17): find(), neighbors(), row(), run_score(), finder(), test_any_unresolved_answer_counts_as_mismatch_even_if_resolved_ids_equal(), test_both_pass_adopts_bridge_and_unselected_labels_only_change_tag(), test_d1_independent_failure_rules() (+9 more)

### Community 28 - "Community 28"
Cohesion: 0.28
Nodes (18): Scope, 2026-10-02 — S1 — Protocol and decision rules revised to v1.1 after audit, D6 — Pilot decision (S29), D7 — Expansion and intervention feasibility (after S30), Outcomes, 17. Chance baselines [FROZEN], 21. Phase 2 — intervention design [PROVISIONAL], frozen at S29, Phase 2 intervention design (+10 more)

### Community 29 - "Community 29"
Cohesion: 0.20
Nodes (13): datetime, load_records(), main(), markdown_table(), S9 part 1 decision tables, D2 steps 1–2. No threshold choice or feasibility…, write_outputs(), check(), check_outputs() (+5 more)

### Community 30 - "Community 30"
Cohesion: 0.15
Nodes (15): <2026-10-02> — S1 — Protocol and decision rules revised to v1.2 after re-audit, Query grouping, Within-query chance baselines, Provenance Tracker — CoFail-KG, 2. Phase 2 (after the pilot), 3. Related work only, 4. Own contributions (claim these; run a literature search on each before claiming), 5. External code log (+7 more)

### Community 31 - "Community 31"
Cohesion: 0.31
Nodes (14): Reproducibility, 2026-10-02 — S1 — Four consistency fixes after the narrow check, D4 — Panel smoke test (S25), Quantities (pilot queries × 4 agents; latest attempts, §19), 11. Trace and trace graph [FROZEN], 19. Reproducibility [FROZEN], 9.5 Episode status [FROZEN], Checkpoint and resume (+6 more)

### Community 32 - "Community 32"
Cohesion: 0.22
Nodes (12): csv, random, re, fmt(), main(), Path, S2: write BioHopR inspection files (protocol §3.1; LEAKY_QUESTION input, §7.1).…, Case-insensitive match not preceded or followed by a word character (\\w). (+4 more)

### Community 33 - "Community 33"
Cohesion: 0.19
Nodes (13): 10. KG environment (tools) [FROZEN] design — built at S11, get_neighbors tool, inspect_entity tool, Part 5 — Phase D: Agent system, S11 — KG tools, S13 — Ollama client, S32 — Surgery overlay, Function-based graph tools incl. neighbor listing and neighbor counts (+5 more)

### Community 34 - "Community 34"
Cohesion: 0.19
Nodes (11): functools, category(), difference(), main(), labels_between(), neighbors(), resolved_find(), Investigate two S6 failures and describe construction mixtures, without rule… (+3 more)

### Community 35 - "Community 35"
Cohesion: 0.26
Nodes (11): check_outputs(), main(), S6 first prompt: propose mappings and report D1 without freezing (protocol §5).…, Reject stale field-role evidence before computing S6 (§3.1, §3.4)., report_md(), describe(), _score(), validate_s5() (+3 more)

### Community 36 - "Community 36"
Cohesion: 0.29
Nodes (11): D3 — Model selection (S20–S21), 9.1 Runtime settings, Part 11 — Troubleshooting, Part 6 — Phase E: Evaluation core, Part 7 — Phase F: Models, S19 — Per-agent metrics, S20 — Model screening, S21 — Freeze models and engineering limits → Gate D3 (+3 more)

### Community 38 - "Community 38"
Cohesion: 0.36
Nodes (7): pyarrow, pyarrow_parquet, check_outputs(), main(), Build evaluator-only S7 reference data (protocol §0.4, §4, §6, §12)., Stage complete typed Parquet tables before publishing; never overwrite an…, write_outputs()

### Community 39 - "Community 39"
Cohesion: 0.61
Nodes (7): by(), find(), rows(), test_ambiguous_counted_separately(), test_answer_counts(), test_entity_fields_use_their_own_type(), test_summary_has_label()

### Community 40 - "Community 40"
Cohesion: 0.29
Nodes (7): evaluate_d1(), Apply global D1; report counts overall and by proposed construction (§5.3)., parametrize, test_ambiguity_uses_unselected_labels(), test_global_d1_does_not_issue_a_final_outcome_with_unresolved_ties(), test_global_d1_thresholds_and_construction_splits(), test_tie_in_definitely_failed_type_does_not_change_global_gate()

### Community 43 - "Community 43"
Cohesion: 0.47
Nodes (4): importlib_util, proposal(), test_existing_output_prevents_all_writes(), test_reports_include_candidate_scores_and_no_frozen_mapping()

### Community 49 - "Community 49"
Cohesion: 0.50
Nodes (5): LabelsBetween, Nbrs, analyse_row(), Find, resolve()

### Community 50 - "Community 50"
Cohesion: 0.50
Nodes (4): cofail_kg, Python, Reproduce, Setup

### Community 51 - "Community 51"
Cohesion: 0.67
Nodes (4): order_key(), Per relation type (sorted): [(1-based position, row)] for the first `size` rows., s5_sample(), test_sample_order_and_size()

## Knowledge Gaps
- **85 isolated node(s):** `screening — strata`, `smoke — strata`, `pilot — strata`, `expansion — strata`, `3. Small real example` (+80 more)
  These have ≤1 connection - possible missing edges or undocumented components. (Counts symbols only; 271 node(s) total have ≤1 connection when file, concept and rationale nodes are included.)
- **21 thin communities (<3 nodes) omitted from report** — run `graphify query` to explore isolated nodes.

## Suggested Questions
_Questions this graph is uniquely positioned to answer:_

- **Why does `D1 — Relation-mapping gate (end of S6)` connect `Community 20` to `Community 1`, `Community 3`, `Community 4`, `Community 6`, `Community 9`, `Community 12`, `Community 14`, `Community 15`, `Community 17`, `Community 23`, `Community 24`, `Community 28`, `Community 31`?**
  _High betweenness centrality (0.092) - this node is a cross-community bridge._
- **Why does `3.1 BioHopR` connect `Community 14` to `Community 32`, `Community 1`, `Community 2`, `Community 35`, `Community 0`, `Community 6`, `Community 11`, `Community 12`, `Community 15`, `Community 16`, `Community 20`, `Community 22`, `Community 23`, `Community 24`, `Community 31`?**
  _High betweenness centrality (0.078) - this node is a cross-community bridge._
- **Why does `0.4 Terms used throughout` connect `Community 23` to `Community 0`, `Community 1`, `Community 2`, `Community 38`, `Community 9`, `Community 11`, `Community 12`, `Community 16`, `Community 17`, `Community 19`, `Community 24`, `Community 30`, `Community 31`?**
  _High betweenness centrality (0.059) - this node is a cross-community bridge._
- **What connects `screening — strata`, `smoke — strata`, `pilot — strata` to the rest of the system?**
  _85 weakly-connected nodes found - possible documentation gaps or missing edges._
- **Should `Community 0` be split into smaller, more focused modules?**
  _Cohesion score 0.09206349206349207 - nodes in this community are weakly interconnected._
- **Should `Community 1` be split into smaller, more focused modules?**
  _Cohesion score 0.10235690235690235 - nodes in this community are weakly interconnected._
- **Should `Community 2` be split into smaller, more focused modules?**
  _Cohesion score 0.1383399209486166 - nodes in this community are weakly interconnected._