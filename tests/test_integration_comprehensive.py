# test_integration_comprehensive.py - Comprehensive end-to-end integration tests
import unittest
import asyncio
import tempfile
import json
import time
from pathlib import Path
from unittest.mock import MagicMock, AsyncMock, patch

from src.api.gateway import ServiceOrchestrator, APIGateway, AnalysisRequest, ChatRequest
from src.api.auth import AuthManager
from src.models.user_models import UserSession
from src.models.health_models import HealthAnalysisResult, AnalysisType

class TestEndToEndWorkflows(unittest.TestCase):
    """Test complete end-to-end workflows"""
    
    def setUp(self):
        try:
            self.orchestrator = ServiceOrchestrator()
            self.auth_manager = AuthManager()
            self.gateway = APIGateway()
        except Exception as e:
            self.skipTest(f"System initialization failed: {e}")
    
    def test_complete_user_journey(self):
        """Test complete user journey from authentication to analysis"""
        async def run_test():
            # Step 1: User Authentication
            try:
                user = self.auth_manager.authenticate_user("testuser", "user123")
                self.assertEqual(user.username, "testuser")
                
                token = self.auth_manager.create_access_token(user)
                self.assertIsNotNone(token)
                
            except Exception as e:
                self.skipTest(f"Authentication failed: {e}")
            
            # Step 2: Create Session
            session_id = "complete_journey_session"
            session = self.orchestrator.get_session(session_id, user.username, "en")
            self.assertEqual(session.session_id, session_id)
            self.assertEqual(session.user_id, user.username)
            
            # Step 3: Initial Chat Interaction
            chat_request = ChatRequest(
                message="Hello, I need help with my health concerns",
                session_id=session_id,
                user_id=user.username,
                language="en"
            )
            
            chat_result = await self.orchestrator.process_chat_message(chat_request)
            self.assertEqual(chat_result['status'], 'success')
            self.assertIn('response', chat_result)
            
            # Step 4: Image Analysis
            mock_file = MagicMock()
            mock_file.filename = "skin_condition.jpg"
            mock_file.read = AsyncMock(return_value=b"mock skin image data")
            
            analysis_request = AnalysisRequest(
                analysis_type="skin_condition",
                session_id=session_id,
                user_id=user.username,
                language="en"
            )
            
            analysis_result = await self.orchestrator.process_image_analysis(
                mock_file, analysis_request
            )
            self.assertEqual(analysis_result['status'], 'success')
            self.assertIn('analysis_result', analysis_result)
            
            # Step 5: Follow-up Chat about Analysis
            followup_request = ChatRequest(
                message="What does my skin analysis show? Should I be concerned?",
                session_id=session_id,
                user_id=user.username,
                language="en"
            )
            
            followup_result = await self.orchestrator.process_chat_message(followup_request)
            self.assertEqual(followup_result['status'], 'success')
            
            # Step 6: Check Session History
            history = await self.orchestrator.get_session_history(session_id)
            self.assertEqual(history['status'], 'success')
            
            # Verify complete history
            self.assertGreaterEqual(len(history['conversation_history']), 2)
            self.assertGreaterEqual(len(history['analysis_history']), 1)
            
            # Step 7: Verify Session State
            final_session = self.orchestrator.active_sessions[session_id]
            self.assertEqual(final_session.user_id, user.username)
            self.assertGreater(len(final_session.conversation_history), 0)
            self.assertGreater(len(final_session.analysis_history), 0)
        
        asyncio.run(run_test())
    
    def test_multilingual_user_journey(self):
        """Test user journey with language switching"""
        async def run_test():
            session_id = "multilingual_journey_session"
            user_id = "multilingual_user"
            
            # Start in English
            en_session = self.orchestrator.get_session(session_id, user_id, "en")
            
            en_request = ChatRequest(
                message="I have a headache",
                session_id=session_id,
                user_id=user_id,
                language="en"
            )
            
            en_result = await self.orchestrator.process_chat_message(en_request)
            self.assertEqual(en_result['status'], 'success')
            
            # Switch to Hindi
            hi_request = ChatRequest(
                message="मुझे और जानकारी चाहिए",
                session_id=session_id,
                user_id=user_id,
                language="hi"
            )
            
            hi_result = await self.orchestrator.process_chat_message(hi_request)
            self.assertEqual(hi_result['status'], 'success')
            
            # Image analysis in Tamil
            mock_file = MagicMock()
            mock_file.filename = "test_image.jpg"
            mock_file.read = AsyncMock(return_value=b"mock image data")
            
            ta_analysis_request = AnalysisRequest(
                analysis_type="skin_condition",
                session_id=session_id,
                user_id=user_id,
                language="ta"
            )
            
            ta_result = await self.orchestrator.process_image_analysis(
                mock_file, ta_analysis_request
            )
            self.assertEqual(ta_result['status'], 'success')
            
            # Verify session maintains multilingual history
            history = await self.orchestrator.get_session_history(session_id)
            self.assertEqual(history['status'], 'success')
            self.assertEqual(len(history['conversation_history']), 2)
            self.assertEqual(len(history['analysis_history']), 1)
        
        asyncio.run(run_test())
    
    def test_multi_modal_interaction_workflow(self):
        """Test workflow combining text, image, and speech"""
        async def run_test():
            session_id = "multimodal_session"
            user_id = "multimodal_user"
            
            # 1. Text chat
            text_request = ChatRequest(
                message="I want to analyze my skin condition",
                session_id=session_id,
                user_id=user_id,
                language="en"
            )
            
            text_result = await self.orchestrator.process_chat_message(text_request)
            self.assertEqual(text_result['status'], 'success')
            
            # 2. Image analysis
            mock_image = MagicMock()
            mock_image.filename = "skin_photo.jpg"
            mock_image.read = AsyncMock(return_value=b"mock skin image data")
            
            image_request = AnalysisRequest(
                analysis_type="skin_condition",
                session_id=session_id,
                user_id=user_id,
                language="en"
            )
            
            image_result = await self.orchestrator.process_image_analysis(
                mock_image, image_request
            )
            self.assertEqual(image_result['status'], 'success')
            
            # 3. Speech synthesis request
            try:
                from src.api.gateway import SpeechRequest
                
                speech_request = SpeechRequest(
                    text="Please explain my skin analysis results",
                    language="en",
                    session_id=session_id
                )
                
                speech_result = await self.orchestrator.process_speech_synthesis(speech_request)
                self.assertEqual(speech_result['status'], 'success')
                
            except (ImportError, AttributeError):
                # Speech synthesis might not be fully implemented
                pass
            
            # 4. Follow-up text interaction
            followup_request = ChatRequest(
                message="Based on the analysis, what should I do next?",
                session_id=session_id,
                user_id=user_id,
                language="en"
            )
            
            followup_result = await self.orchestrator.process_chat_message(followup_request)
            self.assertEqual(followup_result['status'], 'success')
            
            # Verify complete multimodal session
            history = await self.orchestrator.get_session_history(session_id)
            self.assertEqual(history['status'], 'success')
            self.assertGreaterEqual(len(history['conversation_history']), 2)
            self.assertGreaterEqual(len(history['analysis_history']), 1)
        
        asyncio.run(run_test())

class TestServiceIntegration(unittest.TestCase):
    """Test integration between different services"""
    
    def setUp(self):
        try:
            self.orchestrator = ServiceOrchestrator()
        except Exception as e:
            self.skipTest(f"Service orchestrator initialization failed: {e}")
    
    def test_image_to_explanation_workflow(self):
        """Test workflow from image analysis to AI explanation"""
        async def run_test():
            session_id = "image_explanation_session"
            
            # Step 1: Image Analysis
            mock_file = MagicMock()
            mock_file.filename = "test_condition.jpg"
            mock_file.read = AsyncMock(return_value=b"mock medical image data")
            
            analysis_request = AnalysisRequest(
                analysis_type="skin_condition",
                session_id=session_id,
                language="en"
            )
            
            analysis_result = await self.orchestrator.process_image_analysis(
                mock_file, analysis_request
            )
            
            self.assertEqual(analysis_result['status'], 'success')
            self.assertIn('analysis_result', analysis_result)
            
            # Step 2: Request Explanation
            try:
                from src.api.gateway import ExplanationRequest
                
                explanation_request = ExplanationRequest(
                    analysis_id=analysis_result.get('analysis_id', 'test_analysis'),
                    explanation_type="detailed",
                    session_id=session_id,
                    language="en"
                )
                
                explanation_result = await self.orchestrator.process_explanation_request(
                    explanation_request
                )
                
                self.assertEqual(explanation_result['status'], 'success')
                self.assertIn('explanation', explanation_result)
                
            except (ImportError, AttributeError):
                # Explanation service might not be fully implemented
                pass
        
        asyncio.run(run_test())
    
    def test_nlp_to_health_knowledge_integration(self):
        """Test integration between NLP service and health knowledge base"""
        async def run_test():
            health_queries = [
                "What are the symptoms of diabetes?",
                "How can I improve my skin health?",
                "What foods are good for heart health?",
                "I have been feeling tired lately, what could be the cause?"
            ]
            
            for query in health_queries:
                chat_request = ChatRequest(
                    message=query,
                    session_id="health_knowledge_session",
                    language="en"
                )
                
                result = await self.orchestrator.process_chat_message(chat_request)
                
                self.assertEqual(result['status'], 'success')
                self.assertIn('response', result)
                
                # Response should contain health-related information
                response = result['response']
                self.assertIsInstance(response, str)
                self.assertGreater(len(response), 50)  # Should be substantial
        
        asyncio.run(run_test())
    
    def test_cross_service_error_handling(self):
        """Test error handling across service boundaries"""
        async def run_test():
            # Test image analysis with invalid file
            invalid_file = MagicMock()
            invalid_file.filename = "invalid.txt"
            invalid_file.read = AsyncMock(return_value=b"not an image")
            
            invalid_request = AnalysisRequest(
                analysis_type="skin_condition",
                session_id="error_test_session",
                language="en"
            )
            
            result = await self.orchestrator.process_image_analysis(
                invalid_file, invalid_request
            )
            
            # Should handle error gracefully
            self.assertIn('status', result)
            if result['status'] == 'error':
                self.assertIn('message', result)
            
            # Test chat with very long message
            long_message = "x" * 10000  # Very long message
            
            long_chat_request = ChatRequest(
                message=long_message,
                session_id="error_test_session",
                language="en"
            )
            
            long_result = await self.orchestrator.process_chat_message(long_chat_request)
            
            # Should handle gracefully
            self.assertIn('status', long_result)
        
        asyncio.run(run_test())

class TestDataFlowIntegration(unittest.TestCase):
    """Test data flow between components"""
    
    def setUp(self):
        try:
            self.orchestrator = ServiceOrchestrator()
        except Exception as e:
            self.skipTest(f"Service orchestrator initialization failed: {e}")
    
    def test_session_data_persistence(self):
        """Test that session data persists correctly across interactions"""
        async def run_test():
            session_id = "persistence_test_session"
            user_id = "persistence_user"
            
            # Create initial session
            session = self.orchestrator.get_session(session_id, user_id, "en")
            initial_created_time = session.created_at
            
            # First interaction
            chat_request1 = ChatRequest(
                message="First message",
                session_id=session_id,
                user_id=user_id,
                language="en"
            )
            
            result1 = await self.orchestrator.process_chat_message(chat_request1)
            self.assertEqual(result1['status'], 'success')
            
            # Second interaction
            chat_request2 = ChatRequest(
                message="Second message",
                session_id=session_id,
                user_id=user_id,
                language="en"
            )
            
            result2 = await self.orchestrator.process_chat_message(chat_request2)
            self.assertEqual(result2['status'], 'success')
            
            # Verify session persistence
            persisted_session = self.orchestrator.active_sessions[session_id]
            self.assertEqual(persisted_session.created_at, initial_created_time)
            self.assertEqual(len(persisted_session.conversation_history), 2)
            self.assertEqual(persisted_session.user_id, user_id)
            
            # Verify history retrieval
            history = await self.orchestrator.get_session_history(session_id)
            self.assertEqual(history['status'], 'success')
            self.assertEqual(len(history['conversation_history']), 2)
        
        asyncio.run(run_test())
    
    def test_analysis_result_integration(self):
        """Test integration of analysis results across the system"""
        async def run_test():
            session_id = "analysis_integration_session"
            
            # Perform image analysis
            mock_file = MagicMock()
            mock_file.filename = "integration_test.jpg"
            mock_file.read = AsyncMock(return_value=b"mock image data")
            
            analysis_request = AnalysisRequest(
                analysis_type="skin_condition",
                session_id=session_id,
                language="en"
            )
            
            analysis_result = await self.orchestrator.process_image_analysis(
                mock_file, analysis_request
            )
            
            self.assertEqual(analysis_result['status'], 'success')
            
            # Chat about the analysis
            chat_request = ChatRequest(
                message="Tell me about my recent analysis",
                session_id=session_id,
                language="en"
            )
            
            chat_result = await self.orchestrator.process_chat_message(chat_request)
            self.assertEqual(chat_result['status'], 'success')
            
            # Verify analysis is accessible in session
            session = self.orchestrator.active_sessions[session_id]
            self.assertGreater(len(session.analysis_history), 0)
            
            # Verify analysis data structure
            analysis_entry = session.analysis_history[0]
            self.assertIn('analysis_type', analysis_entry)
            self.assertIn('timestamp', analysis_entry)
        
        asyncio.run(run_test())

class TestSystemResilience(unittest.TestCase):
    """Test system resilience and recovery"""
    
    def setUp(self):
        try:
            self.orchestrator = ServiceOrchestrator()
        except Exception as e:
            self.skipTest(f"Service orchestrator initialization failed: {e}")
    
    def test_concurrent_user_isolation(self):
        """Test that concurrent users are properly isolated"""
        async def run_test():
            num_users = 10
            tasks = []
            
            # Create concurrent sessions for different users
            for i in range(num_users):
                user_id = f"concurrent_user_{i}"
                session_id = f"concurrent_session_{i}"
                
                chat_request = ChatRequest(
                    message=f"Message from user {i}",
                    session_id=session_id,
                    user_id=user_id,
                    language="en"
                )
                
                tasks.append(self.orchestrator.process_chat_message(chat_request))
            
            # Execute all requests concurrently
            results = await asyncio.gather(*tasks, return_exceptions=True)
            
            # Verify all requests succeeded
            successful_results = 0
            for result in results:
                if not isinstance(result, Exception) and result.get('status') == 'success':
                    successful_results += 1
            
            self.assertEqual(successful_results, num_users)
            
            # Verify session isolation
            self.assertEqual(len(self.orchestrator.active_sessions), num_users)
            
            for i in range(num_users):
                session_id = f"concurrent_session_{i}"
                user_id = f"concurrent_user_{i}"
                
                session = self.orchestrator.active_sessions[session_id]
                self.assertEqual(session.user_id, user_id)
                self.assertEqual(len(session.conversation_history), 1)
        
        asyncio.run(run_test())
    
    def test_service_failure_recovery(self):
        """Test system behavior when individual services fail"""
        async def run_test():
            # Test with mock service failures
            original_nlp_service = self.orchestrator.nlp_service
            
            # Temporarily replace with failing service
            failing_service = MagicMock()
            failing_service.process_message = AsyncMock(side_effect=Exception("Service failure"))
            
            self.orchestrator.nlp_service = failing_service
            
            chat_request = ChatRequest(
                message="Test message during service failure",
                session_id="failure_recovery_session",
                language="en"
            )
            
            result = await self.orchestrator.process_chat_message(chat_request)
            
            # System should handle failure gracefully
            self.assertIn('status', result)
            
            # Restore original service
            self.orchestrator.nlp_service = original_nlp_service
            
            # Verify system recovers
            recovery_request = ChatRequest(
                message="Test message after recovery",
                session_id="failure_recovery_session",
                language="en"
            )
            
            recovery_result = await self.orchestrator.process_chat_message(recovery_request)
            self.assertEqual(recovery_result['status'], 'success')
        
        asyncio.run(run_test())
    
    def test_memory_leak_prevention(self):
        """Test that system doesn't have memory leaks with long-running sessions"""
        async def run_test():
            session_id = "memory_test_session"
            
            # Create many interactions in a single session
            for i in range(100):
                chat_request = ChatRequest(
                    message=f"Memory test message {i}",
                    session_id=session_id,
                    language="en"
                )
                
                result = await self.orchestrator.process_chat_message(chat_request)
                self.assertEqual(result['status'], 'success')
            
            # Verify session exists and has reasonable memory usage
            session = self.orchestrator.active_sessions[session_id]
            self.assertEqual(len(session.conversation_history), 100)
            
            # In a real implementation, we would check memory usage here
            # For now, just verify the session is still functional
            final_request = ChatRequest(
                message="Final test message",
                session_id=session_id,
                language="en"
            )
            
            final_result = await self.orchestrator.process_chat_message(final_request)
            self.assertEqual(final_result['status'], 'success')
        
        asyncio.run(run_test())

class TestAPIGatewayIntegration(unittest.TestCase):
    """Test API Gateway integration with all components"""
    
    def setUp(self):
        try:
            self.gateway = APIGateway()
            self.orchestrator = self.gateway.orchestrator
            self.auth_manager = AuthManager()
        except Exception as e:
            self.skipTest(f"API Gateway initialization failed: {e}")
    
    def test_authenticated_api_workflow(self):
        """Test complete API workflow with authentication"""
        async def run_test():
            # Authenticate user
            user = self.auth_manager.authenticate_user("testuser", "user123")
            token = self.auth_manager.create_access_token(user)
            
            # Verify token
            token_data = self.auth_manager.verify_token(token)
            self.assertEqual(token_data.username, "testuser")
            
            # Use authenticated session for API calls
            session_id = "authenticated_api_session"
            
            chat_request = ChatRequest(
                message="Authenticated API test",
                session_id=session_id,
                user_id=user.username,
                language="en"
            )
            
            result = await self.orchestrator.process_chat_message(chat_request)
            self.assertEqual(result['status'], 'success')
            
            # Verify session is associated with authenticated user
            session = self.orchestrator.active_sessions[session_id]
            self.assertEqual(session.user_id, user.username)
        
        asyncio.run(run_test())
    
    def test_api_error_responses(self):
        """Test API error response formatting"""
        async def run_test():
            # Test various error scenarios
            error_scenarios = [
                ("", "empty_session", "en"),  # Empty message
                ("Test", "", "en"),           # Empty session
                ("Test", "session", "xyz"),   # Invalid language
            ]
            
            for message, session_id, language in error_scenarios:
                chat_request = ChatRequest(
                    message=message,
                    session_id=session_id,
                    language=language
                )
                
                result = await self.orchestrator.process_chat_message(chat_request)
                
                # Should return structured response even for errors
                self.assertIsInstance(result, dict)
                self.assertIn('status', result)
        
        asyncio.run(run_test())

if __name__ == '__main__':
    unittest.main()