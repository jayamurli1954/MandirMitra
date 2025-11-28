# Testing Guide - MandirSync

This guide covers the optimized test configuration for both backend and frontend of MandirSync.

## Table of Contents

- [Backend Testing (Python/FastAPI)](#backend-testing-pythonfastapi)
- [Frontend Testing (React/Jest)](#frontend-testing-reactjest)
- [Performance Optimizations](#performance-optimizations)
- [CI/CD Integration](#cicd-integration)
- [Best Practices](#best-practices)

---

## Backend Testing (Python/FastAPI)

### Setup

1. **Install test dependencies:**
   ```bash
   cd backend
   pip install -r requirements-test.txt
   ```

### Running Tests

#### Quick Reference (Using Makefile)

```bash
# Run all tests (parallel execution)
make test

# Fast tests (no coverage)
make test-fast

# Tests with coverage report
make test-coverage

# Run only unit tests
make test-unit

# Run only integration tests
make test-integration

# Run panchang-specific tests
make test-panchang

# Exclude slow tests
make test-no-slow

# Watch mode (auto-rerun on changes)
make test-watch

# Debug mode (single process with pdb)
make test-debug

# Clean test artifacts
make clean-test
```

#### Direct pytest Commands

```bash
# Run all tests
pytest

# Run with specific number of workers
pytest -n 4

# Run specific test file
pytest test_panchang_fixes.py

# Run specific test function
pytest test_panchang_fixes.py::test_panchang_fixes

# Run tests matching pattern
pytest -k "panchang"

# Run with verbose output
pytest -v

# Run with extra verbose output
pytest -vv

# Stop after first failure
pytest -x

# Stop after N failures
pytest --maxfail=3

# Show local variables in tracebacks
pytest -l

# Run last failed tests only
pytest --lf

# Run failed tests first, then others
pytest --ff
```

### Test Markers

Use markers to categorize and selectively run tests:

```python
import pytest

@pytest.mark.unit
def test_basic_function():
    assert True

@pytest.mark.integration
def test_database_integration():
    # Database test
    pass

@pytest.mark.slow
def test_long_running():
    # Slow test
    pass

@pytest.mark.panchang
def test_panchang_calculation():
    # Panchang specific test
    pass
```

Run tests by marker:
```bash
pytest -m unit           # Only unit tests
pytest -m integration    # Only integration tests
pytest -m "not slow"     # All except slow tests
pytest -m "unit or integration"  # Unit OR integration
pytest -m "unit and not slow"    # Unit AND not slow
```

### Coverage Reports

```bash
# Generate HTML coverage report
pytest --cov=app --cov-report=html

# View coverage in terminal
pytest --cov=app --cov-report=term-missing

# Generate XML for CI tools
pytest --cov=app --cov-report=xml

# Open HTML report
open htmlcov/index.html  # macOS
xdg-open htmlcov/index.html  # Linux
```

### Performance Optimization

The pytest configuration includes several performance optimizations:

1. **Parallel Execution**: Uses `pytest-xdist` with `-n auto` to utilize all CPU cores
2. **Database Reuse**: `--reuse-db` flag to avoid recreating test database
3. **Fail Fast**: `--maxfail=5` stops after 5 failures
4. **Caching**: Test results are cached for faster reruns
5. **Selective Testing**: Use markers to run only necessary tests

### Code Quality

```bash
# Run all quality checks
make quality

# Format code
make format

# Security scan
make security

# Full CI pipeline
make ci
```

---

## Frontend Testing (React/Jest)

### Setup

1. **Install dependencies:**
   ```bash
   cd frontend
   npm install
   ```

### Running Tests

#### Available Scripts

```bash
# Interactive watch mode (default)
npm test

# Run all tests once (for CI)
npm run test:ci

# Run with coverage
npm run test:coverage

# Watch mode
npm run test:watch

# Debug mode
npm run test:debug

# Update snapshots
npm run test:update
```

#### Interactive Watch Mode Commands

When running `npm test`, you can use these interactive commands:

- `a` - Run all tests
- `f` - Run only failed tests
- `o` - Run only changed tests
- `p` - Filter by filename pattern
- `t` - Filter by test name pattern
- `q` - Quit watch mode
- `Enter` - Trigger test run

### Writing Tests

#### Basic Component Test

```typescript
import { render, screen } from '@testing-library/react';
import userEvent from '@testing-library/user-event';
import MyComponent from './MyComponent';

describe('MyComponent', () => {
  it('renders correctly', () => {
    render(<MyComponent />);
    expect(screen.getByText('Hello')).toBeInTheDocument();
  });

  it('handles user interaction', async () => {
    const user = userEvent.setup();
    render(<MyComponent />);

    const button = screen.getByRole('button');
    await user.click(button);

    expect(screen.getByText('Clicked')).toBeInTheDocument();
  });
});
```

#### Async Testing

```typescript
import { render, screen, waitFor } from '@testing-library/react';

it('loads data asynchronously', async () => {
  render(<AsyncComponent />);

  await waitFor(() => {
    expect(screen.getByText('Data loaded')).toBeInTheDocument();
  });
});
```

#### Mocking API Calls

```typescript
import axios from 'axios';

jest.mock('axios');
const mockedAxios = axios as jest.Mocked<typeof axios>;

it('fetches data from API', async () => {
  mockedAxios.get.mockResolvedValue({ data: { name: 'Test' } });

  render(<DataComponent />);

  await waitFor(() => {
    expect(screen.getByText('Test')).toBeInTheDocument();
  });
});
```

### Coverage Configuration

The Jest configuration includes coverage thresholds:

- **Branches**: 70%
- **Functions**: 70%
- **Lines**: 70%
- **Statements**: 70%

View coverage report:
```bash
npm run test:coverage
open coverage/lcov-report/index.html  # macOS
xdg-open coverage/lcov-report/index.html  # Linux
```

### Performance Optimization

The Jest configuration includes:

1. **Worker Optimization**: Uses 50% of available CPU cores
2. **Caching**: Results cached in `.jest-cache` directory
3. **Selective Testing**: Test match patterns to avoid unnecessary files
4. **Bail Configuration**: Stops after 5 failures
5. **Transform Optimization**: Efficient file transformation

---

## Performance Optimizations

### Backend Performance Features

1. **Parallel Test Execution**
   - Uses `pytest-xdist` with `-n auto`
   - Automatically detects and uses all available CPU cores
   - Can be customized: `pytest -n 4` for 4 workers

2. **Test Discovery Optimization**
   - Excludes unnecessary directories (migrations, scripts, etc.)
   - Focused test file patterns
   - Reduced filesystem scanning

3. **Coverage Optimization**
   - Parallel coverage with `coverage` branch tracking
   - Excludes test files from coverage
   - Smart exclusion of boilerplate code

4. **Database Optimization**
   - `--reuse-db` flag for faster database tests
   - Consider using `pytest-django` fixtures for database isolation

### Frontend Performance Features

1. **Worker Management**
   - Configured to use 50% of CPU cores
   - Balances speed with system resources
   - Can be adjusted in `jest.config.js`

2. **Cache Management**
   - Persistent cache in `.jest-cache`
   - Significantly faster subsequent runs
   - Clear cache: `npm test -- --clearCache`

3. **Test Isolation**
   - `clearMocks: true` prevents test interference
   - Fresh module registry for each test file
   - Isolated test environments

4. **Watch Mode Optimization**
   - Only reruns affected tests
   - Smart file change detection
   - TypeAhead plugins for faster filtering

---

## CI/CD Integration

### Backend CI Configuration

```yaml
# Example GitHub Actions configuration
name: Backend Tests

on: [push, pull_request]

jobs:
  test:
    runs-on: ubuntu-latest

    steps:
      - uses: actions/checkout@v3

      - name: Set up Python
        uses: actions/setup-python@v4
        with:
          python-version: '3.11'

      - name: Install dependencies
        run: |
          cd backend
          pip install -r requirements-test.txt

      - name: Run tests
        run: |
          cd backend
          pytest --cov=app --cov-report=xml --cov-report=term

      - name: Upload coverage
        uses: codecov/codecov-action@v3
        with:
          file: ./backend/coverage.xml
```

### Frontend CI Configuration

```yaml
# Example GitHub Actions configuration
name: Frontend Tests

on: [push, pull_request]

jobs:
  test:
    runs-on: ubuntu-latest

    steps:
      - uses: actions/checkout@v3

      - name: Set up Node.js
        uses: actions/setup-node@v3
        with:
          node-version: '18'

      - name: Install dependencies
        run: |
          cd frontend
          npm ci

      - name: Run tests
        run: |
          cd frontend
          npm run test:ci

      - name: Upload coverage
        uses: codecov/codecov-action@v3
        with:
          file: ./frontend/coverage/coverage-final.json
```

---

## Best Practices

### General Best Practices

1. **Write Tests First (TDD)**
   - Define expected behavior before implementation
   - Leads to better design and fewer bugs

2. **Keep Tests Independent**
   - Each test should run in isolation
   - No dependencies between tests
   - Use fixtures/setup for shared state

3. **Use Descriptive Names**
   - Test names should describe what they test
   - Use `describe` blocks to group related tests
   - Example: `test_panchang_calculates_gulika_correctly_for_monday`

4. **Test One Thing at a Time**
   - Each test should verify one specific behavior
   - Makes debugging easier
   - Clearer test failures

5. **Use Appropriate Assertions**
   - Choose the most specific assertion
   - Better error messages
   - Example: Use `toHaveLength(5)` instead of `toBe(array.length === 5)`

### Backend Specific

1. **Use Fixtures for Common Setup**
   ```python
   @pytest.fixture
   def panchang_service():
       return PanchangService()
   ```

2. **Mark Tests Appropriately**
   ```python
   @pytest.mark.slow
   @pytest.mark.integration
   def test_complex_integration():
       pass
   ```

3. **Use Parametrize for Multiple Cases**
   ```python
   @pytest.mark.parametrize("day,expected_period", [
       ("Monday", 6),
       ("Tuesday", 3),
       ("Wednesday", 2),
   ])
   def test_gulika_period(day, expected_period):
       assert calculate_gulika_period(day) == expected_period
   ```

### Frontend Specific

1. **Use Testing Library Queries**
   - Prefer `getByRole` over `getByTestId`
   - Makes tests more accessible
   - Better reflects user behavior

2. **Avoid Implementation Details**
   - Test behavior, not implementation
   - Don't test internal state
   - Focus on user-facing functionality

3. **Clean Up After Tests**
   ```typescript
   afterEach(() => {
     jest.clearAllMocks();
     cleanup();
   });
   ```

---

## Troubleshooting

### Common Issues

#### Backend

**Issue**: Tests are slow
- **Solution**: Use `make test-fast` to skip coverage
- **Solution**: Use markers to run specific test subsets
- **Solution**: Check for slow database queries

**Issue**: Import errors
- **Solution**: Ensure `PYTHONPATH` is set correctly
- **Solution**: Run tests from backend directory
- **Solution**: Check virtual environment activation

**Issue**: Database connection errors
- **Solution**: Ensure test database is configured
- **Solution**: Check database permissions
- **Solution**: Use `--reuse-db` flag cautiously

#### Frontend

**Issue**: Tests timeout
- **Solution**: Increase timeout in `jest.config.js`
- **Solution**: Use `waitFor` for async operations
- **Solution**: Check for infinite loops

**Issue**: Module not found
- **Solution**: Clear cache: `npm test -- --clearCache`
- **Solution**: Reinstall: `rm -rf node_modules && npm install`
- **Solution**: Check module name mapper in jest config

**Issue**: Snapshot mismatches
- **Solution**: Review changes carefully
- **Solution**: Update snapshots: `npm run test:update`
- **Solution**: Use `toMatchInlineSnapshot` for small snapshots

---

## Resources

### Backend Testing
- [Pytest Documentation](https://docs.pytest.org/)
- [pytest-xdist](https://pytest-xdist.readthedocs.io/)
- [Coverage.py](https://coverage.readthedocs.io/)

### Frontend Testing
- [Jest Documentation](https://jestjs.io/)
- [React Testing Library](https://testing-library.com/react)
- [Testing Library Queries](https://testing-library.com/docs/queries/about)

---

## Quick Start Commands

### Backend
```bash
cd backend
make install-test    # Install dependencies
make test           # Run all tests
make test-coverage  # Run with coverage
```

### Frontend
```bash
cd frontend
npm install         # Install dependencies
npm test           # Run tests in watch mode
npm run test:ci    # Run all tests once
```

---

**Last Updated**: 2025-11-28
**Version**: 1.0.0
