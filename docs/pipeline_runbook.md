# CoFail-KG — Pipeline Runbook

This is your working guide. For every stage it gives: the goal, what you need first, the exact
prompt for Claude Code, what Claude should hand back, **how you evaluate the result**, **what you
decide**, the commit, and which provenance rows the stage touches.

- The science lives in `docs/frozen_pilot_protocol.md` (cited below as "protocol §N").
- The gates live in `docs/decision_rules.md` (cited as "D1"–"D8").
- Claude Code's permanent rules live in `CLAUDE.md`.

---

# Part 0 — How to use this runbook

## 0.1 The files and where they go

```text
cofail-kg/
├── CLAUDE.md                          ← Claude Code reads this every session
├── docs/
│   ├── frozen_pilot_protocol.md       ← the science (you own it)
│   ├── decision_rules.md              ← the gates (you own it)
│   ├── pipeline_runbook.md            ← this file (your guide)
│   ├── provenance.md                  ← which idea came from where
│   ├── decision_log.md                ← every decision, dated
│   └── progress.md                    ← where you are
```

## 0.2 The loop you repeat for every stage

1. In Claude Code, type `/clear`, then switch to **plan mode** (Shift+Tab until plan mode shows).
2. Paste the **session-start prompt** (0.3) and read Claude's summary.
3. Paste the stage prompt from this runbook. Read Claude's plan. If the plan guesses anything
   scientific, stop it and point to the protocol section.
4. Leave plan mode and let Claude implement. Approve file edits and commands one by one; read
   what each command does before approving.
5. When Claude reports, paste the **audit prompt** (0.3). Claude reviews its own work without
   changing anything.
6. **You evaluate** using the stage's checklist. Always at least:
   ```powershell
   git status
   git diff --stat
   python -m pytest -q
   ```
   and open one real output file with your own eyes.
7. Make the stage's decision (if any) and write it in `docs/decision_log.md`.
8. Commit, then ask Claude to update `docs/progress.md`.

**Never** give Claude two stages at once. **Never** continue past a failed checklist item.

## 0.3 Standard prompts

**Session start**
```text
Read CLAUDE.md, docs/progress.md, and git status. Do not read other files yet and do not
change anything. Tell me: which stage is complete, which stage is next, and whether the
working tree is clean.
```

**Audit (after every stage)**
```text
Do not modify any files.
Audit the stage you just implemented:
1. Read every file you changed and the relevant tests.
2. Run the relevant tests and one small real example.
3. Run git diff and check that docs/frozen_pilot_protocol.md, docs/decision_rules.md and
   CLAUDE.md are unchanged.
4. Check every rule you implemented against the protocol section it cites.
5. Look for silent exception handling, hard-coded values that should come from config,
   non-deterministic ordering, and anything that could leak evaluation data to agents.
6. List design choices beyond the specification (CLAUDE.md, Provenance).
Report findings only. Do not fix anything.
```

**Bug found**
```text
I found a problem: <describe exactly, with query ID / file / line>.
1. Write a failing test that reproduces it.
2. Fix the implementation so the test passes, without changing any definition in the protocol.
3. Run all tests.
4. Show me the diff.
Change nothing outside the files needed for this fix.
```

**Claude proposes changing the science**
```text
Do not change that. The definition is fixed in docs/frozen_pilot_protocol.md §<N>.
Implement it exactly as written. If you believe it cannot be implemented as written,
explain why and stop.
```

## 0.4 When a gate fails

1. Do not change thresholds. Record the outcome and numbers in `decision_log.md`.
2. Follow the action column of that gate in `decision_rules.md`.
3. If you want to try something the rules do not describe, write it in the decision log as
   **exploratory** before doing it.

## 0.5 Decision-log entry format

```text
## 2026-10-14 — S6 — Relation mapping frozen
Decision: <what>
Why: <one or two sentences>
Data seen before deciding: <none / which outputs>
Changes to protocol: <section numbers, or "none">
```

## 0.6 Time budget (rough, part-time, beginner)

| Phase | Stages | Estimate |
|---|---|---|
| A Setup | S0–S1 | 2–3 days |
| B Data and graph | S2–S6 | 1.5–2.5 weeks |
| C Reference sets and sampling | S7–S10 | 1 week |
| D Agent system | S11–S15 | 1.5–2 weeks |
| E Evaluation core | S16–S19 | 1 week |
| F Models | S20–S22 | 1 week (includes GPU time) |
| G Panel metrics and smoke | S23–S25 | 1 week |
| H Pilot | S26–S29 | 1 week (about 1 day of GPU time) |

---

# Part 1 — Stage map

| Stage | Name | Gate | Protocol |
|---|---|---|---|
| **Phase A — Setup** | | | |
| S0 | Environment and repository skeleton | — | — |
| S1 | Protocol audit | — | all |
| **Phase B — Data and graph** | | | |
| S2 | BioHopR loader | — | §3.1 |
| S3 | BioHopR diagnostics | — | §3.1 |
| S4 | PrimeKG ingestion and index | — | §3.2 |
| S5 | Field-semantics verification | — | §3.1, §4 |
| S6 | Relation mapping and ambiguity tags | **D1** | §5 |
| **Phase C — Reference sets and sampling** | | | |
| S7 | Reference sets | — | §6 |
| S8 | Query validation | — | §7.1 |
| S9 | Dataset feasibility and inclusion | **D2** | §7.2 |
| S10 | Sampling manifests | — | §8 |
| **Phase D — Agent system** | | | |
| S11 | KG tools | — | §10 |
| S12 | Trace and trace graph | — | §11 |
| S13 | Ollama client | — | §9.1 |
| S14 | Agent prompt and runner | — | §9.3–9.4 |
| S15 | Leakage audit | — | §9.3, §10 |
| **Phase E — Evaluation core** | | | |
| S16 | Answer normalization | — | §12 |
| S17 | Label A | — | §13 |
| S18 | Label B, reason codes, hop-1 status | — | §14 |
| S19 | Per-agent metrics | — | §15 |
| **Phase F — Models** | | | |
| S20 | Model screening | — | §9.1 |
| S21 | Freeze models and engineering limits | **D3** | §9.1, §10 |
| S22 | Single-agent smoke test | — | — |
| **Phase G — Panel metrics and smoke** | | | |
| S23 | Co-failure metrics | — | §16 |
| S24 | Chance baselines | — | §17 |
| S25 | Panel runner and panel smoke test | **D4** | §9.2, §19 |
| **Phase H — Pilot** | | | |
| S26 | Pre-run freeze check | **D5** | §19–20 |
| S27 | Run the 100-query pilot | — | — |
| S28 | Pilot report | — | §15–17 |
| S29 | Pilot decision | **D6** | — |
| **Phase I — After the pilot (provisional)** | | | |
| S30 | Expand to 500 | **D7** | — |
| S31–S36 | Intervention study | — | §21 |
| S37 | Final scale decision | **D8** | — |
| S38 | Final analysis | — | — |

---

# Part 2 — Phase A: Setup

## S0 — Environment and repository skeleton

**Goal.** A working Python environment, an empty but correctly structured repository, and the
four governing documents in place.

**You need first.** VS Code, Git, Python 3.11, Claude Code, Ollama — each opens and prints a
version (`git --version`, `python --version`, `claude --version`, `ollama --version`).

**Do by hand.**
```powershell
mkdir cofail-kg
cd cofail-kg
git init
python -m venv .venv
.venv\Scripts\Activate.ps1
mkdir docs
```
Copy these provided files into place: `CLAUDE.md` (root), and into `docs/`:
`frozen_pilot_protocol.md`, `decision_rules.md`, `pipeline_runbook.md`, `provenance.md`,
`decision_log.md`, `progress.md`. Then start Claude Code with `claude`.

**Prompt.**
```text
Read CLAUDE.md. Then look at the current directory and git status only.

Create the project skeleton:
- pyproject.toml (minimal, package name "cofail_kg", src layout) so the package installs
  with: pip install -e .
- requirements.txt: pandas, pyarrow, numpy, pyyaml, pytest, datasets, huggingface_hub,
  requests, tqdm, matplotlib, networkx
- README.md: one paragraph (project name, purpose, "see docs/").
- .gitignore: .venv/, __pycache__/, *.pyc, data/raw/, data/cache/, results/runs/
- configs/pilot.yaml and configs/models.yaml containing only a comment line
  "# filled in at a later stage — see docs/pipeline_runbook.md".
- src/cofail_kg/__init__.py and subpackages data, kg, agents, evaluation, analysis, utils,
  each with __init__.py.
- scripts/ and tests/, with tests/test_import.py that imports cofail_kg.
- Empty folders with .gitkeep: data/raw, data/processed, data/cache, results/diagnostics,
  results/semantics, results/runs, results/reports.

Do not modify CLAUDE.md or anything in docs/.
Then: pip install -r requirements.txt, pip install -e ., run pytest, and show the tree.
```

**Expect back.** A tree listing, 1 test passing, the list of files created.

**Evaluate.**
1. `python -m pytest -q` → `1 passed`.
2. `git status` shows the new files; `git diff docs/ CLAUDE.md` shows nothing (they are new, untracked — that is fine).
3. `.gitignore` contains `data/raw/` and `results/runs/` (large files must never go into git; back up `results/runs/` separately, e.g., to an external drive or cloud folder, after every run).
4. Open `pyproject.toml` and check the package name is `cofail_kg`.

**Decide.** Nothing.

**Commit.** `git add . && git commit -m "S0: project skeleton and governing docs"`

**Provenance.** AI-assistance log row for S0.

---

## S1 — Protocol audit

**Goal.** Before any code, Claude checks the protocol and decision rules for ambiguities, missing
definitions, and contradictions. You resolve wording problems now, when they are cheap.

**Prompt.**
```text
Read docs/frozen_pilot_protocol.md and docs/decision_rules.md completely. Do not modify anything.

Report:
1. Every [TBD@Sx] item, with its section and stage.
2. Every term used but not defined.
3. Every rule that cannot be implemented exactly as written, and why.
4. Every quantity a gate in decision_rules.md uses that cannot be computed from the protocol's
   definitions.
5. Anything that could let evaluation information (R1, R2, gold bridge, gold answers, Tq)
   reach the experimental agents.
6. Any contradiction between sections.

Do not propose scientific changes. Report problems only, each with its section number.
```

**Expect back.** A numbered list of issues with section numbers.

**Evaluate.** For each issue, decide which kind it is:
- **Wording problem** (the meaning is clear to you, the text is not): fix the text yourself in the protocol; log it.
- **Real open question**: bring it to your supervisor (or a planning chat) before S2; log the answer.
- **Not an issue**: note why in `progress.md`.

Check that the TBD list matches: S2, S4, S5, S6, S9, S21, and `[PROVISIONAL]` §21.

**Decide.** Protocol v1.0 accepted (with any wording fixes).

**Commit.** `git commit -am "S1: protocol audited, v1.0 accepted"` (plus decision-log entry).

**Provenance.** None.

---

# Part 3 — Phase B: Data and graph

## S2 — BioHopR loader

**Goal.** Download BioHopR once, freeze its revision, and load it into a clean internal format
without changing any original field.

**Prompt.**
```text
Implement ONLY the BioHopR data layer. Protocol §3.1 applies.

Before coding:
1. Inspect the Hugging Face dataset knowlab-research/BioHopR: splits, row count, every field
   name and type. Record the dataset revision (commit hash) using huggingface_hub.
2. Determine from the data how 1-hop and 2-hop questions are stored (separate rows, or both
   in the same row). Do not assume.
3. Identify which field holds the multi-answer 2-hop question text. Report candidates with
   examples; do not choose silently.

Then create:
- scripts/02_download_biohopr.py: downloads the pinned revision to data/raw/biohopr/ and
  writes data/raw/biohopr/metadata.json (repo, revision, download time, row count, file SHA256).
- src/cofail_kg/data/biohopr_loader.py: loads the raw file; keeps every original field
  unchanged; adds query_id = "BH2_" + zero-padded row index within the pinned revision, and
  row_sha256 = SHA256 of the row's JSON with sorted keys.
- tests/test_biohopr_loader.py: loads, row count equals the metadata, query_id unique,
  original fields unchanged, rerun gives identical query_id and row_sha256.
- results/diagnostics/biohopr/inspection_20.md: 20 rows (seed 42), showing every field and
  the first 5 answers of each row plus its answer count.

Do not interpret field roles (which field is the query entity or the bridge). That is S5.
```

**Expect back.** Row count, field list, the revision hash, candidate question fields, the
inspection file.

**Evaluate.**
1. Row count: the paper reports 7,633 2-hop questions. If Claude reports something else, find out why before continuing.
2. Open the dataset viewer on Hugging Face. Pick 5 rows from `inspection_20.md` and compare every field with the viewer.
3. Run the loader twice; the test for identical `query_id` and `row_sha256` must pass.
4. Read the candidate question fields. Choose the one whose text asks for **all** answers of the 2-hop question (e.g., "Name all …").
5. In `inspection_20.md`, look at `hop1`, `hop2` and the questions. Write down in `progress.md` which field *seems* to be the starting entity. You verify it at S5; do not rely on names.

**Decide.**
- Protocol §3.1 revision → fill in the hash.
- Protocol §3.1 question field → fill in the field name.
Log both.

**Commit.** `S2: BioHopR loader, revision pinned`

**Provenance.** Row "BioHopR dataset" (Kim et al., 2025).

---

## S3 — BioHopR diagnostics (no PrimeKG needed)

**Goal.** Know the dataset's shape before designing limits: answer-set sizes, relation-pair
counts, and duplicate questions.

**Prompt.**
```text
Implement dataset diagnostics for BioHopR 2-hop rows. Do not use PrimeKG.

Create src/cofail_kg/data/diagnostics.py and scripts/03_biohopr_diagnostics.py producing,
in results/diagnostics/biohopr/:
1. answer_sizes.csv and answer_sizes.png: distribution of answer-list length
   (min, p25, median, mean, p75, p90, p95, p99, max), overall and per relation pair.
2. relation_pairs.csv: count of rows per relation pair (use the dataset's own type fields).
3. largest_answers.csv: the 20 rows with the most answers.
4. duplicate_questions.csv: group rows by identical 2-hop question text; for each group with
   more than one row, report how many distinct bridges (hop1 values) and distinct answer
   lists it has.
5. summary.json with the key numbers.
Add tests on a tiny synthetic table. Do not choose any threshold.
```

**Evaluate.**
1. Compare `relation_pairs.csv` with the 12 counts in protocol §3.1 (from the paper). Small differences need an explanation; large ones mean something is wrong.
2. Note the answer-size **median, p90 and p99** in `progress.md`. You need them at S21: each answer costs roughly 15–25 output tokens in the JSON format, so the output limit must cover realistic answer lists.
3. Open `duplicate_questions.csv`. If identical question texts appear with different bridges and different answer lists, you have direct evidence of the single-bridge label problem. Note the count; it is a useful sentence for the thesis ("N question texts occur with more than one gold bridge").

**Decide.** Nothing is frozen here. Record the numbers in `progress.md`.

**Commit.** `S3: BioHopR diagnostics`

**Provenance.** None new.

---

## S4 — PrimeKG ingestion and index

**Goal.** Freeze the exact PrimeKG release, understand its columns and edge storage, and build a
fast deterministic index plus a small inspection tool for yourself.

**Do by hand first.** Download PrimeKG's edge file (`kg.csv`) — and the node file if the release
provides one — from the PrimeKG page on Harvard Dataverse. Put them in `data/raw/primekg/`. Write
the release version / DOI and the download date into `progress.md`. Downloading by hand makes you
certain which release you have.

**Prompt.**
```text
Implement ONLY the PrimeKG ingestion and index layer. Protocol §3.2 applies.
Raw files are in data/raw/primekg/.

Before coding, inspect the raw files and report:
1. Column names and 5 example rows.
2. Total row count.
3. Which column is a unique node identifier across the whole graph (check uniqueness;
   do not assume).
4. Distinct relation labels and display labels, each with its row count and the
   (source type, target type) pairs it connects.
5. Edge storage: for a random sample of 10,000 rows (seed 42), how often the reverse row
   (same relation, endpoints swapped) also exists.

Then implement:
- scripts/04_prepare_primekg.py: computes SHA256 of every raw file; writes node and edge
  tables to data/cache/ as parquet; writes data/cache/primekg_metadata.json (hashes, row
  counts, columns, canonical ID column, edge-storage finding, release info I will fill in).
- src/cofail_kg/kg/primekg_index.py with a class that loads the cache and offers:
    get_node(node_id) -> id, name, type, source
    find_by_name(name) -> list of nodes (exact match after lower-case, NFKC, whitespace collapse)
    relations_of(node_id) -> for each relation: label, neighbor types, neighbor count
    neighbors(node_id, relation=None, neighbor_type=None) -> sorted by canonical node ID
  All outputs deterministic. No edge is dropped, merged, or reversed silently.
- scripts/inspect_kg.py: a small command-line tool FOR ME (not for agents), e.g.
    python scripts/inspect_kg.py node "Troglitazone"
    python scripts/inspect_kg.py relations <node_id>
    python scripts/inspect_kg.py neighbors <node_id> --relation <label>
- tests/test_primekg_index.py on a tiny synthetic graph.

Report load time and peak memory for the full graph.
```

**Evaluate.**
1. Open the first rows yourself:
   ```powershell
   python -c "import pandas as pd; print(pd.read_csv('data/raw/primekg/kg.csv', nrows=5).T)"
   ```
2. **Row count check.** The PrimeKG paper reports about 4.05 million relationships. About 8.1 million rows means each relationship is stored in both directions; this should agree with Claude's reverse-row finding.
3. **Release check using a published number.** The BioHopR paper states that Troglitazone has 202 side effects listed in PrimeKG. Run:
   ```powershell
   python scripts/inspect_kg.py node "Troglitazone"
   python scripts/inspect_kg.py relations <the ID it prints>
   ```
   Find the side-effect relation's neighbor count. **About 202 → your release matches BioHopR's.** Far from 202 → you probably have a different release; resolve this before S5.
4. Check that the four BioHopR node types (drug, disease, gene/protein, effect/phenotype) exist under the type names PrimeKG uses.
5. Check the canonical ID column is unique (Claude's report) and the metadata JSON contains the hashes.

**Decide.** Protocol §3.2: release, canonical ID column, edge-storage convention. Protocol §10:
whether `get_neighbors` needs a `direction` argument (only if edges are stored one-way **and**
relations are asymmetric). Log all.

**Commit.** `S4: PrimeKG frozen and indexed` (raw and cache files stay out of git).

**Provenance.** Row "PrimeKG" (Chandak et al., 2023).

---

## S5 — Field-semantics verification

**Goal.** Prove from data which BioHopR field is the query entity, which is the bridge, and how
the answers connect — instead of trusting field names.

**Prompt.**
```text
Verify BioHopR field roles against PrimeKG. Protocol §3.1 and §4 apply.

Take a stratified sample: 5 rows per relation pair (all rows if fewer), seed 42.
For each row:
1. Resolve the hop1 and hop2 names to PrimeKG nodes using the index's exact-name rules and
   the row's own type fields. Record ambiguous or missing names.
2. Check whether an edge connects hop1 and hop2, and with which relation labels.
3. Check what fraction of the answer names are neighbors of hop1, and what fraction are
   neighbors of hop2 (any relation).
Write results/semantics/field_roles.csv (one line per row) and a summary stating, per
relation pair, the evidence for "query = hop2, bridge = hop1" versus the alternative.

State a conclusion only if at least 95% of resolvable rows support the same roles in every
relation pair. Otherwise stop and report the conflicting rows. Do not guess.
```

**Evaluate.**
1. Read the summary: which role assignment does the evidence support, and how strongly?
2. Hand-check 3 rows with `scripts/inspect_kg.py`: find the supposed query entity, list its neighbors through the relation Claude found, confirm the supposed bridge is among them, then list the bridge's neighbors and confirm several gold answers appear.
3. Look at the unresolvable names. A few are normal; many suggest a release mismatch (go back to S4 check 3).

**Decide.** Protocol §3.1 field roles → frozen. Log.

**Commit.** `S5: field roles verified`

**Provenance.** None new.

---

## S6 — Relation mapping and ambiguity tags → Gate D1

**Goal.** Map each BioHopR relation to the exact PrimeKG labels that reproduce BioHopR's answers,
and tag which relations are worded ambiguously — all before any agent exists.

**Prompt, part 1.**
```text
Implement protocol §5.1 and prepare §5.2. Use the field roles frozen at S5.

For each of the 12 relation pairs:
1. List every PrimeKG relation label (with display label) connecting the required node types
   for hop 1 and for hop 2.
2. Validation sample: up to 30 rows per pair (all if fewer), seed 42.
3. For each candidate label set per hop (single labels, and unions of labels that connect the
   same types), compute T_q^{b*} per protocol §6 and the exact-reproduction rate
   (share of rows with T_q^{b*} == A*_q).
4. Propose the mapping using the selection rule in §5.1. If there is a tie or the best rate is
   below 90%, mark the pair UNRESOLVED and do not choose.

Write:
- results/semantics/relation_mapping_candidates.csv (every candidate and its rate)
- results/semantics/relation_mapping_proposed.json
- results/semantics/ambiguity_judgments.csv with columns:
  relation_pair, hop, question_wording_for_this_hop, candidate_label, display_label,
  connects_types, in_accepted_set, judgment
  (one line per PrimeKG label connecting the hop's types; leave "judgment" EMPTY)
- the D1 quantities from docs/decision_rules.md.

Do not fill judgments. Do not freeze anything.
```

**Evaluate.**
1. For each pair, look at the proposed labels and rate. Does the label make biomedical sense for the question wording?
2. For every pair below 90%: ask Claude to print 2 failing rows with the difference between `T_q^{b*}` and `A*_q`. Common causes: wrong field role, direction, a missing second label, or name-normalization failures. Fixing a *cause* is allowed; lowering the threshold is not.
3. **Fill in the ambiguity judgments yourself.** For each line, read only the question wording for that hop and ask: *"Could a biomedical expert reading this wording reasonably mean this PrimeKG relation?"* Write `PLAUSIBLE` or `NOT_PLAUSIBLE`. Judge from wording and label meaning only. If you want robustness, ask your supervisor to fill a copy blind and compare.
4. Apply D1.

**Prompt, part 2 (after you filled the judgments and D1 says PROCEED).**
```text
Using results/semantics/ambiguity_judgments.csv as I filled it, and the mapping I approved:
1. Write results/semantics/relation_mapping.json (final, with a SHA256 in its header).
2. Compute the ambiguity tag per relation pair (protocol §5.2) and write
   results/semantics/relation_ambiguity_tags.csv.
3. Mark pairs that failed D1 as excluded.
Do not change any judgment or mapping.
```

**Decide.** Gate **D1** outcome; mapping frozen; ambiguity tags frozen; excluded pairs listed.
Log all, with the numbers.

**Commit.** `S6: relation mapping and ambiguity tags frozen (D1: PROCEED)`

**Provenance.** Own design (mapping procedure, ambiguity tags).

---

# Part 4 — Phase C: Reference sets and sampling

## S7 — Reference sets

**Goal.** For every query, compute the valid bridges, question-valid answers, and gold-bridge
targets exactly as protocol §6 defines them.

**Prompt.**
```text
Implement protocol §6 for all 2-hop queries in relation pairs that passed D1.

Create src/cofail_kg/evaluation/reference_sets.py and scripts/07_build_reference_sets.py.
Output to data/processed/:
- reference_queries.parquet: query_id, s, b_star, Type_B, Type_T, relation_pair, |B_q|,
  |T_q|, |T_q^{b*}|, |A*_q|
- reference_targets.parquet: one row per (query_id, bridge, target) for every b in B_q
  and t in T_q(b)
- gold_normalized.parquet: A*_q per query after protocol §12 normalization, with
  unresolved gold names listed
Use the frozen relation_mapping.json. Exclude t = s and b = s.
Tests on a synthetic graph: one bridge; several bridges; a target reachable through two
bridges; a query with no valid bridge; type filtering.
None of these files may be imported by agent-facing code.
```

**Evaluate.**
1. Pick one SINGLE-bridge and one MULTI-bridge query from the output. For each, use `scripts/inspect_kg.py` to list the query entity's neighbors through the R1 label(s) and filter to `Type_B` — compare with `|B_q|`.
2. For one bridge of the multi-bridge query, list its R2 neighbors of `Type_T` — compare with the rows in `reference_targets.parquet` for that bridge.
3. Check `|T_q^{b*}|` against `|A*_q|` for 5 queries: equal in most (this is what D1 established).

**Decide.** Nothing.

**Commit.** `S7: reference sets`

**Provenance.** Row "Answer set by executing the query pattern" (Yih et al., 2016).

---

## S8 — Query validation

**Goal.** Label every query CONSISTENT/INCONSISTENT, single/multi-bridge, and measure saturation.

**Prompt.**
```text
Implement protocol §7.1.
Create src/cofail_kg/evaluation/query_validation.py and scripts/08_validate_queries.py.
For each query compute: status (CONSISTENT / INCONSISTENT with exactly one reason code in
the priority order listed in §7.1), bridge multiplicity, and saturation share =
|T_q| / (number of PrimeKG nodes of Type_T).
Write results/diagnostics/query_validation.csv and query_validation_summary.json with
counts by status, reason, relation pair, bridge multiplicity, and ambiguity tag.
Do not exclude anything.
```

**Evaluate.**
1. Read the summary. What share is CONSISTENT overall and per pair?
2. Open 5 INCONSISTENT queries with the most common reason and look at the differing entities. Is there a pattern (e.g., a naming problem) that is a bug rather than a real discrepancy? A bug gets fixed (bug-found prompt); a real discrepancy stays.
3. Look at 5 CONSISTENT MULTI-bridge queries: how many bridges do they typically have?

**Decide.** Nothing yet.

**Commit.** `S8: query validation`

**Provenance.** None new.

---

## S9 — Dataset feasibility and inclusion → Gate D2

**Goal.** Fix the saturation threshold, then check there are enough usable queries.

**Prompt, part 1 (before you see D2).**
```text
Do not compute Gate D2 yet.
From results/diagnostics/query_validation.csv, report for CONSISTENT queries in PASS pairs:
the distribution of the saturation share (p50, p90, p95, p99, max), and a table of how many
queries would be excluded at thresholds 30%, 50%, 70% and 90%, overall and per relation pair.
```

**Evaluate and decide (threshold).** The default is 50% (protocol §7.2). Keep it unless the
table shows it removes a whole relation pair for no good reason. Decide **now**, log it, and only
then run part 2.

**Prompt, part 2.**
```text
Using saturation threshold <X>% (now frozen in protocol §7.2 by me), compute the primary
population and Gate D2 exactly as in docs/decision_rules.md. Report N_P, per-pair counts,
single/multi counts, and the D2 outcome. Write data/processed/primary_population.csv.
```

**Decide.** Gate **D2** outcome. Log with the numbers.

**Commit.** `S9: primary population (D2: <outcome>)`

**Provenance.** Own (saturation rule).

---

## S10 — Sampling manifests

**Goal.** Draw the screening, smoke, pilot, and expansion sets exactly as protocol §8 says.

**Prompt.**
```text
Implement protocol §8 exactly.
Create src/cofail_kg/data/sampling.py and scripts/10_make_samples.py.
Input: data/processed/primary_population.csv.
Output to data/processed/manifests/:
- screening.jsonl (20), smoke.jsonl (4), pilot.jsonl (100), expansion.jsonl (400)
  each line: query_id, relation_pair, bridge multiplicity, ambiguity tag, |T_q| bin
- sampling_report.md: counts per stratum for each set, and any stratum that ran out
- manifests.sha256: SHA256 of each manifest
Fill configs/pilot.yaml with: seed, set sizes, manifest paths and hashes.
Tests: determinism (same inputs give byte-identical manifests), disjointness, sizes,
the SHA256 ordering rule of §8 step 4.
```

**Evaluate.**
1. Run the script twice; `manifests.sha256` must be identical.
2. Check disjointness yourself:
   ```powershell
   python -c "import json;s=lambda f:{json.loads(l)['query_id'] for l in open('data/processed/manifests/'+f)};a,b,c,d=s('screening.jsonl'),s('smoke.jsonl'),s('pilot.jsonl'),s('expansion.jsonl');print(len(a&b),len(a&c),len(b&c),len(c&d))"
   ```
   All zeros.
3. Read `sampling_report.md`: single/multi mix close to 25/75; every PASS pair represented.
4. Read 10 pilot questions to get a feel for what the agents will face.

**Decide.** Manifests frozen (hashes in `configs/pilot.yaml`). Log.

**Commit.** `S10: sampling manifests frozen`

**Provenance.** None new.

---

# Part 5 — Phase D: Agent system

## S11 — KG tools

**Goal.** Build the only door the agents have into PrimeKG: `inspect_entity` and `get_neighbors`,
deterministic, paginated, logged, and blind to evaluation data.

**Prompt.**
```text
Implement ONLY the agent-facing KG environment. Protocol §10 applies exactly.

Create src/cofail_kg/agents/kg_env.py:
- class KGEnvironment built on the PrimeKG index from S4 (read-only).
- inspect_entity(entity_id): id, name, type, and relations touching it, each with label,
  neighbor type(s), neighbor count. Relations sorted alphabetically.
- get_neighbors(entity_id, relation, neighbor_type=None, page=1): neighbors sorted by
  ascending canonical ID; returns items (id, name, type), relation, total_count, page,
  page_size, has_more. <Add a direction argument ONLY if protocol §10 says so after S4.>
- Structured error results for unknown IDs, unknown relations, bad page numbers.
- A call budget: after the budget is used, every call returns
  "Tool budget exhausted. Give your final answer now."
- page_size and budget come from configuration; they are frozen at S21. Use page_size=50
  and budget=30 ONLY inside tests.
- Every call is appended to an in-memory call log (arguments, full result, timestamp).

Create src/cofail_kg/agents/tool_schemas.py: JSON function definitions for the two tools
(the format Ollama's chat API accepts). Descriptions must be neutral: they describe what
the tool does and must not mention any BioHopR relation, relation pair, or answer.

Rules: this module must not import anything from cofail_kg.evaluation or read any file in
data/processed/. Add a test that fails if it does.

Tests (synthetic graph): relation listing and counts; neighbor-type filter; ordering;
page 1 + page 2 union equals the full list with no duplicates; last page has_more=false;
errors; budget exhaustion; the import-isolation test.
```

**Evaluate.**
1. Open a Python shell and try the tools on a real node (the query entity of one screening query):
   ```python
   from cofail_kg.kg.primekg_index import PrimeKGIndex   # use the actual class name
   from cofail_kg.agents.kg_env import KGEnvironment
   env = KGEnvironment(PrimeKGIndex(), page_size=50, budget=30)
   print(env.inspect_entity("<id>"))
   p1 = env.get_neighbors("<id>", "<a relation from the list>", page=1)
   print(p1["total_count"], p1["has_more"], [x["id"] for x in p1["items"]][:5])
   ```
2. Compare `total_count` with `python scripts/inspect_kg.py neighbors <id> --relation <label>`.
3. Request pages until `has_more` is false; confirm the union has exactly `total_count` items and IDs are ascending.
4. Read the tool descriptions in `tool_schemas.py`. Do they hint at any answer or relation choice? They must not.

**Decide.** Approve the tool description wording (it is part of the method). Log it as tool
version "T1".

**Commit.** `S11: KG environment and tool schemas (T1)`

**Provenance.** Rows "Graph-CoT", "Think-on-Graph" (design), own (pagination, ordering, budget).

---

## S12 — Trace and trace graph

**Goal.** Record everything an agent sees and does, and turn it into the trace graph that all
path labels are computed from.

**Prompt.**
```text
Implement protocol §11.
Create src/cofail_kg/agents/trace.py:
- An episode record (JSON) with every field listed in protocol §19, the full message list,
  and the full tool-call log.
- A write-once saver: results/runs/<run_id>/<query_id>__<agent_id>.json; refuses to
  overwrite an existing file.
- build_trace_graph(record): directed edges (u, relation, v) for each neighbor v on each
  returned page of each successful get_neighbors call — nothing else.
- appeared_entities(record): every entity returned by any tool call (neighbors, and subjects
  of successful inspect_entity calls).
- simple_paths(trace_graph, s, x, max_len=3): all simple directed paths, ordered by length,
  then by the index of the tool call that created the last edge.
Tests with hand-written synthetic episode records: the graph contains exactly the returned
page items; unreturned pages add nothing; paths found and ordered correctly; saver refuses
to overwrite.
```

**Evaluate.**
1. Read one synthetic test case and draw its trace graph on paper; compare with what the test asserts.
2. Confirm the saver refuses to overwrite: run the relevant test, and read the code path.

**Decide.** Nothing.

**Commit.** `S12: trace and trace graph`

**Provenance.** Row "KG-TRACES" (path-level traces), own (construction rules).

---

## S13 — Ollama client

**Goal.** A thin, reliable wrapper around Ollama's chat API that records everything needed for
reproducibility.

**You need first.** Ollama running (`ollama list` works). Pull one small model for testing and
check it supports tools: `ollama show <model>` must list **tools** under Capabilities.

**Prompt.**
```text
Implement src/cofail_kg/agents/ollama_client.py:
- chat(model, messages, tools, options) using Ollama's local HTTP API.
- options: temperature, seed, num_ctx, num_predict — all passed explicitly every call.
- Returns: the raw response, parsed assistant message, native tool calls (if any),
  prompt_eval_count, eval_count, latency.
- get_model_identity(model): tag, digest, quantization, parameter size (from the API).
- Timeout per request from configuration. Retries ONLY for connection errors, at most 2,
  logged. Never retry because of the content of a model reply.
- Unit tests with a mocked HTTP layer.
- scripts/13_test_ollama.py: exactly one real plain call and one real tool-call call
  (a dummy tool "add(a, b)"), printing the identity, token counts, latency, and whether a
  native tool call came back.
```

**Evaluate.**
1. Run `python scripts/13_test_ollama.py`. You must see the model digest, token counts, and a native tool call for the `add` tool.
2. If the tool call arrives as plain text instead of a native tool call, that model is unsuitable (see S14 rule on native calls).

**Decide.** Nothing.

**Commit.** `S13: Ollama client`

**Provenance.** Row "Ollama" (software).

---

## S14 — Agent prompt and runner

**Goal.** One complete episode: question in, tool calls executed, JSON answer out, full trace saved.

**The system prompt (draft — review it, then give it to Claude).** Placeholders in braces are
filled from configuration.

```text
You are a biomedical knowledge-graph agent. You answer questions by exploring a knowledge graph
with two tools.

inspect_entity(entity_id): shows an entity, its type, and the relations connected to it, with
the number of neighbors for each relation.
get_neighbors(entity_id, relation, neighbor_type, page): lists the neighbors of an entity through
one relation, {PAGE_SIZE} per page. The result tells you the total number of neighbors and
whether more pages exist.

Rules:
1. Use the tools to find the answer. Every entity in your answer must be one you saw in a tool
   result; copy its ID exactly.
2. You can make at most {BUDGET} tool calls.
3. When you are finished, reply with only this JSON object and nothing else:
   {"status": "answered", "answers": [{"id": "<ID>", "name": "<name>"}]}
   If you cannot find an answer, reply with only:
   {"status": "no_answer", "answers": []}
```

User message template:
```text
{QUESTION}
Starting entity: {NAME} (PrimeKG ID: {ID})
```

**Prompt.**
```text
Implement the agent runner. Protocol §9.3 and §9.4 apply exactly.

Create src/cofail_kg/agents/prompts.py containing the system prompt and user template I give
below VERBATIM, with a PROMPT_VERSION constant "P1". <paste the two texts above>

Create src/cofail_kg/agents/run_agent.py: run_episode(query, model_config, env_config) that
1. builds the two messages from the query's question field (S2) and its starting entity
   (field roles from S5) — nothing else from the dataset row;
2. calls the model with the tool schemas from S11;
3. executes ONLY native tool calls through KGEnvironment and appends their results as tool
   messages; tool-call-looking text inside a normal message is NOT executed and is recorded
   as TEXT_TOOL_CALL;
4. loops until the model sends a message without tool calls, the budget is exhausted (then
   allows exactly one more model turn), or the episode timeout is reached;
5. parses the final message per protocol §9.4, with exactly one fixed re-prompt if parsing
   fails (text in §9.4, verbatim);
6. saves the episode record with the S12 saver. Status: SUCCESS, PARSE_FAIL, TIMEOUT, or
   ERROR (with the exception text).

Tests with a mocked Ollama client: a normal episode; budget exhaustion; parse failure then
success after re-prompt; parse failure twice (PARSE_FAIL); timeout; text tool call not executed.

Then run ONE real episode: the first query in screening.jsonl, with the test model from S13,
page_size 50, budget 30, num_ctx 8192. Print the path of the saved record.
```

**Evaluate — read the real episode record line by line.**
1. The user message contains only the question and the starting entity. No relation names, no answers.
2. Every tool call is well-formed and its result matches what `scripts/inspect_kg.py` shows for the same call.
3. You can follow the agent's route: which relation it chose first, which bridge, which targets.
4. The final JSON parsed; answer IDs appear in earlier tool results.
5. Token counts are recorded; `prompt_eval_count` is well below `num_ctx`.

**Decide.** Approve the system prompt and user template as **P1**. Log them (they are part of the
method and go in the thesis appendix).

**Commit.** `S14: agent runner and prompt P1`

**Provenance.** Row "ReAct" (reason–act loop), own (prompt, parsing rules).

---

## S15 — Leakage audit

**Goal.** Prove that nothing from the evaluation side reaches the agents.

**Prompt.**
```text
Do not change any existing behavior. Add tests/test_leakage.py and run it.

For the 20 screening queries (no model calls needed; build the messages only):
1. Assert that the system and user messages contain none of: the gold bridge's name or ID,
   any gold answer name or ID, any R1/R2 label, the relation-pair name.
2. Assert that kg_env.py, tool_schemas.py, prompts.py and run_agent.py import nothing from
   cofail_kg.evaluation and read no file under data/processed/ (static check of imports and
   file paths).
3. Assert that for 10 random (entity, relation) pairs, get_neighbors returns exactly the same
   IDs as the index's neighbors() (no filtering).
Also print, for one screening query, the exact system and user messages the agent receives.
Report which assertions passed.
```

Note: relation labels and answer entities *will* appear inside tool results — that is the graph
itself, not leakage. The test checks the prompt and the code paths.

**Evaluate.**
1. All assertions pass.
2. Read the printed messages yourself, slowly. Ask: "Could an agent learn anything from this that it should find with the tools?"

**Decide.** Nothing, unless something leaks — then fix before any further stage.

**Commit.** `S15: leakage audit passes`

**Provenance.** None new.

---

# Part 6 — Phase E: Evaluation core

These modules are built before model screening because the screening criteria (D3) use them.
They are tested on synthetic data plus the real episode from S14.

## S16 — Answer normalization

**Prompt.**
```text
Implement protocol §12 exactly in src/cofail_kg/evaluation/normalize.py.
Input: an agent's parsed answer list and the query's Type_T. Output per item: resolved
node ID or UNRESOLVED with reason (AMBIGUOUS_NAME / NO_MATCH), resolution method
(ID / EXACT_NAME / EXACT_NAME_TYPE_FILTER), NAME_ID_MISMATCH flag; duplicates removed
after resolution (report how many).
No fuzzy or embedding matching.
Tests: valid ID; invalid ID with a matching name; name matching two nodes where only one has
Type_T; name matching two nodes of Type_T; no match; ID and name disagreeing; duplicates.
Run it on the S14 real episode and print the result.
```

**Evaluate.** Check each test case matches protocol §12 wording. On the real episode, every
answer copied from tool output should resolve by ID.

**Commit.** `S16: normalization`

**Provenance.** Own; BioHopR's BioLORD-based matching noted as a contrast.

---

## S17 — Label A

**Prompt.**
```text
Implement protocol §13 exactly in src/cofail_kg/evaluation/answer_labels.py.
Input: resolved answers, the query's reference sets (S7) and A*_q.
Priority exactly as in §13. Output one label per answer.
Tests: GOLD; GOLD_BRIDGE_EXTRA; ALT_VALID; OFF_QUESTION; UNRESOLVED; an entity in both
T_q^{b*} and A*_q (must be GOLD); an entity reachable through two bridges.
Run it on the S14 real episode and print each answer with its label.
```

**Evaluate.** For two answers from the real episode, confirm the label by hand: is the entity in
`reference_targets.parquet` for this query? Through the gold bridge or another bridge?

**Commit.** `S17: Label A`

**Provenance.** Own.

---

## S18 — Label B, reason codes, hop-1 status

**Prompt.**
```text
Implement protocol §14 exactly in src/cofail_kg/evaluation/path_labels.py, using the S12
trace-graph utilities and the frozen R1, R2, Type_B, Type_T.

Output per answer: Label B, reason codes (union over paths, and primary-path codes),
primary path, H1(x, i). Output per episode: agent hop-1 status (H1_CLEAN / H1_MIXED /
H1_WRONG / H1_NONE) and "found R1".

Tests (synthetic traces), one per case:
- SUPPORTED through a valid two-hop path
- valid path via a non-gold bridge (SUPPORTED; Label A would be ALT_VALID)
- SHORTCUT (target-type entity reached in one hop)
- WRONG_RELATION_HOP1; WRONG_RELATION_HOP2; WRONG_BRIDGE_TYPE; WRONG_TARGET_TYPE
- WRONG_HOP_COUNT (only a 3-hop path)
- entity reachable both validly and invalidly (SUPPORTED wins)
- KG_UNSUPPORTED (entity appeared, no path from s)
- UNGROUNDED (never appeared)
- an entity on page 2 of a list the agent never opened (UNGROUNDED)
- hop-1 statuses: CLEAN, MIXED, WRONG, NONE; H1(x, i) for a mixed trace
Run on the S14 real episode and print each answer's labels and primary path.
```

**Evaluate.** For every answer of the real episode, trace the primary path by hand in the episode
record and confirm the label and codes. This is the most important label in the project; take
your time.

**Commit.** `S18: Label B and hop-1 status`

**Provenance.** Own; motivation for tracking ungrounded answers (Zhou et al., 2025b).

---

## S19 — Per-agent metrics

**Prompt.**
```text
Implement protocol §15 exactly in src/cofail_kg/evaluation/agent_metrics.py.
One row per (query, agent) with every metric listed in §15, including bridge rank,
bridge-conditional recall, early stop, FIRST_SEEN_PAGE per answer, pages requested,
tool calls used, budget-exhausted flag, and benchmark P/R/F1 against A*_q.
Tests on synthetic episodes for each metric, especially early stop and bridge rank.
Run on the S14 real episode and print the row.
```

**Evaluate.** Check early stop and bridge rank against the real episode record by hand.

**Commit.** `S19: per-agent metrics`

**Provenance.** Standard (P/R/F1); own (the rest).

---

# Part 7 — Phase F: Models

## S20 — Model screening

**Goal.** Measure candidate models against Gate D3 on the 20 screening queries.

**You need first.** Choose 6–8 candidates. Requirements: `ollama show <model>` lists **tools**;
the model fits your GPU (with 8 GB VRAM, roughly ≤ 9B parameters at 4-bit quantization); several
different model families (for example Qwen, Llama, Mistral, Granite, Phi — check each one's tool
capability yourself; availability changes). Pull them with `ollama pull`.

**Prompt.**
```text
Create scripts/20_screen_models.py using the S14 runner and S16–S19 evaluation.
Screening settings (provisional, recorded in the output): num_ctx 8192, page_size 50,
budget 30, temperature 0, seed 42, episode timeout 10 minutes, prompt P1, tools T1.
Candidates: <list of Ollama tags>.
Run every candidate on the 20 screening queries (one model loaded at a time).
Save episode records (write-once) under results/runs/screening/.
Write to results/diagnostics/screening/:
- screening_table.csv: per model — tool-call validity, valid-JSON rate, share of queries
  with ≥1 SUPPORTED question-valid answer, median and max wall time, OOM/errors count,
  max prompt_eval_count, median tool calls used, share of episodes hitting the budget,
  model family, digest,
- the D3 pass/fail per criterion.
Do not select models.
```

**Evaluate.**
1. Read `screening_table.csv` against D3.
2. For each passing model, open 2 episode records and read them. Numbers can pass while behavior is odd (e.g., one model always answers with the first 5 items it sees).
3. Note max `prompt_eval_count` and the budget-hit share; you need them at S21.

**Decide.** Nothing frozen yet (next stage).

**Commit.** `S20: model screening` (commits the table; episode records stay in `results/runs/screening/`, which is backed up but not committed).

**Provenance.** Row "each model" (technical report or model card).

---

## S21 — Freeze models and engineering limits → Gate D3

**Goal.** Choose the four agents and freeze every runtime number the pilot uses.

**Decide (you), using these rules — write every value and its reason in the decision log:**

| Value | Rule |
|---|---|
| Four models | Gate D3: passing models, maximize family diversity, then competence, then speed |
| `num_ctx` | ≥ 1.25 × the largest `prompt_eval_count` any chosen model reached in screening, rounded up to a power of 2; must still run without OOM on your GPU. If it cannot fit, lower `page_size` instead. |
| `page_size` | 50 unless context does not fit (then 25) |
| Tool budget | About 2 × the median tool calls used by the chosen models in screening, between 20 and 40. If > 20% of screening episodes hit the budget, raise it (within 40). |
| `num_predict` (max output tokens per turn) | Enough for the S3 answer-size p90 at ~25 tokens per answer, rounded up (e.g., p90 = 100 answers → 4096) |
| Episode timeout | 3 × the slowest chosen model's median screening wall time, at least 10 minutes |

**Prompt (after deciding).**
```text
Write configs/models.yaml with these four agents: <agent_id, Ollama tag> ×4, and record each
model's digest, quantization, parameter size and family from get_model_identity().
Write the runtime values into configs/pilot.yaml: num_ctx <>, page_size <>, budget <>,
num_predict <>, episode_timeout <>, temperature 0, seed 42, prompt P1, tools T1.
Add a check function that fails if any installed model's digest differs from models.yaml.
Do not change protocol files.
```

Then fill protocol §9.1 and §10 `[TBD@S21]` items yourself.

**Evaluate.** `git diff configs/`: exactly the values you decided. Run the digest check.

**Commit.** `S21: models and runtime frozen (D3)`

**Provenance.** Model rows filled with exact tags.

---

## S22 — Single-agent smoke test

**Goal.** See the four frozen agents behave on real questions with the final settings, and
exercise the evaluation code on real traces.

**Prompt.**
```text
Run each of the four frozen agents on 16 screening queries (as many SINGLE_BRIDGE as the
screening set has, up to 8; the rest MULTI_BRIDGE), with the frozen configuration.
Save records under results/runs/smoke_single/. Then run S16–S19 evaluation on all 64
episodes and write results/diagnostics/smoke_single_summary.md: per model — status counts,
Label A and Label B distributions, reason-code counts, hop-1 statuses, early-stop share,
budget-hit share, max prompt tokens vs num_ctx.
Do not interpret.
```

**Evaluate — manual reading (plan 2–3 hours).**
1. Read at least one full episode per model.
2. For 6 answers across models, check Label A and Label B by hand against the trace.
3. Check no episode came close to `num_ctx` (prompt tokens > 90% of `num_ctx` means silent context loss risk → go back to S21 and adjust, with a log entry).
4. Any systematic technical problem (a model never calls tools, JSON always fails) → back to S21 (model choice), log it.

**Decide.** Proceed, or return to S21. Log.

**Commit.** `S22: single-agent smoke test`

**Provenance.** None new.

---

# Part 8 — Phase G: Panel metrics and smoke

## S23 — Co-failure metrics

**Prompt.**
```text
Implement protocol §16 exactly in src/cofail_kg/evaluation/cofailure.py.
Per query: CF4^Q, CF3^Q (all, grounded-only, hop-1-clean), CF4^BH, CF3^BH, PCF_REL3/4,
PCF_NODE3/4, PCF_SHORTCUT3, with the shared entities / events / nodes, their PrimeKG degree
and degree percentile, relation(s), and the query's ambiguity tag. Per agent pair: pairwise
error agreement (§16.4).

Tests with toy data:
- all four share wrong entity X → CF4=1, CF3=1
- three share X, fourth correct → CF4=0, CF3=1
- X, X, Y, Z → CF3=0
- all different → CF3=0
- three share X but one reached it with H1=0 → CF3^{Q,H1}=0
- shared X is UNGROUNDED for one agent → grounded CF3 recomputed correctly
- shared answer that is ALT_VALID → not a co-failure; but counts for CF^BH
- UNRESOLVED answers never counted
- three agents take the same wrong relation at the same node → PCF_REL3=1
- shared off-path node → PCF_NODE3=1
- pairwise agreement on a hand-computed example
```

**Evaluate.** Read the toy tests and confirm each expected value against protocol §16 yourself.

**Commit.** `S23: co-failure metrics`

**Provenance.** Row "Kim et al. 2025" (pairwise agreement, adapted); own (rest).

---

## S24 — Chance baselines

**Prompt.**
```text
Implement protocol §17 exactly in src/cofail_kg/evaluation/null_models.py:
nulls N1 (uniform over C_iq) and N2 (page-1 restricted), 10,000 trials, seed 42,
per-query null probabilities, aggregate null distribution of totals, 95th percentile,
exceedance p, for CF3 and CF4, overall and hop-1-clean subset.
Use independent, seeded random streams per query so results do not depend on query order.

Tests:
- REQUIRED: all agents give the same single wrong answer, each saw 200 other wrong
  candidates of Type_T → null CF3 probability is small (< 0.01)
- tiny pools (each agent's pool has exactly its answer) → null probability 1
- k_iq never exceeds |C_iq| (assert)
- determinism: same seed, same result; query order shuffled, same result
- aggregate: hand-checkable case with two queries
```

**Evaluate.** Read the REQUIRED test. Understand why the null is low there — you will explain
this in the thesis.

**Commit.** `S24: chance baselines`

**Provenance.** Own; context row "Kohli 2026" (independent-voting null).

---

## S25 — Panel runner and panel smoke test → Gate D4

**Prompt.**
```text
Implement src/cofail_kg/agents/panel_runner.py and scripts/25_run_panel.py:
- Runs the four frozen agents on a manifest, one model at a time (all queries for agent 1,
  then agent 2, ...). Agents never share state (protocol §9.2).
- Verifies model digests and config hashes before starting; refuses to run on mismatch.
- Checkpoints after every episode; on restart skips completed episodes (by file existence
  and a completed-status check) and never overwrites.
- Writes a progress file (episodes done / total, failures so far).
- After the run: evaluation (S16–S19, S23, S24) → results/runs/<run_id>/analysis/.
Tests: resume after a simulated crash (no duplicates, nothing missing), digest mismatch
refusal, write-once.

Then run the smoke manifest (4 queries × 4 agents = 16 episodes) as run_id "smoke_panel".
Halfway through, I will stop the process; tell me the exact moment to press Ctrl+C.
Then restart the same command and confirm completion without duplicates.
Produce results/runs/smoke_panel/analysis/ and an audit sheet
results/runs/smoke_panel/audit_sheet.csv listing 8 episodes (2 per agent) with columns:
episode, answer_id, label_A, label_B, primary_path, my_label_A, my_label_B, notes
(leave my_* empty).
```

**Evaluate — your manual audit.**
1. Do the kill-and-resume exactly as instructed; check the episode count is 16 with no duplicates.
2. Fill `my_label_A` and `my_label_B` for every answer in the audit sheet by reading the traces. Any disagreement is either your mistake or a bug — resolve it (bug-found prompt).
3. Check all D4 conditions.

**Decide.** Gate **D4** PASS, or fix and repeat. Log.

**Commit.** `S25: panel runner, smoke test (D4: PASS)`

**Provenance.** None new.

---

# Part 9 — Phase H: Pilot

## S26 — Pre-run freeze check → Gate D5

**Prompt.**
```text
Do not modify anything. Check every condition of Gate D5 in docs/decision_rules.md:
1. List any [TBD@Sx] with x ≤ 26 remaining in the protocol or decision rules.
2. Run the full test suite.
3. git status must be clean; print the commit hash.
4. Recompute PrimeKG SHA256 and BioHopR revision; compare with recorded values.
5. Compare installed model digests with configs/models.yaml.
6. Recompute the pilot manifest hash; compare with configs/pilot.yaml.
Report PASS/FAIL per condition and the overall D5 result.
```

**Evaluate.** Every line PASS. Write the commit hash into the decision log: this commit *is* your
pilot's method.

**Commit.** Nothing new should be needed. If a fix was needed, commit it and rerun S26.

---

## S27 — Run the 100-query pilot

**Before starting.** Plug in the laptop, disable sleep, close other GPU programs. Expected time:
400 episodes × your median episode time (from S22) — often 10–25 hours. Running it across
several nights is fine; the runner resumes.

**Prompt.**
```text
Start the pilot: python scripts/25_run_panel.py --manifest pilot --run-id pilot_v1
Do not change any code or configuration while it runs. Report the progress file every time I
ask. If the process stops, tell me the resume command; do not edit anything.
```

**While it runs.**
- Check `progress` occasionally. A few failures are normal.
- If failures pile up with the same error (e.g., every episode of one model times out), **stop**. This is a technical problem: fix it with the bug-found prompt (no definition changes), log it, and resume. Episodes that already completed stay.
- Back up `results/runs/pilot_v1/` after each session.

**Evaluate.** 400 episode records exist (or failures are explicitly recorded). No duplicates.

**Commit.** Commit the analysis outputs and the progress file, not the raw episode records.

---

## S28 — Pilot report

**Prompt.**
```text
Do not change any code, definition, or threshold.
Create scripts/28_pilot_report.py and results/reports/pilot_v1_report.md with separate
sections: (A) observed facts, (B) descriptive comparisons, (C) open questions.
No causal language anywhere.

Tables:
1. Technical: status counts per model; E.
2. Per model: Label A and Label B distributions; question-valid precision; OFF_QUESTION rate;
   UNGROUNDED rate; benchmark P/R/F1; hop-1 statuses; early-stop share; budget-hit share.
3. Co-failure: CF3^Q, CF4^Q (all / grounded / hop-1-clean), CF3^BH, CF4^BH, PCF_REL3/4,
   PCF_NODE3/4, PCF_SHORTCUT3; pairwise error agreement matrix.
4. Chance baselines: N1 and N2 for CF3 and CF3^{Q,H1}: observed, null mean, 95th percentile, p.
5. Strata: all co-failure metrics by ambiguity tag, by SINGLE/MULTI bridge, by relation pair.
6. Ordering: distribution of chosen bridge ranks; FIRST_SEEN_PAGE of shared wrong answers.
7. Case sheets: for EVERY query with CF3^{Q,H1}=1, one page: the question, each co-failing
   agent's primary path to the shared entity, reason codes, the shared node's degree
   percentile, ambiguity tag.
Also compute the D6 quantities (E, H, N, O vs null, P) but do not state the outcome.
```

**Evaluate — the most important reading of the project.**
1. Read every case sheet. For each, write one line in `progress.md`: does this look like a structural trap (shortcut, off-path hub, fan-out), a wording problem, or a technical artifact?
2. Check the ordering table: are shared wrong answers mostly from page 1? (That will matter for the N2 comparison.)
3. Sanity-check 3 numbers in the report by hand from the analysis files.

**Commit.** `S28: pilot report`

---

## S29 — Pilot decision → Gate D6

**Prompt.**
```text
Apply Gate D6 from docs/decision_rules.md mechanically to the quantities in
results/reports/pilot_v1_report.md, in the stated order (HOLD, RED, GREEN, YELLOW).
Show each quantity, each rule, and whether it holds. Report the outcome and the two
interpretation flags. Do not modify anything.
```

**Evaluate.** Recompute the outcome yourself from the table — it takes five minutes and it is your
decision, not Claude's.

**Decide.** Record in the decision log: outcome, all five quantities, both flags, and the next
step (S30 expansion, or descriptive write-up). Discuss with your supervisor before starting Phase I.

**Commit.** `S29: pilot decision — <outcome>`

---

# Part 10 — Phase I: After the pilot (provisional)

These stages depend on the pilot. Before starting them, revise protocol §21 using what the pilot
showed (which mechanisms actually occur), mark it `[FROZEN]`, and log the change as made **after**
seeing pilot data. Prompts below are templates.

## S30 — Expand to 500 → Gate D7

```text
Run scripts/25_run_panel.py --manifest expansion --run-id pilot_v1 (same run, adding the 400
expansion queries). Everything frozen stays identical; verify with the S26 checks first.
Then regenerate the report for all 500 queries (S28 script) and compute D7's quantities,
including C = candidates meeting protocol §21's candidate rule with an available matched
control. Do not state the outcome.
```
You apply D7 yourself and log it.

## S31 — Intervention candidates and design freeze

```text
Using only the frozen 500-query analysis, list every query meeting the protocol §21 candidate
rule. For each: shared entity, shared structural feature (edge, relation branch at a node, or
off-path node), mechanism (SHORTCUT / WRONG_RELATION_HOP1 / WRONG_RELATION_HOP2 / off-path
node / fan-out), whether a SUPPORTED route remains after blocking it, and up to 3 matched-
control candidates per the §21 matching rule. Write results/interventions/candidates.csv.
Do not select cases; list all.
```
You freeze: included mechanisms, candidate list, one control per case (the closest match by the
§21 rule — decide the tie-break rule before looking at any outcomes). Log.

## S32 — Surgery overlay

```text
Implement protocol §21 surgery as a query-local overlay inside KGEnvironment: a list of
blocked edges (u, r, v) or hidden (u, r) pairs, applied only when the episode's query_id
matches. Original PrimeKG files and cache are never modified. The overlay spec is saved with
every episode. Tests: blocked edges disappear from inspect_entity counts and get_neighbors
results; nothing else changes; no overlay leaks into other queries.
```

## S33 — Matched controls

```text
For each frozen candidate, build the treatment overlay and the control overlay from
results/interventions/candidates.csv. Verify for both: a SUPPORTED route to T_q remains,
only the intended edges are removed. Write results/interventions/manifest.jsonl.
```

## S34 — Intervention smoke test

```text
Run 3 treatment and 3 control overlays with all four agents (24 episodes) as run_id
"intervention_smoke". Report tool-output differences versus the original run for the
same queries.
```
You check by hand: only the intended structure changed; agents can still navigate; a valid route
exists.

## S35 — Intervention runs

```text
Run all treatment and control overlays with the frozen agents as run_id "intervention_v1",
with the same resume and verification rules as the pilot.
```

## S36 — Intervention evaluation

```text
Compute per case and in aggregate, per protocol §21: CF3/CF4 before vs after for treatment
and control, PCF before vs after, recovery share, no-answer change, displacement categories
per agent (VALID_RELATION / SAME_WRONG_RELATION_OTHER_NEIGHBOR / OTHER_WRONG / NO_ANSWER),
ΔCF and τ_CF. Report treatment-only cases separately as exploratory. No causal language in
the "observed facts" section.
```

## S37 — Final scale decision → Gate D8

Apply D8; log it. If scaling, repeat S30–S36 on new manifests drawn with the same procedure.

## S38 — Final analysis and thesis tables

```text
Produce the final tables:
1. Dataset: CONSISTENT/INCONSISTENT by reason; SINGLE/MULTI; relation pairs; ambiguity tags;
   saturation.
2. Agent behavior: hop-1 statuses; bridge ranks; Label A and Label B distributions; benchmark F1.
3. Co-failure: CF3/CF4 (Q, grounded, H1, BH); PCF; pairwise agreement; N1 and N2 baselines.
4. Mechanisms: counts of SHORTCUT, WRONG_RELATION, off-path node, early stop, by stratum.
5. Counterfactual: before / after treatment / after control; ΔCF; τ_CF; recovery;
   displacement; no-answer change.
Each table in results/reports/final/ as CSV and Markdown, with the commit hash that produced it.
```

---

# Part 11 — Troubleshooting

| Symptom | Likely cause | What to do |
|---|---|---|
| A model writes tool calls as text instead of calling tools | The model or its Ollama template lacks native tool support | It is recorded as `TEXT_TOOL_CALL` and not executed. If frequent, the model fails D3; choose another. |
| `prompt_eval_count` close to `num_ctx` | Long tool outputs fill the context; Ollama may drop earlier messages | Before the pilot: raise `num_ctx` or lower `page_size` (S21, log it). During the pilot: do not change; report affected episodes. |
| Out-of-memory from Ollama | `num_ctx` too large for 8 GB VRAM | Lower `num_ctx` or choose a smaller model (S21). |
| PrimeKG loading is slow or uses too much RAM | 8 million rows in pandas | Ask Claude to load from the parquet cache with only the needed columns; keep one index object alive per run. |
| Claude says a test "should" be changed to pass | The code or the test is wrong | Use the bug-found prompt: ask which one is wrong and why, before any change. |
| Claude proposes changing a definition | Normal eagerness | Use the "Claude proposes changing the science" prompt. |
| Tests pass but a real output looks wrong | Tests do not cover the case | Write a failing test from the real example first (bug-found prompt). |
| Gate result you dislike | — | Follow `decision_rules.md`. Do not change thresholds. Anything extra is exploratory and logged first. |
| You lost track of where you are | — | Session-start prompt; read `progress.md` and the last decision-log entries. |

---

# Part 12 — Where each stage's output goes in the thesis

| Thesis section | Comes from |
|---|---|
| Data | S2, S3, S4 (release, hashes), S5, S6 (mapping, ambiguity), S8–S9 (dataset table) |
| Method: task and answer key | Protocol §4–§7; S7 |
| Method: agents and environment | Protocol §9–§11; S11, S14 (prompt P1, tools T1 — appendix), S21 (models) |
| Method: evaluation | Protocol §12–§17 |
| Method: design and gates | Protocol §18, `decision_rules.md`, decision log |
| Results: pilot | S28 report, S29 decision |
| Results: interventions | S36, S38 |
| Reproducibility statement | S26 commit hash, hashes, model digests |
| AI-use disclosure | `provenance.md` AI-assistance log |
