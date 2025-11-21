"""
Test Example Functions - Verify all example functions work correctly

This test file validates that:
1. Example functions can be called without errors
2. Functions handle mocked responses correctly
3. No runtime errors in example code
"""

import pytest
from unittest.mock import patch, MagicMock


class TestServicesExamples:
    """Test examples from services.py."""

    @patch('services.get_metadata_client')
    def test_create_database_service_snowflake(self, mock_get_client, mock_metadata_client):
        """Test Snowflake database service creation."""
        mock_get_client.return_value = mock_metadata_client

        import services
        result = services.create_database_service_snowflake()

        assert result is not None
        mock_metadata_client.create_or_update.assert_called_once()

    @patch('services.get_metadata_client')
    def test_create_storage_service_s3(self, mock_get_client, mock_metadata_client):
        """Test S3 storage service creation."""
        mock_get_client.return_value = mock_metadata_client

        import services
        result = services.create_storage_service_s3()

        assert result is not None
        mock_metadata_client.create_or_update.assert_called_once()

    @patch('services.get_metadata_client')
    def test_create_pipeline_service_airflow(self, mock_get_client, mock_metadata_client):
        """Test Airflow pipeline service creation."""
        mock_get_client.return_value = mock_metadata_client

        import services
        result = services.create_pipeline_service_airflow()

        assert result is not None
        mock_metadata_client.create_or_update.assert_called_once()

    @patch('services.get_metadata_client')
    def test_create_messaging_service_kafka(self, mock_get_client, mock_metadata_client):
        """Test Kafka messaging service creation."""
        mock_get_client.return_value = mock_metadata_client

        import services
        result = services.create_messaging_service_kafka()

        assert result is not None
        mock_metadata_client.create_or_update.assert_called_once()


class TestEntitiesExamples:
    """Test examples from entities.py."""

    @patch('entities.get_metadata_client')
    def test_create_database_schema_table_hierarchy(self, mock_get_client, mock_metadata_client):
        """Test database/schema/table hierarchy creation."""
        mock_get_client.return_value = mock_metadata_client

        import entities
        db, schema, table = entities.create_database_schema_table_hierarchy()

        assert db is not None
        assert schema is not None
        assert table is not None
        assert mock_metadata_client.create_or_update.call_count == 3

    @patch('entities.get_metadata_client')
    def test_create_tables_for_lineage(self, mock_get_client, mock_metadata_client):
        """Test lineage table creation."""
        mock_get_client.return_value = mock_metadata_client

        import entities
        table_a, table_b = entities.create_tables_for_lineage()

        assert table_a is not None
        assert table_b is not None
        assert mock_metadata_client.create_or_update.call_count == 2

    @patch('entities.get_metadata_client')
    def test_create_pipeline_with_tasks(self, mock_get_client, mock_metadata_client):
        """Test pipeline creation with tasks."""
        mock_get_client.return_value = mock_metadata_client

        import entities
        pipeline = entities.create_pipeline_with_tasks()

        assert pipeline is not None
        mock_metadata_client.create_or_update.assert_called_once()


class TestMetadataOpsExamples:
    """Test examples from metadata_ops.py."""

    @patch('metadata_ops.get_metadata_client')
    def test_add_table_level_tags(self, mock_get_client, mock_metadata_client):
        """Test adding table-level tags."""
        mock_get_client.return_value = mock_metadata_client

        import metadata_ops
        result = metadata_ops.add_table_level_tags()

        assert result is not None
        mock_metadata_client.get_by_name.assert_called()
        mock_metadata_client.patch_tags.assert_called_once()

    @patch('metadata_ops.get_metadata_client')
    def test_add_column_level_tags(self, mock_get_client, mock_metadata_client):
        """Test adding column-level tags."""
        mock_get_client.return_value = mock_metadata_client

        import metadata_ops
        result = metadata_ops.add_column_level_tags()

        assert result is not None
        mock_metadata_client.get_by_name.assert_called()
        mock_metadata_client.patch_column_tags.assert_called()

    @patch('metadata_ops.get_metadata_client')
    def test_update_table_description(self, mock_get_client, mock_metadata_client):
        """Test updating table description."""
        mock_get_client.return_value = mock_metadata_client

        import metadata_ops
        result = metadata_ops.update_table_description()

        assert result is not None
        mock_metadata_client.get_by_name.assert_called()
        mock_metadata_client.patch.assert_called_once()


class TestLineageExamples:
    """Test examples from lineage.py."""

    @patch('lineage.get_metadata_client')
    def test_create_table_pipeline_table_lineage(self, mock_get_client, mock_metadata_client):
        """Test table-pipeline-table lineage creation."""
        mock_get_client.return_value = mock_metadata_client

        import lineage
        lineage1, lineage2 = lineage.create_table_pipeline_table_lineage()

        assert lineage1 is not None
        assert lineage2 is not None
        assert mock_metadata_client.add_lineage.call_count == 2

    @patch('lineage.get_metadata_client')
    def test_create_table_to_table_lineage(self, mock_get_client, mock_metadata_client):
        """Test direct table-to-table lineage."""
        mock_get_client.return_value = mock_metadata_client

        import lineage
        result = lineage.create_table_to_table_lineage()

        assert result is not None
        mock_metadata_client.add_lineage.assert_called_once()


class TestQueriesExamples:
    """Test examples from queries.py."""

    @patch('queries.get_metadata_client')
    def test_get_entity_by_name(self, mock_get_client, mock_metadata_client):
        """Test getting entity by name."""
        mock_get_client.return_value = mock_metadata_client

        import queries
        result = queries.get_entity_by_name()

        assert result is not None
        mock_metadata_client.get_by_name.assert_called()

    @patch('queries.get_metadata_client')
    def test_get_entity_by_id(self, mock_get_client, mock_metadata_client):
        """Test getting entity by ID."""
        mock_get_client.return_value = mock_metadata_client

        import queries
        result = queries.get_entity_by_id()

        assert result is not None
        mock_metadata_client.get_by_id.assert_called()

    @patch('queries.get_metadata_client')
    def test_health_check(self, mock_get_client, mock_metadata_client):
        """Test health check."""
        mock_get_client.return_value = mock_metadata_client

        import queries
        result = queries.health_check()

        assert result is True
        mock_metadata_client.health_check.assert_called_once()


class TestAdvancedExamples:
    """Test examples from advanced.py."""

    @patch('advanced.get_metadata_client')
    def test_bulk_create_tables(self, mock_get_client, mock_metadata_client):
        """Test bulk table creation."""
        mock_get_client.return_value = mock_metadata_client

        import advanced
        stats = advanced.bulk_create_tables()

        assert stats is not None
        assert 'created' in stats
        assert 'failed' in stats
        assert stats['created'] + stats['failed'] == 3  # 3 tables defined

    @patch('advanced.get_metadata_client')
    def test_error_handling_patterns(self, mock_get_client, mock_metadata_client):
        """Test error handling patterns."""
        mock_get_client.return_value = mock_metadata_client

        import advanced
        results = advanced.error_handling_patterns()

        assert results is not None
        assert 'successes' in results
        assert 'failures' in results
        assert 'success_rate' in results
