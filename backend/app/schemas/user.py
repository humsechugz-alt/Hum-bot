"""User API schemas."""

import uuid
from datetime import datetime

from pydantic import BaseModel, EmailStr, Field


class UserCreate(BaseModel):
    """Schema for user registration."""

    email: EmailStr
    username: str = Field(min_length=3, max_length=50, pattern=r"^[a-zA-Z0-9_-]+$")
    display_name: str = Field(min_length=1, max_length=100)
    password: str = Field(min_length=8, max_length=128)
    referral_code: str | None = None


class UserLogin(BaseModel):
    """Schema for user login."""

    email: EmailStr
    password: str


class UserResponse(BaseModel):
    """Schema for user response."""

    id: uuid.UUID
    email: str
    username: str
    display_name: str
    role: str
    is_active: bool
    is_verified: bool
    avatar_url: str | None = None
    language: str
    ai_personality: str
    referral_code: str | None = None
    created_at: datetime

    model_config = {"from_attributes": True}


class UserUpdate(BaseModel):
    """Schema for updating user profile."""

    display_name: str | None = Field(None, min_length=1, max_length=100)
    bio: str | None = Field(None, max_length=500)
    language: str | None = Field(None, max_length=10)
    timezone: str | None = Field(None, max_length=50)
    ai_personality: str | None = Field(None, max_length=50)
    voice_preference: str | None = Field(None, max_length=50)
    avatar_url: str | None = Field(None, max_length=500)


class TokenResponse(BaseModel):
    """Schema for authentication token response."""

    access_token: str
    refresh_token: str
    token_type: str = "bearer"
    expires_in: int
    user: UserResponse
