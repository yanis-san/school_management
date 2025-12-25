Param(
  [string]$File,
  [switch]$Force,
  [switch]$OnlyDb,
  [switch]$OnlyMedia
)

$ErrorActionPreference = 'Stop'
Set-Location -Path $PSScriptRoot

$venv = Join-Path $PSScriptRoot '.venv\Scripts\python.exe'
if (-not (Test-Path $venv)) {
  Write-Host 'Erreur: Environnement virtuel introuvable (.venv)' -ForegroundColor Red
  exit 1
}

Write-Host "Exécution de la restauration..." -ForegroundColor Cyan

$args_list = @('manage.py', 'restore_data', '--force')
if ($File) { $args_list += '--file'; $args_list += $File }
if ($OnlyDb) { $args_list += '--only-db' }
if ($OnlyMedia) { $args_list += '--only-media' }

& $venv $args_list

if ($LASTEXITCODE -ne 0) {
  Write-Host "Erreur lors de la restauration" -ForegroundColor Red
  exit $LASTEXITCODE
}
Write-Host "Restauration terminée avec succès !" -ForegroundColor Green
