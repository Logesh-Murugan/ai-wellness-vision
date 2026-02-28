#!/usr/bin/env python3
"""
Quick test to check server status and available endpoints
"""

import requests
import json

def test_server():
    """Test if server is running and what endpoints are available"""
    base_urls = [
        "http://localhost:8000",
        "http://127.0.0.1:8000",
        "http://10.135.99.214:8000"
    ]
    
    print("🔍 Testing server connectivity...")
    
    working_url = None
    for url in base_urls:
        try:
            response = requests.get(url, timeout=5)
            if response.status_code == 200:
                print(f"✅ Server is running at: {url}")
                working_url = url
                break
        except Exception as e:
            print(f"❌ {url} - {e}")
    
    if not working_url:
        print("❌ Server is not accessible on any URL")
        return False
    
    # Test specific endpoints
    endpoints_to_test = [
        "/",
        "/health", 
        "/api/v1/health",
        "/docs",
        "/api/v1/auth/login",
        "/api/v1/chat/message",
        "/api/v1/analysis/image",
        "/api/v1/voice/transcribe"
    ]
    
    print(f"\n🔍 Testing endpoints on {working_url}...")
    
    for endpoint in endpoints_to_test:
        try:
            url = f"{working_url}{endpoint}"
            
            if endpoint in ["/api/v1/auth/login", "/api/v1/chat/message"]:
                # POST endpoints - test with dummy data
                response = requests.post(url, json={"test": "data"}, timeout=5)
            elif endpoint == "/api/v1/analysis/image":
                # Skip file upload test for now
                print(f"⏭️  {endpoint} - Skipping file upload test")
                continue
            elif endpoint == "/api/v1/voice/transcribe":
                # Skip audio upload test for now  
                print(f"⏭️  {endpoint} - Skipping audio upload test")
                continue
            else:
                # GET endpoints
                response = requests.get(url, timeout=5)
            
            if response.status_code in [200, 201, 400, 422]:  # 400/422 are OK for POST with dummy data
                print(f"✅ {endpoint} - Status: {response.status_code}")
            else:
                print(f"❌ {endpoint} - Status: {response.status_code}")
                
        except Exception as e:
            print(f"❌ {endpoint} - Error: {e}")
    
    return True

if __name__ == "__main__":
    test_server()