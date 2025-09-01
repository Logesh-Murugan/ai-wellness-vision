# encryption.py - Data encryption and decryption services
import os
import base64
import hashlib
import secrets
import json
from typing import Dict, Any, Optional, Union, Tuple, List
from datetime import datetime, timedelta
from dataclasses import dataclass, field
from enum import Enum

# Optional imports with fallbacks
try:
    from cryptography.fernet import Fernet
    from cryptography.hazmat.primitives import hashes, serialization
    from cryptography.hazmat.primitives.asymmetric import rsa, padding
    from cryptography.hazmat.primitives.kdf.pbkdf2 import PBKDF2HMAC
    from cryptography.hazmat.primitives.ciphers import Cipher, algorithms, modes
    CRYPTOGRAPHY_AVAILABLE = True
except ImportError:
    CRYPTOGRAPHY_AVAILABLE = False
    import logging
    logging.warning("Cryptography library not available - using mock encryption")

from src.utils.logging_config import get_structured_logger
from src.utils.error_handling import handle_error, ErrorCode, ErrorSeverity, ErrorContext

logger = get_structured_logger(__name__)

class EncryptionType(Enum):
    """Types of encryption"""
    SYMMETRIC = "symmetric"
    ASYMMETRIC = "asymmetric"
    HASH = "hash"

class KeyType(Enum):
    """Types of encryption keys"""
    AES_256 = "aes_256"
    RSA_2048 = "rsa_2048"
    RSA_4096 = "rsa_4096"

@dataclass
class EncryptionKey:
    """Encryption key information"""
    key_id: str
    key_type: KeyType
    created_at: datetime
    expires_at: Optional[datetime] = None
    is_active: bool = True
    metadata: Dict[str, Any] = field(default_factory=dict)

@dataclass
class EncryptedData:
    """Encrypted data container"""
    encrypted_content: bytes
    key_id: str
    encryption_type: EncryptionType
    iv: Optional[bytes] = None  # Initialization vector for symmetric encryption
    salt: Optional[bytes] = None  # Salt for key derivation
    metadata: Dict[str, Any] = field(default_factory=dict)
    created_at: datetime = field(default_factory=datetime.now)

class MockEncryption:
    """Mock encryption for when cryptography is not available"""
    
    @staticmethod
    def encrypt(data: bytes, key: bytes) -> bytes:
        """Mock encryption - just base64 encode"""
        return base64.b64encode(data)
    
    @staticmethod
    def decrypt(encrypted_data: bytes, key: bytes) -> bytes:
        """Mock decryption - just base64 decode"""
        return base64.b64decode(encrypted_data)
    
    @staticmethod
    def generate_key() -> bytes:
        """Generate mock key"""
        return b"mock_encryption_key_32_bytes_long"
    
    @staticmethod
    def hash_data(data: bytes) -> bytes:
        """Hash data using SHA-256"""
        return hashlib.sha256(data).digest()

class SymmetricEncryption:
    """Symmetric encryption using AES"""
    
    def __init__(self):
        self.key_size = 32  # 256 bits
        self.iv_size = 16   # 128 bits
    
    def generate_key(self) -> bytes:
        """Generate a new AES key"""
        if CRYPTOGRAPHY_AVAILABLE:
            return Fernet.generate_key()
        else:
            return MockEncryption.generate_key()
    
    def encrypt(self, data: Union[str, bytes], key: bytes, 
                associated_data: Optional[bytes] = None) -> EncryptedData:
        """Encrypt data using AES"""
        try:
            if isinstance(data, str):
                data = data.encode('utf-8')
            
            if CRYPTOGRAPHY_AVAILABLE:
                # Use Fernet for simplicity (includes authentication)
                fernet = Fernet(key)
                encrypted_content = fernet.encrypt(data)
                
                return EncryptedData(
                    encrypted_content=encrypted_content,
                    key_id="symmetric_key",
                    encryption_type=EncryptionType.SYMMETRIC,
                    metadata={"algorithm": "AES-256", "mode": "Fernet"}
                )
            else:
                # Mock encryption
                encrypted_content = MockEncryption.encrypt(data, key)
                return EncryptedData(
                    encrypted_content=encrypted_content,
                    key_id="mock_key",
                    encryption_type=EncryptionType.SYMMETRIC,
                    metadata={"algorithm": "mock"}
                )
                
        except Exception as e:
            logger.error(f"Symmetric encryption failed: {e}")
            handle_error(
                ErrorCode.ENCRYPTION_ERROR,
                f"Failed to encrypt data: {str(e)}",
                ErrorSeverity.HIGH,
                ErrorContext(service_name="encryption_service", function_name="encrypt")
            )
            raise
    
    def decrypt(self, encrypted_data: EncryptedData, key: bytes) -> bytes:
        """Decrypt data using AES"""
        try:
            if CRYPTOGRAPHY_AVAILABLE:
                fernet = Fernet(key)
                decrypted_data = fernet.decrypt(encrypted_data.encrypted_content)
                return decrypted_data
            else:
                # Mock decryption
                return MockEncryption.decrypt(encrypted_data.encrypted_content, key)
                
        except Exception as e:
            logger.error(f"Symmetric decryption failed: {e}")
            handle_error(
                ErrorCode.DECRYPTION_ERROR,
                f"Failed to decrypt data: {str(e)}",
                ErrorSeverity.HIGH,
                ErrorContext(service_name="encryption_service", function_name="decrypt")
            )
            raise

class AsymmetricEncryption:
    """Asymmetric encryption using RSA"""
    
    def __init__(self):
        self.key_size = 2048  # Default RSA key size
    
    def generate_key_pair(self, key_size: int = 2048) -> Tuple[bytes, bytes]:
        """Generate RSA key pair"""
        try:
            if CRYPTOGRAPHY_AVAILABLE:
                private_key = rsa.generate_private_key(
                    public_exponent=65537,
                    key_size=key_size
                )
                
                private_pem = private_key.private_bytes(
                    encoding=serialization.Encoding.PEM,
                    format=serialization.PrivateFormat.PKCS8,
                    encryption_algorithm=serialization.NoEncryption()
                )
                
                public_key = private_key.public_key()
                public_pem = public_key.public_bytes(
                    encoding=serialization.Encoding.PEM,
                    format=serialization.PublicFormat.SubjectPublicKeyInfo
                )
                
                return private_pem, public_pem
            else:
                # Mock key pair
                private_key = b"mock_private_key"
                public_key = b"mock_public_key"
                return private_key, public_key
                
        except Exception as e:
            logger.error(f"Key pair generation failed: {e}")
            handle_error(
                ErrorCode.ENCRYPTION_ERROR,
                f"Failed to generate key pair: {str(e)}",
                ErrorSeverity.HIGH,
                ErrorContext(service_name="encryption_service", function_name="generate_key_pair")
            )
            raise
    
    def encrypt(self, data: Union[str, bytes], public_key: bytes) -> EncryptedData:
        """Encrypt data using RSA public key"""
        try:
            if isinstance(data, str):
                data = data.encode('utf-8')
            
            if CRYPTOGRAPHY_AVAILABLE:
                public_key_obj = serialization.load_pem_public_key(public_key)
                
                encrypted_content = public_key_obj.encrypt(
                    data,
                    padding.OAEP(
                        mgf=padding.MGF1(algorithm=hashes.SHA256()),
                        algorithm=hashes.SHA256(),
                        label=None
                    )
                )
                
                return EncryptedData(
                    encrypted_content=encrypted_content,
                    key_id="rsa_public_key",
                    encryption_type=EncryptionType.ASYMMETRIC,
                    metadata={"algorithm": "RSA-OAEP", "key_size": self.key_size}
                )
            else:
                # Mock encryption
                encrypted_content = MockEncryption.encrypt(data, public_key)
                return EncryptedData(
                    encrypted_content=encrypted_content,
                    key_id="mock_rsa_key",
                    encryption_type=EncryptionType.ASYMMETRIC,
                    metadata={"algorithm": "mock_rsa"}
                )
                
        except Exception as e:
            logger.error(f"Asymmetric encryption failed: {e}")
            handle_error(
                ErrorCode.ENCRYPTION_ERROR,
                f"Failed to encrypt data with RSA: {str(e)}",
                ErrorSeverity.HIGH,
                ErrorContext(service_name="encryption_service", function_name="encrypt_rsa")
            )
            raise
    
    def decrypt(self, encrypted_data: EncryptedData, private_key: bytes) -> bytes:
        """Decrypt data using RSA private key"""
        try:
            if CRYPTOGRAPHY_AVAILABLE:
                private_key_obj = serialization.load_pem_private_key(
                    private_key, password=None
                )
                
                decrypted_data = private_key_obj.decrypt(
                    encrypted_data.encrypted_content,
                    padding.OAEP(
                        mgf=padding.MGF1(algorithm=hashes.SHA256()),
                        algorithm=hashes.SHA256(),
                        label=None
                    )
                )
                
                return decrypted_data
            else:
                # Mock decryption
                return MockEncryption.decrypt(encrypted_data.encrypted_content, private_key)
                
        except Exception as e:
            logger.error(f"Asymmetric decryption failed: {e}")
            handle_error(
                ErrorCode.DECRYPTION_ERROR,
                f"Failed to decrypt data with RSA: {str(e)}",
                ErrorSeverity.HIGH,
                ErrorContext(service_name="encryption_service", function_name="decrypt_rsa")
            )
            raise

class HashingService:
    """Data hashing and verification service"""
    
    def __init__(self):
        self.default_algorithm = "SHA-256"
    
    def hash_data(self, data: Union[str, bytes], salt: Optional[bytes] = None) -> Tuple[bytes, bytes]:
        """Hash data with optional salt"""
        try:
            if isinstance(data, str):
                data = data.encode('utf-8')
            
            if salt is None:
                salt = secrets.token_bytes(32)  # 256-bit salt
            
            if CRYPTOGRAPHY_AVAILABLE:
                digest = hashes.Hash(hashes.SHA256())
                digest.update(salt + data)
                hash_value = digest.finalize()
            else:
                # Fallback to hashlib
                hash_value = hashlib.sha256(salt + data).digest()
            
            return hash_value, salt
            
        except Exception as e:
            logger.error(f"Data hashing failed: {e}")
            handle_error(
                ErrorCode.ENCRYPTION_ERROR,
                f"Failed to hash data: {str(e)}",
                ErrorSeverity.MEDIUM,
                ErrorContext(service_name="encryption_service", function_name="hash_data")
            )
            raise
    
    def verify_hash(self, data: Union[str, bytes], hash_value: bytes, salt: bytes) -> bool:
        """Verify data against hash"""
        try:
            computed_hash, _ = self.hash_data(data, salt)
            return secrets.compare_digest(computed_hash, hash_value)
            
        except Exception as e:
            logger.error(f"Hash verification failed: {e}")
            return False
    
    def hash_password(self, password: str, salt: Optional[bytes] = None) -> Tuple[bytes, bytes]:
        """Hash password using PBKDF2"""
        try:
            if salt is None:
                salt = secrets.token_bytes(32)
            
            if CRYPTOGRAPHY_AVAILABLE:
                kdf = PBKDF2HMAC(
                    algorithm=hashes.SHA256(),
                    length=32,
                    salt=salt,
                    iterations=100000,  # OWASP recommended minimum
                )
                hash_value = kdf.derive(password.encode('utf-8'))
            else:
                # Fallback using hashlib
                hash_value = hashlib.pbkdf2_hmac('sha256', password.encode('utf-8'), salt, 100000)
            
            return hash_value, salt
            
        except Exception as e:
            logger.error(f"Password hashing failed: {e}")
            handle_error(
                ErrorCode.ENCRYPTION_ERROR,
                f"Failed to hash password: {str(e)}",
                ErrorSeverity.HIGH,
                ErrorContext(service_name="encryption_service", function_name="hash_password")
            )
            raise

class KeyManager:
    """Encryption key management service"""
    
    def __init__(self):
        self.keys: Dict[str, EncryptionKey] = {}
        self.key_storage: Dict[str, bytes] = {}
        self.symmetric_encryption = SymmetricEncryption()
        self.asymmetric_encryption = AsymmetricEncryption()
    
    def generate_symmetric_key(self, key_id: str, expires_in_days: Optional[int] = None) -> EncryptionKey:
        """Generate and store a symmetric encryption key"""
        try:
            key_bytes = self.symmetric_encryption.generate_key()
            
            expires_at = None
            if expires_in_days:
                expires_at = datetime.now() + timedelta(days=expires_in_days)
            
            encryption_key = EncryptionKey(
                key_id=key_id,
                key_type=KeyType.AES_256,
                created_at=datetime.now(),
                expires_at=expires_at,
                metadata={"algorithm": "AES-256", "mode": "Fernet"}
            )
            
            self.keys[key_id] = encryption_key
            self.key_storage[key_id] = key_bytes
            
            logger.info(f"Generated symmetric key: {key_id}")
            return encryption_key
            
        except Exception as e:
            logger.error(f"Symmetric key generation failed: {e}")
            handle_error(
                ErrorCode.ENCRYPTION_ERROR,
                f"Failed to generate symmetric key: {str(e)}",
                ErrorSeverity.HIGH,
                ErrorContext(service_name="key_manager", function_name="generate_symmetric_key")
            )
            raise
    
    def generate_asymmetric_key_pair(self, key_id: str, key_size: int = 2048,
                                   expires_in_days: Optional[int] = None) -> EncryptionKey:
        """Generate and store an asymmetric key pair"""
        try:
            private_key, public_key = self.asymmetric_encryption.generate_key_pair(key_size)
            
            expires_at = None
            if expires_in_days:
                expires_at = datetime.now() + timedelta(days=expires_in_days)
            
            key_type = KeyType.RSA_2048 if key_size == 2048 else KeyType.RSA_4096
            
            encryption_key = EncryptionKey(
                key_id=key_id,
                key_type=key_type,
                created_at=datetime.now(),
                expires_at=expires_at,
                metadata={"algorithm": "RSA", "key_size": key_size}
            )
            
            self.keys[key_id] = encryption_key
            self.key_storage[f"{key_id}_private"] = private_key
            self.key_storage[f"{key_id}_public"] = public_key
            
            logger.info(f"Generated asymmetric key pair: {key_id}")
            return encryption_key
            
        except Exception as e:
            logger.error(f"Asymmetric key generation failed: {e}")
            handle_error(
                ErrorCode.ENCRYPTION_ERROR,
                f"Failed to generate asymmetric key pair: {str(e)}",
                ErrorSeverity.HIGH,
                ErrorContext(service_name="key_manager", function_name="generate_asymmetric_key_pair")
            )
            raise
    
    def get_key(self, key_id: str) -> Optional[bytes]:
        """Retrieve encryption key"""
        return self.key_storage.get(key_id)
    
    def get_key_info(self, key_id: str) -> Optional[EncryptionKey]:
        """Get key information"""
        return self.keys.get(key_id)
    
    def is_key_valid(self, key_id: str) -> bool:
        """Check if key is valid and not expired"""
        key_info = self.keys.get(key_id)
        if not key_info or not key_info.is_active:
            return False
        
        if key_info.expires_at and datetime.now() > key_info.expires_at:
            return False
        
        return True
    
    def rotate_key(self, key_id: str) -> EncryptionKey:
        """Rotate an existing key"""
        try:
            old_key = self.keys.get(key_id)
            if not old_key:
                raise ValueError(f"Key {key_id} not found")
            
            # Deactivate old key
            old_key.is_active = False
            
            # Generate new key with same parameters
            if old_key.key_type == KeyType.AES_256:
                return self.generate_symmetric_key(f"{key_id}_rotated")
            else:
                key_size = 2048 if old_key.key_type == KeyType.RSA_2048 else 4096
                return self.generate_asymmetric_key_pair(f"{key_id}_rotated", key_size)
                
        except Exception as e:
            logger.error(f"Key rotation failed: {e}")
            handle_error(
                ErrorCode.ENCRYPTION_ERROR,
                f"Failed to rotate key: {str(e)}",
                ErrorSeverity.HIGH,
                ErrorContext(service_name="key_manager", function_name="rotate_key")
            )
            raise
    
    def cleanup_expired_keys(self) -> int:
        """Remove expired keys"""
        expired_count = 0
        current_time = datetime.now()
        
        expired_keys = [
            key_id for key_id, key_info in self.keys.items()
            if key_info.expires_at and current_time > key_info.expires_at
        ]
        
        for key_id in expired_keys:
            del self.keys[key_id]
            # Remove associated key data
            for storage_key in list(self.key_storage.keys()):
                if storage_key.startswith(key_id):
                    del self.key_storage[storage_key]
            expired_count += 1
        
        if expired_count > 0:
            logger.info(f"Cleaned up {expired_count} expired keys")
        
        return expired_count

class EncryptionService:
    """Main encryption service that coordinates all encryption operations"""
    
    def __init__(self):
        self.key_manager = KeyManager()
        self.symmetric_encryption = SymmetricEncryption()
        self.asymmetric_encryption = AsymmetricEncryption()
        self.hashing_service = HashingService()
        
        # Data at rest encryption
        self.data_at_rest_keys = {}
        self.encrypted_storage = {}
        
        # Initialize default keys
        self._initialize_default_keys()
    
    def _initialize_default_keys(self):
        """Initialize default encryption keys"""
        try:
            # Generate default symmetric key for general use
            self.key_manager.generate_symmetric_key("default_symmetric", expires_in_days=365)
            
            # Generate default asymmetric key pair
            self.key_manager.generate_asymmetric_key_pair("default_asymmetric", expires_in_days=365)
            
            logger.info("Default encryption keys initialized")
            
        except Exception as e:
            logger.error(f"Failed to initialize default keys: {e}")
    
    def encrypt_data(self, data: Union[str, bytes], key_id: Optional[str] = None,
                    encryption_type: EncryptionType = EncryptionType.SYMMETRIC) -> EncryptedData:
        """Encrypt data using specified encryption type"""
        try:
            if key_id is None:
                key_id = "default_symmetric" if encryption_type == EncryptionType.SYMMETRIC else "default_asymmetric"
            
            if encryption_type == EncryptionType.SYMMETRIC:
                key = self.key_manager.get_key(key_id)
                if not key:
                    raise ValueError(f"Symmetric key {key_id} not found")
                
                encrypted_data = self.symmetric_encryption.encrypt(data, key)
                encrypted_data.key_id = key_id
                return encrypted_data
                
            elif encryption_type == EncryptionType.ASYMMETRIC:
                public_key = self.key_manager.get_key(f"{key_id}_public")
                if not public_key:
                    raise ValueError(f"Public key {key_id}_public not found")
                
                encrypted_data = self.asymmetric_encryption.encrypt(data, public_key)
                encrypted_data.key_id = key_id
                return encrypted_data
                
            else:
                raise ValueError(f"Unsupported encryption type: {encryption_type}")
                
        except Exception as e:
            logger.error(f"Data encryption failed: {e}")
            handle_error(
                ErrorCode.ENCRYPTION_ERROR,
                f"Failed to encrypt data: {str(e)}",
                ErrorSeverity.HIGH,
                ErrorContext(service_name="encryption_service", function_name="encrypt_data")
            )
            raise
    
    def decrypt_data(self, encrypted_data: EncryptedData) -> bytes:
        """Decrypt data using the appropriate key"""
        try:
            if encrypted_data.encryption_type == EncryptionType.SYMMETRIC:
                key = self.key_manager.get_key(encrypted_data.key_id)
                if not key:
                    raise ValueError(f"Symmetric key {encrypted_data.key_id} not found")
                
                return self.symmetric_encryption.decrypt(encrypted_data, key)
                
            elif encrypted_data.encryption_type == EncryptionType.ASYMMETRIC:
                private_key = self.key_manager.get_key(f"{encrypted_data.key_id}_private")
                if not private_key:
                    raise ValueError(f"Private key {encrypted_data.key_id}_private not found")
                
                return self.asymmetric_encryption.decrypt(encrypted_data, private_key)
                
            else:
                raise ValueError(f"Unsupported encryption type: {encrypted_data.encryption_type}")
                
        except Exception as e:
            logger.error(f"Data decryption failed: {e}")
            handle_error(
                ErrorCode.DECRYPTION_ERROR,
                f"Failed to decrypt data: {str(e)}",
                ErrorSeverity.HIGH,
                ErrorContext(service_name="encryption_service", function_name="decrypt_data")
            )
            raise
    
    def hash_data(self, data: Union[str, bytes], salt: Optional[bytes] = None) -> Tuple[bytes, bytes]:
        """Hash data with optional salt"""
        return self.hashing_service.hash_data(data, salt)
    
    def verify_hash(self, data: Union[str, bytes], hash_value: bytes, salt: bytes) -> bool:
        """Verify data against hash"""
        return self.hashing_service.verify_hash(data, hash_value, salt)
    
    def hash_password(self, password: str, salt: Optional[bytes] = None) -> Tuple[bytes, bytes]:
        """Hash password using PBKDF2"""
        return self.hashing_service.hash_password(password, salt)
    
    def generate_secure_token(self, length: int = 32) -> str:
        """Generate a secure random token"""
        return secrets.token_urlsafe(length)
    
    def encrypt_data_at_rest(self, data: Union[str, bytes, Dict[str, Any]], 
                            storage_key: str, user_id: Optional[str] = None) -> str:
        """Encrypt data for storage at rest"""
        try:
            # Convert data to JSON string if it's a dict
            if isinstance(data, dict):
                data = json.dumps(data)
            
            # Generate or get storage-specific key
            if storage_key not in self.data_at_rest_keys:
                self.data_at_rest_keys[storage_key] = self.key_manager.generate_symmetric_key(
                    f"storage_{storage_key}", expires_in_days=365
                )
            
            # Encrypt the data
            encrypted_data = self.encrypt_data(data, f"storage_{storage_key}")
            
            # Store encrypted data with metadata
            storage_id = f"{storage_key}_{secrets.token_urlsafe(16)}"
            self.encrypted_storage[storage_id] = {
                "encrypted_data": encrypted_data,
                "user_id": user_id,
                "created_at": datetime.now(),
                "storage_key": storage_key
            }
            
            logger.info(f"Encrypted data at rest for storage key: {storage_key}")
            return storage_id
            
        except Exception as e:
            logger.error(f"Data at rest encryption failed: {e}")
            handle_error(
                ErrorCode.ENCRYPTION_ERROR,
                f"Failed to encrypt data at rest: {str(e)}",
                ErrorSeverity.HIGH,
                ErrorContext(service_name="encryption_service", function_name="encrypt_data_at_rest")
            )
            raise
    
    def decrypt_data_at_rest(self, storage_id: str) -> Union[str, Dict[str, Any]]:
        """Decrypt data from storage at rest"""
        try:
            if storage_id not in self.encrypted_storage:
                raise ValueError(f"Storage ID {storage_id} not found")
            
            storage_record = self.encrypted_storage[storage_id]
            encrypted_data = storage_record["encrypted_data"]
            
            # Decrypt the data
            decrypted_bytes = self.decrypt_data(encrypted_data)
            decrypted_str = decrypted_bytes.decode('utf-8')
            
            # Try to parse as JSON, return as string if it fails
            try:
                return json.loads(decrypted_str)
            except json.JSONDecodeError:
                return decrypted_str
                
        except Exception as e:
            logger.error(f"Data at rest decryption failed: {e}")
            handle_error(
                ErrorCode.DECRYPTION_ERROR,
                f"Failed to decrypt data at rest: {str(e)}",
                ErrorSeverity.HIGH,
                ErrorContext(service_name="encryption_service", function_name="decrypt_data_at_rest")
            )
            raise
    
    def delete_encrypted_data_at_rest(self, storage_id: str) -> bool:
        """Securely delete encrypted data at rest"""
        try:
            if storage_id in self.encrypted_storage:
                del self.encrypted_storage[storage_id]
                logger.info(f"Deleted encrypted data at rest: {storage_id}")
                return True
            return False
            
        except Exception as e:
            logger.error(f"Failed to delete encrypted data at rest: {e}")
            return False
    
    def cleanup_expired_storage(self) -> int:
        """Clean up expired encrypted storage"""
        try:
            current_time = datetime.now()
            expired_storage = []
            
            for storage_id, record in self.encrypted_storage.items():
                # Remove data older than 1 year by default
                if (current_time - record["created_at"]).days > 365:
                    expired_storage.append(storage_id)
            
            for storage_id in expired_storage:
                del self.encrypted_storage[storage_id]
            
            if expired_storage:
                logger.info(f"Cleaned up {len(expired_storage)} expired storage records")
            
            return len(expired_storage)
            
        except Exception as e:
            logger.error(f"Storage cleanup failed: {e}")
            return 0
    
    def get_user_encrypted_data(self, user_id: str) -> List[str]:
        """Get all encrypted data storage IDs for a user"""
        return [
            storage_id for storage_id, record in self.encrypted_storage.items()
            if record.get("user_id") == user_id
        ]
    
    def delete_user_encrypted_data(self, user_id: str) -> int:
        """Delete all encrypted data for a user"""
        user_storage_ids = self.get_user_encrypted_data(user_id)
        deleted_count = 0
        
        for storage_id in user_storage_ids:
            if self.delete_encrypted_data_at_rest(storage_id):
                deleted_count += 1
        
        logger.info(f"Deleted {deleted_count} encrypted storage records for user {user_id}")
        return deleted_count

    def get_encryption_status(self) -> Dict[str, Any]:
        """Get encryption service status"""
        return {
            "cryptography_available": CRYPTOGRAPHY_AVAILABLE,
            "total_keys": len(self.key_manager.keys),
            "active_keys": sum(1 for key in self.key_manager.keys.values() if key.is_active),
            "key_types": {
                key_type.value: sum(1 for key in self.key_manager.keys.values() 
                                  if key.key_type == key_type)
                for key_type in KeyType
            },
            "default_keys_available": {
                "symmetric": self.key_manager.get_key("default_symmetric") is not None,
                "asymmetric": self.key_manager.get_key("default_asymmetric_public") is not None
            },
            "data_at_rest": {
                "storage_keys": len(self.data_at_rest_keys),
                "encrypted_records": len(self.encrypted_storage),
                "total_storage_size": sum(
                    len(str(record["encrypted_data"].encrypted_content)) 
                    for record in self.encrypted_storage.values()
                )
            }
        }

# Global encryption service instance
encryption_service = EncryptionService()

def get_encryption_service() -> EncryptionService:
    """Get global encryption service instance"""
    return encryption_service