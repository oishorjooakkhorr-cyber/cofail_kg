# Final tables (S38)

Produced by `scripts/38_final_tables.py` at commit `d6a00137dc22cbec6f9d537432a0166f5d0f9c6b` (tracked files clean: True; producing code committed at this commit: True). Runbook Part 10, S38, with its DESCRIPTIVE additions; Table 12 (IC) added on the researcher's instruction of 2026-11-14.

| Table | Title | Status | Basis | CSV files |
|---|---|---|---|---|
| 1 | [Dataset](table01_dataset.md) | Dataset description (S6, S8, S9 outputs). Descriptive. | protocol §5.1–§5.3, §7.1, §7.2, §8 | table01a_relation_types.csv, table01b_inconsistent_reasons.csv, table01c_bridge_multiplicity.csv, table01d_ambiguity_tags.csv, table01e_construction.csv, table01f_saturation.csv, table01g_inclusion.csv |
| 2 | [Agent behaviour](table02_agent_behaviour.md) | Results of record: pilot_v1 + expansion_v1, 500 queries × 4 agents, latest attempts (protocol §19); Gate D7 DESCRIPTIVE (decision log 2026-11-12). Descriptive. | protocol §9.5, §13, §14.1, §14.3, §15; split by construction and ambiguity tag (§5.3) | table02a_episode_status.csv, table02b_hop1_status.csv, table02c_bridge_ranks.csv, table02d_label_a.csv, table02e_label_b.csv, table02f_ratio_metrics.csv |
| 3 | [Co-failure](table03_cofailure.md) | Results of record: pilot_v1 + expansion_v1, 500 queries × 4 agents, latest attempts (protocol §19); Gate D7 DESCRIPTIVE (decision log 2026-11-12). Descriptive. | protocol §16, §17, §19.1; strata §5.2, §5.3, §7.1 | table03a_cofailure_totals.csv, table03b_flagged_queries.csv, table03c_pairwise_agreement.csv, table03d_chance_baselines.csv, table03e_cofailure_by_stratum.csv |
| 4 | [Mechanisms](table04_mechanisms.md) | Results of record: pilot_v1 + expansion_v1, 500 queries × 4 agents, latest attempts (protocol §19); Gate D7 DESCRIPTIVE (decision log 2026-11-12). Descriptive. | protocol §14.2, §15, §16.3, §21; strata §5.2, §5.3, §7.1 | table04a_reason_codes_by_stratum.csv, table04b_reason_codes_by_agent.csv, table04c_path_cofailure_by_stratum.csv, table04d_flagged_query_mechanisms.csv |
| 5 | [Counterfactual (illustrative cases)](table05_counterfactual.md) | DESCRIPTIVE, TREATMENT-ONLY, EXPLORATORY (D7 DESCRIPTIVE). Per case only. | protocol §21; docs/decision_log.md, entry 2026-11-12 "S30 — Plan after D7", section A4; docs/decision_log.md, entry 2026-11-13 "S36 — Readings of the §21 outcomes" | table05a_cofailure_before_after.csv, table05b_recovery_no_answer.csv, table05c_displacement_per_holder.csv, table05d_displacement_per_case.csv |
| 6 | [B1 — Off-label opportunity and uptake](table06_b1_offlabel_uptake.md) | EXPLORATORY (protocol §20) | docs/decision_log.md, entry 2026-11-12 "S30 — Plan after D7", section B1; docs/decision_log.md, entries 2026-11-12 "B1 — Readings of the B1 definitions" and 2026-11-13 "B1 — Outcome NOT CLEAN; follow-up not run; no full run" | table06a_uptake.csv, table06b_outcome.csv, table06c_excluded_episodes.csv |
| 7 | [B2 — Strict vs lenient answer key](table07_b2_strict_vs_lenient.md) | EXPLORATORY (protocol §20) | docs/decision_log.md, entry 2026-11-12 "S30 — Plan after D7", section B2; docs/decision_log.md, entry 2026-11-13 "B2 — Inputs and the contraindication step" | table07a_cofailure.csv, table07b_precision_hop1.csv, table07c_contraindication.csv |
| 8 | [B5 — Treat concentration](table08_b5_treat_concentration.md) | EXPLORATORY (protocol §20) | docs/decision_log.md, entry 2026-11-12 "S30 — Plan after D7", section B5 | table08a_groups.csv, table08b_hypergeometric.csv |
| 9 | [B6 — Benchmark vs graph labels, with the hand-check](table09_b6_benchmark_vs_graph.md) | EXPLORATORY (protocol §20) | docs/decision_log.md, entry 2026-11-12 "S30 — Plan after D7", section B6; docs/decision_log.md, entries 2026-11-12 "B6 — Hand-check mark definitions" and 2026-11-12 "B6 — Outcome: hand-check NOT CLEAN (10 of 15 VALID)" | table09a_by_relation_type.csv, table09b_handcheck.csv, table09c_handcheck_outcome.csv |
| 10 | [RP — Repeat run (repeat_v1)](table10_rp_repeat_run.md) | EXPLORATORY (protocol §20) | docs/decision_log.md, entry 2026-11-12 "S30 — Plan after D7", section D; docs/decision_log.md, entries 2026-11-13 "RP — Repeat-run inputs" and "RP — Pre-run checks" | table10a_per_query.csv, table10b_summary.csv, table10c_jaccard.csv |
| 11 | [Follow-up (P1, P2)](table11_followup.md) | EXPLORATORY — NOT RUN | docs/decision_log.md, entry 2026-11-12 "S30 — Plan after D7", section C3; docs/decision_log.md, entry 2026-11-13 "B1 — Outcome NOT CLEAN; follow-up not run; no full run"; docs/decision_log.md, entry 2026-11-14 "S37 — D8 not applicable after D7 DESCRIPTIVE; no scaling" | table11a_predictions.csv |
| 12 | [IC — Independence check of off-label uptake](table12_ic_independence_check.md) | EXPLORATORY (protocol §20) | docs/decision_log.md, entry 2026-11-13 "IC — Independence check of off-label uptake (rule fixed before computing)"; docs/decision_log.md, entry 2026-11-12 "S30 — Plan after D7" (B1 inputs) | table12a_summary.csv, table12b_rates.csv, table12c_per_query.csv |

Cross-checks passed before writing:

- cofailure.json per-query flags add up to its stored totals (both views)
- manifest relation type and ambiguity tag equal cofailure.json for all 500 queries
- B1, B2, B5, B6, RP and IC were computed on the current cofailure.json (SHA256)
- B2 strict, B5 both/total and B6 total equal the cofailure.json totals (both views)
- RP original flags, IC CF3^{Q,H1} and S36 'before' flags equal cofailure.json per query
- S31 candidates.csv lists exactly the queries meeting the flag part of the §21 candidate rule

Input and output SHA256: `provenance.json`.
