#!/usr/bin/env python3
"""
Test script to verify all Flutter app backend integrations are working
"""

import requests
import json
import time
from pathlib import Path

# Backend URL
BASE_URL = "http://localhost:8000/api/v1"

def test_health_check():
    """Test basic health check"""
    print("🔍 Testing health check...")
    try:
        # Try both health endpoints
        health_urls = [
            f"{BASE_URL.replace('/api/v1', '')}/health",
            f"{BASE_URL}/health"
        ]
        
        for url in health_urls:
            try:
                response = requests.get(url)
                if response.status_code == 200:
                    print("✅ Health check passed")
                    return True
            except:
                continue
        
        print(f"❌ Health check failed on all endpoints")
        return False
    except Exception as e:
        print(f"❌ Health check error: {e}")
        return False

def test_authentication():
    """Test authentication endpoints"""
    print("\n🔐 Testing authentication...")
    
    # Test registration with a unique email each time
    import random
    unique_email = f"test{random.randint(1000, 9999)}@example.com"
    
    try:
        register_data = {
            "email": unique_email,
            "password": "testpass123",
            "firstName": "Test",
            "lastName": "User"
        }
        
        response = requests.post(f"{BASE_URL}/auth/register", json=register_data)
        if response.status_code in [200, 201, 409]:  # 409 if user already exists
            print("✅ Registration endpoint working")
            if response.status_code == 409:
                print("   (User already exists - this is expected)")
        else:
            print(f"❌ Registration failed: {response.status_code}")
            print(f"   Response: {response.text}")
            return False
    except Exception as e:
        print(f"❌ Registration error: {e}")
        return False
    
    # Test login with the same email
    try:
        login_data = {
            "email": unique_email,
            "password": "testpass123"
        }
        
        response = requests.post(f"{BASE_URL}/auth/login", json=login_data)
        if response.status_code == 200:
            print("✅ Login endpoint working")
            data = response.json()
            access_token = data.get("access_token")
            print(f"   Access token received: {access_token[:20]}..." if access_token else "   No access token")
            return access_token
        else:
            print(f"❌ Login failed: {response.status_code}")
            print(f"   Response: {response.text}")
            return False
    except Exception as e:
        print(f"❌ Login error: {e}")
        return False

def test_chat_endpoints(token=None):
    """Test chat endpoints"""
    print("\n💬 Testing chat endpoints...")
    
    headers = {}
    if token:
        headers["Authorization"] = f"Bearer {token}"
    
    # Test chat message
    try:
        chat_data = {
            "message": "Hello, I have a headache",
            "conversation_id": "test_conv"
        }
        
        response = requests.post(f"{BASE_URL}/chat/message", json=chat_data, headers=headers)
        if response.status_code == 200:
            print("✅ Chat message endpoint working")
            data = response.json()
            print(f"   Response: {data.get('content', '')[:50]}...")
        else:
            print(f"❌ Chat message failed: {response.status_code}")
            return False
    except Exception as e:
        print(f"❌ Chat message error: {e}")
        return False
    
    # Test conversations
    try:
        response = requests.get(f"{BASE_URL}/chat/conversations", headers=headers)
        if response.status_code == 200:
            print("✅ Get conversations endpoint working")
        else:
            print(f"❌ Get conversations failed: {response.status_code}")
    except Exception as e:
        print(f"❌ Get conversations error: {e}")
    
    return True

def test_image_analysis():
    """Test image analysis endpoints"""
    print("\n📸 Testing image analysis...")
    
    # Create a dummy image file for testing
    try:
        # Create a small test image file
        test_image_path = Path("test_image.jpg")
        if not test_image_path.exists():
            # Create a minimal JPEG file for testing
            with open(test_image_path, "wb") as f:
                # Minimal JPEG header
                f.write(b'\xff\xd8\xff\xe0\x00\x10JFIF\x00\x01\x01\x01\x00H\x00H\x00\x00\xff\xdb\x00C\x00\x08\x06\x06\x07\x06\x05\x08\x07\x07\x07\t\t\x08\n\x0c\x14\r\x0c\x0b\x0b\x0c\x19\x12\x13\x0f\x14\x1d\x1a\x1f\x1e\x1d\x1a\x1c\x1c $.\' ",#\x1c\x1c(7),01444\x1f\'9=82<.342\xff\xc0\x00\x11\x08\x00\x01\x00\x01\x01\x01\x11\x00\x02\x11\x01\x03\x11\x01\xff\xc4\x00\x14\x00\x01\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x08\xff\xc4\x00\x14\x10\x01\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\xff\xda\x00\x0c\x03\x01\x00\x02\x11\x03\x11\x00\x3f\x00\xaa\xff\xd9')
        
        with open(test_image_path, "rb") as f:
            files = {"image": ("test.jpg", f, "image/jpeg")}
            data = {
                "analysis_type": "skin",
                "session_id": "test_session",
                "language": "en"
            }
            
            response = requests.post(f"{BASE_URL}/analysis/image", files=files, data=data)
            if response.status_code == 200:
                print("✅ Image analysis endpoint working")
                result = response.json()
                print(f"   Analysis result: {result.get('result', '')[:50]}...")
            else:
                print(f"❌ Image analysis failed: {response.status_code}")
                print(f"   Response: {response.text}")
                return False
                
    except Exception as e:
        print(f"❌ Image analysis error: {e}")
        return False
    finally:
        # Clean up test file
        if test_image_path.exists():
            test_image_path.unlink()
    
    # Test analysis history
    try:
        response = requests.get(f"{BASE_URL}/analysis/history")
        if response.status_code == 200:
            print("✅ Analysis history endpoint working")
        else:
            print(f"❌ Analysis history failed: {response.status_code}")
    except Exception as e:
        print(f"❌ Analysis history error: {e}")
    
    return True

def test_voice_endpoints():
    """Test voice endpoints"""
    print("\n🎤 Testing voice endpoints...")
    
    # Test text-to-speech
    try:
        tts_data = {
            "text": "Hello, this is a test message",
            "language": "en",
            "voice": "female"
        }
        
        response = requests.post(f"{BASE_URL}/voice/synthesize", json=tts_data)
        if response.status_code == 200:
            print("✅ Text-to-speech endpoint working")
            data = response.json()
            print(f"   Audio URL: {data.get('audio_url', '')}")
        else:
            print(f"❌ Text-to-speech failed: {response.status_code}")
            return False
    except Exception as e:
        print(f"❌ Text-to-speech error: {e}")
        return False
    
    # Test speech-to-text (with dummy audio file)
    try:
        # Create a minimal WAV file for testing
        test_audio_path = Path("test_audio.wav")
        with open(test_audio_path, "wb") as f:
            # Minimal WAV header
            f.write(b'RIFF$\x00\x00\x00WAVEfmt \x10\x00\x00\x00\x01\x00\x01\x00D\xac\x00\x00\x88X\x01\x00\x02\x00\x10\x00data\x00\x00\x00\x00')
        
        with open(test_audio_path, "rb") as f:
            files = {"audio": ("test.wav", f, "audio/wav")}
            
            response = requests.post(f"{BASE_URL}/voice/transcribe", files=files)
            if response.status_code == 200:
                print("✅ Speech-to-text endpoint working")
                data = response.json()
                print(f"   Transcription: {data.get('transcription', '')}")
            else:
                print(f"❌ Speech-to-text failed: {response.status_code}")
                return False
                
    except Exception as e:
        print(f"❌ Speech-to-text error: {e}")
        return False
    finally:
        # Clean up test file
        if test_audio_path.exists():
            test_audio_path.unlink()
    
    return True

def main():
    """Run all integration tests"""
    print("🚀 Starting Flutter Backend Integration Tests")
    print("=" * 60)
    
    results = []
    
    # Test health check
    results.append(test_health_check())
    
    # Test authentication
    token = test_authentication()
    results.append(bool(token))
    
    # Test chat endpoints
    results.append(test_chat_endpoints(token))
    
    # Test image analysis
    results.append(test_image_analysis())
    
    # Test voice endpoints
    results.append(test_voice_endpoints())
    
    # Summary
    print("\n" + "=" * 60)
    print("📊 TEST SUMMARY")
    print("=" * 60)
    
    passed = sum(results)
    total = len(results)
    
    test_names = [
        "Health Check",
        "Authentication",
        "Chat Endpoints", 
        "Image Analysis",
        "Voice Endpoints"
    ]
    
    for i, (name, result) in enumerate(zip(test_names, results)):
        status = "✅ PASS" if result else "❌ FAIL"
        print(f"{status} {name}")
    
    print(f"\nOverall: {passed}/{total} tests passed")
    
    if passed == total:
        print("🎉 All backend integrations are working!")
        print("\n📱 Your Flutter app should now be able to:")
        print("   ✅ Authenticate users")
        print("   ✅ Send chat messages")
        print("   ✅ Analyze images")
        print("   ✅ Process voice input/output")
        print("   ✅ Retrieve analysis history")
    else:
        print("⚠️  Some integrations need attention")
        print("\n🔧 Next steps:")
        print("   1. Make sure the backend server is running")
        print("   2. Check network connectivity")
        print("   3. Verify API endpoints are correctly implemented")
    
    return passed == total

if __name__ == "__main__":
    success = main()
    exit(0 if success else 1)