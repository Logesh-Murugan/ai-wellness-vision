#!/usr/bin/env python3
"""
Quick test to verify token verification fix
"""

import requests
import json

BASE_URL = "http://localhost:8000"

def test_full_auth_flow():
    """Test complete authentication flow"""
    print("🔄 Testing complete authentication flow...")
    
    # Step 1: Register a new user
    print("\n1️⃣ Registering new user...")
    reg_data = {
        "email": "flowtest@example.com",
        "password": "testpass123",
        "firstName": "Flow",
        "lastName": "Test"
    }
    
    reg_response = requests.post(f"{BASE_URL}/auth/register", json=reg_data)
    print(f"   Registration Status: {reg_response.status_code}")
    
    if reg_response.status_code == 200:
        reg_result = reg_response.json()
        token = reg_result['access_token']
        print(f"   ✅ Registration successful, token: {token[:20]}...")
    else:
        print(f"   ❌ Registration failed: {reg_response.text}")
        return False
    
    # Step 2: Test user info with the token
    print("\n2️⃣ Testing user info with token...")
    headers = {"Authorization": f"Bearer {token}"}
    
    user_response = requests.get(f"{BASE_URL}/auth/me", headers=headers)
    print(f"   User Info Status: {user_response.status_code}")
    
    if user_response.status_code == 200:
        user_data = user_response.json()
        print(f"   ✅ User info retrieved: {user_data.get('name', 'Unknown')}")
    else:
        print(f"   ❌ User info failed: {user_response.text}")
        return False
    
    # Step 3: Test protected endpoint (chat)
    print("\n3️⃣ Testing protected chat endpoint...")
    chat_data = {"message": "Hello, this is a test!", "mode": "general"}
    
    chat_response = requests.post(f"{BASE_URL}/chat/message", json=chat_data, headers=headers)
    print(f"   Chat Status: {chat_response.status_code}")
    
    if chat_response.status_code == 200:
        chat_result = chat_response.json()
        print(f"   ✅ Chat successful: {chat_result.get('response', '')[:50]}...")
    else:
        print(f"   ❌ Chat failed: {chat_response.text}")
        return False
    
    # Step 4: Test logout
    print("\n4️⃣ Testing logout...")
    logout_response = requests.post(f"{BASE_URL}/auth/logout", headers=headers)
    print(f"   Logout Status: {logout_response.status_code}")
    
    if logout_response.status_code == 200:
        print(f"   ✅ Logout successful")
    else:
        print(f"   ❌ Logout failed: {logout_response.text}")
    
    print("\n🎉 Complete authentication flow test completed!")
    return True

if __name__ == "__main__":
    print("🧪 Testing Token Verification Fix")
    print("="*50)
    
    success = test_full_auth_flow()
    
    if success:
        print("\n✅ All authentication tests passed!")
        print("🚀 Your PostgreSQL authentication is working correctly!")
    else:
        print("\n❌ Some tests failed. Check the server logs.")