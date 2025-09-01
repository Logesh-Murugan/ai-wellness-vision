# __init__.py - Security module initialization
"""
AI WellnessVision Security Module

This module provides comprehensive security features including:
- Data encryption (at rest and in transit)
- Privacy management and data anonymization
- User consent management
- Transport security (HTTPS/WebSocket)
- Data protection and compliance
"""

from .encryption import get_encryption_service, EncryptionService
from .privacy import get_privacy_manager, PrivacyManager, DataCategory, AnonymizationLevel
from .consent import get_consent_manager, ConsentManager, ConsentType, ConsentStatus
from .data_protection import get_data_protection_service, DataProtectionService
from .security_middleware import get_security_middleware, SecurityMiddleware
from .transport_security import get_transport_security_manager, TransportSecurityManager

__all__ = [
    # Services
    'get_encryption_service',
    'get_privacy_manager', 
    'get_consent_manager',
    'get_data_protection_service',
    'get_security_middleware',
    'get_transport_security_manager',
    
    # Classes
    'EncryptionService',
    'PrivacyManager',
    'ConsentManager', 
    'DataProtectionService',
    'SecurityMiddleware',
    'TransportSecurityManager',
    
    # Enums
    'DataCategory',
    'AnonymizationLevel',
    'ConsentType',
    'ConsentStatus'
]

# Version info
__version__ = "1.0.0"
__author__ = "AI WellnessVision Security Team"