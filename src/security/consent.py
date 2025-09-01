# consent.py - User consent management system
from typing import Dict, Any, Optional, List, Set
from datetime import datetime, timedelta
from dataclasses import dataclass, field
from enum import Enum
import json

from src.utils.logging_config import get_structured_logger
from src.utils.error_handling import handle_error, ErrorCode, ErrorSeverity, ErrorContext

logger = get_structured_logger(__name__)

class ConsentType(Enum):
    """Types of consent"""
    DATA_PROCESSING = "data_processing"
    MARKETING = "marketing"
    ANALYTICS = "analytics"
    THIRD_PARTY_SHARING = "third_party_sharing"
    BIOMETRIC_DATA = "biometric_data"
    HEALTH_DATA = "health_data"
    LOCATION_TRACKING = "location_tracking"
    COOKIES = "cookies"

class ConsentStatus(Enum):
    """Consent status values"""
    GRANTED = "granted"
    DENIED = "denied"
    WITHDRAWN = "withdrawn"
    EXPIRED = "expired"
    PENDING = "pending"

class ConsentBasis(Enum):
    """Legal basis for data processing"""
    CONSENT = "consent"                    # Article 6(1)(a) GDPR
    CONTRACT = "contract"                  # Article 6(1)(b) GDPR
    LEGAL_OBLIGATION = "legal_obligation"  # Article 6(1)(c) GDPR
    VITAL_INTERESTS = "vital_interests"    # Article 6(1)(d) GDPR
    PUBLIC_TASK = "public_task"           # Article 6(1)(e) GDPR
    LEGITIMATE_INTERESTS = "legitimate_interests"  # Article 6(1)(f) GDPR

@dataclass
class ConsentRecord:
    """Individual consent record"""
    consent_id: str
    user_id: str
    consent_type: ConsentType
    status: ConsentStatus
    legal_basis: ConsentBasis
    purpose: str
    granted_at: Optional[datetime] = None
    withdrawn_at: Optional[datetime] = None
    expires_at: Optional[datetime] = None
    version: str = "1.0"
    metadata: Dict[str, Any] = field(default_factory=dict)
    
    def is_valid(self) -> bool:
        """Check if consent is currently valid"""
        if self.status != ConsentStatus.GRANTED:
            return False
        
        if self.expires_at and datetime.now() > self.expires_at:
            return False
        
        return True
    
    def is_expired(self) -> bool:
        """Check if consent has expired"""
        return self.expires_at and datetime.now() > self.expires_at

@dataclass
class ConsentTemplate:
    """Template for consent requests"""
    template_id: str
    consent_type: ConsentType
    title: str
    description: str
    purpose: str
    legal_basis: ConsentBasis
    required: bool = False
    expires_in_days: Optional[int] = None
    version: str = "1.0"
    created_at: datetime = field(default_factory=datetime.now)

@dataclass
class ConsentRequest:
    """Consent request to user"""
    request_id: str
    user_id: str
    consent_templates: List[ConsentTemplate]
    requested_at: datetime = field(default_factory=datetime.now)
    expires_at: Optional[datetime] = None
    completed: bool = False
    metadata: Dict[str, Any] = field(default_factory=dict)

class ConsentValidator:
    """Validates consent requirements"""
    
    def __init__(self):
        self.required_consents = {
            ConsentType.DATA_PROCESSING: True,
            ConsentType.HEALTH_DATA: True,
            ConsentType.BIOMETRIC_DATA: True,
        }
    
    def validate_consent_for_operation(self, user_id: str, operation: str, 
                                     user_consents: Dict[ConsentType, ConsentRecord]) -> Dict[str, Any]:
        """Validate if user has required consents for operation"""
        validation_result = {
            "valid": True,
            "missing_consents": [],
            "expired_consents": [],
            "warnings": []
        }
        
        # Define operation requirements
        operation_requirements = self._get_operation_requirements(operation)
        
        for consent_type in operation_requirements:
            consent_record = user_consents.get(consent_type)
            
            if not consent_record:
                validation_result["missing_consents"].append(consent_type.value)
                validation_result["valid"] = False
            elif not consent_record.is_valid():
                if consent_record.is_expired():
                    validation_result["expired_consents"].append(consent_type.value)
                validation_result["valid"] = False
            elif consent_record.expires_at and consent_record.expires_at < datetime.now() + timedelta(days=30):
                validation_result["warnings"].append(f"Consent for {consent_type.value} expires soon")
        
        return validation_result
    
    def _get_operation_requirements(self, operation: str) -> List[ConsentType]:
        """Get consent requirements for specific operations"""
        requirements_map = {
            "image_analysis": [ConsentType.DATA_PROCESSING, ConsentType.BIOMETRIC_DATA, ConsentType.HEALTH_DATA],
            "voice_processing": [ConsentType.DATA_PROCESSING, ConsentType.BIOMETRIC_DATA],
            "health_assessment": [ConsentType.DATA_PROCESSING, ConsentType.HEALTH_DATA],
            "data_analytics": [ConsentType.DATA_PROCESSING, ConsentType.ANALYTICS],
            "marketing_communication": [ConsentType.MARKETING],
            "third_party_integration": [ConsentType.THIRD_PARTY_SHARING],
            "location_services": [ConsentType.LOCATION_TRACKING],
        }
        
        return requirements_map.get(operation, [ConsentType.DATA_PROCESSING])

class ConsentManager:
    """Main consent management service"""
    
    def __init__(self):
        self.consent_records: Dict[str, Dict[ConsentType, ConsentRecord]] = {}  # user_id -> consents
        self.consent_templates: Dict[str, ConsentTemplate] = {}
        self.consent_requests: Dict[str, ConsentRequest] = {}
        self.consent_validator = ConsentValidator()
        
        # Initialize default consent templates
        self._initialize_default_templates()
    
    def _initialize_default_templates(self):
        """Initialize default consent templates"""
        default_templates = [
            ConsentTemplate(
                template_id="data_processing_consent",
                consent_type=ConsentType.DATA_PROCESSING,
                title="Data Processing Consent",
                description="We need your consent to process your personal data for providing health analysis services.",
                purpose="To analyze your health data and provide personalized recommendations",
                legal_basis=ConsentBasis.CONSENT,
                required=True,
                expires_in_days=365
            ),
            ConsentTemplate(
                template_id="health_data_consent",
                consent_type=ConsentType.HEALTH_DATA,
                title="Health Data Processing",
                description="Consent to process sensitive health information including medical images and health assessments.",
                purpose="To provide accurate health analysis and recommendations",
                legal_basis=ConsentBasis.CONSENT,
                required=True,
                expires_in_days=365
            ),
            ConsentTemplate(
                template_id="biometric_data_consent",
                consent_type=ConsentType.BIOMETRIC_DATA,
                title="Biometric Data Processing",
                description="Consent to process biometric data including facial images and voice recordings.",
                purpose="To analyze images and voice for health assessment purposes",
                legal_basis=ConsentBasis.CONSENT,
                required=True,
                expires_in_days=365
            ),
            ConsentTemplate(
                template_id="analytics_consent",
                consent_type=ConsentType.ANALYTICS,
                title="Analytics and Improvement",
                description="Help us improve our services by allowing anonymous usage analytics.",
                purpose="To improve service quality and user experience",
                legal_basis=ConsentBasis.LEGITIMATE_INTERESTS,
                required=False,
                expires_in_days=730
            ),
            ConsentTemplate(
                template_id="marketing_consent",
                consent_type=ConsentType.MARKETING,
                title="Marketing Communications",
                description="Receive updates about new features and health tips via email.",
                purpose="To send relevant health information and service updates",
                legal_basis=ConsentBasis.CONSENT,
                required=False,
                expires_in_days=365
            )
        ]
        
        for template in default_templates:
            self.consent_templates[template.template_id] = template
        
        logger.info("Default consent templates initialized")
    
    def create_consent_request(self, user_id: str, template_ids: List[str],
                             expires_in_hours: int = 24) -> ConsentRequest:
        """Create a consent request for user"""
        try:
            request_id = f"consent_req_{user_id}_{int(datetime.now().timestamp())}"
            
            # Get templates
            templates = []
            for template_id in template_ids:
                template = self.consent_templates.get(template_id)
                if template:
                    templates.append(template)
                else:
                    logger.warning(f"Consent template not found: {template_id}")
            
            if not templates:
                raise ValueError("No valid consent templates found")
            
            consent_request = ConsentRequest(
                request_id=request_id,
                user_id=user_id,
                consent_templates=templates,
                expires_at=datetime.now() + timedelta(hours=expires_in_hours)
            )
            
            self.consent_requests[request_id] = consent_request
            
            logger.info(f"Created consent request {request_id} for user {user_id}")
            return consent_request
            
        except Exception as e:
            logger.error(f"Failed to create consent request: {e}")
            handle_error(
                ErrorCode.VALIDATION_ERROR,
                f"Failed to create consent request: {str(e)}",
                ErrorSeverity.MEDIUM,
                ErrorContext(user_id=user_id, service_name="consent_manager")
            )
            raise
    
    def process_consent_response(self, request_id: str, 
                               consent_responses: Dict[str, bool]) -> Dict[str, Any]:
        """Process user's consent responses"""
        try:
            consent_request = self.consent_requests.get(request_id)
            if not consent_request:
                raise ValueError(f"Consent request {request_id} not found")
            
            if consent_request.completed:
                raise ValueError(f"Consent request {request_id} already completed")
            
            if consent_request.expires_at and datetime.now() > consent_request.expires_at:
                raise ValueError(f"Consent request {request_id} has expired")
            
            user_id = consent_request.user_id
            processed_consents = []
            
            # Initialize user consent records if not exists
            if user_id not in self.consent_records:
                self.consent_records[user_id] = {}
            
            # Process each consent response
            for template in consent_request.consent_templates:
                template_id = template.template_id
                granted = consent_responses.get(template_id, False)
                
                # Check if required consent was denied
                if template.required and not granted:
                    raise ValueError(f"Required consent {template_id} was denied")
                
                # Create consent record
                consent_id = f"consent_{user_id}_{template.consent_type.value}_{int(datetime.now().timestamp())}"
                
                expires_at = None
                if template.expires_in_days:
                    expires_at = datetime.now() + timedelta(days=template.expires_in_days)
                
                consent_record = ConsentRecord(
                    consent_id=consent_id,
                    user_id=user_id,
                    consent_type=template.consent_type,
                    status=ConsentStatus.GRANTED if granted else ConsentStatus.DENIED,
                    legal_basis=template.legal_basis,
                    purpose=template.purpose,
                    granted_at=datetime.now() if granted else None,
                    expires_at=expires_at,
                    version=template.version,
                    metadata={
                        "template_id": template_id,
                        "request_id": request_id
                    }
                )
                
                # Store consent record
                self.consent_records[user_id][template.consent_type] = consent_record
                processed_consents.append({
                    "consent_type": template.consent_type.value,
                    "status": consent_record.status.value,
                    "expires_at": expires_at.isoformat() if expires_at else None
                })
            
            # Mark request as completed
            consent_request.completed = True
            
            logger.info(f"Processed consent responses for user {user_id}")
            
            return {
                "user_id": user_id,
                "request_id": request_id,
                "processed_consents": processed_consents,
                "completed_at": datetime.now().isoformat(),
                "status": "success"
            }
            
        except Exception as e:
            logger.error(f"Failed to process consent response: {e}")
            handle_error(
                ErrorCode.VALIDATION_ERROR,
                f"Failed to process consent response: {str(e)}",
                ErrorSeverity.HIGH,
                ErrorContext(service_name="consent_manager", function_name="process_consent_response")
            )
            raise
    
    def grant_consent(self, user_id: str, consent_type: ConsentType, 
                     purpose: str, legal_basis: ConsentBasis = ConsentBasis.CONSENT,
                     expires_in_days: Optional[int] = None) -> ConsentRecord:
        """Grant consent for user"""
        try:
            consent_id = f"consent_{user_id}_{consent_type.value}_{int(datetime.now().timestamp())}"
            
            expires_at = None
            if expires_in_days:
                expires_at = datetime.now() + timedelta(days=expires_in_days)
            
            consent_record = ConsentRecord(
                consent_id=consent_id,
                user_id=user_id,
                consent_type=consent_type,
                status=ConsentStatus.GRANTED,
                legal_basis=legal_basis,
                purpose=purpose,
                granted_at=datetime.now(),
                expires_at=expires_at
            )
            
            # Initialize user consent records if not exists
            if user_id not in self.consent_records:
                self.consent_records[user_id] = {}
            
            self.consent_records[user_id][consent_type] = consent_record
            
            logger.info(f"Granted consent {consent_type.value} for user {user_id}")
            return consent_record
            
        except Exception as e:
            logger.error(f"Failed to grant consent: {e}")
            handle_error(
                ErrorCode.VALIDATION_ERROR,
                f"Failed to grant consent: {str(e)}",
                ErrorSeverity.MEDIUM,
                ErrorContext(user_id=user_id, service_name="consent_manager")
            )
            raise
    
    def withdraw_consent(self, user_id: str, consent_type: ConsentType) -> bool:
        """Withdraw consent for user"""
        try:
            if user_id not in self.consent_records:
                return False
            
            consent_record = self.consent_records[user_id].get(consent_type)
            if not consent_record:
                return False
            
            consent_record.status = ConsentStatus.WITHDRAWN
            consent_record.withdrawn_at = datetime.now()
            
            logger.info(f"Withdrew consent {consent_type.value} for user {user_id}")
            return True
            
        except Exception as e:
            logger.error(f"Failed to withdraw consent: {e}")
            return False
    
    def check_consent(self, user_id: str, consent_type: ConsentType) -> bool:
        """Check if user has valid consent for specific type"""
        if user_id not in self.consent_records:
            return False
        
        consent_record = self.consent_records[user_id].get(consent_type)
        if not consent_record:
            return False
        
        return consent_record.is_valid()
    
    def validate_operation_consent(self, user_id: str, operation: str) -> Dict[str, Any]:
        """Validate if user has required consents for operation"""
        user_consents = self.consent_records.get(user_id, {})
        return self.consent_validator.validate_consent_for_operation(user_id, operation, user_consents)
    
    def get_user_consents(self, user_id: str) -> Dict[str, Any]:
        """Get all consents for user"""
        if user_id not in self.consent_records:
            return {"user_id": user_id, "consents": {}}
        
        user_consents = self.consent_records[user_id]
        
        consents_summary = {}
        for consent_type, consent_record in user_consents.items():
            consents_summary[consent_type.value] = {
                "status": consent_record.status.value,
                "granted_at": consent_record.granted_at.isoformat() if consent_record.granted_at else None,
                "expires_at": consent_record.expires_at.isoformat() if consent_record.expires_at else None,
                "withdrawn_at": consent_record.withdrawn_at.isoformat() if consent_record.withdrawn_at else None,
                "purpose": consent_record.purpose,
                "legal_basis": consent_record.legal_basis.value,
                "is_valid": consent_record.is_valid()
            }
        
        return {
            "user_id": user_id,
            "consents": consents_summary,
            "total_consents": len(user_consents),
            "valid_consents": sum(1 for c in user_consents.values() if c.is_valid())
        }
    
    def get_expiring_consents(self, days_ahead: int = 30) -> List[Dict[str, Any]]:
        """Get consents that will expire within specified days"""
        expiring_consents = []
        cutoff_date = datetime.now() + timedelta(days=days_ahead)
        
        for user_id, user_consents in self.consent_records.items():
            for consent_type, consent_record in user_consents.items():
                if (consent_record.expires_at and 
                    consent_record.status == ConsentStatus.GRANTED and
                    consent_record.expires_at <= cutoff_date):
                    
                    expiring_consents.append({
                        "user_id": user_id,
                        "consent_type": consent_type.value,
                        "expires_at": consent_record.expires_at.isoformat(),
                        "days_until_expiry": (consent_record.expires_at - datetime.now()).days
                    })
        
        return sorted(expiring_consents, key=lambda x: x["days_until_expiry"])
    
    def cleanup_expired_consents(self) -> Dict[str, Any]:
        """Mark expired consents and clean up old records"""
        try:
            current_time = datetime.now()
            expired_count = 0
            cleaned_count = 0
            
            for user_id, user_consents in self.consent_records.items():
                for consent_type, consent_record in list(user_consents.items()):
                    # Mark expired consents
                    if consent_record.is_expired() and consent_record.status == ConsentStatus.GRANTED:
                        consent_record.status = ConsentStatus.EXPIRED
                        expired_count += 1
                    
                    # Remove very old withdrawn/expired consents (older than 3 years)
                    if consent_record.status in [ConsentStatus.WITHDRAWN, ConsentStatus.EXPIRED]:
                        reference_date = consent_record.withdrawn_at or consent_record.expires_at
                        if reference_date and (current_time - reference_date).days > 1095:  # 3 years
                            del user_consents[consent_type]
                            cleaned_count += 1
            
            logger.info(f"Consent cleanup: {expired_count} expired, {cleaned_count} cleaned")
            
            return {
                "expired_consents": expired_count,
                "cleaned_consents": cleaned_count,
                "cleanup_completed_at": current_time.isoformat()
            }
            
        except Exception as e:
            logger.error(f"Consent cleanup failed: {e}")
            return {"error": str(e)}
    
    def export_user_consents(self, user_id: str) -> Dict[str, Any]:
        """Export all consent data for user (data portability)"""
        try:
            user_consents = self.get_user_consents(user_id)
            
            # Add detailed consent history
            if user_id in self.consent_records:
                detailed_consents = []
                for consent_type, consent_record in self.consent_records[user_id].items():
                    detailed_consents.append({
                        "consent_id": consent_record.consent_id,
                        "consent_type": consent_type.value,
                        "status": consent_record.status.value,
                        "legal_basis": consent_record.legal_basis.value,
                        "purpose": consent_record.purpose,
                        "granted_at": consent_record.granted_at.isoformat() if consent_record.granted_at else None,
                        "withdrawn_at": consent_record.withdrawn_at.isoformat() if consent_record.withdrawn_at else None,
                        "expires_at": consent_record.expires_at.isoformat() if consent_record.expires_at else None,
                        "version": consent_record.version,
                        "metadata": consent_record.metadata
                    })
                
                user_consents["detailed_consents"] = detailed_consents
            
            user_consents["exported_at"] = datetime.now().isoformat()
            
            return user_consents
            
        except Exception as e:
            logger.error(f"Failed to export user consents: {e}")
            return {"error": str(e), "user_id": user_id}
    
    def delete_user_consents(self, user_id: str) -> bool:
        """Delete all consent records for user"""
        try:
            if user_id in self.consent_records:
                del self.consent_records[user_id]
            
            # Remove from consent requests
            requests_to_remove = [
                req_id for req_id, req in self.consent_requests.items()
                if req.user_id == user_id
            ]
            for req_id in requests_to_remove:
                del self.consent_requests[req_id]
            
            logger.info(f"Deleted all consent records for user {user_id}")
            return True
            
        except Exception as e:
            logger.error(f"Failed to delete user consents: {e}")
            return False
    
    def update_consent_preferences(self, user_id: str, 
                                  preferences: Dict[ConsentType, bool]) -> Dict[str, Any]:
        """Update user consent preferences"""
        try:
            updated_consents = []
            
            for consent_type, granted in preferences.items():
                if granted:
                    # Grant or update consent
                    consent_record = self.grant_consent(
                        user_id, consent_type, 
                        f"Updated preference for {consent_type.value}",
                        expires_in_days=365
                    )
                    updated_consents.append({
                        "consent_type": consent_type.value,
                        "action": "granted",
                        "expires_at": consent_record.expires_at.isoformat() if consent_record.expires_at else None
                    })
                else:
                    # Withdraw consent
                    if self.withdraw_consent(user_id, consent_type):
                        updated_consents.append({
                            "consent_type": consent_type.value,
                            "action": "withdrawn",
                            "withdrawn_at": datetime.now().isoformat()
                        })
            
            logger.info(f"Updated consent preferences for user {user_id}")
            
            return {
                "user_id": user_id,
                "updated_consents": updated_consents,
                "updated_at": datetime.now().isoformat(),
                "status": "success"
            }
            
        except Exception as e:
            logger.error(f"Failed to update consent preferences: {e}")
            return {
                "user_id": user_id,
                "status": "error",
                "error": str(e)
            }
    
    def get_consent_dashboard(self, user_id: str) -> Dict[str, Any]:
        """Get user consent dashboard with recommendations"""
        try:
            user_consents = self.get_user_consents(user_id)
            
            # Get recommendations for missing consents
            recommendations = []
            for template in self.consent_templates.values():
                if template.consent_type not in self.consent_records.get(user_id, {}):
                    recommendations.append({
                        "consent_type": template.consent_type.value,
                        "title": template.title,
                        "description": template.description,
                        "required": template.required,
                        "purpose": template.purpose
                    })
            
            # Get expiring consents for this user
            expiring_consents = [
                consent for consent in self.get_expiring_consents(30)
                if consent["user_id"] == user_id
            ]
            
            return {
                "user_id": user_id,
                "current_consents": user_consents["consents"],
                "recommendations": recommendations,
                "expiring_consents": expiring_consents,
                "consent_health_score": self._calculate_consent_health_score(user_id),
                "last_updated": datetime.now().isoformat()
            }
            
        except Exception as e:
            logger.error(f"Failed to get consent dashboard: {e}")
            return {
                "user_id": user_id,
                "error": str(e)
            }
    
    def _calculate_consent_health_score(self, user_id: str) -> Dict[str, Any]:
        """Calculate consent health score for user"""
        try:
            if user_id not in self.consent_records:
                return {"score": 0, "status": "no_consents"}
            
            user_consents = self.consent_records[user_id]
            total_templates = len(self.consent_templates)
            
            # Count valid consents
            valid_consents = sum(1 for consent in user_consents.values() if consent.is_valid())
            
            # Count required consents
            required_templates = sum(1 for template in self.consent_templates.values() if template.required)
            required_consents = sum(
                1 for consent_type, consent in user_consents.items()
                if consent.is_valid() and any(
                    template.consent_type == consent_type and template.required
                    for template in self.consent_templates.values()
                )
            )
            
            # Calculate score (0-100)
            base_score = (valid_consents / total_templates) * 100 if total_templates > 0 else 0
            required_bonus = (required_consents / required_templates) * 20 if required_templates > 0 else 0
            
            final_score = min(100, base_score + required_bonus)
            
            # Determine status
            if final_score >= 90:
                status = "excellent"
            elif final_score >= 70:
                status = "good"
            elif final_score >= 50:
                status = "fair"
            else:
                status = "needs_attention"
            
            return {
                "score": round(final_score, 1),
                "status": status,
                "valid_consents": valid_consents,
                "total_possible": total_templates,
                "required_consents": required_consents,
                "required_total": required_templates
            }
            
        except Exception as e:
            logger.error(f"Failed to calculate consent health score: {e}")
            return {"score": 0, "status": "error", "error": str(e)}

    def get_consent_statistics(self) -> Dict[str, Any]:
        """Get consent management statistics"""
        total_users = len(self.consent_records)
        total_consents = sum(len(consents) for consents in self.consent_records.values())
        
        # Count by status
        status_counts = {}
        type_counts = {}
        
        for user_consents in self.consent_records.values():
            for consent_record in user_consents.values():
                status = consent_record.status.value
                consent_type = consent_record.consent_type.value
                
                status_counts[status] = status_counts.get(status, 0) + 1
                type_counts[consent_type] = type_counts.get(consent_type, 0) + 1
        
        return {
            "total_users": total_users,
            "total_consents": total_consents,
            "consent_templates": len(self.consent_templates),
            "pending_requests": len([r for r in self.consent_requests.values() if not r.completed]),
            "by_status": status_counts,
            "by_type": type_counts,
            "expiring_soon": len(self.get_expiring_consents(30))
        }

# Global consent manager instance
consent_manager = ConsentManager()

def get_consent_manager() -> ConsentManager:
    """Get global consent manager instance"""
    return consent_manager