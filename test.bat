@echo off
REM Quick test script for Intel CPU Crawler
REM Runs the comprehensive integration test suite

echo 🧪 Running Intel CPU Crawler Tests...
echo.

REM Activate virtual environment if it exists
if exist ".venv\Scripts\activate.bat" (
    call .venv\Scripts\activate.bat
    echo ✅ Virtual environment activated
) else (
    echo ⚠️  Virtual environment not found, using system Python
)

REM Run integration tests
python run_tests.py --integration

echo.
echo ✨ Test complete!
pause