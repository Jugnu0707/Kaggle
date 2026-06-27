"""Pytest fixtures for Risk Assessment Agent unit tests."""

from unittest.mock import patch

import pytest
from agents.conftest import build_mock_ai_runtime
from sqlalchemy import create_engine
from sqlalchemy.orm import Session, sessionmaker
from sqlalchemy.pool import StaticPool

import app.models  # noqa: F401
from app.db.database import Base


@pytest.fixture
def mock_ai_runtime():
    mock_runtime = build_mock_ai_runtime()
    with patch("agents.risk.service.get_ai_runtime", return_value=mock_runtime):
        yield mock_runtime


@pytest.fixture
def db_session() -> Session:
    """Provide an isolated in-memory database session for Risk Assessment tests."""
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
