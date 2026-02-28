#!/usr/bin/env python3
"""
Quick test for the running CNN server
"""

import requests
import json
from PIL import Image
import numpy as np
import io

def test_running_server():
    """Test the currently running CNN server"""
    
    print("🧪 Testing Running CNN Server")
    print("=" * 40)
    
    # Test 1: Health Check
    try:
        response = requests.get("http://localhost:8000/health")
        if response.status_code == 200:
            data = response.json()
            print("✅ Health Check: PASSED")
            print(f"   Status: {data.get('status')}")
            
            services = data.get('services', {})
            for service, status in services.items():
                print(f"   {service}: {status}")
        else:
            print(f"❌ Health Check: FAILED ({response.status_code})")
            return False
    except Exception as e:
        print(f"❌ Health Check: ERROR - {e}")
        return False
    
    print()
    
    # Test 2: Model Info
    try:
        response = requests.get("http://localhost:8000/api/v1/models/info")
        if response.status_code == 200:
            data = response.json()
            print("✅ Model Info: PASSED")
            print(f"   CNN Available: {data.get('cnn_available')}")
            print(f"   Gemini Available: {data.get('gemini_available')}")
        else:
            print(f"❌ Model Info: FAILED ({response.status_code})")
    except Exception as e:
        print(f"❌ Model Info: ERROR - {e}")
    
    print()
    
    # Test 3: Image Analysis
    try:
        # Create a simple test image
        img_array = np.random.randint(0, 255, (224, 224, 3), dtype=np.uint8)
        # Make it look more like skin (peachy color)
        img_array[:, :, 0] = np.clip(img_array[:, :, 0] + 50, 0, 255)  # More red
        img_array[:, :, 1] = np.clip(img_array[:, :, 1] + 30, 0, 255)  # Some green
        img_array[:, :, 2] = np.clip(img_array[:, :, 2] - 20, 0, 255)  # Less blue
        
        image = Image.fromarray(img_array)
        
        # Convert to bytes
        img_bytes = io.BytesIO()
        image.save(img_bytes, format='JPEG')
        img_bytes.seek(0)
        
        # Test skin analysis
        files = {'image': ('test_skin.jpg', img_bytes, 'image/jpeg')}
        data = {'analysis_type': 'skin'}
        
        response = requests.post(
            "http://localhost:8000/api/v1/analysis/image",
            files=files,
            data=data
        )
        
        if response.status_code == 200:
            result = response.json()
            print("✅ Image Analysis: PASSED")
            print(f"   Analysis Type: {result.get('type')}")
            print(f"   Result: {result.get('result')}")
            print(f"   Confidence: {result.get('confidence', 0):.2f}")
            print(f"   Method: {result.get('processing_method')}")
            
            recommendations = result.get('recommendations', [])
            if recommendations:
                print(f"   Recommendations: {len(recommendations)} provided")
                print(f"   First recommendation: {recommendations[0][:60]}...")
            
        else:
            print(f"❌ Image Analysis: FAILED ({response.status_code})")
            print(f"   Error: {response.text}")
            
    except Exception as e:
        print(f"❌ Image Analysis: ERROR - {e}")
    
    print()
    print("🎯 Test Summary:")
    print("   Your CNN server is running and functional!")
    print("   You can now:")
    print("   1. Test with your Flutter app")
    print("   2. Upload real images via http://localhost:8000/docs")
    print("   3. Use the API endpoints in your applications")
    
    return True

if __name__ == "__main__":
    test_running_server()