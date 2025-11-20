"""
Test Suite Configuration - SDK Examples

This file configures pytest and provides shared fixtures for all tests.
"""

import pytest
from unittest.mock import Mock, MagicMock, patch
import sys
from pathlib import Path

# Add sdk-examples to path so we can import the example files
SDK_EXAMPLES_DIR = Path(__file__).parent.parent
sys.path.insert(0, str(SDK_EXAMPLES_DIR))


@pytest.fixture
def mock_metadata_client():
    """
    Mock OpenMetadata client for testing without a real server.

    This fixture provides a mock client with all common methods.
    """
    mock_client = MagicMock()

    # Mock health_check
    mock_client.health_check.return_value = None

    # Mock create_or_update (returns the input data)
    def mock_create_or_update(data):
        # Add mock ID and FQN
        mock_entity = MagicMock()
        mock_entity.id = Mock()
        mock_entity.id.__root__ = "mock-uuid-1234"
        mock_entity.name = Mock()
        mock_entity.name.__root__ = getattr(data, 'name', 'mock-name')
        mock_entity.fullyQualifiedName = Mock()
        mock_entity.fullyQualifiedName.__root__ = f"mock.fqn.{getattr(data, 'name', 'entity')}"
        return mock_entity

    mock_client.create_or_update.side_effect = mock_create_or_update

    # Mock get_by_name
    def mock_get_by_name(entity, fqn, fields=None):
        mock_entity = MagicMock()
        mock_entity.id = Mock()
        mock_entity.id.__root__ = "mock-uuid-1234"
        mock_entity.name = Mock()
        mock_entity.name.__root__ = fqn.split('.')[-1]
        mock_entity.fullyQualifiedName = Mock()
        mock_entity.fullyQualifiedName.__root__ = fqn
        mock_entity.columns = Mock()
        mock_entity.columns.__root__ = []
        mock_entity.owners = Mock()
        mock_entity.owners.__root__ = []
        mock_entity.tags = []
        return mock_entity

    mock_client.get_by_name.side_effect = mock_get_by_name

    # Mock get_by_id
    mock_client.get_by_id.side_effect = mock_get_by_name

    # Mock list_all_entities (returns empty generator)
    mock_client.list_all_entities.return_value = iter([])

    # Mock list_entities
    mock_list_result = MagicMock()
    mock_list_result.entities = []
    mock_client.list_entities.return_value = mock_list_result

    # Mock patch operations
    mock_client.patch.return_value = None
    mock_client.patch_tags.return_value = None
    mock_client.patch_column_tags.return_value = None
    mock_client.patch_domain.return_value = None

    # Mock add_lineage
    mock_client.add_lineage.return_value = MagicMock()

    return mock_client


@pytest.fixture
def mock_connection():
    """
    Mock the OpenMetadata connection setup.

    This prevents actual network calls during testing.
    """
    with patch('metadata.ingestion.ometa.ometa_api.OpenMetadata') as mock_om:
        mock_om.return_value = MagicMock()
        yield mock_om


@pytest.fixture
def valid_jwt_token():
    """Provide a valid-looking JWT token for testing."""
    return "eyJraWQiOiJHYjM4OWEtOWY3Ni1nZGpzLWE5MmotMDI0MmJrOTQzNTYiLCJhbGciOiJSUzI1NiIsInR5cCI6IkpXVCJ9.test.token"


@pytest.fixture
def valid_server_url():
    """Provide a valid server URL for testing."""
    return "http://localhost:8585/api"
