@echo off
title AI Wellness Vision - Project Launcher

echo ========================================
echo AI WELLNESS VISION - PROJECT LAUNCHER
echo ========================================
echo.

REM Check Python
python --version >nul 2>&1
if errorlevel 1 (
    echo ERROR: Python is not installed or not in PATH
    echo Please install Python from: https://python.org
    pause
    exit /b 1
)

echo Python is available
echo.

REM Run the simple launcher
python start_project_simple.py

echo.
echo Press any key to exit...
pause >nul