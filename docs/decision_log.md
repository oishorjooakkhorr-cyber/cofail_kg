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
