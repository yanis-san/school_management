@echo off
REM Sauvegarde DB + media vers OneDrive (settings.BACKUP_DIR)
cd /d "%~dp0"

if not exist ".venv\Scripts\python.exe" (
  echo [ERREUR] Environnement virtuel introuvable (.venv)
  echo Veuillez lancer: python -m venv .venv
  pause
  exit /b 1
)

echo.
echo ========================================
echo  SAUVEGARDE DE LA BASE DE DONNEES
echo ========================================
echo.
echo Demarrage de la sauvegarde...
echo.

".venv\Scripts\python.exe" manage.py backup_data

if errorlevel 1 (
  echo.
  echo [ERREUR] La sauvegarde a echoue.
  echo Verifiez la base de donnees PostgreSQL est accessible.
  echo.
  pause
  exit /b 1
)

echo.
echo ========================================
echo  SAUVEGARDE TERMINEE AVEC SUCCES!
echo ========================================
echo.
pause
