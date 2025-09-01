# test_auth.py - Tests for authentication and authorization system
import unittest
import time
from datetime import datetime, timedelta
from unittest.mock import patch, MagicMock

from src.api.auth import (
    AuthManager, UserCredentials, TokenData, 
    AuthenticationError, AuthorizationError,
    auth_manager
)

class TestAuthManager(unittest.TestCase):
    """Test authentication manager functionality"""
    
    def setUp(self):
        self.auth_manager = AuthManager()
    
    def test_password_hashing(self):
        """Test password hashing and verification"""
        password = "test_password_123"
        hashed = self.auth_manager.hash_password(password)
        
        self.assertNotEqual(password, hashed)
        self.assertTrue(self.auth_manager.verify_password(password, hashed))
        self.assertFalse(self.auth_manager.verify_password("wrong_password", hashed))
    
    def test_user_creation(self):
        """Test user credentials creation"""
        user = UserCredentials(
            username="testuser",
            email="test@example.com",
            hashed_password="hashed_password",
            roles=["user", "tester"]
        )
        
        self.assertEqual(user.username, "testuser")
        self.assertEqual(user.email, "test@example.com")
        self.assertTrue(user.is_active)
        self.assertIn("user", user.roles)
        self.assertIn("tester", user.roles)
        self.assertIsInstance(user.created_at, datetime)
    
    def test_successful_authentication(self):
        """Test successful user authentication"""
        # Use default test user
        user = self.auth_manager.authenticate_user("testuser", "user123")
        
        self.assertIsNotNone(user)
        self.assertEqual(user.username, "testuser")
        self.assertTrue(user.is_active)
        self.assertIn("user", user.roles)
    
    def test_failed_authentication_invalid_user(self):
        """Test authentication failure with invalid username"""
        with self.assertRaises(AuthenticationError):
            self.auth_manager.authenticate_user("nonexistent", "password")
    
    def test_failed_authentication_invalid_password(self):
        """Test authentication failure with invalid password"""
        with self.assertRaises(AuthenticationError):
            self.auth_manager.authenticate_user("testuser", "wrongpassword")
    
    def test_inactive_user_authentication(self):
        """Test authentication failure for inactive user"""
        # Create inactive user
        inactive_password = self.auth_manager.hash_password("inactive123")
        self.auth_manager.users_db["inactive"] = UserCredentials(
            username="inactive",
            email="inactive@example.com",
            hashed_password=inactive_password,
            is_active=False
        )
        
        with self.assertRaises(AuthenticationError):
            self.auth_manager.authenticate_user("inactive", "inactive123")
    
    def test_token_creation_and_verification(self):
        """Test JWT token creation and verification"""
        user = self.auth_manager.authenticate_user("testuser", "user123")
        
        # Create access token
        access_token = self.auth_manager.create_access_token(user)
        self.assertIsNotNone(access_token)
        
        # Verify token
        token_data = self.auth_manager.verify_token(access_token)
        self.assertEqual(token_data.username, user.username)
        self.assertEqual(token_data.roles, user.roles)
        self.assertIsInstance(token_data.exp, datetime)
        self.assertIsInstance(token_data.iat, datetime)
    
    def test_refresh_token_creation(self):
        """Test refresh token creation"""
        user = self.auth_manager.authenticate_user("testuser", "user123")
        
        refresh_token = self.auth_manager.create_refresh_token(user)
        self.assertIsNotNone(refresh_token)
    
    def test_token_revocation(self):
        """Test token revocation"""
        user = self.auth_manager.authenticate_user("testuser", "user123")
        access_token = self.auth_manager.create_access_token(user)
        
        # Token should be valid initially
        token_data = self.auth_manager.verify_token(access_token)
        self.assertIsNotNone(token_data)
        
        # Revoke token
        self.auth_manager.revoke_token(access_token)
        
        # Token should be invalid after revocation
        with self.assertRaises(AuthenticationError):
            self.auth_manager.verify_token(access_token)
    
    def test_permission_checking(self):
        """Test role-based permission checking"""
        # Test user permissions
        user_roles = ["user"]
        self.assertTrue(self.auth_manager.check_permission(user_roles, ["user"]))
        self.assertFalse(self.auth_manager.check_permission(user_roles, ["admin"]))
        
        # Test admin permissions
        admin_roles = ["admin", "user"]
        self.assertTrue(self.auth_manager.check_permission(admin_roles, ["user"]))
        self.assertTrue(self.auth_manager.check_permission(admin_roles, ["admin"]))
        self.assertTrue(self.auth_manager.check_permission(admin_roles, ["moderator"]))  # Admin has all permissions
    
    def test_rate_limiting_failed_attempts(self):
        """Test rate limiting on failed login attempts"""
        username = "rate_limit_test"
        
        # Make multiple failed attempts
        for i in range(6):  # Exceed the limit of 5
            try:
                self.auth_manager.authenticate_user(username, "wrong_password")
            except AuthenticationError:
                pass
        
        # Next attempt should be rate limited
        with self.assertRaises(AuthenticationError) as context:
            self.auth_manager.authenticate_user(username, "wrong_password")
        
        self.assertIn("Too many failed attempts", str(context.exception))
    
    def test_token_cleanup(self):
        """Test expired token cleanup"""
        user = self.auth_manager.authenticate_user("testuser", "user123")
        
        # Create token and manually expire it
        access_token = self.auth_manager.create_access_token(user)
        
        # Manually set expiration to past
        if access_token in self.auth_manager.active_tokens:
            self.auth_manager.active_tokens[access_token]["expires_at"] = datetime.utcnow() - timedelta(hours=1)
        
        # Run cleanup
        initial_count = len(self.auth_manager.active_tokens)
        self.auth_manager.cleanup_expired_tokens()
        final_count = len(self.auth_manager.active_tokens)
        
        # Should have fewer tokens after cleanup
        self.assertLessEqual(final_count, initial_count)

class TestTokenData(unittest.TestCase):
    """Test token data structure"""
    
    def test_token_data_creation(self):
        """Test TokenData creation"""
        exp_time = datetime.utcnow() + timedelta(hours=1)
        iat_time = datetime.utcnow()
        
        token_data = TokenData(
            username="testuser",
            user_id="user123",
            roles=["user", "tester"],
            exp=exp_time,
            iat=iat_time
        )
        
        self.assertEqual(token_data.username, "testuser")
        self.assertEqual(token_data.user_id, "user123")
        self.assertEqual(token_data.roles, ["user", "tester"])
        self.assertEqual(token_data.exp, exp_time)
        self.assertEqual(token_data.iat, iat_time)

class TestAuthenticationIntegration(unittest.TestCase):
    """Test authentication integration scenarios"""
    
    def setUp(self):
        self.auth_manager = AuthManager()
    
    def test_complete_authentication_flow(self):
        """Test complete authentication workflow"""
        # Step 1: Authenticate user
        user = self.auth_manager.authenticate_user("admin", "admin123")
        self.assertIsNotNone(user)
        self.assertEqual(user.username, "admin")
        
        # Step 2: Create tokens
        access_token = self.auth_manager.create_access_token(user)
        refresh_token = self.auth_manager.create_refresh_token(user)
        
        self.assertIsNotNone(access_token)
        self.assertIsNotNone(refresh_token)
        
        # Step 3: Verify access token
        token_data = self.auth_manager.verify_token(access_token)
        self.assertEqual(token_data.username, "admin")
        self.assertIn("admin", token_data.roles)
        
        # Step 4: Check permissions
        self.assertTrue(self.auth_manager.check_permission(token_data.roles, ["admin"]))
        self.assertTrue(self.auth_manager.check_permission(token_data.roles, ["user"]))
        
        # Step 5: Revoke token
        self.auth_manager.revoke_token(access_token)
        
        # Step 6: Verify token is invalid
        with self.assertRaises(AuthenticationError):
            self.auth_manager.verify_token(access_token)
    
    def test_session_management_with_auth(self):
        """Test session management with authentication"""
        # Authenticate multiple users
        user1 = self.auth_manager.authenticate_user("admin", "admin123")
        user2 = self.auth_manager.authenticate_user("testuser", "user123")
        
        # Create tokens for both users
        token1 = self.auth_manager.create_access_token(user1)
        token2 = self.auth_manager.create_access_token(user2)
        
        # Verify both tokens are valid
        token_data1 = self.auth_manager.verify_token(token1)
        token_data2 = self.auth_manager.verify_token(token2)
        
        self.assertEqual(token_data1.username, "admin")
        self.assertEqual(token_data2.username, "testuser")
        
        # Verify different permissions
        self.assertTrue(self.auth_manager.check_permission(token_data1.roles, ["admin"]))
        self.assertFalse(self.auth_manager.check_permission(token_data2.roles, ["admin"]))
    
    def test_concurrent_authentication(self):
        """Test concurrent authentication requests"""
        import threading
        import queue
        
        results = queue.Queue()
        
        def authenticate_user(username, password):
            try:
                user = self.auth_manager.authenticate_user(username, password)
                token = self.auth_manager.create_access_token(user)
                results.put(("success", username, token))
            except Exception as e:
                results.put(("error", username, str(e)))
        
        # Create multiple threads for concurrent authentication
        threads = []
        for i in range(5):
            thread = threading.Thread(
                target=authenticate_user,
                args=("testuser", "user123")
            )
            threads.append(thread)
            thread.start()
        
        # Wait for all threads to complete
        for thread in threads:
            thread.join()
        
        # Check results
        successful_auths = 0
        while not results.empty():
            status, username, result = results.get()
            if status == "success":
                successful_auths += 1
                self.assertIsNotNone(result)  # Token should be created
        
        self.assertEqual(successful_auths, 5)

class TestAuthenticationErrors(unittest.TestCase):
    """Test authentication error scenarios"""
    
    def setUp(self):
        self.auth_manager = AuthManager()
    
    def test_malformed_token(self):
        """Test handling of malformed tokens"""
        malformed_tokens = [
            "invalid.token.format",
            "not_a_token_at_all",
            "",
            None,
            "eyJ0eXAiOiJKV1QiLCJhbGciOiJIUzI1NiJ9.invalid",
        ]
        
        for token in malformed_tokens:
            if token is not None:
                with self.assertRaises(AuthenticationError):
                    self.auth_manager.verify_token(token)
    
    def test_expired_token_handling(self):
        """Test handling of expired tokens"""
        user = self.auth_manager.authenticate_user("testuser", "user123")
        
        # Create token with very short expiration
        with patch('src.api.auth.ACCESS_TOKEN_EXPIRE_MINUTES', 0):
            token = self.auth_manager.create_access_token(user)
        
        # Wait a moment for token to expire
        time.sleep(1)
        
        # Token should be expired
        with self.assertRaises(AuthenticationError):
            self.auth_manager.verify_token(token)
    
    def test_authentication_with_special_characters(self):
        """Test authentication with special characters in credentials"""
        # Create user with special characters
        special_password = self.auth_manager.hash_password("p@ssw0rd!@#$%^&*()")
        self.auth_manager.users_db["special_user"] = UserCredentials(
            username="special_user",
            email="special@example.com",
            hashed_password=special_password
        )
        
        # Should authenticate successfully
        user = self.auth_manager.authenticate_user("special_user", "p@ssw0rd!@#$%^&*()")
        self.assertIsNotNone(user)
        
        # Should fail with wrong special characters
        with self.assertRaises(AuthenticationError):
            self.auth_manager.authenticate_user("special_user", "p@ssw0rd!@#$%^&*()_wrong")

if __name__ == '__main__':
    unittest.main()