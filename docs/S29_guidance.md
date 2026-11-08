# S29 — What is left to do, step by step

Status on 2026-11-08: the mechanical D6 check is done (outcome **YELLOW**). The four steps below
are yours. Claude Code has not done any of them and does not edit the protocol, decision rules or
decision log unless you ask it to in that message.

Order matters: **check → freeze §21 → log → commit.** Do all of it before starting S30.

---

## Step 1 — Recompute D6 yourself (about 5 minutes)

Open `results/reports/pilot_v1_report.md`, section **"D6 quantities"** (near line 654), and
`docs/decision_rules.md`, section **D6** (line 119).

Check each number against its source table in the report:

| Quantity | Report value | Where to cross-check it in the report |
|---|---|---|
| `E` | 0.0425 (17/400) | Table 1, "All" row: 17 technical failures / 400 episodes |
| `H` | 1.000 (100/100) | Only given in the D6 section (SUCCESS-only value 0.990 is for inspection only) |
| `N` | 3 | Table 3, row CF3^{Q,H1}, "All queries" column: 3/100 |
| `O > null` | yes | Table 4, "All queries", row N1-H1 / ≥ 3 agents: observed 3 > p95 2.0 |
| `P` | 3 | Table 5, "By relation type — all queries", CF3^{Q,H1} column: three rows have a 1 |

Then apply the rules in order. Write each one down:

1. HOLD if `E > 0.15` → 0.0425: **no**
2. RED if `H < 0.20` or `N < 3` or not `O > null` → no / no (3 is not < 3) / no: **no**
3. GREEN if `H ≥ 0.40` and `N ≥ 10` and `O > null` and `P ≥ 3` → `N ≥ 10` fails: **no**
4. YELLOW otherwise: **yes**

Flags:
- Ordering flag: O_N1 above p95 = yes, O_N2 above p95 = yes → **not set** (Table 4).
- Ambiguity flag: 3 of 3 N queries are R2_AMBIGUOUS or BOTH_AMBIGUOUS → **set** (case sheets,
  Table 7).

**Your call before moving on:** D6 is computed on all pilot queries. Without the one
SOURCE_NAME_OVERLAP query (BH2_05778), N would be 2 → RED. D6 as written does not exclude it.
Decide whether you accept YELLOW as written, and note your reasoning in Step 3. If you decide
anything other than "D6 as written", that is a change to a frozen rule and needs its own
decision-log entry (protocol §20).

---

## Step 2 — Freeze protocol §21 (the scientific step)

File: `docs/frozen_pilot_protocol.md`, **§21 "Phase 2 — intervention design"** (line 791).

According to `docs/progress.md` (line 670), the S29 freeze covers two things: the **mechanism
list** and the **control tie-break**. Read §21 line by line and decide each bullet.

### 2a. What the pilot showed (facts to read before deciding)

Shared events (≥ 3 agents) from Table 3, all queries:

| §21 mechanism | Matching pilot indicator | Pilot count |
|---|---|---|
| `WRONG_TURN_HOP2` | PCF_REL3 (all three case-sheet paths: WRONG_RELATION_HOP2, `off-label use` instead of `indication`) | 3 queries (BH2_03356, BH2_05290, BH2_05778) |
| `WRONG_TURN_HOP1` | PCF_REL3 at step 1 | 0 shared |
| `SHORTCUT` | PCF_SHORTCUT3 | 0 |
| `OFF_PATH_NODE` | PCF_NODE3 | 0 |

Not shared but present per agent (Table 2d, primary paths): SHORTCUT (Granite41-8B 70,
Ministral3-14B 4), WRONG_RELATION_HOP1 (Gemma4-12B 77, Ministral3-14B 114), WRONG_TARGET_TYPE
and WRONG_HOP_COUNT (Granite41-8B only).

Other facts that may matter for the candidate and control rules:
- Every shared wrong answer was first seen on page 1 (Table 6b).
- Shared paths: BH2_03356 via `atrial fibrillation` (21 off-label drugs, one list of size 21);
  BH2_05290 via `Vitamin A` (list size 2); BH2_05778 via the `Ewing sarcoma` disease node (list size 11).
- BH2_05778 is the SOURCE_NAME_OVERLAP query.

### 2b. Decisions to make and write into §21

Go through each bullet and either keep it or rewrite it:

1. **Mechanisms.** Keep all four, or narrow the list to what occurred? (Pilot: only
   WRONG_TURN_HOP2 was shared.) Remember: the expansion run (S30) may show mechanisms the pilot did not.
2. **Candidate rule.** Keep "CF3^{Q,H1} = 1, or a PCF event shared by ≥ 3 agents", or change it?
   Should SOURCE_NAME_OVERLAP queries be eligible?
3. **Surgery.** For a hop-2 wrong turn, which surgery: hide specific edges `(u, r, v)`, or hide
   label `r` at node `u`? For BH2_03356 the label `off-label use` at `atrial fibrillation` covers
   all 21 shared answers; decide whether that is the intended granularity.
4. **Matched control tie-break.** §21 says "degree (or branch degree) within ±25% (else nearest)".
   It does not say what to do when **several** controls qualify, or two are equally near. Write
   the rule (for example: smallest absolute degree difference, then lowest node index). This is
   the tie-break the progress file says must be fixed now.
5. **Outcomes and effect.** Confirm or edit.
6. **Fan-out sentence.** Keep "analyzed descriptively, not an intervention mechanism", or change it.

### 2c. Edit the file

1. In the heading, change `[PROVISIONAL]` to `[FROZEN]` and add the date, e.g.
   `## 21. Phase 2 — intervention design `[FROZEN]` at S29 (2026-11-08, after seeing pilot data)`.
2. Rewrite the bullets according to 2b.
3. In §0.1 (line 21), the `[PROVISIONAL]` row can stay (it explains the tag) or be updated to say
   §21 is now frozen; your choice.
4. Decide whether this is a version change. Earlier tag-only freezes (S2, S5, S26) kept the
   version. If you **rewrite** §21 content, bump the version in the header (line 3, currently
   1.3.6) and add a line to `docs/CHANGES.md`.

---

## Step 3 — Write the decision-log entry

File: `docs/decision_log.md`. Add at the **bottom**. Never edit older entries.

Template (fill in the bracketed parts; the numbers are already correct):

```markdown
## 2026-11-08 — S29 — Gate D6: YELLOW; protocol §21 frozen after seeing pilot data
Decision: Gate D6 outcome YELLOW on run pilot_v1 (latest attempts). Pilot passes.
Quantities (results/reports/pilot_v1_report.md, D6 section):
- E = 0.0425 (17/400) → HOLD not met (> 0.15 required)
- H = 1.000 (100/100)
- N = 3 (BH2_03356, BH2_05290, BH2_05778)
- O > null: yes (O_H1 = 3, N1-H1 p95 = 2.0, p = 0.0107)
- P = 3 (effect/phenotype:disease:drug; gene/protein:disease:drug; gene/protein:drug:disease)
- RED not met (H ≥ 20%, N = 3 not < 3, O > null); GREEN not met (N < 10) → YELLOW.
Interpretation flags: ordering flag not set (O_N1 and O_N2 both above p95);
ambiguity flag set (3/3 N queries R2_AMBIGUOUS or BOTH_AMBIGUOUS).
Note: BH2_05778 is the only SOURCE_NAME_OVERLAP query; without it N = 2. D6 applied as written
(all pilot queries). [your reasoning here]
Why: [one or two sentences, e.g. recomputed by hand; matches the mechanical check]
Data seen before deciding: pilot_v1 report and analysis outputs (all of them).
Changes to protocol or decision rules: protocol §21 [PROVISIONAL] → [FROZEN], frozen after
seeing pilot data (protocol §20: any Phase 2 result is reported as exploratory where §20 applies).
§21 changes: [list: mechanism list kept/narrowed; candidate rule; surgery; control tie-break rule;
anything else]. Protocol version [1.3.6 unchanged / → 1.3.7].
Next step: S30 expansion run. Phase 2 exploratory unless D7 is CONFIRMATORY. Discussed with
supervisor on [date] / [not yet — will discuss before Phase I].
```

---

## Step 4 — Commit

Use Git Bash or PowerShell from `D:\cofailKG`. First look at exactly what changed:

```bash
git status
```

```bash
git diff docs/frozen_pilot_protocol.md docs/decision_log.md
```

Stage only the files you meant to change (add `docs/CHANGES.md` if you bumped the version, and this
guidance file if you want it in history):

```bash
git add docs/frozen_pilot_protocol.md docs/decision_log.md
```

```bash
git commit -m "S29: pilot decision — YELLOW"
```

---

## Before S30 — one thing to know

`docs/frozen_pilot_protocol.md` is a **pinned run source**. At S26 a tag-only edit to it forced a
D5 rerun and a new method commit. Editing §21 has the same effect: the S29 commit becomes the new
method commit for S30. When you start S30, ask Claude Code to re-run the D5-style checks (clean
tree, tests, frozen hashes) on the S29 commit and log the new method commit, before the
expansion run starts.

Also talk to your supervisor before Phase I (runbook S29, "Decide").
