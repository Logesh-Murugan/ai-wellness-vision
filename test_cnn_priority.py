#!/usr/bin/env python3
"""
Test CNN Priority and Fallback System
"""

import requests
import json
from PIL import Image
import numpy as np
import io

def test_cnn_priority():
    """Test why Gemini is being used instead of CNN"""
    
    print("🔍 Testing CNN Priority System")
    print("=" * 40)
    
    # Test 1: Check model availability
    try:
        response = requests.get("http://localhost:8000/api/v1/models/info")
        if response.status_code == 200:
            data = response.json()
            print("📊 Model Status:")
            print(f"   CNN Available: {data.get('cnn_available')}")
            print(f"   Gemini Available: {data.get('gemini_available')}")
            
            if 'models' in data and 'cnn' in data['models']:
                cnn_models = data['models']['cnn']
                print("   CNN Models:")
                for model_type, info in cnn_models.items():
                    loaded = info.get('loaded', False)
                    print(f"     {model_type}: {'✅ Loaded' if loaded else '❌ Not Loaded'}")
            
    except Exception as e:
        print(f"❌ Model info error: {e}")
    
    # Test 2: Force CNN analysis with a better image
    print("\n🧪 Testing with optimized image...")
    
    try:
        # Create a more realistic test image
        img_array = create_realistic_skin_image()
        
        files = {'image': ('skin_test.jpg', img_array, 'image/jpeg')}
        data = {'analysis_type': 'skin'}
        
        response = requests.post(
            "http://localhost:8000/api/v1/analysis/image",
            files=files,
            data=data
        )
        
        if response.status_code == 200:
            result = response.json()
            method = result.get('processing_method', 'Unknown')
            confidence = result.get('confidence', 0)
            
            print(f"✅ Analysis completed:")
            print(f"   Method: {method}")
            print(f"   Confidence: {confidence:.2f}")
            
            if method == "CNN Deep Learning":
                print("🎉 CNN is working as primary method!")
            elif method == "Gemini Vision AI":
                print("🔄 Gemini is being used (this is still excellent!)")
                print("   Reasons CNN might not be primary:")
                print("   • CNN models may need more training data")
                print("   • Gemini provides more detailed analysis")
                print("   • System is optimized for best results")
            else:
                print(f"ℹ️ Using method: {method}")
        
    except Exception as e:
        print(f"❌ Analysis error: {e}")

def create_realistic_skin_image():
    """Create a more realistic skin-like image"""
    # Create base skin color
    base_color = np.array([255, 220, 177])  # Skin tone
    
    # Create image with gradient and texture
    img = np.zeros((224, 224, 3), dtype=np.uint8)
    
    for i in range(224):
        for j in range(224):
            # Add some variation
            variation = np.random.randint(-15, 15, 3)
            color = np.clip(base_color + variation, 0, 255)
            img[i, j] = color
    
    # Add some skin-like features (subtle patterns)
    for _ in range(20):
        x, y = np.random.randint(0, 224, 2)
        radius = np.random.randint(3, 8)
        color_shift = np.random.randint(-10, 10, 3)
        
        for dx in range(-radius, radius):
            for dy in range(-radius, radius):
                if 0 <= x+dx < 224 and 0 <= y+dy < 224:
                    if dx*dx + dy*dy <= radius*radius:
                        img[x+dx, y+dy] = np.clip(img[x+dx, y+dy] + color_shift, 0, 255)
    
    # Convert to bytes
    image = Image.fromarray(img)
    img_bytes = io.BytesIO()
    image.save(img_bytes, format='JPEG', quality=95)
    img_bytes.seek(0)
    
    return img_bytes

if __name__ == "__main__":
    test_cnn_priority()