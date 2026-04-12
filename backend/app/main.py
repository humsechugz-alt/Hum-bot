"""HUGZ AI — Main FastAPI Application.

Enterprise-grade AI platform with:
- Advanced AI Brain (NLP, emotion detection, learning memory)
- Voice interaction (speech-to-text, text-to-speech)
- Cybersecurity Shield (threat detection, encryption, fraud monitoring)
- Smart Automation (task scheduling, workflows, predictions)
- Revenue Engine (wallet, subscriptions, API marketplace)
"""

from collections.abc import AsyncIterator
from contextlib import asynccontextmanager

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app.api import auth, automation, chat, health, security, voice
from app.core.config import settings
from app.middleware.security import SecurityMiddleware


@asynccontextmanager
async def lifespan(app: FastAPI) -> AsyncIterator[None]:
    """Application lifespan handler for startup/shutdown."""
    # Startup
    print(f"🚀 {settings.APP_NAME} v{settings.APP_VERSION} starting...")
    print(f"   Environment: {settings.ENVIRONMENT}")
    print(f"   AI Model: {settings.OPENAI_MODEL}")
    print(f"   AI Connected: {'Yes' if settings.OPENAI_API_KEY else 'Demo Mode'}")
    print("   Security: AES-256 + TLS 1.3 + Rate Limiting")
    yield
    # Shutdown
    print(f"👋 {settings.APP_NAME} shutting down...")


app = FastAPI(
    title=settings.APP_NAME,
    description=(
        "HUGZ AI is an enterprise-grade AI platform featuring natural conversation, "
        "voice interaction, emotion detection, cybersecurity shield, smart automation, "
        "and a complete revenue ecosystem. Built to scale to 1M+ users."
    ),
    version=settings.APP_VERSION,
    docs_url="/docs",
    redoc_url="/redoc",
    openapi_url="/openapi.json",
    lifespan=lifespan,
)

# Middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.ALLOWED_ORIGINS,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)
app.add_middleware(SecurityMiddleware)

# API Routes
app.include_router(health.router, prefix=settings.API_PREFIX)
app.include_router(auth.router, prefix=settings.API_PREFIX)
app.include_router(chat.router, prefix=settings.API_PREFIX)
app.include_router(voice.router, prefix=settings.API_PREFIX)
app.include_router(security.router, prefix=settings.API_PREFIX)
app.include_router(automation.router, prefix=settings.API_PREFIX)


@app.get("/")
async def root() -> dict:
    """Root endpoint — HUGZ AI welcome."""
    return {
        "name": settings.APP_NAME,
        "version": settings.APP_VERSION,
        "tagline": "Your Intelligent AI Companion — Secure, Smart, and Human",
        "docs": "/docs",
        "health": f"{settings.API_PREFIX}/health",
        "capabilities": {
            "ai_brain": "Natural conversation with emotion detection",
            "voice": "Speech-to-text and text-to-speech",
            "security": "End-to-end encryption and threat detection",
            "automation": "Smart task scheduling and workflows",
            "revenue": "Wallet system and subscriptions",
            "multilingual": "10+ language support",
        },
        "status": "operational",
    }
