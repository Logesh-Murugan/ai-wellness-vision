#!/usr/bin/env python3
"""
Simple authentication test without JWT decoding
"""

import requests
import json

BASE_URL = "http://localhost:8002"

def test_admin_login_and_info():
    """Test admin login and user info"""
    print("🧪 Simple Authentication Test")
    print("="*40)
    
    # Test 1: Login as admin
    print("\n1️⃣ Testing admin login...")
    login_data = {
        "email": "admin@wellnessvision.ai",
        "password": "admin123"
    }
    
    try:
        response = requests.post(f"{BASE_URL}/auth/login", json=login_data)
        print(f"   Status: {response.status_code}")
        
        if response.status_code == 200:
            data = response.json()
            token = data['access_token']
            print(f"   ✅ Login successful")
            print(f"   Token: {token[:30]}...")
        else:
            print(f"   ❌ Login failed: {response.text}")
            return False
    except Exception as e:
        print(f"   ❌ Login error: {e}")
        return False
    
    # Test 2: Check debug users
    print("\n2️⃣ Checking users in database...")
    try:
        response = requests.get(f"{BASE_URL}/debug/users")
        if response.status_code == 200:
            data = response.json()
            print(f"   Users found: {data.get('count', 0)}")
            for user in data.get('users', []):
                email = user.get('email', 'unknown')
                name = user.get('name', 'no name')
                print(f"   - {email} | Name: '{name}'")
        else:
            print(f"   ❌ Debug failed: {response.status_code}")
    except Exception as e:
        print(f"   ❌ Debug error: {e}")
    
    # Test 3: Get user info
    print("\n3️⃣ Testing user info...")
    try:
        headers = {"Authorization": f"Bearer {token}"}
        response = requests.get(f"{BASE_URL}/auth/me", headers=headers)
        
        print(f"   Status: {response.status_code}")
        print(f"   Response: {response.text}")
        
        if response.status_code == 200:
            data = response.json()
            print(f"   ✅ User info retrieved")
            print(f"   Name: {data.get('name', 'No name')}")
            print(f"   Email: {data.get('email', 'No email')}")
            return True
        else:
            print(f"   ❌ User info failed")
            return False
            
    except Exception as e:
        print(f"   ❌ User info error: {e}")
        return False

if __name__ == "__main__":
    success = test_admin_login_and_info()
    
    if success:
        print("\n🎉 Authentication is working!")
    else:
        print("\n❌ Authentication has issues. Check server logs.")
        print("\n💡 Server logs should show detailed error information.")
        print("   Look for lines starting with 'ERROR' or 'INFO' in the server terminal.")