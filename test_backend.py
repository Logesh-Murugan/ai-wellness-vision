#!/usr/bin/env python3
"""
Test the enhanced health backend
"""

import requests
import json

def test_health_endpoint():
    """Test the health check endpoint"""
    try:
        response = requests.get("http://localhost:8000/api/v1/health")
        if response.status_code == 200:
            print("✅ Health endpoint working")
            return True
        else:
            print(f"❌ Health endpoint failed: {response.status_code}")
            return False
    except Exception as e:
        print(f"❌ Health endpoint error: {e}")
        return False

def test_chat_endpoint():
    """Test the chat endpoint with different questions"""
    test_questions = [
        "I can't sleep at night",
        "What should I eat for breakfast?",
        "How do I build muscle?",
        "I feel stressed about work",
        "My skin is breaking out"
    ]
    
    success_count = 0
    
    for question in test_questions:
        try:
            response = requests.post(
                "http://localhost:8000/api/v1/chat/message",
                json={"message": question, "conversation_id": "test"}
            )
            
            if response.status_code == 200:
                data = response.json()
                print(f"✅ Question: '{question}'")
                print(f"   Response: {data['content'][:100]}...")
                print()
                success_count += 1
            else:
                print(f"❌ Chat failed for: '{question}' - Status: {response.status_code}")
                
        except Exception as e:
            print(f"❌ Chat error for '{question}': {e}")
    
    return success_count == len(test_questions)

def main():
    print("🧪 Testing Enhanced Health Backend...")
    print("=" * 60)
    
    # Test health endpoint
    health_ok = test_health_endpoint()
    
    if not health_ok:
        print("❌ Backend not running. Start it with: python main_api_server.py")
        return
    
    # Test chat functionality
    print("\n🤖 Testing Chat Responses...")
    print("-" * 40)
    
    chat_ok = test_chat_endpoint()
    
    print("=" * 60)
    if health_ok and chat_ok:
        print("🎉 All tests PASSED! Your health app backend is ready!")
    else:
        print("⚠️  Some tests failed. Check the backend logs.")

if __name__ == "__main__":
    main()