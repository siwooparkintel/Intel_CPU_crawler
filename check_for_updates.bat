@echo off
REM Quick Dry Run - Check for new products without updating database

echo ================================================================================
echo Intel CPU Database Updater - DRY RUN MODE
echo ================================================================================
echo This will check for new products WITHOUT adding them to the database
echo.

cd /d "%~dp0"

D:\Users\siwoopar\code\Intel_cpu_crawler\.venv\Scripts\python.exe scripts\update_database.py --dry-run --verbose

echo.
echo ================================================================================
pause
