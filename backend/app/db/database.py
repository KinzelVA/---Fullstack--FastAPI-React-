from collections.abc import Generator
from sqlite3 import Connection as SQLiteConnection
from typing import Any

from sqlalchemy import Engine, create_engine, event
from sqlalchemy.orm import DeclarativeBase, Session, sessionmaker

from backend.app.core.config import get_settings

settings = get_settings()

connect_args: dict[str, bool] = {}
if settings.database_url.startswith("sqlite"):
    connect_args = {"check_same_thread": False}

engine = create_engine(settings.database_url, connect_args=connect_args)


def _sqlite_unicode_lower(value: Any) -> Any:
    if value is None:
        return None

    return str(value).lower()


def register_sqlite_unicode_lower(sqlalchemy_engine: Engine) -> None:
    """Register Unicode-aware lower() for SQLite connections.

    SQLAlchemy compiles ilike() for SQLite as:

        lower(column) LIKE lower(:pattern)

    Built-in SQLite lower() handles only ASCII letters, so Cyrillic
    case-insensitive search does not work correctly out of the box.
    """

    if sqlalchemy_engine.url.get_backend_name() != "sqlite":
        return

    @event.listens_for(sqlalchemy_engine, "connect")
    def _register_unicode_lower(dbapi_connection: object, _: object) -> None:
        if not isinstance(dbapi_connection, SQLiteConnection):
            return

        try:
            dbapi_connection.create_function(
                "lower",
                1,
                _sqlite_unicode_lower,
                deterministic=True,
            )
        except TypeError:
            dbapi_connection.create_function("lower", 1, _sqlite_unicode_lower)


register_sqlite_unicode_lower(engine)

SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)


class Base(DeclarativeBase):
    pass


def get_db() -> Generator[Session, None, None]:
    db = SessionLocal()

    try:
        yield db
    finally:
        db.close()
