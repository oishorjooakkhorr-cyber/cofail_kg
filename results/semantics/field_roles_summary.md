# S5 field-role verification — per-relation-type summary

Protocol §3.1 (v1.3.2). Working hypothesis: `hop2` = query entity, `hop1` = bridge, `answer` = targets. Sample: first 5 rows per relation type in SHA256("42" + row_id) order. Any label; §3.2 edge convention; §12 reference policy. Full rows: `field_roles.csv`.

| relation type | rows in dataset | sampled | resolvable | supporting | support | outcome |
|---|---|---|---|---|---|---|
| disease:drug:effect/phenotype | 949 | 5 | 5 | 5 | 100% | PASS |
| disease:drug:gene/protein | 381 | 5 | 5 | 5 | 100% | PASS |
| disease:effect/phenotype:drug | 36 | 5 | 5 | 5 | 100% | PASS |
| disease:gene/protein:drug | 899 | 5 | 5 | 5 | 100% | PASS |
| drug:disease:effect/phenotype | 213 | 5 | 5 | 5 | 100% | PASS |
| drug:disease:gene/protein | 321 | 5 | 5 | 5 | 100% | PASS |
| drug:effect/phenotype:disease | 5 | 5 | 5 | 5 | 100% | PASS |
| drug:gene/protein:disease | 3029 | 5 | 5 | 5 | 100% | PASS |
| effect/phenotype:disease:drug | 546 | 5 | 5 | 5 | 100% | PASS |
| effect/phenotype:drug:disease | 215 | 5 | 5 | 5 | 100% | PASS |
| gene/protein:disease:drug | 577 | 5 | 5 | 5 | 100% | PASS |
| gene/protein:drug:disease | 462 | 5 | 4 | 4 | 100% | PASS |

**§3.1 failure rule.**
- Failing types: none
- Rows covered by failing types: 0 of 7633 (0.00%)
- Rule outcome: **ROLES_SUPPORTED**

**Conflicting and unresolved rows.**
- gene/protein:drug:disease: conflicting none; unresolved ['BH2_05493']

**Provenance.**
- biohopr_revision: `08f06692c3900347e7405ba55ff6a6d330f55ddb`
- kg_fingerprint: `bc5d3fd2f12aeb29398fe4684c83d8c65c7bd5c1edf704573322295bdc6b2e95`
- git_commit: `5ae77f6b929aca5896ef0a6bedc7840e9ae559cb`
- protocol_version: `1.3.2`
- run_time_utc: `2026-10-12T18:44:40+00:00`
