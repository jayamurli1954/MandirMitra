# Makefile for MandirSync - Temple Management System
# Makes running tests and common tasks super easy!

.PHONY: help test test-fast test-parallel test-watch test-changed test-failed \
        test-coverage test-unit test-integration test-api test-donations test-hr \
        test-sevas test-accounting test-inventory test-e2e test-load \
        install install-test install-e2e install-load clean lint format \
        run-backend run-frontend migrate seed

# Default target - show help
help:
	@echo "╔════════════════════════════════════════════════════════════╗"
	@echo "║          MandirSync - Make Commands Reference             ║"
	@echo "╚════════════════════════════════════════════════════════════╝"
	@echo ""
	@echo "🧪 TESTING COMMANDS"
	@echo "  make test              - Run all tests (parallel, with coverage)"
	@echo "  make test-fast         - Run tests without coverage (faster)"
	@echo "  make test-parallel     - Run tests in parallel (uses all CPUs)"
	@echo "  make test-watch        - Auto-run tests on file changes"
	@echo "  make test-changed      - Run tests for changed files only"
	@echo "  make test-failed       - Re-run only failed tests"
	@echo "  make test-coverage     - Generate detailed coverage report"
	@echo ""
	@echo "🎯 TEST BY MODULE"
	@echo "  make test-unit         - Run fast unit tests only"
	@echo "  make test-integration  - Run integration tests"
	@echo "  make test-api          - Run API endpoint tests"
	@echo "  make test-donations    - Run donation module tests"
	@echo "  make test-hr           - Run HR/payroll tests"
	@echo "  make test-sevas        - Run seva booking tests"
	@echo "  make test-accounting   - Run accounting tests"
	@echo "  make test-inventory    - Run inventory tests"
	@echo ""
	@echo "🎭 E2E & LOAD TESTING"
	@echo "  make test-e2e          - Run end-to-end browser tests"
	@echo "  make test-load         - Run load tests (Locust)"
	@echo ""
	@echo "📦 INSTALLATION"
	@echo "  make install           - Install all dependencies"
	@echo "  make install-test      - Install testing dependencies"
	@echo "  make install-e2e       - Install E2E testing (Playwright)"
	@echo "  make install-load      - Install load testing (Locust)"
	@echo ""
	@echo "🚀 DEVELOPMENT"
	@echo "  make run-backend       - Start FastAPI backend server"
	@echo "  make run-frontend      - Start React frontend"
	@echo "  make migrate           - Run database migrations"
	@echo "  make seed              - Seed database with test data"
	@echo ""
	@echo "🔧 CODE QUALITY"
	@echo "  make lint              - Check code style"
	@echo "  make format            - Auto-format code"
	@echo "  make clean             - Remove cache and temp files"
	@echo ""

# ============================================================================
# TESTING COMMANDS
# ============================================================================

# Run all tests with coverage (DEFAULT)
test:
	@echo "Running all tests with coverage..."
	cd backend && pytest

# Fast tests without coverage (for development)
test-fast:
	@echo "Running fast tests (no coverage)..."
	cd backend && pytest --no-cov -x

# Parallel execution (uses all CPU cores)
test-parallel:
	@echo "Running tests in parallel..."
	cd backend && pytest -n auto

# Auto-run tests on file changes (requires pytest-watch)
test-watch:
	@echo "Watching for file changes..."
	cd backend && ptw -- -v

# Run tests for changed files only (requires pytest-testmon)
test-changed:
	@echo "Running tests for changed files..."
	cd backend && pytest --testmon

# Re-run only failed tests
test-failed:
	@echo "Re-running failed tests..."
	cd backend && pytest --lf -v

# Generate detailed coverage report
test-coverage:
	@echo "Generating coverage report..."
	cd backend && pytest --cov=app --cov-report=html --cov-report=term
	@echo "✅ Coverage report generated: backend/htmlcov/index.html"

# ============================================================================
# TEST BY CATEGORY/MODULE
# ============================================================================

# Unit tests only (fast)
test-unit:
	@echo "Running unit tests..."
	cd backend && pytest -m unit -v

# Integration tests (slower)
test-integration:
	@echo "Running integration tests..."
	cd backend && pytest -m integration -v

# API endpoint tests
test-api:
	@echo "Running API tests..."
	cd backend && pytest -m api -v

# Module-specific tests
test-donations:
	@echo "Running donation module tests..."
	cd backend && pytest tests/test_donations.py -v

test-hr:
	@echo "Running HR module tests..."
	cd backend && pytest tests/test_hr.py -v

test-sevas:
	@echo "Running seva module tests..."
	cd backend && pytest tests/test_sevas.py -v

test-accounting:
	@echo "Running accounting module tests..."
	cd backend && pytest tests/test_accounting.py -v

test-inventory:
	@echo "Running inventory module tests..."
	cd backend && pytest tests/test_inventory.py -v

test-budget:
	@echo "Running budget module tests..."
	cd backend && pytest tests/test_budget.py -v

test-hundi:
	@echo "Running hundi module tests..."
	cd backend && pytest tests/test_hundi.py -v

# ============================================================================
# E2E & LOAD TESTING
# ============================================================================

# Run E2E tests with Playwright
test-e2e:
	@echo "Running E2E tests..."
	cd e2e-tests && npm test

# Run E2E tests with browser visible
test-e2e-headed:
	@echo "Running E2E tests (headed mode)..."
	cd e2e-tests && npm run test:headed

# Run load tests with Locust
test-load:
	@echo "Starting Locust load testing..."
	@echo "Open http://localhost:8089 in your browser"
	cd load-tests && locust -f locustfile.py --host=http://localhost:8000

# ============================================================================
# INSTALLATION
# ============================================================================

# Install all dependencies
install: install-backend install-frontend install-test install-e2e install-load
	@echo "✅ All dependencies installed!"

# Install backend dependencies
install-backend:
	@echo "Installing backend dependencies..."
	cd backend && pip install -r requirements.txt

# Install frontend dependencies
install-frontend:
	@echo "Installing frontend dependencies..."
	cd frontend && npm install

# Install testing dependencies
install-test:
	@echo "Installing testing dependencies..."
	cd backend && pip install -r requirements-test.txt

# Install E2E testing
install-e2e:
	@echo "Installing Playwright..."
	cd e2e-tests && npm install && npx playwright install --with-deps

# Install load testing
install-load:
	@echo "Installing Locust..."
	cd load-tests && pip install -r requirements.txt

# ============================================================================
# DEVELOPMENT
# ============================================================================

# Start backend server
run-backend:
	@echo "Starting FastAPI backend on http://localhost:8000"
	cd backend && uvicorn app.main:app --reload --host 0.0.0.0 --port 8000

# Start frontend
run-frontend:
	@echo "Starting React frontend on http://localhost:3000"
	cd frontend && npm start

# Run database migrations
migrate:
	@echo "Running database migrations..."
	cd backend && alembic upgrade head

# Seed database with test data
seed:
	@echo "Seeding database..."
	cd backend && python seed_chart_of_accounts.py
	cd backend && python seed_sevas.py

# ============================================================================
# CODE QUALITY
# ============================================================================

# Lint code
lint:
	@echo "Linting Python code..."
	cd backend && flake8 app/ --max-line-length=120 --extend-ignore=E203,W503

# Format code
format:
	@echo "Formatting Python code..."
	cd backend && black app/
	cd backend && isort app/

# Clean cache and temp files
clean:
	@echo "Cleaning cache and temp files..."
	find . -type d -name "__pycache__" -exec rm -rf {} + 2>/dev/null || true
	find . -type d -name ".pytest_cache" -exec rm -rf {} + 2>/dev/null || true
	find . -type d -name ".coverage" -exec rm -rf {} + 2>/dev/null || true
	find . -type d -name "htmlcov" -exec rm -rf {} + 2>/dev/null || true
	find . -type f -name "*.pyc" -delete 2>/dev/null || true
	@echo "✅ Cleaned!"

# ============================================================================
# CONTINUOUS INTEGRATION
# ============================================================================

# Run full CI pipeline (what GitHub Actions runs)
ci:
	@echo "Running full CI pipeline..."
	make lint
	make test
	make test-e2e
	@echo "✅ CI pipeline completed!"

# Quick check before commit
pre-commit:
	@echo "Running pre-commit checks..."
	make lint
	make test-fast
	@echo "✅ Ready to commit!"
