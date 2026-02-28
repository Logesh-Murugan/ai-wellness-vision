#!/usr/bin/env python3
"""
Production Deployment Configuration for CNN Health Analysis System
"""

import os
from pathlib import Path
from typing import Dict, List
import yaml

class ProductionConfig:
    """Production deployment configuration"""
    
    def __init__(self):
        self.config = {
            # Server Configuration
            'server': {
                'host': '0.0.0.0',
                'port': 8000,
                'workers': 4,
                'max_requests': 1000,
                'timeout': 300,
                'keepalive': 2,
                'ssl_enabled': True,
                'ssl_cert_path': '/etc/ssl/certs/server.crt',
                'ssl_key_path': '/etc/ssl/private/server.key'
            },
            
            # Database Configuration
            'database': {
                'type': 'postgresql',
                'host': os.getenv('DB_HOST', 'localhost'),
                'port': int(os.getenv('DB_PORT', 5432)),
                'name': os.getenv('DB_NAME', 'ai_wellness'),
                'user': os.getenv('DB_USER', 'wellness_user'),
                'password': os.getenv('DB_PASSWORD', ''),
                'pool_size': 20,
                'max_overflow': 30,
                'pool_timeout': 30,
                'pool_recycle': 3600
            },
            
            # Redis Configuration (for caching and sessions)
            'redis': {
                'host': os.getenv('REDIS_HOST', 'localhost'),
                'port': int(os.getenv('REDIS_PORT', 6379)),
                'db': int(os.getenv('REDIS_DB', 0)),
                'password': os.getenv('REDIS_PASSWORD', ''),
                'max_connections': 50,
                'socket_timeout': 5,
                'socket_connect_timeout': 5
            },
            
            # CNN Model Configuration
            'cnn_models': {
                'model_path': '/app/models/cnn_health',
                'batch_size': 1,
                'max_image_size': 10 * 1024 * 1024,  # 10MB
                'supported_formats': ['.jpg', '.jpeg', '.png', '.bmp', '.webp'],
                'preprocessing': {
                    'resize_to': (224, 224),
                    'normalize': True,
                    'augmentation': False  # Disabled in production
                },
                'performance': {
                    'gpu_enabled': True,
                    'mixed_precision': True,
                    'model_caching': True,
                    'prediction_timeout': 30
                }
            },
            
            # Security Configuration
            'security': {
                'secret_key': os.getenv('SECRET_KEY', 'your-secret-key-here'),
                'jwt_algorithm': 'HS256',
                'jwt_expiration': 3600,
                'cors_origins': [
                    'https://your-flutter-app.com',
                    'https://your-web-app.com'
                ],
                'rate_limiting': {
                    'enabled': True,
                    'requests_per_minute': 60,
                    'requests_per_hour': 1000,
                    'burst_limit': 10
                },
                'input_validation': {
                    'max_file_size': 10 * 1024 * 1024,
                    'allowed_mime_types': [
                        'image/jpeg', 'image/png', 'image/bmp', 'image/webp'
                    ]
                }
            },
            
            # Monitoring Configuration
            'monitoring': {
                'enabled': True,
                'metrics_endpoint': '/metrics',
                'health_endpoint': '/health',
                'log_level': 'INFO',
                'log_format': 'json',
                'performance_tracking': True,
                'error_tracking': True,
                'alerts': {
                    'email_notifications': True,
                    'slack_webhook': os.getenv('SLACK_WEBHOOK_URL', ''),
                    'error_threshold': 5,  # errors per minute
                    'response_time_threshold': 5.0  # seconds
                }
            },
            
            # Scaling Configuration
            'scaling': {
                'auto_scaling': True,
                'min_replicas': 2,
                'max_replicas': 10,
                'target_cpu_utilization': 70,
                'target_memory_utilization': 80,
                'scale_up_cooldown': 300,  # seconds
                'scale_down_cooldown': 600  # seconds
            },
            
            # Storage Configuration
            'storage': {
                'type': 's3',  # or 'local', 'gcs', 'azure'
                'bucket_name': os.getenv('S3_BUCKET', 'ai-wellness-storage'),
                'region': os.getenv('AWS_REGION', 'us-east-1'),
                'access_key': os.getenv('AWS_ACCESS_KEY_ID', ''),
                'secret_key': os.getenv('AWS_SECRET_ACCESS_KEY', ''),
                'upload_path': 'uploads/',
                'model_path': 'models/',
                'backup_path': 'backups/',
                'retention_days': 30
            },
            
            # External Services
            'external_services': {
                'gemini_api': {
                    'enabled': True,
                    'api_key': os.getenv('GEMINI_API_KEY', ''),
                    'timeout': 30,
                    'retry_attempts': 3,
                    'fallback_enabled': True
                },
                'notification_service': {
                    'email_provider': 'sendgrid',
                    'api_key': os.getenv('SENDGRID_API_KEY', ''),
                    'from_email': 'noreply@ai-wellness.com'
                }
            }
        }
    
    def get_docker_compose_config(self) -> Dict:
        """Generate Docker Compose configuration"""
        
        return {
            'version': '3.8',
            'services': {
                'ai-wellness-api': {
                    'build': {
                        'context': '.',
                        'dockerfile': 'Dockerfile.production'
                    },
                    'ports': [f"{self.config['server']['port']}:8000"],
                    'environment': [
                        f"DB_HOST={self.config['database']['host']}",
                        f"DB_PORT={self.config['database']['port']}",
                        f"DB_NAME={self.config['database']['name']}",
                        f"REDIS_HOST={self.config['redis']['host']}",
                        f"REDIS_PORT={self.config['redis']['port']}",
                        "ENVIRONMENT=production"
                    ],
                    'volumes': [
                        './models:/app/models:ro',
                        './logs:/app/logs'
                    ],
                    'depends_on': ['postgres', 'redis'],
                    'restart': 'unless-stopped',
                    'deploy': {
                        'replicas': self.config['scaling']['min_replicas'],
                        'resources': {
                            'limits': {
                                'cpus': '2.0',
                                'memory': '4G'
                            },
                            'reservations': {
                                'cpus': '1.0',
                                'memory': '2G'
                            }
                        }
                    }
                },
                
                'postgres': {
                    'image': 'postgres:13',
                    'environment': [
                        f"POSTGRES_DB={self.config['database']['name']}",
                        f"POSTGRES_USER={self.config['database']['user']}",
                        f"POSTGRES_PASSWORD={self.config['database']['password']}"
                    ],
                    'volumes': [
                        'postgres_data:/var/lib/postgresql/data',
                        './init.sql:/docker-entrypoint-initdb.d/init.sql'
                    ],
                    'restart': 'unless-stopped'
                },
                
                'redis': {
                    'image': 'redis:6-alpine',
                    'command': f"redis-server --requirepass {self.config['redis']['password']}",
                    'volumes': ['redis_data:/data'],
                    'restart': 'unless-stopped'
                },
                
                'nginx': {
                    'image': 'nginx:alpine',
                    'ports': ['80:80', '443:443'],
                    'volumes': [
                        './nginx.conf:/etc/nginx/nginx.conf:ro',
                        './ssl:/etc/ssl:ro'
                    ],
                    'depends_on': ['ai-wellness-api'],
                    'restart': 'unless-stopped'
                }
            },
            
            'volumes': {
                'postgres_data': {},
                'redis_data': {}
            },
            
            'networks': {
                'ai-wellness-network': {
                    'driver': 'bridge'
                }
            }
        }
    
    def get_kubernetes_config(self) -> Dict:
        """Generate Kubernetes deployment configuration"""
        
        return {
            'apiVersion': 'apps/v1',
            'kind': 'Deployment',
            'metadata': {
                'name': 'ai-wellness-api',
                'labels': {
                    'app': 'ai-wellness-api'
                }
            },
            'spec': {
                'replicas': self.config['scaling']['min_replicas'],
                'selector': {
                    'matchLabels': {
                        'app': 'ai-wellness-api'
                    }
                },
                'template': {
                    'metadata': {
                        'labels': {
                            'app': 'ai-wellness-api'
                        }
                    },
                    'spec': {
                        'containers': [{
                            'name': 'ai-wellness-api',
                            'image': 'ai-wellness:latest',
                            'ports': [{
                                'containerPort': 8000
                            }],
                            'env': [
                                {'name': 'ENVIRONMENT', 'value': 'production'},
                                {'name': 'DB_HOST', 'value': 'postgres-service'},
                                {'name': 'REDIS_HOST', 'value': 'redis-service'}
                            ],
                            'resources': {
                                'requests': {
                                    'cpu': '1000m',
                                    'memory': '2Gi'
                                },
                                'limits': {
                                    'cpu': '2000m',
                                    'memory': '4Gi'
                                }
                            },
                            'livenessProbe': {
                                'httpGet': {
                                    'path': '/health',
                                    'port': 8000
                                },
                                'initialDelaySeconds': 30,
                                'periodSeconds': 10
                            },
                            'readinessProbe': {
                                'httpGet': {
                                    'path': '/health',
                                    'port': 8000
                                },
                                'initialDelaySeconds': 5,
                                'periodSeconds': 5
                            }
                        }]
                    }
                }
            }
        }
    
    def generate_nginx_config(self) -> str:
        """Generate Nginx configuration for production"""
        
        return f"""
events {{
    worker_connections 1024;
}}

http {{
    upstream ai_wellness_backend {{
        server ai-wellness-api:8000;
    }}
    
    # Rate limiting
    limit_req_zone $binary_remote_addr zone=api:10m rate=10r/s;
    
    server {{
        listen 80;
        server_name your-domain.com;
        return 301 https://$server_name$request_uri;
    }}
    
    server {{
        listen 443 ssl http2;
        server_name your-domain.com;
        
        ssl_certificate /etc/ssl/certs/server.crt;
        ssl_certificate_key /etc/ssl/private/server.key;
        
        # Security headers
        add_header X-Frame-Options DENY;
        add_header X-Content-Type-Options nosniff;
        add_header X-XSS-Protection "1; mode=block";
        add_header Strict-Transport-Security "max-age=31536000; includeSubDomains";
        
        # File upload size limit
        client_max_body_size {self.config['security']['input_validation']['max_file_size'] // (1024*1024)}M;
        
        location / {{
            limit_req zone=api burst=20 nodelay;
            
            proxy_pass http://ai_wellness_backend;
            proxy_set_header Host $host;
            proxy_set_header X-Real-IP $remote_addr;
            proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
            proxy_set_header X-Forwarded-Proto $scheme;
            
            proxy_connect_timeout 30s;
            proxy_send_timeout 30s;
            proxy_read_timeout 30s;
        }}
        
        location /health {{
            proxy_pass http://ai_wellness_backend/health;
            access_log off;
        }}
    }}
}}
"""
    
    def save_configs(self, output_dir: str = "deploy"):
        """Save all configuration files"""
        
        output_path = Path(output_dir)
        output_path.mkdir(exist_ok=True)
        
        # Docker Compose
        docker_compose = self.get_docker_compose_config()
        with open(output_path / 'docker-compose.prod.yml', 'w') as f:
            yaml.dump(docker_compose, f, default_flow_style=False)
        
        # Kubernetes
        k8s_config = self.get_kubernetes_config()
        with open(output_path / 'k8s-deployment.yml', 'w') as f:
            yaml.dump(k8s_config, f, default_flow_style=False)
        
        # Nginx
        nginx_config = self.generate_nginx_config()
        with open(output_path / 'nginx.conf', 'w') as f:
            f.write(nginx_config)
        
        # Environment template
        env_template = f"""
# Production Environment Variables
ENVIRONMENT=production
SECRET_KEY={self.config['security']['secret_key']}

# Database
DB_HOST={self.config['database']['host']}
DB_PORT={self.config['database']['port']}
DB_NAME={self.config['database']['name']}
DB_USER={self.config['database']['user']}
DB_PASSWORD=your_secure_password_here

# Redis
REDIS_HOST={self.config['redis']['host']}
REDIS_PORT={self.config['redis']['port']}
REDIS_PASSWORD=your_redis_password_here

# External APIs
GEMINI_API_KEY=your_gemini_api_key_here

# AWS (if using S3)
AWS_ACCESS_KEY_ID=your_aws_access_key
AWS_SECRET_ACCESS_KEY=your_aws_secret_key
AWS_REGION={self.config['storage']['region']}
S3_BUCKET={self.config['storage']['bucket_name']}

# Notifications
SENDGRID_API_KEY=your_sendgrid_api_key
SLACK_WEBHOOK_URL=your_slack_webhook_url
"""
        
        with open(output_path / '.env.production', 'w') as f:
            f.write(env_template)
        
        print(f"Production configuration files saved to {output_path}/")

if __name__ == "__main__":
    config = ProductionConfig()
    config.save_configs()