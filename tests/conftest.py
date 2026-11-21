"""Shared test setup. Every test gets its OWN temporary SQLite file, seeded with the
three books, so tests can never damage lending.db and never affect each other."""
import pytest
from fastapi.testclient import TestClient
from sqlalchemy.orm import sessionmaker

from app.database import Base, get_db, make_engine
from app.main import app
from database.seed import seed_books


@pytest.fixture()
def session_factory(tmp_path):
    """A factory for sessions on a fresh, seeded test database."""
    engine = make_engine(f"sqlite:///{(tmp_path / 'test.db').as_posix()}")
    Base.metadata.create_all(bind=engine)
    factory = sessionmaker(bind=engine, autoflush=False, expire_on_commit=False)
    with factory() as session:
        seed_books(session)
    yield factory
    engine.dispose()


@pytest.fixture()
def client(session_factory):
    """A test client whose requests use the temporary database."""

    def override_get_db():
        db = session_factory()
        try:
            yield db
        finally:
            db.close()

    app.dependency_overrides[get_db] = override_get_db
    yield TestClient(app)  # not used as a context manager, so startup code is skipped
    app.dependency_overrides.clear()
