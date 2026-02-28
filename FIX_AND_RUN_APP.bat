@echo off
echo 🔧 Fixed duplicate HTTP dependency in pubspec.yaml
echo.
cd flutter_app
echo 📦 Getting dependencies...
flutter pub get
echo.
echo 🚀 Starting Flutter app with real backend connection...
flutter run
pause