"""User database model."""

import uuid
from datetime import UTC, datetime
from enum import StrEnum

from sqlalchemy import Boolean, DateTime, Index, String, Text
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.core.database import Base


class UserRole(StrEnum):
    """User roles for RBAC."""

    FREE = "free"
    PRO = "pro"
    ENTERPRISE = "enterprise"
    DEVELOPER = "developer"
    ADMIN = "admin"


class User(Base):
    """User account model."""

    __tablename__ = "users"

    id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    email: Mapped[str] = mapped_column(String(255), unique=True, nullable=False, index=True)
    username: Mapped[str] = mapped_column(String(50), unique=True, nullable=False, index=True)
    display_name: Mapped[str] = mapped_column(String(100), nullable=False)
    hashed_password: Mapped[str] = mapped_column(String(255), nullable=False)
    role: Mapped[str] = mapped_column(String(20), default=UserRole.FREE, nullable=False)
    is_active: Mapped[bool] = mapped_column(Boolean, default=True, nullable=False)
    is_verified: Mapped[bool] = mapped_column(Boolean, default=False, nullable=False)
    mfa_enabled: Mapped[bool] = mapped_column(Boolean, default=False, nullable=False)
    mfa_secret: Mapped[str | None] = mapped_column(String(255), nullable=True)

    # Profile
    avatar_url: Mapped[str | None] = mapped_column(String(500), nullable=True)
    bio: Mapped[str | None] = mapped_column(Text, nullable=True)
    language: Mapped[str] = mapped_column(String(10), default="en", nullable=False)
    timezone: Mapped[str] = mapped_column(String(50), default="UTC", nullable=False)

    # AI Preferences
    ai_personality: Mapped[str] = mapped_column(String(50), default="friendly", nullable=False)
    voice_preference: Mapped[str] = mapped_column(
        String(50), default="en-US-AriaNeural", nullable=False
    )

    # Security
    api_key: Mapped[str | None] = mapped_column(String(100), unique=True, nullable=True)
    last_login_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True), nullable=True)
    last_login_ip: Mapped[str | None] = mapped_column(String(45), nullable=True)
    failed_login_attempts: Mapped[int] = mapped_column(default=0, nullable=False)
    locked_until: Mapped[datetime | None] = mapped_column(DateTime(timezone=True), nullable=True)

    # Referral
    referral_code: Mapped[str | None] = mapped_column(
        String(20), unique=True, nullable=True, index=True
    )
    referred_by: Mapped[uuid.UUID | None] = mapped_column(UUID(as_uuid=True), nullable=True)

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
    conversations: Mapped[list["Conversation"]] = relationship(  # type: ignore[name-defined]  # noqa: F821
        back_populates="user", lazy="selectin"
    )
    wallet: Mapped["Wallet | None"] = relationship(  # type: ignore[name-defined]  # noqa: F821
        back_populates="user", uselist=False, lazy="selectin"
    )

    __table_args__ = (
        Index("idx_users_email_active", "email", "is_active"),
        Index("idx_users_role", "role"),
    )

    def __repr__(self) -> str:
        return f"<User {self.username} ({self.email})>"
