@echo off
chcp 65001 >nul
REM Sauvegarde DB + media vers OneDrive (settings.BACKUP_DIR)
REM Script AUTONOME - Aucune action requise, juste double-cliquez!

cd /d "%~dp0"

if not exist ".venv\Scripts\python.exe" (
  echo.
  echo [ERREUR CRITIQUE]
  echo L'environnement virtuel .venv n'existe pas!
  echo.
  echo Solution: Ouvrez PowerShell ici et lancez:
  echo   python -m venv .venv
  echo   .venv\Scripts\pip install -r requirements.txt
  echo.
  pause
  exit /b 1
)

cls
echo.
echo ╔════════════════════════════════════════════════════════════╗
echo ║                                                            ║
echo ║           SAUVEGARDE DE LA BASE DE DONNEES                ║
echo ║                                                            ║
echo ╚════════════════════════════════════════════════════════════╝
echo.
echo Demarrage...
echo.

".venv\Scripts\python.exe" manage.py backup_data

if errorlevel 1 (
  echo.
  echo ╔════════════════════════════════════════════════════════════╗
  echo ║                     [ERREUR]                               ║
  echo ║  La sauvegarde a echoue.                                  ║
  echo ║                                                            ║
  echo ║  Verifiez que PostgreSQL est demarree.                    ║
  echo ╚════════════════════════════════════════════════════════════╝
  echo.
  pause
  exit /b 1
)

echo.
echo ╔════════════════════════════════════════════════════════════╗
echo ║                                                            ║
echo ║           ✓ SAUVEGARDE REUSSIE!                           ║
echo ║                                                            ║
echo ║  Les fichiers ont ete sauvegardent automatiquement.        ║
echo ║                                                            ║
echo ╚════════════════════════════════════════════════════════════╝
echo.
pause
exit /b 0
