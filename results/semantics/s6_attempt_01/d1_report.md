# S6 relation mapping — D1 report

**Not frozen. First-prompt proposal only.**

Protocol §5.1–5.3, v1.3.3; decision rules D1. All nonempty subsets of actual relation labels are scored. Display labels never affect scores. Validation uses the first 30 rows with resolved query and bridge in SHA256("42" + row_id) order. An unresolved answer is a mismatch.

**D1: awaiting researcher tie decision.** 9/12 types PASS; 3 FAIL; 0 pending. PASS types cover 7377/7633 rows (96.65%). Global thresholds: at least 6 types and at least 70% row coverage.

| Construction | Types | Dataset rows | PASS types | PASS rows | FAIL types | Pending |
|---|---:|---:|---:|---:|---:|---:|
| BRIDGE | 8 | 6428 | 8 | 6428 | 0 | 0 |
| UNION | 1 | 949 | 1 | 949 | 0 | 0 |
| UNADOPTED | 3 | 256 | 0 | 0 | 3 | 0 |

## Per-type scores

Skipped counts include unresolved query/bridge rows encountered before the sample fills. Alternative scenarios are shown for every tied hop-1 set. NA tags have no uniquely adopted mapping.

| Relation type | Sample | Skipped | R1 | Hop 1 | BRIDGE hop 2 | UNION hop 2 | Construction | R2 | D1 | Ambiguity |
|---|---:|---:|---|---|---|---|---|---|---|---|
| disease:drug:effect/phenotype | 30 | 0 | ['indication'] | 30/30 (100.0%) | 15/30 (50.0%) | 30/30 (100.0%) | UNION | [['drug_effect']] | PASS | R1_AMBIGUOUS |
| disease:drug:gene/protein | 30 | 0 | ['indication'] | 30/30 (100.0%) | 30/30 (100.0%) | 30/30 (100.0%) | BRIDGE | [['drug_protein']] | PASS | R1_AMBIGUOUS |
| disease:effect/phenotype:drug | 30 | 0 | ['disease_phenotype_positive'] | 30/30 (100.0%) | 3/30 (10.0%) | 3/30 (10.0%) | neither | [] | FAIL | NA |
| disease:gene/protein:drug | 30 | 0 | ['disease_protein'] | 30/30 (100.0%) | 30/30 (100.0%) | 30/30 (100.0%) | BRIDGE | [['drug_protein']] | PASS | NONE |
| drug:disease:effect/phenotype | 30 | 0 | ['indication'] | 30/30 (100.0%) | 30/30 (100.0%) | 30/30 (100.0%) | BRIDGE | [['disease_phenotype_positive']] | PASS | BOTH_AMBIGUOUS |
| drug:disease:gene/protein | 30 | 0 | ['indication'] | 30/30 (100.0%) | 30/30 (100.0%) | 30/30 (100.0%) | BRIDGE | [['disease_protein']] | PASS | R1_AMBIGUOUS |
| drug:effect/phenotype:disease | 5 | 0 | ['drug_effect'] | 5/5 (100.0%) | 0/5 (0.0%) | 0/5 (0.0%) | neither | [] | FAIL | NA |
| drug:gene/protein:disease | 30 | 0 | ['drug_protein'] | 30/30 (100.0%) | 30/30 (100.0%) | 30/30 (100.0%) | BRIDGE | [['disease_protein']] | PASS | NONE |
| effect/phenotype:disease:drug | 30 | 0 | ['disease_phenotype_positive'] | 30/30 (100.0%) | 28/30 (93.3%) | 26/30 (86.7%) | BRIDGE | [['indication']] | PASS | BOTH_AMBIGUOUS |
| effect/phenotype:drug:disease | 30 | 0 | ['drug_effect'] | 30/30 (100.0%) | 26/30 (86.7%) | 20/30 (66.7%) | neither | [] | FAIL | NA |
| gene/protein:disease:drug | 30 | 0 | ['disease_protein'] | 30/30 (100.0%) | 30/30 (100.0%) | 30/30 (100.0%) | BRIDGE | [['indication']] | PASS | R2_AMBIGUOUS |
| gene/protein:drug:disease | 30 | 0 | ['drug_protein'] | 30/30 (100.0%) | 30/30 (100.0%) | 30/30 (100.0%) | BRIDGE | [['indication']] | PASS | R2_AMBIGUOUS |

## Candidate labels (display labels are informational)

| Relation type | Hop | Relation labels and display labels |
|---|---|---|
| disease:drug:effect/phenotype | hop1 | {"contraindication": ["contraindication"], "indication": ["indication"], "off-label use": ["off-label use"]} |
| disease:drug:effect/phenotype | hop2 | {"drug_effect": ["side effect"]} |
| disease:drug:gene/protein | hop1 | {"contraindication": ["contraindication"], "indication": ["indication"], "off-label use": ["off-label use"]} |
| disease:drug:gene/protein | hop2 | {"drug_protein": ["carrier", "enzyme", "target", "transporter"]} |
| disease:effect/phenotype:drug | hop1 | {"disease_phenotype_negative": ["phenotype absent"], "disease_phenotype_positive": ["phenotype present"]} |
| disease:effect/phenotype:drug | hop2 | {"drug_effect": ["side effect"]} |
| disease:gene/protein:drug | hop1 | {"disease_protein": ["associated with"]} |
| disease:gene/protein:drug | hop2 | {"drug_protein": ["carrier", "enzyme", "target", "transporter"]} |
| drug:disease:effect/phenotype | hop1 | {"contraindication": ["contraindication"], "indication": ["indication"], "off-label use": ["off-label use"]} |
| drug:disease:effect/phenotype | hop2 | {"disease_phenotype_negative": ["phenotype absent"], "disease_phenotype_positive": ["phenotype present"]} |
| drug:disease:gene/protein | hop1 | {"contraindication": ["contraindication"], "indication": ["indication"], "off-label use": ["off-label use"]} |
| drug:disease:gene/protein | hop2 | {"disease_protein": ["associated with"]} |
| drug:effect/phenotype:disease | hop1 | {"drug_effect": ["side effect"]} |
| drug:effect/phenotype:disease | hop2 | {"disease_phenotype_negative": ["phenotype absent"], "disease_phenotype_positive": ["phenotype present"]} |
| drug:gene/protein:disease | hop1 | {"drug_protein": ["carrier", "enzyme", "target", "transporter"]} |
| drug:gene/protein:disease | hop2 | {"disease_protein": ["associated with"]} |
| effect/phenotype:disease:drug | hop1 | {"disease_phenotype_negative": ["phenotype absent"], "disease_phenotype_positive": ["phenotype present"]} |
| effect/phenotype:disease:drug | hop2 | {"contraindication": ["contraindication"], "indication": ["indication"], "off-label use": ["off-label use"]} |
| effect/phenotype:drug:disease | hop1 | {"drug_effect": ["side effect"]} |
| effect/phenotype:drug:disease | hop2 | {"contraindication": ["contraindication"], "indication": ["indication"], "off-label use": ["off-label use"]} |
| gene/protein:disease:drug | hop1 | {"disease_protein": ["associated with"]} |
| gene/protein:disease:drug | hop2 | {"contraindication": ["contraindication"], "indication": ["indication"], "off-label use": ["off-label use"]} |
| gene/protein:drug:disease | hop1 | {"drug_protein": ["carrier", "enzyme", "target", "transporter"]} |
| gene/protein:drug:disease | hop2 | {"contraindication": ["contraindication"], "indication": ["indication"], "off-label use": ["off-label use"]} |

## Decisions and mismatch evidence

Examples below use each best-scoring label set, including ties. Complete missing/extra ID lists, all mismatch row IDs, sample IDs and skipped-row reasons are in `relation_mapping_proposed.json`. Examples show up to two rows per best set; long ID differences are summarized here only.

### disease:drug:effect/phenotype

- D1: PASS; reasons: none.
- Query/bridge rows skipped: 0; sampled rows with unresolved answers: 0.
- Hop-1 selection: SELECTED; sets: [['indication']].
- R1 ['indication']: only UNION reaches 90%.
- BRIDGE: SELECTED; sets [['drug_effect']]; score 15/30 (50.0%).
- BRIDGE, R2 ['drug_effect'], BH2_03879: s=36937 (clear cell renal carcinoma), bridge=15205 (Pazopanib); gold 271, reached 86; missing: 22229 (Hyperkeratosis); 22250 (Sinusitis); 22272 (Hypotonia); 22304 (Hearing impairment); 22323 (Muscle weakness); 22380 (Visual impairment); 22382 (Hemorrhage of the eye); 22447 (Anxiety); … (185 total); extra: none; unresolved: [].
- BRIDGE, R2 ['drug_effect'], BH2_03920: s=29113 (diabetic ketoacidosis), bridge=14329 (Insulin detemir); gold 156, reached 127; missing: 22398 (Behavioral abnormality); 22613 (Blurred vision); 22951 (Ketoacidosis); 23007 (Respiratory tract infection); 23010 (Abnormal lung morphology); 23011 (Dyspnea); 23135 (Dysarthria); 23267 (Tachypnea); … (29 total); extra: none; unresolved: [].
- UNION: SELECTED; sets [['drug_effect']]; score 30/30 (100.0%).

### disease:drug:gene/protein

- D1: PASS; reasons: none.
- Query/bridge rows skipped: 0; sampled rows with unresolved answers: 0.
- Hop-1 selection: SELECTED; sets: [['indication']].
- R1 ['indication']: both reach 90%; BRIDGE tie rule.
- BRIDGE: SELECTED; sets [['drug_protein']]; score 30/30 (100.0%).
- UNION: SELECTED; sets [['drug_protein']]; score 30/30 (100.0%).

### disease:effect/phenotype:drug

- D1: FAIL; reasons: hop-2 score below 90% under both constructions.
- Query/bridge rows skipped: 0; sampled rows with unresolved answers: 0.
- Hop-1 selection: SELECTED; sets: [['disease_phenotype_positive']].
- R1 ['disease_phenotype_positive']: neither construction reaches 90%.
- BRIDGE: SELECTED; sets [['drug_effect']]; score 3/30 (10.0%).
- BRIDGE, R2 ['drug_effect'], BH2_06128: s=37887 (pleural empyema (disease)), bridge=25150 (Pleural effusion); gold 44, reached 111; missing: none; extra: 14106 (Hydroxocobalamin); 14111 (Alitretinoin); 14155 (Gefitinib); 14165 (Rosiglitazone); 14204 (Sulindac); 14207 (Imatinib); 14229 (Tretinoin); 14251 (Tacrolimus); … (67 total); unresolved: [].
- BRIDGE, R2 ['drug_effect'], BH2_06120: s=30391 (microcephaly-intellectual disability-phalangeal and neurological anomalies syndrome), bridge=22675 (Intellectual disability); gold 14, reached 20; missing: none; extra: 14025 (Mitotane); 14164 (Alprazolam); 14560 (Ergocalciferol); 14686 (Clomifene); 14981 (Buprenorphine); 15856 (Naltrexone); unresolved: [].
- UNION: SELECTED; sets [['drug_effect']]; score 3/30 (10.0%).
- UNION, R2 ['drug_effect'], BH2_06128: s=37887 (pleural empyema (disease)), bridge=25150 (Pleural effusion); gold 44, reached 111; missing: none; extra: 14106 (Hydroxocobalamin); 14111 (Alitretinoin); 14155 (Gefitinib); 14165 (Rosiglitazone); 14204 (Sulindac); 14207 (Imatinib); 14229 (Tretinoin); 14251 (Tacrolimus); … (67 total); unresolved: [].
- UNION, R2 ['drug_effect'], BH2_06120: s=30391 (microcephaly-intellectual disability-phalangeal and neurological anomalies syndrome), bridge=22675 (Intellectual disability); gold 14, reached 20; missing: none; extra: 14025 (Mitotane); 14164 (Alprazolam); 14560 (Ergocalciferol); 14686 (Clomifene); 14981 (Buprenorphine); 15856 (Naltrexone); unresolved: [].

### disease:gene/protein:drug

- D1: PASS; reasons: none.
- Query/bridge rows skipped: 0; sampled rows with unresolved answers: 0.
- Hop-1 selection: SELECTED; sets: [['disease_protein']].
- R1 ['disease_protein']: both reach 90%; BRIDGE tie rule.
- BRIDGE: SELECTED; sets [['drug_protein']]; score 30/30 (100.0%).
- UNION: SELECTED; sets [['drug_protein']]; score 30/30 (100.0%).

### drug:disease:effect/phenotype

- D1: PASS; reasons: none.
- Query/bridge rows skipped: 0; sampled rows with unresolved answers: 0.
- Hop-1 selection: SELECTED; sets: [['indication']].
- R1 ['indication']: both reach 90%; BRIDGE tie rule.
- BRIDGE: SELECTED; sets [['disease_phenotype_positive']]; score 30/30 (100.0%).
- UNION: SELECTED; sets [['disease_phenotype_positive']]; score 30/30 (100.0%).

### drug:disease:gene/protein

- D1: PASS; reasons: none.
- Query/bridge rows skipped: 0; sampled rows with unresolved answers: 0.
- Hop-1 selection: SELECTED; sets: [['indication']].
- R1 ['indication']: both reach 90%; BRIDGE tie rule.
- BRIDGE: SELECTED; sets [['disease_protein']]; score 30/30 (100.0%).
- UNION: SELECTED; sets [['disease_protein']]; score 30/30 (100.0%).

### drug:effect/phenotype:disease

- D1: FAIL; reasons: fewer than 10 validation rows, hop-2 score below 90% under both constructions.
- Query/bridge rows skipped: 0; sampled rows with unresolved answers: 0.
- Hop-1 selection: SELECTED; sets: [['drug_effect']].
- R1 ['drug_effect']: neither construction reaches 90%.
- BRIDGE: TIE; sets [['disease_phenotype_negative'], ['disease_phenotype_positive']]; score 0/5 (0.0%).
- BRIDGE, R2 ['disease_phenotype_negative'], BH2_00004: s=14751 (Zinc sulfate), bridge=84409 (Nausea); gold 29, reached 0; missing: 27426 (fructose intolerance); 27502 (familial lipoprotein lipase deficiency); 28257 (Ehlers-Danlos syndrome, classic type); 28547 (Parkinson disease); 29457 (variegate porphyria); 29923 (lysinuric protein intolerance); 29924 (ovarian hyperstimulation syndrome); 30177 (migraine, familial typical, susceptibility to, 2); … (29 total); extra: none; unresolved: [].
- BRIDGE, R2 ['disease_phenotype_negative'], BH2_00003: s=14490 (Zinc chloride), bridge=89055 (Decreased circulating copper concentration); gold 3, reached 0; missing: 27983 (IRIDA syndrome); 30928 (MEDNIK syndrome); 32379 (COG2-CDG); extra: none; unresolved: [].
- BRIDGE, R2 ['disease_phenotype_positive'], BH2_00004: s=14751 (Zinc sulfate), bridge=84409 (Nausea); gold 29, reached 89; missing: none; extra: 27210 (Charcot-Marie-Tooth disease with ptosis and parkinsonism); 27691 (mitochondrial DNA depletion syndrome); 27699 (Caroli disease); 27702 (IgG4-related hepatopathy); 27723 (familial hyperaldosteronism); 27774 (liver neuroendocrine carcinoma); 27813 (episodic ataxia); 27832 (aldosterone-producing adenoma with seizures and neurological abnormalities); … (60 total); unresolved: [].
- BRIDGE, R2 ['disease_phenotype_positive'], BH2_00003: s=14490 (Zinc chloride), bridge=89055 (Decreased circulating copper concentration); gold 3, reached 5; missing: none; extra: 27772 (aceruloplasminemia); 28458 (familial benign copper deficiency); unresolved: [].
- UNION: TIE; sets [['disease_phenotype_negative'], ['disease_phenotype_positive']]; score 0/5 (0.0%).
- UNION, R2 ['disease_phenotype_negative'], BH2_00004: s=14751 (Zinc sulfate), bridge=84409 (Nausea); gold 29, reached 0; missing: 27426 (fructose intolerance); 27502 (familial lipoprotein lipase deficiency); 28257 (Ehlers-Danlos syndrome, classic type); 28547 (Parkinson disease); 29457 (variegate porphyria); 29923 (lysinuric protein intolerance); 29924 (ovarian hyperstimulation syndrome); 30177 (migraine, familial typical, susceptibility to, 2); … (29 total); extra: none; unresolved: [].
- UNION, R2 ['disease_phenotype_negative'], BH2_00003: s=14490 (Zinc chloride), bridge=89055 (Decreased circulating copper concentration); gold 3, reached 0; missing: 27983 (IRIDA syndrome); 30928 (MEDNIK syndrome); 32379 (COG2-CDG); extra: none; unresolved: [].
- UNION, R2 ['disease_phenotype_positive'], BH2_00004: s=14751 (Zinc sulfate), bridge=84409 (Nausea); gold 29, reached 89; missing: none; extra: 27210 (Charcot-Marie-Tooth disease with ptosis and parkinsonism); 27691 (mitochondrial DNA depletion syndrome); 27699 (Caroli disease); 27702 (IgG4-related hepatopathy); 27723 (familial hyperaldosteronism); 27774 (liver neuroendocrine carcinoma); 27813 (episodic ataxia); 27832 (aldosterone-producing adenoma with seizures and neurological abnormalities); … (60 total); unresolved: [].
- UNION, R2 ['disease_phenotype_positive'], BH2_00003: s=14490 (Zinc chloride), bridge=89055 (Decreased circulating copper concentration); gold 3, reached 5; missing: none; extra: 27772 (aceruloplasminemia); 28458 (familial benign copper deficiency); unresolved: [].

### drug:gene/protein:disease

- D1: PASS; reasons: none.
- Query/bridge rows skipped: 0; sampled rows with unresolved answers: 0.
- Hop-1 selection: SELECTED; sets: [['drug_protein']].
- R1 ['drug_protein']: both reach 90%; BRIDGE tie rule.
- BRIDGE: SELECTED; sets [['disease_protein']]; score 30/30 (100.0%).
- UNION: SELECTED; sets [['disease_protein']]; score 30/30 (100.0%).

### effect/phenotype:disease:drug

- D1: PASS; reasons: none.
- Query/bridge rows skipped: 0; sampled rows with unresolved answers: 0.
- Hop-1 selection: SELECTED; sets: [['disease_phenotype_positive']].
- R1 ['disease_phenotype_positive']: only BRIDGE reaches 90%.
- BRIDGE: SELECTED; sets [['indication']]; score 28/30 (93.3%).
- BRIDGE, R2 ['indication'], BH2_05949: s=23979 (Opportunistic infection), bridge=32524 (filarial elephantiasis); gold 2, reached 1; missing: 17112 (Filgrastim); extra: none; unresolved: [].
- BRIDGE, R2 ['indication'], BH2_06015: s=94369 (Pyrimidine-responsive megaloblastic anemia), bridge=31298 (orotic aciduria); gold 2, reached 1; missing: 20274 (Leucovorin); extra: none; unresolved: [].
- UNION: SELECTED; sets [['indication']]; score 26/30 (86.7%).
- UNION, R2 ['indication'], BH2_05686: s=89391 (Cephalohematoma), bridge=27656 (congenital prothrombin deficiency); gold 1, reached 15; missing: none; extra: 14557 (Turoctocog alfa pegol); 14594 (Albutrepenonacog alfa); 14595 (Desmopressin); 14619 (Antihemophilic factor, human recombinant); 14621 (Lonoctocog alfa); 14622 (Moroctocog alfa); 15975 (Coagulation Factor IX (Recombinant)); 15979 (Coagulation Factor IX Human); … (14 total); unresolved: [].
- UNION, R2 ['indication'], BH2_05843: s=88994 (Impaired ristocetin-induced platelet aggregation), bridge=27527 (Glanzmann thrombasthenia); gold 1, reached 4; missing: none; extra: 14699 (Lusutrombopag); 15799 (Avatrombopag); 17141 (Oprelvekin); unresolved: [].

### effect/phenotype:drug:disease

- D1: FAIL; reasons: hop-2 score below 90% under both constructions.
- Query/bridge rows skipped: 0; sampled rows with unresolved answers: 0.
- Hop-1 selection: SELECTED; sets: [['drug_effect']].
- R1 ['drug_effect']: neither construction reaches 90%.
- BRIDGE: SELECTED; sets [['indication']]; score 26/30 (86.7%).
- BRIDGE, R2 ['indication'], BH2_05081: s=25487 (Thyroid follicular adenoma), bridge=15490 (Pergolide); gold 4, reached 2; missing: 28017 (migraine with or without aura, susceptibility to); 37768 (migraine disorder); extra: none; unresolved: [].
- BRIDGE, R2 ['indication'], BH2_04897: s=84710 (Agoraphobia), bridge=15073 (Fluvoxamine); gold 9, reached 3; missing: 28313 (schizophrenia); 31912 (autism susceptibility 1); 37717 (autism spectrum disorder); 38242 (bipolar disorder); 83763 (manic bipolar affective disorder); 84310 (autism (disease)); extra: none; unresolved: [].
- UNION: SELECTED; sets [['indication']]; score 20/30 (66.7%).
- UNION, R2 ['indication'], BH2_04907: s=22699 (Ataxia), bridge=15859 (Raltegravir); gold 2, reached 26; missing: none; extra: 28764 (Sjogren syndrome); 28849 (colorectal cancer); 29078 (rheumatoid arthritis); 29945 (gastric cancer); 31380 (diffuse gastric adenocarcinoma); 31850 (seborrheic keratosis); 35916 (dry eye syndrome); 36000 (gastric neoplasm); … (24 total); unresolved: [].
- UNION, R2 ['indication'], BH2_04943: s=22784 (Decreased body weight), bridge=14881 (Phenylephrine); gold 12, reached 15; missing: none; extra: 28313 (schizophrenia); 38242 (bipolar disorder); 83763 (manic bipolar affective disorder); unresolved: [].

### gene/protein:disease:drug

- D1: PASS; reasons: none.
- Query/bridge rows skipped: 0; sampled rows with unresolved answers: 0.
- Hop-1 selection: SELECTED; sets: [['disease_protein']].
- R1 ['disease_protein']: both reach 90%; BRIDGE tie rule.
- BRIDGE: SELECTED; sets [['indication']]; score 30/30 (100.0%).
- UNION: SELECTED; sets [['indication']]; score 30/30 (100.0%).

### gene/protein:drug:disease

- D1: PASS; reasons: none.
- Query/bridge rows skipped: 0; sampled rows with unresolved answers: 0.
- Hop-1 selection: SELECTED; sets: [['drug_protein']].
- R1 ['drug_protein']: both reach 90%; BRIDGE tie rule.
- BRIDGE: SELECTED; sets [['indication']]; score 30/30 (100.0%).
- UNION: SELECTED; sets [['indication']]; score 30/30 (100.0%).

## Provenance

```json
{
  "biohopr_revision": "08f06692c3900347e7405ba55ff6a6d330f55ddb",
  "elapsed_seconds": 12.915,
  "git_commit": "a7ffef583368e2d77b3389fbd02e0ec8778bf23d",
  "kg_fingerprint": "bc5d3fd2f12aeb29398fe4684c83d8c65c7bd5c1edf704573322295bdc6b2e95",
  "protocol_version": "1.3.3",
  "run_time_utc": "2026-10-13T01:45:52+00:00",
  "sha256": {
    "configs/frozen_hashes.yaml": "6d88c898cd0a8207aae366ec940824cd6828f2fce41d04d6abba2f62b69d83fe",
    "data/raw/biohopr/BioHopR.json": "1adda2f23d305c394537e7b56d3e972b2d8f4141ae716ede54e0d08876eb527d",
    "docs/decision_rules.md": "c007b1afb96c2b1967fc3ba5964d0dcfdf0197ba0039d71a46c46febbe222175",
    "docs/frozen_pilot_protocol.md": "a73346aa75bea142e426687af3b109d50c66703a61e2189a9b22f01ddd297582",
    "results/semantics/field_roles_summary.json": "6c8e9400db47b9175c76b99588285ddc04a66fc7b6a6b08aaa83c3458fe7605f",
    "scripts/06_relation_mapping.py": "60876f35cc03adb7f290f08b195e581c80f2825fc251b54dc764c0c167d5c6f0",
    "src/cofail_kg/__init__.py": "e3b0c44298fc1c149afbf4c8996fb92427ae41e4649b934ca495991b7852b855",
    "src/cofail_kg/agents/__init__.py": "e3b0c44298fc1c149afbf4c8996fb92427ae41e4649b934ca495991b7852b855",
    "src/cofail_kg/analysis/__init__.py": "e3b0c44298fc1c149afbf4c8996fb92427ae41e4649b934ca495991b7852b855",
    "src/cofail_kg/data/__init__.py": "e3b0c44298fc1c149afbf4c8996fb92427ae41e4649b934ca495991b7852b855",
    "src/cofail_kg/data/biohopr_loader.py": "0ab1de558c393c1b5a68c3fba7c3e2b688c72b00f300951fe3b4826a92f41a2a",
    "src/cofail_kg/data/diagnostics.py": "9c0ca21667702af80892daadf78991a13415f5efcef1b5af73bdcb8eff3d33e3",
    "src/cofail_kg/data/field_roles.py": "2058c020f46649d2e009c1849fb5f59ace3ba787a7102efb3d859b69dc7818ee",
    "src/cofail_kg/evaluation/__init__.py": "e3b0c44298fc1c149afbf4c8996fb92427ae41e4649b934ca495991b7852b855",
    "src/cofail_kg/evaluation/normalize.py": "9f5dd89b93f9a89c2406fa47e2f9b0151e47307bd02d0cbb8b20b95b02e7c4e8",
    "src/cofail_kg/evaluation/relation_mapping.py": "f195f3ac5d10f3d0191e7a354ab5cf2a958ff8c7d60d20d7bd1756bc47ac09d2",
    "src/cofail_kg/kg/__init__.py": "e3b0c44298fc1c149afbf4c8996fb92427ae41e4649b934ca495991b7852b855",
    "src/cofail_kg/kg/prepare.py": "0852293aee83bd7878417f33b71628ba8c10f1568065c2b77b510802f80d1eb1",
    "src/cofail_kg/kg/primekg_index.py": "3d1545d07ba5553c75568b548ad0730b018b2e8fe0e436b205a08a5adbbb61a2",
    "src/cofail_kg/utils/__init__.py": "e3b0c44298fc1c149afbf4c8996fb92427ae41e4649b934ca495991b7852b855",
    "src/cofail_kg/utils/frozen_hashes.py": "c6f03344020be7fb85a62af5adc0dcb16807a89b574378bc0d3afe23d0ee75bf"
  }
}
```
