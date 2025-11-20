# SDK Examples Test Suite

This directory contains comprehensive tests for all OpenMetadata SDK examples.

## Overview

The test suite validates:
- ✅ All imports work correctly
- ✅ All pydantic models can be instantiated
- ✅ All example functions execute without errors
- ✅ SDK dependencies are available
- ✅ No syntax or runtime errors

## Test Files

| File | Purpose | Tests |
|------|---------|-------|
| `conftest.py` | Pytest configuration and fixtures | Mock clients, common fixtures |
| `test_imports.py` | Validate all imports | Import checks for all example files and SDK modules |
| `test_models.py` | Test pydantic models | Model instantiation, validation, required fields |
| `test_examples.py` | Test example functions | Function execution with mocked clients |

## Running Tests

### Prerequisites

```bash
# Install test dependencies
pip install -r requirements-test.txt
```

### Run All Tests

```bash
# From sdk-examples directory
pytest tests/

# With verbose output
pytest tests/ -v

# With coverage report
pytest tests/ --cov=. --cov-report=term-missing
```

### Run Specific Tests

```bash
# Test only imports
pytest tests/test_imports.py -v

# Test only models
pytest tests/test_models.py -v

# Test only example functions
pytest tests/test_examples.py -v

# Test a specific function
pytest tests/test_imports.py::test_import_services -v
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

## Test Coverage

Current test coverage includes:

### Import Tests (test_imports.py)
- ✅ All 7 example files can be imported
- ✅ All SDK modules are available
- ✅ No missing dependencies
- ✅ No circular imports

### Model Tests (test_models.py)
- ✅ Service models (DatabaseService, PipelineService, etc.)
- ✅ Entity models (Database, Schema, Table, etc.)
- ✅ Type models (TagLabel, EntityReference, Markdown)
- ✅ Lineage models (AddLineageRequest, EntitiesEdge)
- ✅ Model validation and error handling

### Example Function Tests (test_examples.py)
- ✅ All example functions from services.py
- ✅ All example functions from entities.py
- ✅ All example functions from metadata_ops.py
- ✅ All example functions from lineage.py
- ✅ All example functions from queries.py
- ✅ All example functions from advanced.py

## CI/CD Integration

Tests run automatically on:
- **Pull Requests** that modify `sdk-examples/**`
- **Pushes** to main or claude branches

### GitHub Actions Workflow

Location: `.github/workflows/test-sdk-examples.yml`

The workflow:
1. **Tests** - Runs on Python 3.8, 3.9, 3.10, 3.11
2. **Lint** - Checks formatting with black, isort, ruff
3. **Validate** - Verifies syntax and imports

### Viewing Test Results

- Check the "Actions" tab in GitHub
- Look for "Test SDK Examples" workflow
- View detailed test output and coverage reports

## Writing New Tests

When adding new examples, add corresponding tests:

### 1. Add Import Test

```python
# In test_imports.py
def test_import_new_example():
    """Test that new_example.py can be imported."""
    try:
        import new_example
        assert hasattr(new_example, 'new_function')
    except ImportError as e:
        pytest.fail(f"Failed to import new_example.py: {e}")
```

### 2. Add Model Test (if new models used)

```python
# In test_models.py
def test_new_model():
    """Test new pydantic model."""
    model = NewModel(
        required_field="value",
        optional_field=123
    )
    assert model.required_field == "value"
```

### 3. Add Example Function Test

```python
# In test_examples.py
@patch('new_example.get_metadata_client')
def test_new_function(mock_get_client, mock_metadata_client):
    """Test new example function."""
    mock_get_client.return_value = mock_metadata_client

    import new_example
    result = new_example.new_function()

    assert result is not None
    mock_metadata_client.some_method.assert_called_once()
```

## Troubleshooting

### Import Errors

If you see import errors:
```bash
# Ensure you're in the sdk-examples directory
cd sdk-examples

# Install dependencies
pip install -r requirements-test.txt

# Run tests
pytest tests/
```

### Mock Issues

If mocks aren't working:
- Check that the patch path matches the import path in the example file
- Verify the mock client is configured in `conftest.py`
- Use `pytest -vv` for more detailed output

### Coverage Issues

To see which lines aren't covered:
```bash
pytest tests/ --cov=. --cov-report=html
open htmlcov/index.html
```

## Best Practices

1. **Mock External Dependencies**: Always mock `get_metadata_client()` to avoid network calls
2. **Test Happy Path**: Focus on validating examples work correctly
3. **Use Fixtures**: Leverage `conftest.py` fixtures for common setup
4. **Keep Tests Fast**: Tests should complete in < 10 seconds
5. **Clear Assertions**: Use descriptive assertion messages

## Continuous Improvement

This test suite ensures:
- ✅ All examples remain working as SDK evolves
- ✅ Changes to examples are validated
- ✅ Pydantic model changes are caught early
- ✅ Import errors are detected before users see them
- ✅ Code quality is maintained

## Questions?

- Check example files for inline documentation
- Review `conftest.py` for available fixtures
- See `.github/workflows/test-sdk-examples.yml` for CI config
- Consult pytest documentation: https://docs.pytest.org/
