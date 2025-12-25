@echo off
REM Sauvegarde DB + media vers OneDrive (settings.BACKUP_DIR)
cd /d "%~dp0"

if not exist ".venv\Scripts\python.exe" (
  echo Erreur: Environnement virtuel introuvable (.venv)
  pause
  exit /b 1
)

echo Creation de la sauvegarde...
".venv\Scripts\python.exe" manage.py backup_data
if errorlevel 1 (
  echo Echec de la sauvegarde.
  pause
  exit /b 1
)

echo Sauvegarde terminee avec succes.
pause
