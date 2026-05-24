import uuid
import logging
from typing import List, Optional, Dict, Any

from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, update, delete

from src.database.models import AnalysisRecord, FamilyMember

logger = logging.getLogger(__name__)


class FamilyRepository:
    """Async SQLAlchemy 2.0 repository for FamilyMember CRUD."""

    def __init__(self, session: AsyncSession) -> None:
        self.session = session

    async def create(
        self,
        owner_user_id: uuid.UUID,
        name: str,
        relationship: str,
        age: Optional[int],
        language_preference: str,
    ) -> FamilyMember:
        """Insert a new family member row and return the refreshed ORM object."""
        from src.database.models import FamilyRelationship
        member = FamilyMember(
            owner_user_id=owner_user_id,
            name=name,
            relationship=FamilyRelationship(relationship),
            age=age,
            language_preference=language_preference,
        )
        self.session.add(member)
        await self.session.commit()
        await self.session.refresh(member)
        logger.debug("FamilyMember created: id=%s owner=%s", member.id, owner_user_id)
        return member

    async def get_by_owner(self, owner_user_id: uuid.UUID) -> List[FamilyMember]:
        """Return all family members for a given owner, ordered by created_at ASC."""
        stmt = (
            select(FamilyMember)
            .where(FamilyMember.owner_user_id == owner_user_id)
            .order_by(FamilyMember.created_at.asc())
        )
        result = await self.session.execute(stmt)
        return list(result.scalars().all())

    async def get_by_id(self, member_id: uuid.UUID) -> Optional[FamilyMember]:
        """Return a single FamilyMember by primary key, or None."""
        stmt = select(FamilyMember).where(FamilyMember.id == member_id)
        result = await self.session.execute(stmt)
        return result.scalar_one_or_none()

    async def update(self, member_id: uuid.UUID, data: Dict[str, Any]) -> FamilyMember:
        """Apply partial updates and return the refreshed ORM object."""
        from src.database.models import FamilyRelationship
        if "relationship" in data and isinstance(data["relationship"], str):
            data["relationship"] = FamilyRelationship(data["relationship"])

        stmt = (
            update(FamilyMember)
            .where(FamilyMember.id == member_id)
            .values(**data)
            .returning(FamilyMember)
        )
        result = await self.session.execute(stmt)
        await self.session.commit()
        updated = result.scalar_one()
        logger.debug("FamilyMember updated: id=%s", member_id)
        return updated

    async def delete(self, member_id: uuid.UUID) -> None:
        """Delete a family member row by primary key."""
        stmt = delete(FamilyMember).where(FamilyMember.id == member_id)
        await self.session.execute(stmt)
        await self.session.commit()
        logger.debug("FamilyMember deleted: id=%s", member_id)

    async def get_member_analyses(
        self, member_id: uuid.UUID, limit: int = 50
    ) -> List[AnalysisRecord]:
        """Return AnalysisRecords tagged with this family member, newest first."""
        stmt = (
            select(AnalysisRecord)
            .where(AnalysisRecord.family_member_id == member_id)
            .order_by(AnalysisRecord.created_at.desc())
            .limit(limit)
        )
        result = await self.session.execute(stmt)
        return list(result.scalars().all())
