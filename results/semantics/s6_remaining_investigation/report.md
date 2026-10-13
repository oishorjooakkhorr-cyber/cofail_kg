# S6: remaining failures and construction mixtures

Date: 2026-10-13. Scope: both remaining failed types, on their original 30-row S6 validation samples. Diagnostic only; no mapping, exclusion, threshold, normalization, or protocol change. Protocol sections 3.1, 3.2, 5.1, 5.3 and 12; decision rule D1.

## Main results

| Type | Dataset rows | Validation rows | Hop 1 | Best BRIDGE | Best UNION | Current D1 |
|---|---:|---:|---:|---:|---:|---|
| disease:effect/phenotype:drug | 36 | 30 | 30/30 | 3/30 (10%) | 3/30 (10%) | FAIL |
| effect/phenotype:drug:disease | 215 | 30 | 30/30 | 26/30 (86.67%) | 20/30 (66.67%) | FAIL |

The 90% threshold requires 27/30. Neither type has a construction that reaches it. Both have enough validation rows; every query, bridge and reference answer in the samples resolves, with no skipped validation rows. All 36 and 215 available query/bridge pairs resolve. The sample size is 30 because section 5.1 caps it at 30, not because other rows fail resolution.

## Permitted D1 investigation

- Field roles: all type fields agree. The original S5 outcome remains PASS for both types (5/5 supporting in each original S5 sample). A separate support check on the larger, fixed S6 samples supports 30/30 and 29/30 respectively. The latter conflict is BH2_05027, detailed below; this does not rerun or replace the frozen S5 gate.
- Edge storage: scanned all 8,100,498 raw edges. Outgoing-only and incoming-only results each equal the cached, either-direction results for selected-R1 bridges and every R2 subset under both constructions on all 60 validation rows. No orientation or cache discrepancy explains these failures.
- Release: raw SHA256s match frozen metadata; metadata matches the frozen KG fingerprint; raw MD5s match the publisher checksums recorded at S4; the pinned BioHopR revision and loader integrity checks pass. This verifies the local files against the recorded release; it does not establish which upstream generation choices produced every BioHopR answer list.
- Candidate labels: the original full per-type S6 results reproduce exactly. All nonempty R2 subsets were independently evaluated below. No better permitted candidate repairs either failure.

## Construction mixture (exploratory)

Each row is compared with both constructions using the same best label set. BOTH counts in both original scores, but only once in the either-construction total.

| Type | BOTH | BRIDGE only | UNION only | NEITHER | Either exact |
|---|---:|---:|---:|---:|---:|
| disease:effect/phenotype:drug | 3 | 0 | 0 | 27 | 3/30 (10%) |
| effect/phenotype:drug:disease | 17 | 9 | 3 | 1 | 29/30 (96.67%) |

For disease:effect/phenotype:drug, all 30 samples have one valid bridge, so BRIDGE and UNION are identical. All 27 failures contain all reference drugs plus extras. Mixing constructions cannot help. The evidence establishes a set-size mismatch, not the upstream cause of the smaller reference lists.

For effect/phenotype:drug:disease, the nine BRIDGE-only rows gain extra diseases under UNION. The three UNION-only rows omit reference diseases under BRIDGE and recover them via other valid drug bridges under UNION. The remaining row has both one extra and one missing disease under either construction. The observed reference sets fit different constructions on different rows, but this does not prove how BioHopR generated them.

The 29/30 figure uses reference answers to choose which construction matches each row. It is an oracle diagnostic, not a validated selector and not a D1 pass. Section 5.3 requires one construction per type. Adopting a mixed rule after observing these data would be exploratory. No mixed selector, full-dataset mixture estimate, or measured cofailure effect is claimed. No agent episodes were run.

## Identity conflict BH2_05027

Query: Neuropathic arthropathy (85260). Stored and only valid drug bridge: Methylprednisolone (14269). Both constructions reach 118 diseases against 118 reference diseases, with 117 shared.

- Raw BioHopR answer is `acute lymphoblastic leukemia ` (trailing space).
- Section 12 trims it and finds the exact disease name: node 35852, source MONDO_grouped, source ID 3541_870.
- The graph instead reaches node 33621, `acute lymphoblastic leukemia (disease)`, source MONDO, source ID 4967.
- The suffix retry applies only when the exact match finds no disease node, so it correctly does not fire here.
- No tested drug-disease label subset reaches reference node 35852 through the valid drug bridge.

This is a documented reference/graph node-identity conflict, not an unresolved name or demonstrated resolver bug. Similar names and a trailing space do not establish that the nodes can be merged. Preferentially remapping to the connected node would use the desired answer path to change identity. No remapping is applied. Even if a separately justified correction made this one row exact, BRIDGE would become 27/30; that is a counterfactual only and is not used as the official score.

## Every candidate R2 subset

### disease:effect/phenotype:drug

R1: disease_phenotype_positive.

| R2 subset | BRIDGE matches | UNION matches |
|---|---:|---:|
| drug_effect | 3/30 | 3/30 |

### effect/phenotype:drug:disease

R1: drug_effect.

| R2 subset | BRIDGE matches | UNION matches |
|---|---:|---:|
| contraindication | 0/30 | 0/30 |
| indication | 26/30 | 20/30 |
| off-label use | 0/30 | 0/30 |
| contraindication, indication | 3/30 | 1/30 |
| contraindication, off-label use | 0/30 | 0/30 |
| indication, off-label use | 14/30 | 10/30 |
| contraindication, indication, off-label use | 3/30 | 1/30 |

## Named validation examples

Full reference, reached, extra and missing sets follow, ordered by numeric canonical ID. The first two BRIDGE failures in each type use the original validation order. Additional examples show a BRIDGE-only row and the identity conflict. All 60 rows and every candidate are preserved in evidence.json; mixtures.csv lists the per-row counts.

### BH2_06128 — disease:effect/phenotype:drug

Name all drugs that have a side effect which is also a phenotype of a disease pleural empyema .

Query: pleural empyema (disease) [37887]. Stored bridge: Pleural effusion [25150].

Valid bridges: Pleural effusion [25150]

Category: NEITHER. R2: drug_effect.

Reference (44): Argatroban [14146]; Valproic acid [14153]; Acetaminophen [14154]; Fluoxetine [14176]; Ciprofloxacin [14188]; Methotrexate [14194]; Fentanyl [14241]; Doxorubicin [14275]; Letrozole [14277]; Amiodarone [14302]; Levofloxacin [14309]; Dantrolene [14511]; Ifosfamide [14608]; Epirubicin [14719]; Busulfan [14738]; Paclitaxel [14792]; Docetaxel [14793]; Nisoldipine [14946]; Cyclophosphamide [14954]; Cevimeline [15075]; Clozapine [15093]; Bicalutamide [15143]; Nitrofurantoin [15273]; Moxifloxacin [15289]; Anagrelide [15290]; Ofloxacin [15326]; Gemcitabine [15413]; Azacitidine [15414]; Azithromycin [15419]; Methysergide [15423]; Cabergoline [15424]; Lisuride [15448]; Amphotericin B [15456]; Felbamate [15475]; Pergolide [15490]; Bromocriptine [15493]; Mycophenolic acid [15842]; Minoxidil [15855]; Mesalazine [15876]; Epoprostenol [16331]; Lisinopril [16690]; Pamidronic acid [17727]; Ganciclovir [20263]; Iopromide [20806]

BRIDGE reached (111): Hydroxocobalamin [14106]; Alitretinoin [14111]; Argatroban [14146]; Valproic acid [14153]; Acetaminophen [14154]; Gefitinib [14155]; Rosiglitazone [14165]; Fluoxetine [14176]; Ciprofloxacin [14188]; Methotrexate [14194]; Sulindac [14204]; Imatinib [14207]; Tretinoin [14229]; Fentanyl [14241]; Tacrolimus [14251]; Isotretinoin [14271]; Doxorubicin [14275]; Letrozole [14277]; Amiodarone [14302]; Levofloxacin [14309]; Arsenic trioxide [14313]; Dantrolene [14511]; Voriconazole [14602]; Thalidomide [14606]; Ifosfamide [14608]; Chenodeoxycholic acid [14711]; Decitabine [14713]; Epirubicin [14719]; Busulfan [14738]; Capecitabine [14758]; Bivalirudin [14770]; Paclitaxel [14792]; Docetaxel [14793]; Dasatinib [14794]; Insulin human [14799]; Procainamide [14852]; Aprotinin [14871]; Procarbazine [14914]; Nelarabine [14919]; Sorafenib [14945]; Nisoldipine [14946]; Cyclophosphamide [14954]; Sirolimus [14975]; Zaleplon [14982]; Sunitinib [15002]; Temsirolimus [15012]; Ambrisentan [15014]; Cevimeline [15075]; Esmolol [15076]; Bortezomib [15077]; Clozapine [15093]; Dexmedetomidine [15111]; Selegiline [15138]; Bicalutamide [15143]; Propafenone [15150]; Everolimus [15176]; Nilotinib [15187]; Nitrofurantoin [15273]; Insulin pork [15287]; Interferon alfa-2b [15288]; Moxifloxacin [15289]; Anagrelide [15290]; Ropivacaine [15292]; Riluzole [15308]; Ofloxacin [15326]; Rasagiline [15333]; Insulin beef [15378]; Gemcitabine [15413]; Azacitidine [15414]; Azithromycin [15419]; Methysergide [15423]; Cabergoline [15424]; Bexarotene [15428]; Caspofungin [15443]; Valdecoxib [15447]; Lisuride [15448]; Amphotericin B [15456]; Felbamate [15475]; Topotecan [15481]; Pergolide [15490]; Bromocriptine [15493]; Rifapentine [15494]; Sitaxentan [15562]; Clofarabine [15805]; Ursodeoxycholic acid [15822]; Mycophenolic acid [15842]; Minoxidil [15855]; Mesalazine [15876]; Balsalazide [15985]; Epoprostenol [16331]; Pegaptanib [16512]; Nafarelin [16575]; Lisinopril [16690]; Lenalidomide [16753]; Remifentanil [17152]; Rivastigmine [17174]; Porfimer sodium [17335]; Pregabalin [17558]; Pamidronic acid [17727]; Zoledronic acid [17728]; Glatiramer [19324]; Mifamurtide [19356]; Valganciclovir [20215]; Ganciclovir [20263]; Tigecycline [20344]; Meropenem [20351]; Ertapenem [20360]; Anidulafungin [20433]; Daptomycin [20456]; Cefpodoxime [20657]; Iopromide [20806]

BRIDGE extra (67): Hydroxocobalamin [14106]; Alitretinoin [14111]; Gefitinib [14155]; Rosiglitazone [14165]; Sulindac [14204]; Imatinib [14207]; Tretinoin [14229]; Tacrolimus [14251]; Isotretinoin [14271]; Arsenic trioxide [14313]; Voriconazole [14602]; Thalidomide [14606]; Chenodeoxycholic acid [14711]; Decitabine [14713]; Capecitabine [14758]; Bivalirudin [14770]; Dasatinib [14794]; Insulin human [14799]; Procainamide [14852]; Aprotinin [14871]; Procarbazine [14914]; Nelarabine [14919]; Sorafenib [14945]; Sirolimus [14975]; Zaleplon [14982]; Sunitinib [15002]; Temsirolimus [15012]; Ambrisentan [15014]; Esmolol [15076]; Bortezomib [15077]; Dexmedetomidine [15111]; Selegiline [15138]; Propafenone [15150]; Everolimus [15176]; Nilotinib [15187]; Insulin pork [15287]; Interferon alfa-2b [15288]; Ropivacaine [15292]; Riluzole [15308]; Rasagiline [15333]; Insulin beef [15378]; Bexarotene [15428]; Caspofungin [15443]; Valdecoxib [15447]; Topotecan [15481]; Rifapentine [15494]; Sitaxentan [15562]; Clofarabine [15805]; Ursodeoxycholic acid [15822]; Balsalazide [15985]; Pegaptanib [16512]; Nafarelin [16575]; Lenalidomide [16753]; Remifentanil [17152]; Rivastigmine [17174]; Porfimer sodium [17335]; Pregabalin [17558]; Zoledronic acid [17728]; Glatiramer [19324]; Mifamurtide [19356]; Valganciclovir [20215]; Tigecycline [20344]; Meropenem [20351]; Ertapenem [20360]; Anidulafungin [20433]; Daptomycin [20456]; Cefpodoxime [20657]

BRIDGE missing (0): None.

UNION reached (111): Hydroxocobalamin [14106]; Alitretinoin [14111]; Argatroban [14146]; Valproic acid [14153]; Acetaminophen [14154]; Gefitinib [14155]; Rosiglitazone [14165]; Fluoxetine [14176]; Ciprofloxacin [14188]; Methotrexate [14194]; Sulindac [14204]; Imatinib [14207]; Tretinoin [14229]; Fentanyl [14241]; Tacrolimus [14251]; Isotretinoin [14271]; Doxorubicin [14275]; Letrozole [14277]; Amiodarone [14302]; Levofloxacin [14309]; Arsenic trioxide [14313]; Dantrolene [14511]; Voriconazole [14602]; Thalidomide [14606]; Ifosfamide [14608]; Chenodeoxycholic acid [14711]; Decitabine [14713]; Epirubicin [14719]; Busulfan [14738]; Capecitabine [14758]; Bivalirudin [14770]; Paclitaxel [14792]; Docetaxel [14793]; Dasatinib [14794]; Insulin human [14799]; Procainamide [14852]; Aprotinin [14871]; Procarbazine [14914]; Nelarabine [14919]; Sorafenib [14945]; Nisoldipine [14946]; Cyclophosphamide [14954]; Sirolimus [14975]; Zaleplon [14982]; Sunitinib [15002]; Temsirolimus [15012]; Ambrisentan [15014]; Cevimeline [15075]; Esmolol [15076]; Bortezomib [15077]; Clozapine [15093]; Dexmedetomidine [15111]; Selegiline [15138]; Bicalutamide [15143]; Propafenone [15150]; Everolimus [15176]; Nilotinib [15187]; Nitrofurantoin [15273]; Insulin pork [15287]; Interferon alfa-2b [15288]; Moxifloxacin [15289]; Anagrelide [15290]; Ropivacaine [15292]; Riluzole [15308]; Ofloxacin [15326]; Rasagiline [15333]; Insulin beef [15378]; Gemcitabine [15413]; Azacitidine [15414]; Azithromycin [15419]; Methysergide [15423]; Cabergoline [15424]; Bexarotene [15428]; Caspofungin [15443]; Valdecoxib [15447]; Lisuride [15448]; Amphotericin B [15456]; Felbamate [15475]; Topotecan [15481]; Pergolide [15490]; Bromocriptine [15493]; Rifapentine [15494]; Sitaxentan [15562]; Clofarabine [15805]; Ursodeoxycholic acid [15822]; Mycophenolic acid [15842]; Minoxidil [15855]; Mesalazine [15876]; Balsalazide [15985]; Epoprostenol [16331]; Pegaptanib [16512]; Nafarelin [16575]; Lisinopril [16690]; Lenalidomide [16753]; Remifentanil [17152]; Rivastigmine [17174]; Porfimer sodium [17335]; Pregabalin [17558]; Pamidronic acid [17727]; Zoledronic acid [17728]; Glatiramer [19324]; Mifamurtide [19356]; Valganciclovir [20215]; Ganciclovir [20263]; Tigecycline [20344]; Meropenem [20351]; Ertapenem [20360]; Anidulafungin [20433]; Daptomycin [20456]; Cefpodoxime [20657]; Iopromide [20806]

UNION extra (67): Hydroxocobalamin [14106]; Alitretinoin [14111]; Gefitinib [14155]; Rosiglitazone [14165]; Sulindac [14204]; Imatinib [14207]; Tretinoin [14229]; Tacrolimus [14251]; Isotretinoin [14271]; Arsenic trioxide [14313]; Voriconazole [14602]; Thalidomide [14606]; Chenodeoxycholic acid [14711]; Decitabine [14713]; Capecitabine [14758]; Bivalirudin [14770]; Dasatinib [14794]; Insulin human [14799]; Procainamide [14852]; Aprotinin [14871]; Procarbazine [14914]; Nelarabine [14919]; Sorafenib [14945]; Sirolimus [14975]; Zaleplon [14982]; Sunitinib [15002]; Temsirolimus [15012]; Ambrisentan [15014]; Esmolol [15076]; Bortezomib [15077]; Dexmedetomidine [15111]; Selegiline [15138]; Propafenone [15150]; Everolimus [15176]; Nilotinib [15187]; Insulin pork [15287]; Interferon alfa-2b [15288]; Ropivacaine [15292]; Riluzole [15308]; Rasagiline [15333]; Insulin beef [15378]; Bexarotene [15428]; Caspofungin [15443]; Valdecoxib [15447]; Topotecan [15481]; Rifapentine [15494]; Sitaxentan [15562]; Clofarabine [15805]; Ursodeoxycholic acid [15822]; Balsalazide [15985]; Pegaptanib [16512]; Nafarelin [16575]; Lenalidomide [16753]; Remifentanil [17152]; Rivastigmine [17174]; Porfimer sodium [17335]; Pregabalin [17558]; Zoledronic acid [17728]; Glatiramer [19324]; Mifamurtide [19356]; Valganciclovir [20215]; Tigecycline [20344]; Meropenem [20351]; Ertapenem [20360]; Anidulafungin [20433]; Daptomycin [20456]; Cefpodoxime [20657]

UNION missing (0): None.

### BH2_06120 — disease:effect/phenotype:drug

Name all drugs that have a side effect which is also a phenotype of a disease microcephaly-intellectual disability-phalangeal and neurological anomalies syndrome.

Query: microcephaly-intellectual disability-phalangeal and neurological anomalies syndrome [30391]. Stored bridge: Intellectual disability [22675].

Valid bridges: Intellectual disability [22675]

Category: NEITHER. R2: drug_effect.

Reference (14): Topiramate [14144]; Aripiprazole [14323]; Capecitabine [14758]; Nelarabine [14919]; Quetiapine [14999]; Tramadol [15078]; Tapentadol [15199]; Tolcapone [15772]; Vigabatrin [15782]; Degarelix [16578]; Ziconotide [17028]; Pregabalin [17558]; Varenicline [17889]; Febuxostat [19245]

BRIDGE reached (20): Mitotane [14025]; Topiramate [14144]; Alprazolam [14164]; Aripiprazole [14323]; Ergocalciferol [14560]; Clomifene [14686]; Capecitabine [14758]; Nelarabine [14919]; Buprenorphine [14981]; Quetiapine [14999]; Tramadol [15078]; Tapentadol [15199]; Tolcapone [15772]; Vigabatrin [15782]; Naltrexone [15856]; Degarelix [16578]; Ziconotide [17028]; Pregabalin [17558]; Varenicline [17889]; Febuxostat [19245]

BRIDGE extra (6): Mitotane [14025]; Alprazolam [14164]; Ergocalciferol [14560]; Clomifene [14686]; Buprenorphine [14981]; Naltrexone [15856]

BRIDGE missing (0): None.

UNION reached (20): Mitotane [14025]; Topiramate [14144]; Alprazolam [14164]; Aripiprazole [14323]; Ergocalciferol [14560]; Clomifene [14686]; Capecitabine [14758]; Nelarabine [14919]; Buprenorphine [14981]; Quetiapine [14999]; Tramadol [15078]; Tapentadol [15199]; Tolcapone [15772]; Vigabatrin [15782]; Naltrexone [15856]; Degarelix [16578]; Ziconotide [17028]; Pregabalin [17558]; Varenicline [17889]; Febuxostat [19245]

UNION extra (6): Mitotane [14025]; Alprazolam [14164]; Ergocalciferol [14560]; Clomifene [14686]; Buprenorphine [14981]; Naltrexone [15856]

UNION missing (0): None.

### BH2_05081 — effect/phenotype:drug:disease

Name all diseases that are treated by a drug that has side effect Thyroid follicular adenoma.

Query: Thyroid follicular adenoma [25487]. Stored bridge: Pergolide [15490].

Valid bridges: Eletriptan [14596]; Pergolide [15490]

Category: UNION_ONLY. R2: indication.

Reference (4): migraine with or without aura, susceptibility to [28017]; Parkinson disease [28547]; parkinsonian disorder [37706]; migraine disorder [37768]

BRIDGE reached (2): Parkinson disease [28547]; parkinsonian disorder [37706]

BRIDGE extra (0): None.

BRIDGE missing (2): migraine with or without aura, susceptibility to [28017]; migraine disorder [37768]

UNION reached (4): migraine with or without aura, susceptibility to [28017]; Parkinson disease [28547]; parkinsonian disorder [37706]; migraine disorder [37768]

UNION extra (0): None.

UNION missing (0): None.

### BH2_04897 — effect/phenotype:drug:disease

Name all diseases that are treated by a drug that has side effect Agoraphobia.

Query: Agoraphobia [84710]. Stored bridge: Fluvoxamine [15073].

Valid bridges: Aripiprazole [14323]; Fluvoxamine [15073]

Category: UNION_ONLY. R2: indication.

Reference (9): schizophrenia [28313]; obsessive-compulsive disorder [28899]; autism susceptibility 1 [31912]; phobic disorder [36105]; autism spectrum disorder [37717]; bipolar disorder [38242]; manic bipolar affective disorder [83763]; social phobia [83904]; autism (disease) [84310]

BRIDGE reached (3): obsessive-compulsive disorder [28899]; phobic disorder [36105]; social phobia [83904]

BRIDGE extra (0): None.

BRIDGE missing (6): schizophrenia [28313]; autism susceptibility 1 [31912]; autism spectrum disorder [37717]; bipolar disorder [38242]; manic bipolar affective disorder [83763]; autism (disease) [84310]

UNION reached (9): schizophrenia [28313]; obsessive-compulsive disorder [28899]; autism susceptibility 1 [31912]; phobic disorder [36105]; autism spectrum disorder [37717]; bipolar disorder [38242]; manic bipolar affective disorder [83763]; social phobia [83904]; autism (disease) [84310]

UNION extra (0): None.

UNION missing (0): None.

### BH2_04907 — effect/phenotype:drug:disease

Name all diseases that are treated by a drug that has side effect Ataxia.

Query: Ataxia [22699]. Stored bridge: Raltegravir [15859].

Valid bridges: Fluorouracil [14190]; Amiodarone [14302]; Cyclosporine [14934]; Raltegravir [15859]

Category: BRIDGE_ONLY. R2: indication.

Reference (2): HIV infectious disease [37805]; AIDS [84072]

BRIDGE reached (2): HIV infectious disease [37805]; AIDS [84072]

BRIDGE extra (0): None.

BRIDGE missing (0): None.

UNION reached (26): Sjogren syndrome [28764]; colorectal cancer [28849]; rheumatoid arthritis [29078]; gastric cancer [29945]; diffuse gastric adenocarcinoma [31380]; seborrheic keratosis [31850]; dry eye syndrome [35916]; gastric neoplasm [36000]; malignant colon neoplasm [36223]; colonic neoplasm [36581]; skin disease [36644]; pancreatic adenocarcinoma [36881]; squamous cell carcinoma of colon [37144]; gastric carcinoma [37273]; HIV infectious disease [37805]; inverted follicular keratosis [38031]; keratoacanthoma [39470]; ventricular fibrillation (disease) [39880]; superficial multifocal basal cell carcinoma [83755]; actinic keratosis (disease) [83756]; actinic cheilitis [83757]; melanoacanthoma [83758]; metastasis from malignant tumor of colon [83825]; gastric linitis plastica [83899]; xerophthalmia [83938]; AIDS [84072]

UNION extra (24): Sjogren syndrome [28764]; colorectal cancer [28849]; rheumatoid arthritis [29078]; gastric cancer [29945]; diffuse gastric adenocarcinoma [31380]; seborrheic keratosis [31850]; dry eye syndrome [35916]; gastric neoplasm [36000]; malignant colon neoplasm [36223]; colonic neoplasm [36581]; skin disease [36644]; pancreatic adenocarcinoma [36881]; squamous cell carcinoma of colon [37144]; gastric carcinoma [37273]; inverted follicular keratosis [38031]; keratoacanthoma [39470]; ventricular fibrillation (disease) [39880]; superficial multifocal basal cell carcinoma [83755]; actinic keratosis (disease) [83756]; actinic cheilitis [83757]; melanoacanthoma [83758]; metastasis from malignant tumor of colon [83825]; gastric linitis plastica [83899]; xerophthalmia [83938]

UNION missing (0): None.

### BH2_05027 — effect/phenotype:drug:disease

Name all diseases that are treated by a drug that has side effect Neuropathic arthropathy.

Query: Neuropathic arthropathy [85260]. Stored bridge: Methylprednisolone [14269].

Valid bridges: Methylprednisolone [14269]

Category: NEITHER. R2: indication.

Reference (118): spondyloarthropathy, susceptibility to [27366]; Diamond-Blackfan anemia [27452]; familial glucocorticoid deficiency [27648]; X-linked adrenal hypoplasia congenita [27878]; inflammatory bowel disease [28158]; autoimmune disease [28478]; leukemia, lymphocytic, susceptibility to [28830]; rheumatoid arthritis [29078]; systemic lupus erythematosus (disease) [29182]; dermatitis, atopic [29709]; chondrocalcinosis [29715]; hereditary angioedema [29854]; classic Hodgkin lymphoma [29993]; lymphoma, non-Hodgkin, familial [30447]; familial adrenal hypoplasia with absent pituitary luteinizing hormone [30602]; acute lymphoblastic/lymphocytic leukemia [30654]; juvenile arthritis due to defect in LACC1 [30800]; Addison disease [30813]; mycosis fungoides and variants [30990]; autoimmune thrombocytopenic [31511]; autoimmune hemolytic anemia [31723]; seborrheic keratosis [31850]; juvenile idiopathic arthritis [32325]; adrenal insufficiency [32384]; mantle cell lymphoma [32531]; heparin-induced thrombocytopenia (disease) [32563]; inherited isolated adrenal insufficiency due to partial CYP11A1 deficiency [32584]; Stevens-Johnson syndrome [32746]; Trichinellosis [32815]; sarcoidosis [32967]; Hodgkins lymphoma [33077]; eosinophilic pneumonia [33206]; follicular lymphoma [33294]; dermatitis herpetiformis [33410]; granulomatous slack skin disease [33452]; pediatric systemic lupus erythematosus [33534]; thyroiditis (disease) [33576]; aspiration pneumonia (disease) [33596]; exanthem (disease) [33649]; seborrheic dermatitis [33651]; asthma [33675]; adrenogenital syndrome [35510]; non-Hodgkin lymphoma [35650]; B-cell neoplasm [35651]; disease of orbital region [35665]; musculoskeletal system disease [35750]; eye disease [35823]; acute lymphoblastic leukemia [35852]; lymphoma [35970]; tendinitis [35992]; atopic eczema [36129]; spondyloarthropathy [36265]; bursitis [36272]; synovitis (disease) [36347]; rheumatic heart disease [36433]; tenosynovitis [36436]; Langerhans cell histiocytosis [36458]; exostosis [36562]; nephrotic syndrome [36604]; skin disease [36644]; neoplasm of mature B-cells [36724]; pneumonitis [37541]; multiple sclerosis [37722]; contact dermatitis [37770]; Crohn disease [37784]; allergic rhinitis [37888]; pemphigus [38016]; lichen disease [38021]; psoriasis [38024]; lupus erythematosus [38342]; inherited aplastic anemia [38496]; congenital adrenal hyperplasia [38513]; chronic primary adrenal insufficiency [38515]; adrenocortical insufficiency [38666]; primary cutaneous T-cell non-Hodgkin lymphoma [38708]; familial nephrotic syndrome [38719]; acquired angioedema [39111]; primary cutaneous T-cell lymphoma [39208]; pulmonary eosinophilia [39506]; psoriatic arthritis [39524]; chronic cutaneous lupus erythematosus [39533]; angioedema [39540]; acquired thrombocytopenia [39546]; parapsoriasis [39728]; allergic asthma [39773]; trichinosis [39808]; ankylosing spondylitis [39820]; actinic keratosis (disease) [83756]; humoral hypercalcemia of malignancy [83767]; precursor T-cell acute lymphoblastic leukemia [83769]; Crohn's colitis [83770]; renin-angiotensin-aldosterone system-blocker-induced angioedema [83772]; non-histaminic angioedema [83773]; lipoid nephrosis [83774]; brain edema [83775]; occupational dermatitis [83777]; fetal erythroblastosis [83780]; intrinsic asthma [83781]; exfoliative dermatitis [83782]; enterobiasis [83783]; Trichinella spiralis infectious disease [83784]; folliculotropic mycosis fungoides [83785]; localized pagetoid reticulosis [83786]; periarthritis [83787]; erythema multiforme [83788]; serum sickness [83789]; gout [83790]; vasomotor rhinitis [83791]; obsolete Hodgkin's granuloma [83792]; Hodgkin's paragranuloma [83793]; classic Hodgkin lymphoma, lymphocyte-rich type [83794]; chronic beryllium disease [83795]; lymphosarcoma [83796]; granuloma annulare [83882]; neurodermatitis [84028]; discoid lupus erythematosus [84030]; epicondylitis [84040]; miliary tuberculosis [84044]

BRIDGE reached (118): spondyloarthropathy, susceptibility to [27366]; Diamond-Blackfan anemia [27452]; familial glucocorticoid deficiency [27648]; X-linked adrenal hypoplasia congenita [27878]; inflammatory bowel disease [28158]; autoimmune disease [28478]; leukemia, lymphocytic, susceptibility to [28830]; rheumatoid arthritis [29078]; systemic lupus erythematosus (disease) [29182]; dermatitis, atopic [29709]; chondrocalcinosis [29715]; hereditary angioedema [29854]; classic Hodgkin lymphoma [29993]; lymphoma, non-Hodgkin, familial [30447]; familial adrenal hypoplasia with absent pituitary luteinizing hormone [30602]; acute lymphoblastic/lymphocytic leukemia [30654]; juvenile arthritis due to defect in LACC1 [30800]; Addison disease [30813]; mycosis fungoides and variants [30990]; autoimmune thrombocytopenic [31511]; autoimmune hemolytic anemia [31723]; seborrheic keratosis [31850]; juvenile idiopathic arthritis [32325]; adrenal insufficiency [32384]; mantle cell lymphoma [32531]; heparin-induced thrombocytopenia (disease) [32563]; inherited isolated adrenal insufficiency due to partial CYP11A1 deficiency [32584]; Stevens-Johnson syndrome [32746]; Trichinellosis [32815]; sarcoidosis [32967]; Hodgkins lymphoma [33077]; eosinophilic pneumonia [33206]; follicular lymphoma [33294]; dermatitis herpetiformis [33410]; granulomatous slack skin disease [33452]; pediatric systemic lupus erythematosus [33534]; thyroiditis (disease) [33576]; aspiration pneumonia (disease) [33596]; acute lymphoblastic leukemia (disease) [33621]; exanthem (disease) [33649]; seborrheic dermatitis [33651]; asthma [33675]; adrenogenital syndrome [35510]; non-Hodgkin lymphoma [35650]; B-cell neoplasm [35651]; disease of orbital region [35665]; musculoskeletal system disease [35750]; eye disease [35823]; lymphoma [35970]; tendinitis [35992]; atopic eczema [36129]; spondyloarthropathy [36265]; bursitis [36272]; synovitis (disease) [36347]; rheumatic heart disease [36433]; tenosynovitis [36436]; Langerhans cell histiocytosis [36458]; exostosis [36562]; nephrotic syndrome [36604]; skin disease [36644]; neoplasm of mature B-cells [36724]; pneumonitis [37541]; multiple sclerosis [37722]; contact dermatitis [37770]; Crohn disease [37784]; allergic rhinitis [37888]; pemphigus [38016]; lichen disease [38021]; psoriasis [38024]; lupus erythematosus [38342]; inherited aplastic anemia [38496]; congenital adrenal hyperplasia [38513]; chronic primary adrenal insufficiency [38515]; adrenocortical insufficiency [38666]; primary cutaneous T-cell non-Hodgkin lymphoma [38708]; familial nephrotic syndrome [38719]; acquired angioedema [39111]; primary cutaneous T-cell lymphoma [39208]; pulmonary eosinophilia [39506]; psoriatic arthritis [39524]; chronic cutaneous lupus erythematosus [39533]; angioedema [39540]; acquired thrombocytopenia [39546]; parapsoriasis [39728]; allergic asthma [39773]; trichinosis [39808]; ankylosing spondylitis [39820]; actinic keratosis (disease) [83756]; humoral hypercalcemia of malignancy [83767]; precursor T-cell acute lymphoblastic leukemia [83769]; Crohn's colitis [83770]; renin-angiotensin-aldosterone system-blocker-induced angioedema [83772]; non-histaminic angioedema [83773]; lipoid nephrosis [83774]; brain edema [83775]; occupational dermatitis [83777]; fetal erythroblastosis [83780]; intrinsic asthma [83781]; exfoliative dermatitis [83782]; enterobiasis [83783]; Trichinella spiralis infectious disease [83784]; folliculotropic mycosis fungoides [83785]; localized pagetoid reticulosis [83786]; periarthritis [83787]; erythema multiforme [83788]; serum sickness [83789]; gout [83790]; vasomotor rhinitis [83791]; obsolete Hodgkin's granuloma [83792]; Hodgkin's paragranuloma [83793]; classic Hodgkin lymphoma, lymphocyte-rich type [83794]; chronic beryllium disease [83795]; lymphosarcoma [83796]; granuloma annulare [83882]; neurodermatitis [84028]; discoid lupus erythematosus [84030]; epicondylitis [84040]; miliary tuberculosis [84044]

BRIDGE extra (1): acute lymphoblastic leukemia (disease) [33621]

BRIDGE missing (1): acute lymphoblastic leukemia [35852]

UNION reached (118): spondyloarthropathy, susceptibility to [27366]; Diamond-Blackfan anemia [27452]; familial glucocorticoid deficiency [27648]; X-linked adrenal hypoplasia congenita [27878]; inflammatory bowel disease [28158]; autoimmune disease [28478]; leukemia, lymphocytic, susceptibility to [28830]; rheumatoid arthritis [29078]; systemic lupus erythematosus (disease) [29182]; dermatitis, atopic [29709]; chondrocalcinosis [29715]; hereditary angioedema [29854]; classic Hodgkin lymphoma [29993]; lymphoma, non-Hodgkin, familial [30447]; familial adrenal hypoplasia with absent pituitary luteinizing hormone [30602]; acute lymphoblastic/lymphocytic leukemia [30654]; juvenile arthritis due to defect in LACC1 [30800]; Addison disease [30813]; mycosis fungoides and variants [30990]; autoimmune thrombocytopenic [31511]; autoimmune hemolytic anemia [31723]; seborrheic keratosis [31850]; juvenile idiopathic arthritis [32325]; adrenal insufficiency [32384]; mantle cell lymphoma [32531]; heparin-induced thrombocytopenia (disease) [32563]; inherited isolated adrenal insufficiency due to partial CYP11A1 deficiency [32584]; Stevens-Johnson syndrome [32746]; Trichinellosis [32815]; sarcoidosis [32967]; Hodgkins lymphoma [33077]; eosinophilic pneumonia [33206]; follicular lymphoma [33294]; dermatitis herpetiformis [33410]; granulomatous slack skin disease [33452]; pediatric systemic lupus erythematosus [33534]; thyroiditis (disease) [33576]; aspiration pneumonia (disease) [33596]; acute lymphoblastic leukemia (disease) [33621]; exanthem (disease) [33649]; seborrheic dermatitis [33651]; asthma [33675]; adrenogenital syndrome [35510]; non-Hodgkin lymphoma [35650]; B-cell neoplasm [35651]; disease of orbital region [35665]; musculoskeletal system disease [35750]; eye disease [35823]; lymphoma [35970]; tendinitis [35992]; atopic eczema [36129]; spondyloarthropathy [36265]; bursitis [36272]; synovitis (disease) [36347]; rheumatic heart disease [36433]; tenosynovitis [36436]; Langerhans cell histiocytosis [36458]; exostosis [36562]; nephrotic syndrome [36604]; skin disease [36644]; neoplasm of mature B-cells [36724]; pneumonitis [37541]; multiple sclerosis [37722]; contact dermatitis [37770]; Crohn disease [37784]; allergic rhinitis [37888]; pemphigus [38016]; lichen disease [38021]; psoriasis [38024]; lupus erythematosus [38342]; inherited aplastic anemia [38496]; congenital adrenal hyperplasia [38513]; chronic primary adrenal insufficiency [38515]; adrenocortical insufficiency [38666]; primary cutaneous T-cell non-Hodgkin lymphoma [38708]; familial nephrotic syndrome [38719]; acquired angioedema [39111]; primary cutaneous T-cell lymphoma [39208]; pulmonary eosinophilia [39506]; psoriatic arthritis [39524]; chronic cutaneous lupus erythematosus [39533]; angioedema [39540]; acquired thrombocytopenia [39546]; parapsoriasis [39728]; allergic asthma [39773]; trichinosis [39808]; ankylosing spondylitis [39820]; actinic keratosis (disease) [83756]; humoral hypercalcemia of malignancy [83767]; precursor T-cell acute lymphoblastic leukemia [83769]; Crohn's colitis [83770]; renin-angiotensin-aldosterone system-blocker-induced angioedema [83772]; non-histaminic angioedema [83773]; lipoid nephrosis [83774]; brain edema [83775]; occupational dermatitis [83777]; fetal erythroblastosis [83780]; intrinsic asthma [83781]; exfoliative dermatitis [83782]; enterobiasis [83783]; Trichinella spiralis infectious disease [83784]; folliculotropic mycosis fungoides [83785]; localized pagetoid reticulosis [83786]; periarthritis [83787]; erythema multiforme [83788]; serum sickness [83789]; gout [83790]; vasomotor rhinitis [83791]; obsolete Hodgkin's granuloma [83792]; Hodgkin's paragranuloma [83793]; classic Hodgkin lymphoma, lymphocyte-rich type [83794]; chronic beryllium disease [83795]; lymphosarcoma [83796]; granuloma annulare [83882]; neurodermatitis [84028]; discoid lupus erythematosus [84030]; epicondylitis [84040]; miliary tuberculosis [84044]

UNION extra (1): acute lymphoblastic leukemia (disease) [33621]

UNION missing (1): acute lymphoblastic leukemia [35852]

## Current status and review

Both types remain FAIL; this investigation does not add exclusions. The earlier five-row type remains excluded with its tie unresolved. Global D1 therefore remains PROCEED: 9/12 types, 7,377/7,633 rows (96.65%); denominators remain unchanged. No mapping is frozen and S7 has not started.

Under the existing D1 rule, exclusion is the next action for these still-failing types. The researcher can review the concrete evidence before that status is recorded. Retaining the mixture and identity findings as exploratory diagnostics does not require weakening the primary gate.

## Verification, assumptions and engineering choices

- Full test suite: 119 passed, including five added tests for all four exact-set categories and extra/missing differences. Tests were observed failing before implementation.
- Runtime assertions check original sample IDs, original per-type scores, resolution, frozen inputs, raw orientations and protected-file hashes.
- Assumptions: the frozen normalization, roles, type map, either-direction convention and exact-equality rule remain authoritative. Similar names are not assumed to be equivalent nodes.
- Routine engineering choices: memoized typed neighbors; chunked raw-edge scan; deterministic numeric ID order; four descriptive mixture categories; complete sets in JSON and selected full named examples in this report; exclusive output creation. No new scientific method or threshold.
- Inspect by hand: the two named node identities in BH2_05027 and the BRIDGE-only/UNION-only examples before any policy discussion.

Artifacts: scripts/06_investigate_remaining.py; tests/test_s6_investigation.py; this report; evidence.json; identity_check.json; mixtures.csv. Documentation updated in docs/S6_implementation.md, docs/progress.md and docs/decision_log.md.
