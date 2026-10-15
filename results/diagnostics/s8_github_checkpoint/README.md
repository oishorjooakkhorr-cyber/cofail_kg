# Preserved GitHub S8 checkpoint

Source: GitHub commit `6436653`, fetched while publishing local stages S8–S10 on 2026-10-15.
This directory preserves all nine files introduced by that commit byte-for-byte, including
its S8 code, tests, documentation, CSV and summary. They are a historical snapshot, not
the active implementation. To run that checkpoint's original tests, use its original
Git commit; the current tests target the current implementation and field schema.

The local and upstream S8 outputs have different schemas but agree on all 7,377 queries
for status, primary reason, leakage, saturation, S6 sample overlap and bridge multiplicity.
`comparison.json` records that verification. Both implementations report 7,362 consistent,
15 inconsistent, 186 leaky queries and 270 S6-overlap queries.

The upstream S8 decision records were preserved in the active decision log. The active
validator now follows their explicit leakage interpretation: match normalized BioHopR names
and resolved graph names, using Unicode word boundaries and a minimum normalized length
of four characters. A fresh calculation on all 7,377 reference queries reproduced every
saved leakage/status label. S9 population and S10 samples/hashes remain unchanged.

The active CSV schema is retained because the completed S9 evidence and frozen S10 samples
were built from it. This merge preserves both histories and both evidence snapshots; it
does not force-push or replace the upstream commit.
