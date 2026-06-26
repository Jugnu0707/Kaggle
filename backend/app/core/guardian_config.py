"""Guardian Agent configuration loaded from environment variables."""

from pydantic import Field
from pydantic_settings import BaseSettings, SettingsConfigDict


class GuardianSettings(BaseSettings):
    """Environment-driven Guardian validation settings."""

    model_config = SettingsConfigDict(
        env_file=(".env", "../.env"),
        env_file_encoding="utf-8",
        extra="ignore",
    )

    guardian_enabled: bool = Field(default=True, validation_alias="GUARDIAN_ENABLED")
    min_ai_confidence: int = Field(default=70, ge=0, le=100, validation_alias="MIN_AI_CONFIDENCE")
    mask_secrets: bool = Field(default=True, validation_alias="MASK_SECRETS")
    mask_pii: bool = Field(default=True, validation_alias="MASK_PII")


guardian_settings = GuardianSettings()
