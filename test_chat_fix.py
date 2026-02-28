#!/usr/bin/env python3
"""
Test script to verify the chat endpoint is working correctly
"""

import requests
import json

def test_chat_endpoint():
    """Test the CNN server chat endpoint"""
    
    base_url = "http://localhost:8000"
    endpoint = "/api/v1/chat/send"
    
    # Test different types of questions
    test_questions = [
        "How can I sleep better?",
        "What should I eat for breakfast?", 
        "I'm feeling stressed at work",
        "How much water should I drink?",
        "I want to start exercising",
        "Hello, how are you?",
        "Thank you for the help"
    ]
    
    print("🧪 Testing Chat Endpoint...")
    print(f"📡 Server: {base_url}{endpoint}")
    print("=" * 60)
    
    for i, question in enumerate(test_questions, 1):
        print(f"\n{i}. Testing: '{question}'")
        print("-" * 40)
        
        try:
            # Prepare request data
            data = {
                "message": question,
                "conversation_id": f"test_conversation_{i}"
            }
            
            # Make request
            response = requests.post(
                f"{base_url}{endpoint}",
                json=data,
                headers={"Content-Type": "application/json"},
                timeout=10
            )
            
            if response.status_code == 200:
                result = response.json()
                ai_response = result.get('ai_response', {}).get('content', 'No response')
                
                print(f"✅ Status: {response.status_code}")
                print(f"🤖 AI Response: {ai_response[:100]}...")
                if len(ai_response) > 100:
                    print(f"    (Full response: {len(ai_response)} characters)")
                
            else:
                print(f"❌ Status: {response.status_code}")
                print(f"❌ Error: {response.text}")
                
        except requests.exceptions.ConnectionError:
            print("❌ Connection Error: Is the server running on localhost:8000?")
        except requests.exceptions.Timeout:
            print("❌ Timeout: Server took too long to respond")
        except Exception as e:
            print(f"❌ Error: {e}")
    
    print("\n" + "=" * 60)
    print("🏁 Chat endpoint testing complete!")
    print("\n💡 If you see ✅ responses above, your chat is working!")
    print("💡 If you see ❌ errors, check that your server is running:")
    print("   python main_api_server_cnn.py")

if __name__ == "__main__":
    test_chat_endpoint()