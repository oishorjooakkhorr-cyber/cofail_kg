param([Parameter(Mandatory=$true)][string]$RclonePath)
$ErrorActionPreference = 'Stop'
$fixture = Join-Path $env:TEMP ('cofail-git-backup-test-' + [guid]::NewGuid())
$sourceScripts = Join-Path $PSScriptRoot '../scripts'
$originalConfig = $env:RCLONE_CONFIG
$originalRclone = $env:COFAIL_RCLONE
$originalDestination = $env:COFAIL_BACKUP_DESTINATION
$originalState = $env:COFAIL_BACKUP_STATE
function Assert($condition, $message) { if (!$condition) { throw $message } }
function Prepare-Scripts($repo) {
    New-Item -ItemType Directory -Path "$repo/scripts", "$repo/results/runs" -Force | Out-Null
    foreach ($name in @('backup_cofail_kg.ps1','git_cofail_kg.ps1','enable_cofail_kg_backup.ps1')) { Copy-Item "$sourceScripts/$name" "$repo/scripts/$name" }
}
try {
    New-Item -ItemType Directory -Path $fixture | Out-Null
    $env:RCLONE_CONFIG = "$fixture/rclone.conf"
    Set-Content $env:RCLONE_CONFIG "[test]`ntype = local"
    & git.exe init --bare -q "$fixture/origin.git"
    & git.exe init -q -b main "$fixture/a"
    & git.exe -C "$fixture/a" config user.name 'Backup Test'
    & git.exe -C "$fixture/a" config user.email 'backup-test@example.invalid'
    & git.exe -C "$fixture/a" remote add origin "$fixture/origin.git"
    Prepare-Scripts "$fixture/a"
    Set-Content "$fixture/a/.gitignore" "results/runs/`n.cofail-backup-history/`nscripts/"
    Set-Content "$fixture/a/source.txt" 'one'
    Set-Content "$fixture/a/results/runs/output.json" 'upload-a'
    (Get-Item "$fixture/a/results/runs/output.json").LastWriteTimeUtc = [datetime]::UtcNow.AddHours(-1)
    Push-Location "$fixture/a"
    . "$fixture/a/scripts/enable_cofail_kg_backup.ps1" -RclonePath $RclonePath -Destination "test:$fixture/drive"
    $env:COFAIL_BACKUP_STATE = "$fixture/state-a"
    git add .gitignore source.txt
    git commit -q -m initial
    Assert ($LASTEXITCODE -eq 0) 'Commit failed'
    Assert (!(Test-Path "$fixture/drive/current")) 'Commit triggered a transfer'
    git push --dry-run origin main
    Assert ($LASTEXITCODE -eq 0) 'Dry-run push failed'
    Assert (!(Test-Path "$fixture/drive/current")) 'Dry-run push transferred outputs'
    git push missing-remote main 2>$null
    Assert ($LASTEXITCODE -ne 0) 'Expected failed push'
    Assert (!(Test-Path "$fixture/drive/current")) 'Failed push transferred outputs'
    git push -u origin main
    Assert ($LASTEXITCODE -eq 0) 'Push plus backup failed'
    Assert ((Get-Content "$fixture/drive/current/results/runs/output.json") -eq 'upload-a') 'Successful push did not upload'
    Set-Content "$fixture/a/results/runs/output.json" 'unpublished-a'
    git status --short | Out-Null
    Assert ((Get-Content "$fixture/drive/current/results/runs/output.json") -eq 'upload-a') 'Status uploaded unpublished output'
    Pop-Location
    & git.exe clone -q --branch main "$fixture/origin.git" "$fixture/b"
    Prepare-Scripts "$fixture/b"
    Set-Content "$fixture/b/results/runs/output.json" 'local-b'
    Push-Location "$fixture/b"
    . "$fixture/b/scripts/enable_cofail_kg_backup.ps1" -RclonePath $RclonePath -Destination "test:$fixture/drive"
    $env:COFAIL_BACKUP_STATE = "$fixture/state-b"
    git pull --ff-only origin main
    Assert ($LASTEXITCODE -eq 0) 'Pull plus download failed'
    Assert ((Get-Content "$fixture/b/results/runs/output.json") -eq 'upload-a') 'Up-to-date Git pull did not download'
    $previous = @(Get-ChildItem "$fixture/b/.cofail-backup-history" -Recurse -Filter output.json)
    Assert ($previous.Count -eq 1 -and (Get-Content $previous[0].FullName) -eq 'local-b') 'Pull did not preserve old local output'
    Set-Content "$fixture/drive/current/results/runs/output.json" 'drive-new'
    git pull missing-remote main 2>$null
    Assert ($LASTEXITCODE -ne 0) 'Expected failed pull'
    Assert ((Get-Content "$fixture/b/results/runs/output.json") -eq 'upload-a') 'Failed pull downloaded outputs'
    Set-Content "$fixture/a/source.txt" 'two'
    & git.exe -C "$fixture/a" commit -qam update
    & git.exe -C "$fixture/a" push -q origin main
    git -C "$fixture/b" pull --ff-only origin main
    Assert ($LASTEXITCODE -eq 0) 'Pull with -C failed'
    Assert ((Get-Content "$fixture/b/source.txt") -eq 'two') 'Git changes were not pulled'
    Assert ((Get-Content "$fixture/b/results/runs/output.json") -eq 'drive-new') 'Drive changes were not pulled'
    & git.exe config user.name 'Backup Test'
    & git.exe config user.email 'backup-test@example.invalid'
    Set-Content "$fixture/b/source.txt" 'three'
    git commit -qam third
    Assert ($LASTEXITCODE -eq 0) 'Second computer commit failed'
    Assert ((Get-Content "$fixture/drive/current/results/runs/output.json") -eq 'drive-new') 'Commit changed Drive'
    (Get-Item "$fixture/b/results/runs/output.json").LastWriteTimeUtc = [datetime]::UtcNow.AddHours(-1)
    $env:COFAIL_BACKUP_DESTINATION = "missing:$fixture/missing"
    git push origin main
    Assert ($LASTEXITCODE -eq 1) 'A failed Drive transfer after successful Git was not reported'
    $pushedCommit = & git.exe --git-dir="$fixture/origin.git" rev-parse refs/heads/main
    $localCommit = & git.exe rev-parse HEAD
    Assert ($pushedCommit -eq $localCommit) 'Drive failure incorrectly undid the Git push'
    $env:COFAIL_BACKUP_DESTINATION = "test:$fixture/drive"
    git push origin main
    Assert ($LASTEXITCODE -eq 0) 'Retry through a subsequent push failed'
    Pop-Location
    Write-Output 'PASS: commit/status/failed commands/dry run cause no transfer; successful push uploads; successful pull downloads and preserves local versions; git -C works; Drive failure is reported without undoing Git'
} finally {
    Remove-Item Function:git -ErrorAction SilentlyContinue
    $env:RCLONE_CONFIG = $originalConfig
    $env:COFAIL_RCLONE = $originalRclone
    $env:COFAIL_BACKUP_DESTINATION = $originalDestination
    $env:COFAIL_BACKUP_STATE = $originalState
    Write-Output "Test evidence: $fixture"
}
