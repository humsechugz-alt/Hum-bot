"""Voice Processor — Speech-to-text and text-to-speech service."""

import io
import tempfile
from dataclasses import dataclass
from pathlib import Path

from app.core.config import settings


@dataclass
class STTResult:
    """Speech-to-text result."""

    text: str
    language: str
    confidence: float
    duration_ms: int


@dataclass
class TTSResult:
    """Text-to-speech result."""

    audio_data: bytes
    format: str  # mp3, wav
    duration_ms: int
    voice_used: str


async def speech_to_text(
    audio_data: bytes,
    language: str = "en",
) -> STTResult:
    """Convert speech audio to text using Whisper.

    In production, uses OpenAI Whisper API or local Whisper model.
    Falls back to a placeholder for demo mode.
    """
    if settings.OPENAI_API_KEY:
        return await _whisper_api_transcribe(audio_data, language)

    # Demo fallback
    return STTResult(
        text="[Voice input received — Whisper API key required for transcription]",
        language=language,
        confidence=0.0,
        duration_ms=0,
    )


async def text_to_speech(
    text: str,
    voice: str | None = None,
    language: str = "en",
) -> TTSResult:
    """Convert text to speech audio.

    Uses Edge TTS for free, high-quality voice synthesis.
    Falls back to a placeholder for demo mode.
    """
    voice = voice or settings.TTS_VOICE

    try:
        return await _edge_tts_synthesize(text, voice)
    except Exception:
        # Fallback: return empty audio with metadata
        return TTSResult(
            audio_data=b"",
            format="mp3",
            duration_ms=0,
            voice_used=voice,
        )


async def _whisper_api_transcribe(audio_data: bytes, language: str) -> STTResult:
    """Transcribe audio using OpenAI Whisper API."""
    try:
        import openai

        client = openai.AsyncOpenAI(api_key=settings.OPENAI_API_KEY)

        # Write audio to temp file (Whisper API requires file-like object)
        with tempfile.NamedTemporaryFile(suffix=".wav", delete=False) as tmp:
            tmp.write(audio_data)
            tmp_path = Path(tmp.name)

        with open(tmp_path, "rb") as audio_file:
            transcript = await client.audio.transcriptions.create(
                model="whisper-1",
                file=audio_file,
                language=language,
                response_format="verbose_json",
            )

        tmp_path.unlink(missing_ok=True)

        return STTResult(
            text=transcript.text,
            language=transcript.language or language,
            confidence=0.95,  # Whisper doesn't return confidence per-segment easily
            duration_ms=int(transcript.duration * 1000) if transcript.duration else 0,
        )
    except Exception as e:
        return STTResult(
            text=f"[Transcription error: {e}]",
            language=language,
            confidence=0.0,
            duration_ms=0,
        )


async def _edge_tts_synthesize(text: str, voice: str) -> TTSResult:
    """Synthesize speech using Edge TTS (free Microsoft voices)."""
    try:
        import edge_tts

        communicate = edge_tts.Communicate(text, voice)
        audio_buffer = io.BytesIO()

        async for chunk in communicate.stream():
            if chunk["type"] == "audio":
                audio_buffer.write(chunk["data"])

        audio_data = audio_buffer.getvalue()
        # Rough estimate: ~150 words per minute, 200ms per word
        word_count = len(text.split())
        estimated_duration = int(word_count * 400)  # ms

        return TTSResult(
            audio_data=audio_data,
            format="mp3",
            duration_ms=estimated_duration,
            voice_used=voice,
        )
    except ImportError:
        return TTSResult(
            audio_data=b"",
            format="mp3",
            duration_ms=0,
            voice_used=voice,
        )


def get_available_voices() -> list[dict[str, str]]:
    """Get list of available TTS voices."""
    return [
        {"id": "en-US-AriaNeural", "name": "Aria", "language": "en-US", "gender": "Female"},
        {"id": "en-US-GuyNeural", "name": "Guy", "language": "en-US", "gender": "Male"},
        {"id": "en-US-JennyNeural", "name": "Jenny", "language": "en-US", "gender": "Female"},
        {"id": "en-GB-SoniaNeural", "name": "Sonia", "language": "en-GB", "gender": "Female"},
        {"id": "en-GB-RyanNeural", "name": "Ryan", "language": "en-GB", "gender": "Male"},
        {"id": "es-ES-ElviraNeural", "name": "Elvira", "language": "es-ES", "gender": "Female"},
        {"id": "fr-FR-DeniseNeural", "name": "Denise", "language": "fr-FR", "gender": "Female"},
        {"id": "de-DE-KatjaNeural", "name": "Katja", "language": "de-DE", "gender": "Female"},
        {"id": "ja-JP-NanamiNeural", "name": "Nanami", "language": "ja-JP", "gender": "Female"},
        {"id": "zh-CN-XiaoxiaoNeural", "name": "Xiaoxiao", "language": "zh-CN", "gender": "Female"},
        {"id": "ar-SA-ZariyahNeural", "name": "Zariyah", "language": "ar-SA", "gender": "Female"},
        {"id": "hi-IN-SwaraNeural", "name": "Swara", "language": "hi-IN", "gender": "Female"},
        {
            "id": "pt-BR-FranciscaNeural",
            "name": "Francisca",
            "language": "pt-BR",
            "gender": "Female",
        },
        {"id": "ko-KR-SunHiNeural", "name": "SunHi", "language": "ko-KR", "gender": "Female"},
    ]
