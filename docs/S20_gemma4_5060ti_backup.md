# Gemma S20 backup completed - 2026-10-29

**Current verified status: 69/69 Gemma scientific-output files match Drive;
zero differences.** This supersedes the historical quota-blocked check below.
The researcher authorized the alternate university Google account, completed
reauthentication, and its exact email plus write access to the existing folder
were verified privately before upload. The cofail_gdrive remote now uses this
account; credentials remain outside the repository. The folder ID and backup
policy were not changed.

The documented manual repair workflow staged 1939 stable files, with the
normal ten-minute rule, under backup ID
20261029T143019162Z-9bd75fe433dc468788cf19d527aba302. Gemma uploads succeeded.
A separate exact-list, one-way rclone checksum check at **14:33:42 UTC** exited
zero and reported:

```text
Google drive root 'current': 0 differences found
Google drive root 'current': 69 matching files
```

The matching set includes all twenty raw attempt-1 episodes, their immutable
configuration, twenty evaluator metrics, and 28 other diagnostic/evidence files.
Every local MD5 still matches the inventory retained below. No inference or
scientific output was rerun or modified. Local transcripts:
`.venv/gemma-bracu-check.txt` and `.venv/gemma-bracu-check-combined.txt`.

**Broader backup limitation:** the whole-repository copy exited 1 because it
could not archive nine older S13-S15 files: Drive returned `cannotAddParent`
while moving their existing versions into history. Those files are outside
this Gemma run. Their existing remote versions were not deleted or overwritten;
no preservation rule was bypassed. Gemma's separate 69-file check passed, but
this is not a claim that all 1939 repository outputs were refreshed.
The backup log is
`C:\Users\USERAS\AppData\Local\CoFail-KG-Backup\20261029T143019162Z-9bd75fe433dc468788cf19d527aba302.log`.
Resolve those older-file ownership/move permissions separately before relying
on an overall zero-exit backup. No code or profile change was needed here.

---

# Gemma S20 Drive publication check - 2026-10-29

GitHub result commit 8c53402 was pushed to main, following pre-inference
launcher/authorization b49ac91. Destination used, without substitution:
`cofail_gdrive,root_folder_id=1lA-lOinAY1Z8m9fpvQD2QQyxgonMGxbk:current`.

The documented wrapped push staged 1939 stable files at 14:20:47 UTC.
All 69 Gemma scientific-output files below were older than ten minutes.
Drive rejected uploads with HTTP 403 storageQuotaExceeded. The specific copy
process was stopped after repeated permanent quota errors. The wrapper exited
1 and explicitly reported that Git push had already succeeded. No local or
shared data was deleted, and the age rule was not bypassed.

A subsequent exact-list, one-way rclone checksum check at 14:22:51 UTC exited
1. Its combined report marks all 69 paths as source-only (missing on Drive):

```text
Google drive root 'current': 69 files missing
Google drive root 'current': 69 differences found
Google drive root 'current': 69 errors while checking
```

**Verified backup status: 0/69 present; 69/69 missing. Not backed up.**
The twenty raw episodes and configuration remain intact locally; their SHA-256
values are in final-run-hashes.json. Diagnostic evidence is on GitHub. Free
capacity/increase storage in the authenticated account, rerun the existing
backup workflow, and checksum-check these exact paths. Do not rerun episodes.

Backup log (local):
`C:\Users\USERAS\AppData\Local\CoFail-KG-Backup\20261029T142043155Z-8145a78ee14e4a008fe0142c401873c9.log`.
Command transcripts: `.venv/gemma-push-backup.txt`, `.venv/gemma-drive-check.txt`
and `.venv/gemma-drive-check-combined.txt`. No credentials are included here.

## Expected local MD5 inventory (all missing on Drive at the check)

| Path relative to repository / Drive current | MD5 |
|---|---|
| `results/diagnostics/s20/gemma4-5060ti-16k-20261028/final-run-hashes.json` | `2b29889625fe87bb2adea8f4de55c903` |
| `results/diagnostics/s20/gemma4-5060ti-16k-20261028/final-validation.json` | `c2d56c0cfe3d02fbd4e4b0d1740aabe0` |
| `results/diagnostics/s20/gemma4-5060ti-16k-20261028/historical-hashes.json` | `346877730f5e924bebe16f9e20aa3ad8` |
| `results/diagnostics/s20/gemma4-5060ti-16k-20261028/host-server.json` | `0f4155b9b2852c45b59df3619a598494` |
| `results/diagnostics/s20/gemma4-5060ti-16k-20261028/identity.json` | `fd84510a4e6d87d6835bd6300c31cd68` |
| `results/diagnostics/s20/gemma4-5060ti-16k-20261028/manifest.json` | `4ad9369a97631f9835cf02e1235e57bf` |
| `results/diagnostics/s20/gemma4-5060ti-16k-20261028/metrics/BH2_00461.json` | `a574696c8d9623ba7f8b6c9f8b46c2f4` |
| `results/diagnostics/s20/gemma4-5060ti-16k-20261028/metrics/BH2_02033.json` | `87f21e87e58d80be2e34c9676573b62e` |
| `results/diagnostics/s20/gemma4-5060ti-16k-20261028/metrics/BH2_03434.json` | `ccfdcfbceabbf688bfc9ceeaaad840cc` |
| `results/diagnostics/s20/gemma4-5060ti-16k-20261028/metrics/BH2_03619.json` | `2621766c9f9177073ad64b7612e8a4ed` |
| `results/diagnostics/s20/gemma4-5060ti-16k-20261028/metrics/BH2_03750.json` | `211c42abb4bc6512a3608ad4e3425182` |
| `results/diagnostics/s20/gemma4-5060ti-16k-20261028/metrics/BH2_03760.json` | `d9eb5e438705835032b0aa0dacc08588` |
| `results/diagnostics/s20/gemma4-5060ti-16k-20261028/metrics/BH2_03762.json` | `f1902944f8933e845a1441ac1976a056` |
| `results/diagnostics/s20/gemma4-5060ti-16k-20261028/metrics/BH2_03850.json` | `0f362113e4fe41e32fd500ed82d9a2bb` |
| `results/diagnostics/s20/gemma4-5060ti-16k-20261028/metrics/BH2_03856.json` | `f4f3530c55fd0e24590d80ecf23deed4` |
| `results/diagnostics/s20/gemma4-5060ti-16k-20261028/metrics/BH2_03879.json` | `ddf24b39bcb2beb7db9cdf006eb48076` |
| `results/diagnostics/s20/gemma4-5060ti-16k-20261028/metrics/BH2_03881.json` | `c815545b83fcff386b4fa924ad238ea8` |
| `results/diagnostics/s20/gemma4-5060ti-16k-20261028/metrics/BH2_03953.json` | `854782748eafabfb7acf1ca74bb8d490` |
| `results/diagnostics/s20/gemma4-5060ti-16k-20261028/metrics/BH2_03991.json` | `cfd9bac7c46efb0e1843802568300de4` |
| `results/diagnostics/s20/gemma4-5060ti-16k-20261028/metrics/BH2_04003.json` | `b01cdcbdf302522880564adfac875d15` |
| `results/diagnostics/s20/gemma4-5060ti-16k-20261028/metrics/BH2_04007.json` | `44d5f993a7d1e45008d78ad7d67be8cd` |
| `results/diagnostics/s20/gemma4-5060ti-16k-20261028/metrics/BH2_04425.json` | `7b18b3a4df0cf5db541286a2da293dd5` |
| `results/diagnostics/s20/gemma4-5060ti-16k-20261028/metrics/BH2_05366.json` | `8a2c11be18a5fb96e958ef0a2428e488` |
| `results/diagnostics/s20/gemma4-5060ti-16k-20261028/metrics/BH2_05686.json` | `08dd16894d25220ed32a631249fff35f` |
| `results/diagnostics/s20/gemma4-5060ti-16k-20261028/metrics/BH2_05843.json` | `4903861c4a87846f3dddcdddab4c462f` |
| `results/diagnostics/s20/gemma4-5060ti-16k-20261028/metrics/BH2_06427.json` | `4d3412e299b47d9b855129ca46daf481` |
| `results/diagnostics/s20/gemma4-5060ti-16k-20261028/offline-harness-path-error.txt` | `05c651daae25ef112c487e12edd54c82` |
| `results/diagnostics/s20/gemma4-5060ti-16k-20261028/offline-report-exit.txt` | `21438ef4b9ad4fc266b6129a2f60de29` |
| `results/diagnostics/s20/gemma4-5060ti-16k-20261028/offline-report.txt` | `83fbe35106af14d3952d16e767e0fd4a` |
| `results/diagnostics/s20/gemma4-5060ti-16k-20261028/paired-comparison.csv` | `3f7f9480496b858b495087ff1f3e1b4a` |
| `results/diagnostics/s20/gemma4-5060ti-16k-20261028/paired-inspection.json` | `b8780b12ce36f5cab84384decd9c04d1` |
| `results/diagnostics/s20/gemma4-5060ti-16k-20261028/preflight-console.txt` | `dc4dc4a630ee6b68ab5a0074571a48b1` |
| `results/diagnostics/s20/gemma4-5060ti-16k-20261028/review-mutation.txt` | `01875466d43e8ece2e0d9163431c6fea` |
| `results/diagnostics/s20/gemma4-5060ti-16k-20261028/run-console.txt` | `039b78a47935f8003c328f5a1746c762` |
| `results/diagnostics/s20/gemma4-5060ti-16k-20261028/run-exit.txt` | `21438ef4b9ad4fc266b6129a2f60de29` |
| `results/diagnostics/s20/gemma4-5060ti-16k-20261028/runtime-cleanup.json` | `86c7a2787445c4bff31b68cd40dca61a` |
| `results/diagnostics/s20/gemma4-5060ti-16k-20261028/runtime-samples.jsonl` | `dbf30f452a178f09ca34c23c2114f80b` |
| `results/diagnostics/s20/gemma4-5060ti-16k-20261028/runtime-versions.json` | `a395265ec7c9f416fd1eb66a376c16c6` |
| `results/diagnostics/s20/gemma4-5060ti-16k-20261028/server.stderr.log` | `3be2dc92d221dc1ef4399290a0f7c01c` |
| `results/diagnostics/s20/gemma4-5060ti-16k-20261028/server.stdout.log` | `7a5728db134fdcdd3456b3b9e25a9005` |
| `results/diagnostics/s20/gemma4-5060ti-16k-20261028/source-relocation.json` | `b66b12836aa585d9c4f49fa30c2e36c5` |
| `results/diagnostics/s20/gemma4-5060ti-16k-20261028/summary.json` | `e29cf4442dea1cade8c519635d829317` |
| `results/diagnostics/s20/gemma4-5060ti-16k-20261028/synthetic-ps.json` | `d6d61287a5f50d4a363cbd9636e5c2e7` |
| `results/diagnostics/s20/gemma4-5060ti-16k-20261028/synthetic-result.json` | `ebfd4431d316b619ba95467072abbe3b` |
| `results/diagnostics/s20/gemma4-5060ti-16k-20261028/synthetic.json` | `c08dbb09b44c5eaffa41f9faff422601` |
| `results/diagnostics/s20/gemma4-5060ti-16k-20261028/tests-focused.txt` | `a04ce403aa94df33d369dea50b6f7d84` |
| `results/diagnostics/s20/gemma4-5060ti-16k-20261028/tests-full.txt` | `f342db15874dd83e61943ba58e3cd7ef` |
| `results/diagnostics/s20/gemma4-5060ti-16k-20261028/unload.json` | `daa372b1f762e5911bb9f5aec45d5ce8` |
| `results/runs/screening-5060ti/gemma4-5060ti-16k-20261028/BH2_00461__Gemma4-E4B__a1.json` | `e032b6ab3b732fbb5311dd6972706086` |
| `results/runs/screening-5060ti/gemma4-5060ti-16k-20261028/BH2_02033__Gemma4-E4B__a1.json` | `4a1e010d89fc93e6d879a27c51620455` |
| `results/runs/screening-5060ti/gemma4-5060ti-16k-20261028/BH2_03434__Gemma4-E4B__a1.json` | `5920b24562990b6ede798cc2879c7005` |
| `results/runs/screening-5060ti/gemma4-5060ti-16k-20261028/BH2_03619__Gemma4-E4B__a1.json` | `189a787c534d8bc6099a3b766ddf20be` |
| `results/runs/screening-5060ti/gemma4-5060ti-16k-20261028/BH2_03750__Gemma4-E4B__a1.json` | `7488bc1297a5a57c219772ac39424085` |
| `results/runs/screening-5060ti/gemma4-5060ti-16k-20261028/BH2_03760__Gemma4-E4B__a1.json` | `c2e82d4ce64228c4b79bd03480d285b8` |
| `results/runs/screening-5060ti/gemma4-5060ti-16k-20261028/BH2_03762__Gemma4-E4B__a1.json` | `ee662b37135aeb7c38e5a79e30a6cfeb` |
| `results/runs/screening-5060ti/gemma4-5060ti-16k-20261028/BH2_03850__Gemma4-E4B__a1.json` | `5246c91c7dab7cafabefbe6e6d75bc1a` |
| `results/runs/screening-5060ti/gemma4-5060ti-16k-20261028/BH2_03856__Gemma4-E4B__a1.json` | `96a1d502f3a03431ece3981ea0cfe467` |
| `results/runs/screening-5060ti/gemma4-5060ti-16k-20261028/BH2_03879__Gemma4-E4B__a1.json` | `4f0bc4fa846303ae99b5f3f596142ab0` |
| `results/runs/screening-5060ti/gemma4-5060ti-16k-20261028/BH2_03881__Gemma4-E4B__a1.json` | `ecf845a49c2a522888480baf9f4f9565` |
| `results/runs/screening-5060ti/gemma4-5060ti-16k-20261028/BH2_03953__Gemma4-E4B__a1.json` | `f8df7cb2eb5f00c24269c08207d19c25` |
| `results/runs/screening-5060ti/gemma4-5060ti-16k-20261028/BH2_03991__Gemma4-E4B__a1.json` | `70492d0ff6e5b2f8e4e6352b3cbf24c2` |
| `results/runs/screening-5060ti/gemma4-5060ti-16k-20261028/BH2_04003__Gemma4-E4B__a1.json` | `9f8a6ae273d9df4957295f129f2e9afd` |
| `results/runs/screening-5060ti/gemma4-5060ti-16k-20261028/BH2_04007__Gemma4-E4B__a1.json` | `10071d4fc52653711b521cd15a379616` |
| `results/runs/screening-5060ti/gemma4-5060ti-16k-20261028/BH2_04425__Gemma4-E4B__a1.json` | `bd24a996900fa827ad1b4e2c67d68b2a` |
| `results/runs/screening-5060ti/gemma4-5060ti-16k-20261028/BH2_05366__Gemma4-E4B__a1.json` | `2069d08e2aeb70210a72295eed4c4d17` |
| `results/runs/screening-5060ti/gemma4-5060ti-16k-20261028/BH2_05686__Gemma4-E4B__a1.json` | `b32e38712eed3f5348b4b6d76c4a50c6` |
| `results/runs/screening-5060ti/gemma4-5060ti-16k-20261028/BH2_05843__Gemma4-E4B__a1.json` | `f2bfd1740df29d42e3535e894c2a265f` |
| `results/runs/screening-5060ti/gemma4-5060ti-16k-20261028/BH2_06427__Gemma4-E4B__a1.json` | `2d446382817671fe8333d2ae279fb068` |
| `results/runs/screening-5060ti/gemma4-5060ti-16k-20261028/Gemma4-E4B.config.json` | `4ad9369a97631f9835cf02e1235e57bf` |
