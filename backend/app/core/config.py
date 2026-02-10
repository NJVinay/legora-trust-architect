"""
Application configuration using Pydantic Settings.
All secrets and environment-specific values are loaded from environment variables.
"""

import json
from functools import lru_cache

from pydantic_settings import BaseSettings


class Settings(BaseSettings):
    """Application settings loaded from environment variables."""

    # --- Application ---
    APP_NAME: str = "Legora Trust-Architect"
    APP_VERSION: str = "0.1.0"
    DEBUG: bool = False

    # --- Azure OpenAI ---
    AZURE_OPENAI_API_KEY: str = ""
    AZURE_OPENAI_ENDPOINT: str = ""
    AZURE_OPENAI_API_VERSION: str = "2024-06-01"
    AZURE_OPENAI_DEPLOYMENT_NAME: str = ""

    # --- Data Paths ---
    SOURCE_DOCUMENTS_DIR: str = "data/source_documents"

    # --- Agent Config ---
    MAX_VALIDATION_RETRIES: int = 3
    LLM_TEMPERATURE: float = 0.2
    LLM_MAX_TOKENS: int = 2048

    # --- CORS (Req #1) ---
    # Override via CORS_ORIGINS env var for different environments.
    # Accepts: JSON array '["https://example.com"]' or comma-separated 'https://a.com,https://b.com'
    CORS_ORIGINS: str = "http://localhost:5173,http://localhost:3000"

    @property
    def cors_origins_list(self) -> list[str]:
        """Parse CORS_ORIGINS string into a list of origins."""
        v = self.CORS_ORIGINS.strip()
        if v.startswith("["):
            try:
                return json.loads(v)
            except json.JSONDecodeError:
                pass
        return [origin.strip() for origin in v.split(",") if origin.strip()]

    # --- Security (Req #5) ---
    API_KEY: str = ""  # Set via env var; empty = auth disabled (dev only)

    # --- JWT / Sessions (Req #9) ---
    JWT_SECRET: str = "change-me-in-production"  # MUST override in prod
    JWT_ALGORITHM: str = "HS256"
    JWT_ACCESS_TOKEN_EXPIRE_MINUTES: int = 15
    JWT_REFRESH_TOKEN_EXPIRE_DAYS: int = 7

    # --- Rate Limiting (Req #6) ---
    RATE_LIMIT_DEFAULT: str = "60/minute"
    RATE_LIMIT_GENERATE: str = "10/minute"

    # --- Storage Policies (Req #3) ---
    MAX_UPLOAD_SIZE_MB: int = 10
    ALLOWED_FILE_EXTENSIONS: list[str] = [".pdf", ".md", ".txt", ".docx"]

    # --- Redirect Allowlist (Req #2) ---
    ALLOWED_REDIRECT_DOMAINS: list[str] = [
        "localhost",
    ]

    model_config = {
        "env_file": ".env",
        "env_file_encoding": "utf-8",
        "case_sensitive": True,
    }


@lru_cache()
def get_settings() -> Settings:
    """Cached settings instance — created once, reused everywhere."""
    return Settings()
