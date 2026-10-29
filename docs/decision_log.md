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

## 2026-10-15 — S13 — Ollama client and synthetic software check

Researcher requested: "Run the prompt of s13". Implemented only the S13 client,
HTTP timeout config, mocked tests and two-call diagnostic per the runbook and
protocol §9.1, §9.5, §19. No scientific decision was needed or made.

Used the existing installed qwen3:4b, 4.0B, Q4_K_M; native tools advertised by
the local server. Full digest before/after both calls:
359d7dd4bcdab3d86b87d73ac27966f4dbb9f5efdfcc75d34a8764a09474fae7.
Plain reply: Hello! (16 prompt/209 generated tokens, 46.914 s). Native dummy
tool call: add(a=2,b=3) (146/295 tokens, 3.111 s). Both sent temperature 0,
seed 42, num_ctx 8192, num_predict 4096. Complete requests/raw responses:
results/diagnostics/s13_ollama.json. No biomedical inputs or evaluation data used.

Engineering choices (including exact OOM phrases, 120-second HTTP timeout,
CONNECTION classification for transport timeouts without retry, and fixed two
connection-only retries) are documented in docs/S13_implementation.md. They do
not choose S21 final settings. Episode TIMEOUT precedence remains the S14 runner's
responsibility. Gate D3 remains unassessed; configs/models.yaml remains unfilled.

Tests: 294 passed (45 new). Full suite run outside sandbox after four existing
S12 hard-link tests hit sandbox permissions; tests/code were not weakened.
Protocol, decision rules, earlier data/artifacts and frozen hashes unchanged.
S13 complete; S14 not started.

## 2026-10-15 — S13 follow-up — explicit think and host verification; commit held

Researcher requested exact execution/install locations, unchanged S12 saver
verification in the host environment, mandatory config-driven think, and no
commit until their reply. Original S13 commit f79165a already existed before
this instruction; it is preserved and no further commit has been made.

Added required boolean think to the client and top-level chat payload; the
diagnostic loads config["think"] with no fallback. Config true is an S13
synthetic-check setting only, not a decision for the experiment. Thinking output
remains untouched in raw response/message. Both true/false and omission/null
handling tested. Experimental thinking policy remains a researcher decision
to record before S20; no scientific protocol/rule/frozen hash was edited.

Verified Windows host DESKTOP-5903S8A, project E:\Phitron Thesis\cofail_kg,
Ollama executable .venv\ollama\ollama.exe, API 127.0.0.1:11434, model manifest
D:\Models\manifests\registry.ollama.ai\library\qwen3\4b and referenced blobs.
Outside sandbox, plain `.\.venv\Scripts\python.exe -m pytest -q`: 301 passed,
zero skips/failures, no temp-dir override or saver workaround. Additional probe
under the actual results/runs exercised the unchanged S12 saver, save/load,
hard-link identity and refusal to overwrite an existing record/link target.
Probe files cleaned up. Evidence: results/diagnostics/s13_environment_check.json.

New synthetic diagnostic with explicit think:true succeeded; raw thinking saved
in results/diagnostics/s13_ollama_explicit_think.json; old diagnostic preserved.
No biomedical episode, S14 work or Gate D3 choice. Researcher has not yet confirmed
the real-episode execution environment: verified host works outside sandbox;
current sandbox still blocks the saver. Review reply: docs/S13_review_reply.md.


## 2026-10-16 — Fix verification failures; implement S14 for review

Researcher requested fixes, explicitly chose to complete S14 while keeping its
existing tests active, and chose think=true for the single real S14 example.
Restored think=true in configs/ollama.yaml for the S13 synthetic diagnostic,
as already described by the 2026-10-15 decision; no experimental policy inferred.
Implemented the exact runbook templates, runner and single-example launcher.
Full host suite: 348 passed in 10.02 s, with no skips or exclusions. S12 saver is
unchanged; host execution and a pre-inference results-directory hard-link check
address the restricted-sandbox persistence limitation operationally.

One actual episode, BH2_00461 with qwen3:4b and the frozen screening settings,
was saved under s14-review-20261016 with status PARSE_FAIL. Both replies ended
at 4096 generated tokens, with thinking but empty content and no native calls.
The runner sent exactly one fixed re-prompt. Prompt tokens were 598/627,
identity was stable, and full raw messages were retained. No answer or route was
produced; no further generation or setting/prompt change was made to obtain a pass.
The initial launcher connection failure happened before the episode; the existing
local Ollama server was started on localhost using D:\Models before the one run.

Report: docs/S14_implementation.md. P1 hash is
8f93b7c42ef7a90f64bbcd83e6b77db62e4f3c6b0c08a45f068b435a9c655265.
P1 is not frozen: runbook S14 / protocol 9.3 require researcher review and approval.
The single-example thinking choice does not select the later experimental policy.
No protocol/frozen-hash change, commit, S15 work or model-selection decision.


## 2026-10-16 — Authorized S14 diagnostic: thinking disabled, output cap 6144

Researcher requested one repeat with think=false and a moderately larger output
window compatible with the GPU. RTX 3060 Ti has 8192 MiB VRAM; pre-run nvidia-smi
reported 679 MiB used and 7346 MiB free. Earlier Ollama evidence fitted all 37/37
layers on GPU at num_ctx=8192 (about 3697 MiB model/context/compute allocation).
Selected num_predict=6144 (50% above the 4096 default), retaining num_ctx=8192,
qwen3:4b, P1, the same first screening query, temperature 0, seed 42, page size 50,
budget 30 and 600-second episode timeout. This is a diagnostic deviation from
screening, explicitly requested by the researcher; no frozen setting changes.
Run ID: s14-nothink6144-20261016. Prior failed record remains untouched.
Added an explicit diagnostic output-cap CLI option; default remains 4096.
Full host suite before generation: 351 passed (no skips/exclusions).
GPU use will be sampled during the episode; no success outcome is presumed.


S14 diagnostic outcome (same date): one episode completed as PARSE_FAIL after
174.107482 s, but four native tools succeeded and returned 21 disease entries
through TTR. Both final JSON suffixes exactly matched those returned ID/name pairs;
reasoning prefixes made the complete replies invalid under unchanged protocol 9.4.
GPU sampled peak 4714/8192 MiB, full model GPU resident, no OOM; all six turns
stopped before the 6144 cap. The final prompt was 7295 tokens and two context
shifts occurred during its long response.

Render-only inspection (no further generation) confirmed identical true/false
prompts ending in an open thinking tag, and two malformed rendered JSON tool
definitions. The installed template uses .Function without JSON serialization
and lacks a false-thinking closing prefix. A two-expression repair proposal was
saved as results/diagnostics/s14_qwen3_template_proposed.Modelfile but was not
installed or run. Original model and strict parser unchanged. Root-cause evidence,
limitations and proposed validation: docs/S14_nothink6144_diagnostic.md.

## 2026-10-16 — Authorized template repair and one S14 repeat

Researcher requested repair and rerun. Created the separate local variant
cofail-qwen3:4b-templatefix from the installed weights, correcting tool JSON
serialization and adding the proposed false-thinking closing prefix. Actual
Ollama rendering validates both tool definitions and distinct true/false prefixes.
Added an explicit diagnostic model override and regression; full host suite:
352 passed, no skips/exclusions. Original model and both failed records preserved.

One repeat with think=false, num_predict=6144, num_ctx=8192 completed SUCCESS in
101.511760 s after the existing single JSON re-prompt. Four successful native
calls; 21 final ID/name pairs match the returned disease list and inspection CLI.
Sampled GPU peak 4742/8192 MiB; full model GPU resident. No parser relaxation.

Corrected earlier assumption: installed qwen3:4b metadata identifies
Qwen3-4B-Thinking-2507, whose official model card supports only thinking mode.
Reasoning persisted despite the changed prefix. This is a successful diagnostic,
not validation of non-thinking behavior or a replacement experimental model.
True non-thinking requires a researcher-selected compatible set of weights.
No model download, P1 freeze, frozen protocol change, gold scoring, S15 or commit.
Engineering choices, exact identities and evidence: docs/S14_template_repair.md.

## 2026-10-16 — Researcher approval and freeze of P1

Researcher authorized: "approve it if s14 didnt required broader reliability".
Runbook S14 requires one real example and specified trace/format checks; it does
not require broader reliability or gold-answer scoring. The condition is met.
The exact unfilled P1 text in src/cofail_kg/agents/prompts.py was checked verbatim
against the runbook and frozen through the existing write_once helper as:
prompt: 8f93b7c42ef7a90f64bbcd83e6b77db62e4f3c6b0c08a45f068b435a9c655265

All existing frozen values were preserved; repeating the same write was verified
to be a no-op. The successful diagnostic used this unchanged P1. Historical
records retain their original draft-review provenance. This approval does not
select experimental weights, thinking policy or token settings, accept the
diagnostic context margin, authorize a commit, or begin S15. No new design choice.

Subsequent authorization: researcher said "okay commit" after being told this
would create the local `S14: agent runner and prompt P1` commit without pushing.
The runner and diagnostic evidence already exist in checkpoint 8322145; this
commit records the P1 freeze and approval. Unrelated backup-script work is excluded.
Pre-commit verification: 352 tests passed; frozen prompt matches the implementation.


## 2026-10-16 — S15 strict leakage failure retained

Researcher authorized execution of the S15 audit plan. No model calls were made.
Protocol §19.1(a) produces one case-insensitive whole-word match: Folic acid,
additional valid B_q bridge ID 14678, within BH2_04007's starting entity name
folic acid deficiency anemia (83880). Gold bridge is Cyanocobalamin (14706).
No evaluation data was injected; the literal lexical rule still fails.

After reviewing this finding, researcher explicitly chose: "Keep strict failure;
decide a remedy later". Do not add exceptions, exclude the query, alter matching,
change the starting name, or mark the failure xfail. No protocol revision or
scientific remedy was authorized. S15 is not accepted and S16 is not started.

Checks (b)-(d) pass on audited paths; focused tests 25 passed/1 failed; complete
sandbox suite 383 passed/1 failed, no skips/exclusions. TTR for BH2_00461 remains
on the manual-review list, absent from both scanned surfaces. Full evidence and
engineering choices: docs/S15_implementation.md and results/diagnostics/s15/.
Production modules, frozen hashes, protocol, data and episodes are unchanged.


## 2026-10-16 — S15 source-name overlap amendment and pre-registered split report

Researcher explicitly authorized the narrow §19.1(a) exemption and later confirmed
the chronology correction: before any pilot model run or co-failure results.
No entry in configs/frozen_hashes.yaml covers the protocol; that file is unchanged.
Only check (a) of the Leakage test row was amended, with this text:

Source-name overlap exemption (added 2026-10-16, before any pilot model run or co-failure results): a match is not a failure when all of these hold: (i) the matched term is the name of a B_q member that is neither a gold bridge nor a gold answer; (ii) the matched span lies entirely within start_name; (iii) start_name equals the PrimeKG canonical name of node s. Each such query is flagged SOURCE_NAME_OVERLAP and listed in the audit output. Every other match still fails, including any match of a gold, T_q, ID, label, relation-type or evaluator term, and any match outside start_name. SOURCE_NAME_OVERLAP never changes an answer set or a gate input. Every co-failure metric (§16) and chance-baseline comparison (§17) is reported on all queries and again with SOURCE_NAME_OVERLAP queries excluded. Gates use all queries.

Why: §9.3 requires the canonical starting name, repeating the entity named in the
question, which is outside the prohibited-term scan. No evaluator-derived
annotation is added. The exemption requires the matched span to lie inside the
exact canonical start_name; it does not require the name to occur verbatim in
the question (the documented disease-suffix cases remain eligible).

Evidence for this decision: lexical audit counts over 524 input rows, with four
non-gold B_q name overlaps: screening BH2_04007; pilot BH2_05778; expansion
BH2_05971 and BH2_06099. Each has two valid bridges, with the matched member
non-gold. No gold, T_q, ID or label matches, and no system prompt matches.
The earlier S14 diagnostic model episodes and reviewed outputs already existed
and remain historical evidence (docs/S14_template_repair.md); this is not a
claim that no model had ever run. No pilot or co-failure results had been seen.
This S15 amendment makes no model call and creates no episode.

Under §20, this is an explicitly authorized frozen-item change before pilot
results. It replaces the earlier "keep strict failure; decide later" hold.
All original failure evidence is retained. SOURCE_NAME_OVERLAP is evaluator-only;
answer sets, sample membership and gate populations are unchanged. Reporting
every §16 metric and §17 comparison with and without flagged queries is now
pre-registered; gates use all queries. Reporting execution belongs to later
stages. No decision_rules.md change, S16 work or commit is authorized here.

Revision verification: 43 focused tests and all 401 sandbox tests pass, no skips
or deselections. The 524-row scan confirms exactly the four expected flags and
zero failures; 34 short-name query/name entries require manual review. New
evidence is versioned under results/diagnostics/s15/; original evidence and all
protected files remain unchanged. Manual review is pending; no commit made.

## 2026-10-16 — S15 per-row overlap decisions

Researcher requested per-row decisions in the audit evidence, specifying
contained-phrase acceptance for chat-table rows 1, 3 and 4, and authorizing
either acceptance as full-name, cross-type overlap or exclusion for row 2.
Recorded in `results/diagnostics/s15/overlap_review.json`:

| Chat row | Query | Decision | Classification |
|---|---|---|---|
| 1 | BH2_04007 | Accept | contained-phrase overlap |
| 2 | BH2_05778 | Accept | full-name, cross-type overlap |
| 3 | BH2_05971 | Accept | contained-phrase overlap |
| 4 | BH2_06099 | Accept | contained-phrase overlap |

For row 2 the assistant selected the authorized acceptance option: canonical
starting phenotype node 89218 and non-gold bridge disease node 29749 share the
name Ewing sarcoma. The approved §19.1(a) exemption permits full-name containment.
No new scientific rule, exclusion or protocol change is introduced. All four
retain SOURCE_NAME_OVERLAP; official gates include them and pre-registered
sensitivity reports exclude them. Original automated evidence is unchanged.
Short-name and captured-message review remain pending; this entry does not
claim full S15 acceptance or absence of overlap effects on model behavior.

## 2026-10-16 — S15 manual review and approval

Reviewer: Oishu (researcher). Review basis, as stated by the researcher: the 34
short-name entries, the common system prompt and the 24 captured screening/smoke
user messages in `results/diagnostics/s15/manual_review_packet.md` were checked
with AI assistance (Claude, in chat on 2026-10-16, and again in code), and the
researcher accepts them on that basis on 2026-10-16.

Decisions:
1. Short names: all 34 query/name entries (26 queries) accepted. None occurs as
   a whole word in its starting line, the common system prompt or the question.
   "AR" (BH2_01282) occurs only inside longer words: "Andarine" in the starting
   line and the question, and words such as "are" in the system prompt and the
   question. It never occurs as a whole word, so it carries no information.
2. Messages: the common system prompt and all 24 captured user messages accepted.
   Each user message is exactly question_text + "\n" + "Starting entity:
   <start_name> (PrimeKG ID: <start_id>)". Apart from the rule list numbers 1-3,
   the only numbers in the system prompt are page size (50) and tool budget (30).
   The " (disease)" suffix in BH2_03750, BH2_03951 and BH2_04474 is PrimeKG's
   canonical name (protocol §12, decision 2026-10-13) and adds no evaluator
   information.
3. Overlaps: the researcher confirms, as their own decision, all four rows in
   `overlap_review.json`, including BH2_05778 (Ewing sarcoma) accepted as
   full-name, cross-type overlap. This supersedes the earlier provenance note
   that the assistant selected that option.
4. **S15 approved.**

Code verification (read-only; same whole-word rule as tests/test_leakage.py,
plus raw substring): 24 captures, exactly one distinct system prompt, 24/24 user
messages match the exact pattern; 34 entries in 26 queries, 0 whole-word hits;
the only raw substring hit is AR in BH2_01282 (inside Starting, Andarine and
are). Verification found two literal mismatches in the first decision wording;
the researcher supplied the corrected wording above. No concerns unresolved.
Record: `results/diagnostics/s15/manual_review_20261016.json` and `.md`.

This supersedes the "pending" status in the two preceding S15 entries, which
are retained. SOURCE_NAME_OVERLAP flags, gate populations and the pre-registered
all/excluded reporting are unchanged. No code, test, protocol, decision rule,
config, frozen hash, data or prior evidence change; no model call or episode.
S16 requires a separate researcher instruction.

## 2026-10-17 - S16 acceptance and pilot reporting requirement

Decision: the researcher accepts S16's normalization behavior and verification
evidence, including ID precedence and the recorded unresolved-duplicate policy.
Unresolved deduplication uses exact submitted `(id, name)` pairs: no case or
whitespace folding and no ID type coercion. This is the researcher's conservative
reading of protocol §12. The name/ID mismatch flag is literal and diagnostic only;
it does not override ID precedence or independently change evaluation labels.

For the pilot results, report any unresolved answers that would merge under
normalized comparison. This is an additional diagnostic report, not a change to
official deduplication or scoring. The precise counterfactual comparison rule
must be stated in that report; no alternative normalization rule is selected here.

Evidence reviewed in this conversation: the S16 implementation report, protocol
§12, duplicate-policy tests and saved verification evidence (49 focused tests,
443 full-suite tests, and 21/21 saved S14 answers resolved by ID). The researcher
explicitly accepted this evidence; no new checks or model calls were run for
this acceptance record.

Changes to protocol, decision rules, code, data and frozen settings: none.
This entry supersedes earlier pending S16 acceptance statements. S17 has not
been authorized by this acceptance.

## 2026-10-17 - S16 authorization and unresolved duplicate identity

Decision: researcher explicitly requested starting S16 and selected removal of
identical unresolved (submitted ID, submitted name) pairs, with distinct unresolved
submissions kept separate. Resolved answers are deduplicated by canonical node ID
after resolution, as required by §12. First occurrence is retained; per-item
resolution evidence and flags remain available even for removed duplicates.

Why: §12 requires post-normalization deduplication but does not define identity
for unresolved answers. This clarification can affect §15's UNRESOLVED rate, so
the assistant asked before implementing it. Submitted values are compared exactly:
integer versus string IDs, case differences and whitespace differences remain
distinct for unresolved pairs. Name lookup itself continues to follow §12.

Data seen before deciding: the existing saved S14 diagnostic episode was inspected;
single-item S16 synthetic tests and unchanged S7 tests passed (42). No new model
call, pilot run, co-failure result or new scientific label was produced. The
duplicate choice was requested before list-level deduplication was implemented.

Changes to protocol: none; §12's unresolved duplicate identity is clarified here
under direct researcher authorization. No frozen hash, sample or gate change.
S15 approval is recorded in the preceding remote decision-log entry. The
researcher separately authorized S16 here. No S17 work was performed.

Implementation verification: 49 focused tests and 443 full sandbox tests passed,
with no skips/deselections. All 21 answers of the saved successful S14 BH2_00461
episode resolved by ID with no mismatch, unresolved item or duplicate. A deliberate
mutation ignoring submitted ID in unresolved identity was detected and restored
before the full suite. All 50 protected-file hashes and four S7 definitions are
unchanged. Report: docs/S16_implementation.md. Researcher inspection/acceptance of
S16 remains pending; no new model call, episode, commit/push or S17 implementation.

Integration update (2026-10-17): researcher requested committing/pushing S16
and updating local files from the latest remote commit. Remote S15 approval
20997df was integrated; its acceptance record and handoff removal are preserved.
S16 source, tests, scientific rules and prior diagnostic evidence are unchanged.

## 2026-10-17 - S17 authorization and Label A implementation

The researcher explicitly authorized S17 and required S7 G_q per protocol §6/§13:
BRIDGE uses T_q^{B*}, UNION uses T_q. Required a UNION-cannot-produce-ALT_VALID
test, an error for any GOLD_BRIDGE_EXTRA emitted on a CONSISTENT query, and an
explicit construction mode in the S14 hand check. These follow the existing
protocol; no scientific rule or frozen setting was changed. The older S17 runbook
wording was aligned with that protocol and this instruction.

Implemented evaluator-only label_answers over S16 retained resolutions and S7
query rows. First matching rule wins. Explicit consistency flag and ValueError
on forbidden extra labels are routine engineering, as are G_q/construction
validation, set membership and order-preserving list output. Official callers
remain restricted to primary-population queries; synthetic inconsistent fixtures
test the otherwise forbidden GOLD_BRIDGE_EXTRA label.

Verification: 17 new S17 cases; 76 focused checks passed; full suite 460 passed
without skips/deselections. A deliberately inverted consistency guard caused
three expected failures and was restored byte-for-byte before the full suite.
Review also strengthened the UNION error case to use a target outside the
gold-bridge target set. A mutation using those targets instead of G_q was caught
(one expected failure), restored byte-for-byte, then final checks reran.
Saved S14 BH2_00461 is drug:gene/protein:disease, BRIDGE, CONSISTENT and in the
primary population: 21/21 GOLD. Hand-checked Finnish type amyloidosis (27413) and
AL amyloidosis (27710): each is in reference_targets through gold bridge TTR (111),
A*_q and G_q. Frozen drug_protein/disease_protein edges confirmed with the KG.
All 53 protected-file identities are unchanged, including S7, S16 normalization,
protocol, raw/processed data, cache, settings, agent code and episode records.

Report: docs/S17_implementation.md; evidence: results/diagnostics/s17/.
Researcher inspection/acceptance of S17 pending. No model calls, new episodes,
metrics, S18 work, commit or push were performed.

## 2026-10-17 - S17 acceptance and commit/push authorization

The researcher explicitly stated: "I accept S17 (Label A) and its verification
evidence." They requested recording acceptance in this log, committing as
`S17: Label A`, and pushing the commit.

Accepted behavior: protocol §6/§13 Label A priority using S7 G_q by construction
(BRIDGE -> T_q^{B*}, UNION -> T_q); UNION cannot produce ALT_VALID; any
GOLD_BRIDGE_EXTRA emitted on a CONSISTENT query raises an error.

Accepted verification evidence: 17 synthetic S17 cases, 76 focused checks and
460 full-suite tests passed without skips/deselections; both deliberate mutations
were caught and restored. Saved S14 BH2_00461 uses BRIDGE construction and has
21 GOLD answers. The two hand checks confirmed Finnish type amyloidosis (27413)
and AL amyloidosis (27710) through gold bridge TTR (111), with membership in A*_q
and G_q and frozen relation edges checked. All 53 protected identities unchanged.
Full report: docs/S17_implementation.md; evidence: results/diagnostics/s17/.

This acceptance supersedes earlier pending S17 statements. Recording acceptance
changes no code, data, protocol, scientific rule, frozen setting or scoring.
Commit/push are now explicitly authorized. S18 has not been authorized or started.

## 2026-10-17 - S18 authorization and H1 simple-path clarification

The researcher explicitly requested S18 implementation and questions for needed
decisions. Authority: frozen protocol §14 and runbook S18. No S19 work or new
model inference is authorized by this implementation request.

For §14.3 per-answer H1, the researcher selected "Count only a path without
repeated nodes". A correct R1 edge s→b does not establish H1 when b can reach
the answer only through s again (for example s→b→s→x). The H1 supporting path
is simple and has no length cap; the ≤3 bound remains specific to §14.2's
reason-code union. This clarification can affect H1 on cyclic traces and is
recorded before implementing H1. No scientific threshold, frozen file, dataset,
episode, Label A rule or reason-code rule changes.

Evidence seen before deciding: existing saved S14/S17 evidence and the initial
S18 synthetic Label B/reason-code slice (65 checks passed with S12/S17 tests).
No new model call or pilot result.

Implementation/automated verification complete: 48 synthetic S18 cases; 142
focused checks and 508 full-suite tests passed, no skips/deselections. An H1
source-return mutation caused two failures; a disabled-SUPPORTED mutation caused
five. Both were restored byte-for-byte before the full suite. All 71 protected
identities are unchanged, including S12/S16/S17, frozen rules/settings, raw and
processed data, cache and episode records.

Saved S14 BH2_00461: all 21 answers GOLD/SUPPORTED, H1=1, codes empty; episode
H1_CLEAN and found R1=true. All primary paths were checked against raw call 1
(14097 --drug_protein--> TTR 111) and call 3 (111 --disease_protein--> each answer),
including returned items, creation indices, types and underlying real KG edges.
The no-OFF_QUESTION-and-SUPPORTED invariant passes synthetic/real checks.

Report: docs/S18_implementation.md. Full all-answer inspection table:
results/diagnostics/s18/hand-check.md. Researcher inspection/acceptance pending;
no protocol/scientific-file edit, new model call/episode, setting change, S19
implementation, commit or push. Output shape, sorted codes, cached types and
source-excluding reverse reachability are routine engineering, documented in
the report. No scientific choice beyond the researcher's H1 clarification.

## 2026-10-17 - S18 commit/push authorization

After the S18 implementation/verification report, the researcher explicitly
authorized committing and pushing the S18 changes. Publish as
`S18: Label B and hop-1 status`. This supersedes the earlier no-commit/push
status. No additional model call, scientific decision or S19 work is authorized.
This records publication authorization; it does not claim the researcher has
completed the separately listed all-answer manual inspection or stage acceptance.

## 2026-10-17 - S18 delegated acceptance and commit/push authorization

After receiving the remaining review checklist, the researcher stated:
"Okay, you may accept it and commit and push. You are fully authorized to do so.
You have my permission."

This explicitly delegates the acceptance review and authorizes publication of
the resulting acceptance record. It does not claim the researcher personally
performed the manual inspection.

The delegated review inspected the saved-episode verifier, all 21 inspection-table
rows, the cyclic-source H1 regression and the SUPPORTED-with-shortcut case.
A fresh run of `results/diagnostics/s18/check_s14.py` verified every answer/path
against raw returned items, frozen identities and the KG. Its parsed JSON exactly
matched the retained `s14_labels.json`; all 21 table rows matched those verified
answers, paths, labels, codes and H1 values. All 48 cases in
`tests/test_path_labels.py` passed again (0.80 s).

S18 is accepted under this explicit delegated authority, including the retained
142 focused/508 full-suite checks, mutation checks and 71 unchanged protected
identities. The full suite was not rerun for this documentation-only update.
This supersedes earlier pending S18 inspection/acceptance statements.
Implementation is already committed as `efee848` (`S18: Label B and hop-1 status`).
Commit and push this acceptance record. No code, data, scientific rule, frozen
setting, saved episode or S19 work changes.

## 2026-10-17 - S19 authorization and metric clarifications

The researcher requested S19 and questions for any needed decisions. Scope:
protocol §15 and runbook S19; no S20, new inference or frozen-file changes.

Before computing S19 results, the researcher selected:
- Benchmark precision against A*_q uses resolved retained answers only;
  unresolved answers are reported separately.
- Benchmark F1 uses `2 * correct / (resolved answer count + gold count)`;
  nonempty disjoint sets give zero, and a zero denominator gives NA.
- TIMEOUT, ERROR and PARSE_FAIL have NA answer-quality scores, with tool effort
  and trace diagnostics retained. They are not scored as valid empty answers.

Data seen before deciding: existing S14/S18 evidence and the examples in the
clarification questions. No new model call or pilot outcome. These decisions
clarify unspecified S19 conventions without editing frozen scientific files.

S19 implementation/automated verification complete. The evaluator-only helper
reuses the existing parser, S12 reconstruction, S16 normalization and S17/S18
labels unchanged. All §15 metrics are returned with complete answer/bridge
diagnostics and full-KG degree/percentile values. JSON null represents NA;
numerators/denominators and undefined counts support correct later aggregation.

Verification: 48 new synthetic cases; 148 focused checks passed (2.30 s);
full suite 556 passed (31.13 s), no skips/deselections. Reversing the early-stop
page-2 condition caused seven failures; overwriting first bridge rank caused
one. Both mutations were restored byte-for-byte. All 112 protected identities
are unchanged, including existing code/tests, science, settings, data/cache and
saved episodes. Final replay output exactly matches the retained metrics JSON.

Saved S14 BH2_00461: 21 GOLD/SUPPORTED answers, benchmark P/R/F1=1, question-valid
precision=1, OFF_QUESTION/UNRESOLVED/UNGROUNDED rates=0. TTR 111 is the only explored
bridge, first returned on call 1/page 1/position 1 (rank 1); bridge recall=21/21=1.
Early stop=false because neither successful page has has_more=true. Two neighbor
pages, four charged calls, no exhausted budget or TEXT_TOOL_CALL; H1_CLEAN.
Every answer's first-list/path list size and reported node degrees were verified.

Routine engineering details are listed in docs/S19_implementation.md, including
counting actual page requests (errors/repeats included, ignored calls excluded),
first-list semantics, and retaining per-answer path fan-out for later PCF use.
No co-failure metric, new inference, episode, S20 work, frozen-file/scientific-rule
edit, commit or push was performed. Researcher stage acceptance remains pending.
Complete evidence and hand checks: results/diagnostics/s19/.

## 2026-10-17 - Technical failures in §16 and S19 acceptance

Decision: technical-failure episodes (TIMEOUT, ERROR, PARSE_FAIL) must not count
as answer failures in protocol §16 co-failure metrics. Preserve their technical
status separately; do not treat them as wrong-answer sets or evidence of shared
answer failure. This is a requirement for the later §16 implementation; S19's
existing NA answer-quality treatment is unchanged. No §16 code is added here.

The researcher explicitly stated: "I accept S19 (per-agent metrics) and its
verification evidence." S19 is accepted, including its 48 synthetic cases,
148 focused/556 full-suite checks, both caught/restored mutations, all 112
unchanged protected identities and saved S14 replay/inspection evidence.
This supersedes earlier pending S19 acceptance statements.

Data seen before deciding: the S19 report and verification evidence, including
TTR bridge rank 1, bridge recall 1, early_stop=false, benchmark P/R/F1=1,
two page requests and four charged calls on the unchanged saved S14 episode.

The researcher authorized committing as `S19: per-agent metrics`, explicitly
instructed not to push, and prohibited starting S20. Record these decisions
before the local commit. No frozen protocol/gate file is edited.

Pre-commit verification: full suite 556 passed (26.89 s), no skips/deselections;
all 112 protected identities remain unchanged. Evidence:
`results/diagnostics/s19/full-suite-acceptance-20261017.txt`.

## 2026-10-18 - S20 authorization and decisions before screening

Researcher authorized implementing the S20 launcher and running the first official
Llama screening episode ("go on" after the explicit implementation/first-episode
question). This supersedes the S19 instruction not to start S20. Stop after the
first saved episode and inspection; no remaining episodes, S21 selection, commit
or push is authorized by this checkpoint.

Experimental policy: think=false for all candidates. Use unmodified Ollama tags
with native tools and no thinking mode or a supported disabled-thinking mode;
exclude thinking-only weights and custom diagnostic templates. No thinking-enabled
screening; a possible later thinking comparison is exploratory and outside gates.
Use protocol section 9.1 screening settings exactly: temperature 0, seed 42,
num_ctx 8192, num_predict 4096, page_size 50, budget 30, timeout 600 seconds.
Keep the existing 120-second request timeout. No frozen science/config is edited.

Researcher accepts a 7B-9B target range. Planned pool (local eligibility still to
be checked for subsequent models): llama3.1:8b, qwen3:8b, granite3.3:8b,
mistral:7b, command-r7b:7b, qwen2.5:7b, aya-expanse:8b, granite3.2:8b.
ministral-3:8b remains a proposed reserve, not an automatic replacement. Only
Llama is approved for inference at this checkpoint. Run each candidate's complete
screening block before moving to another, with intermediate results visible;
never drop/swap candidates based on early performance. Apply D3 selection at S21
after the approved screening pool finishes. The first-episode checkpoint does not
freeze models or final engineering limits.

Primary run remains on RTX 3060 Ti 8 GB; screening, smoke and pilot for this run
stay on that machine. The separately declared RTX 5060 Ti 16 GB run has independent
screening, freeze/configs/results/run IDs and descriptive exploratory reporting;
it cannot change a primary gate or claim. No secondary inference is authorized here.

Evidence seen before this decision: prior S14 diagnostics, S19 acceptance, model
library descriptions and today's user-run Llama synthetic greeting/native add(2,3)
responses. User's ollama ps showed 100% GPU, context 8192, loaded size 5.8 GB.
Installed Llama tag/digest confirmed: llama3.1:8b,
46e0c10c039e019119339687c3c1757cc81b9da49709a3b3924863ba87ca666e,
8.0B Q4_K_M, native tools advertised. No S20 biomedical result had been seen.

Engineering plan: a new S20 launcher with correct agent identity, immutable run
configuration/source/input hashes, bounded new-episode count and resumable
write-once records. A saved TIMEOUT/ERROR/PARSE_FAIL is completed and is never
automatically retried. Partial tables show observed quantities but no D3 verdict.
Initial sandbox metadata request is socket-blocked; host metadata access succeeds
with Ollama 0.40.4. Use host execution for the authorized episode, preserving the
same machine/config. This avoids creating a known infrastructure-failure episode.

### S20 first-episode checkpoint evidence (no new scientific decision)

After the decisions above were recorded, exactly one official Llama episode ran:
BH2_00461, primary-3060ti-20261018, agent Llama31-8B. All 598 tests passed before
inference (42 new) and 122 protected identities were unchanged. Frozen settings,
data, prompt, tools, existing evaluators and scientific rules are unchanged.

Result: SUCCESS status for valid {"status":"no_answer","answers":[]}; 25.875167
seconds; 30 charged calls; 0/31 well-formed/attempted native calls; zero supported
answers, no OOM, largest prompt count 2071. It guessed unknown relation labels,
never used inspect_entity and emitted string page="1" on all native calls.
No argument coercion, prompt repair, automatic retry or candidate rejection.
During-episode GPU evidence confirms full residency at context 8192. Identity
remained stable. Report-only resume used no model inference and retained identical
episode/config hashes; one episode remains saved. Partial table has no D3 verdict.

This is the authorized first-episode checkpoint only. Researcher review and
instructions for the remaining 19 are pending. No S21 selection, commit or push.
Full report and engineering choices: docs/S20_implementation.md.

## 2026-10-18 - S20 Llama continuation authorization; preflight stop

The researcher accepted the first-episode checkpoint and authorized the remaining
19 Llama screening queries in primary-3060ti-20261018, agent Llama31-8B, with
--max-new 19 on the host. No other model, S21 selection/freeze, source/config/data
change, commit or push is authorized. The saved BH2_00461 record must not be
overwritten or rerun. Stop immediately on any failed preflight/hash/identity check
or any saved ERROR episode, including OUT_OF_MEMORY; no fix, retry or workaround.

Researcher decision, recorded before any further inference: D3 well-formedness
requires argument types matching T1 with no coercion. page="1" is not well-formed.
This follows D3's "arguments parse and match the schema types" definition and
remains fixed before further results. The implemented checker was read alongside
T1 and D3 and matches this rule: it parses a JSON argument object when needed,
checks declared tool names, required fields and exact declared types, and never
coerces argument values. A string page and Boolean page both fail; integer page
passes. No evaluator edit was made.

Pre-run checks: parser/source and --help confirm --run-id, --agent-id and
--max-new (0-20). Exactly one final record exists, BH2_00461, and all 19 remaining
IDs match the frozen manifest order. All 43 pinned source/input hashes match.
The existing episode hash remains
36a51907078f857fe75aeb25a0defa71c620d53405fdc138aa95e0f49cdea051;
the per-model configuration hash remains
8c936436896ca42ef60bbbe617df263fddb61d03e814d954189d4b128923a85b.

Preflight also found a stop-policy incompatibility: run_screening saves and loads
each episode, validates provenance, appends the record and proceeds without
checking whether status is ERROR. The agent runner catches runtime errors and
saves ERROR as a normal return, so --max-new 19 cannot itself guarantee the
new immediate-stop requirement. No further inference was started. The launcher
was not changed and no in-memory patch, supervisor, retry or workaround was used.
Further execution is pending resolution of this incompatibility by the researcher.

## 2026-10-18 - S20 continuation: researcher-approved per-invocation stop policy

The researcher accepts the preflight and resolves the stop-policy incompatibility
without changing code: invoke scripts/20_screen_models.py with --run-id
primary-3060ti-20261018, --agent-id Llama31-8B and --max-new 1, repeatedly, at most
19 invocations. Other required flags remain --model llama3.1:8b, --family Llama,
--expected-digest 46e0c10c039e019119339687c3c1757cc81b9da49709a3b3924863ba87ca666e.
Run on the existing host Ollama server. After each invocation, check the native
process exit code and newly saved record's status before issuing another. Stop
immediately if the exit is non-zero, any drift is reported, or the new status is
ERROR (any cause, including OUT_OF_MEMORY). No fix, retry or workaround after a
stop condition. TIMEOUT/PARSE_FAIL remain saved completed episodes under the
previously frozen rules; only the specified conditions stop this continuation.

The shell orchestration will also confirm exactly one new record in frozen order
and unchanged hashes for all earlier records/config, including BH2_00461. This is
the explicitly requested execution method, not a launcher/agent/evaluator change.
The previous strict no-coercion D3 decision remains unchanged. No other candidate,
S21 decision/freeze, source/config/data/test edit, commit or push is authorized.

Rechecked before inference: parser/--help flags are unchanged, the exact-type D3
check remains in place, one episode and nineteen remaining frozen queries are
present, and all 43 pinned source/input hashes matched at accepted preflight.
Live host metadata now confirms Ollama 0.40.4, the exact approved Llama digest,
and no currently loaded competing model. No additional model result has yet been
observed. Existing generation settings/timeouts and P1/T1 remain fixed.

### S20 Llama block complete: evidence, no new scientific decision

Executed exactly nineteen separate --max-new 1 host invocations. Each Python
launcher exited zero and produced exactly one new SUCCESS record in frozen
order; every new status and previous-file hash was checked before another
invocation. No ERROR (any cause), reported drift or order/hash discrepancy occurred.
The original BH2_00461 episode was not rerun or changed. No other candidate ran.

All 20 Llama episodes are now saved; complete=true and d3_pass=false. D3 values:
well-formed/attempted=0/620 (0%, FAIL); SUCCESS=20/20 (100%, PASS);
competence=0/20 (0%, FAIL); median wall=22.132269 seconds (n=20, PASS against
300 s); ERROR with OUT_OF_MEMORY=0 among 20 episodes (PASS). There are no TIMEOUT,
ERROR or PARSE_FAIL episodes. All final outputs are no_answer with empty answers;
no episode has a successful KG call or a submitted answer. All 620 native calls
are get_neighbors with string page values; zero TEXT_TOOL_CALL events. Budget-hit
share=20/20; median charged calls=30; largest prompt count=2165.

Full unchanged suite: 598 passed in 42.45 s, no skips/deselections, with base temp
directory inside ignored .venv/. Report-only resume (--max-new 0) exited zero,
left exactly 20 unique episodes and retained identical hashes for all 21 run
files (20 records plus configuration). All 43 pinned source/input hashes and
122 protected identities remain unchanged. Full per-query report and manual
inspection suggestions: docs/S20_llama_screening.md. Evidence is under
results/diagnostics/s20/llama-*; screening_table.csv was regenerated.

The shell's optional live wall-time display had a non-terminating date-formatting
error after PowerShell converted JSON timestamps to date objects. This did not
affect Python exits, statuses, stop checks, raw records or settings. Final wall
times were derived from the unchanged raw ISO timestamps using the evaluator's
same datetime.fromisoformat calculation. Original invocation journal retained.

No code, evaluator, test, config, prompt, schema, data or frozen rule changed;
no S21 selection/freeze, commit or push. Stop after this candidate report.

## 2026-10-18 - Qwen3.5 9B added; official screening paused for memory investigation

Researcher requested S20 testing of the newly pulled qwen3.5:9b and explicitly
chose to add it as an extra candidate while retaining the original eight-model
pool, including the unrun qwen3:8b. This is an explicit pool extension to nine,
recorded before any Qwen3.5 biomedical result. No S21 selection is made.

Installed identity: qwen3.5:9b, Qwen lineage, 9.0B Q4_K_M, digest
56671c2ab9385f9cfcb404638e32cd62d88e3501d44822208363c010179a3c90.
Ollama 0.40.4 advertises native tools and thinking. A synthetic add(2,3)
exchange at temperature=0, seed=42, num_ctx=8192, num_predict=4096,
think=false emitted the native add tool with integer arguments, then answered 5;
neither response contained a nonempty thinking field. Identity was unchanged.
These diagnostics do not establish biomedical competence or a D3 verdict.

The unchanged repository suite passed: 598 tests in 41.73 seconds, no skips or
deselections. All 122 protected-file hashes and 43 Llama-pinned source/input
hashes match. Existing official run hashes are saved in
results/diagnostics/s20/qwen35/integrity-preflight.json.

During the synthetic check, /api/ps reported size=6402196107 bytes,
size_vram=5614044445 bytes, context_length=8192. ollama ps displayed
12%/88% CPU/GPU; nvidia-smi sampled 7563 MiB of 8192 MiB used. Only this model
was loaded. Asked whether to proceed with this placement, the researcher chose:
"Pause official screening and investigate GPU memory first". No Qwen3.5 S20
episode or official run configuration has been created. Official inference must
remain paused pending researcher resolution after the memory investigation.

The investigation may use isolated synthetic/allocation diagnostics, with logs
under results/diagnostics/s20/qwen35/. Frozen generation settings, source,
agent, evaluator, prompt, tool schemas, data and prior episodes remain unchanged.

Captured isolated Ollama load reproduced the primary loaded-size/VRAM values and
confirmed 32/33 text layers on GPU. The fitter retained context 8192 and reported
a 70 MiB shortfall against its 1927 MiB free-memory target, including the vision
projector's 1152.01 MiB worst-case reserve. The temporary model/server were
stopped. Full evidence and diagnostic limitations: docs/S20_qwen35_preflight.md.

Researcher chose "I'll close unused GPU apps; then recheck with unchanged
settings". Wait for readiness before repeating the memory diagnostic. This
choice authorizes the recheck; official screening remains paused while its
memory outcome is unresolved.

Researcher confirmed readiness after closing apps. An unchanged isolated
Ollama recheck again loaded 32/33 layers on GPU with the identical 70 MiB
fitting shortfall and size/VRAM values. Baseline GPU usage was 926 MiB and
loaded usage 7353 MiB. Evidence: results/diagnostics/s20/qwen35/memory-recheck-01/.
Temporary model/server stopped. Official queries remain unrun, pending the
researcher's choice of accepting placement, diagnostic tuning, or staying paused.

Researcher resolved the pause: "Run all 20 S20 queries with the offload
documented (recommended)". Authorizes the full qwen3.5:9b screening block on
the existing primary RTX 3060 Ti host, run primary-3060ti-20261018, agent
Qwen35-9B, family Qwen, exact digest above. Accept the observed 32/33-layer
GPU placement; retain all frozen screening settings and think=false. Use
separate --max-new 1 launcher invocations and check process exit, saved status,
frozen order, prior-file/config hashes and pinned sources between invocations.
Stop on any ERROR, nonzero exit, drift or order discrepancy; no automatic retry,
repair or workaround. Saved TIMEOUT/PARSE_FAIL are completed under existing
rules. No S21 choice/freeze, source/config/data changes, commit or push.

### Qwen3.5 full candidate block complete: evidence, no S21 decision

Executed 20 separate --max-new 1 host invocations, each exiting zero and saving
one record in frozen order. All inter-invocation status/identity/hash checks
passed; no ERROR, nonzero exit, drift or order discrepancy. All 20 are saved:
18 SUCCESS and two PARSE_FAIL (BH2_03856, BH2_03881), zero TIMEOUT/ERROR/OOM.
No saved outcome was rerun, repaired or overwritten. No other model ran.

Complete=true; this candidate passes all five D3 criteria:
well-formed/attempted=210/210 (100%); SUCCESS=18/20 (90%);
competence=15/20 (75%); median wall=26.383874 seconds; OOM=0.
All 210 attempts were native, with zero TEXT_TOOL_CALL events. Median charged
calls=9; budget-hit share=0; largest prompt_eval_count=8189; zero nonempty
thinking fields in recorded assistant messages. Submitted answer labels:
341 GOLD, 17 ALT_VALID, four OFF_QUESTION; 358 SUPPORTED, four PATH_INVALID.
Competence is at least one valid supported answer per query, not completeness.

Both PARSE_FAIL records ended at the context boundary with done_reason=length;
empty/truncated final output remained unparsed after the existing re-prompt.
Some competent queries have very low benchmark recall. These limitations and
wrong-target behavior were inspected without tuning or changing a threshold.
If selected later at S21, largest prompt 8189 > 0.8*8192 triggers section 9.1's
five-query context-16384 check; none was run and final runtime values are unfrozen.

Full pre-inference suite: 598 passed in 41.73 seconds, no skips/deselections.
Report-only --max-new 0 exited zero with no inference and retained all 42
run-file hashes, including all 21 original Llama files. All 122 protected-file
and 43 pinned source/input hashes match. Final proof, per-query values,
invocation journal and raw diagnostic evidence are in
results/diagnostics/s20/qwen35/. Report: docs/S20_qwen35_screening.md.

Qwen3.5 stays an extra candidate; the original eight-model pool is retained.
Seven planned candidates remain unrun. This completes the authorized Qwen
block only: no full S20 acceptance, S21 selection/freeze, 16K follow-up,
source/config/data/test change, commit or push.

## 2026-10-19 - Granite 3.3 8B S20 screening authorized

Researcher: "granite 3.3 model has been download, now run s20 on that model".
This authorizes the complete 20-query block for the original planned candidate
granite3.3:8b on the existing primary RTX 3060 Ti host, with the established
per-invocation checks. Agent Granite33-8B, family Granite, experiment run
primary-3060ti-20261018. Installed identity verified before inference: 8.2B
Q4_K_M, digest fd429f23b90980ed1bef53b990894e7b0199331f6ae90c5650240a7d5b70f1f7;
Ollama 0.40.4 advertises completion and native tools. Existing server was stopped;
started the installed Ollama executable with D:\Models on 127.0.0.1:11434.

Retain frozen screening settings and think=false, 120-second request timeout,
strict schema typing without coercion, original pool and saved outcomes. First
check synthetic native tools, GPU placement, full suite, protected/pinned hashes
and all existing official records. Use separate --max-new 1 invocations, stopping
on any ERROR, nonzero exit, identity/hash drift or frozen-order discrepancy.
Saved TIMEOUT/PARSE_FAIL remain completed and are never rerun. Operational
helpers reuse the preceding Qwen block's checks with Granite identity/output
paths. No scientific rules, agent/launcher/evaluator, source/config/data/test
changes, S21 selection/freeze, other candidate run, commit or push.

Granite preflight passed before official inference: unchanged full suite 598
passed in 43.55 seconds, no skips/deselections; 122 protected identities, 43
pinned source/input hashes and all 42 prior Llama/Qwen run files match. Synthetic
native add(2,3) used integer arguments and answered 5 with no nonempty thinking
field; model identity stayed unchanged. /api/ps reports context 8192,
size=size_vram=6403905289 bytes (full GPU residency); sampled GPU usage 7404 MiB
of 8192 MiB. Raw metadata and synthetic evidence are retained under
results/diagnostics/s20/granite33/. Proceeding with the authorized official block.


### Granite 3.3 full block complete: evidence, no S21 decision

Completed all 20 separate --max-new 1 invocations in frozen order. Every launcher
exited zero and saved exactly one new SUCCESS record. No ERROR, TIMEOUT,
PARSE_FAIL, OOM, identity/hash drift or order discrepancy occurred. All prior
records were retained; no reruns or source/prompt/template/argument repairs.

D3 fails: well-formed/attempted=0/8 (0%); competence=0/20 (0%). Other criteria
pass: SUCCESS=20/20, median episode wall=13.597764 seconds, OOM=0. Zero native
calls and eight logged TEXT_TOOL_CALL occurrences; no KG call was executed.
SUCCESS reflects parsing under the existing parser, not a correct answer.
69 evaluated answer items: 53 OFF_QUESTION, 15 UNRESOLVED, one GOLD; all 54 resolved
items are UNGROUNDED, unresolved items NOT_APPLICABLE. No supported answers.
Largest prompt_eval_count=3546; no nonempty assistant thinking fields.

Full suite before inference: 598 passed in 43.55 seconds. All 20 placement samples
confirm size=size_vram=6403905289 at context 8192, consistent with the preflight
41/41 GPU-layer log. Report-only --max-new 0 exited zero without inference and
retained all 63 run-file hashes, including all 42 prior Llama/Qwen files.
122 protected identities and 43 pinned source/input hashes match.

Report: docs/S20_granite33_screening.md; evidence/operational helper copies:
results/diagnostics/s20/granite33/. Inspected first text-tool output, the
BH2_03762 GOLD-but-UNGROUNDED name-fallback result and BH2_03850 placeholders.
The auxiliary raw-output inspection initially used strict JSON decoding, which
rejected an existing code fence; reran only the inspection using the unchanged
runner parser. Official screening, outcomes and metrics were unaffected.

Three candidates are screened; six original planned candidates remain unrun.
No S21 selection/freeze, 16K follow-up, other candidate, source/config/data/test
change, commit or push. This completes the requested Granite block.

## 2026-10-19 - Local S20 commits authorized per model

Researcher requested committing the changes, separately for each model where
possible. This supersedes historical no-commit checkpoints for the completed
S20 implementation and these three candidate blocks. Separate shared launcher/
D3 code from Llama, Qwen3.5 and Granite reports, diagnostics and metric rows;
retain generated graph context separately. No push was requested.

Pre-commit focused suite: 42 passed in 2.46 seconds; unchanged full suite already
passed 598 tests before the Granite run. Preserve original episode/configuration
bytes and recorded run provenance. Raw episodes remain ignored under
results/runs/. Extend .gitattributes to preserve exact S20 source/evidence bytes
because screening manifests and integrity proofs identify them by SHA256.
Index-only documentation/table snapshots split shared files by candidate without
rewriting the current working files or any completed episode.

## 2026-10-19 - Researcher requests updated models at a similar parameter scale

Researcher: "i think we should work with the updated models but similar parameter
size". Record the direction of reviewing newer releases in the previously
accepted 7B-9B class. Granite 4.1 testing was deferred ("i will test it later").
No new model inference or download is authorized or performed by this planning
update. No frozen protocol, D3 threshold, runtime setting or model freeze changes.

Source-checked proposal: docs/S20_updated_model_pool_proposal.md. Initial
shortlist: existing pinned Qwen3.5 9B, Ministral 3 8B Instruct, OLMo 3 7B
Instruct, and conditional Granite 4.2 8B; Granite 4.1 8B is a proposed fallback
or additional candidate. Exact membership, remaining-old-model disposition and
D3 round accounting remain researcher decisions before new official inference.
Published capability is not local eligibility; every new exact tag must pass
native-tools, non-thinking and GPU placement preflight without altering P1/T1.

Preserve all completed Llama/Granite/Qwen records and prior chronological pool
decisions, including failures. This recency preference was expressed after the
three candidate outcomes were observed; record that timing transparently.
The proposed list has four developer families but is not a four-model S21
selection. D3 still requires four passing models covering at least three families.

## 2026-10-19 - Failed model downloads removed at researcher request

Researcher explicitly requested removal of downloaded Granite 3.3 and Llama
weights to free disk space after their D3 failures. Verified installed tags and
original screening digests, then used the existing Ollama server's native
removal command for exactly granite3.3:8b and llama3.1:8b. Both tags are now absent.
All three Qwen tags/digests remain unchanged, including screened qwen3.5:9b.

D: free space increased from 250234822656 to 260098826240 bytes: 9864003584 bytes
reclaimed (9.86 GB decimal / 9.187 GiB). Metadata manifests were retained as tiny
archival JSON files alongside before/after tags and disk measurements under
results/diagnostics/s20/model-storage-cleanup-20261019/. Downloaded weight files
are removed; completed episodes, configurations, metrics and reports are retained.
This is storage maintenance, not a change to historical screening outcomes,
scientific rules, pool membership or model-selection gates.


## 2026-10-19 - Ministral 3 8B S20 block authorized

Researcher downloaded ministral-3:8b and explicitly requested: "now run s20 on this model". This authorizes its complete 20-query block after exact identity, native tools, disabled thinking and context-8192 placement preflight. Treat this as an additional screened candidate; preserve original candidate history and all prior outcomes. No replacement, D3 round assignment or S21 panel selection is inferred. Reuse the unchanged launcher with one --max-new 1 invocation per episode and existing stop/integrity checks. Frozen protocol, inputs, P1/T1, source, config and prior records remain unchanged; no other model, 16K follow-up, commit or push.

Ministral preflight passed: exact digest 1922accd5827ebe6829e536369195db25eaf664528dc66206d646ea3bb386b71, 8.9B Q4_K_M, tools advertised, synthetic native add(2,3) with integer arguments then result 5, no nonempty thinking. Runtime context 8192, size=6591967394 and size_vram=5549137591 bytes; CLI reports 16%/84% CPU/GPU. Proceed under the current full-block request with this automatic placement documented and unchanged settings. Exact GPU layer count is not established by the percentage. Full suite: 598 passed in 28.33 s on host; initial sandbox run had temporary-directory setup errors (438 passed/160 errors), independently reproduced with -x and resolved by host execution. All 122 protected and 43 pinned hashes match; 63 prior run-file hashes saved. Operational helpers reused from Granite with identity/output substitutions only.

### Ministral stopped at query 16: ERROR/CONNECTION retained

Saved first 16 frozen queries through BH2_04425: 11 SUCCESS, four PARSE_FAIL, one ERROR/CONNECTION. Each launcher exited zero; the between-invocation checker then stopped on ERROR as designed. The failed request hit the existing 120-second HTTP read timeout; the saved episode wall time is 139.070961 s. Subsequent read-only /api/ps responded with unchanged identity/placement; the generation-stall cause remains unresolved. No retry, repair, context change or further inference. Remaining IDs: BH2_05366, BH2_05686, BH2_05843, BH2_06427.

Partial row: 155/155 well-formed native calls, 7/16 competent, median 70.374565 s, zero OOM, largest prompt 8184; four parse failures preserved. No complete D3 verdict assigned; SUCCESS can reach at most 15/20, below 90%. Report-only resume and all 80 run-file hashes (63 prior), 122 protected and 43 pinned identities verified. Report: docs/S20_ministral3_screening.md; evidence: results/diagnostics/s20/ministral3/. No S21 work, other candidate, commit or push.

### Ministral continuation explicitly authorized

Researcher selected "Continue the remaining four (Recommended)" after reviewing the 16/20 stop checkpoint. This authorizes only BH2_05366, BH2_05686, BH2_05843 and BH2_06427 in frozen order, retaining all 16 saved final outcomes, including BH2_04425 ERROR/CONNECTION. Resume unchanged S20 settings and one --max-new 1 invocation per episode; stop on any new ERROR, nonzero exit, identity/hash drift or order discrepancy. No error retry, source/config change, other model, S21, commit or push. Baseline: stopped-integrity-proof.json (80 run files); stopped summaries retained separately before final derivation.

### Ministral full block complete: D3 fails SUCCESS rate

The explicitly authorized four-query continuation completed SUCCESS for BH2_05366, BH2_05686, BH2_05843 and BH2_06427, with no new stop condition. All 20 outcomes saved; the original 16 including ERROR/CONNECTION are unchanged. D3 FAIL: well-formed 197/197 (100%, PASS), SUCCESS 15/20 (75%, FAIL), competence 10/20 (50%, PASS), median wall 62.850686 s (PASS), OOM 0 (PASS). Four PARSE_FAIL and the one CONNECTION error remain in the denominators. Largest prompt 8184, median calls 8.5, budget-hit share 0, zero thinking messages. 266 answer items: 243 GOLD, 17 ALT_VALID, six OFF_QUESTION; 260 SUPPORTED, six PATH_INVALID.

Final report-only --max-new 0 exited zero; all 84 run-file hashes match, including all 80 stopped-checkpoint and 63 pre-Ministral files. All 122 protected and 43 pinned identities match. Prior candidate table rows unchanged. Full-suite result remains 598 passed before inference; source is unchanged. Report updated: docs/S20_ministral3_screening.md. Reviewed stop report/derivations retained separately in results/diagnostics/s20/ministral3/. No rerun, source/config/scientific edit, 16K follow-up, S21 selection, other model, commit or push. Stop after this candidate.

## 2026-10-19 - Ministral timeout investigation: buffered generation exceeds read cap

Researcher asked why the CONNECTION timeout occurred. Read-only trace/source/process/hardware checks plus one isolated replay of the saved seventh HTTP request were performed outside official runs. Original request settings/payload unchanged; only diagnostic client wait increased from 120 to 300 seconds. Replay returned in 153.471033 s: 143.567916 s generation, 2576 output tokens, prompt 4569, load 7.226668 s. Same original CPU/GPU placement and digest. This reproduces a long buffered completion exceeding the read deadline; CONNECTION is the client's broad timeout classification, not proof of a network disconnect. No original server log was found, so exact historical completion text/latency is unknown. Replay was prose and failed final-JSON parsing; no subsequent turn or full episode was run. All 84 official run hashes, 122 protected and 43 pinned hashes and the full D3 row remain unchanged. Report: docs/S20_ministral3_timeout_investigation.md. No production source/config/runtime or scientific settings changed; no commit/push.

## 2026-10-19 - Separate full BH2_04425 diagnostic authorized

Researcher requested "run that query once again off the books" after the single-request timeout diagnosis. Authorizes one complete exploratory episode for BH2_04425, excluded from official screening. Reuse the unchanged runner, model identity, P1/T1, context 8192, output cap 4096, seed 42, temperature 0, budget 30, page size 50 and think=false. Only diagnostic request cap changes 120 to 600 seconds, bounded by the unchanged 600-second episode limit. New diagnostic run ID: ministral3-bh204425-diagnostic-20261019T075024Z. Full trace and evaluator-only metrics saved separately; official ERROR, all official metrics and D3 retained. No automatic additional run, production code/config edits, commit or push.

### One exploratory full-query result: SUCCESS outside official S20

Exactly one complete BH2_04425 diagnostic episode saved under E:\Phitron Thesis\cofail_kg\results\runs\diagnostic\ministral3-bh204425-diagnostic-20261019T075024Z\BH2_04425__Ministral3-8B__a1.json. SUCCESS after 237.017349 s, six well-formed native calls, 65 GOLD/SUPPORTED answers; benchmark precision 100%, recall 65/75 (86.6667%), F1 0.9285714. With diagnostic request cap 600 (episode cap unchanged 600), the long prose turn returned after 135.261922 s, crossing the official 120-second cap; the standard single JSON re-prompt completed in 74.903480 s. No page-2 call for the 60-item Doxycycline neighbor list (first 50 retrieved). All 84 official run files, official table/metrics and other protected identities unchanged (290 distinct files). No second exploratory episode, production source/config change or official result replacement. Full diagnostic evidence: results/diagnostics/s20/ministral3/offbook-20261019T075024Z/README.md.

## 2026-10-19 - Ministral checkpoint commit authorized

Researcher requested "okay commit and take me what should be the next model". Authorizes a local commit of completed Ministral official screening, timeout investigation and the separately labeled one-query diagnostic. Preserve recorded episode/config provenance and all write-once results. Pre-commit suite: 598 passed in 29.14 s; six diagnostic helpers parse; evidence/metric credential-pattern scan found no matches. All 84 official run-file hashes, 122 protected identities and 43 pinned source/input hashes match. Stage shared documentation snapshots for Ministral only, preserving earlier uncommitted shortlist/cleanup changes in the working files. Raw results/runs records remain ignored under the existing policy. No push or next-model inference/download requested.


## 2026-10-19 - OLMo 3 7B Instruct S20 screening authorized

Researcher supplied the successful pull of olmo-3:7b-instruct and requested
"run s20 on this model, and lemme know if u need any decisions". This authorizes
the full unchanged 20-query block on the primary RTX 3060 Ti host, subject to
existing preflight and between-invocation stop checks. Agent OLMo3-7B, family
OLMo, experiment primary-3060ti-20261018. Exact installed tag: 7.3B Q4_K_M,
digest ea72df8c85d75c6783ab0d00278803c53a634fc9d0fe38d3fd4ab6f35adbdbb2.
Ollama 0.40.4 advertises completion and tools. No default/Think tag substitution.

Retain frozen P1/T1, context 8192, output 4096, temperature 0, seed 42, budget
30, page size 50, episode timeout 600 s, request timeout 120 s and think=false.
Reuse the prior candidate's operational helpers with identity/path substitutions.
Check synthetic native tools, placement, full suite, 122 protected identities,
43 pinned source/input hashes and all 84 prior run files before inference.
Run separate --max-new 1 invocations; stop on ERROR, nonzero exit, identity/hash
drift or order discrepancy. Every saved final status remains completed.
No scientific/source/prompt/template/config changes, reruns, S21 selection,
other candidate, commit or push. Pool membership/round decisions remain for
the researcher; this single-candidate measurement does not settle them.

OLMo preflight passed: 598 unchanged tests in 35.69 seconds, no skips or
deselections; synthetic native add(2,3) used exact integer arguments and
answered 5, with no nonempty thinking fields. Identity unchanged. Context 8192,
size=6511625501 and size_vram=5298192384 bytes: automatic partial CPU/GPU offload,
recorded under the same unchanged placement procedure used for Ministral. No
placement tuning or new eligibility threshold. All 84 prior official files,
122 protected identities and 43 pinned source/input hashes match. Proceeding
with the authorized OLMo block, one frozen query per invocation.


### OLMo 3 Instruct full block complete: D3 FAIL on competence

All 20 separate --max-new 1 invocations exited zero, saved exactly one SUCCESS
record in frozen order, and passed between-invocation checks. No ERROR, TIMEOUT,
PARSE_FAIL, OOM, drift or rerun. D3: 60/62 well-formed (96.7742%), SUCCESS 20/20,
competence 0/20 (FAIL), median wall 8.951106 s, OOM 0. All 62 attempts native;
61 charged and 51 successful KG calls. Two missing required page arguments in
BH2_03762 fail strict well-formedness. Budget-hit share 5%; largest prompt 8137.
18 no_answer outputs; two answered outputs submit 12 items, all OFF_QUESTION
and PATH_INVALID. No supported answers or nonempty thinking fields.

Report-only --max-new 0 exited zero without inference and preserved all 105
run files, including all 84 prior files. All 122 protected and 43 pinned hashes
match. All 20 placement samples retain context 8192 and the synthetic partial
CPU/GPU placement sizes. Full suite before inference: 598 passed in 35.69 s.
Report: docs/S20_olmo3_screening.md; diagnostics: results/diagnostics/s20/olmo3/.
No scientific/source/config change, other candidate, 16K follow-up, S21 choice,
commit or push. No new researcher decision was needed for this candidate block.


## 2026-10-19 - OLMo result commit and model removal authorized

Researcher: "commit it and delete the model from the computer to free up space".
Authorizes a local commit of the completed OLMo S20 report, metrics, diagnostics
and status updates, followed by native Ollama removal of exactly
olmo-3:7b-instruct. Preserve all episode/configuration bytes and their recorded
provenance; downloaded weights are separate from historical results. No push.

Pre-commit review confirms the unchanged 598-test suite passed before inference,
all 105 official run-file hashes, 122 protected identities and 43 pinned sources
match, and earlier models' table rows remain unchanged. Reuse the established
index-only snapshots for shared documents so pending shortlist/earlier cleanup
changes stay uncommitted and working files stay intact. No new inference or
production-code change is required.


## 2026-10-19 - Granite 4.2 8B S20 screening authorized

Researcher supplied the successful pull of granite4.2:8b and requested "run s20 on this model". Authorizes the complete unchanged 20-query block for Granite42-8B, family Granite, in primary-3060ti-20261018, after established preflight. This single-candidate measurement does not settle revised pool membership, D3 round accounting or S21 selection. Preserve prior outcomes and pending shortlist/cleanup edits; no other model, rerun, commit or push.

Installed identity: granite4.2:8b, 8.8B Q4_K_M, digest f586c02fdecdf151b656207c339aa003997345774a41768bac1fd6d2fb85913b. Existing Ollama 0.40.4 server advertises tools, thinking and completion. An attempted server start found port 11434 already occupied; the healthy existing endpoint was used. Synthetic native add(2,3) emitted exact integer arguments and answered 5, with no nonempty thinking fields and unchanged identity. Context 8192 placement reports size=6862195914 and size_vram=6268114697 bytes (automatic partial CPU/GPU offload); GPU usage sampled 7208/8192 MiB. Same unchanged placement procedure as recent candidates; no tuning or new threshold.

Retain protocol section 9.1 settings, P1/T1 and think=false: temperature 0, seed 42, context 8192, output cap 4096, budget 30, page size 50, episode timeout 600 s, request timeout 120 s. Reused OLMo operational helpers with only candidate identity/output substitutions and existing assertions. All 105 prior official run-file hashes, 122 protected identities and 43 pinned source/input hashes match. Full suite required before official inference. Use separate --max-new 1 invocations in frozen order; stop on ERROR, nonzero exit, drift or order discrepancy. Every saved final status remains completed without retry.

Granite 4.2 preflight complete: unchanged full suite 598 passed in 34.27 s, no skips/deselections. Proceeding with the authorized block; evidence under results/diagnostics/s20/granite42/.


### Granite 4.2 stopped at query 12: ERROR/CONNECTION preserved

Eleven SUCCESS and one ERROR/CONNECTION saved through BH2_03953. Its next chat request exceeded the unchanged 120-second HTTP read timeout after eight successful responses; episode wall time 139.565813 s. Launcher exited zero and saved the final error; outer checker then stopped before query 13 under the established policy. Read-only Ollama identity/placement check responded unchanged; exact slow-generation cause unresolved. No replay, retry, timeout change or new inference.

Partial observations: 168/168 well-formed native calls, SUCCESS 11/12, competent 5/12, median wall 86.6405435 s, zero OOM, largest prompt 8187, median charged calls 9.5, budget-hit share 25%, zero thinking messages. 131 answers: 129 GOLD/SUPPORTED and two OFF_QUESTION/PATH_INVALID. Partial D3 fields remain undefined. Optional page omission is valid under the frozen T1 schema; direct evaluator/schema inspection corrected an intermediate commentary claim without changing any result.

Offline report-only exited zero. All 118 run-file hashes (105 prior), 122 protected identities, 43 pinned sources, 100 prior metrics and five prior table rows match. Full suite before inference: 598 passed in 34.27 s. Checkpoint report: docs/S20_granite42_screening.md; evidence: results/diagnostics/s20/granite42/. Eight frozen queries remain; continuation decision required before further inference. No production/scientific edit, S21 selection, other model, commit or push.


### Granite 4.2 remaining-eight continuation authorized

Researcher selected "Continue the remaining eight (Recommended)" after reviewing the 12/20 ERROR checkpoint. Authorizes only BH2_03991, BH2_04003, BH2_04007, BH2_04425, BH2_05366, BH2_05686, BH2_05843 and BH2_06427 in frozen order, preserving all twelve saved final outcomes, including BH2_03953 ERROR/CONNECTION. Unchanged frozen settings, one --max-new 1 invocation per episode and existing stop/integrity checks. No retry, timeout/source/config/scientific change, other model, S21, commit or push.

Continuation preflight: all 118 stopped-checkpoint run files, 122 protected, 43 pinned and 100 prior metric hashes match. Reused Ministral continuation helper with Granite identity/path and twelve-record prefix substitutions; syntax and assertions checked. Full-suite evidence remains 598 passed before inference; pinned source is unchanged, so no repeat was required. Preserve the stopped report, summary, per-query CSV, inspection, proof and table snapshot separately.


### Granite 4.2 continuation stopped at 15/20: second ERROR/CONNECTION

Authorized remaining-eight continuation saved BH2_03991 SUCCESS (155.876456 s), BH2_04003 SUCCESS (176.102251 s) and BH2_04007 ERROR/CONNECTION (144.983317 s), then stopped before query 16. All three launchers exited zero; outer checker stopped on the newly saved ERROR under the retained policy. BH2_04007 had fourteen successful model responses before the next request hit the 120-second read timeout. Read-only model identity/placement check responded unchanged. No retry, timeout adjustment or diagnostic inference. All earlier outcomes including BH2_03953 ERROR remain unchanged.

Partial: 244/244 well-formed native calls, SUCCESS 13/15, competence 5/15, median wall 108.939291 s, OOM 0, largest prompt 8190, median charged calls 14, budget-hit share 1/3, no thinking messages. 132 answers: 129 GOLD/SUPPORTED, three OFF_QUESTION/PATH_INVALID. Final D3 fields remain undefined.

Offline report-only exited zero. All 121 run hashes match, including all 118 stopped-checkpoint and 105 prior files; all 122 protected, 43 pinned and 100 prior metric hashes and five prior table rows unchanged. Suite remains 598 passed before inference, unchanged source. Original 12/20 evidence retained; new numbered stopped-15 report/summary/proof saved separately. Five frozen queries remain: BH2_04425, BH2_05366, BH2_05686, BH2_05843, BH2_06427. Further inference requires the established continuation decision. Report: docs/S20_granite42_screening.md. No source/scientific change, S21, commit or push.


### Granite 4.2 remaining-five continuation authorized

Researcher selected "Continue the remaining five (Recommended)" after reviewing the second ERROR checkpoint at 15/20. Authorizes only BH2_04425, BH2_05366, BH2_05686, BH2_05843 and BH2_06427 in frozen order, retaining all fifteen final outcomes and both ERROR/CONNECTION records. Keep all settings, one --max-new 1 invocation per episode and stop on each new ERROR, nonzero exit, drift or order discrepancy. No retry, timeout/source/config/scientific change, other model, S21, commit or push.

All 121 run files, 122 protected identities, 43 pinned source/input hashes and 100 historical metric hashes match. Captured all 115 current metric hashes and the 15/20 table as continuation baselines. Reused the prior continuation helper with only checkpoint, prefix and output-name substitutions; syntax and frozen-prefix assertions retained. The prior 598-test pass remains applicable because pinned sources are unchanged.


### Granite 4.2 stopped at 16/20: third ERROR/CONNECTION

Approved remaining-five continuation saved BH2_04425 ERROR/CONNECTION (142.561278 s), then stopped before query 17 under the retained policy. Seven successful model responses preceded the next request's 120-second HTTP read timeout. Launcher exited zero; outer checker stopped on ERROR. Read-only identity/placement check responded unchanged. All fifteen prior outcomes and both earlier errors are unchanged; no replay, retry or timeout adjustment.

Partial: 251/251 well-formed native calls, SUCCESS 13/16, competent 5/16, median wall 124.252552 s, zero OOM, largest prompt 8190, median charged calls 12.5, budget-hit share 31.25%, zero thinking fields. 132 answer items unchanged: 129 GOLD/SUPPORTED, three OFF_QUESTION/PATH_INVALID. At most 17/20 SUCCESS (85%) remains possible, below frozen D3's 90%; no complete verdict is assigned while four queries are unrun.

Offline report-only exited zero. All 122 run hashes match (121 previous checkpoint, 105 pre-Granite); 122 protected, 43 pinned and 115 existing metric hashes and five prior table rows match. Unchanged source; full suite remains 598 passed before inference. Separate stopped-16 report/summary/proof retained; earlier checkpoints unchanged. Final four: BH2_05366, BH2_05686, BH2_05843, BH2_06427. Further inference awaits continuation authorization. A proposed operational option is to finish these four despite further CONNECTION errors, preserving those outcomes and keeping all other stop conditions; it is not implemented or authorized yet. No source/scientific edit, S21, commit or push.


### Granite 4.2 final-four continuation and narrower stop policy authorized

Researcher selected "Finish four; continue past CONNECTION timeouts (Recommended)" after the verified 16/20 checkpoint. Authorizes only BH2_05366, BH2_05686, BH2_05843 and BH2_06427 with all scientific settings and the 120-second request timeout unchanged. Preserve all sixteen saved outcomes and all further timeouts in the official denominator. The between-invocation checker may continue only for ERROR/CONNECTION with a logged timed-out request; other ERROR causes, CONNECTION failures without timeout evidence, nonzero exits, identity/hash drift and order/count discrepancies still stop. No failed query is retried or repaired. This is a researcher-approved operational stop-policy amendment, not a scientific rule/threshold change.

All 122 run-file hashes, 122 protected and 43 pinned identities and the existing 115-metric baseline match; captured all 116 current metric hashes. Reused continuation helper with sixteen-record prefix, separate journal/log names and the approved narrow timeout exception. Its actual AST guard passed six synthetic assert-based checks: SUCCESS, logged CONNECTION timeout and PARSE_FAIL continue; refused CONNECTION, OUT_OF_MEMORY and RUNTIME stop. The 598-test result remains applicable to unchanged production source. No S21 work, other candidate, commit or push.


### Granite 4.2 full block complete: D3 FAIL on SUCCESS and competence

All four final queries completed SUCCESS: BH2_05366 (13.160678 s), BH2_05686 (148.298446 s), BH2_05843 (131.556515 s), BH2_06427 (44.859084 s). The approved logged-CONNECTION-timeout exception was therefore not triggered in live continuation. All twenty frozen outcomes saved; all prior records and three ERROR/CONNECTION outcomes remain unchanged. Each of twenty individual launcher invocations exited zero, saved exactly one record in frozen order and passed the applicable between-invocation integrity checks.

Final D3 FAIL: well-formed 327/327=100% (PASS); SUCCESS 17/20=85% (FAIL); competence 6/20=30% (FAIL); median wall 120.247903 s (PASS); OOM 0 (PASS). Zero text-tool attempts, PARSE_FAIL, episode TIMEOUT or nonempty thinking fields. Largest prompt 8190, median charged calls 12.5, seven budget hits (35%). 135 answer items: 132 GOLD/SUPPORTED and three OFF_QUESTION/PATH_INVALID. Final BH2_06427 submits three GOLD/SUPPORTED answers with benchmark precision/recall 1.0; raw example in final report/manual inspection.

Offline --max-new 0 exited zero. All 126 run-file hashes match, including all 122 last-checkpoint and 105 pre-Granite files; all twenty journal episode hashes match. All 122 protected identities, 43 pinned source/input hashes, 116 existing metric hashes and five prior candidate rows unchanged. Seventeen available post-invocation placement samples retain pinned digest/context 8192 and unchanged automatic partial CPU/GPU sizes. Unchanged full-suite evidence: 598 passed in 34.27 s; six guard checks passed. Proofs: results/diagnostics/s20/granite42/official-final-integrity.json and official-validation.json.

Report updated: docs/S20_granite42_screening.md. Earlier 12/20, 15/20 and 16/20 checkpoint reports and derivations preserved separately. No retry, diagnostic inference, timeout/source/config/scientific change, other model, 16K follow-up, S21 selection, commit or push. Stop after this candidate report.


## 2026-10-20 — S20 — Gemma 4 E4B full uninterrupted screening authorized
Decision: Researcher explicitly requested `gemma4:e4b-it-q4_K_M`: "run s20 tests on this model, all 20 queries uninterrupted". Run the existing frozen twenty-query block continuously, retaining every saved final outcome without retries or intermediate continuation approval. Use agent ID Gemma4-E4B in primary-3060ti-20261018.
Why: Measure this exact downloaded candidate under unchanged S20 settings. The existing runner supports --max-new 20 and checkpoints every episode.
Data seen before deciding: Researcher supplied the download transcript; prior candidate history existed. No Gemma biomedical episode had run when authorization was given. Subsequent preflight verified installed 7.5B Q4_K_M, tools, disabled thinking, and exact digest dc35e8d9c6061baa6f0fa870975ab6932e2542b579b13ea0f199fa4bb7300c9c; synthetic add and all 598 tests passed.
Changes to protocol or decision rules: none. Full-block execution replaces only intermediate operational continuation pauses for this request. Pool/round accounting and S21 selection remain separate researcher decisions.

## 2026-10-20 — S20 — Gemma 4 E4B complete; D3 FAIL
Decision: Record the unchanged evaluator result after all twenty uninterrupted queries: FAIL only on SUCCESS rate (16/20=80%, required >=90%). Four PARSE_FAIL outcomes remain official. Other criteria pass: 149/149 well-formed native calls, competence 11/20=55%, median wall 11.9732305 s and zero OOM. No S21 selection made.
Why: Apply existing D3 criteria to all frozen queries without outcome-dependent changes.
Data seen before deciding: All twenty saved outcomes and metrics; all four parse failures have incomplete JSON and final done_reason=length. Full suite 598 passed; report-only and 147 run hashes (126 prior), 120 prior metrics, 122 protected, 43 pinned sources and six prior rows verified unchanged.
Changes to protocol or decision rules: none. Report: docs/S20_gemma4_screening.md.

## 2026-10-20 — Gemma 4 E4B — Authorized isolated 16K context diagnostic
Decision: Researcher accepted the proposed four-failure diagnostic: "yeah do that with 16K context for this model and see". Rerun exactly BH2_03619, BH2_03762, BH2_03850 and BH2_03953 under a separate diagnostic run ID with num_ctx=16384 and every other scientific setting unchanged. Retain original S20 outcomes and D3 verdict.
Why: Test the context-limit explanation for the four incomplete 8K final outputs.
Data seen before deciding: Complete official 8K block and four parse-failure traces with done_reason=length; no 16K Gemma outcomes.
Changes to protocol or decision rules: none. This selected diagnostic is separate from S20 scoring and the S21 five-query requirement.

## 2026-10-20 — Gemma 4 E4B — 16K diagnostic results retained
Decision: Record all four diagnostic outcomes as SUCCESS; three queries have GOLD/SUPPORTED answers, while BH2_03762 has six OFF_QUESTION/PATH_INVALID answers. All four final reasons changed from length to stop. Context-limit explanation is strongly supported; no full-20-query 16K D3 verdict or S21 selection inferred.
Why: Separate recovered formatting from biomedical competence and preserve the official experiment.
Data seen before deciding: All four diagnostic traces and unchanged evaluator metrics; actual context 16384; 51/51 well-formed calls, zero OOM/thinking; all 147 official runs, 140 metrics, official table, 43 pinned and 122 protected hashes unchanged.
Changes to protocol or decision rules: none. Report: docs/S20_gemma4_16k_diagnostic.md.

## 2026-10-20 — S20 — Offline context-window parse-failure audit
Decision: Document previous models with observed context-related parse failures without changing official statuses or gates. Qwen3.5 has two direct final context-truncation cases; Ministral has three direct cases and one mixed case (BH2_03619: initial length termination at 8192, then normal-stop final JSON missing answers). No Qwen/Ministral 16K recovery is claimed. Link the already-completed Gemma 16K diagnostic (4/4 parse recovery, 3/4 competent).
Why: Researcher requested investigation of prior models after Gemma recovered at 16K; avoid conflating context truncation, schema omission and request timeouts.
Data seen before deciding: All 140 official S20 episodes, 20 exactly reproduced saved parser errors, existing timeout report and Gemma comparison. Five earlier final attempts have length termination, exact prompt-plus-output 8192 and output below num_predict=4096. All original run/metric/table/source and separate Gemma diagnostic hashes unchanged.
Changes to protocol or decision rules: none. No new model call or rerun. Report: docs/S20_context_window_audit.md.

## 2026-10-20 — S20 — Full 16K D3 reassessment authorized for Gemma, Qwen and Ministral
Decision: Researcher requests increased-context tests for Qwen3.5 9B and Ministral 3 8B, and allows Gemma 4 to count as passing only if it meets all D3 thresholds now. Run a complete fresh twenty-query block at num_ctx=16384 for each of the three exact existing model digests, in fixed order Gemma, Qwen, Ministral. Apply unchanged D3 thresholds to each entire block, including every failed outcome. Do not combine old 8K successes with selected 16K recoveries. Current researcher acceptance for these three candidates is conditional on the full 16K D3 verdict. Preserve chronological 8K history separately.
Why: Researcher-authorized context reassessment after observed context truncation; a four-query diagnostic cannot establish full-block D3 eligibility.
Data seen before deciding: All 140 official 8K episodes, original D3 verdicts, offline trace audit and Gemma selected four-query 16K results (4/4 parsing recovery, 3/4 competence). No full twenty-query 16K block exists for these candidates. No pilot/co-failure outcomes have been run.
Changes to protocol or decision rules: Authorized scoped exception to section 9.1 screening num_ctx=8192 for these separately labelled full 16K reassessment blocks, recorded under section 20. D3 definitions/thresholds unchanged; all other scientific runtime settings unchanged. Frozen protocol/decision-rule files are preserved. No S21 selection/freeze or additional candidate authorization implied. Run root results/runs/screening-16k; run ID context16k-3060ti-20261020.

## 2026-10-20 — Full 16K reassessment — Gemma passes all D3 thresholds
Decision: Accept Gemma4-E4B as passing at 16K under the researcher-authorized reassessment: complete fresh 20-query block, 181/181 well-formed calls, SUCCESS 19/20=95%, competence 14/20=70%, median wall 16.2779325 s and zero OOM. The one PARSE_FAIL remains included. Preserve the original 8K FAIL and separate four-query diagnostic; neither substitutes for this block.
Why: The researcher explicitly conditioned current acceptance on meeting the existing D3 thresholds after increasing context; all five now pass.
Data seen before deciding: Complete Gemma 16K block and unchanged evaluator metrics, actual context samples, immutable configuration/records and original hash checks. Qwen and Ministral full 16K verdicts are not yet available.
Changes to protocol or decision rules: no new change beyond the already logged scoped 16K reassessment authorization. No S21 panel selection/freeze.

## 2026-10-20 — Full 16K reassessment — Qwen passes all D3 thresholds
Decision: Accept Qwen35-9B as passing at 16K on its complete fresh block: 263/263 well-formed calls, SUCCESS 19/20=95%, competence 13/20=65%, median wall 56.839506 s and zero OOM. One new PARSE_FAIL (BH2_03991) remains included; both original 8K PARSE_FAIL queries now have SUCCESS. Preserve original 8K PASS and its metrics (18 SUCCESS, 15 competent); context increase is not assumed to improve every metric.
Why: Apply the researcher-authorized current 16K D3 acceptance rule to the full unchanged-threshold block.
Data seen before deciding: All twenty Qwen 16K outcomes and metrics, actual 16K samples, model identity and integrity checks; Gemma full 16K PASS already recorded, Ministral pending.
Changes to protocol or decision rules: no new change beyond the logged scoped context amendment; no S21 selection/freeze.

## 2026-10-20 — Full 16K reassessment complete — Gemma and Qwen accepted; Ministral fails
Decision: Apply the same D3 thresholds to all three complete fresh 16K blocks and implement current acceptance as Gemma4-E4B PASS, Qwen35-9B PASS, Ministral3-8B FAIL. Gemma: SUCCESS 19/20, competence 14/20, 181/181 valid calls, median 16.2779325 s, OOM 0. Qwen: 19/20, 13/20, 263/263, 56.839506 s, OOM 0. Ministral: 12/20, 12/20, 167/167, 168.0803425 s, OOM 0; eight request read timeouts fail only its SUCCESS threshold. All failures retained, no selective retries or stitched denominator. Historical 8K results remain unchanged.
Why: Researcher explicitly conditioned current acceptance on passing D3 after increased-context testing. Larger context qualifies Gemma on full evidence; Qwen still qualifies; Ministral still does not meet the gate.
Data seen before deciding: All sixty new episodes and metrics; four reproduced parse errors; eight saved 120-second read-timeout errors; 117 actual-16K context samples; three successful offline reports; all original/new source and result hash checks. Qwen old parse failures now parse no_answer, without competence recovery; Gemma selected-diagnostic recovery was not substituted into the fresh block.
Changes to protocol or decision rules: no new change beyond the pre-inference scoped 16K context amendment logged under section 20. All D3 thresholds unchanged; no S21 selection/freeze. Complete report docs/S20_full_16k_reassessment.md; acceptance artifact results/diagnostics/s20/full-16k-20261020/acceptance.json.

## 2026-10-21 — S20 — Granite 4.1 complete; shared screening status reconciled

Decision: Record the completed researcher-authorized Granite41-8B 8K block as
D3 PASS and reconcile all eight completed candidates in the shared documents.
The earlier Granite 4.1 deferral is superseded by the user's later instruction
to run all twenty queries and continue after query errors. The completed block
has 20/20 SUCCESS, 14/20 competent queries, 217/217 well-formed native calls,
median wall 61.3250475 s and zero OOM. There were no ERROR, TIMEOUT, PARSE_FAIL
or thinking messages. Of 568 submitted items, 525 are question-valid/SUPPORTED
and 43 are OFF_QUESTION/PATH_INVALID. SUCCESS remains distinct from correctness.

Why: The researcher requested a documentation update including the other failed
models. A complete status summary must retain all failures and distinguish the
original 8K blocks from the three researcher-authorized full 16K reassessments.

Data seen before deciding: All eight original screening-table rows, per-model
reports, Granite 4.1's completed traces/metrics and final integrity proof, and
the existing complete 16K acceptance artifact. Original 8K failures: Llama31-8B
and Granite33-8B on call validity/competence; Granite42-8B on SUCCESS/competence;
OLMo3-7B on competence; Ministral3-8B and Gemma4-E4B on SUCCESS. Qwen35-9B and
Granite41-8B pass at 8K. Separate full 16K results: Gemma PASS, Qwen PASS,
Ministral FAIL on SUCCESS (eight retained request-timeout errors). Current
passing candidates therefore number three across three families: Granite,
Gemma and Qwen; the other five completed candidates remain failing. A fourth
passing model is still needed before the D3 panel requirement can be met.

Granite 4.1 evidence: 42 focused tests passed in 6.38 s; synthetic native tools
and think=false passed; full and offline report invocations exited zero.
Final proof verifies twenty unique sequential attempt-1 records, 21 new
configuration/episode hashes, 359 prior result/metric hashes, 43 source/input
pins, 122 protected identities and seven unchanged prior table rows. The full
suite was not repeated because the pinned implementation was unchanged.

Changes to protocol or decision rules: none. This entry records existing
evidence and corrects shared documentation only; no new inference, retry,
metric/source/configuration change, additional model authorization or S21
selection/freeze. Historical entries remain intact. Routine engineering choice:
one linked current-status document, with dated notices above historical
progress/plan/checklists and the old shortlist. Reports:
docs/S20_granite41_screening.md and docs/S20_screening_status.md.

## 2026-10-21 — S20 — Granite 4.1 full 16K block authorized

Decision: The researcher requested "run granite 4.1 at 16K and update". Run a
fresh complete twenty-query block for the same Granite41-8B identity at
num_ctx=16384, retaining all other scientific settings, all saved failures and
the previous continue-after-query-error instruction. Use isolated run ID
granite41-context16k-3060ti-20261021 under results/runs/screening-16k. Apply the
unchanged D3 criteria to the full block and report both 8K and 16K evidence;
do not replace or stitch the existing 8K PASS with selected new outcomes.

Why: Researcher-authorized context reassessment after the complete original
8K block; its largest recorded prompt was 8187 tokens. No Granite 4.1 16K
screening episode existed when this authorization and manifest were recorded.

Data seen before deciding: The full 8K PASS (20 SUCCESS, 14 competent,
217/217 valid calls, median 61.3250475 s, zero OOM), existing other-model 16K
results and the researcher's explicit request. Preflight confirms the original
digest 444af1c4b2fedd6b54041aca558e7300b0b3d5c0468c44619126240323ba2852,
43 unchanged source/input pins and 122 protected identities. The 42 screening
tests passed in 2.15 s. A baseline protects 488 existing evidence files.

Changes to protocol or decision rules: Scoped researcher-authorized exception
to section 9.1's screening context for this separately labelled full 16K block,
as in the earlier section 20 reassessments; D3 thresholds unchanged. No source,
prompt, tool, timeout, temperature, seed or output-cap change, failed-episode
retry, additional candidate authorization or S21 selection/freeze. Routine
engineering: reuse the earlier 16K driver with this candidate, UTF-8 reads and
allow missing placement after a failed episode while checking every observed
matching-model context. Diagnostics: results/diagnostics/s20/granite41-16k-20261021/.

## 2026-10-21 — Granite 4.1 16K stopped on researcher instruction

Decision: The researcher explicitly requested "stop the test, i understand it
will not pass". Terminate the screening processes immediately, unload the
model and do not resume without a new instruction. Fifteen final outcomes are
saved: six SUCCESS and nine ERROR/CONNECTION, each with a logged 120-second
read timeout. Query 16 (BH2_04425) was interrupted without a final record;
BH2_05366, BH2_05686, BH2_05843 and BH2_06427 were not started.

Why: Honor the explicit stop request. With nine saved errors, at most 11/20
SUCCESS (55%) is possible, below the existing 90% requirement, even if every
unsaved query succeeded. Retain an incomplete/stopped status with no final
D3 verdict or full-block competence; do not fabricate the five missing outcomes.

Data seen before deciding: Fifteen immutable final records, runtime samples,
console timeouts and the researcher instruction. All fifteen initial message
pairs match the original 8K block. Preflight passed 42 screening tests, four
context-guard cases, native tools and disabled thinking at actual context
16384. Stop-time checks preserve 488 earlier evidence hashes and 122 protected
identities. Sixteen new run/configuration hashes are recorded in stopped-summary.json.

Changes to protocol or decision rules: none. The explicit stop supersedes the
earlier authorization to finish twenty queries. Original Granite 4.1 8K PASS
remains intact; no 16K acceptance or final S21 selection. No retry, timeout
change, further inference or final full-block evaluator/report-only invocation.
Report: docs/S20_granite41_16k_stopped.md; shared progress/plan/checklist and
complete screening status updated to record the stop.

## 2026-10-21 — S20 — Command R7B complete full original 8K block

Decision: Execute the researcher's explicit request to run the whole S20 test,
all twenty queries, for downloaded command-r7b:7b. Apply original protocol
section 9.1 settings and unchanged D3 using the existing launcher. Isolate run
command-r7b-3060ti-20261021, agent CommandR7B-7B, family Cohere. Retain every
final outcome without retries. No S21 selection or D3 round accounting assigned.

Data seen before inference: existing candidate history; native-tools metadata
for installed digest ff4e9696ef9f19b62e3f7d7261c95dcc9bb15a7c0398493366d851119fe2e1ef,
Q4_K_M, parameter metadata 8.0B; 42 passing screening tests; frozen 8K settings
and 512 baseline hashes. The synthetic add test returned valid prose without
a native call and its assertion failed. That evidence was retained in preflight;
the explicitly requested full block measured behavior without introducing a
new synthetic-use gate, tuning prompts or changing model packaging. Policy
and identity/placement evidence were saved before official inference.

Result: all twenty attempt-1 queries saved sequentially; nineteen SUCCESS and
one PARSE_FAIL (BH2_00461 returned a JSON array rather than the required object).
Zero native/text-tool attempts; well-formed rate is undefined and fails D3.
Competence 0/20 also fails. Median 2.889849 s, OOM 0. Two submitted answer
items were OFF_QUESTION/UNGROUNDED and UNRESOLVED/NOT_APPLICABLE. No thinking,
request errors or episode timeouts. Largest prompt=2292, not near the 8192 cap.
Overall D3 FAIL. Three passing candidates remain; a fourth is still needed.

Verification: official/offline exit zero, 42 tests passed in 2.31 s; all 512
baseline hashes, 43 source/input pins, 21 new run hashes and eight prior
screening rows match. No source/configuration/prompt/tool/input/rule change.
Routine engineering: dated isolated run and diagnostics, reuse of existing
preflight/summary code, runtime samples, immutable evidence and offline replay.
No scientific amendment, completed-episode retry, commit or push.
Report: docs/S20_command_r7b_screening.md.

## 2026-10-21 — S20 checkpoint commit and push authorized

Researcher explicitly requested committing and pushing the completed work.
Include the pending related S20 reports, candidate metrics, context diagnostics,
full 16K reassessments, stopped Granite 4.1 16K evidence and Command R7B block
as one screening checkpoint, preserving all historical outcomes and settings.
Keep unrelated scratch console output, Graphify state and Ministral speed
experiments out of the commit. Raw results/runs remain ignored under repository
policy. The existing unpushed OLMo commit is included in the requested push.

Pre-commit verification: 598 tests passed in 47.92 s; all 264 new JSON artifacts
parsed, twelve diagnostic Python helpers passed syntax checks and the selected
files had zero credential-pattern matches. Command R7B's 512 historical/source
and 21 new run hashes still match. Review corrected only accidental encoding
damage in older checklist text. No experimental source/configuration, frozen
rule, result or S21 selection change. Fetch confirmed main has no remote-only
commits; use a normal push without rewriting history.

## 2026-10-28 — S20 — fresh Ministral block on RTX 5060 Ti

Researcher instruction: prepare S20 and run Ministral at context 16K with an
unquantized KV cache. The subsequent explicit clarification retains existing
Q4_K_M weights and selects f16 KV, rather than BF16 model weights. Execute all
twenty frozen screening queries under fresh run ministral3-5060ti-16k-20261028;
preserve all historical outcomes and every new final status without retries.

Use the installed Ollama 0.40.12 on the new host, recorded separately from the
historical 0.40.4 runs. Dedicated localhost port 11435, model store D:\Models,
Flash Attention enabled, one sequence, f16 KV. Runtime evidence confirms context
16384, K/V f16, all 35 layers on the RTX 5060 Ti and size_vram=size. Model tag
ministral-3:8b retains digest
1922accd5827ebe6829e536369195db25eaf664528dc66206d646ea3bb386b71.
All other screening settings and D3 definitions remain unchanged: think=false,
temperature=0, seed=42, num_predict=4096, page_size=50, budget=30, request timeout
120 s, episode timeout 600 s. No S21 selection or D3 round assignment.

Before official inference: 596 tests passed, two real-data tests skipped because
raw BioHopR is absent; frozen S20 inputs and references are restored. Two new
offline driver checks pass, covering runtime identity/context/full residency/KV
and rejecting source content changes while permitting checkout-only CRLF.
Seven relocated files differ from historical source hashes only by CRLF; the
new manifest pins their actual current bytes. Historical manifests stay intact.
Synthetic add(2,3) emitted one native call with integer arguments and no thinking.
The driver reuses existing screening, agent, persistence and evaluation code;
source, input and historical-output hashes are checked between episodes.

Routine engineering choices: isolated port, fresh host/run paths, separate
immutable manifest, runtime samples, operational driver and isolated reporting.
No frozen protocol, prompt, tool, data, scientific threshold or evaluator change.
Artifacts: results/diagnostics/s20/ministral3-5060ti-16k-20261028/.

Completed result: D3 PASS for this isolated host/runtime block. Twenty final
outcomes: eighteen SUCCESS, two PARSE_FAIL (BH2_03619, BH2_03879), no errors,
timeouts or OOM. Competent queries 17/20; native calls 179/179 well-formed;
median episode wall time 45.307066 s. Both parse failures retain final
done_reason=length at prompt_eval_count=16364. No outcome was retried.
Offline report exited zero without inference; all 21 new run-file hashes,
459 historical-file hashes and source/input pins match. Dedicated server was
unloaded/stopped; original server remains. Full report:
docs/S20_ministral3_5060ti_16k.md. No old-host reclassification or S21 selection.

Researcher subsequently explicitly authorized committing, pushing and updating
the Drive backup folders. Publish the completed new-host S20 reports, operational
driver/tests and diagnostic evidence. Preserve the pre-existing untracked
Ministral speed experiments outside this commit; raw run records remain ignored
by Git and are included through the existing Drive backup procedure. Remote
main matches local HEAD before publication. Focused screening/driver verification:
44 tests passed; source pins, 459 historical and 21 new run-file hashes match;
31 new JSON artifacts parse and the selected files have no credential patterns.


## 2026-10-28 — S20 — authorized fresh Gemma block on RTX 5060 Ti

Before inference, the researcher explicitly authorizes implementing/testing the
new-host launcher, one complete fresh twenty-query Gemma4-E4B S20 block,
investigation, project records, scoped commits/push to GitHub main and upload to
the existing shared Google Drive backup. No further confirmation is needed.
Stop after this model; no other candidate or S21 work is authorized.

Run ID gemma4-5060ti-16k-20261028, model gemma4:e4b-it-q4_K_M,
digest dc35e8d9c6061baa6f0fa870975ab6932e2542b579b13ea0f199fa4bb7300c9c.
Use installed PATH Ollama client/server 0.40.12, without version changes, as a
separate host/runtime condition from historical 3060 Ti / Ollama 0.40.4.
Store D:\Models; isolated server port 11435, f16 KV only, context 16384,
think=false, temperature 0, seed 42, num_predict 4096, page_size 50, budget 30,
request timeout 120 s, episode timeout 600 s. Preserve Q4_K_M weights, all
prompts/tools/parsers/evaluators/D3 thresholds, twenty-query order, historical
results and acceptance records. Preflight requires native tools, actual 16K,
f16 K/V logs and /api/ps size_vram=size corroborated by all-layer GPU logs.
If any requirement fails, publish the blocker before official inference.

Data seen before deciding: historical 8K Gemma 16 SUCCESS / 11 competent;
complete 16K 19 SUCCESS / 14 competent, including BH2_03762 PARSE_FAIL;
selected four-query 16K diagnostic parsed BH2_03762 with unsupported answers.
The prior new-host Ministral outcome is present as unrelated uncommitted work.
Do not tune or add experimental retries. Save every final status; crash resume
may execute only unfinished queries. Commit tested launcher before inference.

Routine engineering choices: adapt existing new-host driver, use separate
manifests/metrics/output paths, preserve saved Git provenance on resume,
normalize CRLF only when validating historical source identities, pin actual
new-host bytes, and verify historical hashes plus runtime samples throughout.
Host CPU is Ryzen 7 7700; usable RAM about 31 GiB; GPU RTX 5060 Ti 16311 MiB,
driver 610.88. New host/runtime results cannot isolate a GPU-only causal effect.


## 2026-10-29 - S20 - Gemma new-host block investigated

The authorized 2026-10-28 run gemma4-5060ti-16k-20261028 completed all twenty
queries in one invocation: 19 SUCCESS, one PARSE_FAIL (BH2_03879), zero
ERROR/TIMEOUT/OOM. All five D3 criteria PASS: 185/185 calls well formed,
95% SUCCESS, 70% competence, median 10.8510705 s, zero OOM. Preserve each
final outcome; no further inference or retry follows the repeated request.

Runtime checks: exact pinned Q4_K_M digest, Ollama 0.40.12 client/server,
context 16384, f16 K/V logs, 43/43 GPU layers and size_vram=size in all 41
samples. All generation/episode settings, prompts/tools/parsers/evaluators
and D3 definitions remain unchanged. Launcher/authorization commit b49ac91
preceded all inference. Historical source relocation differs only in CRLF
for seven files; actual bytes are pinned.

Six material outcome changes were investigated against both historical full
blocks. BH2_03762 recovers valid no_answer JSON after missing-relation calls
and budget exhaustion; competence remains zero. BH2_03879 newly fails after
prose at the 4096-output cap and truncated JSON near 16K. BH2_03619 submits
79 supported items versus 77; BH2_03953 submits 82 versus 90. BH2_04003
returns four wrong-type/hop answers; BH2_05366 returns thirty shortcut answers.
All fourteen competent query identities remain the same as the old full 16K
block. Full evidence and limitations: docs/S20_gemma4_5060ti_16k.md.

Network-forbidden offline reporting passes with the isolated server stopped,
reproducing the metrics and preserving all 21 new run/configuration hashes,
1315 historical evidence hashes and 46 source/input pins. One initial relative
runpy-path harness error was corrected in the test invocation only; its
transcript is retained. Production/scientific code and records were unchanged.
The separate host/runtime condition prevents GPU-only causal attribution.
Historical acceptance is preserved; no S21 selection is made. Publish only
this task's scoped changes, then verify actual Drive uploads under the
documented ten-minute rule.


## 2026-10-29 - S20 - Gemma publication and Drive quota blocker

Scoped result/report commit 8c53402 and prior launcher/authorization b49ac91
were pushed normally to GitHub main. The documented Drive wrapper staged
1939 stable files; the 69 Gemma scientific files were all older than ten
minutes. Drive repeatedly rejected new uploads with HTTP 403
storageQuotaExceeded. Stop only this copy process rather than repeating a
permanent storage failure; preserve all local/shared data.

A subsequent exact-list one-way rclone checksum check at 14:22:51 UTC exited
1: all 69 Gemma scientific files were missing, zero present. Backup is not
complete, despite successful Git publication. Raw episodes and their original
hashes remain local; diagnostics are published on GitHub. Full expected local
MD5 inventory and blocker: docs/S20_gemma4_5060ti_backup.md. The researcher
must restore available storage in the authenticated Drive account before
upload/verification can finish. Do not delete research data, substitute a
backup destination, bypass the age rule, or rerun model episodes to address
this external blocker. No S21 or additional-model work follows.


## 2026-10-29 - S20 - Gemma Drive backup recovered with authorized alternate account

The researcher instructed use of their university Google account, already an
Editor of the existing shared folder, and completed rclone reauthentication.
The exact requested account identity and canAddChildren capability were
verified privately through Drive metadata before retrying. Credentials remain
outside Git. The cofail_gdrive remote now uses that account; no folder ID,
profile, backup script, age rule, experiment or preservation policy changed.

The documented manual backup-repair workflow uploaded the Gemma outputs.
At 14:33:42 UTC an independent exact-list rclone checksum check exited zero:
69 matching Gemma scientific files, zero differences. All local MD5 values
still match the retained inventory; the twenty raw attempt-1 episodes and
configuration are now verified on Drive. No model calls/retries were made.
The previous quota-blocked attempt remains dated history.

The whole-repository copy still exited 1 because nine older S13-S15 files
could not be archived into history (Google cannotAddParent). They are outside
this run; their existing remote versions were preserved. Record that broader
limitation without weakening backups or claiming all 1939 files were refreshed.
Gemma's complete 69-file backup is independently verified. Evidence and expected
hashes: docs/S20_gemma4_5060ti_backup.md. Stop; no next model or S21 work.


## 2026-10-29 - Authorized fresh Granite41-8B S20 on RTX 5060 Ti

Researcher explicitly authorizes launcher adaptation/tests, one fresh complete
20-query block, investigation, scoped records/commits/push and shared Drive
backup. This does not resume or replace the stopped 3060 Ti block. No further
model or S21 work. Use installed PATH Ollama 0.40.12 without version changes,
separate from historical 0.40.4; D:\Models; f16 KV only; Q4_K_M pinned weights.
Run granite41-5060ti-16k-20261029; digest
444af1c4b2fedd6b54041aca558e7300b0b3d5c0468c44619126240323ba2852.
Context 16384, think=false, temperature0, seed42, num_predict4096, budget30,
page_size50, request120s, episode600s. Unchanged prompts/tools/parsers/D3.
Require actual context, f16 logs, size_vram=size and all-layer GPU evidence
before official inference. Preserve every final status, no completed retries.
Data already seen: old 8K 20 SUCCESS/14 competent; stopped 16K 15 outcomes,
six SUCCESS/nine read-timeout CONNECTION errors; Gemma and Ministral new-host
results. Hardware/runtime changed together; no GPU-only causal attribution.
Routine engineering: adapt tested Gemma driver, isolated port/manifests,
source/history pins, all-status resume and separate offline evaluation.
No other model experiment or Ollama process was running at preparation.


## 2026-10-29 - Granite41 fresh 5060 Ti block completed

D3 PASS:20 SUCCESS,16 competent,236/236 calls,median38.870718s,zero OOM,
ERROR,HTTP read timeout or episode TIMEOUT. Max response69.404479s. All41
runtime samples confirm f16/context16384/full GPU. Nine old incomplete16K
timeout queries recover SUCCESS; no invented outcomes or verdict for that
stopped block. Nine material8K changes investigated. Network-forbidden offline
report and1388 historical/21 new/46 source hashes pass. See
docs/S20_granite41_5060ti_16k.md. No retries,tuning,new model or S21.


## 2026-10-29 - Granite41 publication and verified Drive backup

Results7826348 pushed to main; launcher/authorization fe0aab2 preceded inference.
Initial backup deferred recent files. After all65 became age-eligible, repeated
documented backup staged2004 stable files. Exact checksum check at15:07:33 UTC
exited0:65 matching Granite files,zero differences,including twenty raw episodes
and configuration. Local MD5 values match the retained inventory. Same shared
folder and authorized university account; no age-rule bypass or deletion.
Nine broader historical archive move errors remain outside this run, so global
backup success is not claimed. See docs/S20_granite41_5060ti_backup.md.
No extra experiment,model retry or S21 work. Historical evidence preserved.

## 2026-10-29 — Authorized Qwen35-9B fresh RTX 5060 Ti 16K S20
Researcher explicitly authorizes launcher implementation/testing, synthetic preflight,
one fresh sequential twenty-query block, investigation, records, commit/push to main
and existing shared Drive backup. Installed PATH Ollama is authorized unchanged
(departure from historical 0.40.4; verify actual client/server). D:\Models, pinned
Q4_K_M digest, f16 only, actual16384, full GPU API equality plus runtime logs required.
All other protocol settings and D3 thresholds unchanged. Stop on preflight blocker;
keep every final status, resume unfinished only, no extra conditions or S21.
Execution note: initial commit failed because local Git author was unset; synthetic preflight inadvertently continued before commit. No official query ran. Reuse existing repository author via per-command Git settings; commit executable launcher before official inference. Preflight passed exact identity, tools/no-thinking, actual16K, f16 and33/33 GPU layers with size equality.


## Qwen RTX 5060 Ti S20 completed — 2026-10-29
Fresh16K D3 FAIL:16/20 SUCCESS,12 competent,259/259 well-formed calls,
median30.627939s,zero OOM. Four retained PARSE_FAIL. Full GPU/f16/actual16K
verified; historical8K and16K PASS preserved. See docs/S20_qwen35_5060ti_16k.md.
No retries,additional condition,other model or S21.


## 2026-10-29 — Authorized Qwen35-9B 32K context reassessment

Researcher explicitly authorizes one fresh complete twenty-query S20 block at
num_ctx=32768 on the RTX 5060 Ti, launcher implementation/tests, investigation,
scoped commits/push to GitHub main and existing shared Drive backup. This is a
post-result reassessment chosen after observing historical 8K (18 SUCCESS/15
competent), historical 16K (19/13) and same-host 16K (16/12, D3 FAIL). It does
not replace any prior run or acceptance, select S21, or authorize another model
or condition. This explicit amendment supersedes the guide's 16K-only scope for
this block; frozen protocol and decision-rule documents remain unchanged.

Run ID qwen35-5060ti-32k-20261029. Reuse tested new-host Qwen launcher and
unchanged runner, prompt, tools, parser, evaluators and all five D3 thresholds.
Pinned qwen3.5:9b Q4_K_M digest
56671c2ab9385f9cfcb404638e32cd62d88e3501d44822208363c010179a3c90.
Only context changes: think=false, temperature=0, seed=42, num_predict=4096,
budget=30, page_size=50, request timeout=120s, episode timeout=600s remain.
Installed PATH runtime preserved (baseline client/server 0.40.12, distinct from
historical 0.40.4), existing Flash Attention configuration preserved, f16 only,
D:\Models explicitly set on isolated port11435. Commit executable changes and
this authorization before synthetic/official inference. Require actual32768,
f16 K/V runtime logs, size_vram=size and33/33 GPU layers; stop/publish blocker
if any fails. Keep every final status, resume only unfinished queries.

No active model experiment or Ollama server found; unrelated graphify services
and untracked ministral_speed directory preserved. Remote main matched dc8a553.
Routine engineering: unique output roots, adapt tested guards to32768, retain
source/input/history pins, per-episode memory samples, offline paired reporting.
No new scientific rule or method.

32K preflight engineering correction: committed launcher3bc7b69 preceded all
inference. Synthetic native add/result, identity, actual32768, f16 K/V,
size_vram=size and33/33 GPU layers passed. An extra guard incorrectly required
the server environment string FLASH_ATTENTION:true. The inherited environment
had no override (preserved), server reported false, but backend explicitly
logged "warmup: flash attention is enabled". Correct guard to require effective
backend Flash Attention, without changing environment/runtime/model settings.
Initial manifest/config preserved as preflight-initial.* before repinning the
corrected executable; no official episode exists and no synthetic retry needed.
Baseline16K configured FLASH_ATTENTION:true; both backends enable it, but the
configuration-string difference is disclosed rather than claiming an exact
context-only controlled comparison. No scientific component or check weakened.


## 2026-10-29 — Qwen35-9B 32K block completed

D3 FAIL:13/20 SUCCESS,12 competent,294/294 well-formed calls,median28.6345515s,
zero OOM/ERROR/TIMEOUT. All twenty attempt-1 outcomes retained. No crash,repeat,
repair or additional condition. Three same-host16K no_answer results03619,03881,
04003 become PARSE_FAIL without competence change; all422 supported IDs unchanged.
Seven failures investigated: output caps, final-turn calls/prose,32K boundary
pressure. All42 runtime samples verify actual32768,f16,full GPU; backend Flash
Attention enabled. Source/input/history pins and network-forbidden offline replay
pass.1527 historical,21 new,51 source/input hashes verified. Model unloaded and
isolated server stopped. Detailed report:docs/S20_qwen35_5060ti_32k.md. No S21
selection or modification of historical acceptance.


## 2026-10-29 — Qwen32K publication and verified backup

Results b0d0f9e pushed to main. After first backup deferred recent files,waited
until every expected file passed the default10-minute age rule; reran documented
backup16:19:47 UTC. Exact-list checksum check16:21:53 UTC exited0:74 matching
files,zero differences,including20 episodes and config. Local MD5 inventory
unchanged. Both broad backups retain nine unrelated historical cannotAddParent
archive failures; no global backup-success claim or preservation-policy change.
See docs/S20_qwen35_5060ti_32k_backup.md for all74 expected hashes. Final docs
restore an unintended encoding change in older task text; original text verified.
No further model inference or S21.


## 2026-10-29 — Authorized Gemma4-E4B 32K context reassessment

Researcher explicitly authorizes one fresh complete20-query S20 block at32768,
launcher/tests, investigation, scoped records/commits/push to GitHub main and
existing shared Drive backup. Post-result reassessment after same-host16K
19 SUCCESS/14 competent and historical8K16/11,16K19/14; Qwen32K13/12 also seen.
Supersedes guide's16K-only scope for this block only, preserving historical
acceptance. No other model,extra condition,retry,output repair or S21 selection.

Run gemma4-5060ti-32k-20261029; gemma4:e4b-it-q4_K_M,Gemma4-E4B,digest
dc35e8d9c6061baa6f0fa870975ab6932e2542b579b13ea0f199fa4bb7300c9c.
Only scientific setting change:num_ctx16384→32768. Keep4096 output,f16 KV,
think=false,temp0,seed42,budget30,page50,request120s,episode600s,original query
order,prompt/tools/parser/evaluator/re-prompt and all five D3 thresholds.
Installed PATH client/server0.40.12 unchanged,historical0.40.4 separate.
Recreate tested Gemma16K server configuration:Flash Attention true,one sequence,
D:\Models,isolated11435; server default context follows authorized32768.
Preserve runtime-selected draft-mtp,max3,backend sampling,draft blob identity,
main43/43 and draft5/5 GPU layers,f16 sliding/non-sliding caches. No speculative
tuning. Require API actual32768,size_vram=size and corroborating runtime logs;
stop/publish blocker before official block if unmet.

Commit authorization/executable code before synthetic or official inference.
Unique output roots,exact source/input/history pins,all-status write-once resume,
per-episode memory samples,network-forbidden reporting and paired inspection are
routine engineering. No scientific rule/method change. No active experiment or
Ollama process found; remote main883d7a4 current; unrelated minispeed work kept.


## 2026-10-29 — Gemma32K block completed

D3 PASS:20 SUCCESS,16 competent,188/188 calls,median11.0878265s,zero OOM,
ERROR or TIMEOUT. One sequential twenty-query invocation,no completed retries.
Only03879 and04003 materially change against same-host16K:86 and74 supported
answers gained; total569→729 across16 queries,still incomplete retrieval. Other
eighteen outcomes/sets unchanged;03762 no_answer,05366/03881 shortcuts,03991
no_answer persist. All41 runtime samples pass; main43/43,draft5/5 GPU,f16
sliding/non-sliding caches,actual32768,identical Flash Attention and speculative
configuration. Configured context-only same-host reassessment,not replicated
causal evidence or historical acceptance replacement.
Network-forbidden offline reporting and1606 historical/21 new/51 source/input
hashes pass. Model unloaded and isolated server stopped. Report:
docs/S20_gemma4_5060ti_32k.md. No S21 or further model/condition.


## 2026-10-30 — Authorized Ministral3-8B same-host 32K S20 reassessment
Researcher explicitly authorizes a fresh complete twenty-query block at num_ctx32768,
chosen after observing same-host16K18 SUCCESS/17 competent with two parse failures.
This supersedes guide16K-only scope for this block. Preserve all historical outcomes
and acceptance. Keep num_predict4096,f16 KV,Q4_K_M digest1922accd5827ebe6829e536369195db25eaf664528dc66206d646ea3bb386b71,
installed PATH Ollama version and Flash Attention on,one sequence,D:\Models.
All other scientific settings,prompts,tools,parser,JSON re-prompt,evaluators and D3
unchanged. Commit executable code before synthetic or official inference. Require
actual32768,f16 K/V,API size_vram=size and35/35 GPU logs or publish blocker.
Explicit authorization includes launcher tests,investigation,records,commit,push main,
existing shared Drive backup with default age/checksums. No extra condition,other
model,S21 selection or replacement/retry of completed outcomes is authorized.
