# S29 — Gate D6 mechanical check (pilot_v1)

**Status:** this is the mechanical application of Gate D6 by Claude Code (2026-11-08), as asked in
the runbook S29 prompt. It is **not** the researcher's pilot decision. The decision, the protocol
§21 freeze and the decision-log entry follow separately (see `docs/S29_guidance.md`).

Sources: `docs/decision_rules.md` D6 (line 119); `results/reports/pilot_v1_report.md`, section
"D6 quantities" (pilot_v1, 100 queries × 4 agents, latest attempts). Nothing was modified to
produce this check.

## Outcome: **YELLOW** (pilot passes; D6 passes on GREEN or YELLOW)

## Quantities

| Symbol | Value |
|---|---|
| `E` | 0.0425 (17/400) |
| `H` | 1.000 (100/100) |
| `N` | 3 (BH2_03356, BH2_05290, BH2_05778) |
| `O > null` | O_H1 = 3, N1-H1 p95 = 2.0 → 3 > 2.0, **true** (p = 0.0107) |
| `P` | 3 (effect/phenotype:disease:drug; gene/protein:disease:drug; gene/protein:drug:disease) |

## Rules in the stated order

| Order | Outcome | Rule | Evaluation | Holds |
|---|---|---|---|---|
| 1 | HOLD | `E > 15%` | 0.0425 > 0.15 | no |
| 2 | RED | `H < 20%` or `N < 3` or not `O > null` | 1.000 < 0.20: no · 3 < 3: no · not(true): no | no |
| 3 | GREEN | `H ≥ 40%` and `N ≥ 10` and `O > null` and `P ≥ 3` | yes · **3 ≥ 10: no** · yes · yes | no |
| 4 | YELLOW | otherwise | — | **yes** |

Action for YELLOW (decision_rules.md D6): freeze §21 (S29); run the expansion reserve (S30);
Phase 2 exploratory unless D7 is CONFIRMATORY.

## Interpretation flags (reported, not gates)

- **Ordering flag** (`O_N1` exceeds N1 but `O_N2` does not exceed N2): **not set**. O_N1 = 3 > p95
  2.0, and O_N2 = 3 > p95 2.0.
- **Ambiguity flag** (> 70% of the `N` queries in R1/R2/BOTH_AMBIGUOUS types): **set**, 3/3 = 100%
  (BH2_03356 R2_AMBIGUOUS, BH2_05290 R2_AMBIGUOUS, BH2_05778 BOTH_AMBIGUOUS).

## For the researcher to inspect (do not change the mechanical outcome)

- `N` = 3 sits exactly on the RED boundary (`N < 3` fails only by equality).
- BH2_05778 is the only SOURCE_NAME_OVERLAP query. Without it: N = 2, O_H1 = 2 vs p95 1.0, P = 2,
  and `N < 3` would give RED. D6 as written uses all pilot queries, so it was applied that way.
- `O > null` holds by one query (3 vs p95 2.0).
- H over SUCCESS episodes only is 0.990 (99/100); no rule changes.
