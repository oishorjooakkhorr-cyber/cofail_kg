# Table 3 — Co-failure

**Status:** Results of record: pilot_v1 + expansion_v1, 500 queries × 4 agents, latest attempts (protocol §19); Gate D7 DESCRIPTIVE (decision log 2026-11-12). Descriptive.

**Basis:** protocol §16, §17, §19.1; strata §5.2, §5.3, §7.1

Produced by `scripts/38_final_tables.py` at commit `d6a00137dc22cbec6f9d537432a0166f5d0f9c6b` (tracked files clean: True; producing code committed at this commit: True).

Inputs (SHA256 in `provenance.json`; last commit that touched each):

- `results/combined/pilot_expansion_v1/components.json` — 02e0182f404610727741a6407169dbbe201671e7
- `data/processed/manifests/expansion.jsonl` — a0c586781ba30484b9589fd2cc96b79d4e2a5afc
- `results/runs/expansion_v1/analysis/metrics` — 02e0182f404610727741a6407169dbbe201671e7
- `data/processed/manifests/pilot.jsonl` — a0c586781ba30484b9589fd2cc96b79d4e2a5afc
- `results/runs/pilot_v1/analysis/metrics` — d43af3085a82a5d3706b97f6ad5de6441d5d0b69
- `results/combined/pilot_expansion_v1/cofailure.json` — 02e0182f404610727741a6407169dbbe201671e7
- `results/combined/pilot_expansion_v1/nulls.json` — 02e0182f404610727741a6407169dbbe201671e7

## 3a. Co-failure (§16.1–§16.3): queries with the flag = 1

CSV: `table03a_cofailure_totals.csv`

| Metric | All: queries flagged | All: queries | All: share | Without SNO: queries flagged | Without SNO: queries | Without SNO: share |
|---|---|---|---|---|---|---|
| CF3^Q | 8 | 500 | 0.0160 | 7 | 497 | 0.0141 |
| CF4^Q | 2 | 500 | 0.0040 | 1 | 497 | 0.0020 |
| CF3^Q grounded | 8 | 500 | 0.0160 | 7 | 497 | 0.0141 |
| CF4^Q grounded | 2 | 500 | 0.0040 | 1 | 497 | 0.0020 |
| CF3^{Q,H1} | 6 | 500 | 0.0120 | 5 | 497 | 0.0101 |
| CF4^{Q,H1} | 2 | 500 | 0.0040 | 1 | 497 | 0.0020 |
| CF3^BH | 39 | 500 | 0.0780 | 38 | 497 | 0.0765 |
| CF4^BH | 23 | 500 | 0.0460 | 22 | 497 | 0.0443 |
| PCF_REL3 | 8 | 500 | 0.0160 | 7 | 497 | 0.0141 |
| PCF_REL4 | 2 | 500 | 0.0040 | 1 | 497 | 0.0020 |
| PCF_NODE3 | 0 | 500 | 0.0000 | 0 | 497 | 0.0000 |
| PCF_NODE4 | 0 | 500 | 0.0000 | 0 | 497 | 0.0000 |
| PCF_SHORTCUT3 | 2 | 500 | 0.0040 | 2 | 497 | 0.0040 |

SOURCE_NAME_OVERLAP (SNO) queries (§19.1): BH2_05778, BH2_05971, BH2_06099. Gates use all queries.

## 3b. Queries with each flag = 1 (all queries)

CSV: `table03b_flagged_queries.csv`

| Metric | Queries flagged | Query IDs | Of which SOURCE_NAME_OVERLAP |
|---|---|---|---|
| CF3^Q | 8 | BH2_03356, BH2_04650, BH2_04856, BH2_05290, BH2_05778, BH2_05890, BH2_05997, BH2_06016 | BH2_05778 |
| CF4^Q | 2 | BH2_05778, BH2_06016 | BH2_05778 |
| CF3^Q grounded | 8 | BH2_03356, BH2_04650, BH2_04856, BH2_05290, BH2_05778, BH2_05890, BH2_05997, BH2_06016 | BH2_05778 |
| CF4^Q grounded | 2 | BH2_05778, BH2_06016 | BH2_05778 |
| CF3^{Q,H1} | 6 | BH2_03356, BH2_05290, BH2_05778, BH2_05890, BH2_05997, BH2_06016 | BH2_05778 |
| CF4^{Q,H1} | 2 | BH2_05778, BH2_06016 | BH2_05778 |
| CF3^BH | 39 | BH2_03356, BH2_04650, BH2_04856, BH2_05290, BH2_05572, BH2_05576, BH2_05578, BH2_05587, BH2_05604, BH2_05609, BH2_05627, BH2_05680, BH2_05695, BH2_05704, BH2_05716, BH2_05741, BH2_05757, BH2_05771, BH2_05778, BH2_05812, BH2_05838, BH2_05847, BH2_05856, BH2_05868, BH2_05874, BH2_05890, BH2_05900, BH2_05905, BH2_05932, BH2_05964, BH2_05989, BH2_05997, BH2_06016, BH2_06031, BH2_06034, BH2_06040, BH2_06052, BH2_06076, BH2_06087 | BH2_05778 |
| CF4^BH | 23 | BH2_05572, BH2_05576, BH2_05578, BH2_05587, BH2_05604, BH2_05680, BH2_05704, BH2_05716, BH2_05741, BH2_05771, BH2_05778, BH2_05838, BH2_05847, BH2_05856, BH2_05874, BH2_05890, BH2_05905, BH2_05989, BH2_05997, BH2_06016, BH2_06031, BH2_06034, BH2_06087 | BH2_05778 |
| PCF_REL3 | 8 | BH2_03356, BH2_04650, BH2_04856, BH2_05290, BH2_05778, BH2_05890, BH2_05997, BH2_06016 | BH2_05778 |
| PCF_REL4 | 2 | BH2_05778, BH2_06016 | BH2_05778 |
| PCF_NODE3 | 0 | — | — |
| PCF_NODE4 | 0 | — | — |
| PCF_SHORTCUT3 | 2 | BH2_04650, BH2_04856 | — |

## 3c. Pairwise error agreement (§16.4): among queries where both agents have a non-empty W (OFF_QUESTION set), the share where the two sets intersect

CSV: `table03c_pairwise_agreement.csv`

| View | Agent i | Agent j | Intersecting | Both non-empty | Agreement |
|---|---|---|---|---|---|
| All queries | Gemma4-12B | Granite41-8B | 3 | 5 | 0.6000 |
| All queries | Gemma4-12B | Ministral3-14B | 3 | 3 | 1.0000 |
| All queries | Gemma4-12B | Cogito-14B | 6 | 6 | 1.0000 |
| All queries | Granite41-8B | Ministral3-14B | 14 | 19 | 0.7368 |
| All queries | Granite41-8B | Cogito-14B | 12 | 22 | 0.5455 |
| All queries | Ministral3-14B | Cogito-14B | 17 | 18 | 0.9444 |
| Without SOURCE_NAME_OVERLAP | Gemma4-12B | Granite41-8B | 2 | 4 | 0.5000 |
| Without SOURCE_NAME_OVERLAP | Gemma4-12B | Ministral3-14B | 2 | 2 | 1.0000 |
| Without SOURCE_NAME_OVERLAP | Gemma4-12B | Cogito-14B | 5 | 5 | 1.0000 |
| Without SOURCE_NAME_OVERLAP | Granite41-8B | Ministral3-14B | 13 | 18 | 0.7222 |
| Without SOURCE_NAME_OVERLAP | Granite41-8B | Cogito-14B | 11 | 21 | 0.5238 |
| Without SOURCE_NAME_OVERLAP | Ministral3-14B | Cogito-14B | 16 | 17 | 0.9412 |

Agreement is NA (—) when no query has both sets non-empty; the denominator is always shown.

## 3d. Chance baselines (§17), 10000 trials

CSV: `table03d_chance_baselines.csv`

| View | Null | Observed | Version | Queries | Observed total | Null mean | Null median | Null p95 | p | Observed above p95 |
|---|---|---|---|---|---|---|---|---|---|---|
| All queries | N1 | O_N1 | ≥ 3 agents | 500 | 8 | 7.6199 | 8.0000 | 8.0000 | 0.6412 | no |
| All queries | N1 | O_N1 | all 4 agents | 500 | 2 | 2.0762 | 2.0000 | 3.0000 | 1.0000 | no |
| All queries | N1-H1 | O_H1 | ≥ 3 agents | 500 | 6 | 5.6236 | 6.0000 | 6.0000 | 0.6440 | no |
| All queries | N1-H1 | O_H1 | all 4 agents | 500 | 2 | 2.0741 | 2.0000 | 3.0000 | 1.0000 | no |
| All queries | N2 | O_N2 | ≥ 3 agents | 500 | 8 | 7.6101 | 8.0000 | 8.0000 | 0.6352 | no |
| All queries | N2 | O_N2 | all 4 agents | 500 | 2 | 2.0754 | 2.0000 | 3.0000 | 1.0000 | no |
| Without SOURCE_NAME_OVERLAP | N1 | O_N1 | ≥ 3 agents | 497 | 7 | 6.6199 | 7.0000 | 7.0000 | 0.6412 | no |
| Without SOURCE_NAME_OVERLAP | N1 | O_N1 | all 4 agents | 497 | 1 | 1.0762 | 1.0000 | 2.0000 | 1.0000 | no |
| Without SOURCE_NAME_OVERLAP | N1-H1 | O_H1 | ≥ 3 agents | 497 | 5 | 4.6236 | 5.0000 | 5.0000 | 0.6440 | no |
| Without SOURCE_NAME_OVERLAP | N1-H1 | O_H1 | all 4 agents | 497 | 1 | 1.0741 | 1.0000 | 2.0000 | 1.0000 | no |
| Without SOURCE_NAME_OVERLAP | N2 | O_N2 | ≥ 3 agents | 497 | 7 | 6.6101 | 7.0000 | 7.0000 | 0.6352 | no |
| Without SOURCE_NAME_OVERLAP | N2 | O_N2 | all 4 agents | 497 | 1 | 1.0754 | 1.0000 | 2.0000 | 1.0000 | no |
| Excluding queries with a technical failure | N1 | O_N1 | ≥ 3 agents | 399 | 8 | 7.6199 | 8.0000 | 8.0000 | 0.6412 | no |
| Excluding queries with a technical failure | N1 | O_N1 | all 4 agents | 399 | 2 | 2.0762 | 2.0000 | 3.0000 | 1.0000 | no |
| Excluding queries with a technical failure | N1-H1 | O_H1 | ≥ 3 agents | 399 | 6 | 5.6236 | 6.0000 | 6.0000 | 0.6440 | no |
| Excluding queries with a technical failure | N1-H1 | O_H1 | all 4 agents | 399 | 2 | 2.0741 | 2.0000 | 3.0000 | 1.0000 | no |
| Excluding queries with a technical failure | N2 | O_N2 | ≥ 3 agents | 399 | 8 | 7.6101 | 8.0000 | 8.0000 | 0.6352 | no |
| Excluding queries with a technical failure | N2 | O_N2 | all 4 agents | 399 | 2 | 2.0754 | 2.0000 | 3.0000 | 1.0000 | no |

"Observed exceeds null" = observed total above the null's 95th percentile (§17). The gate comparison (D6, D7) is O_H1 against N1-H1. p = (1 + #{trials with null total ≥ observed}) / (1 + trials).

## 3e. Co-failure by stratum (§5.2, §5.3, §7.1): queries with the flag = 1

CSV: `table03e_cofailure_by_stratum.csv`

| View | Stratum | Value | Queries | CF3^Q | CF4^Q | CF3^Q grounded | CF4^Q grounded | CF3^{Q,H1} | CF4^{Q,H1} | CF3^BH | CF4^BH | PCF_REL3 | PCF_REL4 | PCF_NODE3 | PCF_NODE4 | PCF_SHORTCUT3 |
|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|
| All queries | Relation type | disease:drug:effect/phenotype | 336 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 |
| All queries | Relation type | disease:drug:gene/protein | 8 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 |
| All queries | Relation type | disease:gene/protein:drug | 16 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 |
| All queries | Relation type | drug:disease:effect/phenotype | 6 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 |
| All queries | Relation type | drug:disease:gene/protein | 8 | 2 | 0 | 2 | 0 | 0 | 0 | 2 | 0 | 2 | 0 | 0 | 0 | 2 |
| All queries | Relation type | drug:gene/protein:disease | 51 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 |
| All queries | Relation type | effect/phenotype:disease:drug | 55 | 4 | 2 | 4 | 2 | 4 | 2 | 35 | 23 | 4 | 2 | 0 | 0 | 0 |
| All queries | Relation type | gene/protein:disease:drug | 11 | 1 | 0 | 1 | 0 | 1 | 0 | 1 | 0 | 1 | 0 | 0 | 0 | 0 |
| All queries | Relation type | gene/protein:drug:disease | 9 | 1 | 0 | 1 | 0 | 1 | 0 | 1 | 0 | 1 | 0 | 0 | 0 | 0 |
| All queries | Ambiguity tag | BOTH_AMBIGUOUS | 61 | 4 | 2 | 4 | 2 | 4 | 2 | 35 | 23 | 4 | 2 | 0 | 0 | 0 |
| All queries | Ambiguity tag | NONE | 67 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 |
| All queries | Ambiguity tag | R1_AMBIGUOUS | 352 | 2 | 0 | 2 | 0 | 0 | 0 | 2 | 0 | 2 | 0 | 0 | 0 | 2 |
| All queries | Ambiguity tag | R2_AMBIGUOUS | 20 | 2 | 0 | 2 | 0 | 2 | 0 | 2 | 0 | 2 | 0 | 0 | 0 | 0 |
| All queries | Construction | BRIDGE | 164 | 8 | 2 | 8 | 2 | 6 | 2 | 39 | 23 | 8 | 2 | 0 | 0 | 2 |
| All queries | Construction | UNION | 336 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 |
| All queries | Bridge multiplicity | MULTI_BRIDGE | 375 | 3 | 1 | 3 | 1 | 3 | 1 | 34 | 22 | 3 | 1 | 0 | 0 | 0 |
| All queries | Bridge multiplicity | SINGLE_BRIDGE | 125 | 5 | 1 | 5 | 1 | 3 | 1 | 5 | 1 | 5 | 1 | 0 | 0 | 2 |
| Without SOURCE_NAME_OVERLAP | Relation type | disease:drug:effect/phenotype | 336 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 |
| Without SOURCE_NAME_OVERLAP | Relation type | disease:drug:gene/protein | 8 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 |
| Without SOURCE_NAME_OVERLAP | Relation type | disease:gene/protein:drug | 16 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 |
| Without SOURCE_NAME_OVERLAP | Relation type | drug:disease:effect/phenotype | 6 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 |
| Without SOURCE_NAME_OVERLAP | Relation type | drug:disease:gene/protein | 8 | 2 | 0 | 2 | 0 | 0 | 0 | 2 | 0 | 2 | 0 | 0 | 0 | 2 |
| Without SOURCE_NAME_OVERLAP | Relation type | drug:gene/protein:disease | 51 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 |
| Without SOURCE_NAME_OVERLAP | Relation type | effect/phenotype:disease:drug | 52 | 3 | 1 | 3 | 1 | 3 | 1 | 34 | 22 | 3 | 1 | 0 | 0 | 0 |
| Without SOURCE_NAME_OVERLAP | Relation type | gene/protein:disease:drug | 11 | 1 | 0 | 1 | 0 | 1 | 0 | 1 | 0 | 1 | 0 | 0 | 0 | 0 |
| Without SOURCE_NAME_OVERLAP | Relation type | gene/protein:drug:disease | 9 | 1 | 0 | 1 | 0 | 1 | 0 | 1 | 0 | 1 | 0 | 0 | 0 | 0 |
| Without SOURCE_NAME_OVERLAP | Ambiguity tag | BOTH_AMBIGUOUS | 58 | 3 | 1 | 3 | 1 | 3 | 1 | 34 | 22 | 3 | 1 | 0 | 0 | 0 |
| Without SOURCE_NAME_OVERLAP | Ambiguity tag | NONE | 67 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 |
| Without SOURCE_NAME_OVERLAP | Ambiguity tag | R1_AMBIGUOUS | 352 | 2 | 0 | 2 | 0 | 0 | 0 | 2 | 0 | 2 | 0 | 0 | 0 | 2 |
| Without SOURCE_NAME_OVERLAP | Ambiguity tag | R2_AMBIGUOUS | 20 | 2 | 0 | 2 | 0 | 2 | 0 | 2 | 0 | 2 | 0 | 0 | 0 | 0 |
| Without SOURCE_NAME_OVERLAP | Construction | BRIDGE | 161 | 7 | 1 | 7 | 1 | 5 | 1 | 38 | 22 | 7 | 1 | 0 | 0 | 2 |
| Without SOURCE_NAME_OVERLAP | Construction | UNION | 336 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 |
| Without SOURCE_NAME_OVERLAP | Bridge multiplicity | MULTI_BRIDGE | 372 | 2 | 0 | 2 | 0 | 2 | 0 | 33 | 21 | 2 | 0 | 0 | 0 | 0 |
| Without SOURCE_NAME_OVERLAP | Bridge multiplicity | SINGLE_BRIDGE | 125 | 5 | 1 | 5 | 1 | 3 | 1 | 5 | 1 | 5 | 1 | 0 | 0 | 2 |
