# test_security_comprehensive.py - Comprehensive tests for security system
import pytest
import time
from unittest.mock import Mock, patch, MagicMock
from datetime import datetime, timedelta

from src.security.encryption import (
    EncryptionService, SymmetricEncryption, AsymmetricEncryption, 
    HashingService, KeyManager, EncryptionType, KeyType
)
from src.security.privacy import (
    PrivacyManager, DataAnonymizer, PIIDetector, DataRetentionManager,
    DataCategory, AnonymizationLevel
)
from src.security.consent import (
    ConsentManager, ConsentRecord, ConsentTemplate, ConsentRequest,
    ConsentType, ConsentStatus, ConsentBasis
)
from src.security.data_protection import (
    DataProtectionService, DataProtectionPolicy, DataClassification,
    ProcessingActivity
)
from src.security.security_middleware import (
    SecurityMiddleware, RateLimiter, InputValidator, SessionManager,
    SecurityHeaders, require_consent, require_data_protection
)

class TestEncryptionService:
    """Test encryption service functionality"""
    
    def setup_method(self):
        """Set up test fixtures"""
        self.encryption_service = EncryptionService()
    
    def test_symmetric_encryption(self):
        """Test symmetric encryption and decryption"""
        test_data = "sensitive health information"
        
        # Encrypt data
        encrypted_data = self.encryption_service.encrypt_data(
            test_data, encryption_type=EncryptionType.SYMMETRIC
        )
        
        assert encrypted_data.encryption_type == EncryptionType.SYMMETRIC
        assert encrypted_data.encrypted_content != test_data.encode()
        
        # Decrypt data
        decrypted_data = self.encryption_service.decrypt_data(encrypted_data)
        assert decrypted_data.decode() == test_data
    
    def test_asymmetric_encryption(self):
        """Test asymmetric encryption and decryption"""
        test_data = "confidential patient data"
        
        # Encrypt data
        encrypted_data = self.encryption_service.encrypt_data(
            test_data, encryption_type=EncryptionType.ASYMMETRIC
        )
        
        assert encrypted_data.encryption_type == EncryptionType.ASYMMETRIC
        assert encrypted_data.encrypted_content != test_data.encode()
        
        # Decrypt data
        decrypted_data = self.encryption_service.decrypt_data(encrypted_data)
        assert decrypted_data.decode() == test_data
    
    def test_password_hashing(self):
        """Test password hashing and verification"""
        password = "secure_password_123"
        
        # Hash password
        hash_value, salt = self.encryption_service.hash_password(password)
        
        assert len(hash_value) > 0
        assert len(salt) > 0
        
        # Verify password
        is_valid = self.encryption_service.verify_hash(password, hash_value, salt)
        assert is_valid
        
        # Verify wrong password
        is_invalid = self.encryption_service.verify_hash("wrong_password", hash_value, salt)
        assert not is_invalid
    
    def test_key_management(self):
        """Test encryption key management"""
        key_manager = self.encryption_service.key_manager
        
        # Generate symmetric key
        sym_key = key_manager.generate_symmetric_key("test_sym_key", expires_in_days=30)
        assert sym_key.key_type == KeyType.AES_256
        assert sym_key.expires_at is not None
        
        # Generate asymmetric key pair
        asym_key = key_manager.generate_asymmetric_key_pair("test_asym_key", expires_in_days=365)
        assert asym_key.key_type == KeyType.RSA_2048
        
        # Check key validity
        assert key_manager.is_key_valid("test_sym_key")
        assert key_manager.is_key_valid("test_asym_key")
    
    def test_secure_token_generation(self):
        """Test secure token generation"""
        token1 = self.encryption_service.generate_secure_token()
        token2 = self.encryption_service.generate_secure_token()
        
        assert len(token1) > 0
        assert len(token2) > 0
        assert token1 != token2  # Should be unique
    
    def test_encryption_status(self):
        """Test encryption service status"""
        status = self.encryption_service.get_encryption_status()
        
        assert "total_keys" in status
        assert "active_keys" in status
        assert "default_keys_available" in status
        assert status["total_keys"] >= 2  # At least default keys

class TestPrivacyManager:
    """Test privacy management functionality"""
    
    def setup_method(self):
        """Set up test fixtures"""
        self.privacy_manager = PrivacyManager()
    
    def test_pii_detection(self):
        """Test PII detection in text"""
        text_with_pii = "Contact John Doe at john.doe@email.com or call 555-123-4567"
        
        detected_pii = self.privacy_manager.detect_pii_in_text(text_with_pii)
        
        assert "email" in detected_pii
        assert "phone" in detected_pii
        assert "name" in detected_pii
        assert "john.doe@email.com" in detected_pii["email"]
        assert "555-123-4567" in detected_pii["phone"]
    
    def test_data_anonymization(self):
        """Test data anonymization"""
        test_data = {
            "patient_name": "Alice Johnson",
            "email": "alice@example.com",
            "age": 35,
            "diagnosis": "hypertension"
        }
        
        anonymized_data = self.privacy_manager.process_data(
            "user123", test_data, DataCategory.HEALTH_DATA, "medical_analysis"
        )
        
        # Should be anonymized
        assert anonymized_data["patient_name"] != "Alice Johnson"
        assert anonymized_data["email"] != "alice@example.com"
        assert "diagnosis" in anonymized_data  # Should still be present
    
    def test_text_anonymization_levels(self):
        """Test different anonymization levels"""
        text = "Patient John Smith, age 45, diagnosed with diabetes"
        
        # Pseudonymization
        pseudo_text = self.privacy_manager.anonymize_text(text, DataCategory.HEALTH_DATA)
        assert "John Smith" not in pseudo_text
        assert "diabetes" in pseudo_text  # Medical terms should remain
        
        # Test consistency
        pseudo_text2 = self.privacy_manager.anonymize_text(text, DataCategory.HEALTH_DATA)
        assert pseudo_text == pseudo_text2  # Should be consistent
    
    def test_user_data_summary(self):
        """Test user data summary generation"""
        # Process some data first
        test_data = {"name": "Test User", "condition": "test condition"}
        self.privacy_manager.process_data(
            "user123", test_data, DataCategory.HEALTH_DATA, "testing"
        )
        
        summary = self.privacy_manager.get_user_data_summary("user123")
        
        assert summary["user_id"] == "user123"
        assert summary["total_records"] > 0
        assert "by_category" in summary
    
    def test_user_data_deletion(self):
        """Test user data deletion (right to be forgotten)"""
        # Process some data first
        test_data = {"name": "Test User", "email": "test@example.com"}
        self.privacy_manager.process_data(
            "user456", test_data, DataCategory.PERSONAL_IDENTIFIER, "testing"
        )
        
        # Verify data exists
        summary_before = self.privacy_manager.get_user_data_summary("user456")
        assert summary_before["total_records"] > 0
        
        # Delete user data
        deletion_result = self.privacy_manager.delete_user_data("user456")
        assert deletion_result["status"] == "success"
        
        # Verify data is deleted
        summary_after = self.privacy_manager.get_user_data_summary("user456")
        assert summary_after["total_records"] == 0
    
    def test_privacy_status(self):
        """Test privacy manager status"""
        status = self.privacy_manager.get_privacy_status()
        
        assert "total_privacy_rules" in status
        assert "active_rules" in status
        assert "data_categories_covered" in status
        assert status["total_privacy_rules"] > 0

class TestConsentManager:
    """Test consent management functionality"""
    
    def setup_method(self):
        """Set up test fixtures"""
        self.consent_manager = ConsentManager()
    
    def test_consent_request_creation(self):
        """Test creating consent requests"""
        template_ids = ["data_processing_consent", "health_data_consent"]
        
        consent_request = self.consent_manager.create_consent_request(
            "user123", template_ids, expires_in_hours=48
        )
        
        assert consent_request.user_id == "user123"
        assert len(consent_request.consent_templates) == 2
        assert consent_request.expires_at is not None
        assert not consent_request.completed
    
    def test_consent_response_processing(self):
        """Test processing consent responses"""
        # Create consent request
        template_ids = ["data_processing_consent", "analytics_consent"]
        consent_request = self.consent_manager.create_consent_request("user123", template_ids)
        
        # Process responses
        responses = {
            "data_processing_consent": True,
            "analytics_consent": False
        }
        
        result = self.consent_manager.process_consent_response(
            consent_request.request_id, responses
        )
        
        assert result["status"] == "success"
        assert len(result["processed_consents"]) == 2
        
        # Check consent status
        assert self.consent_manager.check_consent("user123", ConsentType.DATA_PROCESSING)
        assert not self.consent_manager.check_consent("user123", ConsentType.ANALYTICS)
    
    def test_consent_withdrawal(self):
        """Test consent withdrawal"""
        # Grant consent first
        self.consent_manager.grant_consent(
            "user123", ConsentType.MARKETING, "Marketing communications"
        )
        
        # Verify consent exists
        assert self.consent_manager.check_consent("user123", ConsentType.MARKETING)
        
        # Withdraw consent
        withdrawn = self.consent_manager.withdraw_consent("user123", ConsentType.MARKETING)
        assert withdrawn
        
        # Verify consent is withdrawn
        assert not self.consent_manager.check_consent("user123", ConsentType.MARKETING)
    
    def test_operation_consent_validation(self):
        """Test consent validation for operations"""
        # Grant required consents
        self.consent_manager.grant_consent(
            "user123", ConsentType.DATA_PROCESSING, "Data processing"
        )
        self.consent_manager.grant_consent(
            "user123", ConsentType.HEALTH_DATA, "Health data processing"
        )
        
        # Validate operation
        validation = self.consent_manager.validate_operation_consent(
            "user123", "health_assessment"
        )
        
        assert validation["valid"]
        assert len(validation["missing_consents"]) == 0
    
    def test_expiring_consents(self):
        """Test expiring consent detection"""
        # Create consent that expires soon
        consent_record = self.consent_manager.grant_consent(
            "user123", ConsentType.DATA_PROCESSING, "Test consent", expires_in_days=1
        )
        
        expiring_consents = self.consent_manager.get_expiring_consents(days_ahead=7)
        
        assert len(expiring_consents) > 0
        assert any(c["user_id"] == "user123" for c in expiring_consents)
    
    def test_consent_export(self):
        """Test consent data export"""
        # Grant some consents
        self.consent_manager.grant_consent(
            "user123", ConsentType.DATA_PROCESSING, "Data processing"
        )
        
        export_data = self.consent_manager.export_user_consents("user123")
        
        assert export_data["user_id"] == "user123"
        assert "consents" in export_data
        assert "detailed_consents" in export_data
        assert "exported_at" in export_data
    
    def test_consent_statistics(self):
        """Test consent statistics"""
        stats = self.consent_manager.get_consent_statistics()
        
        assert "total_users" in stats
        assert "total_consents" in stats
        assert "by_status" in stats
        assert "by_type" in stats

class TestDataProtectionService:
    """Test data protection service functionality"""
    
    def setup_method(self):
        """Set up test fixtures"""
        self.data_protection_service = DataProtectionService()
    
    def test_secure_data_processing(self):
        """Test secure data processing"""
        # First grant required consents
        self.data_protection_service.consent_manager.grant_consent(
            "user123", ConsentType.DATA_PROCESSING, "Data processing"
        )
        self.data_protection_service.consent_manager.grant_consent(
            "user123", ConsentType.HEALTH_DATA, "Health data processing"
        )
        
        test_data = {
            "patient_name": "John Doe",
            "diagnosis": "hypertension",
            "age": 45
        }
        
        processed_data = self.data_protection_service.process_data_securely(
            "user123", test_data, DataCategory.HEALTH_DATA, "medical_analysis"
        )
        
        # Data should be processed and anonymized
        assert "patient_name" in processed_data
        assert processed_data["patient_name"] != "John Doe"  # Should be anonymized
    
    def test_data_access_validation(self):
        """Test data access validation"""
        # Grant consent
        self.data_protection_service.consent_manager.grant_consent(
            "user123", ConsentType.DATA_PROCESSING, "Data processing"
        )
        
        validation = self.data_protection_service.validate_data_access(
            "user123", DataCategory.HEALTH_DATA, "health_assessment"
        )
        
        assert "access_granted" in validation
        assert "consent_status" in validation
    
    def test_user_data_export(self):
        """Test comprehensive user data export"""
        # Process some data first
        self.data_protection_service.consent_manager.grant_consent(
            "user123", ConsentType.DATA_PROCESSING, "Data processing"
        )
        
        test_data = {"name": "Test User", "condition": "test"}
        self.data_protection_service.process_data_securely(
            "user123", test_data, DataCategory.HEALTH_DATA, "testing"
        )
        
        export_data = self.data_protection_service.export_user_data("user123")
        
        assert export_data["user_id"] == "user123"
        assert "consent_data" in export_data
        assert "privacy_data" in export_data
        assert "processing_logs" in export_data
    
    def test_user_data_deletion(self):
        """Test comprehensive user data deletion"""
        # Set up user data
        self.data_protection_service.consent_manager.grant_consent(
            "user456", ConsentType.DATA_PROCESSING, "Data processing"
        )
        
        test_data = {"name": "Test User", "email": "test@example.com"}
        self.data_protection_service.process_data_securely(
            "user456", test_data, DataCategory.PERSONAL_IDENTIFIER, "testing"
        )
        
        # Delete all user data
        deletion_result = self.data_protection_service.delete_user_data("user456")
        
        assert deletion_result["status"] == "completed"
        assert "deletion_results" in deletion_result
    
    def test_data_protection_audit(self):
        """Test data protection audit"""
        audit_report = self.data_protection_service.audit_data_protection()
        
        assert "audit_timestamp" in audit_report
        assert "total_processing_activities" in audit_report
        assert "compliance_issues" in audit_report
        assert "encryption_usage_rate" in audit_report
    
    def test_protection_status(self):
        """Test data protection status"""
        status = self.data_protection_service.get_protection_status()
        
        assert "encryption_service" in status
        assert "privacy_manager" in status
        assert "consent_manager" in status
        assert "protection_policies" in status

class TestSecurityMiddleware:
    """Test security middleware functionality"""
    
    def setup_method(self):
        """Set up test fixtures"""
        self.security_middleware = SecurityMiddleware()
    
    def test_rate_limiting(self):
        """Test rate limiting functionality"""
        client_ip = "192.168.1.100"
        
        # Should not be rate limited initially
        assert not self.security_middleware.rate_limiter.is_rate_limited(client_ip, max_requests=5)
        
        # Exceed rate limit
        for _ in range(6):
            self.security_middleware.rate_limiter.is_rate_limited(client_ip, max_requests=5)
        
        # Should now be rate limited
        assert self.security_middleware.rate_limiter.is_rate_limited(client_ip, max_requests=5)
    
    def test_input_validation(self):
        """Test input validation"""
        # Test safe input
        safe_input = {"name": "John Doe", "age": 30}
        validation = self.security_middleware.input_validator.validate_input(safe_input)
        
        assert validation["valid"]
        assert len(validation["threats_detected"]) == 0
        
        # Test dangerous input
        dangerous_input = {"query": "SELECT * FROM users", "script": "<script>alert('xss')</script>"}
        validation = self.security_middleware.input_validator.validate_input(dangerous_input)
        
        assert not validation["valid"]
        assert len(validation["threats_detected"]) > 0
    
    def test_session_management(self):
        """Test session management"""
        user_id = "user123"
        client_ip = "192.168.1.100"
        user_agent = "Mozilla/5.0"
        
        # Create session
        session_result = self.security_middleware.create_secure_session(
            user_id, client_ip, user_agent
        )
        
        assert session_result["success"]
        assert "session_id" in session_result
        assert "csrf_token" in session_result
        
        session_id = session_result["session_id"]
        csrf_token = session_result["csrf_token"]
        
        # Validate session
        validation = self.security_middleware.session_manager.validate_session(
            session_id, client_ip, user_agent
        )
        
        assert validation["valid"]
        assert validation["session_data"]["user_id"] == user_id
        
        # Validate CSRF token
        assert self.security_middleware.validate_csrf_token(session_id, csrf_token)
        assert not self.security_middleware.validate_csrf_token(session_id, "wrong_token")
        
        # Logout
        logout_success = self.security_middleware.logout_user(session_id)
        assert logout_success
        
        # Session should be invalid after logout
        validation = self.security_middleware.session_manager.validate_session(session_id)
        assert not validation["valid"]
    
    def test_security_headers(self):
        """Test security headers"""
        headers = self.security_middleware.security_headers.get_security_headers()
        
        assert "X-Frame-Options" in headers
        assert "X-Content-Type-Options" in headers
        assert "X-XSS-Protection" in headers
        assert "Strict-Transport-Security" in headers
        assert "Content-Security-Policy" in headers
        
        assert headers["X-Frame-Options"] == "DENY"
        assert headers["X-Content-Type-Options"] == "nosniff"
    
    def test_request_processing(self):
        """Test complete request processing"""
        request_data = {
            "client_ip": "192.168.1.100",
            "user_agent": "Mozilla/5.0",
            "input_data": {"message": "Hello, world!"}
        }
        
        result = self.security_middleware.process_request(request_data)
        
        assert result["allowed"]
        assert "security_headers" in result
        assert len(result["errors"]) == 0
    
    def test_data_request_processing(self):
        """Test data request processing"""
        user_id = "user123"
        
        # Grant required consent
        self.security_middleware.consent_manager.grant_consent(
            user_id, ConsentType.DATA_PROCESSING, "Data processing"
        )
        self.security_middleware.consent_manager.grant_consent(
            user_id, ConsentType.HEALTH_DATA, "Health data processing"
        )
        
        request_data = {"data": {"condition": "test condition"}}
        
        result = self.security_middleware.process_data_request(
            user_id, DataCategory.HEALTH_DATA, "health_assessment", request_data
        )
        
        assert result["allowed"]
        assert "access_validation" in result
    
    def test_security_status(self):
        """Test security middleware status"""
        status = self.security_middleware.get_security_status()
        
        assert "active_sessions" in status
        assert "rate_limited_ips" in status
        assert "security_headers_enabled" in status
        assert "input_validation_patterns" in status

class TestSecurityDecorators:
    """Test security decorators"""
    
    def test_require_consent_decorator(self):
        """Test consent requirement decorator"""
        consent_manager = ConsentManager()
        
        @require_consent([ConsentType.DATA_PROCESSING])
        def protected_function(user_id):
            return f"Success for {user_id}"
        
        # Should fail without consent
        with pytest.raises(PermissionError):
            protected_function("user123")
        
        # Grant consent
        consent_manager.grant_consent(
            "user123", ConsentType.DATA_PROCESSING, "Data processing"
        )
        
        # Should succeed with consent
        result = protected_function("user123")
        assert "Success for user123" in result
    
    def test_require_data_protection_decorator(self):
        """Test data protection requirement decorator"""
        data_protection_service = DataProtectionService()
        
        # Grant required consents
        data_protection_service.consent_manager.grant_consent(
            "user123", ConsentType.DATA_PROCESSING, "Data processing"
        )
        
        @require_data_protection(DataCategory.HEALTH_DATA)
        def protected_function(user_id):
            return f"Protected data access for {user_id}"
        
        # Should work with proper setup
        try:
            result = protected_function("user123")
            # May succeed or fail depending on validation logic
        except PermissionError:
            # Expected if validation fails
            pass

class TestSecurityIntegration:
    """Integration tests for security system"""
    
    def test_end_to_end_data_processing(self):
        """Test complete end-to-end secure data processing"""
        data_protection_service = DataProtectionService()
        security_middleware = SecurityMiddleware()
        
        user_id = "integration_user"
        client_ip = "192.168.1.200"
        
        # 1. Create secure session
        session_result = security_middleware.create_secure_session(
            user_id, client_ip, "Mozilla/5.0"
        )
        assert session_result["success"]
        
        # 2. Grant required consents
        data_protection_service.consent_manager.grant_consent(
            user_id, ConsentType.DATA_PROCESSING, "Data processing"
        )
        data_protection_service.consent_manager.grant_consent(
            user_id, ConsentType.HEALTH_DATA, "Health data processing"
        )
        
        # 3. Process data request
        test_data = {
            "patient_name": "Integration Test Patient",
            "diagnosis": "test condition",
            "age": 35
        }
        
        request_data = {"data": test_data}
        
        result = security_middleware.process_data_request(
            user_id, DataCategory.HEALTH_DATA, "health_assessment", request_data
        )
        
        assert result["allowed"]
        assert "processed_data" in result
        
        # 4. Verify data was processed securely
        processed_data = result["processed_data"]
        assert processed_data["patient_name"] != "Integration Test Patient"  # Should be anonymized
    
    def test_security_violation_handling(self):
        """Test handling of security violations"""
        security_middleware = SecurityMiddleware()
        
        # Test rate limiting violation
        client_ip = "192.168.1.300"
        for _ in range(10):  # Exceed rate limit
            request_data = {"client_ip": client_ip, "input_data": {"test": "data"}}
            result = security_middleware.process_request(request_data)
        
        # Should be blocked
        assert not result["allowed"]
        assert "Rate limit exceeded" in result["errors"]
        
        # Test input validation violation
        malicious_request = {
            "client_ip": "192.168.1.301",
            "input_data": {"query": "DROP TABLE users;"}
        }
        
        result = security_middleware.process_request(malicious_request)
        # Should have warnings about threats
        assert len(result["warnings"]) > 0

class TestTransportSecurity:
    """Test transport security functionality"""
    
    def setup_method(self):
        """Set up test fixtures"""
        from src.security.transport_security import TransportSecurityManager
        self.transport_manager = TransportSecurityManager()
    
    def test_https_initialization(self):
        """Test HTTPS security initialization"""
        result = self.transport_manager.initialize_https_security("test_cert", "localhost")
        
        assert "initialized" in result
        assert "certificate_name" in result
        assert result["certificate_name"] == "test_cert"
    
    def test_ssl_context_creation(self):
        """Test SSL context creation"""
        # Initialize HTTPS first
        self.transport_manager.initialize_https_security("test_cert")
        
        # Create SSL context
        ssl_context = self.transport_manager.https_manager.create_ssl_context("test_cert")
        assert ssl_context is not None
    
    def test_security_headers(self):
        """Test security headers"""
        headers = self.transport_manager.https_manager.get_security_headers()
        
        required_headers = [
            "Strict-Transport-Security",
            "Content-Security-Policy",
            "X-Content-Type-Options",
            "X-Frame-Options",
            "X-XSS-Protection"
        ]
        
        for header in required_headers:
            assert header in headers
    
    def test_websocket_connection_validation(self):
        """Test WebSocket connection validation"""
        validation = self.transport_manager.websocket_manager.validate_websocket_connection(
            "192.168.1.100", "https://localhost", {"User-Agent": "Test"}
        )
        
        assert validation["allowed"]
        assert "connection_id" in validation
    
    def test_websocket_message_validation(self):
        """Test WebSocket message validation"""
        # First establish connection
        connection_validation = self.transport_manager.websocket_manager.validate_websocket_connection(
            "192.168.1.100", "https://localhost", {}
        )
        
        connection_id = connection_validation["connection_id"]
        
        # Test valid message
        message_validation = self.transport_manager.websocket_manager.validate_websocket_message(
            connection_id, b"Hello, world!", "text"
        )
        
        assert message_validation["valid"]
    
    def test_websocket_security_threat_detection(self):
        """Test WebSocket security threat detection"""
        # Establish connection
        connection_validation = self.transport_manager.websocket_manager.validate_websocket_connection(
            "192.168.1.100", "https://localhost", {}
        )
        
        connection_id = connection_validation["connection_id"]
        
        # Test malicious message
        malicious_message = b"<script>alert('xss')</script>"
        message_validation = self.transport_manager.websocket_manager.validate_websocket_message(
            connection_id, malicious_message, "text"
        )
        
        assert not message_validation["valid"]
        assert message_validation["reason"] == "security_threat_detected"

class TestDataAtRestEncryption:
    """Test data at rest encryption functionality"""
    
    def setup_method(self):
        """Set up test fixtures"""
        from src.security.encryption import get_encryption_service
        self.encryption_service = get_encryption_service()
    
    def test_data_at_rest_encryption(self):
        """Test encrypting and decrypting data at rest"""
        test_data = {
            "patient_name": "John Doe",
            "diagnosis": "hypertension",
            "age": 45,
            "medical_history": "Previous heart condition"
        }
        
        # Encrypt data at rest
        storage_id = self.encryption_service.encrypt_data_at_rest(
            test_data, "health_records", "user123"
        )
        
        assert storage_id is not None
        assert len(storage_id) > 0
        
        # Decrypt data at rest
        decrypted_data = self.encryption_service.decrypt_data_at_rest(storage_id)
        
        assert decrypted_data["patient_name"] == "John Doe"
        assert decrypted_data["diagnosis"] == "hypertension"
        assert decrypted_data["age"] == 45
    
    def test_data_at_rest_user_isolation(self):
        """Test that encrypted data is properly isolated by user"""
        user1_data = {"name": "User One", "condition": "condition1"}
        user2_data = {"name": "User Two", "condition": "condition2"}
        
        # Encrypt data for different users
        storage_id1 = self.encryption_service.encrypt_data_at_rest(
            user1_data, "health_records", "user1"
        )
        storage_id2 = self.encryption_service.encrypt_data_at_rest(
            user2_data, "health_records", "user2"
        )
        
        # Get user-specific encrypted data
        user1_storage_ids = self.encryption_service.get_user_encrypted_data("user1")
        user2_storage_ids = self.encryption_service.get_user_encrypted_data("user2")
        
        assert storage_id1 in user1_storage_ids
        assert storage_id2 in user2_storage_ids
        assert storage_id1 not in user2_storage_ids
        assert storage_id2 not in user1_storage_ids
    
    def test_secure_data_deletion(self):
        """Test secure deletion of encrypted data"""
        test_data = {"sensitive": "information", "user": "test_user"}
        
        # Encrypt data
        storage_id = self.encryption_service.encrypt_data_at_rest(
            test_data, "sensitive_data", "test_user"
        )
        
        # Verify data exists
        decrypted_data = self.encryption_service.decrypt_data_at_rest(storage_id)
        assert decrypted_data["sensitive"] == "information"
        
        # Delete data
        deleted = self.encryption_service.delete_encrypted_data_at_rest(storage_id)
        assert deleted
        
        # Verify data is deleted
        with pytest.raises(Exception):
            self.encryption_service.decrypt_data_at_rest(storage_id)
    
    def test_user_data_deletion(self):
        """Test deletion of all user encrypted data"""
        user_id = "deletion_test_user"
        
        # Create multiple encrypted records for user
        data1 = {"record": "1", "data": "sensitive1"}
        data2 = {"record": "2", "data": "sensitive2"}
        data3 = {"record": "3", "data": "sensitive3"}
        
        storage_id1 = self.encryption_service.encrypt_data_at_rest(data1, "records", user_id)
        storage_id2 = self.encryption_service.encrypt_data_at_rest(data2, "records", user_id)
        storage_id3 = self.encryption_service.encrypt_data_at_rest(data3, "records", user_id)
        
        # Verify data exists
        user_storage_ids = self.encryption_service.get_user_encrypted_data(user_id)
        assert len(user_storage_ids) == 3
        
        # Delete all user data
        deleted_count = self.encryption_service.delete_user_encrypted_data(user_id)
        assert deleted_count == 3
        
        # Verify all data is deleted
        user_storage_ids_after = self.encryption_service.get_user_encrypted_data(user_id)
        assert len(user_storage_ids_after) == 0

class TestTransportSecurityCompliance:
    """Test transport security compliance with security standards"""
    
    def setup_method(self):
        """Set up test fixtures"""
        from src.security.transport_security import get_transport_security_manager
        self.transport_manager = get_transport_security_manager()
    
    def test_https_security_headers_compliance(self):
        """Test HTTPS security headers compliance with OWASP standards"""
        headers = self.transport_manager.https_manager.get_security_headers()
        
        # Test required security headers
        required_headers = {
            "Strict-Transport-Security": "max-age=31536000; includeSubDomains; preload",
            "X-Content-Type-Options": "nosniff",
            "X-Frame-Options": "DENY",
            "X-XSS-Protection": "1; mode=block",
            "Referrer-Policy": "strict-origin-when-cross-origin"
        }
        
        for header, expected_value in required_headers.items():
            assert header in headers
            assert headers[header] == expected_value
        
        # Test CSP header exists and is restrictive
        assert "Content-Security-Policy" in headers
        csp = headers["Content-Security-Policy"]
        assert "default-src 'self'" in csp
        assert "frame-ancestors 'none'" in csp
    
    def test_tls_configuration_security(self):
        """Test TLS configuration meets security standards"""
        # Initialize HTTPS security
        result = self.transport_manager.initialize_https_security("test_cert")
        assert result["initialized"]
        
        # Create SSL context and verify configuration
        ssl_context = self.transport_manager.https_manager.create_ssl_context("test_cert")
        
        # Verify minimum TLS version
        assert ssl_context.minimum_version.name in ["TLSv1_2", "TLSv1_3"]
        
        # Verify security options are set
        import ssl
        assert ssl_context.options & ssl.OP_NO_SSLv2
        assert ssl_context.options & ssl.OP_NO_SSLv3
        assert ssl_context.options & ssl.OP_NO_TLSv1
        assert ssl_context.options & ssl.OP_NO_TLSv1_1
    
    def test_websocket_security_validation(self):
        """Test WebSocket security validation"""
        ws_manager = self.transport_manager.websocket_manager
        
        # Test origin validation
        ws_manager.config.require_origin_check = True
        ws_manager.config.allowed_origins = ["https://localhost", "https://example.com"]
        
        # Valid origin should be allowed
        validation = ws_manager.validate_websocket_connection(
            "192.168.1.100", "https://localhost", {"User-Agent": "Test"}
        )
        assert validation["allowed"]
        
        # Invalid origin should be rejected
        validation = ws_manager.validate_websocket_connection(
            "192.168.1.100", "https://malicious.com", {"User-Agent": "Test"}
        )
        assert not validation["allowed"]
        assert "Origin not allowed" in validation["errors"]
    
    def test_websocket_message_size_limits(self):
        """Test WebSocket message size limits"""
        ws_manager = self.transport_manager.websocket_manager
        
        # Establish connection
        connection_validation = ws_manager.validate_websocket_connection(
            "192.168.1.100", "https://localhost", {}
        )
        connection_id = connection_validation["connection_id"]
        
        # Test normal message
        normal_message = b"Hello, world!"
        validation = ws_manager.validate_websocket_message(connection_id, normal_message)
        assert validation["valid"]
        
        # Test oversized message
        oversized_message = b"x" * (ws_manager.config.max_message_size + 1)
        validation = ws_manager.validate_websocket_message(connection_id, oversized_message)
        assert not validation["valid"]
        assert validation["reason"] == "message_too_large"
    
    def test_websocket_connection_limits(self):
        """Test WebSocket connection limits per IP"""
        ws_manager = self.transport_manager.websocket_manager
        client_ip = "192.168.1.200"
        
        # Create connections up to limit
        connection_ids = []
        for i in range(ws_manager.config.max_connections_per_ip):
            validation = ws_manager.validate_websocket_connection(
                client_ip, "https://localhost", {"User-Agent": f"Test{i}"}
            )
            assert validation["allowed"]
            connection_ids.append(validation["connection_id"])
        
        # Next connection should be rejected
        validation = ws_manager.validate_websocket_connection(
            client_ip, "https://localhost", {"User-Agent": "TestOverLimit"}
        )
        assert not validation["allowed"]
        assert "Connection limit exceeded" in validation["errors"]
        
        # Clean up connections
        for conn_id in connection_ids:
            ws_manager.close_websocket_connection(conn_id)

class TestDataProtectionCompliance:
    """Test data protection compliance with privacy regulations"""
    
    def setup_method(self):
        """Set up test fixtures"""
        from src.security.data_protection import get_data_protection_service
        self.data_protection_service = get_data_protection_service()
    
    def test_gdpr_right_to_access(self):
        """Test GDPR right to access (data portability)"""
        user_id = "gdpr_test_user"
        
        # Grant consents and process data
        self.data_protection_service.consent_manager.grant_consent(
            user_id, ConsentType.DATA_PROCESSING, "Data processing"
        )
        self.data_protection_service.consent_manager.grant_consent(
            user_id, ConsentType.HEALTH_DATA, "Health data processing"
        )
        
        test_data = {
            "name": "GDPR Test User",
            "email": "gdpr@example.com",
            "health_condition": "test condition"
        }
        
        self.data_protection_service.process_data_securely(
            user_id, test_data, DataCategory.HEALTH_DATA, "testing"
        )
        
        # Export user data (right to access)
        export_data = self.data_protection_service.export_user_data(user_id)
        
        assert export_data["user_id"] == user_id
        assert "consent_data" in export_data
        assert "privacy_data" in export_data
        assert "processing_logs" in export_data
        assert "export_timestamp" in export_data
    
    def test_gdpr_right_to_be_forgotten(self):
        """Test GDPR right to be forgotten (data deletion)"""
        user_id = "deletion_test_user"
        
        # Set up user data
        self.data_protection_service.consent_manager.grant_consent(
            user_id, ConsentType.DATA_PROCESSING, "Data processing"
        )
        
        test_data = {"name": "Deletion Test User", "email": "delete@example.com"}
        self.data_protection_service.process_data_securely(
            user_id, test_data, DataCategory.PERSONAL_IDENTIFIER, "testing"
        )
        
        # Verify data exists
        export_before = self.data_protection_service.export_user_data(user_id)
        assert export_before["privacy_data"]["total_records"] > 0
        
        # Delete all user data
        deletion_result = self.data_protection_service.delete_user_data(user_id)
        assert deletion_result["status"] == "completed"
        
        # Verify data is deleted
        export_after = self.data_protection_service.export_user_data(user_id)
        assert export_after["privacy_data"]["total_records"] == 0
    
    def test_consent_withdrawal_compliance(self):
        """Test consent withdrawal compliance"""
        user_id = "consent_test_user"
        
        # Grant consent
        self.data_protection_service.consent_manager.grant_consent(
            user_id, ConsentType.MARKETING, "Marketing communications"
        )
        
        # Verify consent is active
        assert self.data_protection_service.consent_manager.check_consent(
            user_id, ConsentType.MARKETING
        )
        
        # Withdraw consent
        withdrawn = self.data_protection_service.consent_manager.withdraw_consent(
            user_id, ConsentType.MARKETING
        )
        assert withdrawn
        
        # Verify consent is withdrawn
        assert not self.data_protection_service.consent_manager.check_consent(
            user_id, ConsentType.MARKETING
        )
        
        # Verify withdrawal is logged
        user_consents = self.data_protection_service.consent_manager.get_user_consents(user_id)
        marketing_consent = user_consents["consents"].get("marketing")
        assert marketing_consent["status"] == "withdrawn"
        assert marketing_consent["withdrawn_at"] is not None
    
    def test_data_minimization_principle(self):
        """Test data minimization principle compliance"""
        user_id = "minimization_test_user"
        
        # Grant minimal required consents
        self.data_protection_service.consent_manager.grant_consent(
            user_id, ConsentType.DATA_PROCESSING, "Data processing"
        )
        
        # Process data with excessive information
        excessive_data = {
            "name": "Test User",
            "email": "test@example.com",
            "phone": "555-1234",
            "ssn": "123-45-6789",
            "credit_card": "4111-1111-1111-1111",
            "relevant_health_info": "headache"
        }
        
        processed_data = self.data_protection_service.process_data_securely(
            user_id, excessive_data, DataCategory.HEALTH_DATA, "symptom_analysis"
        )
        
        # Verify sensitive data is anonymized or removed
        assert processed_data["name"] != "Test User"  # Should be pseudonymized
        assert processed_data["email"] != "test@example.com"  # Should be pseudonymized
        
        # Health info should be preserved for medical accuracy
        assert "relevant_health_info" in processed_data
    
    def test_purpose_limitation_compliance(self):
        """Test purpose limitation principle compliance"""
        user_id = "purpose_test_user"
        
        # Grant consent for specific purpose
        self.data_protection_service.consent_manager.grant_consent(
            user_id, ConsentType.DATA_PROCESSING, "Health analysis only"
        )
        self.data_protection_service.consent_manager.grant_consent(
            user_id, ConsentType.HEALTH_DATA, "Health analysis only"
        )
        
        test_data = {"symptoms": "headache", "age": 30}
        
        # Process data for allowed purpose
        processed_data = self.data_protection_service.process_data_securely(
            user_id, test_data, DataCategory.HEALTH_DATA, "health_analysis"
        )
        assert processed_data is not None
        
        # Verify processing is logged with purpose
        audit_report = self.data_protection_service.audit_data_protection()
        assert audit_report["total_processing_activities"] > 0

class TestSecurityAuditAndCompliance:
    """Test security audit and compliance features"""
    
    def setup_method(self):
        """Set up test fixtures"""
        from src.security.data_protection import get_data_protection_service
        from src.security.security_middleware import SecurityMiddleware
        self.data_protection_service = get_data_protection_service()
        self.security_middleware = SecurityMiddleware()
    
    def test_security_audit_logging(self):
        """Test comprehensive security audit logging"""
        user_id = "audit_test_user"
        
        # Perform various security operations
        self.data_protection_service.consent_manager.grant_consent(
            user_id, ConsentType.DATA_PROCESSING, "Data processing"
        )
        
        test_data = {"name": "Audit User", "condition": "test"}
        self.data_protection_service.process_data_securely(
            user_id, test_data, DataCategory.HEALTH_DATA, "audit_testing"
        )
        
        # Generate audit report
        audit_report = self.data_protection_service.audit_data_protection()
        
        assert "audit_timestamp" in audit_report
        assert "total_processing_activities" in audit_report
        assert "compliance_issues" in audit_report
        assert "encryption_usage_rate" in audit_report
        assert "consent_verification_rate" in audit_report
        
        # Verify audit covers recent activities
        assert audit_report["total_processing_activities"] > 0
    
    def test_security_incident_detection(self):
        """Test security incident detection and response"""
        # Test rate limiting violation
        client_ip = "192.168.1.999"
        
        # Trigger rate limiting
        for _ in range(20):  # Exceed rate limit
            request_data = {
                "client_ip": client_ip,
                "input_data": {"test": "data"}
            }
            result = self.security_middleware.process_request(request_data)
        
        # Should detect and block excessive requests
        assert not result["allowed"]
        assert "Rate limit exceeded" in result["errors"]
        
        # Test malicious input detection
        malicious_request = {
            "client_ip": "192.168.1.888",
            "input_data": {
                "query": "DROP TABLE users; --",
                "script": "<script>alert('xss')</script>",
                "command": "rm -rf /"
            }
        }
        
        result = self.security_middleware.process_request(malicious_request)
        assert len(result["warnings"]) > 0  # Should detect threats
    
    def test_data_breach_simulation(self):
        """Test data breach detection and response procedures"""
        # Simulate unauthorized access attempt
        try:
            # Attempt to access data without proper consent
            user_id = "breach_test_user"
            test_data = {"sensitive": "information"}
            
            # This should fail due to missing consent
            with pytest.raises(ValueError):
                self.data_protection_service.process_data_securely(
                    user_id, test_data, DataCategory.HEALTH_DATA, "unauthorized_access"
                )
        except Exception as e:
            # Verify error is properly logged and handled
            assert "consent" in str(e).lower()
    
    def test_encryption_key_rotation(self):
        """Test encryption key rotation for security"""
        from src.security.encryption import get_encryption_service
        encryption_service = get_encryption_service()
        
        # Generate initial key
        original_key = encryption_service.key_manager.generate_symmetric_key("rotation_test")
        assert original_key.is_active
        
        # Rotate key
        new_key = encryption_service.key_manager.rotate_key("rotation_test")
        assert new_key.is_active
        
        # Verify old key is deactivated
        old_key_info = encryption_service.key_manager.get_key_info("rotation_test")
        assert not old_key_info.is_active
    
    def test_session_security_validation(self):
        """Test session security validation"""
        user_id = "session_test_user"
        client_ip = "192.168.1.100"
        user_agent = "Mozilla/5.0"
        
        # Create secure session
        session_result = self.security_middleware.create_secure_session(
            user_id, client_ip, user_agent
        )
        
        assert session_result["success"]
        session_id = session_result["session_id"]
        csrf_token = session_result["csrf_token"]
        
        # Test session hijacking protection
        different_ip = "192.168.1.200"
        validation = self.security_middleware.session_manager.validate_session(
            session_id, different_ip, user_agent
        )
        # Should detect IP change and invalidate session
        assert not validation["valid"] or "ip_mismatch" in validation.get("warnings", [])
        
        # Test CSRF protection
        assert self.security_middleware.validate_csrf_token(session_id, csrf_token)
        assert not self.security_middleware.validate_csrf_token(session_id, "invalid_token")

class TestPrivacyByDesign:
    """Test privacy by design principles implementation"""
    
    def setup_method(self):
        """Set up test fixtures"""
        from src.security.privacy import get_privacy_manager
        self.privacy_manager = get_privacy_manager()
    
    def test_default_privacy_settings(self):
        """Test that privacy is enabled by default"""
        # Verify default privacy rules are active
        status = self.privacy_manager.get_privacy_status()
        assert status["active_rules"] > 0
        assert status["total_privacy_rules"] > 0
        
        # Verify default anonymization levels are appropriate
        health_rule = None
        for rule in self.privacy_manager.privacy_rules.values():
            if rule.data_category == DataCategory.HEALTH_DATA:
                health_rule = rule
                break
        
        assert health_rule is not None
        assert health_rule.anonymization_level in [
            AnonymizationLevel.PSEUDONYMIZATION,
            AnonymizationLevel.GENERALIZATION
        ]
    
    def test_data_anonymization_consistency(self):
        """Test that data anonymization is consistent across sessions"""
        test_text = "Patient John Smith has diabetes"
        
        # Anonymize text multiple times
        anonymized1 = self.privacy_manager.anonymize_text(test_text, DataCategory.HEALTH_DATA)
        anonymized2 = self.privacy_manager.anonymize_text(test_text, DataCategory.HEALTH_DATA)
        
        # Should be consistent
        assert anonymized1 == anonymized2
        
        # Should not contain original PII
        assert "John Smith" not in anonymized1
        
        # Should preserve medical information
        assert "diabetes" in anonymized1
    
    def test_automatic_pii_detection(self):
        """Test automatic PII detection and handling"""
        text_with_pii = """
        Patient Information:
        Name: Alice Johnson
        Email: alice.johnson@email.com
        Phone: (555) 123-4567
        SSN: 123-45-6789
        Medical Condition: Hypertension
        """
        
        detected_pii = self.privacy_manager.detect_pii_in_text(text_with_pii)
        
        # Should detect various types of PII
        assert "email" in detected_pii
        assert "phone" in detected_pii
        assert "name" in detected_pii
        assert "ssn" in detected_pii
        
        # Verify specific values are detected
        assert "alice.johnson@email.com" in detected_pii["email"]
        assert any("555" in phone for phone in detected_pii["phone"])
    
    def test_health_data_special_handling(self):
        """Test special handling of health data for medical accuracy"""
        health_data = {
            "patient_name": "Dr. Smith's Patient",
            "diagnosis": "Type 2 Diabetes Mellitus",
            "medication": "Metformin 500mg",
            "blood_pressure": "140/90 mmHg",
            "symptoms": "Frequent urination, excessive thirst",
            "doctor_notes": "Patient shows good compliance with treatment"
        }
        
        anonymized_data = self.privacy_manager.data_anonymizer.anonymize_health_data(
            health_data, preserve_medical_accuracy=True
        )
        
        # Personal identifiers should be anonymized
        assert anonymized_data["patient_name"] != "Dr. Smith's Patient"
        
        # Medical information should be preserved
        assert anonymized_data["diagnosis"] == "Type 2 Diabetes Mellitus"
        assert anonymized_data["medication"] == "Metformin 500mg"
        assert anonymized_data["symptoms"] == "Frequent urination, excessive thirst"
        
        # Measurements might have noise added but should be recognizable
        assert "blood_pressure" in anonymized_data
    
    def test_data_retention_enforcement(self):
        """Test automatic data retention policy enforcement"""
        user_id = "retention_test_user"
        
        # Process data with retention policy
        test_data = {"name": "Retention Test", "data": "test_data"}
        processed_data = self.privacy_manager.process_data(
            user_id, test_data, DataCategory.PERSONAL_IDENTIFIER, "testing"
        )
        
        # Verify data is scheduled for deletion
        user_summary = self.privacy_manager.get_user_data_summary(user_id)
        assert user_summary["scheduled_deletions"] > 0
        
        # Test cleanup of expired data
        cleanup_result = self.privacy_manager.cleanup_expired_data()
        assert "deleted_records" in cleanup_result
            "age": 45
        }
        
        # Encrypt data at rest
        storage_id = self.encryption_service.encrypt_data_at_rest(
            test_data, "health_records", "user123"
        )
        
        assert storage_id is not None
        assert len(storage_id) > 0
        
        # Decrypt data at rest
        decrypted_data = self.encryption_service.decrypt_data_at_rest(storage_id)
        
        assert decrypted_data == test_data
    
    def test_user_data_encryption_management(self):
        """Test user-specific encrypted data management"""
        test_data = {"sensitive": "information"}
        
        # Encrypt data for user
        storage_id = self.encryption_service.encrypt_data_at_rest(
            test_data, "user_data", "user456"
        )
        
        # Get user's encrypted data
        user_storage_ids = self.encryption_service.get_user_encrypted_data("user456")
        assert storage_id in user_storage_ids
        
        # Delete user's encrypted data
        deleted_count = self.encryption_service.delete_user_encrypted_data("user456")
        assert deleted_count == 1
        
        # Verify data is deleted
        user_storage_ids_after = self.encryption_service.get_user_encrypted_data("user456")
        assert len(user_storage_ids_after) == 0

class TestEnhancedPrivacyFeatures:
    """Test enhanced privacy features"""
    
    def setup_method(self):
        """Set up test fixtures"""
        from src.security.privacy import get_privacy_manager
        self.privacy_manager = get_privacy_manager()
    
    def test_health_data_anonymization(self):
        """Test specialized health data anonymization"""
        health_data = {
            "patient_name": "Alice Johnson",
            "age": 35,
            "diagnosis": "diabetes",
            "weight": 65.5,
            "blood_pressure": "120/80",
            "email": "alice@example.com"
        }
        
        # Anonymize with medical accuracy preserved
        anonymized_data = self.privacy_manager.data_anonymizer.anonymize_health_data(
            health_data, preserve_medical_accuracy=True
        )
        
        # Personal identifiers should be anonymized
        assert anonymized_data["patient_name"] != "Alice Johnson"
        assert anonymized_data["email"] != "alice@example.com"
        
        # Medical data should be preserved for accuracy
        assert anonymized_data["diagnosis"] == "diabetes"
        
        # Numeric data should have noise added
        assert anonymized_data["weight"] != 65.5  # Should have noise
    
    def test_datetime_anonymization(self):
        """Test datetime anonymization"""
        from datetime import datetime
        
        test_datetime = datetime(2024, 1, 15, 14, 30, 0)
        
        # Test generalization (date only)
        from src.security.privacy import AnonymizationLevel
        anonymized_date = self.privacy_manager.data_anonymizer._anonymize_datetime(
            test_datetime, AnonymizationLevel.GENERALIZATION
        )
        
        assert anonymized_date == "2024-01-15"  # Should be date string only

class TestEnhancedConsentManagement:
    """Test enhanced consent management features"""
    
    def setup_method(self):
        """Set up test fixtures"""
        from src.security.consent import get_consent_manager
        self.consent_manager = get_consent_manager()
    
    def test_consent_preferences_update(self):
        """Test updating consent preferences"""
        from src.security.consent import ConsentType
        
        preferences = {
            ConsentType.DATA_PROCESSING: True,
            ConsentType.MARKETING: False,
            ConsentType.ANALYTICS: True
        }
        
        result = self.consent_manager.update_consent_preferences("user123", preferences)
        
        assert result["status"] == "success"
        assert len(result["updated_consents"]) == 3
        
        # Verify consents were updated
        assert self.consent_manager.check_consent("user123", ConsentType.DATA_PROCESSING)
        assert not self.consent_manager.check_consent("user123", ConsentType.MARKETING)
        assert self.consent_manager.check_consent("user123", ConsentType.ANALYTICS)
    
    def test_consent_dashboard(self):
        """Test consent dashboard functionality"""
        from src.security.consent import ConsentType
        
        # Grant some consents
        self.consent_manager.grant_consent(
            "user123", ConsentType.DATA_PROCESSING, "Data processing"
        )
        
        dashboard = self.consent_manager.get_consent_dashboard("user123")
        
        assert dashboard["user_id"] == "user123"
        assert "current_consents" in dashboard
        assert "recommendations" in dashboard
        assert "consent_health_score" in dashboard
    
    def test_consent_health_score(self):
        """Test consent health score calculation"""
        from src.security.consent import ConsentType
        
        # Grant required consents
        self.consent_manager.grant_consent(
            "user123", ConsentType.DATA_PROCESSING, "Data processing"
        )
        self.consent_manager.grant_consent(
            "user123", ConsentType.HEALTH_DATA, "Health data"
        )
        
        score = self.consent_manager._calculate_consent_health_score("user123")
        
        assert "score" in score
        assert "status" in score
        assert score["score"] >= 0
        assert score["score"] <= 100

class TestSecurityIntegrationEnhanced:
    """Enhanced integration tests for security system"""
    
    def test_end_to_end_secure_data_flow(self):
        """Test complete secure data flow with all security features"""
        from src.security import (
            get_encryption_service, get_privacy_manager, 
            get_consent_manager, get_data_protection_service
        )
        from src.security.transport_security import get_transport_security_manager
        from src.security.consent import ConsentType
        from src.security.privacy import DataCategory
        
        # Initialize all services
        encryption_service = get_encryption_service()
        privacy_manager = get_privacy_manager()
        consent_manager = get_consent_manager()
        data_protection_service = get_data_protection_service()
        transport_manager = get_transport_security_manager()
        
        user_id = "integration_test_user"
        
        # 1. Initialize transport security
        transport_result = transport_manager.initialize_https_security("test_cert")
        assert transport_result["initialized"]
        
        # 2. Grant required consents
        consent_manager.grant_consent(
            user_id, ConsentType.DATA_PROCESSING, "Data processing"
        )
        consent_manager.grant_consent(
            user_id, ConsentType.HEALTH_DATA, "Health data processing"
        )
        
        # 3. Process sensitive health data
        health_data = {
            "patient_name": "Test Patient",
            "age": 45,
            "diagnosis": "hypertension",
            "weight": 70.5,
            "email": "test@example.com"
        }
        
        # Process data securely
        processed_data = data_protection_service.process_data_securely(
            user_id, health_data, DataCategory.HEALTH_DATA, "health_assessment"
        )
        
        # 4. Encrypt processed data at rest
        storage_id = encryption_service.encrypt_data_at_rest(
            processed_data, "health_records", user_id
        )
        
        # 5. Verify data was processed securely
        assert processed_data["patient_name"] != "Test Patient"  # Should be anonymized
        assert processed_data["email"] != "test@example.com"  # Should be anonymized
        
        # 6. Verify data can be decrypted
        decrypted_data = encryption_service.decrypt_data_at_rest(storage_id)
        assert decrypted_data is not None
        
        # 7. Clean up - delete all user data
        deletion_result = data_protection_service.delete_user_data(user_id)
        assert deletion_result["status"] == "completed"
    
    def test_security_compliance_audit(self):
        """Test security compliance audit"""
        from src.security import get_data_protection_service
        
        data_protection_service = get_data_protection_service()
        
        # Perform audit
        audit_report = data_protection_service.audit_data_protection()
        
        assert "audit_timestamp" in audit_report
        assert "compliance_issues" in audit_report
        assert "encryption_usage_rate" in audit_report
        assert "consent_verification_rate" in audit_report
        
        # Audit should not have critical compliance issues in test environment
        assert isinstance(audit_report["compliance_issues"], list)

def test_security_system_initialization():
    """Test that all security components initialize correctly"""
    # Test that all services can be imported and initialized
    from src.security import (
        get_encryption_service, get_privacy_manager, 
        get_consent_manager, get_data_protection_service
    )
    from src.security.transport_security import get_transport_security_manager
    
    encryption_service = get_encryption_service()
    privacy_manager = get_privacy_manager()
    consent_manager = get_consent_manager()
    data_protection_service = get_data_protection_service()
    transport_manager = get_transport_security_manager()
    
    assert encryption_service is not None
    assert privacy_manager is not None
    assert consent_manager is not None
    assert data_protection_service is not None
    assert transport_manager is not None
    
    # Test status methods
    assert encryption_service.get_encryption_status()["total_keys"] >= 0
    assert privacy_manager.get_privacy_status()["total_privacy_rules"] >= 0
    assert consent_manager.get_consent_statistics()["total_users"] >= 0
    assert data_protection_service.get_protection_status()["protection_policies"]["total"] >= 0
    assert transport_manager.get_transport_security_status()["https"]["certificates"] >= 0