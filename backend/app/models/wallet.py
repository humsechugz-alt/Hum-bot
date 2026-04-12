"""Wallet and Transaction database models."""

import uuid
from datetime import UTC, datetime
from decimal import Decimal
from enum import StrEnum

from sqlalchemy import DateTime, ForeignKey, Index, Numeric, String, Text
from sqlalchemy.dialects.postgresql import JSONB, UUID
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.core.database import Base


class TransactionType(StrEnum):
    """Transaction types."""

    DEPOSIT = "deposit"
    WITHDRAWAL = "withdrawal"
    SUBSCRIPTION = "subscription"
    API_USAGE = "api_usage"
    MARKETPLACE = "marketplace"
    REFERRAL_REWARD = "referral_reward"
    TRANSFER = "transfer"
    REFUND = "refund"


class TransactionStatus(StrEnum):
    """Transaction statuses."""

    PENDING = "pending"
    COMPLETED = "completed"
    FAILED = "failed"
    CANCELLED = "cancelled"
    REFUNDED = "refunded"


class Wallet(Base):
    """User wallet for HUGZ Credits."""

    __tablename__ = "wallets"

    id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    user_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), ForeignKey("users.id", ondelete="CASCADE"), unique=True, nullable=False
    )
    balance: Mapped[Decimal] = mapped_column(
        Numeric(precision=12, scale=2), default=Decimal("0.00"), nullable=False
    )
    currency: Mapped[str] = mapped_column(String(3), default="USD", nullable=False)
    is_active: Mapped[bool] = mapped_column(default=True, nullable=False)

    # Limits
    daily_limit: Mapped[Decimal] = mapped_column(
        Numeric(precision=12, scale=2), default=Decimal("1000.00"), nullable=False
    )
    monthly_limit: Mapped[Decimal] = mapped_column(
        Numeric(precision=12, scale=2), default=Decimal("10000.00"), nullable=False
    )

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
    user: Mapped["User"] = relationship(back_populates="wallet")  # type: ignore[name-defined]  # noqa: F821
    transactions: Mapped[list["Transaction"]] = relationship(
        back_populates="wallet", lazy="selectin"
    )

    def __repr__(self) -> str:
        return f"<Wallet {self.user_id} balance={self.balance}>"


class Transaction(Base):
    """Financial transaction record."""

    __tablename__ = "transactions"

    id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    wallet_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), ForeignKey("wallets.id", ondelete="CASCADE"), nullable=False
    )
    transaction_type: Mapped[str] = mapped_column(String(30), nullable=False)
    status: Mapped[str] = mapped_column(
        String(20), default=TransactionStatus.PENDING, nullable=False
    )
    amount: Mapped[Decimal] = mapped_column(Numeric(precision=12, scale=2), nullable=False)
    currency: Mapped[str] = mapped_column(String(3), default="USD", nullable=False)
    description: Mapped[str | None] = mapped_column(Text, nullable=True)

    # Reference
    reference_id: Mapped[str | None] = mapped_column(String(100), nullable=True, index=True)
    external_id: Mapped[str | None] = mapped_column(String(200), nullable=True)

    # Metadata
    metadata_json: Mapped[dict | None] = mapped_column(JSONB, nullable=True)
    ip_address: Mapped[str | None] = mapped_column(String(45), nullable=True)

    # Fraud Detection
    risk_score: Mapped[float | None] = mapped_column(nullable=True)
    is_flagged: Mapped[bool] = mapped_column(default=False, nullable=False)

    # Timestamps
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), default=lambda: datetime.now(UTC), nullable=False
    )
    completed_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True), nullable=True)

    # Relationships
    wallet: Mapped["Wallet"] = relationship(back_populates="transactions")

    __table_args__ = (
        Index("idx_transactions_wallet", "wallet_id", "created_at"),
        Index("idx_transactions_type_status", "transaction_type", "status"),
        Index("idx_transactions_flagged", "is_flagged"),
    )

    def __repr__(self) -> str:
        return f"<Transaction {self.id} {self.transaction_type} {self.amount}>"
