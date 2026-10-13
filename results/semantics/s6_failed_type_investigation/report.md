# S6 D1 investigation: drug → effect/phenotype → disease

**Pre-exclusion evidence. Tie retained unresolved; no mapping frozen.**

## Candidate scores

| Hop-2 candidate set | BRIDGE | UNION |
|---|---:|---:|
| disease_phenotype_negative | 0/5 (0%) | 0/5 (0%) |
| disease_phenotype_positive | 0/5 (0%) | 0/5 (0%) |
| disease_phenotype_negative, disease_phenotype_positive | 0/5 (0%) | 0/5 (0%) |

The two singleton sets are tied after the smallest-set rule. The two-label set also scores zero, but loses that size comparison. Hop 1 is drug_effect: 5/5 (100%). Neither singleton is chosen.

## Why only five validation rows

The pinned file has 7,633 records, with exactly five of this relation type. All five query entities, bridges and all answer names resolve. No rows were skipped. All five were selected; there are no additional records to fill the 30-row sample. D1 requires at least ten, independently of answer reproduction.

| Validation order | Row | Query drug | Stored phenotype bridge | Reference diseases | Valid bridges |
|---:|---|---|---|---:|---:|
| 1 | BH2_00004 | Zinc sulfate | Nausea | 29 | 1 |
| 2 | BH2_00003 | Zinc chloride | Decreased circulating copper concentration | 3 | 1 |
| 3 | BH2_00001 | Idoxuridine | Blepharitis | 23 | 1 |
| 4 | BH2_00000 | Benzyl benzoate | Pain | 42 | 1 |
| 5 | BH2_00002 | Vitamin A | Anaphylactic shock | 2 | 1 |

## Permitted causes checked

- **Field roles:** explicit row types and question text agree with hop2 = drug/query, hop1 = phenotype/bridge, answer = disease targets. All five fresh S5 support checks pass; hop-1 drug_effect reaches the stored bridge in every row. Support is containment, not exact set equality.
- **Normalization:** every reference disease resolves uniquely under the frozen §12 policy; no answer is lost. No fuzzy matches or new aliases were added.
- **Edge storage/direction:** a fresh scan of all 8,100,498 raw rows reproduced every candidate set for all five rows under BRIDGE and UNION. Outgoing-only, incoming-only, either-direction and cached-index results agree for these checks; duplicate rows are deduplicated as sets.
- **Release:** raw kg.csv and nodes.csv SHA256s match the frozen metadata, whose SHA256 matches kg_fingerprint. Both MD5s match the publisher checksums recorded and accepted at S4. BioHopR matches the pinned revision and file checksum. No release substitution was made.
- **Answer construction:** every nonempty candidate set was checked under both frozen constructions. Each query has one valid bridge, so BRIDGE and UNION are identical here. Positive phenotype edges reach gold diseases plus extras; negative edges miss gold diseases.

These checks found no permitted implementation/data-integrity correction that repairs the failures. The upstream reason for the smaller BioHopR answer sets is not established. No threshold or scientific definition was changed.

## Two failing validation rows — full disease sets

The first two rows in the prescribed validation order follow. All sets below are complete, with canonical PrimeKG IDs and names. For each candidate, BRIDGE and UNION give exactly the same sets.

### BH2_00004: Zinc sulfate → Nausea

Name all diseases that are related to a effect/phenotype that is associated with drug Zinc sulfate.

**Reference diseases (29):** fructose intolerance (`27426`); familial lipoprotein lipase deficiency (`27502`); Ehlers-Danlos syndrome, classic type (`28257`); Parkinson disease (`28547`); variegate porphyria (`29457`); lysinuric protein intolerance (`29923`); ovarian hyperstimulation syndrome (`29924`); migraine, familial typical, susceptibility to, 2 (`30177`); choroid plexus papilloma (`30230`); hypokalemic alkalosis, familial, with specific renal tubulopathy (`30309`); multiple acyl-CoA dehydrogenase deficiency (`30653`); cyclic vomiting syndrome (`30753`); hypervitaminosis a, susceptibility to (`31024`); Fabry disease (`31384`); urticaria (`32231`); Zygomycosis (`32249`); lead poisoning (`32274`); mercury poisoning (`32280`); Turcot syndrome with polyposis (`32298`); anterior cutaneous nerve entrapment syndrome (`32304`); amoebiasis due to free-living amoebae (`32327`); angiostrongyliasis (`32338`); toxic shock syndrome (`32395`); SUNCT syndrome (`32399`); mitochondrial neurogastrointestinal encephalomyopathy (`32417`); tick-borne encephalitis (`32422`); acute disseminated encephalomyelitis (`32501`); human African trypanosomiasis (`32503`); graft versus host disease (`32520`)

**Candidate `disease_phenotype_negative` — BRIDGE = UNION**

- **Reached diseases (0):** ∅ (empty)
- **Extra diseases (0):** ∅ (empty)
- **Missing diseases (29):** fructose intolerance (`27426`); familial lipoprotein lipase deficiency (`27502`); Ehlers-Danlos syndrome, classic type (`28257`); Parkinson disease (`28547`); variegate porphyria (`29457`); lysinuric protein intolerance (`29923`); ovarian hyperstimulation syndrome (`29924`); migraine, familial typical, susceptibility to, 2 (`30177`); choroid plexus papilloma (`30230`); hypokalemic alkalosis, familial, with specific renal tubulopathy (`30309`); multiple acyl-CoA dehydrogenase deficiency (`30653`); cyclic vomiting syndrome (`30753`); hypervitaminosis a, susceptibility to (`31024`); Fabry disease (`31384`); urticaria (`32231`); Zygomycosis (`32249`); lead poisoning (`32274`); mercury poisoning (`32280`); Turcot syndrome with polyposis (`32298`); anterior cutaneous nerve entrapment syndrome (`32304`); amoebiasis due to free-living amoebae (`32327`); angiostrongyliasis (`32338`); toxic shock syndrome (`32395`); SUNCT syndrome (`32399`); mitochondrial neurogastrointestinal encephalomyopathy (`32417`); tick-borne encephalitis (`32422`); acute disseminated encephalomyelitis (`32501`); human African trypanosomiasis (`32503`); graft versus host disease (`32520`)

**Candidate `disease_phenotype_positive` — BRIDGE = UNION**

- **Reached diseases (89):** Charcot-Marie-Tooth disease with ptosis and parkinsonism (`27210`); fructose intolerance (`27426`); familial lipoprotein lipase deficiency (`27502`); mitochondrial DNA depletion syndrome (`27691`); Caroli disease (`27699`); IgG4-related hepatopathy (`27702`); familial hyperaldosteronism (`27723`); liver neuroendocrine carcinoma (`27774`); episodic ataxia (`27813`); aldosterone-producing adenoma with seizures and neurological abnormalities (`27832`); mal de Debarquement (`27838`); hereditary coproporphyria (`27842`); acute intermittent porphyria (`27843`); migraine with or without aura, susceptibility to (`28017`); hyperthermia, cutaneous, with headaches and nausea (`28070`); Ehlers-Danlos syndrome, classic type (`28257`); monosodium glutamate sensitivity (`28269`); multiple endocrine neoplasia (`28426`); glucocorticoid-remediable aldosteronism (`28505`); Parkinson disease (`28547`); hepatitis, fulminant viral, susceptibility to (`29024`); hyperammonemia due to N-acetylglutamate synthase deficiency (`29034`); Charcot-Marie-Tooth disease, Guadalajara neuronal type (`29427`); variegate porphyria (`29457`); hereditary angioedema (`29854`); lysinuric protein intolerance (`29923`); ovarian hyperstimulation syndrome (`29924`); migraine, familial typical, susceptibility to, 2 (`30177`); choroid plexus papilloma (`30230`); HELLP syndrome (`30274`); hypokalemic alkalosis, familial, with specific renal tubulopathy (`30309`); multiple acyl-CoA dehydrogenase deficiency (`30653`); cyclic vomiting syndrome (`30753`); hypervitaminosis a, susceptibility to (`31024`); pseudotumor cerebri (`31072`); Fabry disease (`31384`); seizures-scoliosis-macrocephaly syndrome (`31388`); gastric mucosal hypertrophy (`31674`); urticaria (`32231`); Zygomycosis (`32249`); lead poisoning (`32274`); mercury poisoning (`32280`); Turcot syndrome with polyposis (`32298`); anterior cutaneous nerve entrapment syndrome (`32304`); amoebiasis due to free-living amoebae (`32327`); angiostrongyliasis (`32338`); toxic shock syndrome (`32395`); SUNCT syndrome (`32399`); mitochondrial neurogastrointestinal encephalomyopathy (`32417`); tick-borne encephalitis (`32422`); acute disseminated encephalomyelitis (`32501`); human African trypanosomiasis (`32503`); graft versus host disease (`32520`); cryptosporidiosis (`32598`); panhypophysitis (`32600`); adenohypophysitis (`32603`); superficial siderosis (`32713`); AA amyloidosis (`32717`); microsporidiosis (`32749`); glycogen storage disease due to liver phosphorylase kinase deficiency (`32796`); ectopic aldosterone-producing tumor (`32811`); Trichinellosis (`32815`); aldosterone-producing adrenal cortex adenoma (`32820`); Zollinger-Ellison syndrome (`32875`); Sheehan syndrome (`32905`); acute liver failure (`32928`); acquired aneurysmal subarachnoid hemorrhage (`32930`); brucellosis (`32932`); cocaine intoxication (`32933`); primary unilateral adrenal hyperplasia (`32943`); shigellosis (`32999`); colchicine poisoning (`33018`); ethylene glycol poisoning (`33020`); serotonin syndrome (`33091`); gallbladder neuroendocrine tumor, grade 1/2 (`33106`); duodenal neuroendocrine tumor, well differentiated, low or intermediate grade (`33119`); jejunal neuroendocrine tumor, well differentiated, low or intermediate grade (`33121`); ileal neuroendocrine tumor, well differentiated, low or intermediate grade (`33122`); sporadic pheochromocytoma/secreting paraganglioma (`33207`); poliomyelitis (`33284`); listeriosis (`33297`); optic pathway glioma (`33318`); renal nutcracker syndrome (`33362`); neuromyelitis optica (`33400`); hereditary pheochromocytoma-paraganglioma (`33431`); neuroleptic malignant syndrome (`33454`); hereditary renal hypouricemia (`33457`); non-secreting paraganglioma (`33462`); boutonneuse fever (`33543`)
- **Extra diseases (60):** Charcot-Marie-Tooth disease with ptosis and parkinsonism (`27210`); mitochondrial DNA depletion syndrome (`27691`); Caroli disease (`27699`); IgG4-related hepatopathy (`27702`); familial hyperaldosteronism (`27723`); liver neuroendocrine carcinoma (`27774`); episodic ataxia (`27813`); aldosterone-producing adenoma with seizures and neurological abnormalities (`27832`); mal de Debarquement (`27838`); hereditary coproporphyria (`27842`); acute intermittent porphyria (`27843`); migraine with or without aura, susceptibility to (`28017`); hyperthermia, cutaneous, with headaches and nausea (`28070`); monosodium glutamate sensitivity (`28269`); multiple endocrine neoplasia (`28426`); glucocorticoid-remediable aldosteronism (`28505`); hepatitis, fulminant viral, susceptibility to (`29024`); hyperammonemia due to N-acetylglutamate synthase deficiency (`29034`); Charcot-Marie-Tooth disease, Guadalajara neuronal type (`29427`); hereditary angioedema (`29854`); HELLP syndrome (`30274`); pseudotumor cerebri (`31072`); seizures-scoliosis-macrocephaly syndrome (`31388`); gastric mucosal hypertrophy (`31674`); cryptosporidiosis (`32598`); panhypophysitis (`32600`); adenohypophysitis (`32603`); superficial siderosis (`32713`); AA amyloidosis (`32717`); microsporidiosis (`32749`); glycogen storage disease due to liver phosphorylase kinase deficiency (`32796`); ectopic aldosterone-producing tumor (`32811`); Trichinellosis (`32815`); aldosterone-producing adrenal cortex adenoma (`32820`); Zollinger-Ellison syndrome (`32875`); Sheehan syndrome (`32905`); acute liver failure (`32928`); acquired aneurysmal subarachnoid hemorrhage (`32930`); brucellosis (`32932`); cocaine intoxication (`32933`); primary unilateral adrenal hyperplasia (`32943`); shigellosis (`32999`); colchicine poisoning (`33018`); ethylene glycol poisoning (`33020`); serotonin syndrome (`33091`); gallbladder neuroendocrine tumor, grade 1/2 (`33106`); duodenal neuroendocrine tumor, well differentiated, low or intermediate grade (`33119`); jejunal neuroendocrine tumor, well differentiated, low or intermediate grade (`33121`); ileal neuroendocrine tumor, well differentiated, low or intermediate grade (`33122`); sporadic pheochromocytoma/secreting paraganglioma (`33207`); poliomyelitis (`33284`); listeriosis (`33297`); optic pathway glioma (`33318`); renal nutcracker syndrome (`33362`); neuromyelitis optica (`33400`); hereditary pheochromocytoma-paraganglioma (`33431`); neuroleptic malignant syndrome (`33454`); hereditary renal hypouricemia (`33457`); non-secreting paraganglioma (`33462`); boutonneuse fever (`33543`)
- **Missing diseases (0):** ∅ (empty)

### BH2_00003: Zinc chloride → Decreased circulating copper concentration

Name all diseases that are related to a effect/phenotype that is associated with drug Zinc chloride.

**Reference diseases (3):** IRIDA syndrome (`27983`); MEDNIK syndrome (`30928`); COG2-CDG (`32379`)

**Candidate `disease_phenotype_negative` — BRIDGE = UNION**

- **Reached diseases (0):** ∅ (empty)
- **Extra diseases (0):** ∅ (empty)
- **Missing diseases (3):** IRIDA syndrome (`27983`); MEDNIK syndrome (`30928`); COG2-CDG (`32379`)

**Candidate `disease_phenotype_positive` — BRIDGE = UNION**

- **Reached diseases (5):** aceruloplasminemia (`27772`); IRIDA syndrome (`27983`); familial benign copper deficiency (`28458`); MEDNIK syndrome (`30928`); COG2-CDG (`32379`)
- **Extra diseases (2):** aceruloplasminemia (`27772`); familial benign copper deficiency (`28458`)
- **Missing diseases (0):** ∅ (empty)

## Evidence files

`evidence.json` contains the same complete sets for all five validation rows, all three candidate subsets, both constructions, field-role checks and raw-file hashes.

This report presents the investigation before an exclusion record is written. Exclusion and the recomputed global gate, if recorded under the user’s conditional authorization, are separate artifacts.
