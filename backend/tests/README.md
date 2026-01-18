# MandirMitra Testing Guide

This directory contains automated tests for the MandirMitra backend API.

## 📁 Directory Structure

```
tests/
├── conftest.py          # Pytest fixtures and configuration
├── test_health.py       # Sample health check tests
├── test_donations.py    # Donation module tests (to be added)
├── test_sevas.py        # Seva booking tests (to be added)
├── test_hr.py           # HR module tests (to be added)
├── test_accounting.py   # Accounting tests (to be added)
└── README.md           # This file
```

## 🚀 Running Tests

### Install Testing Dependencies

```bash
cd backend
pip install pytest pytest-cov pytest-asyncio httpx
```

### Run All Tests

```bash
pytest
```

### Run with Coverage Report

```bash
pytest --cov=app --cov-report=term-missing
```

### Run Specific Test File

```bash
pytest tests/test_health.py
```

### Run Specific Test

```bash
pytest tests/test_health.py::TestHealthCheck::test_root_endpoint
```

### Run Tests by Marker (Category)

```bash
pytest -m donations     # Only donation tests
pytest -m hr            # Only HR tests
pytest -m api           # Only API tests
```

### Verbose Output

```bash
pytest -v
```

## 📝 Writing New Tests

### 1. Create a New Test File

Create `test_<module_name>.py` in the tests directory:

```python
import pytest
from fastapi import status


@pytest.mark.donations
class TestDonations:
    """Tests for donation endpoints."""

    def test_create_donation(self, authenticated_client, test_donation_data):
        """Test creating a new donation."""
        response = authenticated_client.post(
            "/api/donations/",
            json=test_donation_data
        )

        assert response.status_code == status.HTTP_201_CREATED
        data = response.json()
        assert data["donor_name"] == test_donation_data["donor_name"]
```

### 2. Use Available Fixtures

The `conftest.py` file provides these fixtures:

- **`client`**: FastAPI TestClient (unauthenticated)
- **`authenticated_client`**: TestClient with logged-in user
- **`db_session`**: Database session for tests
- **`test_user_data`**: Sample user data
- **`test_donation_data`**: Sample donation data
- **`test_seva_data`**: Sample seva booking data

### 3. Test Structure Best Practices

```python
def test_feature_name(self, client):
    """
    Clear description of what this test verifies.
    """
    # Arrange: Set up test data
    test_data = {...}

    # Act: Perform the action
    response = client.post("/api/endpoint", json=test_data)

    # Assert: Verify the results
    assert response.status_code == 200
    assert response.json()["key"] == "expected_value"
```

## 🏷️ Test Markers

Use markers to categorize tests:

- `@pytest.mark.unit` - Fast, isolated unit tests
- `@pytest.mark.integration` - Tests requiring database/services
- `@pytest.mark.slow` - Slow end-to-end tests
- `@pytest.mark.api` - API endpoint tests
- `@pytest.mark.donations` - Donation module tests
- `@pytest.mark.sevas` - Seva booking tests
- `@pytest.mark.hr` - HR module tests

## 🤖 GitHub Actions Integration

Tests run automatically on:
- Every push to main or claude/* branches
- Every pull request
- Manual trigger from GitHub UI

View results at: `https://github.com/YOUR-USERNAME/MandirMitra/actions`

## 📊 Coverage Goals

- **Minimum**: 70% overall coverage
- **Target**: 80%+ for critical modules (donations, accounting, sevas)
- **Exclude**: Migration files, test files, configuration

## 🐛 Debugging Failed Tests

### View detailed error output:

```bash
pytest -vv --tb=long
```

### Run only failed tests:

```bash
pytest --lf
```

### Stop at first failure:

```bash
pytest -x
```

### Print statements in tests:

```bash
pytest -s
```

## 📚 Resources

- [Pytest Documentation](https://docs.pytest.org/)
- [FastAPI Testing](https://fastapi.tiangolo.com/tutorial/testing/)
- [GitHub Actions Guide](https://docs.github.com/en/actions)

## ✅ Next Steps

1. Write tests for existing endpoints (donations, sevas, accounting)
2. Add integration tests with real PostgreSQL
3. Create E2E tests with Playwright (for frontend flows)
4. Set up load testing with Locust
5. Monitor coverage and maintain 80%+ goal
