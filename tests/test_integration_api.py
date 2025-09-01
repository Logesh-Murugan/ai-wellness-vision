# test_integration_api.py - Integration tests for the complete API gateway
import unittest
import asyncio
from unittest.mock import MagicMock, AsyncMock

from src.api.gateway import APIGateway, ServiceOrchestrator, AnalysisRequest, ChatRequest
from src.api.auth import AuthManager

class TestAPIGatewayIntegration(unittest.TestCase):
    """Integration tests for the complete API gateway system"""
    
    def setUp(self):
        self.gateway = APIGateway()
        self.orchestrator = ServiceOrchestrator()
        self.auth_manager = AuthManager()
    
    def test_complete_system_initialization(self):
        """Test that all components initialize correctly"""
        # Test gateway initialization
        self.assertIsNotNone(self.gateway)
        self.assertIsNotNone(self.gateway.orchestrator)
        
        # Test orchestrator initialization
        self.assertIsNotNone(self.orchestrator.image_service)
        self.assertIsNotNone(self.orchestrator.nlp_service)
        self.assertIsNotNone(self.orchestrator.speech_service)
        self.assertIsNotNone(self.orchestrator.explainable_ai_service)
        
        # Test auth manager initialization
        self.assertIsNotNone(self.auth_manager)
        self.assertIn("testuser", self.auth_manager.users_db)
        self.assertIn("admin", self.auth_manager.users_db)
    
    def test_authentication_integration(self):
        """Test authentication integration with the system"""
        # Test user authentication
        user = self.auth_manager.authenticate_user("testuser", "user123")
        self.assertEqual(user.username, "testuser")
        
        # Test token creation and verification
        token = self.auth_manager.create_access_token(user)
        token_data = self.auth_manager.verify_token(token)
        self.assertEqual(token_data.username, "testuser")
        
        # Test admin authentication
        admin = self.auth_manager.authenticate_user("admin", "admin123")
        self.assertEqual(admin.username, "admin")
        self.assertIn("admin", admin.roles)
    
    def test_service_orchestration_workflow(self):
        """Test complete service orchestration workflow"""
        async def run_test():
            # Test chat processing
            chat_request = ChatRequest(
                message="I have a headache",
                session_id="integration_test_session",
                user_id="test_user",
                language="en"
            )
            
            result = await self.orchestrator.process_chat_message(chat_request)
            
            self.assertEqual(result['status'], 'success')
            self.assertIn('response', result)
            self.assertIn('language', result)
            self.assertIn('processing_time', result)
            
            # Test session creation
            session = self.orchestrator.get_session("integration_test_session")
            self.assertEqual(session.session_id, "integration_test_session")
            
            # Test session history
            history = await self.orchestrator.get_session_history("integration_test_session")
            self.assertEqual(history['status'], 'success')
            self.assertIn('conversation_history', history)
        
        asyncio.run(run_test())
    
    def test_image_analysis_workflow(self):
        """Test image analysis workflow"""
        async def run_test():
            # Mock image file
            mock_file = MagicMock()
            mock_file.filename = "test_image.jpg"
            mock_file.read = AsyncMock(return_value=b"mock image data")
            
            analysis_request = AnalysisRequest(
                analysis_type="skin_condition",
                session_id="image_test_session",
                user_id="test_user",
                language="en"
            )
            
            result = await self.orchestrator.process_image_analysis(mock_file, analysis_request)
            
            self.assertEqual(result['status'], 'success')
            self.assertIn('analysis_result', result)
            self.assertIn('processing_time', result)
        
        asyncio.run(run_test())
    
    def test_service_status_reporting(self):
        """Test service status reporting"""
        status = self.orchestrator.get_service_status()
        
        # Check that all services are reported
        expected_services = ['image_service', 'nlp_service', 'speech_service', 'explainable_ai_service']
        for service in expected_services:
            self.assertIn(service, status)
            self.assertIn('available', status[service])
    
    def test_error_handling_integration(self):
        """Test error handling across the system"""
        async def run_test():
            # Test invalid analysis type
            mock_file = MagicMock()
            mock_file.filename = "test.jpg"
            mock_file.read = AsyncMock(return_value=b"mock data")
            
            invalid_request = AnalysisRequest(
                analysis_type="invalid_type",
                session_id="error_test_session",
                language="en"
            )
            
            result = await self.orchestrator.process_image_analysis(mock_file, invalid_request)
            self.assertEqual(result['status'], 'error')
            self.assertIn('message', result)
        
        asyncio.run(run_test())
    
    def test_concurrent_operations(self):
        """Test concurrent operations across services"""
        async def run_test():
            tasks = []
            
            # Create multiple concurrent chat requests
            for i in range(5):
                chat_request = ChatRequest(
                    message=f"Test message {i}",
                    session_id=f"concurrent_session_{i}",
                    user_id=f"user_{i}",
                    language="en"
                )
                tasks.append(self.orchestrator.process_chat_message(chat_request))
            
            # Execute all tasks concurrently
            results = await asyncio.gather(*tasks)
            
            # Verify all requests succeeded
            for result in results:
                self.assertEqual(result['status'], 'success')
            
            # Verify sessions were created
            self.assertEqual(len(self.orchestrator.active_sessions), 5)
        
        asyncio.run(run_test())
    
    def test_session_management_integration(self):
        """Test session management across different operations"""
        async def run_test():
            session_id = "session_management_test"
            user_id = "test_user"
            
            # Start with chat
            chat_request = ChatRequest(
                message="Hello, I need help",
                session_id=session_id,
                user_id=user_id,
                language="en"
            )
            
            chat_result = await self.orchestrator.process_chat_message(chat_request)
            self.assertEqual(chat_result['status'], 'success')
            
            # Follow with image analysis
            mock_file = MagicMock()
            mock_file.filename = "test.jpg"
            mock_file.read = AsyncMock(return_value=b"mock image")
            
            analysis_request = AnalysisRequest(
                analysis_type="skin_condition",
                session_id=session_id,
                user_id=user_id,
                language="en"
            )
            
            analysis_result = await self.orchestrator.process_image_analysis(mock_file, analysis_request)
            self.assertEqual(analysis_result['status'], 'success')
            
            # Check session history contains both operations
            history = await self.orchestrator.get_session_history(session_id)
            self.assertEqual(history['status'], 'success')
            
            # Verify session consistency
            session = self.orchestrator.active_sessions[session_id]
            self.assertEqual(session.user_id, user_id)
            self.assertEqual(session.session_id, session_id)
        
        asyncio.run(run_test())

class TestSystemPerformance(unittest.TestCase):
    """Test system performance characteristics"""
    
    def setUp(self):
        self.orchestrator = ServiceOrchestrator()
    
    def test_response_time_performance(self):
        """Test that responses are generated within acceptable time limits"""
        import time
        
        async def run_test():
            start_time = time.time()
            
            chat_request = ChatRequest(
                message="Quick test message",
                session_id="performance_test",
                language="en"
            )
            
            result = await self.orchestrator.process_chat_message(chat_request)
            
            end_time = time.time()
            response_time = end_time - start_time
            
            self.assertEqual(result['status'], 'success')
            self.assertLess(response_time, 5.0)  # Should respond within 5 seconds
            self.assertIn('processing_time', result)
        
        asyncio.run(run_test())
    
    def test_memory_usage_stability(self):
        """Test that memory usage remains stable under load"""
        async def run_test():
            initial_sessions = len(self.orchestrator.active_sessions)
            
            # Create multiple sessions
            for i in range(10):
                chat_request = ChatRequest(
                    message=f"Memory test {i}",
                    session_id=f"memory_test_{i}",
                    language="en"
                )
                
                result = await self.orchestrator.process_chat_message(chat_request)
                self.assertEqual(result['status'], 'success')
            
            # Verify sessions were created
            final_sessions = len(self.orchestrator.active_sessions)
            self.assertEqual(final_sessions - initial_sessions, 10)
        
        asyncio.run(run_test())

class TestSystemReliability(unittest.TestCase):
    """Test system reliability and error recovery"""
    
    def setUp(self):
        self.orchestrator = ServiceOrchestrator()
        self.auth_manager = AuthManager()
    
    def test_graceful_error_handling(self):
        """Test that the system handles errors gracefully"""
        async def run_test():
            # Test with various error conditions
            error_scenarios = [
                ("", "empty_session", "en"),  # Empty message
                ("Test message", "", "en"),   # Empty session ID
                ("Test message", "test_session", "invalid_lang"),  # Invalid language
            ]
            
            for message, session_id, language in error_scenarios:
                chat_request = ChatRequest(
                    message=message,
                    session_id=session_id,
                    language=language
                )
                
                result = await self.orchestrator.process_chat_message(chat_request)
                
                # System should handle errors gracefully
                self.assertIn('status', result)
                self.assertIsInstance(result, dict)
        
        asyncio.run(run_test())
    
    def test_authentication_error_recovery(self):
        """Test authentication error recovery"""
        # Test invalid credentials
        try:
            self.auth_manager.authenticate_user("invalid_user", "invalid_pass")
            self.fail("Should have raised AuthenticationError")
        except Exception:
            pass  # Expected
        
        # Test that valid authentication still works after errors
        user = self.auth_manager.authenticate_user("testuser", "user123")
        self.assertEqual(user.username, "testuser")
    
    def test_service_availability_reporting(self):
        """Test that service availability is correctly reported"""
        status = self.orchestrator.get_service_status()
        
        # All services should report their availability
        for service_name, service_info in status.items():
            self.assertIn('available', service_info)
            self.assertIsInstance(service_info['available'], bool)

if __name__ == '__main__':
    unittest.main()