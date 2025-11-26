"""
Sanity Test - Verify basic pytest functionality

This is a minimal test to verify pytest is working correctly.
"""

import pytest


def test_pytest_works():
    """Test that pytest is running."""
    assert True


def test_python_imports():
    """Test that Python can import basic modules."""
    import json
    import sys
    assert json is not None
    assert sys is not None


def test_sdk_import():
    """Test that we can import the SDK."""
    try:
        from metadata.ingestion.ometa.ometa_api import OpenMetadata
        assert OpenMetadata is not None
    except ImportError as e:
        pytest.fail(f"Failed to import SDK: {e}")
