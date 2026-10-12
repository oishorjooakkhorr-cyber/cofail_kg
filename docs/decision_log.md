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
