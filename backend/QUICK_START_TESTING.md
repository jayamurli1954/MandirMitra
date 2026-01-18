# Quick Start: Running All Tests

## One Command to Run Everything

```bash
pytest -v --tb=short
```

This single command runs:
- ✅ All 151 existing tests
- ✅ New payment gateway tests (~8 tests)
- ✅ New notification service tests (~8 tests)
- ✅ New sponsorship tests (~6 tests)
- ✅ **Total: ~173 tests** (all integrated)

## What's Included

### Existing Tests (151 tests)
- Accounting (journal entries, trial balance, financial reports)
- Donations (cash, in-kind, receipts, 80G certificates)
- HR (departments, employees, payroll)
- Sevas (bookings, categories, receipts)
- Inventory (items, stock movements, audits)
- Hundi (collections, reports)
- Budget management
- Health checks

### New Tests (Integrated)
- **Payment Gateway** (`test_payment_gateway.py`)
  - Service initialization
  - Order creation (success/failure)
  - Payment verification
  - Error handling
  
- **Notification Service** (`test_notification_service.py`)
  - SMS sending (enabled/disabled, success/failure)
  - Email sending (enabled/disabled, success/failure)
  - Invalid input handling
  
- **Sponsorships** (`test_sponsorships.py`)
  - Sponsorship CRUD operations
  - Direct payment to vendor
  - Payment recording
  - Filtering and search

## Test Organization

All tests are automatically discovered by pytest. They follow the same structure:

```
tests/
├── test_*.py          # All test files
└── conftest.py        # Shared fixtures
```

## Running Specific Test Categories

```bash
# All unit tests (services)
pytest -v -m "unit"

# All API tests
pytest -v -m "api"

# Payment tests only
pytest -v -m "payment"

# Notification tests only
pytest -v -m "notifications"

# Sponsorship tests only
pytest -v -m "sponsorships"

# All new coverage improvement tests
pytest -v -m "payment or notifications or sponsorships"
```

## Coverage Report

```bash
# Full coverage report
pytest -v --cov=app --cov-report=term-missing

# HTML coverage report (opens in browser)
pytest --cov=app --cov-report=html
# Then open: htmlcov/index.html
```

## Expected Results

After running `pytest -v --tb=short`:

```
=========================================== 173 passed, 412 warnings in 50s ============================================
```

All tests should pass! The new tests are fully integrated and use the same fixtures and patterns as existing tests.

## Troubleshooting

**If new tests don't appear:**
- Check file names start with `test_`
- Check test functions start with `test_`
- Check test classes start with `Test`

**If tests fail:**
- Check that fixtures are available (they should be in `conftest.py`)
- Verify mocks match actual service implementations
- Check test data matches API schemas

## Next Steps

1. Run: `pytest -v --tb=short`
2. Verify all tests pass
3. Check coverage improvement
4. Add more tests following the same patterns

---

## 🎭 Frontend E2E Tests

We also have **Playwright E2E tests** for frontend! See the complete guide:

📖 **Full Testing Guide**: `../COMPREHENSIVE_TESTING_GUIDE.md`

### Quick Start for Frontend Tests

```bash
# Make sure backend and frontend are running first!
cd ../e2e-tests
npx playwright test --headed
```

This tests:
- ✅ Donation workflow
- ✅ Seva booking flow (including popup behavior!)
- ✅ HR module flow

---

**Everything is integrated!** Just run `pytest -v --tb=short` and all tests (existing + new) will run together! 🎉

