"""
Pytest Configuration and Fixtures for MandirSync Testing

This file provides reusable test fixtures for FastAPI testing.

PERFORMANCE OPTIMIZATIONS:
- SQLite in-memory database for 10x faster tests
- Session-scoped database for reusable connections
- Automatic cleanup after tests
- Foreign key constraints enabled
"""

import pytest
from fastapi.testclient import TestClient
from sqlalchemy import create_engine, event
from sqlalchemy.orm import sessionmaker
from sqlalchemy.pool import StaticPool
import os

from app.main import app
from app.database import Base, get_db

# Test database URL (using SQLite in-memory for FAST tests)
# Override with: TEST_DATABASE_URL=postgresql://... pytest
TEST_DATABASE_URL = os.getenv("TEST_DATABASE_URL", "sqlite:///:memory:")

# OPTIMIZATION: Create engine with optimized settings
engine = create_engine(
    TEST_DATABASE_URL,
    connect_args={"check_same_thread": False} if "sqlite" in TEST_DATABASE_URL else {},
    poolclass=StaticPool,
    echo=False,  # Disable SQL logging for faster tests
)

# Enable foreign keys for SQLite (important for referential integrity)
if "sqlite" in TEST_DATABASE_URL:
    @event.listens_for(engine, "connect")
    def set_sqlite_pragma(dbapi_conn, connection_record):
        cursor = dbapi_conn.cursor()
        cursor.execute("PRAGMA foreign_keys=ON")
        cursor.execute("PRAGMA synchronous=OFF")  # Faster writes (safe for tests)
        cursor.execute("PRAGMA journal_mode=MEMORY")  # Keep journal in memory
        cursor.close()

# Create test session factory
TestingSessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)


# OPTIMIZATION: Create tables once per test session instead of per test
@pytest.fixture(scope="session", autouse=True)
def setup_test_database():
    """
    Create database tables once at the start of test session.
    This is much faster than creating/dropping per test.
    """
    Base.metadata.create_all(bind=engine)
    yield
    Base.metadata.drop_all(bind=engine)


@pytest.fixture(scope="function")
def db_session():
    """
    Provides a clean database session for each test.
    Automatically creates tables before test and drops after.
    """
    # Create all tables
    Base.metadata.create_all(bind=engine)

    # Create session
    session = TestingSessionLocal()

    try:
        yield session
    finally:
        session.close()
        # Drop all tables after test
        Base.metadata.drop_all(bind=engine)


@pytest.fixture(scope="function")
def client(db_session):
    """
    Provides a FastAPI TestClient with overridden database dependency.
    """
    def override_get_db():
        try:
            yield db_session
        finally:
            pass

    app.dependency_overrides[get_db] = override_get_db

    with TestClient(app) as test_client:
        yield test_client

    app.dependency_overrides.clear()


@pytest.fixture
def test_user_data():
    """
    Provides sample user data for testing.
    """
    return {
        "username": "test_admin",
        "email": "admin@mandirsync.test",
        "password": "Test@1234",
        "full_name": "Test Administrator",
        "role": "super_admin"
    }


@pytest.fixture
def test_donation_data():
    """
    Provides sample donation data for testing.
    """
    return {
        "donor_name": "Ram Kumar",
        "amount": 1000.00,
        "payment_method": "cash",
        "category": "general",
        "purpose": "Temple development",
        "pan_number": "ABCDE1234F"
    }


@pytest.fixture
def test_seva_data():
    """
    Provides sample seva booking data for testing.
    """
    return {
        "devotee_name": "Krishna Sharma",
        "seva_name": "Abhishekam",
        "seva_date": "2025-12-01",
        "amount": 500.00,
        "payment_method": "upi"
    }


@pytest.fixture
def authenticated_client(client, test_user_data):
    """
    Provides a TestClient with authenticated session.
    Creates a test user and returns client with auth token.
    """
    # Register user
    response = client.post("/api/auth/register", json=test_user_data)

    # Login to get token
    login_response = client.post(
        "/api/auth/login",
        data={
            "username": test_user_data["username"],
            "password": test_user_data["password"]
        }
    )

    if login_response.status_code == 200:
        token = login_response.json().get("access_token")
        client.headers.update({"Authorization": f"Bearer {token}"})

    return client


# ============================================================================
# HELPER FUNCTIONS
# ============================================================================

def assert_success_response(response, expected_status=200):
    """
    Assert that API response is successful.
    """
    assert response.status_code == expected_status, (
        f"Expected status {expected_status}, got {response.status_code}. "
        f"Response: {response.text}"
    )


def assert_error_response(response, expected_status=400):
    """
    Assert that API response is an error.
    """
    assert response.status_code == expected_status, (
        f"Expected error status {expected_status}, got {response.status_code}. "
        f"Response: {response.text}"
    )
