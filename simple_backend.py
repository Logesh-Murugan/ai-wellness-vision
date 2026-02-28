#!/usr/bin/env python3
"""
Simple AI Wellness Vision Backend - No Dependencies Issues
"""

from fastapi import FastAPI, File, UploadFile, HTTPException
from fastapi.middleware.cors import CORSMiddleware
import uvicorn
import json
from datetime import datetime
import uuid

# Create FastAPI app
app = FastAPI(title="AI Wellness Vision API", version="1.0.0")

# Add CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Simple in-memory storage
users_db = {}
analyses_db = []

@app.get("/")
async def root():
    return {
        "message": "AI Wellness Vision API is running!",
        "status": "healthy",
        "timestamp": datetime.now().isoformat()
    }

@app.get("/api/v1/health")
async def health_check():
    return {"status": "healthy", "timestamp": datetime.now().isoformat()}

@app.post("/api/v1/auth/login")
async def login(email: str, password: str):
    if email and password:
        user_id = str(uuid.uuid4())
        user = {
            "id": user_id,
            "name": email.split('@')[0].title(),
            "email": email,
            "created_at": datetime.now().isoformat()
        }
        users_db[user_id] = user
        return {
            "user": user,
            "token": f"token_{user_id}",
            "message": "Login successful"
        }
    raise HTTPException(status_code=400, detail="Invalid credentials")

@app.post("/api/v1/analysis/image")
async def analyze_image(image: UploadFile = File(...)):
    # Simple mock analysis
    analysis = {
        "id": str(uuid.uuid4()),
        "type": "skin",
        "result": "Healthy skin detected with good hydration levels",
        "confidence": 0.89,
        "recommendations": [
            "Continue your current skincare routine",
            "Apply sunscreen daily",
            "Stay hydrated",
            "Get adequate sleep"
        ],
        "timestamp": datetime.now().isoformat()
    }
    analyses_db.append(analysis)
    return analysis

@app.post("/api/v1/chat/message")
async def chat_message(message: str):
    # Enhanced AI-like responses based on keywords
    message_lower = message.lower()
    
    if any(word in message_lower for word in ['sleep', 'tired', 'rest']):
        content = "For better sleep: Aim for 7-9 hours nightly, avoid screens 1 hour before bed, keep your room cool and dark, and establish a consistent bedtime routine."
    elif any(word in message_lower for word in ['exercise', 'workout', 'fitness', 'muscle', 'bicep']):
        content = "For fitness: Start with 150 minutes of moderate exercise weekly. For muscle building, focus on compound movements like squats, deadlifts, and push-ups. Progressive overload is key!"
    elif any(word in message_lower for word in ['diet', 'nutrition', 'food', 'eat']):
        content = "For nutrition: Focus on whole foods - lean proteins, vegetables, fruits, and whole grains. Stay hydrated with 8 glasses of water daily. Limit processed foods and added sugars."
    elif any(word in message_lower for word in ['stress', 'anxiety', 'mental']):
        content = "For mental health: Practice deep breathing, try meditation apps, maintain social connections, and consider talking to a counselor. Regular exercise also helps reduce stress."
    elif any(word in message_lower for word in ['skin', 'acne', 'skincare']):
        content = "For skin health: Use gentle cleansers, moisturize daily, apply SPF 30+ sunscreen, stay hydrated, and avoid touching your face. Consider seeing a dermatologist for persistent issues."
    else:
        content = "I'm here to help with your health and wellness questions! I can provide advice on fitness, nutrition, sleep, mental health, and skincare. What specific area would you like to know about?"
    
    response = {
        "id": str(uuid.uuid4()),
        "content": content,
        "is_user": False,
        "timestamp": datetime.now().isoformat()
    }
    return response

@app.get("/api/v1/analysis/history")
async def get_history():
    return analyses_db

if __name__ == "__main__":
    print("🚀 Starting Simple AI Wellness Vision API...")
    print("📱 Flutter app can connect to: http://localhost:8000")
    print("📖 API docs: http://localhost:8000/docs")
    
    uvicorn.run("simple_backend:app", host="0.0.0.0", port=8000, reload=True)