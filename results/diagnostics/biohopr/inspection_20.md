# BioHopR inspection — 20 rows

Sample: `sorted(random.Random(42).sample(range(7633), 20))`. `answer` shows the first 5 items and the count. String values are shown JSON-escaped (\n = newline).

## BH2_00204

| Field | Value |
|---|---|
| row_sha256 | `7faca050cd79738cbaa206c81f338443cea23ece709cf70621ed035f81661a35` |
| hop1 | `"CDK2"` |
| hop1_question | `"Name a disease that is related to gene/protein CDK2."` |
| hop1_question_multi | `"Name all diseases that are related to gene/protein CDK2."` |
| hop1_type | `"gene/protein"` |
| hop2 | `"(5E)-2-Amino-5-(2-pyridinylmethylene)-1,3-thiazol-4(5H)-one"` |
| hop2_question | `"Name a disease that is related to a gene/protein that is associated with drug (5E)-2-Amino-5-(2-pyridinylmethylene)-1,3-thiazol-4(5H)-one."` |
| hop2_question_multi | `"Name all diseases that are related to a gene/protein that is associated with drug (5E)-2-Amino-5-(2-pyridinylmethylene)-1,3-thiazol-4(5H)-one."` |
| hop2_type | `"drug"` |
| prompt | `"Name a disease that is related to a gene/protein that is associated with drug (5E)-2-Amino-5-(2-pyridinylmethylene)-1,3-thiazol-4(5H)-one.\nJust give me the answer without any explanations.\nAnswer:\n"` |
| relation_hop1 | `"gene/protein:disease"` |
| relation_hop2 | `"drug:gene/protein:disease"` |
| system | `"You are an expert biomedical researcher."` |
| target_type | `"disease"` |
| answer (count) | 19 |
| answer (first 5) | `["obsolete Hodgkin's granuloma", "diffuse large B-cell lymphoma of the central nervous system", "diffuse large B-cell lymphoma", "glioma susceptibility", "squamous cell carcinoma"]` |

## BH2_00244

| Field | Value |
|---|---|
| row_sha256 | `f842794247f4fc1d409e5247dfacb403d1bf9406b9517288eb3dc870ba343662` |
| hop1 | `"F11"` |
| hop1_question | `"Name a disease that is related to gene/protein F11."` |
| hop1_question_multi | `"Name all diseases that are related to gene/protein F11."` |
| hop1_type | `"gene/protein"` |
| hop2 | `"(R)-1-(4-(4-(hydroxymethyl)-1,3,2-dioxaborolan-2-yl)benzyl)guanidine"` |
| hop2_question | `"Name a disease that is related to a gene/protein that is associated with drug (R)-1-(4-(4-(hydroxymethyl)-1,3,2-dioxaborolan-2-yl)benzyl)guanidine."` |
| hop2_question_multi | `"Name all diseases that are related to a gene/protein that is associated with drug (R)-1-(4-(4-(hydroxymethyl)-1,3,2-dioxaborolan-2-yl)benzyl)guanidine."` |
| hop2_type | `"drug"` |
| prompt | `"Name a disease that is related to a gene/protein that is associated with drug (R)-1-(4-(4-(hydroxymethyl)-1,3,2-dioxaborolan-2-yl)benzyl)guanidine.\nJust give me the answer without any explanations.\nAnswer:\n"` |
| relation_hop1 | `"gene/protein:disease"` |
| relation_hop2 | `"drug:gene/protein:disease"` |
| system | `"You are an expert biomedical researcher."` |
| target_type | `"disease"` |
| answer (count) | 1 |
| answer (first 5) | `["congenital factor XI deficiency"]` |

## BH2_00260

| Field | Value |
|---|---|
| row_sha256 | `72070aee1bd98de125ca7e2db42205c6ccfee26df474961b546246eb7caff7ca` |
| hop1 | `"DPP4"` |
| hop1_question | `"Name a disease that is related to gene/protein DPP4."` |
| hop1_question_multi | `"Name all diseases that are related to gene/protein DPP4."` |
| hop1_type | `"gene/protein"` |
| hop2 | `"(S)-2-[(R)-3-amino-4-(2-fluorophenyl)butyryl]-1,2,3,4-tetrahydroisoquinoline-3-carboxamide"` |
| hop2_question | `"Name a disease that is related to a gene/protein that is associated with drug (S)-2-[(R)-3-amino-4-(2-fluorophenyl)butyryl]-1,2,3,4-tetrahydroisoquinoline-3-carboxamide."` |
| hop2_question_multi | `"Name all diseases that are related to a gene/protein that is associated with drug (S)-2-[(R)-3-amino-4-(2-fluorophenyl)butyryl]-1,2,3,4-tetrahydroisoquinoline-3-carboxamide."` |
| hop2_type | `"drug"` |
| prompt | `"Name a disease that is related to a gene/protein that is associated with drug (S)-2-[(R)-3-amino-4-(2-fluorophenyl)butyryl]-1,2,3,4-tetrahydroisoquinoline-3-carboxamide.\nJust give me the answer without any explanations.\nAnswer:\n"` |
| relation_hop1 | `"gene/protein:disease"` |
| relation_hop2 | `"drug:gene/protein:disease"` |
| system | `"You are an expert biomedical researcher."` |
| target_type | `"disease"` |
| answer (count) | 4 |
| answer (first 5) | `["neurotic disorder", "anxiety disorder", "unipolar depression", "dysthymic disorder"]` |

## BH2_00712

| Field | Value |
|---|---|
| row_sha256 | `39b883cf7562269d9276d59bd0ae75958d0bf81e22bb4c0b1335efeb25eaa0a8` |
| hop1 | `"SOD2"` |
| hop1_question | `"Name a disease that is related to gene/protein SOD2."` |
| hop1_question_multi | `"Name all diseases that are related to gene/protein SOD2."` |
| hop1_type | `"gene/protein"` |
| hop2 | `"3-Fluoro-L-tyrosine"` |
| hop2_question | `"Name a disease that is related to a gene/protein that is associated with drug 3-Fluoro-L-tyrosine."` |
| hop2_question_multi | `"Name all diseases that are related to a gene/protein that is associated with drug 3-Fluoro-L-tyrosine."` |
| hop2_type | `"drug"` |
| prompt | `"Name a disease that is related to a gene/protein that is associated with drug 3-Fluoro-L-tyrosine.\nJust give me the answer without any explanations.\nAnswer:\n"` |
| relation_hop1 | `"gene/protein:disease"` |
| relation_hop2 | `"drug:gene/protein:disease"` |
| system | `"You are an expert biomedical researcher."` |
| target_type | `"disease"` |
| answer (count) | 273 |
| answer (first 5) | `["Alzheimer disease without neurofibrillary tangles", "situs inversus", "myelomeningocele", "hemoglobinopathy", "precancerous condition"]` |

## BH2_00767

| Field | Value |
|---|---|
| row_sha256 | `9e3dce84229552702d10e896b0df8c2a2b7ab41fa433450f2cc3aca5d1fdf8b8` |
| hop1 | `"LTF"` |
| hop1_question | `"Name a disease that is related to gene/protein LTF."` |
| hop1_question_multi | `"Name all diseases that are related to gene/protein LTF."` |
| hop1_type | `"gene/protein"` |
| hop2 | `"3h-Indole-5,6-Diol"` |
| hop2_question | `"Name a disease that is related to a gene/protein that is associated with drug 3h-Indole-5,6-Diol."` |
| hop2_question_multi | `"Name all diseases that are related to a gene/protein that is associated with drug 3h-Indole-5,6-Diol."` |
| hop2_type | `"drug"` |
| prompt | `"Name a disease that is related to a gene/protein that is associated with drug 3h-Indole-5,6-Diol.\nJust give me the answer without any explanations.\nAnswer:\n"` |
| relation_hop1 | `"gene/protein:disease"` |
| relation_hop2 | `"drug:gene/protein:disease"` |
| system | `"You are an expert biomedical researcher."` |
| target_type | `"disease"` |
| answer (count) | 21 |
| answer (first 5) | `["malignant colon neoplasm", "liver cancer", "candidiasis", "necrotizing enterocolitis", "endometriosis of uterus"]` |

## BH2_00839

| Field | Value |
|---|---|
| row_sha256 | `979602da3cd3a5c003aa7efd632417dcc52ddd1bb4f3f5a238c4e1bdcd72d9bb` |
| hop1 | `"F2"` |
| hop1_question | `"Name a disease that is related to gene/protein F2."` |
| hop1_question_multi | `"Name all diseases that are related to gene/protein F2."` |
| hop1_type | `"gene/protein"` |
| hop2 | `"4-({[4-(3-METHYLBENZOYL)PYRIDIN-2-YL]AMINO}METHYL)BENZENECARBOXIMIDAMIDE"` |
| hop2_question | `"Name a disease that is related to a gene/protein that is associated with drug 4-({[4-(3-METHYLBENZOYL)PYRIDIN-2-YL]AMINO}METHYL)BENZENECARBOXIMIDAMIDE."` |
| hop2_question_multi | `"Name all diseases that are related to a gene/protein that is associated with drug 4-({[4-(3-METHYLBENZOYL)PYRIDIN-2-YL]AMINO}METHYL)BENZENECARBOXIMIDAMIDE."` |
| hop2_type | `"drug"` |
| prompt | `"Name a disease that is related to a gene/protein that is associated with drug 4-({[4-(3-METHYLBENZOYL)PYRIDIN-2-YL]AMINO}METHYL)BENZENECARBOXIMIDAMIDE.\nJust give me the answer without any explanations.\nAnswer:\n"` |
| relation_hop1 | `"gene/protein:disease"` |
| relation_hop2 | `"drug:gene/protein:disease"` |
| system | `"You are an expert biomedical researcher."` |
| target_type | `"disease"` |
| answer (count) | 45 |
| answer (first 5) | `["Alzheimer disease without neurofibrillary tangles", "liver cancer", "acquired purpura fulminans", "cirrhosis of liver", "Creutzfeldt Jacob disease"]` |

## BH2_00912

| Field | Value |
|---|---|
| row_sha256 | `8d0d30bd9c4ff7b159a6258097d9adcdab3f9f934f801571ac89d0264c0a75c7` |
| hop1 | `"CFB"` |
| hop1_question | `"Name a disease that is related to gene/protein CFB."` |
| hop1_question_multi | `"Name all diseases that are related to gene/protein CFB."` |
| hop1_type | `"gene/protein"` |
| hop2 | `"4-guanidinobenzoic acid"` |
| hop2_question | `"Name a disease that is related to a gene/protein that is associated with drug 4-guanidinobenzoic acid."` |
| hop2_question_multi | `"Name all diseases that are related to a gene/protein that is associated with drug 4-guanidinobenzoic acid."` |
| hop2_type | `"drug"` |
| prompt | `"Name a disease that is related to a gene/protein that is associated with drug 4-guanidinobenzoic acid.\nJust give me the answer without any explanations.\nAnswer:\n"` |
| relation_hop1 | `"gene/protein:disease"` |
| relation_hop2 | `"drug:gene/protein:disease"` |
| system | `"You are an expert biomedical researcher."` |
| target_type | `"disease"` |
| answer (count) | 14 |
| answer (first 5) | `["membranoproliferative glomerulonephritis", "typical hemolytic-uremic syndrome", "hemolytic-uremic syndrome", "myasthenia gravis", "macular degeneration"]` |

## BH2_01143

| Field | Value |
|---|---|
| row_sha256 | `4a1608ab9be74a4c36bf0fc0683a1905efd517f549ae7e0f7a9659659d9b6011` |
| hop1 | `"PPARG"` |
| hop1_question | `"Name a disease that is related to gene/protein PPARG."` |
| hop1_question_multi | `"Name all diseases that are related to gene/protein PPARG."` |
| hop1_type | `"gene/protein"` |
| hop2 | `"9(S)-HODE"` |
| hop2_question | `"Name a disease that is related to a gene/protein that is associated with drug 9(S)-HODE."` |
| hop2_question_multi | `"Name all diseases that are related to a gene/protein that is associated with drug 9(S)-HODE."` |
| hop2_type | `"drug"` |
| prompt | `"Name a disease that is related to a gene/protein that is associated with drug 9(S)-HODE.\nJust give me the answer without any explanations.\nAnswer:\n"` |
| relation_hop1 | `"gene/protein:disease"` |
| relation_hop2 | `"drug:gene/protein:disease"` |
| system | `"You are an expert biomedical researcher."` |
| target_type | `"disease"` |
| answer (count) | 104 |
| answer (first 5) | `["Alzheimer disease without neurofibrillary tangles", "Fabry disease", "pancreatic neoplasm", "Crohn disease", "heart failure"]` |

## BH2_01828

| Field | Value |
|---|---|
| row_sha256 | `7633c8abe3058e2b357b81a2b6ee9bdb96230877b24501d1b70aa17afdf64805` |
| hop1 | `"ALB"` |
| hop1_question | `"Name a disease that is related to gene/protein ALB."` |
| hop1_question_multi | `"Name all diseases that are related to gene/protein ALB."` |
| hop1_type | `"gene/protein"` |
| hop2 | `"Guaiacol"` |
| hop2_question | `"Name a disease that is related to a gene/protein that is associated with drug Guaiacol."` |
| hop2_question_multi | `"Name all diseases that are related to a gene/protein that is associated with drug Guaiacol."` |
| hop2_type | `"drug"` |
| prompt | `"Name a disease that is related to a gene/protein that is associated with drug Guaiacol.\nJust give me the answer without any explanations.\nAnswer:\n"` |
| relation_hop1 | `"gene/protein:disease"` |
| relation_hop2 | `"drug:gene/protein:disease"` |
| system | `"You are an expert biomedical researcher."` |
| target_type | `"disease"` |
| answer (count) | 71 |
| answer (first 5) | `["neurotic disorder", "membranoproliferative glomerulonephritis", "cirrhosis of liver", "newborn respiratory distress syndrome", "endogenous depression"]` |

## BH2_02006

| Field | Value |
|---|---|
| row_sha256 | `5d6b3ad0bf6605bca6216450c0fe259770e84235ed54d4ed420ef7e2e7541fad` |
| hop1 | `"ACHE"` |
| hop1_question | `"Name a disease that is related to gene/protein ACHE."` |
| hop1_question_multi | `"Name all diseases that are related to gene/protein ACHE."` |
| hop1_type | `"gene/protein"` |
| hop2 | `"M-(N,N,N-Trimethylammonio)-2,2,2-Trifluoro-1,1-Dihydroxyethylbenzene"` |
| hop2_question | `"Name a disease that is related to a gene/protein that is associated with drug M-(N,N,N-Trimethylammonio)-2,2,2-Trifluoro-1,1-Dihydroxyethylbenzene."` |
| hop2_question_multi | `"Name all diseases that are related to a gene/protein that is associated with drug M-(N,N,N-Trimethylammonio)-2,2,2-Trifluoro-1,1-Dihydroxyethylbenzene."` |
| hop2_type | `"drug"` |
| prompt | `"Name a disease that is related to a gene/protein that is associated with drug M-(N,N,N-Trimethylammonio)-2,2,2-Trifluoro-1,1-Dihydroxyethylbenzene.\nJust give me the answer without any explanations.\nAnswer:\n"` |
| relation_hop1 | `"gene/protein:disease"` |
| relation_hop2 | `"drug:gene/protein:disease"` |
| system | `"You are an expert biomedical researcher."` |
| target_type | `"disease"` |
| answer (count) | 90 |
| answer (first 5) | `["Alzheimer disease without neurofibrillary tangles", "autosomal dominant limb-girdle muscular dystrophy type 1E (DES)", "distal myopathy with anterior tibial onset", "hereditary breast carcinoma", "autosomal dominant limb-girdle muscular dystrophy type 1D (DNAJB6)"]` |

## BH2_02253

| Field | Value |
|---|---|
| row_sha256 | `3269b5ad5ba7fd73276b78df9dfdce9017bd1ade93b5508f001bd00f8ce1c2a9` |
| hop1 | `"EGLN1"` |
| hop1_question | `"Name a disease that is related to gene/protein EGLN1."` |
| hop1_question_multi | `"Name all diseases that are related to gene/protein EGLN1."` |
| hop1_type | `"gene/protein"` |
| hop2 | `"N-[(4-HYDROXY-8-IODOISOQUINOLIN-3-YL)CARBONYL]GLYCINE"` |
| hop2_question | `"Name a disease that is related to a gene/protein that is associated with drug N-[(4-HYDROXY-8-IODOISOQUINOLIN-3-YL)CARBONYL]GLYCINE."` |
| hop2_question_multi | `"Name all diseases that are related to a gene/protein that is associated with drug N-[(4-HYDROXY-8-IODOISOQUINOLIN-3-YL)CARBONYL]GLYCINE."` |
| hop2_type | `"drug"` |
| prompt | `"Name a disease that is related to a gene/protein that is associated with drug N-[(4-HYDROXY-8-IODOISOQUINOLIN-3-YL)CARBONYL]GLYCINE.\nJust give me the answer without any explanations.\nAnswer:\n"` |
| relation_hop1 | `"gene/protein:disease"` |
| relation_hop2 | `"drug:gene/protein:disease"` |
| system | `"You are an expert biomedical researcher."` |
| target_type | `"disease"` |
| answer (count) | 14 |
| answer (first 5) | `["erythrocytosis, familial", "adrenal gland cancer", "adrenal gland pheochromocytoma", "sympathetic paraganglioma", "encephalopathy"]` |

## BH2_03456

| Field | Value |
|---|---|
| row_sha256 | `0d228d317df2e50f68718950403582b16379e95b12805a08acf9a13da177374c` |
| hop1 | `"hereditary breast carcinoma"` |
| hop1_question | `"Name a drug that can treat disease hereditary breast carcinoma."` |
| hop1_question_multi | `"Name all drugs that can treat disease hereditary breast carcinoma."` |
| hop1_type | `"disease"` |
| hop2 | `"RINT1"` |
| hop2_question | `"Name a drug that can treat a disease that is associated with gene/protein RINT1."` |
| hop2_question_multi | `"Name all drugs that can treat a disease that is associated with gene/protein RINT1."` |
| hop2_type | `"gene/protein"` |
| prompt | `"Name a drug that can treat a disease that is associated with gene/protein RINT1.\nJust give me the answer without any explanations.\nAnswer:\n"` |
| relation_hop1 | `"disease:drug"` |
| relation_hop2 | `"gene/protein:disease:drug"` |
| system | `"You are an expert biomedical researcher."` |
| target_type | `"drug"` |
| answer (count) | 2 |
| answer (first 5) | `["Bevacizumab", "Drostanolone propionate"]` |

## BH2_04467

| Field | Value |
|---|---|
| row_sha256 | `c05b0c5fc36870755bb864148c1e87059a80d4eba874ff5b9c9089b3f6f7998e` |
| hop1 | `"Liothyronine"` |
| hop1_question | `"Name a effect/phenotype which is a side effect of drug Liothyronine."` |
| hop1_question_multi | `"Name all effect/phenotypes which are side effects of drug Liothyronine."` |
| hop1_type | `"drug"` |
| hop2 | `"substernal goiter"` |
| hop2_question | `"Name a effect/phenotype which is a side effect of drug that can treat disease substernal goiter."` |
| hop2_question_multi | `"Name all effect/phenotypes which are side effects of drug that can treat disease substernal goiter."` |
| hop2_type | `"disease"` |
| prompt | `"Name a effect/phenotype which is a side effect of drug that can treat disease substernal goiter.\nJust give me the answer without any explanations.\nAnswer:\n"` |
| relation_hop1 | `"drug:effect/phenotype"` |
| relation_hop2 | `"disease:drug:effect/phenotype"` |
| system | `"You are an expert biomedical researcher."` |
| target_type | `"effect/phenotype"` |
| answer (count) | 6 |
| answer (first 5) | `["Fever", "Angina pectoris", "Congestive heart failure", "Tachycardia", "Arrhythmia"]` |

## BH2_04837

| Field | Value |
|---|---|
| row_sha256 | `ba72aeb513be8979efd4084e2a624708272e9b397a44aa634269d8877d11161d` |
| hop1 | `"benign prostatic hyperplasia (disease)"` |
| hop1_question | `"Name a gene/protein that is related to disease benign prostatic hyperplasia ."` |
| hop1_question_multi | `"Name all gene/proteins that are related to disease benign prostatic hyperplasia ."` |
| hop1_type | `"disease"` |
| hop2 | `"Tamsulosin"` |
| hop2_question | `"Name a gene/protein that is related to disease that is treated by drug Tamsulosin."` |
| hop2_question_multi | `"Name all gene/proteins that are related to disease that is treated by drug Tamsulosin."` |
| hop2_type | `"drug"` |
| prompt | `"Name a gene/protein that is related to disease that is treated by drug Tamsulosin.\nJust give me the answer without any explanations.\nAnswer:\n"` |
| relation_hop1 | `"disease:gene/protein"` |
| relation_hop2 | `"drug:disease:gene/protein"` |
| system | `"You are an expert biomedical researcher."` |
| target_type | `"gene/protein"` |
| answer (count) | 4 |
| answer (first 5) | `["PRL", "KLK3", "SRD5A2", "FGF7"]` |

## BH2_05238

| Field | Value |
|---|---|
| row_sha256 | `67ebcbf925a9b129b57150e470c6d7fd4e54beb3354bc02654dccba5196b169a` |
| hop1 | `"Tretinoin"` |
| hop1_question | `"Name a disease that is treated by drug Tretinoin."` |
| hop1_question_multi | `"Name all diseases that are treated by drug Tretinoin."` |
| hop1_type | `"drug"` |
| hop2 | `"GPRC5A"` |
| hop2_question | `"Name a disease that is treated by a drug that is associated with gene/protein GPRC5A."` |
| hop2_question_multi | `"Name all diseases that are treated by a drug that is associated with gene/protein GPRC5A."` |
| hop2_type | `"gene/protein"` |
| prompt | `"Name a disease that is treated by a drug that is associated with gene/protein GPRC5A.\nJust give me the answer without any explanations.\nAnswer:\n"` |
| relation_hop1 | `"drug:disease"` |
| relation_hop2 | `"gene/protein:drug:disease"` |
| system | `"You are an expert biomedical researcher."` |
| target_type | `"disease"` |
| answer (count) | 4 |
| answer (first 5) | `["acquired keratosis", "acne ", "acute promyelocytic leukemia", "palmoplantar keratoderma"]` |

## BH2_05543

| Field | Value |
|---|---|
| row_sha256 | `291676459b19faacbc484a9ae3e54d4518193d9b5f687cf0e6b179ab2b7ce3ef` |
| hop1 | `"Fostamatinib"` |
| hop1_question | `"Name a disease that is treated by drug Fostamatinib."` |
| hop1_question_multi | `"Name all diseases that are treated by drug Fostamatinib."` |
| hop1_type | `"drug"` |
| hop2 | `"TNNI3K"` |
| hop2_question | `"Name a disease that is treated by a drug that is associated with gene/protein TNNI3K."` |
| hop2_question_multi | `"Name all diseases that are treated by a drug that is associated with gene/protein TNNI3K."` |
| hop2_type | `"gene/protein"` |
| prompt | `"Name a disease that is treated by a drug that is associated with gene/protein TNNI3K.\nJust give me the answer without any explanations.\nAnswer:\n"` |
| relation_hop1 | `"drug:disease"` |
| relation_hop2 | `"gene/protein:drug:disease"` |
| system | `"You are an expert biomedical researcher."` |
| target_type | `"disease"` |
| answer (count) | 1 |
| answer (first 5) | `["thrombocytopenia due to immune destruction"]` |

## BH2_06033

| Field | Value |
|---|---|
| row_sha256 | `a45d57539446ad5c11b9f10d27e2ab400fefa5a1a95dd7a13f7f887c2e0ff645` |
| hop1 | `"familial papillary thyroid carcinoma with renal papillary neoplasia"` |
| hop1_question | `"Name a drug that can treat disease familial papillary thyroid carcinoma with renal papillary neoplasia."` |
| hop1_question_multi | `"Name all drugs that can treat disease familial papillary thyroid carcinoma with renal papillary neoplasia."` |
| hop1_type | `"disease"` |
| hop2 | `"Renal oncocytoma"` |
| hop2_question | `"Name a drug that can treat a disease that has phenotype Renal oncocytoma."` |
| hop2_question_multi | `"Name all drugs that can treat a disease that has phenotype Renal oncocytoma."` |
| hop2_type | `"effect/phenotype"` |
| prompt | `"Name a drug that can treat a disease that has phenotype Renal oncocytoma.\nJust give me the answer without any explanations.\nAnswer:\n"` |
| relation_hop1 | `"disease:drug"` |
| relation_hop2 | `"effect/phenotype:disease:drug"` |
| system | `"You are an expert biomedical researcher."` |
| target_type | `"drug"` |
| answer (count) | 3 |
| answer (first 5) | `["Liothyronine", "Levothyroxine", "Doxorubicin"]` |

## BH2_06067

| Field | Value |
|---|---|
| row_sha256 | `c820964382267666d916a6ce55ea6786e76d2187c192ad1492dc3ef49d01a625` |
| hop1 | `"tuberous sclerosis"` |
| hop1_question | `"Name a drug that can treat disease tuberous sclerosis."` |
| hop1_question_multi | `"Name all drugs that can treat disease tuberous sclerosis."` |
| hop1_type | `"disease"` |
| hop2 | `"Subependymal giant-cell astrocytoma"` |
| hop2_question | `"Name a drug that can treat a disease that has phenotype Subependymal giant-cell astrocytoma."` |
| hop2_question_multi | `"Name all drugs that can treat a disease that has phenotype Subependymal giant-cell astrocytoma."` |
| hop2_type | `"effect/phenotype"` |
| prompt | `"Name a drug that can treat a disease that has phenotype Subependymal giant-cell astrocytoma.\nJust give me the answer without any explanations.\nAnswer:\n"` |
| relation_hop1 | `"disease:drug"` |
| relation_hop2 | `"effect/phenotype:disease:drug"` |
| system | `"You are an expert biomedical researcher."` |
| target_type | `"drug"` |
| answer (count) | 1 |
| answer (first 5) | `["Everolimus"]` |

## BH2_06074

| Field | Value |
|---|---|
| row_sha256 | `21af339de3bf63f645947219683910ed2a0d36a27aa07bd616b752dfca93cc0e` |
| hop1 | `"mastocytosis"` |
| hop1_question | `"Name a drug that can treat disease mastocytosis."` |
| hop1_question_multi | `"Name all drugs that can treat disease mastocytosis."` |
| hop1_type | `"disease"` |
| hop2 | `"Telangiectasia macularis eruptiva perstans"` |
| hop2_question | `"Name a drug that can treat a disease that has phenotype Telangiectasia macularis eruptiva perstans."` |
| hop2_question_multi | `"Name all drugs that can treat a disease that has phenotype Telangiectasia macularis eruptiva perstans."` |
| hop2_type | `"effect/phenotype"` |
| prompt | `"Name a drug that can treat a disease that has phenotype Telangiectasia macularis eruptiva perstans.\nJust give me the answer without any explanations.\nAnswer:\n"` |
| relation_hop1 | `"disease:drug"` |
| relation_hop2 | `"effect/phenotype:disease:drug"` |
| system | `"You are an expert biomedical researcher."` |
| target_type | `"drug"` |
| answer (count) | 5 |
| answer (first 5) | `["Rabeprazole", "Cromoglicic acid", "Imatinib", "Midostaurin", "Cimetidine"]` |

## BH2_07308

| Field | Value |
|---|---|
| row_sha256 | `65eb19a833006c06acdfac75c94424980029a334762dae70c059fca23bc627e0` |
| hop1 | `"Isoprenaline"` |
| hop1_question | `"Name a gene/protein that is associated with drug Isoprenaline."` |
| hop1_question_multi | `"Name all gene/proteins that are associated with drug Isoprenaline."` |
| hop1_type | `"drug"` |
| hop2 | `"atrioventricular block (disease)"` |
| hop2_question | `"Name a gene/protein that is associated with drug that can treat disease atrioventricular block ."` |
| hop2_question_multi | `"Name all gene/proteins that are associated with drug that can treat disease atrioventricular block ."` |
| hop2_type | `"disease"` |
| prompt | `"Name a gene/protein that is associated with drug that can treat disease atrioventricular block .\nJust give me the answer without any explanations.\nAnswer:\n"` |
| relation_hop1 | `"drug:gene/protein"` |
| relation_hop2 | `"disease:drug:gene/protein"` |
| system | `"You are an expert biomedical researcher."` |
| target_type | `"gene/protein"` |
| answer (count) | 9 |
| answer (first 5) | `["ADRB3", "MAPK1", "ADRB1", "PIK3R2", "PIK3R1"]` |
