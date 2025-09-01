# data_protection.py - Comprehensive data protection service
from typing import Dict, Any, Optional, List, Union
from datetime import datetime, timedelta
from dataclasses import dataclass, field
from enum import Enum
import json

from src.security.encryption import get_encryption_service, EncryptionType, EncryptedData
from src.security.privacy import get_privacy_manager, DataCategory, AnonymizationLevel
from src.security.consent import get_consent_manager, ConsentType
from src.utils.logging_config import get_structured_logger
from src.utils.error_handling import handle_error, ErrorCode, ErrorSeverity, ErrorContext

logger = get_structured_logger(__name__)

class DataClassification(Enum):
    """Data classification levels"""
    PUBLIC = "public"
    INTERNAL = "internal"
    CONFIDENTIAL = "confidential"
    RESTRICTED = "restricted"

class ProcessingActivity(Enum):
    """Types of data processing activities"""
    COLLECTION = "collection"
    STORAGE = "storage"
    ANALYSIS = "analysis"
    SHARING = "sharing"
    DELETION = "deletion"
    ANONYMIZATION = "anonymization"

@dataclass
class DataProtectionPolicy:
    """Data protection policy definition"""
    policy_id: str
    name: str
    description: str
    data_categories: List[DataCategory]
    classification: DataClassification
    encryption_required: bool
    anonymization_level: AnonymizationLevel
    retention_days: Optional[int] = None
    consent_required: List[ConsentType] = field(default_factory=list)
    created_at: datetime = field(default_factory=datetime.now)
    is_active: bool = True

@dataclass
class DataProcessingLog:
    """Log entry for data processing activities"""
    log_id: str
    user_id: str
    activity: ProcessingActivity
    data_category: DataCategory
    data_classification: DataClassification
    policy_applied: str
    encryption_used: bool
    anonymization_applied: AnonymizationLevel
    consent_verified: bool
    processed_at: datetime = field(default_factory=datetime.now)
    metadata: Dict[str, Any] = field(default_factory=dict)

class DataProtectionService:
    """Main data protection service"""
    
    def __init__(self):
        self.encryption_service = get_encryption_service()
        self.privacy_manager = get_privacy_manager()
        self.consent_manager = get_consent_manager()
        
        self.protection_policies: Dict[str, DataProtectionPolicy] = {}
        self.processing_logs: List[DataProcessingLog] = []
        self.max_log_size = 10000
        
        # Initialize default policies
        self._initialize_default_policies()
    
    def _initialize_default_policies(self):
        """Initialize default data protection policies"""
        default_policies = [
            DataProtectionPolicy(
                policy_id="health_data_protection",
                name="Health Data Protection Policy",
                description="Comprehensive protection for sensitive health information",
                data_categories=[DataCategory.HEALTH_DATA],
                classification=DataClassification.RESTRICTED,
                encryption_required=True,
                anonymization_level=AnonymizationLevel.PSEUDONYMIZATION,
                retention_days=2555,  # 7 years
                consent_required=[ConsentType.HEALTH_DATA, ConsentType.DATA_PROCESSING]
            ),
            DataProtectionPolicy(
                policy_id="biometric_data_protection",
                name="Biometric Data Protection Policy",
                description="Protection for biometric data including images and voice",
                data_categories=[DataCategory.BIOMETRIC_DATA],
                classification=DataClassification.RESTRICTED,
                encryption_required=True,
                anonymization_level=AnonymizationLevel.PSEUDONYMIZATION,
                retention_days=1095,  # 3 years
                consent_required=[ConsentType.BIOMETRIC_DATA, ConsentType.DATA_PROCESSING]
            ),
            DataProtectionPolicy(
                policy_id="personal_identifier_protection",
                name="Personal Identifier Protection Policy",
                description="Protection for personal identifiers like names, emails, phone numbers",
                data_categories=[DataCategory.PERSONAL_IDENTIFIER],
                classification=DataClassification.CONFIDENTIAL,
                encryption_required=True,
                anonymization_level=AnonymizationLevel.PSEUDONYMIZATION,
                retention_days=365,
                consent_required=[ConsentType.DATA_PROCESSING]
            ),
            DataProtectionPolicy(
                policy_id="behavioral_data_protection",
                name="Behavioral Data Protection Policy",
                description="Protection for user behavior and usage patterns",
                data_categories=[DataCategory.BEHAVIORAL_DATA],
                classification=DataClassification.INTERNAL,
                encryption_required=False,
                anonymization_level=AnonymizationLevel.GENERALIZATION,
                retention_days=730,  # 2 years
                consent_required=[ConsentType.ANALYTICS]
            ),
            DataProtectionPolicy(
                policy_id="technical_data_protection",
                name="Technical Data Protection Policy",
                description="Protection for technical data like IP addresses, device info",
                data_categories=[DataCategory.TECHNICAL_DATA],
                classification=DataClassification.INTERNAL,
                encryption_required=False,
                anonymization_level=AnonymizationLevel.GENERALIZATION,
                retention_days=90
            )
        ]
        
        for policy in default_policies:
            self.protection_policies[policy.policy_id] = policy
        
        logger.info("Default data protection policies initialized")
    
    def add_protection_policy(self, policy: DataProtectionPolicy):
        """Add a new data protection policy"""
        self.protection_policies[policy.policy_id] = policy
        logger.info(f"Added data protection policy: {policy.policy_id}")
    
    def process_data_securely(self, user_id: str, data: Dict[str, Any], 
                             data_category: DataCategory, processing_purpose: str,
                             activity: ProcessingActivity = ProcessingActivity.ANALYSIS) -> Dict[str, Any]:
        """Process data according to protection policies"""
        try:
            # Find applicable policy
            policy = self._find_applicable_policy(data_category)
            if not policy:
                raise ValueError(f"No protection policy found for category: {data_category}")
            
            # Verify consent if required
            consent_verified = self._verify_consent(user_id, policy)
            if not consent_verified and policy.consent_required:
                raise ValueError(f"Required consent not granted for {data_category}")
            
            # Apply encryption if required
            encrypted_data = data
            encryption_used = False
            if policy.encryption_required:
                encrypted_data = self._encrypt_sensitive_fields(data, policy)
                encryption_used = True
            
            # Apply anonymization
            anonymized_data = self.privacy_manager.process_data(
                user_id, encrypted_data, data_category, processing_purpose
            )
            
            # Log processing activity
            self._log_processing_activity(
                user_id, activity, data_category, policy, 
                encryption_used, consent_verified, processing_purpose
            )
            
            logger.info(f"Securely processed {data_category.value} data for user {user_id}")
            return anonymized_data
            
        except Exception as e:
            logger.error(f"Secure data processing failed: {e}")
            handle_error(
                ErrorCode.DATA_BREACH_DETECTED,
                f"Failed to process data securely: {str(e)}",
                ErrorSeverity.CRITICAL,
                ErrorContext(user_id=user_id, service_name="data_protection_service")
            )
            raise
    
    def _find_applicable_policy(self, data_category: DataCategory) -> Optional[DataProtectionPolicy]:
        """Find applicable protection policy for data category"""
        for policy in self.protection_policies.values():
            if data_category in policy.data_categories and policy.is_active:
                return policy
        return None
    
    def _verify_consent(self, user_id: str, policy: DataProtectionPolicy) -> bool:
        """Verify user has required consents"""
        if not policy.consent_required:
            return True
        
        for consent_type in policy.consent_required:
            if not self.consent_manager.check_consent(user_id, consent_type):
                logger.warning(f"Missing consent {consent_type.value} for user {user_id}")
                return False
        
        return True
    
    def _encrypt_sensitive_fields(self, data: Dict[str, Any], 
                                 policy: DataProtectionPolicy) -> Dict[str, Any]:
        """Encrypt sensitive fields in data"""
        encrypted_data = {}
        
        for field, value in data.items():
            if self._is_sensitive_field(field, policy):
                if isinstance(value, str):
                    encrypted_value = self.encryption_service.encrypt_data(
                        value, encryption_type=EncryptionType.SYMMETRIC
                    )
                    # Store as base64 for JSON serialization
                    import base64
                    encrypted_data[field] = {
                        "encrypted": True,
                        "data": base64.b64encode(encrypted_value.encrypted_content).decode('utf-8'),
                        "key_id": encrypted_value.key_id
                    }
                else:
                    encrypted_data[field] = value
            else:
                encrypted_data[field] = value
        
        return encrypted_data
    
    def _is_sensitive_field(self, field_name: str, policy: DataProtectionPolicy) -> bool:
        """Determine if field is sensitive based on policy"""
        sensitive_patterns = {
            DataCategory.HEALTH_DATA: ['diagnosis', 'symptom', 'condition', 'medical', 'health'],
            DataCategory.PERSONAL_IDENTIFIER: ['name', 'email', 'phone', 'id', 'ssn'],
            DataCategory.BIOMETRIC_DATA: ['image', 'voice', 'fingerprint', 'face'],
            DataCategory.LOCATION_DATA: ['location', 'address', 'gps', 'coordinates']
        }
        
        field_lower = field_name.lower()
        for category in policy.data_categories:
            patterns = sensitive_patterns.get(category, [])
            if any(pattern in field_lower for pattern in patterns):
                return True
        
        return False
    
    def _log_processing_activity(self, user_id: str, activity: ProcessingActivity,
                               data_category: DataCategory, policy: DataProtectionPolicy,
                               encryption_used: bool, consent_verified: bool,
                               processing_purpose: str):
        """Log data processing activity"""
        log_id = f"log_{user_id}_{int(datetime.now().timestamp())}"
        
        log_entry = DataProcessingLog(
            log_id=log_id,
            user_id=user_id,
            activity=activity,
            data_category=data_category,
            data_classification=policy.classification,
            policy_applied=policy.policy_id,
            encryption_used=encryption_used,
            anonymization_applied=policy.anonymization_level,
            consent_verified=consent_verified,
            metadata={
                "processing_purpose": processing_purpose,
                "policy_name": policy.name
            }
        )
        
        self.processing_logs.append(log_entry)
        
        # Maintain log size limit
        if len(self.processing_logs) > self.max_log_size:
            self.processing_logs = self.processing_logs[-self.max_log_size:]
    
    def decrypt_data(self, encrypted_data: Dict[str, Any]) -> Dict[str, Any]:
        """Decrypt previously encrypted data"""
        try:
            decrypted_data = {}
            
            for field, value in encrypted_data.items():
                if isinstance(value, dict) and value.get("encrypted"):
                    # Decrypt the field
                    import base64
                    encrypted_content = base64.b64decode(value["data"])
                    key_id = value["key_id"]
                    
                    # Create EncryptedData object
                    encrypted_obj = EncryptedData(
                        encrypted_content=encrypted_content,
                        key_id=key_id,
                        encryption_type=EncryptionType.SYMMETRIC
                    )
                    
                    decrypted_bytes = self.encryption_service.decrypt_data(encrypted_obj)
                    decrypted_data[field] = decrypted_bytes.decode('utf-8')
                else:
                    decrypted_data[field] = value
            
            return decrypted_data
            
        except Exception as e:
            logger.error(f"Data decryption failed: {e}")
            handle_error(
                ErrorCode.DECRYPTION_ERROR,
                f"Failed to decrypt data: {str(e)}",
                ErrorSeverity.HIGH,
                ErrorContext(service_name="data_protection_service")
            )
            raise
    
    def validate_data_access(self, user_id: str, data_category: DataCategory,
                           requested_operation: str) -> Dict[str, Any]:
        """Validate if user can access data for specific operation"""
        try:
            # Check consent
            consent_validation = self.consent_manager.validate_operation_consent(
                user_id, requested_operation
            )
            
            # Check policy requirements
            policy = self._find_applicable_policy(data_category)
            policy_compliant = policy is not None
            
            # Check if data exists and is not expired
            user_data_summary = self.privacy_manager.get_user_data_summary(user_id)
            has_data = user_data_summary.get("total_records", 0) > 0
            
            validation_result = {
                "user_id": user_id,
                "data_category": data_category.value,
                "operation": requested_operation,
                "access_granted": (consent_validation["valid"] and policy_compliant and has_data),
                "consent_status": consent_validation,
                "policy_compliant": policy_compliant,
                "has_data": has_data,
                "validation_timestamp": datetime.now().isoformat()
            }
            
            if not validation_result["access_granted"]:
                logger.warning(f"Data access denied for user {user_id}, operation {requested_operation}")
            
            return validation_result
            
        except Exception as e:
            logger.error(f"Data access validation failed: {e}")
            return {
                "user_id": user_id,
                "access_granted": False,
                "error": str(e)
            }
    
    def export_user_data(self, user_id: str) -> Dict[str, Any]:
        """Export all user data (data portability right)"""
        try:
            # Get consent data
            consent_data = self.consent_manager.export_user_consents(user_id)
            
            # Get privacy data
            privacy_data = self.privacy_manager.get_user_data_summary(user_id)
            
            # Get processing logs for user
            user_logs = [
                {
                    "log_id": log.log_id,
                    "activity": log.activity.value,
                    "data_category": log.data_category.value,
                    "processed_at": log.processed_at.isoformat(),
                    "policy_applied": log.policy_applied,
                    "encryption_used": log.encryption_used,
                    "consent_verified": log.consent_verified
                }
                for log in self.processing_logs
                if log.user_id == user_id
            ]
            
            export_data = {
                "user_id": user_id,
                "export_timestamp": datetime.now().isoformat(),
                "consent_data": consent_data,
                "privacy_data": privacy_data,
                "processing_logs": user_logs,
                "data_protection_policies_applied": [
                    {
                        "policy_id": policy.policy_id,
                        "name": policy.name,
                        "data_categories": [cat.value for cat in policy.data_categories],
                        "classification": policy.classification.value
                    }
                    for policy in self.protection_policies.values()
                ]
            }
            
            logger.info(f"Exported data for user {user_id}")
            return export_data
            
        except Exception as e:
            logger.error(f"Data export failed: {e}")
            return {"error": str(e), "user_id": user_id}
    
    def delete_user_data(self, user_id: str) -> Dict[str, Any]:
        """Delete all user data (right to be forgotten)"""
        try:
            deletion_results = {}
            
            # Delete consent data
            consent_deleted = self.consent_manager.delete_user_consents(user_id)
            deletion_results["consent_data"] = consent_deleted
            
            # Delete privacy data
            privacy_deletion = self.privacy_manager.delete_user_data(user_id)
            deletion_results["privacy_data"] = privacy_deletion
            
            # Remove processing logs
            original_log_count = len(self.processing_logs)
            self.processing_logs = [
                log for log in self.processing_logs
                if log.user_id != user_id
            ]
            deleted_logs = original_log_count - len(self.processing_logs)
            deletion_results["processing_logs"] = {"deleted_count": deleted_logs}
            
            logger.info(f"Deleted all data for user {user_id}")
            
            return {
                "user_id": user_id,
                "deletion_timestamp": datetime.now().isoformat(),
                "deletion_results": deletion_results,
                "status": "completed"
            }
            
        except Exception as e:
            logger.error(f"User data deletion failed: {e}")
            handle_error(
                ErrorCode.DATA_BREACH_DETECTED,
                f"Failed to delete user data: {str(e)}",
                ErrorSeverity.CRITICAL,
                ErrorContext(user_id=user_id, service_name="data_protection_service")
            )
            return {"error": str(e), "user_id": user_id, "status": "failed"}
    
    def audit_data_protection(self) -> Dict[str, Any]:
        """Perform data protection audit"""
        try:
            current_time = datetime.now()
            
            # Audit processing logs
            recent_logs = [
                log for log in self.processing_logs
                if (current_time - log.processed_at).days <= 30
            ]
            
            # Count activities
            activity_counts = {}
            category_counts = {}
            policy_usage = {}
            
            for log in recent_logs:
                activity = log.activity.value
                category = log.data_category.value
                policy = log.policy_applied
                
                activity_counts[activity] = activity_counts.get(activity, 0) + 1
                category_counts[category] = category_counts.get(category, 0) + 1
                policy_usage[policy] = policy_usage.get(policy, 0) + 1
            
            # Check compliance
            compliance_issues = []
            
            # Check for processing without consent
            no_consent_logs = [log for log in recent_logs if not log.consent_verified]
            if no_consent_logs:
                compliance_issues.append(f"{len(no_consent_logs)} processing activities without verified consent")
            
            # Check for unencrypted sensitive data
            unencrypted_sensitive = [
                log for log in recent_logs 
                if log.data_classification in [DataClassification.RESTRICTED, DataClassification.CONFIDENTIAL]
                and not log.encryption_used
            ]
            if unencrypted_sensitive:
                compliance_issues.append(f"{len(unencrypted_sensitive)} sensitive data processed without encryption")
            
            audit_report = {
                "audit_timestamp": current_time.isoformat(),
                "audit_period_days": 30,
                "total_processing_activities": len(recent_logs),
                "activity_breakdown": activity_counts,
                "data_category_breakdown": category_counts,
                "policy_usage": policy_usage,
                "compliance_issues": compliance_issues,
                "total_policies": len(self.protection_policies),
                "active_policies": sum(1 for p in self.protection_policies.values() if p.is_active),
                "encryption_usage_rate": (
                    sum(1 for log in recent_logs if log.encryption_used) / len(recent_logs) * 100
                    if recent_logs else 0
                ),
                "consent_verification_rate": (
                    sum(1 for log in recent_logs if log.consent_verified) / len(recent_logs) * 100
                    if recent_logs else 0
                )
            }
            
            logger.info("Data protection audit completed")
            return audit_report
            
        except Exception as e:
            logger.error(f"Data protection audit failed: {e}")
            return {"error": str(e), "audit_timestamp": datetime.now().isoformat()}
    
    def get_protection_status(self) -> Dict[str, Any]:
        """Get overall data protection status"""
        return {
            "encryption_service": self.encryption_service.get_encryption_status(),
            "privacy_manager": self.privacy_manager.get_privacy_status(),
            "consent_manager": self.consent_manager.get_consent_statistics(),
            "protection_policies": {
                "total": len(self.protection_policies),
                "active": sum(1 for p in self.protection_policies.values() if p.is_active),
                "by_classification": {
                    classification.value: sum(
                        1 for p in self.protection_policies.values() 
                        if p.classification == classification
                    )
                    for classification in DataClassification
                }
            },
            "processing_logs": {
                "total": len(self.processing_logs),
                "recent_24h": len([
                    log for log in self.processing_logs
                    if (datetime.now() - log.processed_at).days < 1
                ])
            }
        }

# Global data protection service instance
data_protection_service = DataProtectionService()

def get_data_protection_service() -> DataProtectionService:
    """Get global data protection service instance"""
    return data_protection_service