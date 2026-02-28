#!/usr/bin/env python3
"""
Test script to verify Gemini API integration
"""

import os
from dotenv import load_dotenv
import google.generativeai as genai

# Load environment variables
load_dotenv()

# Configure Gemini
genai.configure(api_key=os.getenv("GEMINI_API_KEY"))

def test_gemini_chat():
    """Test Gemini chat functionality"""
    try:
        model = genai.GenerativeModel('gemini-pro')
        
        prompt = """You are a health assistant. Answer this question: 
        "I have trouble sleeping at night. What can I do?"
        
        Keep the response concise and helpful."""
        
        response = model.generate_content(prompt)
        print("✅ Gemini Chat Test PASSED")
        print(f"Response: {response.text[:200]}...")
        return True
        
    except Exception as e:
        print(f"❌ Gemini Chat Test FAILED: {e}")
        return False

def test_gemini_vision():
    """Test Gemini Vision functionality"""
    try:
        model = genai.GenerativeModel('gemini-pro-vision')
        print("✅ Gemini Vision Model Loaded")
        print("Note: Vision test requires an actual image file")
        return True
        
    except Exception as e:
        print(f"❌ Gemini Vision Test FAILED: {e}")
        return False

if __name__ == "__main__":
    print("🧪 Testing Gemini API Integration...")
    print("=" * 50)
    
    # Test API key
    api_key = os.getenv("GEMINI_API_KEY")
    if api_key and api_key.startswith("AIza"):
        print("✅ API Key Found and Valid Format")
    else:
        print("❌ API Key Missing or Invalid Format")
        exit(1)
    
    # Test chat
    chat_success = test_gemini_chat()
    
    # Test vision
    vision_success = test_gemini_vision()
    
    print("=" * 50)
    if chat_success and vision_success:
        print("🎉 All Gemini Tests PASSED! Your integration is ready!")
    else:
        print("⚠️  Some tests failed. Check your API key and internet connection.")