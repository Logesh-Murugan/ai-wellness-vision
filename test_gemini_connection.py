#!/usr/bin/env python3
"""
Test Gemini AI connection
"""

import os
import google.generativeai as genai
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

# Configure Gemini API
api_key = os.getenv("GEMINI_API_KEY")
print(f"API Key: {api_key[:10]}..." if api_key else "No API key found")

if api_key:
    genai.configure(api_key=api_key)
    
    try:
        # First list available models
        print("\n📋 Available Models:")
        available_models = []
        for m in genai.list_models():
            if 'generateContent' in m.supported_generation_methods:
                print(f"  - {m.name}")
                available_models.append(m.name)
        
        # Try to use the first available model
        if available_models:
            model_name = available_models[0]
            print(f"\n🧪 Testing with model: {model_name}")
            
            model = genai.GenerativeModel(model_name)
            response = model.generate_content("Hello, can you help with health questions?")
            
            print("✅ Gemini AI Connection Successful!")
            print(f"Response: {response.text[:100]}...")
        else:
            print("❌ No compatible models found")
                
    except Exception as e:
        print(f"❌ Gemini AI Error: {e}")
else:
    print("❌ No Gemini API key found in .env file")