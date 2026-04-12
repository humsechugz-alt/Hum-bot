"""Conversation and Message database models."""

import uuid
from datetime import UTC, datetime
from enum import StrEnum

from sqlalchemy import DateTime, ForeignKey, Index, Integer, String, Text
from sqlalchemy.dialects.postgresql import JSONB, UUID
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.core.database import Base


class MessageRole(StrEnum):
    """Message sender role."""

    USER = "user"
    ASSISTANT = "assistant"
    SYSTEM = "system"


class EmotionLabel(StrEnum):
    """Detected emotion labels."""

    NEUTRAL = "neutral"
    HAPPY = "happy"
    SAD = "sad"
    ANGRY = "angry"
    SURPRISED = "surprised"
    FEARFUL = "fearful"
    DISGUSTED = "disgusted"
    EXCITED = "excited"
    CONFUSED = "confused"


class Conversation(Base):
    """Conversation session model."""

    __tablename__ = "conversations"

    id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    user_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), ForeignKey("users.id", ondelete="CASCADE"), nullable=False
    )
    title: Mapped[str] = mapped_column(String(200), default="New Conversation", nullable=False)
    summary: Mapped[str | None] = mapped_column(Text, nullable=True)
    is_active: Mapped[bool] = mapped_column(default=True, nullable=False)
    message_count: Mapped[int] = mapped_column(Integer, default=0, nullable=False)

    # AI Context
    personality: Mapped[str] = mapped_column(String(50), default="friendly", nullable=False)
    language: Mapped[str] = mapped_column(String(10), default="en", nullable=False)
    context_metadata: Mapped[dict | None] = mapped_column(JSONB, nullable=True)

    # Timestamps
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), default=lambda: datetime.now(UTC), nullable=False
    )
    updated_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        default=lambda: datetime.now(UTC),
        onupdate=lambda: datetime.now(UTC),
        nullable=False,
    )

    # Relationships
    user: Mapped["User"] = relationship(back_populates="conversations")  # type: ignore[name-defined]  # noqa: F821
    messages: Mapped[list["Message"]] = relationship(
        back_populates="conversation", lazy="selectin", order_by="Message.created_at"
    )

    __table_args__ = (
        Index("idx_conversations_user_active", "user_id", "is_active"),
        Index("idx_conversations_updated", "updated_at"),
    )

    def __repr__(self) -> str:
        return f"<Conversation {self.id} - {self.title}>"


class Message(Base):
    """Individual message in a conversation."""

    __tablename__ = "messages"

    id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    conversation_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), ForeignKey("conversations.id", ondelete="CASCADE"), nullable=False
    )
    role: Mapped[str] = mapped_column(String(20), nullable=False)
    content: Mapped[str] = mapped_column(Text, nullable=False)

    # Voice
    has_voice: Mapped[bool] = mapped_column(default=False, nullable=False)
    voice_url: Mapped[str | None] = mapped_column(String(500), nullable=True)
    voice_duration_ms: Mapped[int | None] = mapped_column(Integer, nullable=True)

    # Emotion Detection
    detected_emotion: Mapped[str | None] = mapped_column(String(20), nullable=True)
    emotion_confidence: Mapped[float | None] = mapped_column(nullable=True)
    emotion_metadata: Mapped[dict | None] = mapped_column(JSONB, nullable=True)

    # AI Metadata
    model_used: Mapped[str | None] = mapped_column(String(50), nullable=True)
    tokens_used: Mapped[int | None] = mapped_column(Integer, nullable=True)
    response_time_ms: Mapped[int | None] = mapped_column(Integer, nullable=True)

    # Timestamps
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), default=lambda: datetime.now(UTC), nullable=False
    )

    # Relationships
    conversation: Mapped["Conversation"] = relationship(back_populates="messages")

    __table_args__ = (Index("idx_messages_conversation", "conversation_id", "created_at"),)

    def __repr__(self) -> str:
        return f"<Message {self.id} ({self.role})>"
