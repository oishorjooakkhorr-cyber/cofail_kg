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
