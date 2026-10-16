# S15 remaining manual review packet

Review aid only; no acceptance is recorded by generating this file.
Sources: audit-v2.json (24 captured screening/smoke initial messages), source_name_overlap.json (34 short-name entries), and current agent-input sheets.
Pilot/expansion starting lines below are reconstructed from the input sheets using the audited format, not captured model calls.

## What to decide

For short names, inspect each listed name against its starting line and the common system prompt below. The audit reports no case-insensitive whole-word occurrences; a substring inside a longer word is not automatically a prohibited whole-word match. Record Accept, Concern, or Unsure per query.
For messages, inspect the common system prompt and all 24 captured user messages for unintended evaluator information. Original question text is allowed and outside the prohibited-term scan. The previously accepted canonical-name overlaps remain flagged.
No decisions about medical correctness or model performance are required for this lexical review.

## Common system prompt

Identical in all 24 captured messages. Read once, and compare the short names below against it.

```text
You are a biomedical knowledge-graph agent. You answer questions by exploring a knowledge graph
with two tools.

inspect_entity(entity_id): shows an entity, its type, and the relations connected to it, with
the number of neighbors for each relation.
get_neighbors(entity_id, relation, neighbor_type, page): lists the neighbors of an entity through
one relation, 50 per page. The result tells you the total number of neighbors and
whether more pages exist.

Rules:
1. Use the tools to find the answer. Every entity in your answer must be one you saw in a tool
   result; copy its ID exactly.
2. You can make at most 30 tool calls.
3. When you are finished, reply with only this JSON object and nothing else:
   {"status": "answered", "answers": [{"id": "<ID>", "name": "<name>"}]}
   If you cannot find an answer, reply with only:
   {"status": "no_answer", "answers": []}
```

## Short-name review: all 34 entries grouped into 26 queries

| Split | Query | Short names | Starting entity (ID) | Decision |
|---|---|---|---|---|
| expansion | BH2_00244 | F11 | (R)-1-(4-(4-(hydroxymethyl)-1,3,2-dioxaborolan-2-yl)benzyl)guanidine (18371) | Pending |
| expansion | BH2_00732 | GCK | 3-[(4-fluorophenyl)sulfanyl]-N-(4-methyl-1,3-thiazol-2-yl)-6-[(4-methyl-4H-1,2,4-triazol-3-yl)sulfanyl]pyridine-2-carboxamide (18420) | Pending |
| expansion | BH2_00841 | ABO | 4-AMINO-2-OCTYLOXY-6-HYDROXYMETHYL-TETRAHYDRO-PYRAN-3,5-DIOL (16606) | Pending |
| expansion | BH2_00874 | UNG | 4-[(1E,7E)-8-(2,6-DIOXO-1,2,3,6-TETRAHYDROPYRIMIDIN-4-YL)-3,6-DIOXA-2,7-DIAZAOCTA-1,7-DIEN-1-YL]BENZOIC ACID (19843) | Pending |
| expansion | BH2_01061 | GSR | 6-(3-METHYL-1,4-DIOXO-1,4-DIHYDRONAPHTHALEN-2-YL)HEXANOIC ACID (17531) | Pending |
| expansion | BH2_01223 | ALB | Acetrizoic acid (14430) | Pending |
| expansion | BH2_01280 | KIT | Ancestim (17285) | Pending |
| expansion | BH2_01282 | AR | Andarine (16450) | Pending |
| expansion | BH2_02390 | LTF | Nitrilotriacetic acid (18279) | Pending |
| expansion | BH2_02780 | F2 | TRANS-4-(GUANIDINOMETHYL)-CYCLOHEXANE-L-YL-D-3-CYCLOHEXYLALANYL-L-AZETIDINE-2-YL-D-TYROSINYL-L-HOMOARGININAMIDE (16099) | Pending |
| expansion | BH2_04824 | NGF | Solifenacin (14583) | Pending |
| expansion | BH2_04856 | CKB, CKM, CRP, GSN, IL6, TNF, VCL, VIM | Tirofiban (17226) | Pending |
| expansion | BH2_06279 | MCC | X-linked hereditary sensory and autonomic neuropathy with deafness (28259) | Pending |
| expansion | BH2_06294 | ATP | acromegaloid facial appearance syndrome (31831) | Pending |
| expansion | BH2_06423 | RB1 | chromosome 13q14 deletion syndrome (28362) | Pending |
| expansion | BH2_06518 | EPX | eosinophil peroxidase deficiency (32078) | Pending |
| expansion | BH2_07325 | ALB | cavernous hemangiomas of face-supraumbilical midline raphe syndrome (30533) | Pending |
| expansion | BH2_07343 | CA1, CA2 | congenital isolated hyperinsulinism (38889) | Pending |
| expansion | BH2_07383 | ALB | epithelioid hemangioendothelioma (84235) | Pending |
| expansion | BH2_07578 | ALB | retiform hemangioendothelioma (84239) | Pending |
| pilot | BH2_00341 | ADA | 1-Deaza-Adenosine (19259) | Pending |
| pilot | BH2_02789 | PGR | Tanaproget (17392) | Pending |
| pilot | BH2_04828 | XDH | Sulfinpyrazone (14574) | Pending |
| pilot | BH2_06865 | C3 | pemphigus vulgaris (30998) | Pending |
| pilot | BH2_07479 | ALB | lymphangioma (36025) | Pending |
| screening | BH2_00461 | TTR | 2,6-dimethyl-4-[(E)-2-phenylethenyl]phenol (14097) | Pending |

### Exact starting-line text for short-name review

#### BH2_00244 (expansion): F11

```text
Starting entity: (R)-1-(4-(4-(hydroxymethyl)-1,3,2-dioxaborolan-2-yl)benzyl)guanidine (PrimeKG ID: 18371)
```

#### BH2_00732 (expansion): GCK

```text
Starting entity: 3-[(4-fluorophenyl)sulfanyl]-N-(4-methyl-1,3-thiazol-2-yl)-6-[(4-methyl-4H-1,2,4-triazol-3-yl)sulfanyl]pyridine-2-carboxamide (PrimeKG ID: 18420)
```

#### BH2_00841 (expansion): ABO

```text
Starting entity: 4-AMINO-2-OCTYLOXY-6-HYDROXYMETHYL-TETRAHYDRO-PYRAN-3,5-DIOL (PrimeKG ID: 16606)
```

#### BH2_00874 (expansion): UNG

```text
Starting entity: 4-[(1E,7E)-8-(2,6-DIOXO-1,2,3,6-TETRAHYDROPYRIMIDIN-4-YL)-3,6-DIOXA-2,7-DIAZAOCTA-1,7-DIEN-1-YL]BENZOIC ACID (PrimeKG ID: 19843)
```

#### BH2_01061 (expansion): GSR

```text
Starting entity: 6-(3-METHYL-1,4-DIOXO-1,4-DIHYDRONAPHTHALEN-2-YL)HEXANOIC ACID (PrimeKG ID: 17531)
```

#### BH2_01223 (expansion): ALB

```text
Starting entity: Acetrizoic acid (PrimeKG ID: 14430)
```

#### BH2_01280 (expansion): KIT

```text
Starting entity: Ancestim (PrimeKG ID: 17285)
```

#### BH2_01282 (expansion): AR

```text
Starting entity: Andarine (PrimeKG ID: 16450)
```

#### BH2_02390 (expansion): LTF

```text
Starting entity: Nitrilotriacetic acid (PrimeKG ID: 18279)
```

#### BH2_02780 (expansion): F2

```text
Starting entity: TRANS-4-(GUANIDINOMETHYL)-CYCLOHEXANE-L-YL-D-3-CYCLOHEXYLALANYL-L-AZETIDINE-2-YL-D-TYROSINYL-L-HOMOARGININAMIDE (PrimeKG ID: 16099)
```

#### BH2_04824 (expansion): NGF

```text
Starting entity: Solifenacin (PrimeKG ID: 14583)
```

#### BH2_04856 (expansion): CKB, CKM, CRP, GSN, IL6, TNF, VCL, VIM

```text
Starting entity: Tirofiban (PrimeKG ID: 17226)
```

#### BH2_06279 (expansion): MCC

```text
Starting entity: X-linked hereditary sensory and autonomic neuropathy with deafness (PrimeKG ID: 28259)
```

#### BH2_06294 (expansion): ATP

```text
Starting entity: acromegaloid facial appearance syndrome (PrimeKG ID: 31831)
```

#### BH2_06423 (expansion): RB1

```text
Starting entity: chromosome 13q14 deletion syndrome (PrimeKG ID: 28362)
```

#### BH2_06518 (expansion): EPX

```text
Starting entity: eosinophil peroxidase deficiency (PrimeKG ID: 32078)
```

#### BH2_07325 (expansion): ALB

```text
Starting entity: cavernous hemangiomas of face-supraumbilical midline raphe syndrome (PrimeKG ID: 30533)
```

#### BH2_07343 (expansion): CA1, CA2

```text
Starting entity: congenital isolated hyperinsulinism (PrimeKG ID: 38889)
```

#### BH2_07383 (expansion): ALB

```text
Starting entity: epithelioid hemangioendothelioma (PrimeKG ID: 84235)
```

#### BH2_07578 (expansion): ALB

```text
Starting entity: retiform hemangioendothelioma (PrimeKG ID: 84239)
```

#### BH2_00341 (pilot): ADA

```text
Starting entity: 1-Deaza-Adenosine (PrimeKG ID: 19259)
```

#### BH2_02789 (pilot): PGR

```text
Starting entity: Tanaproget (PrimeKG ID: 17392)
```

#### BH2_04828 (pilot): XDH

```text
Starting entity: Sulfinpyrazone (PrimeKG ID: 14574)
```

#### BH2_06865 (pilot): C3

```text
Starting entity: pemphigus vulgaris (PrimeKG ID: 30998)
```

#### BH2_07479 (pilot): ALB

```text
Starting entity: lymphangioma (PrimeKG ID: 36025)
```

#### BH2_00461 (screening): TTR

```text
Starting entity: 2,6-dimethyl-4-[(E)-2-phenylethenyl]phenol (PrimeKG ID: 14097)
```

## Captured initial user messages: all 24

The system prompt above accompanies every message below. These user messages are copied verbatim from the saved audit.

### BH2_00461 (screening)

```text
Name all diseases that are related to a gene/protein that is associated with drug 2,6-dimethyl-4-[(E)-2-phenylethenyl]phenol.
Starting entity: 2,6-dimethyl-4-[(E)-2-phenylethenyl]phenol (PrimeKG ID: 14097)
```

Decision: Pending.

### BH2_02033 (screening)

```text
Name all diseases that are related to a gene/protein that is associated with drug MYO-029.
Starting entity: MYO-029 (PrimeKG ID: 19601)
```

Decision: Pending.

### BH2_03434 (screening)

```text
Name all drugs that can treat a disease that is associated with gene/protein PSMD3.
Starting entity: PSMD3 (PrimeKG ID: 3248)
```

Decision: Pending.

### BH2_03619 (screening)

```text
Name all effect/phenotypes which are side effects of drug that can treat disease Balo concentric sclerosis.
Starting entity: Balo concentric sclerosis (PrimeKG ID: 84092)
```

Decision: Pending.

### BH2_03750 (screening)

```text
Name all effect/phenotypes which are side effects of drug that can treat disease amenorrhea .
Starting entity: amenorrhea (disease) (PrimeKG ID: 33574)
```

Decision: Pending.

### BH2_03760 (screening)

```text
Name all effect/phenotypes which are side effects of drug that can treat disease androgen insensitivity syndrome.
Starting entity: androgen insensitivity syndrome (PrimeKG ID: 31630)
```

Decision: Pending.

### BH2_03762 (screening)

```text
Name all effect/phenotypes which are side effects of drug that can treat disease angioedema.
Starting entity: angioedema (PrimeKG ID: 39540)
```

Decision: Pending.

### BH2_03850 (screening)

```text
Name all effect/phenotypes which are side effects of drug that can treat disease cervical carcinoma.
Starting entity: cervical carcinoma (PrimeKG ID: 36665)
```

Decision: Pending.

### BH2_03856 (screening)

```text
Name all effect/phenotypes which are side effects of drug that can treat disease chlamydia trachomatis infectious disease.
Starting entity: chlamydia trachomatis infectious disease (PrimeKG ID: 36106)
```

Decision: Pending.

### BH2_03879 (screening)

```text
Name all effect/phenotypes which are side effects of drug that can treat disease clear cell renal carcinoma.
Starting entity: clear cell renal carcinoma (PrimeKG ID: 36937)
```

Decision: Pending.

### BH2_03881 (screening)

```text
Name all effect/phenotypes which are side effects of drug that can treat disease coccidioidomycosis.
Starting entity: coccidioidomycosis (PrimeKG ID: 32651)
```

Decision: Pending.

### BH2_03953 (screening)

```text
Name all effect/phenotypes which are side effects of drug that can treat disease endometrium neoplasm.
Starting entity: endometrium neoplasm (PrimeKG ID: 37038)
```

Decision: Pending.

### BH2_03991 (screening)

```text
Name all effect/phenotypes which are side effects of drug that can treat disease familial male-limited precocious puberty.
Starting entity: familial male-limited precocious puberty (PrimeKG ID: 29908)
```

Decision: Pending.

### BH2_04003 (screening)

```text
Name all effect/phenotypes which are side effects of drug that can treat disease fetal erythroblastosis.
Starting entity: fetal erythroblastosis (PrimeKG ID: 83780)
```

Decision: Pending.

### BH2_04007 (screening)

```text
Name all effect/phenotypes which are side effects of drug that can treat disease folic acid deficiency anemia.
Starting entity: folic acid deficiency anemia (PrimeKG ID: 83880)
```

Decision: Pending.

### BH2_04425 (screening)

```text
Name all effect/phenotypes which are side effects of drug that can treat disease scrub typhus.
Starting entity: scrub typhus (PrimeKG ID: 33542)
```

Decision: Pending.

### BH2_05366 (screening)

```text
Name all diseases that are treated by a drug that is associated with gene/protein OXT.
Starting entity: OXT (PrimeKG ID: 321)
```

Decision: Pending.

### BH2_05686 (screening)

```text
Name all drugs that can treat a disease that has phenotype Cephalohematoma.
Starting entity: Cephalohematoma (PrimeKG ID: 89391)
```

Decision: Pending.

### BH2_05843 (screening)

```text
Name all drugs that can treat a disease that has phenotype Impaired ristocetin-induced platelet aggregation.
Starting entity: Impaired ristocetin-induced platelet aggregation (PrimeKG ID: 88994)
```

Decision: Pending.

### BH2_06427 (screening)

```text
Name all drugs that are associated with gene/protein that is related to disease chronic diarrheal disease.
Starting entity: chronic diarrheal disease (PrimeKG ID: 39126)
```

Decision: Pending.

### BH2_01682 (smoke)

```text
Name all diseases that are related to a gene/protein that is associated with drug Elaidamide.
Starting entity: Elaidamide (PrimeKG ID: 18973)
```

Decision: Pending.

### BH2_03951 (smoke)

```text
Name all effect/phenotypes which are side effects of drug that can treat disease endometriosis .
Starting entity: endometriosis (disease) (PrimeKG ID: 33680)
```

Decision: Pending.

### BH2_04459 (smoke)

```text
Name all effect/phenotypes which are side effects of drug that can treat disease streptococcal meningitis.
Starting entity: streptococcal meningitis (PrimeKG ID: 38087)
```

Decision: Pending.

### BH2_04474 (smoke)

```text
Name all effect/phenotypes which are side effects of drug that can treat disease synovitis .
Starting entity: synovitis (disease) (PrimeKG ID: 36347)
```

Decision: Pending.

## Record your review

Short-name review: Accept all 34 entries, or list query IDs/names with concerns.
Message review: Accept the common system prompt and all 24 captured user messages, or list concerns.
Only record acceptance after inspecting the relevant text. S15 acceptance remains pending until both reviews are completed.
