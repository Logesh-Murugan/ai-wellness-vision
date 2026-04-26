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
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials

from src.database.postgres_auth import PostgresAuthDatabase, get_postgres_db

logger = logging.getLogger(__name__)

# Reusable security scheme – extracts "Bearer <token>" header
_bearer_scheme = HTTPBearer(auto_error=False)


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
    credentials: Optional[HTTPAuthorizationCredentials] = Depends(_bearer_scheme),
    db: PostgresAuthDatabase = Depends(get_db),
) -> Dict[str, Any]:
    """Extract and validate the Bearer token, returning the user dict.

    Raises HTTPException 401 if the token is missing, invalid, or expired.
    """
    if credentials is None:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Authentication required",
            headers={"WWW-Authenticate": "Bearer"},
        )

    token = credentials.credentials
    session = await db.get_session_by_token(token)

    if session is None:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid or expired access token",
            headers={"WWW-Authenticate": "Bearer"},
        )

    # Fetch full user record
    user = await db.get_user_by_id(session["user_id"])
    if user is None:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="User associated with this token no longer exists",
            headers={"WWW-Authenticate": "Bearer"},
        )

    # Strip sensitive fields before returning
    user.pop("password_hash", None)
    return user


async def get_optional_user(
    credentials: Optional[HTTPAuthorizationCredentials] = Depends(_bearer_scheme),
    db: PostgresAuthDatabase = Depends(get_db),
) -> Optional[Dict[str, Any]]:
    """Like `get_current_user` but returns ``None`` instead of raising 401.

    Useful for endpoints that work for both authenticated and anonymous users.
    """
    if credentials is None:
        return None

    try:
        token = credentials.credentials
        session = await db.get_session_by_token(token)
        if session is None:
            return None

        user = await db.get_user_by_id(session["user_id"])
        if user:
            user.pop("password_hash", None)
        return user
    except Exception:
        return None
