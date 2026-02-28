@echo off
echo ========================================
echo AI Wellness Vision - Flutter Web with Camera
echo ========================================
echo.

echo Starting Flutter Web App on Chrome...
echo Camera permissions will be requested by browser
echo.
echo IMPORTANT: 
echo 1. Click "Allow" when Chrome asks for camera permission
echo 2. Look for camera icon in address bar if needed
echo 3. App will open at: http://localhost:8080
echo.

cd flutter_app

echo Running Flutter Web...
flutter run -d chrome --web-port=8080 --web-hostname=localhost

pause
