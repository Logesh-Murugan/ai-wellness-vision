#!/usr/bin/env python3
"""
List available Gemini models
"""

import google.generativeai as genai
from dotenv import load_dotenv
import os

# Load environment variables
load_dotenv()

def list_models():
    try:
        # Configure Gemini
        api_key = os.getenv("GEMINI_API_KEY")
        genai.configure(api_key=api_key)
        
        print("🔍 Available Gemini Models:")
        print("=" * 50)
        
        models = genai.list_models()
        for model in models:
            print(f"✅ {model.name}")
            if hasattr(model, 'supported_generation_methods'):
                print(f"   Methods: {model.supported_generation_methods}")
            print()
        
        return True
        
    except Exception as e:
        print(f"❌ Error listing models: {e}")
        return False

if __name__ == "__main__":
    list_models()