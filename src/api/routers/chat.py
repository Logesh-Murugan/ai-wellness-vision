"""
Chat router – conversations, messages, WebSocket.

All REST endpoints are prefixed with ``/api/v1/chat`` and tagged ``chat``.
The WebSocket endpoint lives at ``/ws``.
"""

import json
import logging
import uuid
from datetime import datetime
from typing import Any, Dict, List, Optional

from fastapi import APIRouter, Depends, HTTPException, Query, WebSocket, WebSocketDisconnect, status

from src.api.dependencies import get_db, get_optional_user
from src.database.postgres_auth import PostgresAuthDatabase
from src.models.api_schemas import (
    ChatMessageResponse,
    ChatRequest,
    ConversationResponse,
    CreateConversationRequest,
    PaginatedMessages,
)
from src.services.chat_service import generate_health_response

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/api/v1/chat", tags=["chat"])


# ──────────────────────────────────────────────
# WebSocket connection manager (module-level singleton)
# ──────────────────────────────────────────────

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
                pass  # dead connection; will be cleaned up on next disconnect


manager = ConnectionManager()


# ──────────────────────────────────────────────
# Conversations
# ──────────────────────────────────────────────

@router.get("/conversations", response_model=List[ConversationResponse])
async def get_conversations(
    db: PostgresAuthDatabase = Depends(get_db),
    current_user: Optional[Dict[str, Any]] = Depends(get_optional_user),
) -> List[ConversationResponse]:
    """List all conversations for the current user."""
    user_id = current_user["id"] if current_user else None
    rows = await db.get_conversations(user_id=user_id)
    return [ConversationResponse(**r) for r in rows]


@router.post("/conversations", response_model=ConversationResponse, status_code=status.HTTP_201_CREATED)
async def create_conversation(
    request: CreateConversationRequest,
    db: PostgresAuthDatabase = Depends(get_db),
    current_user: Optional[Dict[str, Any]] = Depends(get_optional_user),
) -> ConversationResponse:
    """Create a new chat conversation."""
    user_id = current_user["id"] if current_user else None
    conv = await db.save_conversation(user_id=user_id, title=request.title, mode=request.mode)
    if not conv:
        raise HTTPException(status_code=500, detail="Failed to create conversation")
    return ConversationResponse(**conv)


# ──────────────────────────────────────────────
# Messages
# ──────────────────────────────────────────────

@router.get("/conversations/{conversation_id}/messages", response_model=PaginatedMessages)
async def get_conversation_messages(
    conversation_id: str,
    page: int = Query(1, ge=1),
    limit: int = Query(50, ge=1, le=200),
    db: PostgresAuthDatabase = Depends(get_db),
) -> PaginatedMessages:
    """Return paginated messages for a conversation."""
    data = await db.get_messages_paginated(conversation_id=conversation_id, page=page, limit=limit)
    return PaginatedMessages(**data)


@router.post("/message", response_model=ChatMessageResponse)
async def send_chat_message(
    request: ChatRequest,
    db: PostgresAuthDatabase = Depends(get_db),
    current_user: Optional[Dict[str, Any]] = Depends(get_optional_user),
) -> ChatMessageResponse:
    """Send a message and receive an AI-generated health response.

    Both the user message and the AI reply are persisted to the database.
    The AI reply is also broadcast to any active WebSocket connections.
    """
    # 1. Persist user message
    await db.save_message(
        conversation_id=request.conversation_id,
        content=request.message,
        is_user=True,
    )

    # 2. Generate AI response
    ai_text = await generate_health_response(request.message)

    # 3. Persist AI message
    ai_msg = await db.save_message(
        conversation_id=request.conversation_id,
        content=ai_text,
        is_user=False,
    )

    response = ChatMessageResponse(
        id=ai_msg["id"] if ai_msg else str(uuid.uuid4()),
        content=ai_text,
        is_user=False,
        timestamp=ai_msg["timestamp"] if ai_msg else datetime.now().isoformat(),
    )

    # 4. Broadcast to WebSocket clients
    await manager.broadcast(json.dumps(response.model_dump()))

    logger.info("Chat message processed successfully")
    return response


# ──────────────────────────────────────────────
# WebSocket
# ──────────────────────────────────────────────

@router.websocket("/ws")
async def websocket_endpoint(websocket: WebSocket) -> None:
    """Real-time WebSocket channel for chat messages."""
    await manager.connect(websocket)
    try:
        while True:
            data = await websocket.receive_text()
            # Generate a response and echo back
            ai_text = await generate_health_response(data)
            await manager.send_personal(ai_text, websocket)
    except WebSocketDisconnect:
        manager.disconnect(websocket)
