"""
Pytest configuration and shared fixtures for MandirMitra tests

This file contains database fixtures and common test utilities that are
automatically discovered by pytest and made available to all tests.
"""

import pytest
from typing import Generator
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker, Session
from sqlalchemy.pool import StaticPool

from app.core.database import Base, get_db
from app.core.security import get_password_hash
from app.main import app
from app.models.user import User


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


@pytest.fixture(scope="function")
def test_user(db_session):
    """
    Create a test user in the database.
    
    Returns a User instance that can be used for authentication in tests.
    """
    from app.models.temple import Temple
    
    # Create or get temple
    temple = db_session.query(Temple).filter(Temple.name == "Test Temple").first()
    if not temple:
        temple = Temple(
            name="Test Temple",
            slug="test-temple",
            is_active=True,
            certificate_80g_number="80G/12345/2023-24",
            certificate_80g_valid_from="2023-04-01",
            certificate_80g_valid_to="2024-03-31"
        )
        db_session.add(temple)
        db_session.flush()
    
    user = User(
        email="testuser@example.com",
        password_hash=get_password_hash("testpass123"),
        full_name="Test User",
        role="admin",  # Admin role for tests that require admin permissions (e.g., seva creation)
        is_active=True,
        is_superuser=False,
        temple_id=temple.id  # Link user to temple
    )
    db_session.add(user)
    db_session.commit()
    db_session.refresh(user)
    
    return user


@pytest.fixture
def chart_of_accounts(db_session, test_user):
    """
    Create basic Chart of Accounts for testing.
    This ensures donation creation can create journal entries.
    """
    from app.models.accounting import Account, AccountType, AccountSubType
    from app.models.temple import Temple
    
    # Get or create temple
    temple = db_session.query(Temple).filter(Temple.id == test_user.temple_id).first()
    if not temple:
        # Create a test temple
        temple = Temple(
            name="Test Temple",
            slug="test-temple",
            is_active=True
        )
        db_session.add(temple)
        db_session.flush()
        test_user.temple_id = temple.id
        db_session.commit()
    
    # Create essential accounts
    accounts = [
        # Main donation income account
        Account(
            temple_id=temple.id,
            account_code="D100",
            account_name="Donation Income",
            account_type=AccountType.INCOME,
            account_subtype=AccountSubType.DONATION_INCOME,
            is_system_account=True,
            allow_manual_entry=True
        ),
        # Cash account
        Account(
            temple_id=temple.id,
            account_code="A101",
            account_name="Cash in Hand - Counter",
            account_type=AccountType.ASSET,
            account_subtype=AccountSubType.CASH_BANK,
            is_system_account=True,
            allow_manual_entry=True
        ),
        # UPI account
        Account(
            temple_id=temple.id,
            account_code="A110",
            account_name="Bank - UPI",
            account_type=AccountType.ASSET,
            account_subtype=AccountSubType.CASH_BANK,
            is_system_account=False,
            allow_manual_entry=True
        ),
        # Inventory account (for in-kind donations)
        Account(
            temple_id=temple.id,
            account_code="1300",
            account_name="Inventory",
            account_type=AccountType.ASSET,
            account_subtype=AccountSubType.INVENTORY,
            is_system_account=True,
            allow_manual_entry=True
        ),
        # Asset account (for in-kind asset donations)
        Account(
            temple_id=temple.id,
            account_code="1500",
            account_name="Fixed Assets",
            account_type=AccountType.ASSET,
            account_subtype=AccountSubType.FIXED_ASSET,
            is_system_account=True,
            allow_manual_entry=True
        ),
        # Seva income account (main)
        Account(
            temple_id=temple.id,
            account_code="4200",
            account_name="Seva Income - Main",
            account_type=AccountType.INCOME,
            account_subtype=AccountSubType.OTHER_INCOME,
            is_system_account=True,
            allow_manual_entry=True
        ),
        # Sponsorship Receivable account
        Account(
            temple_id=temple.id,
            account_code="1402",
            account_name="Sponsorship Receivable",
            account_type=AccountType.ASSET,
            account_subtype=AccountSubType.RECEIVABLE,
            is_system_account=True,
            allow_manual_entry=True
        ),
        # Sponsorship Income account (parent)
        Account(
            temple_id=temple.id,
            account_code="4300",
            account_name="Sponsorship Income",
            account_type=AccountType.INCOME,
            account_subtype=AccountSubType.OTHER_INCOME,
            is_system_account=True,
            allow_manual_entry=True
        ),
        # Sponsorship Income - Direct Payment
        Account(
            temple_id=temple.id,
            account_code="4301",
            account_name="Sponsorship Income - Direct Payment",
            account_type=AccountType.INCOME,
            account_subtype=AccountSubType.OTHER_INCOME,
            is_system_account=True,
            allow_manual_entry=True
        ),
        # In-Kind Donation Income (for direct payment fallback)
        Account(
            temple_id=temple.id,
            account_code="4400",
            account_name="In-Kind Donation Income",
            account_type=AccountType.INCOME,
            account_subtype=AccountSubType.OTHER_INCOME,
            is_system_account=True,
            allow_manual_entry=True
        ),
        # In-Kind Sponsorship Income (preferred for direct payment)
        Account(
            temple_id=temple.id,
            account_code="4403",
            account_name="In-Kind Sponsorship Income",
            account_type=AccountType.INCOME,
            account_subtype=AccountSubType.OTHER_INCOME,
            is_system_account=True,
            allow_manual_entry=True
        ),
        # Flower Decoration Expense
        Account(
            temple_id=temple.id,
            account_code="E201",
            account_name="Flowers for daily pooja and decoration",
            account_type=AccountType.EXPENSE,
            account_subtype=AccountSubType.OPERATIONAL_EXPENSE,
            is_system_account=True,
            allow_manual_entry=True
        ),
        # Festival Expenses (default)
        Account(
            temple_id=temple.id,
            account_code="5400",
            account_name="Festival Expenses",
            account_type=AccountType.EXPENSE,
            account_subtype=AccountSubType.OPERATIONAL_EXPENSE,
            is_system_account=True,
            allow_manual_entry=True
        ),
        # Lighting Expense
        Account(
            temple_id=temple.id,
            account_code="E403",
            account_name="Lighting Expense",
            account_type=AccountType.EXPENSE,
            account_subtype=AccountSubType.OPERATIONAL_EXPENSE,
            is_system_account=True,
            allow_manual_entry=True
        ),
        # Tent Hiring
        Account(
            temple_id=temple.id,
            account_code="E401",
            account_name="Tent Hiring",
            account_type=AccountType.EXPENSE,
            account_subtype=AccountSubType.OPERATIONAL_EXPENSE,
            is_system_account=True,
            allow_manual_entry=True
        ),
        # Sound System
        Account(
            temple_id=temple.id,
            account_code="E402",
            account_name="Sound System",
            account_type=AccountType.EXPENSE,
            account_subtype=AccountSubType.OPERATIONAL_EXPENSE,
            is_system_account=True,
            allow_manual_entry=True
        ),
    ]
    
    for account in accounts:
        # Check if account already exists
        existing = db_session.query(Account).filter(
            Account.temple_id == temple.id,
            Account.account_code == account.account_code
        ).first()
        if not existing:
            db_session.add(account)
    
    db_session.commit()
    return accounts


@pytest.fixture
def authenticated_client(client, test_user, chart_of_accounts):
    """
    Create an authenticated test client.

    Returns a client with authentication headers for the test user.
    """
    # Login to get token
    response = client.post(
        "/api/v1/login",
        data={"username": test_user.email, "password": "testpass123"}
    )

    if response.status_code == 200:
        token = response.json().get("access_token")
        if token:
            client.headers["Authorization"] = f"Bearer {token}"
        else:
            # Try alternative response format
            token = response.json().get("token")
            if token:
                client.headers["Authorization"] = f"Bearer {token}"
    else:
        # Log error for debugging
        print(f"Login failed: {response.status_code} - {response.text}")

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
