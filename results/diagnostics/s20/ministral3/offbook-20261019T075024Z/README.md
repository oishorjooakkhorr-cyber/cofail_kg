# One exploratory BH2_04425 episode (2026-10-19)

Diagnostic only; excluded from official S20 and D3. Researcher requested one fresh
full episode after the isolated HTTP replay. Official ERROR/CONNECTION retained.

Result: SUCCESS in 237.017349 seconds, six native calls, all six well-formed.
The final reply contains 65 unique GOLD/SUPPORTED answer items. Benchmark
precision=100%, recall=86.6667% (65/75), F1=0.9285714.

All model/prompt/tool/generation settings match screening. Only the diagnostic
request timeout is 600 seconds instead of 120, capped by the unchanged total
600-second episode deadline. See manifest.json for the exact run/configuration.

The seventh response took 135.261922 seconds (2576 output tokens) and was prose,
which the parser rejected. The unchanged runner's single re-prompt then returned
valid JSON in 74.903480 seconds (1297 output tokens). The full episode therefore
benefited from waiting past the original 120-second request limit.

The model retrieved only the first 50 of 60 Doxycycline neighbors despite the
has_more=true flag, then retrieved Fusidic acid's 28-item complete list. It did
not paginate the remaining Doxycycline results; final benchmark coverage is
incomplete. These are frozen-KG/benchmark labels, not independently verified
medical claims.

Full saved episode: E:\Phitron Thesis\cofail_kg\results\runs\diagnostic\ministral3-bh204425-diagnostic-20261019T075024Z\BH2_04425__Ministral3-8B__a1.json

All 84 official run files, the screening table/metrics and other protected
identities retain their hashes (290 distinct protected files checked).
No production source/config edits, official replacement, D3 recalculation,
second exploratory episode, commit or push. An initial launcher path-type error
was corrected before any model inference; its preflight-only log is retained.
