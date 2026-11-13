# PW — Population-weighted co-failure rate (EXPLORATORY, descriptive)

EXPLORATORY (protocol §20) — docs/decision_log.md, entry 2026-11-14 "PW — Population-weighted co-failure rate" (rule fixed before computing). Descriptive: no threshold, no outcome.

Produced by `scripts/49_weighted_rate.py` at commit `b78255dbbaf7f76bc158b356e53d13f01d953d6c` (tracked files clean: True). Inputs (SHA256): `data/processed/manifests/expansion.jsonl` `2cfc09e132e77f5a4c9eeb3b4957692051f7c9fc32cc97ecd0cd37de0e602689`, `data/processed/manifests/pilot.jsonl` `102a1cb1133ae7ea3bf36972965101c3842b26b231739363b53e7250714a28d4`, `data/processed/primary_population.csv` `24a876a1bcca9e4e4fc5d273460212b47e38d95b0949c1770096fb46b79b41b8`, `results/combined/pilot_expansion_v1/cofailure.json` `198b9aa18770d1a815429361be8f79601330276642665feb025783dd5560f87d`.

Population: the primary population (7,176 queries, protocol §7.2), not all of BioHopR. Strata: relation type × bridge multiplicity (§8). Sample: the 500 queries of record, all queries (§19.1).

Correction (decision log 2026-11-14 "PW — Correction"): the median of the same Monte Carlo draws is added as the summary that matches the interval. The plug-in estimate and the interval are unchanged from the logged run (results/exploratory/pw/, commit 8fdd8e3).

## Rates

| Metric | Sample | Sample rate (Wilson 95%) | Weighted: plug-in | Weighted: median (95% interval) |
|---|---|---|---|---|
| CF3^Q | 8/500 | 1.60% (0.81%–3.13%) | 3.29% | 5.59% (2.92%–9.35%) |
| CF3^{Q,H1} (primary) | 6/500 | 1.20% (0.55%–2.59%) | 2.17% | 4.59% (2.14%–8.22%) |
| CF4^Q | 2/500 | 0.40% (0.11%–1.45%) | 0.69% | 3.23% (1.27%–6.44%) |

Weighted median and interval: Monte Carlo, 100,000 draws of Σ_h (N_h/N)·θ_h with θ_h ~ Beta(y_h+½, n_h−y_h+½) per stratum (Jeffreys), seed 42. The plug-in adds nothing for strata with no event; every draw adds a positive amount for them, so the median and the interval sit above the plug-in. The width comes mostly from thinly sampled large strata, not from observed failures.

## Strata

| Relation type | Multiplicity | N_h (population) | n_h (sample) | Weight N_h/N | y_h CF3^Q | y_h CF3^{Q,H1} | y_h CF4^Q |
|---|---|---|---|---|---|---|---|
| disease:drug:effect/phenotype | MULTI_BRIDGE | 528 | 329 | 0.0736 | 0 | 0 | 0 |
| disease:drug:effect/phenotype | SINGLE_BRIDGE | 319 | 7 | 0.0445 | 0 | 0 | 0 |
| disease:drug:gene/protein | SINGLE_BRIDGE | 376 | 8 | 0.0524 | 0 | 0 | 0 |
| disease:gene/protein:drug | SINGLE_BRIDGE | 852 | 16 | 0.1187 | 0 | 0 | 0 |
| drug:disease:effect/phenotype | SINGLE_BRIDGE | 213 | 6 | 0.0297 | 0 | 0 | 0 |
| drug:disease:gene/protein | SINGLE_BRIDGE | 321 | 8 | 0.0447 | 2 | 0 | 0 |
| drug:gene/protein:disease | SINGLE_BRIDGE | 3028 | 51 | 0.4220 | 0 | 0 | 0 |
| effect/phenotype:disease:drug | MULTI_BRIDGE | 73 | 46 | 0.0102 | 3 | 3 | 1 |
| effect/phenotype:disease:drug | SINGLE_BRIDGE | 430 | 9 | 0.0599 | 1 | 1 | 1 |
| gene/protein:disease:drug | SINGLE_BRIDGE | 577 | 11 | 0.0804 | 1 | 1 | 0 |
| gene/protein:drug:disease | SINGLE_BRIDGE | 459 | 9 | 0.0640 | 1 | 1 | 0 |

Limits (logged with the rule): stratum rates rest on 6 to 51 sampled queries in 10 of 11 strata; most strata have no event; the interval is wide where strata are thin and large.
