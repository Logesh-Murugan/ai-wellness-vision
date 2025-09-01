# privacy.py - Privacy management and data anonymization
import re
import hashlib
import secrets
from typing import Dict, Any, Optional, List, Union, Set
from datetime import datetime, timedelta
from dataclasses import dataclass, field
from enum import Enum

from src.utils.logging_config import get_structured_logger
from src.utils.error_handling import handle_error, ErrorCode, ErrorSeverity, ErrorContext

logger = get_structured_logger(__name__)

class DataCategory(Enum):
    """Categories of personal data"""
    PERSONAL_IDENTIFIER = "personal_identifier"  # Name, email, phone
    HEALTH_DATA = "health_data"                  # Medical information
    BIOMETRIC_DATA = "biometric_data"            # Images, voice recordings
    BEHAVIORAL_DATA = "behavioral_data"          # Usage patterns, preferences
    LOCATION_DATA = "location_data"              # Geographic information
    TECHNICAL_DATA = "technical_data"            # IP addresses, device info

class AnonymizationLevel(Enum):
    """Levels of data anonymization"""
    NONE = "none"                    # No anonymization
    PSEUDONYMIZATION = "pseudonymization"  # Replace with pseudonyms
    GENERALIZATION = "generalization"      # Reduce precision
    SUPPRESSION = "suppression"            # Remove completely
    NOISE_ADDITION = "noise_addition"      # Add statistical noise

@dataclass
class PrivacyRule:
    """Privacy rule for data processing"""
    rule_id: str
    data_category: DataCategory
    anonymization_level: AnonymizationLevel
    retention_days: Optional[int] = None
    conditions: Dict[str, Any] = field(default_factory=dict)
    created_at: datetime = field(default_factory=datetime.now)
    is_active: bool = True

@dataclass
class DataProcessingRecord:
    """Record of data processing activity"""
    record_id: str
    user_id: str
    data_category: DataCategory
    processing_purpose: str
    data_fields: List[str]
    anonymization_applied: AnonymizationLevel
    processed_at: datetime = field(default_factory=datetime.now)
    retention_until: Optional[datetime] = None

class PIIDetector:
    """Detects personally identifiable information in text"""
    
    def __init__(self):
        self.patterns = {
            'email': re.compile(r'\b[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Z|a-z]{2,}\b'),
            'phone': re.compile(r'\b(?:\+?1[-.\s]?)?\(?[0-9]{3}\)?[-.\s]?[0-9]{3}[-.\s]?[0-9]{4}\b'),
            'ssn': re.compile(r'\b\d{3}-?\d{2}-?\d{4}\b'),
            'credit_card': re.compile(r'\b(?:\d{4}[-\s]?){3}\d{4}\b'),
            'ip_address': re.compile(r'\b(?:[0-9]{1,3}\.){3}[0-9]{1,3}\b'),
            'name': re.compile(r'\b[A-Z][a-z]+ [A-Z][a-z]+\b'),  # Simple name pattern
        }
    
    def detect_pii(self, text: str) -> Dict[str, List[str]]:
        """Detect PII in text"""
        detected_pii = {}
        
        for pii_type, pattern in self.patterns.items():
            matches = pattern.findall(text)
            if matches:
                detected_pii[pii_type] = matches
        
        return detected_pii
    
    def has_pii(self, text: str) -> bool:
        """Check if text contains any PII"""
        return bool(self.detect_pii(text))

class DataAnonymizer:
    """Anonymizes personal data according to privacy rules"""
    
    def __init__(self):
        self.pii_detector = PIIDetector()
        self.pseudonym_cache = {}  # Cache for consistent pseudonyms
    
    def anonymize_text(self, text: str, anonymization_level: AnonymizationLevel,
                      preserve_format: bool = True) -> str:
        """Anonymize text data"""
        try:
            if anonymization_level == AnonymizationLevel.NONE:
                return text
            
            elif anonymization_level == AnonymizationLevel.SUPPRESSION:
                return "[REDACTED]"
            
            elif anonymization_level == AnonymizationLevel.PSEUDONYMIZATION:
                return self._pseudonymize_text(text, preserve_format)
            
            elif anonymization_level == AnonymizationLevel.GENERALIZATION:
                return self._generalize_text(text)
            
            elif anonymization_level == AnonymizationLevel.NOISE_ADDITION:
                return self._add_noise_to_text(text)
            
            else:
                logger.warning(f"Unknown anonymization level: {anonymization_level}")
                return text
                
        except Exception as e:
            logger.error(f"Text anonymization failed: {e}")
            return "[ANONYMIZATION_ERROR]"
    
    def _pseudonymize_text(self, text: str, preserve_format: bool) -> str:
        """Replace PII with consistent pseudonyms"""
        anonymized_text = text
        detected_pii = self.pii_detector.detect_pii(text)
        
        for pii_type, matches in detected_pii.items():
            for match in matches:
                pseudonym = self._get_pseudonym(match, pii_type, preserve_format)
                anonymized_text = anonymized_text.replace(match, pseudonym)
        
        return anonymized_text
    
    def _get_pseudonym(self, original: str, pii_type: str, preserve_format: bool) -> str:
        """Get consistent pseudonym for original value"""
        cache_key = f"{pii_type}:{original}"
        
        if cache_key in self.pseudonym_cache:
            return self.pseudonym_cache[cache_key]
        
        # Generate pseudonym based on type
        if pii_type == 'email':
            pseudonym = f"user{abs(hash(original)) % 10000}@example.com"
        elif pii_type == 'phone':
            pseudonym = f"555-{abs(hash(original)) % 1000:03d}-{abs(hash(original)) % 10000:04d}"
        elif pii_type == 'name':
            pseudonym = f"Person{abs(hash(original)) % 1000}"
        elif pii_type == 'ip_address':
            pseudonym = f"192.168.{abs(hash(original)) % 256}.{abs(hash(original)) % 256}"
        else:
            # Generic pseudonym
            pseudonym = f"[{pii_type.upper()}_{abs(hash(original)) % 10000}]"
        
        self.pseudonym_cache[cache_key] = pseudonym
        return pseudonym
    
    def _generalize_text(self, text: str) -> str:
        """Generalize text by reducing precision"""
        # Simple generalization - replace specific numbers with ranges
        import re
        
        # Replace specific ages with age ranges
        text = re.sub(r'\b(\d{1,2})\s*years?\s*old\b', 
                     lambda m: f"{(int(m.group(1)) // 10) * 10}-{(int(m.group(1)) // 10) * 10 + 9} years old", 
                     text)
        
        # Replace specific dates with months/years
        text = re.sub(r'\b\d{1,2}/\d{1,2}/(\d{4})\b', r'[DATE_\1]', text)
        
        return text
    
    def _add_noise_to_text(self, text: str) -> str:
        """Add noise to text data"""
        # Simple noise addition - randomly replace some characters
        import random
        
        if len(text) < 10:
            return text
        
        text_list = list(text)
        num_changes = max(1, len(text) // 20)  # Change ~5% of characters
        
        for _ in range(num_changes):
            pos = random.randint(0, len(text_list) - 1)
            if text_list[pos].isalpha():
                text_list[pos] = random.choice('abcdefghijklmnopqrstuvwxyz')
        
        return ''.join(text_list)
    
    def anonymize_structured_data(self, data: Dict[str, Any], 
                                 field_rules: Dict[str, AnonymizationLevel]) -> Dict[str, Any]:
        """Anonymize structured data according to field rules"""
        try:
            anonymized_data = {}
            
            for field, value in data.items():
                anonymization_level = field_rules.get(field, AnonymizationLevel.NONE)
                
                if anonymization_level == AnonymizationLevel.SUPPRESSION:
                    # Skip suppressed fields
                    continue
                elif anonymization_level == AnonymizationLevel.NONE:
                    anonymized_data[field] = value
                else:
                    if isinstance(value, str):
                        anonymized_data[field] = self.anonymize_text(value, anonymization_level)
                    elif isinstance(value, (int, float)):
                        anonymized_data[field] = self._anonymize_numeric(value, anonymization_level)
                    elif isinstance(value, dict):
                        anonymized_data[field] = self.anonymize_structured_data(value, field_rules)
                    elif isinstance(value, list):
                        anonymized_data[field] = [
                            self.anonymize_text(str(item), anonymization_level) if isinstance(item, str)
                            else item for item in value
                        ]
                    else:
                        anonymized_data[field] = value
            
            return anonymized_data
            
        except Exception as e:
            logger.error(f"Structured data anonymization failed: {e}")
            return {"error": "anonymization_failed"}
    
    def _anonymize_numeric(self, value: Union[int, float], 
                          anonymization_level: AnonymizationLevel) -> Union[int, float]:
        """Anonymize numeric data"""
        if anonymization_level == AnonymizationLevel.GENERALIZATION:
            # Round to nearest 10 for integers, 0.1 for floats
            if isinstance(value, int):
                return (value // 10) * 10
            else:
                return round(value, 1)
        elif anonymization_level == AnonymizationLevel.NOISE_ADDITION:
            # Add small random noise
            import random
            noise_factor = 0.05  # 5% noise
            noise = random.uniform(-noise_factor, noise_factor) * value
            return value + noise
        else:
            return value
    
    def anonymize_health_data(self, data: Dict[str, Any], 
                             preserve_medical_accuracy: bool = True) -> Dict[str, Any]:
        """Specialized anonymization for health data"""
        try:
            anonymized_data = {}
            
            # Define health-specific anonymization rules
            health_field_rules = {
                # Personal identifiers - pseudonymize
                'patient_name': AnonymizationLevel.PSEUDONYMIZATION,
                'name': AnonymizationLevel.PSEUDONYMIZATION,
                'email': AnonymizationLevel.PSEUDONYMIZATION,
                'phone': AnonymizationLevel.PSEUDONYMIZATION,
                'address': AnonymizationLevel.PSEUDONYMIZATION,
                
                # Age - generalize to ranges
                'age': AnonymizationLevel.GENERALIZATION,
                'birth_date': AnonymizationLevel.GENERALIZATION,
                'dob': AnonymizationLevel.GENERALIZATION,
                
                # Medical data - preserve if medically relevant
                'diagnosis': AnonymizationLevel.NONE if preserve_medical_accuracy else AnonymizationLevel.GENERALIZATION,
                'symptoms': AnonymizationLevel.NONE if preserve_medical_accuracy else AnonymizationLevel.GENERALIZATION,
                'condition': AnonymizationLevel.NONE if preserve_medical_accuracy else AnonymizationLevel.GENERALIZATION,
                'medication': AnonymizationLevel.NONE if preserve_medical_accuracy else AnonymizationLevel.GENERALIZATION,
                
                # Measurements - add noise to preserve privacy while maintaining utility
                'weight': AnonymizationLevel.NOISE_ADDITION,
                'height': AnonymizationLevel.NOISE_ADDITION,
                'blood_pressure': AnonymizationLevel.NOISE_ADDITION,
                'heart_rate': AnonymizationLevel.NOISE_ADDITION,
                'temperature': AnonymizationLevel.NOISE_ADDITION,
                
                # Location data - generalize
                'location': AnonymizationLevel.GENERALIZATION,
                'zip_code': AnonymizationLevel.GENERALIZATION,
                'city': AnonymizationLevel.GENERALIZATION,
                
                # Timestamps - generalize to date only
                'timestamp': AnonymizationLevel.GENERALIZATION,
                'created_at': AnonymizationLevel.GENERALIZATION,
                'updated_at': AnonymizationLevel.GENERALIZATION
            }
            
            for field, value in data.items():
                field_lower = field.lower()
                
                # Find matching rule
                anonymization_level = AnonymizationLevel.NONE
                for pattern, level in health_field_rules.items():
                    if pattern in field_lower:
                        anonymization_level = level
                        break
                
                # Apply anonymization
                if anonymization_level == AnonymizationLevel.NONE:
                    anonymized_data[field] = value
                elif anonymization_level == AnonymizationLevel.SUPPRESSION:
                    # Skip suppressed fields
                    continue
                else:
                    if isinstance(value, str):
                        anonymized_data[field] = self.anonymize_text(value, anonymization_level)
                    elif isinstance(value, (int, float)):
                        anonymized_data[field] = self._anonymize_numeric(value, anonymization_level)
                    elif isinstance(value, datetime):
                        anonymized_data[field] = self._anonymize_datetime(value, anonymization_level)
                    else:
                        anonymized_data[field] = value
            
            return anonymized_data
            
        except Exception as e:
            logger.error(f"Health data anonymization failed: {e}")
            return {"error": "health_anonymization_failed"}
    
    def _anonymize_datetime(self, dt: datetime, 
                           anonymization_level: AnonymizationLevel) -> Union[str, datetime]:
        """Anonymize datetime values"""
        if anonymization_level == AnonymizationLevel.GENERALIZATION:
            # Return only date, not time
            return dt.date().isoformat()
        elif anonymization_level == AnonymizationLevel.NOISE_ADDITION:
            # Add random hours/minutes
            import random
            noise_hours = random.randint(-12, 12)
            noise_minutes = random.randint(-30, 30)
            return dt + timedelta(hours=noise_hours, minutes=noise_minutes)
        else:
            return dt

class DataRetentionManager:
    """Manages data retention and deletion"""
    
    def __init__(self):
        self.retention_rules = {}
        self.deletion_queue = []
    
    def set_retention_rule(self, data_category: DataCategory, retention_days: int):
        """Set retention rule for data category"""
        self.retention_rules[data_category] = retention_days
        logger.info(f"Set retention rule: {data_category.value} -> {retention_days} days")
    
    def calculate_deletion_date(self, data_category: DataCategory, 
                               created_at: datetime) -> Optional[datetime]:
        """Calculate when data should be deleted"""
        retention_days = self.retention_rules.get(data_category)
        if retention_days is None:
            return None
        
        return created_at + timedelta(days=retention_days)
    
    def schedule_deletion(self, record_id: str, user_id: str, 
                         data_category: DataCategory, deletion_date: datetime):
        """Schedule data for deletion"""
        self.deletion_queue.append({
            'record_id': record_id,
            'user_id': user_id,
            'data_category': data_category,
            'deletion_date': deletion_date
        })
    
    def get_expired_data(self) -> List[Dict[str, Any]]:
        """Get data that should be deleted"""
        current_time = datetime.now()
        expired_data = [
            item for item in self.deletion_queue
            if item['deletion_date'] <= current_time
        ]
        return expired_data
    
    def mark_as_deleted(self, record_id: str):
        """Mark data as deleted"""
        self.deletion_queue = [
            item for item in self.deletion_queue
            if item['record_id'] != record_id
        ]

class PrivacyManager:
    """Main privacy management service"""
    
    def __init__(self):
        self.privacy_rules = {}
        self.processing_records = {}
        self.data_anonymizer = DataAnonymizer()
        self.retention_manager = DataRetentionManager()
        self.pii_detector = PIIDetector()
        
        # Initialize default privacy rules
        self._initialize_default_rules()
    
    def _initialize_default_rules(self):
        """Initialize default privacy rules"""
        default_rules = [
            PrivacyRule(
                rule_id="health_data_pseudonymization",
                data_category=DataCategory.HEALTH_DATA,
                anonymization_level=AnonymizationLevel.PSEUDONYMIZATION,
                retention_days=2555  # 7 years for health data
            ),
            PrivacyRule(
                rule_id="personal_id_suppression",
                data_category=DataCategory.PERSONAL_IDENTIFIER,
                anonymization_level=AnonymizationLevel.PSEUDONYMIZATION,
                retention_days=365
            ),
            PrivacyRule(
                rule_id="biometric_data_encryption",
                data_category=DataCategory.BIOMETRIC_DATA,
                anonymization_level=AnonymizationLevel.PSEUDONYMIZATION,
                retention_days=1095  # 3 years
            ),
            PrivacyRule(
                rule_id="behavioral_generalization",
                data_category=DataCategory.BEHAVIORAL_DATA,
                anonymization_level=AnonymizationLevel.GENERALIZATION,
                retention_days=730  # 2 years
            )
        ]
        
        for rule in default_rules:
            self.privacy_rules[rule.rule_id] = rule
            self.retention_manager.set_retention_rule(rule.data_category, rule.retention_days)
        
        logger.info("Default privacy rules initialized")
    
    def add_privacy_rule(self, rule: PrivacyRule):
        """Add a new privacy rule"""
        self.privacy_rules[rule.rule_id] = rule
        if rule.retention_days:
            self.retention_manager.set_retention_rule(rule.data_category, rule.retention_days)
        
        logger.info(f"Added privacy rule: {rule.rule_id}")
    
    def process_data(self, user_id: str, data: Dict[str, Any], 
                    data_category: DataCategory, processing_purpose: str) -> Dict[str, Any]:
        """Process data according to privacy rules"""
        try:
            # Find applicable privacy rule
            applicable_rule = self._find_applicable_rule(data_category)
            
            if not applicable_rule:
                logger.warning(f"No privacy rule found for category: {data_category}")
                return data
            
            # Apply anonymization
            field_rules = self._determine_field_rules(data, applicable_rule)
            anonymized_data = self.data_anonymizer.anonymize_structured_data(data, field_rules)
            
            # Record processing activity
            record_id = f"{user_id}_{int(datetime.now().timestamp())}"
            processing_record = DataProcessingRecord(
                record_id=record_id,
                user_id=user_id,
                data_category=data_category,
                processing_purpose=processing_purpose,
                data_fields=list(data.keys()),
                anonymization_applied=applicable_rule.anonymization_level
            )
            
            # Set retention period
            if applicable_rule.retention_days:
                processing_record.retention_until = self.retention_manager.calculate_deletion_date(
                    data_category, processing_record.processed_at
                )
                self.retention_manager.schedule_deletion(
                    record_id, user_id, data_category, processing_record.retention_until
                )
            
            self.processing_records[record_id] = processing_record
            
            logger.info(f"Processed data for user {user_id} with rule {applicable_rule.rule_id}")
            return anonymized_data
            
        except Exception as e:
            logger.error(f"Data processing failed: {e}")
            handle_error(
                ErrorCode.PRIVACY_VIOLATION,
                f"Failed to process data according to privacy rules: {str(e)}",
                ErrorSeverity.HIGH,
                ErrorContext(user_id=user_id, service_name="privacy_manager")
            )
            raise
    
    def _find_applicable_rule(self, data_category: DataCategory) -> Optional[PrivacyRule]:
        """Find applicable privacy rule for data category"""
        for rule in self.privacy_rules.values():
            if rule.data_category == data_category and rule.is_active:
                return rule
        return None
    
    def _determine_field_rules(self, data: Dict[str, Any], 
                              privacy_rule: PrivacyRule) -> Dict[str, AnonymizationLevel]:
        """Determine anonymization level for each field"""
        field_rules = {}
        
        for field, value in data.items():
            # Check if field contains PII
            if isinstance(value, str) and self.pii_detector.has_pii(value):
                field_rules[field] = privacy_rule.anonymization_level
            else:
                # Apply rule based on field name patterns
                field_lower = field.lower()
                if any(keyword in field_lower for keyword in ['name', 'email', 'phone', 'id']):
                    field_rules[field] = AnonymizationLevel.PSEUDONYMIZATION
                elif any(keyword in field_lower for keyword in ['age', 'date', 'time']):
                    field_rules[field] = AnonymizationLevel.GENERALIZATION
                else:
                    field_rules[field] = AnonymizationLevel.NONE
        
        return field_rules
    
    def anonymize_text(self, text: str, data_category: DataCategory) -> str:
        """Anonymize text according to category rules"""
        applicable_rule = self._find_applicable_rule(data_category)
        if not applicable_rule:
            return text
        
        return self.data_anonymizer.anonymize_text(text, applicable_rule.anonymization_level)
    
    def detect_pii_in_text(self, text: str) -> Dict[str, List[str]]:
        """Detect PII in text"""
        return self.pii_detector.detect_pii(text)
    
    def get_user_data_summary(self, user_id: str) -> Dict[str, Any]:
        """Get summary of user's data processing"""
        user_records = [
            record for record in self.processing_records.values()
            if record.user_id == user_id
        ]
        
        if not user_records:
            return {"user_id": user_id, "total_records": 0}
        
        # Group by data category
        by_category = {}
        for record in user_records:
            category = record.data_category.value
            if category not in by_category:
                by_category[category] = []
            by_category[category].append(record)
        
        return {
            "user_id": user_id,
            "total_records": len(user_records),
            "by_category": {
                category: {
                    "count": len(records),
                    "latest_processing": max(r.processed_at for r in records).isoformat(),
                    "retention_until": records[0].retention_until.isoformat() if records[0].retention_until else None
                }
                for category, records in by_category.items()
            },
            "scheduled_deletions": len([
                item for item in self.retention_manager.deletion_queue
                if item['user_id'] == user_id
            ])
        }
    
    def delete_user_data(self, user_id: str) -> Dict[str, Any]:
        """Delete all data for a user (right to be forgotten)"""
        try:
            # Find all user records
            user_records = [
                record_id for record_id, record in self.processing_records.items()
                if record.user_id == user_id
            ]
            
            # Remove processing records
            for record_id in user_records:
                del self.processing_records[record_id]
            
            # Remove from deletion queue
            self.retention_manager.deletion_queue = [
                item for item in self.retention_manager.deletion_queue
                if item['user_id'] != user_id
            ]
            
            # Clear pseudonym cache for user
            user_cache_keys = [
                key for key in self.data_anonymizer.pseudonym_cache.keys()
                if user_id in key
            ]
            for key in user_cache_keys:
                del self.data_anonymizer.pseudonym_cache[key]
            
            logger.info(f"Deleted all data for user: {user_id}")
            
            return {
                "user_id": user_id,
                "deleted_records": len(user_records),
                "deletion_completed_at": datetime.now().isoformat(),
                "status": "success"
            }
            
        except Exception as e:
            logger.error(f"User data deletion failed: {e}")
            handle_error(
                ErrorCode.DATA_BREACH_DETECTED,
                f"Failed to delete user data: {str(e)}",
                ErrorSeverity.CRITICAL,
                ErrorContext(user_id=user_id, service_name="privacy_manager")
            )
            raise
    
    def cleanup_expired_data(self) -> Dict[str, Any]:
        """Clean up expired data according to retention rules"""
        try:
            expired_data = self.retention_manager.get_expired_data()
            deleted_count = 0
            
            for item in expired_data:
                record_id = item['record_id']
                if record_id in self.processing_records:
                    del self.processing_records[record_id]
                    deleted_count += 1
                
                self.retention_manager.mark_as_deleted(record_id)
            
            logger.info(f"Cleaned up {deleted_count} expired data records")
            
            return {
                "deleted_records": deleted_count,
                "cleanup_completed_at": datetime.now().isoformat(),
                "remaining_scheduled_deletions": len(self.retention_manager.deletion_queue)
            }
            
        except Exception as e:
            logger.error(f"Data cleanup failed: {e}")
            return {"error": str(e), "deleted_records": 0}
    
    def get_privacy_status(self) -> Dict[str, Any]:
        """Get privacy management status"""
        return {
            "total_privacy_rules": len(self.privacy_rules),
            "active_rules": sum(1 for rule in self.privacy_rules.values() if rule.is_active),
            "total_processing_records": len(self.processing_records),
            "scheduled_deletions": len(self.retention_manager.deletion_queue),
            "data_categories_covered": list(set(rule.data_category.value for rule in self.privacy_rules.values())),
            "anonymization_levels_used": list(set(rule.anonymization_level.value for rule in self.privacy_rules.values())),
            "pseudonym_cache_size": len(self.data_anonymizer.pseudonym_cache)
        }

# Global privacy manager instance
privacy_manager = PrivacyManager()

def get_privacy_manager() -> PrivacyManager:
    """Get global privacy manager instance"""
    return privacy_manager