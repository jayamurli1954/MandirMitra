# Quick Test Guide - MandirSync

## 🚀 Quick Start - Run Tests Now!

### Backend Tests (Python)

```bash
# Navigate to backend
cd backend

# Install dependencies (first time only)
pip install -r requirements.txt
pip install -r requirements-test.txt

# Run ALL tests (parallel, with coverage)
make test

# Or using pytest directly
pytest
```

### Frontend Tests (React)

```bash
# Navigate to frontend
cd frontend

# Install dependencies (first time only)
npm install

# Run tests in watch mode
npm test

# Run all tests once
npm run test:ci
```

---

## 📋 Backend Test Commands (Fastest to Most Complete)

```bash
# ⚡ FASTEST - No coverage, max speed
make test-fast

# 🎯 Run only unit tests
make test-unit

# 🔗 Run only integration tests
make test-integration

# 📊 Run with full coverage report
make test-coverage

# 🌙 Run panchang-specific tests
make test-panchang

# ⏱️ Skip slow tests
make test-no-slow

# 🐛 Debug mode (single process with debugger)
make test-debug

# 🧹 Clean test artifacts
make clean-test
```

---

## 📋 Frontend Test Commands

```bash
# Interactive watch mode (recommended for development)
npm test

# Run all tests once (for CI/CD)
npm run test:ci

# Run with coverage report
npm run test:coverage

# Watch mode
npm run test:watch

# Debug mode
npm run test:debug

# Update snapshots
npm run test:update
```

---

## 🎯 Running Specific Tests

### Backend

```bash
# Run a specific test file
pytest backend/tests/test_example_unit.py

# Run a specific test function
pytest backend/tests/test_example_unit.py::TestPanchangServiceUnit::test_gulika_period_calculation

# Run tests matching a pattern
pytest -k "panchang"

# Run tests by marker
pytest -m unit              # Only unit tests
pytest -m integration       # Only integration tests
pytest -m "not slow"        # All except slow tests
```

### Frontend

```bash
# In watch mode, press:
p    # Filter by filename pattern
t    # Filter by test name pattern
a    # Run all tests
f    # Run only failed tests
```

---

## 📊 Coverage Reports

### Backend

```bash
# Generate HTML coverage report
make test-coverage

# Open the report in browser
# Linux:
xdg-open backend/htmlcov/index.html

# macOS:
open backend/htmlcov/index.html

# Windows:
start backend/htmlcov/index.html
```

### Frontend

```bash
# Run tests with coverage
npm run test:coverage

# Open the report
# Linux:
xdg-open frontend/coverage/lcov-report/index.html

# macOS:
open frontend/coverage/lcov-report/index.html

# Windows:
start frontend/coverage/lcov-report/index.html
```

---

## 🏗️ Writing New Tests

### Backend - Using Factories

```python
import pytest
from tests.factories import TempleFactory, UserFactory

@pytest.mark.integration
def test_my_feature(db_session):
    # Set the session
    TempleFactory._meta.sqlalchemy_session = db_session
    UserFactory._meta.sqlalchemy_session = db_session

    # Create test data
    temple = TempleFactory(name="My Temple")
    user = UserFactory(temple=temple, role="accountant")

    # Your test code here
    assert user.temple_id == temple.id
```

### Frontend - Component Testing

```typescript
import { render, screen } from '@testing-library/react';
import userEvent from '@testing-library/user-event';
import MyComponent from './MyComponent';

describe('MyComponent', () => {
  it('renders correctly', () => {
    render(<MyComponent />);
    expect(screen.getByText('Hello')).toBeInTheDocument();
  });
});
```

---

## ⚡ Performance Tips

### Backend

1. **Use markers** to run only the tests you need:
   ```bash
   pytest -m unit  # Fast unit tests only
   ```

2. **Skip slow tests** during development:
   ```bash
   pytest -m "not slow"
   ```

3. **Use parallel execution** (already configured):
   ```bash
   pytest -n auto  # Use all CPU cores
   pytest -n 4     # Use 4 cores
   ```

4. **Run last failed tests first**:
   ```bash
   pytest --lf  # Last failed only
   pytest --ff  # Failed first, then others
   ```

### Frontend

1. **Use watch mode** - it only reruns affected tests:
   ```bash
   npm test  # Then press 'o' for changed tests only
   ```

2. **Clear cache** if tests behave strangely:
   ```bash
   npm test -- --clearCache
   ```

3. **Update snapshots** when intentional changes are made:
   ```bash
   npm run test:update
   ```

---

## 🐛 Debugging Tests

### Backend

```bash
# Run in debug mode
make test-debug

# Or with pytest directly
pytest --pdb  # Drops into debugger on failure

# Run single process with verbose output
pytest -n0 -vv
```

### Frontend

```bash
# Run in debug mode
npm run test:debug

# Or add debugger statement in test
debugger;  // Test will pause here
```

---

## 🔍 Example Test Output

### Successful Run
```
================================ test session starts =================================
platform linux -- Python 3.11.0, pytest-7.4.3, pluggy-1.3.0
plugins: asyncio-0.21.1, cov-4.1.0, xdist-3.5.0, mock-3.12.0
8 workers [45 items]
................................ [100%]

---------- coverage: platform linux, python 3.11.0 -----------
Name                        Stmts   Miss  Cover
-----------------------------------------------
app/models/temple.py           45      2    96%
app/models/user.py             38      1    97%
app/services/panchang.py      120      8    93%
-----------------------------------------------
TOTAL                         203     11    95%

================================ 45 passed in 2.35s ==================================
```

---

## 📚 Test Structure

```
backend/
├── tests/
│   ├── __init__.py
│   ├── conftest.py              # Fixtures and configuration
│   ├── factories.py             # Test data factories
│   ├── test_example_unit.py     # Unit test examples
│   └── test_example_integration.py  # Integration test examples
├── pytest.ini                   # Pytest configuration
├── Makefile                     # Test commands
└── requirements-test.txt        # Test dependencies

frontend/
├── src/
│   ├── __mocks__/              # Mock files
│   ├── setupTests.ts           # Test setup
│   └── **/*.test.tsx           # Test files next to components
├── jest.config.js              # Jest configuration
└── package.json                # Test scripts
```

---

## ❓ Troubleshooting

### Backend

**Problem**: ModuleNotFoundError
```bash
# Solution: Install dependencies
pip install -r requirements-test.txt
```

**Problem**: Tests are slow
```bash
# Solution: Skip coverage
make test-fast
```

**Problem**: Import errors
```bash
# Solution: Run from backend directory
cd backend
pytest
```

### Frontend

**Problem**: Tests timeout
```bash
# Solution: Increase timeout or check for infinite loops
# In jest.config.js, increase testTimeout
```

**Problem**: Module not found
```bash
# Solution: Clear cache
npm test -- --clearCache
```

**Problem**: Snapshot mismatches
```bash
# Solution: Review and update
npm run test:update
```

---

## 🎯 CI/CD

Tests run automatically on:
- Push to main, develop, or claude/** branches
- Pull requests to main or develop

View results in GitHub Actions tab.

---

## 📖 Full Documentation

For comprehensive details, see [TESTING_GUIDE.md](./TESTING_GUIDE.md)

---

**Last Updated**: 2025-11-28
