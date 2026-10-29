# Qwen35 RTX 5060 Ti S20 Drive verification — 2026-10-29

**66 matching files, zero differences; rclone check exited zero at15:40:26 UTC
(21:40:26 Dhaka).** Includes20 raw attempt-1 episodes,config,20 metrics and25
other scientific evidence files. Shared folder ID1lA-lOinAY1Z8m9fpvQD2QQyxgonMGxbk,
current/. All local MD5 values remain unchanged from the pre-backup inventory.

First documented manual repair backup deferred fresh files under default10-minute
age policy. Second pass began15:38:26 UTC after all66 were eligible at15:38:11;
staged2070 stable repository files. No age override,version-preservation change or
deletion. Both broad copies retain the known nine unrelated historical archive
errors (cannotAddParent). Global backup success is not claimed. Independent
one-way checksum check of exactly this run's66 files establishes scoped success.

Command: rclone check D:/cofailKG
cofail_gdrive,root_folder_id=1lA-lOinAY1Z8m9fpvQD2QQyxgonMGxbk:current
--files-from .venv/qwen-drive-files.txt --one-way --checksum.
Backup used scripts/backup_cofail_kg.ps1 with explicit RepositoryRoot and installed
C:/Users/USERAS/.local/bin/rclone.exe; initial omitted-root invocation failed at
PowerShell parameter binding before transfer. OAuth settings were untouched.
Logs retained under LOCALAPPDATA/CoFail-KG-Backup and local .venv/qwen-backup*.
Python executable scripts are on GitHub; backup allowlist excludes .py.

Results commit d20926a and pre-inference launcher ad8e549 were pushed to main.
Final documentation commit adds this checksum proof and exact historical placement.
No other model or S21 started. Model unloaded and isolated server stopped.

|File|MD5|
|---|---|
|`results/diagnostics/s20/qwen35-5060ti-16k-20261029/final-run-hashes.json`|`6bf41016df348a3d55f336ac816ee9d3`|
|`results/diagnostics/s20/qwen35-5060ti-16k-20261029/final-validation.json`|`dccab39e226325e36377f9412ca55821`|
|`results/diagnostics/s20/qwen35-5060ti-16k-20261029/historical-hashes.json`|`d8af47a0252ce8f2fed7b84a35c49fa0`|
|`results/diagnostics/s20/qwen35-5060ti-16k-20261029/host.json`|`fc8db71d86ca9903cfbf14702126bb3e`|
|`results/diagnostics/s20/qwen35-5060ti-16k-20261029/identity.json`|`8c0667b361a06c34d75c85b1c0268201`|
|`results/diagnostics/s20/qwen35-5060ti-16k-20261029/manifest.json`|`4a92d65200cb569920de248033422364`|
|`results/diagnostics/s20/qwen35-5060ti-16k-20261029/metrics/BH2_00461.json`|`2dacaffae694718dfa7d3c40107a29ee`|
|`results/diagnostics/s20/qwen35-5060ti-16k-20261029/metrics/BH2_02033.json`|`a6adf3517527ca85d7fb63726baf36d3`|
|`results/diagnostics/s20/qwen35-5060ti-16k-20261029/metrics/BH2_03434.json`|`f678064176965da8b6d8d30c3b4b6335`|
|`results/diagnostics/s20/qwen35-5060ti-16k-20261029/metrics/BH2_03619.json`|`a956b7cf4ec3ef70e8e7694a272428fc`|
|`results/diagnostics/s20/qwen35-5060ti-16k-20261029/metrics/BH2_03750.json`|`5d7a2c6d4ba19c16a0aed26334184bdc`|
|`results/diagnostics/s20/qwen35-5060ti-16k-20261029/metrics/BH2_03760.json`|`38eabb28c31fc15e9bd88099416b737b`|
|`results/diagnostics/s20/qwen35-5060ti-16k-20261029/metrics/BH2_03762.json`|`0e62a51b15c7aeae904c6881e343ae2e`|
|`results/diagnostics/s20/qwen35-5060ti-16k-20261029/metrics/BH2_03850.json`|`97e70537b321ee977eb39599bf665e58`|
|`results/diagnostics/s20/qwen35-5060ti-16k-20261029/metrics/BH2_03856.json`|`f1d872cd2869d426ac473d348b95fb73`|
|`results/diagnostics/s20/qwen35-5060ti-16k-20261029/metrics/BH2_03879.json`|`47d7316676975d38ac743f7667538003`|
|`results/diagnostics/s20/qwen35-5060ti-16k-20261029/metrics/BH2_03881.json`|`f451f362a159c8446c08fdf5bdca39ee`|
|`results/diagnostics/s20/qwen35-5060ti-16k-20261029/metrics/BH2_03953.json`|`d499ebde600de2e9b7f41e4a60e21f90`|
|`results/diagnostics/s20/qwen35-5060ti-16k-20261029/metrics/BH2_03991.json`|`2f4292440ef3c7873b19a60744330db0`|
|`results/diagnostics/s20/qwen35-5060ti-16k-20261029/metrics/BH2_04003.json`|`4507ccf670b319bb9bead29c991500bc`|
|`results/diagnostics/s20/qwen35-5060ti-16k-20261029/metrics/BH2_04007.json`|`38d8fb521ebb2b71086dd3856458ed97`|
|`results/diagnostics/s20/qwen35-5060ti-16k-20261029/metrics/BH2_04425.json`|`d6dac7a95166944e08b1399a016c992c`|
|`results/diagnostics/s20/qwen35-5060ti-16k-20261029/metrics/BH2_05366.json`|`74d77efb2211be9155f54aa717bc536d`|
|`results/diagnostics/s20/qwen35-5060ti-16k-20261029/metrics/BH2_05686.json`|`3205d4deb18da22cd48ca5137e4763ed`|
|`results/diagnostics/s20/qwen35-5060ti-16k-20261029/metrics/BH2_05843.json`|`5aefc56bd8217b35a995485eae880c1e`|
|`results/diagnostics/s20/qwen35-5060ti-16k-20261029/metrics/BH2_06427.json`|`c832bcee6ade63f56acdc439b2b0a953`|
|`results/diagnostics/s20/qwen35-5060ti-16k-20261029/offline-exit.txt`|`21438ef4b9ad4fc266b6129a2f60de29`|
|`results/diagnostics/s20/qwen35-5060ti-16k-20261029/offline-relative-path-failure.txt`|`d8fdc000b1daa9a232b3a431bc81c885`|
|`results/diagnostics/s20/qwen35-5060ti-16k-20261029/offline-report.txt`|`bd20922636cd57862f2dc8e092540562`|
|`results/diagnostics/s20/qwen35-5060ti-16k-20261029/paired-comparison.csv`|`2ab82f97a436fe4f9ed686fa849d6444`|
|`results/diagnostics/s20/qwen35-5060ti-16k-20261029/paired-inspection.json`|`50ae3981dd2c6ef0dd05c195dab37a8e`|
|`results/diagnostics/s20/qwen35-5060ti-16k-20261029/preflight-console.txt`|`366f5e316b008d4c8fce3b450b0a2199`|
|`results/diagnostics/s20/qwen35-5060ti-16k-20261029/run-console.txt`|`8cea30ee22487e3795c2598e11e5641e`|
|`results/diagnostics/s20/qwen35-5060ti-16k-20261029/run-exit.txt`|`21438ef4b9ad4fc266b6129a2f60de29`|
|`results/diagnostics/s20/qwen35-5060ti-16k-20261029/runtime-samples.jsonl`|`3fb1971c6e5d5e697300d7d8c8d26bdb`|
|`results/diagnostics/s20/qwen35-5060ti-16k-20261029/server.pid.txt`|`c5f8cc3242dea7cc4a874e7c8d98c669`|
|`results/diagnostics/s20/qwen35-5060ti-16k-20261029/server.stderr.log`|`18a31981504290eee6cd641820c52655`|
|`results/diagnostics/s20/qwen35-5060ti-16k-20261029/server.stdout.log`|`3b6f8f5ad0d232efc7039f1bcffdde34`|
|`results/diagnostics/s20/qwen35-5060ti-16k-20261029/summary.json`|`7f5eeee6ddb0c557abba5c91a47dcef3`|
|`results/diagnostics/s20/qwen35-5060ti-16k-20261029/synthetic-ps.json`|`ce218a310aa00932d4160acd880484fa`|
|`results/diagnostics/s20/qwen35-5060ti-16k-20261029/synthetic-result.json`|`7a72cd9ffd4c5bc84b20c0ed3188d588`|
|`results/diagnostics/s20/qwen35-5060ti-16k-20261029/synthetic.json`|`9d8275c570232457cf95904367979a97`|
|`results/diagnostics/s20/qwen35-5060ti-16k-20261029/tests-focused.txt`|`e1b5a5a9126fda871b5ab89f87eb7e72`|
|`results/diagnostics/s20/qwen35-5060ti-16k-20261029/tests-full.txt`|`0418053663531f873ecf7d375e0280bd`|
|`results/diagnostics/s20/qwen35-5060ti-16k-20261029/unload.json`|`4139dbd12638ed6c5608715c77eac00f`|
|`results/runs/screening-5060ti/qwen35-5060ti-16k-20261029/BH2_00461__Qwen35-9B__a1.json`|`58a5f872c7ed22b46abb009ad2bb987a`|
|`results/runs/screening-5060ti/qwen35-5060ti-16k-20261029/BH2_02033__Qwen35-9B__a1.json`|`a3df27361e84eec7b3ceb7c54c29faaa`|
|`results/runs/screening-5060ti/qwen35-5060ti-16k-20261029/BH2_03434__Qwen35-9B__a1.json`|`bb52963ca8a662fc52f6e3a94cea36a7`|
|`results/runs/screening-5060ti/qwen35-5060ti-16k-20261029/BH2_03619__Qwen35-9B__a1.json`|`ab12a362d188e1edb2bad94db3cd144c`|
|`results/runs/screening-5060ti/qwen35-5060ti-16k-20261029/BH2_03750__Qwen35-9B__a1.json`|`ce1b6df666a6280b049cddbb5ef9a456`|
|`results/runs/screening-5060ti/qwen35-5060ti-16k-20261029/BH2_03760__Qwen35-9B__a1.json`|`f31ca3074644af52980764e0bead0d1d`|
|`results/runs/screening-5060ti/qwen35-5060ti-16k-20261029/BH2_03762__Qwen35-9B__a1.json`|`78ebcb9b66a5fac27e8a09f1df801f60`|
|`results/runs/screening-5060ti/qwen35-5060ti-16k-20261029/BH2_03850__Qwen35-9B__a1.json`|`bd1f82177947b3d644ce739db268d586`|
|`results/runs/screening-5060ti/qwen35-5060ti-16k-20261029/BH2_03856__Qwen35-9B__a1.json`|`b56122c093524b959eb60057c541afc2`|
|`results/runs/screening-5060ti/qwen35-5060ti-16k-20261029/BH2_03879__Qwen35-9B__a1.json`|`77d61eb4c4e268cd8040504651e261ab`|
|`results/runs/screening-5060ti/qwen35-5060ti-16k-20261029/BH2_03881__Qwen35-9B__a1.json`|`bff85d6430670c8f1de7a83613363ad8`|
|`results/runs/screening-5060ti/qwen35-5060ti-16k-20261029/BH2_03953__Qwen35-9B__a1.json`|`b17668a7129aeecc3cb51263176a0595`|
|`results/runs/screening-5060ti/qwen35-5060ti-16k-20261029/BH2_03991__Qwen35-9B__a1.json`|`8f3d69c65dac2307ab0c1e6d241c4555`|
|`results/runs/screening-5060ti/qwen35-5060ti-16k-20261029/BH2_04003__Qwen35-9B__a1.json`|`656cc3e639b56302acd55079bb102ba8`|
|`results/runs/screening-5060ti/qwen35-5060ti-16k-20261029/BH2_04007__Qwen35-9B__a1.json`|`072be525ce46205f582156ecc79b49a6`|
|`results/runs/screening-5060ti/qwen35-5060ti-16k-20261029/BH2_04425__Qwen35-9B__a1.json`|`8361d402fe35ac6adee506139d09ec57`|
|`results/runs/screening-5060ti/qwen35-5060ti-16k-20261029/BH2_05366__Qwen35-9B__a1.json`|`4fc0787a4d9c5c66c4c3c941d90450e0`|
|`results/runs/screening-5060ti/qwen35-5060ti-16k-20261029/BH2_05686__Qwen35-9B__a1.json`|`d5d1628a20da8b41b6fb064a26453c64`|
|`results/runs/screening-5060ti/qwen35-5060ti-16k-20261029/BH2_05843__Qwen35-9B__a1.json`|`3a7e57354474677cf363770533ccfa4d`|
|`results/runs/screening-5060ti/qwen35-5060ti-16k-20261029/BH2_06427__Qwen35-9B__a1.json`|`6f6ce5e2f109c0f7600ef4af78c8b752`|
|`results/runs/screening-5060ti/qwen35-5060ti-16k-20261029/Qwen35-9B.config.json`|`4a92d65200cb569920de248033422364`|
