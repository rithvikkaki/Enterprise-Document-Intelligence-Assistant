import os
from typing import List, Optional
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

    # Local LLM (Ollama)
    OLLAMA_BASE_URL: str = "http://localhost:11434"
    OLLAMA_MODEL: str = "llama3.2:1b"

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


settings = Settings()
