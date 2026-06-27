"""Pytest fixtures for Response Planning Agent unit tests."""

from unittest.mock import MagicMock, patch

import pytest
from sqlalchemy import create_engine
from sqlalchemy.orm import Session, sessionmaker
from sqlalchemy.pool import StaticPool

import app.models  # noqa: F401
from agents.conftest import build_mock_ai_runtime
from app.db.database import Base


@pytest.fixture
def mock_ai_runtime() -> MagicMock:
    """Mock AI runtime for Response Planning service tests."""
    mock_runtime = build_mock_ai_runtime()
    with patch("agents.response.service.get_ai_runtime", return_value=mock_runtime):
        yield mock_runtime


@pytest.fixture
def db_session() -> Session:
    """Provide an isolated in-memory database session for Response Planning tests."""
    engine = create_engine(
        "sqlite://",
        connect_args={"check_same_thread": False},
        poolclass=StaticPool,
    )
    testing_session_local = sessionmaker(autocommit=False, autoflush=False, bind=engine)
    Base.metadata.create_all(bind=engine)
    session = testing_session_local()
    try:
        yield session
    finally:
        session.close()
        Base.metadata.drop_all(bind=engine)
