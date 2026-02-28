@echo off
echo ========================================
echo AI WELLNESS VISION - FULL PROJECT
echo ========================================
echo.
echo Starting all project components...
echo.

REM Check if Python is available
python --version >nul 2>&1
if errorlevel 1 (
    echo ERROR: Python is not installed or not in PATH
    pause
    exit /b 1
)

REM Run the full project launcher
python run_full_project.py

pause