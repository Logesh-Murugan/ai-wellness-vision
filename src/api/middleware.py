# middleware.py - API middleware for authentication, rate limiting, and validation
import logging
import time
import hashlib
from typing import Dict, List, Optional, Any, Callable
from datetime import datetime, timedelta
from collections import defaultdict, deque

# Optional imports with fallbacks
try:
    from fastapi import Request, Response, HTTPException
    from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
    from starlette.middleware.base import BaseHTTPMiddleware
    FASTAPI_AVAILABLE = True
except ImportError:
    FASTAPI_AVAILABLE = False
    logging.warning("FastAPI not available - using mock middleware")
    
    # Mock classes
    class BaseHTTPMiddleware:
        def __init__(self, app):
            self.app = app
    
    class Request:
        def __init__(self):
            self.client = type('Client', (), {'host': '127.0.0.1'})()
            self.url = type('URL', (), {'path': '/test'})()
            self.method = 'GET'
    
    class Response:
        def __init__(self, content="", status_code=200):
            self.content = content
            self.status_code = status_code
    
    class HTTPException(Exception):
        def __init__(self, status_code: int, detail: str):
            self.status_code = status_code
            self.detail = detail

from src.config import AppConfig
from src.utils.logging_config import get_logger

logger = get_logger(__name__)

class RateLimitMiddleware(BaseHTTPMiddleware if FASTAPI_AVAILABLE else object):
    """Rate limiting middleware to prevent API abuse"""
    
    def __init__(self, app, requests_per_minute: int = 60, requests_per_hour: int = 1000):
        if FASTAPI_AVAILABLE:
            super().__init__(app)
        self.requests_per_minute = requests_per_minute
        self.requests_per_hour = requests_per_hour
        
        # Store request timestamps per IP
        self.request_history = defaultdict(lambda: {
            'minute': deque(),
            'hour': deque()
        })
        
        logger.info(f"Rate limiting: {requests_per_minute}/min, {requests_per_hour}/hour")
    
    async def dispatch(self, request: Request, call_next: Callable) -> Response:
        """Process request with rate limiting"""
        if not FASTAPI_AVAILABLE:
            return Response("Mock response - FastAPI not available")
        
        try:
            client_ip = self._get_client_ip(request)
            current_time = time.time()
            
            # Check rate limits
            if self._is_rate_limited(client_ip, current_time):
                logger.warning(f"Rate limit exceeded for IP: {client_ip}")
                raise HTTPException(
                    status_code=429,
                    detail="Rate limit exceeded. Please try again later."
                )
            
            # Record this request
            self._record_request(client_ip, current_time)
            
            # Process request
            response = await call_next(request)
            
            # Add rate limit headers
            remaining_minute = self._get_remaining_requests(client_ip, 'minute')
            remaining_hour = self._get_remaining_requests(client_ip, 'hour')
            
            response.headers["X-RateLimit-Limit-Minute"] = str(self.requests_per_minute)
            response.headers["X-RateLimit-Remaining-Minute"] = str(remaining_minute)
            response.headers["X-RateLimit-Limit-Hour"] = str(self.requests_per_hour)
            response.headers["X-RateLimit-Remaining-Hour"] = str(remaining_hour)
            
            return response
            
        except HTTPException:
            raise
        except Exception as e:
            logger.error(f"Rate limiting middleware error: {e}")
            # Continue processing on middleware error
            return await call_next(request)
    
    def _get_client_ip(self, request: Request) -> str:
        """Extract client IP address"""
        # Check for forwarded headers first (for reverse proxies)
        forwarded_for = request.headers.get("X-Forwarded-For")
        if forwarded_for:
            return forwarded_for.split(",")[0].strip()
        
        real_ip = request.headers.get("X-Real-IP")
        if real_ip:
            return real_ip
        
        # Fallback to direct client IP
        return request.client.host if hasattr(request, 'client') else "unknown"
    
    def _is_rate_limited(self, client_ip: str, current_time: float) -> bool:
        """Check if client has exceeded rate limits"""
        history = self.request_history[client_ip]
        
        # Clean old requests
        self._clean_old_requests(history, current_time)
        
        # Check minute limit
        if len(history['minute']) >= self.requests_per_minute:
            return True
        
        # Check hour limit
        if len(history['hour']) >= self.requests_per_hour:
            return True
        
        return False
    
    def _record_request(self, client_ip: str, current_time: float):
        """Record a request timestamp"""
        history = self.request_history[client_ip]
        history['minute'].append(current_time)
        history['hour'].append(current_time)
    
    def _clean_old_requests(self, history: Dict, current_time: float):
        """Remove old request timestamps"""
        minute_cutoff = current_time - 60  # 1 minute ago
        hour_cutoff = current_time - 3600  # 1 hour ago
        
        # Clean minute history
        while history['minute'] and history['minute'][0] < minute_cutoff:
            history['minute'].popleft()
        
        # Clean hour history
        while history['hour'] and history['hour'][0] < hour_cutoff:
            history['hour'].popleft()
    
    def _get_remaining_requests(self, client_ip: str, period: str) -> int:
        """Get remaining requests for the period"""
        history = self.request_history[client_ip]
        
        if period == 'minute':
            return max(0, self.requests_per_minute - len(history['minute']))
        elif period == 'hour':
            return max(0, self.requests_per_hour - len(history['hour']))
        
        return 0

class SecurityMiddleware(BaseHTTPMiddleware if FASTAPI_AVAILABLE else object):
    """Security middleware for headers and basic protection"""
    
    def __init__(self, app):
        if FASTAPI_AVAILABLE:
            super().__init__(app)
        
        self.security_headers = {
            "X-Content-Type-Options": "nosniff",
            "X-Frame-Options": "DENY",
            "X-XSS-Protection": "1; mode=block",
            "Strict-Transport-Security": "max-age=31536000; includeSubDomains",
            "Referrer-Policy": "strict-origin-when-cross-origin",
            "Content-Security-Policy": "default-src 'self'; script-src 'self' 'unsafe-inline'; style-src 'self' 'unsafe-inline';"
        }
        
        logger.info("Security middleware initialized")
    
    async def dispatch(self, request: Request, call_next: Callable) -> Response:
        """Process request with security headers"""
        if not FASTAPI_AVAILABLE:
            return Response("Mock response - FastAPI not available")
        
        try:
            # Process request
            response = await call_next(request)
            
            # Add security headers
            for header, value in self.security_headers.items():
                response.headers[header] = value
            
            # Add request ID for tracing
            request_id = self._generate_request_id(request)
            response.headers["X-Request-ID"] = request_id
            
            return response
            
        except Exception as e:
            logger.error(f"Security middleware error: {e}")
            # Continue processing on middleware error
            return await call_next(request)
    
    def _generate_request_id(self, request: Request) -> str:
        """Generate unique request ID"""
        timestamp = str(time.time())
        client_ip = getattr(request.client, 'host', 'unknown') if hasattr(request, 'client') else 'unknown'
        path = request.url.path if hasattr(request, 'url') else '/unknown'
        
        # Create hash from timestamp, IP, and path
        request_data = f"{timestamp}:{client_ip}:{path}"
        return hashlib.md5(request_data.encode()).hexdigest()[:16]

class LoggingMiddleware(BaseHTTPMiddleware if FASTAPI_AVAILABLE else object):
    """Logging middleware for request/response tracking"""
    
    def __init__(self, app):
        if FASTAPI_AVAILABLE:
            super().__init__(app)
        
        self.sensitive_headers = {'authorization', 'cookie', 'x-api-key'}
        self.log_body_max_size = 1000  # Max body size to log
        
        logger.info("Logging middleware initialized")
    
    async def dispatch(self, request: Request, call_next: Callable) -> Response:
        """Process request with comprehensive logging"""
        if not FASTAPI_AVAILABLE:
            return Response("Mock response - FastAPI not available")
        
        start_time = time.time()
        request_id = getattr(request, 'request_id', 'unknown')
        
        try:
            # Log request
            await self._log_request(request, request_id)
            
            # Process request
            response = await call_next(request)
            
            # Calculate processing time
            processing_time = time.time() - start_time
            
            # Log response
            self._log_response(request, response, processing_time, request_id)
            
            return response
            
        except Exception as e:
            processing_time = time.time() - start_time
            logger.error(f"Request failed [{request_id}]: {str(e)} (took {processing_time:.3f}s)")
            raise
    
    async def _log_request(self, request: Request, request_id: str):
        """Log incoming request details"""
        try:
            client_ip = getattr(request.client, 'host', 'unknown') if hasattr(request, 'client') else 'unknown'
            method = request.method if hasattr(request, 'method') else 'UNKNOWN'
            path = request.url.path if hasattr(request, 'url') else '/unknown'
            
            # Log basic request info
            logger.info(f"Request [{request_id}]: {method} {path} from {client_ip}")
            
            # Log headers (excluding sensitive ones)
            if hasattr(request, 'headers'):
                safe_headers = {
                    k: v for k, v in request.headers.items() 
                    if k.lower() not in self.sensitive_headers
                }
                logger.debug(f"Request headers [{request_id}]: {safe_headers}")
            
        except Exception as e:
            logger.error(f"Error logging request [{request_id}]: {e}")
    
    def _log_response(self, request: Request, response: Response, 
                     processing_time: float, request_id: str):
        """Log response details"""
        try:
            method = request.method if hasattr(request, 'method') else 'UNKNOWN'
            path = request.url.path if hasattr(request, 'url') else '/unknown'
            status_code = response.status_code if hasattr(response, 'status_code') else 'unknown'
            
            # Log response info
            logger.info(f"Response [{request_id}]: {method} {path} -> {status_code} (took {processing_time:.3f}s)")
            
            # Log slow requests
            if processing_time > 5.0:  # 5 seconds threshold
                logger.warning(f"Slow request [{request_id}]: {processing_time:.3f}s for {method} {path}")
            
        except Exception as e:
            logger.error(f"Error logging response [{request_id}]: {e}")

class ValidationMiddleware(BaseHTTPMiddleware if FASTAPI_AVAILABLE else object):
    """Enhanced request validation middleware"""
    
    def __init__(self, app):
        if FASTAPI_AVAILABLE:
            super().__init__(app)
        
        self.max_content_length = AppConfig.MAX_UPLOAD_SIZE
        self.allowed_content_types = {
            'application/json',
            'multipart/form-data',
            'application/x-www-form-urlencoded',
            'image/jpeg',
            'image/png',
            'image/webp',
            'image/gif',
            'image/bmp',
            'audio/wav',
            'audio/mpeg',
            'audio/mp4',
            'audio/ogg',
            'audio/flac'
        }
        
        # Malicious patterns to check for
        self.malicious_patterns = [
            r'<script[^>]*>.*?</script>',
            r'javascript:',
            r'vbscript:',
            r'onload\s*=',
            r'onerror\s*=',
            r'eval\s*\(',
            r'exec\s*\(',
            r'system\s*\(',
            r'\.\./',  # Path traversal
            r'\\.\\.\\',  # Windows path traversal
        ]
        
        logger.info("Enhanced validation middleware initialized")
    
    async def dispatch(self, request: Request, call_next: Callable) -> Response:
        """Process request with comprehensive validation"""
        if not FASTAPI_AVAILABLE:
            return Response("Mock response - FastAPI not available")
        
        try:
            # Validate content length
            content_length = request.headers.get('content-length')
            if content_length and int(content_length) > self.max_content_length:
                logger.warning(f"Request too large: {content_length} bytes from {request.client.host}")
                raise HTTPException(
                    status_code=413,
                    detail=f"Request too large. Maximum size: {self.max_content_length} bytes"
                )
            
            # Validate content type for POST/PUT requests
            if request.method in ['POST', 'PUT', 'PATCH']:
                content_type = request.headers.get('content-type', '').split(';')[0].lower()
                if content_type and not any(allowed in content_type for allowed in self.allowed_content_types):
                    logger.warning(f"Unsupported content type: {content_type} from {request.client.host}")
                    raise HTTPException(
                        status_code=415,
                        detail=f"Unsupported content type: {content_type}"
                    )
            
            # Validate URL path for malicious patterns
            path = str(request.url.path)
            if self._contains_malicious_patterns(path):
                logger.warning(f"Malicious pattern detected in path: {path} from {request.client.host}")
                raise HTTPException(
                    status_code=400,
                    detail="Invalid request path"
                )
            
            # Validate query parameters
            query_params = str(request.url.query)
            if query_params and self._contains_malicious_patterns(query_params):
                logger.warning(f"Malicious pattern detected in query: {query_params} from {request.client.host}")
                raise HTTPException(
                    status_code=400,
                    detail="Invalid query parameters"
                )
            
            # Validate headers for suspicious content
            for header_name, header_value in request.headers.items():
                if self._contains_malicious_patterns(header_value):
                    logger.warning(f"Malicious pattern detected in header {header_name}: {header_value}")
                    raise HTTPException(
                        status_code=400,
                        detail="Invalid request headers"
                    )
            
            # Process request
            response = await call_next(request)
            
            return response
            
        except HTTPException:
            raise
        except Exception as e:
            logger.error(f"Validation middleware error: {e}")
            raise HTTPException(
                status_code=500,
                detail="Request validation failed"
            )
    
    def _contains_malicious_patterns(self, text: str) -> bool:
        """Check if text contains malicious patterns"""
        import re
        
        text_lower = text.lower()
        for pattern in self.malicious_patterns:
            if re.search(pattern, text_lower, re.IGNORECASE):
                return True
        return False

class HealthCheckMiddleware(BaseHTTPMiddleware if FASTAPI_AVAILABLE else object):
    """Health check and monitoring middleware"""
    
    def __init__(self, app):
        if FASTAPI_AVAILABLE:
            super().__init__(app)
        
        self.request_count = 0
        self.error_count = 0
        self.start_time = time.time()
        
        logger.info("Health check middleware initialized")
    
    async def dispatch(self, request: Request, call_next: Callable) -> Response:
        """Process request with health monitoring"""
        if not FASTAPI_AVAILABLE:
            return Response("Mock response - FastAPI not available")
        
        self.request_count += 1
        
        try:
            response = await call_next(request)
            
            # Count errors
            if hasattr(response, 'status_code') and response.status_code >= 400:
                self.error_count += 1
            
            return response
            
        except Exception as e:
            self.error_count += 1
            logger.error(f"Health check middleware - request failed: {e}")
            raise
    
    def get_health_stats(self) -> Dict[str, Any]:
        """Get current health statistics"""
        uptime = time.time() - self.start_time
        error_rate = (self.error_count / self.request_count) if self.request_count > 0 else 0
        
        return {
            'uptime_seconds': uptime,
            'total_requests': self.request_count,
            'total_errors': self.error_count,
            'error_rate': error_rate,
            'status': 'healthy' if error_rate < 0.1 else 'degraded'
        }

# Global middleware instances
rate_limit_middleware = None
security_middleware = None
logging_middleware = None
validation_middleware = None
health_check_middleware = None

def setup_middleware(app):
    """Setup all middleware for the FastAPI app"""
    global rate_limit_middleware, security_middleware, logging_middleware
    global validation_middleware, health_check_middleware
    
    if not FASTAPI_AVAILABLE:
        logger.warning("Middleware setup skipped - FastAPI not available")
        return
    
    try:
        # Add middleware in reverse order (last added is executed first)
        health_check_middleware = HealthCheckMiddleware(app)
        app.add_middleware(HealthCheckMiddleware)
        
        validation_middleware = ValidationMiddleware(app)
        app.add_middleware(ValidationMiddleware)
        
        logging_middleware = LoggingMiddleware(app)
        app.add_middleware(LoggingMiddleware)
        
        security_middleware = SecurityMiddleware(app)
        app.add_middleware(SecurityMiddleware)
        
        rate_limit_middleware = RateLimitMiddleware(app)
        app.add_middleware(RateLimitMiddleware)
        
        logger.info("All middleware configured successfully")
        
    except Exception as e:
        logger.error(f"Middleware setup failed: {e}")

def get_health_stats() -> Dict[str, Any]:
    """Get health statistics from middleware"""
    if health_check_middleware:
        return health_check_middleware.get_health_stats()
    else:
        return {
            'status': 'unknown',
            'message': 'Health check middleware not available'
        }