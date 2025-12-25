@echo off
chcp 65001 >nul
REM Restaure depuis la DERNIERE sauvegarde dans OneDrive (settings.BACKUP_DIR)
REM Script AUTONOME avec DOUBLE CONFIRMATION

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
echo ║         RESTAURATION DE LA BASE DE DONNEES                ║
echo ║                                                            ║
echo ║     ⚠️  ATTENTION: CECI VA ECRASER TOUTES LES DONNEES!    ║
echo ║                                                            ║
echo ╚════════════════════════════════════════════════════════════╝
echo.
echo.
echo PREMIERE CONFIRMATION:
echo Tapez OUI en majuscules pour continuer (ou entrez pour annuler):
set /p confirm1=">>> "

if /i not "%confirm1%"=="OUI" (
  echo.
  echo Restauration annulee.
  echo.
  pause
  exit /b 0
)

cls
echo.
echo ╔════════════════════════════════════════════════════════════╗
echo ║                                                            ║
echo ║                DEUXIEME CONFIRMATION                      ║
echo ║                                                            ║
echo ║  Cette action va SUPPRIMER les donnees actuelles!         ║
echo ║  Confirmez une seconde fois: tapez OUI                    ║
echo ║                                                            ║
echo ╚════════════════════════════════════════════════════════════╝
echo.
echo.
set /p confirm2=">>> "

if /i not "%confirm2%"=="OUI" (
  echo.
  echo Restauration annulee.
  echo.
  pause
  exit /b 0
)

echo.
echo Demarrage de la restauration...
echo.

".venv\Scripts\python.exe" manage.py restore_data --force

if errorlevel 1 (
  echo.
  echo ╔════════════════════════════════════════════════════════════╗
  echo ║                     [ERREUR]                               ║
  echo ║  La restauration a echoue.                                ║
  echo ║                                                            ║
  echo ║  Verifiez que:                                            ║
  echo ║  - PostgreSQL est demarree                                ║
  echo ║  - Un backup existe dans OneDrive                         ║
  echo ╚════════════════════════════════════════════════════════════╝
  echo.
  pause
  exit /b 1
)

echo.
echo ╔════════════════════════════════════════════════════════════╗
echo ║                                                            ║
echo ║           ✓ RESTAURATION REUSSIE!                         ║
echo ║                                                            ║
echo ║  La base de donnees a ete restauree.                      ║
echo ║                                                            ║
echo ╚════════════════════════════════════════════════════════════╝
echo.
pause
exit /b 0
