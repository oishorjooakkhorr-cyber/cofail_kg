# Qwen35-9B 32K S20 Drive verification — 2026-10-29

**74 matching files, zero differences; independent checksum check exited0 at
16:21:53 UTC (22:21:53 Dhaka).** Includes20 raw attempt-1 episodes, immutable
configuration,20 metrics and33 other scientific evidence files. Local MD5 hashes
still match the inventory captured before backup. Existing shared folder:
[CoFail-KG-Backups](https://drive.google.com/drive/folders/1lA-lOinAY1Z8m9fpvQD2QQyxgonMGxbk), current/.

Results commit b0d0f9e was pushed to GitHub main. Executable/authorization commits
cea27c7 and3bc7b69 preceded synthetic inference; corrected guard d293ea7 preceded
all official queries. Final documentation follow-up adds this proof and restores
unintended task-document text encoding changes; historical task text is intact.

First documented manual repair backup started16:12:35 UTC, staged2101 stable
files and deferred fresh outputs under the unchanged10-minute age rule. All74
became eligible at16:19:22.967 UTC. Second backup started16:19:47 UTC, staged2144
stable files, uploaded the new outputs and retained previous remote versions.
No age override, destination change, credential/profile change or deletion.
Both broad copies exit1 on the same nine older S13–S15 cannotAddParent archive
permission errors. No Qwen32K path appears in those errors. This exact-list check
establishes scoped success, not a claim that all repository outputs were refreshed.

Commands used scripts/backup_cofail_kg.ps1 with RepositoryRoot D:/cofailKG and
installed C:/Users/USERAS/.local/bin/rclone.exe, followed independently by:

```powershell
& C:/Users/USERAS/.local/bin/rclone.exe check D:/cofailKG 'cofail_gdrive,root_folder_id=1lA-lOinAY1Z8m9fpvQD2QQyxgonMGxbk:current' --files-from .venv/qwen32-drive-files.txt --one-way --checksum
```

Logs retained in LOCALAPPDATA/CoFail-KG-Backup and local .venv/qwen32-backup-*,
.venv/qwen32-drive-check.txt and .venv/qwen32-drive-outcome.json. Source .py files
are on GitHub; the documented Drive format allowlist excludes them. No further
inference, model or S21 work. Model unloaded and isolated server stopped.

|Expected file|MD5|
|---|---|
|`results/diagnostics/s20/qwen35-5060ti-32k-20261029/baseline-comparability.json`|`9b7f227b5d9529b813969f95ae71c714`|
|`results/diagnostics/s20/qwen35-5060ti-32k-20261029/final-run-hashes.json`|`77b00a827c6d7dfe92b42db895aeb8c9`|
|`results/diagnostics/s20/qwen35-5060ti-32k-20261029/final-validation.json`|`ddc7b8f711960aa5be8db4d612d61d3e`|
|`results/diagnostics/s20/qwen35-5060ti-32k-20261029/historical-hashes.json`|`e928413653929344f304830da26e5f63`|
|`results/diagnostics/s20/qwen35-5060ti-32k-20261029/host.json`|`68aa0354052aef4797e2f29f0633c570`|
|`results/diagnostics/s20/qwen35-5060ti-32k-20261029/identity.json`|`8c0667b361a06c34d75c85b1c0268201`|
|`results/diagnostics/s20/qwen35-5060ti-32k-20261029/investigation-console.txt`|`ddc7b8f711960aa5be8db4d612d61d3e`|
|`results/diagnostics/s20/qwen35-5060ti-32k-20261029/manifest.json`|`c9cdd964036b4d1cbc52489539fbdad5`|
|`results/diagnostics/s20/qwen35-5060ti-32k-20261029/metrics/BH2_00461.json`|`04c12f987c0951f410594ee34d78d55d`|
|`results/diagnostics/s20/qwen35-5060ti-32k-20261029/metrics/BH2_02033.json`|`3c6eeef30c32db0dcb0c43c797c8a8c4`|
|`results/diagnostics/s20/qwen35-5060ti-32k-20261029/metrics/BH2_03434.json`|`8b3af8d23051b38680971ef1c4a64bac`|
|`results/diagnostics/s20/qwen35-5060ti-32k-20261029/metrics/BH2_03619.json`|`ebc1ea9aae2ad0c4379f376a792e76ef`|
|`results/diagnostics/s20/qwen35-5060ti-32k-20261029/metrics/BH2_03750.json`|`f5be208517b05a7a8023ca0aae4a8f02`|
|`results/diagnostics/s20/qwen35-5060ti-32k-20261029/metrics/BH2_03760.json`|`fbff2f7c7ae845e75c7076b4520e87ac`|
|`results/diagnostics/s20/qwen35-5060ti-32k-20261029/metrics/BH2_03762.json`|`cb81ac24eaedb174e8ed2e3804dfbcf3`|
|`results/diagnostics/s20/qwen35-5060ti-32k-20261029/metrics/BH2_03850.json`|`07c2abf75098d132fdf83636a263101f`|
|`results/diagnostics/s20/qwen35-5060ti-32k-20261029/metrics/BH2_03856.json`|`dcba224de319fe8a4f2d23b2040c1362`|
|`results/diagnostics/s20/qwen35-5060ti-32k-20261029/metrics/BH2_03879.json`|`33d3583524aae2290e788d9c0fdb396f`|
|`results/diagnostics/s20/qwen35-5060ti-32k-20261029/metrics/BH2_03881.json`|`33d5c9f013119df85026114aef0e70fe`|
|`results/diagnostics/s20/qwen35-5060ti-32k-20261029/metrics/BH2_03953.json`|`a0753b4743695023452a80aa22ae426a`|
|`results/diagnostics/s20/qwen35-5060ti-32k-20261029/metrics/BH2_03991.json`|`b59f65658f547dc71ce0d14a1e83d319`|
|`results/diagnostics/s20/qwen35-5060ti-32k-20261029/metrics/BH2_04003.json`|`5e70c34a8e1092500d3f53ce412027a3`|
|`results/diagnostics/s20/qwen35-5060ti-32k-20261029/metrics/BH2_04007.json`|`bab7c135f6e9420470ac1367ed9daeb8`|
|`results/diagnostics/s20/qwen35-5060ti-32k-20261029/metrics/BH2_04425.json`|`1b591e90fde273da5fab8b117be0ba72`|
|`results/diagnostics/s20/qwen35-5060ti-32k-20261029/metrics/BH2_05366.json`|`829285177189aba05256edb3514a16a4`|
|`results/diagnostics/s20/qwen35-5060ti-32k-20261029/metrics/BH2_05686.json`|`437e6024b31b83909a0a6f816a39aba2`|
|`results/diagnostics/s20/qwen35-5060ti-32k-20261029/metrics/BH2_05843.json`|`49845d3bbc7fa28dc3ff2ba2abed0cab`|
|`results/diagnostics/s20/qwen35-5060ti-32k-20261029/metrics/BH2_06427.json`|`f2c61b0547400a797b2544c609482999`|
|`results/diagnostics/s20/qwen35-5060ti-32k-20261029/offline-report.txt`|`21007222a367e790588e31085a81bce2`|
|`results/diagnostics/s20/qwen35-5060ti-32k-20261029/packages.txt`|`f5c7414e3c1f12bb89fb551b351b63e6`|
|`results/diagnostics/s20/qwen35-5060ti-32k-20261029/paired-comparison.csv`|`119055ad07879ddb75b094b0750a3312`|
|`results/diagnostics/s20/qwen35-5060ti-32k-20261029/paired-inspection.json`|`c3400c1cbfe21d457388e9fc8725afa3`|
|`results/diagnostics/s20/qwen35-5060ti-32k-20261029/preflight-console.txt`|`46cba2a050f18e57635a80b41c139339`|
|`results/diagnostics/s20/qwen35-5060ti-32k-20261029/preflight-exit.txt`|`a5ea0ad9260b1550a14cc58d2c39b03d`|
|`results/diagnostics/s20/qwen35-5060ti-32k-20261029/preflight-initial.config.json`|`5bc995782301a5f9562f9f7966c643f4`|
|`results/diagnostics/s20/qwen35-5060ti-32k-20261029/preflight-initial.manifest.json`|`5bc995782301a5f9562f9f7966c643f4`|
|`results/diagnostics/s20/qwen35-5060ti-32k-20261029/prepare-corrected-console.txt`|`854c52da66f53ad5f0b979612f9f090d`|
|`results/diagnostics/s20/qwen35-5060ti-32k-20261029/run-console.txt`|`9668dd66514c3094505808144b38db04`|
|`results/diagnostics/s20/qwen35-5060ti-32k-20261029/run-exit.txt`|`21438ef4b9ad4fc266b6129a2f60de29`|
|`results/diagnostics/s20/qwen35-5060ti-32k-20261029/runtime-analysis.json`|`a50a609eccd52056ffbff4ba70efa750`|
|`results/diagnostics/s20/qwen35-5060ti-32k-20261029/runtime-samples.jsonl`|`bd01ee5e7e07e019d6a5da76c54d0a6a`|
|`results/diagnostics/s20/qwen35-5060ti-32k-20261029/server-version.json`|`732ed83810832a969861a5c0f70ddfea`|
|`results/diagnostics/s20/qwen35-5060ti-32k-20261029/server.pid.txt`|`474391c58d89491f5310bf36a4726b09`|
|`results/diagnostics/s20/qwen35-5060ti-32k-20261029/server.stderr.log`|`cb9f9fa281e2b57c7149269e5f5e5c65`|
|`results/diagnostics/s20/qwen35-5060ti-32k-20261029/server.stdout.log`|`a5e108595590c08781221b56fc702098`|
|`results/diagnostics/s20/qwen35-5060ti-32k-20261029/summary.json`|`3caaff6f8eb5dd2b9fab5435c9858c6d`|
|`results/diagnostics/s20/qwen35-5060ti-32k-20261029/synthetic-ps.json`|`c00d47b64898f38ee1e30672c41a41ca`|
|`results/diagnostics/s20/qwen35-5060ti-32k-20261029/synthetic-result.json`|`2527f268cab3dd2fb9e28dc914afb706`|
|`results/diagnostics/s20/qwen35-5060ti-32k-20261029/synthetic.json`|`4f6e60d0ae87114bee5eb7070fb5ba67`|
|`results/diagnostics/s20/qwen35-5060ti-32k-20261029/tests-corrected-guard.txt`|`7a9eadd2944783094f8f6660fd0f021f`|
|`results/diagnostics/s20/qwen35-5060ti-32k-20261029/tests-focused.txt`|`8dcd312fd6a66a70def139c115b64a77`|
|`results/diagnostics/s20/qwen35-5060ti-32k-20261029/tests-full.txt`|`ca70ecdc84fe4976420465386bb57362`|
|`results/diagnostics/s20/qwen35-5060ti-32k-20261029/unload.json`|`4897aae397dca9f66ca95cf50250213f`|
|`results/runs/screening-5060ti/qwen35-5060ti-32k-20261029/BH2_00461__Qwen35-9B__a1.json`|`e77a2ba257e1a6c8f0a63b2448980927`|
|`results/runs/screening-5060ti/qwen35-5060ti-32k-20261029/BH2_02033__Qwen35-9B__a1.json`|`d6d6229bab3b0d900e54d2f186fc3541`|
|`results/runs/screening-5060ti/qwen35-5060ti-32k-20261029/BH2_03434__Qwen35-9B__a1.json`|`4bc1e81528e0be943b3b2142de182fa2`|
|`results/runs/screening-5060ti/qwen35-5060ti-32k-20261029/BH2_03619__Qwen35-9B__a1.json`|`2e9bb0208c1ec3ebdc4d1c2a23538f68`|
|`results/runs/screening-5060ti/qwen35-5060ti-32k-20261029/BH2_03750__Qwen35-9B__a1.json`|`3f0af230ef6b9ca88cdacfc3603e470c`|
|`results/runs/screening-5060ti/qwen35-5060ti-32k-20261029/BH2_03760__Qwen35-9B__a1.json`|`c553d8eb54f43992fc70b646d05ed582`|
|`results/runs/screening-5060ti/qwen35-5060ti-32k-20261029/BH2_03762__Qwen35-9B__a1.json`|`b853df4ec51eebb02f1f51a70e49c2f5`|
|`results/runs/screening-5060ti/qwen35-5060ti-32k-20261029/BH2_03850__Qwen35-9B__a1.json`|`f004c786bb51e36a90a942491f69a7b6`|
|`results/runs/screening-5060ti/qwen35-5060ti-32k-20261029/BH2_03856__Qwen35-9B__a1.json`|`bf125e624087ae1a403dce50fe628e6e`|
|`results/runs/screening-5060ti/qwen35-5060ti-32k-20261029/BH2_03879__Qwen35-9B__a1.json`|`045ba516bbec77294108def22eb5b385`|
|`results/runs/screening-5060ti/qwen35-5060ti-32k-20261029/BH2_03881__Qwen35-9B__a1.json`|`e254762c919aea3ee12763d95435e12e`|
|`results/runs/screening-5060ti/qwen35-5060ti-32k-20261029/BH2_03953__Qwen35-9B__a1.json`|`1b05f6ef21afedb6427282ca795beec6`|
|`results/runs/screening-5060ti/qwen35-5060ti-32k-20261029/BH2_03991__Qwen35-9B__a1.json`|`ec3a9099e94e35735adfad838ea6c9d0`|
|`results/runs/screening-5060ti/qwen35-5060ti-32k-20261029/BH2_04003__Qwen35-9B__a1.json`|`e65c9d08c9e1f903b7aced319ab8bca3`|
|`results/runs/screening-5060ti/qwen35-5060ti-32k-20261029/BH2_04007__Qwen35-9B__a1.json`|`f35fef1e2d27ee249d9b4042a22686e1`|
|`results/runs/screening-5060ti/qwen35-5060ti-32k-20261029/BH2_04425__Qwen35-9B__a1.json`|`e1587bcca3a283b1a11fa38e3cb7a065`|
|`results/runs/screening-5060ti/qwen35-5060ti-32k-20261029/BH2_05366__Qwen35-9B__a1.json`|`bedaf3437f9d59228a2d6213b62150b2`|
|`results/runs/screening-5060ti/qwen35-5060ti-32k-20261029/BH2_05686__Qwen35-9B__a1.json`|`85b3f81f07e0e012f06742f315c814f4`|
|`results/runs/screening-5060ti/qwen35-5060ti-32k-20261029/BH2_05843__Qwen35-9B__a1.json`|`8151f5b434bffaa913d12384a74c9545`|
|`results/runs/screening-5060ti/qwen35-5060ti-32k-20261029/BH2_06427__Qwen35-9B__a1.json`|`04d86bacfde45d1c6bd8c8c1950373f9`|
|`results/runs/screening-5060ti/qwen35-5060ti-32k-20261029/Qwen35-9B.config.json`|`c9cdd964036b4d1cbc52489539fbdad5`|
