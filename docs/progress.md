# Progress — CoFail-KG

**S16 accepted (2026-10-17).** The researcher accepted normalization behavior
and verification evidence, including ID precedence. Unresolved duplicates use
exact submitted `(id, name)` pairs, without case/whitespace folding or ID type
coercion: a conservative reading of §12. The mismatch flag is literal and
diagnostic only. Pilot results must report unresolved answers that would merge
under normalized comparison, without changing official deduplication/scoring.
See the decision-log entry "S16 acceptance and pilot reporting requirement".
This supersedes pending S16 acceptance statements below. S17 is not authorized.

S16 implemented and automatically verified (2026-10-17), under the researcher's
explicit instruction to start S16. Protocol §12 agent normalization now handles
canonical ID precedence, exact typed-name/disease-suffix fallback, unique any-type
matches, unresolved reasons, mismatch flags and post-resolution duplicates.
Researcher selected exact submitted (id, name) identity for unresolved duplicates;
distinct unresolved pairs remain separate. All per-item evidence is retained.
Focused **49 passed** (42 new agent cases + 7 unchanged reference cases); full
sandbox **443 passed**, no skips/deselections. Saved S14 BH2_00461: **21/21 by ID**,
zero unresolved/mismatches/duplicates, all copied pairs verified against tool output.
All 50 protected files and all four S7 definitions unchanged. Report:
`docs/S16_implementation.md`; evidence: `results/diagnostics/s16/`.
S16 researcher inspection/acceptance pending. The latest remote S15 approval
record is integrated below; S15 is accepted. Commit/push and immediate Drive
backup were subsequently authorized. No model calls, new episodes,
data/settings/protocol edits or S17 work.

**S15 accepted (2026-10-16).** Researcher Oishu reviewed, with AI assistance,
all 34 short-name entries (26 queries), the common system prompt and all 24
captured user messages, and accepted them; confirmed all four overlap rows as
their own decision (including BH2_05778); and approved S15. Code verification:
24/24 messages match the exact pattern, one system prompt, 0 whole-word
short-name hits. Record: `results/diagnostics/s15/manual_review_20261016.json`
and `.md`; decision log 2026-10-16 "S15 manual review and approval". Full suite
at approval: `results/diagnostics/s15/full-suite-approval-20261016.txt`. The
"pending" statements below are superseded but kept as history. At that checkpoint, S16 had not started.

S15 overlap review (2026-10-16): per-row decisions recorded in
`results/diagnostics/s15/overlap_review.json`. BH2_04007, BH2_05971 and BH2_06099
accepted as contained-phrase overlaps; BH2_05778 accepted as a full-name,
cross-type overlap under the researcher's authorized choice. All four retain
SOURCE_NAME_OVERLAP; gate and sensitivity populations are unchanged. Short-name
and captured-message reviews remain pending, so S15 acceptance remains pending.

S15 revision 2 (2026-10-16): authorized source-name overlap exemption implemented;
**all automated checks pass**. Only protocol §19.1(a) amended, with chronology
corrected to before any pilot model run or co-failure results and prior S14
diagnostics acknowledged. Screening/smoke: zero failures, BH2_04007 flagged.
All 524 rows: zero failures, exactly four flags (screening 1, smoke 0, pilot 1,
expansion 2). Full short-name review list: 34 query/name entries, none matching
scanned surfaces. Focused **43 passed**; full sandbox suite **401 passed**, no
skips/deselections. Every §16 metric and §17 baseline comparison is now required
on all queries and with flagged queries excluded; official gates use all queries.
That reporting runs in later stages. Evidence: `results/diagnostics/s15/audit-v2.json`
and `source_name_overlap.json`; report: dated revision in `docs/S15_implementation.md`.
Original failure evidence preserved. Manual review pending; no production/data/
frozen-hash change, model call, episode, commit or S16 work.

S15 audit implemented and executed (2026-10-16), **NOT accepted**. Strict protocol
§19.1(a) flags `Folic acid` (additional B_q bridge 14678) within screening query
BH2_04007's starting name `folic acid deficiency anemia`; gold bridge is
Cyanocobalamin (14706). Researcher explicitly chose to retain the strict failure
and defer a remedy. (b) import/guarded-input isolation, (c) all 524 four-field
sheet rows, and (d) 10 real neighbor pairs/12 pages/187 neighbors pass. Short-name
manual review: TTR for BH2_00461, absent from both scanned surfaces. Focused:
25 passed/1 failed; final complete sandbox suite: **383 passed/1 failed**, no
skips/exclusions, only the retained leakage failure. Exact messages and evidence:
`results/diagnostics/s15/`; report: `docs/S15_implementation.md`. No production,
data, protocol/frozen-setting change, model call, episode save, commit or S16 work.

S12 sandbox portability fix (2026-10-16): Windows publishes staged episode files
with no-overwrite rename; other platforms retain hard links. Saver and S14 preflight
share the publisher; flush/fsync, reconstruction, cleanup and write-once protection
remain. All four original sandbox failures now pass. Full **sandbox** suite:
**358 passed in 13.56 s**, no skips/exclusions; actual `results/runs` synthetic
save/load/overwrite probe and preflight pass. New checks include competing writers
and explicit filesystem-error handling. Workspace pytest temp root is still needed.
No host test execution, model call, protocol/frozen-setting change, commit or S15
work. Report: `docs/S12_sandbox_fix_20261016.md`. This supersedes the prior host-only
execution recommendation below; historical evidence is retained.

S12 environment freshly verified (2026-10-16): unchanged S12 tests **21/21 pass**
on host; full host suite **352 passed** in 12.47 s, no skips/exclusions. Actual
`results/runs` preflight and synthetic save/load/reconstruction/overwrite-refusal
probe pass. Sandbox with workspace temp still gives 17 passed/4 failed at hard-link
persistence. Use approved host execution; sandbox policy and saver are unchanged.
No model call, code/test/frozen-setting change, commit, or S15 work. Report and
future-run procedure: `docs/S12_environment_verification_20261016.md`.

## Earlier stage records
P1 approved and frozen by the researcher (2026-10-16), conditional on broader
reliability not being required by S14; the runbook confirms that condition.
`configs/frozen_hashes.yaml` now contains the exact unfilled P1 template SHA256:
`8f93b7c42ef7a90f64bbcd83e6b77db62e4f3c6b0c08a45f068b435a9c655265`.
This approves P1, not experimental model/settings changes. The researcher then
authorized the local S14 commit; acceptance of the diagnostic settings/context
margin remains separate. No new episode or S15.

S14 template repair and authorized repeat (2026-10-16): **SUCCESS** after one fixed
re-prompt; four successful native calls and 21 final ID/name pairs matching the
returned disease items. Full host suite: **352 passed**, no skips/exclusions.
Separate variant `cofail-qwen3:4b-templatefix` has valid JSON tool definitions and
different true/false prefixes, verified by render-only requests. Runtime 101.512 s;
sampled GPU peak 4742/8192 MiB, fully GPU resident. Original model and prior records
are unchanged. Crucial correction: local `qwen3:4b` metadata identifies
Qwen3-4B-Thinking-2507, which supports only thinking mode. Reasoning persisted
despite `think=false`; the first final reply failed parsing, the re-prompt succeeded.
This establishes a successful example, not reliable non-thinking behavior or gold
accuracy. P1 approval/freeze is now complete; no S15 or experimental model choice.
Details and next-step options: `docs/S14_template_repair.md`.

Previous diagnostic checkpoint:
S14 authorized follow-up diagnostic (2026-10-16): `think=false`, output cap 6144,
context 8192, same first screening query/model. **4 successful native tool calls**
retrieved 21 disease entries via TTR; every result matches the inspection CLI.
Still **PARSE_FAIL** because reasoning precedes final JSON on both final attempts.
GPU peak sampled usage 4714/8192 MiB; model fully GPU resident. Runtime render-only
checks show identical true/false prefixes ending in `<think>` and malformed tool
schema serialization. Proposed template repair saved, not installed or generated
with. Last prompt 7295 tokens; context shifts occurred during the re-prompt reply.
Full host suite: **351 passed**. Details: `docs/S14_nothink6144_diagnostic.md`.
No frozen setting, installed model or parser change; original failed runs preserved.

S14 implementation verified; researcher review pending (2026-10-16): requested
S13 diagnostic config restored (`think: true`, synthetic diagnostic only), missing
S14 prompt/runner implemented, all original draft tests retained. Plain host suite:
**348 passed**, no skips/exclusions. The unchanged S12 saver works on host; the S14
launcher checks actual results-directory hard links before any model call.
Researcher enabled thinking for one S14 example. First screening query BH2_00461
with qwen3:4b was saved as **PARSE_FAIL**: two thinking-only replies, each at the
4096-token output cap, empty final content, zero native tool calls; exactly one
fixed re-prompt. Prompt tokens 598/627; model digest stable; duration 90.105 s.
This verifies recording/failure handling but not a successful real traversal.
Report: `docs/S14_implementation.md`; record:
`results/runs/s14-review-20261016/BH2_00461__S14-qwen3-4b__a1.json`.
P1 approval/freeze and acceptance of the real example remain pending. No commit,
protocol/frozen-hash change, model-selection decision or S15 work.

S12 rerun checked (2026-10-16): unchanged S12 tests pass **21/21 outside the sandbox**.
Sandbox with workspace temp reproduces the same four `os.link` WinError 5 failures
(17 passed); default sandbox temp instead causes six fixture setup errors (15 passed).
At that checkpoint the plain host suite stopped collecting at untracked S14 `test_run_agent.py`
(missing `run_agent` module). Explicitly excluding that file gives **296 passed,
5 failed**, all S13 script failures from missing `think` in `configs/ollama.yaml`.
That checkpoint did not reproduce the historical 301-pass result below; fixed above.
Analysis and raw-output references: `docs/S12_rerun_20261016.md`. No code/config
change, model call or commit was made for this rerun.

S13 follow-up verified, **uncommitted pending researcher reply** (2026-10-15):
required explicit config `think`, thinking text preserved, and host environment
identified. Plain full-suite command outside the sandbox: 301 passed (249 prior
+ 52 S13), no skips or test/temp overrides. Unchanged S12 saver and hard links
work under the actual `results/runs` path on DESKTOP-5903S8A outside the sandbox;
sandbox remains unsuitable. New explicit-think synthetic check passed.
Original S13 commit `f79165a` predates the commit hold; no new commit made.
Review reply: `docs/S13_review_reply.md`. Researcher must confirm real-episode
execution environment and decide experimental thinking policy before S20.

S13 completed (2026-10-15): local Ollama HTTP client, explicit generation options,
identity, error classification, bounded logged connection retries and diagnostic script.
Suite: 294 passed (45 new). Real installed qwen3:4b (Q4_K_M, 4.0B) returned `Hello!`
and native `add(a=2,b=3)`; full digest stable before/after. Counts: 16/209 plain,
146/295 tool (prompt/generated); latency 46.914/3.111 s. Details:
`docs/S13_implementation.md`; evidence: `results/diagnostics/s13_ollama.json`.
Only synthetic model calls; no biomedical episode or Gate D3 choice.
Next: S14, when requested by the researcher.

S12 completed (2026-10-15): trace, trace graph, primary/simple paths and write-once episode
records (`src/cofail_kg/agents/trace.py`); §14.2 tie-break per protocol v1.3.4. Suite: 249 passed
(21 new). No model run. S13 subsequently completed as recorded above.

S11 completed (2026-10-15); researcher approved wording B and authorized the commit.
T1 schema source SHA256 is frozen under `tools`. The two tools use
the S4 index with configured pagination/budgets, exact errors and full call logs.
Suite: 228 passed (43 new). Real screening entity MYO-029: 329 unique `drug_drug`
neighbors across seven pages, every item matching the inspection CLI. Details and
approved wording: `docs/S11_implementation.md`; evidence: `results/diagnostics/s11_tools.json`.
No model run. Next: S12, when requested by the researcher.
S12 subsequently completed as recorded above.

S10 completed (2026-10-15): seed 42; screening 20 (5 single/15 multi), smoke 4 (1/3),
pilot 100 (25/75 default confirmed), expansion reserve 400 (100/300). No shortfalls;
524 unique queries and all six pairwise overlaps zero. Pilot/expansion represent all
nine passing types. Four evaluator manifests and four agent-input sheets created;
all eight SHA256s frozen under `manifests`, configs/pilot.yaml filled. Second script
run is byte-identical; independent allocation/identity/hash checks pass. Suite: 183 passed.
Report: `data/processed/manifests/sampling_report.md`; details: `docs/S10_implementation.md`.
S11 subsequently completed with approved T1 wording B as recorded above.

S9 completed (2026-10-15): researcher selected θ = 0.50, frozen in protocol §7.2 and
recorded before computation. Primary population N_P = 7,176 (6,575 SINGLE_BRIDGE,
601 MULTI_BRIDGE); K = 9 types with ≥20 queries; Gate D2 GREEN. Excluded 15
INCONSISTENT and 186 LEAKY_QUESTION queries, no overlap; zero saturation exclusions.
Outputs: `data/processed/primary_population.csv`, `primary_population_summary.json`,
`primary_population_report.md`. Full suite: 170 passed. Details: `docs/S9_implementation.md`.
S10 subsequently completed as recorded above.

S9 part 1 completed (2026-10-15): all nine D1 PASS types CONFIRMED on queries outside
the S6 validation sample (lowest consistency 506/516 = 98.0620%). No mapping decision
required. Saturation maximum 5.1527%; zero exclusions at θ = 0.30, 0.50, 0.70, 0.90.
Evidence: `results/diagnostics/s9_decision_evidence/decision_evidence.md` (plus CSV/JSON tables).
Full suite: 158 passed. Details: `docs/S9_part1_implementation.md`.
Researcher subsequently chose θ = 0.50; part 2 completed as recorded above.

S8 outputs generated and verified locally (2026-10-15): 7,377 queries, 7,362 CONSISTENT,
15 INCONSISTENT (all primary GOLD_MISSING_FROM_KG; 3 also EXTRA_TARGETS), 186 leakage
flags, and 270 queries overlapping S6 validation. Full suite: 152 passed (17 new S8 tests).
Evidence: `results/diagnostics/query_validation.csv` and `query_validation_summary.json`;
ten graph spot-checks: `results/diagnostics/s8_verification.json`. See `docs/S8_implementation.md`.
S9 is complete as recorded above; θ = 0.50 and the primary population are now fixed.
The S7 details below describe the preceding verified checkpoint.

S7 completed (2026-10-13): 7,377 queries from the 7,377 rows of the nine D1 PASS types.
S6 mapping and ambiguity tags were frozen in ab67cf1; D1 remains PROCEED (9/12 types,
96.65% dataset-row coverage). All three failed types remain excluded, covering 256 rows;
the five-row type's tie remains unresolved. No automatic re-admission.
S7 outputs: 6,673 SINGLE-bridge queries, 704 MULTI-bridge queries, no unresolved reference
names, 57 disease-suffix resolution occurrences, and 481,617 query/bridge/target rows.
All 7,377 query sets were independently checked against the cached edge tables; required
inspection CLI checks pass. Full suite: 135 passed (16 new S7 tests). Details and engineering
choices: `docs/S7_implementation.md`.
No query inclusion or new research decision was made at S7.

## Completed stages
S10 — completed 2026-10-15: four disjoint sets, default pilot 25/75 confirmed;
  manifests/sheets frozen, all requested sizes met. See docs/S10_implementation.md.
S9 — completed 2026-10-15: θ = 0.50, N_P = 7,176, K = 9, Gate D2 GREEN.
S8 — Query validation completed and outputs verified locally 2026-10-15; 7,362/7,377
  CONSISTENT, 15 INCONSISTENT, 186 leakage flags. See docs/S8_implementation.md.
S0
S1
S2 — BioHopR loader. 18/18 tests pass (incl. real-file test); audit found no science/gate problems.
  Question-text field selected: `hop2_question_multi` ("Name all …").
  Protocol §3.1 revision and question field filled in ([FROZEN] at S2); decision-log entry added.
  Post-S2 repo hygiene: requirements.lock (exact versions), requires-python >=3.12 (the lock needs
  it), README Reproduce/Contribute/Data credits. Fresh-clone check: 17 passed + 1 skipped before
  the BioHopR download, 18 passed after; S2 outputs regenerate identically.
S3 — BioHopR diagnostics. 27/27 tests pass; audit found no science/gate problems.
  All 12 relation-type counts match protocol §3.1.
  Answer-size median 11, p90 102, p99 325.36.
  Duplicate question texts: 0 (exact and normalised).

S4 — completed 2026-10-12: ingestion, index, inspection CLI, protocol fields and fingerprint finalized.
  45/45 tests pass. Implementation report: docs/S4_implementation.md.
  Raw inspection: results/diagnostics/primekg/inspection.md; 8,100,498 rows, 129,375 nodes.
  10,000/10,000 sampled rows have a reverse; 28/30 labels sampled (two rare labels unsampled).
  Cached tables and machine-written metadata exist locally; kg_fingerprint was written by
  the preparation script with researcher authorization on 2026-10-12 and independently
  checked against the metadata SHA256.
  Real Troglitazone checks match raw CSV exactly. Load 6.57 s; verification process peak 880.7 MiB.
  The supplied nodes.csv matches all kg.csv node fields. On 2026-10-12 the researcher supplied
  its full MD5 from the publisher's website: 7f9ab4109c54049e819ecd14e15a6038.
  A fresh local calculation matches exactly, resolving the checksum check through
  researcher-provided website verification (the automated Dataverse request returned HTTP 403).
  Earlier release/answer-construction investigation: docs/S4_findings.md.
  Release verified: kg.csv MD5 matches Dataverse file 6180620 (same file in v1.0/2.0/2.1);
  7,370/7,633 BioHopR answer lists reproduced exactly from kg.csv. The paper's "202 side effects"
  for Troglitazone is a 2-hop answer-list size (KG has 17), not a release mismatch.
  nodes.tab identical to kg.csv's node set (no isolated nodes; same per-type counts).
  Answer construction DECIDED 2026-10-12: option C (S4_findings.md Report 2). Per relation type at
  S6: BRIDGE (T_q^{B*}) or UNION (T_q), whichever reaches 90% on hop 2; BRIDGE if both (tie rule
  fixed before S6 results). Protocol §5.1, §5.3 (new), §6, §7.1, §13 amended; decision log and
  CHANGES.md updated.
  Cache reproduction check 2026-10-12 (researcher's machine): this branch's prepare script, run
  without --freeze on the local raw files, gave metadata SHA256 bc5d3fd2…2e95 = frozen
  kg_fingerprint exactly. Bookkeeping note: local primekg_release.json records download date
  2026-10-12; the S4 report records 2026-10-10. Not part of the fingerprint; left as is.
  Field-role support AMENDED 2026-10-13 (protocol v1.3.1): §3.1 now defines resolvable rows
  (hop2, hop1 and at least half, and at least one, of the answer names resolve) and support
  (hop2–hop1 adjacent; ≥1 answer via hop1; every answer via hop1 or another bridge of hop2).
  Runbook S5 step 3 updated to match; decision log and CHANGES.md updated. Sample, ordering,
  95% threshold and every-type rule unchanged.
  Exploratory evidence seen before this decision: results/diagnostics/s5_field_role_preview.csv
  (55 rows, positions 6–10 per type, disjoint from the S5 sample; S5 sample not viewed).
  Field-role failure handling AMENDED 2026-10-13 (protocol v1.3.2): a single failing relation
  type is excluded (FAIL in Gate D1) instead of stopping S5; S5 stops if more than one type fails
  or the failing types cover more than 1% of the 7,633 rows. Decided before S5 ran, with the same
  exploratory evidence; S5 sample not viewed.
S5 — completed 2026-10-13: field roles verified (hop2 = query entity, hop1 = bridge,
  answer = gold targets; protocol §3.1 [FROZEN] at S5). All 12 relation types PASS at 100%;
  rule outcome ROLES_SUPPORTED; 0 failing types. 60 rows sampled, 59 resolvable (BH2_05493
  unresolvable). 5 rows supported only through other bridges (3 disease:drug:effect/phenotype,
  2 effect/phenotype:drug:disease). Hand-checks BH2_00004, BH2_06128, BH2_04078 agree.
  Results: results/semantics/field_roles* (code commit 5ae77f6). 20 new tests; 74 pass.

## S6 first prompt — computed, not frozen
- Implementation: `scripts/06_relation_mapping.py`, `src/cofail_kg/evaluation/relation_mapping.py`,
  and two graph-index accessors. 335 validation rows; no skipped query/bridge rows and no
  unresolved sampled answers under §12 v1.3.3.
- D1: 9 types PASS, covering 7,377/7,633 rows (96.65%); global PROCEED. Eight passing types
  adopt BRIDGE and one (`disease:drug:effect/phenotype`, 949 rows) adopts UNION.
- FAIL: `disease:effect/phenotype:drug` (3/30 under either construction),
  `drug:effect/phenotype:disease` (0/5 under either, also insufficient validation rows),
  `effect/phenotype:drug:disease` (BRIDGE 26/30, UNION 20/30).
- The five-row type ties positive/negative disease-phenotype labels at zero under both
  constructions. No label was chosen. The tie cannot change its FAIL or global PROCEED.
  Researcher disposition (2026-10-13): keep the failed type's tie unresolved; no diagnostic
  label selection. This disposition is recorded in the decision log.
- Passing-type ambiguity tags: NONE 2, R1_AMBIGUOUS 3, R2_AMBIGUOUS 2, BOTH_AMBIGUOUS 2.
  Failed types have no adopted R2/construction and hence no computable tag.
- Outputs: `results/semantics/relation_mapping_candidates.csv`, `relation_mapping_proposed.json`,
  `relation_ambiguity_tags.csv`, `d1_report.md`. See `docs/S6_implementation.md` for verification.
- 114 tests pass. Eight raw-CSV mismatch checks agree; an independent existing-index check
  reproduces all 271 UNION targets of BH2_03879 (stored bridge alone reaches 86).
- No `relation_mapping.json`, frozen hash, protocol amendment or S7 work.
- Subsequent authorized investigation (2026-10-13): `drug:effect/phenotype:disease` EXCLUDED.
  Exactly five records exist; all qualify, none are skipped. All candidate sets still score
  0/5 under both constructions. Field roles, normalization, raw edge orientations and local
  release integrity checked; no permitted correction found. Full named sets for two rows:
  `results/semantics/s6_failed_type_investigation/report.md`; all five rows: `evidence.json`.
  Exclusion registry: `results/semantics/relation_type_exclusions.json`; recomputed gate:
  `results/semantics/d1_after_exclusion.json` and `.md`. Original denominators retained.

## Latest commit
S6 calculation code: `2f2caf1`; this checkpoint records the first-prompt outputs and verification.
Earlier: 962637b (team update for S4 and S5); ea4b980 (S5 field roles verified); 5ae77f6 (S5
field-role verification code); edc9b3e (protocol v1.3.2, field-role failure handling);
48b47cb (protocol v1.3.1, field-role support definition); b48952f (protocol v1.3,
answer construction option C); 7998bb3 (S4 completion checkpoint); a0578b2 (index and CLI),
d09c66b (preparation).

## Numbers to remember (filled as you go)
- BioHopR revision (S2): 08f06692c3900347e7405ba55ff6a6d330f55ddb (BioHopR.json SHA256 1adda2f23d305c394537e7b56d3e972b2d8f4141ae716ede54e0d08876eb527d)
- 2-hop row count (S2): 7,633 (matches paper). 1-hop and 2-hop questions share one record; every record is a 2-hop record. 12 relation-type counts match protocol §3.1 exactly.
- S2 diagnostics:
  - Question-field candidates: hop2_question_multi (selected; 7,633 distinct texts), hop2_question, prompt.
  - 135 rows: hop2 value ends in " (disease)" but question texts drop it (e.g. "acne (disease)" → "…disease acne ."). Relevant at S5/S12.
  - hop1 text inside hop2_question_multi: 61 case-sensitive substring · 126 case-insensitive substring · 81 case-insensitive whole word · 76 whole word with hop1 ≥ 4 chars (results/diagnostics/biohopr/hop1_in_question.csv).
  - Answer list length range 1–890.
- Answer size median / p90 / p99 (S3): 11 / 102 / 325.36 (numpy linear percentiles; list length = set size on every row)
- Duplicate question texts with >1 bridge (S3): 0 — no question text occurs twice (exact or normalised)
- PrimeKG release, download date, row count (S4): frozen v2.1, DOI 10.7910/DVN/IXA7BM;
  existing release file records 2026-10-10 (inferred archive date); 8,100,498 rows.
- Troglitazone side-effect count (S4 check, paper says 202): 17 direct neighbours, confirmed
  by the new index and independent raw CSV scan. The prior findings explain the 202 as two-hop.
- D1 outcome (S6 first prompt): PROCEED, 9 PASS / 3 FAIL; 96.65% row coverage. Not frozen.
- N_P and D2 outcome (S9): 7,176; K = 9; GREEN; θ = 0.50 (2026-10-15).
- Max prompt tokens in screening (S20):
- Frozen models and digests (S21):
- Pilot commit hash (S26):

## Known issues
S2 engineering observations (none can change a result as things stand):
- Loader checks file SHA256 against metadata.json but not metadata revision against configs/frozen_hashes.yaml (natural check at S26).
- scripts/02_download_biohopr.py and inspection helpers have no unit tests (verified by real runs only).
- write_once (frozen_hashes.yaml) is not atomic; matters more as the file grows.
- BioHopR README.md has no Hub SHA256 to verify against (not LFS); its SHA256 is recorded in metadata.json.
- Loader default raw dir is relative to the working directory; scripts pass absolute paths.
- Venv editable install was repointed (pip install -e .) after the project moved from OneDrive.
## Fix at stage (deferred from the S1 audits)
- S5: some BioHopR answer names have trailing spaces. Resolved by researcher on 2026-10-12:
  trim leading/trailing whitespace as well as collapse internal whitespace (decision log).
  Implemented in S4 name lookup; explicit protocol §12 wording finalized with researcher
  authorization on 2026-10-12.
  162 answer strings (45 distinct names) in 120 rows, all trailing, none leading. Examples:
  'acne ', 'atrial fibrillation ', "Kaposi's sarcoma ". BH2_05031 and BH2_05040 contain both
  'myocardial infarction ' and 'myocardial infarction' (two names under exact comparison, §0.4).
- S13: how OUT_OF_MEMORY is detected (engineering; decided in code and documented).
- S29: final freeze of protocol §21 (mechanism list, control tie-break), using pilot results.
- Every stage: Claude Code lists its engineering choices at the end; record any that matter here.

## Next action
The release check in protocol §3.2 and runbook S4 was corrected with researcher authorization
on 2026-10-12: publisher checksums plus 17 direct neighbours, with the 202 two-hop count explained.
The canonical node ID row in protocol §3.2 was confirmed and frozen with researcher approval
on 2026-10-12: x_index/y_index correspond to node_index; decimal strings, numeric ordering.
The edge-storage sample finding (including the unsampled-label limitation) and either-direction
convention with no exceptions were frozen with researcher approval on 2026-10-12; §10 now
explicitly has no direction argument.
The v2.1 release in §3.2 and explicit whitespace-trimming wording in §12 were finalized
with researcher authorization on 2026-10-12. The kg_fingerprint freeze is complete.
The §3.3 identity type map was confirmed and frozen with researcher approval on 2026-10-12.
The researcher subsequently authorized S4 completion. Final checks passed: 45 tests,
raw-input/cache validation, frozen metadata SHA256 comparison, and the 17-neighbour real check.
Answer construction resolved (option C, 2026-10-12); S5 subsequently completed on 2026-10-13.
DONE (2026-10-13, 4d18892): runbook S6/S7 aligned with protocol §5.3 (BRIDGE and UNION scored,
construction adopted per type, BRIDGE if both pass, G_q at S7, results split by construction).
S8 uses protocol G_q correctly; before S17, check any remaining gold-bridge-only wording.
Field-role support defined in protocol §3.1 (v1.3.1, 2026-10-13); runbook S5 step 3 matches.
DECIDED (v1.3.2, 2026-10-13): global-stop policy if drug:effect/phenotype:disease (5 rows, no
disjoint preview evidence) fails S5 — a single failing type is excluded (FAIL in Gate D1); S5
stops only if more than one type fails or the failing types cover more than 1% of the rows.
RESOLVED BY S6 EVIDENCE (2026-10-13):
- `disease:effect/phenotype:drug` has only `drug_effect` as a hop-2 candidate; it reproduces
  3/30 sampled gold sets under either construction. S5 checks containment/support; S6 requires
  exact equality. Raw examples confirm additional reachable drugs, so those findings do not conflict.
S5 completed 2026-10-13 (field roles verified; decision log).
S6 completed 2026-10-13 (ab67cf1): approved mapping and ambiguity tags frozen;
  8 BRIDGE types / 6,428 rows, 1 UNION type / 949 rows, three failed types excluded.
S7 completed 2026-10-13: reference queries, targets and summary created and independently
  checked. Implementation and verification: docs/S7_implementation.md.
S6 note: the unresolved answer names in the S5 sample ("autism" in BH2_04897, "vitamin A
deficiency" in BH2_05290, "insomnia" in BH2_05493) are not type mismatches: they match no
PrimeKG node of any type, but PrimeKG has disease nodes "autism (disease)" (84310), "vitamin A
deficiency (disease)" (84142) and "insomnia (disease)" (32033) — the same " (disease)" suffix
pattern as the 135 S2 rows. Decided (v1.3.3, 2026-10-13): §12 now retries a disease-typed name
with " (disease)" appended (exactly one match only); all 152 such answer names in 115 rows
resolve; the S5 outcome is unchanged.
DONE (2026-10-13, 4d18892): §12 suffix retry implemented in src/cofail_kg/evaluation/normalize.py
(reference policy), 7 unit tests; all 152 previously unresolved answer names now resolve.
S6 mapping and hash were frozen with researcher authorization in ab67cf1 (decision log).
S11 completed with approved and frozen T1 wording B (2026-10-15). Next action: S12
when requested by the researcher. No experimental agents have been run.
Before S17, check
the runbook's older gold-bridge-only comparison wording against protocol §7.1/§13, which
already uses the construction reference G_q. Historical pre-freeze S6 reports remain intact.
S12 completed (2026-10-15): trace, trace graph, paths and write-once episode records in
  src/cofail_kg/agents/trace.py; 249 tests pass (21 new). §14.2 tie-break pairs are
  (source node, label) per edge (protocol v1.3.4, decision log 2026-10-15). Researcher confirmed
  x = s: the length-0 path is the only simple path (coded WRONG_HOP_COUNT under §14.2).
  No experimental agents have been run. Next action: S13 when requested by the researcher.
Note for S14: on resume, count only final …__a<attempt>.json records and ignore leftover .tmp files.
