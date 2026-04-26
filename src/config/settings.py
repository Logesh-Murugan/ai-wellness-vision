"""
Production-grade settings using pydantic-settings.

Loads configuration from environment variables (and ``.env`` file)
with startup validation and security checks.

Usage::

    from src.config.settings import get_settings

    settings = get_settings()          # cached singleton
    print(settings.DATABASE_URL)
"""

from __future__ import annotations

import logging
import warnings
from functools import lru_cache
from pathlib import Path
from typing import List, Literal, Optional

from pydantic import field_validator, model_validator
from pydantic_settings import BaseSettings, SettingsConfigDict

logger = logging.getLogger(__name__)

# ─── Project paths ─────────────────────────────
PROJECT_ROOT = Path(__file__).resolve().parent.parent.parent
LOGS_DIR = PROJECT_ROOT / "logs"
UPLOADS_DIR = PROJECT_ROOT / "uploads"
MODELS_DIR = PROJECT_ROOT / "models"
CACHE_DIR = PROJECT_ROOT / "cache"

for _d in (LOGS_DIR, UPLOADS_DIR, MODELS_DIR, CACHE_DIR):
    _d.mkdir(exist_ok=True)


# ─── Settings model ───────────────────────────
class Settings(BaseSettings):
    """Central application settings.

    Required env-vars will raise at startup if missing.
    Optional ones default to ``None`` (feature disabled).
    """

    model_config = SettingsConfigDict(
        env_file=str(PROJECT_ROOT / ".env"),
        env_file_encoding="utf-8",
        case_sensitive=True,
        extra="ignore",
    )

    # ── Environment ────────────────────────────
    ENVIRONMENT: Literal["development", "staging", "production"] = "development"
    DEBUG: bool = False

    # ── Server ─────────────────────────────────
    HOST: str = "0.0.0.0"
    PORT: int = 8000
    API_PORT: int = 8000

    # ── Database (required) ────────────────────
    DATABASE_URL: str

    # ── Redis (required) ───────────────────────
    REDIS_URL: str

    # ── JWT / Auth ─────────────────────────────
    SECRET_KEY: str                               # doubles as JWT_SECRET
    JWT_ALGORITHM: str = "HS256"
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 30
    REFRESH_TOKEN_EXPIRE_DAYS: int = 7

    # ── CORS ───────────────────────────────────
    ALLOWED_ORIGINS: str = "http://localhost:3000,http://localhost:8501"
    CORS_ORIGINS: str = ""  # legacy alias — merged at runtime

    # ── AI API Keys (optional) ─────────────────
    GEMINI_API_KEY: Optional[str] = None
    OPENAI_API_KEY: Optional[str] = None
    HUGGINGFACE_API_KEY: Optional[str] = None

    # ── Upload / rate limits ───────────────────
    MAX_IMAGE_SIZE_MB: int = 10
    MAX_UPLOAD_SIZE: int = 10 * 1024 * 1024       # bytes
    RATE_LIMIT_PER_MINUTE: int = 60
    REQUEST_TIMEOUT: int = 30

    # ── Feature flags ──────────────────────────
    ENABLE_OFFLINE_MODE: bool = True
    ENABLE_VOICE_FEATURES: bool = True
    ENABLE_EXPLAINABLE_AI: bool = True
    ENABLE_CACHE: bool = True

    # ── Logging ────────────────────────────────
    LOG_LEVEL: str = "INFO"
    USE_JSON_LOGGING: bool = False

    # ── Monitoring ─────────────────────────────
    ENABLE_METRICS: bool = True
    METRICS_PORT: int = 9090
    HEALTH_CHECK_INTERVAL: int = 30

    # ── Model config ──────────────────────────
    IMAGE_MODEL_NAME: str = "resnet50"
    WHISPER_MODEL_SIZE: str = "base"

    # ─── Validators ────────────────────────────

    @field_validator("SECRET_KEY")
    @classmethod
    def _validate_secret_key(cls, v: str) -> str:
        if len(v) < 32:
            raise ValueError(
                f"SECRET_KEY must be at least 32 characters (got {len(v)}). "
                "Generate one with: python -c \"import secrets; print(secrets.token_urlsafe(48))\""
            )
        return v

    @field_validator("DATABASE_URL")
    @classmethod
    def _validate_database_url(cls, v: str) -> str:
        if not v or v.strip() == "":
            raise ValueError("DATABASE_URL is required and cannot be empty")
        return v

    @field_validator("REDIS_URL")
    @classmethod
    def _validate_redis_url(cls, v: str) -> str:
        if not v or v.strip() == "":
            raise ValueError("REDIS_URL is required and cannot be empty")
        return v

    @model_validator(mode="after")
    def _warn_production_defaults(self) -> "Settings":
        """Emit warnings when production env uses insecure defaults."""
        if self.ENVIRONMENT == "production":
            _WEAK = {"dev-secret-key", "your-secret-key", "change-in-production"}
            if any(tok in self.SECRET_KEY.lower() for tok in _WEAK):
                warnings.warn(
                    "⚠️  PRODUCTION detected with a placeholder SECRET_KEY — "
                    "rotate immediately!",
                    RuntimeWarning,
                    stacklevel=2,
                )
            if self.DEBUG:
                warnings.warn(
                    "⚠️  PRODUCTION detected with DEBUG=true — "
                    "disable debug mode in production!",
                    RuntimeWarning,
                    stacklevel=2,
                )
        return self

    # ─── Computed helpers ──────────────────────

    @property
    def allowed_origins_list(self) -> List[str]:
        """Parse comma-separated origins into a list."""
        combined = ",".join(
            o for o in (self.ALLOWED_ORIGINS, self.CORS_ORIGINS) if o
        )
        return [o.strip() for o in combined.split(",") if o.strip()]

    @property
    def max_upload_bytes(self) -> int:
        return self.MAX_IMAGE_SIZE_MB * 1024 * 1024

    @property
    def is_production(self) -> bool:
        return self.ENVIRONMENT == "production"

    @property
    def is_development(self) -> bool:
        return self.ENVIRONMENT == "development"


# ─── Startup validation ───────────────────────

def validate_startup(settings: Settings) -> None:
    """Run startup checks and log the configuration summary."""
    logger.info("=" * 60)
    logger.info("  AI WellnessVision — Configuration Summary")
    logger.info("=" * 60)
    logger.info("  Environment   : %s", settings.ENVIRONMENT)
    logger.info("  Debug         : %s", settings.DEBUG)
    logger.info("  Server        : %s:%d", settings.HOST, settings.PORT)
    logger.info("  Database      : %s", _mask_url(settings.DATABASE_URL))
    logger.info("  Redis         : %s", _mask_url(settings.REDIS_URL))
    logger.info("  CORS origins  : %s", settings.allowed_origins_list)
    logger.info("  JWT algorithm : %s", settings.JWT_ALGORITHM)
    logger.info("  Access TTL    : %d min", settings.ACCESS_TOKEN_EXPIRE_MINUTES)
    logger.info("  Refresh TTL   : %d days", settings.REFRESH_TOKEN_EXPIRE_DAYS)
    logger.info("  Max upload    : %d MB", settings.MAX_IMAGE_SIZE_MB)
    logger.info("  Rate limit    : %d req/min", settings.RATE_LIMIT_PER_MINUTE)
    logger.info("-" * 60)

    # API key status
    _api_status = {
        "Gemini": settings.GEMINI_API_KEY,
        "OpenAI": settings.OPENAI_API_KEY,
        "HuggingFace": settings.HUGGINGFACE_API_KEY,
    }
    for name, key in _api_status.items():
        status = "✅ ENABLED" if key else "⬚  disabled"
        logger.info("  %-14s: %s", name, status)

    # Feature flags
    logger.info("-" * 60)
    _flags = {
        "Offline mode": settings.ENABLE_OFFLINE_MODE,
        "Voice features": settings.ENABLE_VOICE_FEATURES,
        "Explainable AI": settings.ENABLE_EXPLAINABLE_AI,
        "Cache (Redis)": settings.ENABLE_CACHE,
        "Metrics": settings.ENABLE_METRICS,
    }
    for name, enabled in _flags.items():
        logger.info("  %-14s: %s", name, "ON" if enabled else "OFF")

    logger.info("=" * 60)

    # Production safety checks
    if settings.is_production:
        if settings.ALLOWED_ORIGINS.strip() == "*":
            logger.warning("⚠️  CORS allow_origins='*' in production — tighten this!")
        if not settings.GEMINI_API_KEY and not settings.OPENAI_API_KEY:
            logger.warning("⚠️  No AI API keys configured — all responses will use fallback")


def _mask_url(url: str) -> str:
    """Mask password in a database/redis URL for safe logging."""
    if "://" not in url:
        return url
    try:
        from urllib.parse import urlparse, urlunparse

        parsed = urlparse(url)
        if parsed.password:
            masked = parsed._replace(
                netloc=f"{parsed.username}:****@{parsed.hostname}"
                + (f":{parsed.port}" if parsed.port else "")
            )
            return urlunparse(masked)
    except Exception:
        pass
    return url[:20] + "****"


# ─── Cached singleton ─────────────────────────

@lru_cache(maxsize=1)
def get_settings() -> Settings:
    """Return the Settings singleton (created once, cached forever)."""
    settings = Settings()  # type: ignore[call-arg]
    validate_startup(settings)
    return settings
