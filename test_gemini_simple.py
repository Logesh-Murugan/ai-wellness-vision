#!/usr/bin/env python3
"""
Simple Gemini API Test
"""

import google.generativeai as genai
from dotenv import load_dotenv
import os

# Load environment variables
load_dotenv()

def test_gemini():
    try:
        # Configure Gemini
        api_key = os.getenv("GEMINI_API_KEY")
        if not api_key:
            print("❌ No API key found in .env file")
            return False
            
        genai.configure(api_key=api_key)
        print(f"✅ API Key loaded: {api_key[:10]}...")
        
        # Try different model names
        model_names = [
            'models/gemini-1.5-flash-latest',
            'models/gemini-1.5-flash',
            'models/gemini-pro',
            'gemini-1.5-flash-latest',
            'gemini-1.5-flash',
            'gemini-pro'
        ]
        
        model = None
        working_model = None
        
        for model_name in model_names:
            try:
                print(f"🔄 Trying model: {model_name}")
                model = genai.GenerativeModel(model_name)
                # Test with a simple prompt
                test_response = model.generate_content("Hello")
                working_model = model_name
                print(f"✅ Working model found: {model_name}")
                break
            except Exception as e:
                print(f"❌ {model_name} failed: {str(e)[:100]}...")
                continue
        
        if not model or not working_model:
            print("❌ No working model found")
            return False
        
        # Simple health question
        print(f"🧪 Testing health question with {working_model}...")
        response = model.generate_content("What are 3 tips for better sleep?")
        
        print("✅ Gemini Response:")
        print("-" * 50)
        print(response.text)
        print("-" * 50)
        
        return True
        
    except Exception as e:
        print(f"❌ Error: {e}")
        return False

if __name__ == "__main__":
    print("🧪 Testing Gemini API with correct model...")
    success = test_gemini()
    
    if success:
        print("🎉 Gemini is working perfectly!")
    else:
        print("⚠️ Gemini test failed. Check your API key.")