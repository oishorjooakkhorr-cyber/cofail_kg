# Progress — CoFail-KG

## Current stage
S5 complete — field roles verified (2026-10-13). S6 has not started.

## Completed stages
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

## Latest commit
`S5: amend protocol to v1.3.3 - disease-suffix name fallback (§12)` (this update).
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
- D1 outcome (S6):
- N_P and D2 outcome (S9):
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
Answer construction resolved (option C, 2026-10-12). No S5 work has been performed.
Runbook S6/S7 steps still describe only T_q^{B*}; align them with protocol §5.3 before S6.
Field-role support defined in protocol §3.1 (v1.3.1, 2026-10-13); runbook S5 step 3 matches.
DECIDED (v1.3.2, 2026-10-13): global-stop policy if drug:effect/phenotype:disease (5 rows, no
disjoint preview evidence) fails S5 — a single failing type is excluded (FAIL in Gate D1); S5
stops only if more than one type fails or the failing types cover more than 1% of the rows.
OPEN (not decided):
- S6 label-set question for disease:effect/phenotype:drug: the S4 single-label-pair simulation
  (S4_findings.md Report 2: 32/36 rows follow neither construction) and the any-label preview
  (5/5 rows: every answer via the stored bridge) disagree.
S5 completed 2026-10-13 (field roles verified; decision log).
S6 note: the unresolved answer names in the S5 sample ("autism" in BH2_04897, "vitamin A
deficiency" in BH2_05290, "insomnia" in BH2_05493) are not type mismatches: they match no
PrimeKG node of any type, but PrimeKG has disease nodes "autism (disease)" (84310), "vitamin A
deficiency (disease)" (84142) and "insomnia (disease)" (32033) — the same " (disease)" suffix
pattern as the 135 S2 rows. Decided (v1.3.3, 2026-10-13): §12 now retries a disease-typed name
with " (disease)" appended (exactly one match only); all 152 such answer names in 115 rows
resolve; the S5 outcome is unchanged.
BEFORE S6: implement the §12 suffix retry in name resolution, with tests.
S6 has not started. Start S6 in docs/pipeline_runbook.md when instructed.
