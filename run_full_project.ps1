#!/usr/bin/env pwsh
# AI Wellness Vision - Full Project Launcher (PowerShell)

Write-Host "========================================" -ForegroundColor Cyan
Write-Host "AI WELLNESS VISION - FULL PROJECT" -ForegroundColor Cyan
Write-Host "========================================" -ForegroundColor Cyan
Write-Host ""
Write-Host "Starting all project components..." -ForegroundColor Green
Write-Host ""

# Check if Python is available
try {
    $pythonVersion = python --version 2>&1
    Write-Host "✅ Python: $pythonVersion" -ForegroundColor Green
} catch {
    Write-Host "❌ ERROR: Python is not installed or not in PATH" -ForegroundColor Red
    Read-Host "Press Enter to exit"
    exit 1
}

# Check if Flutter is available
try {
    $flutterVersion = flutter --version 2>&1 | Select-Object -First 1
    Write-Host "✅ Flutter: $flutterVersion" -ForegroundColor Green
} catch {
    Write-Host "⚠️ WARNING: Flutter is not installed or not in PATH" -ForegroundColor Yellow
    Write-Host "Flutter mobile app will not be available" -ForegroundColor Yellow
}

Write-Host ""
Write-Host "🚀 Launching full project..." -ForegroundColor Cyan

# Run the full project launcher
python run_full_project.py

Write-Host ""
Write-Host "Press any key to exit..." -ForegroundColor Yellow
$null = $Host.UI.RawUI.ReadKey("NoEcho,IncludeKeyDown")