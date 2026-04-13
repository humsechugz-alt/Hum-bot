"""Health check and system status endpoints."""

import platform
import time
from datetime import UTC, datetime

from fastapi import APIRouter

from app.core.config import settings

router = APIRouter(tags=["Health"])

_start_time = time.time()


@router.get("/health")
async def health_check() -> dict:
    """Basic health check endpoint."""
    return {
        "status": "healthy",
        "service": settings.APP_NAME,
        "version": settings.APP_VERSION,
        "timestamp": datetime.now(UTC).isoformat(),
    }


@router.get("/health/detailed")
async def detailed_health() -> dict:
    """Detailed system health with component status."""
    uptime = time.time() - _start_time

    return {
        "status": "healthy",
        "service": settings.APP_NAME,
        "version": settings.APP_VERSION,
        "environment": settings.ENVIRONMENT,
        "uptime_seconds": round(uptime, 2),
        "timestamp": datetime.now(UTC).isoformat(),
        "system": {
            "python_version": platform.python_version(),
            "platform": platform.platform(),
            "architecture": platform.machine(),
        },
        "components": {
            "api": {"status": "healthy"},
            "ai_brain": {
                "status": "healthy" if settings.OPENAI_API_KEY else "degraded",
                "model": settings.OPENAI_MODEL,
                "note": "Running in demo mode" if not settings.OPENAI_API_KEY else "Connected",
            },
            "voice": {
                "status": "healthy",
                "stt_engine": "whisper",
                "tts_engine": settings.TTS_ENGINE,
            },
            "security": {
                "status": "healthy",
                "encryption": "AES-256-GCM",
                "auth": "JWT + OAuth2",
            },
        },
    }
