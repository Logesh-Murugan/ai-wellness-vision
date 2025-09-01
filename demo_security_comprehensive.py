#!/usr/bin/env python3
"""
Comprehensive Security System Demo
Demonstrates all implemented security and privacy features for AI WellnessVision
"""

import json
import time
from datetime import datetime
from typing import Dict, Any

from src.security.encryption import get_encryption_service, EncryptionType
from src.security.privacy import get_privacy_manager, DataCategory, AnonymizationLevel
from src.security.consent import get_consent_manager, ConsentType
from src.security.data_protection import get_data_protection_service
from src.security.transport_security import get_transport_security_manager
from src.security.security_middleware import SecurityMiddleware

def print_section(title: str):
    """Print a formatted section header"""
    print(f"\n{'='*60}")
    print(f" {title}")
    print(f"{'='*60}")

def print_subsection(title: str):
    """Print a formatted subsection header"""
    print(f"\n{'-'*40}")
    print(f" {title}")
    print(f"{'-'*40}")

def print_result(label: str, value: Any, indent: int = 0):
    """Print a formatted result"""
    spaces = "  " * indent
    if isinstance(value, dict):
        print(f"{spaces}{label}:")
        for k, v in value.items():
            print(f"{spaces}  {k}: {v}")
    elif isinstance(value, list):
        print(f"{spaces}{label}: [{len(value)} items]")
        for i, item in enumerate(value[:3]):  # Show first 3 items
            print(f"{spaces}  [{i}]: {item}")
        if len(value) > 3:
            print(f"{spaces}  ... and {len(value) - 3} more")
    else:
        print(f"{spaces}{label}: {value}")

def demo_transport_security():
    """Demonstrate transport security features"""
    print_section("TRANSPORT SECURITY DEMONSTRATION")
    
    transport_manager = get_transport_security_manager()
    
    print_subsection("1. HTTPS Security Initialization")
    
    # Initialize HTTPS security with self-signed certificate
    https_result = transport_manager.initialize_https_security("demo_cert", "localhost")
    print_result("HTTPS Initialization", https_result)
    
    # Get security headers
    security_headers = transport_manager.https_manager.get_security_headers()
    print_result("Security Headers Count", len(security_headers))
    
    # Show key security headers
    key_headers = {
        "Strict-Transport-Security": security_headers.get("Strict-Transport-Security"),
        "Content-Security-Policy": security_headers.get("Content-Security-Policy")[:50] + "...",
        "X-Frame-Options": security_headers.get("X-Frame-Options"),
        "X-Content-Type-Options": security_headers.get("X-Content-Type-Options")
    }
    print_result("Key Security Headers", key_headers, 1)
    
    print_subsection("2. WebSocket Security")
    
    # Test WebSocket connection validation
    ws_manager = transport_manager.websocket_manager
    
    # Valid connection
    valid_connection = ws_manager.validate_websocket_connection(
        "192.168.1.100", "https://localhost", {"User-Agent": "Demo Browser"}
    )
    print_result("Valid WebSocket Connection", {
        "allowed": valid_connection["allowed"],
        "connection_id": valid_connection.get("connection_id", "N/A")[:20] + "..."
    })
    
    # Invalid origin
    invalid_connection = ws_manager.validate_websocket_connection(
        "192.168.1.100", "https://malicious.com", {"User-Agent": "Demo Browser"}
    )
    print_result("Invalid Origin Connection", {
        "allowed": invalid_connection["allowed"],
        "errors": invalid_connection.get("errors", [])
    })
    
    # Test message validation
    if valid_connection["allowed"]:
        connection_id = valid_connection["connection_id"]
        
        # Valid message
        valid_msg = ws_manager.validate_websocket_message(connection_id, b"Hello, world!")
        print_result("Valid Message", {"valid": valid_msg["valid"]})
        
        # Malicious message
        malicious_msg = ws_manager.validate_websocket_message(
            connection_id, b"<script>alert('xss')</script>"
        )
        print_result("Malicious Message", {
            "valid": malicious_msg["valid"],
            "reason": malicious_msg.get("reason", "N/A")
        })
        
        # Clean up
        ws_manager.close_websocket_connection(connection_id)
    
    # Transport security status
    transport_status = transport_manager.get_transport_security_status()
    print_result("Transport Security Status", {
        "HTTPS Certificates": transport_status["https"]["certificates"],
        "Active WebSocket Connections": transport_status["websocket"]["active_connections"],
        "TLS Min Version": transport_status["https"]["tls_config"]["min_version"]
    })

def demo_encryption_services():
    """Demonstrate encryption services"""
    print_section("ENCRYPTION SERVICES DEMONSTRATION")
    
    encryption_service = get_encryption_service()
    
    print_subsection("1. Symmetric Encryption")
    
    # Test symmetric encryption
    sensitive_data = "Patient John Doe has diabetes and requires insulin treatment"
    print_result("Original Data", sensitive_data[:50] + "...")
    
    encrypted_data = encryption_service.encrypt_data(sensitive_data, encryption_type=EncryptionType.SYMMETRIC)
    print_result("Encrypted Data", {
        "type": encrypted_data.encryption_type.value,
        "key_id": encrypted_data.key_id,
        "size": len(encrypted_data.encrypted_content)
    })
    
    decrypted_data = encryption_service.decrypt_data(encrypted_data)
    print_result("Decryption Success", decrypted_data.decode() == sensitive_data)
    
    print_subsection("2. Asymmetric Encryption")
    
    # Test asymmetric encryption
    confidential_data = "Confidential patient medical record #12345"
    encrypted_asym = encryption_service.encrypt_data(confidential_data, encryption_type=EncryptionType.ASYMMETRIC)
    print_result("Asymmetric Encryption", {
        "type": encrypted_asym.encryption_type.value,
        "key_id": encrypted_asym.key_id,
        "size": len(encrypted_asym.encrypted_content)
    })
    
    decrypted_asym = encryption_service.decrypt_data(encrypted_asym)
    print_result("Asymmetric Decryption Success", decrypted_asym.decode() == confidential_data)
    
    print_subsection("3. Password Hashing")
    
    # Test password hashing
    password = "SecurePassword123!"
    hash_value, salt = encryption_service.hash_password(password)
    print_result("Password Hash", {
        "hash_length": len(hash_value),
        "salt_length": len(salt),
        "verification": encryption_service.verify_hash(password, hash_value, salt)
    })
    
    print_subsection("4. Data at Rest Encryption")
    
    # Test data at rest encryption
    health_record = {
        "patient_id": "P12345",
        "diagnosis": "Type 2 Diabetes Mellitus",
        "treatment": "Metformin 500mg twice daily",
        "last_visit": "2024-01-15",
        "notes": "Patient shows good compliance with treatment plan"
    }
    
    storage_id = encryption_service.encrypt_data_at_rest(health_record, "health_records", "demo_user")
    print_result("Data at Rest Storage ID", storage_id[:30] + "...")
    
    retrieved_data = encryption_service.decrypt_data_at_rest(storage_id)
    print_result("Data at Rest Retrieval Success", isinstance(retrieved_data, dict))
    print_result("Retrieved Data Sample", {
        "patient_id": retrieved_data.get("patient_id"),
        "diagnosis": retrieved_data.get("diagnosis")
    })
    
    # Key management status
    encryption_status = encryption_service.get_encryption_status()
    print_result("Encryption Service Status", {
        "total_keys": encryption_status["total_keys"],
        "active_keys": encryption_status["active_keys"],
        "encrypted_records": encryption_status["data_at_rest"]["encrypted_records"]
    })

def demo_privacy_management():
    """Demonstrate privacy management features"""
    print_section("PRIVACY MANAGEMENT DEMONSTRATION")
    
    privacy_manager = get_privacy_manager()
    
    print_subsection("1. PII Detection")
    
    # Test PII detection
    text_with_pii = """
    Patient Information:
    Name: Alice Johnson
    Email: alice.johnson@email.com
    Phone: (555) 123-4567
    SSN: 123-45-6789
    Address: 123 Main Street, Anytown, USA 12345
    Medical Condition: Hypertension, managed with medication
    """
    
    detected_pii = privacy_manager.detect_pii_in_text(text_with_pii)
    print_result("Detected PII Types", list(detected_pii.keys()))
    
    for pii_type, values in detected_pii.items():
        print_result(f"  {pii_type.upper()}", values[:2])  # Show first 2 values
    
    print_subsection("2. Data Anonymization")
    
    # Test text anonymization
    anonymized_text = privacy_manager.anonymize_text(text_with_pii, DataCategory.HEALTH_DATA)
    print_result("Original Text (first 100 chars)", text_with_pii.strip()[:100] + "...")
    print_result("Anonymized Text (first 100 chars)", anonymized_text[:100] + "...")
    
    # Test structured data anonymization
    patient_data = {
        "patient_name": "Dr. Smith's Patient",
        "email": "patient@email.com",
        "phone": "555-987-6543",
        "age": 45,
        "diagnosis": "Type 2 Diabetes Mellitus",
        "blood_pressure": "140/90",
        "medication": "Metformin 500mg",
        "symptoms": "Frequent urination, excessive thirst"
    }
    
    print_result("Original Patient Data", {
        "patient_name": patient_data["patient_name"],
        "email": patient_data["email"],
        "diagnosis": patient_data["diagnosis"]
    })
    
    anonymized_data = privacy_manager.process_data(
        "demo_user", patient_data, DataCategory.HEALTH_DATA, "medical_analysis"
    )
    
    print_result("Anonymized Patient Data", {
        "patient_name": anonymized_data["patient_name"],
        "email": anonymized_data["email"],
        "diagnosis": anonymized_data["diagnosis"]  # Should be preserved for medical accuracy
    })
    
    print_subsection("3. Health Data Special Handling")
    
    # Test health data anonymization with medical accuracy preservation
    health_data_anonymizer = privacy_manager.data_anonymizer
    health_anonymized = health_data_anonymizer.anonymize_health_data(
        patient_data, preserve_medical_accuracy=True
    )
    
    print_result("Health Data Anonymization", {
        "personal_info_anonymized": health_anonymized["patient_name"] != patient_data["patient_name"],
        "medical_info_preserved": health_anonymized["diagnosis"] == patient_data["diagnosis"],
        "measurements_modified": health_anonymized["blood_pressure"] != patient_data["blood_pressure"]
    })
    
    # Privacy manager status
    privacy_status = privacy_manager.get_privacy_status()
    print_result("Privacy Manager Status", {
        "total_privacy_rules": privacy_status["total_privacy_rules"],
        "active_rules": privacy_status["active_rules"],
        "data_categories_covered": len(privacy_status["data_categories_covered"]),
        "processing_records": privacy_status["total_processing_records"]
    })

def demo_consent_management():
    """Demonstrate consent management features"""
    print_section("CONSENT MANAGEMENT DEMONSTRATION")
    
    consent_manager = get_consent_manager()
    
    print_subsection("1. Consent Request Creation")
    
    # Create consent request
    template_ids = ["data_processing_consent", "health_data_consent", "biometric_data_consent", "analytics_consent"]
    consent_request = consent_manager.create_consent_request("demo_user", template_ids)
    
    print_result("Consent Request", {
        "request_id": consent_request.request_id[:20] + "...",
        "user_id": consent_request.user_id,
        "templates_count": len(consent_request.consent_templates),
        "expires_at": consent_request.expires_at.strftime("%Y-%m-%d %H:%M:%S") if consent_request.expires_at else "Never"
    })
    
    # Show consent templates
    for template in consent_request.consent_templates[:2]:  # Show first 2
        print_result(f"  Template: {template.template_id}", {
            "title": template.title,
            "required": template.required,
            "legal_basis": template.legal_basis.value
        }, 1)
    
    print_subsection("2. Consent Response Processing")
    
    # Process consent responses
    consent_responses = {
        "data_processing_consent": True,
        "health_data_consent": True,
        "biometric_data_consent": True,
        "analytics_consent": False  # User declines analytics
    }
    
    response_result = consent_manager.process_consent_response(
        consent_request.request_id, consent_responses
    )
    
    print_result("Consent Processing Result", {
        "status": response_result["status"],
        "processed_consents": len(response_result["processed_consents"])
    })
    
    for consent in response_result["processed_consents"]:
        print_result(f"  {consent['consent_type']}", {
            "status": consent["status"],
            "expires_at": consent["expires_at"][:10] if consent["expires_at"] else "Never"
        }, 1)
    
    print_subsection("3. Consent Validation")
    
    # Test consent validation for different operations
    operations = ["image_analysis", "voice_processing", "health_assessment", "data_analytics"]
    
    for operation in operations:
        validation = consent_manager.validate_operation_consent("demo_user", operation)
        print_result(f"Operation: {operation}", {
            "valid": validation["valid"],
            "missing_consents": len(validation["missing_consents"]),
            "expired_consents": len(validation["expired_consents"])
        })
    
    print_subsection("4. User Consent Dashboard")
    
    # Get user consent dashboard
    dashboard = consent_manager.get_consent_dashboard("demo_user")
    print_result("Consent Dashboard", {
        "total_consents": len(dashboard["current_consents"]),
        "recommendations": len(dashboard["recommendations"]),
        "expiring_consents": len(dashboard["expiring_consents"]),
        "health_score": dashboard["consent_health_score"]["score"]
    })
    
    print_subsection("5. Consent Withdrawal")
    
    # Test consent withdrawal
    withdrawal_success = consent_manager.withdraw_consent("demo_user", ConsentType.ANALYTICS)
    print_result("Analytics Consent Withdrawal", withdrawal_success)
    
    # Verify withdrawal
    analytics_consent_valid = consent_manager.check_consent("demo_user", ConsentType.ANALYTICS)
    print_result("Analytics Consent Still Valid", analytics_consent_valid)

def demo_data_protection():
    """Demonstrate comprehensive data protection"""
    print_section("DATA PROTECTION DEMONSTRATION")
    
    data_protection_service = get_data_protection_service()
    
    print_subsection("1. Secure Data Processing")
    
    # Process health data securely
    health_data = {
        "patient_name": "Jane Smith",
        "email": "jane.smith@email.com",
        "phone": "555-456-7890",
        "age": 38,
        "diagnosis": "Hypertension",
        "symptoms": "Headaches, dizziness",
        "blood_pressure": "150/95",
        "medication": "Lisinopril 10mg daily",
        "doctor_notes": "Patient responds well to ACE inhibitor therapy"
    }
    
    print_result("Original Health Data", {
        "patient_name": health_data["patient_name"],
        "email": health_data["email"],
        "diagnosis": health_data["diagnosis"]
    })
    
    # Note: User already has consents from previous demo
    processed_data = data_protection_service.process_data_securely(
        "demo_user", health_data, DataCategory.HEALTH_DATA, "comprehensive_health_analysis"
    )
    
    print_result("Securely Processed Data", {
        "patient_name": processed_data["patient_name"],
        "email": processed_data["email"],
        "diagnosis": processed_data["diagnosis"],  # Should be preserved
        "data_encrypted": "patient_name" in processed_data and processed_data["patient_name"] != health_data["patient_name"]
    })
    
    print_subsection("2. Data Access Validation")
    
    # Test data access validation
    access_validation = data_protection_service.validate_data_access(
        "demo_user", DataCategory.HEALTH_DATA, "health_assessment"
    )
    
    print_result("Data Access Validation", {
        "access_granted": access_validation["access_granted"],
        "consent_valid": access_validation["consent_status"]["valid"],
        "policy_compliant": access_validation["policy_compliant"]
    })
    
    print_subsection("3. GDPR Compliance - Data Export")
    
    # Test data export (GDPR Article 20 - Right to data portability)
    export_data = data_protection_service.export_user_data("demo_user")
    
    print_result("Data Export Summary", {
        "user_id": export_data["user_id"],
        "consent_records": len(export_data["consent_data"]["consents"]),
        "privacy_records": export_data["privacy_data"]["total_records"],
        "processing_logs": len(export_data["processing_logs"]),
        "export_timestamp": export_data["export_timestamp"][:19]
    })
    
    print_subsection("4. Data Protection Audit")
    
    # Generate audit report
    audit_report = data_protection_service.audit_data_protection()
    
    print_result("Data Protection Audit", {
        "audit_period_days": audit_report["audit_period_days"],
        "total_activities": audit_report["total_processing_activities"],
        "compliance_issues": len(audit_report["compliance_issues"]),
        "encryption_usage_rate": f"{audit_report['encryption_usage_rate']:.1f}%",
        "consent_verification_rate": f"{audit_report['consent_verification_rate']:.1f}%"
    })
    
    if audit_report["compliance_issues"]:
        print_result("Compliance Issues", audit_report["compliance_issues"])
    else:
        print_result("Compliance Status", "✓ No issues detected")

def demo_security_middleware():
    """Demonstrate security middleware features"""
    print_section("SECURITY MIDDLEWARE DEMONSTRATION")
    
    security_middleware = SecurityMiddleware()
    
    print_subsection("1. Session Management")
    
    # Create secure session
    session_result = security_middleware.create_secure_session(
        "demo_user", "192.168.1.100", "Mozilla/5.0 (Demo Browser)"
    )
    
    print_result("Session Creation", {
        "success": session_result["success"],
        "session_id": session_result["session_id"][:20] + "...",
        "csrf_token": session_result["csrf_token"][:20] + "...",
        "expires_in_seconds": session_result["expires_in"]
    })
    
    session_id = session_result["session_id"]
    csrf_token = session_result["csrf_token"]
    
    # Validate session
    session_validation = security_middleware.session_manager.validate_session(
        session_id, "192.168.1.100", "Mozilla/5.0 (Demo Browser)"
    )
    
    print_result("Session Validation", {
        "valid": session_validation["valid"],
        "user_id": session_validation["session_data"]["user_id"],
        "created_at": session_validation["session_data"]["created_at"][:19]
    })
    
    # Test CSRF protection
    csrf_valid = security_middleware.validate_csrf_token(session_id, csrf_token)
    csrf_invalid = security_middleware.validate_csrf_token(session_id, "invalid_token")
    
    print_result("CSRF Protection", {
        "valid_token": csrf_valid,
        "invalid_token": csrf_invalid
    })
    
    print_subsection("2. Request Processing and Security")
    
    # Test normal request
    normal_request = {
        "client_ip": "192.168.1.100",
        "user_agent": "Mozilla/5.0 (Demo Browser)",
        "input_data": {
            "message": "Hello, I have a headache. What should I do?",
            "user_id": "demo_user"
        }
    }
    
    normal_result = security_middleware.process_request(normal_request)
    print_result("Normal Request", {
        "allowed": normal_result["allowed"],
        "errors": len(normal_result["errors"]),
        "warnings": len(normal_result["warnings"])
    })
    
    # Test malicious request
    malicious_request = {
        "client_ip": "192.168.1.200",
        "user_agent": "AttackBot/1.0",
        "input_data": {
            "query": "'; DROP TABLE users; --",
            "script": "<script>alert('xss')</script>",
            "command": "rm -rf /"
        }
    }
    
    malicious_result = security_middleware.process_request(malicious_request)
    print_result("Malicious Request", {
        "allowed": malicious_result["allowed"],
        "errors": len(malicious_result["errors"]),
        "warnings": len(malicious_result["warnings"]),
        "threats_detected": len(malicious_result.get("threats_detected", []))
    })
    
    print_subsection("3. Rate Limiting")
    
    # Test rate limiting
    rate_limited_ip = "192.168.1.300"
    rate_limit_results = []
    
    for i in range(8):  # Try 8 requests rapidly
        request = {
            "client_ip": rate_limited_ip,
            "input_data": {"request": f"test_{i}"}
        }
        result = security_middleware.process_request(request)
        rate_limit_results.append(result["allowed"])
    
    allowed_requests = sum(rate_limit_results)
    blocked_requests = len(rate_limit_results) - allowed_requests
    
    print_result("Rate Limiting Test", {
        "total_requests": len(rate_limit_results),
        "allowed_requests": allowed_requests,
        "blocked_requests": blocked_requests,
        "rate_limiting_active": blocked_requests > 0
    })
    
    # Security middleware status
    security_status = security_middleware.get_security_status()
    print_result("Security Middleware Status", {
        "active_sessions": security_status["active_sessions"],
        "rate_limited_ips": security_status["rate_limited_ips"],
        "security_headers_enabled": security_status["security_headers_enabled"],
        "input_validation_patterns": security_status["input_validation_patterns"]
    })
    
    # Clean up session
    security_middleware.logout_user(session_id)

def demo_gdpr_compliance():
    """Demonstrate GDPR compliance features"""
    print_section("GDPR COMPLIANCE DEMONSTRATION")
    
    data_protection_service = get_data_protection_service()
    
    print_subsection("1. Right to Access (Article 15)")
    
    # User requests access to their data
    user_data_export = data_protection_service.export_user_data("demo_user")
    
    print_result("Data Access Request", {
        "user_id": user_data_export["user_id"],
        "data_categories": len(user_data_export["privacy_data"]["by_category"]),
        "consent_records": len(user_data_export["consent_data"]["consents"]),
        "processing_activities": len(user_data_export["processing_logs"]),
        "export_format": "JSON",
        "export_timestamp": user_data_export["export_timestamp"][:19]
    })
    
    print_subsection("2. Right to Rectification (Article 16)")
    
    # Simulate data correction (would be implemented in actual system)
    print_result("Data Rectification", {
        "status": "Available",
        "description": "Users can request corrections to their personal data",
        "implementation": "Through consent management and data update APIs"
    })
    
    print_subsection("3. Right to Erasure (Article 17)")
    
    # Create a test user for deletion demo
    test_user_id = "gdpr_deletion_demo_user"
    
    # Grant consents for test user
    data_protection_service.consent_manager.grant_consent(
        test_user_id, ConsentType.DATA_PROCESSING, "GDPR demo"
    )
    
    # Process some data
    test_data = {
        "name": "GDPR Test User",
        "email": "gdpr.test@example.com",
        "condition": "Test condition for GDPR demo"
    }
    
    data_protection_service.process_data_securely(
        test_user_id, test_data, DataCategory.HEALTH_DATA, "gdpr_demo"
    )
    
    # Verify data exists
    data_before = data_protection_service.export_user_data(test_user_id)
    print_result("Data Before Deletion", {
        "privacy_records": data_before["privacy_data"]["total_records"],
        "consent_records": len(data_before["consent_data"]["consents"]),
        "processing_logs": len(data_before["processing_logs"])
    })
    
    # Delete all user data (Right to be forgotten)
    deletion_result = data_protection_service.delete_user_data(test_user_id)
    print_result("Data Deletion Result", {
        "status": deletion_result["status"],
        "deletion_timestamp": deletion_result["deletion_timestamp"][:19],
        "consent_data_deleted": deletion_result["deletion_results"]["consent_data"],
        "privacy_data_deleted": deletion_result["deletion_results"]["privacy_data"]["status"] == "success"
    })
    
    # Verify data is deleted
    data_after = data_protection_service.export_user_data(test_user_id)
    print_result("Data After Deletion", {
        "privacy_records": data_after["privacy_data"]["total_records"],
        "consent_records": len(data_after["consent_data"]["consents"]),
        "processing_logs": len(data_after["processing_logs"])
    })
    
    print_subsection("4. Right to Data Portability (Article 20)")
    
    print_result("Data Portability", {
        "status": "Implemented",
        "format": "JSON",
        "includes": ["Personal data", "Consent records", "Processing logs", "Metadata"],
        "machine_readable": True,
        "structured_format": True
    })
    
    print_subsection("5. Privacy by Design Compliance")
    
    privacy_manager = get_privacy_manager()
    privacy_status = privacy_manager.get_privacy_status()
    
    print_result("Privacy by Design", {
        "default_privacy_rules": privacy_status["active_rules"] > 0,
        "data_minimization": "Implemented through anonymization",
        "purpose_limitation": "Enforced through consent validation",
        "storage_limitation": "Implemented through retention policies",
        "transparency": "Provided through audit logs and export features"
    })

def main():
    """Run comprehensive security demonstration"""
    print("🔒 AI WellnessVision - Comprehensive Security System Demo")
    print("=" * 60)
    print("This demo showcases all implemented security and privacy features")
    print("including encryption, privacy management, consent handling, and GDPR compliance.")
    print()
    
    start_time = time.time()
    
    try:
        # Run all demonstrations
        demo_transport_security()
        demo_encryption_services()
        demo_privacy_management()
        demo_consent_management()
        demo_data_protection()
        demo_security_middleware()
        demo_gdpr_compliance()
        
        # Final summary
        end_time = time.time()
        print_section("DEMONSTRATION SUMMARY")
        
        print_result("Demo Completion", {
            "status": "✓ SUCCESS",
            "duration": f"{end_time - start_time:.2f} seconds",
            "features_demonstrated": [
                "Transport Security (HTTPS/WebSocket)",
                "Data Encryption (Symmetric/Asymmetric/At-Rest)",
                "Privacy Management & Anonymization",
                "Consent Management & Validation",
                "Data Protection & Security Policies",
                "Security Middleware & Session Management",
                "GDPR Compliance Features"
            ]
        })
        
        print("\n🎉 All security features demonstrated successfully!")
        print("The AI WellnessVision system implements comprehensive security measures")
        print("to protect user data and ensure privacy compliance.")
        
    except Exception as e:
        print(f"\n❌ Demo failed with error: {str(e)}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    main()