import uuid
from typing import List, Optional
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, update, delete
from src.database.models import User

class UserRepository:
    def __init__(self, session: AsyncSession):
        self.session = session

    async def create(self, user_data: dict) -> User:
        user = User(**user_data)
        self.session.add(user)
        await self.session.commit()
        await self.session.refresh(user)
        return user

    async def get_by_id(self, user_id: uuid.UUID) -> Optional[User]:
        stmt = select(User).where(User.id == user_id)
        result = await self.session.execute(stmt)
        return result.scalar_one_or_none()

    async def get_by_email(self, email: str) -> Optional[User]:
        stmt = select(User).where(User.email == email)
        result = await self.session.execute(stmt)
        return result.scalar_one_or_none()

    async def update(self, user_id: uuid.UUID, update_data: dict) -> Optional[User]:
        stmt = update(User).where(User.id == user_id).values(**update_data).returning(User)
        result = await self.session.execute(stmt)
        await self.session.commit()
        return result.scalar_one_or_none()

    async def delete(self, user_id: uuid.UUID) -> bool:
        stmt = delete(User).where(User.id == user_id)
        result = await self.session.execute(stmt)
        await self.session.commit()
        return result.rowcount > 0

    async def list_all(self, limit: int = 100, offset: int = 0) -> List[User]:
        stmt = select(User).limit(limit).offset(offset)
        result = await self.session.execute(stmt)
        return list(result.scalars().all())
