# Results chapter — working outline (draft)

Draft for the researcher. Every number comes from `results/reports/final/` (S38, tables produced at
commit `d6a0013`, committed as `9af1529`) or from the decision log. Check each number against its table
before it goes into the thesis text.

---

## 0. How the chapter is labelled

Every section carries one of three labels. State them once at the start of the chapter, and put the
label in each section heading.

| Label | Meaning | Sections |
|---|---|---|
| **Pre-registered** | Hypotheses (protocol §1), metrics, chance baselines and Gate D7 were fixed before the data | R3, the H1/H2 parts of R4, R8's design |
| **Exploratory** | Chosen after seeing pilot or S30 results; each rule logged before its own output existed (protocol §20) | R4 (B5), R5 (B2, B6), R6 (B1, IC), R7 (RP), R9 |
| **Illustrative** | 5 treatment-only cases, no matched control (D7 DESCRIPTIVE, C = 0) | R8 |

Suggested opening paragraph: what was run (500 questions × 4 agents = 2,000 episodes), what the gate
said (D7 DESCRIPTIVE), and that everything after R3 is exploratory or illustrative.

---

## Chapter flow

| Section | Question it answers | Tables | Hypothesis |
|---|---|---|---|
| R1 | What data and sample? | 1 | — |
| R2 | How did the agents behave? | 2 | — |
| R3 | Do agents fail together more than chance? | 3 | **H1** |
| R4 | Where do the shared failures occur? | 3e, 4, 8 | **H2** |
| R5 | How much does the answer key matter? | 7, 9 | — |
| R6 | Why do they occur: shared habit or each model's own rate? | 6, 12 | **H4** |
| R7 | Are the results stable on a rerun? | 10 | — |
| R8 | What happens when the shared feature is hidden? | 5 | **H3** (illustrative) |
| R9 | The pre-registered follow-up that was not run | 11 | H4 (untested part) |
| R10 | Summary of hypotheses | — | all |

---

## R1. Dataset and sample (Table 1) — descriptive

**Purpose:** show where the 500 questions come from.

**Key numbers (Table 1a, 1c, 1d)**
- BioHopR 2-hop rows: 7,633 in 12 relation types; 9 types pass Gate D1, 3 fail.
- Queries validated: 7,377; CONSISTENT 7,362; INCONSISTENT 15 (all `GOLD_MISSING_FROM_KG`).
- LEAKY_QUESTION: 186. SATURATED: 0. Primary population: **7,176**.
- Sample: pilot 100 + expansion 400 = 500 (§8 quotas: 125 SINGLE_BRIDGE, 375 MULTI_BRIDGE).
- The sample over-represents MULTI_BRIDGE questions (75% of the sample, 8% of the population) and
  under-represents `drug:gene/protein:disease` (51 of 500 sampled, 3,028 of 7,176 in the population).

**Main text:** Table 1a (relation types). **Appendix:** 1b–1g.

**Say:** the sample follows the §8 quotas, so rates describe the sample, not the population; the
population-weighted rate is in R3 (PW).
**Don't say:** "x% of BioHopR questions lead to shared failure" (the sample is not population-weighted).

---

## R2. Agent behaviour (Table 2) — descriptive

**Purpose:** the four agents are competent enough for co-failure to be meaningful.

**Key numbers (Tables 2a, 2b, 2f; S30 report Table 1–2)**
- Episodes: 2,000; technical failures E = 108 (5.4%): Gemma 2, Granite 14, Ministral 54, Cogito 38.
- R1 found by ≥ 3 of 4 agents on 99.2% of questions (H = 0.992).
- Question-valid precision (mean per episode): Gemma 0.994, Granite 0.866, Ministral 0.966, Cogito 0.960.
- Benchmark F1 (mean): Gemma 0.747, Granite 0.620, Ministral 0.771, Cogito 0.647.
- Error styles differ (Table 4b): Granite mostly SHORTCUT (702 answers) and WRONG_HOP_COUNT (350);
  Ministral mostly WRONG_RELATION_HOP1 (176); Cogito SHORTCUT (179) and WRONG_RELATION_HOP2 (157);
  Gemma few errors (77 + 31).

**Main text:** one compact per-agent table (status, precision, F1, hop-1 status). **Appendix:** the
split tables (Table 2 is long: 7 splits × 4 agents; show only the "All" rows in the main text).

**Say:** agents are mostly correct and fail in different ways.

---

## R3. Co-failure against chance (Table 3) — **pre-registered, H1**

**Purpose:** the main result.

**Key numbers (Tables 3a, 3d; decision log 2026-11-12 "Gate D7")**
- Shared failures (≥ 3 agents share a question-invalid answer): CF3^Q = **8 / 500 (1.6%)**;
  all 4 agents: CF4^Q = 2.
- Gate-counting version (hop-1-clean): CF3^{Q,H1} = N = **6 (1.2%)**.
- Chance baseline N1-H1 (each agent draws from what it actually saw): observed 6, null mean 5.62,
  p95 6.0, **p = 0.644 → not above chance.** N1 (8 vs 7.62, p = 0.641) and N2 (8 vs 7.61, p = 0.635)
  agree.
- Pilot vs full sample: in the pilot alone, O_H1 = 3 was above chance (p95 2.0, p = 0.011; Gate D6
  YELLOW). At 500 questions it is not.
- Gate D7: E 0.054, N 6, not above chance, P 3, C 0 → **DESCRIPTIVE**.
- Pairwise agreement (Table 3c), when both agents are wrong: Ministral–Cogito 17/18, Granite–Ministral
  14/19, Granite–Cogito 12/22; Gemma pairs have tiny denominators (3–6).
- Without SOURCE_NAME_OVERLAP questions: 7, 5, same conclusions.

**Interval and population rate (PW, exploratory; decision log 2026-11-14, two entries):**
- Sample rate 1.2% (6/500), Wilson 95% interval 0.55%–2.59%.
- Weighted to the primary population (7,176): plug-in **2.2%**; median of the Jeffreys draws 4.6%,
  95% interval 2.1%–8.2%. The median and the upper end are pushed up by the prior in strata with no
  event and only 6–16 sampled questions; the data themselves point to about 2%.
- Say: "about 2% in the population; the data cannot rule out a few percent more, because several large
  question types were sampled thinly." Don't present 4.6% as the estimate.

**Suggested figure:** observed total against the N1-H1 null distribution, if the stored null totals
allow it.

**Say:** H1 is not supported. Shared failure is rare and no more frequent than what each agent saw
already explains. The pilot signal did not hold at 500.
**Don't say:** "agents never fail together" or "the graph has no effect".

---

## R4. Where shared failures occur (Tables 3e, 4, 8) — **H2 pre-registered (descriptive); B5 exploratory**

**Purpose:** structure behind the few shared failures.

**Key numbers**
- All 8 flagged questions are BRIDGE construction (8/164; UNION 0/336). By ambiguity tag:
  BOTH 4/61, R2 2/20, R1 2/352, NONE 0/67 (Table 3e).
- Mechanisms (Table 4d): 6 WRONG_TURN_HOP2 (all the label `off-label use`), 2 SHORTCUT
  (`drug_protein`). No off-path-node events (PCF_NODE = 0).
- All 168 shared wrong agent-answers were first seen on page 1 (S30 report Table 6b); the ordering
  flag is not set.
- **B5 (Table 8):** all 6 gate-counting shared failures are in the 75 "treat-final" questions
  (R2 = indication); 0 in the other 425. Pilot 3/16, expansion 3/59. Probability that the expansion's
  3 all land in its 59 treat-final questions by chance: **0.0031** (0.0028 without SOURCE_NAME_OVERLAP).
- Ambiguity flag set: 6/6 in ambiguous types.

**Main text:** a small table (group × pilot/expansion × shared failures) from Table 8.

**Say:** shared failures sit on one feature, the off-label branch at the final "treat" step, and this
pattern repeated in new questions. H2 is half supported: identifiable feature yes, but it is relation
ambiguity.
**Don't say:** "predicted" (no prediction was written before the expansion analysis; it is a
replication of a pattern seen in the pilot, whose report was committed before the expansion ran).

---

## R5. The answer key (Tables 7, 9) — exploratory

**Purpose:** how much the measured co-failure depends on what counts as wrong.

**Key numbers**
- **B6 (Table 9):** CF3^BH (BioHopR's own answer lists) = **39**; CF3^Q (strict graph key) = **8**;
  31 benchmark-only questions, all `effect/phenotype:disease:drug`.
- Hand-check of 15 benchmark-only cases: 10 VALID, 5 QUESTIONABLE, 0 NOT_VALID → NOT CLEAN
  (rule: ≥ 12 VALID). Sources gathered and marks proposed by Claude Code; every final mark set by the
  researcher, who changed 1 of 15.
- **B2 (Table 7):** lenient key (off-label accepted wherever indication is): CF3^Q 8 → **2**
  (the 2 shortcut cases); CF3^{Q,H1} 6 → **0**. Precision rises for every agent (for example Cogito
  0.960 → 0.983).
- Contraindication answers (wrong under either key): Granite 34 answers in 8 questions, Cogito 21 in 4,
  Ministral 1, Gemma 0. Never shared by 3 agents.

**Suggested figure:** a three-bar "39 → 8 → 2" chart (benchmark, strict, lenient).

**Say:** the same runs give 39, 8 or 2 shared failures depending on the key. Most benchmark-only
failures checked were valid answers missing from BioHopR's lists.
**Don't say:** "BioHopR is wrong" (15 cases, 5 questionable, outcome NOT CLEAN). Off-label as
"treat" is a judgment call; present both keys.

---

## R6. Mechanism: each model's own rate (Tables 6, 12) — exploratory, **H4**

**Purpose:** are shared failures a shared habit or coincidence of individual habits?

**Key numbers**
- **B1 (Table 6),** treat-final questions, when an off-label list was available:
  | Agent | Took it | Opened it | Kept it once opened |
  |---|---|---|---|
  | Gemma | 6/35 (17%) | 6/35 | 6/6 |
  | Granite | 8/28 (29%) | 11/28 | 8/11 |
  | Ministral | 18/30 (60%) | 19/30 | 18/19 |
  | Cogito | 25/33 (76%) | 29/33 | 25/29 |
  Outcome NOT CLEAN (2 of 4 agents ≥ 0.50). At the first step ("treat-first"), uptake ≤ 2.4% for
  every agent.
- **IC (Table 12):** questions where ≥ 3 agents took the off-label route: **6 observed, 5.51 expected**
  under independence (95% range 2–10), P(≥ 6) = 0.482 → **AGREES**. These 6 are exactly the 6
  gate-counting shared failures. Pairs taking together: 40 vs 32.1 expected (descriptive only).

**Suggested figure:** per-model uptake bars with counts.

**Say:** the decision point is whether to open the off-label list; once opened, models keep it. Each
model has its own rate, and those rates alone explain how often three of them coincide. H4: "where"
supported; "all agents resolve it the same way" not supported.
**Limit to state:** rates estimated from the same episodes; pairs slightly above expectation may
reflect some questions being more tempting.

---

## R7. Reliability (Table 10) — exploratory

**Purpose:** are the shared failures stable?

**Key numbers**
- Rerun of the 8 flagged questions (32 episodes): **28 of 32** agent answer sets identical.
- Shared failure reproduced in **5 of 8** (logged expectation ≥ 6: **not met**).
- The 3 that did not reproduce each lost one agent: a parse failure (BH2_03356, Ministral), a
  different answer set (BH2_04856, Ministral), dropped off-label answers (BH2_05890, Cogito).

**Say:** models are mostly repeatable at temperature 0, but a shared failure resting on exactly 3
agents flips when one varies; this fits R6.

---

## R8. Illustrative interventions (Table 5) — illustrative, **H3 not testable**

**Purpose:** what happens when the shared feature is hidden.

**Key numbers**
- No matched control for any case (C = 0), so H3 cannot be tested; 5 treatment-only cases.
- Shared failure 1 → 0 in **5 of 5** cases.
- Holders giving only valid answers afterwards: **14 of 15** (1 OTHER_WRONG: Granite, shortcut case).
  2 Ministral parse failures excluded.
- No agent moved to another wrong list (SAME_WRONG_RELATION_OTHER_NEIGHBOR = 0); valid answers kept
  (for example 24 → 24 on BH2_06016); no-answer rate 0 before and after.
- Shortcut case BH2_04650: 0 valid answers before, 13 after for two agents.
- Repeat-run reference: without surgery, the same holders failed again.
- Surgery check (S34/S35): 0 tool-output differences not explained by the overlay.

**Suggested figure:** one case diagram (BH2_03356: MYOCD → atrial fibrillation → indication vs
off-label drugs).

**Say:** illustrations only. For the 4 off-label cases, removing the wrong answers is partly by
construction; the informative outcomes are no displacement and the shortcut case.
**Don't say:** "causes", "proves", "reduces co-failure" in general.

---

## R9. Pre-registered follow-up not run (Table 11) — exploratory

**Purpose:** report what was planned and why it did not run.

- Predictions P1 and P2 (quoted verbatim in Table 11) were logged and pushed on 2026-11-12, before any
  follow-up data.
- The stop rule (B1 must be CLEAN) gave NOT CLEAN, so the follow-up was not run (decision log
  2026-11-13). P1 and P2 are untested.

**Say:** this in two or three sentences; it shows the stop rule was followed.

---

## R10. Summary of hypotheses

| Hypothesis | Status | Evidence |
|---|---|---|
| H1: shared failures above chance | Not supported | R3 |
| H2: concentrated on structural features, not only ambiguity | Partly: one feature, but it is relation ambiguity | R4 |
| H3: removing the feature beats a matched control | Not testable (C = 0); 5 illustrative cases | R8 |
| H4 (exploratory): verb coarser than graph labels; agents resolve it the same way | Location supported; "same way" not supported | R4, R5, R6 |

One-sentence result: independent agents on the same graph rarely fail together; when they do, it is
because they saw the same tempting list, not because they are linked, and the answer key largely
decides how much shared failure is measured.

---

## Open items before writing the final text

1. **Interval for the co-failure rate:** done (PW, see R3).
2. **Teammate's log items:** the "full_v1 stopped" line, who asked for S39, and whether anyone opened
   its results. Needed for an honest methods section (full_v1 is not used anywhere in these results).
3. **Reproducibility note:** pilot_v1 and expansion_v1 re-analyse only at their pinned commit
   (`b8209e6`); later code changes (S32 overlay, new hash entries) make the runner refuse at HEAD.
4. **Sample vs population:** state that rates describe the quota sample (R1).
5. **Off-label judgment:** present strict and lenient keys side by side; do not choose one silently.
6. **Exploratory analyses chosen after the pilot:** B1, B2, B5, B6, RP, IC and the S36 readings are
   exploratory; say so in each heading.
