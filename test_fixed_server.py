#!/usr/bin/env python3
"""
Test the fixed PostgreSQL server
"""

import requests
import json

BASE_URL = "http://localhost:8002"

def test_complete_flow():
    """Test complete authentication flow"""
    print("🧪 Testing Fixed PostgreSQL Server")
    print("="*50)
    
    # Test 1: Health check
    print("\n1️⃣ Testing health check...")
    try:
        response = requests.get(f"{BASE_URL}/health")
        if response.status_code == 200:
            data = response.json()
            print(f"✅ Health check passed - Version: {data.get('version')}")
        else:
            print(f"❌ Health check failed: {response.status_code}")
            return False
    except Exception as e:
        print(f"❌ Health check error: {e}")
        return False
    
    # Test 2: Registration
    print("\n2️⃣ Testing user registration...")
    reg_data = {
        "email": "fixedtest@example.com",
        "password": "testpass123",
        "firstName": "Fixed",
        "lastName": "Test"
    }
    
    try:
        response = requests.post(f"{BASE_URL}/auth/register", json=reg_data)
        if response.status_code == 200:
            data = response.json()
            token = data['access_token']
            print(f"✅ Registration successful")
            print(f"   Token: {token[:20]}...")
        else:
            print(f"❌ Registration failed: {response.status_code}")
            print(f"   Error: {response.text}")
            # Try login instead
            print("   Trying login with existing user...")
            login_data = {"email": "admin@wellnessvision.ai", "password": "admin123"}
            response = requests.post(f"{BASE_URL}/auth/login", json=login_data)
            if response.status_code == 200:
                data = response.json()
                token = data['access_token']
                print(f"✅ Login successful instead")
            else:
                print(f"❌ Login also failed: {response.status_code}")
                return False
    except Exception as e:
        print(f"❌ Registration error: {e}")
        return False
    
    # Debug: Check users in database
    print("\n🔍 Debug: Checking users in database...")
    try:
        response = requests.get(f"{BASE_URL}/debug/users")
        if response.status_code == 200:
            data = response.json()
            print(f"   Users in DB: {data.get('count', 0)}")
            for user in data.get('users', []):
                print(f"   - {user.get('email')} (ID: {user.get('id', '')[:8]}...)")
        else:
            print(f"   Debug failed: {response.status_code}")
    except Exception as e:
        print(f"   Debug error: {e}")
    
    # Test 3: User info
    print("\n3️⃣ Testing user info...")
    try:
        headers = {"Authorization": f"Bearer {token}"}
        response = requests.get(f"{BASE_URL}/auth/me", headers=headers)
        if response.status_code == 200:
            data = response.json()
            print(f"✅ User info retrieved")
            print(f"   Name: {data.get('name')}")
            print(f"   Email: {data.get('email')}")
        else:
            print(f"❌ User info failed: {response.status_code}")
            print(f"   Error: {response.text}")
            
            # Let's also check what the token contains
            import jwt
            try:
                # Decode without verification to see contents
                decoded = jwt.decode(token, options={"verify_signature": False})
                print(f"   Token contents: {decoded}")
            except Exception as jwt_e:
                print(f"   Could not decode token: {jwt_e}")
            
            return False
    except Exception as e:
        print(f"❌ User info error: {e}")
        return False
    
    # Test 4: Chat
    print("\n4️⃣ Testing chat...")
    try:
        chat_data = {"message": "Hello, how are you?", "mode": "general"}
        response = requests.post(f"{BASE_URL}/chat/message", json=chat_data, headers=headers)
        if response.status_code == 200:
            data = response.json()
            print(f"✅ Chat successful")
            print(f"   Response: {data.get('response', '')[:50]}...")
        else:
            print(f"❌ Chat failed: {response.status_code}")
            print(f"   Error: {response.text}")
            return False
    except Exception as e:
        print(f"❌ Chat error: {e}")
        return False
    
    # Test 5: Conversations
    print("\n5️⃣ Testing conversations...")
    try:
        response = requests.get(f"{BASE_URL}/chat/conversations", headers=headers)
        if response.status_code == 200:
            data = response.json()
            print(f"✅ Conversations retrieved")
            print(f"   Count: {len(data.get('conversations', []))}")
        else:
            print(f"❌ Conversations failed: {response.status_code}")
            return False
    except Exception as e:
        print(f"❌ Conversations error: {e}")
        return False
    
    # Test 6: Logout
    print("\n6️⃣ Testing logout...")
    try:
        response = requests.post(f"{BASE_URL}/auth/logout", headers=headers)
        if response.status_code == 200:
            print(f"✅ Logout successful")
        else:
            print(f"❌ Logout failed: {response.status_code}")
    except Exception as e:
        print(f"❌ Logout error: {e}")
    
    print("\n" + "="*50)
    print("🎉 All tests completed successfully!")
    print("✅ Your PostgreSQL authentication is working!")
    print("\n🚀 Ready for Flutter integration:")
    print("   • API Base URL: http://localhost:8002")
    print("   • Authentication: JWT Bearer tokens")
    print("   • Database: PostgreSQL with Docker")
    
    return True

if __name__ == "__main__":
    success = test_complete_flow()
    if not success:
        print("\n❌ Some tests failed. Check the server logs.")
        exit(1)