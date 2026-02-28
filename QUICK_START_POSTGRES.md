# 🚀 Quick Start: AI Wellness Vision with PostgreSQL

Get your AI Wellness Vision app running with PostgreSQL authentication in minutes!

## ⚡ One-Command Setup

### Windows (PowerShell)
```powershell
.\start_postgres_server.ps1
```

### macOS/Linux
```bash
python start_postgres_server.py
```

This will automatically:
- ✅ Start PostgreSQL (via Docker if needed)
- ✅ Install Python dependencies
- ✅ Create database schema
- ✅ Set up default users
- ✅ Start the API server

## 🧪 Test Everything Works

```bash
# Test the PostgreSQL authentication
python test_postgres_auth.py

# Test Flutter integration endpoints
python test_flutter_postgres_integration.py
```

## 📱 Flutter App Configuration

Update your Flutter app's API configuration:

```dart
// lib/core/config/api_config.dart
class ApiConfig {
  static const String baseUrl = 'http://localhost:8000';
  // ... rest of your config
}
```

## 🎯 What You Get

### 🔐 Authentication
- User registration and login
- JWT token-based security
- Session management
- Password hashing with bcrypt

### 💬 Chat Features
- AI-powered responses
- Multiple chat modes (general, nutrition, fitness, mental health)
- Conversation history

### 📸 Image Analysis
- Multiple analysis types (skin, nutrition, general)
- Confidence scoring
- Personalized recommendations
- Analysis history

### 🎤 Voice Processing
- Text-to-speech synthesis
- Speech-to-text transcription
- Audio file handling

### 👤 User Management
- User profiles
- Preferences storage
- Profile updates

## 🗄️ Database

Your PostgreSQL database includes:
- **users** - User accounts and profiles
- **user_sessions** - JWT token sessions
- **analysis_history** - Image analysis results
- **chat_conversations** - Chat threads
- **chat_messages** - Individual messages

## 🔑 Default Test Users

| Email | Password | Role |
|-------|----------|------|
| `admin@wellnessvision.ai` | `admin123` | Admin |
| `test@wellnessvision.ai` | `user123` | User |

## 🌐 API Endpoints

Once running, access:
- **API Server:** http://localhost:8000
- **API Documentation:** http://localhost:8000/docs
- **Health Check:** http://localhost:8000/health

## 🐳 Docker Alternative

```bash
# Start with Docker Compose
docker-compose -f docker-compose.postgres.yml up -d

# Check logs
docker-compose -f docker-compose.postgres.yml logs -f api

# Stop services
docker-compose -f docker-compose.postgres.yml down
```

## 🔧 Manual Setup (if needed)

1. **Install PostgreSQL:**
   ```bash
   # Ubuntu/Debian
   sudo apt install postgresql postgresql-contrib
   
   # macOS
   brew install postgresql
   
   # Windows: Download from postgresql.org
   ```

2. **Create Database:**
   ```bash
   createdb ai_wellness_vision
   ```

3. **Install Dependencies:**
   ```bash
   pip install asyncpg bcrypt fastapi uvicorn python-jose[cryptography] passlib[bcrypt]
   ```

4. **Setup Database:**
   ```bash
   python setup_postgres.py
   ```

5. **Start Server:**
   ```bash
   python main_api_server_postgres.py
   ```

## 🚨 Troubleshooting

### PostgreSQL Connection Issues
```bash
# Check if PostgreSQL is running
sudo systemctl status postgresql

# Start PostgreSQL
sudo systemctl start postgresql

# Test connection
python setup_postgres.py test
```

### Common Errors

**"Connection refused"**
```bash
# Start PostgreSQL service
sudo systemctl start postgresql
# or with Docker
docker-compose -f docker-compose.postgres.yml up -d postgres
```

**"Database does not exist"**
```bash
# Create the database
createdb ai_wellness_vision
# or run setup script
python setup_postgres.py
```

**"Authentication failed"**
```bash
# Reset PostgreSQL password
sudo -u postgres psql
ALTER USER postgres PASSWORD 'password';
```

**"Permission denied"**
```bash
# Grant database permissions
sudo -u postgres psql
GRANT ALL PRIVILEGES ON DATABASE ai_wellness_vision TO postgres;
```

### Dependency Issues
```bash
# Install missing dependencies
pip install -r requirements.txt

# Or install individually
pip install asyncpg bcrypt fastapi uvicorn python-jose[cryptography] passlib[bcrypt]
```

## 📊 Testing Results

After running the test scripts, you should see:

```
🚀 Starting PostgreSQL Authentication Tests
============================================================
✅ Health check passed - Database: postgresql
✅ Registration successful
✅ Login successful
✅ User info retrieved
✅ Chat endpoint working
✅ Conversations endpoint working
✅ Logout successful
✅ Invalid token properly rejected
✅ Admin login successful

📊 TEST SUMMARY
============================================================
✅ PASS Health Check
✅ PASS User Registration
✅ PASS User Login
✅ PASS Get User Info
✅ PASS Protected Endpoints
✅ PASS User Logout
✅ PASS Invalid Token Rejection
✅ PASS Admin Login

Overall: 8/8 tests passed
🎉 All PostgreSQL authentication tests passed!
```

## 🔄 Development Workflow

1. **Start Development:**
   ```bash
   python start_postgres_server.py
   ```

2. **Make Changes:**
   - Edit your code
   - Server auto-reloads with changes

3. **Test Changes:**
   ```bash
   python test_postgres_auth.py
   ```

4. **Flutter Development:**
   ```bash
   cd flutter_app
   flutter run
   ```

## 📱 Flutter Integration Examples

### Authentication Service
```dart
class AuthService {
  final Dio _dio = Dio();
  static const String baseUrl = 'http://localhost:8000';

  Future<AuthResponse> register({
    required String email,
    required String password,
    String? firstName,
    String? lastName,
  }) async {
    final response = await _dio.post(
      '$baseUrl/auth/register',
      data: {
        'email': email,
        'password': password,
        'firstName': firstName,
        'lastName': lastName,
      },
    );
    return AuthResponse.fromJson(response.data);
  }

  Future<AuthResponse> login({
    required String email,
    required String password,
  }) async {
    final response = await _dio.post(
      '$baseUrl/auth/login',
      data: {
        'email': email,
        'password': password,
      },
    );
    return AuthResponse.fromJson(response.data);
  }
}
```

### Chat Service
```dart
class ChatService {
  final Dio _dio = Dio();
  static const String baseUrl = 'http://localhost:8000';

  Future<ChatResponse> sendMessage({
    required String message,
    String mode = 'general',
    required String token,
  }) async {
    _dio.options.headers['Authorization'] = 'Bearer $token';
    
    final response = await _dio.post(
      '$baseUrl/chat/message',
      data: {
        'message': message,
        'mode': mode,
      },
    );
    return ChatResponse.fromJson(response.data);
  }
}
```

### Image Analysis Service
```dart
class ImageAnalysisService {
  final Dio _dio = Dio();
  static const String baseUrl = 'http://localhost:8000';

  Future<AnalysisResponse> analyzeImage({
    required File imageFile,
    String analysisType = 'general',
    required String token,
  }) async {
    _dio.options.headers['Authorization'] = 'Bearer $token';
    
    final formData = FormData.fromMap({
      'file': await MultipartFile.fromFile(imageFile.path),
      'analysis_type': analysisType,
    });

    final response = await _dio.post(
      '$baseUrl/image/analyze',
      data: formData,
    );
    return AnalysisResponse.fromJson(response.data);
  }
}
```

## 🎯 Production Deployment

### Environment Variables
```env
DATABASE_URL=postgresql://username:password@host:5432/database
SECRET_KEY=your-production-secret-key
ENVIRONMENT=production
DEBUG=false
```

### Docker Production
```bash
# Build production image
docker build -t ai-wellness-api .

# Run with production database
docker run -e DATABASE_URL=postgresql://... ai-wellness-api
```

### Kubernetes Deployment
```bash
# Apply Kubernetes manifests
kubectl apply -f k8s/
```

## 📚 API Documentation

### Authentication Endpoints
- `POST /auth/register` - Register new user
- `POST /auth/login` - Login user
- `GET /auth/me` - Get current user info
- `POST /auth/logout` - Logout user

### Chat Endpoints
- `POST /chat/message` - Send chat message
- `GET /chat/conversations` - Get user conversations

### Image Analysis Endpoints
- `POST /image/analyze` - Analyze uploaded image
- `GET /image/history` - Get analysis history

### Voice Endpoints
- `POST /voice/text-to-speech` - Convert text to speech
- `POST /voice/speech-to-text` - Convert speech to text

## 🔐 Security Features

- **Password Hashing:** bcrypt with salt
- **JWT Tokens:** Secure authentication
- **Session Management:** Database-backed sessions
- **Rate Limiting:** Protection against brute force
- **CORS:** Configurable cross-origin requests
- **Input Validation:** Pydantic model validation

## 🎉 You're Ready!

Your AI Wellness Vision app with PostgreSQL authentication is now running! 

### Next Steps:
1. ✅ Test all endpoints with the provided scripts
2. ✅ Configure your Flutter app to use the API
3. ✅ Customize the AI responses and analysis logic
4. ✅ Deploy to production when ready

### Support:
- 📖 Full documentation: `POSTGRESQL_SETUP_GUIDE.md`
- 🧪 Test scripts: `test_postgres_auth.py`
- 🐳 Docker setup: `docker-compose.postgres.yml`
- 🔧 Manual setup: `setup_postgres.py`

Happy coding! 🚀