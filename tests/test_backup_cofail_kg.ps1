param([Parameter(Mandatory=$true)][string]$RclonePath)
$ErrorActionPreference = 'Stop'
$testRoot = Join-Path $env:TEMP ('cofail-backup-test-' + [guid]::NewGuid())
$script = Join-Path $PSScriptRoot '../scripts/backup_cofail_kg.ps1'
$originalConfig = $env:RCLONE_CONFIG
function Assert($condition, $message) { if (!$condition) { throw $message } }
function Run-Backup([string[]]$extra = @()) {
    & powershell.exe -NoProfile -ExecutionPolicy Bypass -File $script -RepositoryRoot "$testRoot/repo" -StateDirectory "$testRoot/state" -RclonePath $RclonePath -Destination "test:$testRoot/remote" @extra
    Assert ($LASTEXITCODE -eq 0) 'Backup failed'
}
try {
    foreach ($name in @('backup_cofail_kg.ps1','enable_cofail_kg_backup.ps1')) {
        $tokens = $null; $parseErrors = $null
        $ast = [Management.Automation.Language.Parser]::ParseFile((Join-Path $PSScriptRoot "../scripts/$name"), [ref]$tokens, [ref]$parseErrors)
        Assert (!$parseErrors) "Script parse failed: $name"
        $destination = $ast.ParamBlock.Parameters | Where-Object { $_.Name.VariablePath.UserPath -eq 'Destination' }
        Assert ($destination.DefaultValue.SafeGetValue() -eq 'cofail_gdrive,root_folder_id=1lA-lOinAY1Z8m9fpvQD2QQyxgonMGxbk:') "Default must target the verified shared folder ID: $name"
    }
    New-Item -ItemType Directory -Path "$testRoot/repo/results/runs", "$testRoot/repo/data/raw", "$testRoot/repo/data/cache" -Force | Out-Null
    & git.exe -C "$testRoot/repo" init -q
    Assert ($LASTEXITCODE -eq 0) 'Test Git initialization failed'
    $env:RCLONE_CONFIG = "$testRoot/rclone.conf"
    Set-Content $env:RCLONE_CONFIG "[test]`ntype = local"
    Set-Content "$testRoot/repo/results/runs/output.json" 'first'
    Set-Content "$testRoot/repo/results/runs/recent.json" 'active'
    Set-Content "$testRoot/repo/results/runs/locked.json" 'writing'
    Set-Content "$testRoot/repo/results/runs/credentials.json" 'secret'
    Set-Content "$testRoot/repo/data/raw/dataset.csv" 'raw'
    Set-Content "$testRoot/repo/data/cache/primekg_nodes.parquet" 'cache'
    Get-ChildItem "$testRoot/repo" -Recurse -File | ForEach-Object { $_.LastWriteTimeUtc = [datetime]::UtcNow.AddHours(-1) }
    (Get-Item "$testRoot/repo/results/runs/recent.json").LastWriteTimeUtc = [datetime]::UtcNow
    $writer = [IO.File]::Open("$testRoot/repo/results/runs/locked.json", 'Open', 'Write', 'Read')
    Run-Backup @('-DryRun')
    Assert (!(Test-Path "$testRoot/remote/current/results/runs/output.json")) 'Dry run uploaded'
    Run-Backup
    Assert ((Get-Content "$testRoot/remote/current/results/runs/output.json") -eq 'first') 'Missing first backup'
    foreach ($name in @('recent.json', 'locked.json', 'credentials.json')) {
        Assert (!(Test-Path "$testRoot/remote/current/results/runs/$name")) "Uploaded excluded file $name"
    }
    Assert (!(Test-Path "$testRoot/remote/current/data/raw")) 'Uploaded raw data'
    Assert (!(Test-Path "$testRoot/remote/current/data/cache/primekg_nodes.parquet")) 'Uploaded cache table'
    Run-Backup
    Assert (@(Get-ChildItem "$testRoot/remote/history" -Recurse -File -ErrorAction SilentlyContinue).Count -eq 0) 'Unchanged file was versioned'
    Set-Content "$testRoot/repo/results/runs/output.json" 'other'
    (Get-Item "$testRoot/repo/results/runs/output.json").LastWriteTimeUtc = [datetime]::UtcNow.AddHours(-1)
    Run-Backup
    Assert ((Get-Content "$testRoot/remote/current/results/runs/output.json") -eq 'other') 'Changed file missing'
    $old = @(Get-ChildItem "$testRoot/remote/history" -Recurse -Filter output.json)
    Assert ($old.Count -eq 1 -and (Get-Content $old[0].FullName) -eq 'first') 'Old version lost'
    Run-Backup @('-VerifyOnly')
    Set-Content "$testRoot/remote/current/results/runs/output.json" 'corrupt'
    & powershell.exe -NoProfile -ExecutionPolicy Bypass -File $script -RepositoryRoot "$testRoot/repo" -StateDirectory "$testRoot/state" -RclonePath $RclonePath -Destination "test:$testRoot/remote" -VerifyOnly
    Assert ($LASTEXITCODE -ne 0) 'Verification missed corruption'
    Run-Backup
    Remove-Item -LiteralPath "$testRoot/repo/results/runs/output.json"
    Run-Backup
    Assert (Test-Path "$testRoot/remote/current/results/runs/output.json") 'Local deletion removed backup'
    $writer.Dispose()
    $writer = $null
    (Get-Item "$testRoot/repo/results/runs/recent.json").LastWriteTimeUtc = [datetime]::UtcNow.AddHours(-1)
    # A failed remote connection must be reported, then a later run must catch up.
    Set-Content $env:RCLONE_CONFIG '[unavailable]'
    & powershell.exe -NoProfile -ExecutionPolicy Bypass -File $script -RepositoryRoot "$testRoot/repo" -StateDirectory "$testRoot/state" -RclonePath $RclonePath -Destination "test:$testRoot/remote"
    Assert ($LASTEXITCODE -ne 0) 'Unavailable remote reported success'
    Set-Content $env:RCLONE_CONFIG "[test]`ntype = local"
    Run-Backup
    Assert (Test-Path "$testRoot/remote/current/results/runs/locked.json") 'Deferred writer did not catch up'
    Assert (Test-Path "$testRoot/remote/current/results/runs/recent.json") 'Deferred recent file did not catch up'
    Assert (@(Get-ChildItem "$testRoot/state" -Directory -Filter 'stage-*').Count -eq 0) 'Snapshots leaked after runs'
    Set-Content "$testRoot/repo/results/tracked.json" 'managed-by-git'
    & git.exe -C "$testRoot/repo" add results/tracked.json
    Set-Content "$testRoot/remote/current/results/tracked.json" 'stale-drive-copy'
    Set-Content "$testRoot/remote/current/results/runs/recent.json" 'cloud-update'
    Run-Backup @('-Pull', '-DryRun')
    Assert ((Get-Content "$testRoot/repo/results/runs/recent.json") -eq 'active') 'Pull dry run modified local output'
    Run-Backup @('-Pull')
    Assert ((Get-Content "$testRoot/repo/results/runs/recent.json") -eq 'cloud-update') 'Pull failed to update an existing file'
    Assert ((Get-Content "$testRoot/repo/results/tracked.json") -eq 'managed-by-git') 'Drive overwrote a Git-tracked file'
    $previous = @(Get-ChildItem "$testRoot/repo/.cofail-backup-history" -Recurse -Filter recent.json)
    Assert ($previous.Count -eq 1 -and (Get-Content $previous[0].FullName) -eq 'active') 'Pull lost the previous local version'
    Assert (Test-Path "$testRoot/repo/results/runs/output.json") 'Pull did not restore missing output'
    Set-Content "$testRoot/remote/current/results/runs/recent.json" 'next-cloud-update'
    $writer = [IO.File]::Open("$testRoot/repo/results/runs/recent.json", 'Open', 'Write', 'Read')
    & powershell.exe -NoProfile -ExecutionPolicy Bypass -File $script -RepositoryRoot "$testRoot/repo" -StateDirectory "$testRoot/state" -RclonePath $RclonePath -Destination "test:$testRoot/remote" -Pull
    Assert ($LASTEXITCODE -ne 0) 'Pull ignored a busy local writer'
    Assert ((Get-Content "$testRoot/repo/results/runs/recent.json") -eq 'cloud-update') 'Pull overwrote a busy local file'
    $writer.Dispose(); $writer = $null
    Run-Backup @('-Pull')
    Assert ((Get-Content "$testRoot/repo/results/runs/recent.json") -eq 'next-cloud-update') 'Pull did not catch up after writer closed'
    Write-Output 'PASS: incremental upload, remote history, verification, no deletion, download updates, local history, tracked-file protection, busy writers'
} finally {
    if ($writer) { $writer.Dispose() }
    $env:RCLONE_CONFIG = $originalConfig
    # Keep the small isolated fixture and logs for inspection; never touch real outputs.
    Write-Output "Test evidence: $testRoot"
}
