@echo off
REM Script batch pour vérifier le contenu de la dernière sauvegarde
cd /d "%~dp0"
.venv\Scripts\python.exe verify_backup.py
pause
