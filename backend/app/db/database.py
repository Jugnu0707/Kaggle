"""SQLAlchemy database engine, session factory, and FastAPI dependency."""

from collections.abc import Generator

from sqlalchemy import create_engine, inspect, text
from sqlalchemy.orm import DeclarativeBase, Session, sessionmaker

from app.core.config import resolve_database_url, settings
from app.core.logging import get_logger

logger = get_logger(__name__)


class Base(DeclarativeBase):
    """Declarative base class for all SQLAlchemy ORM models."""


engine = create_engine(
    resolve_database_url(settings.database_url),
    connect_args={"check_same_thread": False},
)

SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)


def sync_sqlite_schema() -> None:
    """Add missing columns to existing SQLite tables without dropping data."""
    if engine.dialect.name != "sqlite":
        return

    import app.models  # noqa: F401

    inspector = inspect(engine)
    existing_tables = set(inspector.get_table_names())

    for table_name, table in Base.metadata.tables.items():
        if table_name not in existing_tables:
            continue

        existing_columns = {
            column["name"] for column in inspector.get_columns(table_name)
        }
        for column in table.columns:
            if column.name in existing_columns:
                continue

            column_type = column.type.compile(dialect=engine.dialect)
            alter_sql = (
                f"ALTER TABLE {table_name} ADD COLUMN {column.name} {column_type}"
            )
            if column.nullable:
                alter_sql += " NULL"

            with engine.begin() as connection:
                connection.execute(text(alter_sql))

            logger.info("Added missing column: %s.%s", table_name, column.name)


def init_db() -> None:
    """Create database tables for all registered ORM models."""
    import app.models  # noqa: F401

    Base.metadata.create_all(bind=engine)
    sync_sqlite_schema()
    logger.info("Database tables initialized")


def get_db() -> Generator[Session, None, None]:
    """Yield a database session for FastAPI dependency injection."""
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


def check_database_connection(db: Session) -> bool:
    """Return True when the database accepts a simple connectivity query."""
    try:
        db.execute(text("SELECT 1"))
        return True
    except Exception:
        return False


def get_table_names(db: Session) -> list[str]:
    """Return sorted table names detected in the connected database."""
    inspector = inspect(db.get_bind())
    return sorted(inspector.get_table_names())
