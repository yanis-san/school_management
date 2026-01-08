@echo off
REM Configure PostgreSQL to listen on all interfaces for network access

setlocal enabledelayedexpansion

echo Configuring PostgreSQL to accept network connections...

REM PostgreSQL config file location
set PGCONF="C:\Program Files\PostgreSQL\18\data\postgresql.conf"

REM Backup original
copy %PGCONF% "%PGCONF%.backup"

REM Replace listen_addresses
powershell -Command "(Get-Content %PGCONF%) -replace '^#?listen_addresses = .*', 'listen_addresses = ''*''  # Listen on all addresses' | Set-Content %PGCONF%"

echo.
echo ✅ PostgreSQL configuration updated!
echo.
echo Next steps:
echo 1. Restart PostgreSQL service
echo 2. Update pg_hba.conf to allow network connections (optional but recommended)
echo 3. Test connection from another PC: psql -h 192.168.42.39 -U yanis -d institut_torii_db
echo.
pause
