# CoFail-KG — Team update: Stages 4 and 5

**Date:** 13 October 2026
**Branch:** `codex/s4-primekg-complete` (everything below is pushed to GitHub)
**Protocol version now:** v1.3.2 (was v1.2)

---

## The short version

- **S4 is done.** PrimeKG is loaded, checked and frozen. The frozen data was **rebuilt on a second
  computer and came out identical**, so our S4 setup is reproducible.
- **We found a real problem in how BioHopR builds its answer lists** and fixed the rulebook
  (protocol) for it, **before** running the stages it affects.
- **S5 is done.** All 12 relation types passed the field-role check at 100%. The field roles are
  now frozen: `hop2` = the question's starting entity, `hop1` = the bridge, `answer` = the correct
  answers.
- Every rule change was **written down, dated and explained** in `docs/decision_log.md` and
  `docs/CHANGES.md`. Every change was made **before** seeing the results it could affect.

---

## Quick reminder: what a BioHopR question looks like

Each question takes two hops through the knowledge graph:

```
start entity  →  bridge  →  answers
  (hop2)          (hop1)     (answer)
  e.g. a disease → a drug  → that drug's side effects
```

A disease can have **many** drugs, which means many possible bridges. That detail is behind most of
the decisions below.

---

## Decision 1 — Our PrimeKG file is the right one (S4)

**What happened.** The BioHopR paper says the drug Troglitazone has "202 side effects". In our
PrimeKG file it has only 17. That looked like we had the wrong version of PrimeKG.

**What we found.**
- Our `kg.csv` is **byte-for-byte identical** to the only `kg.csv` PrimeKG has ever published
  (MD5 match with the official Dataverse file). Versions 1.0, 2.0 and 2.1 all share this same file.
- The "202" is **not** Troglitazone's own side effects. It's the answer to a 2-hop question: *the
  side effects of all 49 drugs used for type 2 diabetes*. We rebuilt all 202 answers exactly from
  our file.
- **7,370 of the 7,633** BioHopR answer lists can be rebuilt exactly from our file.

**Why this is the right call.** The old check ("Troglitazone should have about 202 side effects")
was testing the wrong number. It would have rejected the correct file. We replaced it with the
publisher's checksum plus the real count (17). This is stronger evidence than any single count.

---

## Decision 2 — We use the `codex/s4-primekg-complete` branch as the official S4

**What happened.** Two versions of the S4 code existed: one on my local `main` and one on this
branch. We chose this branch.

**The check that settles it.** I moved my old data cache aside, which I kept as a backup and didn't
delete, and rebuilt the cache using this branch's code on my own computer. The result's fingerprint
(`bc5d3fd2…2e95`) **matches the frozen fingerprint exactly**. That fingerprint was first made on a
teammate's computer.

**Why this matters.** Two different computers produced the exact same frozen data. That's direct
proof that S4 is reproducible, which is something examiners look for.

**Nothing was lost:** my old S4 work (`051d5da`) is still on my local `main`. It was never pushed
and never merged.

---

## Decision 3 — Answer construction: option C (protocol v1.3)

**The problem.** We assumed BioHopR's answer list is always *"the answers reached through the one
stored bridge"*. In S4 we found that this is **not true for every relation type**:

| How BioHopR built the answer list | Name we use | Where it happens |
|---|---|---|
| Only the answers from the **stored bridge** | **BRIDGE** | Most relation types |
| The answers from **all valid bridges combined** | **UNION** | Mainly `disease:drug:effect/phenotype` (611 rows) |

The old rulebook only knew BRIDGE. So it would have marked **64%** of that one relation type as
"broken", even though those rows are perfectly fine.

**The three options we considered** (the numbers are S4 estimates from 30-row samples):

| Option | Idea | Main problem |
|---|---|---|
| A | Keep BRIDGE everywhere | That type mostly fails; only about 73 multi-bridge queries remain, which is too few for the study |
| B | Use UNION everywhere | Another type (`effect/phenotype:disease:drug`) drops to 87% and fails; one of our answer labels (`ALT_VALID`) disappears |
| **C** ✅ | **Each relation type uses whichever construction matches its data** | Results must be reported split by construction, which we now do |

**What option C does, in plain words.** At S6, each relation type is scored both ways. Whichever
way reaches the 90% bar is used for that type. If **both** reach 90%, we use **BRIDGE**. If neither
does, the type fails, as before.

**Why option C is the strongest choice.**
- **It follows the data instead of forcing one assumption onto all 12 types.** The S4 analysis shows
  that BioHopR genuinely mixes the two constructions.
- **More relation types survive, and the multi-bridge pool grows** from about 73 queries to about
  700 queries across three types. Multi-bridge questions are central to our co-failure research
  question.
- **The tie rule was fixed before any S6 result exists.** Nobody can say we picked the
  construction that gave nicer numbers.
- **It stays transparent:** every result is reported overall **and** split by construction.

---

## Decision 4 — A clear definition of "supports the field roles" (protocol v1.3.1)

**The problem.** S5 checks that the BioHopR fields mean what we think. The old rule effectively
asked: *"Are the answers neighbours of the stored bridge?"* For UNION rows, many correct answers
come through **other** bridges, so the old rule would have failed rows whose roles are actually
correct, and S5 would have stopped.

**The fix.** A sampled row now **supports** the roles if all three of these hold:
1. the start entity and the bridge are connected in PrimeKG;
2. at least one answer is reached through the stored bridge;
3. **every** answer is reached through the stored bridge **or** another bridge of the start entity.

A row only counts if at least half of its answer names (and at least one) can be found in PrimeKG.
That way, a row with mostly unfindable answers can't pass on weak evidence.

**How we made sure this was fair.**
- Before writing the rule, we tested the idea on **different rows** (positions 6–10 per type).
  The real S5 sample (positions 1–5) stayed **unseen** until S5 ran.
- The 5-row sample, the ordering and the **95% threshold were not changed**.
- A reviewer's critique of the first draft was taken on board: we added the "at least half"
  safeguard and dropped an overclaim.

---

## Decision 5 — One tiny failing type shouldn't stop the whole study (protocol v1.3.2)

**The problem.** The old rule said S5 stops if **any** relation type fails. One type
(`drug:effect/phenotype:disease`) has only **5 rows** in the whole dataset, which is 0.07% of the
data. Those 5 rows could have halted all 12 types.

**The fix.**
- **One** failing type covering **≤ 1%** of rows is **excluded** and logged, and S5 continues.
- S5 still **stops** if more than one type fails, or if the failing types cover more than 1% of the
  rows. A real problem with the field roles will still stop us.
- Gate D1 in `docs/decision_rules.md` was updated to match. A type that fails S5 **can't be
  re-admitted later**, because that would mean changing our minds after seeing the results.

**Why this is the right call.** It matches how Gate D1 already treats failing types (one at a
time), it keeps a strong safety stop, and it was decided **before** S5 ran.

---

## S5 result — the field roles are confirmed

| What we checked | Result |
|---|---|
| Relation types passing | **12 / 12, all at 100%** |
| Rows sampled | 60 (5 per type); 59 usable. 1 row's only answer couldn't be found in PrimeKG |
| Failing types | **0**, so nothing excluded |
| Hand-checks with the inspection tool | 3 rows checked by hand, all agree (29/29, 44/44 and 33/33 answers found) |

**This is strong evidence for Decision 4.** **5 of the 60 rows passed only because of the new
definition**: their answers come partly through other bridges. Under the old wording, **two
relation types would have failed, and S5 would have stopped the study.** We made the decision before
seeing those rows. The rule change wasn't a convenience; without it, a correct dataset would have
been rejected.

---

## How we kept this scientifically honest

- **Every rule was decided before its results existed.** Option C before S6, the S5 definitions
  before S5.
- **Everything we had looked at is disclosed.** Each decision-log entry has a "Data seen before
  deciding" line, including the exploratory preview.
- **Thresholds were never loosened.** The 95% (S5) and 90% (D1) bars are unchanged.
- **Every change is traceable:** dated entries in `docs/decision_log.md`, a summary in
  `docs/CHANGES.md`, and one commit per change on GitHub.
- **Results record exactly which code made them.** The S5 results point to commit `5ae77f6`.

---

## What changed in the repository

| Commit | What it is |
|---|---|
| `b48952f` | Protocol v1.3: answer construction option C |
| `48b47cb` | Protocol v1.3.1: field-role "support" definition, plus the exploratory preview script and results |
| `edc9b3e` | Protocol v1.3.2: field-role failure handling, plus the Gate D1 update in `decision_rules.md` |
| `5ae77f6` | S5 code (field-role check and its 20 tests) |
| `ea4b980` | S5 results and the frozen field roles |

All tests pass (74). No force-pushes. `main` was not touched.

**Please pull the branch** and read `docs/CHANGES.md` for the three protocol amendments.

---

## Still open, before S6

1. **The " (disease)" name suffix.** Some BioHopR answers (for example "insomnia") match PrimeKG
   only as "insomnia **(disease)**". Under the current name-matching rule, these stay unmatched, and
   their rows count as "not matching" in the S6 score. This could unfairly push a type below 90%.
   **Next step:** count how many rows this affects per type, then decide on a fix **before** S6,
   as we did above.
2. **Runbook S6/S7 steps** still describe only BRIDGE answers. They need a small update to match
   option C.
3. **Graphify graph** (`graphify-out/`) was made before v1.3, so it needs regenerating.
4. **Label set for `disease:effect/phenotype:drug`:** two earlier checks disagree. This will most
   likely be settled automatically at S6, which tries every label combination.

Questions or concerns? Please raise them **before S6 starts**. That's the point where changing a
rule is still clean.
