# error_handling.py - Comprehensive error handling system
import logging
import traceback
import sys
from typing import Dict, Any, Optional, Union, List
from enum import Enum
from dataclasses import dataclass, field
from datetime import datetime
import json

from src.utils.logging_config import get_logger

logger = get_logger(__name__)

class ErrorCode(Enum):
    """Standardized error codes for the application"""
    
    # General errors (1000-1999)
    UNKNOWN_ERROR = "E1000"
    VALIDATION_ERROR = "E1001"
    CONFIGURATION_ERROR = "E1002"
    INITIALIZATION_ERROR = "E1003"
    RESOURCE_NOT_FOUND = "E1004"
    PERMISSION_DENIED = "E1005"
    TIMEOUT_ERROR = "E1006"
    RATE_LIMIT_EXCEEDED = "E1007"
    
    # Image processing errors (2000-2999)
    IMAGE_UPLOAD_ERROR = "E2000"
    IMAGE_FORMAT_ERROR = "E2001"
    IMAGE_SIZE_ERROR = "E2002"
    IMAGE_PROCESSING_ERROR = "E2003"
    MODEL_LOADING_ERROR = "E2004"
    ANALYSIS_FAILED = "E2005"
    SKIN_ANALYSIS_ERROR = "E2006"
    EYE_ANALYSIS_ERROR = "E2007"
    FOOD_RECOGNITION_ERROR = "E2008"
    
    # NLP errors (3000-3999)
    TEXT_PROCESSING_ERROR = "E3000"
    LANGUAGE_DETECTION_ERROR = "E3001"
    TRANSLATION_ERROR = "E3002"
    SENTIMENT_ANALYSIS_ERROR = "E3003"
    CONVERSATION_ERROR = "E3004"
    QA_SYSTEM_ERROR = "E3005"
    
    # Speech processing errors (4000-4999)
    AUDIO_UPLOAD_ERROR = "E4000"
    AUDIO_FORMAT_ERROR = "E4001"
    SPEECH_TO_TEXT_ERROR = "E4002"
    TEXT_TO_SPEECH_ERROR = "E4003"
    AUDIO_PROCESSING_ERROR = "E4004"
    VOICE_SYNTHESIS_ERROR = "E4005"
    
    # API and network errors (5000-5999)
    API_REQUEST_ERROR = "E5000"
    NETWORK_ERROR = "E5001"
    SERVICE_UNAVAILABLE = "E5002"
    AUTHENTICATION_ERROR = "E5003"
    AUTHORIZATION_ERROR = "E5004"
    INVALID_REQUEST = "E5005"
    EXTERNAL_API_ERROR = "E5006"
    
    # Database and storage errors (6000-6999)
    DATABASE_ERROR = "E6000"
    STORAGE_ERROR = "E6001"
    CACHE_ERROR = "E6002"
    FILE_SYSTEM_ERROR = "E6003"
    BACKUP_ERROR = "E6004"
    
    # Security and privacy errors (7000-7999)
    ENCRYPTION_ERROR = "E7000"
    DECRYPTION_ERROR = "E7001"
    DATA_BREACH_DETECTED = "E7002"
    PRIVACY_VIOLATION = "E7003"
    SECURITY_VALIDATION_FAILED = "E7004"
    
    # Offline mode and optimization errors (8000-8999)
    OFFLINE_MODE_ERROR = "E8000"
    MODEL_OPTIMIZATION_ERROR = "E8001"
    CACHE_MISS_ERROR = "E8002"
    CONNECTIVITY_ERROR = "E8003"
    DEGRADATION_ERROR = "E8004"

class ErrorSeverity(Enum):
    """Error severity levels"""
    LOW = "low"
    MEDIUM = "medium"
    HIGH = "high"
    CRITICAL = "critical"

@dataclass
class ErrorContext:
    """Context information for errors"""
    user_id: Optional[str] = None
    session_id: Optional[str] = None
    request_id: Optional[str] = None
    service_name: Optional[str] = None
    function_name: Optional[str] = None
    input_data: Optional[Dict[str, Any]] = None
    system_info: Optional[Dict[str, Any]] = None
    additional_context: Dict[str, Any] = field(default_factory=dict)

@dataclass
class ApplicationError:
    """Structured error information"""
    error_code: ErrorCode
    message: str
    severity: ErrorSeverity
    timestamp: datetime
    context: ErrorContext
    original_exception: Optional[Exception] = None
    stack_trace: Optional[str] = None
    user_message: Optional[str] = None
    suggested_actions: List[str] = field(default_factory=list)
    recovery_possible: bool = True
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert error to dictionary for logging/API responses"""
        return {
            "error_code": self.error_code.value,
            "message": self.message,
            "severity": self.severity.value,
            "timestamp": self.timestamp.isoformat(),
            "user_message": self.user_message,
            "suggested_actions": self.suggested_actions,
            "recovery_possible": self.recovery_possible,
            "context": {
                "user_id": self.context.user_id,
                "session_id": self.context.session_id,
                "request_id": self.context.request_id,
                "service_name": self.context.service_name,
                "function_name": self.context.function_name,
                "additional_context": self.context.additional_context
            },
            "stack_trace": self.stack_trace if self.severity in [ErrorSeverity.HIGH, ErrorSeverity.CRITICAL] else None
        }
    
    def to_json(self) -> str:
        """Convert error to JSON string"""
        return json.dumps(self.to_dict(), indent=2, default=str)

class ErrorHandler:
    """Centralized error handling system"""
    
    def __init__(self):
        self.error_history = []
        self.max_history_size = 1000
        self.error_callbacks = []
        self.fallback_messages = self._load_fallback_messages()
    
    def _load_fallback_messages(self) -> Dict[ErrorCode, Dict[str, Any]]:
        """Load user-friendly fallback messages for each error code"""
        return {
            ErrorCode.IMAGE_UPLOAD_ERROR: {
                "user_message": "There was a problem uploading your image. Please try again.",
                "suggested_actions": [
                    "Check that your image file is valid (JPG, PNG, etc.)",
                    "Ensure the image is smaller than 10MB",
                    "Try uploading a different image",
                    "Check your internet connection"
                ]
            },
            ErrorCode.IMAGE_PROCESSING_ERROR: {
                "user_message": "We couldn't analyze your image right now. Please try again.",
                "suggested_actions": [
                    "Try uploading a clearer image",
                    "Ensure good lighting in the photo",
                    "Try again in a few moments",
                    "Contact support if the problem persists"
                ]
            },
            ErrorCode.SPEECH_TO_TEXT_ERROR: {
                "user_message": "We couldn't understand your voice input. Please try again.",
                "suggested_actions": [
                    "Speak clearly and at a normal pace",
                    "Reduce background noise",
                    "Check your microphone permissions",
                    "Try typing your message instead"
                ]
            },
            ErrorCode.NETWORK_ERROR: {
                "user_message": "Connection problem detected. Some features may be limited.",
                "suggested_actions": [
                    "Check your internet connection",
                    "Try refreshing the page",
                    "Some features work offline",
                    "Contact support if issues persist"
                ]
            },
            ErrorCode.SERVICE_UNAVAILABLE: {
                "user_message": "This service is temporarily unavailable. Please try again later.",
                "suggested_actions": [
                    "Try again in a few minutes",
                    "Use alternative features if available",
                    "Check system status page",
                    "Contact support for urgent issues"
                ]
            },
            ErrorCode.AUTHENTICATION_ERROR: {
                "user_message": "Authentication failed. Please log in again.",
                "suggested_actions": [
                    "Check your login credentials",
                    "Clear browser cache and cookies",
                    "Reset your password if needed",
                    "Contact support for account issues"
                ]
            },
            ErrorCode.OFFLINE_MODE_ERROR: {
                "user_message": "Limited functionality in offline mode.",
                "suggested_actions": [
                    "Connect to the internet for full features",
                    "Use available offline features",
                    "Data will sync when online",
                    "Check connection settings"
                ]
            }
        }
    
    def handle_error(self, 
                    error_code: ErrorCode,
                    message: str,
                    severity: ErrorSeverity = ErrorSeverity.MEDIUM,
                    context: Optional[ErrorContext] = None,
                    original_exception: Optional[Exception] = None) -> ApplicationError:
        """Handle an error with comprehensive logging and user messaging"""
        
        # Create error context if not provided
        if context is None:
            context = ErrorContext()
        
        # Get stack trace if exception provided
        stack_trace = None
        if original_exception:
            stack_trace = ''.join(traceback.format_exception(
                type(original_exception), original_exception, original_exception.__traceback__
            ))
        
        # Get fallback message info
        fallback_info = self.fallback_messages.get(error_code, {})
        user_message = fallback_info.get("user_message", "An unexpected error occurred.")
        suggested_actions = fallback_info.get("suggested_actions", ["Please try again later."])
        
        # Create structured error
        app_error = ApplicationError(
            error_code=error_code,
            message=message,
            severity=severity,
            timestamp=datetime.now(),
            context=context,
            original_exception=original_exception,
            stack_trace=stack_trace,
            user_message=user_message,
            suggested_actions=suggested_actions,
            recovery_possible=severity not in [ErrorSeverity.CRITICAL]
        )
        
        # Log the error
        self._log_error(app_error)
        
        # Add to history
        self._add_to_history(app_error)
        
        # Notify callbacks
        self._notify_callbacks(app_error)
        
        return app_error
    
    def _log_error(self, error: ApplicationError) -> None:
        """Log error with appropriate level"""
        error_dict = error.to_dict()
        
        if error.severity == ErrorSeverity.CRITICAL:
            logger.critical(f"CRITICAL ERROR [{error.error_code.value}]: {error.message}", 
                          extra={"error_details": error_dict})
        elif error.severity == ErrorSeverity.HIGH:
            logger.error(f"HIGH SEVERITY [{error.error_code.value}]: {error.message}",
                        extra={"error_details": error_dict})
        elif error.severity == ErrorSeverity.MEDIUM:
            logger.warning(f"MEDIUM SEVERITY [{error.error_code.value}]: {error.message}",
                          extra={"error_details": error_dict})
        else:
            logger.info(f"LOW SEVERITY [{error.error_code.value}]: {error.message}",
                       extra={"error_details": error_dict})
    
    def _add_to_history(self, error: ApplicationError) -> None:
        """Add error to history with size limit"""
        self.error_history.append(error)
        
        # Maintain history size limit
        if len(self.error_history) > self.max_history_size:
            self.error_history = self.error_history[-self.max_history_size:]
    
    def _notify_callbacks(self, error: ApplicationError) -> None:
        """Notify registered error callbacks"""
        for callback in self.error_callbacks:
            try:
                callback(error)
            except Exception as e:
                logger.error(f"Error callback failed: {e}")
    
    def register_callback(self, callback) -> None:
        """Register error callback function"""
        self.error_callbacks.append(callback)
    
    def get_error_statistics(self) -> Dict[str, Any]:
        """Get error statistics from history"""
        if not self.error_history:
            return {
                "total_errors": 0,
                "by_severity": {},
                "by_error_code": {},
                "recent_errors": []
            }
        
        # Count by severity
        severity_counts = {}
        for error in self.error_history:
            severity = error.severity.value
            severity_counts[severity] = severity_counts.get(severity, 0) + 1
        
        # Count by error code
        code_counts = {}
        for error in self.error_history:
            code = error.error_code.value
            code_counts[code] = code_counts.get(code, 0) + 1
        
        # Get recent errors (last 10)
        recent_errors = [
            {
                "error_code": error.error_code.value,
                "message": error.message,
                "severity": error.severity.value,
                "timestamp": error.timestamp.isoformat()
            }
            for error in self.error_history[-10:]
        ]
        
        return {
            "total_errors": len(self.error_history),
            "by_severity": severity_counts,
            "by_error_code": code_counts,
            "recent_errors": recent_errors,
            "most_common_errors": sorted(code_counts.items(), key=lambda x: x[1], reverse=True)[:5]
        }
    
    def clear_history(self) -> None:
        """Clear error history"""
        self.error_history.clear()
        logger.info("Error history cleared")

class FallbackManager:
    """Manages fallback mechanisms for service failures"""
    
    def __init__(self):
        self.fallback_strategies = {}
        self.circuit_breakers = {}
        self.retry_configs = {}
    
    def register_fallback(self, service_name: str, fallback_func, 
                         max_failures: int = 5, reset_timeout: int = 60) -> None:
        """Register a fallback function for a service"""
        self.fallback_strategies[service_name] = fallback_func
        self.circuit_breakers[service_name] = {
            "failures": 0,
            "max_failures": max_failures,
            "last_failure": None,
            "reset_timeout": reset_timeout,
            "state": "closed"  # closed, open, half-open
        }
    
    def execute_with_fallback(self, service_name: str, primary_func, *args, **kwargs):
        """Execute function with fallback on failure"""
        circuit_breaker = self.circuit_breakers.get(service_name)
        
        # Check circuit breaker state
        if circuit_breaker and self._should_use_fallback(circuit_breaker):
            logger.warning(f"Circuit breaker open for {service_name}, using fallback")
            return self._execute_fallback(service_name, *args, **kwargs)
        
        try:
            # Try primary function
            result = primary_func(*args, **kwargs)
            
            # Reset circuit breaker on success
            if circuit_breaker:
                circuit_breaker["failures"] = 0
                circuit_breaker["state"] = "closed"
            
            return result
            
        except Exception as e:
            # Record failure
            if circuit_breaker:
                circuit_breaker["failures"] += 1
                circuit_breaker["last_failure"] = datetime.now()
                
                if circuit_breaker["failures"] >= circuit_breaker["max_failures"]:
                    circuit_breaker["state"] = "open"
                    logger.error(f"Circuit breaker opened for {service_name}")
            
            # Use fallback
            logger.warning(f"Primary function failed for {service_name}, using fallback: {e}")
            return self._execute_fallback(service_name, *args, **kwargs)
    
    def _should_use_fallback(self, circuit_breaker: Dict[str, Any]) -> bool:
        """Check if fallback should be used based on circuit breaker state"""
        if circuit_breaker["state"] == "closed":
            return False
        
        if circuit_breaker["state"] == "open":
            # Check if reset timeout has passed
            if circuit_breaker["last_failure"]:
                time_since_failure = (datetime.now() - circuit_breaker["last_failure"]).seconds
                if time_since_failure >= circuit_breaker["reset_timeout"]:
                    circuit_breaker["state"] = "half-open"
                    return False
            return True
        
        # Half-open state - try primary function
        return False
    
    def _execute_fallback(self, service_name: str, *args, **kwargs):
        """Execute fallback function"""
        fallback_func = self.fallback_strategies.get(service_name)
        
        if fallback_func:
            try:
                return fallback_func(*args, **kwargs)
            except Exception as e:
                logger.error(f"Fallback function failed for {service_name}: {e}")
                raise ApplicationError(
                    error_code=ErrorCode.SERVICE_UNAVAILABLE,
                    message=f"Both primary and fallback functions failed for {service_name}",
                    severity=ErrorSeverity.HIGH,
                    timestamp=datetime.now(),
                    context=ErrorContext(service_name=service_name),
                    original_exception=e
                )
        else:
            raise ApplicationError(
                error_code=ErrorCode.SERVICE_UNAVAILABLE,
                message=f"No fallback available for {service_name}",
                severity=ErrorSeverity.HIGH,
                timestamp=datetime.now(),
                context=ErrorContext(service_name=service_name)
            )
    
    def get_circuit_breaker_status(self) -> Dict[str, Any]:
        """Get status of all circuit breakers"""
        return {
            service: {
                "state": breaker["state"],
                "failures": breaker["failures"],
                "max_failures": breaker["max_failures"],
                "last_failure": breaker["last_failure"].isoformat() if breaker["last_failure"] else None
            }
            for service, breaker in self.circuit_breakers.items()
        }

# Global instances
error_handler = ErrorHandler()
fallback_manager = FallbackManager()

def handle_error(error_code: ErrorCode, message: str, 
                severity: ErrorSeverity = ErrorSeverity.MEDIUM,
                context: Optional[ErrorContext] = None,
                original_exception: Optional[Exception] = None) -> ApplicationError:
    """Convenience function for error handling"""
    return error_handler.handle_error(error_code, message, severity, context, original_exception)

def with_fallback(service_name: str):
    """Decorator for functions with fallback support"""
    def decorator(func):
        def wrapper(*args, **kwargs):
            return fallback_manager.execute_with_fallback(service_name, func, *args, **kwargs)
        return wrapper
    return decorator

def get_error_handler() -> ErrorHandler:
    """Get global error handler instance"""
    return error_handler

def get_fallback_manager() -> FallbackManager:
    """Get global fallback manager instance"""
    return fallback_manager