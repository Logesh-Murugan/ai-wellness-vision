# auth.py - Authentication and authorization for API gateway
import logging
import time
import hashlib
from typing import Dict, List, Optional, Any
from datetime import datetime, timedelta
from dataclasses import dataclass

# Optional imports with fallbacks
try:
    from fastapi import HTTPException, Depends, status
    from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
    from jose import JWTError, jwt
    from passlib.context import CryptContext
    FASTAPI_AVAILABLE = True
except ImportError:
    FASTAPI_AVAILABLE = False
    logging.warning("FastAPI/Auth libraries not available - using mock authentication")
    
    # Mock classes
    class HTTPException(Exception):
        def __init__(self, status_code: int, detail: str):
            self.status_code = status_code
            self.detail = detail
    
    class HTTPBearer:
        def __init__(self, auto_error: bool = True):
            self.auto_error = auto_error
    
    class HTTPAuthorizationCredentials:
        def __init__(self, scheme: str, credentials: str):
            self.scheme = scheme
            self.credentials = credentials

from src.config import AppConfig
from src.utils.logging_config import get_logger

logger = get_logger(__name__)

# JWT Configuration
SECRET_KEY = AppConfig.SECRET_KEY
ALGORITHM = "HS256"
ACCESS_TOKEN_EXPIRE_MINUTES = 30
REFRESH_TOKEN_EXPIRE_DAYS = 7

# Password hashing
if FASTAPI_AVAILABLE:
    pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")
else:
    pwd_context = None

@dataclass
class UserCredentials:
    """User credentials for authentication"""
    username: str
    email: str
    hashed_password: str
    is_active: bool = True
    roles: List[str] = None
    created_at: datetime = None
    last_login: datetime = None
    
    def __post_init__(self):
        if self.roles is None:
            self.roles = ["user"]
        if self.created_at is None:
            self.created_at = datetime.utcnow()

@dataclass
class TokenData:
    """Token payload data"""
    username: str
    user_id: str
    roles: List[str]
    exp: datetime
    iat: datetime

class AuthenticationError(Exception):
    """Custom authentication error"""
    pass

class AuthorizationError(Exception):
    """Custom authorization error"""
    pass

class AuthManager:
    """Manages authentication and authorization"""
    
    def __init__(self):
        self.users_db = {}  # In-memory user store (replace with real DB)
        self.active_tokens = {}  # Track active tokens
        self.failed_attempts = {}  # Track failed login attempts
        
        # Create default admin user for development
        if AppConfig.ENVIRONMENT.value == "development":
            self._create_default_users()
        
        logger.info("Authentication manager initialized")
    
    def _create_default_users(self):
        """Create default users for development"""
        try:
            # Admin user
            admin_password = self.hash_password("admin123")
            self.users_db["admin"] = UserCredentials(
                username="admin",
                email="admin@wellnessvision.ai",
                hashed_password=admin_password,
                roles=["admin", "user"]
            )
            
            # Regular user
            user_password = self.hash_password("user123")
            self.users_db["testuser"] = UserCredentials(
                username="testuser",
                email="test@wellnessvision.ai",
                hashed_password=user_password,
                roles=["user"]
            )
            
            logger.info("Default users created for development")
            
        except Exception as e:
            logger.error(f"Failed to create default users: {e}")
    
    def hash_password(self, password: str) -> str:
        """Hash a password"""
        if pwd_context:
            return pwd_context.hash(password)
        else:
            # Fallback hashing for mock mode
            return hashlib.sha256(password.encode()).hexdigest()
    
    def verify_password(self, plain_password: str, hashed_password: str) -> bool:
        """Verify a password against its hash"""
        if pwd_context:
            return pwd_context.verify(plain_password, hashed_password)
        else:
            # Fallback verification for mock mode
            return hashlib.sha256(plain_password.encode()).hexdigest() == hashed_password
    
    def authenticate_user(self, username: str, password: str) -> Optional[UserCredentials]:
        """Authenticate user with username and password"""
        try:
            # Check for rate limiting on failed attempts
            if self._is_rate_limited(username):
                raise AuthenticationError("Too many failed attempts. Please try again later.")
            
            user = self.users_db.get(username)
            if not user:
                self._record_failed_attempt(username)
                raise AuthenticationError("Invalid username or password")
            
            if not user.is_active:
                raise AuthenticationError("Account is disabled")
            
            if not self.verify_password(password, user.hashed_password):
                self._record_failed_attempt(username)
                raise AuthenticationError("Invalid username or password")
            
            # Clear failed attempts on successful login
            self.failed_attempts.pop(username, None)
            
            # Update last login
            user.last_login = datetime.utcnow()
            
            logger.info(f"User authenticated successfully: {username}")
            return user
            
        except AuthenticationError:
            raise
        except Exception as e:
            logger.error(f"Authentication error: {e}")
            raise AuthenticationError("Authentication failed")
    
    def create_access_token(self, user: UserCredentials) -> str:
        """Create JWT access token"""
        try:
            if not FASTAPI_AVAILABLE:
                # Mock token for testing
                return f"mock_token_{user.username}_{int(time.time())}"
            
            expire = datetime.utcnow() + timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
            
            payload = {
                "sub": user.username,
                "user_id": user.username,  # Using username as user_id for simplicity
                "roles": user.roles,
                "exp": expire,
                "iat": datetime.utcnow()
            }
            
            token = jwt.encode(payload, SECRET_KEY, algorithm=ALGORITHM)
            
            # Track active token
            self.active_tokens[token] = {
                "username": user.username,
                "created_at": datetime.utcnow(),
                "expires_at": expire
            }
            
            return token
            
        except Exception as e:
            logger.error(f"Token creation failed: {e}")
            raise AuthenticationError("Failed to create access token")
    
    def create_refresh_token(self, user: UserCredentials) -> str:
        """Create JWT refresh token"""
        try:
            if not FASTAPI_AVAILABLE:
                return f"mock_refresh_token_{user.username}_{int(time.time())}"
            
            expire = datetime.utcnow() + timedelta(days=REFRESH_TOKEN_EXPIRE_DAYS)
            
            payload = {
                "sub": user.username,
                "type": "refresh",
                "exp": expire,
                "iat": datetime.utcnow()
            }
            
            return jwt.encode(payload, SECRET_KEY, algorithm=ALGORITHM)
            
        except Exception as e:
            logger.error(f"Refresh token creation failed: {e}")
            raise AuthenticationError("Failed to create refresh token")
    
    def verify_token(self, token: str) -> TokenData:
        """Verify and decode JWT token"""
        try:
            if not FASTAPI_AVAILABLE:
                # Mock token verification
                if token.startswith("mock_token_"):
                    parts = token.split("_")
                    username = parts[2] if len(parts) > 2 else "unknown"
                    return TokenData(
                        username=username,
                        user_id=username,
                        roles=["user"],
                        exp=datetime.utcnow() + timedelta(hours=1),
                        iat=datetime.utcnow()
                    )
                else:
                    raise AuthenticationError("Invalid token format")
            
            # Check if token is in active tokens
            if token not in self.active_tokens:
                raise AuthenticationError("Token not found or expired")
            
            payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
            
            username = payload.get("sub")
            if username is None:
                raise AuthenticationError("Invalid token payload")
            
            # Verify user still exists and is active
            user = self.users_db.get(username)
            if not user or not user.is_active:
                raise AuthenticationError("User not found or inactive")
            
            return TokenData(
                username=username,
                user_id=payload.get("user_id", username),
                roles=payload.get("roles", ["user"]),
                exp=datetime.fromtimestamp(payload.get("exp", 0)),
                iat=datetime.fromtimestamp(payload.get("iat", 0))
            )
            
        except JWTError as e:
            logger.warning(f"JWT verification failed: {e}")
            raise AuthenticationError("Invalid token")
        except Exception as e:
            logger.error(f"Token verification error: {e}")
            raise AuthenticationError("Token verification failed")
    
    def revoke_token(self, token: str):
        """Revoke an active token"""
        try:
            self.active_tokens.pop(token, None)
            logger.info("Token revoked successfully")
        except Exception as e:
            logger.error(f"Token revocation failed: {e}")
    
    def check_permission(self, user_roles: List[str], required_roles: List[str]) -> bool:
        """Check if user has required permissions"""
        if "admin" in user_roles:
            return True  # Admin has all permissions
        
        return any(role in user_roles for role in required_roles)
    
    def _is_rate_limited(self, username: str) -> bool:
        """Check if user is rate limited due to failed attempts"""
        if username not in self.failed_attempts:
            return False
        
        attempts = self.failed_attempts[username]
        
        # Allow 5 attempts per 15 minutes
        recent_attempts = [
            attempt for attempt in attempts
            if datetime.utcnow() - attempt < timedelta(minutes=15)
        ]
        
        return len(recent_attempts) >= 5
    
    def _record_failed_attempt(self, username: str):
        """Record a failed login attempt"""
        if username not in self.failed_attempts:
            self.failed_attempts[username] = []
        
        self.failed_attempts[username].append(datetime.utcnow())
        
        # Keep only recent attempts (last 24 hours)
        cutoff = datetime.utcnow() - timedelta(hours=24)
        self.failed_attempts[username] = [
            attempt for attempt in self.failed_attempts[username]
            if attempt > cutoff
        ]
    
    def cleanup_expired_tokens(self):
        """Clean up expired tokens"""
        try:
            current_time = datetime.utcnow()
            expired_tokens = [
                token for token, data in self.active_tokens.items()
                if data["expires_at"] < current_time
            ]
            
            for token in expired_tokens:
                self.active_tokens.pop(token, None)
            
            if expired_tokens:
                logger.info(f"Cleaned up {len(expired_tokens)} expired tokens")
                
        except Exception as e:
            logger.error(f"Token cleanup failed: {e}")

# Global auth manager instance
auth_manager = AuthManager()

# FastAPI dependencies
security = HTTPBearer() if FASTAPI_AVAILABLE else None

async def get_current_user(credentials: HTTPAuthorizationCredentials = Depends(security) if FASTAPI_AVAILABLE else None) -> TokenData:
    """FastAPI dependency to get current authenticated user"""
    if not FASTAPI_AVAILABLE:
        # Mock user for testing
        return TokenData(
            username="mock_user",
            user_id="mock_user",
            roles=["user"],
            exp=datetime.utcnow() + timedelta(hours=1),
            iat=datetime.utcnow()
        )
    
    if not credentials:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Authentication required",
            headers={"WWW-Authenticate": "Bearer"},
        )
    
    try:
        token_data = auth_manager.verify_token(credentials.credentials)
        return token_data
    except AuthenticationError as e:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail=str(e),
            headers={"WWW-Authenticate": "Bearer"},
        )

def require_roles(required_roles: List[str]):
    """Decorator to require specific roles"""
    def role_checker(current_user: TokenData = Depends(get_current_user) if FASTAPI_AVAILABLE else None):
        if not FASTAPI_AVAILABLE:
            return current_user
        
        if not auth_manager.check_permission(current_user.roles, required_roles):
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail=f"Insufficient permissions. Required roles: {required_roles}"
            )
        return current_user
    
    return role_checker

# Convenience dependencies
require_user = require_roles(["user"])
require_admin = require_roles(["admin"])

def get_auth_manager() -> AuthManager:
    """Get the global auth manager instance"""
    return auth_manager