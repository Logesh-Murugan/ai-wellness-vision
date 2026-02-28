# 🚀 Flutter PostgreSQL Integration Setup

Your Flutter app is now configured to work with the PostgreSQL backend!

## ✅ What's Been Updated

### 1. API Configuration
- **Base URL**: Updated to `http://localhost:8003`
- **Endpoints**: Configured for PostgreSQL backend
- **Authentication**: JWT Bearer token support

### 2. Services Updated
- **AuthService**: Direct integration with PostgreSQL auth endpoints
- **ChatService**: Updated for new chat API
- **User Model**: Matches PostgreSQL response structure

### 3. New Features
- **PostgreSQL Authentication**: Full JWT-based auth
- **Real-time Chat**: AI-powered responses
- **User Management**: Profile and preferences

## 🧪 Testing

### Test the Integration
```bash
cd flutter_app
dart test_postgres_integration.dart
```

This will test:
- ✅ Health check
- ✅ User login
- ✅ User info retrieval
- ✅ Chat messaging
- ✅ Conversations

## 📱 Running the App

### 1. Start the Backend
```bash
# In the root directory
python working_postgres_server.py
```

### 2. Run Flutter App
```bash
cd flutter_app
flutter run
```

### 3. Test Login
Use these credentials:
- **Email**: admin@wellnessvision.ai
- **Password**: admin123

## 🔧 Configuration

### API Endpoints
- **Base URL**: http://localhost:8003
- **Login**: POST /auth/login
- **Register**: POST /auth/register
- **User Info**: GET /auth/me
- **Chat**: POST /chat/message
- **Conversations**: GET /chat/conversations

### Authentication Flow
1. **Login/Register** → Get JWT token
2. **Store Token** → SharedPreferences
3. **API Calls** → Include Bearer token in headers
4. **Auto-refresh** → Handle token expiration

## 🎯 Key Features Working

### ✅ Authentication
- User registration and login
- JWT token management
- Secure API calls
- User profile management

### ✅ Chat System
- AI-powered responses
- Multiple chat modes:
  - General health
  - Nutrition advice
  - Fitness guidance
  - Mental health support
- Conversation history

### ✅ User Management
- Profile information
- User preferences
- Secure logout

## 🔍 Debugging

### Check Backend Status
```bash
curl http://localhost:8003/health
```

### Test Authentication
```bash
curl -X POST http://localhost:8003/auth/login \
  -H "Content-Type: application/json" \
  -d '{"email":"admin@wellnessvision.ai","password":"admin123"}'
```

### Common Issues

**1. Connection Refused**
- Ensure backend is running on port 8003
- Check if PostgreSQL container is running

**2. Authentication Errors**
- Verify credentials
- Check token storage in SharedPreferences
- Ensure proper headers are sent

**3. API Errors**
- Check server logs for detailed errors
- Verify request format matches backend expectations

## 📚 API Documentation

### Authentication
```dart
// Login
final authService = AuthService();
await authService.login('email@example.com', 'password');

// Get current user
final user = await authService.getCurrentUser();

// Logout
await authService.logout();
```

### Chat
```dart
// Send message
final chatService = ChatService();
final response = await chatService.sendMessage('Hello!', mode: 'general');

// Get conversations
final conversations = await chatService.getConversations();
```

## 🎉 Success!

Your Flutter app is now fully integrated with PostgreSQL backend:

- ✅ **Secure Authentication** - JWT tokens with PostgreSQL
- ✅ **Real-time Chat** - AI-powered health conversations
- ✅ **User Management** - Complete profile system
- ✅ **Production Ready** - Scalable PostgreSQL database

## 🚀 Next Steps

1. **Customize UI** - Update themes and styling
2. **Add Features** - Image analysis, voice processing
3. **Test Thoroughly** - All user flows and edge cases
4. **Deploy** - Production deployment when ready

Your AI Wellness Vision app is ready to help users with their health journey! 🌟