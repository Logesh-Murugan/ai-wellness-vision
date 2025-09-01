# security_middleware.py - Security middleware for web applications
from typing import Dict, Any, Optional, Callable, List
from datetime import datetime, timedelta
import re
import hashlib
import secrets
from functools import wraps

from src.security.data_protection import get_data_protection_service, DataCategory, ProcessingActivity
from src.security.consent import get_consent_manager, ConsentType
from src.utils.logging_config import get_structured_logger
from src.utils.error_handling import handle_error, ErrorCode, ErrorSeverity, ErrorContext

logger = get_structured_logger(__name__)

class SecurityHeaders:
    """Security headers for HTTP responses"""
    
    @staticmethod
    def get_security_headers() -> Dict[str, str]:
        """Get recommended security headers"""
        return {
            # Prevent clickjacking
            "X-Frame-Options": "DENY",
            
            # Prevent MIME type sniffing
            "X-Content-Type-Options": "nosniff",
            
            # Enable XSS protection
            "X-XSS-Protection": "1; mode=block",
            
            # Strict transport security (HTTPS only)
            "Strict-Transport-Security": "max-age=31536000; includeSubDomains",
            
            # Content Security Policy
            "Content-Security-Policy": (
                "default-src 'self'; "
                "script-src 'self' 'unsafe-inline' 'unsafe-eval'; "
                "style-src 'self' 'unsafe-inline'; "
                "img-src 'self' data: https:; "
                "font-src 'self' https:; "
                "connect-src 'self' https:; "
                "frame-ancestors 'none';"
            ),
            
            # Referrer policy
            "Referrer-Policy": "strict-origin-when-cross-origin",
            
            # Permissions policy
            "Permissions-Policy": (
                "camera=(), microphone=(), geolocation=(), "
                "payment=(), usb=(), magnetometer=(), gyroscope=()"
            )
        }

class RateLimiter:
    """Rate limiting for API endpoints"""
    
    def __init__(self):
        self.requests = {}  # IP -> list of timestamps
        self.blocked_ips = {}  # IP -> block_until timestamp
    
    def is_rate_limited(self, client_ip: str, max_requests: int = 100, 
                       window_minutes: int = 15) -> bool:
        """Check if client IP is rate limited"""
        current_time = datetime.now()
        
        # Check if IP is currently blocked
        if client_ip in self.blocked_ips:
            if current_time < self.blocked_ips[client_ip]:
                return True
            else:
                # Unblock expired blocks
                del self.blocked_ips[client_ip]
        
        # Initialize or clean old requests
        if client_ip not in self.requests:
            self.requests[client_ip] = []
        
        # Remove old requests outside the window
        window_start = current_time - timedelta(minutes=window_minutes)
        self.requests[client_ip] = [
            req_time for req_time in self.requests[client_ip]
            if req_time > window_start
        ]
        
        # Check rate limit
        if len(self.requests[client_ip]) >= max_requests:
            # Block IP for double the window time
            self.blocked_ips[client_ip] = current_time + timedelta(minutes=window_minutes * 2)
            logger.warning(f"Rate limit exceeded for IP: {client_ip}")
            return True
        
        # Record this request
        self.requests[client_ip].append(current_time)
        return False

class InputValidator:
    """Input validation and sanitization"""
    
    def __init__(self):
        self.dangerous_patterns = [
            # SQL injection patterns
            r"(\b(SELECT|INSERT|UPDATE|DELETE|DROP|CREATE|ALTER|EXEC|UNION)\b)",
            
            # XSS patterns
            r"(<script[^>]*>.*?</script>)",
            r"(javascript:)",
            r"(on\w+\s*=)",
            
            # Path traversal
            r"(\.\./)",
            r"(\.\.\\)",
            
            # Command injection
            r"(\b(eval|exec|system|shell_exec|passthru)\b)",
            
            # LDAP injection
            r"(\*|\(|\)|\||&)",
        ]
        
        self.compiled_patterns = [re.compile(pattern, re.IGNORECASE) for pattern in self.dangerous_patterns]
    
    def validate_input(self, input_data: Any, field_name: str = "input") -> Dict[str, Any]:
        """Validate input for security threats"""
        validation_result = {
            "valid": True,
            "threats_detected": [],
            "sanitized_data": input_data
        }
        
        if isinstance(input_data, str):
            # Check for dangerous patterns
            for i, pattern in enumerate(self.compiled_patterns):
                if pattern.search(input_data):
                    validation_result["valid"] = False
                    validation_result["threats_detected"].append(f"Pattern {i+1} detected in {field_name}")
            
            # Sanitize the input
            validation_result["sanitized_data"] = self._sanitize_string(input_data)
            
        elif isinstance(input_data, dict):
            sanitized_dict = {}
            for key, value in input_data.items():
                key_validation = self.validate_input(key, f"{field_name}.key")
                value_validation = self.validate_input(value, f"{field_name}.{key}")
                
                if not key_validation["valid"] or not value_validation["valid"]:
                    validation_result["valid"] = False
                    validation_result["threats_detected"].extend(key_validation["threats_detected"])
                    validation_result["threats_detected"].extend(value_validation["threats_detected"])
                
                sanitized_dict[key_validation["sanitized_data"]] = value_validation["sanitized_data"]
            
            validation_result["sanitized_data"] = sanitized_dict
            
        elif isinstance(input_data, list):
            sanitized_list = []
            for i, item in enumerate(input_data):
                item_validation = self.validate_input(item, f"{field_name}[{i}]")
                
                if not item_validation["valid"]:
                    validation_result["valid"] = False
                    validation_result["threats_detected"].extend(item_validation["threats_detected"])
                
                sanitized_list.append(item_validation["sanitized_data"])
            
            validation_result["sanitized_data"] = sanitized_list
        
        return validation_result
    
    def _sanitize_string(self, text: str) -> str:
        """Sanitize string input"""
        # HTML encode dangerous characters
        sanitized = text.replace("&", "&amp;")
        sanitized = sanitized.replace("<", "&lt;")
        sanitized = sanitized.replace(">", "&gt;")
        sanitized = sanitized.replace('"', "&quot;")
        sanitized = sanitized.replace("'", "&#x27;")
        sanitized = sanitized.replace("/", "&#x2F;")
        
        return sanitized

class SessionManager:
    """Secure session management"""
    
    def __init__(self):
        self.sessions = {}  # session_id -> session_data
        self.session_timeout = timedelta(hours=2)
    
    def create_session(self, user_id: str, additional_data: Dict[str, Any] = None) -> str:
        """Create a new secure session"""
        session_id = secrets.token_urlsafe(32)
        
        session_data = {
            "user_id": user_id,
            "created_at": datetime.now(),
            "last_accessed": datetime.now(),
            "ip_address": None,  # Should be set by middleware
            "user_agent": None,  # Should be set by middleware
            "csrf_token": secrets.token_urlsafe(32),
            "additional_data": additional_data or {}
        }
        
        self.sessions[session_id] = session_data
        
        logger.info(f"Created session for user {user_id}")
        return session_id
    
    def validate_session(self, session_id: str, client_ip: str = None, 
                        user_agent: str = None) -> Dict[str, Any]:
        """Validate session and return session data"""
        if session_id not in self.sessions:
            return {"valid": False, "reason": "session_not_found"}
        
        session_data = self.sessions[session_id]
        current_time = datetime.now()
        
        # Check timeout
        if current_time - session_data["last_accessed"] > self.session_timeout:
            del self.sessions[session_id]
            return {"valid": False, "reason": "session_expired"}
        
        # Check IP address consistency (optional)
        if client_ip and session_data.get("ip_address"):
            if client_ip != session_data["ip_address"]:
                logger.warning(f"IP address mismatch for session {session_id}")
                # Don't invalidate immediately, but log for monitoring
        
        # Update last accessed
        session_data["last_accessed"] = current_time
        if client_ip:
            session_data["ip_address"] = client_ip
        if user_agent:
            session_data["user_agent"] = user_agent
        
        return {
            "valid": True,
            "session_data": session_data
        }
    
    def invalidate_session(self, session_id: str) -> bool:
        """Invalidate a session"""
        if session_id in self.sessions:
            user_id = self.sessions[session_id].get("user_id")
            del self.sessions[session_id]
            logger.info(f"Invalidated session for user {user_id}")
            return True
        return False
    
    def cleanup_expired_sessions(self) -> int:
        """Clean up expired sessions"""
        current_time = datetime.now()
        expired_sessions = []
        
        for session_id, session_data in self.sessions.items():
            if current_time - session_data["last_accessed"] > self.session_timeout:
                expired_sessions.append(session_id)
        
        for session_id in expired_sessions:
            del self.sessions[session_id]
        
        if expired_sessions:
            logger.info(f"Cleaned up {len(expired_sessions)} expired sessions")
        
        return len(expired_sessions)

class SecurityMiddleware:
    """Main security middleware class"""
    
    def __init__(self):
        self.data_protection_service = get_data_protection_service()
        self.consent_manager = get_consent_manager()
        self.rate_limiter = RateLimiter()
        self.input_validator = InputValidator()
        self.session_manager = SessionManager()
        self.security_headers = SecurityHeaders()
    
    def process_request(self, request_data: Dict[str, Any]) -> Dict[str, Any]:
        """Process incoming request with security checks"""
        try:
            client_ip = request_data.get("client_ip", "unknown")
            user_agent = request_data.get("user_agent", "unknown")
            session_id = request_data.get("session_id")
            
            security_result = {
                "allowed": True,
                "security_headers": self.security_headers.get_security_headers(),
                "warnings": [],
                "errors": []
            }
            
            # Rate limiting check
            if self.rate_limiter.is_rate_limited(client_ip):
                security_result["allowed"] = False
                security_result["errors"].append("Rate limit exceeded")
                
                handle_error(
                    ErrorCode.RATE_LIMIT_EXCEEDED,
                    f"Rate limit exceeded for IP: {client_ip}",
                    ErrorSeverity.MEDIUM,
                    ErrorContext(service_name="security_middleware")
                )
                return security_result
            
            # Session validation
            if session_id:
                session_validation = self.session_manager.validate_session(
                    session_id, client_ip, user_agent
                )
                
                if not session_validation["valid"]:
                    security_result["allowed"] = False
                    security_result["errors"].append(f"Invalid session: {session_validation['reason']}")
                    return security_result
                
                # Add user context to request
                request_data["user_id"] = session_validation["session_data"]["user_id"]
                request_data["csrf_token"] = session_validation["session_data"]["csrf_token"]
            
            # Input validation
            if "input_data" in request_data:
                validation_result = self.input_validator.validate_input(
                    request_data["input_data"], "request_input"
                )
                
                if not validation_result["valid"]:
                    security_result["warnings"].extend(validation_result["threats_detected"])
                    
                    # Log security threat
                    handle_error(
                        ErrorCode.SECURITY_VALIDATION_FAILED,
                        f"Security threats detected: {validation_result['threats_detected']}",
                        ErrorSeverity.HIGH,
                        ErrorContext(service_name="security_middleware")
                    )
                
                # Use sanitized data
                request_data["input_data"] = validation_result["sanitized_data"]
            
            # Log security event
            logger.log_security_event(
                "request_processed",
                severity="low",
                client_ip=client_ip,
                user_agent=user_agent,
                threats_detected=len(security_result["warnings"]),
                session_valid=session_id is not None
            )
            
            return security_result
            
        except Exception as e:
            logger.error(f"Security middleware processing failed: {e}")
            return {
                "allowed": False,
                "errors": [f"Security processing error: {str(e)}"],
                "security_headers": self.security_headers.get_security_headers()
            }
    
    def process_data_request(self, user_id: str, data_category: DataCategory,
                           operation: str, request_data: Dict[str, Any]) -> Dict[str, Any]:
        """Process data-related requests with privacy and consent checks"""
        try:
            # Validate data access
            access_validation = self.data_protection_service.validate_data_access(
                user_id, data_category, operation
            )
            
            if not access_validation["access_granted"]:
                logger.warning(f"Data access denied for user {user_id}, operation {operation}")
                
                handle_error(
                    ErrorCode.AUTHORIZATION_ERROR,
                    f"Data access denied: {access_validation}",
                    ErrorSeverity.HIGH,
                    ErrorContext(user_id=user_id, service_name="security_middleware")
                )
                
                return {
                    "allowed": False,
                    "reason": "access_denied",
                    "details": access_validation
                }
            
            # Process data securely if this is a data processing request
            if "data" in request_data:
                processed_data = self.data_protection_service.process_data_securely(
                    user_id, request_data["data"], data_category, operation,
                    ProcessingActivity.ANALYSIS
                )
                request_data["processed_data"] = processed_data
            
            logger.info(f"Data request processed for user {user_id}, operation {operation}")
            
            return {
                "allowed": True,
                "access_validation": access_validation,
                "processed_data": request_data.get("processed_data")
            }
            
        except Exception as e:
            logger.error(f"Data request processing failed: {e}")
            return {
                "allowed": False,
                "reason": "processing_error",
                "error": str(e)
            }
    
    def create_secure_session(self, user_id: str, client_ip: str, 
                            user_agent: str) -> Dict[str, Any]:
        """Create a secure session for user"""
        try:
            session_id = self.session_manager.create_session(
                user_id, 
                {"login_ip": client_ip, "login_user_agent": user_agent}
            )
            
            session_validation = self.session_manager.validate_session(
                session_id, client_ip, user_agent
            )
            
            logger.log_security_event(
                "session_created",
                severity="low",
                user_id=user_id,
                client_ip=client_ip,
                session_id=session_id
            )
            
            return {
                "success": True,
                "session_id": session_id,
                "csrf_token": session_validation["session_data"]["csrf_token"],
                "expires_in": int(self.session_manager.session_timeout.total_seconds())
            }
            
        except Exception as e:
            logger.error(f"Session creation failed: {e}")
            return {
                "success": False,
                "error": str(e)
            }
    
    def validate_csrf_token(self, session_id: str, provided_token: str) -> bool:
        """Validate CSRF token"""
        try:
            session_validation = self.session_manager.validate_session(session_id)
            
            if not session_validation["valid"]:
                return False
            
            expected_token = session_validation["session_data"]["csrf_token"]
            return secrets.compare_digest(expected_token, provided_token)
            
        except Exception as e:
            logger.error(f"CSRF token validation failed: {e}")
            return False
    
    def logout_user(self, session_id: str) -> bool:
        """Logout user and invalidate session"""
        try:
            session_validation = self.session_manager.validate_session(session_id)
            
            if session_validation["valid"]:
                user_id = session_validation["session_data"]["user_id"]
                
                logger.log_security_event(
                    "user_logout",
                    severity="low",
                    user_id=user_id,
                    session_id=session_id
                )
            
            return self.session_manager.invalidate_session(session_id)
            
        except Exception as e:
            logger.error(f"Logout failed: {e}")
            return False
    
    def get_security_status(self) -> Dict[str, Any]:
        """Get security middleware status"""
        return {
            "active_sessions": len(self.session_manager.sessions),
            "rate_limited_ips": len(self.rate_limiter.blocked_ips),
            "total_requests_tracked": sum(
                len(requests) for requests in self.rate_limiter.requests.values()
            ),
            "security_headers_enabled": len(self.security_headers.get_security_headers()),
            "input_validation_patterns": len(self.input_validator.compiled_patterns),
            "session_timeout_hours": self.session_manager.session_timeout.total_seconds() / 3600
        }

# Decorator for protecting endpoints
def require_consent(consent_types: List[ConsentType]):
    """Decorator to require specific consents for endpoint access"""
    def decorator(func):
        @wraps(func)
        def wrapper(*args, **kwargs):
            # Extract user_id from request context
            user_id = kwargs.get("user_id") or (args[0] if args else None)
            
            if not user_id:
                raise ValueError("User ID required for consent validation")
            
            consent_manager = get_consent_manager()
            
            # Check all required consents
            for consent_type in consent_types:
                if not consent_manager.check_consent(user_id, consent_type):
                    handle_error(
                        ErrorCode.AUTHORIZATION_ERROR,
                        f"Missing required consent: {consent_type.value}",
                        ErrorSeverity.HIGH,
                        ErrorContext(user_id=user_id)
                    )
                    raise PermissionError(f"Consent required: {consent_type.value}")
            
            return func(*args, **kwargs)
        return wrapper
    return decorator

def require_data_protection(data_category: DataCategory):
    """Decorator to ensure data protection for specific data categories"""
    def decorator(func):
        @wraps(func)
        def wrapper(*args, **kwargs):
            user_id = kwargs.get("user_id") or (args[0] if args else None)
            
            if not user_id:
                raise ValueError("User ID required for data protection")
            
            data_protection_service = get_data_protection_service()
            
            # Validate data access
            validation = data_protection_service.validate_data_access(
                user_id, data_category, func.__name__
            )
            
            if not validation["access_granted"]:
                handle_error(
                    ErrorCode.AUTHORIZATION_ERROR,
                    f"Data access denied for category: {data_category.value}",
                    ErrorSeverity.HIGH,
                    ErrorContext(user_id=user_id)
                )
                raise PermissionError(f"Access denied for data category: {data_category.value}")
            
            return func(*args, **kwargs)
        return wrapper
    return decorator

# Global security middleware instance
security_middleware = SecurityMiddleware()

def get_security_middleware() -> SecurityMiddleware:
    """Get global security middleware instance"""
    return security_middleware