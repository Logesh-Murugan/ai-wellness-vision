@echo off
title AI WellnessVision - Full System Launcher
echo ===================================================
echo   AI WellnessVision - Launching Full Stack
echo ===================================================

cd /d "%~dp0"

echo [*] Launching Backend API Server in a new window...
start "AI WellnessVision API" cmd /k "run_backend.bat"

echo [*] Waiting for Backend API to become available...
powershell -Command "for ($i=0; $i -lt 15; $i++) { try { $r = Invoke-WebRequest -Uri 'http://127.0.0.1:8000/health' -UseBasicParsing -TimeoutSec 2; if ($r.StatusCode -eq 200) { Write-Host 'Backend is healthy!'; exit 0 } } catch {}; Start-Sleep -Seconds 1 }; Write-Host 'Continuing startup...'"

echo.
echo [*] Launching Flutter frontend...
cd flutter_app
call flutter run -d chrome

pause
