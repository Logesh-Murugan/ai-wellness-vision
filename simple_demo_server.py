#!/usr/bin/env python3
"""
AI Wellness Vision - Simple Demo Server
No database required - works with mock data
"""

from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from typing import List, Optional
import uvicorn
from datetime import datetime
import json

# ============================================================================
# FASTAPI APP SETUP
# ============================================================================

app = FastAPI(
    title="AI Wellness Vision Demo API",
    description="Simple demo server with mock data - no database required",
    version="1.0.0"
)

# CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# ============================================================================
# DATA MODELS
# ============================================================================

class LoginRequest(BaseModel):
    email: str
    password: str

class LoginResponse(BaseModel):
    token: str
    user: dict

class ChatRequest(BaseModel):
    message: str
    conversation_id: str = "default"

class ChatResponse(BaseModel):
    id: str
    content: str
    is_user: bool
    timestamp: str
    type: Optional[str] = None

# ============================================================================
# MOCK DATA
# ============================================================================

# Mock users
MOCK_USERS = {
    "admin@wellnessvision.ai": {
        "id": "user_001",
        "name": "Demo User",
        "email": "admin@wellnessvision.ai",
        "profile_image": None,
        "created_at": "2024-01-01T00:00:00Z"
    },
    "demo@example.com": {
        "id": "user_002", 
        "name": "Demo User",
        "email": "demo@example.com",
        "profile_image": None,
        "created_at": "2024-01-01T00:00:00Z"
    }
}

# Mock analysis results
MOCK_ANALYSES = [
    {
        "id": "analysis_001",
        "type": "skin",
        "result": "Healthy skin detected with good hydration levels",
        "confidence": 0.92,
        "recommendations": [
            "Continue your current skincare routine",
            "Use sunscreen daily",
            "Stay hydrated"
        ],
        "timestamp": "2024-01-15T10:30:00Z",
        "image_path": None
    },
    {
        "id": "analysis_002", 
        "type": "food",
        "result": "Nutritious meal with balanced macronutrients",
        "confidence": 0.88,
        "recommendations": [
            "Great protein source",
            "Add more vegetables for fiber",
            "Consider portion size"
        ],
        "timestamp": "2024-01-14T18:45:00Z",
        "image_path": None
    }
]

# Mock chat responses
CHAT_RESPONSES = [
    "I'm here to help with your health and wellness questions!",
    "That's a great question about nutrition. A balanced diet includes proteins, carbohydrates, healthy fats, vitamins, and minerals.",
    "For better sleep, try maintaining a consistent sleep schedule and creating a relaxing bedtime routine.",
    "Regular exercise is important for overall health. Start with 30 minutes of moderate activity most days.",
    "Staying hydrated is crucial. Aim for 8 glasses of water daily, more if you're active.",
    "Stress management techniques like meditation, deep breathing, or yoga can be very beneficial.",
    "If you have specific health concerns, it's always best to consult with a healthcare professional."
]

# ============================================================================
# API ENDPOINTS
# ============================================================================

@app.get("/")
async def root():
    return {
        "message": "AI Wellness Vision Demo API",
        "status": "running",
        "mode": "demo",
        "timestamp": datetime.now().isoformat()
    }

@app.get("/health")
async def health_check():
    return {
        "status": "healthy",
        "mode": "demo",
        "database": "mock_data",
        "timestamp": datetime.now().isoformat()
    }

# ============================================================================
# AUTHENTICATION ENDPOINTS
# ============================================================================

@app.post("/auth/login", response_model=LoginResponse)
async def login(request: LoginRequest):
    """Demo login - accepts any email/password combination"""
    
    # For demo, accept any credentials
    user_data = MOCK_USERS.get(request.email, {
        "id": "demo_user",
        "name": "Demo User", 
        "email": request.email,
        "profile_image": None,
        "created_at": datetime.now().isoformat()
    })
    
    return LoginResponse(
        token="demo_token_12345",
        user=user_data
    )

@app.get("/auth/me")
async def get_current_user():
    """Get current user info"""
    return {
        "id": "demo_user",
        "name": "Demo User",
        "email": "demo@example.com", 
        "profile_image": None,
        "created_at": "2024-01-01T00:00:00Z"
    }

# ============================================================================
# ANALYSIS ENDPOINTS  
# ============================================================================

@app.post("/analysis/image")
async def analyze_image():
    """Mock image analysis"""
    import random
    
    # Return a random mock analysis
    analysis = random.choice(MOCK_ANALYSES).copy()
    analysis["id"] = f"analysis_{datetime.now().strftime('%Y%m%d_%H%M%S')}"
    analysis["timestamp"] = datetime.now().isoformat()
    
    return analysis

@app.get("/analysis/history")
async def get_analysis_history():
    """Get analysis history"""
    return MOCK_ANALYSES

# ============================================================================
# CHAT ENDPOINTS
# ============================================================================

@app.post("/chat/message", response_model=ChatResponse)
async def send_chat_message(request: ChatRequest):
    """Send chat message and get AI response"""
    import random
    
    # Return a random response
    response_content = random.choice(CHAT_RESPONSES)
    
    return ChatResponse(
        id=f"msg_{datetime.now().strftime('%Y%m%d_%H%M%S')}",
        content=response_content,
        is_user=False,
        timestamp=datetime.now().isoformat(),
        type="ai_response"
    )

@app.get("/chat/history")
async def get_chat_history():
    """Get chat history"""
    return []

# ============================================================================
# MAIN SERVER STARTUP
# ============================================================================

if __name__ == "__main__":
    print("🚀 Starting AI Wellness Vision Demo Server...")
    print("📊 Features: Demo Authentication, Mock Analysis, AI Chat")
    print("🗄️ Database: Mock Data (No PostgreSQL required)")
    print("🌐 Server: http://localhost:8003")
    print("📚 API Docs: http://localhost:8003/docs")
    print("🎯 Mode: DEMO - No real authentication required")
    print("=" * 60)
    
    uvicorn.run(
        "simple_demo_server:app",
        host="0.0.0.0",
        port=8003,
        reload=True,
        log_level="info"
    )