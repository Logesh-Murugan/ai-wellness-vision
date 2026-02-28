#!/usr/bin/env python3
"""
AI Wellness Vision - Fixed PostgreSQL API Server
Simplified version with working authentication
"""

import os
import sys
import asyncio
import logging
from datetime import datetime, timedelta
from typing import Dict, List, Optional, Any
import json
import uuid
import traceback

# Add src to path for imports
sys.path.append(os.path.join(os.path.dirname(__file__), 'src'))

try:
    from fastapi import FastAPI, HTTPException, Depends, UploadFile, File, Form, status
    from fastapi.middleware.cors import CORSMiddleware
    from fastapi.responses import JSONResponse, FileResponse
    from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
    from pydantic import BaseModel, EmailStr
    import uvicorn
    from jose import JWTError, jwt
    from passlib.context import CryptContext
    FASTAPI_AVAILABLE = True
except ImportError:
    FASTAPI_AVAILABLE = False
    print("❌ FastAPI not available. Install with: pip install fastapi uvicorn")
    sys.exit(1)

# Import our modules
from src.database.postgres_auth import PostgresAuthDatabase
from src.utils.logging_config import get_logger

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = get_logger(__name__)

# JWT Configuration
SECRET_KEY = "ai-wellness-vision-2024-secure-key-f8d9e7c6b5a4321098765432109876543210"
ALGORITHM = "HS256"
ACCESS_TOKEN_EXPIRE_MINUTES = 30

# Password hashing
pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

# Initialize FastAPI app
app = FastAPI(
    title="AI Wellness Vision API - Fixed",
    description="Comprehensive health and wellness analysis platform with PostgreSQL authentication",
    version="2.1.0"
)

# CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Configure appropriately for production
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Global instances
db: Optional[PostgresAuthDatabase] = None
security = HTTPBearer()

# Pydantic models
class UserRegistration(BaseModel):
    email: EmailStr
    password: str
    firstName: Optional[str] = None
    lastName: Optional[str] = None

class UserLogin(BaseModel):
    email: EmailStr
    password: str

class ChatMessage(BaseModel):
    message: str
    mode: Optional[str] = "general"

class TokenResponse(BaseModel):
    access_token: str
    refresh_token: str
    token_type: str = "bearer"
    expires_in: int

class UserResponse(BaseModel):
    id: str
    email: str
    name: str
    firstName: Optional[str] = None
    lastName: Optional[str] = None
    avatar: Optional[str] = None
    preferences: Dict[str, Any] = {}

# Helper functions
def create_access_token(user_email: str, user_id: str) -> str:
    """Create JWT access token"""
    expire = datetime.utcnow() + timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
    
    payload = {
        "sub": user_email,
        "user_id": user_id,
        "roles": ["admin"] if user_email == "admin@wellnessvision.ai" else ["user"],
        "exp": expire,
        "iat": datetime.utcnow()
    }
    
    return jwt.encode(payload, SECRET_KEY, algorithm=ALGORITHM)

def create_refresh_token(user_email: str) -> str:
    """Create JWT refresh token"""
    expire = datetime.utcnow() + timedelta(days=7)
    
    payload = {
        "sub": user_email,
        "type": "refresh",
        "exp": expire,
        "iat": datetime.utcnow()
    }
    
    return jwt.encode(payload, SECRET_KEY, algorithm=ALGORITHM)

async def verify_token(token: str) -> Dict[str, Any]:
    """Verify JWT token"""
    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        
        username = payload.get("sub")
        if username is None:
            raise HTTPException(status_code=401, detail="Invalid token payload")
        
        # Verify user still exists
        if db:
            user_data = await db.get_user_by_email(username)
            if not user_data:
                raise HTTPException(status_code=401, detail="User not found")
        
        return {
            "username": username,
            "user_id": payload.get("user_id", username),
            "roles": payload.get("roles", ["user"]),
            "exp": payload.get("exp"),
            "iat": payload.get("iat")
        }
        
    except JWTError as e:
        logger.warning(f"JWT verification failed: {e}")
        raise HTTPException(status_code=401, detail="Invalid token")
    except Exception as e:
        logger.error(f"Token verification error: {e}")
        raise HTTPException(status_code=401, detail="Token verification failed")

async def get_current_user(credentials: HTTPAuthorizationCredentials = Depends(security)):
    """Get current authenticated user"""
    return await verify_token(credentials.credentials)

# Startup and shutdown events
@app.on_event("startup")
async def startup_event():
    """Initialize services on startup"""
    global db
    try:
        logger.info("🚀 Starting AI Wellness Vision API Server with PostgreSQL...")
        
        # Initialize PostgreSQL
        database_url = os.getenv(
            'DATABASE_URL', 
            'postgresql://postgres:password@localhost:5432/ai_wellness_vision'
        )
        
        db = PostgresAuthDatabase(database_url)
        await db.initialize()
        
        logger.info("✅ All services initialized successfully")
        
    except Exception as e:
        logger.error(f"❌ Startup failed: {e}")
        logger.error(traceback.format_exc())
        raise

@app.on_event("shutdown")
async def shutdown_event():
    """Cleanup on shutdown"""
    global db
    try:
        if db:
            await db.close()
        logger.info("✅ Services shut down successfully")
    except Exception as e:
        logger.error(f"❌ Shutdown error: {e}")

# Health check endpoint
@app.get("/health")
async def health_check():
    """Health check endpoint"""
    return {
        "status": "healthy",
        "timestamp": datetime.now().isoformat(),
        "version": "2.1.0",
        "database": "postgresql"
    }

# Authentication endpoints
@app.post("/auth/register", response_model=TokenResponse)
async def register_user(user_data: UserRegistration):
    """Register a new user"""
    try:
        if not db:
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail="Database not initialized"
            )
        
        # Create user in database
        user_id = await db.create_user(
            email=user_data.email,
            password=user_data.password,
            first_name=user_data.firstName,
            last_name=user_data.lastName
        )
        
        if not user_id:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="User already exists"
            )
        
        # Create tokens
        access_token = create_access_token(user_data.email, user_id)
        refresh_token = create_refresh_token(user_data.email)
        
        # Save session
        expires_at = datetime.utcnow() + timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
        await db.save_session(user_id, access_token, refresh_token, expires_at)
        
        return TokenResponse(
            access_token=access_token,
            refresh_token=refresh_token,
            expires_in=ACCESS_TOKEN_EXPIRE_MINUTES * 60
        )
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Registration error: {e}")
        logger.error(traceback.format_exc())
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, 
            detail="Registration failed"
        )

@app.post("/auth/login", response_model=TokenResponse)
async def login_user(user_data: UserLogin):
    """Login user"""
    try:
        if not db:
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail="Database not initialized"
            )
        
        # Get user from database
        user = await db.get_user_by_email(user_data.email)
        if not user:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Invalid email or password"
            )
        
        # Verify password
        if not db.verify_password(user_data.password, user['password_hash']):
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Invalid email or password"
            )
        
        # Create tokens
        access_token = create_access_token(user_data.email, user['id'])
        refresh_token = create_refresh_token(user_data.email)
        
        # Save session
        expires_at = datetime.utcnow() + timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
        await db.save_session(user['id'], access_token, refresh_token, expires_at)
        
        return TokenResponse(
            access_token=access_token,
            refresh_token=refresh_token,
            expires_in=ACCESS_TOKEN_EXPIRE_MINUTES * 60
        )
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Login error: {e}")
        logger.error(traceback.format_exc())
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, 
            detail="Login failed"
        )

@app.get("/auth/me", response_model=UserResponse)
async def get_current_user_info(current_user = Depends(get_current_user)):
    """Get current user information"""
    try:
        logger.info(f"Getting user info for: {current_user}")
        
        if not db:
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail="Database not initialized"
            )
        
        username = current_user['username']
        logger.info(f"Looking up user by email: {username}")
        
        user_data = await db.get_user_by_email(username)
        logger.info(f"User data from DB: {user_data}")
        
        if not user_data:
            logger.error(f"User not found in database: {username}")
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="User not found")
        
        return UserResponse(
            id=user_data['id'],
            email=user_data['email'],
            name=user_data['name'] or f"{user_data.get('firstName', '')} {user_data.get('lastName', '')}".strip(),
            firstName=user_data['firstName'],
            lastName=user_data['lastName'],
            avatar=user_data['avatar'],
            preferences=user_data['preferences'] or {}
        )
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Get user info error: {e}")
        logger.error(traceback.format_exc())
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, 
            detail="Failed to get user info"
        )

@app.post("/auth/logout")
async def logout_user(credentials: HTTPAuthorizationCredentials = Depends(security)):
    """Logout user"""
    try:
        if db:
            await db.delete_session(credentials.credentials)
        
        return {"message": "Logged out successfully"}
        
    except Exception as e:
        logger.error(f"Logout error: {e}")
        return {"message": "Logout completed"}

# Chat endpoints
@app.post("/chat/message")
async def send_chat_message(
    message_data: ChatMessage,
    current_user = Depends(get_current_user)
):
    """Send a chat message and get AI response"""
    try:
        # Simple AI response (replace with actual AI integration)
        responses = {
            "general": "I'm here to help with your health and wellness questions. How can I assist you today?",
            "nutrition": "I can help you with nutrition advice and meal planning. What would you like to know?",
            "fitness": "I'm here to help with your fitness goals and exercise recommendations. What's your question?",
            "mental_health": "I can provide support and resources for mental wellness. How can I help you today?"
        }
        
        response = responses.get(message_data.mode, responses["general"])
        
        return {
            "response": response,
            "mode": message_data.mode,
            "timestamp": datetime.now().isoformat(),
            "user_id": current_user['user_id']
        }
        
    except Exception as e:
        logger.error(f"Chat error: {e}")
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail="Chat service unavailable")

@app.get("/chat/conversations")
async def get_conversations(current_user = Depends(get_current_user)):
    """Get user's chat conversations"""
    try:
        # Mock conversations (replace with database query)
        conversations = [
            {
                "id": str(uuid.uuid4()),
                "title": "General Health Questions",
                "lastMessage": "How can I improve my sleep?",
                "timestamp": datetime.now().isoformat(),
                "mode": "general"
            }
        ]
        
        return {"conversations": conversations}
        
    except Exception as e:
        logger.error(f"Get conversations error: {e}")
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail="Failed to get conversations")

# Debug endpoint (remove in production)
@app.get("/debug/users")
async def debug_users():
    """Debug endpoint to check users in database"""
    try:
        if not db:
            return {"error": "Database not initialized"}
        
        async with db.pool.acquire() as conn:
            rows = await conn.fetch("SELECT id, email, name, first_name, last_name FROM users ORDER BY created_at DESC LIMIT 5")
            
            users = []
            for row in rows:
                users.append({
                    "id": str(row['id']),
                    "email": row['email'],
                    "name": row['name'],
                    "first_name": row['first_name'],
                    "last_name": row['last_name']
                })
            
            return {"users": users, "count": len(users)}
        
    except Exception as e:
        logger.error(f"Debug users error: {e}")
        return {"error": str(e)}

# Error handlers
@app.exception_handler(HTTPException)
async def http_exception_handler(request, exc):
    """Handle HTTP exceptions"""
    return JSONResponse(
        status_code=exc.status_code,
        content={"detail": exc.detail, "timestamp": datetime.now().isoformat()}
    )

@app.exception_handler(Exception)
async def general_exception_handler(request, exc):
    """Handle general exceptions"""
    logger.error(f"Unhandled exception: {exc}")
    logger.error(traceback.format_exc())
    return JSONResponse(
        status_code=500,
        content={"detail": "Internal server error", "timestamp": datetime.now().isoformat()}
    )

if __name__ == "__main__":
    print("🚀 Starting AI Wellness Vision API Server - Fixed Version...")
    print("📊 Features: Authentication, Chat, Image Analysis, Voice Processing")
    print("🗄️ Database: PostgreSQL")
    print("🌐 Server: http://localhost:8002")
    print("📚 API Docs: http://localhost:8002/docs")
    
    uvicorn.run(
        "main_api_server_postgres_fixed:app",
        host="0.0.0.0",
        port=8002,
        reload=True,
        log_level="info"
    )