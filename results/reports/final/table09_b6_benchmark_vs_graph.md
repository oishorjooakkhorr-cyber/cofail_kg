# Table 9 — B6 — Benchmark vs graph labels, with the hand-check

**Status:** EXPLORATORY (protocol §20)

**Basis:** docs/decision_log.md, entry 2026-11-12 "S30 — Plan after D7", section B6; docs/decision_log.md, entries 2026-11-12 "B6 — Hand-check mark definitions" and 2026-11-12 "B6 — Outcome: hand-check NOT CLEAN (10 of 15 VALID)"

Produced by `scripts/38_final_tables.py` at commit `d6a00137dc22cbec6f9d537432a0166f5d0f9c6b` (tracked files clean: True; producing code committed at this commit: True).

Inputs (SHA256 in `provenance.json`; last commit that touched each):

- `results/exploratory/b6/b6_table.csv` — 318c0db47ac28329383dab98868c1a478d8e1542
- `results/exploratory/b6/b6.json` — 318c0db47ac28329383dab98868c1a478d8e1542
- `results/exploratory/b6_handcheck.csv` — e1cec7e8958347aaf7d3ff72bfde746d3f9d0d54

BH-only queries: 31. Produced by scripts/43_b6_benchmark.py at commit 0add419c82493df2ffe0ddd2f7731529ee554b53; marks from results/exploratory/b6_handcheck.csv.

## 9a. CF3^BH vs CF3^Q by relation type (BH-only = CF3^BH = 1 and CF3^Q = 0)

CSV: `table09a_by_relation_type.csv`

| View | Relation type | Queries | CF3^BH | CF3^Q | Both | BH-only | Q-only |
|---|---|---|---|---|---|---|---|
| All queries | disease:drug:effect/phenotype | 336 | 0 | 0 | 0 | 0 | 0 |
| All queries | disease:drug:gene/protein | 8 | 0 | 0 | 0 | 0 | 0 |
| All queries | disease:gene/protein:drug | 16 | 0 | 0 | 0 | 0 | 0 |
| All queries | drug:disease:effect/phenotype | 6 | 0 | 0 | 0 | 0 | 0 |
| All queries | drug:disease:gene/protein | 8 | 2 | 2 | 2 | 0 | 0 |
| All queries | drug:gene/protein:disease | 51 | 0 | 0 | 0 | 0 | 0 |
| All queries | effect/phenotype:disease:drug | 55 | 35 | 4 | 4 | 31 | 0 |
| All queries | gene/protein:disease:drug | 11 | 1 | 1 | 1 | 0 | 0 |
| All queries | gene/protein:drug:disease | 9 | 1 | 1 | 1 | 0 | 0 |
| All queries | total | 500 | 39 | 8 | 8 | 31 | 0 |
| Without SOURCE_NAME_OVERLAP | disease:drug:effect/phenotype | 336 | 0 | 0 | 0 | 0 | 0 |
| Without SOURCE_NAME_OVERLAP | disease:drug:gene/protein | 8 | 0 | 0 | 0 | 0 | 0 |
| Without SOURCE_NAME_OVERLAP | disease:gene/protein:drug | 16 | 0 | 0 | 0 | 0 | 0 |
| Without SOURCE_NAME_OVERLAP | drug:disease:effect/phenotype | 6 | 0 | 0 | 0 | 0 | 0 |
| Without SOURCE_NAME_OVERLAP | drug:disease:gene/protein | 8 | 2 | 2 | 2 | 0 | 0 |
| Without SOURCE_NAME_OVERLAP | drug:gene/protein:disease | 51 | 0 | 0 | 0 | 0 | 0 |
| Without SOURCE_NAME_OVERLAP | effect/phenotype:disease:drug | 52 | 34 | 3 | 3 | 31 | 0 |
| Without SOURCE_NAME_OVERLAP | gene/protein:disease:drug | 11 | 1 | 1 | 1 | 0 | 0 |
| Without SOURCE_NAME_OVERLAP | gene/protein:drug:disease | 9 | 1 | 1 | 1 | 0 | 0 |
| Without SOURCE_NAME_OVERLAP | total | 497 | 38 | 7 | 7 | 31 | 0 |

## 9b. Hand-check: 15 of the BH-only queries, final marks (researcher)

CSV: `table09b_handcheck.csv`

| Order | Query | Relation type | Entity | Holders | Holder agents | In T_q | Graph path(s) | BioHopR gold size | BioHopR gold list | Final mark |
|---|---|---|---|---|---|---|---|---|---|---|
| 1 | BH2_05964 | effect/phenotype:disease:drug | Vandetanib [14373] | 3 | Gemma4-12B, Granite41-8B, Ministral3-14B | yes | Parathyroid carcinoma [86799] -disease_phenotype_positive-> thyroid gland carcinoma [30749] -indication-> Vandetanib [14373] | 3 | Alfacalcidol; Etelcalcetide; Evocalcet | QUESTIONABLE |
| 2 | BH2_05771 | effect/phenotype:disease:drug | Torasemide [14133] | 4 | Gemma4-12B, Granite41-8B, Ministral3-14B, Cogito-14B | yes | Episodic hypertension [94180] -disease_phenotype_positive-> hypertensive disorder [33577] -indication-> Torasemide [14133] | 3 | Metyrosine; Phenoxybenzamine; Phentolamine | VALID |
| 3 | BH2_05587 | effect/phenotype:disease:drug | Benzatropine [14139] | 4 | Gemma4-12B, Granite41-8B, Ministral3-14B, Cogito-14B | yes | Abnormal nervous system physiology [22230] -disease_phenotype_positive-> atypical juvenile parkinsonism [32974] -indication-> Benzatropine [14139] | 2 | Bevacizumab; Carmustine | VALID |
| 4 | BH2_06040 | effect/phenotype:disease:drug | Selumetinib [14449] | 3 | Gemma4-12B, Ministral3-14B, Cogito-14B | yes | Retinal hamartoma [24944] -disease_phenotype_positive-> neurofibromatosis [27275] -indication-> Selumetinib [14449] | 1 | Everolimus | QUESTIONABLE |
| 5 | BH2_05578 | effect/phenotype:disease:drug | Atorvastatin [14297] | 4 | Gemma4-12B, Granite41-8B, Ministral3-14B, Cogito-14B | yes | Abnormal internal carotid artery morphology [23955] -disease_phenotype_positive-> homozygous familial hypercholesterolemia [33299] -indication-> Atorvastatin [14297] | 3 | Alglucosidase alfa; Penicillamine; Tiopronin | VALID |
| 6 | BH2_05905 | effect/phenotype:disease:drug | Betamethasone [14019] | 3 | Gemma4-12B, Ministral3-14B, Cogito-14B | yes | Maculopapular exanthema [94295] -disease_phenotype_positive-> sarcoidosis [32967] -indication-> Betamethasone [14019] \| Maculopapular exanthema [94295] -disease_phenotype_positive-> exanthem (disease) [33649] -indication-> Betamethasone [14019] | 1 | Canakinumab | VALID |
| 7 | BH2_05627 | effect/phenotype:disease:drug | Cimetidine [14729] | 3 | Gemma4-12B, Ministral3-14B, Cogito-14B | yes | Abnormality of the integument [22528] -disease_phenotype_positive-> multiple endocrine neoplasia [28426] -indication-> Cimetidine [14729] | 1 | Ezetimibe | VALID |
| 8 | BH2_05609 | effect/phenotype:disease:drug | Pentamidine [14696] | 3 | Gemma4-12B, Ministral3-14B, Cogito-14B | yes | Abnormality of circulating cortisol level [23492] -disease_phenotype_positive-> human African trypanosomiasis [32503] -indication-> Pentamidine [14696] | 3 | Ketoconazole; Pasireotide; Trilostane | QUESTIONABLE |
| 9 | BH2_06076 | effect/phenotype:disease:drug | Ciprofloxacin [14188] | 3 | Gemma4-12B, Ministral3-14B, Cogito-14B | yes | Tenesmus [89499] -disease_phenotype_positive-> shigellosis [32999] -indication-> Ciprofloxacin [14188] | 1 | Migalastat | VALID |
| 10 | BH2_05838 | effect/phenotype:disease:drug | Lusutrombopag [14699] | 4 | Gemma4-12B, Granite41-8B, Ministral3-14B, Cogito-14B | yes | Impaired ADP-induced platelet aggregation [86012] -disease_phenotype_positive-> thrombocytopenia [27626] -indication-> Lusutrombopag [14699] | 1 | Anagrelide | QUESTIONABLE |
| 11 | BH2_05812 | effect/phenotype:disease:drug | Acetylcysteine [16036] | 3 | Gemma4-12B, Ministral3-14B, Cogito-14B | yes | Hepatic amyloidosis [89237] -disease_phenotype_positive-> amyloidosis (disease) [33591] -indication-> Acetylcysteine [16036] | 1 | Canakinumab | QUESTIONABLE |
| 12 | BH2_05874 | effect/phenotype:disease:drug | Ketoconazole [14281] | 4 | Gemma4-12B, Granite41-8B, Ministral3-14B, Cogito-14B | yes | Invasive fungal infection [25735] -disease_phenotype_positive-> coccidioidomycosis [32651] -indication-> Ketoconazole [14281] | 2 | Amphotericin B; Isavuconazonium | VALID |
| 13 | BH2_06087 | effect/phenotype:disease:drug | Ezetimibe [15477] | 4 | Gemma4-12B, Granite41-8B, Ministral3-14B, Cogito-14B | yes | Tuberous xanthoma [94217] -disease_phenotype_positive-> sitosterolemia [28490] -indication-> Ezetimibe [15477] | 1 | Cholic Acid | VALID |
| 14 | BH2_05900 | effect/phenotype:disease:drug | Ketoconazole [14281] | 3 | Gemma4-12B, Granite41-8B, Ministral3-14B | yes | Lymphangiectasis [23933] -disease_phenotype_positive-> chromomycosis [32764] -indication-> Ketoconazole [14281] | 1 | Diethylcarbamazine | VALID |
| 15 | BH2_05932 | effect/phenotype:disease:drug | Pemetrexed [14802] | 3 | Gemma4-12B, Granite41-8B, Cogito-14B | yes | Neoplasm by anatomical site [23277] -disease_phenotype_positive-> malignant mesothelioma (disease) [30725] -indication-> Pemetrexed [14802] | 5 | Daunorubicin; Doxorubicin; Interferon alfa-2b; Paclitaxel; Vinblastine | VALID |

Selection: first 15 BH-only queries by SHA256("42" + query_id); entity = the benchmark shared entity with the smallest node ID. Sources gathered and marks proposed by Claude Code (an LLM); every final mark set by the researcher (results/exploratory/b6_handcheck_notes.md).

## 9c. Hand-check outcome (rule fixed before any mark)

CSV: `table09c_handcheck_outcome.csv`

| VALID | QUESTIONABLE | NOT_VALID | Rows | Rule | Outcome |
|---|---|---|---|---|---|
| 10 | 5 | 0 | 15 | CLEAN if at least 12 of 15 final marks are VALID | NOT CLEAN |
