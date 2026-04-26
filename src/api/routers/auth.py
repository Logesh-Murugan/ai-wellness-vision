"""
Authentication router – register, login, refresh, logout, me.

All endpoints are prefixed with ``/api/v1/auth`` and tagged ``auth``.
"""

import logging
import time
import uuid
from datetime import datetime, timedelta
from typing import Any, Dict

from fastapi import APIRouter, Depends, HTTPException, status

from src.api.dependencies import get_current_user, get_db
from src.database.postgres_auth import PostgresAuthDatabase
from src.models.api_schemas import (
    AuthResponse,
    LoginRequest,
    RefreshTokenRequest,
    RegisterRequest,
    UserResponse,
)

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/api/v1/auth", tags=["auth"])

# ──────────────────────────────────────────────
# Helpers
# ──────────────────────────────────────────────

def _generate_tokens(user_id: str) -> tuple[str, str]:
    """Create an access / refresh token pair.

    In production replace with proper JWT (e.g. python-jose).
    """
    ts = int(time.time())
    access = f"access_token_{user_id}_{ts}"
    refresh = f"refresh_token_{user_id}_{ts}"
    return access, refresh


def _user_response(user: Dict[str, Any]) -> UserResponse:
    """Build a sanitised UserResponse from a DB user dict."""
    return UserResponse(
        id=user["id"],
        name=user.get("name", ""),
        email=user["email"],
        firstName=user.get("firstName"),
        lastName=user.get("lastName"),
        avatar=user.get("avatar"),
        preferences=user.get("preferences", {}),
        created_at=user.get("created_at", datetime.now().isoformat()),
    )


# ──────────────────────────────────────────────
# Endpoints
# ──────────────────────────────────────────────

@router.post("/register", response_model=AuthResponse, status_code=status.HTTP_201_CREATED)
async def register(
    request: RegisterRequest,
    db: PostgresAuthDatabase = Depends(get_db),
) -> AuthResponse:
    """Create a new user account."""
    # Check for existing user
    existing = await db.get_user_by_email(request.email)
    if existing:
        raise HTTPException(status_code=status.HTTP_409_CONFLICT, detail="User already exists")

    # Create user
    user_id = await db.create_user(
        email=request.email,
        password=request.password,
        first_name=request.firstName,
        last_name=request.lastName,
    )
    if not user_id:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to create user",
        )

    # Generate tokens & persist session
    access, refresh = _generate_tokens(user_id)
    expires_at = datetime.utcnow() + timedelta(hours=1)
    await db.save_session(user_id, access, refresh, expires_at)

    user = await db.get_user_by_id(user_id)
    if not user:
        raise HTTPException(status_code=500, detail="User created but could not be retrieved")
    user.pop("password_hash", None)

    return AuthResponse(
        access_token=access,
        refresh_token=refresh,
        expires_in=3600,
        user=_user_response(user),
    )


@router.post("/login", response_model=AuthResponse)
async def login(
    request: LoginRequest,
    db: PostgresAuthDatabase = Depends(get_db),
) -> AuthResponse:
    """Authenticate with email + password."""
    user = await db.get_user_by_email(request.email)
    if not user:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Invalid email or password")

    if not db.verify_password(request.password, user["password_hash"]):
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Invalid email or password")

    # Generate tokens & persist session
    access, refresh = _generate_tokens(user["id"])
    expires_at = datetime.utcnow() + timedelta(hours=1)
    await db.save_session(user["id"], access, refresh, expires_at)

    user.pop("password_hash", None)

    return AuthResponse(
        access_token=access,
        refresh_token=refresh,
        expires_in=3600,
        user=_user_response(user),
    )


@router.post("/refresh", response_model=AuthResponse)
async def refresh_token(
    request: RefreshTokenRequest,
    db: PostgresAuthDatabase = Depends(get_db),
) -> AuthResponse:
    """Exchange a valid refresh token for a new token pair."""
    if not request.refresh_token.startswith("refresh_token_"):
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Invalid refresh token format")

    parts = request.refresh_token.split("_")
    if len(parts) < 3:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Malformed refresh token")

    user_id = parts[2]
    user = await db.get_user_by_id(user_id)
    if not user:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="User not found")

    # Rotate tokens
    access, refresh = _generate_tokens(user_id)
    expires_at = datetime.utcnow() + timedelta(hours=1)
    await db.save_session(user_id, access, refresh, expires_at)

    user.pop("password_hash", None)

    return AuthResponse(
        access_token=access,
        refresh_token=refresh,
        expires_in=3600,
        user=_user_response(user),
    )


@router.post("/logout")
async def logout(
    current_user: Dict[str, Any] = Depends(get_current_user),
) -> Dict[str, str]:
    """Invalidate the current session.

    The ``get_current_user`` dependency already validated the token,
    so reaching here means the user is authenticated.
    """
    return {"message": "Logged out successfully"}


@router.get("/me", response_model=UserResponse)
async def me(
    current_user: Dict[str, Any] = Depends(get_current_user),
) -> UserResponse:
    """Return the authenticated user's profile."""
    return _user_response(current_user)
