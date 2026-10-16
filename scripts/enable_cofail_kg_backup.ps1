# Dot-source this file so ordinary git commands in this PowerShell use the wrapper.
param(
    [string]$RclonePath = 'rclone',
    [ValidatePattern('^[A-Za-z0-9_-]+:.+')][string]$Destination = 'cofail_gdrive:CoFail-KG-Backups'
)
if ($MyInvocation.InvocationName -ne '.') { throw 'Dot-source this script: . .\scripts\enable_cofail_kg_backup.ps1' }
if (Test-Path Alias:git) { throw 'An existing git alias would hide the wrapper. Resolve that alias first.' }
if ((Test-Path Function:git) -and (Get-Item Function:git).Definition -notmatch 'CoFailGitWrapperPath') { throw 'An existing git function is already installed; resolve it before enabling this wrapper.' }
$env:COFAIL_RCLONE = (Get-Command $RclonePath -CommandType Application -ErrorAction Stop | Select-Object -First 1).Source
$env:COFAIL_BACKUP_DESTINATION = $Destination
$global:CoFailGitWrapperPath = Join-Path $PSScriptRoot 'git_cofail_kg.ps1'
function global:git {
    & $global:CoFailGitWrapperPath @args
    Set-Variable LASTEXITCODE -Value $global:LASTEXITCODE -Scope 1
}
Write-Output 'Drive transfers enabled in this PowerShell: after successful git push/pull only. No schedule.'
