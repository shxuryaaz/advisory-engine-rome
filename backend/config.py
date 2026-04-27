from functools import lru_cache
from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    """Runtime configuration loaded from environment variables."""

    model_config = SettingsConfigDict(env_file=".env", env_file_encoding="utf-8", extra="ignore")

    app_name: str = "Personal Decision Intelligence System"
    app_version: str = "0.1.0"
    environment: str = "development"

    openai_api_key: str | None = None
    openai_model: str = "gpt-4.1"
    openai_embedding_model: str = "text-embedding-3-small"

    database_url: str | None = None
    supabase_url: str | None = None
    supabase_service_role_key: str | None = None

    cors_origins: str = "http://localhost:5173"
    default_user_id: str = "00000000-0000-0000-0000-000000000001"

    @property
    def cors_origin_list(self) -> list[str]:
        return [origin.strip() for origin in self.cors_origins.split(",") if origin.strip()]


@lru_cache
def get_settings() -> Settings:
    return Settings()


settings = get_settings()
