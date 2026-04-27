import uuid
from typing import List, Optional, Dict, Any
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, func
from src.database.models import AnalysisRecord, AnalysisType

class AnalysisRepository:
    def __init__(self, session: AsyncSession):
        self.session = session

    async def create(self, analysis_data: dict) -> AnalysisRecord:
        record = AnalysisRecord(**analysis_data)
        self.session.add(record)
        await self.session.commit()
        await self.session.refresh(record)
        return record

    async def get_user_history(
        self, 
        user_id: uuid.UUID, 
        limit: int = 50, 
        offset: int = 0, 
        analysis_type: Optional[str] = None
    ) -> List[AnalysisRecord]:
        stmt = select(AnalysisRecord).where(AnalysisRecord.user_id == user_id)
        
        if analysis_type:
            stmt = stmt.where(AnalysisRecord.analysis_type == AnalysisType(analysis_type))
            
        stmt = stmt.order_by(AnalysisRecord.created_at.desc()).limit(limit).offset(offset)
        result = await self.session.execute(stmt)
        return list(result.scalars().all())

    async def get_stats(self, user_id: uuid.UUID) -> Dict[str, Any]:
        """Aggregate stats for the user's analyses."""
        stmt = (
            select(
                AnalysisRecord.analysis_type, 
                func.count(AnalysisRecord.id).label("count")
            )
            .where(AnalysisRecord.user_id == user_id)
            .group_by(AnalysisRecord.analysis_type)
        )
        result = await self.session.execute(stmt)
        
        stats = {}
        total = 0
        for row in result:
            stats[row.analysis_type.value] = row.count
            total += row.count
            
        stats["total_analyses"] = total
        return stats
