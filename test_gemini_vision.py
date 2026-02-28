#!/usr/bin/env python3
"""
Test Gemini Vision API directly
"""

import os
import google.generativeai as genai
from pathlib import Path

def test_gemini_vision():
    """Test Gemini Vision API directly"""
    
    print("🧪 Testing Gemini Vision API...")
    print("=" * 50)
    
    # Check API key
    api_key = os.getenv("GEMINI_API_KEY", "your-gemini-api-key-here")
    if api_key == "your-gemini-api-key-here":
        print("❌ Gemini API key not configured!")
        print("💡 Set GEMINI_API_KEY in your .env file")
        return
    
    print(f"✅ API Key found: {api_key[:10]}...")
    
    try:
        # Configure Gemini
        genai.configure(api_key=api_key)
        
        # Create a simple test image (1x1 pixel PNG)
        test_image_data = b'\x89PNG\r\n\x1a\n\x00\x00\x00\rIHDR\x00\x00\x00\x01\x00\x00\x00\x01\x08\x02\x00\x00\x00\x90wS\xde\x00\x00\x00\tpHYs\x00\x00\x0b\x13\x00\x00\x0b\x13\x01\x00\x9a\x9c\x18\x00\x00\x00\x12IDATx\x9cc```bPPP\x00\x02\xac\xea\x05\xc1\x1e\x1d\x1d\x00\x00\x00\x00IEND\xaeB`\x82'
        
        # Save test image
        test_image_path = "test_gemini_image.png"
        with open(test_image_path, 'wb') as f:
            f.write(test_image_data)
        
        print("📸 Test image created")
        
        # Test Gemini Vision
        model = genai.GenerativeModel('models/gemini-2.5-flash')
        
        # Read the image
        with open(test_image_path, 'rb') as img_file:
            img_data = img_file.read()
        
        img = {
            'mime_type': 'image/png',
            'data': img_data
        }
        
        prompt = "Analyze this image for health-related content. Provide a brief description."
        
        print("🤖 Sending request to Gemini Vision...")
        response = model.generate_content([prompt, img])
        
        if response and response.text:
            print("✅ Gemini Vision API working!")
            print(f"📝 Response: {response.text[:200]}...")
        else:
            print("❌ Gemini Vision returned empty response")
            print(f"🔍 Response object: {response}")
        
        # Clean up
        os.remove(test_image_path)
        
    except Exception as e:
        print(f"❌ Gemini Vision API Error: {e}")
        print(f"🔍 Error type: {type(e).__name__}")
        
        # Clean up
        try:
            os.remove(test_image_path)
        except:
            pass
    
    print("\n" + "=" * 50)
    print("🏁 Gemini Vision test complete!")

if __name__ == "__main__":
    # Load environment variables
    from dotenv import load_dotenv
    load_dotenv()
    
    test_gemini_vision()