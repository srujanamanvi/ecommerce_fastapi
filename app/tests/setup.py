import pytest
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
import pytest
from fastapi.testclient import TestClient

from app.main import app
from app.settings.production import get_db, Base


SQLALCHEMY_DATABASE_URL = "sqlite:///./test.db"


@pytest.fixture
def test_db():
    # Create the SQLite engine and session
    engine = create_engine(
        SQLALCHEMY_DATABASE_URL, connect_args={"check_same_thread": False}
    )
    TestingSessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

    # Create tables
    Base.metadata.create_all(bind=engine)

    # Override the app's get_db dependency
    def override_get_db():
        try:
            db = TestingSessionLocal()
            yield db
        finally:
            db.close()

    app.dependency_overrides[get_db] = override_get_db

    # Return the session for test use
    db = TestingSessionLocal()
    try:
        yield db
    finally:
        db.close()

    # Drop tables after test
    Base.metadata.drop_all(bind=engine)


@pytest.fixture
def client(test_db):
    return TestClient(app)
