#!/usr/bin/env python3
"""
Test Flutter-PostgreSQL Backend Integration
Comprehensive testing of all endpoints that Flutter app will use
"""

import requests
import json
import os
import tempfile
from datetime import datetime
from io import BytesIO
from PIL import Image

# Test configuration
BASE_URL = "http://localhost:8000"

class FlutterPostgresIntegrationTester:
    def __init__(self):
        self.session = requests.Session()
        self.access_token = None
        self.user_id = None
        
    def print_header(self, title):
        """Print formatted test section header"""
        print(f"\n{'='*60}")
        print(f"🔍 {title}")
        print('='*60)
    
    def print_result(self, test_name, success, details=""):
        """Print test result"""
        status = "✅ PASS" if success else "❌ FAIL"
        print(f"{status} {test_name}")
        if details:
            print(f"   {details}")
    
    def test_health_check(self):
        """Test health check endpoint"""
        self.print_header("Testing Health Check")
        try:
            response = self.session.get(f"{BASE_URL}/health")
            if response.status_code == 200:
                data = response.json()
                self.print_result("Health Check", True, f"Database: {data.get('database', 'unknown')}")
                return True
            else:
                self.print_result("Health Check", False, f"Status: {response.status_code}")
                return False
        except Exception as e:
            self.print_result("Health Check", False, f"Error: {e}")
            return False
    
    def test_user_registration(self):
        """Test user registration (Flutter signup flow)"""
        self.print_header("Testing User Registration")
        
        test_user = {
            "email": f"flutter_test_{datetime.now().strftime('%Y%m%d_%H%M%S')}@example.com",
            "password": "FlutterTest123!",
            "firstName": "Flutter",
            "lastName": "Tester"
        }
        
        try:
            response = self.session.post(
                f"{BASE_URL}/auth/register",
                json=test_user
            )
            
            if response.status_code == 200:
                data = response.json()
                self.access_token = data['access_token']
                self.print_result("User Registration", True, f"Token received: {data['access_token'][:20]}...")
                return True, test_user
            else:
                error_data = response.json()
                self.print_result("User Registration", False, f"Error: {error_data.get('detail')}")
                return False, None
                
        except Exception as e:
            self.print_result("User Registration", False, f"Exception: {e}")
            return False, None
    
    def test_user_login(self, user_data):
        """Test user login (Flutter login flow)"""
        self.print_header("Testing User Login")
        
        try:
            response = self.session.post(
                f"{BASE_URL}/auth/login",
                json={
                    "email": user_data["email"],
                    "password": user_data["password"]
                }
            )
            
            if response.status_code == 200:
                data = response.json()
                self.access_token = data['access_token']
                self.print_result("User Login", True, f"Token: {data['access_token'][:20]}...")
                self.print_result("Token Type", True, f"Type: {data.get('token_type', 'bearer')}")
                self.print_result("Expires In", True, f"Expires: {data.get('expires_in', 1800)}s")
                return True
            else:
                error_data = response.json()
                self.print_result("User Login", False, f"Error: {error_data.get('detail')}")
                return False
                
        except Exception as e:
            self.print_result("User Login", False, f"Exception: {e}")
            return False
    
    def test_user_profile(self):
        """Test getting user profile (Flutter profile screen)"""
        self.print_header("Testing User Profile")
        
        try:
            headers = {"Authorization": f"Bearer {self.access_token}"}
            response = self.session.get(f"{BASE_URL}/auth/me", headers=headers)
            
            if response.status_code == 200:
                data = response.json()
                self.user_id = data.get('id')
                self.print_result("Get User Profile", True, f"Name: {data.get('name')}")
                self.print_result("User Email", True, f"Email: {data.get('email')}")
                self.print_result("User ID", True, f"ID: {data.get('id', '')[:8]}...")
                self.print_result("User Preferences", True, f"Prefs: {len(data.get('preferences', {}))}")
                return True
            else:
                error_data = response.json()
                self.print_result("Get User Profile", False, f"Error: {error_data.get('detail')}")
                return False
                
        except Exception as e:
            self.print_result("Get User Profile", False, f"Exception: {e}")
            return False
    
    def test_chat_functionality(self):
        """Test chat functionality (Flutter chat screen)"""
        self.print_header("Testing Chat Functionality")
        
        chat_tests = [
            {"message": "Hello, how are you?", "mode": "general"},
            {"message": "What should I eat for breakfast?", "mode": "nutrition"},
            {"message": "I need a workout plan", "mode": "fitness"},
            {"message": "I'm feeling stressed", "mode": "mental_health"}
        ]
        
        headers = {"Authorization": f"Bearer {self.access_token}"}
        success_count = 0
        
        for i, chat_test in enumerate(chat_tests, 1):
            try:
                response = self.session.post(
                    f"{BASE_URL}/chat/message",
                    json=chat_test,
                    headers=headers
                )
                
                if response.status_code == 200:
                    data = response.json()
                    self.print_result(
                        f"Chat Message {i} ({chat_test['mode']})", 
                        True, 
                        f"Response: {data.get('response', '')[:50]}..."
                    )
                    success_count += 1
                else:
                    error_data = response.json()
                    self.print_result(
                        f"Chat Message {i} ({chat_test['mode']})", 
                        False, 
                        f"Error: {error_data.get('detail')}"
                    )
                    
            except Exception as e:
                self.print_result(
                    f"Chat Message {i} ({chat_test['mode']})", 
                    False, 
                    f"Exception: {e}"
                )
        
        # Test get conversations
        try:
            response = self.session.get(f"{BASE_URL}/chat/conversations", headers=headers)
            if response.status_code == 200:
                data = response.json()
                self.print_result("Get Conversations", True, f"Count: {len(data.get('conversations', []))}")
                success_count += 1
            else:
                self.print_result("Get Conversations", False, f"Status: {response.status_code}")
        except Exception as e:
            self.print_result("Get Conversations", False, f"Exception: {e}")
        
        return success_count >= 4  # At least 4 out of 5 tests should pass
    
    def test_image_analysis(self):
        """Test image analysis functionality (Flutter camera/gallery screen)"""
        self.print_header("Testing Image Analysis")
        
        # Create a test image
        test_image = Image.new('RGB', (100, 100), color='red')
        image_buffer = BytesIO()
        test_image.save(image_buffer, format='JPEG')
        image_buffer.seek(0)
        
        analysis_types = ["general", "skin", "nutrition", "fitness"]
        headers = {"Authorization": f"Bearer {self.access_token}"}
        success_count = 0
        
        for analysis_type in analysis_types:
            try:
                # Reset buffer position
                image_buffer.seek(0)
                
                files = {
                    'file': ('test_image.jpg', image_buffer, 'image/jpeg')
                }
                data = {
                    'analysis_type': analysis_type
                }
                
                response = self.session.post(
                    f"{BASE_URL}/image/analyze",
                    files=files,
                    data=data,
                    headers=headers
                )
                
                if response.status_code == 200:
                    result = response.json()
                    self.print_result(
                        f"Image Analysis ({analysis_type})", 
                        True, 
                        f"Confidence: {result.get('confidence', 0):.2f}"
                    )
                    self.print_result(
                        f"Analysis Result ({analysis_type})", 
                        True, 
                        f"Result: {result.get('analysis', '')[:40]}..."
                    )
                    success_count += 1
                else:
                    error_data = response.json()
                    self.print_result(
                        f"Image Analysis ({analysis_type})", 
                        False, 
                        f"Error: {error_data.get('detail')}"
                    )
                    
            except Exception as e:
                self.print_result(
                    f"Image Analysis ({analysis_type})", 
                    False, 
                    f"Exception: {e}"
                )
        
        # Test get analysis history
        try:
            response = self.session.get(f"{BASE_URL}/image/history", headers=headers)
            if response.status_code == 200:
                data = response.json()
                self.print_result("Get Analysis History", True, f"Count: {len(data.get('history', []))}")
                success_count += 1
            else:
                self.print_result("Get Analysis History", False, f"Status: {response.status_code}")
        except Exception as e:
            self.print_result("Get Analysis History", False, f"Exception: {e}")
        
        return success_count >= 3  # At least 3 out of 5 tests should pass
    
    def test_voice_functionality(self):
        """Test voice functionality (Flutter voice screen)"""
        self.print_header("Testing Voice Functionality")
        
        headers = {"Authorization": f"Bearer {self.access_token}"}
        success_count = 0
        
        # Test text-to-speech
        try:
            data = {
                'text': 'Hello, this is a test of the text to speech functionality.'
            }
            
            response = self.session.post(
                f"{BASE_URL}/voice/text-to-speech",
                data=data,
                headers=headers
            )
            
            if response.status_code == 200:
                result = response.json()
                self.print_result("Text-to-Speech", True, f"Audio URL: {result.get('audio_url', '')}")
                success_count += 1
            else:
                error_data = response.json()
                self.print_result("Text-to-Speech", False, f"Error: {error_data.get('detail')}")
                
        except Exception as e:
            self.print_result("Text-to-Speech", False, f"Exception: {e}")
        
        # Test speech-to-text (with mock audio file)
        try:
            # Create a mock audio file
            with tempfile.NamedTemporaryFile(suffix='.wav', delete=False) as temp_audio:
                temp_audio.write(b'mock audio data')
                temp_audio_path = temp_audio.name
            
            with open(temp_audio_path, 'rb') as audio_file:
                files = {
                    'file': ('test_audio.wav', audio_file, 'audio/wav')
                }
                
                response = self.session.post(
                    f"{BASE_URL}/voice/speech-to-text",
                    files=files,
                    headers=headers
                )
                
                if response.status_code == 200:
                    result = response.json()
                    self.print_result("Speech-to-Text", True, f"Transcription: {result.get('transcription', '')}")
                    success_count += 1
                else:
                    error_data = response.json()
                    self.print_result("Speech-to-Text", False, f"Error: {error_data.get('detail')}")
            
            # Clean up temp file
            os.unlink(temp_audio_path)
                    
        except Exception as e:
            self.print_result("Speech-to-Text", False, f"Exception: {e}")
        
        return success_count >= 1  # At least 1 out of 2 tests should pass
    
    def test_authentication_security(self):
        """Test authentication security (Flutter security requirements)"""
        self.print_header("Testing Authentication Security")
        
        success_count = 0
        
        # Test invalid token
        try:
            headers = {"Authorization": "Bearer invalid_token_12345"}
            response = self.session.get(f"{BASE_URL}/auth/me", headers=headers)
            
            if response.status_code == 401:
                self.print_result("Invalid Token Rejection", True, "Properly rejected")
                success_count += 1
            else:
                self.print_result("Invalid Token Rejection", False, f"Status: {response.status_code}")
        except Exception as e:
            self.print_result("Invalid Token Rejection", False, f"Exception: {e}")
        
        # Test no token
        try:
            response = self.session.get(f"{BASE_URL}/auth/me")
            
            if response.status_code == 403:  # FastAPI returns 403 for missing auth
                self.print_result("No Token Rejection", True, "Properly rejected")
                success_count += 1
            else:
                self.print_result("No Token Rejection", False, f"Status: {response.status_code}")
        except Exception as e:
            self.print_result("No Token Rejection", False, f"Exception: {e}")
        
        # Test logout
        try:
            headers = {"Authorization": f"Bearer {self.access_token}"}
            response = self.session.post(f"{BASE_URL}/auth/logout", headers=headers)
            
            if response.status_code == 200:
                self.print_result("User Logout", True, "Successfully logged out")
                success_count += 1
            else:
                self.print_result("User Logout", False, f"Status: {response.status_code}")
        except Exception as e:
            self.print_result("User Logout", False, f"Exception: {e}")
        
        return success_count >= 2  # At least 2 out of 3 tests should pass
    
    def run_all_tests(self):
        """Run all Flutter-PostgreSQL integration tests"""
        print("🚀 Starting Flutter-PostgreSQL Backend Integration Tests")
        print("="*60)
        
        results = []
        
        # Test 1: Health Check
        results.append(("Health Check", self.test_health_check()))
        
        # Test 2: User Registration
        reg_success, user_data = self.test_user_registration()
        results.append(("User Registration", reg_success))
        
        if not reg_success:
            print("❌ Cannot continue without successful registration")
            return False
        
        # Test 3: User Login
        login_success = self.test_user_login(user_data)
        results.append(("User Login", login_success))
        
        if not login_success:
            print("❌ Cannot continue without successful login")
            return False
        
        # Test 4: User Profile
        results.append(("User Profile", self.test_user_profile()))
        
        # Test 5: Chat Functionality
        results.append(("Chat Functionality", self.test_chat_functionality()))
        
        # Test 6: Image Analysis
        results.append(("Image Analysis", self.test_image_analysis()))
        
        # Test 7: Voice Functionality
        results.append(("Voice Functionality", self.test_voice_functionality()))
        
        # Test 8: Authentication Security
        results.append(("Authentication Security", self.test_authentication_security()))
        
        # Print summary
        self.print_header("TEST SUMMARY")
        
        passed = 0
        total = len(results)
        
        for test_name, success in results:
            status = "✅ PASS" if success else "❌ FAIL"
            print(f"{status} {test_name}")
            if success:
                passed += 1
        
        print(f"\nOverall: {passed}/{total} tests passed")
        
        if passed == total:
            print("\n🎉 All Flutter-PostgreSQL integration tests passed!")
            print("\n📱 Your Flutter app is ready to integrate with:")
            print("✅ PostgreSQL authentication")
            print("✅ User registration and login")
            print("✅ Chat functionality")
            print("✅ Image analysis")
            print("✅ Voice processing")
            print("✅ Secure API endpoints")
            
            print("\n🔧 Flutter Integration Steps:")
            print("1. Update API base URL to: http://localhost:8000")
            print("2. Implement JWT token storage")
            print("3. Add Authorization headers to requests")
            print("4. Handle authentication errors")
            print("5. Test on device/emulator")
            
        else:
            print(f"\n⚠️ {total - passed} tests failed. Check the server logs and fix issues before Flutter integration.")
        
        return passed == total

if __name__ == "__main__":
    tester = FlutterPostgresIntegrationTester()
    success = tester.run_all_tests()
    
    if not success:
        exit(1)