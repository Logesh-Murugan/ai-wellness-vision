#!/usr/bin/env python3
"""
Basic Gemini test that finds and uses any available model
"""

import google.generativeai as genai
from dotenv import load_dotenv
import os

# Load environment variables
load_dotenv()

def find_working_model():
    """Find any working Gemini model"""
    try:
        api_key = os.getenv("GEMINI_API_KEY")
        genai.configure(api_key=api_key)
        
        print("🔍 Finding available models...")
        
        # Get all available models
        models = genai.list_models()
        
        for model in models:
            model_name = model.name
            print(f"🔄 Testing: {model_name}")
            
            try:
                # Test if this model supports generateContent
                if hasattr(model, 'supported_generation_methods'):
                    if 'generateContent' in model.supported_generation_methods:
                        # Try to use this model
                        test_model = genai.GenerativeModel(model_name)
                        response = test_model.generate_content("Hello, how are you?")
                        
                        print(f"✅ SUCCESS! Working model: {model_name}")
                        print(f"Response: {response.text[:100]}...")
                        return model_name
                        
            except Exception as e:
                print(f"❌ {model_name} failed: {str(e)[:50]}...")
                continue
        
        print("❌ No working models found")
        return None
        
    except Exception as e:
        print(f"❌ Error: {e}")
        return None

def test_health_chat(model_name):
    """Test health-related chat with the working model"""
    try:
        model = genai.GenerativeModel(model_name)
        
        health_question = "What are 3 simple tips for better sleep?"
        print(f"\n🧪 Testing health question: {health_question}")
        
        response = model.generate_content(health_question)
        
        print("✅ Health Response:")
        print("-" * 50)
        print(response.text)
        print("-" * 50)
        
        return True
        
    except Exception as e:
        print(f"❌ Health test failed: {e}")
        return False

if __name__ == "__main__":
    print("🧪 Finding and testing Gemini models...")
    print("=" * 60)
    
    # Find a working model
    working_model = find_working_model()
    
    if working_model:
        print(f"\n🎉 Found working model: {working_model}")
        
        # Test health chat
        success = test_health_chat(working_model)
        
        if success:
            print("\n🎉 Gemini is ready for your health app!")
            print(f"Use this model name in your backend: {working_model}")
        else:
            print("\n⚠️ Model works but health test failed")
    else:
        print("\n❌ No working Gemini models found")
        print("Check your API key or try a different key")