"""Database and system endpoint tests."""

from fastapi.testclient import TestClient
from sqlalchemy import inspect
from sqlalchemy.orm import Session

from tests.conftest import EXPECTED_TABLES


def test_tables_are_created(db_session: Session) -> None:
    """All Sprint 1 Task 3 tables exist after metadata initialization."""
    inspector = inspect(db_session.get_bind())
    table_names = set(inspector.get_table_names())
    assert EXPECTED_TABLES.issubset(table_names)


def test_system_tables_endpoint(client: TestClient) -> None:
    """System tables endpoint returns the expected table names."""
    response = client.get("/api/v1/system/tables")

    assert response.status_code == 200
    body = response.json()

    assert body["success"] is True
    assert body["message"] == "Tables retrieved"
    assert body["data"] is not None

    tables = set(body["data"]["tables"])
    assert EXPECTED_TABLES.issubset(tables)
