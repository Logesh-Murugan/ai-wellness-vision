@echo off
title AI WellnessVision - Backend API Server
echo ===================================================
echo   AI WellnessVision - Starting Backend API Server
echo ===================================================

cd /d "%~dp0"

if not exist ".venv\Scripts\python.exe" (
    echo [ERROR] Virtual environment not found at .venv
    echo Please create the virtual environment and install dependencies.
    pause
    exit /b 1
)

echo [*] Starting Uvicorn API server on http://127.0.0.1:8000 ...
.venv\Scripts\python.exe -m uvicorn src.api.main:app --host 127.0.0.1 --port 8000 --reload
pause
