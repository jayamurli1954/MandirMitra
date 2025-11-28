.PHONY: test test-fast test-coverage test-unit test-integration test-slow test-watch test-debug clean-test

# Run all tests with parallel execution
test:
	pytest

# Run tests without coverage for faster execution
test-fast:
	pytest -n auto --no-cov -v

# Run tests with coverage report
test-coverage:
	pytest --cov=app --cov-report=html --cov-report=term

# Run only unit tests
test-unit:
	pytest -m unit -v

# Run only integration tests
test-integration:
	pytest -m integration -v

# Run only panchang tests
test-panchang:
	pytest -m panchang -v

# Run slow tests
test-slow:
	pytest -m slow -v

# Run tests excluding slow tests
test-no-slow:
	pytest -m "not slow" -v

# Watch mode - rerun tests on file changes
test-watch:
	pytest-watch

# Debug mode - single process for debugging
test-debug:
	pytest -n0 -vv --pdb

# Run specific test file
test-file:
	pytest $(FILE) -v

# Clean test artifacts
clean-test:
	rm -rf .pytest_cache
	rm -rf htmlcov
	rm -rf .coverage
	rm -rf coverage.xml
	find . -type d -name __pycache__ -exec rm -rf {} +
	find . -type f -name "*.pyc" -delete

# Install test dependencies
install-test:
	pip install -r requirements-test.txt

# Run code quality checks
quality:
	black --check .
	isort --check-only .
	flake8 .
	mypy app

# Format code
format:
	black .
	isort .

# Security scan
security:
	bandit -r app -ll

# Full CI pipeline
ci: quality test-coverage security
	@echo "✅ All CI checks passed!"
