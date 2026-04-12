"""Conversation and message API schemas."""

import uuid
from datetime import datetime

from pydantic import BaseModel, Field


class EmotionResponse(BaseModel):
    """Schema for emotion detection result."""

    label: str
    confidence: float
    all_emotions: dict[str, float] = {}


class MessageCreate(BaseModel):
    """Schema for sending a message."""

    content: str = Field(min_length=1, max_length=10000)
    has_voice: bool = False
    voice_url: str | None = None


class MessageResponse(BaseModel):
    """Schema for message response."""

    id: uuid.UUID
    conversation_id: uuid.UUID
    role: str
    content: str
    has_voice: bool
    voice_url: str | None = None
    detected_emotion: str | None = None
    emotion_confidence: float | None = None
    model_used: str | None = None
    tokens_used: int | None = None
    response_time_ms: int | None = None
    created_at: datetime

    model_config = {"from_attributes": True}


class ConversationCreate(BaseModel):
    """Schema for creating a conversation."""

    title: str = Field(default="New Conversation", max_length=200)
    personality: str = Field(default="friendly", max_length=50)
    language: str = Field(default="en", max_length=10)


class ConversationResponse(BaseModel):
    """Schema for conversation response."""

    id: uuid.UUID
    user_id: uuid.UUID
    title: str
    summary: str | None = None
    is_active: bool
    message_count: int
    personality: str
    language: str
    created_at: datetime
    updated_at: datetime

    model_config = {"from_attributes": True}


class ConversationDetailResponse(ConversationResponse):
    """Schema for conversation with messages."""

    messages: list[MessageResponse] = []


class ChatRequest(BaseModel):
    """Schema for chat request with full context."""

    message: str = Field(min_length=1, max_length=10000)
    conversation_id: uuid.UUID | None = None
    personality: str = Field(default="friendly", max_length=50)
    language: str = Field(default="en", max_length=10)
    include_emotion: bool = True
    include_voice: bool = False
    voice_preference: str = Field(default="en-US-AriaNeural", max_length=50)


class ChatResponse(BaseModel):
    """Schema for chat response."""

    message: MessageResponse
    conversation_id: uuid.UUID
    emotion: EmotionResponse | None = None
    voice_url: str | None = None
