#!/usr/bin/env python3
"""
Debug authentication endpoint to find the exact error
"""

import requests
import json
import traceback

def test_auth_endpoints():
    """Test authentication endpoints with detailed error reporting"""
    base_url = "http://localhost:8000/api/v1"
    
    print("🔍 Debugging Authentication Endpoints")
    print("=" * 50)
    
    # Test 1: Registration with detailed error handling
    print("\n1. Testing Registration...")
    try:
        register_data = {
            "email": "debug_test@example.com",
            "password": "testpass123",
            "firstName": "Debug",
            "lastName": "Test"
        }
        
        print(f"📤 Sending: {json.dumps(register_data, indent=2)}")
        
        response = requests.post(f"{base_url}/auth/register", 
                               json=register_data, 
                               timeout=10)
        
        print(f"📥 Status Code: {response.status_code}")
        print(f"📥 Headers: {dict(response.headers)}")
        
        try:
            response_json = response.json()
            print(f"📥 Response: {json.dumps(response_json, indent=2)}")
        except:
            print(f"📥 Raw Response: {response.text}")
            
    except Exception as e:
        print(f"❌ Registration Error: {e}")
        traceback.print_exc()
    
    # Test 2: Login
    print("\n2. Testing Login...")
    try:
        login_data = {
            "email": "debug_test@example.com",
            "password": "testpass123"
        }
        
        print(f"📤 Sending: {json.dumps(login_data, indent=2)}")
        
        response = requests.post(f"{base_url}/auth/login", 
                               json=login_data, 
                               timeout=10)
        
        print(f"📥 Status Code: {response.status_code}")
        
        try:
            response_json = response.json()
            print(f"📥 Response: {json.dumps(response_json, indent=2)}")
        except:
            print(f"📥 Raw Response: {response.text}")
            
    except Exception as e:
        print(f"❌ Login Error: {e}")
        traceback.print_exc()
    
    # Test 3: Check server health
    print("\n3. Testing Server Health...")
    try:
        response = requests.get("http://localhost:8000/health", timeout=5)
        print(f"📥 Health Status: {response.status_code}")
        if response.status_code == 200:
            print(f"📥 Health Response: {response.json()}")
    except Exception as e:
        print(f"❌ Health Check Error: {e}")

if __name__ == "__main__":
    test_auth_endpoints()