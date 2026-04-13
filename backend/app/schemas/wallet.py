"""Wallet and transaction API schemas."""

import uuid
from datetime import datetime
from decimal import Decimal

from pydantic import BaseModel, Field


class WalletResponse(BaseModel):
    """Schema for wallet response."""

    id: uuid.UUID
    user_id: uuid.UUID
    balance: Decimal
    currency: str
    is_active: bool
    daily_limit: Decimal
    monthly_limit: Decimal
    created_at: datetime

    model_config = {"from_attributes": True}


class DepositRequest(BaseModel):
    """Schema for wallet deposit."""

    amount: Decimal = Field(gt=0, le=10000, decimal_places=2)
    payment_method: str = Field(max_length=50)  # stripe, paypal, crypto
    description: str | None = None


class WithdrawalRequest(BaseModel):
    """Schema for wallet withdrawal."""

    amount: Decimal = Field(gt=0, decimal_places=2)
    destination: str = Field(max_length=200)  # bank account, paypal, etc.
    description: str | None = None


class TransferRequest(BaseModel):
    """Schema for wallet-to-wallet transfer."""

    recipient_id: uuid.UUID
    amount: Decimal = Field(gt=0, decimal_places=2)
    description: str | None = None


class TransactionResponse(BaseModel):
    """Schema for transaction response."""

    id: uuid.UUID
    wallet_id: uuid.UUID
    transaction_type: str
    status: str
    amount: Decimal
    currency: str
    description: str | None = None
    reference_id: str | None = None
    risk_score: float | None = None
    is_flagged: bool
    created_at: datetime
    completed_at: datetime | None = None

    model_config = {"from_attributes": True}


class TransactionListResponse(BaseModel):
    """Schema for paginated transaction list."""

    transactions: list[TransactionResponse]
    total: int
    page: int
    page_size: int
