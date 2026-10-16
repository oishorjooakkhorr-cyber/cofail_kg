# Windows PowerShell 5.1; invoked by the Git wrapper or explicitly for manual use.
[CmdletBinding()]
param(
    [string]$RepositoryRoot = (Split-Path $PSScriptRoot -Parent),
    [ValidatePattern('^[A-Za-z0-9_-]+:.+')][string]$Destination = 'cofail_gdrive:CoFail-KG-Backups',
    [string]$RclonePath = 'rclone',
    [string]$StateDirectory = (Join-Path $env:LOCALAPPDATA 'CoFail-KG-Backup'),
    [ValidateRange(1,1440)][int]$MinimumAgeMinutes = 10,
    [switch]$DryRun,
    [switch]$VerifyOnly,
    [switch]$Pull
)
$ErrorActionPreference = 'Stop'
if ($DryRun -and $VerifyOnly) { throw 'Use either -DryRun or -VerifyOnly.' }
if ($Pull -and $VerifyOnly) { throw 'Use -Pull or -VerifyOnly.' }
$root = (Resolve-Path -LiteralPath $RepositoryRoot).Path.TrimEnd('\', '/')
if (!(Test-Path -LiteralPath (Join-Path $root 'results') -PathType Container)) { throw 'RepositoryRoot must contain results/.' }
$rclone = (Get-Command $RclonePath -CommandType Application -ErrorAction Stop | Select-Object -First 1).Source
$state = [IO.Path]::GetFullPath($StateDirectory)
New-Item -ItemType Directory -Path $state -Force | Out-Null
try {
    $lock = [IO.File]::Open((Join-Path $state 'backup.lock'), 'OpenOrCreate', 'ReadWrite', 'None')
} catch [IO.IOException] {
    Write-Output 'Another backup is running; skipping this invocation.'
    exit 0
}
$id = [datetime]::UtcNow.ToString('yyyyMMddTHHmmssfffZ') + '-' + [guid]::NewGuid().ToString('N')
$stage = Join-Path $state "stage-$id"
$log = Join-Path $state "$id.log"
function Log([string]$message) {
    $line = "$( [datetime]::UtcNow.ToString('o') ) $message"
    Add-Content -LiteralPath $log -Value $line -Encoding UTF8
    Write-Output $line
}
function Snapshot-Directory([string]$directory) {
    foreach ($entry in Get-ChildItem -LiteralPath $directory -Force) {
        # Never follow junctions/symlinks outside the selected output directories.
        if ($entry.Attributes -band [IO.FileAttributes]::ReparsePoint) { continue }
        if ($entry.Name -match '(?i)^(\.git|\.aws|\.ssh|\.venv|__pycache__|models?|datasets?|raw|secrets?|credentials?)(\.|$)' -or
            $entry.Name -match '(?i)(^\.env($|\.)|rclone\.conf$|token|api[_-]?key|private[_-]?key)' ) { continue }
        if ($entry.PSIsContainer) { Snapshot-Directory $entry.FullName; continue }
        if ($entry.Extension -notin @('.csv','.tsv','.json','.jsonl','.txt','.log','.md','.yaml','.yml','.parquet','.arrow','.feather','.npy','.npz','.html','.pdf','.png','.jpg','.svg')) { continue }
        Snapshot-File $entry
    }
}
function Snapshot-File($entry) {
    if ($Pull) { Install-DownloadedFile $entry; return }
    # shortcut: age cannot prove logical completion, use completion markers if writers develop long idle gaps.
    if ($entry.Attributes -band [IO.FileAttributes]::ReparsePoint) { return }
    if ($entry.LastWriteTimeUtc -gt [datetime]::UtcNow.AddMinutes(-$MinimumAgeMinutes)) {
        Log "Deferred (recent): $($entry.FullName)"; return
    }
    $relative = $entry.FullName.Substring($root.Length + 1)
    $target = Join-Path $stage $relative
    $inputStream = $null
    $outputStream = $null
    try {
        # Denies writers and deletion during snapshot; an existing writer makes Open fail.
        $inputStream = [IO.File]::Open($entry.FullName, 'Open', 'Read', 'Read')
    } catch [IO.IOException] {
        Log "Deferred (busy/disappeared): $relative"; return
    }
    try {
        $modified = [IO.File]::GetLastWriteTimeUtc($entry.FullName)
        if ($modified -gt [datetime]::UtcNow.AddMinutes(-$MinimumAgeMinutes)) { return }
        New-Item -ItemType Directory -Path (Split-Path $target -Parent) -Force | Out-Null
        $outputStream = [IO.File]::Create($target)
        $inputStream.CopyTo($outputStream)
    } finally {
        if ($outputStream) { $outputStream.Dispose() }
        $inputStream.Dispose()
    }
    [IO.File]::SetLastWriteTimeUtc($target, $modified)
    $script:count++
}
function Install-DownloadedFile($entry) {
    $relative = $entry.FullName.Substring($stage.Length + 1)
    if ($tracked -contains $relative.Replace('\','/')) { Log "Git manages this file; skipped Drive copy: $relative"; return }
    $target = Join-Path $root $relative
    $parent = $root
    foreach ($part in ($relative -split '[\\/]')) {
        $parent = Join-Path $parent $part
        if ((Test-Path -LiteralPath $parent) -and ((Get-Item -LiteralPath $parent -Force).Attributes -band [IO.FileAttributes]::ReparsePoint)) { throw "Refusing to write through a link: $parent" }
    }
    New-Item -ItemType Directory -Path (Split-Path $target -Parent) -Force | Out-Null
    $temporary = $target + '.cofail-download-' + $id
    $existing = $null
    try {
        if (Test-Path -LiteralPath $target) {
            # Deny existing/new writers, but permit the atomic replacement below.
            try { $existing = [IO.File]::Open($target, 'Open', 'Read', 'Read, Delete') }
            catch [IO.IOException] { Log "Deferred (local file busy): $relative"; $script:deferred++; return }
            $sha = [Security.Cryptography.SHA256]::Create()
            try { $localHash = [BitConverter]::ToString($sha.ComputeHash($existing)).Replace('-','') }
            finally { $sha.Dispose() }
            if ($localHash -eq (Get-FileHash -LiteralPath $entry.FullName -Algorithm SHA256).Hash) { return }
        }
        [IO.File]::Copy($entry.FullName, $temporary, $false)
        [IO.File]::SetLastWriteTimeUtc($temporary, $entry.LastWriteTimeUtc)
        if ($existing) {
            $historyRoot = Join-Path $root '.cofail-backup-history'
            if ((Test-Path -LiteralPath $historyRoot) -and ((Get-Item -LiteralPath $historyRoot -Force).Attributes -band [IO.FileAttributes]::ReparsePoint)) { throw 'Local history must not be a link.' }
            $previous = Join-Path $root ('.cofail-backup-history/' + $id + '/' + $relative)
            New-Item -ItemType Directory -Path (Split-Path $previous -Parent) -Force | Out-Null
            [IO.File]::Replace($temporary, $target, $previous)
            Log "Updated $relative; previous version: $previous"
        } else {
            [IO.File]::Move($temporary, $target)
            Log "Downloaded $relative"
        }
        $script:count++
    } finally {
        if ($existing) { $existing.Dispose() }
        if (Test-Path -LiteralPath $temporary) { Remove-Item -LiteralPath $temporary -Force }
    }
}
try {
    Log "Starting repository=$root destination=$Destination dryRun=$DryRun verifyOnly=$VerifyOnly pull=$Pull"
    New-Item -ItemType Directory -Path $stage | Out-Null
    $script:count = 0
    $script:deferred = 0
    $common = @('--log-file', $log, '--log-level', 'INFO', '--retries', '3', '--low-level-retries', '5', '--contimeout', '20s', '--timeout', '2m')
    $current = $Destination.TrimEnd('/') + '/current'
    $scanRoot = $root
    if ($Pull) {
        $filters = @('--filter', '+ /results/**', '--filter', '+ /data/processed/**', '--filter', '+ /data/agent_inputs/**', '--filter', '+ /data/cache/primekg_metadata.json', '--filter', '+ /data/cache/primekg_release.json', '--filter', '- **')
        $downloadArgs = @('copy', $current, $stage, '--checksum') + $filters + $common
        if ($DryRun) { $downloadArgs += '--dry-run' }
        & $rclone @downloadArgs
        if ($LASTEXITCODE -ne 0) { throw "Drive download failed with exit code $LASTEXITCODE" }
        if ($DryRun) { Log 'Pull dry run complete; local research files unchanged'; exit 0 }
        & $rclone check $current $stage --one-way @filters @common
        if ($LASTEXITCODE -ne 0) { throw "Download integrity check failed with exit code $LASTEXITCODE" }
        $scanRoot = $stage
        $tracked = @(& git.exe -C $root ls-files)
        if ($LASTEXITCODE -ne 0) { throw 'Pull requires a Git repository so tracked files stay managed by Git.' }
    }
    foreach ($relative in @('results', 'data/processed', 'data/agent_inputs')) {
        if ($relative.StartsWith('data/') -and ((Get-Item -LiteralPath (Join-Path $scanRoot 'data') -ErrorAction SilentlyContinue).Attributes -band [IO.FileAttributes]::ReparsePoint)) { continue }
        $folder = Join-Path $scanRoot $relative
        if (Test-Path -LiteralPath $folder) {
            $item = Get-Item -LiteralPath $folder
            if (!($item.Attributes -band [IO.FileAttributes]::ReparsePoint)) { Snapshot-Directory $folder }
        }
    }
    $cache = Join-Path $scanRoot 'data/cache'
    if ((Test-Path -LiteralPath $cache) -and !((Get-Item -LiteralPath (Join-Path $scanRoot 'data')).Attributes -band [IO.FileAttributes]::ReparsePoint) -and !((Get-Item -LiteralPath $cache).Attributes -band [IO.FileAttributes]::ReparsePoint)) {
        foreach ($name in @('primekg_metadata.json', 'primekg_release.json')) {
            $path = Join-Path $cache $name
            if (Test-Path -LiteralPath $path) { Snapshot-File (Get-Item -LiteralPath $path) }
        }
    }
    if ($Pull) {
        Log "Installed $script:count downloaded files; deferred $script:deferred busy files"
        if ($script:deferred -gt 0) { throw 'Some local files were busy; retry the pull transfer when their writers have finished.' }
        Log 'Pull completed successfully'
        exit 0
    }
    Log "Staged $script:count stable files"
    if ($script:count -gt 0) {
        $common = @('--log-file', $log, '--log-level', 'INFO', '--retries', '3', '--low-level-retries', '5', '--contimeout', '20s', '--timeout', '2m')
        $current = $Destination.TrimEnd('/') + '/current'
        if (!$VerifyOnly) {
            $copyArgs = @('copy', $stage, $current, '--checksum', '--backup-dir', ($Destination.TrimEnd('/') + '/history/' + $id)) + $common
            if ($DryRun) { $copyArgs += '--dry-run' }
            & $rclone @copyArgs
            if ($LASTEXITCODE -ne 0) { throw "rclone copy failed with exit code $LASTEXITCODE; next run retries all eligible files." }
        }
        if (!$DryRun) {
            & $rclone check $stage $current --one-way @common
            if ($LASTEXITCODE -ne 0) { throw "Integrity check failed with exit code $LASTEXITCODE. See $log" }
        }
    }
    Log 'Completed successfully'
} catch {
    Log "FAILED: $_"
    exit 1
} finally {
    # Delete only this invocation's temporary snapshot, never research outputs.
    if ((Split-Path $stage -Parent) -ne $state -or (Split-Path $stage -Leaf) -ne "stage-$id") { throw 'Unsafe staging cleanup path' }
    if (Test-Path -LiteralPath $stage) { Remove-Item -LiteralPath $stage -Recurse -Force }
    $lock.Dispose()
}
