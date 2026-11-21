"""Database configuration: engine, session factory and the base class for models.

Everything that talks to SQLite is set up here so the rest of the code never
has to worry about connection details.
"""
import os

from sqlalchemy import create_engine, event
from sqlalchemy.engine import Engine
from sqlalchemy.orm import DeclarativeBase, sessionmaker

# Default: a file called lending.db in the folder where you start the server.
DATABASE_URL = os.getenv("DATABASE_URL", "sqlite:///./lending.db")


class Base(DeclarativeBase):
    """Parent class of all database models (Book, Loan)."""


def make_engine(url: str) -> Engine:
    """Create a SQLite engine.

    - check_same_thread=False: FastAPI may use a connection from another thread.
    - timeout=30: if another request is writing, wait up to 30 s instead of failing.
    - PRAGMA foreign_keys=ON: SQLite ignores foreign keys unless this is switched on
      for every new connection, so we do it here.
    """
    engine = create_engine(url, connect_args={"check_same_thread": False, "timeout": 30})

    @event.listens_for(engine, "connect")
    def _enable_foreign_keys(dbapi_connection, _connection_record):
        cursor = dbapi_connection.cursor()
        cursor.execute("PRAGMA foreign_keys=ON")
        cursor.close()

    return engine


engine = make_engine(DATABASE_URL)
SessionLocal = sessionmaker(bind=engine, autoflush=False, expire_on_commit=False)


def init_db() -> None:
    """Create the tables if they do not exist yet (safe to call repeatedly)."""
    from app import models  # noqa: F401  (importing registers the models on Base)

    Base.metadata.create_all(bind=engine)


def get_db():
    """FastAPI dependency: give each request its own session and always close it."""
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()
