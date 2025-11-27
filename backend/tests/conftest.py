"""
Pytest Configuration and Fixtures for MandirSync Testing

This file provides reusable test fixtures for FastAPI testing.
"""

import pytest
from fastapi.testclient import TestClient
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from sqlalchemy.pool import StaticPool

from app.main import app
from app.database import Base, get_db

# Test database URL (using SQLite in-memory for fast tests)
# For PostgreSQL tests, use: postgresql://postgres:postgres@localhost:5432/mandirsync_test
TEST_DATABASE_URL = "sqlite:///:memory:"

# Create test engine
engine = create_engine(
    TEST_DATABASE_URL,
    connect_args={"check_same_thread": False},
    poolclass=StaticPool,
)

# Create test session factory
TestingSessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)


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
