"""Tests for health check endpoints."""

import pytest
from fastapi.testclient import TestClient

from app.main import app


@pytest.fixture
def client() -> TestClient:
    return TestClient(app)


def test_root(client: TestClient) -> None:
    """Test root endpoint returns platform info."""
    response = client.get("/")
    assert response.status_code == 200
    data = response.json()
    assert data["name"] == "HUGZ AI"
    assert "capabilities" in data
    assert data["status"] == "operational"


def test_health_check(client: TestClient) -> None:
    """Test basic health check."""
    response = client.get("/api/v1/health")
    assert response.status_code == 200
    data = response.json()
    assert data["status"] == "healthy"
    assert data["service"] == "HUGZ AI"


def test_detailed_health(client: TestClient) -> None:
    """Test detailed health check returns component status."""
    response = client.get("/api/v1/health/detailed")
    assert response.status_code == 200
    data = response.json()
    assert data["status"] == "healthy"
    assert "components" in data
    assert "ai_brain" in data["components"]
    assert "security" in data["components"]
    assert "voice" in data["components"]
