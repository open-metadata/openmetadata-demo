"""Contract tests for the custom database demo."""

from metadata.generated.schema.api.data.createDatabase import CreateDatabaseRequest
from metadata.generated.schema.api.data.createDatabaseSchema import (
    CreateDatabaseSchemaRequest,
)
from metadata.generated.schema.api.data.createStoredProcedure import (
    CreateStoredProcedureRequest,
)
from metadata.generated.schema.api.data.createTable import CreateTableRequest
from metadata.generated.schema.api.services.createDatabaseService import (
    CreateDatabaseServiceRequest,
)
from metadata.ingestion.models.barrier import Barrier
from metadata.ingestion.models.ometa_classification import OMetaTagAndClassification
from metadata.ingestion.models.ometa_lineage import OMetaFQNLineageRequest

from openmetadata_demo_connectors.database import CustomDatabaseSource


def source_config() -> dict:
    """Return the source portion of a valid custom database workflow."""
    return {
        "type": "custom-database",
        "serviceName": "custom_database_demo",
        "serviceConnection": {
            "config": {
                "type": "CustomDatabase",
                "sourcePythonClass": ("openmetadata_demo_connectors.database.CustomDatabaseSource"),
                "connectionOptions": {"databaseName": "customer_catalog"},
            }
        },
        "sourceConfig": {"config": {"type": "DatabaseMetadata"}},
    }


def test_database_connector_emits_a_complete_catalog_in_dependency_order() -> None:
    """The example should demonstrate service, assets, lineage, and ordering."""
    source = CustomDatabaseSource.create(source_config(), metadata=object())

    records = [result.right for result in source._iter()]

    assert [type(record) for record in records] == [
        CreateDatabaseServiceRequest,
        OMetaTagAndClassification,
        CreateDatabaseRequest,
        CreateDatabaseSchemaRequest,
        CreateTableRequest,
        CreateTableRequest,
        CreateDatabaseSchemaRequest,
        CreateTableRequest,
        CreateStoredProcedureRequest,
        Barrier,
        OMetaFQNLineageRequest,
    ]
    barrier_index = next(
        index for index, record in enumerate(records) if isinstance(record, Barrier)
    )
    lineage_index = next(
        index for index, record in enumerate(records) if isinstance(record, OMetaFQNLineageRequest)
    )
    assert barrier_index < lineage_index

    orders = next(
        record
        for record in records
        if isinstance(record, CreateTableRequest) and record.name.root == "orders"
    )
    procedure = next(
        record for record in records if isinstance(record, CreateStoredProcedureRequest)
    )
    assert {"day", "total_amount"} <= {column.name.root for column in orders.columns}
    assert "SELECT day, sum(total_amount)" in procedure.storedProcedureCode.code


def test_database_connector_uses_connection_options() -> None:
    """Customers can override the in-memory catalog name without changing code."""
    source = CustomDatabaseSource.create(source_config(), metadata=object())

    database = next(
        result.right for result in source._iter() if isinstance(result.right, CreateDatabaseRequest)
    )

    assert database.name.root == "customer_catalog"
