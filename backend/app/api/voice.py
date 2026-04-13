"""Voice interaction API endpoints."""

from fastapi import APIRouter, HTTPException, UploadFile, status

from app.services.voice_processor import (
    get_available_voices,
    speech_to_text,
    text_to_speech,
)

router = APIRouter(prefix="/voice", tags=["Voice"])


@router.post("/transcribe")
async def transcribe_audio(file: UploadFile, language: str = "en") -> dict:
    """Transcribe audio file to text using Whisper."""
    if not file.content_type or not file.content_type.startswith("audio/"):
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="File must be an audio file",
        )

    # Check Content-Length header first to reject obviously oversized uploads
    max_size = 25 * 1024 * 1024  # 25 MB limit
    if file.size and file.size > max_size:
        raise HTTPException(
            status_code=status.HTTP_413_REQUEST_ENTITY_TOO_LARGE,
            detail="Audio file too large (max 25 MB)",
        )

    audio_data = await file.read()
    if len(audio_data) > max_size:
        raise HTTPException(
            status_code=status.HTTP_413_REQUEST_ENTITY_TOO_LARGE,
            detail="Audio file too large (max 25 MB)",
        )

    result = await speech_to_text(audio_data, language)

    return {
        "text": result.text,
        "language": result.language,
        "confidence": result.confidence,
        "duration_ms": result.duration_ms,
    }


@router.post("/synthesize")
async def synthesize_speech(
    text: str, voice: str = "en-US-AriaNeural", language: str = "en"
) -> dict:
    """Convert text to speech audio."""
    if len(text) > 5000:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Text too long (max 5000 characters)",
        )

    result = await text_to_speech(text, voice, language)

    return {
        "format": result.format,
        "duration_ms": result.duration_ms,
        "voice_used": result.voice_used,
        "audio_size_bytes": len(result.audio_data),
        "message": "Audio synthesized successfully"
        if result.audio_data
        else "TTS engine not available in demo mode",
    }


@router.get("/voices")
async def list_voices() -> dict:
    """List available TTS voices."""
    voices = get_available_voices()
    return {
        "voices": voices,
        "total": len(voices),
        "default": "en-US-AriaNeural",
    }
