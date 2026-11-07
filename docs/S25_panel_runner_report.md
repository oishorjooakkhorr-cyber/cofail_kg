# S25 — Panel runner and panel smoke test (Gate D4 input)

Date: 2026-11-07. Stage prompt: runbook S25. Code commit for the run: `f1451b5`.
**Gate D4 is not decided here:** it needs the researcher's manual audit of `audit_sheet.csv`.

## 1. Files created or changed

| File | What |
|---|---|
| `src/cofail_kg/agents/panel_runner.py` (new) | Agent-major plan, identity and hash checks, resume that skips any saved §9.5 status, progress file, §19 rerun planning |
| `src/cofail_kg/evaluation/panel_analysis.py` (new) | §19.1 kill-and-resume completeness check, §19.1 audit selection, audit-sheet rows |
| `scripts/25_run_panel.py` (new) | `run` (isolated pinned Ollama server per agent, S20 runtime guards, synthetic probe, episodes) and `analyze` |
| `tests/test_panel_runner.py` (new) | 11 tests |
| `src/cofail_kg/agents/run_agent.py` | `run_episode(..., attempt=1)`: attempt number for §19 reruns (default unchanged) |
| `src/cofail_kg/agents/trace.py`, `tests/test_trace.py` | `PROTOCOL_VERSION` 1.3.5 → 1.3.6 (decision log 2026-11-07: fix at the start of S25) |
| `tests/test_leakage.py` | `agents.panel_runner` added to the §19.1(b) agent-module import-isolation check |
| `docs/decision_log.md` | Entry for the stop at 11/16 and the stash/resume |
| `docs/S25_panel_runner_report.md` (new) | This report |

Committed with this report but **not written in this session**: the researcher's D5 wording fix in
`docs/decision_rules.md`, its `docs/decision_log.md` entry and the `docs/progress.md` note (made in
another session; see the decision-log entries "D5 model-digest entry clarified" and "S25 smoke_panel:
stop at 11/16").

Run outputs (gitignored under `results/runs/`, on the inference host only):
`results/runs/smoke_panel/` — 16 episode records, `progress.json`, `configs/`, `runtime/`,
`analysis/` (`metrics/`, `cofailure.json`, `nulls.json`, `verification.json`, `leakage_test.txt`) and
`audit_sheet.csv`.

## 2. Tests

- `tests/test_panel_runner.py`: **11 passed** — agent-major plan; resume after a simulated Ctrl+C
  (no duplicates, nothing missing, the ERROR episode never rerun, a completed run resumes to a
  no-op); resume refuses records from a different configuration; digest mismatch and missing native
  tools refused before any episode; hash mismatch refused; write-once records (also the real
  `run_episode`); §19 rerun routes; completeness flags duplicates/missing/extra; audit selection and
  audit rows.
- Full suite: **727 passed, 2 skipped** (BioHopR not downloaded), before the run.
- §19.1 leakage test on screening + smoke queries: `tests/test_leakage.py`, **43 passed**
  (output: `results/runs/smoke_panel/analysis/leakage_test.txt`). (a) no forbidden term; smoke has
  no SOURCE_NAME_OVERLAP query; one short name (TTR, screening BH2_00461) listed for manual review,
  not present. (b) agent modules, now including `panel_runner`, import nothing from evaluation.
  (c) all 524 sheet lines have the four §8 fields. (d) 10 random (entity, label) pairs match the index.

## 3. Real run: `smoke_panel`, 4 smoke queries × 4 agents

- **Kill-and-resume:** the researcher pressed Ctrl+C at the HALFWAY banner (8/16, during
  Ministral3-14B's server start-up). The restart skipped all 8 completed episodes.
- **Unplanned stop at 11/16:** a pinned source (`docs/decision_rules.md`) changed during the run; the
  run stopped itself. Resolved by stash → resume → stash pop (decision log). No episode was rerun.
- **Final:** 16/16 saved, no duplicates, none missing, none extra; reconstruction passes for all 16.

| Agent | BH2_01682 | BH2_03951 | BH2_04459 | BH2_04474 | Largest prompt / 32768 |
|---|---|---|---|---|---|
| Gemma4-12B | SUCCESS | SUCCESS | SUCCESS | SUCCESS | 5,141 (15.7%) |
| Granite41-8B | SUCCESS | SUCCESS | SUCCESS | SUCCESS | 25,335 (77.3%) |
| Ministral3-14B | SUCCESS | SUCCESS | SUCCESS | SUCCESS | 20,484 (62.5%) |
| Cogito-14B | SUCCESS | **ERROR** (240 s request timeout) | SUCCESS | SUCCESS | 25,818 (78.8%) |

- SUCCESS 15/16 (93.8%; D4 needs ≥ 14/16). No episode above 90% of `num_ctx`; no OUT_OF_MEMORY.
- Cogito BH2_03951: a reply was cut at 240 s after ~4,000 tokens at ~17.5 tok/s, with ~22,600 tokens
  of context (server log). Same failure type as at S22; no runtime revision (researcher, 2026-11-07).
- No answer is both OFF_QUESTION and SUPPORTED.
- Co-failure (§16): every CF3/CF4 (question, grounded, hop-1-clean, benchmark) and PCF total is 0.
  Chance baselines (§17): every observed and null total 0, p = 1. Same with SOURCE_NAME_OVERLAP
  queries excluded (none in smoke).
- **Audit sheet:** 8 episodes (2 per agent), **557 answer rows**: 556 GOLD/SUPPORTED and 1
  OFF_QUESTION/UNGROUNDED (Cogito-14B BH2_04474, answer 84470; corrected 2026-11-07, first written
  as Gemma4-12B). Episodes: BH2_04474 and BH2_01682 (Gemma4-12B), BH2_01682 and
  BH2_04459 (Granite41-8B), BH2_04459 and BH2_04474 (Ministral3-14B), BH2_04474 and BH2_01682
  (Cogito-14B). `my_label_A`, `my_label_B`, `notes` are empty.

## 4. Assumptions

1. **Audit selection when an agent has no OFF_QUESTION episode:** the code takes the first two
   eligible episodes in hash order, so each agent contributes 2 (8 in total). The §19.1 sentence read
   literally gives only one ("the first not already chosen"); the "fewer than 2" clause and the
   runbook's "8 episodes" imply two. **Researcher check needed before D4.**
2. **§19.1(b) file rule for `panel_runner`:** it reads and writes its own run records and the
   progress file (as `trace.py` already did), never evaluator data. I read "open no files except the
   agent-input sheet and the PrimeKG cache" as being about inputs. **Researcher check needed.**
3. A record is "completed" when its file exists; the progress file is a status file (rewritten), not
   a result.
4. `git_commit` is marked `-dirty` only for tracked-file changes (`--untracked-files=no`); the
   untracked `results/diagnostics/ministral_speed/` folder no longer marks a run dirty.

## 5. Design choices beyond the specification (all routine engineering)

- Inference orchestration in `agents/panel_runner.py` (no evaluation imports); serving, guards and
  evaluation in the script; S22's frozen runtime guards and server setup reused unchanged.
- Run configuration pinned per agent under `results/runs/<run_id>/configs/`; resume refuses any
  change, and a changed commit stops the run (§19 code-change rule).
- Sources re-checked before and after every episode; analysis may run after a fix to evaluation-only
  code (`scripts/25_run_panel.py`, `src/cofail_kg/evaluation/`), never after a change to inference
  sources.
- HALFWAY banner after episode `total // 2` for the kill-and-resume test.
- Rerun planning: D6/D7 HOLD → failed episodes; D4 FAIL and CODE_CHANGE → all listed episodes; each
  as attempt + 1 under a new run ID with a decision-log reference.
- Audit sheet is write-once in its machine columns; the researcher's columns may be filled in place.
- Audit `answer_id`: the resolved node ID, or `unresolved:<submitted id>`; `primary_path` rendered as
  `u -label-> v ; ...`.

## 6. Inspect by hand

1. **Manual audit:** fill `my_label_A` / `my_label_B` for all 557 rows of
   `results/runs/smoke_panel/audit_sheet.csv` from the traces (runbook S25). Most are GOLD/SUPPORTED;
   the one OFF_QUESTION/UNGROUNDED row is Cogito-14B's.
2. Confirm assumptions 1 and 2 above.

**Update 2026-11-07 (decision log, "S25 audit sheet filled ..."):** assumptions 1 and 2 confirmed by
the researcher. At the researcher's instruction the `my_label_*` columns were filled with an
independent re-derivation (`scripts/25_audit_independent_check.py`, no `cofail_kg` imports, reference
sets rebuilt from raw `kg.csv`/BioHopR): 557/557 rows agree with the code on Label A, Label B and the
primary path. It is not a by-hand audit. Gate D4 is still the researcher's decision.
3. Read one full episode per model (e.g. the 4 BH2_01682 episodes are short: 4 tool calls each).
4. Then decide Gate D4 and log it.
