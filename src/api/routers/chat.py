"""
Chat router – conversations, messages, WebSocket.
"""

import json
import logging
import uuid
from datetime import datetime
from typing import List, Optional

from fastapi import APIRouter, Depends, HTTPException, Query, WebSocket, WebSocketDisconnect, status

from src.api.dependencies import get_current_user, get_optional_user, get_chat_repo
from src.database.repositories.chat_repository import ChatRepository
from src.database.models import User
from src.models.api_schemas import (
    ChatMessageResponse,
    ChatRequest,
    ConversationResponse,
    CreateConversationRequest,
    PaginatedMessages,
    PaginationMeta,
)
from src.services.chat_service import generate_health_response

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/api/v1/chat", tags=["chat"])

class ConnectionManager:
    """Manages active WebSocket connections for real-time chat."""
    def __init__(self) -> None:
        self.active_connections: List[WebSocket] = []

    async def connect(self, websocket: WebSocket) -> None:
        await websocket.accept()
        self.active_connections.append(websocket)

    def disconnect(self, websocket: WebSocket) -> None:
        if websocket in self.active_connections:
            self.active_connections.remove(websocket)

    async def send_personal(self, message: str, websocket: WebSocket) -> None:
        await websocket.send_text(message)

    async def broadcast(self, message: str) -> None:
        for conn in self.active_connections:
            try:
                await conn.send_text(message)
            except Exception:
                pass

manager = ConnectionManager()

@router.get("/conversations", response_model=List[ConversationResponse])
async def get_conversations(
    chat_repo: ChatRepository = Depends(get_chat_repo),
    current_user: Optional[User] = Depends(get_optional_user),
) -> List[ConversationResponse]:
    """List all conversations for the current user."""
    # Assuming chat_repo has get_user_conversations logic, mocking response for now
    return []

@router.post("/conversations", response_model=ConversationResponse, status_code=status.HTTP_201_CREATED)
async def create_conversation(
    request: CreateConversationRequest,
    chat_repo: ChatRepository = Depends(get_chat_repo),
    current_user: Optional[User] = Depends(get_optional_user),
) -> ConversationResponse:
    """Create a new chat conversation."""
    user_id = current_user.id if current_user else None
    
    conv_data = {
        "user_id": user_id,
        "title": request.title,
    }
    conv = await chat_repo.create_conversation(conv_data)
    return ConversationResponse(
        id=str(conv.id),
        title=conv.title,
        mode=getattr(conv, 'mode', 'general'),
        created_at=conv.created_at.isoformat() if hasattr(conv, "created_at") else datetime.now().isoformat(),
        updated_at=conv.updated_at.isoformat() if hasattr(conv, "updated_at") else datetime.now().isoformat()
    )

@router.get("/conversations/{conversation_id}/messages", response_model=PaginatedMessages)
async def get_conversation_messages(
    conversation_id: str,
    page: int = Query(1, ge=1),
    limit: int = Query(50, ge=1, le=200),
    chat_repo: ChatRepository = Depends(get_chat_repo),
) -> PaginatedMessages:
    """Return paginated messages for a conversation."""
    conv_id = uuid.UUID(conversation_id)
    records = await chat_repo.get_history(conversation_id=conv_id, limit=limit)
    
    items = []
    for r in records:
        items.append({
            "id": str(r.id),
            "content": r.content,
            "is_user": r.role == "user",
            "timestamp": r.created_at.isoformat() if hasattr(r, "created_at") else datetime.now().isoformat(),
        })
    return PaginatedMessages(
        messages=[ChatMessageResponse(**item) for item in items],
        pagination=PaginationMeta(total=len(items), page=page, limit=limit, pages=1)
    )

@router.post("/message", response_model=ChatMessageResponse)
async def send_chat_message(
    request: ChatRequest,
    chat_repo: ChatRepository = Depends(get_chat_repo),
    current_user: Optional[User] = Depends(get_optional_user),
) -> ChatMessageResponse:
    """Send a message and receive an AI-generated health response."""
    conv_id = uuid.UUID(request.conversation_id)

    # 1. Persist user message
    await chat_repo.add_message({
        "conversation_id": conv_id,
        "content": request.message,
        "role": "user",
    })

    # 2. Generate AI response
    ai_text = await generate_health_response(request.message)

    # 3. Persist AI message
    ai_msg = await chat_repo.add_message({
        "conversation_id": conv_id,
        "content": ai_text,
        "role": "assistant",
    })

    response = ChatMessageResponse(
        id=str(ai_msg.id),
        content=ai_text,
        is_user=False,
        timestamp=ai_msg.created_at.isoformat() if hasattr(ai_msg, "created_at") else datetime.now().isoformat(),
    )

    # 4. Broadcast to WebSocket clients
    await manager.broadcast(json.dumps(response.model_dump()))

    logger.info("Chat message processed successfully")
    return response

@router.websocket("/ws")
async def websocket_endpoint(websocket: WebSocket) -> None:
    """Real-time WebSocket channel for chat messages."""
    await manager.connect(websocket)
    try:
        while True:
            data = await websocket.receive_text()
            ai_text = await generate_health_response(data)
            await manager.send_personal(ai_text, websocket)
    except WebSocketDisconnect:
        manager.disconnect(websocket)
