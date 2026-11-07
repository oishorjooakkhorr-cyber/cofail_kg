# S24 — Chance baselines (protocol §17)

Date: 2026-11-07. Stage prompt: runbook S24. Not committed at the time of writing.

## 1. Files created or changed

| File | What |
|---|---|
| `src/cofail_kg/evaluation/null_models.py` (new) | §17 nulls N1, N1-H1, N2: pools, observed sets, simulation, per-query probabilities, aggregates (3- and 4-agent) |
| `tests/test_null_models.py` (new) | 11 tests on synthetic episodes |
| `scripts/24_null_models_s21r2.py` (new) | Offline example on the accepted S22 run `smoke_single_s21r2` |
| `results/diagnostics/s24/smoke_single_s21r2_nulls.json` (new, write-once) | Example output |
| `results/diagnostics/s24/smoke_single_s21r2-console.txt` (new) | Example console output |
| `docs/S24_null_models_report.md` (new) | This report |

No existing source file was changed, so the pinned S22 sources (and `22_smoke_single_s21r2.py report`)
are unaffected.

## 2. Tests

- `tests/test_null_models.py`: **11 passed**.
  - REQUIRED: all four agents give the same single wrong answer; each pool has 200 other wrong Type_T
    candidates (201 in all) → N1 CF3 and CF4 null probabilities < 0.01.
  - Tiny pools (one shared entity, answered by all) → probability 1 for N1, N1-H1 and N2, CF3 and CF4.
  - Pools and observed sets follow the §17 table on a hand-built episode (T_q member, `s`, a page-2-only
    entity, a non-R1 route, an unreachable entity, a never-appeared answer, a GOLD answer); each observed
    set ⊆ its pool.
  - Determinism: same inputs → identical output; queries and agents shuffled → identical output.
  - Aggregate: hand-checkable two-query case (mean, median, 95th percentile, p, "exceeds").
  - Extra: seed scheme equals `SeedSequence([42, h, v])`; draws follow ascending agent order on one
    stream (reproduced by hand); H1 disagreeing with the S19 row is rejected; a failed episode gives empty
    observed sets and is reported; the aggregate excluding technical failures; panel/agent mismatch rejected.
- Full suite: **716 passed, 2 skipped** (the 2 skips need BioHopR, which is not downloaded). Run with
  `--basetemp` in the session scratch folder, because this sandbox denies the default pytest temp folder.

## 3. Real example: `smoke_single_s21r2`, 20 screening queries, 10,000 trials (4.6 s)

| Null | Version | Queries | Observed | Null mean | Median | 95th pct | p | Exceeds |
|---|---|---:|---:|---:|---:|---:|---:|---|
| N1 | CF3 | 20 | 0 | 0 | 0 | 0 | 1.0 | no |
| N1-H1 | CF3 | 20 | 0 | 0 | 0 | 0 | 1.0 | no |
| N2 | CF3 | 20 | 0 | 0 | 0 | 0 | 1.0 | no |

The CF4 rows and the 17-query aggregate without technical-failure queries (BH2_02033, BH2_03953, BH2_04425)
are identical: all zero, p = 1.

Why everything is zero: only Granite41-8B and Ministral3-14B have non-empty observed sets `W'`
(Granite: BH2_03762 1, BH2_05366 30, BH2_06427 25; Ministral: BH2_05366 11). On no query do three or
more agents have a non-empty observed set, so no share is possible in the data or in the null. Cross-checks:
Gemma4-12B's 24 OFF_QUESTION answers are all UNGROUNDED (never appeared), so they are not in `W'`;
Granite's 74 OFF_QUESTION answers minus its 18 WRONG_TARGET_TYPE answers (not Type_T) = 56 = 1 + 30 + 25.
Every N1-H1 observed set is empty (all wrong answers are SHORTCUTs with H1 = 0). This agrees with S23
(question-level CF3 = 0).

## 4. Assumptions

1. **"Ascending agent order"** = the frozen agent order in `configs/pilot.yaml` (Gemma4-12B,
   Granite41-8B, Ministral3-14B, Cogito-14B), i.e. ascending agent index i, as in S23. Not alphabetical.
2. **H1 for pool entities** (needed for the N1-H1 pool) uses the §14.3 definition directly on the trace
   graph, with the same reachability rule as S19's `label_paths` (simple path, no length cap, no return
   through `s`). For every observed entity it is checked against the stored S19 `h1`; a disagreement stops
   the run.
3. **"Page 1"** = a successful `get_neighbors` result whose `page` is 1 (tool pages start at 1).
4. **Entity type** comes from the PrimeKG cache (`kg.get_node(x)["type"]`), the same source S19 uses.
5. The 3-agent and 4-agent versions use the same draws. Both use the same seeds, so running them separately
   would produce the same draws anyway.

## 5. Design choices beyond the specification

| Choice | Class |
|---|---|
| Inputs: S12 episode record (raw `call_log`) + S19 metrics row per (query, agent), S7 reference row, mapping, node-type lookup | routine engineering |
| H1 of non-answer pool entities recomputed from the trace graph, cross-checked against S19 for answers (assumption 2) | routine engineering |
| An agent with an empty observed set makes no `choice` call (draws nothing, uses no random numbers); a query where fewer than 3 agents draw skips simulation (result is necessarily 0) | routine engineering |
| 95th percentile = `numpy.percentile(totals, 95)`, NumPy's default linear interpolation | routine engineering — **see question 1** |
| Queries with a technical failure kept in every total, plus a second aggregate excluding them (extends the 2026-11-07 §16 decision to §17) | routine engineering — **see question 2** |
| `p` uses `≥` and the `(1 + count) / (1 + trials)` form exactly as §17 states | specified; Monte Carlo p-value with +1 correction is a possible literature method |
| Sanity checks that stop the run: record/row/reference mismatch, OFF_QUESTION answer inside `T_q`, observed ⊄ pool, wrong panel | routine engineering |
| Output sorted by query_id; IDs ordered numerically | routine engineering |

## 6. Inspect by hand / questions for the researcher

1. **95th-percentile method.** §17 says "above that null's 95th percentile" but does not fix the
   percentile definition. Null totals are integers, so the method can matter exactly at the boundary
   (e.g. linear interpolation can give 2.3 where "nearest rank" gives 3), and "observed exceeds null"
   feeds D6/D7. The code uses NumPy's default (linear). **Confirm, or name another definition.**
2. **Technical failures in §17.** I applied your §16 decision (keep all queries, report separately) to the
   nulls too. **Confirm that this also holds for §17**, and which aggregate D6/D7 should use (all queries,
   presumably).
3. Look at `results/diagnostics/s24/smoke_single_s21r2_nulls.json` for BH2_05366 (Granite pool 30,
   Ministral pool 30, observed 30 and 11): the only query where two agents have non-empty observed sets.
