"""Application configuration with environment variable support."""

from pydantic_settings import BaseSettings


class Settings(BaseSettings):
    """HUGZ AI application settings."""

    # Application
    APP_NAME: str = "HUGZ AI"
    APP_VERSION: str = "0.1.0"
    DEBUG: bool = False
    ENVIRONMENT: str = "development"
    API_PREFIX: str = "/api/v1"

    # Server
    HOST: str = "0.0.0.0"
    PORT: int = 8000
    WORKERS: int = 4

    # Security
    SECRET_KEY: str = "hugz-ai-dev-secret-key-change-in-production"
    JWT_ALGORITHM: str = "HS256"
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 15
    REFRESH_TOKEN_EXPIRE_DAYS: int = 7
    ALLOWED_ORIGINS: list[str] = [
        "http://localhost:3000",
        "http://localhost:5173",
        "https://hugzai.com",
    ]

    # Database
    DATABASE_URL: str = "postgresql+asyncpg://hugz:hugz@localhost:5432/hugzai"
    DATABASE_POOL_SIZE: int = 20
    DATABASE_MAX_OVERFLOW: int = 10

    # Redis
    REDIS_URL: str = "redis://localhost:6379/0"
    REDIS_CACHE_TTL: int = 300  # 5 minutes

    # AI / LLM
    OPENAI_API_KEY: str = ""
    OPENAI_MODEL: str = "gpt-4"
    AI_MAX_TOKENS: int = 4096
    AI_TEMPERATURE: float = 0.7

    # Voice
    WHISPER_MODEL: str = "base"
    TTS_ENGINE: str = "edge-tts"
    TTS_VOICE: str = "en-US-AriaNeural"

    # Rate Limiting
    RATE_LIMIT_FREE: int = 60  # requests per minute
    RATE_LIMIT_PRO: int = 1000
    RATE_LIMIT_ENTERPRISE: int = 10000

    # Encryption
    ENCRYPTION_KEY: str = ""  # AES-256 key, generated on first run

    # File Storage
    STORAGE_BACKEND: str = "local"  # local, s3, minio
    STORAGE_BUCKET: str = "hugz-ai-storage"
    S3_ACCESS_KEY: str = ""
    S3_SECRET_KEY: str = ""
    S3_REGION: str = "us-east-1"

    model_config = {"env_file": ".env", "env_file_encoding": "utf-8", "case_sensitive": True}


settings = Settings()
