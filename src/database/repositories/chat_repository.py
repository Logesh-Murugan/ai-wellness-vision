import uuid
from typing import List
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from src.database.models import Conversation, ChatMessage
from src.security.encryption import EncryptionService


class ChatRepository:
    def __init__(self, session: AsyncSession, encryption_service: EncryptionService = None):
        self.session = session
        self.encryption_service = encryption_service or EncryptionService()

    async def create_conversation(self, conversation_data: dict) -> Conversation:
        conversation = Conversation(**conversation_data)
        self.session.add(conversation)
        await self.session.commit()
        await self.session.refresh(conversation)
        return conversation

    async def add_message(self, message_data: dict) -> ChatMessage:
        # ENCRYPT content before storing
        original_content = None
        if "content" in message_data:
            original_content = message_data["content"]
            # FIX: use correct method name from EncryptionService
            message_data["content"] = self.encryption_service.encrypt_data_at_rest(
                original_content, storage_key="chat"
            )

        message = ChatMessage(**message_data)
        self.session.add(message)
        await self.session.commit()
        await self.session.refresh(message)

        # Return with DECRYPTED content so caller gets readable text
        if original_content is not None:
            message.content = original_content
        return message

    async def get_history(
        self, conversation_id: uuid.UUID, limit: int = 50
    ) -> List[ChatMessage]:
        stmt = (
            select(ChatMessage)
            .where(ChatMessage.conversation_id == conversation_id)
            .order_by(ChatMessage.created_at.asc())
            .limit(limit)
        )
        result = await self.session.execute(stmt)
        messages = list(result.scalars().all())

        # DECRYPT each message content on read
        for msg in messages:
            try:
                # FIX: use correct method name from EncryptionService
                msg.content = self.encryption_service.decrypt_data_at_rest(msg.content)
            except Exception:
                # FIX: corrected corrupted em dash character
                msg.content = "[Encrypted message — decryption failed]"

        return messages