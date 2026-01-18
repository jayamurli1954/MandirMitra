# 🧪 Comprehensive Testing Guide - MandirMitra

Complete guide for running **both Backend (Pytest) and Frontend (Playwright E2E)** tests.

---

## 📋 Table of Contents

1. [Quick Start](#quick-start)
2. [Backend Tests (Pytest)](#backend-tests-pytest)
3. [Frontend E2E Tests (Playwright)](#frontend-e2e-tests-playwright)
4. [Complete Testing Workflow](#complete-testing-workflow)
5. [Test Coverage Overview](#test-coverage-overview)

---

## 🚀 Quick Start

### Run All Backend Tests
```bash
cd backend
pytest -v --tb=short
```

### Run All Frontend E2E Tests
```bash
cd e2e-tests
npx playwright test --headed
```

### Run Everything (Recommended Workflow)
```bash
# Terminal 1: Start Backend
cd backend
python -m uvicorn app.main:app --reload --host 0.0.0.0 --port 8000

# Terminal 2: Start Frontend
cd frontend
npm start

# Terminal 3: Run Backend Tests
cd backend
pytest -v --tb=short

# Terminal 4: Run Frontend E2E Tests
cd e2e-tests
npx playwright test --headed
```

---

## 🔧 Backend Tests (Pytest)

### Overview
- **Framework**: Pytest
- **Location**: `backend/tests/`
- **Total Tests**: ~173 tests
- **Coverage**: Unit tests, Integration tests, API tests

### Test Categories

#### ✅ Existing Tests (151 tests)
- **Accounting** - Journal entries, trial balance, financial reports
- **Donations** - Cash, in-kind, receipts, 80G certificates
- **HR** - Departments, employees, payroll, payslips
- **Sevas** - Bookings, categories, receipts, accounting
- **Inventory** - Items, stock movements, audits, alerts
- **Hundi** - Collections, reports, denominations
- **Budget** - Budget planning and tracking
- **Health Checks** - API health endpoints

#### ✨ New Tests (22 tests)
- **Payment Gateway** (`test_payment_gateway.py`) - 8 tests
  - Service initialization
  - Order creation (success/failure)
  - Payment verification
  - Error handling
  
- **Notification Service** (`test_notification_service.py`) - 8 tests
  - SMS sending (enabled/disabled, success/failure)
  - Email sending (enabled/disabled, success/failure)
  - Invalid input handling
  
- **Sponsorships** (`test_sponsorships.py`) - 6 tests
  - Sponsorship CRUD operations
  - Direct payment to vendor
  - Payment recording
  - Filtering and search

### Running Backend Tests

#### Run All Tests
```bash
cd backend
pytest -v --tb=short
```

#### Run Specific Categories
```bash
# Unit tests only (services)
pytest -v -m "unit"

# API tests only
pytest -v -m "api"

# Payment tests
pytest -v -m "payment"

# Notification tests
pytest -v -m "notifications"

# Sponsorship tests
pytest -v -m "sponsorships"

# HR tests
pytest -v -m "hr"

# Donation tests
pytest -v -m "donations"

# Seva tests
pytest -v -m "sevas"
```

#### Run Specific Test Files
```bash
# Payment gateway tests
pytest tests/test_payment_gateway.py -v

# Notification service tests
pytest tests/test_notification_service.py -v

# Sponsorship tests
pytest tests/test_sponsorships.py -v

# Donation tests
pytest tests/test_donations.py -v

# Seva tests
pytest tests/test_sevas.py -v
```

#### Coverage Reports
```bash
# Terminal coverage report
pytest -v --cov=app --cov-report=term-missing

# HTML coverage report (opens in browser)
pytest --cov=app --cov-report=html
# Then open: htmlcov/index.html

# Coverage for specific module
pytest tests/test_payment_gateway.py --cov=app.services.payment_gateway --cov-report=term-missing
```

### Expected Output
```
=========================================== 173 passed, 412 warnings in 50s ============================================
```

---

## 🎭 Frontend E2E Tests (Playwright)

### Overview
- **Framework**: Playwright
- **Location**: `e2e-tests/tests/`
- **Total Tests**: ~15 tests
- **Coverage**: Complete user workflows, UI interactions, popup behavior

### Test Files

#### 1. `donation-flow.spec.js` - Donation Workflow
Tests complete donation creation flow:
- ✅ Navigate to donations page
- ✅ Open new donation form
- ✅ Search devotee by mobile
- ✅ Fill donation details
- ✅ Select payment method (cash/UPI)
- ✅ Submit donation
- ✅ Verify receipt generated
- ✅ Check donation appears in list
- ✅ Verify accounting entry created

#### 2. `seva-booking-flow.spec.js` - Seva Booking Flow ⭐
Tests seva booking including popup behavior:
- ✅ Navigate to sevas page
- ✅ Click "Book Seva" button
- ✅ Enter mobile number
- ✅ Auto-fill devotee (if exists)
- ✅ OR create new devotee
- ✅ Select seva, date, time
- ✅ Enter payment details
- ✅ Submit booking
- ✅ Verify booking saved
- ✅ Check booking appears in calendar
- ✅ **Verify popup closes properly** ← Tests your popup issue!

#### 3. `hr-flow.spec.js` - HR Module Flow
Tests complete HR workflow:
- ✅ Navigate to HR module
- ✅ Add employee
- ✅ Create salary structure
- ✅ Process payroll
- ✅ Generate payslip
- ✅ Export reports

### Setup (First Time Only)

```bash
cd e2e-tests

# Install dependencies
npm install

# Install Playwright browsers
npx playwright install
```

### Running Frontend E2E Tests

#### Prerequisites
**IMPORTANT**: Make sure both backend and frontend are running before running E2E tests!

```bash
# Terminal 1: Backend
cd backend
python -m uvicorn app.main:app --reload --host 0.0.0.0 --port 8000

# Terminal 2: Frontend
cd frontend
npm start
```

#### Run All E2E Tests
```bash
cd e2e-tests

# Run all tests (headless - no browser window)
npx playwright test

# Run with browser visible (recommended for debugging)
npx playwright test --headed

# Run with UI mode (best for exploring)
npx playwright test --ui
```

#### Run Specific Tests
```bash
# Run seva booking test (tests your popup!)
npx playwright test seva-booking-flow.spec.js --headed

# Run donation flow test
npx playwright test donation-flow.spec.js --headed

# Run HR flow test
npx playwright test hr-flow.spec.js --headed
```

#### Debug Mode
```bash
# Debug specific test (step through)
npx playwright test seva-booking-flow.spec.js --debug

# Run with single worker (see everything)
npx playwright test --headed --workers=1
```

#### View Test Reports
```bash
# Generate and view HTML report
npx playwright show-report
```

### Expected Output
```
Running 15 tests using 3 workers

  ✓ donation-flow.spec.js:5:1 › Create cash donation (3.2s)
  ✓ donation-flow.spec.js:25:1 › Create UPI donation (2.8s)
  ✓ seva-booking-flow.spec.js:7:1 › Book seva for existing devotee (4.1s)
  ✓ seva-booking-flow.spec.js:30:1 › Book seva for new devotee (5.3s)
  ✓ hr-flow.spec.js:6:1 › Add employee and process payroll (6.2s)

  15 passed (21.6s)
```

### Debugging Your Seva Popup Issue

Since you had a seva popup issue, use this specific test:

```bash
cd e2e-tests

# Run seva test with browser visible
npx playwright test seva-booking-flow.spec.js --headed

# Or in debug mode to step through
npx playwright test seva-booking-flow.spec.js --debug
```

This will:
- ✅ Open the seva page
- ✅ Click "Book Seva"
- ✅ Fill the form
- ✅ Click Save
- ✅ **Verify the popup behavior**
- ✅ Take screenshot if it fails

### Quick Commands Summary

```bash
# Setup (first time only)
cd e2e-tests
npm install
npx playwright install

# Run all tests
npx playwright test

# Run with browser visible
npx playwright test --headed

# Run specific test
npx playwright test seva-booking-flow.spec.js --headed

# Debug mode
npx playwright test --debug

# UI mode (best for exploring)
npx playwright test --ui

# Generate HTML report
npx playwright show-report
```

---

## 🔄 Complete Testing Workflow

### Recommended Testing Sequence

#### 1. Backend Tests (Unit/Integration)
```bash
cd backend
pytest -v --tb=short
```
**Purpose**: Verify API endpoints, business logic, database operations

#### 2. Frontend E2E Tests (User Flows)
```bash
# Make sure backend and frontend are running first!
cd e2e-tests
npx playwright test --headed
```
**Purpose**: Verify complete user workflows, UI interactions, popup behavior

#### 3. Manual Testing
- Use checklist for edge cases
- Test printing/exports
- Test UI/UX
- Test on different browsers/devices

### Full Test Suite Run

Create a script to run everything:

**Windows (PowerShell)**:
```powershell
# test-all.ps1
Write-Host "Starting Backend Tests..." -ForegroundColor Green
cd backend
pytest -v --tb=short

Write-Host "`nStarting Frontend E2E Tests..." -ForegroundColor Green
cd ..\e2e-tests
npx playwright test --headed
```

**Linux/Mac (Bash)**:
```bash
#!/bin/bash
# test-all.sh

echo "Starting Backend Tests..."
cd backend
pytest -v --tb=short

echo ""
echo "Starting Frontend E2E Tests..."
cd ../e2e-tests
npx playwright test --headed
```

---

## 📊 Test Coverage Overview

### Backend Coverage
- **Total Tests**: ~173 tests
- **Coverage Areas**:
  - ✅ Accounting (100% critical paths)
  - ✅ Donations (95%+)
  - ✅ HR/Payroll (90%+)
  - ✅ Sevas (90%+)
  - ✅ Inventory (85%+)
  - ✅ Payment Gateway (80%+)
  - ✅ Notifications (80%+)
  - ✅ Sponsorships (70%+)
  - ⚠️ Bank Reconciliation (14% - needs improvement)
  - ⚠️ Financial Closing (9% - needs improvement)

### Frontend Coverage
- **Total Tests**: ~15 E2E tests
- **Coverage Areas**:
  - ✅ Donation workflow (complete)
  - ✅ Seva booking workflow (complete, including popup)
  - ✅ HR workflow (complete)
  - ⚠️ Other modules (can be expanded)

### Combined Coverage
- **Backend**: API endpoints, business logic, database
- **Frontend**: User workflows, UI interactions, popup behavior
- **Together**: Complete system validation

---

## 🐛 Troubleshooting

### Backend Tests

**If tests don't appear:**
- Check file names start with `test_`
- Check test functions start with `test_`
- Check test classes start with `Test`

**If tests fail:**
- Check that fixtures are available (in `conftest.py`)
- Verify mocks match actual service implementations
- Check test data matches API schemas
- Ensure database is properly set up

**Rate limiting issues:**
- Rate limiting is disabled in debug mode
- Check `backend/app/core/config.py` for `RATE_LIMIT_ENABLED`

### Frontend E2E Tests

**If tests fail to start:**
- Ensure backend is running on `http://localhost:8000`
- Ensure frontend is running on `http://localhost:3000` (or configured port)
- Check `playwright.config.js` for correct base URLs

**If browser doesn't open:**
- Run with `--headed` flag
- Check that browsers are installed: `npx playwright install`

**If tests timeout:**
- Increase timeout in `playwright.config.js`
- Check network connectivity
- Verify backend/frontend are responding

**Popup issues:**
- Use `--debug` mode to step through
- Check screenshots in `test-results/`
- Verify popup selectors in test file

---

## 📁 Test File Structure

```
MandirMitra/
├── backend/
│   ├── tests/
│   │   ├── test_accounting.py
│   │   ├── test_donations.py
│   │   ├── test_hr.py
│   │   ├── test_sevas.py
│   │   ├── test_inventory.py
│   │   ├── test_hundi.py
│   │   ├── test_budget.py
│   │   ├── test_payment_gateway.py      # ✨ NEW
│   │   ├── test_notification_service.py # ✨ NEW
│   │   ├── test_sponsorships.py         # ✨ NEW
│   │   └── conftest.py                  # Shared fixtures
│   └── pytest.ini                       # Pytest configuration
│
└── e2e-tests/
    ├── tests/
    │   ├── donation-flow.spec.js
    │   ├── seva-booking-flow.spec.js
    │   └── hr-flow.spec.js
    ├── playwright.config.js
    └── package.json
```

---

## ✅ Quick Reference

### Backend Tests
```bash
cd backend
pytest -v --tb=short                    # Run all
pytest -v -m "unit"                     # Unit tests only
pytest -v -m "api"                     # API tests only
pytest --cov=app --cov-report=html     # Coverage report
```

### Frontend E2E Tests
```bash
cd e2e-tests
npx playwright test                      # Run all (headless)
npx playwright test --headed            # Run all (visible)
npx playwright test --ui                # UI mode
npx playwright test seva-booking-flow.spec.js --debug  # Debug specific
```

---

## 🎯 Next Steps

1. ✅ Run backend tests: `cd backend && pytest -v --tb=short`
2. ✅ Run frontend E2E tests: `cd e2e-tests && npx playwright test --headed`
3. ✅ Review coverage reports
4. ✅ Add more tests for low-coverage areas
5. ✅ Expand E2E tests for other modules

---

## 📝 Notes

- **Backend tests** run independently (no frontend needed)
- **Frontend E2E tests** require both backend and frontend to be running
- **E2E tests** are slower but test complete user workflows
- **Backend tests** are faster and test individual components
- **Both** are important for comprehensive testing!

---

**Happy Testing! 🚀**

For questions or issues, check:
- Backend test docs: `backend/QUICK_START_TESTING.md`
- Frontend test docs: `e2e-tests/README.md` (if exists)
- Coverage plan: `backend/TEST_COVERAGE_IMPROVEMENT_PLAN.md`













