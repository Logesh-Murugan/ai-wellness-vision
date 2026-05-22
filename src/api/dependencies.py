"""
Shared FastAPI dependencies for AI WellnessVision.
"""

import logging
from typing import Optional

from fastapi import Depends, HTTPException, status
from fastapi.security import OAuth2PasswordBearer
from sqlalchemy.ext.asyncio import AsyncSession
import uuid

# Import SQLAlchemy session maker instead of legacy db wrapper
from src.database.session import get_db
from src.utils.jwt_utils import verify_token
from src.database.repositories.user_repository import UserRepository
from src.database.repositories.analysis_repository import AnalysisRepository
from src.database.repositories.chat_repository import ChatRepository
from src.database.models import User

logger = logging.getLogger(__name__)

oauth2_scheme = OAuth2PasswordBearer(tokenUrl="/api/v1/auth/login", auto_error=False)

# ──────────────────────────────────────────────
# Repository Factories
# ──────────────────────────────────────────────

async def get_user_repo(db: AsyncSession = Depends(get_db)) -> UserRepository:
    return UserRepository(db)

async def get_analysis_repo(db: AsyncSession = Depends(get_db)) -> AnalysisRepository:
    return AnalysisRepository(db)

async def get_chat_repo(db: AsyncSession = Depends(get_db)) -> ChatRepository:
    return ChatRepository(db)

# ──────────────────────────────────────────────
# Auth dependencies
# ──────────────────────────────────────────────

async def get_current_user(
    token: str = Depends(oauth2_scheme),
    user_repo: UserRepository = Depends(get_user_repo),
) -> User:
    """Extract and validate the JWT token, returning the User object."""
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

    try:
        uid = uuid.UUID(user_id)
    except ValueError:
        raise HTTPException(status_code=401, detail="Invalid user ID format")

    user = await user_repo.get_by_id(uid)
    if user is None:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="User associated with this token no longer exists",
            headers={"WWW-Authenticate": "Bearer"},
        )

    # Check account is active
    if not getattr(user, "is_active", True):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="User account has been deactivated",
            headers={"WWW-Authenticate": "Bearer"},
        )

    return user

async def get_optional_user(
    token: str = Depends(oauth2_scheme),
    user_repo: UserRepository = Depends(get_user_repo),
) -> Optional[User]:
    """Like `get_current_user` but returns ``None`` instead of raising 401."""
    if not token:
        return None

    try:
        payload = verify_token(token, expected_type="access")
        user_id = payload.get("sub")
        if not user_id:
            return None

        uid = uuid.UUID(user_id)

        user = await user_repo.get_by_id(uid)
        if user:
            if not getattr(user, "is_active", True):
                return None
        return user
    except Exception:
        return None