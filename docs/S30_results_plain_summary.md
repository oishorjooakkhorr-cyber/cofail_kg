# CoFail-KG: S30 results in plain words

A plain-language summary of the S30 results (pilot + expansion, 500 questions) and Gate D7.
The numbers come from [pilot_expansion_v1_report.md](../results/reports/pilot_expansion_v1_report.md);
this summary has not recomputed them. The Gate D7 outcome is applied and logged by the researcher.

## What is the experiment?

- We have **4 AI models** (the "agents"). Each one answers medical questions **on its own**. They never talk to each other.
- To answer, each agent walks through a big medical map called **PrimeKG**. It connects genes, diseases and drugs, like a city map connects places with roads.
- A question needs **two steps** on the map. For example: start at a gene, step to a disease, then step to the drugs that treat it.

**The big research question:** when the agents get something wrong, do they all make the **same mistake**? And is the **shape of the map** what pushes them into it?

## What happened in S30

- **Before:** the pilot tested 100 questions.
- **Now:** **400 more questions** were run. Each question went to all 4 agents, so 1,600 answers in total.
- **Result:** every answer finished. The report now covers all **500 questions**.

## Gate D7: the "which road do we take next?" checkpoint

A gate is a set of rules, written **before** seeing the results, that decides what happens next. You look at the numbers and follow the rules. That way nobody can bend the plan after seeing the results.

Here are the four numbers in plain words:

| Number | What it means | Result | What it says |
|---|---|---|---|
| **E** | How often a model crashed or gave a broken answer (a technical problem, not a wrong answer) | 5.4% | Low enough, so the data is usable |
| **N** | Questions where **3 or more agents gave the same wrong answer** | 6 | Too few (the rule needs 15+) |
| **O vs chance** | Is 6 more than you'd get by luck? | Luck alone gives about 5.6 | **No**, 6 is basically what luck gives |
| **C** | Of those shared mistakes, how many have a fair "comparison twin" for a proper experiment? | 0 | None (the rule needs 8+) |

All three result rules point the same way, to **DESCRIPTIVE**. That means "we can **describe** what we saw, but we can't run the big cause-and-effect experiment." The researcher applies the gate and records it in the decision log; the numbers leave no other outcome.

## The six findings

**1. Shared mistakes are rare.**
Out of 500 questions, only 8 had 3+ agents making the same mistake. 2 of those 8 don't count, because an agent was already wrong at the very first step. So **6 count**. Overall the models were right **87–99%** of the time.

**2. It's not more than luck.**
Think of 4 people each picking a wrong item from the **same short menu**. Sometimes they'll pick the same thing just by chance. The agents see the same lists on the map, so they overlap by accident sometimes. Chance predicts about **5.6** overlaps, and we got **6**. So nothing special is happening overall.

**3. All 6 shared mistakes are the same story.**
- **The questions:** every one asks "which drugs **treat** this disease?"
- **What the map has:** two kinds of links between drug and disease:
  - **"Indication":** the drug is officially approved for it.
  - **"Off-label":** doctors sometimes use it, but it isn't officially approved.
- **What the agents did:** they listed **both kinds**, approved plus off-label. The answer key only counts approved ones, so the off-label drugs were marked wrong.
- **So:** the agents aren't really being stupid. They're all reading "treat" broadly in the same way.

| Question | Shared wrong answers |
|---|---|
| BH2_03356 (MYOCD), *pilot* | 21 heart drugs, off-label for atrial fibrillation |
| BH2_05290 (LRAT), *pilot* | 2 diseases, off-label uses of Vitamin A |
| BH2_05778 (Ewing sarcoma), *pilot* | 11 cancer drugs |
| BH2_05890 (lichenoid lesion), **new** | Thalidomide |
| BH2_05997 (facial fat loss), **new** | 2 sulfa drugs |
| BH2_06016 (quotidian fever), **new** | 8 drugs, all 4 agents |

**4. The pattern held on new questions. This is the best finding.**
- **Treat questions:** only 75 of the 500 questions end with a "treat" step, and **all 6** shared mistakes are among those 75. The other 425 questions have **zero**.
- **New questions only:** among the 400 new ones, 3 shared mistakes appeared, and all 3 were "treat" questions.
- **Not luck:** if mistakes landed randomly, that would happen only about **3 times in 1,000**.
- **The catch:** that number is an extra calculation, not part of the official plan, so it counts as "exploratory".

**5. The answer key (BioHopR) has gaps.**
- **By BioHopR's answer list:** 39 questions *look like* shared mistakes.
- **By our own map-based checking:** only 8 really are.
- **So:** about **31** "mistakes" are actually correct answers that BioHopR's answer list misses. 35 of the 39 are one question type (phenotype → disease → drug). That's a separate useful finding: **the benchmark itself is incomplete**.

**6. C = 0: no fair comparison test is possible.**
- **The planned test:** for the cause-and-effect experiment, we'd remove the off-label link from the map (the "treatment") and see if the mistake goes away. We'd also remove a similar link from a **matched twin question** (the "control") to make sure it isn't just any removal causing the change.
- **The problem:** none of the 8 cases has a suitable twin.
- **What's still allowed:** treatment-only tests, without twins. They're weaker, but the protocol (§21) allows them as long as they're reported separately.

## The three hypotheses: scoreboard

| Hypothesis | Plain question | Answer |
|---|---|---|
| **H1** | Do agents make the same mistakes? | Yes, but rarely, and not more than luck |
| **H2** | Is it linked to the map's shape? | Yes. Every case is a "treat" question where the map has an off-label link |
| **H3** | Does the map **cause** it? | Can't be properly tested. At most a few small example tests |

## Honest summary

- ❌ **Big claim, not supported:** "The map makes independent AIs fail together more than chance."
- ✅ **Smaller claim, supported:** "Shared failures are rare. When they happen, it's the 'treat' vs 'approved / off-label' split, and all the AIs handle it the same way." This held on new data.
- ✅ **Separate finding:** the BioHopR answer key misses many correct answers.

## Open question for the researcher

**Was the "treat"/off-label pattern written down as a prediction before S30?** It could be an email to the supervisor, notes, anything with a date.
- **If yes:** finding 4 becomes a **confirmed prediction**. It was guessed in advance and came true, which is very strong evidence.
- **If no:** it is called **"consistent with the pilot"**. Still good, just weaker, because the pattern was noticed after the fact.

## Next steps

1. **Apply Gate D7** using the four numbers above and record the outcome in the decision log (the researcher's decision).
2. **Take the DESCRIPTIVE path:**
   - **S31:** list the cases.
   - **S32–S36:** run up to 5 small "remove the off-label link" tests, treatment-only.
   - **S37:** no scaling up.
   - **S38:** final tables for the thesis.
3. **Optional extras** (both labelled "exploratory", nice to have but not official results):
   - **Strict vs lenient answer key:** re-score with off-label counted as wrong, and again as right.
   - **Small repeat run:** check the results are stable.
