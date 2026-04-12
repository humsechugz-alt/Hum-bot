"""Authentication API endpoints."""

import secrets
import uuid
from datetime import UTC, datetime

from fastapi import APIRouter, HTTPException, status

from app.core.config import settings
from app.core.security import (
    create_access_token,
    create_refresh_token,
    decode_token,
    generate_api_key,
    hash_password,
    verify_password,
)
from app.schemas.user import TokenResponse, UserCreate, UserLogin, UserResponse

router = APIRouter(prefix="/auth", tags=["Authentication"])

# In-memory user store for demo (replaced by database in production)
_users_store: dict[str, dict] = {}


@router.post("/register", response_model=TokenResponse, status_code=status.HTTP_201_CREATED)
async def register(user_data: UserCreate) -> TokenResponse:
    """Register a new user account."""
    # Check if email already exists
    if any(u["email"] == user_data.email for u in _users_store.values()):
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail="Email already registered",
        )

    # Check if username already exists
    if any(u["username"] == user_data.username for u in _users_store.values()):
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail="Username already taken",
        )

    # Create user
    user_id = str(uuid.uuid4())
    referral_code = secrets.token_urlsafe(8)

    user = {
        "id": user_id,
        "email": user_data.email,
        "username": user_data.username,
        "display_name": user_data.display_name,
        "hashed_password": hash_password(user_data.password),
        "role": "free",
        "is_active": True,
        "is_verified": False,
        "mfa_enabled": False,
        "language": "en",
        "ai_personality": "friendly",
        "voice_preference": "en-US-AriaNeural",
        "api_key": generate_api_key(),
        "referral_code": referral_code,
        "referred_by": user_data.referral_code,
        "avatar_url": None,
        "created_at": datetime.now(UTC).isoformat(),
    }
    _users_store[user_id] = user

    # Generate tokens
    token_data = {"sub": user_id, "role": user["role"]}
    access_token = create_access_token(token_data)
    refresh_token = create_refresh_token(token_data)

    return TokenResponse(
        access_token=access_token,
        refresh_token=refresh_token,
        token_type="bearer",
        expires_in=settings.ACCESS_TOKEN_EXPIRE_MINUTES * 60,
        user=UserResponse(
            id=uuid.UUID(user_id),
            email=user["email"],
            username=user["username"],
            display_name=user["display_name"],
            role=user["role"],
            is_active=user["is_active"],
            is_verified=user["is_verified"],
            language=user["language"],
            ai_personality=user["ai_personality"],
            referral_code=user["referral_code"],
            created_at=datetime.fromisoformat(user["created_at"]),
        ),
    )


@router.post("/login", response_model=TokenResponse)
async def login(credentials: UserLogin) -> TokenResponse:
    """Authenticate a user and return tokens."""
    # Find user by email
    user = None
    user_id = None
    for uid, u in _users_store.items():
        if u["email"] == credentials.email:
            user = u
            user_id = uid
            break

    if not user or not verify_password(credentials.password, user["hashed_password"]):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid email or password",
            headers={"WWW-Authenticate": "Bearer"},
        )

    if not user["is_active"]:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Account is deactivated",
        )

    # Generate tokens
    token_data = {"sub": user_id, "role": user["role"]}
    access_token = create_access_token(token_data)
    refresh_token = create_refresh_token(token_data)

    return TokenResponse(
        access_token=access_token,
        refresh_token=refresh_token,
        token_type="bearer",
        expires_in=settings.ACCESS_TOKEN_EXPIRE_MINUTES * 60,
        user=UserResponse(
            id=uuid.UUID(user_id),  # type: ignore[arg-type]
            email=user["email"],
            username=user["username"],
            display_name=user["display_name"],
            role=user["role"],
            is_active=user["is_active"],
            is_verified=user["is_verified"],
            language=user["language"],
            ai_personality=user["ai_personality"],
            referral_code=user["referral_code"],
            created_at=datetime.fromisoformat(user["created_at"]),
        ),
    )


@router.post("/refresh", response_model=dict)
async def refresh_token(refresh_token: str) -> dict:
    """Refresh an access token."""
    payload = decode_token(refresh_token)
    if not payload or payload.get("type") != "refresh":
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid refresh token",
        )

    user_id = payload.get("sub")
    user = _users_store.get(user_id)  # type: ignore[arg-type]
    if not user:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="User not found",
        )

    token_data = {"sub": user_id, "role": user["role"]}
    new_access_token = create_access_token(token_data)

    return {
        "access_token": new_access_token,
        "token_type": "bearer",
        "expires_in": settings.ACCESS_TOKEN_EXPIRE_MINUTES * 60,
    }
