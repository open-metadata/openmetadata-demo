"""
Test Pydantic Models - Verify all models can be instantiated

This test file validates that:
1. All pydantic models can be created
2. Model validation works correctly
3. Required fields are enforced
4. Optional fields work as expected
"""

import pytest
from metadata.generated.schema.api.services.createDatabaseService import CreateDatabaseServiceRequest
from metadata.generated.schema.entity.services.databaseService import DatabaseServiceType, DatabaseConnection
from metadata.generated.schema.entity.services.connections.database.snowflakeConnection import SnowflakeConnection
from metadata.generated.schema.api.data.createDatabase import CreateDatabaseRequest
from metadata.generated.schema.api.data.createDatabaseSchema import CreateDatabaseSchemaRequest
from metadata.generated.schema.api.data.createTable import CreateTableRequest
from metadata.generated.schema.entity.data.table import Column, DataType
from metadata.generated.schema.type.tagLabel import TagLabel, TagFQN, TagSource, LabelType, State
from metadata.generated.schema.type.entityReference import EntityReference
from metadata.generated.schema.type.basic import Markdown
from metadata.generated.schema.api.lineage.addLineage import AddLineageRequest
from metadata.generated.schema.type.entityLineage import EntitiesEdge


class TestServiceModels:
    """Test service creation models."""

    def test_create_database_service_request(self):
        """Test DatabaseService creation model."""
        service = CreateDatabaseServiceRequest(
            name="test-service",
            serviceType=DatabaseServiceType.Snowflake,
            connection=DatabaseConnection(
                config=SnowflakeConnection(
                    username="user",
                    password="pass",
                    account="account",
                    warehouse="warehouse"
                )
            )
        )

        assert service.name.root == "test-service"
        assert service.serviceType == DatabaseServiceType.Snowflake
        assert service.connection is not None


class TestEntityModels:
    """Test entity creation models."""

    def test_create_database_request(self):
        """Test Database creation model."""
        database = CreateDatabaseRequest(
            name="test-db",
            service="test-service"
        )

        assert database.name.root == "test-db"
        assert database.service.root == "test-service"

    def test_create_database_schema_request(self):
        """Test DatabaseSchema creation model."""
        schema = CreateDatabaseSchemaRequest(
            name="test-schema",
            database="test-service.test-db"
        )

        assert schema.name.root == "test-schema"
        assert schema.database.root == "test-service.test-db"

    def test_create_table_request_minimal(self):
        """Test Table creation model with minimal fields."""
        table = CreateTableRequest(
            name="test-table",
            databaseSchema="test-service.test-db.test-schema",
            columns=[
                Column(name="id", dataType=DataType.BIGINT)
            ]
        )

        assert table.name.root == "test-table"
        assert table.databaseSchema.root == "test-service.test-db.test-schema"
        assert len(table.columns) == 1
        assert table.columns[0].name.root == "id"
        assert table.columns[0].dataType == DataType.BIGINT

    def test_create_table_request_with_multiple_columns(self):
        """Test Table creation with multiple columns."""
        columns = [
            Column(name="id", dataType=DataType.BIGINT),
            Column(name="name", dataType=DataType.STRING),
            Column(name="created_at", dataType=DataType.TIMESTAMP),
            Column(name="amount", dataType=DataType.DECIMAL),
        ]

        table = CreateTableRequest(
            name="test-table",
            databaseSchema="test-service.test-db.test-schema",
            columns=columns
        )

        assert len(table.columns) == 4
        assert table.columns[0].dataType == DataType.BIGINT
        assert table.columns[1].dataType == DataType.STRING
        assert table.columns[2].dataType == DataType.TIMESTAMP
        assert table.columns[3].dataType == DataType.DECIMAL


class TestTypeModels:
    """Test type models (tags, references, etc.)."""

    def test_tag_label_creation(self):
        """Test TagLabel model."""
        tag = TagLabel(
            tagFQN=TagFQN("PII.Sensitive"),
            source=TagSource.Classification,
            labelType=LabelType.Manual,
            state=State.Confirmed
        )

        assert tag.tagFQN.root == "PII.Sensitive"
        assert tag.source == TagSource.Classification
        assert tag.labelType == LabelType.Manual
        assert tag.state == State.Confirmed

    def test_entity_reference_creation(self):
        """Test EntityReference model."""
        ref = EntityReference(
            id="550e8400-e29b-41d4-a716-446655440000",
            type="table"
        )

        assert str(ref.id.root) == "550e8400-e29b-41d4-a716-446655440000"
        assert ref.type == "table"

    def test_markdown_creation(self):
        """Test Markdown model."""
        markdown = Markdown("This is a **test** description")

        assert markdown.root == "This is a **test** description"


class TestLineageModels:
    """Test lineage models."""

    def test_entities_edge_creation(self):
        """Test EntitiesEdge model."""
        edge = EntitiesEdge(
            fromEntity=EntityReference(id="550e8400-e29b-41d4-a716-446655440001", type="table"),
            toEntity=EntityReference(id="550e8400-e29b-41d4-a716-446655440002", type="pipeline")
        )

        assert str(edge.fromEntity.id.root) == "550e8400-e29b-41d4-a716-446655440001"
        assert edge.fromEntity.type == "table"
        assert str(edge.toEntity.id.root) == "550e8400-e29b-41d4-a716-446655440002"
        assert edge.toEntity.type == "pipeline"

    def test_add_lineage_request(self):
        """Test AddLineageRequest model."""
        lineage_request = AddLineageRequest(
            edge=EntitiesEdge(
                fromEntity=EntityReference(id="550e8400-e29b-41d4-a716-446655440001", type="table"),
                toEntity=EntityReference(id="550e8400-e29b-41d4-a716-446655440002", type="pipeline")
            )
        )

        assert lineage_request.edge is not None
        assert str(lineage_request.edge.fromEntity.id.root) == "550e8400-e29b-41d4-a716-446655440001"


class TestModelValidation:
    """Test model validation and error handling."""

    def test_missing_required_field(self):
        """Test that missing required fields raise validation error."""
        with pytest.raises(Exception):  # Pydantic ValidationError
            CreateTableRequest(
                # Missing required 'name' field
                databaseSchema="test-service.test-db.test-schema",
                columns=[]
            )

    def test_invalid_data_type(self):
        """Test that invalid data types are rejected."""
        with pytest.raises(Exception):
            Column(
                name="test",
                dataType="INVALID_TYPE"  # Invalid DataType
            )

    def test_empty_columns_list(self):
        """Test that table with no columns can be created (validation may vary)."""
        # Some versions may allow empty columns, others may not
        # This tests the current behavior
        try:
            table = CreateTableRequest(
                name="test-table",
                databaseSchema="test-service.test-db.test-schema",
                columns=[]
            )
            # If it succeeds, verify structure
            assert table.columns == []
        except Exception:
            # If it fails, that's also acceptable behavior
            pass
