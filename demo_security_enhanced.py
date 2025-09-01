#!/usr/bin/env python3
"""
Enhanced Security System Demo

This script demonstrates the comprehensive security features implemented for
AI WellnessVision, including:

1. HTTPS and WebSocket security
2. Data encryption at rest
3. Enhanced privacy and anonymization
4. User consent management
5. Data protection compliance
"""

import asyncio
import json
from datetime import datetime
from typing import Dict, Any

from src.security import (
    get_encryption_service,
    get_privacy_manager,
    get_consent_manager,
    get_data_protection_service,
    get_security_middleware,
    get_transport_security_manager,
    DataCategory,
    ConsentType,
    AnonymizationLevel
)
from src.utils.logging_config import get_structured_logger

logger = get_structured_logger(__name__)

class SecuritySystemDemo:
    """Comprehensive security system demonstration"""
    
    def 