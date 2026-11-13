# Table 11 — Follow-up (P1, P2)

**Status:** EXPLORATORY — NOT RUN

**Basis:** docs/decision_log.md, entry 2026-11-12 "S30 — Plan after D7", section C3; docs/decision_log.md, entry 2026-11-13 "B1 — Outcome NOT CLEAN; follow-up not run; no full run"; docs/decision_log.md, entry 2026-11-14 "S37 — D8 not applicable after D7 DESCRIPTIVE; no scaling"

Produced by `scripts/38_final_tables.py` at commit `d6a00137dc22cbec6f9d537432a0166f5d0f9c6b` (tracked files clean: True; producing code committed at this commit: True).

Inputs (SHA256 in `provenance.json`; last commit that touched each):

- `docs/decision_log.md` — e7e844962e02a5908d785747d8dece5e4d21ab11

Not run (decision log 2026-11-13, B1 NOT CLEAN): the follow-up (F1–F3) has no episode, so neither prediction is held or not held.

## 11a. Pre-registered predictions of the follow-up study

CSV: `table11a_predictions.csv`

| Item | Text of decision log 2026-11-12 "Plan after D7", section C3 (verbatim) | Status |
|---|---|---|
| P1 (original wording) | P1 (original wording): (a) at least 5 of the 150 queries have CF3^{Q,H1} = 1; and (b) in at least 80% of those queries, the shared feature chosen by the §21 candidate rule is (u, `off-label use`) with mechanism WRONG_TURN_HOP2. | Not run (decision log 2026-11-13, B1 NOT CLEAN) |
| P2 (approved vs original) | P2 (approved vs original): per agent, X = number of queries (SUCCESS in both runs for that agent) with ≥ 1 off-label answer. An agent is testable if X_orig ≥ 3. P2 holds if at least 3 agents are testable and X_approved < X_orig for every testable agent. | Not run (decision log 2026-11-13, B1 NOT CLEAN) |
| Also reported, not part of P2 | Also reported, not part of P2: CF3^{Q,H1} under each wording, per-agent question-valid precision, benchmark recall, no-answer rate, answers per episode (to show whether the rewording only suppresses answers in general). | Not run (decision log 2026-11-13, B1 NOT CLEAN) |

Section C3 opens: "3. Predictions (fixed now, before any follow-up episode exists):" and closes: "Each prediction is reported as held or not held, whatever the result."

Quoted verbatim from docs/decision_log.md by the script; only the log's hard line wraps are joined.
