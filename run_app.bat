@echo off
title AI WellnessVision - Flutter Client
echo ===================================================
echo   AI WellnessVision - Starting Flutter Application
echo ===================================================

cd /d "%~dp0flutter_app"

echo [*] Available Devices:
call flutter devices

echo.
echo Select target platform:
echo [1] Chrome (Web) - Recommended for rapid testing
echo [2] Windows (Desktop)
echo [3] Default / Auto-detect
echo.
set /p choice="Enter choice (1-3) [default=1]: "

if "%choice%"=="2" (
    echo [*] Launching on Windows Desktop...
    call flutter run -d windows
) else if "%choice%"=="3" (
    echo [*] Launching on default device...
    call flutter run
) else (
    echo [*] Launching in Chrome Web...
    call flutter run -d chrome
)

pause
