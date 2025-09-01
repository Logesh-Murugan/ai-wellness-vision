# user_models.py - User-related data models
from datetime import datetime
from typing import Dict, List, Optional, Any
from dataclasses import dataclass, field
from enum import Enum

from .base import BaseModel, add_validators, RequiredValidator, LengthValidator, ChoiceValidator

class UserRole(Enum):
    """User role enumeration"""
    GUEST = "guest"
    USER = "user"
    PREMIUM = "premium"
    ADMIN = "admin"

class SessionStatus(Enum):
    """Session status enumeration"""
    ACTIVE = "active"
    INACTIVE = "inactive"
    EXPIRED = "expired"

@add_validators({
    'language_preference': [RequiredValidator(), ChoiceValidator(['en', 'hi', 'ta', 'te', 'bn', 'gu', 'mr'])],
    'session_id': [RequiredValidator(), LengthValidator(min_length=10)],
})
@dataclass
class UserSession(BaseModel):
    """User session model for tracking user interactions"""
    
    session_id: str = field(default="")  # Will be validated as required
    language_preference: str = "en"
    user_id: Optional[str] = None
    conversation_history: List[Dict[str, Any]] = field(default_factory=list)
    analysis_history: List[Dict[str, Any]] = field(default_factory=list)
    status: SessionStatus = SessionStatus.ACTIVE
    last_activity: datetime = field(default_factory=datetime.utcnow)
    user_agent: Optional[str] = None
    ip_address: Optional[str] = None
    preferences: Dict[str, Any] = field(default_factory=dict)
    
    def add_conversation_entry(self, message: str, response: str, message_type: str = "text") -> None:
        """Add a conversation entry to the history"""
        entry = {
            "timestamp": datetime.utcnow().isoformat(),
            "message": message,
            "response": response,
            "type": message_type,
            "language": self.language_preference
        }
        self.conversation_history.append(entry)
        self.last_activity = datetime.utcnow()
        self.updated_at = datetime.utcnow()
    
    def add_analysis_entry(self, analysis_type: str, result: Dict[str, Any]) -> None:
        """Add an analysis result to the history"""
        entry = {
            "timestamp": datetime.utcnow().isoformat(),
            "analysis_type": analysis_type,
            "result": result,
            "session_id": self.session_id
        }
        self.analysis_history.append(entry)
        self.last_activity = datetime.utcnow()
        self.updated_at = datetime.utcnow()
    
    def get_recent_conversations(self, limit: int = 10) -> List[Dict[str, Any]]:
        """Get recent conversation entries"""
        return self.conversation_history[-limit:] if self.conversation_history else []
    
    def get_recent_analyses(self, limit: int = 5) -> List[Dict[str, Any]]:
        """Get recent analysis entries"""
        return self.analysis_history[-limit:] if self.analysis_history else []
    
    def is_active(self) -> bool:
        """Check if session is active"""
        return self.status == SessionStatus.ACTIVE
    
    def expire_session(self) -> None:
        """Mark session as expired"""
        self.status = SessionStatus.EXPIRED
        self.updated_at = datetime.utcnow()

@add_validators({
    'user_id': [RequiredValidator(), LengthValidator(min_length=5)],
    'email': [RequiredValidator()],  # EmailValidator would be added here
    'role': [RequiredValidator()],
})
@dataclass
class User(BaseModel):
    """User model for registered users"""
    
    user_id: str = field(default="")  # Will be validated as required
    email: str = field(default="")  # Will be validated as required
    role: UserRole = UserRole.USER
    display_name: Optional[str] = None
    preferred_language: str = "en"
    timezone: str = "UTC"
    is_active: bool = True
    last_login: Optional[datetime] = None
    profile_data: Dict[str, Any] = field(default_factory=dict)
    privacy_settings: Dict[str, bool] = field(default_factory=lambda: {
        "data_collection": True,
        "analytics": True,
        "personalization": True,
        "marketing": False
    })
    
    def update_last_login(self) -> None:
        """Update last login timestamp"""
        self.last_login = datetime.utcnow()
        self.updated_at = datetime.utcnow()
    
    def update_profile(self, **profile_data) -> None:
        """Update user profile data"""
        self.profile_data.update(profile_data)
        self.updated_at = datetime.utcnow()
    
    def update_privacy_settings(self, **settings) -> None:
        """Update privacy settings"""
        self.privacy_settings.update(settings)
        self.updated_at = datetime.utcnow()
    
    def can_access_feature(self, feature: str) -> bool:
        """Check if user can access a specific feature based on role"""
        feature_permissions = {
            UserRole.GUEST: ["basic_analysis", "limited_chat"],
            UserRole.USER: ["basic_analysis", "chat", "history", "export"],
            UserRole.PREMIUM: ["advanced_analysis", "chat", "history", "export", "priority_support"],
            UserRole.ADMIN: ["all"]
        }
        
        user_permissions = feature_permissions.get(self.role, [])
        return "all" in user_permissions or feature in user_permissions