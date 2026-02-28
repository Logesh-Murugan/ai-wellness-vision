#!/usr/bin/env python3
"""
AI Wellness Vision - Main API Server with PostgreSQL Authentication
Enhanced backend server with comprehensive health and wellness features
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
    FASTAPI_AVAILABLE = True
except ImportError:
    FASTAPI_AVAILABLE = False
    print("❌ FastAPI not available. Install with: pip install fastapi uvicorn")
    sys.exit(1)

# Import our modules
from src.database.postgres_auth import PostgresAuthDatabase, init_postgres_auth, close_postgres_auth
from src.api.auth import AuthManager, get_current_user, AuthenticationError
from src.utils.logging_config import get_logger

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = get_logger(__name__)

# Initialize FastAPI app
app = FastAPI(
    title="AI Wellness Vision API",
    description="Comprehensive health and wellness analysis platform with PostgreSQL authentication",
    version="2.0.0"
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
auth_manager = AuthManager()
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

# Startup and shutdown events
@app.on_event("startup")
async def startup_event():
    """Initialize services on startup"""
    try:
        logger.info("🚀 Starting AI Wellness Vision API Server with PostgreSQL...")
        
        # Initialize PostgreSQL authentication
        await init_postgres_auth()
        await auth_manager.initialize()
        
        logger.info("✅ All services initialized successfully")
        
    except Exception as e:
        logger.error(f"❌ Startup failed: {e}")
        logger.error(traceback.format_exc())
        raise

@app.on_event("shutdown")
async def shutdown_event():
    """Cleanup on shutdown"""
    try:
        await close_postgres_auth()
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
        "version": "2.0.0",
        "database": "postgresql"
    }

# Authentication endpoints
@app.post("/auth/register", response_model=TokenResponse)
async def register_user(user_data: UserRegistration):
    """Register a new user"""
    try:
        db = auth_manager.db
        if not db:
            await auth_manager.initialize()
            db = auth_manager.db
        
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
        
        # Authenticate the newly created user
        user = await auth_manager.authenticate_user(user_data.email, user_data.password)
        
        # Create tokens
        access_token = auth_manager.create_access_token(user)
        refresh_token = auth_manager.create_refresh_token(user)
        
        # Save session
        expires_at = datetime.utcnow() + timedelta(minutes=30)
        await db.save_session(user_id, access_token, refresh_token, expires_at)
        
        return TokenResponse(
            access_token=access_token,
            refresh_token=refresh_token,
            expires_in=1800  # 30 minutes
        )
        
    except AuthenticationError as e:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(e))
    except Exception as e:
        logger.error(f"Registration error: {e}")
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail="Registration failed")

@app.post("/auth/login", response_model=TokenResponse)
async def login_user(user_data: UserLogin):
    """Login user"""
    try:
        # Authenticate user
        user = await auth_manager.authenticate_user(user_data.email, user_data.password)
        
        # Create tokens
        access_token = auth_manager.create_access_token(user)
        refresh_token = auth_manager.create_refresh_token(user)
        
        # Save session
        db = auth_manager.db
        user_db_data = await db.get_user_by_email(user_data.email)
        expires_at = datetime.utcnow() + timedelta(minutes=30)
        await db.save_session(user_db_data['id'], access_token, refresh_token, expires_at)
        
        return TokenResponse(
            access_token=access_token,
            refresh_token=refresh_token,
            expires_in=1800  # 30 minutes
        )
        
    except AuthenticationError as e:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail=str(e))
    except Exception as e:
        logger.error(f"Login error: {e}")
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail="Login failed")

@app.get("/auth/me", response_model=UserResponse)
async def get_current_user_info(current_user = Depends(get_current_user)):
    """Get current user information"""
    try:
        db = auth_manager.db
        user_data = await db.get_user_by_email(current_user.username)
        
        if not user_data:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="User not found")
        
        return UserResponse(
            id=user_data['id'],
            email=user_data['email'],
            name=user_data['name'],
            firstName=user_data['firstName'],
            lastName=user_data['lastName'],
            avatar=user_data['avatar'],
            preferences=user_data['preferences']
        )
        
    except Exception as e:
        logger.error(f"Get user info error: {e}")
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail="Failed to get user info")

@app.post("/auth/logout")
async def logout_user(credentials: HTTPAuthorizationCredentials = Depends(security)):
    """Logout user"""
    try:
        db = auth_manager.db
        await db.delete_session(credentials.credentials)
        auth_manager.revoke_token(credentials.credentials)
        
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
            "user_id": current_user.user_id
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

# Image analysis endpoints
@app.post("/image/analyze")
async def analyze_image(
    file: UploadFile = File(...),
    analysis_type: str = Form("general"),
    current_user = Depends(get_current_user)
):
    """Analyze uploaded image"""
    try:
        # Save uploaded file
        upload_dir = "uploads"
        os.makedirs(upload_dir, exist_ok=True)
        
        file_path = os.path.join(upload_dir, f"{uuid.uuid4()}_{file.filename}")
        
        with open(file_path, "wb") as buffer:
            content = await file.read()
            buffer.write(content)
        
        # Mock analysis result (replace with actual AI analysis)
        analysis_results = {
            "skin": "Healthy skin detected with good hydration levels and no visible concerns.",
            "general": "Image analysis completed. No immediate health concerns detected.",
            "nutrition": "Food items identified. Nutritional analysis suggests a balanced meal.",
            "fitness": "Exercise form analysis completed. Good posture and technique observed."
        }
        
        result = analysis_results.get(analysis_type, analysis_results["general"])
        
        return {
            "analysis": result,
            "confidence": 0.85,
            "analysis_type": analysis_type,
            "timestamp": datetime.now().isoformat(),
            "image_path": file_path,
            "recommendations": [
                "Continue maintaining good health habits",
                "Regular check-ups are recommended",
                "Stay hydrated and get adequate sleep"
            ]
        }
        
    except Exception as e:
        logger.error(f"Image analysis error: {e}")
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail="Image analysis failed")

@app.get("/image/history")
async def get_analysis_history(current_user = Depends(get_current_user)):
    """Get user's image analysis history"""
    try:
        # Mock history (replace with database query)
        history = [
            {
                "id": str(uuid.uuid4()),
                "analysis_type": "skin",
                "result": "Healthy skin detected",
                "confidence": 0.85,
                "timestamp": datetime.now().isoformat(),
                "recommendations": ["Stay hydrated", "Use sunscreen"]
            }
        ]
        
        return {"history": history}
        
    except Exception as e:
        logger.error(f"Get history error: {e}")
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail="Failed to get history")

# Voice endpoints
@app.post("/voice/text-to-speech")
async def text_to_speech(
    text: str = Form(...),
    current_user = Depends(get_current_user)
):
    """Convert text to speech"""
    try:
        # Mock TTS (replace with actual TTS service)
        audio_filename = f"tts_{uuid.uuid4()}.mp3"
        audio_path = os.path.join("uploads", audio_filename)
        
        # Create a mock audio file (in real implementation, generate actual audio)
        os.makedirs("uploads", exist_ok=True)
        with open(audio_path, "w") as f:
            f.write("mock audio content")
        
        return {
            "audio_url": f"http://localhost:8000/audio/{audio_filename}",
            "text": text,
            "timestamp": datetime.now().isoformat()
        }
        
    except Exception as e:
        logger.error(f"TTS error: {e}")
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail="TTS service unavailable")

@app.post("/voice/speech-to-text")
async def speech_to_text(
    file: UploadFile = File(...),
    current_user = Depends(get_current_user)
):
    """Convert speech to text"""
    try:
        # Mock STT (replace with actual STT service)
        transcription = "I'm feeling stressed lately"
        
        return {
            "transcription": transcription,
            "confidence": 0.92,
            "timestamp": datetime.now().isoformat()
        }
        
    except Exception as e:
        logger.error(f"STT error: {e}")
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail="STT service unavailable")

# Audio file serving
@app.get("/audio/{filename}")
async def get_audio_file(filename: str):
    """Serve audio files"""
    try:
        file_path = os.path.join("uploads", filename)
        if os.path.exists(file_path):
            return FileResponse(file_path, media_type="audio/mpeg")
        else:
            raise HTTPException(status_code=404, detail="Audio file not found")
    except Exception as e:
        logger.error(f"Audio serve error: {e}")
        raise HTTPException(status_code=500, detail="Failed to serve audio file")

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
    print("🚀 Starting AI Wellness Vision API Server with PostgreSQL Authentication...")
    print("📊 Features: Authentication, Chat, Image Analysis, Voice Processing")
    print("🗄️ Database: PostgreSQL")
    print("🌐 Server: http://localhost:8000")
    print("📚 API Docs: http://localhost:8000/docs")
    
    uvicorn.run(
        "main_api_server_postgres:app",
        host="0.0.0.0",
        port=8000,
        reload=True,
        log_level="info"
    )