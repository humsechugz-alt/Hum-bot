"""Tests for AI Brain engine."""

import pytest

from app.services.ai_brain import (
    build_system_prompt,
    detect_emotion_from_text,
    generate_ai_response,
)


def test_emotion_detection_happy() -> None:
    """Test emotion detection for happy text."""
    result = detect_emotion_from_text("I'm so happy and excited today!")
    assert result.label in ("happy", "excited")
    assert result.confidence > 0


def test_emotion_detection_sad() -> None:
    """Test emotion detection for sad text."""
    result = detect_emotion_from_text("I'm feeling really sad and disappointed")
    assert result.label == "sad"
    assert result.confidence > 0


def test_emotion_detection_neutral() -> None:
    """Test emotion detection for neutral text."""
    result = detect_emotion_from_text("The weather is moderate today")
    assert result.label == "neutral"
    assert result.confidence == 0.8


def test_emotion_detection_angry() -> None:
    """Test emotion detection for angry text."""
    result = detect_emotion_from_text("I'm so angry and frustrated with this!")
    assert result.label == "angry"
    assert result.confidence > 0


def test_build_system_prompt_friendly() -> None:
    """Test system prompt generation for friendly personality."""
    prompt = build_system_prompt("friendly", "en")
    assert "HUGZ AI" in prompt
    assert "warm" in prompt or "friendly" in prompt


def test_build_system_prompt_professional() -> None:
    """Test system prompt generation for professional personality."""
    prompt = build_system_prompt("professional", "en")
    assert "professional" in prompt


def test_build_system_prompt_multilingual() -> None:
    """Test system prompt includes language instruction for non-English."""
    prompt = build_system_prompt("friendly", "es")
    assert "es" in prompt


@pytest.mark.asyncio
async def test_generate_ai_response_fallback() -> None:
    """Test AI response generation in fallback/demo mode."""
    response = await generate_ai_response(
        user_message="Hello, how are you?",
        conversation_history=[],
        personality="friendly",
        language="en",
    )
    assert response.content
    assert response.model_used == "hugz-fallback-v1"
    assert response.tokens_used > 0
    assert response.response_time_ms >= 0


@pytest.mark.asyncio
async def test_generate_ai_response_with_emotion() -> None:
    """Test AI response includes emotion detection."""
    response = await generate_ai_response(
        user_message="I'm so excited about this new project!",
        conversation_history=[],
        detect_emotion=True,
    )
    assert response.emotion is not None
    assert response.emotion.label in ("excited", "happy")
