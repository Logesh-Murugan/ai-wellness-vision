# 🚀 Complete Flutter App Setup Guide

This guide will help you set up and run the complete AI Wellness Vision Flutter app with all backend integrations working.

## 📋 Prerequisites

### Required Software
- **Flutter SDK** 3.0.0 or higher
- **Dart SDK** 2.17.0 or higher
- **Android Studio** or **VS Code** with Flutter extensions
- **Python 3.8+** (for backend)
- **Git**

### Device/Emulator
- Android device or emulator (API level 21+)
- iOS device or simulator (iOS 11.0+)

## 🔧 Backend Setup

### 1. Start the Python Backend
```bash
# Navigate to project root
cd ai-wellnessvision

# Install Python dependencies
pip install -r requirements.txt

# Start the backend server
python main_api_server.py
```

The backend will start on `http://localhost:8000`

### 2. Verify Backend is Running
```bash
# Test the backend
python test_flutter_backend_integration.py
```

You should see all tests passing ✅

## 📱 Flutter App Setup

### 1. Install Dependencies
```bash
cd flutter_app
flutter pub get
```

### 2. Update Network Configuration

**For Android Emulator:**
- The app is configured to use `http://10.135.99.214:8000`
- This should work if your backend is running on the same machine

**For Physical Device:**
- Find your computer's IP address:
  ```bash
  # Windows
  ipconfig
  
  # macOS/Linux
  ifconfig
  ```
- Update the IP in these files:
  - `lib/core/config/api_config.dart`
  - `lib/core/config/app_config.dart`
  - `lib/core/services/api_service.dart`

### 3. Run the App
```bash
# Check connected devices
flutter devices

# Run on connected device/emulator
flutter run

# Or run in debug mode
flutter run --debug
```

## 🎯 Features Now Working

### ✅ **Authentication**
- **Login Page**: `lib/features/auth/presentation/pages/login_page.dart`
- **Register Page**: `lib/features/auth/presentation/pages/register_page.dart`
- **Backend API**: `POST /auth/login`, `POST /auth/register`

### ✅ **Image Analysis**
- **Analysis Page**: `lib/features/image_analysis/presentation/pages/image_analysis_page.dart`
- **Camera & Gallery**: Image selection and upload
- **Backend API**: `POST /analysis/image`
- **Analysis Types**: Skin, Food, Eye, Emotion, Symptom

### ✅ **Chat Assistant**
- **Chat Page**: `lib/features/chat/presentation/pages/chat_page.dart`
- **Real-time Chat**: Send messages and get AI responses
- **Backend API**: `POST /chat/message`
- **Multiple Modes**: General, Symptoms, Wellness, Mental Health

### ✅ **Voice Interaction**
- **Voice Page**: `lib/features/voice/presentation/pages/voice_interaction_page.dart`
- **Speech-to-Text**: Record voice and get transcription
- **Text-to-Speech**: Convert AI responses to speech
- **Backend API**: `POST /voice/transcribe`, `POST /voice/synthesize`

### ✅ **History & Data**
- **History Page**: `lib/features/history/presentation/pages/history_page.dart`
- **Analysis History**: View past image analyses
- **Chat History**: View conversation history
- **Backend API**: `GET /analysis/history`, `GET /chat/conversations`

## 🧪 Testing the Integration

### 1. Test Authentication
1. Open the app
2. Go to Login/Register page
3. Create a new account or login
4. Verify you're redirected to the home page

### 2. Test Image Analysis
1. Navigate to Image Analysis tab
2. Select analysis type (e.g., Skin Analysis)
3. Take a photo or select from gallery
4. Tap "Analyze Image"
5. Verify results are displayed with confidence scores

### 3. Test Chat
1. Navigate to Chat tab
2. Select chat mode (e.g., General Health)
3. Send a message like "I have a headache"
4. Verify AI responds with health advice

### 4. Test Voice
1. Navigate to Voice tab
2. Tap and hold the microphone button
3. Speak a health question
4. Verify transcription appears
5. Verify AI responds with voice

## 🔧 Troubleshooting

### Backend Connection Issues
```bash
# Check if backend is running
curl http://localhost:8000/health

# Check network connectivity
ping 10.135.99.214
```

### Flutter Build Issues
```bash
# Clean and rebuild
flutter clean
flutter pub get
flutter run
```

### Android Network Issues
Add to `android/app/src/main/AndroidManifest.xml`:
```xml
<uses-permission android:name="android.permission.INTERNET" />
<application
    android:usesCleartextTraffic="true"
    ...>
```

### iOS Network Issues
Add to `ios/Runner/Info.plist`:
```xml
<key>NSAppTransportSecurity</key>
<dict>
    <key>NSAllowsArbitraryLoads</key>
    <true/>
</dict>
```

## 📊 API Endpoints Summary

| Feature | Method | Endpoint | Status |
|---------|--------|----------|--------|
| Health Check | GET | `/health` | ✅ |
| Login | POST | `/auth/login` | ✅ |
| Register | POST | `/auth/register` | ✅ |
| Image Analysis | POST | `/analysis/image` | ✅ |
| Analysis History | GET | `/analysis/history` | ✅ |
| Chat Message | POST | `/chat/message` | ✅ |
| Conversations | GET | `/chat/conversations` | ✅ |
| Voice Transcribe | POST | `/voice/transcribe` | ✅ |
| Voice Synthesize | POST | `/voice/synthesize` | ✅ |

## 🎉 Success Indicators

When everything is working correctly, you should see:

1. **Login/Register** - Users can create accounts and login
2. **Image Analysis** - Photos are analyzed with AI results
3. **Chat** - Messages get intelligent health responses
4. **Voice** - Speech is transcribed and responses are spoken
5. **History** - Past analyses and chats are saved and retrievable

## 📞 Support

If you encounter issues:

1. Check the backend logs in the terminal
2. Check Flutter logs with `flutter logs`
3. Verify network connectivity
4. Ensure all dependencies are installed
5. Try restarting both backend and Flutter app

## 🚀 Next Steps

With all features working, you can now:

1. **Customize UI** - Modify themes and layouts
2. **Add Features** - Implement additional health tools
3. **Deploy Backend** - Move to production server
4. **Publish App** - Deploy to App Store/Play Store
5. **Add Analytics** - Track user engagement

Your AI Wellness Vision app is now fully functional with all backend integrations! 🎉