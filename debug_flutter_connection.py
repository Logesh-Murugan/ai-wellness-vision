#!/usr/bin/env python3
"""
Debug Flutter-Backend Connection Issues
"""

import requests
import json
import time

def test_backend_connection():
    """Test if backend is accessible"""
    
    print("🔍 Debugging Flutter-Backend Connection...")
    print("=" * 50)
    
    # Test 1: Basic server health
    try:
        response = requests.get("http://localhost:8000/docs", timeout=5)
        if response.status_code == 200:
            print("✅ Backend server is running and accessible")
        else:
            print(f"❌ Backend server returned status: {response.status_code}")
    except Exception as e:
        print(f"❌ Cannot reach backend server: {e}")
        return False
    
    # Test 2: Test chat endpoint
    print("\n🧪 Testing Chat Endpoint...")
    try:
        chat_data = {
            "message": "Hello from debug test",
            "conversation_id": "debug_test_123"
        }
        response = requests.post(
            "http://localhost:8000/api/v1/chat/send",
            json=chat_data,
            headers={"Content-Type": "application/json"},
            timeout=10
        )
        
        if response.status_code == 200:
            print("✅ Chat endpoint working")
            data = response.json()
            print(f"📝 Response: {data.get('ai_response', {}).get('content', 'No content')[:50]}...")
        else:
            print(f"❌ Chat endpoint failed: {response.status_code}")
            print(f"❌ Response: {response.text}")
    except Exception as e:
        print(f"❌ Chat endpoint error: {e}")
    
    # Test 3: Test image analysis endpoint
    print("\n🖼️ Testing Image Analysis Endpoint...")
    try:
        # Create a simple test image
        test_image_data = b'\x89PNG\r\n\x1a\n\x00\x00\x00\rIHDR\x00\x00\x00\x01\x00\x00\x00\x01\x08\x02\x00\x00\x00\x90wS\xde\x00\x00\x00\tpHYs\x00\x00\x0b\x13\x00\x00\x0b\x13\x01\x00\x9a\x9c\x18\x00\x00\x00\x12IDATx\x9cc```bPPP\x00\x02\xac\xea\x05\xc1\x1e\x1d\x1d\x00\x00\x00\x00IEND\xaeB`\x82'
        
        files = {'image': ('test.png', test_image_data, 'image/png')}
        data = {'analysis_type': 'skin'}
        
        response = requests.post(
            "http://localhost:8000/api/v1/analysis/image",
            files=files,
            data=data,
            timeout=30
        )
        
        if response.status_code == 200:
            print("✅ Image analysis endpoint working")
            result = response.json()
            print(f"🔍 Analysis Type: {result.get('type')}")
            print(f"⚙️ Processing Method: {result.get('processing_method')}")
            print(f"🎯 Confidence: {result.get('confidence')}")
        else:
            print(f"❌ Image analysis failed: {response.status_code}")
            print(f"❌ Response: {response.text}")
    except Exception as e:
        print(f"❌ Image analysis error: {e}")
    
    print("\n" + "=" * 50)
    print("🏁 Connection debugging complete!")
    
    # Test 4: Check CORS headers
    print("\n🌐 Checking CORS Configuration...")
    try:
        response = requests.options("http://localhost:8000/api/v1/chat/send")
        cors_headers = {k: v for k, v in response.headers.items() if 'access-control' in k.lower()}
        if cors_headers:
            print("✅ CORS headers found:")
            for header, value in cors_headers.items():
                print(f"   {header}: {value}")
        else:
            print("⚠️ No CORS headers found - this might cause Flutter connection issues")
    except Exception as e:
        print(f"❌ CORS check failed: {e}")
    
    return True

def monitor_backend_requests():
    """Monitor backend for incoming requests"""
    
    print("\n👀 Monitoring Backend Requests...")
    print("Now try using your Flutter app and watch for requests here...")
    print("Press Ctrl+C to stop monitoring")
    
    try:
        while True:
            time.sleep(1)
            # This is just a placeholder - the actual monitoring happens in the backend logs
    except KeyboardInterrupt:
        print("\n🛑 Monitoring stopped")

if __name__ == "__main__":
    if test_backend_connection():
        print("\n💡 Backend is working. If Flutter still can't connect:")
        print("   1. Check if Flutter app is running on localhost:3000")
        print("   2. Check browser console for CORS errors")
        print("   3. Verify Flutter is calling the correct endpoints")
        print("   4. Check if Flutter app is using HTTP (not HTTPS)")
        
        monitor_backend_requests()