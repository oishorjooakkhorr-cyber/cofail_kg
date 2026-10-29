## Qwen35-9B 32K reassessment completed — 2026-10-29

Fresh same-host32K block: **D3 FAIL,13/20 SUCCESS,12/20 competent**, seven
retained PARSE_FAIL;294/294 calls,median28.6345515s,zero OOM/errors/timeouts.
Full GPU,actual32768,f16 and backend Flash Attention enabled verified in42 samples.
Supported IDs unchanged from same-host16K;03619,03881,04003 lose valid no_answer
parsing without competence change. Output-cap/final-turn failures persist;
03879/04003 also show32K boundary pressure. Configuration-string Flash Attention
difference disclosed; no strict context-only causal claim. Post-result reassessment,
historical acceptance preserved; no other model or S21 selected.
[Separate report](S20_qwen35_5060ti_32k.md). Offline reporting and all1527 historical,
21 new and51 source/input hash checks pass. Publication/Drive proof recorded below.

# Granite41 RTX 5060 Ti S20 completed - 2026-10-29

D3 PASS:20/20 SUCCESS,16/20 competent,236/236 well-formed calls,
median38.870718s,zero errors/timeouts/OOM. Full GPU,f16,actual16K verified.
Historical stopped16K remains incomplete and untouched. Offline/hash checks pass.
Report: S20_granite41_5060ti_16k.md.
Results pushed as7826348; Drive verified65/65 checksum matches,zero differences.
Broader backup retains nine unrelated historical archive errors. No further
inference or S21.

# Tested Gemma launcher update — 2026-10-29

The Gemma-specific launcher is now tested and its authorized fresh block is
complete: **D3 PASS, 19 SUCCESS / 14 competent**. See
[S20 Gemma on RTX 5060 Ti](S20_gemma4_5060ti_16k.md). The older setup proposal
below is retained as history; its runtime and host assumptions are superseded
for this run by the explicit researcher authorization in decision_log.md.

Actual project `D:\cofailKG`; Python `D:\cofailKG\.venv\Scripts\python.exe`;
installed user-PATH Ollama client/server 0.40.12 (historical 0.40.4 unchanged),
model store `D:\Models`. Host Ryzen 7 7700, about 31 GiB usable RAM,
RTX 5060 Ti 16311 MiB, driver 610.88. The tool shell may omit user PATH;
resolve the installed host user PATH rather than replacing/upgrading Ollama.
Full model digest remains the Gemma digest in section 4 below.

Launcher:
`results/diagnostics/s20/gemma4-5060ti-16k-20261028/run_model.py`.
It reuses unchanged runner/evaluators with isolated records and preserves all
final statuses on resume. Inference is complete: use only offline reporting
for this run, without an Ollama server:

```powershell
& D:\cofailKG\.venv\Scripts\python.exe D:\cofailKG\results\diagnostics\s20\gemma4-5060ti-16k-20261028\run_model.py --report-only
```

Before any separately authorized future run, create its own run ID/manifests;
do not edit/reuse this completed run to retry failures. Require f16 K/V runtime
evidence, actual context 16384, /api/ps size_vram=size and all-layer GPU logs.
Gemma was verified 43/43 layers with 41 runtime samples; small API byte accounting
does not measure total VRAM. Results establish this host/runtime condition and
do not attribute differences solely to hardware. No further model or S21
action is authorized by this completed task.

# S20 on the RTX 5060 Ti host — run guide (draft, 2026-10-21)

Status: setup/run plan, not an executable launcher. Publishing this guide does not authorize
new inference. Record the new-host decision in `decision_log.md` and build/test the launcher
before starting the four blocks.

Goal: fresh, complete 20-query S20 blocks for **Qwen35-9B, Gemma4-E4B, Ministral3-8B and Granite41-8B**
at `num_ctx=16384`, on one machine, with each model fully on the GPU. All other scientific
settings unchanged (temperature 0, seed 42, `num_predict` 4096, budget 30, page size 50,
120 s request timeout, 600 s episode timeout, `think=false`, f16 KV cache, unchanged D3 thresholds).
All 3060 Ti results stay as history; nothing is mixed across hosts.

## 0. Before the day (researcher)

1. Add a `decision_log.md` entry (draft below) before any inference on the new host.
2. Card confirmed by the researcher: RTX 5060 Ti **16 GB VRAM** (2026-10-21).
3. Have the new-host launcher ready (needs to be built; see section 6).

## 1. Restore the project and its records

The destination drive and project location are **not decided yet**. Choose them on the
new computer, clone the repository there, then initialize this variable in **each
PowerShell terminal** before using the commands below:

```powershell
$projectRoot = Read-Host 'Full path of the cloned cofail_kg folder on your chosen drive'
$projectRoot = (Resolve-Path -LiteralPath $projectRoot -ErrorAction Stop).Path
if (!(Test-Path -LiteralPath (Join-Path $projectRoot 'pyproject.toml'))) {
    throw 'Select the cloned cofail_kg project folder.'
}
Set-Location -LiteralPath $projectRoot
```

All destination paths below are relative to this chosen project root. Source-computer
paths mentioned for copying files do not prescribe the new computer's drive or location.

| What | How |
|---|---|
| Code | Clone `https://github.com/oishorjooakkhorr-cyber/cofail_kg.git`, including this guide. Record the actual `git rev-parse HEAD`; `9b3956d` is the earlier screening checkpoint. |
| Location | Choose the destination drive/folder and set `$projectRoot` above. Matching this computer's path is not required. Use fresh destination paths in the new-host manifests; never rewrite historical configs. |
| Previous records and inputs | Restore `results/`, `data/processed/` and `data/agent_inputs/` using the [Drive restore instructions](google_drive_backup.md#other-developers-using-the-same-backup-folder). Clone alone does not restore ignored `results/runs/` records. |
| PrimeKG cache | Transfer the two Parquet files below separately, along with their original cache metadata. |
| Python and Ollama | Follow sections 2 and 3; keep project packages, caches and runtime files under the chosen project folder. |
| Models | Pull the exact tags in section 4 and verify their full digests. Copy existing models only if a matching download is unavailable. |

### Why the cache files are excluded from Drive

The existing backup script scans `results/`, processed data and agent inputs, but allows only
`primekg_metadata.json` and `primekg_release.json` from `data/cache/`. This is the existing
cache-backup policy, not a restriction on these particular files. The required Parquet pair
is only **17,291,080 bytes (about 17.3 MB)** on the source computer. This guide does not change
the backup policy.

Copy these exact files from this computer's `data/cache/` into the same relative directory
on the new computer. Use USB, a shared folder or a separate transfer; they are not in the
standard Drive backup. Verify the full SHA-256 values after transfer:

| File | SHA-256 |
|---|---|
| `primekg_nodes.parquet` | `ec43d05e4dd0570d73772a0289166360d90f3e1c79225f4ec840a5fd644dbb17` |
| `primekg_edges.parquet` | `129f2d881e7aa9a678341e3920e2bba0f2081c5fada1951a545e004fcb25289e` |

```powershell
Set-Location -LiteralPath $projectRoot
Get-FileHash -Algorithm SHA256 -LiteralPath .\data\cache\primekg_nodes.parquet, .\data\cache\primekg_edges.parquet | Format-List Path, Hash
```

Any hash mismatch: stop and obtain the original bytes. Keep the restored inputs, relation
mapping, frozen hashes and all historical records intact.

## 2. Install Python dependencies inside the chosen project folder

On the new Windows computer, install the **64-bit Python 3.13.9** release using its
[official installer](https://www.python.org/downloads/release/python-3139/). Choose
**Customize installation**, retain pip/venv support, and choose the interpreter location
on the selected drive instead of accepting an unrelated default location. Note the full
path to its `python.exe` for the prompt below. Use the regular CPython build,
not the experimental free-threaded build. Do not copy this computer's Python `.venv`;
recreate it on the destination.

Run the following in PowerShell from the new clone. This creates the virtual environment,
pip cache and temporary setup files **under the chosen project folder**. Explicit interpreter
paths avoid installing into another Python installation. The pip configuration reset prevents
an existing user configuration from redirecting installations to another directory.

```powershell
$ErrorActionPreference = 'Stop'
Set-Location -LiteralPath $projectRoot
$basePython = Read-Host 'Full path to your Python 3.13.9 python.exe on the selected drive'
& $basePython -c "import sys; assert sys.version_info[:3] == (3, 13, 9), sys.version"
if ($LASTEXITCODE -ne 0) { throw 'Python 3.13.9 is required.' }

New-Item -ItemType Directory -Force -Path .\.venv\setup-tmp, .\.venv\pip-cache | Out-Null
$env:TEMP = Join-Path $projectRoot '.venv\setup-tmp'
$env:TMP = $env:TEMP
$env:PIP_CACHE_DIR = Join-Path $projectRoot '.venv\pip-cache'
$env:PIP_CONFIG_FILE = 'NUL'
$env:PYTHONNOUSERSITE = '1'
Remove-Item Env:PIP_TARGET, Env:PIP_PREFIX, Env:PYTHONPATH -ErrorAction SilentlyContinue

& $basePython -m venv .venv
if ($LASTEXITCODE -ne 0) { throw 'Virtual environment creation failed.' }
$env:PIP_REQUIRE_VIRTUALENV = 'true'
& .\.venv\Scripts\python.exe -m pip install --no-user -r .\requirements.lock
if ($LASTEXITCODE -ne 0) { throw 'Pinned dependency installation failed; do not unpin versions.' }
& .\.venv\Scripts\python.exe -m pip install --no-user --no-deps -e .
if ($LASTEXITCODE -ne 0) { throw 'Project installation failed.' }
& .\.venv\Scripts\python.exe -m pip check
if ($LASTEXITCODE -ne 0) { throw 'Dependency compatibility check failed.' }
```

Verify the interpreter, import location and dependency directory before testing:

```powershell
Set-Location -LiteralPath $projectRoot
& .\.venv\Scripts\python.exe -c "import pathlib, sys, sysconfig, cofail_kg; root=pathlib.Path.cwd().resolve(); env=(root/'.venv').resolve(); packages=pathlib.Path(sysconfig.get_path('purelib')).resolve(); assert sys.version_info[:3] == (3,13,9); assert pathlib.Path(sys.prefix).resolve() == env; assert packages == env/'Lib'/'site-packages'; assert pathlib.Path(cofail_kg.__file__).resolve().is_relative_to(root/'src'); print(sys.executable); print(packages)"
if ($LASTEXITCODE -ne 0) { throw 'Python or dependency installation is outside the expected project environment.' }
& .\.venv\Scripts\python.exe -m pytest -q --basetemp .\.venv\pytest-5060ti
if ($LASTEXITCODE -ne 0) { throw 'Tests failed; do not start screening.' }
```

Expected package directory: `<projectRoot>\.venv\Lib\site-packages` on the chosen drive.
Do not use a bare `pip install`, `--user`, or `--system-site-packages`. In a new terminal,
repeat the session's cache/temp environment settings before installing anything else.

## 3. Set up the same Ollama runtime locally

Transfer the existing **Ollama 0.40.4** runtime from this computer. Copy `ollama.exe` and the
**entire `lib/` tree** from this source computer's
`E:\Phitron Thesis\cofail_kg\.venv\ollama\` into `<projectRoot>\.venv\ollama\` on the
destination, preserving the directory layout. Runtime libraries are
required; copying only `ollama.exe` is insufficient. Copy this runtime after creating the
new Python virtual environment; do not replace it with the source Python environment.

No upload of the model weights is required for this step. Do not substitute an unpinned
Ollama installer or allow an automatic upgrade. If 0.40.4 cannot use the new GPU, stop and
record the incompatibility; a runtime change needs a separately recorded decision.

Quit any pre-existing Ollama desktop app/server first. In a dedicated PowerShell terminal:

```powershell
Set-Location -LiteralPath $projectRoot
if (Get-NetTCPConnection -LocalPort 11434 -State Listen -ErrorAction SilentlyContinue) {
    throw 'Port 11434 is occupied; identify and stop the existing Ollama server first.'
}
$env:OLLAMA_MODELS = Join-Path (Get-Location).Path '.venv\ollama-models'
New-Item -ItemType Directory -Force -Path $env:OLLAMA_MODELS | Out-Null
Remove-Item Env:OLLAMA_KV_CACHE_TYPE, Env:OLLAMA_FLASH_ATTENTION -ErrorAction SilentlyContinue
& .\.venv\ollama\ollama.exe serve
```

Leave that terminal open. The server's `OLLAMA_MODELS` setting puts downloaded weights in
`<projectRoot>\.venv\ollama-models` on the chosen drive, rather than a user-profile default.
Unsetting the two cache/attention overrides preserves the source runtime defaults; confirm
f16 KV cache from the runtime evidence during preflight.

In a second terminal, verify the running server, then use this terminal for section 4:

```powershell
Set-Location -LiteralPath $projectRoot
$runtime = Invoke-RestMethod -Uri 'http://127.0.0.1:11434/api/version'
if ($runtime.version -ne '0.40.4') { throw 'Unexpected Ollama server version.' }
$runtime | ConvertTo-Json
```

## 4. Download models and check their identities

Downloading from Ollama's registry is acceptable **only when the installed full digest
matches the recorded identity**. A tag can change; the same tag or model size alone is
insufficient. Pulling downloads weights to the new computer; inference uses its local GPU.

```powershell
Set-Location -LiteralPath $projectRoot
foreach ($tag in @('qwen3.5:9b', 'gemma4:e4b-it-q4_K_M', 'ministral-3:8b', 'ibm/granite4.1:8b')) {
    & .\.venv\ollama\ollama.exe pull $tag
    if ($LASTEXITCODE -ne 0) { throw "Model download failed: $tag" }
}
```

The required full digests are:

| Agent | Tag | Digest |
|---|---|---|
| Qwen35-9B | `qwen3.5:9b` | `56671c2ab9385f9cfcb404638e32cd62d88e3501d44822208363c010179a3c90` |
| Gemma4-E4B | `gemma4:e4b-it-q4_K_M` | `dc35e8d9c6061baa6f0fa870975ab6932e2542b579b13ea0f199fa4bb7300c9c` |
| Ministral3-8B | `ministral-3:8b` | `1922accd5827ebe6829e536369195db25eaf664528dc66206d646ea3bb386b71` |
| Granite41-8B | `ibm/granite4.1:8b` | `444af1c4b2fedd6b54041aca558e7300b0b3d5c0468c44619126240323ba2852` |

Check full digests using the API; `ollama list` displays shortened IDs:

```powershell
$expected = @{
    'qwen3.5:9b' = '56671c2ab9385f9cfcb404638e32cd62d88e3501d44822208363c010179a3c90'
    'gemma4:e4b-it-q4_K_M' = 'dc35e8d9c6061baa6f0fa870975ab6932e2542b579b13ea0f199fa4bb7300c9c'
    'ministral-3:8b' = '1922accd5827ebe6829e536369195db25eaf664528dc66206d646ea3bb386b71'
    'ibm/granite4.1:8b' = '444af1c4b2fedd6b54041aca558e7300b0b3d5c0468c44619126240323ba2852'
}
$models = (Invoke-RestMethod -Uri 'http://127.0.0.1:11434/api/tags').models
foreach ($tag in $expected.Keys) {
    $model = @($models | Where-Object { $_.name -eq $tag })
    if ($model.Count -ne 1 -or $model[0].digest -ne $expected[$tag]) {
        throw "Installed model identity mismatch: $tag"
    }
    if ($model[0].details.quantization_level -ne 'Q4_K_M') {
        throw "Unexpected quantization: $tag"
    }
}
$models | Where-Object { $expected.ContainsKey($_.name) } | Select-Object name, digest, details | ConvertTo-Json -Depth 4
```

On any mismatch, stop before synthetic or official inference. Qwen's public page has
multiple backend variants; its llama.cpp identity must match the recorded digest.
If the registry no longer supplies the required version, transfer the existing model store
from this computer's `D:\Models` instead. Preserve both `manifests/` and `blobs/`, place them
under the destination's configured `OLLAMA_MODELS` directory while its server is stopped,
restart, and repeat the full digest checks. Keep the source copies until verification passes.

## 5. Record and verify the host

Save GPU name and VRAM, NVIDIA driver version, CPU, system RAM, Windows version and Ollama
version (`nvidia-smi`, `/api/version`) into the run's diagnostics folder before inference.
Also record Python/package versions, the Git commit, runtime environment overrides and
the four installed model identities. The proposed host has 16 GB system RAM; check available
RAM as well as VRAM during preflight rather than assuming either capacity is sufficient.

Ollama's current [GPU support documentation](https://docs.ollama.com/gpu) lists RTX 5060 Ti,
but that is not proof that this particular 0.40.4 runtime/driver combination works on the
destination. Verify it there. **16 GB VRAM does not guarantee full GPU residency at 16K,
faster completion within the existing timeouts, or a D3 pass.**

## 6. Build/test the new-host launcher before inference

The existing 16K launchers (`results/diagnostics/s20/*/run_model.py`) and saved manifests
refer to the 3060 Ti runs. Do not execute them unchanged on the new computer or resume the
stopped Granite block as if it were a new-host run.

The new-host launcher still needs to be built and tested. It must reuse the unchanged agent
runner/evaluators while creating fresh per-model manifests with new run IDs/output roots,
destination paths, current Git provenance, model/source/input pins and recorded host details.
It must locate restored historical records under the chosen project root without requiring
the source computer's drive paths to exist or modifying those historical manifests.
Keep the twenty frozen queries in their original order and preserve every final status.
Tests must cover identity/hash mismatch refusal, isolation from old records, all-status
write-once resume and offline reporting. The current user request updates/publishes this
guide; it does not implement the launcher or start inference.

## 7. Per model: preflight, then the 20 queries

One model at a time, in a fixed order (proposed: Qwen, Gemma, Ministral, Granite):

1. Pass the project suite and the new launcher tests using the project `.venv` interpreter.
2. Preflight: synthetic native tool call with `think=false`, and a load at `num_ctx=16384`.
   Check the matching model/digest in `/api/ps`: **`size_vram` must equal `size`** (100% on GPU)
   and `context_length` must be 16384. Retain runtime/GPU evidence, including f16 KV cache,
   and collect placement samples during the block. Unload the preceding model between blocks.
3. Run all 20 queries in one invocation under a new run ID, e.g. `context16k-5060ti-<date>`,
   in its own runs root. Keep every final status; no retries, no stitching.
4. Report-only pass, integrity hashes, D3 row.

If the preflight cannot satisfy the recorded runtime/context/GPU conditions, stop before
the official block and document the failure. Do not silently change versions, cache
precision, context, timeouts or prompts to make it pass. Retain all subsequent saved query
failures in the full-block denominator. Compare the fresh host-specific results with the
old results without mixing records across hosts.

## 8. Draft decision-log entry (researcher to approve/edit)

> ## 2026-10-2x — S20 — Full 16K re-screening on RTX 5060 Ti host
> Decision: Run fresh complete 20-query S20 blocks for Qwen35-9B, Gemma4-E4B, Ministral3-8B
> and Granite41-8B on a second host (RTX 5060 Ti 16 GB, i9 14th gen, 16 GB RAM) at num_ctx=16384,
> with all other section 9.1 settings, the frozen prompt/tools/manifests, exact pinned model
> digests, Ollama 0.40.4 and unchanged D3 thresholds. All four candidates run on the same host.
> Why: On the 8 GB RTX 3060 Ti, Ministral and Granite 4.1 offloaded layers to the CPU at 16K and
> hit 120 s request timeouts. Test whether the new host can achieve full GPU residency
> for all four at 16K; this must be verified rather than assumed to resolve the timeouts.
> Data seen before deciding: all 3060 Ti S20 outcomes (8K and 16K), including D3 verdicts, the
> stopped Granite 4.1 16K block, and exploratory Ministral KV-cache diagnostics
> (results/diagnostics/ministral_speed/, not official).
> Changes to protocol or decision rules: execution host changes (not a frozen protocol item);
> context per the existing scoped 16K amendment. 3060 Ti results retained unchanged as history;
> no results are combined across hosts. No S21 selection implied.

## References and verification limits

- [Python virtual environments](https://docs.python.org/3.13/library/venv.html): recreate the
  environment on the destination and install packages into its own `site-packages`.
- [pip configuration](https://pip.pypa.io/en/stable/topics/configuration/) and
  [pip cache settings](https://pip.pypa.io/en/stable/cli/pip/#cmdoption-cache-dir): explicit
  environment/configuration settings keep this setup's package/cache paths under the chosen
  project folder.
- [Ollama model metadata](https://docs.ollama.com/api/tags) and
  [model storage location](https://docs.ollama.com/faq#where-are-models-stored): verify full
  digests and set `OLLAMA_MODELS` in the server's environment.

Source computer verified on 2026-10-21: Python 3.13.9, Ollama 0.40.4, all four recorded
model digests, and the two cache hashes above. Destination installation, GPU placement
and new-host inference remain untested until the corresponding steps are completed there.
Local guide checks: all eight PowerShell blocks parse; the model guard accepts matching
fixtures and rejects missing models, changed digests and changed quantization. The current
project passes the interpreter/site-packages location check and `pip check`. No dependency
reinstallation, model download or new inference was performed to validate this document.


## Qwen RTX 5060 Ti S20 completed — 2026-10-29
Fresh16K D3 FAIL:16/20 SUCCESS,12 competent,259/259 well-formed calls,
median30.627939s,zero OOM. Four retained PARSE_FAIL. Full GPU/f16/actual16K
verified; historical8K and16K PASS preserved. See docs/S20_qwen35_5060ti_16k.md.
No retries,additional condition,other model or S21.
