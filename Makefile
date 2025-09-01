# Makefile for AI WellnessVision Testing

.PHONY: help test test-unit test-integration test-performance test-multilingual test-accessibility test-security test-all test-coverage test-report clean install-test-deps

# Default target
help:
	@echo "AI WellnessVision Test Suite"
	@echo "============================"
	@echo ""
	@echo "Available targets:"
	@echo "  help                 - Show this help message"
	@echo "  install-test-deps    - Install testing dependencies"
	@echo "  test                 - Run all tests"
	@echo "  test-unit           - Run unit tests only"
	@echo "  test-integration    - Run integration tests only"
	@echo "  test-performance    - Run performance tests only"
	@echo "  test-multilingual   - Run multilingual tests only"
	@echo "  test-accessibility  - Run accessibility tests only"
	@echo "  test-security       - Run security tests only"
	@echo "  test-services       - Run AI services tests only"
	@echo "  test-api            - Run API tests only"
	@echo "  test-ui             - Run UI tests only"
	@echo "  test-coverage       - Run tests with coverage report"
	@echo "  test-report         - Generate comprehensive test report"
	@echo "  test-fast           - Run fast tests only (exclude slow tests)"
	@echo "  test-parallel       - Run tests in parallel"
	@echo "  clean               - Clean test artifacts"
	@echo ""

# Install testing dependencies
install-test-deps:
	@echo "Installing testing dependencies..."
	pip install pytest pytest-asyncio pytest-cov pytest-mock pytest-xdist pytest-html pytest-benchmark coverage locust selenium

# Run all tests
test:
	@echo "Running all tests..."
	python -m pytest tests/ -v

# Run unit tests only
test-unit:
	@echo "Running unit tests..."
	python -m pytest tests/ -m "unit" -v

# Run integration tests only
test-integration:
	@echo "Running integration tests..."
	python -m pytest tests/ -m "integration" -v

# Run performance tests only
test-performance:
	@echo "Running performance tests..."
	python -m pytest tests/ -m "performance" -v --durations=0

# Run multilingual tests only
test-multilingual:
	@echo "Running multilingual tests..."
	python -m pytest tests/ -m "multilingual" -v

# Run accessibility tests only
test-accessibility:
	@echo "Running accessibility tests..."
	python -m pytest tests/ -m "accessibility" -v

# Run security tests only
test-security:
	@echo "Running security tests..."
	python -m pytest tests/ -m "security" -v

# Run AI services tests only
test-services:
	@echo "Running AI services tests..."
	python -m pytest tests/ -m "services" -v

# Run API tests only
test-api:
	@echo "Running API tests..."
	python -m pytest tests/ -m "api" -v

# Run UI tests only
test-ui:
	@echo "Running UI tests..."
	python -m pytest tests/ -m "ui" -v

# Run tests with coverage
test-coverage:
	@echo "Running tests with coverage..."
	python -m pytest tests/ --cov=src --cov-report=html --cov-report=term-missing --cov-report=xml --cov-fail-under=80 -v

# Generate comprehensive test report
test-report:
	@echo "Generating comprehensive test report..."
	python tests/test_runner.py
	@echo "Test report generated!"

# Run fast tests only (exclude slow tests)
test-fast:
	@echo "Running fast tests..."
	python -m pytest tests/ -m "not slow" -v

# Run tests in parallel
test-parallel:
	@echo "Running tests in parallel..."
	python -m pytest tests/ -n auto -v

# Run specific test categories
test-categories:
	@echo "Running specific test categories..."
	python tests/test_runner.py --categories unit integration performance

# Run tests with benchmark
test-benchmark:
	@echo "Running tests with benchmarking..."
	python -m pytest tests/ --benchmark-only -v

# Run tests with HTML report
test-html:
	@echo "Running tests with HTML report..."
	python -m pytest tests/ --html=reports/test_report.html --self-contained-html -v

# Lint and format code before testing
lint:
	@echo "Linting code..."
	python -m flake8 src/ tests/ --max-line-length=120 --ignore=E203,W503
	python -m black src/ tests/ --check
	python -m isort src/ tests/ --check-only

# Format code
format:
	@echo "Formatting code..."
	python -m black src/ tests/
	python -m isort src/ tests/

# Type checking
typecheck:
	@echo "Running type checks..."
	python -m mypy src/ --ignore-missing-imports

# Security scanning
security-scan:
	@echo "Running security scan..."
	python -m bandit -r src/ -f json -o reports/security_report.json
	python -m safety check --json --output reports/safety_report.json

# Clean test artifacts
clean:
	@echo "Cleaning test artifacts..."
	rm -rf htmlcov/
	rm -rf reports/
	rm -rf .pytest_cache/
	rm -rf .coverage
	rm -f coverage.xml
	rm -f test_report.json
	find . -type d -name "__pycache__" -exec rm -rf {} +
	find . -type f -name "*.pyc" -delete
	find . -type f -name "*.pyo" -delete

# Setup test environment
setup-test-env:
	@echo "Setting up test environment..."
	mkdir -p reports
	mkdir -p htmlcov
	mkdir -p logs

# Run smoke tests (quick validation)
smoke-test:
	@echo "Running smoke tests..."
	python -m pytest tests/test_models.py::TestBaseModel::test_base_model_creation -v
	python -m pytest tests/test_config.py::TestConfigManager::test_config_loading -v
	python -c "import src.config; print('✅ Basic imports working')"

# Run tests with different Python versions (if available)
test-python-versions:
	@echo "Testing with different Python versions..."
	python3.8 -m pytest tests/ -v || echo "Python 3.8 not available"
	python3.9 -m pytest tests/ -v || echo "Python 3.9 not available"
	python3.10 -m pytest tests/ -v || echo "Python 3.10 not available"
	python3.11 -m pytest tests/ -v || echo "Python 3.11 not available"

# Load testing with Locust
load-test:
	@echo "Running load tests..."
	locust -f tests/locustfile.py --headless -u 10 -r 2 -t 60s --host=http://localhost:8000

# Database tests (if applicable)
test-db:
	@echo "Running database tests..."
	python -m pytest tests/ -k "database" -v

# API endpoint tests
test-endpoints:
	@echo "Running API endpoint tests..."
	python -m pytest tests/test_api_gateway.py tests/test_integration_api.py -v

# Memory leak tests
test-memory:
	@echo "Running memory leak tests..."
	python -m pytest tests/test_performance.py::TestPerformanceMetrics::test_memory_usage_stability -v

# Stress tests
stress-test:
	@echo "Running stress tests..."
	python -m pytest tests/test_performance.py::TestLoadTesting -v --durations=0

# Continuous integration target
ci-test:
	@echo "Running CI tests..."
	python -m pytest tests/ --cov=src --cov-report=xml --cov-fail-under=75 -v --tb=short

# Development test target (fast feedback)
dev-test:
	@echo "Running development tests..."
	python -m pytest tests/ -x -v --tb=short

# Watch mode for development
test-watch:
	@echo "Running tests in watch mode..."
	python -m pytest-watch tests/ -- -v

# Generate test data
generate-test-data:
	@echo "Generating test data..."
	python -c "from tests.conftest import *; print('Test data generation complete')"

# Validate test configuration
validate-tests:
	@echo "Validating test configuration..."
	python -m pytest --collect-only tests/
	@echo "Test configuration is valid!"

# All quality checks
quality-check: lint typecheck security-scan test-coverage
	@echo "All quality checks completed!"

# Full test suite (everything)
test-all: clean setup-test-env quality-check test-coverage test-report
	@echo "Full test suite completed!"

# Quick test (for development)
quick-test:
	@echo "Running quick tests..."
	python -m pytest tests/test_models.py tests/test_config.py -v

# Integration with external services
test-external:
	@echo "Running external service tests..."
	python -m pytest tests/ -m "external" -v

# Test specific file
test-file:
	@echo "Usage: make test-file FILE=tests/test_models.py"
	python -m pytest $(FILE) -v

# Test with specific marker
test-marker:
	@echo "Usage: make test-marker MARKER=unit"
	python -m pytest tests/ -m "$(MARKER)" -v