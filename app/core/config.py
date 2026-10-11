import os
from typing import List, Optional, Any, Union
from pydantic import model_validator, field_validator
from pydantic_settings import BaseSettings, SettingsConfigDict



class Settings(BaseSettings):
    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        extra="ignore"
    )

    # Application
    APP_NAME: str = "Enterprise Document Intelligence Platform"
    ENVIRONMENT: str = "development"
    DEBUG: bool = True
    LOG_LEVEL: str = "INFO"
    SECRET_KEY: str = "change_this_to_a_secure_random_secret_key_in_production"
    CORS_ORIGINS: List[str] = [
        "http://localhost:5173",
        "http://localhost:3000",
        "http://127.0.0.1:5173",
        "http://127.0.0.1:3000",
    ]

    @field_validator("CORS_ORIGINS", mode="before")
    @classmethod
    def assemble_cors_origins(cls, v: Any) -> Any:
        if isinstance(v, str) and not v.startswith("["):
            return [i.strip() for i in v.split(",") if i.strip()]
        elif isinstance(v, (list, str)):
            return v
        return v

    # Database
    DATABASE_URL: str = "postgresql+asyncpg://postgres:postgres@localhost:5432/document_intelligence"
    SYNC_DATABASE_URL: str = "postgresql://postgres:postgres@localhost:5432/document_intelligence"

    # Redis / Celery
    REDIS_URL: str = "redis://localhost:6379/0"
    CELERY_BROKER_URL: Optional[str] = None
    CELERY_RESULT_BACKEND: Optional[str] = None

    # JWT Security
    JWT_SECRET_KEY: str = "super_secret_jwt_key_please_change_in_production"
    JWT_ALGORITHM: str = "HS256"
    JWT_ACCESS_TOKEN_EXPIRE_MINUTES: int = 60
    JWT_REFRESH_TOKEN_EXPIRE_DAYS: int = 7

    # Storage
    STORAGE_PROVIDER: str = "local"
    LOCAL_STORAGE_PATH: str = "./storage"

    # Embeddings (Default: local free sentence-transformers/all-MiniLM-L6-v2)
    EMBEDDING_PROVIDER: str = "huggingface"
    EMBEDDING_MODEL: str = "sentence-transformers/all-MiniLM-L6-v2"
    EMBEDDING_DIMENSION: int = 384
    EMBEDDING_BATCH_SIZE: int = 32

    # Reranking
    RERANKING_ENABLED: bool = True
    RERANKER_MODEL: str = "cross-encoder/ms-marco-MiniLM-L-6-v2"
    RRF_K: int = 60

    # LLM Settings (Supports Local Ollama and Cloud Groq)
    OLLAMA_BASE_URL: str = "http://localhost:11434"
    OLLAMA_MODEL: str = "llama3.2:1b"
    GROQ_API_KEY: Optional[str] = None
    GROQ_MODEL: str = "openai/gpt-oss-20b"

    # File Processing & Safety Limits
    MAX_UPLOAD_SIZE_MB: int = 50
    MAX_ZIP_FILES: int = 100
    MAX_ZIP_EXTRACTED_SIZE_MB: int = 500
    MAX_ZIP_NESTING_DEPTH: int = 1

    # Chunking
    DEFAULT_CHUNK_SIZE: int = 512
    DEFAULT_CHUNK_OVERLAP: int = 64

    def get_celery_broker(self) -> str:
        return self.CELERY_BROKER_URL or self.REDIS_URL

    def get_celery_backend(self) -> str:
        return self.CELERY_RESULT_BACKEND or self.REDIS_URL

    @model_validator(mode="after")
    def validate_production_secrets(self) -> "Settings":
        if self.ENVIRONMENT == "production":
            if self.SECRET_KEY in ("change_this_to_a_secure_random_secret_key_in_production", ""):
                raise ValueError("Insecure default SECRET_KEY cannot be used in production environment.")
            if self.JWT_SECRET_KEY in ("super_secret_jwt_key_please_change_in_production", ""):
                raise ValueError("Insecure default JWT_SECRET_KEY cannot be used in production environment.")
        return self


settings = Settings()
