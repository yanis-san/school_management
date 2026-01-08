@echo off
REM Start Institut Torii Application Server
REM Run this at startup to launch the app for all network users

cd /d "C:\Users\Social Media Manager\Documents\codes\school_management"

REM Activate virtual environment and start Django
cmd /k ".venv\Scripts\activate.bat && python manage.py runserver 0.0.0.0:8000"
