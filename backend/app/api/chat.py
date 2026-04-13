"""Chat and conversation API endpoints."""

import uuid
from datetime import UTC, datetime

from fastapi import APIRouter, HTTPException, status

from app.schemas.conversation import (
    ChatRequest,
    ConversationCreate,
    ConversationDetailResponse,
    ConversationResponse,
    MessageResponse,
)
from app.services.ai_brain import generate_ai_response

router = APIRouter(prefix="/chat", tags=["Chat & AI"])

# In-memory conversation store for demo (replaced by database in production)
_conversations: dict[str, dict] = {}
_messages: dict[str, list[dict]] = {}


@router.post(
    "/conversations", response_model=ConversationResponse, status_code=status.HTTP_201_CREATED
)
async def create_conversation(data: ConversationCreate) -> ConversationResponse:
    """Create a new conversation."""
    conv_id = str(uuid.uuid4())
    user_id = str(uuid.uuid4())  # In production, from auth token
    now = datetime.now(UTC)

    conversation = {
        "id": conv_id,
        "user_id": user_id,
        "title": data.title,
        "summary": None,
        "is_active": True,
        "message_count": 0,
        "personality": data.personality,
        "language": data.language,
        "created_at": now,
        "updated_at": now,
    }
    _conversations[conv_id] = conversation
    _messages[conv_id] = []

    return ConversationResponse(**conversation)


@router.get("/conversations", response_model=list[ConversationResponse])
async def list_conversations() -> list[ConversationResponse]:
    """List all conversations for the current user."""
    return [ConversationResponse(**conv) for conv in _conversations.values()]


@router.get("/conversations/{conversation_id}", response_model=ConversationDetailResponse)
async def get_conversation(conversation_id: str) -> ConversationDetailResponse:
    """Get a conversation with all messages."""
    conv = _conversations.get(conversation_id)
    if not conv:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Conversation not found")

    messages = _messages.get(conversation_id, [])
    return ConversationDetailResponse(
        **conv,
        messages=[MessageResponse(**m) for m in messages],
    )


@router.post("/message", response_model=dict)
async def send_message(request: ChatRequest) -> dict:
    """Send a message and get an AI response.

    This is the primary chat endpoint that:
    1. Creates a conversation if none exists
    2. Stores the user message
    3. Generates an AI response with emotion detection
    4. Returns both the response and emotion analysis
    """
    # Get or create conversation
    conv_id = str(request.conversation_id) if request.conversation_id else str(uuid.uuid4())

    if conv_id not in _conversations:
        now = datetime.now(UTC)
        _conversations[conv_id] = {
            "id": conv_id,
            "user_id": str(uuid.uuid4()),
            "title": request.message[:50] + "..." if len(request.message) > 50 else request.message,
            "summary": None,
            "is_active": True,
            "message_count": 0,
            "personality": request.personality,
            "language": request.language,
            "created_at": now,
            "updated_at": now,
        }
        _messages[conv_id] = []

    # Store user message
    user_msg_id = str(uuid.uuid4())
    user_message = {
        "id": user_msg_id,
        "conversation_id": conv_id,
        "role": "user",
        "content": request.message,
        "has_voice": False,
        "voice_url": None,
        "detected_emotion": None,
        "emotion_confidence": None,
        "model_used": None,
        "tokens_used": None,
        "response_time_ms": None,
        "created_at": datetime.now(UTC),
    }
    _messages[conv_id].append(user_message)

    # Build conversation history
    history = [{"role": m["role"], "content": m["content"]} for m in _messages[conv_id][-20:]]

    # Generate AI response
    ai_response = await generate_ai_response(
        user_message=request.message,
        conversation_history=history[:-1],  # Exclude the just-added user message
        personality=request.personality,
        language=request.language,
        detect_emotion=request.include_emotion,
    )

    # Store AI response message
    ai_msg_id = str(uuid.uuid4())
    ai_message = {
        "id": ai_msg_id,
        "conversation_id": conv_id,
        "role": "assistant",
        "content": ai_response.content,
        "has_voice": False,
        "voice_url": None,
        "detected_emotion": ai_response.emotion.label if ai_response.emotion else None,
        "emotion_confidence": ai_response.emotion.confidence if ai_response.emotion else None,
        "model_used": ai_response.model_used,
        "tokens_used": ai_response.tokens_used,
        "response_time_ms": ai_response.response_time_ms,
        "created_at": datetime.now(UTC),
    }
    _messages[conv_id].append(ai_message)

    # Update conversation
    _conversations[conv_id]["message_count"] = len(_messages[conv_id])
    _conversations[conv_id]["updated_at"] = datetime.now(UTC)

    # Build response
    response: dict = {
        "conversation_id": conv_id,
        "message": MessageResponse(**ai_message),
        "voice_url": None,
    }

    if ai_response.emotion:
        response["emotion"] = {
            "label": ai_response.emotion.label,
            "confidence": ai_response.emotion.confidence,
            "all_emotions": ai_response.emotion.all_emotions,
        }

    return response


@router.delete("/conversations/{conversation_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_conversation(conversation_id: str) -> None:
    """Delete a conversation and all its messages."""
    if conversation_id not in _conversations:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Conversation not found")

    del _conversations[conversation_id]
    _messages.pop(conversation_id, None)
