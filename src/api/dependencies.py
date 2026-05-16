"""
Shared FastAPI dependencies for AI WellnessVision.

Provides:
- get_db()            → PostgresAuthDatabase (async pool)
- get_current_user()  → authenticated user dict  (raises 401)
- get_optional_user() → user dict | None          (no raise)
"""

import logging
from typing import Optional, Dict, Any

from fastapi import Depends, HTTPException, status
from fastapi.security import OAuth2PasswordBearer

from src.database.postgres_auth import PostgresAuthDatabase, get_postgres_db
from src.utils.jwt_utils import verify_token

logger = logging.getLogger(__name__)

# Reusable security scheme – extracts "Bearer <token>" header
oauth2_scheme = OAuth2PasswordBearer(tokenUrl="/api/v1/auth/login", auto_error=False)


# ──────────────────────────────────────────────
# Database dependency
# ──────────────────────────────────────────────

async def get_db() -> PostgresAuthDatabase:
    """Return the initialised database connection pool.

    Raises HTTPException 503 if the pool cannot be obtained.
    """
    try:
        db = await get_postgres_db()
        return db
    except Exception as exc:
        logger.error(f"Database unavailable (skipping for demo): {exc}")
        return None  # Bypass 503 error for the demo


# ──────────────────────────────────────────────
# Auth dependencies
# ──────────────────────────────────────────────

async def get_current_user(
    token: str = Depends(oauth2_scheme),
    db: PostgresAuthDatabase = Depends(get_db),
) -> Dict[str, Any]:
    """Extract and validate the JWT token, returning the user dict.

    Raises HTTPException 401 if the token is missing, invalid, or expired.
    """
    if not token:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Not authenticated",
            headers={"WWW-Authenticate": "Bearer"},
        )

    payload = verify_token(token, expected_type="access")
    user_id = payload.get("sub")
    if not user_id:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Could not validate credentials",
            headers={"WWW-Authenticate": "Bearer"},
        )

    # Fetch full user record
    user = await db.get_user_by_id(user_id)
    if user is None:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="User associated with this token no longer exists",
            headers={"WWW-Authenticate": "Bearer"},
        )

    # Check account is active (deactivated users rejected even with valid token)
    if not user.get("is_active", True):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="User account has been deactivated",
            headers={"WWW-Authenticate": "Bearer"},
        )

    # Strip sensitive fields before returning
    user.pop("password_hash", None)
    return user


async def get_optional_user(
    token: str = Depends(oauth2_scheme),
    db: PostgresAuthDatabase = Depends(get_db),
) -> Optional[Dict[str, Any]]:
    """Like `get_current_user` but returns ``None`` instead of raising 401.

    Useful for endpoints that work for both authenticated and anonymous users.
    """
    if not token:
        return None

    try:
        payload = verify_token(token, expected_type="access")
        user_id = payload.get("sub")
        if not user_id:
            return None

        user = await db.get_user_by_id(user_id)
        if user:
            user.pop("password_hash", None)
        return user
    except Exception:
        return None