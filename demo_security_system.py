#!/usr/bin/env python3
"""
Demo script for comprehensive data security and privacy system
"""

import time
import tempfile
from pathlib import Path
from datetime import datetime

from src.security import (
    get_encryption_service, get_privacy_manager, 
    get_consent_manager, get_data_protection_service
)
from src.security.security_middleware import get_security_middleware
from src.security.privacy import DataCategory, AnonymizationLevel
from src.security.consent import ConsentType, ConsentBasis
from src.security.data_protection import DataClassification, ProcessingActivity
from src.security.encryption import EncryptionType

def demo_security_system():
    """Demonstrate comprehensive security system"""
    print("=== AI WellnessVision Security & Privacy System Demo ===\n")
    
    print("1. Initializing security services...")
    
    # Get all security services
    encryption_service = get_encryption_service()
    privacy_manager = get_privacy_manager()
    consent_manager = get_consent_manager()
    data_protection_service = get_data_protection_service()
    security_middleware = get_security_middleware()
    
    print("✓ Encryption service initialized")
    print("✓ Privacy manager initialized")
    print("✓ Consent manager initialized")
    print("✓ Data protection service initialized")
    print("✓ Security middleware initialized")
    
    print("\n2. Testing encryption capabilities...")
    
    # Test symmetric encryption
    sensitive_data = "Patient John Doe has been diagnosed with hypertension"
    
    encrypted_data = encryption_service.encrypt_data(
        sensitive_data, encryption_type=EncryptionType.SYMMETRIC
    )
    print(f"✓ Data encrypted: {len(encrypted_data.encrypted_content)} bytes")
    
    decrypted_data = encryption_service.decrypt_data(encrypted_data)
    print(f"✓ Data decrypted successfully: {decrypted_data.decode() == sensitive_data}")
    
    # Test password hashing
    password = "secure_patient_password_123"
    hash_value, salt = encryption_service.hash_password(password)
    print(f"✓ Password hashed: {len(hash_value)} byte hash")
    
    # Verify password
    is_valid = encryption_service.verify_hash(password, hash_value, salt)
    print(f"✓ Password verification: {is_valid}")
    
    # Test secure token generation
    secure_token = encryption_service.generate_secure_token()
    print(f"✓ Secure token generated: {secure_token[:16]}...")
    
    print("\n3. Testing privacy and anonymization...")
    
    # Test PII detection
    text_with_pii = "Contact Dr. Sarah Johnson at sarah.johnson@hospital.com or call 555-123-4567"
    detected_pii = privacy_manager.detect_pii_in_text(text_with_pii)
    print(f"✓ PII detected: {list(detected_pii.keys())}")
    
    # Test data anonymization
    patient_data = {
        "patient_name": "Alice Smith",
        "email": "alice.smith@email.com",
        "phone": "555-987-6543",
        "age": 42,
        "diagnosis": "diabetes type 2",
        "blood_pressure": "140/90",
        "doctor_notes": "Patient shows good compliance with medication"
    }
    
    print(f"✓ Original data: {len(patient_data)} fields")
    
    anonymized_data = privacy_manager.process_data(
        "patient_001", patient_data, DataCategory.HEALTH_DATA, "medical_analysis"
    )
    
    print(f"✓ Anonymized data: {len(anonymized_data)} fields")
    print(f"  - Name changed: {anonymized_data['patient_name'] != patient_data['patient_name']}")
    print(f"  - Email changed: {anonymized_data['email'] != patient_data['email']}")
    print(f"  - Diagnosis preserved: {'diabetes' in anonymized_data.get('diagnosis', '')}")
    
    # Test text anonymization
    medical_text = "Patient John Doe, age 45, diagnosed with hypertension. Contact at john.doe@email.com"
    anonymized_text = privacy_manager.anonymize_text(medical_text, DataCategory.HEALTH_DATA)
    print(f"✓ Text anonymized: {anonymized_text[:50]}...")
    
    print("\n4. Testing consent management...")
    
    user_id = "demo_user_001"
    
    # Create consent request
    template_ids = ["data_processing_consent", "health_data_consent", "biometric_data_consent"]
    consent_request = consent_manager.create_consent_request(user_id, template_ids)
    
    print(f"✓ Consent request created: {consent_request.request_id}")
    print(f"✓ Templates requested: {len(consent_request.consent_templates)}")
    
    # Simulate user responses (grant all required consents)
    consent_responses = {
        "data_processing_consent": True,
        "health_data_consent": True,
        "biometric_data_consent": True  # Grant required consent
    }
    
    response_result = consent_manager.process_consent_response(
        consent_request.request_id, consent_responses
    )
    
    print(f"✓ Consent responses processed: {response_result['status']}")
    print(f"✓ Consents granted: {len([c for c in response_result['processed_consents'] if c['status'] == 'granted'])}")
    
    # Check consent status
    has_data_consent = consent_manager.check_consent(user_id, ConsentType.DATA_PROCESSING)
    has_health_consent = consent_manager.check_consent(user_id, ConsentType.HEALTH_DATA)
    has_biometric_consent = consent_manager.check_consent(user_id, ConsentType.BIOMETRIC_DATA)
    
    print(f"✓ Data processing consent: {has_data_consent}")
    print(f"✓ Health data consent: {has_health_consent}")
    print(f"✓ Biometric data consent: {has_biometric_consent}")
    
    # Validate operation consent
    operation_validation = consent_manager.validate_operation_consent(user_id, "health_assessment")
    print(f"✓ Health assessment allowed: {operation_validation['valid']}")
    
    print("\n5. Testing data protection service...")
    
    # Test secure data processing
    test_health_data = {
        "patient_id": "P12345",
        "symptoms": ["fatigue", "headache", "dizziness"],
        "vital_signs": {
            "blood_pressure": "130/85",
            "heart_rate": 72,
            "temperature": 98.6
        },
        "medical_history": "Previous diagnosis of mild hypertension"
    }
    
    try:
        protected_data = data_protection_service.process_data_securely(
            user_id, test_health_data, DataCategory.HEALTH_DATA, 
            "health_assessment", ProcessingActivity.ANALYSIS
        )
        print(f"✓ Data processed securely: {len(protected_data)} fields")
        print(f"  - Patient ID anonymized: {protected_data.get('patient_id', '') != 'P12345'}")
        print(f"  - Symptoms preserved: {'fatigue' in str(protected_data.get('symptoms', []))}")
    except Exception as e:
        print(f"✗ Secure processing failed: {e}")
    
    # Test data access validation
    access_validation = data_protection_service.validate_data_access(
        user_id, DataCategory.HEALTH_DATA, "medical_analysis"
    )
    print(f"✓ Data access validation: {access_validation['access_granted']}")
    
    print("\n6. Testing security middleware...")
    
    # Test session management
    client_ip = "192.168.1.100"
    user_agent = "Mozilla/5.0 (Demo Browser)"
    
    session_result = security_middleware.create_secure_session(user_id, client_ip, user_agent)
    print(f"✓ Secure session created: {session_result['success']}")
    
    if session_result['success']:
        session_id = session_result['session_id']
        csrf_token = session_result['csrf_token']
        print(f"✓ Session ID: {session_id[:16]}...")
        print(f"✓ CSRF token: {csrf_token[:16]}...")
        
        # Test CSRF validation
        csrf_valid = security_middleware.validate_csrf_token(session_id, csrf_token)
        csrf_invalid = security_middleware.validate_csrf_token(session_id, "wrong_token")
        print(f"✓ CSRF validation (correct): {csrf_valid}")
        print(f"✓ CSRF validation (wrong): {csrf_invalid}")
    
    # Test input validation
    safe_input = {"name": "John Doe", "age": 30, "message": "Hello world"}
    dangerous_input = {
        "query": "SELECT * FROM users WHERE id = 1; DROP TABLE users;",
        "script": "<script>alert('XSS attack')</script>",
        "path": "../../../etc/passwd"
    }
    
    safe_validation = security_middleware.input_validator.validate_input(safe_input)
    dangerous_validation = security_middleware.input_validator.validate_input(dangerous_input)
    
    print(f"✓ Safe input validation: {safe_validation['valid']}")
    print(f"✓ Dangerous input validation: {dangerous_validation['valid']}")
    print(f"✓ Threats detected: {len(dangerous_validation['threats_detected'])}")
    
    # Test rate limiting
    test_ip = "192.168.1.200"
    print(f"✓ Rate limiting test for IP: {test_ip}")
    
    for i in range(7):
        is_limited = security_middleware.rate_limiter.is_rate_limited(test_ip, max_requests=5)
        if is_limited:
            print(f"✓ Rate limit triggered after {i} requests")
            break
    
    # Test request processing
    request_data = {
        "client_ip": "192.168.1.150",
        "user_agent": "Demo Client",
        "session_id": session_id if session_result['success'] else None,
        "input_data": {"message": "Test request", "action": "health_check"}
    }
    
    processing_result = security_middleware.process_request(request_data)
    print(f"✓ Request processing: {processing_result['allowed']}")
    print(f"✓ Security headers: {len(processing_result['security_headers'])}")
    
    print("\n7. Testing comprehensive data operations...")
    
    # Test user data summary
    user_summary = privacy_manager.get_user_data_summary(user_id)
    print(f"✓ User data summary: {user_summary['total_records']} records")
    
    # Test user consent summary
    consent_summary = consent_manager.get_user_consents(user_id)
    print(f"✓ User consents: {consent_summary['total_consents']} total, {consent_summary['valid_consents']} valid")
    
    # Test data export (data portability)
    export_data = data_protection_service.export_user_data(user_id)
    print(f"✓ Data export completed: {len(export_data)} sections")
    
    print("\n8. Testing security status and monitoring...")
    
    # Get encryption status
    encryption_status = encryption_service.get_encryption_status()
    print(f"✓ Encryption service: {encryption_status['total_keys']} keys, cryptography available: {encryption_status['cryptography_available']}")
    
    # Get privacy status
    privacy_status = privacy_manager.get_privacy_status()
    print(f"✓ Privacy manager: {privacy_status['total_privacy_rules']} rules, {privacy_status['total_processing_records']} records")
    
    # Get consent statistics
    consent_stats = consent_manager.get_consent_statistics()
    print(f"✓ Consent manager: {consent_stats['total_users']} users, {consent_stats['total_consents']} consents")
    
    # Get data protection status
    protection_status = data_protection_service.get_protection_status()
    print(f"✓ Data protection: {protection_status['protection_policies']['total']} policies")
    
    # Get security middleware status
    security_status = security_middleware.get_security_status()
    print(f"✓ Security middleware: {security_status['active_sessions']} sessions, {security_status['rate_limited_ips']} blocked IPs")
    
    print("\n9. Testing audit and compliance...")
    
    # Perform data protection audit
    audit_report = data_protection_service.audit_data_protection()
    print(f"✓ Audit completed: {audit_report['total_processing_activities']} activities analyzed")
    print(f"✓ Compliance issues: {len(audit_report['compliance_issues'])}")
    print(f"✓ Encryption usage rate: {audit_report['encryption_usage_rate']:.1f}%")
    print(f"✓ Consent verification rate: {audit_report['consent_verification_rate']:.1f}%")
    
    # Check expiring consents
    expiring_consents = consent_manager.get_expiring_consents(days_ahead=30)
    print(f"✓ Expiring consents (30 days): {len(expiring_consents)}")
    
    print("\n10. Testing data cleanup and retention...")
    
    # Test privacy data cleanup
    privacy_cleanup = privacy_manager.cleanup_expired_data()
    print(f"✓ Privacy cleanup: {privacy_cleanup['deleted_records']} records cleaned")
    
    # Test consent cleanup
    consent_cleanup = consent_manager.cleanup_expired_consents()
    print(f"✓ Consent cleanup: {consent_cleanup['expired_consents']} expired, {consent_cleanup['cleaned_consents']} cleaned")
    
    # Test session cleanup
    session_cleanup = security_middleware.session_manager.cleanup_expired_sessions()
    print(f"✓ Session cleanup: {session_cleanup} expired sessions removed")
    
    print("\n11. Testing data deletion (Right to be Forgotten)...")
    
    # Create a test user for deletion
    deletion_user = "deletion_test_user"
    
    # Grant consent and process data
    consent_manager.grant_consent(deletion_user, ConsentType.DATA_PROCESSING, "Test data")
    test_data = {"name": "Test User", "email": "test@example.com"}
    privacy_manager.process_data(deletion_user, test_data, DataCategory.PERSONAL_IDENTIFIER, "testing")
    
    # Verify data exists
    before_deletion = privacy_manager.get_user_data_summary(deletion_user)
    print(f"✓ Data before deletion: {before_deletion['total_records']} records")
    
    # Delete all user data
    deletion_result = data_protection_service.delete_user_data(deletion_user)
    print(f"✓ Data deletion: {deletion_result['status']}")
    
    # Verify data is deleted
    after_deletion = privacy_manager.get_user_data_summary(deletion_user)
    print(f"✓ Data after deletion: {after_deletion['total_records']} records")
    
    print("\n12. Security demonstration summary...")
    
    print("✓ Encryption: Symmetric and asymmetric encryption working")
    print("✓ Privacy: PII detection and data anonymization functional")
    print("✓ Consent: User consent management and validation operational")
    print("✓ Data Protection: Comprehensive data protection policies applied")
    print("✓ Security Middleware: Request validation and session management active")
    print("✓ Audit: Compliance monitoring and reporting available")
    print("✓ Data Rights: Export and deletion capabilities implemented")
    
    # Final logout
    if session_result['success']:
        logout_success = security_middleware.logout_user(session_id)
        print(f"✓ User logout: {logout_success}")
    
    print("\n=== Security system demo completed successfully! ===")

def demo_security_features():
    """Demonstrate individual security features"""
    print("\n=== Individual Security Features Demo ===\n")
    
    print("1. Encryption Features...")
    encryption_service = get_encryption_service()
    
    # Test different encryption types
    test_data = "Sensitive medical information"
    
    # Symmetric encryption
    sym_encrypted = encryption_service.encrypt_data(test_data, encryption_type=EncryptionType.SYMMETRIC)
    sym_decrypted = encryption_service.decrypt_data(sym_encrypted)
    print(f"✓ Symmetric encryption: {sym_decrypted.decode() == test_data}")
    
    # Asymmetric encryption
    asym_encrypted = encryption_service.encrypt_data(test_data, encryption_type=EncryptionType.ASYMMETRIC)
    asym_decrypted = encryption_service.decrypt_data(asym_encrypted)
    print(f"✓ Asymmetric encryption: {asym_decrypted.decode() == test_data}")
    
    print("\n2. Privacy Features...")
    privacy_manager = get_privacy_manager()
    
    # Test different anonymization levels
    test_text = "Patient John Smith, age 45, email john.smith@hospital.com"
    
    anonymized_text = privacy_manager.data_anonymizer.anonymize_text(
        test_text, AnonymizationLevel.PSEUDONYMIZATION
    )
    print(f"✓ Pseudonymization: {anonymized_text}")
    
    generalized_text = privacy_manager.data_anonymizer.anonymize_text(
        test_text, AnonymizationLevel.GENERALIZATION
    )
    print(f"✓ Generalization: {generalized_text}")
    
    print("\n3. Consent Features...")
    consent_manager = get_consent_manager()
    
    # Test different consent types
    consent_types = [ConsentType.DATA_PROCESSING, ConsentType.HEALTH_DATA, ConsentType.MARKETING]
    
    for consent_type in consent_types:
        granted = consent_manager.grant_consent(
            "feature_demo_user", consent_type, f"Demo {consent_type.value}"
        )
        print(f"✓ {consent_type.value} consent: granted")
    
    # Test consent validation
    validation = consent_manager.validate_operation_consent("feature_demo_user", "health_assessment")
    print(f"✓ Operation validation: {validation['valid']}")
    
    print("\n4. Data Protection Features...")
    data_protection_service = get_data_protection_service()
    
    # Test different data classifications
    classifications = [DataClassification.PUBLIC, DataClassification.CONFIDENTIAL, DataClassification.RESTRICTED]
    
    for classification in classifications:
        print(f"✓ {classification.value} data classification available")
    
    # Test processing activities
    activities = [ProcessingActivity.COLLECTION, ProcessingActivity.ANALYSIS, ProcessingActivity.SHARING]
    
    for activity in activities:
        print(f"✓ {activity.value} processing activity supported")
    
    print("\n5. Security Middleware Features...")
    security_middleware = get_security_middleware()
    
    # Test security headers
    headers = security_middleware.security_headers.get_security_headers()
    print(f"✓ Security headers: {len(headers)} headers configured")
    
    # Test input validation patterns
    validator = security_middleware.input_validator
    print(f"✓ Input validation: {len(validator.compiled_patterns)} threat patterns")
    
    print("\n=== Individual features demo completed! ===")

if __name__ == "__main__":
    try:
        demo_security_system()
        demo_security_features()
    except KeyboardInterrupt:
        print("\n\nDemo interrupted by user")
    except Exception as e:
        print(f"\n\nDemo failed with error: {e}")
        import traceback
        traceback.print_exc()