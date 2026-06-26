"""AI and Google ADK configuration loaded from environment variables."""

from pydantic import Field
from pydantic_settings import BaseSettings, SettingsConfigDict


class AISettings(BaseSettings):
    """Environment-driven AI and ADK settings."""

    model_config = SettingsConfigDict(
        env_file=(".env", "../.env"),
        env_file_encoding="utf-8",
        extra="ignore",
    )

    google_api_key: str = Field(default="", validation_alias="GOOGLE_API_KEY")
    google_model: str = Field(default="gemini-2.5-pro", validation_alias="GOOGLE_MODEL")
    adk_app_name: str = Field(default="oz_ai", validation_alias="ADK_APP_NAME")
    adk_enable_tracing: bool = Field(default=False, validation_alias="ADK_ENABLE_TRACING")


ai_settings = AISettings()
