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
│   ├── progress.md                    ← where you are (incl. the "fix at stage" list)
│   ├── CHANGES.md                     ← one-page summary of protocol changes
│   └── S1_audit_response.md           ← how every audit item was resolved
├── configs/
│   └── frozen_hashes.yaml             ← every frozen hash (created at S2, filled stage by stage)
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
Following protocol §0.3, report as problems only issues that could change a scientific result or
a gate outcome; list engineering observations separately and briefly.
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
| S21 | Freeze models and engineering limits | **D3** | §9.1 |
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

Following protocol §0.3, report only problems that could change a scientific result or a gate
outcome. Do not propose scientific changes. Report problems only, each with its section number.
```

**Expect back.** A numbered list of issues with section numbers.

**Evaluate.** For each issue, decide which kind it is:
- **Wording problem** (the meaning is clear to you, the text is not): fix the text yourself in the protocol; log it.
- **Real open question**: bring it to your supervisor (or a planning chat) before S2; log the answer.
- **Not an issue**: note why in `progress.md`.

Check that the TBD list matches: S2, S4, S5, S6, S9, S11, S14, S21, and `[PROVISIONAL]` §21
(frozen at S29).

**Decide.** The current protocol version is accepted (with any wording fixes).

**Commit.** `git commit -am "S1: protocol audited"` (plus decision-log entry).

**Provenance.** None.

---

# Part 3 — Phase B: Data and graph

## S2 — BioHopR loader

**Goal.** Download BioHopR once, freeze its revision, and load it without changing any field.

**Prompt.**
```text
Implement ONLY the BioHopR data layer. Protocol §0.4 (row, row_id) and §3.1 apply.

Before coding:
1. Inspect the Hugging Face dataset knowlab-research/BioHopR: splits, row count, every field
   name and type. Get the dataset revision (commit hash) with huggingface_hub.
2. Determine from the data how 1-hop and 2-hop questions are stored (separate rows, or both in
   the same row). Do not assume. Report which records count as 2-hop records.
3. Identify which field holds the multi-answer 2-hop question text. Report candidates with
   examples; do not choose silently.

Then create:
- scripts/02_download_biohopr.py: downloads the pinned revision to data/raw/biohopr/, writes
  data/raw/biohopr/metadata.json (repo, revision, download time, row count, file SHA256), and
  creates configs/frozen_hashes.yaml with the key biohopr_revision (protocol §3.4) if absent.
- src/cofail_kg/data/biohopr_loader.py: loads the raw file; keeps every original field unchanged;
  adds row_id = "BH2_" + the record's 0-based position among the 2-hop records, zero-padded to
  5 digits, and row_sha256 = SHA256 of the record's JSON with sorted keys.
- tests/test_biohopr_loader.py: row count equals the metadata; row_id unique and 5-digit padded;
  original fields unchanged; a rerun gives identical row_id and row_sha256.
- results/diagnostics/biohopr/inspection_20.md: 20 rows (seed 42) with every field, the first 5
  answers of each row and its answer count.
Also report how many rows have a 2-hop question text containing the hop1 field's text (input to
the LEAKY_QUESTION check, protocol §7.1), with examples.

Do not interpret field roles (which field is the query entity or the bridge). That is S5.
```

**Expect back.** Row count, field list, revision hash, candidate question fields, inspection file.

**Evaluate.**
1. Row count: the paper reports 7,633 2-hop questions. Any difference needs an explanation first.
2. Compare 5 rows of `inspection_20.md` field by field with the Hugging Face dataset viewer.
3. The rerun test (identical `row_id` and `row_sha256`) passes.
4. Choose the question field: the one asking for **all** answers ("Name all …").
5. Note in `progress.md` which field *seems* to be the starting entity (verified at S5).

**Decide.** Protocol §3.1 revision and question field. Log both.

**Commit.** `S2: BioHopR loader, revision pinned`

**Provenance.** Row "BioHopR dataset" (Kim et al., 2025).

---

## S3 — BioHopR diagnostics (no PrimeKG needed)

**Goal.** Know the dataset's shape before designing limits: answer-set sizes, relation-type
counts, and duplicate questions.

**Prompt.**
```text
Implement dataset diagnostics for BioHopR 2-hop rows. Do not use PrimeKG.

Create src/cofail_kg/data/diagnostics.py and scripts/03_biohopr_diagnostics.py producing,
in results/diagnostics/biohopr/:
1. answer_sizes.csv and answer_sizes.png: distribution of answer-list length
   (min, p25, median, mean, p75, p90, p95, p99, max), overall and per relation type.
2. relation_types.csv: count of rows per relation type (use the dataset's own type fields).
3. largest_answers.csv: the 20 rows with the most answers.
4. duplicate_questions.csv: group rows by identical 2-hop question text; for each group with
   more than one row, report how many distinct bridges (hop1 values) and distinct answer
   sets it has. Compare answer lists as sets (order and repeated names ignored; names compared
   as exact strings), per protocol §0.4.
   Also report how many rows contain the same answer name more than once.
5. summary.json with the key numbers.
Add tests on a tiny synthetic table. Do not choose any threshold.
```

**Evaluate.**
1. Compare `relation_types.csv` with the 12 counts in protocol §3.1 (from the paper). Small differences need an explanation; large ones mean something is wrong.
2. Note the answer-size **median, p90 and p99** in `progress.md`. You need them at S21: each answer costs roughly 15–25 output tokens in the JSON format, so the output limit must cover realistic answer lists.
3. Open `duplicate_questions.csv`. If identical question texts appear with different bridges and different answer lists, you have direct evidence of the single-bridge label problem. Note the count; it is a useful sentence for the thesis ("N question texts occur with more than one gold bridge").

**Decide.** Nothing is frozen here. Record the numbers in `progress.md`.

**Commit.** `S3: BioHopR diagnostics`

**Provenance.** None new.

---

## S4 — PrimeKG ingestion and index

**Goal.** Freeze the PrimeKG release, understand its columns and edge storage, build a fast
deterministic index, and give yourself a small inspection tool.

**Do by hand first.** Download PrimeKG's edge file (`kg.csv`), plus the node file if the release
has one, from the PrimeKG page on Harvard Dataverse into `data/raw/primekg/`. Create
`data/cache/primekg_release.json` yourself with the release version / DOI and the download date
(protocol §3.4: this file is not part of the fingerprint).

**Prompt.**
```text
Implement ONLY the PrimeKG ingestion and index layer. Protocol §3.2–§3.4 apply.
Raw files are in data/raw/primekg/.

Before coding, inspect the raw files and report:
1. Column names and 5 example rows; total row count.
2. Which column is a unique node identifier across the whole graph (check; do not assume).
3. Every distinct label (relation) and display label, with row counts and the
   (source type, target type) pairs each connects.
4. Edge storage: for a random sample of 10,000 rows (seed 42), how often the reverse row
   (same label, endpoints swapped) exists — overall and per label.
5. The distinct node types (for the protocol §3.3 type map).

Then implement:
- scripts/04_prepare_primekg.py: SHA256 of every raw file; node and edge tables as parquet in
  data/cache/; data/cache/primekg_metadata.json written by the script only (hashes, row counts,
  columns, canonical ID column, edge-storage findings). Add kg_fingerprint = SHA256 of that
  metadata file to configs/frozen_hashes.yaml. Never edit the metadata file afterwards.
- src/cofail_kg/kg/primekg_index.py: a class loading the cache, offering
    get_node(node_id); find_by_name(name, node_type=None) (exact match after lower-case, NFKC,
    whitespace collapse); relations_of(node_id) (label, display labels, neighbor types, unique
    neighbor count); neighbors(node_id, label=None, neighbor_type=None) sorted by numeric ID;
    degree(node_id) (unique neighbors, all labels).
  Make the edge convention a single configurable component (protocol §3.2) used by every
  traversal, defaulting to "either direction".
- scripts/inspect_kg.py: a command-line tool FOR ME (not for agents):
    python scripts/inspect_kg.py node "Troglitazone"
    python scripts/inspect_kg.py relations <node_id>
    python scripts/inspect_kg.py neighbors <node_id> --relation <label>
- tests/test_primekg_index.py on a tiny synthetic graph.
Report load time and peak memory.
```

**Evaluate.**
1. Look at the raw rows yourself:
   ```powershell
   python -c "import pandas as pd; print(pd.read_csv('data/raw/primekg/kg.csv', nrows=5).T)"
   ```
2. **Row count:** about 4.05 million relationships in the paper; about 8.1 million rows means both directions are stored (should agree with Claude's reverse-row finding).
3. **Release check:** the BioHopR paper says Troglitazone has 202 side effects in PrimeKG.
   ```powershell
   python scripts/inspect_kg.py node "Troglitazone"
   python scripts/inspect_kg.py relations <the ID it prints>
   ```
   About 202 on the side-effect label → your release matches. Far off → resolve before S5.
4. The four BioHopR types exist as PrimeKG node types (the type map).
5. The canonical ID column is unique; `frozen_hashes.yaml` contains `kg_fingerprint`.

**Decide.** Protocol §3.2: release, canonical ID column, edge storage, **edge convention** (list
any directional labels stored one way; otherwise "either direction"); §3.3: type map; §10: whether
`get_neighbors` gets a `direction` argument (only if directional labels were listed). Log all.

**Commit.** `S4: PrimeKG frozen and indexed`

**Provenance.** Row "PrimeKG" (Chandak et al., 2023).

---

## S5 — Field-semantics verification

**Goal.** Prove from data which BioHopR field is the query entity, which is the bridge, and how the
answers connect.

**Prompt.**
```text
Apply the field-role verification rule of protocol §3.1 exactly (5 rows per relation type,
SHA256("42" + row_id) ordering, 95% in every relation type). Use the type map from S4 and
the reference normalization policy (§12).

For each sampled row:
1. Resolve the hop1 and hop2 names to PrimeKG nodes; record unresolved or ambiguous names.
2. Find which labels connect hop1 and hop2.
3. Measure what share of the answer names are neighbors of hop1 and of hop2.
Write results/semantics/field_roles.csv and a per-relation-type summary of the evidence.
State a conclusion only if the §3.1 rule is met; otherwise stop and report conflicting rows.
```

**Evaluate.**
1. Which role assignment does the evidence support, and how strongly?
2. Hand-check 3 rows with `scripts/inspect_kg.py`: the query entity's neighbors include the bridge; the bridge's neighbors include several gold answers.
3. Many unresolvable names suggest a release mismatch (back to S4 check 3).

**Decide.** Protocol §3.1 field roles. Log.

**Commit.** `S5: field roles verified`

**Provenance.** None new.

---

## S6 — Relation mapping and ambiguity tags → Gate D1

**Goal.** Find, from BioHopR's own answers, which PrimeKG labels each hop uses; compute the
ambiguity tags by code. No agent exists yet, and no manual judgment is needed.

**Prompt.**
```text
Implement protocol §5 exactly. Use the field roles frozen at S5 and the type map from S4.

For each of the 12 relation types:
1. List hop-1 candidate labels (connecting Type_S and Type_B) and hop-2 candidate labels
   (connecting Type_B and Type_T), from PrimeKG's `relation` column, with display labels for
   information.
2. Draw the validation sample exactly as §5.1 says (SHA256("42" + row_id) ordering, first 30
   rows whose query entity and bridge resolve); report how many rows were skipped as unresolved.
3. For every non-empty subset of candidates, compute the hop-1 score and the hop-2 score (§5.1).
4. Select per hop by §5.1 (highest score, then smallest set). If a tie remains, report it as a
   TIE and do not choose.
5. Compute the ambiguity tag per relation type by the §5.2 rule.
6. Compute the D1 quantities from docs/decision_rules.md and the D1 outcome.

Write:
- results/semantics/relation_mapping_candidates.csv (every candidate set, both scores)
- results/semantics/relation_mapping_proposed.json
- results/semantics/relation_ambiguity_tags.csv
- results/semantics/d1_report.md
Do not freeze anything.
```

**Evaluate.**
1. For each relation type, look at the selected labels. Do they make biomedical sense for the
   question wording? (A sanity check only; the scores decide.)
2. For every type that fails D1, ask Claude to print two failing rows with the difference between
   reached targets and BioHopR's list. Common causes: field roles, edge storage, name normalization.
   Fixing a cause is allowed; lowering a threshold is not.
3. For any TIE, decide yourself from the failing rows; log it.
4. Look at the ambiguity tags: how many relation types are NONE? That is the size of your
   "clear wording" pile later.

**Prompt, part 2 (after D1 says PROCEED).**
```text
Freeze the mapping I approved: write results/semantics/relation_mapping.json, mark excluded
relation types, recompute relation_ambiguity_tags.csv from the frozen mapping, and add
relation_mapping = SHA256 of relation_mapping.json to configs/frozen_hashes.yaml.
Change nothing else.
```

**Decide.** Gate **D1**; mapping frozen; tags frozen; excluded types listed. Log all, with numbers.

**Commit.** `S6: relation mapping and ambiguity tags (D1: PROCEED)`

**Provenance.** Own (mapping procedure, ambiguity rule).

---

# Part 4 — Phase C: Reference sets and sampling

## S7 — Reference sets

**Goal.** Group rows into queries and compute the valid bridges and question-valid answers exactly
as protocol §4 and §6 define them.

**Prompt.**
```text
Implement protocol §0.4 (query definition), §4, §6 and §12 (reference policy) for all relation
types that passed D1.

Create src/cofail_kg/evaluation/reference_sets.py and scripts/07_build_reference_sets.py.
1. Resolve each row's query entity (reference policy, Type_S). Group rows by (resolved node s,
   relation type); a row whose query entity does not resolve forms its own query.
   query_id = row_id of the lowest-index row. Record each query's row_ids and question texts.
2. Resolve each gold bridge (Type_B) and gold answer (Type_T) with the reference policy.
   Implement the protocol §12 REFERENCE policy in src/cofail_kg/evaluation/normalize.py (the agent
   policy comes at S16).
3. Compute T_q(b), B_q (bridges with non-empty T_q(b)), dead-end bridges, T_q, and T_q^{B*}
   with the frozen relation_mapping.json and the §3.2 edge convention.
Output to data/processed/:
- reference_queries.parquet: query_id, row_ids, s, gold bridges, Type_S/B/T, relation type,
  sizes of B_q, dead-end set, T_q, T_q^{B*}, A*_q; unresolved names listed
- reference_targets.parquet: one row per (query_id, bridge, target) for b in B_q, t in T_q(b)
Tests on a synthetic graph: one bridge; several bridges; a target via two bridges; a dead-end
bridge (excluded from B_q); no valid bridge; two rows of the same query merged correctly;
type filtering; two names resolving to one node grouped together; an unresolvable query entity
forming its own query. Nothing agent-facing may import these files.
```

**Evaluate.**
1. Pick one SINGLE-bridge and one MULTI-bridge query. With `scripts/inspect_kg.py`, list the query
   entity's neighbors through the R1 label(s) of type Type_B; compare with the bridges in the output.
2. For one bridge, list its R2 neighbors of type Type_T; compare with `reference_targets.parquet`.
3. Find a query built from two or more rows (if any) and check its gold answers are the union.

**Decide.** Nothing.

**Commit.** `S7: queries and reference sets`

**Provenance.** Row "answer set by executing the query pattern" (Yih et al., 2016).

---

## S8 — Query validation

**Goal.** Label every query CONSISTENT/INCONSISTENT, count its bridges, and measure saturation.

**Prompt.**
```text
Implement protocol §7.1 exactly.
Create src/cofail_kg/evaluation/query_validation.py and scripts/08_validate_queries.py.
For each query: CONSISTENT/INCONSISTENT (the five conditions of §7.1), all applicable reason
codes (NA where §7.1 says so) plus the primary reason in the §7.1 order, bridge multiplicity,
dead-end bridge count, the LEAKY_QUESTION flag, and saturation share.
Mark whether the query contains any S6 validation-sample row (needed for D2 step 1).
Write results/diagnostics/query_validation.csv and query_validation_summary.json with counts by
status, primary reason, relation type, multiplicity, and ambiguity tag.
Tests: one synthetic case per reason code; several codes at once (primary by order); a gold
bridge that resolves but is not in B_q; an unmapped gold name with the rest matching (must be
INCONSISTENT); differing question texts; a question naming its bridge (LEAKY_QUESTION).
Do not exclude anything.
```

**Evaluate.**
1. What share is CONSISTENT overall and per relation type?
2. Open 5 INCONSISTENT queries with the most common primary reason. A pattern that looks like a
   bug (e.g., a naming problem) gets the bug-found prompt; a real discrepancy stays.
3. Look at 5 CONSISTENT MULTI_BRIDGE queries: how many bridges do they typically have?

**Decide.** Nothing yet.

**Commit.** `S8: query validation`

**Provenance.** None new.

---

## S9 — Mapping confirmation, saturation, feasibility → Gate D2

**Goal.** Confirm each mapping on queries it was not chosen from, fix the saturation threshold,
then check there are enough usable queries.

**Prompt, part 1.**
```text
Do not compute D2 step 3 yet.
1. D2 step 1: for each relation type that passed D1, the CONSISTENT share among queries that
   contain no S6 validation-sample row. Flag types below 80% and types with no such queries
   (UNCONFIRMABLE).
2. For CONSISTENT queries in confirmed or UNCONFIRMABLE types: the saturation-share distribution (p50, p90, p95,
   p99, max) and how many queries would be excluded at θ = 0.30, 0.50, 0.70, 0.90, overall and per
   relation type.
```

**Evaluate and decide.**
1. Any type below 80%? Follow D2 step 1: revise its mapping (log it, re-apply D1 to that type,
   rerun S7–S8, repeat step 1) or exclude it (log it). Both are allowed because no agent exists yet.
2. Choose θ (recommended 0.50). Keep it unless the table shows it removes a whole relation type for
   no good reason. Write θ into protocol §7.2 and log it **before** part 2.

**Prompt, part 2.**
```text
Using θ = <X> (now in protocol §7.2), compute the primary population (§7.2) and D2 step 3
exactly as in docs/decision_rules.md, in the stated order. Report N_P, K, per-type counts,
single/multi counts, and the outcome. Write data/processed/primary_population.csv.
```

**Decide.** Gate **D2**. Log with the numbers.

**Commit.** `S9: primary population (D2: <outcome>)`

**Provenance.** Own (saturation rule, mapping confirmation).

---

## S10 — Sampling manifests and agent-input sheets

**Goal.** Draw the screening, smoke, pilot and expansion sets exactly as protocol §8 says, and
write the separate agent-input sheets the agents will read.

**Prompt.**
```text
Implement protocol §8 exactly.
Create src/cofail_kg/data/sampling.py and scripts/10_make_samples.py.
Input: data/processed/primary_population.csv and the S7 reference data.
Outputs:
- data/processed/manifests/screening.jsonl, smoke.jsonl, pilot.jsonl, expansion.jsonl —
  each line: query_id, relation_type, multiplicity, ambiguity_tag, tq_size_bin
- data/agent_inputs/screening.jsonl, smoke.jsonl, pilot.jsonl, expansion.jsonl — each line has
  EXACTLY the four fields query_id, question_text, start_name, start_id (protocol §8)
- data/processed/manifests/sampling_report.md: counts per stratum per set, and any shortfall
- the SHA256 of every manifest and sheet added to configs/frozen_hashes.yaml (manifests key)
Fill configs/pilot.yaml with the seed, set sizes and file paths.
Tests: byte-identical outputs on rerun; disjoint sets; sizes and shortfall rule; floors applied
within each multiplicity group; largest-remainder ties broken by relation-type name; the
SHA256("42" + query_id) ordering of §8 step 3; agent-input lines have exactly four fields.
```

**Evaluate.**
1. Run the script twice; the hashes in `frozen_hashes.yaml` must not change.
2. Disjointness:
   ```powershell
   python -c "import json;s=lambda f:{json.loads(l)['query_id'] for l in open('data/processed/manifests/'+f)};a,b,c,d=s('screening.jsonl'),s('smoke.jsonl'),s('pilot.jsonl'),s('expansion.jsonl');print(len(a&b),len(a&c),len(b&c),len(c&d))"
   ```
   All zeros.
3. `sampling_report.md`: single/multi mix close to 25/75 in the pilot; every PASS type represented.
4. Open `data/agent_inputs/pilot.jsonl`: each line has only the four fields. Read 10 questions to
   get a feel for what the agents will face.

**Decide.** Confirm the 25/75 default (protocol §8); manifests frozen. Log.

**Commit.** `S10: sampling manifests and agent-input sheets`

**Provenance.** None new.

---

# Part 5 — Phase D: Agent system

## S11 — KG tools

**Goal.** Build the only door the agents have into PrimeKG: deterministic, paginated, logged, and
blind to evaluation data.

**Prompt.**
```text
Implement ONLY the agent-facing KG environment. Protocol §10 applies exactly, using the edge
convention component from S4.

Create src/cofail_kg/agents/kg_env.py:
- class KGEnvironment on the read-only PrimeKG index.
- inspect_entity(entity_id): id, name, type; for each label touching it: label, display label(s),
  neighbor type(s), unique neighbor count. Labels sorted alphabetically.
- get_neighbors(entity_id, relation, neighbor_type=None, page=1): items (id, name, type, display
  label) sorted by numeric ID; total_count, page, page_size, has_more. Empty results are a
  successful page 1 with total_count 0. <Add a direction argument ONLY if protocol §10 says so.>
- Errors use exactly the §10 templates and echo only the agent's own arguments.
- A call budget; once used, every call returns the §10 budget message.
- page_size and budget come from the configuration object (screening values 50/30 are in
  protocol §9.1; final values come at S21).
- An in-memory call log: arguments, full result, success flag, timestamp.

Create src/cofail_kg/agents/tool_schemas.py: the two tools as JSON function definitions for
Ollama's chat API (tool version T1). Descriptions must be neutral (protocol §10) — draft them and
show them to me for approval.

The module must not import cofail_kg.evaluation or open files under data/processed/ — add a test.
Tests (synthetic graph): listing and counts; neighbor-type filter; ordering; pages 1+2 union equals
the full list with no duplicates; last page; empty list; each error template; budget exhaustion;
import isolation.
After my approval of the descriptions, add tools = SHA256 of tool_schemas.py to
configs/frozen_hashes.yaml.
```

**Evaluate.**
1. Try the tools on a real entity (the query entity of one screening query):
   ```python
   from cofail_kg.kg.primekg_index import PrimeKGIndex   # use the actual class name
   from cofail_kg.agents.kg_env import KGEnvironment
   env = KGEnvironment(PrimeKGIndex(), page_size=50, budget=30)
   print(env.inspect_entity("<id>"))
   p1 = env.get_neighbors("<id>", "<a label from the list>", page=1)
   print(p1["total_count"], p1["has_more"], [x["id"] for x in p1["items"]][:5])
   ```
2. Compare `total_count` with `python scripts/inspect_kg.py neighbors <id> --relation <label>`.
3. Page through until `has_more` is false; the union has exactly `total_count` items in ascending ID order.
4. Read the tool descriptions: do they hint at any answer or relation choice? They must not.

**Decide.** Approve the tool descriptions as **T1** (protocol §10). Log.

**Commit.** `S11: KG environment and tool schemas (T1)`

**Provenance.** Rows "Graph-CoT", "Think-on-Graph" (design); own (pagination, ordering, budget).

---

## S12 — Trace and trace graph

**Goal.** Record everything an agent sees and does, and turn it into the trace graph all path
labels come from.

**Prompt.**
```text
Implement protocol §11 and the primary-path order of §14.2.
Create src/cofail_kg/agents/trace.py:
- The episode record (JSON) with every field of protocol §19, all messages and the call log.
- A write-once saver: results/runs/<run_id>/<query_id>__<agent_id>__a<attempt>.json; refuses to
  overwrite.
- build_trace_graph(record): edges (u, label, v) for each neighbor on each returned page of each
  successful get_neighbors call, oriented per the edge convention, each with its creation index
  (the first successful call that returned it).
- appeared_entities(record): every entity returned by any successful call (neighbors and
  inspect_entity subjects).
- paths(trace_graph, s, x): all simple paths of length ≤ 3, and the primary path (shortest path of
  any length, ordered exactly by §14.2: length, then largest creation index, then the sequence of
  (numeric node ID, label) pairs).
Tests with hand-written records: only returned page items become edges; creation indexes; parallel
edges with different labels are both kept and ordered by §14.2; numeric (not string) ID order;
saver refuses to overwrite.
```

**Evaluate.** Draw one test case's trace graph on paper and compare with the test's assertions,
including the parallel-edge case.

**Commit.** `S12: trace and trace graph`

**Provenance.** Row "KG-TRACES" (path-level traces); own (construction rules).

---

## S13 — Ollama client

**Goal.** A thin, reliable wrapper around Ollama's chat API that records what reproducibility needs.

**You need first.** Ollama running (`ollama list` works). Pull one small model for testing and
check that `ollama show <model>` lists **tools** under Capabilities.

**Prompt.**
```text
Implement src/cofail_kg/agents/ollama_client.py:
- chat(model, messages, tools, options) via Ollama's local HTTP API; options temperature, seed,
  num_ctx, num_predict always passed explicitly.
- Returns the raw response, the assistant message, native tool calls, prompt_eval_count,
  eval_count, latency.
- get_model_identity(model): tag, digest, quantization, parameter size.
- Classify failures into the protocol §9.5 ERROR causes (OUT_OF_MEMORY, CONNECTION, RUNTIME,
  OTHER); document how OUT_OF_MEMORY is detected.
- Request timeout from configuration. Retries (engineering choice): connection errors only, at
  most 2, logged; never retry because of reply content.
- Unit tests with a mocked HTTP layer, including each error cause.
- scripts/13_test_ollama.py: one plain call and one tool call (dummy tool add(a, b)), printing
  identity, token counts, latency, and whether a native tool call came back.
```

**Evaluate.** Run `python scripts/13_test_ollama.py`: you see the digest, token counts, and a
native tool call. (Whether a model is usable is decided later by Gate D3, not here.)

**Commit.** `S13: Ollama client`

**Provenance.** Row "Ollama" (software).

---

## S14 — Agent prompt and runner

**Goal.** One complete episode: the question in, tool calls executed, JSON answer out, full trace saved.

**The P1 template (draft — review it, then give it to Claude).** `{PAGE_SIZE}` and `{BUDGET}` are
filled from the configuration; the template itself is what gets hashed (protocol §9.3).

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

User message template (protocol §9.3):
```text
{QUESTION}
Starting entity: {START_NAME} (PrimeKG ID: {START_ID})
```

**Prompt.**
```text
Implement the agent runner. Protocol §9.2–§9.5 apply exactly.

1. src/cofail_kg/agents/prompts.py: the P1 template and the user template I give below, VERBATIM,
   with PROMPT_VERSION = "P1" and a function returning the template's SHA256. <paste both texts>
2. src/cofail_kg/agents/run_agent.py: run_episode(query_id, agent_config, run_config) that
   - reads the query's line from the agent-input sheet (data/agent_inputs/<set>.jsonl) — the ONLY
     data file it may open besides the PrimeKG cache;
   - builds the two messages from question_text, start_name and start_id;
   - executes ONLY native tool calls through KGEnvironment; records TEXT_TOOL_CALL per §9.5
     without executing it;
   - stops per §9.4 (final message rules, budget message, one extra turn after it);
   - parses per §9.4 (string or integer IDs, fences, extra keys, empty lists, one fixed re-prompt);
   - assigns the status per §9.5 with its precedence (TIMEOUT, ERROR with cause, PARSE_FAIL,
     SUCCESS);
   - saves the record with the S12 saver, attempt 1.
Tests with a mocked client: normal episode; budget exhaustion; tool calls after the budget message
ignored; fenced JSON with a language tag; integer IDs; "answered" with an empty list; parse failure
then success; PARSE_FAIL; timeout during the re-prompt (TIMEOUT wins); TEXT_TOOL_CALL detection and
non-execution.

Then run ONE real episode: the first query of the screening sheet, with the test model from S13 and
the full screening configuration of protocol §9.1 (num_ctx 8192, num_predict 4096, page size 50,
budget 30, timeout 10 minutes). Print the record's path.
```

**Evaluate — read the real episode record line by line.**
1. The user message contains only the question and the starting-entity line.
2. Every tool call is well-formed, and its result matches `scripts/inspect_kg.py` for the same call.
3. You can follow the route: first label chosen, bridge(s), targets.
4. The final JSON parsed; answer IDs appeared in earlier tool results.
5. Token counts are recorded; the prompt token count is well below `num_ctx`.

**Decide.** Approve the template as **P1** (protocol §9.3). Add `prompt` = template SHA256 to
`configs/frozen_hashes.yaml`. Log it; the text goes in the thesis appendix.

**Commit.** `S14: agent runner and prompt P1`

**Provenance.** Row "ReAct" (loop); own (prompt, parsing rules).

---

## S15 — Leakage audit

**Goal.** Prove nothing from the evaluation side reaches the agents.

**Prompt.**
```text
Do not change existing behavior. Implement the leakage test of protocol §19.1 exactly as
tests/test_leakage.py and run it on the screening and smoke queries (messages only; no model calls).
It must check:
(a) system prompt and starting-entity line contain none of: R1/R2 labels, any gold bridge or gold
    answer name or ID, names of other B_q or T_q members, the relation-type string, evaluator label
    names — case-insensitive whole-word matching; names shorter than 4 characters listed for my
    manual review instead;
(b) agent-facing modules (kg_env, tool_schemas, prompts, run_agent) import nothing from
    cofail_kg.evaluation and open no files except data/agent_inputs/ and the PrimeKG cache;
(c) every agent-input sheet line has exactly the four §8 fields;
(d) for 10 random (entity, label) pairs, get_neighbors returns exactly the index's neighbors.
Print the exact system and user messages for one screening query.
Report each check's result and the list of short names for manual review.
```

Note: labels and answer entities *will* appear inside tool results and may appear in the question
text itself. That is the task, not leakage; questions that name their own bridge or answers were
already excluded at S8 (LEAKY_QUESTION).

**Evaluate.** All checks pass. Read the printed messages slowly: could an agent learn anything it
should find with the tools? Review the short-name list.

**Commit.** `S15: leakage audit passes`

**Provenance.** None new.

---

# Part 6 — Phase E: Evaluation core

These modules are built before model screening because the screening criteria (D3) use them.
They are tested on synthetic data plus the real episode from S14.

## S16 — Answer normalization

**Prompt.**
```text
Implement the AGENT policy of protocol §12 in src/cofail_kg/evaluation/normalize.py (the
reference policy already exists from S7; do not change it).
Input: an agent's parsed answer list and the query's Type_T. Output per item: resolved node ID or
UNRESOLVED with reason (AMBIGUOUS_NAME / NO_MATCH), resolution method (ID / NAME_TARGET_TYPE /
NAME_UNIQUE_ANY_TYPE), NAME_ID_MISMATCH flag; duplicates removed after resolution (report how many).
No fuzzy or embedding matching.
Tests: string ID; integer ID; invalid ID with a matching name; a name matching two nodes where
exactly one has Type_T; a name matching two nodes of Type_T (UNRESOLVED); a name matching exactly
one node of another type (resolves to it); no match; ID and name disagreeing; duplicates.
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
T_q^{B*} and A*_q (must be GOLD); an entity reachable through two bridges.
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
- the answer x = s, in a fixture where s appeared (PATH_INVALID, WRONG_HOP_COUNT); and x = s
  where s never appeared (UNGROUNDED)
- a length-1 path to a wrong-type node (WRONG_TARGET_TYPE and WRONG_HOP_COUNT)
- H1 when the answer itself is the Type_B neighbor of s (H1 = 0, since b must differ from x)
- an only path of length 4 (primary path found by breadth-first search; WRONG_HOP_COUNT)
- an UNRESOLVED answer (Label B = NOT_APPLICABLE)
- INVARIANT: across all tests and the real episode, assert no answer is both OFF_QUESTION
  and SUPPORTED
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

**You need first.** Choose 6–8 candidates: `ollama show <model>` lists **tools**; the model fits
your GPU (with 8 GB VRAM, roughly ≤ 9B parameters at 4-bit quantization); several model families
(for example Qwen, Llama, Mistral, Granite, Phi — check each one's tool capability yourself). Pull
them with `ollama pull`.

**Prompt.**
```text
Create scripts/20_screen_models.py using the S14 runner and S16–S19 evaluation, with the screening
configuration of protocol §9.1 exactly.
Candidates: <list of Ollama tags>.
Run every candidate on the 20 screening queries, one model loaded at a time. Save episode records
(write-once) under results/runs/screening/.
Write results/diagnostics/screening/screening_table.csv with, per model, every Gate D3 quantity
exactly as D3 defines it: well-formed / attempted calls (attempted includes TEXT_TOOL_CALL),
share of SUCCESS episodes, competence, median wall time, number of ERROR episodes with cause
OUT_OF_MEMORY — plus, for S21: largest prompt_eval_count, median tool calls used, share of
episodes that hit the budget, family, digest. Add the D3 pass/fail per criterion.
Do not select models.
```

**Evaluate.**
1. Read `screening_table.csv` against D3.
2. For each passing model, read 2 episode records. Numbers can pass while behavior is odd (e.g., always answering with the first 5 items seen).

**Decide.** Nothing frozen yet (S21).

**Commit.** `S20: model screening` (the table only; records in `results/runs/screening/` are backed up, not committed).

**Provenance.** Row "each model" (technical report or model card).

---

## S21 — Freeze models and engineering limits → Gate D3

**Goal.** Choose the four agents and set every final runtime value, using the rules in protocol §9.1.

**Decide (you).**
1. Apply Gate D3 to choose four models.
2. Apply the §9.1 rules for `num_ctx`, page size, budget, `num_predict` and timeout. If any chosen
   model's largest screening prompt count exceeds 0.8 × 8192, first run this prompt:
   ```text
   Rerun 5 screening queries for <model> with num_ctx 16384 (other screening settings unchanged)
   as run ID screening_ctx16k, and report the largest prompt_eval_count and any OUT_OF_MEMORY.
   ```
3. Write each value and the rule that produced it in the decision log. Fill protocol §9.1's
   `[TBD@S21]` items.

**Prompt (after deciding).**
```text
Write configs/models.yaml with the four agents (agent_id, Ollama tag) and each model's digest,
quantization, parameter size and family from get_model_identity(); add the models entry to
configs/frozen_hashes.yaml. Write the final runtime values into configs/pilot.yaml. Add a check
that fails if an installed model's digest differs from frozen_hashes.yaml.
Do not change protocol files.
```

**Evaluate.** `git diff configs/` shows exactly your values; the digest check passes.

**Commit.** `S21: models and runtime frozen (D3)`

**Provenance.** Model rows filled with exact tags.

---

## S22 — Single-agent smoke test

**Goal.** See the four frozen agents on real questions with the final settings, and exercise the
evaluation code on real traces.

**Prompt.**
```text
Run each of the four frozen agents on all 20 screening queries with the final configuration, as
run ID smoke_single. Run S16–S19 evaluation on all 80 episodes and write
results/diagnostics/smoke_single_summary.md: per model — status counts (with ERROR causes),
Label A and Label B distributions, reason codes, hop-1 statuses, early-stop share, budget-hit share,
largest prompt tokens versus num_ctx. Assert that no answer is both OFF_QUESTION and SUPPORTED.
Do not interpret.
```

**Evaluate — manual reading (plan 2–3 hours).**
1. Read at least one full episode per model.
2. Check Label A and Label B by hand for 6 answers across models.
3. Any episode with prompt tokens above 90% of `num_ctx`, or any OUT_OF_MEMORY error: apply the
   protocol §9.1 re-selection rule with the S22 measurements (log it).
4. Systematic technical problems (a model never calls tools; JSON always fails): return to S21 (log it).

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
- pairwise agreement on a hand-computed example; a pair with no shared-error queries → NA
- a primary path violating both hops → two wrong-turn events
- PCF_NODE ignores s and the answer itself
```

**Evaluate.** Read the toy tests and confirm each expected value against protocol §16 yourself.

**Commit.** `S23: co-failure metrics`

**Provenance.** Row "Kim et al. 2025" (pairwise agreement, adapted); own (rest).

---

## S24 — Chance baselines

**Prompt.**
```text
Implement protocol §17 exactly in src/cofail_kg/evaluation/null_models.py: nulls N1, N1-H1 and
N2, each with its own pool, observed set and observed total (O_N1, O_H1, O_N2) as in the §17
table; 10,000 trials; the §17 random-number scheme (SeedSequence([42, h, v]), agents in ascending
order, Generator.choice without replacement on pools sorted by numeric ID); per-query null
probabilities; aggregate totals, 95th percentile and p — for the 3-agent and 4-agent versions.

Tests:
- REQUIRED: all agents give the same single wrong answer, each saw 200 other wrong
  candidates of Type_T → null CF3 probability is small (< 0.01)
- tiny pools: every agent's pool contains only the same single entity, which each agent
  answered → null probability 1
- each observed set is a subset of its pool, for N1, N1-H1 and N2 (assert)
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
- Checkpoints after every episode; on restart skips every completed episode — a record with
  ANY §9.5 status, including failures (protocol §19) — and never overwrites. Failed episodes
  are rerun only in the cases protocol §19 allows, as new attempts under a new run ID.
- Writes a progress file (episodes done / total, failures so far).
- After the run: evaluation (S16–S19, S23, S24) → results/runs/<run_id>/analysis/.
Tests: resume after a simulated crash (no duplicates, nothing missing), digest mismatch
refusal, write-once.

Then run the smoke manifest (4 queries × 4 agents = 16 episodes) as run_id "smoke_panel",
and run the protocol §19.1 leakage test on the smoke queries.
Halfway through, I will stop the process; tell me the exact moment to press Ctrl+C.
Then restart the same command and confirm completion without duplicates.
Produce results/runs/smoke_panel/analysis/ and an audit sheet
results/runs/smoke_panel/audit_sheet.csv listing the 8 episodes chosen by the protocol §19.1
audit-selection rule, with columns:
episode, answer_id, label_A, label_B, primary_path, my_label_A, my_label_B, notes
(leave my_* empty).
```

**Evaluate — your manual audit.**
1. Do the kill-and-resume exactly as instructed; check the episode count is 16 with no duplicates.
   (If audit selection finds fewer than 8 eligible episodes, audit all that exist — protocol §19.1.)
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
1. List any unfilled [TBD@Sx] with x ≤ 26, and any unconfirmed [DEFAULT] with stage ≤ 26.
2. Run the full test suite.
3. git status must be clean; print the commit hash.
4. Recompute every hash listed in configs/frozen_hashes.yaml (KG fingerprint, relation mapping,
   tool schema, prompt template, pilot manifest, pilot agent-input sheet) and compare.
5. Compare the BioHopR revision and the installed model digests with frozen_hashes.yaml.
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
- If failures pile up with the same error (e.g., every episode of one model times out), **stop the run first**. Fix it with the bug-found prompt (no definition changes) and follow protocol §19 "code changes during a run": earlier episodes are kept only if a decision-log entry explains why the fix cannot have affected them; otherwise they are rerun as new attempts under the new commit.
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
4. Chance baselines: N1 vs O_N1, N1-H1 vs O_H1, N2 vs O_N2 (protocol §17): observed total,
   null mean, 95th percentile, p — 3-agent and 4-agent versions.
5. Strata: all co-failure metrics by ambiguity tag, by SINGLE/MULTI bridge, by relation type.
6. Ordering: distribution of explored-bridge ranks (§15); FIRST_SEEN_PAGE of shared wrong answers;
   list sizes (fan-out) on the primary paths of shared wrong answers.
7. Case sheets: for EVERY query with CF3^{Q,H1}=1, one page: the question, each co-failing
   agent's primary path to the shared entity, reason codes, the shared node's degree
   percentile, ambiguity tag.
Also compute the D6 quantities (E on latest attempts, H, N, O_H1 vs N1-H1, P) and both
interpretation flags, but do not state the outcome.
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

**If GREEN or YELLOW — freeze Phase 2 now.** Before S30, revise protocol §21 using what the
pilot showed (which mechanisms occur), mark it `[FROZEN]`, and log that it was frozen after
seeing pilot data. D7 depends on this frozen rule.

**Decide.** Record in the decision log: outcome, all five quantities, both flags, and the next
step (S30 expansion, or descriptive write-up). Discuss with your supervisor before starting Phase I.

**Commit.** `S29: pilot decision — <outcome>`

---

# Part 10 — Phase I: After the pilot (provisional)

These stages depend on the pilot. Protocol §21 is frozen at S29 (after D6, before S30); the
prompts below are templates to be adjusted to that frozen version.

## S30 — Run the expansion reserve → Gate D7

```text
First repeat the S26 checks, adding the expansion manifest and expansion agent-input sheet hashes
from configs/frozen_hashes.yaml. Then run scripts/25_run_panel.py --manifest expansion
--run-id expansion_v1. Everything frozen stays identical.
Regenerate the report over pilot + expansion queries (S28 script) and compute D7's quantities,
including C = number of candidate queries meeting the protocol §21 candidate rule (frozen at S29)
with a matched control. Do not state the outcome.
```
You apply D7 yourself and log it.

## S31 — Intervention candidates and design freeze

```text
Using only the frozen 500-query analysis, list every query meeting the protocol §21 candidate
rule (frozen at S29). For each: shared entity, the shared feature chosen by the §21 rule, its
mechanism (SHORTCUT / WRONG_TURN_HOP1 / WRONG_TURN_HOP2 / OFF_PATH_NODE), whether a
valid route (§21) remains after blocking it, and up to 3 matched-control candidates by the §21
matching rule. Write results/interventions/candidates.csv. Do not select cases; list all.
```
You choose one control per case: the closest by the §21 rule (if tied, the one with the smaller
numeric node ID — written in the decision log before any intervention runs).

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
results/interventions/candidates.csv. Verify for both: a valid route (protocol §21) remains,
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

Apply D8; log it. If scaling, draw new sets with the protocol §8 algorithm from queries not yet
drawn (D8), then repeat S30–S36.

## S38 — Final analysis and thesis tables

```text
Produce the final tables:
1. Dataset: CONSISTENT/INCONSISTENT by reason; SINGLE/MULTI; relation types; ambiguity tags;
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
| `prompt_eval_count` close to `num_ctx` | Long tool outputs fill the context; Ollama may drop earlier messages | Before S26: apply the protocol §9.1 re-selection rule (log it). From S26 on: do not change; report affected episodes. |
| Out-of-memory from Ollama | `num_ctx` too large for 8 GB VRAM | Before S26: apply the protocol §9.1 re-selection rule; if no value fits, choose another model through Gate D3 (S21). Log it. |
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
