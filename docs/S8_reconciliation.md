# S8 — Reconciliation before publishing S10

On 2026-10-15, fetching GitHub found S8 commit `6436653` beyond the shared S7 base.
The local S8–S10 commits had been created without that fetched checkpoint. The two S8
implementations use different field schemas, so their code and evidence cannot be combined
by selecting individual conflict lines.

All nine upstream S8 files are preserved exactly under
`results/diagnostics/s8_github_checkpoint/`, and the upstream commit remains in the merged
Git history. Its two leakage-interpretation decision entries are preserved in the active
decision log before the S9 entries. The original upstream tests remain in the snapshot;
the active tests target the current local API consumed by S9.

Compared all 7,377 queries: no differences in status, primary reason, leakage flag,
saturation share, S6 sample overlap or bridge multiplicity. Therefore the S9 mapping
confirmation, selected primary population, S10 membership and all eight frozen sampling
hashes remain valid and unchanged.

Updated the active leakage matcher to implement the upstream recorded interpretation:
§12 normalization of names and questions, raw plus resolved graph names, normalized
length ≥4 and Unicode word boundaries. The production S8 script supplies canonical graph
names from the verified node cache. Two new tests cover graph-name-only normalized matches
and the normalized minimum length. An independent full-data recalculation reproduced all
saved leakage/status labels; comparison details are in the preserved checkpoint directory.

The current S8 CSV/summary remain the completed local evidence snapshot, with their original
run/source hashes. The enhanced code is a later checked revision, not a claim that the old
outputs were regenerated. No scientific threshold, S9 output, S10 sample or frozen hash
was altered. Graphify is refreshed after reconciliation so its source commit and document
navigation describe the merged state through S10.
