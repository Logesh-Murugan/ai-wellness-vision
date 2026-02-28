#!/usr/bin/env python3
"""
Working PostgreSQL server - Direct SQL approach
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
    from fastapi import FastAPI, HTTPException, Depends, status
    from fastapi.middleware.cors import CORSMiddleware
    from fastapi.responses import JSONResponse
    from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
    from pydantic import BaseModel, EmailStr
    import uvicorn
    from jose import JWTError, jwt
    from passlib.context import CryptContext
    import asyncpg
    import bcrypt
    FASTAPI_AVAILABLE = True
except ImportError:
    FASTAPI_AVAILABLE = False
    print("❌ Required libraries not available")
    sys.exit(1)

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# JWT Configuration
SECRET_KEY = "ai-wellness-vision-2024-secure-key-f8d9e7c6b5a4321098765432109876543210"
ALGORITHM = "HS256"
ACCESS_TOKEN_EXPIRE_MINUTES = 30

# Database URL
DATABASE_URL = os.getenv(
    'DATABASE_URL', 
    'postgresql://wellness_user:wellness_pass123@localhost:5432/ai_wellness_vision'
)

# Initialize FastAPI app
app = FastAPI(
    title="Working AI Wellness Vision API",
    description="Working PostgreSQL authentication",
    version="3.0.0"
)

# CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Global database pool
db_pool = None
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
def hash_password(password: str) -> str:
    """Hash password using bcrypt"""
    salt = bcrypt.gensalt()
    return bcrypt.hashpw(password.encode('utf-8'), salt).decode('utf-8')

def verify_password(password: str, hashed: str) -> bool:
    """Verify password against hash"""
    return bcrypt.checkpw(password.encode('utf-8'), hashed.encode('utf-8'))

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

# Database functions
async def get_user_by_email_direct(email: str) -> Optional[Dict[str, Any]]:
    """Get user by email using direct SQL"""
    try:
        async with db_pool.acquire() as conn:
            row = await conn.fetchrow('''
                SELECT id, email, password_hash, first_name, last_name, name, 
                       avatar, preferences, created_at, updated_at
                FROM users WHERE email = $1
            ''', email)
            
            if row:
                # Parse preferences JSON string to dict
                preferences = {}
                if row['preferences']:
                    try:
                        if isinstance(row['preferences'], str):
                            preferences = json.loads(row['preferences'])
                        else:
                            preferences = row['preferences']
                    except (json.JSONDecodeError, TypeError):
                        preferences = {}
                
                return {
                    'id': str(row['id']),
                    'email': row['email'],
                    'password_hash': row['password_hash'],
                    'firstName': row['first_name'],
                    'lastName': row['last_name'],
                    'name': row['name'],
                    'avatar': row['avatar'],
                    'preferences': preferences,
                    'created_at': row['created_at'].isoformat() if row['created_at'] else None,
                    'updated_at': row['updated_at'].isoformat() if row['updated_at'] else None
                }
            return None
            
    except Exception as e:
        logger.error(f"Failed to get user by email: {e}")
        return None

async def create_user_direct(email: str, password: str, first_name: str = None, last_name: str = None) -> Optional[str]:
    """Create user using direct SQL"""
    try:
        password_hash = hash_password(password)
        name = f"{first_name or ''} {last_name or ''}".strip() or email.split('@')[0].title()
        
        async with db_pool.acquire() as conn:
            user_id = await conn.fetchval('''
                INSERT INTO users (email, password_hash, first_name, last_name, name)
                VALUES ($1, $2, $3, $4, $5)
                RETURNING id
            ''', email, password_hash, first_name, last_name, name)
            
            logger.info(f"✅ User created: {email}")
            return str(user_id)
            
    except asyncpg.UniqueViolationError:
        logger.warning(f"User already exists: {email}")
        return None
    except Exception as e:
        logger.error(f"Failed to create user: {e}")
        return None

# Startup and shutdown events
@app.on_event("startup")
async def startup_event():
    """Initialize services on startup"""
    global db_pool
    try:
        logger.info("🚀 Starting Working PostgreSQL API Server...")
        
        # Initialize PostgreSQL connection pool
        db_pool = await asyncpg.create_pool(
            DATABASE_URL,
            min_size=5,
            max_size=20,
            command_timeout=60
        )
        
        logger.info("✅ PostgreSQL connection pool initialized")
        
    except Exception as e:
        logger.error(f"❌ Startup failed: {e}")
        logger.error(traceback.format_exc())
        raise

@app.on_event("shutdown")
async def shutdown_event():
    """Cleanup on shutdown"""
    global db_pool
    try:
        if db_pool:
            await db_pool.close()
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
        "version": "3.0.0",
        "database": "postgresql-direct"
    }

# Debug endpoint
@app.get("/debug/users")
async def debug_users():
    """Debug endpoint to check users in database"""
    try:
        async with db_pool.acquire() as conn:
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

# Authentication endpoints
@app.post("/auth/register", response_model=TokenResponse)
async def register_user(user_data: UserRegistration):
    """Register a new user"""
    try:
        # Create user in database
        user_id = await create_user_direct(
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
        # Get user from database
        user = await get_user_by_email_direct(user_data.email)
        if not user:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Invalid email or password"
            )
        
        # Verify password
        if not verify_password(user_data.password, user['password_hash']):
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Invalid email or password"
            )
        
        # Create tokens
        access_token = create_access_token(user_data.email, user['id'])
        refresh_token = create_refresh_token(user_data.email)
        
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
        logger.info(f"Getting user info for: {current_user['username']}")
        
        user_data = await get_user_by_email_direct(current_user['username'])
        logger.info(f"User data retrieved: {user_data}")
        
        if not user_data:
            logger.error(f"User not found in database: {current_user['username']}")
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="User not found")
        
        return UserResponse(
            id=user_data['id'],
            email=user_data['email'],
            name=user_data['name'] or f"{user_data.get('firstName', '')} {user_data.get('lastName', '')}".strip() or "Unknown User",
            firstName=user_data['firstName'],
            lastName=user_data['lastName'],
            avatar=user_data['avatar'],
            preferences=user_data['preferences']
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
    return {"message": "Logged out successfully"}

def generate_intelligent_response(user_message: str) -> str:
    """Generate intelligent health-focused responses"""
    message = user_message.lower()
    
    # Sleep-related questions
    if 'sleep' in message or 'insomnia' in message or 'tired' in message:
        if 'better' in message or 'improve' in message:
            return 'For better sleep, try these tips:\n• Maintain a consistent bedtime (even on weekends)\n• Avoid screens 1 hour before bed\n• Keep your room cool (60-67°F)\n• Try relaxation techniques like deep breathing\n• Avoid caffeine after 2 PM'
        elif 'how much' in message or 'hours' in message:
            return 'Most adults need 7-9 hours of sleep per night. Quality matters as much as quantity - deep, uninterrupted sleep is key for recovery and health.'
        else:
            return 'Sleep is crucial for your health! Good sleep helps with memory, immune function, and mood. What specific sleep issue are you facing?'
    
    # Diet and nutrition questions
    elif any(word in message for word in ['diet', 'food', 'eat', 'nutrition']):
        if 'weight' in message or 'lose' in message:
            return 'For healthy weight management:\n• Focus on whole foods: fruits, vegetables, lean proteins\n• Control portion sizes\n• Stay hydrated (8-10 glasses of water daily)\n• Eat slowly and mindfully\n• Include fiber-rich foods to feel full longer'
        elif 'healthy' in message or 'good' in message:
            return 'A healthy diet includes:\n• 5-9 servings of fruits and vegetables daily\n• Whole grains instead of refined carbs\n• Lean proteins (fish, chicken, beans, nuts)\n• Healthy fats (olive oil, avocados, nuts)\n• Limited processed foods and added sugars'
        elif 'breakfast' in message:
            return 'A healthy breakfast should include protein, fiber, and healthy fats. Try:\n• Greek yogurt with berries and nuts\n• Oatmeal with fruit and chia seeds\n• Eggs with whole grain toast and avocado\n• Smoothie with protein powder, spinach, and fruit'
        else:
            return 'Nutrition is the foundation of good health! A balanced diet provides energy, supports immune function, and helps prevent chronic diseases. What specific nutrition question do you have?'
    
    # Exercise and fitness questions
    elif any(word in message for word in ['exercise', 'workout', 'fitness', 'gym']):
        if 'beginner' in message or 'start' in message:
            return 'Starting your fitness journey? Great! Begin with:\n• 20-30 minutes of walking daily\n• 2-3 strength training sessions per week\n• Start slowly and gradually increase intensity\n• Focus on proper form over heavy weights\n• Listen to your body and rest when needed'
        elif 'home' in message or 'no gym' in message:
            return 'Effective home workouts:\n• Bodyweight exercises: push-ups, squats, lunges\n• Yoga or Pilates videos\n• Resistance bands for strength training\n• Dancing or online fitness classes\n• Stairs climbing for cardio'
        else:
            return 'Regular exercise is amazing for your health! It improves cardiovascular health, strengthens muscles, boosts mood, and increases energy. What type of exercise interests you most?'
    
    # Stress and mental health
    elif any(word in message for word in ['stress', 'anxiety', 'mental', 'mood']):
        if 'manage' in message or 'reduce' in message:
            return 'Stress management techniques:\n• Deep breathing exercises (4-7-8 technique)\n• Regular physical activity\n• Meditation or mindfulness (even 5 minutes daily)\n• Adequate sleep and nutrition\n• Social connections and support\n• Time in nature'
        else:
            return 'Mental health is just as important as physical health! Chronic stress can affect your immune system, sleep, and overall well-being. What\'s your main source of stress?'
    
    # Water and hydration
    elif 'water' in message or 'hydration' in message or 'drink' in message:
        return 'Staying hydrated is essential! Aim for:\n• 8-10 glasses of water daily (more if active)\n• Start your day with a glass of water\n• Drink before you feel thirsty\n• Include water-rich foods (fruits, vegetables)\n• Limit dehydrating drinks (alcohol, excessive caffeine)'
    
    # Immune system
    elif 'immune' in message or 'sick' in message or 'cold' in message:
        return 'Boost your immune system:\n• Get adequate sleep (7-9 hours)\n• Eat colorful fruits and vegetables\n• Stay physically active\n• Manage stress levels\n• Wash hands frequently\n• Stay hydrated\n• Consider probiotics for gut health'
    
    # Greetings
    elif any(word in message for word in ['hello', 'hi', 'hey']):
        return 'Hello! I\'m your AI Health Assistant. I\'m here to help with questions about nutrition, exercise, sleep, stress management, and general wellness. What would you like to know about today?'
    
    elif 'thank' in message:
        return 'You\'re very welcome! I\'m glad I could help. Remember, small consistent changes lead to big health improvements over time. Feel free to ask me anything else!'
    
    # Default response
    else:
        responses = [
            'That\'s an interesting question! I specialize in health and wellness topics like nutrition, exercise, sleep, and stress management. How can I help you with your health today?',
            'I\'m here to help with health and wellness questions! You can ask me about healthy eating, exercise routines, sleep improvement, stress management, or general wellness tips.',
            'I focus on health and wellness guidance. Feel free to ask me about nutrition, fitness, mental health, sleep, or any other wellness topics you\'re curious about!',
        ]
        return responses[hash(user_message) % len(responses)]

# Chat endpoints
@app.post("/chat/message")
async def send_chat_message(
    message_data: dict,
    current_user = Depends(get_current_user)
):
    """Send a chat message and get AI response"""
    try:
        message = message_data.get("message", "")
        mode = message_data.get("mode", "general")
        
        # Intelligent AI response based on message content
        response = generate_intelligent_response(message)
        
        return {
            "response": response,
            "mode": mode,
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
    print("🚀 Starting Working AI Wellness Vision API Server...")
    print("📊 Features: Authentication, Chat")
    print("🗄️ Database: PostgreSQL (Direct SQL)")
    print("🌐 Server: http://localhost:8003")
    print("📚 API Docs: http://localhost:8003/docs")
    
    uvicorn.run(
        "working_postgres_server:app",
        host="0.0.0.0",
        port=8003,
        reload=True,
        log_level="info"
    )