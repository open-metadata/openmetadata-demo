"""
Test Imports - Verify all SDK imports work correctly

This test file validates that:
1. All example files can be imported
2. All SDK dependencies are available
3. No missing modules or circular imports
"""

import pytest
import sys
from pathlib import Path

# Test that we can import all example files
def test_import_setup():
    """Test that setup.py can be imported."""
    try:
        import setup
        assert hasattr(setup, 'get_metadata_client')
        assert hasattr(setup, 'health_check')
    except ImportError as e:
        pytest.fail(f"Failed to import setup.py: {e}")


def test_import_services():
    """Test that services.py can be imported."""
    try:
        import services
        assert hasattr(services, 'create_database_service_snowflake')
        assert hasattr(services, 'create_storage_service_s3')
        assert hasattr(services, 'create_pipeline_service_airflow')
        assert hasattr(services, 'create_messaging_service_kafka')
    except ImportError as e:
        pytest.fail(f"Failed to import services.py: {e}")


def test_import_entities():
    """Test that entities.py can be imported."""
    try:
        import entities
        assert hasattr(entities, 'create_database_schema_table_hierarchy')
        assert hasattr(entities, 'create_tables_for_lineage')
        assert hasattr(entities, 'create_pipeline_with_tasks')
        assert hasattr(entities, 'create_kafka_topic_with_schema')
        assert hasattr(entities, 'create_storage_containers')
        assert hasattr(entities, 'create_api_collection_and_endpoint')
    except ImportError as e:
        pytest.fail(f"Failed to import entities.py: {e}")


def test_import_metadata_ops():
    """Test that metadata_ops.py can be imported."""
    try:
        import metadata_ops
        assert hasattr(metadata_ops, 'add_table_level_tags')
        assert hasattr(metadata_ops, 'add_column_level_tags')
        assert hasattr(metadata_ops, 'update_table_description')
        assert hasattr(metadata_ops, 'update_table_owners')
        assert hasattr(metadata_ops, 'assign_domain_to_table')
        assert hasattr(metadata_ops, 'list_glossaries_and_terms')
        assert hasattr(metadata_ops, 'grouped_patch_operations')
    except ImportError as e:
        pytest.fail(f"Failed to import metadata_ops.py: {e}")


def test_import_lineage():
    """Test that lineage.py can be imported."""
    try:
        import lineage
        assert hasattr(lineage, 'create_table_pipeline_table_lineage')
        assert hasattr(lineage, 'create_table_to_table_lineage')
        assert hasattr(lineage, 'create_multi_source_lineage')
        assert hasattr(lineage, 'create_fanout_lineage')
        assert hasattr(lineage, 'query_entity_lineage')
    except ImportError as e:
        pytest.fail(f"Failed to import lineage.py: {e}")


def test_import_queries():
    """Test that queries.py can be imported."""
    try:
        import queries
        assert hasattr(queries, 'get_entity_by_name')
        assert hasattr(queries, 'get_entity_by_id')
        assert hasattr(queries, 'list_all_entities')
        assert hasattr(queries, 'list_entities_with_filters')
        assert hasattr(queries, 'health_check')
        assert hasattr(queries, 'query_patterns_and_best_practices')
    except ImportError as e:
        pytest.fail(f"Failed to import queries.py: {e}")


def test_import_advanced():
    """Test that advanced.py can be imported."""
    try:
        import advanced
        assert hasattr(advanced, 'bulk_create_tables')
        assert hasattr(advanced, 'bulk_update_with_retry')
        assert hasattr(advanced, 'migrate_users_between_teams')
        assert hasattr(advanced, 'error_handling_patterns')
        assert hasattr(advanced, 'production_best_practices')
    except ImportError as e:
        pytest.fail(f"Failed to import advanced.py: {e}")


# Test critical SDK imports
def test_sdk_ometa_import():
    """Test that OpenMetadata client can be imported."""
    try:
        from metadata.ingestion.ometa.ometa_api import OpenMetadata
        assert OpenMetadata is not None
    except ImportError as e:
        pytest.fail(f"Failed to import OpenMetadata client: {e}")


def test_sdk_connection_imports():
    """Test that connection classes can be imported."""
    try:
        from metadata.generated.schema.entity.services.connections.metadata.openMetadataConnection import (
            OpenMetadataConnection,
            AuthProvider,
        )
        from metadata.generated.schema.security.client.openMetadataJWTClientConfig import (
            OpenMetadataJWTClientConfig,
        )
        assert OpenMetadataConnection is not None
        assert AuthProvider is not None
        assert OpenMetadataJWTClientConfig is not None
    except ImportError as e:
        pytest.fail(f"Failed to import connection classes: {e}")


def test_sdk_service_imports():
    """Test that service creation classes can be imported."""
    try:
        from metadata.generated.schema.api.services.createDatabaseService import CreateDatabaseServiceRequest
        from metadata.generated.schema.api.services.createPipelineService import CreatePipelineServiceRequest
        from metadata.generated.schema.api.services.createMessagingService import CreateMessagingServiceRequest
        from metadata.generated.schema.api.services.createStorageService import CreateStorageServiceRequest

        assert CreateDatabaseServiceRequest is not None
        assert CreatePipelineServiceRequest is not None
        assert CreateMessagingServiceRequest is not None
        assert CreateStorageServiceRequest is not None
    except ImportError as e:
        pytest.fail(f"Failed to import service creation classes: {e}")


def test_sdk_entity_imports():
    """Test that entity creation classes can be imported."""
    try:
        from metadata.generated.schema.api.data.createDatabase import CreateDatabaseRequest
        from metadata.generated.schema.api.data.createDatabaseSchema import CreateDatabaseSchemaRequest
        from metadata.generated.schema.api.data.createTable import CreateTableRequest
        from metadata.generated.schema.api.data.createPipeline import CreatePipelineRequest
        from metadata.generated.schema.api.data.createTopic import CreateTopicRequest
        from metadata.generated.schema.api.data.createContainer import CreateContainerRequest

        assert CreateDatabaseRequest is not None
        assert CreateDatabaseSchemaRequest is not None
        assert CreateTableRequest is not None
        assert CreatePipelineRequest is not None
        assert CreateTopicRequest is not None
        assert CreateContainerRequest is not None
    except ImportError as e:
        pytest.fail(f"Failed to import entity creation classes: {e}")


def test_sdk_type_imports():
    """Test that type classes can be imported."""
    try:
        from metadata.generated.schema.entity.data.table import Table, Column, DataType
        from metadata.generated.schema.type.tagLabel import TagLabel, TagSource, LabelType, State, TagFQN
        from metadata.generated.schema.type.entityReference import EntityReference
        from metadata.generated.schema.type.basic import Markdown

        assert Table is not None
        assert Column is not None
        assert DataType is not None
        assert TagLabel is not None
        assert EntityReference is not None
        assert Markdown is not None
    except ImportError as e:
        pytest.fail(f"Failed to import type classes: {e}")


def test_sdk_lineage_imports():
    """Test that lineage classes can be imported."""
    try:
        from metadata.generated.schema.api.lineage.addLineage import AddLineageRequest
        from metadata.generated.schema.type.entityLineage import EntitiesEdge

        assert AddLineageRequest is not None
        assert EntitiesEdge is not None
    except ImportError as e:
        pytest.fail(f"Failed to import lineage classes: {e}")
