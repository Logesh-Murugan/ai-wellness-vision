@echo off
echo ========================================
echo AI Wellness Vision - Complete Launcher
echo ========================================
echo.

echo Choose your platform:
echo.
echo 1. Windows Desktop (File picker, no camera)
echo 2. Chrome Web (Camera works!)
echo 3. Check available devices
echo 4. Exit
echo.

set /p choice="Enter your choice (1-4): "

if "%choice%"=="1" goto desktop
if "%choice%"=="2" goto web
if "%choice%"=="3" goto devices
if "%choice%"=="4" goto end

:desktop
echo.
echo Starting Windows Desktop App...
echo NOTE: Use "Pick from Gallery" for images
echo.
cd flutter_app
flutter pub get
flutter run -d windows
goto end

:web
echo.
echo Starting Chrome Web App...
echo NOTE: Allow camera permissions when prompted
echo.
cd flutter_app
flutter pub get
flutter run -d chrome --web-port=8080 --web-hostname=localhost
goto end

:devices
echo.
echo Available devices:
cd flutter_app
flutter devices
echo.
pause
goto end

:end
echo.
echo Thank you for using AI Wellness Vision!
pause
