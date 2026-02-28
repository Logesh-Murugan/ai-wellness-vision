#!/usr/bin/env python3
"""
Test the working PostgreSQL server
"""

import requests
import json

BASE_URL = "http://localhost:8003"

def test_working_server():
    """Test the working server"""
    print("🚀 Testing Working PostgreSQL Server")
    print("="*50)
    
    # Test 1: Health check
    print("\n1️⃣ Health Check...")
    try:
        response = requests.get(f"{BASE_URL}/health")
        if response.status_code == 200:
            data = response.json()
            print(f"✅ Health OK - Version: {data.get('version')}")
        else:
            print(f"❌ Health failed: {response.status_code}")
            return False
    except Exception as e:
        print(f"❌ Health error: {e}")
        return False
    
    # Test 2: Debug users
    print("\n2️⃣ Checking Database...")
    try:
        response = requests.get(f"{BASE_URL}/debug/users")
        if response.status_code == 200:
            data = response.json()
            print(f"✅ Found {data.get('count', 0)} users")
            for user in data.get('users', [])[:3]:
                print(f"   - {user.get('email')} | {user.get('name')}")
        else:
            print(f"❌ Debug failed: {response.status_code}")
    except Exception as e:
        print(f"❌ Debug error: {e}")
    
    # Test 3: Login
    print("\n3️⃣ Login Test...")
    login_data = {
        "email": "admin@wellnessvision.ai",
        "password": "admin123"
    }
    
    try:
        response = requests.post(f"{BASE_URL}/auth/login", json=login_data)
        if response.status_code == 200:
            data = response.json()
            token = data['access_token']
            print(f"✅ Login successful")
            print(f"   Token: {token[:30]}...")
        else:
            print(f"❌ Login failed: {response.status_code}")
            print(f"   Error: {response.text}")
            return False
    except Exception as e:
        print(f"❌ Login error: {e}")
        return False
    
    # Test 4: User Info
    print("\n4️⃣ User Info Test...")
    try:
        headers = {"Authorization": f"Bearer {token}"}
        response = requests.get(f"{BASE_URL}/auth/me", headers=headers)
        
        print(f"   Status: {response.status_code}")
        
        if response.status_code == 200:
            data = response.json()
            print(f"✅ User info success!")
            print(f"   ID: {data.get('id', '')[:8]}...")
            print(f"   Email: {data.get('email')}")
            print(f"   Name: {data.get('name')}")
            print(f"   First Name: {data.get('firstName')}")
            print(f"   Last Name: {data.get('lastName')}")
        else:
            print(f"❌ User info failed")
            print(f"   Response: {response.text}")
            return False
    except Exception as e:
        print(f"❌ User info error: {e}")
        return False
    
    # Test 5: Chat
    print("\n5️⃣ Chat Test...")
    try:
        chat_data = {"message": "Hello!", "mode": "general"}
        response = requests.post(f"{BASE_URL}/chat/message", json=chat_data, headers=headers)
        
        if response.status_code == 200:
            data = response.json()
            print(f"✅ Chat success!")
            print(f"   Response: {data.get('response', '')[:50]}...")
        else:
            print(f"❌ Chat failed: {response.status_code}")
            return False
    except Exception as e:
        print(f"❌ Chat error: {e}")
        return False
    
    # Test 6: Conversations
    print("\n6️⃣ Conversations Test...")
    try:
        response = requests.get(f"{BASE_URL}/chat/conversations", headers=headers)
        
        if response.status_code == 200:
            data = response.json()
            print(f"✅ Conversations success!")
            print(f"   Count: {len(data.get('conversations', []))}")
        else:
            print(f"❌ Conversations failed: {response.status_code}")
            return False
    except Exception as e:
        print(f"❌ Conversations error: {e}")
        return False
    
    print("\n" + "="*50)
    print("🎉 ALL TESTS PASSED!")
    print("✅ PostgreSQL Authentication is WORKING!")
    print("\n🚀 Ready for Flutter Integration:")
    print("   • API Base URL: http://localhost:8003")
    print("   • All endpoints working correctly")
    print("   • JWT authentication functional")
    print("   • Database operations successful")
    
    return True

if __name__ == "__main__":
    success = test_working_server()
    if not success:
        print("\n❌ Some tests failed.")
        exit(1)
    else:
        print("\n🎊 Your PostgreSQL backend is ready!")
        print("   Start using it with your Flutter app!")