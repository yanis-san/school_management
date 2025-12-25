@echo off
REM Restaure depuis la DERNIERE sauvegarde dans OneDrive (settings.BACKUP_DIR)
cd /d "%~dp0"

if not exist ".venv\Scripts\python.exe" (
  echo [ERREUR] Environnement virtuel introuvable (.venv)
  echo Veuillez lancer: python -m venv .venv
  pause
  exit /b 1
)

echo.
echo ========================================
echo  RESTAURATION DE LA BASE DE DONNEES
echo ========================================
echo.
echo ATTENTION: Ceci va ECRASER la base actuelle et les medias!
echo Continuer? Appuyez sur une touche pour continuer ou Ctrl+C pour annuler
echo.
pause

echo.
echo Demarrage de la restauration...
echo.

".venv\Scripts\python.exe" manage.py restore_data --force

if errorlevel 1 (
  echo.
  echo [ERREUR] La restauration a echoue.
  echo Verifiez que:
  echo - La base de donnees PostgreSQL est accessible
  echo - Un backup existe dans OneDrive
  echo.
  pause
  exit /b 1
)

echo.
echo ========================================
echo  RESTAURATION TERMINEE AVEC SUCCES!
echo ========================================
echo.
pause
