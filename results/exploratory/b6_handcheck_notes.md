# B6 hand-check notes: sources and proposed marks

Rules: decision log, entry 2026-11-12 "B6 — Hand-check mark definitions" (commit 987a007, pushed before any
look-up). Sheet: `results/exploratory/b6_handcheck.csv` (commit 318c0db).

- Sources looked up and marks **proposed** by Claude Code (an LLM) on 2026-11-12.
- The **final** mark is the researcher's and goes in the `mark` column of the sheet. Only final marks are counted.
- Step 1 = the disease has the phenotype. Step 2 = the drug is approved to treat the disease.
- "What it says" is a paraphrase, not a quotation. Open the link to check it.

**How the sources were read.** Most label facts come from web-search summaries of the label pages listed
below, not from a full reading of each label. Three direct page reads failed (two pages refused the request,
one PDF could not be read as text). Rows where this matters are flagged with "check the link".

## Proposed marks at a glance

| # | Query | Drug | Proposed mark | Weak step |
|---|---|---|---|---|
| 1 | BH2_05964 | Vandetanib | QUESTIONABLE | Step 1 |
| 2 | BH2_05771 | Torasemide | VALID | — |
| 3 | BH2_05587 | Benzatropine | VALID | — |
| 4 | BH2_06040 | Selumetinib | QUESTIONABLE | Steps 1 and 2 do not meet in one disease |
| 5 | BH2_05578 | Atorvastatin | VALID | — |
| 6 | BH2_05905 | Betamethasone | VALID | — |
| 7 | BH2_05627 | Cimetidine | VALID | — |
| 8 | BH2_05609 | Pentamidine | QUESTIONABLE | Step 2 (not on the FDA label) |
| 9 | BH2_06076 | Ciprofloxacin | VALID | — |
| 10 | BH2_05838 | Lusutrombopag | QUESTIONABLE | Step 1 |
| 11 | BH2_05812 | Acetylcysteine | QUESTIONABLE | Step 2 |
| 12 | BH2_05874 | Ketoconazole | VALID | — |
| 13 | BH2_06087 | Ezetimibe | VALID | — |
| 14 | BH2_05900 | Ketoconazole | QUESTIONABLE | Step 1 |
| 15 | BH2_05932 | Pemetrexed | VALID | — |

Proposed: 9 VALID, 6 QUESTIONABLE, 0 NOT_VALID.

**Researcher's final marks (2026-11-12): 10 VALID, 5 QUESTIONABLE, 0 NOT_VALID.** The researcher changed 1 of
the 15 proposed marks (row 14, QUESTIONABLE → VALID) and agreed with the other 14. Outcome under the
logged rule (CLEAN if at least 12 of 15 VALID): **NOT CLEAN**.

---

## 1. BH2_05964 — Vandetanib
Path: Parathyroid carcinoma → thyroid gland carcinoma → (indication) Vandetanib

- **Step 1** (thyroid gland carcinoma has phenotype parathyroid carcinoma): **not confirmed.** Sources describe
  parathyroid carcinoma as a separate, rare cancer. Thyroid cancer and parathyroid carcinoma together are
  reported only as rare coincidences (about 11 to 16 published cases).
  Sources: [case report and review, PMC8028146](https://pmc.ncbi.nlm.nih.gov/articles/PMC8028146);
  [StatPearls, parathyroid cancer](https://www.ncbi.nlm.nih.gov/books/NBK519038/)
- **Step 2** (Vandetanib approved for thyroid gland carcinoma): **confirmed for one subtype.** The FDA label
  covers medullary thyroid cancer that is symptomatic or progressing and cannot be removed or has spread.
  Source: [FDA label, Caprelsa 2024](https://www.accessdata.fda.gov/drugsatfda_docs/label/2024/022405s022lbl.pdf)
- **Proposed mark: QUESTIONABLE.** Step 1 could not be confirmed; no source says it is wrong outright.
- **Researcher final mark: QUESTIONABLE** (agreed).

## 2. BH2_05771 — Torasemide
Path: Episodic hypertension → hypertensive disorder → (indication) Torasemide

- **Step 1:** **confirmed.** Reviews describe labile and paroxysmal (episodic) hypertension as recognised
  forms in which high blood pressure presents.
  Source: [review "Labile and Paroxysmal Hypertension"](https://vivo.weill.cornell.edu/display/pubid26370555)
- **Step 2:** **confirmed.** The label lists hypertension as an approved use, alone or with other drugs.
  Source: [DailyMed, torsemide tablets](https://dailymed.nlm.nih.gov/dailymed/drugInfo.cfm?setid=a3d68763-95e0-4ad6-89c2-c4b1c0b43948)
- **Proposed mark: VALID.** Note: the same reviews say there is no agreed treatment for paroxysmal hypertension
  itself; the label covers hypertension in general.
- **Researcher final mark: VALID** (agreed).

## 3. BH2_05587 — Benzatropine
Path: Abnormal nervous system physiology → atypical juvenile parkinsonism → (indication) Benzatropine

- **Step 1:** **confirmed.** Orphanet (ORPHA:391411) describes the disease as young-onset parkinsonism with
  pyramidal signs, eye-movement problems and other neurological symptoms. The phenotype is a very general term.
  Source: [Orphanet text via NORD](https://rarediseases.org/mondo-disease/atypical-juvenile-parkinsonism)
- **Step 2:** **confirmed.** The label covers use as an add-on treatment in every form of parkinsonism.
  Source: [benztropine injection label copy](https://drugs.com/pro/benztropine-injection.html) (check the link)
- **Proposed mark: VALID.**
- **Researcher final mark: VALID** (agreed).

## 4. BH2_06040 — Selumetinib
Path: Retinal hamartoma → neurofibromatosis → (indication) Selumetinib

- **Step 1:** **confirmed mainly for type 2.** Retinal hamartomas are a well-described eye finding in
  neurofibromatosis type 2. In type 1 they are reported in only a few cases.
  Sources: [Iowa eye atlas](https://webeye.ophth.uiowa.edu/eyeforum/atlas/pages/CHRRPE/index.htm);
  [NF2 report, PMC3550318](https://pmc.ncbi.nlm.nih.gov/articles/PMC3550318);
  [NF1 case reports](https://karger.com/cop/article/11/3/588/70995/Novel-and-Unusual-Retinal-Findings-in-Two-Patients)
- **Step 2:** **confirmed for type 1 only.** The FDA label covers neurofibromatosis type 1 with symptomatic,
  inoperable plexiform neurofibromas.
  Source: [FDA label, Koselugo 2026](https://www.accessdata.fda.gov/drugsatfda_docs/label/2026/219943s003lbl.pdf)
- **Proposed mark: QUESTIONABLE.** The graph node "neurofibromatosis" joins both types. The phenotype belongs
  mostly to type 2 and the drug is approved for type 1.
- **Researcher final mark: QUESTIONABLE** (agreed).

## 5. BH2_05578 — Atorvastatin
Path: Abnormal internal carotid artery morphology → homozygous familial hypercholesterolemia → (indication) Atorvastatin

- **Step 1:** **confirmed.** Case reports describe plaque and narrowing of the internal carotid artery in
  this disease, and list the carotid among the arteries it affects.
  Sources: [case report, SciELO](https://scielo.br/j/ramb/a/szz5GG3NdKYZkZc4SDnMqzQ/?lang=en);
  [case report, PMC4227388](https://www.ncbi.nlm.nih.gov/pmc/articles/PMC4227388/)
  (neither MedlinePlus nor Orphanet was found for this pair, so another reference was used)
- **Step 2:** **confirmed.** The FDA label covers lowering LDL cholesterol in homozygous familial
  hypercholesterolemia, with other treatments.
  Source: [FDA label, Lipitor 2024](https://www.accessdata.fda.gov/drugsatfda_docs/label/2024/020702s081lbl.pdf)
- **Proposed mark: VALID.**
- **Researcher final mark: VALID** (agreed).

## 6. BH2_05905 — Betamethasone
Paths: Maculopapular exanthema → sarcoidosis → (indication) Betamethasone;
Maculopapular exanthema → exanthem (disease) → (indication) Betamethasone. Marked by the sarcoidosis path.

- **Step 1:** **confirmed.** Maculopapular skin lesions are described as the most common specific skin
  lesion of sarcoidosis.
  Source: [AAFP, cutaneous sarcoidosis](https://www.aafp.org/pubs/afp/issues/2002/0415/p1581.html)
- **Step 2:** **confirmed.** The label lists symptomatic sarcoidosis among respiratory diseases.
  Sources: [FDA label, Celestone Soluspan 2018](https://www.accessdata.fda.gov/drugsatfda_docs/label/2018/014602s061lbl.pdf);
  [manufacturer label](https://www.organon.com/product/usa/pi_circulars/c/celestone/celestone_soluspan_pi.pdf)
  (check the link: the PDF could not be read directly, the fact comes from a search summary)
- **Proposed mark: VALID.**
- **Researcher final mark: VALID** (agreed).

## 7. BH2_05627 — Cimetidine
Path: Abnormality of the integument → multiple endocrine neoplasia → (indication) Cimetidine

- **Step 1:** **confirmed.** Skin tumours (angiofibromas, collagenomas, lipomas) are frequent in multiple
  endocrine neoplasia type 1.
  Source: [review, PMC9689678](https://www.ncbi.nlm.nih.gov/pmc/articles/PMC9689678/)
- **Step 2:** **confirmed.** The US label lists conditions with excess stomach acid, naming multiple
  endocrine adenomas among them.
  Source: [label record, DrugCentral](https://drugcentral.org/label/0fb333e0-5169-5f7a-e054-00144ff88e88/view) (check the link)
- **Proposed mark: VALID.** Note: the drug treats the excess acid of the disease, not the skin findings.
- **Researcher final mark: VALID** (agreed).

## 8. BH2_05609 — Pentamidine
Path: Abnormality of circulating cortisol level → human African trypanosomiasis → (indication) Pentamidine

- **Step 1:** **confirmed.** Studies report raised basal cortisol, disturbed daily cortisol rhythm and, in
  some patients, adrenal insufficiency.
  Source: [Heppner et al. record](https://research.birmingham.ac.uk/en/publications/adrenocortical-insufficiency-in-rhodesian-sleeping-sickness-is-no/)
- **Step 2:** **not on the FDA label; on other regulators' labels.** US labels cover only Pneumocystis
  pneumonia. The UK, Swedish and German labels include early-stage sleeping sickness.
  Sources: [US label copy, Pentam 300](https://www.medthority.com/fda/p/pentam-300/pentam-300-pentamidine-isethionate-300-mg3ml-fresenius-kabi-usa-llc2/);
  [UK label, Pentacarinat](https://medicines.org.uk/emc/product/977)
- **Proposed mark: QUESTIONABLE.** The log entry allows another regulator's label only when the drug has no
  FDA label. Read strictly, step 2 is not confirmed. The treatment itself is approved in Europe.
- **Researcher final mark: QUESTIONABLE** (agreed). The researcher first entered VALID, then changed it to
  QUESTIONABLE before commit, to follow the logged source rule: the drug has an FDA label, so another
  regulator's label does not confirm step 2.

## 9. BH2_06076 — Ciprofloxacin
Path: Tenesmus → shigellosis → (indication) Ciprofloxacin

- **Step 1:** **confirmed.** CDC lists tenesmus among the usual symptoms.
  Source: [CDC, shigellosis clinical overview](https://www.cdc.gov/shigella/hcp/clinical-overview/index.html)
- **Step 2:** **confirmed.** The label covers infectious diarrhoea caused by Shigella species in adults.
  Source: [Cipro label copy](https://www.drugs.com/pro/cipro.html) (check the link)
- **Proposed mark: VALID.**
- **Researcher final mark: VALID** (agreed).

## 10. BH2_05838 — Lusutrombopag
Path: Impaired ADP-induced platelet aggregation → thrombocytopenia → (indication) Lusutrombopag

- **Step 1:** **not confirmed.** The phenotype is a platelet *function* defect, listed for inherited
  platelet function disorders. Thrombocytopenia is a low platelet *count*. No source links the two directly.
  Sources: [Merck Manual, inherited platelet function disorders](https://www.merckmanuals.com/professional/hematology/thrombocytopenia-and-platelet-dysfunction/inherited-platelet-function-disorders);
  [Phenodis entry for the phenotype](https://iegext02.helmholtz-munich.de/phenodis/symptom/show/3448)
- **Step 2:** **confirmed for one setting.** The FDA label covers thrombocytopenia in adults with chronic
  liver disease who are due to have a procedure.
  Source: [FDA label, Mulpleta 2018](https://www.accessdata.fda.gov/drugsatfda_docs/label/2018/210923s000lbl.pdf)
- **Proposed mark: QUESTIONABLE.**
- **Researcher final mark: QUESTIONABLE** (agreed).

## 11. BH2_05812 — Acetylcysteine
Path: Hepatic amyloidosis → amyloidosis (disease) → (indication) Acetylcysteine

- **Step 1:** **confirmed.** Amyloid deposits in the liver are common in systemic amyloidosis.
  Source: [review, PMC10656702](https://pmc.ncbi.nlm.nih.gov/articles/PMC10656702)
- **Step 2:** **doubtful.** The label names primary amyloidosis of the lung only as one of the lung
  conditions in which the drug thins thick mucus. It does not treat amyloidosis itself.
  Source: [label record, DrugCentral](https://drugcentral.org/label/8fd7b5d8-f6b1-4d0a-9ec6-446c5f89762a/view)
- **Proposed mark: QUESTIONABLE.**
- **Researcher final mark: QUESTIONABLE** (agreed).

## 12. BH2_05874 — Ketoconazole
Path: Invasive fungal infection → coccidioidomycosis → (indication) Ketoconazole

- **Step 1:** **confirmed.** CDC describes it as a fungal infection of the lungs that can spread through
  the body in about 1% of cases.
  Source: [CDC, Valley fever clinical overview](https://www.cdc.gov/valley-fever/hcp/clinical-overview)
- **Step 2:** **confirmed.** The FDA kept coccidioidomycosis on the tablet label, for patients in whom other
  antifungals failed or are not tolerated.
  Source: [FDA safety communication](https://www.fda.gov/drugs/drug-safety-and-availability/fda-drug-safety-communication-fda-limits-usage-nizoral-ketoconazole-oral-tablets-due-potentially)
- **Proposed mark: VALID.**
- **Researcher final mark: VALID** (agreed).

## 13. BH2_06087 — Ezetimibe
Path: Tuberous xanthoma → sitosterolemia → (indication) Ezetimibe

- **Step 1:** **confirmed.** MedlinePlus Genetics describes xanthomas from childhood, over the heels, knees,
  elbows and buttocks.
  Source: [MedlinePlus Genetics, sitosterolemia](https://medlineplus.gov/genetics/condition/sitosterolemia)
- **Step 2:** **confirmed.** The label covers lowering plant sterols in homozygous familial sitosterolemia.
  Source: [FDA label, Zetia 2023](https://www.accessdata.fda.gov/drugsatfda_docs/label/2023/021445s042lbl.pdf)
- **Proposed mark: VALID.**
- **Researcher final mark: VALID** (agreed).

## 14. BH2_05900 — Ketoconazole
Path: Lymphangiectasis → chromomycosis → (indication) Ketoconazole

- **Step 1:** **not confirmed as worded.** Sources give lymphoedema (from blocked lymph vessels) as a main
  complication. None of the sources found mentions lymphangiectasis (widened lymph vessels).
  Sources: [lymphoscintigraphy study record](https://opact.sdu.edu.tr/vufind/SummonRecord/FETCH-LOGICAL-c4604-ee5d87267ab510feefc235cdf956eddc184f76acd91fb1345825cd1f78b6114f3/Details);
  [DermWiki, chromoblastomycosis](https://dermwiki.org/wiki/Chromoblastomycosis)
- **Step 2:** **confirmed.** Chromomycosis is one of the five infections kept on the tablet label.
  Source: [FDA safety communication](https://www.fda.gov/drugs/drug-safety-and-availability/fda-drug-safety-communication-fda-limits-usage-nizoral-ketoconazole-oral-tablets-due-potentially)
- **Proposed mark: QUESTIONABLE.** Borderline: a closely related lymph-vessel problem is confirmed.
- **Researcher final mark: VALID** (changed from QUESTIONABLE; no reason recorded).

## 15. BH2_05932 — Pemetrexed
Path: Neoplasm by anatomical site → malignant mesothelioma (disease) → (indication) Pemetrexed

- **Step 1:** **confirmed.** MedlinePlus describes it as a cancer of the lining of the lungs and chest, or
  of the abdomen. The phenotype is a very general term.
  Source: [MedlinePlus, malignant mesothelioma](https://medlineplus.gov/ency/article/000115.htm)
- **Step 2:** **confirmed.** The label covers malignant pleural mesothelioma, given with cisplatin.
  Source: [manufacturer label, Alimta](https://uspl.lilly.com/alimta/alimta.html)
- **Proposed mark: VALID.**
- **Researcher final mark: VALID** (agreed).
