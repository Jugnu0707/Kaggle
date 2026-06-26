"""Application configuration loaded from environment variables."""

from pathlib import Path

from pydantic import Field
from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    """Environment-driven application settings."""

    model_config = SettingsConfigDict(
        env_file=(".env", "../.env"),
        env_file_encoding="utf-8",
        extra="ignore",
    )

    app_name: str = Field(default="Oz AI", validation_alias="APP_NAME")
    app_version: str = Field(default="0.1.0", validation_alias="APP_VERSION")
    host: str = Field(default="0.0.0.0", validation_alias="HOST")
    port: int = Field(default=8000, validation_alias="PORT")
    database_url: str = Field(
        default="sqlite:///./oz_ai.db",
        validation_alias="DATABASE_URL",
    )
    upload_dir: str = Field(
        default="storage/uploads",
        validation_alias="UPLOAD_DIR",
    )
    max_upload_size_bytes: int = Field(
        default=52_428_800,
        validation_alias="MAX_UPLOAD_SIZE_BYTES",
    )


settings = Settings()


def resolve_database_url(database_url: str | None = None) -> str:
    """Resolve relative SQLite paths against the backend root directory."""
    url = database_url or settings.database_url
    if not url.startswith("sqlite"):
        return url

    if url.startswith("sqlite:////"):
        return url

    prefix = "sqlite:///"
    if not url.startswith(prefix):
        return url

    path_part = url[len(prefix) :]
    if path_part.startswith("./"):
        path_part = path_part[2:]

    db_path = Path(path_part)
    if db_path.is_absolute():
        return f"sqlite:///{db_path.as_posix()}"

    backend_root = Path(__file__).resolve().parents[2]
    resolved = (backend_root / db_path).resolve()
    return f"sqlite:///{resolved.as_posix()}"


def get_database_path() -> Path:
    """Return the absolute filesystem path for the configured SQLite database."""
    url = resolve_database_url()
    path_part = url.removeprefix("sqlite:///")
    return Path(path_part)


def get_upload_path() -> Path:
    """Return the absolute upload directory path, creating it if needed."""
    configured = Path(settings.upload_dir)
    if configured.is_absolute():
        upload_path = configured
    else:
        app_root = Path(__file__).resolve().parents[2]
        monorepo_root = app_root.parent
        if (monorepo_root / "frontend").exists():
            upload_path = monorepo_root / configured
        else:
            upload_path = app_root / configured

    upload_path.mkdir(parents=True, exist_ok=True)
    return upload_path.resolve()
