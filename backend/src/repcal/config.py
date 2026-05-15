"""Application settings loaded from environment variables (.env)."""

from __future__ import annotations

from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        case_sensitive=False,
        extra="ignore",
    )

    # Database
    database_url: str

    # Discord
    discord_bot_token: str
    discord_guild_id: int | None = None

    # Gemini (unused in Phase 1)
    gemini_api_key: str = ""

    # App
    app_env: str = "development"
    log_level: str = "INFO"

    @property
    def is_development(self) -> bool:
        return self.app_env == "development"


settings = Settings()
