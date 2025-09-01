# config.py - Configuration settings for AI WellnessVision
import os
import logging
from pathlib import Path
from typing import Dict, List, Optional
from dataclasses import dataclass
from enum import Enum

# Project paths
PROJECT_ROOT = Path(__file__).parent.parent
DATA_DIR = PROJECT_ROOT / "data"
MODELS_DIR = PROJECT_ROOT / "models"
LOGS_DIR = PROJECT_ROOT / "logs"
CACHE_DIR = PROJECT_ROOT / "cache"
TEMP_DIR = PROJECT_ROOT / "temp"

# Create directories if they don't exist
for dir_path in [DATA_DIR, MODELS_DIR, LOGS_DIR, CACHE_DIR, TEMP_DIR]:
    dir_path.mkdir(exist_ok=True)

class Environment(Enum):
    DEVELOPMENT = "development"
    TESTING = "testing"
    PRODUCTION = "production"

@dataclass
class DatabaseConfig:
    """Database configuration settings"""
    url: str = "sqlite:///./ai_wellness_vision.db"
    echo: bool = False
    pool_size: int = 5
    max_overflow: int = 10

# AI Model Settings
class ModelConfig:
    # Image Recognition
    IMAGE_MODEL_NAME = "resnet50"
    IMAGE_INPUT_SIZE = (224, 224)
    
    # NLP Settings
    NLP_MODEL_NAME = "distilbert-base-uncased"
    MAX_SEQUENCE_LENGTH = 512
    
    # Speech Settings
    WHISPER_MODEL_SIZE = "base"
    TTS_MODEL = "tts_models/en/ljspeech/tacotron2-DDC"
    
    # Explainable AI
    LIME_NUM_FEATURES = 10
    GRADCAM_LAYER_NAME = "conv5_block3_out"

# Application Settings
class AppConfig:
    # Environment
    ENVIRONMENT = Environment(os.getenv("ENVIRONMENT", "development"))
    DEBUG = os.getenv("DEBUG", "False").lower() == "true"
    
    # Server settings
    HOST = os.getenv("HOST", "localhost")
    PORT = int(os.getenv("PORT", 8501))
    API_PORT = int(os.getenv("API_PORT", 8000))
    
    # Security
    SECRET_KEY = os.getenv("SECRET_KEY", "dev-secret-key-change-in-production")
    CORS_ORIGINS = os.getenv("CORS_ORIGINS", "*").split(",")
    
    # Supported languages
    SUPPORTED_LANGUAGES = ["en", "hi", "ta", "te", "bn", "gu", "mr"]
    DEFAULT_LANGUAGE = "en"
    
    # Performance settings
    MAX_UPLOAD_SIZE = int(os.getenv("MAX_UPLOAD_SIZE", 10 * 1024 * 1024))  # 10MB
    REQUEST_TIMEOUT = int(os.getenv("REQUEST_TIMEOUT", 30))  # 30 seconds
    
    # Feature flags
    ENABLE_OFFLINE_MODE = os.getenv("ENABLE_OFFLINE_MODE", "True").lower() == "true"
    ENABLE_VOICE_FEATURES = os.getenv("ENABLE_VOICE_FEATURES", "True").lower() == "true"
    ENABLE_EXPLAINABLE_AI = os.getenv("ENABLE_EXPLAINABLE_AI", "True").lower() == "true"

# API Keys (use environment variables)
class APIConfig:
    OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")
    HUGGINGFACE_API_KEY = os.getenv("HUGGINGFACE_API_KEY")

# Logging Configuration
class LoggingConfig:
    LEVEL = os.getenv("LOG_LEVEL", "INFO").upper()
    FORMAT = "%(asctime)s - %(name)s - %(levelname)s - %(message)s"
    DATE_FORMAT = "%Y-%m-%d %H:%M:%S"
    
    # File logging
    LOG_FILE = LOGS_DIR / "ai_wellness_vision.log"
    MAX_BYTES = int(os.getenv("LOG_MAX_BYTES", 10 * 1024 * 1024))  # 10MB
    BACKUP_COUNT = int(os.getenv("LOG_BACKUP_COUNT", 5))
    
    # Structured logging for production
    USE_JSON_LOGGING = os.getenv("USE_JSON_LOGGING", "False").lower() == "true"

# Cache Configuration
class CacheConfig:
    REDIS_URL = os.getenv("REDIS_URL", "redis://localhost:6379/0")
    DEFAULT_TTL = int(os.getenv("CACHE_DEFAULT_TTL", 3600))  # 1 hour
    MODEL_CACHE_TTL = int(os.getenv("MODEL_CACHE_TTL", 86400))  # 24 hours
    ENABLE_CACHE = os.getenv("ENABLE_CACHE", "True").lower() == "true"

# Monitoring Configuration
class MonitoringConfig:
    ENABLE_METRICS = os.getenv("ENABLE_METRICS", "True").lower() == "true"
    METRICS_PORT = int(os.getenv("METRICS_PORT", 9090))
    HEALTH_CHECK_INTERVAL = int(os.getenv("HEALTH_CHECK_INTERVAL", 30))  # seconds

def get_config() -> Dict:
    """Get complete configuration dictionary"""
    return {
        "app": AppConfig,
        "model": ModelConfig,
        "api": APIConfig,
        "database": DatabaseConfig(),
        "logging": LoggingConfig,
        "cache": CacheConfig,
        "monitoring": MonitoringConfig,
        "paths": {
            "project_root": PROJECT_ROOT,
            "data_dir": DATA_DIR,
            "models_dir": MODELS_DIR,
            "logs_dir": LOGS_DIR,
            "cache_dir": CACHE_DIR,
            "temp_dir": TEMP_DIR,
        }
    }

def validate_config() -> bool:
    """Validate configuration settings"""
    try:
        # Check required directories exist
        required_dirs = [DATA_DIR, MODELS_DIR, LOGS_DIR]
        for dir_path in required_dirs:
            if not dir_path.exists():
                raise ValueError(f"Required directory does not exist: {dir_path}")
        
        # Validate environment
        if AppConfig.ENVIRONMENT not in Environment:
            raise ValueError(f"Invalid environment: {AppConfig.ENVIRONMENT}")
        
        # Check API keys in production
        if AppConfig.ENVIRONMENT == Environment.PRODUCTION:
            if not APIConfig.OPENAI_API_KEY:
                logging.warning("OpenAI API key not set in production environment")
            if not APIConfig.HUGGINGFACE_API_KEY:
                logging.warning("HuggingFace API key not set in production environment")
        
        return True
    except Exception as e:
        logging.error(f"Configuration validation failed: {e}")
        return False