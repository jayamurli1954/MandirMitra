# Test Integration Guide

## Overview

All new test files have been integrated into the existing pytest test suite. When you run `pytest -v --tb=short`, it will automatically discover and run all tests, including the new coverage improvement tests.

## New Test Files Added

### 1. `tests/test_payment_gateway.py`
- **Type**: Unit tests
- **Markers**: `@pytest.mark.unit`, `@pytest.mark.payment`
- **Coverage Target**: Payment Gateway Service (0% → 80%+)
- **Tests**: Service initialization, order creation, payment verification, error handling

### 2. `tests/test_notification_service.py`
- **Type**: Unit tests
- **Markers**: `@pytest.mark.unit`, `@pytest.mark.notifications`
- **Coverage Target**: Notification Service (0% → 80%+)
- **Tests**: SMS/Email sending, service enabled/disabled states, API failures

### 3. `tests/test_sponsorships.py`
- **Type**: API integration tests
- **Markers**: `@pytest.mark.sponsorships`, `@pytest.mark.api`
- **Coverage Target**: Sponsorships API (8.72% → 70%+)
- **Tests**: Sponsorship CRUD, direct payment, payment recording, filtering

## Running All Tests

### Standard Command (Runs Everything)
```bash
pytest -v --tb=short
```

This will run:
- ✅ All existing tests (151 tests)
- ✅ New payment gateway tests
- ✅ New notification service tests
- ✅ New sponsorship tests
- ✅ All other test files

### Run Specific Test Categories

```bash
# Run only service tests (unit tests)
pytest -v -m "unit"

# Run only API tests
pytest -v -m "api"

# Run payment-related tests
pytest -v -m "payment"

# Run notification tests
pytest -v -m "notifications"

# Run sponsorship tests
pytest -v -m "sponsorships"

# Run all new coverage improvement tests
pytest -v -m "payment or notifications or sponsorships"
```

### Run Specific Test Files

```bash
# Payment gateway tests only
pytest tests/test_payment_gateway.py -v

# Notification service tests only
pytest tests/test_notification_service.py -v

# Sponsorship tests only
pytest tests/test_sponsorships.py -v
```

### Run with Coverage Report

```bash
# Full coverage report
pytest -v --cov=app --cov-report=term-missing

# Coverage for specific modules
pytest tests/test_payment_gateway.py --cov=app.services.payment_gateway --cov-report=term-missing
pytest tests/test_notification_service.py --cov=app.services.notification_service --cov-report=term-missing
pytest tests/test_sponsorships.py --cov=app.api.sponsorships --cov-report=term-missing
```

## Test Integration Details

### Fixtures Used
All new tests use the same fixtures as existing tests:
- `authenticated_client` - For API endpoint tests
- `test_user` - For user context
- `db_session` - For database operations
- `chart_of_accounts` - For accounting setup

### Test Patterns
New tests follow the same patterns as existing tests:
- ✅ Use `@pytest.mark` decorators for categorization
- ✅ Use `authenticated_client` for API tests
- ✅ Use `unittest.mock` for mocking external services
- ✅ Follow naming convention: `test_<feature>_<scenario>`
- ✅ Include docstrings explaining what each test does

### Mocking Strategy
- **Payment Gateway**: Mocks Razorpay client to avoid real API calls
- **Notification Service**: Mocks HTTP requests to SMS/Email providers
- **No External Dependencies**: All external services are mocked

## Expected Test Count

After integration:
- **Before**: 151 tests
- **After**: ~165-170 tests (estimated)
  - +8-10 payment gateway tests
  - +8-10 notification service tests
  - +6-8 sponsorship tests

## Verification

To verify all tests are integrated:

```bash
# List all test files
pytest --collect-only

# Count total tests
pytest --collect-only -q | grep "test session starts" -A 1

# Run all tests and see summary
pytest -v --tb=short
```

## Troubleshooting

### If new tests don't run:
1. Check that test files are in `backend/tests/` directory
2. Verify file names start with `test_`
3. Check that test classes start with `Test`
4. Ensure test functions start with `test_`

### If tests fail:
1. Check that required fixtures are available in `conftest.py`
2. Verify mock patches match actual service implementations
3. Check that test data matches API schema requirements

### If coverage doesn't improve:
1. Run tests with `--cov` flag
2. Check coverage report: `htmlcov/index.html`
3. Verify tests are actually calling the code paths

## Next Steps

1. ✅ Run full test suite: `pytest -v --tb=short`
2. ✅ Verify all tests pass
3. ✅ Check coverage improvement
4. ✅ Add more tests following the same patterns
5. ✅ Extend to other low-coverage modules

## Test Organization

```
backend/tests/
├── test_accounting.py          # Accounting tests
├── test_donations.py            # Donation tests
├── test_hr.py                   # HR/Payroll tests
├── test_sevas.py                # Seva tests
├── test_inventory.py             # Inventory tests
├── test_hundi.py                # Hundi tests
├── test_budget.py               # Budget tests
├── test_health.py               # Health check tests
├── test_example_unit.py         # Unit test examples
├── test_example_integration.py  # Integration test examples
├── test_payment_gateway.py      # ✨ NEW: Payment gateway tests
├── test_notification_service.py # ✨ NEW: Notification tests
└── test_sponsorships.py         # ✨ NEW: Sponsorship tests
```

All tests are automatically discovered and run together! 🎉













