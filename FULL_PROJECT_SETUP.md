# 🏥 AI Wellness Vision - Full Project Setup

## 🚀 Quick Start (Recommended)

### Option 1: Windows Batch File
```bash
# Double-click or run in Command Prompt
run_full_project.bat
```

### Option 2: PowerShell
```powershell
# Run in PowerShell
.\run_full_project.ps1
```

### Option 3: Python Script
```bash
# Run directly with Python
python run_full_project.py
```

## 🎯 What Gets Started

The full project launcher starts all these components:

### 1. 🔧 Backend API Server (Port 8000)
- **URL**: http://localhost:8000
- **Docs**: http://localhost:8000/docs
- **Features**:
  - Health chat with Gemini AI
  - Image analysis (Skin, Food, Eye, Wellness)
  - User authentication
  - Analysis history
  - Voice processing endpoints

### 2. 🌐 Streamlit Web Interface (Port 8501)
- **URL**: http://localhost:8501
- **Features**:
  - Web-based health dashboard
  - Image upload and analysis
  - Chat interface
  - Health analytics
  - User-friendly web UI

### 3. 📱 Flutter Mobile App (Port 8080)
- **URL**: http://localhost:8080
- **Features**:
  - Beautiful mobile-first UI
  - Camera integration
  - Real-time chat
  - Voice interactions
  - Material 3 design
  - Cross-platform (Web/Mobile)

## 🔧 Prerequisites

### Required Software
1. **Python 3.8+** with pip
2. **Flutter SDK** (for mobile app)
3. **Chrome Browser** (for Flutter web)

### Required Python Packages
The launcher will auto-install these:
- `fastapi`
- `uvicorn`
- `google-generativeai`
- `python-dotenv`
- `streamlit`
- `psycopg2-binary`

### Environment Setup
1. **Gemini API Key**: Add to `.env` file
   ```
   GEMINI_API_KEY=your_actual_api_key_here
   ```

2. **Flutter Dependencies**: Auto-installed by launcher

## 🎮 Available Features

### 🤖 AI-Powered Health Analysis
- **Skin Analysis**: Detect skin conditions, hydration, recommendations
- **Food Analysis**: Nutritional assessment, calorie estimation
- **Eye Health**: Basic eye health screening
- **General Wellness**: Overall health insights

### 💬 Intelligent Health Chat
- Powered by Gemini AI
- Health-focused responses
- Smart fallback system
- Conversation history

### 📸 Image Processing
- Multiple analysis types
- Confidence scoring
- Detailed recommendations
- History tracking

### 🎤 Voice Interactions
- Speech-to-text processing
- Voice commands
- Audio responses

### 👤 User Management
- Registration and login
- Profile management
- Personalized recommendations
- Secure authentication

### 📊 Analytics & History
- Analysis history
- Health trends
- Progress tracking
- Export capabilities

## 🔒 Security Features
- Data encryption
- Privacy protection
- Secure API endpoints
- User consent management

## 🛠️ Troubleshooting

### Common Issues

1. **Port Already in Use**
   - Backend (8000): Stop other FastAPI/Django apps
   - Streamlit (8501): Stop other Streamlit apps
   - Flutter (8080): Stop other web servers

2. **Gemini API Errors**
   - Check your API key in `.env`
   - Verify API key has proper permissions
   - Check internet connection

3. **Flutter Issues**
   - Run `flutter doctor` to check setup
   - Ensure Chrome is installed
   - Try `flutter clean` in flutter_app directory

4. **Python Package Issues**
   - Update pip: `python -m pip install --upgrade pip`
   - Install manually: `pip install -r requirements.txt`

### Manual Service Start

If the launcher fails, start services manually:

```bash
# Backend
python main_api_server.py

# Streamlit (new terminal)
streamlit run streamlit_app.py

# Flutter (new terminal)
cd flutter_app
flutter run -d chrome --web-port=8080
```

## 📱 Mobile Development

### Android/iOS Development
```bash
cd flutter_app

# For Android
flutter run -d android

# For iOS (Mac only)
flutter run -d ios
```

### Building for Production
```bash
cd flutter_app

# Web build
flutter build web

# Android APK
flutter build apk

# iOS (Mac only)
flutter build ios
```

## 🌐 Deployment Options

### Docker Deployment
```bash
# Build and run with Docker Compose
docker-compose up --build
```

### Cloud Deployment
- Backend: Deploy to Heroku, AWS, or Google Cloud
- Frontend: Deploy to Netlify, Vercel, or Firebase
- Database: Use PostgreSQL on cloud providers

## 📞 Support

If you encounter issues:
1. Check the console output for error messages
2. Verify all prerequisites are installed
3. Check the troubleshooting section above
4. Ensure your Gemini API key is valid

## 🎉 Success Indicators

When everything is working correctly, you should see:
- ✅ Backend API running on port 8000
- ✅ Streamlit web app on port 8501
- ✅ Flutter mobile app on port 8080
- ✅ All browsers opening automatically
- ✅ No error messages in console

Enjoy your AI-powered wellness application! 🏥✨