import uuid
from typing import List, Optional
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from src.database.models import Conversation, ChatMessage

class ChatRepository:
    def __init__(self, session: AsyncSession):
        self.session = session

    async def create_conversation(self, conversation_data: dict) -> Conversation:
        conversation = Conversation(**conversation_data)
        self.session.add(conversation)
        await self.session.commit()
        await self.session.refresh(conversation)
        return conversation

    async def add_message(self, message_data: dict) -> ChatMessage:
        message = ChatMessage(**message_data)
        self.session.add(message)
        await self.session.commit()
        await self.session.refresh(message)
        return message

    async def get_history(self, conversation_id: uuid.UUID, limit: int = 50) -> List[ChatMessage]:
        stmt = (
            select(ChatMessage)
            .where(ChatMessage.conversation_id == conversation_id)
            .order_by(ChatMessage.created_at.asc())
            .limit(limit)
        )
        result = await self.session.execute(stmt)
        return list(result.scalars().all())
