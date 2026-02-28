#!/usr/bin/env python3
"""
Debug PostgreSQL authentication issues
"""

import requests
import json

BASE_URL = "http://localhost:8000"

def test_health():
    """Test health endpoint"""
    print("🔍 Testing health endpoint...")
    try:
        response = requests.get(f"{BASE_URL}/health")
        print(f"Status: {response.status_code}")
        if response.status_code == 200:
            print(f"Response: {response.json()}")
        else:
            print(f"Error: {response.text}")
    except Exception as e:
        print(f"Error: {e}")

def test_registration():
    """Test registration with detailed error info"""
    print("\n🔐 Testing registration...")
    
    user_data = {
        "email": "debug_test@example.com",
        "password": "testpass123",
        "firstName": "Debug",
        "lastName": "Test"
    }
    
    try:
        response = requests.post(
            f"{BASE_URL}/auth/register",
            json=user_data,
            headers={"Content-Type": "application/json"}
        )
        
        print(f"Status Code: {response.status_code}")
        print(f"Headers: {dict(response.headers)}")
        
        if response.status_code == 200:
            data = response.json()
            print(f"✅ Success: {data}")
            return data.get('access_token')
        else:
            print(f"❌ Error Response: {response.text}")
            try:
                error_data = response.json()
                print(f"❌ Error JSON: {error_data}")
            except:
                print("❌ Could not parse error as JSON")
            return None
            
    except Exception as e:
        print(f"❌ Exception: {e}")
        return None

def test_login():
    """Test login with existing user"""
    print("\n🔑 Testing login with existing user...")
    
    login_data = {
        "email": "admin@wellnessvision.ai",
        "password": "admin123"
    }
    
    try:
        response = requests.post(
            f"{BASE_URL}/auth/login",
            json=login_data,
            headers={"Content-Type": "application/json"}
        )
        
        print(f"Status Code: {response.status_code}")
        
        if response.status_code == 200:
            data = response.json()
            print(f"✅ Login Success")
            print(f"   Token: {data.get('access_token', '')[:20]}...")
            return data.get('access_token')
        else:
            print(f"❌ Login Error: {response.text}")
            return None
            
    except Exception as e:
        print(f"❌ Login Exception: {e}")
        return None

def test_user_info(token):
    """Test getting user info with token"""
    print("\n👤 Testing user info...")
    
    if not token:
        print("❌ No token available")
        return
    
    try:
        headers = {
            "Authorization": f"Bearer {token}",
            "Content-Type": "application/json"
        }
        
        response = requests.get(f"{BASE_URL}/auth/me", headers=headers)
        
        print(f"Status Code: {response.status_code}")
        
        if response.status_code == 200:
            data = response.json()
            print(f"✅ User Info Success: {data}")
        else:
            print(f"❌ User Info Error: {response.text}")
            
    except Exception as e:
        print(f"❌ User Info Exception: {e}")

if __name__ == "__main__":
    print("🐛 Debug PostgreSQL Authentication")
    print("="*50)
    
    # Test health
    test_health()
    
    # Test registration
    reg_token = test_registration()
    
    # Test login
    login_token = test_login()
    
    # Test user info with login token
    if login_token:
        test_user_info(login_token)
    
    print("\n" + "="*50)
    print("🔍 Debug complete. Check server logs for more details.")