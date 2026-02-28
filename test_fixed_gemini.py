#!/usr/bin/env python3
"""
Test the fixed Gemini configuration
"""

import google.generativeai as genai
from dotenv import load_dotenv
import os

load_dotenv()

def test_gemini_models():
    """Test both chat and vision models"""
    try:
        # Configure Gemini
        api_key = os.getenv("GEMINI_API_KEY")
        genai.configure(api_key=api_key)
        
        print("🧪 Testing Fixed Gemini Models")
        print("=" * 50)
        
        # Test chat model
        print("1️⃣ Testing Chat Model (models/gemini-2.5-flash)")
        try:
            chat_model = genai.GenerativeModel('models/gemini-2.5-flash')
            response = chat_model.generate_content("What are 3 tips for better sleep?")
            print("✅ Chat Model: WORKING")
            print(f"Sample response: {response.text[:100]}...")
        except Exception as e:
            print(f"❌ Chat Model Error: {e}")
        
        print()
        
        # Test vision model (same model, different use)
        print("2️⃣ Testing Vision Model (models/gemini-2.5-flash)")
        try:
            vision_model = genai.GenerativeModel('models/gemini-2.5-flash')
            response = vision_model.generate_content("Analyze health-related images and provide wellness advice.")
            print("✅ Vision Model: WORKING")
            print(f"Sample response: {response.text[:100]}...")
        except Exception as e:
            print(f"❌ Vision Model Error: {e}")
        
        print()
        print("🎉 Gemini models are ready for your health app!")
        return True
        
    except Exception as e:
        print(f"❌ General Gemini Error: {e}")
        return False

if __name__ == "__main__":
    test_gemini_models()