"""
Centralized application configuration.
Reads from environment variables / .env file using pydantic-settings.
"""

from functools import lru_cache
from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    """All application settings loaded from .env / environment variables."""

    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        extra="ignore",
    )

    # --- Application ---
    app_port: int = 8000
    app_host: str = "0.0.0.0"

    # --- LLM ---
    llm_model_name: str = "gpt-4o-mini"
    llm_api_key: str = ""
    llm_base_url: str | None = None  # For local/custom endpoints (e.g. Ollama, LM Studio)
    llm_temperature: float = 0.0

    # --- Evaluation LLM (Judge) ---
    evaluation_llm_model_name: str | None = None
    evaluation_llm_api_key: str | None = None
    evaluation_llm_base_url: str | None = None
    evaluation_llm_temperature: float = 0.0

    # --- Embedding / Semantic Chunker ---
    embedding_model_name: str = "sentence-transformers/all-MiniLM-L6-v2"
    sparse_embedding_model_name: str = "prithivida/Splade_PP_en_v1"
    chunker_model_name: str = "all-MiniLM-L6-v2"
    chunker_breakpoint_type: str = "percentile"

    # --- Vector Store ---
    vector_store_collection: str = "candidates"

    # --- LinkedIn ---
    linkedin_access_token: str | None = None
    linkedin_user_urn: str | None = None


@lru_cache
def get_settings() -> Settings:
    """Return a cached Settings instance (loaded once)."""
    return Settings()
