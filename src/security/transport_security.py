# transport_security.py - HTTPS and WebSocket security implementation
import ssl
import socket
import secrets
import hashlib
from typing import Dict, Any, Optional, List, Tuple
from datetime import datetime, timedelta
from dataclasses import dataclass, field
from enum import Enum
import base64

from src.utils.logging_config import get_structured_logger
from src.utils.error_handling import handle_error, ErrorCode, ErrorSeverity, ErrorContext

logger = get_structured_logger(__name__)

class TLSVersion(Enum):
    """Supported TLS versions"""
    TLS_1_2 = "TLSv1.2"
    TLS_1_3 = "TLSv1.3"

class CipherSuite(Enum):
    """Recommended cipher suites"""
    ECDHE_RSA_AES256_GCM_SHA384 = "ECDHE-RSA-AES256-GCM-SHA384"
    ECDHE_RSA_AES128_GCM_SHA256 = "ECDHE-RSA-AES128-GCM-SHA256"
    ECDHE_RSA_CHACHA20_POLY1305 = "ECDHE-RSA-CHACHA20-POLY1305"

@dataclass
class TLSConfiguration:
    """TLS configuration settings"""
    min_version: TLSVersion = TLSVersion.TLS_1_2
    max_version: TLSVersion = TLSVersion.TLS_1_3
    cipher_suites: List[CipherSuite] = field(default_factory=lambda: [
        CipherSuite.ECDHE_RSA_AES256_GCM_SHA384,
        CipherSuite.ECDHE_RSA_AES128_GCM_SHA256,
        CipherSuite.ECDHE_RSA_CHACHA20_POLY1305
    ])
    require_client_cert: bool = False
    verify_hostname: bool = True
    check_hostname: bool = True

@dataclass
class WebSocketSecurityConfig:
    """WebSocket security configuration"""
    require_origin_check: bool = True
    allowed_origins: List[str] = field(default_factory=list)
    max_message_size: int = 1024 * 1024  # 1MB
    max_connections_per_ip: int = 10
    connection_timeout: int = 300  # 5 minutes
    heartbeat_interval: int = 30  # 30 seconds

@dataclass
class SecurityCertificate:
    """Security certificate information"""
    cert_path: str
    key_path: str
    ca_path: Optional[str] = None
    created_at: datetime = field(default_factory=datetime.now)
    expires_at: Optional[datetime] = None
    is_self_signed: bool = False

class HTTPSSecurityManager:
    """Manages HTTPS security configuration"""
    
    def __init__(self):
        self.tls_config = TLSConfiguration()
        self.certificates: Dict[str, SecurityCertificate] = {}
        self.security_headers = self._get_security_headers()
    
    def _get_security_headers(self) -> Dict[str, str]:
        """Get comprehensive security headers for HTTPS"""
        return {
            # HTTPS enforcement
            "Strict-Transport-Security": "max-age=31536000; includeSubDomains; preload",
            
            # Content security
            "Content-Security-Policy": (
                "default-src 'self'; "
                "script-src 'self' 'unsafe-inline' 'unsafe-eval'; "
                "style-src 'self' 'unsafe-inline'; "
                "img-src 'self' data: https:; "
                "font-src 'self' https:; "
                "connect-src 'self' wss: https:; "
                "frame-ancestors 'none'; "
                "base-uri 'self'; "
                "form-action 'self';"
            ),
            
            # XSS protection
            "X-Content-Type-Options": "nosniff",
            "X-Frame-Options": "DENY",
            "X-XSS-Protection": "1; mode=block",
            
            # Referrer policy
            "Referrer-Policy": "strict-origin-when-cross-origin",
            
            # Permissions policy
            "Permissions-Policy": (
                "camera=(), microphone=(), geolocation=(), "
                "payment=(), usb=(), magnetometer=(), gyroscope=(), "
                "accelerometer=(), ambient-light-sensor=()"
            ),
            
            # Additional security headers
            "X-Permitted-Cross-Domain-Policies": "none",
            "Cross-Origin-Embedder-Policy": "require-corp",
            "Cross-Origin-Opener-Policy": "same-origin",
            "Cross-Origin-Resource-Policy": "same-origin"
        }
    
    def create_ssl_context(self, cert_name: str = "default") -> ssl.SSLContext:
        """Create secure SSL context"""
        try:
            # Create SSL context with secure defaults
            context = ssl.create_default_context(ssl.Purpose.CLIENT_AUTH)
            
            # Set minimum TLS version
            if self.tls_config.min_version == TLSVersion.TLS_1_2:
                context.minimum_version = ssl.TLSVersion.TLSv1_2
            elif self.tls_config.min_version == TLSVersion.TLS_1_3:
                context.minimum_version = ssl.TLSVersion.TLSv1_3
            
            # Set maximum TLS version
            if self.tls_config.max_version == TLSVersion.TLS_1_3:
                context.maximum_version = ssl.TLSVersion.TLSv1_3
            
            # Configure cipher suites
            cipher_list = ":".join([cipher.value for cipher in self.tls_config.cipher_suites])
            context.set_ciphers(cipher_list)
            
            # Load certificate if available
            if cert_name in self.certificates:
                cert = self.certificates[cert_name]
                context.load_cert_chain(cert.cert_path, cert.key_path)
                
                if cert.ca_path:
                    context.load_verify_locations(cert.ca_path)
            
            # Security options
            context.options |= ssl.OP_NO_SSLv2
            context.options |= ssl.OP_NO_SSLv3
            context.options |= ssl.OP_NO_TLSv1
            context.options |= ssl.OP_NO_TLSv1_1
            context.options |= ssl.OP_SINGLE_DH_USE
            context.options |= ssl.OP_SINGLE_ECDH_USE
            
            # Hostname verification
            if self.tls_config.verify_hostname:
                context.check_hostname = self.tls_config.check_hostname
                context.verify_mode = ssl.CERT_REQUIRED if self.tls_config.require_client_cert else ssl.CERT_NONE
            
            logger.info(f"Created SSL context for certificate: {cert_name}")
            return context
            
        except Exception as e:
            logger.error(f"Failed to create SSL context: {e}")
            handle_error(
                ErrorCode.SECURITY_VALIDATION_FAILED,
                f"SSL context creation failed: {str(e)}",
                ErrorSeverity.HIGH,
                ErrorContext(service_name="https_security_manager")
            )
            raise
    
    def add_certificate(self, name: str, cert_path: str, key_path: str, 
                       ca_path: Optional[str] = None) -> SecurityCertificate:
        """Add security certificate"""
        try:
            # Validate certificate files exist
            import os
            if not os.path.exists(cert_path):
                raise FileNotFoundError(f"Certificate file not found: {cert_path}")
            if not os.path.exists(key_path):
                raise FileNotFoundError(f"Key file not found: {key_path}")
            if ca_path and not os.path.exists(ca_path):
                raise FileNotFoundError(f"CA file not found: {ca_path}")
            
            certificate = SecurityCertificate(
                cert_path=cert_path,
                key_path=key_path,
                ca_path=ca_path
            )
            
            self.certificates[name] = certificate
            logger.info(f"Added certificate: {name}")
            return certificate
            
        except Exception as e:
            logger.error(f"Failed to add certificate: {e}")
            raise
    
    def generate_self_signed_certificate(self, name: str, hostname: str = "localhost") -> SecurityCertificate:
        """Generate self-signed certificate for development"""
        try:
            from cryptography import x509
            from cryptography.x509.oid import NameOID
            from cryptography.hazmat.primitives import hashes, serialization
            from cryptography.hazmat.primitives.asymmetric import rsa
            
            # Generate private key
            private_key = rsa.generate_private_key(
                public_exponent=65537,
                key_size=2048
            )
            
            # Create certificate
            subject = issuer = x509.Name([
                x509.NameAttribute(NameOID.COUNTRY_NAME, "US"),
                x509.NameAttribute(NameOID.STATE_OR_PROVINCE_NAME, "CA"),
                x509.NameAttribute(NameOID.LOCALITY_NAME, "San Francisco"),
                x509.NameAttribute(NameOID.ORGANIZATION_NAME, "AI WellnessVision"),
                x509.NameAttribute(NameOID.COMMON_NAME, hostname),
            ])
            
            cert = x509.CertificateBuilder().subject_name(
                subject
            ).issuer_name(
                issuer
            ).public_key(
                private_key.public_key()
            ).serial_number(
                x509.random_serial_number()
            ).not_valid_before(
                datetime.now()
            ).not_valid_after(
                datetime.now() + timedelta(days=365)
            ).add_extension(
                x509.SubjectAlternativeName([
                    x509.DNSName(hostname),
                    x509.DNSName("localhost"),
                    x509.IPAddress(socket.inet_aton("127.0.0.1")),
                ]),
                critical=False,
            ).sign(private_key, hashes.SHA256())
            
            # Save certificate and key
            cert_path = f"certs/{name}.crt"
            key_path = f"certs/{name}.key"
            
            # Create certs directory if it doesn't exist
            import os
            os.makedirs("certs", exist_ok=True)
            
            # Write certificate
            with open(cert_path, "wb") as f:
                f.write(cert.public_bytes(serialization.Encoding.PEM))
            
            # Write private key
            with open(key_path, "wb") as f:
                f.write(private_key.private_bytes(
                    encoding=serialization.Encoding.PEM,
                    format=serialization.PrivateFormat.PKCS8,
                    encryption_algorithm=serialization.NoEncryption()
                ))
            
            certificate = SecurityCertificate(
                cert_path=cert_path,
                key_path=key_path,
                is_self_signed=True,
                expires_at=datetime.now() + timedelta(days=365)
            )
            
            self.certificates[name] = certificate
            logger.info(f"Generated self-signed certificate: {name}")
            return certificate
            
        except ImportError:
            logger.warning("Cryptography library not available for certificate generation")
            # Create mock certificate for testing
            certificate = SecurityCertificate(
                cert_path="mock_cert.pem",
                key_path="mock_key.pem",
                is_self_signed=True
            )
            self.certificates[name] = certificate
            return certificate
        except Exception as e:
            logger.error(f"Failed to generate self-signed certificate: {e}")
            raise
    
    def validate_certificate(self, name: str) -> Dict[str, Any]:
        """Validate certificate status"""
        if name not in self.certificates:
            return {"valid": False, "reason": "certificate_not_found"}
        
        cert = self.certificates[name]
        
        try:
            # Check if certificate files exist
            import os
            if not os.path.exists(cert.cert_path):
                return {"valid": False, "reason": "certificate_file_missing"}
            if not os.path.exists(cert.key_path):
                return {"valid": False, "reason": "key_file_missing"}
            
            # Check expiration
            if cert.expires_at and datetime.now() > cert.expires_at:
                return {"valid": False, "reason": "certificate_expired"}
            
            return {
                "valid": True,
                "is_self_signed": cert.is_self_signed,
                "expires_at": cert.expires_at.isoformat() if cert.expires_at else None,
                "days_until_expiry": (cert.expires_at - datetime.now()).days if cert.expires_at else None
            }
            
        except Exception as e:
            logger.error(f"Certificate validation failed: {e}")
            return {"valid": False, "reason": f"validation_error: {str(e)}"}
    
    def get_security_headers(self) -> Dict[str, str]:
        """Get security headers for HTTPS responses"""
        return self.security_headers.copy()

class WebSocketSecurityManager:
    """Manages WebSocket security"""
    
    def __init__(self):
        self.config = WebSocketSecurityConfig()
        self.active_connections: Dict[str, Dict[str, Any]] = {}
        self.connection_counts: Dict[str, int] = {}
        self.message_tokens: Dict[str, str] = {}
    
    def validate_websocket_connection(self, client_ip: str, origin: str, 
                                    headers: Dict[str, str]) -> Dict[str, Any]:
        """Validate WebSocket connection request"""
        try:
            validation_result = {
                "allowed": True,
                "connection_id": None,
                "warnings": [],
                "errors": []
            }
            
            # Check connection limit per IP
            current_connections = self.connection_counts.get(client_ip, 0)
            if current_connections >= self.config.max_connections_per_ip:
                validation_result["allowed"] = False
                validation_result["errors"].append("Connection limit exceeded for IP")
                return validation_result
            
            # Validate origin if required
            if self.config.require_origin_check:
                if not origin:
                    validation_result["allowed"] = False
                    validation_result["errors"].append("Origin header required")
                    return validation_result
                
                if self.config.allowed_origins and origin not in self.config.allowed_origins:
                    validation_result["allowed"] = False
                    validation_result["errors"].append("Origin not allowed")
                    return validation_result
            
            # Generate connection ID
            connection_id = f"ws_{client_ip}_{secrets.token_urlsafe(16)}"
            
            # Create connection record
            connection_record = {
                "connection_id": connection_id,
                "client_ip": client_ip,
                "origin": origin,
                "connected_at": datetime.now(),
                "last_activity": datetime.now(),
                "message_count": 0,
                "headers": headers
            }
            
            self.active_connections[connection_id] = connection_record
            self.connection_counts[client_ip] = current_connections + 1
            
            # Generate message token for this connection
            self.message_tokens[connection_id] = secrets.token_urlsafe(32)
            
            validation_result["connection_id"] = connection_id
            logger.info(f"WebSocket connection validated: {connection_id}")
            
            return validation_result
            
        except Exception as e:
            logger.error(f"WebSocket connection validation failed: {e}")
            return {
                "allowed": False,
                "errors": [f"Validation error: {str(e)}"]
            }
    
    def validate_websocket_message(self, connection_id: str, message: bytes, 
                                 message_type: str = "text") -> Dict[str, Any]:
        """Validate WebSocket message"""
        try:
            if connection_id not in self.active_connections:
                return {
                    "valid": False,
                    "reason": "connection_not_found"
                }
            
            connection = self.active_connections[connection_id]
            
            # Check message size
            if len(message) > self.config.max_message_size:
                logger.warning(f"WebSocket message too large: {len(message)} bytes")
                return {
                    "valid": False,
                    "reason": "message_too_large"
                }
            
            # Update connection activity
            connection["last_activity"] = datetime.now()
            connection["message_count"] += 1
            
            # Basic message validation
            if message_type == "text":
                try:
                    decoded_message = message.decode('utf-8')
                    # Check for potential security threats in text messages
                    if self._contains_security_threats(decoded_message):
                        logger.warning(f"Security threat detected in WebSocket message")
                        return {
                            "valid": False,
                            "reason": "security_threat_detected"
                        }
                except UnicodeDecodeError:
                    return {
                        "valid": False,
                        "reason": "invalid_text_encoding"
                    }
            
            return {
                "valid": True,
                "connection_id": connection_id,
                "message_token": self.message_tokens.get(connection_id)
            }
            
        except Exception as e:
            logger.error(f"WebSocket message validation failed: {e}")
            return {
                "valid": False,
                "reason": f"validation_error: {str(e)}"
            }
    
    def _contains_security_threats(self, message: str) -> bool:
        """Check message for security threats"""
        threat_patterns = [
            "<script", "javascript:", "eval(", "document.cookie",
            "window.location", "XMLHttpRequest", "fetch("
        ]
        
        message_lower = message.lower()
        return any(pattern in message_lower for pattern in threat_patterns)
    
    def close_websocket_connection(self, connection_id: str) -> bool:
        """Close WebSocket connection"""
        try:
            if connection_id not in self.active_connections:
                return False
            
            connection = self.active_connections[connection_id]
            client_ip = connection["client_ip"]
            
            # Remove connection
            del self.active_connections[connection_id]
            
            # Update connection count
            if client_ip in self.connection_counts:
                self.connection_counts[client_ip] = max(0, self.connection_counts[client_ip] - 1)
                if self.connection_counts[client_ip] == 0:
                    del self.connection_counts[client_ip]
            
            # Remove message token
            if connection_id in self.message_tokens:
                del self.message_tokens[connection_id]
            
            logger.info(f"WebSocket connection closed: {connection_id}")
            return True
            
        except Exception as e:
            logger.error(f"Failed to close WebSocket connection: {e}")
            return False
    
    def cleanup_inactive_connections(self) -> int:
        """Clean up inactive WebSocket connections"""
        try:
            current_time = datetime.now()
            timeout_threshold = timedelta(seconds=self.config.connection_timeout)
            
            inactive_connections = []
            
            for connection_id, connection in self.active_connections.items():
                if current_time - connection["last_activity"] > timeout_threshold:
                    inactive_connections.append(connection_id)
            
            cleaned_count = 0
            for connection_id in inactive_connections:
                if self.close_websocket_connection(connection_id):
                    cleaned_count += 1
            
            if cleaned_count > 0:
                logger.info(f"Cleaned up {cleaned_count} inactive WebSocket connections")
            
            return cleaned_count
            
        except Exception as e:
            logger.error(f"WebSocket cleanup failed: {e}")
            return 0
    
    def get_connection_status(self) -> Dict[str, Any]:
        """Get WebSocket connection status"""
        return {
            "active_connections": len(self.active_connections),
            "connections_by_ip": dict(self.connection_counts),
            "total_ips": len(self.connection_counts),
            "max_connections_per_ip": self.config.max_connections_per_ip,
            "connection_timeout": self.config.connection_timeout,
            "max_message_size": self.config.max_message_size
        }

class TransportSecurityManager:
    """Main transport security manager"""
    
    def __init__(self):
        self.https_manager = HTTPSSecurityManager()
        self.websocket_manager = WebSocketSecurityManager()
    
    def initialize_https_security(self, cert_name: str = "default", 
                                 hostname: str = "localhost") -> Dict[str, Any]:
        """Initialize HTTPS security"""
        try:
            # Try to use existing certificate or generate self-signed
            if cert_name not in self.https_manager.certificates:
                self.https_manager.generate_self_signed_certificate(cert_name, hostname)
            
            # Validate certificate
            cert_validation = self.https_manager.validate_certificate(cert_name)
            
            # Create SSL context
            ssl_context = self.https_manager.create_ssl_context(cert_name)
            
            return {
                "initialized": True,
                "certificate_name": cert_name,
                "certificate_validation": cert_validation,
                "ssl_context_created": ssl_context is not None,
                "security_headers": len(self.https_manager.get_security_headers())
            }
            
        except Exception as e:
            logger.error(f"HTTPS security initialization failed: {e}")
            return {
                "initialized": False,
                "error": str(e)
            }
    
    def get_transport_security_status(self) -> Dict[str, Any]:
        """Get comprehensive transport security status"""
        return {
            "https": {
                "certificates": len(self.https_manager.certificates),
                "security_headers": len(self.https_manager.security_headers),
                "tls_config": {
                    "min_version": self.https_manager.tls_config.min_version.value,
                    "max_version": self.https_manager.tls_config.max_version.value,
                    "cipher_suites": len(self.https_manager.tls_config.cipher_suites)
                }
            },
            "websocket": self.websocket_manager.get_connection_status()
        }

# Global transport security manager instance
transport_security_manager = TransportSecurityManager()

def get_transport_security_manager() -> TransportSecurityManager:
    """Get global transport security manager instance"""
    return transport_security_manager