# Developer Guide

This guide explains how to set up your development environment and contribute to the OpenMetadata SDK Examples project.

## Table of Contents

- [Prerequisites](#prerequisites)
- [Development Setup](#development-setup)
- [Running Tests](#running-tests)
- [Code Standards](#code-standards)
- [Contributing Workflow](#contributing-workflow)
- [Project Structure](#project-structure)
- [Troubleshooting](#troubleshooting)

## Prerequisites

### Required Software

- **Python 3.10** (required for development and CI/CD)
- **Git** for version control
- **pip** for package management

### Check Your Setup

```bash
# Verify Python version
python3.10 --version
# Should output: Python 3.10.x

# Verify Git
git --version

# Verify pip
python3.10 -m pip --version
```

## Development Setup

### 1. Clone the Repository

```bash
git clone https://github.com/open-metadata/openmetadata-demo.git
cd openmetadata-demo
```

### 2. Set Up Python Environment

We recommend using a virtual environment for development:

```bash
# Create virtual environment with Python 3.10
python3.10 -m venv venv

# Activate virtual environment
# On Linux/macOS:
source venv/bin/activate
# On Windows:
venv\Scripts\activate

# Verify you're using the correct Python
which python  # Should show path to venv/bin/python
python --version  # Should show Python 3.10.x
```

### 3. Install Dependencies

```bash
# Navigate to sdk-examples directory
cd sdk-examples

# Install test dependencies
pip install -r requirements-test.txt

# This installs:
# - pytest (testing framework)
# - pytest-cov (coverage reporting)
# - pytest-mock (mocking utilities)
# - openmetadata-ingestion (SDK)
```

### 4. Verify Installation

```bash
# Run a quick test to verify setup
pytest tests/test_imports.py -v

# You should see all import tests passing
```

## Running Tests

### Run All Tests

```bash
# From sdk-examples directory
pytest tests/ -v
```

### Run Specific Test Files

```bash
# Test only imports
pytest tests/test_imports.py -v

# Test only models
pytest tests/test_models.py -v

# Test only example functions
pytest tests/test_examples.py -v
```

### Run Tests by Marker

```bash
# Run only import tests
pytest tests/ -m imports -v

# Run only model tests
pytest tests/ -m models -v

# Run only example tests
pytest tests/ -m examples -v
```

### Run with Coverage Report

```bash
# Run all tests with coverage
pytest tests/ -v --cov=. --cov-report=term-missing

# Generate HTML coverage report
pytest tests/ --cov=. --cov-report=html
open htmlcov/index.html  # View in browser
```

### Run Specific Test Functions

```bash
# Run a single test function
pytest tests/test_imports.py::test_import_services -v

# Run multiple specific tests
pytest tests/test_models.py::test_database_service -v
```

## Code Standards

### Python Style Guide

We follow **PEP 8** style guidelines with modern tooling:

- **Indentation**: 4 spaces (no tabs)
- **Line Length**: Maximum 100 characters (configured in `pyproject.toml`)
- **Imports**: Organized with `isort` (black-compatible profile)
- **Linting**: Checked with `ruff` (replaces flake8, pylint, etc.)
- **Type Hints**: Checked with `mypy` (informational, not required)
- **Formatting**: Auto-formatted with `black`

### Quick Start

Use the Makefile for common tasks:

```bash
# Install all development dependencies
cd sdk-examples
make install

# Format code automatically
make format

# Check code quality (lint + type-check)
make lint
make type-check

# Run all checks
make check

# Run tests
make test
make test-cov  # with coverage

# Run everything (format + lint + type-check + test)
make all
```

### Formatting Tools

All configuration is in `pyproject.toml`. Tools automatically detect and use this configuration.

```bash
# Auto-format code with Black
black *.py tests/*.py

# Sort imports with isort
isort *.py tests/*.py

# Lint with ruff (fast linter)
ruff check *.py tests/*.py
ruff check --fix *.py tests/*.py  # auto-fix issues

# Type check with mypy
mypy *.py --ignore-missing-imports
```

### Pre-commit Hooks

Install pre-commit hooks to automatically check code before commits:

```bash
cd sdk-examples
make pre-commit
# or
pre-commit install
```

This will run on every commit:
- **black**: Code formatting
- **isort**: Import sorting
- **ruff**: Linting with auto-fix
- **mypy**: Type checking
- **trailing-whitespace**: Remove trailing whitespace
- **end-of-file-fixer**: Ensure files end with newline
- **check-yaml/json/toml**: Validate config files
- **detect-private-key**: Prevent committing secrets

### Environment Variables

Use `.env` files for configuration (never commit these!):

1. **Copy template**:
   ```bash
   cp .env.example .env
   ```

2. **Update with your values**:
   ```bash
   OPENMETADATA_SERVER_URL=http://localhost:8585/api
   OPENMETADATA_JWT_TOKEN=your-actual-token
   ```

3. **Load in Python**:
   ```python
   import os
   from dotenv import load_dotenv

   load_dotenv()
   SERVER_URL = os.getenv("OPENMETADATA_SERVER_URL")
   JWT_TOKEN = os.getenv("OPENMETADATA_JWT_TOKEN")
   ```

### Documentation Standards

Every example file must include:

1. **Module Docstring**: Explain what the file demonstrates
2. **Function Docstrings**: Describe each example function
3. **Inline Comments**: Explain complex logic
4. **Source References**: Line numbers from original SDK code where APIs were found

Example:

```python
"""
Example: Creating Database Services

This file demonstrates how to create various database services using the
OpenMetadata Python SDK.

Source: ingestion/src/metadata/ingestion/api/parser.py:45-67
"""

def create_database_service_snowflake():
    """
    Create a Snowflake database service in OpenMetadata.

    This example shows how to:
    - Configure connection details for Snowflake
    - Set up authentication
    - Create the service using the SDK

    Source: metadata/generated/schema/entity/services/databaseService.py:124

    Returns:
        DatabaseService: The created database service object
    """
    # Implementation here
```

### Self-Contained Pattern

**IMPORTANT**: All example files must be self-contained for easy copy-paste usage.

- ✅ **DO**: Include connection setup inline in each file
- ✅ **DO**: Import all dependencies at the top of each file
- ✅ **DO**: Make examples runnable without modifications
- ❌ **DON'T**: Import from other example files
- ❌ **DON'T**: Require external configuration files

### Testing Requirements

When adding new examples:

1. **Add Import Test** in `tests/test_imports.py`
2. **Add Model Tests** in `tests/test_models.py` (if using new models)
3. **Add Function Tests** in `tests/test_examples.py`
4. **Ensure 100% Coverage**: All new code must be covered by tests

Example:

```python
# In tests/test_examples.py
@patch('your_example.get_metadata_client')
def test_your_new_function(mock_get_client, mock_metadata_client):
    """Test your new example function."""
    mock_get_client.return_value = mock_metadata_client

    import your_example
    result = your_example.your_new_function()

    assert result is not None
    mock_metadata_client.create_or_update.assert_called_once()
```

## Contributing Workflow

### 1. Create a Feature Branch

```bash
# Create branch from main
git checkout main
git pull origin main
git checkout -b feature/your-feature-name
```

### 2. Make Your Changes

```bash
# Make changes to files
# Add new examples or fix bugs

# Stage changes
git add .

# Commit with descriptive message
git commit -m "Add example for creating Glue database service"
```

### 3. Run Tests Locally

```bash
# ALWAYS run tests before pushing
cd sdk-examples
pytest tests/ -v --cov=. --cov-report=term-missing

# Ensure all tests pass
# Ensure coverage remains at 100%
```

### 4. Format and Lint Code

```bash
# Format code
black sdk-examples/*.py sdk-examples/tests/*.py
isort sdk-examples/*.py sdk-examples/tests/*.py

# Check for issues
ruff check sdk-examples/*.py sdk-examples/tests/*.py
```

### 5. Push Changes

```bash
# Push to your branch
git push origin feature/your-feature-name
```

### 6. Create Pull Request

1. Go to GitHub repository
2. Click "New Pull Request"
3. Select your branch
4. Fill in PR template:
   - **Description**: What does this PR do?
   - **Examples Added**: List new examples
   - **Tests**: Confirm all tests pass
   - **Coverage**: Confirm 100% coverage maintained
5. Request review from maintainers

### 7. Address Review Comments

```bash
# Make requested changes
# Commit and push again
git add .
git commit -m "Address review comments: update docstrings"
git push origin feature/your-feature-name
```

## Project Structure

```
openmetadata-demo/
├── sdk-examples/               # SDK example code
│   ├── README.md              # User-facing documentation
│   ├── setup.py               # Connection setup reference
│   ├── services.py            # Service creation examples
│   ├── entities.py            # Entity creation examples
│   ├── metadata_ops.py        # Metadata operations
│   ├── lineage.py             # Lineage examples
│   ├── queries.py             # Query and read operations
│   ├── advanced.py            # Advanced patterns
│   ├── tests/                 # Test suite
│   │   ├── conftest.py        # Pytest fixtures
│   │   ├── test_imports.py    # Import tests
│   │   ├── test_models.py     # Model tests
│   │   ├── test_examples.py   # Function tests
│   │   └── README.md          # Testing documentation
│   ├── pytest.ini             # Pytest configuration
│   ├── .coveragerc            # Coverage configuration
│   └── requirements-test.txt  # Test dependencies
├── .github/
│   └── workflows/
│       └── test-sdk-examples.yml  # CI/CD configuration
├── .gitignore                 # Git ignore rules
└── DEVELOPERS.md              # This file
```

## Continuous Integration

### GitHub Actions Workflow

Our CI/CD pipeline runs automatically on:

- **Pull Requests** that modify `sdk-examples/**`
- **Pushes** to `main` or `claude/**` branches

### CI Jobs

1. **Test** (Python 3.10 only)
   - Installs dependencies
   - Runs all tests
   - Generates coverage report
   - Uploads coverage to Codecov

2. **Lint**
   - Checks formatting with Black
   - Checks import sorting with isort
   - Lints with ruff

3. **Validate**
   - Validates Python syntax
   - Checks for proper docstrings
   - Verifies all imports can be resolved

### Viewing CI Results

1. Go to your PR on GitHub
2. Scroll to "Checks" section at the bottom
3. Click "Details" next to any failed check
4. Review logs and fix issues
5. Push fixes to re-trigger CI

## Troubleshooting

### Import Errors

**Problem**: `ModuleNotFoundError: No module named 'metadata'`

**Solution**:
```bash
# Ensure you're in the virtual environment
source venv/bin/activate

# Install dependencies
cd sdk-examples
pip install -r requirements-test.txt
```

### Test Failures

**Problem**: Tests fail with mocking errors

**Solution**:
```bash
# Check that mock paths match import paths
# In test_examples.py, ensure patch path matches:
@patch('your_file.get_metadata_client')  # Should match the file being tested

# Run with more verbose output
pytest tests/test_examples.py -vv
```

### Coverage Below 100%

**Problem**: Coverage report shows missing lines

**Solution**:
```bash
# Generate HTML coverage report to see what's missing
pytest tests/ --cov=. --cov-report=html
open htmlcov/index.html

# Add tests for uncovered lines
# Re-run tests to verify
pytest tests/ -v --cov=. --cov-report=term-missing
```

### Installation Issues

**Problem**: `openmetadata-ingestion` fails to install

**Solution**:
```bash
# Use prefer-binary flag
pip install --prefer-binary openmetadata-ingestion

# If that fails, try installing problematic packages separately
pip install --prefer-binary antlr4-python3-runtime dsnparse
pip install --prefer-binary openmetadata-ingestion
```

### Python Version Issues

**Problem**: Using wrong Python version

**Solution**:
```bash
# Always use Python 3.10 explicitly
python3.10 -m venv venv
source venv/bin/activate
python --version  # Should show 3.10.x

# In CI, only Python 3.10 is used
```

## Best Practices

### When Writing Examples

1. **Start Simple**: Begin with minimal working examples
2. **Add Complexity Gradually**: Build on simpler examples
3. **Include Error Handling**: Show best practices
4. **Document Everything**: Explain why, not just what
5. **Test Thoroughly**: Every example must have tests

### When Writing Tests

1. **Mock External Dependencies**: Never make real API calls
2. **Test Happy Path**: Focus on correct usage
3. **Keep Tests Fast**: All tests should complete in <10 seconds
4. **Use Descriptive Names**: Test names should explain what they verify
5. **Use Fixtures**: Leverage `conftest.py` for common setup

### When Reviewing PRs

1. **Check Tests**: Verify 100% coverage maintained
2. **Check Docs**: Ensure examples are well-documented
3. **Check Style**: Verify formatting and linting pass
4. **Check Self-Contained**: Ensure examples are copy-paste ready
5. **Check CI**: Ensure all CI checks pass

## Getting Help

### Documentation

- **SDK Examples README**: `sdk-examples/README.md`
- **Test Suite README**: `sdk-examples/tests/README.md`
- **OpenMetadata Docs**: https://docs.open-metadata.org/
- **Pytest Docs**: https://docs.pytest.org/

### Reporting Issues

If you encounter problems:

1. Check this guide first
2. Check existing GitHub issues
3. Create a new issue with:
   - Clear description of the problem
   - Steps to reproduce
   - Error messages
   - Python version
   - Operating system

### Contributing

We welcome contributions! Please:

- Follow the contributing workflow above
- Maintain 100% test coverage
- Write clear, documented code
- Be patient with code review

## License

This project follows the same license as the OpenMetadata project.

---

**Happy Coding!** 🚀

For questions or feedback, please open an issue on GitHub.
