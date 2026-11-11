# B6 — Benchmark vs graph labels (EXPLORATORY)

EXPLORATORY (protocol §20) — docs/decision_log.md, entry 2026-11-12 "Plan after D7", section B6.

Produced by `scripts/43_b6_benchmark.py` at commit `0add419c82493df2ffe0ddd2f7731529ee554b53` (tracked files clean: True). Input: `results/combined/pilot_expansion_v1/cofailure.json` (SHA256 `198b9aa18770d1a815429361be8f79601330276642665feb025783dd5560f87d`).

CF3^Q: protocol §16.1. CF3^BH: protocol §16.2. BH-only = CF3^BH = 1 and CF3^Q = 0; Q-only = CF3^Q = 1 and CF3^BH = 0.

## Table 1 — All queries

| relation_type | queries | CF3^BH | CF3^Q | both | BH-only | Q-only |
|---|---|---|---|---|---|---|
| disease:drug:effect/phenotype | 336 | 0 | 0 | 0 | 0 | 0 |
| disease:drug:gene/protein | 8 | 0 | 0 | 0 | 0 | 0 |
| disease:gene/protein:drug | 16 | 0 | 0 | 0 | 0 | 0 |
| drug:disease:effect/phenotype | 6 | 0 | 0 | 0 | 0 | 0 |
| drug:disease:gene/protein | 8 | 2 | 2 | 2 | 0 | 0 |
| drug:gene/protein:disease | 51 | 0 | 0 | 0 | 0 | 0 |
| effect/phenotype:disease:drug | 55 | 35 | 4 | 4 | 31 | 0 |
| gene/protein:disease:drug | 11 | 1 | 1 | 1 | 0 | 0 |
| gene/protein:drug:disease | 9 | 1 | 1 | 1 | 0 | 0 |
| total | 500 | 39 | 8 | 8 | 31 | 0 |

## Table 2 — Without SOURCE_NAME_OVERLAP queries (BH2_05778, BH2_05971, BH2_06099; protocol §19.1)

| relation_type | queries | CF3^BH | CF3^Q | both | BH-only | Q-only |
|---|---|---|---|---|---|---|
| disease:drug:effect/phenotype | 336 | 0 | 0 | 0 | 0 | 0 |
| disease:drug:gene/protein | 8 | 0 | 0 | 0 | 0 | 0 |
| disease:gene/protein:drug | 16 | 0 | 0 | 0 | 0 | 0 |
| drug:disease:effect/phenotype | 6 | 0 | 0 | 0 | 0 | 0 |
| drug:disease:gene/protein | 8 | 2 | 2 | 2 | 0 | 0 |
| drug:gene/protein:disease | 51 | 0 | 0 | 0 | 0 | 0 |
| effect/phenotype:disease:drug | 52 | 34 | 3 | 3 | 31 | 0 |
| gene/protein:disease:drug | 11 | 1 | 1 | 1 | 0 | 0 |
| gene/protein:drug:disease | 9 | 1 | 1 | 1 | 0 | 0 |
| total | 497 | 38 | 7 | 7 | 31 | 0 |

## Hand-check — 15 of 31 BH-only queries (all queries)

Selection: first 15 BH-only queries by SHA256("42" + query_id) ascending; entity = the benchmark shared entity with the smallest node ID. The researcher's marks (VALID / QUESTIONABLE / NOT_VALID) go in the `mark` column of `results/exploratory/b6_handcheck.csv`.

### 1. BH2_05964 — effect/phenotype:disease:drug

- Question: Name all drugs that can treat a disease that has phenotype Parathyroid carcinoma.
- Entity: Vandetanib [14373] — held by 3 agents (Gemma4-12B, Granite41-8B, Ministral3-14B); in T_q: True
- Graph paths (1):
  - Parathyroid carcinoma [86799] -disease_phenotype_positive-> thyroid gland carcinoma [30749] -indication-> Vandetanib [14373]
- BioHopR gold list (3): Alfacalcidol; Etelcalcetide; Evocalcet

### 2. BH2_05771 — effect/phenotype:disease:drug

- Question: Name all drugs that can treat a disease that has phenotype Episodic hypertension.
- Entity: Torasemide [14133] — held by 4 agents (Gemma4-12B, Granite41-8B, Ministral3-14B, Cogito-14B); in T_q: True
- Graph paths (1):
  - Episodic hypertension [94180] -disease_phenotype_positive-> hypertensive disorder [33577] -indication-> Torasemide [14133]
- BioHopR gold list (3): Metyrosine; Phenoxybenzamine; Phentolamine

### 3. BH2_05587 — effect/phenotype:disease:drug

- Question: Name all drugs that can treat a disease that has phenotype Abnormal nervous system physiology.
- Entity: Benzatropine [14139] — held by 4 agents (Gemma4-12B, Granite41-8B, Ministral3-14B, Cogito-14B); in T_q: True
- Graph paths (1):
  - Abnormal nervous system physiology [22230] -disease_phenotype_positive-> atypical juvenile parkinsonism [32974] -indication-> Benzatropine [14139]
- BioHopR gold list (2): Bevacizumab; Carmustine

### 4. BH2_06040 — effect/phenotype:disease:drug

- Question: Name all drugs that can treat a disease that has phenotype Retinal hamartoma.
- Entity: Selumetinib [14449] — held by 3 agents (Gemma4-12B, Ministral3-14B, Cogito-14B); in T_q: True
- Graph paths (1):
  - Retinal hamartoma [24944] -disease_phenotype_positive-> neurofibromatosis [27275] -indication-> Selumetinib [14449]
- BioHopR gold list (1): Everolimus

### 5. BH2_05578 — effect/phenotype:disease:drug

- Question: Name all drugs that can treat a disease that has phenotype Abnormal internal carotid artery morphology.
- Entity: Atorvastatin [14297] — held by 4 agents (Gemma4-12B, Granite41-8B, Ministral3-14B, Cogito-14B); in T_q: True
- Graph paths (1):
  - Abnormal internal carotid artery morphology [23955] -disease_phenotype_positive-> homozygous familial hypercholesterolemia [33299] -indication-> Atorvastatin [14297]
- BioHopR gold list (3): Alglucosidase alfa; Penicillamine; Tiopronin

### 6. BH2_05905 — effect/phenotype:disease:drug

- Question: Name all drugs that can treat a disease that has phenotype Maculopapular exanthema.
- Entity: Betamethasone [14019] — held by 3 agents (Gemma4-12B, Ministral3-14B, Cogito-14B); in T_q: True
- Graph paths (2):
  - Maculopapular exanthema [94295] -disease_phenotype_positive-> sarcoidosis [32967] -indication-> Betamethasone [14019]
  - Maculopapular exanthema [94295] -disease_phenotype_positive-> exanthem (disease) [33649] -indication-> Betamethasone [14019]
- BioHopR gold list (1): Canakinumab

### 7. BH2_05627 — effect/phenotype:disease:drug

- Question: Name all drugs that can treat a disease that has phenotype Abnormality of the integument.
- Entity: Cimetidine [14729] — held by 3 agents (Gemma4-12B, Ministral3-14B, Cogito-14B); in T_q: True
- Graph paths (1):
  - Abnormality of the integument [22528] -disease_phenotype_positive-> multiple endocrine neoplasia [28426] -indication-> Cimetidine [14729]
- BioHopR gold list (1): Ezetimibe

### 8. BH2_05609 — effect/phenotype:disease:drug

- Question: Name all drugs that can treat a disease that has phenotype Abnormality of circulating cortisol level.
- Entity: Pentamidine [14696] — held by 3 agents (Gemma4-12B, Ministral3-14B, Cogito-14B); in T_q: True
- Graph paths (1):
  - Abnormality of circulating cortisol level [23492] -disease_phenotype_positive-> human African trypanosomiasis [32503] -indication-> Pentamidine [14696]
- BioHopR gold list (3): Ketoconazole; Pasireotide; Trilostane

### 9. BH2_06076 — effect/phenotype:disease:drug

- Question: Name all drugs that can treat a disease that has phenotype Tenesmus.
- Entity: Ciprofloxacin [14188] — held by 3 agents (Gemma4-12B, Ministral3-14B, Cogito-14B); in T_q: True
- Graph paths (1):
  - Tenesmus [89499] -disease_phenotype_positive-> shigellosis [32999] -indication-> Ciprofloxacin [14188]
- BioHopR gold list (1): Migalastat

### 10. BH2_05838 — effect/phenotype:disease:drug

- Question: Name all drugs that can treat a disease that has phenotype Impaired ADP-induced platelet aggregation.
- Entity: Lusutrombopag [14699] — held by 4 agents (Gemma4-12B, Granite41-8B, Ministral3-14B, Cogito-14B); in T_q: True
- Graph paths (1):
  - Impaired ADP-induced platelet aggregation [86012] -disease_phenotype_positive-> thrombocytopenia [27626] -indication-> Lusutrombopag [14699]
- BioHopR gold list (1): Anagrelide

### 11. BH2_05812 — effect/phenotype:disease:drug

- Question: Name all drugs that can treat a disease that has phenotype Hepatic amyloidosis.
- Entity: Acetylcysteine [16036] — held by 3 agents (Gemma4-12B, Ministral3-14B, Cogito-14B); in T_q: True
- Graph paths (1):
  - Hepatic amyloidosis [89237] -disease_phenotype_positive-> amyloidosis (disease) [33591] -indication-> Acetylcysteine [16036]
- BioHopR gold list (1): Canakinumab

### 12. BH2_05874 — effect/phenotype:disease:drug

- Question: Name all drugs that can treat a disease that has phenotype Invasive fungal infection.
- Entity: Ketoconazole [14281] — held by 4 agents (Gemma4-12B, Granite41-8B, Ministral3-14B, Cogito-14B); in T_q: True
- Graph paths (1):
  - Invasive fungal infection [25735] -disease_phenotype_positive-> coccidioidomycosis [32651] -indication-> Ketoconazole [14281]
- BioHopR gold list (2): Amphotericin B; Isavuconazonium

### 13. BH2_06087 — effect/phenotype:disease:drug

- Question: Name all drugs that can treat a disease that has phenotype Tuberous xanthoma.
- Entity: Ezetimibe [15477] — held by 4 agents (Gemma4-12B, Granite41-8B, Ministral3-14B, Cogito-14B); in T_q: True
- Graph paths (1):
  - Tuberous xanthoma [94217] -disease_phenotype_positive-> sitosterolemia [28490] -indication-> Ezetimibe [15477]
- BioHopR gold list (1): Cholic Acid

### 14. BH2_05900 — effect/phenotype:disease:drug

- Question: Name all drugs that can treat a disease that has phenotype Lymphangiectasis.
- Entity: Ketoconazole [14281] — held by 3 agents (Gemma4-12B, Granite41-8B, Ministral3-14B); in T_q: True
- Graph paths (1):
  - Lymphangiectasis [23933] -disease_phenotype_positive-> chromomycosis [32764] -indication-> Ketoconazole [14281]
- BioHopR gold list (1): Diethylcarbamazine

### 15. BH2_05932 — effect/phenotype:disease:drug

- Question: Name all drugs that can treat a disease that has phenotype Neoplasm by anatomical site.
- Entity: Pemetrexed [14802] — held by 3 agents (Gemma4-12B, Granite41-8B, Cogito-14B); in T_q: True
- Graph paths (1):
  - Neoplasm by anatomical site [23277] -disease_phenotype_positive-> malignant mesothelioma (disease) [30725] -indication-> Pemetrexed [14802]
- BioHopR gold list (5): Daunorubicin; Doxorubicin; Interferon alfa-2b; Paclitaxel; Vinblastine
