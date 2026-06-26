"""Application configuration."""

from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    """Environment-driven application settings."""

    model_config = SettingsConfigDict(env_file=".env", env_file_encoding="utf-8")

    app_name: str = "Oz AI"
    app_version: str = "0.1.0"
    host: str = "0.0.0.0"
    port: int = 8000
    database_url: str = "sqlite:///./oz_ai.db"


settings = Settings()
