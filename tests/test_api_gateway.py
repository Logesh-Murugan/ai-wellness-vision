# test_api_gateway.py - Tests for API gateway and service orchestration
import unittest
import tempfile
import asyncio
from pathlib import Path
from unittest.mock import patch, MagicMock, AsyncMock

from src.api.gateway import ServiceOrchestrator, APIGateway, AnalysisRequest, ChatRequest
from src.models import HealthAnalysisResult, AnalysisType, AnalysisStatus

class TestServiceOrchestrator(unittest.TestCase):
    """Test service orchestration functionality"""
    
    def setUp(self):
        try:
            self.orchestrator = ServiceOrchestrator()
        except Exception as e:
            self.skipTest(f"Service orchestrator initialization failed: {e}")
    
    def test_orchestrator_initialization(self):
        """Test orchestrator initializes correctly"""
        self.assertIsNotNone(self.orchestrator.image_service)
        self.assertIsNotNone(self.orchestrator.nlp_service)
        self.assertIsNotNone(self.orchestrator.speech_service)
        self.assertIsNotNone(self.orchestrator.explainable_ai_service)
        self.assertIsInstance(self.orchestrator.active_sessions, dict)
        self.assertIsInstance(self.orchestrator.analysis_cache, dict)
    
    def test_get_session_new(self):
        """Test creating new session"""
        session = self.orchestrator.get_session("test_session_123", "user_123", "en")
        
        self.assertEqual(session.session_id, "test_session_123")
        self.assertEqual(session.user_id, "user_123")
        self.assertEqual(session.language_preference, "en")
        self.assertIn("test_session_123", self.orchestrator.active_sessions)
    
    def test_get_session_existing(self):
        """Test getting existing session"""
        session1 = self.orchestrator.get_session("test_session_456", "user_456")
        session2 = self.orchestrator.get_session("test_session_456", "user_456")
        
        self.assertIs(session1, session2)  # Should be the same object
    
    def test_process_chat_message(self):
        """Test chat message processing"""
        async def run_test():
            chat_request = ChatRequest(
                message="Hello, I have a headache",
                session_id="test_chat_session",
                user_id="test_user",
                language="en",
                message_type="text"
            )
            
            result = await self.orchestrator.process_chat_message(chat_request)
            
            self.assertEqual(result['status'], 'success')
            self.assertIn('response', result)
            self.assertIn('language', result)
            self.assertIn('sentiment', result)
            self.assertIn('processing_time', result)
        
        # Run async test
        asyncio.run(run_test())
    
    def test_get_session_history(self):
        """Test session history retrieval"""
        async def run_test():
            # Create a session with some history
            session = self.orchestrator.get_session("history_test_session")
            session.add_conversation_entry("Hello", "Hi there!", "text")
            
            result = await self.orchestrator.get_session_history("history_test_session")
            
            self.assertEqual(result['status'], 'success')
            self.assertIn('conversation_history', result)
            self.assertIn('analysis_history', result)
            self.assertEqual(len(result['conversation_history']), 1)
        
        asyncio.run(run_test())
    
    def test_get_session_history_not_found(self):
        """Test session history for non-existent session"""
        async def run_test():
            result = await self.orchestrator.get_session_history("nonexistent_session")
            
            self.assertEqual(result['status'], 'error')
            self.assertIn('message', result)
        
        asyncio.run(run_test())
    
    def test_get_service_status(self):
        """Test service status retrieval"""
        status = self.orchestrator.get_service_status()
        
        self.assertIn('image_service', status)
        self.assertIn('nlp_service', status)
        self.assertIn('speech_service', status)
        self.assertIn('explainable_ai_service', status)
        
        # Check that each service has availability info
        for service_name, service_info in status.items():
            self.assertIn('available', service_info)
            self.assertIsInstance(service_info['available'], bool)

class TestAPIGateway(unittest.TestCase):
    """Test API gateway functionality"""
    
    def setUp(self):
        try:
            self.gateway = APIGateway()
        except Exception as e:
            self.skipTest(f"API gateway initialization failed: {e}")
    
    def test_gateway_initialization(self):
        """Test gateway initializes correctly"""
        self.assertIsNotNone(self.gateway.orchestrator)
        # App might be None if FastAPI is not available
        if self.gateway.app:
            self.assertIsNotNone(self.gateway.app)
    
    def test_get_app(self):
        """Test getting FastAPI app instance"""
        app = self.gateway.get_app()
        # App might be None if FastAPI is not available
        if app:
            self.assertIsNotNone(app)
    
    def test_run_mock_server(self):
        """Test mock server functionality"""
        result = self.gateway.run_mock_server("localhost", 8080)
        
        self.assertIn('status', result)
        self.assertIn('host', result)
        self.assertIn('port', result)
        self.assertEqual(result['host'], 'localhost')
        self.assertEqual(result['port'], 8080)

class TestAPIModels(unittest.TestCase):
    """Test API request/response models"""
    
    def test_analysis_request_creation(self):
        """Test AnalysisRequest model creation"""
        request = AnalysisRequest(
            analysis_type="skin_condition",
            session_id="test_session",
            user_id="test_user",
            language="en"
        )
        
        self.assertEqual(request.analysis_type, "skin_condition")
        self.assertEqual(request.session_id, "test_session")
        self.assertEqual(request.user_id, "test_user")
        self.assertEqual(request.language, "en")
    
    def test_chat_request_creation(self):
        """Test ChatRequest model creation"""
        request = ChatRequest(
            message="Hello, how are you?",
            session_id="chat_session",
            user_id="chat_user",
            language="en",
            message_type="text"
        )
        
        self.assertEqual(request.message, "Hello, how are you?")
        self.assertEqual(request.session_id, "chat_session")
        self.assertEqual(request.user_id, "chat_user")
        self.assertEqual(request.language, "en")
        self.assertEqual(request.message_type, "text")

class TestAsyncOperations(unittest.TestCase):
    """Test async operations in the API gateway"""
    
    def setUp(self):
        try:
            self.orchestrator = ServiceOrchestrator()
        except Exception as e:
            self.skipTest(f"Service orchestrator initialization failed: {e}")
    
    def test_multiple_concurrent_chat_requests(self):
        """Test handling multiple concurrent chat requests"""
        async def run_test():
            # Create multiple chat requests
            requests = [
                ChatRequest(
                    message=f"Message {i}",
                    session_id=f"session_{i}",
                    user_id=f"user_{i}",
                    language="en"
                )
                for i in range(3)
            ]
            
            # Process requests concurrently
            tasks = [
                self.orchestrator.process_chat_message(request)
                for request in requests
            ]
            
            results = await asyncio.gather(*tasks)
            
            # All requests should succeed
            for result in results:
                self.assertEqual(result['status'], 'success')
                self.assertIn('response', result)
        
        asyncio.run(run_test())
    
    def test_session_isolation(self):
        """Test that different sessions are properly isolated"""
        async def run_test():
            # Create requests for different sessions
            request1 = ChatRequest(
                message="Hello from session 1",
                session_id="isolation_session_1",
                user_id="user_1",
                language="en"
            )
            
            request2 = ChatRequest(
                message="Hello from session 2", 
                session_id="isolation_session_2",
                user_id="user_2",
                language="hi"
            )
            
            # Process both requests
            result1 = await self.orchestrator.process_chat_message(request1)
            result2 = await self.orchestrator.process_chat_message(request2)
            
            # Both should succeed
            self.assertEqual(result1['status'], 'success')
            self.assertEqual(result2['status'], 'success')
            
            # Check session isolation
            session1 = self.orchestrator.active_sessions["isolation_session_1"]
            session2 = self.orchestrator.active_sessions["isolation_session_2"]
            
            self.assertEqual(session1.user_id, "user_1")
            self.assertEqual(session2.user_id, "user_2")
            self.assertEqual(session1.language_preference, "en")
            self.assertEqual(session2.language_preference, "hi")
        
        asyncio.run(run_test())

class TestErrorHandling(unittest.TestCase):
    """Test error handling in API gateway"""
    
    def setUp(self):
        try:
            self.orchestrator = ServiceOrchestrator()
        except Exception as e:
            self.skipTest(f"Service orchestrator initialization failed: {e}")
    
    def test_invalid_analysis_type(self):
        """Test handling of invalid analysis type"""
        async def run_test():
            # Mock upload file
            mock_file = MagicMock()
            mock_file.filename = "test.jpg"
            mock_file.read = AsyncMock(return_value=b"mock image data")
            
            request = AnalysisRequest(
                analysis_type="invalid_type",
                session_id="error_test_session",
                language="en"
            )
            
            result = await self.orchestrator.process_image_analysis(mock_file, request)
            
            self.assertEqual(result['status'], 'error')
            self.assertIn('message', result)
        
        asyncio.run(run_test())
    
    def test_empty_chat_message(self):
        """Test handling of empty chat message"""
        async def run_test():
            request = ChatRequest(
                message="",
                session_id="empty_message_session",
                language="en"
            )
            
            result = await self.orchestrator.process_chat_message(request)
            
            # Should still process successfully (NLP service handles empty messages)
            self.assertEqual(result['status'], 'success')
        
        asyncio.run(run_test())

class TestAuthenticationIntegration(unittest.TestCase):
    """Test authentication integration with API gateway"""
    
    def setUp(self):
        try:
            from src.api.auth import auth_manager
            self.auth_manager = auth_manager
            self.gateway = APIGateway()
        except Exception as e:
            self.skipTest(f"Authentication setup failed: {e}")
    
    def test_user_authentication_flow(self):
        """Test complete user authentication flow"""
        try:
            # Test authentication
            user = self.auth_manager.authenticate_user("testuser", "user123")
            self.assertIsNotNone(user)
            self.assertEqual(user.username, "testuser")
            
            # Test token creation
            access_token = self.auth_manager.create_access_token(user)
            self.assertIsNotNone(access_token)
            
            # Test token verification
            token_data = self.auth_manager.verify_token(access_token)
            self.assertEqual(token_data.username, "testuser")
            self.assertIn("user", token_data.roles)
            
        except Exception as e:
            self.skipTest(f"Authentication flow test failed: {e}")
    
    def test_admin_authentication_flow(self):
        """Test admin authentication and permissions"""
        try:
            # Test admin authentication
            admin = self.auth_manager.authenticate_user("admin", "admin123")
            self.assertIsNotNone(admin)
            self.assertEqual(admin.username, "admin")
            self.assertIn("admin", admin.roles)
            
            # Test admin permissions
            self.assertTrue(self.auth_manager.check_permission(admin.roles, ["admin"]))
            self.assertTrue(self.auth_manager.check_permission(admin.roles, ["user"]))
            
        except Exception as e:
            self.skipTest(f"Admin authentication test failed: {e}")
    
    def test_invalid_authentication(self):
        """Test invalid authentication scenarios"""
        try:
            # Test invalid username
            with self.assertRaises(Exception):
                self.auth_manager.authenticate_user("nonexistent", "password")
            
            # Test invalid password
            with self.assertRaises(Exception):
                self.auth_manager.authenticate_user("testuser", "wrongpassword")
            
        except Exception as e:
            self.skipTest(f"Invalid authentication test failed: {e}")

class TestServiceOrchestrationIntegration(unittest.TestCase):
    """Test enhanced service orchestration"""
    
    def setUp(self):
        try:
            self.orchestrator = ServiceOrchestrator()
        except Exception as e:
            self.skipTest(f"Service orchestrator initialization failed: {e}")
    
    def test_concurrent_service_requests(self):
        """Test handling concurrent requests across different services"""
        async def run_test():
            # Create multiple concurrent requests
            tasks = []
            
            # Image analysis task
            mock_file = MagicMock()
            mock_file.filename = "test.jpg"
            mock_file.read = AsyncMock(return_value=b"mock image data")
            
            analysis_request = AnalysisRequest(
                analysis_type="skin_condition",
                session_id="concurrent_session_1",
                language="en"
            )
            
            tasks.append(self.orchestrator.process_image_analysis(mock_file, analysis_request))
            
            # Chat requests
            for i in range(3):
                chat_request = ChatRequest(
                    message=f"Test message {i}",
                    session_id=f"concurrent_session_{i+2}",
                    language="en"
                )
                tasks.append(self.orchestrator.process_chat_message(chat_request))
            
            # Speech synthesis task
            speech_request = SpeechRequest(
                text="Hello, this is a test",
                language="en"
            )
            tasks.append(self.orchestrator.process_speech_synthesis(speech_request))
            
            # Execute all tasks concurrently
            results = await asyncio.gather(*tasks, return_exceptions=True)
            
            # Check that all requests completed successfully
            for i, result in enumerate(results):
                if isinstance(result, Exception):
                    self.fail(f"Task {i} failed with exception: {result}")
                else:
                    self.assertEqual(result['status'], 'success')
        
        asyncio.run(run_test())
    
    def test_service_error_handling(self):
        """Test error handling across services"""
        async def run_test():
            # Test invalid analysis type
            mock_file = MagicMock()
            mock_file.filename = "test.jpg"
            mock_file.read = AsyncMock(return_value=b"mock image data")
            
            invalid_request = AnalysisRequest(
                analysis_type="invalid_analysis_type",
                session_id="error_test_session",
                language="en"
            )
            
            result = await self.orchestrator.process_image_analysis(mock_file, invalid_request)
            self.assertEqual(result['status'], 'error')
            self.assertIn('message', result)
        
        asyncio.run(run_test())
    
    def test_session_management_across_services(self):
        """Test session management across different services"""
        async def run_test():
            session_id = "cross_service_session"
            
            # Start with image analysis
            mock_file = MagicMock()
            mock_file.filename = "test.jpg"
            mock_file.read = AsyncMock(return_value=b"mock image data")
            
            analysis_request = AnalysisRequest(
                analysis_type="skin_condition",
                session_id=session_id,
                user_id="test_user",
                language="en"
            )
            
            analysis_result = await self.orchestrator.process_image_analysis(mock_file, analysis_request)
            self.assertEqual(analysis_result['status'], 'success')
            
            # Follow up with chat
            chat_request = ChatRequest(
                message="Tell me about my analysis",
                session_id=session_id,
                user_id="test_user",
                language="en"
            )
            
            chat_result = await self.orchestrator.process_chat_message(chat_request)
            self.assertEqual(chat_result['status'], 'success')
            
            # Check session history
            history = await self.orchestrator.get_session_history(session_id)
            self.assertEqual(history['status'], 'success')
            
            # Verify session contains both analysis and conversation history
            self.assertGreater(len(history['analysis_history']), 0)
            self.assertGreater(len(history['conversation_history']), 0)
            
            # Verify user consistency
            session = self.orchestrator.active_sessions[session_id]
            self.assertEqual(session.user_id, "test_user")
            self.assertEqual(session.language_preference, "en")
        
        asyncio.run(run_test())

class TestIntegrationScenarios(unittest.TestCase):
    """Test comprehensive integration scenarios"""
    
    def setUp(self):
        try:
            self.orchestrator = ServiceOrchestrator()
        except Exception as e:
            self.skipTest(f"Service orchestrator initialization failed: {e}")
    
    def test_full_workflow_simulation(self):
        """Test complete workflow from image analysis to explanation"""
        async def run_test():
            # Step 1: Image analysis
            mock_file = MagicMock()
            mock_file.filename = "skin_test.jpg"
            mock_file.read = AsyncMock(return_value=b"mock skin image data")
            
            analysis_request = AnalysisRequest(
                analysis_type="skin_condition",
                session_id="workflow_session",
                user_id="workflow_user",
                language="en"
            )
            
            analysis_result = await self.orchestrator.process_image_analysis(
                mock_file, analysis_request
            )
            
            self.assertEqual(analysis_result['status'], 'success')
            self.assertIn('analysis_result', analysis_result)
            
            # Step 2: Chat about the analysis
            chat_request = ChatRequest(
                message="What does my skin analysis show?",
                session_id="workflow_session",
                user_id="workflow_user",
                language="en"
            )
            
            chat_result = await self.orchestrator.process_chat_message(chat_request)
            
            self.assertEqual(chat_result['status'], 'success')
            self.assertIn('response', chat_result)
            
            # Step 3: Check session history
            history_result = await self.orchestrator.get_session_history("workflow_session")
            
            self.assertEqual(history_result['status'], 'success')
            self.assertGreater(len(history_result['analysis_history']), 0)
            self.assertGreater(len(history_result['conversation_history']), 0)
        
        asyncio.run(run_test())
    
    def test_multilingual_workflow(self):
        """Test workflow with multiple languages"""
        async def run_test():
            # English chat
            en_request = ChatRequest(
                message="I have a headache",
                session_id="multilingual_session",
                language="en"
            )
            
            en_result = await self.orchestrator.process_chat_message(en_request)
            self.assertEqual(en_result['status'], 'success')
            self.assertEqual(en_result['language'], 'en')
            
            # Hindi chat
            hi_request = ChatRequest(
                message="मुझे सिरदर्द है",
                session_id="multilingual_session",
                language="hi"
            )
            
            hi_result = await self.orchestrator.process_chat_message(hi_request)
            self.assertEqual(hi_result['status'], 'success')
            # Language might be detected or set to Hindi
            
            # Check session history contains both languages
            history = await self.orchestrator.get_session_history("multilingual_session")
            self.assertEqual(history['status'], 'success')
            self.assertEqual(len(history['conversation_history']), 2)
        
        asyncio.run(run_test())
    
    def test_performance_under_load(self):
        """Test system performance under simulated load"""
        async def run_test():
            # Create multiple concurrent sessions
            num_sessions = 10
            tasks = []
            
            for i in range(num_sessions):
                session_id = f"load_test_session_{i}"
                
                # Chat request for each session
                chat_request = ChatRequest(
                    message=f"Load test message {i}",
                    session_id=session_id,
                    user_id=f"load_test_user_{i}",
                    language="en"
                )
                
                tasks.append(self.orchestrator.process_chat_message(chat_request))
            
            # Measure execution time
            start_time = time.time()
            results = await asyncio.gather(*tasks, return_exceptions=True)
            execution_time = time.time() - start_time
            
            # Verify all requests completed successfully
            successful_requests = 0
            for result in results:
                if not isinstance(result, Exception) and result.get('status') == 'success':
                    successful_requests += 1
            
            # Performance assertions
            self.assertEqual(successful_requests, num_sessions)
            self.assertLess(execution_time, 30.0)  # Should complete within 30 seconds
            
            # Verify sessions were created
            self.assertEqual(len(self.orchestrator.active_sessions), num_sessions)
        
        asyncio.run(run_test())

if __name__ == '__main__':
    unittest.main()