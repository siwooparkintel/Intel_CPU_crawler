@echo off
REM Intel CPU Database Updater - Windows Batch Script
REM This script runs the database updater with logging

echo ================================================================================
echo Intel CPU Database Updater
echo ================================================================================
echo.

REM Set the working directory to the script location
cd /d "%~dp0"

REM Set timestamp for log file
set TIMESTAMP=%date:~-4,4%%date:~-10,2%%date:~-7,2%_%time:~0,2%%time:~3,2%%time:~6,2%
set TIMESTAMP=%TIMESTAMP: =0%

REM Create logs directory if it doesn't exist
if not exist "logs" mkdir logs

REM Run the updater and save output to log file
echo Running update check...
echo Start time: %date% %time%
echo.

D:\Users\siwoopar\code\Intel_cpu_crawler\.venv\Scripts\python.exe scripts\update_database.py --verbose > "logs\update_%TIMESTAMP%.log" 2>&1

REM Check exit code
if %ERRORLEVEL% EQU 0 (
    echo.
    echo ================================================================================
    echo SUCCESS: Database update completed successfully!
    echo ================================================================================
    echo Log file: logs\update_%TIMESTAMP%.log
) else if %ERRORLEVEL% EQU 2 (
    echo.
    echo ================================================================================
    echo WARNING: Update completed with some failures
    echo ================================================================================
    echo Log file: logs\update_%TIMESTAMP%.log
) else (
    echo.
    echo ================================================================================
    echo ERROR: Update failed
    echo ================================================================================
    echo Log file: logs\update_%TIMESTAMP%.log
)

echo.
echo End time: %date% %time%
echo ================================================================================
pause
