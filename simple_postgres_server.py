#!/usr/bin/env python3
"""
Simple PostgreSQL server for testing
"""

import os
import sys
import asyncio
from datetime import datetime, timedelta
from typing import Optional

# Add src to path
sys.path.append(os.path.join(os.path.dirname(__file__), 'src'))

try:
    from fastapi import FastAPI, HTTPException, status
    from fastapi.middleware.cors import CORSMiddleware
    from pydantic import BaseModel, EmailStr
    import uvicorn
except ImportError:
    print("❌ FastAPI not available. Install with: pip install fastapi uvicorn")
    sys.exit(1)

from src.database.postgres_auth import PostgresAuthDatabase

# Initialize FastAPI app
app = FastAPI(title="Simple PostgreSQL Test API", version="1.0.0")

# CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Global database instance
db: Optional[PostgresAuthDatabase] = None

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
    token_type: str = "bearer"
    message: str

# Startup event
@app.on_event("startup")
async def startup_event():
    """Initialize database on startup"""
    global db
    try:
        print("🚀 Starting Simple PostgreSQL Test API...")
        
        database_url = os.getenv(
            'DATABASE_URL', 
            'postgresql://postgres:password@localhost:5432/ai_wellness_vision'
        )
        
        db = PostgresAuthDatabase(database_url)
        await db.initialize()
        
        print("✅ Database initialized successfully")
        
    except Exception as e:
        print(f"❌ Startup failed: {e}")
        import traceback
        traceback.print_exc()
        raise

@app.on_event("shutdown")
async def shutdown_event():
    """Cleanup on shutdown"""
    global db
    if db:
        await db.close()
        print("✅ Database connection closed")

# Health check
@app.get("/health")
async def health_check():
    """Health check endpoint"""
    return {
        "status": "healthy",
        "timestamp": datetime.now().isoformat(),
        "database": "postgresql",
        "message": "Simple PostgreSQL Test API is running"
    }

# Registration endpoint
@app.post("/auth/register", response_model=TokenResponse)
async def register_user(user_data: UserRegistration):
    """Register a new user"""
    try:
        print(f"📝 Registration request for: {user_data.email}")
        
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
        
        print(f"✅ User created with ID: {user_id}")
        
        # Create a simple token (not JWT for now)
        access_token = f"simple_token_{user_id}_{int(datetime.now().timestamp())}"
        
        return TokenResponse(
            access_token=access_token,
            message=f"User {user_data.email} registered successfully"
        )
        
    except HTTPException:
        raise
    except Exception as e:
        print(f"❌ Registration error: {e}")
        import traceback
        traceback.print_exc()
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Registration failed: {str(e)}"
        )

# Login endpoint
@app.post("/auth/login", response_model=TokenResponse)
async def login_user(user_data: UserLogin):
    """Login user"""
    try:
        print(f"🔑 Login request for: {user_data.email}")
        
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
        
        print(f"✅ User authenticated: {user_data.email}")
        
        # Create a simple token
        access_token = f"simple_token_{user['id']}_{int(datetime.now().timestamp())}"
        
        return TokenResponse(
            access_token=access_token,
            message=f"User {user_data.email} logged in successfully"
        )
        
    except HTTPException:
        raise
    except Exception as e:
        print(f"❌ Login error: {e}")
        import traceback
        traceback.print_exc()
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Login failed: {str(e)}"
        )

# Get users endpoint (for testing)
@app.get("/users")
async def get_users():
    """Get all users (for testing)"""
    try:
        if not db:
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail="Database not initialized"
            )
        
        # This is a simple test - in production you'd never expose all users
        async with db.pool.acquire() as conn:
            rows = await conn.fetch("SELECT id, email, name, created_at FROM users ORDER BY created_at DESC LIMIT 10")
            
            users = []
            for row in rows:
                users.append({
                    "id": str(row['id']),
                    "email": row['email'],
                    "name": row['name'],
                    "created_at": row['created_at'].isoformat() if row['created_at'] else None
                })
            
            return {"users": users, "count": len(users)}
        
    except Exception as e:
        print(f"❌ Get users error: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to get users: {str(e)}"
        )

if __name__ == "__main__":
    print("🚀 Starting Simple PostgreSQL Test API...")
    print("🌐 Server: http://localhost:8001")
    print("📚 API Docs: http://localhost:8001/docs")
    
    # Set environment variables
    os.environ['DATABASE_URL'] = 'postgresql://postgres:password@localhost:5432/ai_wellness_vision'
    
    uvicorn.run(
        "simple_postgres_server:app",
        host="0.0.0.0",
        port=8001,
        reload=True,
        log_level="info"
    )