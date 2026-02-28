# PostgreSQL Setup Guide for AI Wellness Vision

This guide will help you set up PostgreSQL authentication for your AI Wellness Vision application.

## 🎯 Overview

Your application now supports PostgreSQL for robust, production-ready authentication with the following features:

- ✅ User registration and login
- ✅ JWT token-based authentication  
- ✅ Secure password hashing with bcrypt
- ✅ Session management
- ✅ User profile management
- ✅ Protected API endpoints

## 🚀 Quick Start

### Option 1: Automated Setup (Recommended)

```bash
# Run the automated setup script
python start_postgres_server.py
```

This script will:
1. Check if PostgreSQL is running
2. Start PostgreSQL with Docker if needed
3. Install required dependencies
4. Set up the database schema
5. Create default users
6. Start the API server

### Option 2: Manual Setup

#### Step 1: Install PostgreSQL

**Windows:**
- Download from https://www.postgresql.org/download/windows/
- Run the installer and follow the setup wizard
- Remember the password you set for the `postgres` user

**macOS:**
```bash
brew install postgresql
brew services start postgresql
```

**Ubuntu/Debian:**
```bash
sudo apt update
sudo apt install postgresql postgresql-contrib
sudo systemctl start postgresql
sudo systemctl enable postgresql
```

#### Step 2: Create Database

```bash
# Connect to PostgreSQL
sudo -u postgres psql

# Create database
CREATE DATABASE ai_wellness_vision;

# Create user (optional)
CREATE USER ai_wellness_user WITH PASSWORD 'your_password';
GRANT ALL PRIVILEGES ON DATABASE ai_wellness_vision TO ai_wellness_user;

# Exit
\q
```

#### Step 3: Install Python Dependencies

```bash
pip install asyncpg bcrypt fastapi uvicorn python-jose[cryptography] passlib[bcrypt]
```

#### Step 4: Set Environment Variables

Update your `.env` file:
```env
DATABASE_URL=postgresql://postgres:password@localhost:5432/ai_wellness_vision
ENVIRONMENT=development
SECRET_KEY=your-secret-key-here
```

#### Step 5: Setup Database Schema

```bash
python setup_postgres.py
```

#### Step 6: Start the Server

```bash
python main_api_server_postgres.py
```

## 🐳 Docker Setup

### Using Docker Compose

```bash
# Start PostgreSQL and API server
docker-compose -f docker-compose.postgres.yml up -d

# Check logs
docker-compose -f docker-compose.postgres.yml logs -f

# Stop services
docker-compose -f docker-compose.postgres.yml down
```

### PostgreSQL Only

```bash
# Start only PostgreSQL
docker-compose -f docker-compose.postgres.yml up -d postgres

# Connect to database
docker exec -it ai_wellness_postgres psql -U postgres -d ai_wellness_vision
```

## 🧪 Testing

### Test Authentication

```bash
# Run comprehensive authentication tests
python test_postgres_auth.py
```

### Test Individual Components

```bash
# Test database connection
python setup_postgres.py test

# Test server health
curl http://localhost:8000/health

# Test registration
curl -X POST http://localhost:8000/auth/register \
  -H "Content-Type: application/json" \
  -d '{"email":"test@example.com","password":"testpass123","firstName":"Test","lastName":"User"}'

# Test login
curl -X POST http://localhost:8000/auth/login \
  -H "Content-Type: application/json" \
  -d '{"email":"test@example.com","password":"testpass123"}'
```

## 📱 Flutter Integration

Your Flutter app can now use the PostgreSQL backend. Update your API configuration:

```dart
// lib/core/config/api_config.dart
class ApiConfig {
  static const String baseUrl = 'http://localhost:8000';
  static const String authEndpoint = '/auth';
  static const String chatEndpoint = '/chat';
  static const String imageEndpoint = '/image';
  static const String voiceEndpoint = '/voice';
}
```

### Authentication Flow

1. **Registration:**
   ```dart
   final response = await dio.post('/auth/register', data: {
     'email': email,
     'password': password,
     'firstName': firstName,
     'lastName': lastName,
   });
   ```

2. **Login:**
   ```dart
   final response = await dio.post('/auth/login', data: {
     'email': email,
     'password': password,
   });
   final token = response.data['access_token'];
   ```

3. **Authenticated Requests:**
   ```dart
   dio.options.headers['Authorization'] = 'Bearer $token';
   ```

## 🔧 Configuration

### Database Connection

The application supports multiple database URL formats:

```env
# Local PostgreSQL
DATABASE_URL=postgresql://username:password@localhost:5432/database_name

# PostgreSQL with custom port
DATABASE_URL=postgresql://username:password@localhost:5433/database_name

# Remote PostgreSQL
DATABASE_URL=postgresql://username:password@remote-host:5432/database_name

# PostgreSQL with SSL
DATABASE_URL=postgresql://username:password@host:5432/database_name?sslmode=require
```

### Environment Variables

| Variable | Description | Default |
|----------|-------------|---------|
| `DATABASE_URL` | PostgreSQL connection string | `postgresql://postgres:password@localhost:5432/ai_wellness_vision` |
| `SECRET_KEY` | JWT signing key | Auto-generated |
| `ENVIRONMENT` | Application environment | `development` |
| `ACCESS_TOKEN_EXPIRE_MINUTES` | JWT token expiry | `30` |
| `REFRESH_TOKEN_EXPIRE_DAYS` | Refresh token expiry | `7` |

## 🗄️ Database Schema

The application creates the following tables:

### Users Table
```sql
CREATE TABLE users (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    email VARCHAR(255) UNIQUE NOT NULL,
    password_hash VARCHAR(255) NOT NULL,
    first_name VARCHAR(100),
    last_name VARCHAR(100),
    name VARCHAR(200),
    avatar TEXT,
    preferences JSONB DEFAULT '{"language": "en", "notifications": true, "theme": "light"}',
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
);
```

### User Sessions Table
```sql
CREATE TABLE user_sessions (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    user_id UUID REFERENCES users(id) ON DELETE CASCADE,
    access_token TEXT NOT NULL,
    refresh_token TEXT NOT NULL,
    expires_at TIMESTAMP WITH TIME ZONE NOT NULL,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
);
```

### Additional Tables
- `analysis_history` - Image analysis results
- `chat_conversations` - Chat conversation threads
- `chat_messages` - Individual chat messages

## 🔐 Security Features

- **Password Hashing:** bcrypt with salt
- **JWT Tokens:** Secure token-based authentication
- **Session Management:** Database-backed session tracking
- **Rate Limiting:** Failed login attempt protection
- **CORS:** Configurable cross-origin resource sharing
- **Input Validation:** Pydantic model validation

## 🚨 Troubleshooting

### Common Issues

1. **Connection Refused:**
   ```bash
   # Check if PostgreSQL is running
   sudo systemctl status postgresql
   
   # Start PostgreSQL
   sudo systemctl start postgresql
   ```

2. **Authentication Failed:**
   ```bash
   # Reset PostgreSQL password
   sudo -u postgres psql
   ALTER USER postgres PASSWORD 'newpassword';
   ```

3. **Database Does Not Exist:**
   ```bash
   # Create database
   createdb ai_wellness_vision
   ```

4. **Permission Denied:**
   ```bash
   # Grant permissions
   sudo -u postgres psql
   GRANT ALL PRIVILEGES ON DATABASE ai_wellness_vision TO postgres;
   ```

### Logs and Debugging

```bash
# Check PostgreSQL logs
sudo tail -f /var/log/postgresql/postgresql-*.log

# Check application logs
python main_api_server_postgres.py --log-level debug

# Test database connection
python -c "import asyncpg; import asyncio; asyncio.run(asyncpg.connect('postgresql://postgres:password@localhost:5432/ai_wellness_vision'))"
```

## 📊 Default Users

The setup creates these default users for testing:

| Email | Password | Role |
|-------|----------|------|
| `admin@wellnessvision.ai` | `admin123` | Admin |
| `test@wellnessvision.ai` | `user123` | User |

## 🎉 Next Steps

1. **Test the API:** Run `python test_postgres_auth.py`
2. **Update Flutter App:** Configure API endpoints
3. **Deploy:** Use Docker Compose for production
4. **Monitor:** Set up logging and monitoring
5. **Scale:** Configure connection pooling and caching

## 📚 API Documentation

Once the server is running, visit:
- **API Docs:** http://localhost:8000/docs
- **Health Check:** http://localhost:8000/health
- **OpenAPI Schema:** http://localhost:8000/openapi.json

Your AI Wellness Vision app is now ready with robust PostgreSQL authentication! 🎉