# S5 field-role preview — per-type summary

**Exploratory evidence, disjoint from the S5 sample, viewed before the §3.1 amendment decision.**

Rows 6–10 per relation type in SHA256("42" + row_id) order; the first 5 (the S5 sample) were
never analysed. Not the S5 check: no construction chosen, no label selection, no pass/fail.
Counts are answer names (set semantics, §0.4). Reach columns cover resolved answers only and
are summed over rows whose structure was computed. Full table: `s5_field_role_preview.csv`.

| relation type | rows | s unresolved | bridge unresolved | computed | s–bridge adjacent | answers (resolved / unresolved) | via stored bridge | only via other bridge | via neither |
|---|---|---|---|---|---|---|---|---|---|
| disease:drug:effect/phenotype | 5 | 0 | 0 | 5 | 5/5 | 529 / 0 | 257 | 272 | 0 |
| disease:drug:gene/protein | 5 | 0 | 0 | 5 | 5/5 | 70 / 0 | 70 | 0 | 0 |
| disease:effect/phenotype:drug | 5 | 0 | 0 | 5 | 5/5 | 648 / 0 | 648 | 0 | 0 |
| disease:gene/protein:drug | 5 | 0 | 0 | 5 | 5/5 | 24 / 0 | 24 | 0 | 0 |
| drug:disease:effect/phenotype | 5 | 0 | 0 | 5 | 5/5 | 97 / 0 | 97 | 0 | 0 |
| drug:disease:gene/protein | 5 | 0 | 0 | 5 | 5/5 | 103 / 0 | 103 | 0 | 0 |
| drug:effect/phenotype:disease | 0 | no disjoint rows available | | | | | | | |
| drug:gene/protein:disease | 5 | 0 | 0 | 5 | 5/5 | 184 / 0 | 184 | 0 | 0 |
| effect/phenotype:disease:drug | 5 | 0 | 0 | 5 | 5/5 | 23 / 0 | 23 | 0 | 0 |
| effect/phenotype:drug:disease | 5 | 0 | 0 | 5 | 5/5 | 70 / 1 | 70 | 0 | 0 |
| gene/protein:disease:drug | 5 | 0 | 0 | 5 | 5/5 | 164 / 0 | 164 | 0 | 0 |
| gene/protein:drug:disease | 5 | 0 | 0 | 5 | 5/5 | 4 / 1 | 4 | 0 | 0 |
