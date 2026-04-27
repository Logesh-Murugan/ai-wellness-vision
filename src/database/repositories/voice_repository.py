import uuid
from typing import List
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from src.database.models import VoiceRecord

class VoiceRepository:
    def __init__(self, session: AsyncSession):
        self.session = session

    async def create(self, voice_data: dict) -> VoiceRecord:
        record = VoiceRecord(**voice_data)
        self.session.add(record)
        await self.session.commit()
        await self.session.refresh(record)
        return record

    async def get_user_voice_history(self, user_id: uuid.UUID, limit: int = 50, offset: int = 0) -> List[VoiceRecord]:
        stmt = (
            select(VoiceRecord)
            .where(VoiceRecord.user_id == user_id)
            .order_by(VoiceRecord.created_at.desc())
            .limit(limit)
            .offset(offset)
        )
        result = await self.session.execute(stmt)
        return list(result.scalars().all())
