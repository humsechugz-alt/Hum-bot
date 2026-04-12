"""AI Brain Engine — Core conversational intelligence service."""

import time
from dataclasses import dataclass

from app.core.config import settings


@dataclass
class EmotionResult:
    """Result of emotion detection."""

    label: str
    confidence: float
    all_emotions: dict[str, float]


@dataclass
class AIResponse:
    """Response from the AI brain."""

    content: str
    model_used: str
    tokens_used: int
    response_time_ms: int
    emotion: EmotionResult | None = None


# System prompts for different personality modes
PERSONALITY_PROMPTS: dict[str, str] = {
    "friendly": (
        "You are HUGZ AI, a warm, friendly, and emotionally intelligent assistant. "
        "You respond with empathy, encouragement, and genuine care. You use a conversational "
        "tone while remaining helpful and professional. You remember context from the "
        "conversation and build rapport with the user."
    ),
    "professional": (
        "You are HUGZ AI, a professional enterprise assistant. You provide concise, "
        "accurate, and well-structured responses. You focus on efficiency and clarity "
        "while maintaining a respectful and courteous demeanor."
    ),
    "creative": (
        "You are HUGZ AI, a creative and imaginative assistant. You think outside the box, "
        "offer unique perspectives, and help users brainstorm and innovate. You use vivid "
        "language and creative analogies while staying grounded and helpful."
    ),
    "technical": (
        "You are HUGZ AI, a technical expert assistant. You provide detailed, accurate "
        "technical explanations with code examples when relevant. You break down complex "
        "concepts clearly and suggest best practices."
    ),
    "supportive": (
        "You are HUGZ AI, a supportive and compassionate assistant. You prioritize emotional "
        "well-being, offer encouragement, and help users work through challenges. You listen "
        "actively and validate feelings while gently guiding toward solutions."
    ),
}

# Emotion keywords for basic text-based emotion detection
EMOTION_KEYWORDS: dict[str, list[str]] = {
    "happy": [
        "happy",
        "glad",
        "great",
        "awesome",
        "wonderful",
        "excited",
        "love",
        "joy",
        "amazing",
        "fantastic",
    ],
    "sad": [
        "sad",
        "unhappy",
        "depressed",
        "down",
        "disappointed",
        "upset",
        "miserable",
        "sorry",
        "lonely",
        "cry",
    ],
    "angry": [
        "angry",
        "furious",
        "mad",
        "annoyed",
        "frustrated",
        "irritated",
        "hate",
        "rage",
        "outraged",
    ],
    "surprised": [
        "surprised",
        "shocked",
        "amazed",
        "unexpected",
        "wow",
        "incredible",
        "unbelievable",
        "astonished",
    ],
    "fearful": [
        "scared",
        "afraid",
        "worried",
        "anxious",
        "nervous",
        "terrified",
        "panic",
        "fear",
        "frightened",
    ],
    "confused": [
        "confused",
        "puzzled",
        "lost",
        "unclear",
        "don't understand",
        "what do you mean",
        "help me understand",
    ],
    "excited": [
        "excited",
        "thrilled",
        "can't wait",
        "pumped",
        "eager",
        "hyped",
        "stoked",
        "looking forward",
    ],
}


def detect_emotion_from_text(text: str) -> EmotionResult:
    """Detect emotion from text using keyword analysis.

    In production, this would use a fine-tuned BERT model.
    This is a rule-based fallback for the initial release.
    """
    text_lower = text.lower()
    scores: dict[str, float] = {}

    for emotion, keywords in EMOTION_KEYWORDS.items():
        score = sum(1 for keyword in keywords if keyword in text_lower)
        scores[emotion] = score

    total = sum(scores.values())
    if total == 0:
        return EmotionResult(
            label="neutral",
            confidence=0.8,
            all_emotions={"neutral": 0.8},
        )

    # Normalize scores
    normalized = {k: v / total for k, v in scores.items()}
    top_emotion = max(normalized, key=lambda k: normalized[k])
    confidence = normalized[top_emotion]

    return EmotionResult(
        label=top_emotion,
        confidence=round(confidence, 3),
        all_emotions={k: round(v, 3) for k, v in sorted(normalized.items(), key=lambda x: -x[1])},
    )


def build_system_prompt(personality: str, language: str) -> str:
    """Build the system prompt based on personality and language settings."""
    base_prompt = PERSONALITY_PROMPTS.get(personality, PERSONALITY_PROMPTS["friendly"])

    language_instruction = ""
    if language != "en":
        language_instruction = f"\n\nPlease respond in the language with code '{language}'. "

    return base_prompt + language_instruction


async def generate_ai_response(
    user_message: str,
    conversation_history: list[dict[str, str]],
    personality: str = "friendly",
    language: str = "en",
    detect_emotion: bool = True,
) -> AIResponse:
    """Generate an AI response using the configured LLM.

    This function handles the core AI conversation logic:
    1. Builds the system prompt based on personality
    2. Detects emotion from user input
    3. Generates a contextual response
    4. Returns the complete AI response with metadata
    """
    start_time = time.time()

    # Detect emotion from user message
    emotion = detect_emotion_from_text(user_message) if detect_emotion else None

    # Build messages for the LLM
    system_prompt = build_system_prompt(personality, language)

    # Add emotion context to system prompt if detected
    if emotion and emotion.label != "neutral":
        system_prompt += (
            f"\n\nThe user appears to be feeling {emotion.label} "
            f"(confidence: {emotion.confidence:.0%}). "
            "Adjust your tone and response accordingly to be emotionally supportive."
        )

    messages = [{"role": "system", "content": system_prompt}]
    messages.extend(conversation_history[-20:])  # Keep last 20 messages for context
    messages.append({"role": "user", "content": user_message})

    # Generate response
    if settings.OPENAI_API_KEY:
        response_content, tokens_used, model = await _call_openai(messages)
    else:
        # Fallback response when no API key is configured
        response_content = _generate_fallback_response(user_message, personality, emotion)
        tokens_used = len(user_message.split()) + len(response_content.split())
        model = "hugz-fallback-v1"

    elapsed_ms = int((time.time() - start_time) * 1000)

    return AIResponse(
        content=response_content,
        model_used=model,
        tokens_used=tokens_used,
        response_time_ms=elapsed_ms,
        emotion=emotion,
    )


async def _call_openai(messages: list[dict[str, str]]) -> tuple[str, int, str]:
    """Call OpenAI API for response generation."""
    try:
        import openai

        client = openai.AsyncOpenAI(api_key=settings.OPENAI_API_KEY)
        response = await client.chat.completions.create(
            model=settings.OPENAI_MODEL,
            messages=messages,  # type: ignore[arg-type]
            max_tokens=settings.AI_MAX_TOKENS,
            temperature=settings.AI_TEMPERATURE,
        )
        content = response.choices[0].message.content or ""
        tokens = response.usage.total_tokens if response.usage else 0
        model = response.model
        return content, tokens, model
    except Exception as e:
        return f"I'm having trouble connecting to my AI brain right now. Error: {e}", 0, "error"


def _generate_fallback_response(
    user_message: str, personality: str, emotion: EmotionResult | None
) -> str:
    """Generate a fallback response when no LLM API is available."""
    greeting_words = {
        "hello",
        "hi",
        "hey",
        "greetings",
        "good morning",
        "good afternoon",
        "good evening",
    }
    user_words = set(user_message.lower().split())

    if user_words & greeting_words:
        return (
            "Hello! 👋 I'm HUGZ AI, your intelligent assistant. "
            "I'm here to help you with anything you need. "
            "How can I assist you today?"
        )

    emotion_prefix = ""
    if emotion and emotion.label != "neutral":
        emotion_responses = {
            "happy": "I'm glad you're feeling positive! 😊 ",
            "sad": "I sense you might be feeling down. I'm here for you. 💙 ",
            "angry": "I understand your frustration. Let me help. ",
            "excited": "Your enthusiasm is contagious! 🎉 ",
            "confused": "Let me help clarify things for you. ",
            "fearful": "Don't worry, I'm here to help. ",
            "surprised": "That does sound surprising! ",
        }
        emotion_prefix = emotion_responses.get(emotion.label, "")

    return (
        f"{emotion_prefix}"
        "I'm HUGZ AI — currently running in demo mode without a full LLM connection. "
        "Once configured with an API key, I'll be able to have natural, intelligent "
        "conversations with you, remember our chat history, detect emotions, "
        "and help with complex tasks. For now, I can demonstrate the platform's "
        "architecture and capabilities. What would you like to explore?"
    )
