.PHONY: help install test lint format type-check clean all pre-commit

help:  ## Show this help message
	@echo 'Usage: make [target]'
	@echo ''
	@echo 'Available targets:'
	@awk 'BEGIN {FS = ":.*?## "} /^[a-zA-Z_-]+:.*?## / {printf "  %-20s %s\n", $$1, $$2}' $(MAKEFILE_LIST)

install:  ## Install all dependencies
	pip install --upgrade pip setuptools wheel
	pip install --prefer-binary -r requirements-test.txt

test:  ## Run tests with pytest
	pytest tests/ -v -s

test-cov:  ## Run tests with coverage
	pytest tests/ -v --cov=. --cov-report=term-missing --cov-report=html --cov-report=xml

lint:  ## Run all linters
	@echo "Running ruff..."
	ruff check *.py tests/*.py
	@echo "\nRunning black check..."
	black --check *.py tests/*.py
	@echo "\nRunning isort check..."
	isort --check-only *.py tests/*.py

format:  ## Format code with black and isort
	@echo "Formatting with black..."
	black *.py tests/*.py
	@echo "\nSorting imports with isort..."
	isort *.py tests/*.py
	@echo "\nFixing with ruff..."
	ruff check --fix *.py tests/*.py

type-check:  ## Run type checking with mypy
	mypy *.py --ignore-missing-imports

clean:  ## Clean up generated files
	find . -type d -name "__pycache__" -exec rm -rf {} + 2>/dev/null || true
	find . -type f -name "*.pyc" -delete
	find . -type d -name "*.egg-info" -exec rm -rf {} + 2>/dev/null || true
	find . -type d -name ".pytest_cache" -exec rm -rf {} + 2>/dev/null || true
	find . -type d -name ".mypy_cache" -exec rm -rf {} + 2>/dev/null || true
	find . -type d -name ".ruff_cache" -exec rm -rf {} + 2>/dev/null || true
	rm -f .coverage
	rm -rf htmlcov/
	rm -f coverage.xml

pre-commit:  ## Install pre-commit hooks
	pre-commit install
	pre-commit run --all-files

all: format lint type-check test  ## Run format, lint, type-check, and test

check: lint type-check test  ## Run all checks without formatting

ci: lint type-check test-cov  ## Run CI pipeline (lint, type-check, test with coverage)
