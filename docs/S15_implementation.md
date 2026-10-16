# S15 leakage audit — 2026-10-16

> **Superseded status (2026-10-16): S15 accepted by the researcher.** See the
> final section "S15 manual review and approval". The status text below is
> historical and kept unchanged.

**Implemented and executed; S15 is NOT accepted.** Protocol §19.1(a) has one
strict whole-word match. The researcher explicitly chose “Keep strict failure;
decide a remedy later.” No exception, exclusion or scientific-rule change was
made. Checks (b), (c) and (d) pass within the coverage described below.

## 1. Files created or changed

- `tests/test_leakage.py`: synthetic checker regressions and real-data S15 checks.
- `results/diagnostics/s15/audit.json`: frozen/input identities, all 24 captured
  initial message pairs, query-level scan counts, failures, short names, import/I/O
  inventory, observed reads, and reproducible neighbor pairs.
- `results/diagnostics/s15/example_messages.txt`: exact system and user messages for
  the first screening query, BH2_00461, also printed by pytest.
- `results/diagnostics/s15/short_names.json`: the complete manual-review list.
- Raw verification logs: `red.txt`, `green-helpers.txt`, `audit-first.txt`,
  `audit.txt`, `full-suite.txt`, `full-suite-final.txt`; `audit-first.json` preserves
  the first real audit's extracted evidence. Initial failed runs are retained.
- This report, `docs/progress.md`, `docs/decision_log.md`, `tasks/plan.md` and
  `tasks/todo.md` document execution and the retained failure.

No production module, input data, model configuration, protocol, decision rule,
frozen hash or existing episode was changed. No new dependency, commit or push.

## 2. Tests run and results

All commands ran inside the restricted Windows workspace sandbox using the
existing `.venv/Scripts/python.exe`; no model calls and no test exclusions/skips.

| Run | Command after `.venv/Scripts/python.exe` | Result |
|---|---|---|
| Checker RED | `-m pytest tests/test_leakage.py -q --basetemp results/diagnostics/s15/temp-red` | 20 failed as intended: audit helpers not yet implemented |
| Checker GREEN | `-m pytest tests/test_leakage.py -q --basetemp results/diagnostics/s15/temp-green-helpers` | 20 passed, 0.98 s |
| First real audit | `-m pytest tests/test_leakage.py -q -s --basetemp results/diagnostics/s15/temp-audit-first` | 23 passed, 1 strict audit failure, 4.76 s |
| Final focused audit | `-m pytest tests/test_leakage.py -q -s --basetemp results/diagnostics/s15/temp-audit-final` | 25 passed, 1 strict audit failure, 4.50 s |
| First full suite | `-m pytest -q --basetemp results/diagnostics/s15/temp-full` | 382 passed, 2 failed, 16.72 s |
| Final full suite | `-m pytest -q --basetemp .pytest_tmp_s15_full` | **383 passed, 1 failed, 17.27 s** |

The first full suite's additional failure was an existing S11 subprocess guard
rejecting a synthetic cache under `/results/`. Moving temporary storage outside
that directory resolved it without changing any test or production behavior.
The final suite contains all 358 prior tests and 26 new cases; its only failure
is `test_a_real_screening_and_smoke_messages`. Exit status remains 1 deliberately;
the failure was neither skipped nor marked xfail. Temporary fixtures were removed
after execution; logs and diagnostic evidence are retained.

| Protocol §19.1 check | Result and evidence |
|---|---|
| (a) Messages | **FAIL**: 20 screening and 4 smoke queries scanned. Exactly one match, detailed below. System prompts have no matches. The question body is preserved verbatim and is outside the prohibited-term scan. |
| (b) Imports and input reads | **PASS on audited paths**: all four named agent modules and a closure of 13 local modules inspected; no evaluation imports. Guarded real cache construction reads only its metadata and two Parquet files. All 24 runner initial-message captures read only their agent sheet. The sampled tool calls perform no additional file reads. |
| (c) Sheet schema | **PASS**: exactly the four §8 fields in all 524 lines: screening 20, smoke 4, pilot 100, expansion 400. Frozen sheet hashes match. |
| (d) Tool fidelity | **PASS**: 10 distinct pairs from 290,302 incident entity/label pairs, seed 42. Complete output equality across 12 pages and 187 neighbors, including names, IDs, types, display labels, ordering and metadata. |

Checker regressions cover punctuation and whole-word boundaries; case differences;
short-name reporting without exempting short IDs/labels; each gold vocabulary
source and other B_q/T_q names; extra sheet fields; direct/relative/transitive and
dynamic evaluation imports; forbidden Python/pathlib/os/Parquet reads; write and
network refusal; and corrupted neighbor items and pagination metadata, including
the second page. Real-data tests are integration checks, separate from the tiny
synthetic regression cases in the same test module.

## 3. Small real example and output

The first screening query BH2_00461 passes its message scan. Its exact user message:

```text
Name all diseases that are related to a gene/protein that is associated with drug 2,6-dimethyl-4-[(E)-2-phenylethenyl]phenol.
Starting entity: 2,6-dimethyl-4-[(E)-2-phenylethenyl]phenol (PrimeKG ID: 14097)
```

The complete exact system/user pair is in `example_messages.txt`, in the focused
test's printed output, and in `audit.json`.

The single failed real example is screening query **BH2_04007**:

```text
Name all effect/phenotypes which are side effects of drug that can treat disease folic acid deficiency anemia.
Starting entity: folic acid deficiency anemia (PrimeKG ID: 83880)
```

The required case-insensitive whole-word rule matches **Folic acid**, the name of
node **14678**, inside the starting-entity line. It is an additional valid B_q
bridge; the gold bridge is **Cyanocobalamin**, node **14706**. Thus the match is
not an injected evaluation field or a gold-bridge identity, but still fails the
literal rule banning names of other B_q members. The starting name is the actual
PrimeKG name and remains unchanged. This observation does not establish a model
effect; no model was run.

One sampled tool example: entity **7833**, label `anatomy_protein_present`, returns
**125 neighbors across three pages**, exactly equal to the index. All ten selected
pairs, counts and page counts are recorded in `audit.json`.

## 4. Assumptions and coverage limits

- Protocol §§8, 9.3, 10 and 19.1 are authoritative. Questions and tool results may
  legitimately contain labels/entities; only system content and the entire
  starting-entity portion are scanned by (a).
- Short-name handling applies to names shorter than four literal characters.
  Short numeric IDs and relation/evaluator labels are still scanned. Both raw
  gold names and resolved canonical names are included; no fuzzy matching or
  extra normalization changes the literal matching rule.
- Test-only fake model metadata and `think=False` satisfy runner configuration
  validation solely for capture. They select no experimental model or thinking
  policy. A BaseException stops execution at the first fake chat invocation,
  before inference or saving. The initial messages come from the actual runner;
  the real cache is loaded once under guards and reused for all captures.
- Static import inspection covers local dependencies and inventories 19 I/O
  sites. Runtime guards cover cache construction, 24 initial-message paths and
  the ten tool pairs. They intercept Python `open`, `io.open`, `os.open`, and
  pandas Parquet input, and block socket connections. This is not a universal
  native-code security sandbox or proof about every unexecuted branch.
- Inventory review distinguishes reachable agent inputs from dormant utility
  functions: `prepare_primekg` reads raw ingestion files but is not called by
  `PrimeKGIndex`; `load_cache_metadata` and `file_hash` read only cache files here.
  `load_episode_record` and the frozen-hash utility reader are imported helpers
  but are not called by `run_episode`. The saver writes output rather than
  reading experiment inputs. The runner checks target existence before capture
  but opens no episode. These sites remain visible in the evidence, not hidden
  by an import exemption. Existing S11 fresh-interpreter isolation tests also
  pass in the final full suite.

## 5. Design choices beyond the specification

All are routine engineering choices, not additional scientific methods:

- Keep implementation inside the requested test file and reuse the existing
  runner, templates, index, ToolConfig and frozen-hash reader.
- Use escaped literals with Python regex lookarounds `(?<!\w)` / `(?!\w)` and
  `IGNORECASE`, avoiding punctuation-sensitive `\b` endpoints. No exclusions.
- Inspect local imports using AST, reject dynamic imports, inventory I/O sites,
  and combine this with scoped I/O/network guards.
- Sample uniformly without replacement using `random.Random(42)` from distinct
  incident pairs sorted by numeric entity ID then label. The cache's edge table
  is used only to enumerate pairs; the public index method supplies expected
  neighbors. Preserve page size 50 and provision enough test-only tool budget to
  fetch every page. This changes no frozen episode configuration.
- Emit structured pytest evidence and save it as JSON plus a plain-text message
  sample. Hash the audit source and all evaluator inputs used in preflight.

## 6. Researcher inspection and stage status

- **Retained decision:** keep the BH2_04007 strict failure and decide a remedy
  later, as explicitly directed during this audit.
- Read the exact messages in `example_messages.txt` and the failing example
  above; all 24 message pairs are available in `audit.json`.
- Manual short-name list: **TTR**, screening **BH2_00461**. It appears in neither
  scanned surface. The question and tool results are not evidence of leakage.
- S15 acceptance remains pending because (a) fails; exact-message/short-name
  human review is not claimed complete. No Gate D4 success or S16 work is claimed.

## Revision 2 — 2026-10-16: authorized source-name overlap exemption

**All automated S15 checks now pass.** The original strict failure above and all
original logs/JSON remain intact. The researcher authorized Option 1 and the
corrected chronology, “before any pilot model run or co-failure results,” with
the earlier S14 diagnostic history acknowledged. Manual review remains pending.

### 1. Files created or changed

- `docs/frozen_pilot_protocol.md`: only check (a) of the §19.1 Leakage test row
  gained the authorized paragraph. No entry in `configs/frozen_hashes.yaml`
  covers the protocol; that file was not edited. Removing the inserted paragraph
  reproduces the exact pre-edit protocol bytes and SHA256.
- `docs/decision_log.md`: dated amendment, rationale, prior lexical evidence,
  S14 chronology correction, replacement of the earlier hold, and the
  pre-registered split report. `docs/decision_rules.md` is unchanged.
- `tests/test_leakage.py`: rule-based span exemption, 16 new synthetic cases,
  amended screening/smoke audit, and a separate all-524-row audit. No query-ID
  allowlist participates in matching; the expected query IDs are test assertions
  applied after the scan.
- New evidence: `results/diagnostics/s15/source_name_overlap.json`, `audit-v2.json`,
  `audit-v2.txt`, `full-suite-v2.txt`, `preflight-v2.json`, `verification-v2.json`,
  `red-v2.txt`, and `green-helpers-v2.txt`. Original `audit.json` and other logs
  are unchanged. The overlap artifact contains every requested field, split and
  relation-type counts, and the full short-name review list.
- This revision section, `docs/progress.md`, `tasks/plan.md` and `tasks/todo.md`.

### 2. Tests run and results

All runs used `.venv/Scripts/python.exe` in the restricted Windows sandbox, with
temporary fixture roots outside `results/`.

- New-case RED: 16 failures because the new helper did not yet exist (26 other
  tests deselected for this development-only run). Log: `red-v2.txt`.
- First helper check: 14 passed, 2 failed because two synthetic expected offsets
  counted the 17-character `Starting entity: ` prefix as 16. The expected offsets
  were corrected; production matching was not changed. Log: `green-helpers-v2.txt`.
- Complete focused audit: **43 passed in 12.50 s**, no skips or deselections.
  Command: `.venv/Scripts/python.exe -m pytest tests/test_leakage.py -q -s --basetemp .pytest_tmp_s15_v2_audit`.
- Complete suite: **401 passed in 26.35 s**, no skips or deselections.
  Command: `.venv/Scripts/python.exe -m pytest -q --basetemp .pytest_tmp_s15_v2_full`.

Check (a): zero failures across screening/smoke, exactly one overlap flag. The
separate full scan also checks the filled system prompt and finds zero failures
across 524 rows and exactly four overlap flags. Checks (b)-(d) continue to pass:
the inspected import/read boundaries, 524 four-field rows, and 10 neighbor pairs
across 12 pages/187 neighbors. The literal `scan_surface` matcher is unchanged.

### 3. Small real example and output

BH2_04007 now produces this evaluator-side result:

```text
Starting entity: folic acid deficiency anemia (PrimeKG ID: 83880)
SOURCE_NAME_OVERLAP: Folic acid, node 14678, type drug, span [17, 27)
Canonical start: 83880; gold bridge: Cyanocobalamin (14706)
|B_q| = 2; |T_q| = 30; leakage failures = 0
```

The phrase is a non-gold B_q name entirely within the canonical starting name.
It is flagged for reporting; no input text, answer set or gate population changes.

| Split | Query | Canonical starting name | Matched node | Gold bridge | B_q / T_q sizes |
|---|---|---|---|---|---|
| screening | BH2_04007 | folic acid deficiency anemia (83880) | Folic acid, drug 14678 | Cyanocobalamin (14706) | 2 / 30 |
| pilot | BH2_05778 | Ewing sarcoma (89218) | Ewing sarcoma, disease 29749 | retinoblastoma (31883) | 2 / 2 |
| expansion | BH2_05971 | Perineal hemangioma (94389) | hemangioma, disease 33562 | congenital hemangioma (32222) | 2 / 1 |
| expansion | BH2_06099 | Visceral hemangioma (25461) | hemangioma, disease 33562 | congenital hemangioma (32222) | 2 / 1 |

Per-split flags: screening 1/20, smoke 0/4, pilot 1/100, expansion 2/400.
Per-type flags: `disease:drug:effect/phenotype` 1/352 and
`effect/phenotype:disease:drug` 3/57; the other seven sampled types have zero.
All type counts, including zero-flag groups, are in `source_name_overlap.json`.

### 4. Assumptions

The researcher-specified amendment is authoritative. No extra requirement that
the canonical name appear verbatim in the question was introduced. Short names
still require manual review instead of automatic failure/overlap classification.
Existing S14 diagnostic outputs are acknowledged; the S15 decision is based on
lexical evidence, before pilot model runs or co-failure results. No new model
calls or episodes occurred during this revision.

### 5. Design choices beyond the specification

Routine engineering only: offsets are zero-based, half-open character spans in
the actual starting-entity line. Each occurrence is checked separately, so a
second occurrence outside the name still fails. Canonical-name comparison is
exact. Gold, T_q, ID and label terms take precedence even when a non-gold bridge
has the same case-insensitive name. Exemption logic stays in the test harness;
agents never read the overlap artifact. Existing matcher, templates and
production modules are unchanged. New files are versioned rather than replacing
the first audit's evidence.

The amendment pre-registers **every §16 co-failure metric and §17 chance-baseline
comparison on all queries and again excluding SOURCE_NAME_OVERLAP queries**.
Official gates use all queries. This revision records that obligation; it does
not implement or run later metric stages, compute experimental results, or start
S16.

### 6. Researcher inspection

Review the four flagged cases and the full short-name list in
`results/diagnostics/s15/source_name_overlap.json`: **34 query/name entries,
30 distinct names**, none present in either scanned surface. The original
screening/smoke list remains TTR for BH2_00461. Exact initial messages are retained
in `audit-v2.json`; the original `example_messages.txt` is unchanged.

Automated S15 verification passes; manual message/flag/short-name review is not
claimed complete. No commit, new dependency, model call, production/data/config
change, decision-rule edit, or S16 work was performed.

### Subsequent per-row overlap review — 2026-10-16

Decisions are recorded separately in `results/diagnostics/s15/overlap_review.json`
to preserve the original automated evidence. Rows refer to the table presented
in chat: BH2_04007, BH2_05778, BH2_05971, BH2_06099, in that order.
Rows 1, 3 and 4 are accepted as contained-phrase overlaps. The researcher
authorized acceptance or exclusion for row 2; the assistant selected acceptance
as a full-name, cross-type overlap under the existing exemption. All four retain
their flags and remain in official gate populations; the pre-registered
sensitivity population excludes all four. This does not establish that the
overlaps have no effect on model behavior. The 34 short-name entries and captured
initial messages still require review; S15 acceptance remains pending.

## S15 manual review and approval — 2026-10-16

Supersedes the "pending" statements above, which are kept as history.

Reviewer: Oishu (researcher). Basis: the short-name entries, common system
prompt and captured user messages in `manual_review_packet.md` were checked
with AI assistance (Claude, in chat and again in code), and the researcher
accepts them on that basis.

- **Short names:** all 34 query/name entries (26 queries) accepted; 0
  case-insensitive whole-word occurrences in starting line, system prompt or
  question. AR (BH2_01282) occurs only inside longer words.
- **Messages:** common system prompt and all 24 captured user messages accepted;
  each is exactly the question text plus the starting-entity line. Apart from
  rule-list numbers 1-3, the system prompt contains only 50 (page size) and 30
  (tool budget). The " (disease)" suffix in BH2_03750, BH2_03951 and BH2_04474
  is PrimeKG's canonical name.
- **Overlaps:** all four rows of `overlap_review.json` confirmed as the
  researcher's own decision, including BH2_05778.
- **S15 approved.**

Verification was a read-only script with the same whole-word rule as
`tests/test_leakage.py`, plus raw substring search; its output, input SHA256s
and source are embedded in `results/diagnostics/s15/manual_review_20261016.json`
(readable summary: `.md`). It found two literal mismatches in the first decision
wording (AR also inside "Starting" and "are"; rule-list numbers 1-3 in the
system prompt). The researcher supplied corrected wording, which is what the
record contains. Full suite at approval:
`results/diagnostics/s15/full-suite-approval-20261016.txt`.

Unchanged: production code, tests, protocol, decision rules, configs, frozen
hashes, data, prior evidence, flags and gate/sensitivity populations. No model
call or episode. The temporary `docs/S15_REVIEW_HANDOFF.md` was removed after
this approval was recorded. S16 not started.
