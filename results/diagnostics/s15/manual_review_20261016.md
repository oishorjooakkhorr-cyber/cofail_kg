# S15 manual review and approval — 2026-10-16

Reviewer: **Oishu (researcher)**. Date: 2026-10-16. Machine-readable record: `manual_review_20261016.json`.

## Review basis

The 34 short-name entries, the common system prompt and the 24 captured screening/smoke user messages in results/diagnostics/s15/manual_review_packet.md were checked with AI assistance (Claude, in chat on 2026-10-16, and again in code in step a below). I, Oishu (researcher), accept them on that basis on 2026-10-16.

## Decisions

1. **Short names — Accept all 34 entries (26 queries).** Accept all 34 query/name entries (26 queries). None occurs as a whole word in its starting line, the common system prompt or the question. "AR" (BH2_01282) occurs only inside longer words: "Andarine" in the starting line and the question, and words such as "are" in the system prompt and the question. It never occurs as a whole word, so it carries no information.
2. **Messages — Accept.** Accept the common system prompt and all 24 captured user messages. Each user message is exactly question_text + "\n" + "Starting entity: <start_name> (PrimeKG ID: <start_id>)". Apart from the rule list numbers 1-3, the only numbers in the system prompt are page size (50) and tool budget (30). The " (disease)" suffix in BH2_03750, BH2_03951 and BH2_04474 is PrimeKG's canonical name (protocol §12, decision 2026-10-13) and adds no evaluator information.
3. **Overlaps — Confirmed.** I confirm, as my own researcher decision, all four rows in overlap_review.json, including BH2_05778 (Ewing sarcoma) accepted as full-name, cross-type overlap.
4. **I approve S15.**

| Query | Decision | Classification |
|---|---|---|
| BH2_04007 | accept | contained-phrase overlap |
| BH2_05778 | accept | full-name, cross-type overlap |
| BH2_05971 | accept | contained-phrase overlap |
| BH2_06099 | accept | contained-phrase overlap |

## Per-entry short-name decisions

| Split | Query | Name | Starting entity (ID) | Whole-word hits (line/system/question) | Decision |
|---|---|---|---|---|---|
| expansion | BH2_00244 | F11 | (R)-1-(4-(4-(hydroxymethyl)-1,3,2-dioxaborolan-2-yl)benzyl)guanidine (18371) | 0/0/0 | Accept |
| pilot | BH2_00341 | ADA | 1-Deaza-Adenosine (19259) | 0/0/0 | Accept |
| screening | BH2_00461 | TTR | 2,6-dimethyl-4-[(E)-2-phenylethenyl]phenol (14097) | 0/0/0 | Accept |
| expansion | BH2_00732 | GCK | 3-[(4-fluorophenyl)sulfanyl]-N-(4-methyl-1,3-thiazol-2-yl)-6-[(4-methyl-4H-1,2,4-triazol-3-yl)sulfanyl]pyridine-2-carboxamide (18420) | 0/0/0 | Accept |
| expansion | BH2_00841 | ABO | 4-AMINO-2-OCTYLOXY-6-HYDROXYMETHYL-TETRAHYDRO-PYRAN-3,5-DIOL (16606) | 0/0/0 | Accept |
| expansion | BH2_00874 | UNG | 4-[(1E,7E)-8-(2,6-DIOXO-1,2,3,6-TETRAHYDROPYRIMIDIN-4-YL)-3,6-DIOXA-2,7-DIAZAOCTA-1,7-DIEN-1-YL]BENZOIC ACID (19843) | 0/0/0 | Accept |
| expansion | BH2_01061 | GSR | 6-(3-METHYL-1,4-DIOXO-1,4-DIHYDRONAPHTHALEN-2-YL)HEXANOIC ACID (17531) | 0/0/0 | Accept |
| expansion | BH2_01223 | ALB | Acetrizoic acid (14430) | 0/0/0 | Accept |
| expansion | BH2_01280 | KIT | Ancestim (17285) | 0/0/0 | Accept |
| expansion | BH2_01282 | AR | Andarine (16450) | 0/0/0 | Accept |
| expansion | BH2_02390 | LTF | Nitrilotriacetic acid (18279) | 0/0/0 | Accept |
| expansion | BH2_02780 | F2 | TRANS-4-(GUANIDINOMETHYL)-CYCLOHEXANE-L-YL-D-3-CYCLOHEXYLALANYL-L-AZETIDINE-2-YL-D-TYROSINYL-L-HOMOARGININAMIDE (16099) | 0/0/0 | Accept |
| pilot | BH2_02789 | PGR | Tanaproget (17392) | 0/0/0 | Accept |
| expansion | BH2_04824 | NGF | Solifenacin (14583) | 0/0/0 | Accept |
| pilot | BH2_04828 | XDH | Sulfinpyrazone (14574) | 0/0/0 | Accept |
| expansion | BH2_04856 | CKB | Tirofiban (17226) | 0/0/0 | Accept |
| expansion | BH2_04856 | CKM | Tirofiban (17226) | 0/0/0 | Accept |
| expansion | BH2_04856 | CRP | Tirofiban (17226) | 0/0/0 | Accept |
| expansion | BH2_04856 | GSN | Tirofiban (17226) | 0/0/0 | Accept |
| expansion | BH2_04856 | IL6 | Tirofiban (17226) | 0/0/0 | Accept |
| expansion | BH2_04856 | TNF | Tirofiban (17226) | 0/0/0 | Accept |
| expansion | BH2_04856 | VCL | Tirofiban (17226) | 0/0/0 | Accept |
| expansion | BH2_04856 | VIM | Tirofiban (17226) | 0/0/0 | Accept |
| expansion | BH2_06279 | MCC | X-linked hereditary sensory and autonomic neuropathy with deafness (28259) | 0/0/0 | Accept |
| expansion | BH2_06294 | ATP | acromegaloid facial appearance syndrome (31831) | 0/0/0 | Accept |
| expansion | BH2_06423 | RB1 | chromosome 13q14 deletion syndrome (28362) | 0/0/0 | Accept |
| expansion | BH2_06518 | EPX | eosinophil peroxidase deficiency (32078) | 0/0/0 | Accept |
| pilot | BH2_06865 | C3 | pemphigus vulgaris (30998) | 0/0/0 | Accept |
| expansion | BH2_07325 | ALB | cavernous hemangiomas of face-supraumbilical midline raphe syndrome (30533) | 0/0/0 | Accept |
| expansion | BH2_07343 | CA1 | congenital isolated hyperinsulinism (38889) | 0/0/0 | Accept |
| expansion | BH2_07343 | CA2 | congenital isolated hyperinsulinism (38889) | 0/0/0 | Accept |
| expansion | BH2_07383 | ALB | epithelioid hemangioendothelioma (84235) | 0/0/0 | Accept |
| pilot | BH2_07479 | ALB | lymphangioma (36025) | 0/0/0 | Accept |
| expansion | BH2_07578 | ALB | retiform hemangioendothelioma (84239) | 0/0/0 | Accept |

## Step-a verification (code, read-only)

Rule: case-insensitive whole word (?<!\w)TERM(?!\w), re.IGNORECASE, as tests/test_leakage.py::scan_surface; plus raw case-insensitive substring.

- Captures: 24; distinct system prompts: 1 (SHA256 `c5240f8fa376ca187a69a9a0c2286702c538f60d6bd28cc96a80a0a1f11d8ad1`).
- User messages equal to the exact pattern: 24/24.
- Digit runs in the system prompt: 50, 1, 2, 30, 3 (rule-list enumerators: 1, 2, 3).
- Disease-suffix queries: BH2_03750 `amenorrhea (disease)` (captured: True); BH2_03951 `endometriosis (disease)` (captured: True); BH2_04474 `synovitis (disease)` (captured: True).
- Short-name entries: 34 in 26 queries; whole-word hits: 0.
- Raw substring hits: only BH2_01282 AR — question: are, Andarine; starting_line: Starting, Andarine; system_prompt: are, are.
- Problems: 0.
- Input SHA256: `data/agent_inputs/expansion.jsonl` 290f4323fa80005a6ffc24c3077dd793566d82d4f3995dc26a39961f7306bc4b; `data/agent_inputs/pilot.jsonl` 4c6190d844e8d3a2f14173db9fffa4fd9dd456e5e4cc3b487ea8c4a2ff982361; `data/agent_inputs/screening.jsonl` 4624021f742d1f7a8ece8ef8545033b5481c1de7ec62fba554f952d74f04ba27; `data/agent_inputs/smoke.jsonl` 08610aa6e3331b331ffd78213fab4e88bfda93a15bebe417a113bb3b009df68e; `results/diagnostics/s15/audit-v2.json` 00486a34f3856d95a9a5a0f060c8c1290290151588c5c0d524eaa872550fe24f; `results/diagnostics/s15/source_name_overlap.json` f7dc51563299430e7ee74223c8bb1c0264df509cfed5f88eb4c41bc6e39f3538.

## Wording corrections during review

Step a found two literal mismatches in the first decision text; the researcher supplied corrected wording, recorded above.

- decision 1, AR sentence: initial ""AR" (BH2_01282) occurs only inside longer words ("Andarine", words in the system prompt): not a whole-word match, no information." Finding: AR also occurs inside "Starting" (starting line) and "are" (question).
- decision 2, numbers sentence: initial "the only numbers in the system prompt are page size (50) and tool budget (30)." Finding: The system prompt also contains rule-list enumerators 1., 2., 3.

## Verification notes

- Researcher's corrected AR wording lists "Andarine" and words such as "are"; the code verification also finds AR inside "Starting" in the starting line. All contexts are inside longer words; whole-word count is 0. Full contexts: verification.short_names.

## Unresolved concerns

None.

## Unchanged

SOURCE_NAME_OVERLAP flags, gate populations and pre-registered all/excluded reporting are unchanged. No code, test, protocol, decision rule, config, frozen hash, data or prior evidence file changed. No model call or episode. S16 not started.
