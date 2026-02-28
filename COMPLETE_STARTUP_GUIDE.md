# AI Wellness Vision - Complete Startup Guide

## 🚀 Quick Start (Recommended)

### Option 1: One-Click Startup (Windows)
```bash
# Run the complete system
python start_complete_system.py
```

### Option 2: Manual Step-by-Step

#### 1. Backend Server
```bash
# Start the main API server
python main_api_server_cnn.py
```

#### 2. Flutter Web App
```bash
# Navigate to flutter app directory
cd flutter_app

# Run Flutter web
flutter run -d web-server --web-port 3000
```

## 📋 Prerequisites

### Required Software
- Python 3.8+
- Flutter SDK 3.0+
- Node.js (optional, for additional tools)

### Python Dependencies
```bash
pip install -r requirements.txt
pip install -r requirements_cnn.txt
```

### Flutter Dependencies
```bash
cd flutter_app
flutter pub get
```

## 🔧 Environment Setup

### 1. Environment Variables
Create `.env` file in root directory:
```env
# API Configuration
API_HOST=localhost
API_PORT=8000
CORS_ORIGINS=http://localhost:3000,http://127.0.0.1:3000

# AI Model Configuration
GEMINI_API_KEY=your_gemini_api_key_here
MODEL_PATH=./models/
CNN_MODEL_ENABLED=true

# Database (Optional)
DATABASE_URL=sqlite:///./ai_wellness.db
POSTGRES_URL=postgresql://user:password@localhost:5432/ai_wellness

# Security
SECRET_KEY=your-secret-key-here
JWT_SECRET=your-jwt-secret-here

# Logging
LOG_LEVEL=INFO
DEBUG=true
```

### 2. Model Setup
```bash
# Setup CNN models
python setup_cnn_models.py

# Test model loading
python test_cnn_system.py
```

## 🌐 Server Endpoints

### Main API Server (Port 8000)
- **Health Check**: `GET http://localhost:8000/health`
- **Image Analysis**: `POST http://localhost:8000/api/v1/analysis/image`
- **Chat**: `POST http://localhost:8000/api/v1/chat`
- **Voice**: `POST http://localhost:8000/api/v1/voice`

### Flutter Web App (Port 3000)
- **Main App**: `http://localhost:3000`
- **Image Analysis**: `http://localhost:3000/#/analysis`

## 🔍 Testing the System

### 1. Test Backend
```bash
# Test server status
python check_server_status.py

# Test CNN integration
python test_cnn_priority.py

# Test image analysis
python test_image_analysis_fix.py
```

### 2. Test Flutter Integration
```bash
cd flutter_app
dart test_cnn_connection.dart
```

## 🐛 Troubleshooting

### Common Issues

#### 1. Port Already in Use
```bash
# Kill processes on port 8000
netstat -ano | findstr :8000
taskkill /PID <PID> /F

# Kill processes on port 3000
netstat -ano | findstr :3000
taskkill /PID <PID> /F
```

#### 2. Flutter Web Issues
```bash
# Clean Flutter cache
flutter clean
flutter pub get

# Enable web support
flutter config --enable-web
```

#### 3. Python Dependencies
```bash
# Reinstall dependencies
pip uninstall -r requirements.txt -y
pip install -r requirements.txt

# Virtual environment (recommended)
python -m venv venv
venv\Scripts\activate  # Windows
pip install -r requirements.txt
```

## 📊 System Architecture

```
┌─────────────────┐    ┌─────────────────┐    ┌─────────────────┐
│   Flutter Web   │    │   FastAPI       │    │   AI Models     │
│   (Port 3000)   │◄──►│   (Port 8000)   │◄──►│   (CNN/Gemini)  │
│                 │    │                 │    │                 │
│ - Image Upload  │    │ - Image Analysis│    │ - Health Analysis│
│ - Chat Interface│    │ - Chat API      │    │ - NLP Processing │
│ - Voice Input   │    │ - Voice API     │    │ - Voice Recognition│
└─────────────────┘    └─────────────────┘    └─────────────────┘
```

## 🔐 Security Features

- JWT Authentication
- CORS Protection
- Input Validation
- Rate Limiting
- Secure File Upload

## 📱 Features Available

### ✅ Working Features
- ✅ Image Analysis (CNN + Gemini)
- ✅ Multiple Analysis Types (Skin, Food, Eye, Wellness)
- ✅ Web-Compatible Image Upload
- ✅ Real-time Analysis Results
- ✅ Responsive UI
- ✅ Error Handling

### 🚧 In Development
- 🚧 Chat Interface
- 🚧 Voice Recognition
- 🚧 User Authentication
- 🚧 History Tracking
- 🚧 Advanced Analytics

## 📞 Support

If you encounter issues:
1. Check the logs in the console
2. Verify all dependencies are installed
3. Ensure ports 3000 and 8000 are available
4. Run the test scripts to identify issues

## 🎯 Next Steps

1. **Start the system**: Run `python start_complete_system.py`
2. **Open browser**: Navigate to `http://localhost:3000`
3. **Test image analysis**: Upload an image and select analysis type
4. **Explore features**: Try different analysis types and options