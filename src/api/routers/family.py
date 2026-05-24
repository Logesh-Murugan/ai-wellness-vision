"""
Family Health Hub router.

All endpoints require JWT authentication.
Prefix: /api/v1/family   Tags: family
"""

import logging
import uuid
from datetime import datetime
from typing import Any, Dict, List, Optional

from fastapi import APIRouter, Depends, HTTPException, status
from pydantic import BaseModel, Field
from sqlalchemy.ext.asyncio import AsyncSession

from src.api.dependencies import get_current_user, get_db
from src.database.models import FamilyMember, FamilyRelationship, User
from src.database.repositories.family_repository import FamilyRepository

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/api/v1/family", tags=["family"])


# ─── Pydantic schemas ─────────────────────────────────────────────────────────

class FamilyMemberCreate(BaseModel):
    name: str = Field(..., min_length=1, max_length=100)
    relationship: FamilyRelationship = FamilyRelationship.OTHER
    age: Optional[int] = Field(None, ge=0, le=150)
    language_preference: str = Field("en", min_length=2, max_length=10)


class FamilyMemberUpdate(BaseModel):
    name: Optional[str] = Field(None, min_length=1, max_length=100)
    relationship: Optional[FamilyRelationship] = None
    age: Optional[int] = Field(None, ge=0, le=150)
    language_preference: Optional[str] = Field(None, min_length=2, max_length=10)


class FamilyMemberResponse(BaseModel):
    id: str
    name: str
    relationship: str
    age: Optional[int]
    language_preference: str
    created_at: str

    model_config = {"from_attributes": True}


class MemberSummary(BaseModel):
    member_id: str
    name: str
    relationship: str
    total_analyses: int
    analyses_by_type: Dict[str, int]
    last_analysis_at: Optional[str]


# ─── Dependency ───────────────────────────────────────────────────────────────

async def _get_repo(db: AsyncSession = Depends(get_db)) -> FamilyRepository:
    return FamilyRepository(db)


# ─── Helpers ──────────────────────────────────────────────────────────────────

def _serialize(m: FamilyMember) -> FamilyMemberResponse:
    return FamilyMemberResponse(
        id=str(m.id),
        name=m.name,
        relationship=m.relationship.value if hasattr(m.relationship, "value") else str(m.relationship),
        age=m.age,
        language_preference=m.language_preference,
        created_at=m.created_at.isoformat() if m.created_at else datetime.utcnow().isoformat(),
    )


async def _get_owned_or_404(member_id: str, current_user: User, repo: FamilyRepository) -> FamilyMember:
    """Fetch member and verify ownership, raising 404 if missing or not owned."""
    try:
        mid = uuid.UUID(member_id)
    except ValueError:
        raise HTTPException(status_code=404, detail="Family member not found")

    member = await repo.get_by_id(mid)
    if member is None or member.owner_user_id != current_user.id:
        raise HTTPException(status_code=404, detail="Family member not found")
    return member


# ─── Endpoints ────────────────────────────────────────────────────────────────

@router.post("/members", response_model=FamilyMemberResponse, status_code=status.HTTP_201_CREATED)
async def create_family_member(
    payload: FamilyMemberCreate,
    current_user: User = Depends(get_current_user),
    repo: FamilyRepository = Depends(_get_repo),
) -> FamilyMemberResponse:
    """Create a new family member under the authenticated user's account."""
    member = await repo.create(
        owner_user_id=current_user.id,
        name=payload.name,
        relationship=payload.relationship.value,
        age=payload.age,
        language_preference=payload.language_preference,
    )
    logger.info("Family member created: user=%s member=%s", current_user.id, member.id)
    return _serialize(member)


@router.get("/members", response_model=List[FamilyMemberResponse])
async def list_family_members(
    current_user: User = Depends(get_current_user),
    repo: FamilyRepository = Depends(_get_repo),
) -> List[FamilyMemberResponse]:
    """Return all family members belonging to the current user."""
    members = await repo.get_by_owner(current_user.id)
    return [_serialize(m) for m in members]


@router.put("/members/{member_id}", response_model=FamilyMemberResponse)
async def update_family_member(
    member_id: str,
    payload: FamilyMemberUpdate,
    current_user: User = Depends(get_current_user),
    repo: FamilyRepository = Depends(_get_repo),
) -> FamilyMemberResponse:
    """Update a family member's details (ownership checked)."""
    await _get_owned_or_404(member_id, current_user, repo)

    update_data: Dict[str, Any] = payload.model_dump(exclude_none=True)
    if "relationship" in update_data and isinstance(update_data["relationship"], FamilyRelationship):
        update_data["relationship"] = update_data["relationship"].value

    updated = await repo.update(uuid.UUID(member_id), update_data)
    logger.info("Family member updated: user=%s member=%s", current_user.id, member_id)
    return _serialize(updated)


@router.delete("/members/{member_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_family_member(
    member_id: str,
    current_user: User = Depends(get_current_user),
    repo: FamilyRepository = Depends(_get_repo),
) -> None:
    """Delete a family member (ownership checked)."""
    await _get_owned_or_404(member_id, current_user, repo)
    await repo.delete(uuid.UUID(member_id))
    logger.info("Family member deleted: user=%s member=%s", current_user.id, member_id)


@router.get("/summary", response_model=List[MemberSummary])
async def family_health_summary(
    current_user: User = Depends(get_current_user),
    repo: FamilyRepository = Depends(_get_repo),
) -> List[MemberSummary]:
    """Aggregate health summary for every family member of the current user."""
    members = await repo.get_by_owner(current_user.id)
    summaries: List[MemberSummary] = []

    for m in members:
        records = await repo.get_member_analyses(m.id, limit=500)
        by_type: Dict[str, int] = {}
        last_at: Optional[str] = None

        for r in records:
            t = r.analysis_type.value if hasattr(r.analysis_type, "value") else str(r.analysis_type)
            by_type[t] = by_type.get(t, 0) + 1
            ts = r.created_at.isoformat() if r.created_at else None
            if ts and (last_at is None or ts > last_at):
                last_at = ts

        summaries.append(
            MemberSummary(
                member_id=str(m.id),
                name=m.name,
                relationship=m.relationship.value if hasattr(m.relationship, "value") else str(m.relationship),
                total_analyses=len(records),
                analyses_by_type=by_type,
                last_analysis_at=last_at,
            )
        )

    return summaries
