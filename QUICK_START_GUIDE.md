# 🚀 Quick Start Guide - AI Wellness Vision

This guide will get your AI Wellness Vision system up and running in minutes.

## 📋 Prerequisites

- **Python 3.8+** installed
- **Flutter SDK** (for mobile app)
- **Git** (optional)

## 🔧 Step 1: Start the Backend Server

### Option A: Using the startup script (Recommended)
```bash
python start_backend.py
```

### Option B: Using batch file (Windows)
```bash
run_server.bat
```

### Option C: Using PowerShell (Windows)
```powershell
.\run_server.ps1
```

### Option D: Manual start
```bash
python main_api_server.py
```

## ✅ Step 2: Verify Backend is Running

Once the server starts, you should see:
```
🚀 Starting AI Wellness Vision API Server...
📱 Flutter app can connect to: http://localhost:8000
📖 API documentation: http://localhost:8000/docs
🔍 Health check: http://localhost:8000/api/v1/health
```

### Test the backend:
```bash
python test_flutter_backend_integration.py
```

You should see:
```
✅ PASS Health Check
✅ PASS Authentication  
✅ PASS Chat Endpoints
✅ PASS Image Analysis
✅ PASS Voice Endpoints
```

## 📱 Step 3: Run the Flutter App

### Navigate to Flutter app directory:
```bash
cd flutter_app
```

### Install dependencies:
```bash
flutter pub get
```

### Run the app:
```bash
flutter run
```

## 🎯 What You Can Do Now

### ✅ **Working Features:**

1. **🔐 Authentication**
   - Register new users
   - Login existing users
   - JWT token management

2. **📸 Image Analysis**
   - Take photos or select from gallery
   - Analyze skin conditions
   - Food recognition
   - Eye health screening
   - Emotion detection

3. **💬 Chat Assistant**
   - Ask health questions
   - Get AI-powered responses
   - Multiple chat modes (general, symptoms, wellness)
   - Multilingual support

4. **🎤 Voice Interaction**
   - Speech-to-text transcription
   - Text-to-speech responses
   - Voice-based health queries

5. **📊 History & Data**
   - View analysis history
   - Chat conversation history
   - User profile management

## 🧪 Testing Individual Features

### Test Authentication:
```bash
curl -X POST "http://localhost:8000/api/v1/auth/register" \
  -H "Content-Type: application/json" \
  -d '{"email":"test@example.com","password":"test123"}'
```

### Test Chat:
```bash
curl -X POST "http://localhost:8000/api/v1/chat/message" \
  -H "Content-Type: application/json" \
  -d '{"message":"I have a headache","conversation_id":"test"}'
```

### Test Image Analysis:
```bash
curl -X POST "http://localhost:8000/api/v1/analysis/image" \
  -F "image=@test_image.jpg" \
  -F "analysis_type=skin" \
  -F "session_id=test"
```

## 🔧 Troubleshooting

### Backend Issues:

**Server won't start:**
```bash
# Install missing dependencies
pip install fastapi uvicorn python-multipart pydantic

# Check if port 8000 is in use
netstat -an | findstr :8000
```

**Connection refused:**
- Make sure the backend server is running
- Check firewall settings
- Verify port 8000 is not blocked

### Flutter Issues:

**Build errors:**
```bash
flutter clean
flutter pub get
flutter run
```

**Network issues:**
- Update IP address in Flutter config files
- Check Android/iOS network permissions

## 📊 API Endpoints Summary

| Endpoint | Method | Description | Status |
|----------|--------|-------------|--------|
| `/health` | GET | Health check | ✅ |
| `/api/v1/auth/register` | POST | User registration | ✅ |
| `/api/v1/auth/login` | POST | User login | ✅ |
| `/api/v1/chat/message` | POST | Send chat message | ✅ |
| `/api/v1/analysis/image` | POST | Analyze image | ✅ |
| `/api/v1/voice/transcribe` | POST | Speech-to-text | ✅ |
| `/api/v1/voice/synthesize` | POST | Text-to-speech | ✅ |
| `/api/v1/analysis/history` | GET | Get analysis history | ✅ |

## 🎉 Success Indicators

When everything is working, you should see:

### Backend Server:
- ✅ Server starts without errors
- ✅ Health check returns 200 OK
- ✅ API docs accessible at `/docs`

### Flutter App:
- ✅ App builds and runs
- ✅ Can register/login users
- ✅ Image analysis works
- ✅ Chat responds to messages
- ✅ Voice features work

### Integration Tests:
- ✅ All 5 test categories pass
- ✅ No connection errors
- ✅ Proper API responses

## 🆘 Need Help?

1. **Check server logs** - Look for error messages in the terminal
2. **Verify dependencies** - Make sure all packages are installed
3. **Test endpoints individually** - Use curl or Postman
4. **Check network connectivity** - Ensure no firewall blocking
5. **Restart everything** - Sometimes a fresh start helps

## 🚀 Next Steps

Once everything is working:

1. **Customize the UI** - Modify Flutter app themes and layouts
2. **Add more features** - Implement additional health tools
3. **Deploy to production** - Use Docker or cloud platforms
4. **Publish the app** - Deploy to App Store/Play Store

Your AI Wellness Vision system is now ready to use! 🎉