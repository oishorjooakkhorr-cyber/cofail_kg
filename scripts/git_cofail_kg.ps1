# Run Git first; successful push/pull commands trigger the corresponding Drive transfer.
$ErrorActionPreference = 'Continue'
$gitArguments = @($args)
$gitExecutable = (Get-Command git.exe -CommandType Application -ErrorAction Stop | Select-Object -First 1).Source
$index = 0
$globalGitArguments = @()
while ($index -lt $gitArguments.Count -and $gitArguments[$index].StartsWith('-')) {
    $option = $gitArguments[$index]
    $globalGitArguments += $option
    $index++
    if ($option -in @('-C','-c','--git-dir','--work-tree','--namespace','--config-env') -and $index -lt $gitArguments.Count) {
        $globalGitArguments += $gitArguments[$index]
        $index++
    }
}
$operation = if ($index -lt $gitArguments.Count) { $gitArguments[$index] } else { '' }
& $gitExecutable @gitArguments
$gitExit = $LASTEXITCODE
if ($gitExit -ne 0 -or $operation -notin @('push','pull') -or '--dry-run' -in $gitArguments -or '-n' -in $gitArguments -or '--help' -in $gitArguments -or '-h' -in $gitArguments) {
    $global:LASTEXITCODE = $gitExit
    return
}
$root = Split-Path $PSScriptRoot -Parent
$currentRoot = & $gitExecutable @globalGitArguments rev-parse --show-toplevel 2>$null
$inRepository = $LASTEXITCODE -eq 0 -and $currentRoot -and ([IO.Path]::GetFullPath($currentRoot) -eq [IO.Path]::GetFullPath($root))
if (!$inRepository) { $global:LASTEXITCODE = $gitExit; return }
$backupArguments = @('-RepositoryRoot', $root)
if ($env:COFAIL_RCLONE) { $backupArguments += @('-RclonePath', $env:COFAIL_RCLONE) }
if ($env:COFAIL_BACKUP_DESTINATION) { $backupArguments += @('-Destination', $env:COFAIL_BACKUP_DESTINATION) }
if ($env:COFAIL_BACKUP_STATE) { $backupArguments += @('-StateDirectory', $env:COFAIL_BACKUP_STATE) }
if ($operation -eq 'pull') { $backupArguments += '-Pull' }
# A subprocess isolates backup errors/exit statements from the interactive shell.
& powershell.exe -NoProfile -NonInteractive -ExecutionPolicy Bypass -File (Join-Path $PSScriptRoot 'backup_cofail_kg.ps1') @backupArguments
if ($LASTEXITCODE -ne 0) {
    Write-Warning "Git $operation succeeded, but the Drive transfer failed. Retry with another git $operation when ready; Git has already completed."
    $global:LASTEXITCODE = 1
} else { $global:LASTEXITCODE = 0 }
