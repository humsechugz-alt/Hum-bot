"""Tests for Chat API endpoints."""

import pytest
from fastapi.testclient import TestClient

from app.main import app


@pytest.fixture
def client() -> TestClient:
    return TestClient(app)


def test_send_message(client: TestClient) -> None:
    """Test sending a chat message and receiving AI response."""
    response = client.post(
        "/api/v1/chat/message",
        json={
            "message": "Hello HUGZ AI!",
            "personality": "friendly",
            "language": "en",
        },
    )
    assert response.status_code == 200
    data = response.json()
    assert "conversation_id" in data
    assert "message" in data
    assert data["message"]["role"] == "assistant"
    assert len(data["message"]["content"]) > 0


def test_send_message_with_emotion(client: TestClient) -> None:
    """Test chat message includes emotion detection."""
    response = client.post(
        "/api/v1/chat/message",
        json={
            "message": "I'm so excited about this project!",
            "include_emotion": True,
        },
    )
    assert response.status_code == 200
    data = response.json()
    assert "emotion" in data
    assert data["emotion"]["label"] in ("excited", "happy")
    assert data["emotion"]["confidence"] > 0


def test_create_conversation(client: TestClient) -> None:
    """Test creating a new conversation."""
    response = client.post(
        "/api/v1/chat/conversations",
        json={"title": "Test Conversation", "personality": "professional"},
    )
    assert response.status_code == 201
    data = response.json()
    assert data["title"] == "Test Conversation"
    assert data["personality"] == "professional"
    assert data["is_active"] is True


def test_list_conversations(client: TestClient) -> None:
    """Test listing conversations."""
    response = client.get("/api/v1/chat/conversations")
    assert response.status_code == 200
    data = response.json()
    assert isinstance(data, list)
