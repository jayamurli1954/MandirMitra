"""
Pytest configuration and shared fixtures for MandirSync tests

This file contains database fixtures and common test utilities that are
automatically discovered by pytest and made available to all tests.
"""

import pytest
from typing import Generator
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker, Session
from sqlalchemy.pool import StaticPool

from app.core.database import Base, get_db
from app.main import app


# Use in-memory SQLite for fast testing
SQLALCHEMY_TEST_DATABASE_URL = "sqlite:///:memory:"


@pytest.fixture(scope="session")
def engine():
    """
    Create a test database engine (session scope).
    Uses in-memory SQLite for maximum speed.
    """
    engine = create_engine(
        SQLALCHEMY_TEST_DATABASE_URL,
        connect_args={"check_same_thread": False},
        poolclass=StaticPool,  # Reuse connection for in-memory DB
    )

    # Create all tables
    Base.metadata.create_all(bind=engine)

    yield engine

    # Cleanup
    Base.metadata.drop_all(bind=engine)
    engine.dispose()


@pytest.fixture(scope="function")
def db_session(engine) -> Generator[Session, None, None]:
    """
    Create a new database session for each test (function scope).

    This ensures test isolation - each test gets a clean database state.
    Uses transactions that are rolled back after each test.
    """
    connection = engine.connect()
    transaction = connection.begin()

    # Create session bound to this connection
    SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=connection)
    session = SessionLocal()

    yield session

    # Rollback transaction and close
    session.close()
    transaction.rollback()
    connection.close()


@pytest.fixture(scope="function")
def client(db_session):
    """
    Create a test client with database session override.

    This fixture provides a FastAPI TestClient that uses the test database.
    """
    from fastapi.testclient import TestClient

    def override_get_db():
        try:
            yield db_session
        finally:
            pass

    app.dependency_overrides[get_db] = override_get_db

    with TestClient(app) as test_client:
        yield test_client

    # Clear overrides
    app.dependency_overrides.clear()


@pytest.fixture
def authenticated_client(client, test_user):
    """
    Create an authenticated test client.

    Returns a client with authentication headers for the test user.
    """
    # Login to get token
    response = client.post(
        "/api/auth/login",
        data={"username": test_user.email, "password": "testpass123"}
    )

    if response.status_code == 200:
        token = response.json().get("access_token")
        client.headers["Authorization"] = f"Bearer {token}"

    return client


# Performance optimization: Mark slow tests
def pytest_configure(config):
    """Configure custom markers"""
    config.addinivalue_line(
        "markers", "slow: marks tests as slow (deselect with '-m \"not slow\"')"
    )
    config.addinivalue_line(
        "markers", "integration: marks tests as integration tests"
    )
    config.addinivalue_line(
        "markers", "unit: marks tests as unit tests"
    )
    config.addinivalue_line(
        "markers", "panchang: marks tests related to panchang calculations"
    )
    config.addinivalue_line(
        "markers", "api: marks tests for API endpoints"
    )
    config.addinivalue_line(
        "markers", "database: marks tests that require database"
    )
