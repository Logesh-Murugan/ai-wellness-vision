@echo off
title AI Wellness Vision - CNN System

echo ========================================
echo AI WELLNESS VISION - CNN SYSTEM
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

REM Start the CNN system
echo Starting CNN Health Analysis System...
python start_and_test_cnn.py

echo.
echo Press any key to exit...
pause >nul