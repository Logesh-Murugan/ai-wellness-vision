#!/usr/bin/env python3
"""
Simple authentication test
"""

import requests
import json
import random

def test_auth():
    """Test authentication with a fresh user"""
    base_url = "http://localhost:8000/api/v1"
    
    # Generate unique email
    unique_id = random.randint(10000, 99999)
    email = f"testuser{unique_id}@example.com"
    password = "testpass123"
    
    print(f"🔍 Testing authentication with: {email}")
    
    # Test Registration
    print("\n1. Testing Registration...")
    try:
        register_data = {
            "email": email,
            "password": password,
            "firstName": "Test",
            "lastName": "User"
        }
        
        response = requests.post(f"{base_url}/auth/register", json=register_data)
        print(f"Status: {response.status_code}")
        
        if response.status_code == 200:
            print("✅ Registration successful!")
            data = response.json()
            print(f"Access token: {data.get('access_token', 'None')[:20]}...")
            print(f"User: {data.get('user', {}).get('email', 'None')}")
        else:
            print(f"❌ Registration failed: {response.text}")
            return False
            
    except Exception as e:
        print(f"❌ Registration error: {e}")
        return False
    
    # Test Login
    print("\n2. Testing Login...")
    try:
        login_data = {
            "email": email,
            "password": password
        }
        
        response = requests.post(f"{base_url}/auth/login", json=login_data)
        print(f"Status: {response.status_code}")
        
        if response.status_code == 200:
            print("✅ Login successful!")
            data = response.json()
            print(f"Access token: {data.get('access_token', 'None')[:20]}...")
            return True
        else:
            print(f"❌ Login failed: {response.text}")
            return False
            
    except Exception as e:
        print(f"❌ Login error: {e}")
        return False

if __name__ == "__main__":
    success = test_auth()
    if success:
        print("\n🎉 Authentication is working correctly!")
    else:
        print("\n❌ Authentication has issues")