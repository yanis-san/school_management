@echo off
REM Restaure depuis la DERNIERE sauvegarde dans OneDrive (settings.BACKUP_DIR)
cd /d "%~dp0"

if not exist ".venv\Scripts\python.exe" (
  echo Erreur: Environnement virtuel introuvable (.venv)
  pause
  exit /b 1
)

echo ATTENTION: Ceci va ECRASER la base et/ou les medias.
echo Continuer? (Ctrl+C pour annuler)
pause

".venv\Scripts\python.exe" manage.py restore_data --force
if errorlevel 1 (
  echo Echec de la restauration.
  pause
  exit /b 1
)

echo Restauration terminee avec succes.
pause
