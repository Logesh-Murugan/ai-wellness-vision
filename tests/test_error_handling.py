# test_error_handling.py - Tests for comprehensive error handling system
import pytest
import time
from unittest.mock import Mock, patch, MagicMock
from datetime import datetime, timedelta

from src.utils.error_handling import (
    ErrorHandler, FallbackManager, ApplicationError, ErrorContext,
    ErrorCode, ErrorSeverity, handle_error, with_fallback,
    get_error_handler, get_fallback_manager
)

class TestErrorCode:
    """Test error code enumeration"""
    
    def test_error_code_values(self):
        """Test error code values are properly defined"""
        assert ErrorCode.UNKNOWN_ERROR.value == "E1000"
        assert ErrorCode.IMAGE_UPLOAD_ERROR.value == "E2000"
        assert ErrorCode.TEXT_PROCESSING_ERROR.value == "E3000"
        assert ErrorCode.AUDIO_UPLOAD_ERROR.value == "E4000"
        assert ErrorCode.API_REQUEST_ERROR.value == "E5000"
        assert ErrorCode.DATABASE_ERROR.value == "E6000"
        assert ErrorCode.ENCRYPTION_ERROR.value == "E7000"
        assert ErrorCode.OFFLINE_MODE_ERROR.value == "E8000"
    
    def test_error_code_categories(self):
        """Test error codes are properly categorized"""
        # General errors (1000-1999)
        assert ErrorCode.VALIDATION_ERROR.value.startswith("E1")
        
        # Image processing errors (2000-2999)
        assert ErrorCode.IMAGE_PROCESSING_ERROR.value.startswith("E2")
        
        # NLP errors (3000-3999)
        assert ErrorCode.LANGUAGE_DETECTION_ERROR.value.startswith("E3")
        
        # Speech processing errors (4000-4999)
        assert ErrorCode.SPEECH_TO_TEXT_ERROR.value.startswith("E4")

class TestErrorContext:
    """Test error context functionality"""
    
    def test_error_context_creation(self):
        """Test creating error context"""
        context = ErrorContext(
            user_id="user123",
            session_id="session456",
            service_name="image_service",
            function_name="analyze_image"
        )
        
        assert context.user_id == "user123"
        assert context.session_id == "session456"
        assert context.service_name == "image_service"
        assert context.function_name == "analyze_image"
    
    def test_error_context_defaults(self):
        """Test error context with default values"""
        context = ErrorContext()
        
        assert context.user_id is None
        assert context.session_id is None
        assert context.additional_context == {}

class TestApplicationError:
    """Test application error functionality"""
    
    def test_application_error_creation(self):
        """Test creating application error"""
        context = ErrorContext(user_id="user123")
        error = ApplicationError(
            error_code=ErrorCode.IMAGE_UPLOAD_ERROR,
            message="Failed to upload image",
            severity=ErrorSeverity.MEDIUM,
            timestamp=datetime.now(),
            context=context
        )
        
        assert error.error_code == ErrorCode.IMAGE_UPLOAD_ERROR
        assert error.message == "Failed to upload image"
        assert error.severity == ErrorSeverity.MEDIUM
        assert error.context.user_id == "user123"
        assert error.recovery_possible  # Default True
    
    def test_application_error_to_dict(self):
        """Test converting application error to dictionary"""
        context = ErrorContext(user_id="user123", service_name="test_service")
        error = ApplicationError(
            error_code=ErrorCode.VALIDATION_ERROR,
            message="Validation failed",
            severity=ErrorSeverity.LOW,
            timestamp=datetime.now(),
            context=context,
            user_message="Please check your input",
            suggested_actions=["Check format", "Try again"]
        )
        
        error_dict = error.to_dict()
        
        assert error_dict["error_code"] == "E1001"
        assert error_dict["message"] == "Validation failed"
        assert error_dict["severity"] == "low"
        assert error_dict["user_message"] == "Please check your input"
        assert "Check format" in error_dict["suggested_actions"]
        assert error_dict["context"]["user_id"] == "user123"
    
    def test_application_error_to_json(self):
        """Test converting application error to JSON"""
        context = ErrorContext(user_id="user123")
        error = ApplicationError(
            error_code=ErrorCode.NETWORK_ERROR,
            message="Network connection failed",
            severity=ErrorSeverity.HIGH,
            timestamp=datetime.now(),
            context=context
        )
        
        json_str = error.to_json()
        
        assert isinstance(json_str, str)
        assert "E5001" in json_str
        assert "Network connection failed" in json_str
        assert "high" in json_str

class TestErrorHandler:
    """Test error handler functionality"""
    
    def setup_method(self):
        """Set up test fixtures"""
        self.handler = ErrorHandler()
    
    def test_error_handler_initialization(self):
        """Test error handler initialization"""
        assert len(self.handler.error_history) == 0
        assert self.handler.max_history_size == 1000
        assert len(self.handler.fallback_messages) > 0
    
    def test_handle_error_basic(self):
        """Test basic error handling"""
        context = ErrorContext(user_id="test_user")
        
        app_error = self.handler.handle_error(
            ErrorCode.IMAGE_UPLOAD_ERROR,
            "Test error message",
            ErrorSeverity.MEDIUM,
            context
        )
        
        assert isinstance(app_error, ApplicationError)
        assert app_error.error_code == ErrorCode.IMAGE_UPLOAD_ERROR
        assert app_error.message == "Test error message"
        assert app_error.severity == ErrorSeverity.MEDIUM
        assert app_error.context.user_id == "test_user"
        
        # Should be added to history
        assert len(self.handler.error_history) == 1
        assert self.handler.error_history[0] == app_error
    
    def test_handle_error_with_exception(self):
        """Test error handling with original exception"""
        original_exception = ValueError("Original error")
        context = ErrorContext(service_name="test_service")
        
        app_error = self.handler.handle_error(
            ErrorCode.VALIDATION_ERROR,
            "Validation failed",
            ErrorSeverity.HIGH,
            context,
            original_exception
        )
        
        assert app_error.original_exception == original_exception
        assert app_error.stack_trace is not None
        assert "ValueError" in app_error.stack_trace
    
    def test_fallback_messages(self):
        """Test fallback message assignment"""
        app_error = self.handler.handle_error(
            ErrorCode.IMAGE_UPLOAD_ERROR,
            "Upload failed"
        )
        
        assert app_error.user_message is not None
        assert "image" in app_error.user_message.lower()
        assert len(app_error.suggested_actions) > 0
    
    def test_error_callbacks(self):
        """Test error callbacks"""
        callback_called = False
        callback_error = None
        
        def test_callback(error):
            nonlocal callback_called, callback_error
            callback_called = True
            callback_error = error
        
        self.handler.register_callback(test_callback)
        
        app_error = self.handler.handle_error(
            ErrorCode.NETWORK_ERROR,
            "Network test error"
        )
        
        assert callback_called
        assert callback_error == app_error
    
    def test_error_statistics(self):
        """Test error statistics generation"""
        # Generate some test errors
        for i in range(5):
            self.handler.handle_error(
                ErrorCode.IMAGE_PROCESSING_ERROR,
                f"Error {i}",
                ErrorSeverity.MEDIUM
            )
        
        for i in range(3):
            self.handler.handle_error(
                ErrorCode.NETWORK_ERROR,
                f"Network error {i}",
                ErrorSeverity.HIGH
            )
        
        stats = self.handler.get_error_statistics()
        
        assert stats["total_errors"] == 8
        assert stats["by_severity"]["medium"] == 5
        assert stats["by_severity"]["high"] == 3
        assert len(stats["recent_errors"]) == 8
        assert len(stats["most_common_errors"]) > 0
    
    def test_history_size_limit(self):
        """Test error history size limit"""
        # Set small limit for testing
        self.handler.max_history_size = 5
        
        # Generate more errors than limit
        for i in range(10):
            self.handler.handle_error(
                ErrorCode.UNKNOWN_ERROR,
                f"Error {i}"
            )
        
        # Should only keep last 5
        assert len(self.handler.error_history) == 5
        assert self.handler.error_history[-1].message == "Error 9"
    
    def test_clear_history(self):
        """Test clearing error history"""
        # Add some errors
        for i in range(3):
            self.handler.handle_error(ErrorCode.UNKNOWN_ERROR, f"Error {i}")
        
        assert len(self.handler.error_history) == 3
        
        self.handler.clear_history()
        assert len(self.handler.error_history) == 0

class TestFallbackManager:
    """Test fallback manager functionality"""
    
    def setup_method(self):
        """Set up test fixtures"""
        self.manager = FallbackManager()
    
    def test_register_fallback(self):
        """Test registering fallback function"""
        def mock_fallback():
            return "fallback_result"
        
        self.manager.register_fallback("test_service", mock_fallback)
        
        assert "test_service" in self.manager.fallback_strategies
        assert "test_service" in self.manager.circuit_breakers
        assert self.manager.circuit_breakers["test_service"]["state"] == "closed"
    
    def test_execute_with_fallback_success(self):
        """Test successful execution without fallback"""
        def primary_func():
            return "primary_result"
        
        def fallback_func():
            return "fallback_result"
        
        self.manager.register_fallback("test_service", fallback_func)
        
        result = self.manager.execute_with_fallback("test_service", primary_func)
        
        assert result == "primary_result"
        assert self.manager.circuit_breakers["test_service"]["failures"] == 0
    
    def test_execute_with_fallback_failure(self):
        """Test fallback execution on primary failure"""
        def primary_func():
            raise Exception("Primary failed")
        
        def fallback_func():
            return "fallback_result"
        
        self.manager.register_fallback("test_service", fallback_func)
        
        result = self.manager.execute_with_fallback("test_service", primary_func)
        
        assert result == "fallback_result"
        assert self.manager.circuit_breakers["test_service"]["failures"] == 1
    
    def test_circuit_breaker_opening(self):
        """Test circuit breaker opening after max failures"""
        def primary_func():
            raise Exception("Always fails")
        
        def fallback_func():
            return "fallback_result"
        
        self.manager.register_fallback("test_service", fallback_func, max_failures=3)
        
        # Trigger failures to open circuit breaker
        for i in range(5):
            result = self.manager.execute_with_fallback("test_service", primary_func)
            assert result == "fallback_result"
        
        # Circuit breaker should be open
        circuit_breaker = self.manager.circuit_breakers["test_service"]
        assert circuit_breaker["state"] == "open"
        assert circuit_breaker["failures"] >= 3
    
    def test_circuit_breaker_status(self):
        """Test getting circuit breaker status"""
        def fallback_func():
            return "fallback"
        
        self.manager.register_fallback("service1", fallback_func)
        self.manager.register_fallback("service2", fallback_func)
        
        status = self.manager.get_circuit_breaker_status()
        
        assert "service1" in status
        assert "service2" in status
        assert status["service1"]["state"] == "closed"
        assert status["service1"]["failures"] == 0
    
    def test_no_fallback_registered(self):
        """Test execution with no fallback registered"""
        def primary_func():
            raise Exception("Primary failed")
        
        with pytest.raises(ApplicationError) as exc_info:
            self.manager.execute_with_fallback("unregistered_service", primary_func)
        
        assert exc_info.value.error_code == ErrorCode.SERVICE_UNAVAILABLE
        assert "No fallback available" in exc_info.value.message

class TestErrorHandlingIntegration:
    """Integration tests for error handling system"""
    
    def test_global_error_handler(self):
        """Test global error handler function"""
        context = ErrorContext(user_id="global_test")
        
        app_error = handle_error(
            ErrorCode.API_REQUEST_ERROR,
            "Global error test",
            ErrorSeverity.MEDIUM,
            context
        )
        
        assert isinstance(app_error, ApplicationError)
        assert app_error.error_code == ErrorCode.API_REQUEST_ERROR
        
        # Should be in global handler history
        global_handler = get_error_handler()
        assert len(global_handler.error_history) > 0
    
    def test_with_fallback_decorator(self):
        """Test with_fallback decorator"""
        def fallback_func():
            return "fallback_executed"
        
        fallback_manager = get_fallback_manager()
        fallback_manager.register_fallback("decorated_service", fallback_func)
        
        @with_fallback("decorated_service")
        def decorated_function():
            raise Exception("Function failed")
        
        result = decorated_function()
        assert result == "fallback_executed"
    
    def test_error_handling_with_logging(self):
        """Test error handling integrates with logging"""
        with patch('src.utils.error_handling.logger') as mock_logger:
            handle_error(
                ErrorCode.CRITICAL,
                "Critical error test",
                ErrorSeverity.CRITICAL
            )
            
            # Should log critical error
            mock_logger.critical.assert_called()
    
    def test_comprehensive_error_flow(self):
        """Test complete error handling flow"""
        # Setup callback
        callback_errors = []
        
        def error_callback(error):
            callback_errors.append(error)
        
        handler = get_error_handler()
        handler.register_callback(error_callback)
        
        # Setup fallback
        def service_fallback():
            return "service_recovered"
        
        fallback_manager = get_fallback_manager()
        fallback_manager.register_fallback("integration_service", service_fallback)
        
        # Simulate service failure
        def failing_service():
            raise ValueError("Service is down")
        
        # Execute with fallback
        result = fallback_manager.execute_with_fallback("integration_service", failing_service)
        
        assert result == "service_recovered"
        
        # Manual error handling
        original_exception = ValueError("Manual error")
        context = ErrorContext(
            user_id="integration_user",
            service_name="integration_service"
        )
        
        app_error = handle_error(
            ErrorCode.SERVICE_UNAVAILABLE,
            "Integration test error",
            ErrorSeverity.HIGH,
            context,
            original_exception
        )
        
        # Verify error was handled properly
        assert app_error.error_code == ErrorCode.SERVICE_UNAVAILABLE
        assert app_error.original_exception == original_exception
        assert len(callback_errors) > 0
        
        # Verify statistics
        stats = handler.get_error_statistics()
        assert stats["total_errors"] > 0

def test_error_severity_enum():
    """Test error severity enumeration"""
    assert ErrorSeverity.LOW.value == "low"
    assert ErrorSeverity.MEDIUM.value == "medium"
    assert ErrorSeverity.HIGH.value == "high"
    assert ErrorSeverity.CRITICAL.value == "critical"

def test_error_context_additional_context():
    """Test error context additional context field"""
    context = ErrorContext(
        user_id="test_user",
        additional_context={
            "request_data": {"key": "value"},
            "client_info": {"browser": "chrome"}
        }
    )
    
    assert context.additional_context["request_data"]["key"] == "value"
    assert context.additional_context["client_info"]["browser"] == "chrome"