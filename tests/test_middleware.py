# test_middleware.py - Tests for API middleware
import unittest
import time
import asyncio
from unittest.mock import MagicMock, AsyncMock, patch
from datetime import datetime

from src.api.middleware import (
    RateLimitMiddleware, SecurityMiddleware, LoggingMiddleware,
    ValidationMiddleware, HealthCheckMiddleware, setup_middleware
)

class MockRequest:
    """Mock request object for testing"""
    def __init__(self, method="GET", path="/test", client_host="127.0.0.1", headers=None):
        self.method = method
        self.url = MagicMock()
        self.url.path = path
        self.url.query = ""
        self.client = MagicMock()
        self.client.host = client_host
        self.headers = headers or {}

class MockResponse:
    """Mock response object for testing"""
    def __init__(self, status_code=200, content="OK"):
        self.status_code = status_code
        self.content = content
        self.headers = {}

class TestRateLimitMiddleware(unittest.TestCase):
    """Test rate limiting middleware"""
    
    def setUp(self):
        self.middleware = RateLimitMiddleware(None, requests_per_minute=5, requests_per_hour=20)
    
    def test_rate_limit_initialization(self):
        """Test rate limit middleware initialization"""
        self.assertEqual(self.middleware.requests_per_minute, 5)
        self.assertEqual(self.middleware.requests_per_hour, 20)
        self.assertIsInstance(self.middleware.request_history, dict)
    
    def test_client_ip_extraction(self):
        """Test client IP extraction from request"""
        # Test direct client IP
        request = MockRequest(client_host="192.168.1.100")
        ip = self.middleware._get_client_ip(request)
        self.assertEqual(ip, "192.168.1.100")
        
        # Test X-Forwarded-For header
        request = MockRequest(headers={"X-Forwarded-For": "203.0.113.1, 192.168.1.100"})
        ip = self.middleware._get_client_ip(request)
        self.assertEqual(ip, "203.0.113.1")
        
        # Test X-Real-IP header
        request = MockRequest(headers={"X-Real-IP": "203.0.113.2"})
        ip = self.middleware._get_client_ip(request)
        self.assertEqual(ip, "203.0.113.2")
    
    def test_rate_limiting_logic(self):
        """Test rate limiting logic"""
        client_ip = "192.168.1.100"
        current_time = time.time()
        
        # Should not be rate limited initially
        self.assertFalse(self.middleware._is_rate_limited(client_ip, current_time))
        
        # Record requests up to the limit
        for i in range(5):
            self.middleware._record_request(client_ip, current_time)
        
        # Should be rate limited after exceeding minute limit
        self.assertTrue(self.middleware._is_rate_limited(client_ip, current_time))
    
    def test_request_history_cleanup(self):
        """Test cleanup of old request timestamps"""
        client_ip = "192.168.1.100"
        current_time = time.time()
        old_time = current_time - 3700  # More than 1 hour ago
        
        # Add old requests
        history = self.middleware.request_history[client_ip]
        history['hour'].append(old_time)
        history['minute'].append(old_time)
        
        # Clean up old requests
        self.middleware._clean_old_requests(history, current_time)
        
        # Old requests should be removed
        self.assertEqual(len(history['hour']), 0)
        self.assertEqual(len(history['minute']), 0)
    
    def test_remaining_requests_calculation(self):
        """Test remaining requests calculation"""
        client_ip = "192.168.1.100"
        
        # Initially should have full quota
        remaining_minute = self.middleware._get_remaining_requests(client_ip, 'minute')
        remaining_hour = self.middleware._get_remaining_requests(client_ip, 'hour')
        
        self.assertEqual(remaining_minute, 5)
        self.assertEqual(remaining_hour, 20)
        
        # After recording some requests
        current_time = time.time()
        for i in range(2):
            self.middleware._record_request(client_ip, current_time)
        
        remaining_minute = self.middleware._get_remaining_requests(client_ip, 'minute')
        remaining_hour = self.middleware._get_remaining_requests(client_ip, 'hour')
        
        self.assertEqual(remaining_minute, 3)
        self.assertEqual(remaining_hour, 18)

class TestSecurityMiddleware(unittest.TestCase):
    """Test security middleware"""
    
    def setUp(self):
        self.middleware = SecurityMiddleware(None)
    
    def test_security_headers_configuration(self):
        """Test security headers configuration"""
        expected_headers = [
            "X-Content-Type-Options",
            "X-Frame-Options", 
            "X-XSS-Protection",
            "Strict-Transport-Security",
            "Referrer-Policy",
            "Content-Security-Policy"
        ]
        
        for header in expected_headers:
            self.assertIn(header, self.middleware.security_headers)
    
    def test_request_id_generation(self):
        """Test request ID generation"""
        request = MockRequest(path="/api/test", client_host="192.168.1.100")
        
        request_id = self.middleware._generate_request_id(request)
        
        self.assertIsInstance(request_id, str)
        self.assertEqual(len(request_id), 16)  # MD5 hash truncated to 16 chars
    
    def test_unique_request_ids(self):
        """Test that request IDs are unique"""
        request1 = MockRequest(path="/api/test1")
        request2 = MockRequest(path="/api/test2")
        
        id1 = self.middleware._generate_request_id(request1)
        id2 = self.middleware._generate_request_id(request2)
        
        self.assertNotEqual(id1, id2)

class TestValidationMiddleware(unittest.TestCase):
    """Test validation middleware"""
    
    def setUp(self):
        self.middleware = ValidationMiddleware(None)
    
    def test_allowed_content_types(self):
        """Test allowed content types configuration"""
        expected_types = [
            'application/json',
            'multipart/form-data',
            'image/jpeg',
            'image/png',
            'audio/wav'
        ]
        
        for content_type in expected_types:
            self.assertIn(content_type, self.middleware.allowed_content_types)
    
    def test_malicious_pattern_detection(self):
        """Test malicious pattern detection"""
        malicious_inputs = [
            "<script>alert('xss')</script>",
            "javascript:alert('xss')",
            "onload=alert('xss')",
            "eval(malicious_code)",
            "../../../etc/passwd",
            "..\\..\\windows\\system32"
        ]
        
        for malicious_input in malicious_inputs:
            self.assertTrue(
                self.middleware._contains_malicious_patterns(malicious_input),
                f"Failed to detect malicious pattern: {malicious_input}"
            )
    
    def test_safe_input_validation(self):
        """Test that safe inputs are not flagged as malicious"""
        safe_inputs = [
            "Hello, how are you?",
            "I have a headache and need help",
            "user@example.com",
            "My skin condition is getting better",
            "Can you analyze this image?"
        ]
        
        for safe_input in safe_inputs:
            self.assertFalse(
                self.middleware._contains_malicious_patterns(safe_input),
                f"Safe input incorrectly flagged as malicious: {safe_input}"
            )

class TestLoggingMiddleware(unittest.TestCase):
    """Test logging middleware"""
    
    def setUp(self):
        self.middleware = LoggingMiddleware(None)
    
    def test_sensitive_headers_configuration(self):
        """Test sensitive headers are properly configured"""
        sensitive_headers = ['authorization', 'cookie', 'x-api-key']
        
        for header in sensitive_headers:
            self.assertIn(header, self.middleware.sensitive_headers)
    
    def test_log_body_size_limit(self):
        """Test log body size limit configuration"""
        self.assertEqual(self.middleware.log_body_max_size, 1000)
    
    @patch('src.api.middleware.logger')
    def test_request_logging(self, mock_logger):
        """Test request logging functionality"""
        request = MockRequest(method="POST", path="/api/test", client_host="192.168.1.100")
        request_id = "test_request_123"
        
        # Test request logging
        asyncio.run(self.middleware._log_request(request, request_id))
        
        # Verify logging was called
        mock_logger.info.assert_called()
        call_args = mock_logger.info.call_args[0][0]
        self.assertIn("POST", call_args)
        self.assertIn("/api/test", call_args)
        self.assertIn("192.168.1.100", call_args)
    
    @patch('src.api.middleware.logger')
    def test_response_logging(self, mock_logger):
        """Test response logging functionality"""
        request = MockRequest(method="GET", path="/api/status")
        response = MockResponse(status_code=200)
        processing_time = 0.123
        request_id = "test_request_456"
        
        # Test response logging
        self.middleware._log_response(request, response, processing_time, request_id)
        
        # Verify logging was called
        mock_logger.info.assert_called()
        call_args = mock_logger.info.call_args[0][0]
        self.assertIn("GET", call_args)
        self.assertIn("/api/status", call_args)
        self.assertIn("200", call_args)
        self.assertIn("0.123", call_args)
    
    @patch('src.api.middleware.logger')
    def test_slow_request_logging(self, mock_logger):
        """Test slow request warning logging"""
        request = MockRequest(method="POST", path="/api/slow")
        response = MockResponse(status_code=200)
        processing_time = 6.0  # Exceeds 5 second threshold
        request_id = "slow_request_789"
        
        # Test slow request logging
        self.middleware._log_response(request, response, processing_time, request_id)
        
        # Verify warning was logged
        mock_logger.warning.assert_called()
        warning_args = mock_logger.warning.call_args[0][0]
        self.assertIn("Slow request", warning_args)
        self.assertIn("6.0", warning_args)

class TestHealthCheckMiddleware(unittest.TestCase):
    """Test health check middleware"""
    
    def setUp(self):
        self.middleware = HealthCheckMiddleware(None)
    
    def test_health_stats_initialization(self):
        """Test health statistics initialization"""
        self.assertEqual(self.middleware.request_count, 0)
        self.assertEqual(self.middleware.error_count, 0)
        self.assertIsInstance(self.middleware.start_time, float)
    
    def test_health_stats_calculation(self):
        """Test health statistics calculation"""
        # Simulate some requests and errors
        self.middleware.request_count = 100
        self.middleware.error_count = 5
        
        stats = self.middleware.get_health_stats()
        
        self.assertEqual(stats['total_requests'], 100)
        self.assertEqual(stats['total_errors'], 5)
        self.assertEqual(stats['error_rate'], 0.05)
        self.assertEqual(stats['status'], 'healthy')  # Error rate < 0.1
    
    def test_degraded_status_calculation(self):
        """Test degraded status when error rate is high"""
        # Simulate high error rate
        self.middleware.request_count = 100
        self.middleware.error_count = 15  # 15% error rate
        
        stats = self.middleware.get_health_stats()
        
        self.assertEqual(stats['error_rate'], 0.15)
        self.assertEqual(stats['status'], 'degraded')  # Error rate >= 0.1
    
    def test_uptime_calculation(self):
        """Test uptime calculation"""
        # Set start time to 1 hour ago
        self.middleware.start_time = time.time() - 3600
        
        stats = self.middleware.get_health_stats()
        
        self.assertGreaterEqual(stats['uptime_seconds'], 3600)
        self.assertLess(stats['uptime_seconds'], 3700)  # Allow some margin

class TestMiddlewareIntegration(unittest.TestCase):
    """Test middleware integration scenarios"""
    
    def test_middleware_setup(self):
        """Test middleware setup function"""
        mock_app = MagicMock()
        
        # Test middleware setup
        setup_middleware(mock_app)
        
        # Verify middleware was added to app
        self.assertGreater(mock_app.add_middleware.call_count, 0)
    
    def test_middleware_order(self):
        """Test that middleware is added in correct order"""
        mock_app = MagicMock()
        
        setup_middleware(mock_app)
        
        # Get the middleware classes that were added
        added_middleware = [
            call[0][0] for call in mock_app.add_middleware.call_args_list
        ]
        
        # Verify expected middleware classes are present
        expected_middleware = [
            RateLimitMiddleware,
            SecurityMiddleware,
            LoggingMiddleware,
            ValidationMiddleware,
            HealthCheckMiddleware
        ]
        
        for middleware_class in expected_middleware:
            self.assertIn(middleware_class, added_middleware)

class TestMiddlewareErrorHandling(unittest.TestCase):
    """Test middleware error handling"""
    
    def setUp(self):
        self.rate_limit_middleware = RateLimitMiddleware(None)
        self.security_middleware = SecurityMiddleware(None)
        self.validation_middleware = ValidationMiddleware(None)
    
    def test_rate_limit_middleware_error_handling(self):
        """Test rate limit middleware handles errors gracefully"""
        # This test would require mocking the actual dispatch method
        # For now, we test that the middleware doesn't crash on invalid input
        
        invalid_request = MagicMock()
        invalid_request.client = None  # This should cause an error
        
        # The middleware should handle this gracefully
        try:
            ip = self.rate_limit_middleware._get_client_ip(invalid_request)
            self.assertEqual(ip, "unknown")
        except Exception as e:
            self.fail(f"Rate limit middleware should handle errors gracefully: {e}")
    
    def test_validation_middleware_pattern_matching_errors(self):
        """Test validation middleware handles regex errors"""
        # Test with potentially problematic regex input
        problematic_inputs = [
            None,
            "",
            "a" * 10000,  # Very long string
            "\x00\x01\x02",  # Binary data
        ]
        
        for test_input in problematic_inputs:
            try:
                if test_input is not None:
                    result = self.validation_middleware._contains_malicious_patterns(test_input)
                    self.assertIsInstance(result, bool)
            except Exception as e:
                self.fail(f"Validation middleware should handle problematic input gracefully: {e}")

if __name__ == '__main__':
    unittest.main()