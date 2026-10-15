# Decision Log — CoFail-KG

One entry per decision, newest at the bottom. Never edit an old entry; add a correction entry instead.

Format:

## YYYY-MM-DD — Sx — Title
Decision: <what>
Why: <one or two sentences>
Data seen before deciding: <none / which outputs>
Changes to protocol or decision rules: <section numbers, or "none">

---

## 2026-10-02 — S1 — Protocol v1.0 accepted
Decision: Adopt docs/frozen_pilot_protocol.md v1.0 and docs/decision_rules.md v1.0.
Why: Audited at S1; wording fixes listed below.
Data seen before deciding: none
Changes to protocol or decision rules: <list wording fixes, or "none">

## 2026-10-02 — S1 — Protocol and decision rules revised to v1.1 after audit
Decision: Replace protocol and decision rules v1.0 with v1.1; runbook, CLAUDE.md and provenance updated to match.
Why: The S1 audit found real errors (hop-1 mapping not validated, CONSISTENT without a valid gold bridge, infeasible sampling floors, screening/S21 circularity, D7/§21 circularity, wrong E denominator, Type_B wrongly forbidden) and many underspecified definitions. Item-by-item record: docs/S1_audit_response.md.
Data seen before deciding: none
Changes to protocol or decision rules: see docs/S1_audit_response.md

## <2026-10-02> — S1 — Protocol and decision rules revised to v1.2 after re-audit
Decision: Replace protocol and decision rules v1.1 with v1.2; runbook and CLAUDE.md updated. From now on the protocol covers only rules that can change a scientific result or a gate outcome (protocol §0.3); no further full-protocol audits.
Why: The re-audit found five serious problems (agent inputs vs the data/processed ban; undefined observed totals for the chance baselines; CONSISTENT without all gold names; query grouping key; path tie-break) plus many precision gaps. Every item is resolved in docs/S1_audit_response.md.
Data seen before deciding: none
Changes to protocol or decision rules: see docs/S1_audit_response.md (re-audit section) and docs/CHANGES.md

## 2026-10-02 — S1 — Four consistency fixes after the narrow check
Decision: UNCONFIRMABLE types kept in the primary population; reruns allowed via HOLD, D4 FAIL or the code-change rule; final runtime values re-selectable after S22 only by the §9.1 rules, before S26; §21 mechanisms renamed WRONG_TURN_HOP1/2.
Why: The narrow check found four places where v1.2 sections disagreed.
Data seen before deciding: none
Changes to protocol or decision rules: protocol §7.2, §9.1, §19, §21; runbook S9, S22, S25, S31, troubleshooting.

## 2026-10-02 — S2 — BioHopR revision and question-text field fixed
Decision: BioHopR revision `08f06692c3900347e7405ba55ff6a6d330f55ddb` (from data/raw/biohopr/metadata.json; also in configs/frozen_hashes.yaml as `biohopr_revision`). Question text given to agents: field `hop2_question_multi`, verbatim.
Why: The revision is the dataset commit downloaded at S2 (7,633 2-hop records; the 12 relation-type counts match the paper exactly). `hop2_question_multi` is the only 2-hop field that asks for all answers ("Name all …"); `hop2_question` and `prompt` are single-answer forms.
Data seen before deciding: S2 inspection outputs (field list, results/diagnostics/biohopr/inspection_20.md, hop1_in_question.csv, question-field candidates with examples). No agent outputs.
Changes to protocol or decision rules: protocol §3.1 (Revision and Question-text rows filled in; status [TBD@S2] → [FROZEN] at S2).

## 2026-10-02 — S3 — Answer lists compared as sets
Decision: All comparisons of BioHopR answer lists are set comparisons (order and repeats ignored).
Why: Order in BioHopR answer lists has no meaning; the old wording ("answer list") could be read as order-sensitive, which would affect the S6 mapping scores.
Data seen before deciding: none
Changes to protocol or decision rules: protocol §0.4 (new term), §5.1 wording; runbook S3 item 4.

## 2026-10-12 — S4 — Surrounding whitespace in name lookup
Decision: The researcher approved trimming leading and trailing whitespace as well as collapsing
internal whitespace for S4 name lookup. Original node names remain unchanged in the cache.
Why: Clarifies the open §12 normalization detail noted for S5; names such as "acne " must match "acne".
Data seen before deciding: docs/progress.md and docs/S4_findings.md; the researcher was shown
the "acne " example and answered "Yes—trim surrounding spaces too". No agent outputs.
Changes to protocol or decision rules: none in this implementation. The approval is recorded here;
the explicit clarification of protocol §12 remains for the researcher to authorize with the S4 updates.

## 2026-10-12 — S4 — Correct the release-check interpretation
Decision: With the researcher's explicit instruction to fix the protocol/runbook, replace the
expected 202 direct Troglitazone side effects with publisher-checksum verification and a
sanity check of 17 unique direct drug_effect neighbours for the verified kg.csv.
Why: The existing S4 findings reproduce the 202 as the two-hop answer set in BioHopR row 4518,
via 49 drugs indicated for type 2 diabetes mellitus; it is not Troglitazone's direct degree.
Data seen before deciding: docs/S4_findings.md Report 1 §§3–4; S4 index and independent raw-CSV
checks; publisher kg.csv checksum recorded in the findings; full nodes.csv checksum supplied
by the researcher from the website and matched locally. No experimental agent outputs.
Changes to protocol or decision rules: protocol §3.2 release-check wording and runbook S4
Evaluate item 3. S4 release/ID/storage/convention/type-map fields remain pending; no fingerprint
was written, no answer-construction option was selected, and decision_rules.md was not changed.

## 2026-10-12 — S4 — PrimeKG fingerprint written
Decision: Following the researcher's explicit authorization to update frozen_hashes.yaml,
run `python scripts/04_prepare_primekg.py --freeze` to validate the existing inputs/cache
and write kg_fingerprint once through code.
Why: Record the exact prepared graph for subsequent reproducibility checks.
Data seen before deciding: S4 inspection and implementation reports, raw-file checksum
verification, and the corrected release check. No experimental agent outputs.
Result: `bc5d3fd2f12aeb29398fe4684c83d8c65c7bd5c1edf704573322295bdc6b2e95`,
independently matched to the metadata SHA256. The BioHopR revision is unchanged.
Changes to protocol or decision rules: none; remaining S4 protocol fields and the
answer-construction decision remain pending.

## 2026-10-12 — S4 — Canonical node ID confirmed
Decision: With explicit researcher approval, record x_index/y_index in the edge file as
corresponding to the unique node_index in the node file; return IDs as decimal strings
and order them numerically. Mark only the canonical node ID row [FROZEN] at S4.
Why: The S4 inspection verified these columns rather than assuming their identity.
Data seen before deciding: S4 inspection of 129,375 unique node indices and consistent
edge endpoint metadata; existing index implementation and tests. No experimental agent outputs.
Changes to protocol or decision rules: protocol §3.2 canonical node ID row only.
No code, raw data, metadata or frozen hash changes were needed.

## 2026-10-12 — S4 — Edge storage and traversal finalized
Decision: With explicit researcher approval, freeze the sampled edge-storage finding:
10,000/10,000 sampled rows (seed 42) have same-relation reverse rows; 28/30 labels are
represented, with exposure_cellcomp and exposure_molfunc unsampled. Do not infer that
every graph row or label has a reverse. Adopt either-direction traversal for all labels,
with no directional exceptions, and no direction argument in the §10 tools.
Why: Record the prescribed inspection evidence with its limits and finalize the existing
default navigation rule consistently across reference sets, tools and trace graphs.
Data seen before deciding: S4 inspection report and the explanation of annotations 2 and 3
shown to the researcher. No experimental agent outputs.
Changes to protocol or decision rules: protocol §3.2 Edge storage and Edge convention rows
marked [FROZEN] at S4; §10 direction-argument decision finalized. No code, raw data,
metadata, frozen hashes or answer-construction policy changes.

## 2026-10-12 — S4 — Release and whitespace wording finalized
Decision: With explicit researcher approval, freeze PrimeKG v2.1, DOI 10.7910/DVN/IXA7BM,
using the verified kg.csv (file 6180620) and supplied nodes.csv. Explicitly record the
previously approved leading/trailing whitespace trimming in §12, alongside lower-casing,
NFKC normalization and internal whitespace collapse.
Why: Finalize the verified release and document the implemented name-normalization rule.
Data seen before deciding: S4 findings and inspection report, publisher-checksum comparisons,
17-neighbour real-data check, and the researcher's prior whitespace approval.
Changes to protocol or decision rules: protocol §3.2 Release row marked [FROZEN] at S4;
§12 reference-policy wording clarified. No code, data or frozen hashes changed.
The type map remains pending explanation and approval. S4 closure and the completion
commit are deferred at the researcher's request; no answer-construction option was chosen.

## 2026-10-12 — S4 — Type map finalized
Decision: With researcher approval following the type-map explanation, freeze the identity
mapping from BioHopR to PrimeKG for drug, disease, gene/protein and effect/phenotype.
Why: All four exact node-type labels exist in the inspected graph; no renaming is needed.
Data seen before deciding: S4 node-type inventory and the four-row mapping shown to the
researcher. No experimental agent outputs.
Changes to protocol or decision rules: protocol §3.3 filled with the explicit mapping and
marked [FROZEN] at S4. No code, data or frozen hashes changed. S4 closure and the completion
commit remain deferred; no answer-construction option was chosen.

## 2026-10-12 — S4 — Stage completed
Decision: The researcher authorized completing S4 while leaving the A/B/C answer-construction
decision pending before S5. Mark S4 complete and save a local completion commit.
Why: The ingestion/index requirements, approved protocol entries and fingerprint freeze
are complete; final verification passed.
Data seen before deciding: S4 completion requirements explained to the researcher.
Validation at closure: 45 tests passed; raw inputs and cache validated; frozen metadata
SHA256 matched independently; BioHopR revision unchanged; Troglitazone returned 17 direct
side-effect neighbours; documentation diff checks passed.
Changes to protocol or decision rules: none beyond the previously authorized S4 edits.
The reverse-sample coverage limitation and inferred download date remain documented.
No S5 work, answer-construction decision, push or merge is included in this closure.

## 2026-10-12 — S4 — Answer construction: option C, per relation type
Decision: Adopt option C of docs/S4_findings.md Report 2. At S6 each relation type is scored
under two answer constructions, BRIDGE (stored bridge's targets, T_q^{B*}) and UNION (union over
all valid bridges, T_q), and adopts the one whose hop-2 score reaches the D1 threshold (90%).
Tie rule: if both reach 90%, BRIDGE (T_q^{B*}) is adopted. Neither → the type fails D1 on hop 2.
§7.1 condition 5 and §13 Label A use the adopted construction's reference G_q; all results
are reported overall and split by construction.
Why: S4 found that BioHopR builds answer lists per stored bridge in most types but as the
union over all bridges in disease:drug:effect/phenotype (611 rows). Option C keeps every type
that follows either construction, at the cost of GOLD meaning different things across types.
The tie rule was fixed by the researcher before any S6 result was computed.
Data seen before deciding: docs/S4_findings.md Report 2, which includes a preliminary simulation
on 30-row samples: per-type hop-2 scores under both constructions, CONSISTENT counts and
multi-bridge pool sizes. Those label pairs were the investigator's, not the S6 mapping.
No S6 outputs and no agent outputs.
Changes to protocol or decision rules: protocol §5.1 (hop-2 score per construction; selection
order), new §5.3 (construction rule, tie rule, split reporting), §6 (G_q; source note), §7.1
(condition 5; GOLD_MISSING_FROM_KG and EXTRA_TARGETS use G_q), §13 (rules 3–4 use G_q).
decision_rules.md unchanged. Logged in docs/CHANGES.md.

## 2026-10-13 — S4 — Field-role support defined (§3.1, protocol v1.3.1)
Decision: Add a "Support" definition to the §3.1 field-role verification rule. A sampled row is
resolvable if hop2 resolves as Type_S, hop1 as Type_B, and at least half (and at least one) of
its distinct answer names resolve as Type_T; unresolvable rows are reported and left out of the
95% denominator. A resolvable row supports the working hypothesis if hop2 and hop1 are adjacent,
at least one resolved answer is a Type_T neighbour of hop1, and every resolved answer is a
Type_T neighbour of hop1 or of another Type_B neighbour of hop2 (s never counts). Any label
counts; labels are selected at S6. S5 reports per-row answer and reach counts and does not
determine the answer construction (§5.3, S6).
Why: The previous wording assumed BRIDGE answers (answers are neighbours of the stored bridge),
so S5 would stop on UNION rows whose field roles are correct.
Data seen before deciding: docs/S4_findings.md Report 2, and
results/diagnostics/s5_field_role_preview.csv (55 rows at positions 6–10 per relation type,
disjoint from the S5 sample, exploratory). The S5 sample itself was not viewed. No agent outputs.
Unchanged: the 5-row sample, the SHA256("42" + row_id) ordering, the 95% threshold and the
every-relation-type rule.
Changes to protocol or decision rules: protocol §3.1 (new Support paragraph); header v1.3.1;
runbook S5 prompt step 3. decision_rules.md unchanged. Logged in docs/CHANGES.md.

## 2026-10-13 — S4 — Field-role failure handling (§3.1, protocol v1.3.2)
Decision: A relation type in which fewer than 95% of resolvable sampled rows support the field
roles fails the §3.1 rule; a single small failing type is excluded from all later stages
(decision-log entry) and counts as FAIL in Gate D1, rather than stopping S5. Safeguard: S5 stops
and investigates instead if more than one relation type fails, or if the failing types together
cover more than 1% of the 7,633 2-hop rows. A type with no resolvable sampled row is reported and
treated as failing.
Why: Under "every relation type", a 5-row type (drug:effect/phenotype:disease, all of whose rows
are in the S5 sample) could halt the whole study, while Gate D1 already excludes failing types
individually.
Data seen before deciding: docs/S4_findings.md Report 2, and
results/diagnostics/s5_field_role_preview.csv (55 rows at positions 6–10 per relation type,
disjoint from the S5 sample, exploratory). The S5 sample has still not been viewed; the decision
was made before S5 ran. No agent outputs.
Unchanged: the 5-row sample, the SHA256("42" + row_id) ordering, the 95% threshold and the
Support definition.
Changes to protocol or decision rules: protocol §3.1 (failure handling replaces "otherwise stop
and investigate"; acceptance sentence limited to types not excluded); header v1.3.2; runbook S5
prompt, final sentence. decision_rules.md Gate D1 "Type FAIL" row: new trigger "failed the
protocol §3.1 field-role rule at S5"; such a type is already excluded at S5 and the 2-day
investigation does not apply to it (re-admission after seeing the S5 sample would be post hoc).
Nothing else in decision_rules.md changed. Logged in docs/CHANGES.md.

## 2026-10-13 — S5 — Field roles verified
Decision: Accept the BioHopR field roles: hop2 = query entity, hop1 = bridge, answer = gold
targets (protocol §3.1 Field roles row, [FROZEN] at S5).
Why: Under the §3.1 rule (v1.3.2), all 12 relation types PASS with 100% of resolvable sampled rows
supporting the roles; rule outcome ROLES_SUPPORTED; 0 failing types, so no exclusion. 60 rows
sampled (5 per type), 59 resolvable: BH2_05493 (gene/protein:drug:disease) is unresolvable, its
only answer name not found. 5 rows are supported only through other bridges of hop2 (UNION-style
answers): 3 in disease:drug:effect/phenotype, 2 in effect/phenotype:drug:disease. Hand-checks
with scripts/inspect_kg.py agree with the table: BH2_00004 (Zinc sulfate –drug_effect→ Nausea;
29/29 answers among Nausea's disease neighbours), BH2_06128 (pleural empyema
–disease_phenotype_positive→ Pleural effusion; 44/44 among its drug neighbours), BH2_04078
(hyperargininemia –indication→ Phenylbutyric acid; 33/33 among its effect/phenotype
neighbours). Assumptions:
distinct answer names counted as raw strings (§0.4); counting after §12 normalization gives the
same counts in all 60 rows, so the choice changed nothing. A bridge resolving to the query entity
is not covered by §3.1 and never occurred.
Data seen before deciding: results/semantics/field_roles.csv, field_roles_summary.md and
field_roles_summary.json, produced by commit 5ae77f6 (BioHopR revision 08f06692…, kg_fingerprint
bc5d3fd2…); the three hand-checks; earlier, results/diagnostics/s5_field_role_preview.csv
(exploratory, disjoint rows). No agent outputs.
Changes to protocol: §3.1 Field roles row ([TBD@S5] → [FROZEN] at S5). Header unchanged (1.3.2),
following the S2 and S4 precedent of filling [TBD@Sx] values without a version change.

## 2026-10-13 — S5 — Disease-suffix name fallback (§12, protocol v1.3.3)
Decision: In the §12 reference policy, if no node of the filter type matches and the filter type
is disease, retry once with " (disease)" appended to the normalized name; accept only if exactly
one disease node matches, otherwise unresolved. The §12 agent policy applies the same retry when
matching names against Type_T = disease, before the any-type fallback. Disease-typed only.
Why: 152 answer names in 115 rows (43 distinct strings, all with a trailing space) do not resolve
under §12 as written, and all 152 resolve to exactly one disease node with " (disease)" appended.
They are in effect/phenotype:drug:disease (59 of 215 rows) and gene/protein:drug:disease (56 of
462 rows). Under §5.1 those rows would count as not matching for a naming reason. No hop2 or hop1
name is affected.
Sensitivity check: under the new rule the three S5 rows with unresolved answers (BH2_04897,
BH2_05290, BH2_05493) all resolve fully and still support the roles; gene/protein:drug:disease
becomes 5/5 resolvable and supporting, effect/phenotype:drug:disease stays 5/5. The S5 outcome
(ROLES_SUPPORTED, 0 failing types) is unchanged. Verified by re-running the S5 row analysis on
those rows with the retry.
Data seen before deciding: results/diagnostics/suffix_preview* (exploratory, all 7,633 rows);
docs/S4_findings.md Report 2, including its simulated hop-2 scores for these two types (0.73 and
0.80); the S5 results (results/semantics/field_roles*). No agent outputs. S6 has not run.
Unchanged: the 2026-10-12 trimming decision; decision_rules.md; all thresholds.
Changes to protocol: §12 reference policy (retry sentence) and agent policy step 2 (same retry
for Type_T = disease, before the any-type fallback); header v1.3.3. Logged in docs/CHANGES.md.

## 2026-10-13 — S6 — First-prompt computation (not a mapping approval)

Scope authorized: run the first S6 prompt, explain progress, and ask the researcher for any
needed scientific decision. No authorization to run the second prompt or freeze the mapping.

Computed result: D1 PROCEED; 9 of 12 types PASS, covering 7,377/7,633 rows (96.65%).
Eight passing types propose BRIDGE and one proposes UNION (`disease:drug:effect/phenotype`,
949 rows). 335 validation rows; zero query/bridge skips and zero unresolved sampled answers.
Passing tags: NONE 2, R1_AMBIGUOUS 3, R2_AMBIGUOUS 2, BOTH_AMBIGUOUS 2.

Failing types: `disease:effect/phenotype:drug` (BRIDGE and UNION 3/30),
`drug:effect/phenotype:disease` (both 0/5, also insufficient validation rows), and
`effect/phenotype:drug:disease` (BRIDGE 26/30, UNION 20/30). Exclusions have not been decided.

Researcher decision requested: the five-row type ties `disease_phenotype_negative` and
`disease_phenotype_positive` at zero under both constructions. The positive label reaches gold
diseases plus extras in the checked rows; the negative label misses them. The researcher was
asked whether to retain the tie unresolved for this failing type or select positive for
diagnostics. No choice was made by the assistant, and neither choice can change its FAIL.

Evidence: the four `results/semantics/relation_mapping*`, ambiguity-tag and D1 report outputs;
`results/diagnostics/s6_raw_spot_checks.json` (eight independent raw-CSV checks, all agree);
`results/diagnostics/s6_union_example.json` (BH2_03879: 86 BRIDGE targets, 271 UNION targets,
271 gold targets). Calculation commit `2f2caf1`. 114 tests pass.

Engineering correction: the first run at `a7ffef5` conflated a pending label-tie decision with
an unknown global D1 outcome. Because the only real tie is in a type already known to fail,
the outcome is mechanically PROCEED. The correction is covered by regression tests; the
first attempt is preserved in `results/semantics/s6_attempt_01/`. Every per-type JSON result
and every candidate score is unchanged (candidate CSV byte-identical). No threshold changed.

Changes to protocol or decision rules: none. No `relation_mapping.json` or frozen hash written;
no agent outputs, no S7 work. Details and engineering choices: `docs/S6_implementation.md`.

## 2026-10-13 — S6 — Retain the failed type's unresolved tie

Decision: The researcher selected "Keep the failed type’s tie unresolved (Recommended)" for
`drug:effect/phenotype:disease`. Retain both `disease_phenotype_negative` and
`disease_phenotype_positive` as tied hop-2 candidates under BRIDGE and UNION; choose neither,
including for diagnostics. No construction or R2 is adopted for this failing type.

Why: Both label sets score 0/5 under both constructions. The type also has fewer than the
10 validation rows required by D1, so resolving the tie cannot change its FAIL. The global
D1 outcome remains PROCEED (9/12 types PASS; 7,377/7,633 rows, 96.65%).

Data seen before deciding: the first-prompt results and explanation that the positive label
reaches the gold diseases plus extras while the negative label misses them in the checked
examples. The researcher was explicitly told that neither option freezes a mapping or changes
the FAIL result. No agent outputs.

This records the disposition of the tie only. It does not approve the proposed mappings,
decide exclusions, authorize the second prompt, or freeze any result. The original generated
reports and scores are preserved; their computation-time `NEEDS_DECISION` flag predates this
human disposition. Changes to protocol, decision rules and frozen hashes: none.

## 2026-10-13 — S6 — Exclude drug:effect/phenotype:disease after D1 investigation

Authorization: the researcher explicitly requested that both tied candidates and their scores
remain logged; two failing validation rows with complete reference/reached/extra/missing disease
sets be shown before final exclusion; the five-row sample and permitted D1 causes be investigated;
and, if still failing, the type be excluded and global D1 recomputed. Threshold reductions and
freezing a mapping for this type were expressly prohibited.

Investigation: the pinned 7,633-row BioHopR file contains exactly five records of this type
(BH2_00000 through BH2_00004), matching the protocol's dataset count. All five query entities,
bridges and answer sets resolve; zero rows are skipped. Fresh field-role checks support all five.
Hop 1 (`drug_effect`) scores 5/5. Each query has exactly one valid phenotype bridge, so BRIDGE
and UNION coincide for every row.

| Hop-2 candidate set | BRIDGE exact reproduction | UNION exact reproduction |
|---|---:|---:|
| disease_phenotype_negative | 0/5 (0%) | 0/5 (0%) |
| disease_phenotype_positive | 0/5 (0%) | 0/5 (0%) |
| both labels together | 0/5 (0%) | 0/5 (0%) |

The two singleton sets remain tied after the smallest-set rule; neither is selected.
The two-label set does not break the tie because it has the same score and larger size.

Storage/release checks: a fresh scan of all 8,100,498 raw kg.csv rows reproduced the full
candidate results for all five rows. Outgoing-only, incoming-only, either-direction and
cached-index sets agree for the inspected paths. Raw kg.csv and nodes.csv SHA256s match frozen
metadata; metadata matches kg_fingerprint; raw MD5s match the publisher checksums recorded
at S4. BioHopR's file hash and pinned revision match. No field-role, normalization, edge-storage,
or local release-integrity defect was found. The upstream generation cause of the smaller
BioHopR gold sets is not established; no speculative correction is adopted.

Evidence presented before exclusion: the first two validation rows in prescribed hash order,
with complete named disease sets and IDs in
`results/semantics/s6_failed_type_investigation/report.md`:
- BH2_00004, Zinc sulfate → Nausea: 29 reference diseases; positive reaches 89 (60 extra,
  0 missing), negative reaches 0 (0 extra, 29 missing), under both constructions.
- BH2_00003, Zinc chloride → Decreased circulating copper concentration: 3 reference diseases
  (IRIDA syndrome, MEDNIK syndrome, COG2-CDG); positive reaches those plus aceruloplasminemia
  and familial benign copper deficiency (2 extra, 0 missing); negative reaches none (3 missing).

Decision under the researcher's conditional authorization: **EXCLUDE
drug:effect/phenotype:disease**. The permitted checks are complete, and it still fails both
the minimum-ten-row rule and the 90% hop-2 rule. D1 permits investigation for up to two working
days; it does not require delaying a supported conclusion for the full period. Preserve the
unresolved tie, with no adopted R2 or construction. Record the exclusion in
`results/semantics/relation_type_exclusions.json`.

Recomputed global D1: **PROCEED**, 9 of the original 12 types PASS, covering 7,377 of the
original 7,633 rows (96.65%). Exclusion does not reduce the denominators. Eight passing types
propose BRIDGE; one proposes UNION. The other two FAIL types are not finally excluded by this
decision and await their own review. Current quantities: `results/semantics/d1_after_exclusion.json`.

Changes to protocol, thresholds, scientific definitions, frozen hashes or mappings: none.
Original S6 computation outputs are preserved. No S7 or agent execution. Analytical assertions
checked the five-row count, resolution/support, raw/index agreement, all candidate scores and
global recomputation; no application code changed, so the unchanged unit suite was not rerun.

## 2026-10-13 — S6 — Remaining failures investigated; mixtures exploratory

Authorization: the researcher requested both remaining failed-type investigations and
exploratory construction-mixture analysis. This entry records findings, not a new scientific
rule or additional exclusion. Original S6 samples, thresholds and reference normalization
were retained. Data seen: existing S6 outputs plus the new investigation artifacts below.

Results: disease:effect/phenotype:drug remains FAIL at 3/30 under BRIDGE and UNION;
effect/phenotype:drug:disease remains FAIL at 26/30 BRIDGE and 20/30 UNION. Both have 30
validation rows and hop-1 30/30. All 36 and 215 available query/bridge pairs resolve; no
sample rows or answers were lost to resolution. Original per-type scores reproduce.
A scan of all 8,100,498 raw edges shows outgoing/incoming/cache agreement for all sampled
paths and every R2 subset. Frozen input and S4 release checks pass.

Mixture categories BOTH / BRIDGE-only / UNION-only / NEITHER: 3/0/0/27 for the first type,
17/9/3/1 for the second. First type: every sampled query has one valid bridge; all failures
have extra drugs and no missing drugs. Second type: UNION repairs three BRIDGE failures
but introduces extra targets in nine otherwise-exact rows. Its 29/30 either-construction
coverage is a reference-informed oracle diagnostic, not a validated selection rule or D1 pass.

BH2_05027 explains the remaining second-type failure: the raw reference string
"acute lymphoblastic leukemia " resolves exactly, after trimming, to MONDO_grouped node
35852. The graph reaches MONDO node 33621, "acute lymphoblastic leukemia (disease)".
Section 12 only retries the suffix after zero exact disease matches. No resolver bug is
established and no substitution is applied. Similar names do not authorize merging IDs.
Fresh support checks on the S6 samples support 30/30 and 29/30 respectively; the identity
conflict explains the latter's unsupported row. These diagnostics do not replace the
original frozen S5 samples, which passed 5/5 for both types.

Disposition: investigation complete, both types still FAIL, no additional exclusions
recorded in this request. Existing D1 remains PROCEED, 9/12 types and 7,377/7,633 rows
(96.65%); original denominators retained. The five-row type remains excluded with its tie
unresolved. No mapping is frozen and S7 is not started. Under the existing D1 rule,
exclusion is the next action for types that remain failing; evidence is available for review.

Artifacts: scripts/06_investigate_remaining.py, tests/test_s6_investigation.py, and
results/semantics/s6_remaining_investigation/{report.md,evidence.json,identity_check.json,mixtures.csv}.
Full suite: 119 passed. Runtime assertions checked original score/sample reproduction,
resolution, raw-edge agreement, input hashes, and protected-file hashes. Routine engineering
choices: cached typed neighbors, chunked raw scan, deterministic ID order, four descriptive
categories, and exclusive output creation. No new scientific threshold or method adopted.
Changes to protocol, decision rules, normalization, frozen hashes or mappings: none.


## 2026-10-13 — S6 — Authorize the two remaining exclusions for the time being

Decision: EXCLUDE disease:effect/phenotype:drug and effect/phenotype:drug:disease
from the current primary analysis. Researcher authorization: "okay u may exclude them
for the time being but the report be detailed why they were excluded". Data seen before
deciding: original S6 outputs and the completed investigation/mixture report at 4819ee8.

Why: neither reaches the fixed 90% hop-2 reproduction requirement under either permitted
construction after the D1 investigation. The first scores 3/30 under both, with all 27
failures containing extra drugs. The second scores 26/30 BRIDGE and 20/30 UNION; its
reference-informed either-construction 29/30 is exploratory and not a permitted type rule.
BH2_05027 has a documented 35852-versus-33621 node-identity conflict, with no justified
correction under frozen section 12. Both have 30 validation rows, hop-1 30/30 and original
S5 PASS; insufficient samples and S5 failure are not their exclusion reasons. Raw edge
orientations, cache, release integrity and all candidate subsets were investigated without
finding a permitted repair. Full evidence and alternatives are detailed in
results/semantics/s6_exclusion_decision_02/report.md.

"For the time being" means current EXCLUDED status with evidence retained for later
researcher review, not an expiry or automatic re-admission. No raw records are removed.
Reconsideration requires an explicit documented researcher decision consistent with the
frozen rules; post-result rule changes cannot be silently treated as the original analysis.

All three FAIL types are now excluded (256 dataset rows). The original five-row exclusion
is unchanged and its positive/negative tie stays unresolved. D1 recomputed with the existing
evaluator: PROCEED, 9/12 types, 7,377/7,633 rows (96.65%); denominators unchanged. No excluded
R2 or construction is adopted. No mapping or hash is frozen; S7 has not started.

Updated current exclusion registry and D1 reports; previous versions archived under
results/semantics/s6_exclusion_decision_02/previous/. Prior investigation artifacts and
old decision entries are preserved. Verification assertions checked D1 recomputation,
all-failed-type coverage, preservation of the five-row decision and protected SHA256s.
No code changed; the investigation's 119-passing-test suite was not rerun for this metadata
update. Routine engineering choice: archive previous current reports and add a separate
exclusion decision report. Changes to protocol, decision rules or normalization: none.


## 2026-10-13 — S6 — Approved mapping, constructions and ambiguity tags frozen

Decision: execute S6 prompt part 2 on the nine passing proposals, retaining all three
researcher-authorized exclusions. Authorization: the researcher requested "now execute
the 2nd prompt" after the passing proposals and completed exclusion decisions were explained.
No passing type has an unresolved label tie, so no further scientific choice was needed.
Data seen before deciding: S6 proposals, D1 results, failure investigations, exploratory
mixtures, and all three authorized exclusions (through commit ed00e1a).

Created results/semantics/relation_mapping.json with all 12 types: nine accepted mappings
and three explicit excluded entries. Accepted mappings retain the exact proposed R1, R2
and construction. Excluded entries have null R1, R2 and construction; diagnostic candidate
sets remain in the original proposals/investigations. The five-row type retains its
RETAIN_UNRESOLVED tie disposition, with no candidate selected. The exclusions remain in
force for the current analysis, including the researcher's "for the time being" qualification
recorded in the exclusion registry and detailed report. No automatic re-admission.

Recomputed results/semantics/relation_ambiguity_tags.csv from the final mapping and fresh
PrimeKG candidate-label catalogs using the existing section 5.2 helper. Nine rows are FROZEN;
three are EXCLUDED with no ambiguity tag because no mapping is accepted. Passing tags:
NONE 2, R1_AMBIGUOUS 3, R2_AMBIGUOUS 2, BOTH_AMBIGUOUS 2. These agree with the proposals.
Constructions: BRIDGE 8 (6,428 dataset rows), UNION 1 (949 rows).

The existing write_once helper recorded relation_mapping in configs/frozen_hashes.yaml:
2d609332b6a4ff48423bd7b2f1cb98d8d2d9cafc2fe80c20f7cee8184b8bb8c0
This is SHA256 of the saved mapping file's exact bytes. Existing BioHopR revision and KG
fingerprint values were preserved. The new mapping records proposal, exclusion-registry,
protocol and decision-rule hashes and the source commit. Global D1 remains PROCEED:
9/12 types, 7,377/7,633 rows (96.65%), with all 256 failing-type rows excluded and original
denominators retained.

Verification: 119 tests passed. Assert-based freeze checks verified all original S6
source/input hashes, current proposal/exclusion-registry agreement, the absence of an
existing freeze, every passing type's selection and section 5.3 construction rule, fresh
candidate catalogs, regenerated tag counts, file readback and write-once hash equality.
Original proposed tags are already preserved byte-for-byte in s6_attempt_01. The final
mapping and tag rows were checked again from disk; Git index bytes were checked against
the frozen mapping hash before commit.

Real example: disease:drug:effect/phenotype freezes R1=[indication], R2=[drug_effect],
construction=UNION, tag=R1_AMBIGUOUS. Its original validation scores were BRIDGE 15/30
and UNION 30/30, so section 5.3 requires UNION.

Assumptions: instruction to execute part 2 approves the previously reviewed nine proposals;
all earlier exclusion decisions remain applicable. Routine engineering choices: retain the
existing per_type JSON layout; explicitly represent excluded accepted-label fields as null;
serialize compact UTF-8 with no trailing newline so Git line-ending conversion cannot alter
the frozen mapping bytes; reuse existing ambiguity_tag and write_once helpers without new
application code. Manual review: accepted mapping rows, excluded markers, and the recorded
hash. No new scientific method, score, threshold, normalization or direction rule.

Only the three part-2 artifacts and this required decision-log entry changed. Protocol,
decision rules and historical first-prompt reports were not edited. Their pre-freeze status
statements describe earlier snapshots; this entry and relation_mapping.json record the
current freeze. No S7 work was started.

## 2026-10-15 — S8 — LEAKY_QUESTION interpretation of §7.1
Decision: A query is LEAKY_QUESTION if its question text contains the BioHopR string or the
PrimeKG name of any gold bridge or gold answer, with the at-least-4-characters limit applied to
both bridges and answers. Matching is case-insensitive whole-word or whole-phrase matching on
§12-normalized text (lower-case, NFKC, collapse and trim whitespace) for both name and question
text, with length measured after normalization and Unicode \w boundaries (the match is not
preceded or followed by a word character).
Why: The §7.1 wording does not say whether the 4-character limit applies to bridge names, nor
whether "name" means the BioHopR string or the resolved PrimeKG node name.
Data seen before deciding: none; decided during S8 planning, before any S8 output was computed.
Changes to protocol or decision rules: none (interpretation of existing §7.1 wording).

## 2026-10-15 — S8 — Correction: data seen before the LEAKY_QUESTION interpretation
Decision: The "Data seen before deciding" line of the entry "2026-10-15 — S8 — LEAKY_QUESTION
interpretation of §7.1" should read: the S2 diagnostic count of 76 rows (bridge appears as a
whole word ≥4 chars), shown in the planning question; no S8 output.
Why: The planning question that asked for the interpretation quoted this S2 count; the earlier
entry recorded "none".
Data seen before deciding: the S8 audit, which identified the omission.
Changes to protocol or decision rules: none.

## 2026-10-15 — S9 — Researcher freezes saturation threshold before feasibility

Decision: θ = 0.50 (50%), frozen in protocol §7.2 before calculating D2 step 3.
Researcher authorization: "use theta 50% and do the 2nd part then" after reviewing
the part-1 evidence and the explanation of saturation thresholds.

Evidence seen before deciding: all nine D1 PASS types CONFIRMED on queries containing
no S6 validation-sample row (lowest 506/516 = 98.0620%); all other types remain excluded.
Among 7,362 consistent queries, the maximum saturation share is 0.0515269574 (5.1527%).
Each tested θ (0.30, 0.50, 0.70, 0.90) excludes zero queries overall and per type.
Evidence: results/diagnostics/s9_decision_evidence/decision_evidence.json and .md.

Rationale: retain the protocol's recommended 0.50; the sensitivity table gives no reason
to change it. Saturation remains a strict share > θ comparison. No mapping, name
resolution, consistency, leakage or Gate D2 rule is changed. This fills the scheduled
S9 threshold choice; no primary population or feasibility outcome was computed before
this entry. Part 2 is now authorized under the existing rules.

## 2026-10-15 — S9 — Primary population and Gate D2 GREEN

With θ = 0.50 already frozen above, applied protocol §7.2 inclusion and the ordered
D2 step-3 rules without changing thresholds. Part-1 mapping confirmation was recomputed
and matched the saved evidence exactly: all nine D1 PASS types CONFIRMED.

Input: 7,377 queries from the nine D1 PASS types (the 256 dataset rows in three D1 FAIL
types remain excluded upstream). Excluded 201 queries: 15 INCONSISTENT and 186
LEAKY_QUESTION, with no overlap; 0 SATURATED, 0 unconfirmed mappings. Primary population
N_P = 7,176: 6,575 SINGLE_BRIDGE and 601 MULTI_BRIDGE queries. Per-type counts:
disease:drug:effect/phenotype 847; disease:drug:gene/protein 376;
disease:gene/protein:drug 852; drug:disease:effect/phenotype 213;
drug:disease:gene/protein 321; drug:gene/protein:disease 3,028;
effect/phenotype:disease:drug 503; gene/protein:disease:drug 577;
gene/protein:drug:disease 459. All nine have ≥20, so K = 9.

Gate D2: GREEN. The first rule (N_P < 150) is false; the next rule
(N_P ≥650 and K ≥5) is true. Continue as planned; S10 has not been started.

Artifacts: data/processed/primary_population.csv, primary_population_summary.json,
primary_population_report.md; implementation details: docs/S9_implementation.md.
Full suite: 170 passed (12 new part-2 tests). Independent CSV readback verified exact
membership against S8 predicates, uniqueness, per-type and multiplicity counts, checksum,
and Gate D2. Source/input hashes and the pre-run decision-log hash are recorded in the
summary. Historical S8 and S9 part-1 outputs are preserved unchanged.

## 2026-10-15 — S10 — Confirm pilot default and freeze sampling artifacts

Researcher authorization: "okay carry on the work of s10". Retained and confirmed
the existing protocol §8 DEFAULT: pilot 100 queries, 25 SINGLE_BRIDGE / 75 MULTI_BRIDGE,
seed 42. No quota, allocation, threshold or mapping rule was changed.

Applied the frozen query-sampling algorithm to the 7,176-query primary population in
screening → smoke → pilot → expansion order. Results: screening 20 (5 single/15 multi),
smoke 4 (1/3), pilot 100 (25/75), expansion reserve 400 (100/300). No shortfalls.
All 524 queries are distinct; all six pairwise intersections are empty. Pilot and
expansion each contain all nine D1 PASS types. Type floors are applied separately
within each multiplicity group; only two types have multi-bridge population queries.

Created four evaluator manifests and four agent-input sheets. Agent lines contain
exactly query_id, question_text, start_name and start_id, with canonical starting names
from PrimeKG. No evaluator fields are present in agent sheets. Added SHA256 values for
all eight JSONL artifacts under the write-once manifests key in frozen_hashes.yaml;
existing BioHopR revision, KG fingerprint and mapping values are preserved.
Filled configs/pilot.yaml; sampling report and source/input provenance are saved under
data/processed/manifests/. Details: docs/S10_implementation.md.

Verification: 183 tests passed (13 new). Two actual script runs produced byte-identical
artifacts, config, report, provenance and frozen-hash file. Independent Fraction-based
apportionment and SHA256 ordering reproduced every sampled ID; readback verified all
field sets, question/start identity, pairwise disjointness and eight frozen hashes.
Inspected the first ten pilot questions; no edits were made to sampled question texts.
Protocol, decision rules, primary population and earlier results are unchanged.
S10 is complete; S11 has not started.

## 2026-10-15 — Publishing through S10 — Reconcile upstream S8 checkpoint

Fetching GitHub before the authorized push found S8 commit 6436653. Its leakage
interpretation entries are preserved above. All nine upstream files are preserved
byte-for-byte under results/diagnostics/s8_github_checkpoint/, and the original commit
is retained in the merge history. The active local schema is retained for compatibility
with the completed S9/S10 pipeline; the checkpoint's tests remain in that snapshot.

Compared every query on all S9 input fields: 7,377/7,377 agree on status, primary reason,
leakage, saturation, validation-sample overlap and multiplicity. Updated active leakage
matching to include normalized raw and resolved graph names exactly as the recorded
upstream interpretation requires; recalculation reproduced all saved leakage/status labels.
S9 evidence/population and all eight frozen S10 sample hashes remain unchanged.
This is an implementation/history reconciliation, not a new scientific choice.
Details: docs/S8_reconciliation.md; machine comparison: checkpoint/comparison.json.

## 2026-10-15 — S11 implementation — T1 approval pending

Researcher requested S11 implementation and questions where their decisions are
needed. Implemented only the agent-facing KG environment and proposed T1 schemas,
using protocol §3.2, §9.1 and §10. Configuration remains explicit; screening values
50/30 were used for verification, without selecting final S21 values.

Verification: 227 tests passed (42 new); fresh-process isolation checks reject
evaluation imports and processed/results file reads. Real screening query BH2_02033
(MYO-029, ID 19601) returned 329 unique drug_drug neighbors across seven pages;
every item matched the existing researcher inspection CLI. Full call log and source
hashes: results/diagnostics/s11_tools.json. An intentional in-memory pagination
mutation was detected by the test; disk source was unchanged.

T1 descriptions and all engineering choices are recorded in docs/S11_implementation.md.
Approval is explicitly pending, not inferred from the request to implement. No
`tools` entry was added to frozen_hashes.yaml. Protocol, decision rules, prior frozen
hashes and earlier artifacts remain unchanged. No experimental models ran; S12
has not started. Finalize S11 after researcher approval of the concrete wording.

## 2026-10-15 — S11 complete — T1 wording B approved and frozen

After reviewing alternatives A/B/C and their neutrality, the researcher instructed:
"okay lock B, and commit". Applied option B exactly to both tool descriptions;
parameter descriptions are unchanged. The wording describes ordering, result
fields and pagination without directing relation, node-type or answer selection.
The approved text is reproduced in docs/S11_implementation.md.

Used the existing write_once helper to add the SHA256 of tool_schemas.py as `tools`:
fe95093be50073aca922360645240d4410737fb39f11061aa1f5f2df0a8b0bab.
All earlier frozen values are preserved. Repeating the same freeze changes no bytes.
The original real-graph evidence remains unchanged with its historical draft-schema
hash; kg_env.py is unchanged from that verified run.

Final suite: 228 passed (43 S11 tests), including a new check that source bytes match
the frozen identity. Exact option-B wording was checked before freezing. Protocol
and decision rules are unchanged. S11 is complete; no model ran and S12 has not started.

## 2026-10-15 — S12 — §14.2 tie-break pairing (protocol v1.3.4)

§14.2 tie-break (3) compares a sequence of (numeric node ID, label) pairs, but a path
has one more node than labels, so the pairing was not fixed. Researcher decision: each
edge u –r→ v contributes (numeric u, r), the protocol's (u, r) step unit, so a path is
compared in the order s, r1, n1, r2, …. For paths of ≤ 2 edges this gives the same
result as (target node, label), because a creation-index tie needs a shared call. The
readings can differ only for paths of ≥ 3 edges, which affect only the secondary
path-level metrics. Decided before any agent run; no data seen.
Changes to protocol: one clarifying line in §14.2; header 1.3.3 → 1.3.4.
