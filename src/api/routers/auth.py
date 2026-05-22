"""
Authentication router – register, login, refresh, logout, me.
"""

import logging
import uuid
from datetime import datetime, timedelta
from typing import Dict

from fastapi import APIRouter, Depends, HTTPException, status
from passlib.context import CryptContext

from src.api.dependencies import get_current_user, get_user_repo
from src.database.repositories.user_repository import UserRepository
from src.database.models import User
from src.models.api_schemas import (
    AuthResponse,
    LoginRequest,
    RefreshTokenRequest,
    RegisterRequest,
    UserResponse,
)
from src.utils.jwt_utils import create_access_token, create_refresh_token, verify_token

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/api/v1/auth", tags=["auth"])

pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

def _user_response(user: User) -> UserResponse:
    """Build a sanitised UserResponse from a DB User model."""
    return UserResponse(
        id=str(user.id),
        name=getattr(user, "name", ""),
        email=user.email,
        firstName=getattr(user, "first_name", ""),
        lastName=getattr(user, "last_name", ""),
        avatar=getattr(user, "avatar", None),
        preferences=getattr(user, "preferences", {}),
        created_at=user.created_at.isoformat() if hasattr(user, "created_at") and user.created_at else datetime.utcnow().isoformat(),
    )

@router.post("/register", response_model=AuthResponse, status_code=status.HTTP_201_CREATED)
async def register(
    request: RegisterRequest,
    user_repo: UserRepository = Depends(get_user_repo),
) -> AuthResponse:
    """Create a new user account."""
    existing = await user_repo.get_by_email(request.email)
    if existing:
        raise HTTPException(status_code=status.HTTP_409_CONFLICT, detail="User already exists")

    hashed_password = pwd_context.hash(request.password)

    user_data = {
        "email": request.email,
        "password_hash": hashed_password,
        "first_name": request.firstName,
        "last_name": request.lastName,
    }
    user = await user_repo.create(user_data)
    
    user_id = str(user.id)
    access = create_access_token(data={"sub": user_id})
    refresh = create_refresh_token(data={"sub": user_id})
    
    return AuthResponse(
        access_token=access,
        refresh_token=refresh,
        expires_in=3600,
        user=_user_response(user),
    )

@router.post("/login", response_model=AuthResponse)
async def login(
    request: LoginRequest,
    user_repo: UserRepository = Depends(get_user_repo),
) -> AuthResponse:
    """Authenticate with email + password."""
    user = await user_repo.get_by_email(request.email)
    if not user:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Invalid email or password")

    if not pwd_context.verify(request.password, user.password_hash):
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Invalid email or password")

    user_id = str(user.id)
    
    access = create_access_token(data={"sub": user_id})
    refresh = create_refresh_token(data={"sub": user_id})
    
    return AuthResponse(
        access_token=access,
        refresh_token=refresh,
        expires_in=3600,
        user=_user_response(user),
    )

@router.post("/refresh", response_model=AuthResponse)
async def refresh_token(
    request: RefreshTokenRequest,
    user_repo: UserRepository = Depends(get_user_repo),
) -> AuthResponse:
    """Exchange a valid refresh token for a new token pair."""
    payload = verify_token(request.refresh_token, expected_type="refresh")
    user_id = payload.get("sub")
    
    if not user_id:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Invalid refresh token payload")

    user = await user_repo.get_by_id(uuid.UUID(user_id))
    if not user:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="User not found")

    access = create_access_token(data={"sub": user_id})
    refresh = create_refresh_token(data={"sub": user_id})
    
    return AuthResponse(
        access_token=access,
        refresh_token=refresh,
        expires_in=3600,
        user=_user_response(user),
    )

@router.post("/logout")
async def logout(
    current_user: User = Depends(get_current_user),
) -> Dict[str, str]:
    """Invalidate the current session (stateless JWT)."""
    return {"message": "Successfully logged out"}

@router.get("/me", response_model=UserResponse)
async def me(
    current_user: User = Depends(get_current_user),
) -> UserResponse:
    """Return the authenticated user's profile."""
    return _user_response(current_user)
