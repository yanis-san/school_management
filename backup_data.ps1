Param(
  [switch]$OnlyDb,
  [switch]$OnlyMedia,
  [string]$Dest
)

$ErrorActionPreference = 'Stop'
Set-Location -Path $PSScriptRoot

# Fix encoding for Unicode output
[System.Environment]::SetEnvironmentVariable('PYTHONIOENCODING', 'utf-8')
$env:PYTHONIOENCODING = 'utf-8'

$venv = Join-Path $PSScriptRoot '.venv\Scripts\python.exe'
if (-not (Test-Path $venv)) {
  Write-Host 'Erreur: Environnement virtuel introuvable (.venv)' -ForegroundColor Red
  exit 1
}

Write-Host "Exécution de la sauvegarde..." -ForegroundColor Cyan

$args_list = @('manage.py', 'backup_data')
if ($OnlyDb) { $args_list += '--only-db' }
if ($OnlyMedia) { $args_list += '--only-media' }
if ($Dest) { $args_list += '--dest'; $args_list += $Dest }

& $venv $args_list

if ($LASTEXITCODE -ne 0) {
  Write-Host "Erreur lors de la sauvegarde" -ForegroundColor Red
  exit $LASTEXITCODE
}
Write-Host "Sauvegarde terminée avec succès !" -ForegroundColor Green
