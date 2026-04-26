"""
API Request/Response Pydantic schemas for AI WellnessVision.

All Pydantic models used by the FastAPI routers live here.
Domain models (dataclasses) stay in their existing files.
"""

from pydantic import BaseModel, EmailStr, Field
from typing import List, Optional, Dict, Any
from datetime import datetime


# ──────────────────────────────────────────────
# Auth schemas
# ──────────────────────────────────────────────

class LoginRequest(BaseModel):
    """Credentials submitted for login."""
    email: EmailStr
    password: str = Field(..., min_length=6, description="User password (min 6 chars)")


class RegisterRequest(BaseModel):
    """Payload for creating a new account."""
    email: EmailStr
    password: str = Field(..., min_length=6)
    firstName: Optional[str] = Field(None, max_length=100)
    lastName: Optional[str] = Field(None, max_length=100)


class RefreshTokenRequest(BaseModel):
    """Payload to refresh an access token."""
    refresh_token: str


class UserResponse(BaseModel):
    """Public user representation (never includes password_hash)."""
    id: str
    name: str
    email: str
    firstName: Optional[str] = None
    lastName: Optional[str] = None
    avatar: Optional[str] = None
    preferences: Dict[str, Any] = Field(default_factory=lambda: {
        "language": "en",
        "notifications": True,
        "theme": "light",
    })
    created_at: str


class AuthResponse(BaseModel):
    """Returned after successful login / register / refresh."""
    access_token: str
    refresh_token: str
    token_type: str = "bearer"
    expires_in: int = 3600
    user: UserResponse


# ──────────────────────────────────────────────
# Chat schemas
# ──────────────────────────────────────────────

class ChatRequest(BaseModel):
    """User message sent to the AI assistant."""
    message: str = Field(..., min_length=1, max_length=5000)
    conversation_id: str


class CreateConversationRequest(BaseModel):
    """Create a new chat conversation."""
    title: str = Field("New Conversation", max_length=200)
    mode: str = Field("general", max_length=50)


class ChatMessageResponse(BaseModel):
    """Single chat message returned to the client."""
    id: str
    content: str
    is_user: bool
    timestamp: str
    type: Optional[str] = "text"


class ConversationResponse(BaseModel):
    """A chat conversation summary."""
    id: str
    title: str
    mode: str
    created_at: str
    updated_at: str
    message_count: int = 0


class PaginationMeta(BaseModel):
    """Pagination metadata included in list responses."""
    page: int
    limit: int
    total: int
    pages: int


class PaginatedMessages(BaseModel):
    """Paginated list of chat messages."""
    messages: List[ChatMessageResponse]
    pagination: PaginationMeta


# ──────────────────────────────────────────────
# Analysis schemas
# ──────────────────────────────────────────────

class AnalysisResultResponse(BaseModel):
    """Result of an AI health analysis."""
    id: str
    type: str
    result: str
    confidence: float
    recommendations: List[str]
    timestamp: str
    image_path: Optional[str] = None
    analysis_method: Optional[str] = None


class PaginatedAnalyses(BaseModel):
    """Paginated list of analysis results."""
    results: List[AnalysisResultResponse]
    pagination: PaginationMeta


# ──────────────────────────────────────────────
# Voice schemas
# ──────────────────────────────────────────────

class SynthesizeRequest(BaseModel):
    """Request body for text-to-speech."""
    text: str = Field(..., min_length=1, max_length=5000)
    language: str = "en"
    voice: str = "female"


class TranscriptionResponse(BaseModel):
    """Result of speech-to-text."""
    transcription: str
    confidence: float
    language: str
    duration: float


class SynthesisResponse(BaseModel):
    """Result of text-to-speech."""
    audio_url: str
    text: str
    language: str
    voice: str
    duration: float


# ──────────────────────────────────────────────
# Visual QA schemas
# ──────────────────────────────────────────────

class VisualQARequest(BaseModel):
    """Question about an uploaded image."""
    question: str = Field(..., min_length=1, max_length=2000)
    context: Optional[str] = None


class VisualQAResponse(BaseModel):
    """Answer from the Visual QA system."""
    id: str
    type: str = "visual_qa"
    question: str
    answer: str
    confidence: float
    timestamp: str
    image_path: Optional[str] = None
    processing_method: Optional[str] = None
    capabilities: Optional[List[str]] = None
    error: Optional[str] = None
