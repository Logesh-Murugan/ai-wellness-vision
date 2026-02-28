@echo off
echo ========================================
echo AI Wellness Vision - Flutter Desktop
echo ========================================
echo.

echo Starting Flutter Desktop App on Windows...
echo.
echo NOTE: Camera doesn't work on Windows desktop
echo Use "Pick from Gallery" button to select images
echo.
echo App Features:
echo - Image Analysis (use file picker)
echo - AI Chat
echo - Voice Interface
echo - History
echo - Profile Management
echo.

cd flutter_app

echo Checking Flutter setup...
flutter doctor

echo.
echo Getting dependencies...
flutter pub get

echo.
echo Running Flutter Desktop App...
flutter run -d windows

pause
