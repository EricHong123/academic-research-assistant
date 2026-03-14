"""Configuration for Academic Research Assistant."""
import os
from functools import lru_cache
from pydantic_settings import BaseSettings


class Settings(BaseSettings):
    """Application settings."""

    # App
    app_name: str = "Academic Research Assistant"
    app_version: str = "0.1.0"
    debug: bool = True

    # Database
    database_url: str = "sqlite+aiosqlite:///./ara.db"

    # Redis
    redis_url: str = "redis://localhost:6379/0"

    # LLM
    llm_provider: str = "anthropic"
    openai_api_key: str = ""
    anthropic_api_key: str = ""

    # Vector Database
    pinecone_api_key: str = ""
    pinecone_environment: str = "us-west1"
    weaviate_url: str = "http://localhost:8080"

    # Academic APIs
    wos_api_key: str = ""
    scopus_api_key: str = ""
    pubmed_api_key: str = ""
    ebsco_api_key: str = ""
    google_scholar_enabled: bool = False

    # JWT
    jwt_secret_key: str = "your-secret-key-change-in-production"
    jwt_algorithm: str = "HS256"
    jwt_expiration_minutes: int = 1440

    # Storage
    upload_dir: str = "./uploads"
    pdf_storage_dir: str = "./storage/pdfs"

    # Celery
    celery_broker_url: str = "redis://localhost:6379/1"
    celery_result_backend: str = "redis://localhost:6379/2"

    class Config:
        env_file = ".env"
        extra = "allow"


@lru_cache()
def get_settings() -> Settings:
    """Get cached settings."""
    return Settings()
