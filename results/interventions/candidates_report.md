# S31 — Intervention candidates (protocol §21)

Produced by `scripts/31_candidates.py` at commit `baffcdb1d1e2a1759fbcc2fc0ebe46cf9e97ca2f` (tracked files clean: True). All flagged queries are listed; no case is selected here (the 5 illustrative cases are in the decision log, 2026-11-12, section A).

Candidates: 8 of 8 flagged queries. With a matched control (C): 0.

| query_id | relation_type | mechanism | feature_u | feature_u_name | feature_r | feature_holders | treatment_branch_degree | valid_route_after_block | candidate | control_slots | slots_opened_by_an_agent | eligible_controls | has_matched_control |
|---|---|---|---|---|---|---|---|---|---|---|---|---|---|
| BH2_03356 | gene/protein:disease:drug | WRONG_TURN_HOP2 | 33618 | atrial fibrillation (disease) | off-label use | 3 | 21 | True | True | 0 | 0 | 0 | False |
| BH2_04650 | drug:disease:gene/protein | SHORTCUT | 16843 | Dipivefrin | drug_protein | 3 | 5 | True | True | 0 | 0 | 0 | False |
| BH2_04856 | drug:disease:gene/protein | SHORTCUT | 17226 | Tirofiban | drug_protein | 3 | 2 | True | True | 0 | 0 | 0 | False |
| BH2_05290 | gene/protein:drug:disease | WRONG_TURN_HOP2 | 14052 | Vitamin A | off-label use | 3 | 2 | True | True | 0 | 0 | 0 | False |
| BH2_05778 | effect/phenotype:disease:drug | WRONG_TURN_HOP2 | 29749 | Ewing sarcoma | off-label use | 4 | 11 | True | True | 0 | 0 | 0 | False |
| BH2_05890 | effect/phenotype:disease:drug | WRONG_TURN_HOP2 | 32520 | graft versus host disease | off-label use | 3 | 2 | True | True | 1 | 1 | 0 | False |
| BH2_05997 | effect/phenotype:disease:drug | WRONG_TURN_HOP2 | 33228 | localized scleroderma | off-label use | 3 | 2 | True | True | 0 | 0 | 0 | False |
| BH2_06016 | effect/phenotype:disease:drug | WRONG_TURN_HOP2 | 30800 | juvenile arthritis due to defect in LACC1 | off-label use | 4 | 8 | True | True | 0 | 0 | 0 | False |

## Shared entities (held by ≥ 3 agents)

- **BH2_03356** (s = MYOCD [21987]): W^Q: 14142 Metoprolol (3); 14162 Atenolol (3); 14215 Losartan (3); 14255 Quinapril (3); 14302 Amiodarone (3); 14308 Carvedilol (3); 14317 Captopril (3); 14369 Nebivolol (3); 14605 Candesartan cilexetil (3); 14835 Benazepril (3); 14836 Ramipril (3); 14846 Perindopril (3); 15451 Bisoprolol (3); 15762 Trandolapril (3); 15769 Valsartan (3); 15836 Telmisartan (3); 16210 Eprosartan (3); 16687 Fosinopril (3); 16689 Moexipril (3); 16690 Lisinopril (3). H1: 14142 Metoprolol (3); 14162 Atenolol (3); 14215 Losartan (3); 14255 Quinapril (3); 14302 Amiodarone (3); 14308 Carvedilol (3); 14317 Captopril (3); 14369 Nebivolol (3); 14605 Candesartan cilexetil (3); 14835 Benazepril (3); 14836 Ramipril (3); 14846 Perindopril (3); 15451 Bisoprolol (3); 15762 Trandolapril (3); 15769 Valsartan (3); 15836 Telmisartan (3); 16210 Eprosartan (3); 16687 Fosinopril (3); 16689 Moexipril (3); 16690 Lisinopril (3).
- **BH2_04650** (s = Dipivefrin [16843]): W^Q: 341 BCHE (3); 1494 ADRB2 (3); 1659 ADRA1A (3); 2472 ADRA2A (3); 8038 ACHE (3). H1: none.
- **BH2_04856** (s = Tirofiban [17226]): W^Q: 11356 ITGA2B (3). H1: none.
- **BH2_05290** (s = LRAT [12198]): W^Q: 31820 abetalipoproteinemia (3); 36924 dermatitis (3). H1: 31820 abetalipoproteinemia (3); 36924 dermatitis (3).
- **BH2_05778** (s = Ewing sarcoma [89218], SOURCE_NAME_OVERLAP): W^Q: 14231 Irinotecan (4); 14275 Doxorubicin (4); 14604 Etoposide (4); 14608 Ifosfamide (4); 14715 Coenzyme M (3); 14737 Carboplatin (4); 14793 Docetaxel (4); 14955 Vincristine (4); 15413 Gemcitabine (4); 15481 Topotecan (4); 20336 Temozolomide (4). H1: 14231 Irinotecan (4); 14275 Doxorubicin (4); 14604 Etoposide (4); 14608 Ifosfamide (4); 14715 Coenzyme M (3); 14737 Carboplatin (4); 14793 Docetaxel (4); 14955 Vincristine (4); 15413 Gemcitabine (4); 15481 Topotecan (4); 20336 Temozolomide (4).
- **BH2_05890** (s = Lichenoid skin lesion [91135]): W^Q: 14606 Thalidomide (3). H1: 14606 Thalidomide (3).
- **BH2_05997** (s = Progressive loss of facial adipose tissue [87629]): W^Q: 15438 Sulfadiazine (3); 15982 Sulfasalazine (3). H1: 15438 Sulfadiazine (3); 15982 Sulfasalazine (3).
- **BH2_06016** (s = Quotidian fever [92289]): W^Q: 14175 Nabumetone (4); 14191 Piroxicam (4); 14206 Chloroquine (4); 14262 Salicylic acid (4); 14274 Auranofin (4); 14340 Magnesium salicylate (4); 14347 Hydroxychloroquine (4); 15438 Sulfadiazine (4). H1: 14175 Nabumetone (4); 14191 Piroxicam (4); 14206 Chloroquine (4); 14262 Salicylic acid (4); 14274 Auranofin (4); 14340 Magnesium salicylate (4); 14347 Hydroxychloroquine (4); 15438 Sulfadiazine (4).
