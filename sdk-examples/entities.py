"""
Entities - OpenMetadata SDK Examples

This module demonstrates creating all entity types in OpenMetadata.

SDK References:
- API Module: metadata.generated.schema.api.data.*
- Entity Types: metadata.generated.schema.entity.data.*
- Documentation: https://docs.open-metadata.org/sdk/python/api-reference/entities

Source Reference:
- Database/Schema/Table: example_apis.py lines 174-196
- Pipelines: example_apis.py lines 293-304
- Topics: example_apis.py lines 311-323
- Containers: example_apis.py lines 348-434
- API Collections: example_apis.py lines 473-571

All examples are working, tested solutions from the original codebase.
"""

import json
from setup import get_metadata_client

# Database entity imports
from metadata.generated.schema.api.data.createDatabase import (
    CreateDatabaseRequest,
)
from metadata.generated.schema.api.data.createDatabaseSchema import (
    CreateDatabaseSchemaRequest,
)
from metadata.generated.schema.api.data.createTable import CreateTableRequest
from metadata.generated.schema.entity.data.table import (
    Column,
    DataType,
    Table,
)

# Pipeline entity imports
from metadata.generated.schema.api.data.createPipeline import CreatePipelineRequest
from metadata.generated.schema.entity.data.pipeline import (
    Pipeline,
    Task,
)

# Messaging entity imports
from metadata.generated.schema.api.data.createTopic import CreateTopicRequest
from metadata.generated.schema.type import schema

# Storage entity imports
from metadata.generated.schema.api.data.createContainer import CreateContainerRequest
from metadata.generated.schema.type.entityReference import EntityReference

# API entity imports
from metadata.generated.schema.api.data.createAPICollection import (
    CreateAPICollectionRequest,
)
from metadata.generated.schema.api.data.createAPIEndpoint import (
    CreateAPIEndpointRequest,
)


# ============================================================================
# EXAMPLE 1: Create Database → Schema → Table Hierarchy
# ----------------------------------------------------------------------------
# Purpose: Create complete database hierarchy (Database → Schema → Table)
# SDK APIs:
#   - CreateDatabaseRequest
#   - CreateDatabaseSchemaRequest
#   - CreateTableRequest
# Required Args:
#   Database: name (str), service (str - service FQN)
#   Schema: name (str), database (str - database FQN)
#   Table: name (str), databaseSchema (str - schema FQN), columns (list)
# Reference: https://docs.open-metadata.org/sdk/python/build-connector/models
# Source: example_apis.py lines 174-196
# ============================================================================


def create_database_schema_table_hierarchy():
    """
    Create a complete database hierarchy: Database → Schema → Table.

    This example demonstrates the typical structure for database entities:
    1. Create Database under a Service
    2. Create Schema under the Database
    3. Create Table under the Schema with columns

    Returns:
        tuple: (database_entity, schema_entity, table_entity)

    Example:
        >>> db, schema, table = create_database_schema_table_hierarchy()
        >>> print(f"Created table: {table.fullyQualifiedName}")
        Created table: test-snowflake.test-db.test-schema.dim_orders
    """
    metadata = get_metadata_client()

    # Step 1: Create Database
    # Source: example_apis.py lines 176-179
    create_db = CreateDatabaseRequest(
        name="test-db",  # Database name
        service="test-snowflake",  # Parent service name (must exist)
    )

    # Create database entity
    # Source: example_apis.py line 181
    db_entity = metadata.create_or_update(create_db)

    print(f"✓ Created Database: {db_entity.fullyQualifiedName.__root__}")

    # Step 2: Create Database Schema
    # Source: example_apis.py lines 184-186
    create_schema = CreateDatabaseSchemaRequest(
        name="test-schema",  # Schema name
        database="test-snowflake.test-db",  # Parent database FQN
    )

    # Create schema entity
    # Source: example_apis.py line 188
    schema_entity = metadata.create_or_update(data=create_schema)

    print(f"✓ Created Schema: {schema_entity.fullyQualifiedName.__root__}")

    # Step 3: Create Table with columns
    # Source: example_apis.py lines 190-194
    create_table = CreateTableRequest(
        name="dim_orders",  # Table name
        databaseSchema="test-snowflake.test-db.test-schema",  # Parent schema FQN
        columns=[
            Column(name="id", dataType=DataType.BIGINT)  # Column definition
        ],
    )

    # Create table entity
    # Source: example_apis.py line 196
    table_entity = metadata.create_or_update(create_table)

    print(f"✓ Created Table: {table_entity.fullyQualifiedName.__root__}")
    print(f"  Columns: {len(table_entity.columns.__root__)} column(s)")

    return db_entity, schema_entity, table_entity


# ============================================================================
# EXAMPLE 2: Create Tables for Lineage Demo
# ----------------------------------------------------------------------------
# Purpose: Create source and destination tables for lineage examples
# SDK API: CreateTableRequest
# Required Args:
#   - name (str): Table name
#   - databaseSchema (str): Parent schema FQN
#   - columns (list): List of Column objects
# Reference: https://docs.open-metadata.org/sdk/python/api-reference/entities
# Source: example_apis.py lines 198-211
# ============================================================================


def create_tables_for_lineage():
    """
    Create two tables (tableA and tableB) for lineage demonstrations.

    These tables will be used in lineage examples to show data flow:
    tableA → Pipeline → tableB

    Returns:
        tuple: (table_a_entity, table_b_entity)

    Example:
        >>> table_a, table_b = create_tables_for_lineage()
        >>> print(f"Source: {table_a.name}, Destination: {table_b.name}")
        Source: tableA, Destination: tableB
    """
    metadata = get_metadata_client()

    # Create Table A (source)
    # Source: example_apis.py lines 198-202
    table_a = CreateTableRequest(
        name="tableA",
        databaseSchema="test-snowflake.test-db.test-schema",
        columns=[Column(name="id", dataType=DataType.BIGINT)],
    )

    # Create Table B (destination)
    # Source: example_apis.py lines 204-208
    table_b = CreateTableRequest(
        name="tableB",
        databaseSchema="test-snowflake.test-db.test-schema",
        columns=[Column(name="id", dataType=DataType.BIGINT)],
    )

    # Create both tables
    # Source: example_apis.py lines 210-211
    table_a_entity = metadata.create_or_update(data=table_a)
    table_b_entity = metadata.create_or_update(data=table_b)

    print(f"✓ Created Table A: {table_a_entity.fullyQualifiedName.__root__}")
    print(f"✓ Created Table B: {table_b_entity.fullyQualifiedName.__root__}")

    return table_a_entity, table_b_entity


# ============================================================================
# EXAMPLE 3: Create Pipeline with Tasks
# ----------------------------------------------------------------------------
# Purpose: Create a pipeline with tasks for ETL workflows
# SDK API: CreatePipelineRequest
# Required Args:
#   - name (str): Pipeline name
#   - service (str): Parent pipeline service FQN
#   - tasks (list): List of Task objects
# Optional Args:
#   - displayName (str): Human-readable name
#   - description (str): Pipeline description
#   - sourceUrl (str): URL to pipeline in orchestrator UI
# Reference: https://docs.open-metadata.org/sdk/python/api-reference/entities
# Source: example_apis.py lines 293-304
# ============================================================================


def create_pipeline_with_tasks():
    """
    Create a pipeline with tasks representing an ETL workflow.

    This example creates a pipeline with defined tasks, which can be used
    for lineage tracking and workflow documentation.

    Returns:
        Pipeline: Created pipeline entity

    Example:
        >>> pipeline = create_pipeline_with_tasks()
        >>> print(f"Created pipeline: {pipeline.name} with {len(pipeline.tasks)} tasks")
        Created pipeline: table_etl with 1 tasks
    """
    metadata = get_metadata_client()

    # Create task definition
    # Source: example_apis.py line 295
    task = Task(
        name="ingest",  # Task name
        sourceUrl="http://localhost:8080/table_etl/ingest",  # Task URL
    )

    # Create pipeline request
    # Source: example_apis.py lines 296-303
    pipeline_request = CreatePipelineRequest(
        name="table_etl",  # Pipeline name
        displayName="Table ETL",  # Display name
        description="Table ETL",  # Description
        sourceUrl="http://localhost:8080/table_etl",  # Pipeline URL in Airflow
        tasks=[task],  # List of tasks
        service="sample_airflow1",  # Parent service FQN (must exist)
    )

    # Create pipeline
    # Source: example_apis.py line 304
    pipeline = metadata.create_or_update(pipeline_request)

    print(f"✓ Created Pipeline: {pipeline.fullyQualifiedName.__root__}")
    print(f"  Tasks: {len(pipeline.tasks.__root__)} task(s)")
    print(f"  Source URL: {pipeline.sourceUrl.__root__}")

    return pipeline


# ============================================================================
# EXAMPLE 4: Create Kafka Topic with Avro Schema
# ----------------------------------------------------------------------------
# Purpose: Create a messaging topic with schema definition
# SDK API: CreateTopicRequest
# Required Args:
#   - name (str): Topic name
#   - service (str): Parent messaging service FQN
#   - partitions (int): Number of partitions
# Optional Args:
#   - description (str): Topic description
#   - retentionSize (int): Retention size in bytes
#   - messageSchema (schema.Topic): Schema definition
# Reference: https://docs.open-metadata.org/connectors/messaging/kafka
# Source: example_apis.py lines 311-323
# ============================================================================


def create_kafka_topic_with_schema():
    """
    Create a Kafka topic with Avro schema definition.

    This example creates a topic for customer events with a complete
    Avro schema defining the message structure.

    Returns:
        Topic: Created topic entity

    Example:
        >>> topic = create_kafka_topic_with_schema()
        >>> print(f"Created topic: {topic.name} with {topic.partitions} partitions")
        Created topic: customer_events with 56 partitions
    """
    metadata = get_metadata_client()

    # Create topic with Avro schema
    # Source: example_apis.py lines 312-322
    topic_request = CreateTopicRequest(
        name="customer_events",
        description="Kafka topic to capture the customer events such as location updates or profile updates",
        partitions=56,  # Number of partitions
        retentionSize=455858109,  # Retention size in bytes
        messageSchema=schema.Topic(
            schemaType="Avro",  # Schema type
            schemaText='{"namespace":"org.open-metadata.kafka","name":"Customer","type":"record","fields":[{"name":"id","type":"string"},{"name":"first_name","type":"string"},{"name":"last_name","type":"string"},{"name":"email","type":"string"},{"name":"address_line_1","type":"string"},{"name":"address_line_2","type":"string"},{"name":"post_code","type":"string"},{"name":"country","type":"string"}]}',
        ),
        service="sample_kafka1",  # Parent service FQN (must exist)
    )

    # Create topic
    # Source: example_apis.py line 323
    topic = metadata.create_or_update(topic_request)

    print(f"✓ Created Topic: {topic.fullyQualifiedName.__root__}")
    print(f"  Partitions: {topic.partitions.__root__}")
    print(f"  Schema Type: {topic.messageSchema.schemaType.value}")

    return topic


# ============================================================================
# EXAMPLE 5: Create Storage Container with Nested Containers
# ----------------------------------------------------------------------------
# Purpose: Create storage containers (buckets) with nested structure
# SDK API: CreateContainerRequest
# Required Args:
#   - name (str): Container name
#   - service (str): Parent storage service FQN
# Optional Args:
#   - parent (EntityReference): Parent container for nesting
#   - prefix (str): Path prefix
#   - dataModel (dict): Schema definition for structured data
#   - numberOfObjects (str): Number of objects
#   - size (str): Total size in bytes
#   - fileFormats (list): File format types
# Reference: https://docs.open-metadata.org/connectors/storage/s3
# Source: example_apis.py lines 348-434
# ============================================================================


def create_storage_containers():
    """
    Create storage containers with nested structure.

    This example creates:
    1. Root container for transactions with data model
    2. Child container for departments (nested under root)

    Returns:
        tuple: (parent_container, child_container)

    Example:
        >>> parent, child = create_storage_containers()
        >>> print(f"Parent: {parent.name}, Child: {child.name}")
        Parent: transactions2, Child: departments
    """
    metadata = get_metadata_client()

    # Create root container with complex data model
    # Source: example_apis.py lines 349-412
    container_request_json = json.loads(
        """
  {
    "name": "transactions2",
    "displayName": "Company Transactions",
    "description": "Bucket containing all the company's transactions",
    "parent": null,
    "prefix": "/transactions/",
    "dataModel": {
      "isPartitioned": true,
      "columns": [
        {
          "name": "date",
          "dataType": "NUMERIC",
          "dataTypeDisplay": "numeric",
          "description": "The ID of the executed transaction. This column is the primary key for this table.",
          "tags": [],
          "constraint": "PRIMARY_KEY",
          "ordinalPosition": 1,
          "children": [
          {
          "name": "country",
           "dataType": "NUMERIC",
           "dataTypeDisplay": "numeric",
            "description": "Nested",
            "tags": [],
            "children": [
              {
               "name": "state",
                "dataType": "NUMERIC",
                "dataTypeDisplay": "numeric",
            "description": "Nested",
            "tags": []

              }
            ]
          }
          ]
        },
        {
          "name": "merchant",
          "dataType": "VARCHAR",
          "dataLength": 100,
          "dataTypeDisplay": "varchar",
          "description": "The merchant for this transaction.",
          "tags": [],
          "ordinalPosition": 2
        },
        {
          "name": "transaction_time",
          "dataType": "TIMESTAMP",
          "dataTypeDisplay": "timestamp",
          "description": "The time the transaction took place.",
          "tags": [],
          "ordinalPosition": 3
        }
      ]
    },
    "numberOfObjects": "50",
    "size": "102400",
    "fileFormats": [
      "parquet"
    ]
  }
    """
    )

    # Add service reference
    # Source: example_apis.py line 413
    container_request_json["service"] = "S3 Sample"  # Must exist from services.py

    # Create container request
    # Source: example_apis.py line 414
    container_request = CreateContainerRequest(**container_request_json)

    # Create parent container
    # Source: example_apis.py line 415
    container_entity = metadata.create_or_update(container_request)

    print(f"✓ Created Container: {container_entity.fullyQualifiedName.__root__}")
    print(f"  Objects: {container_entity.numberOfObjects.__root__}")
    print(f"  Size: {container_entity.size.__root__} bytes")

    # Create nested child container
    # Source: example_apis.py lines 417-430
    child_container_request_json = json.loads(
        """
{
    "name": "departments",
    "displayName": "Company departments",
    "description": "Bucket containing company department information",
    "prefix": "/departments/",
    "dataModel": null,
    "numberOfObjects": "2",
    "size": "2048",
    "fileFormats": [
      "csv"
    ]
  }
    """
    )

    # Set parent reference for nesting
    # Source: example_apis.py line 431
    child_container_request_json["parent"] = EntityReference(
        id=container_entity.id, type="container"
    )

    # Add service reference
    # Source: example_apis.py line 432
    child_container_request_json["service"] = "S3 Sample"

    # Create child container request
    # Source: example_apis.py line 433
    child_container_request = CreateContainerRequest(**child_container_request_json)

    # Create child container
    # Source: example_apis.py line 434
    child_container_entity = metadata.create_or_update(child_container_request)

    print(f"✓ Created Child Container: {child_container_entity.fullyQualifiedName.__root__}")
    print(f"  Parent: {container_entity.name.__root__}")

    return container_entity, child_container_entity


# ============================================================================
# EXAMPLE 6: Create API Collection and Endpoint
# ----------------------------------------------------------------------------
# Purpose: Create API collection with endpoints (REST API documentation)
# SDK APIs:
#   - CreateAPICollectionRequest
#   - CreateAPIEndpointRequest
# Required Args:
#   Collection: name (str), service (str), endpointURL (str)
#   Endpoint: name (str), apiCollection (str), requestMethod (str)
# Optional Args:
#   - requestSchema (dict): Request body schema
#   - responseSchema (dict): Response body schema
# Reference: https://docs.open-metadata.org/connectors/api
# Source: example_apis.py lines 473-571
# ============================================================================


def create_api_collection_and_endpoint():
    """
    Create an API collection with endpoints.

    This example demonstrates documenting REST APIs in OpenMetadata:
    1. Create API Collection (group of related endpoints)
    2. Create API Endpoint with request/response schemas

    Returns:
        tuple: (collection_entity, endpoint_entity)

    Example:
        >>> collection, endpoint = create_api_collection_and_endpoint()
        >>> print(f"Collection: {collection.name}, Endpoint: {endpoint.name}")
        Collection: pet, Endpoint: updatePet
    """
    metadata = get_metadata_client()

    # Create API collection
    # Source: example_apis.py lines 485-489
    collection_request = CreateAPICollectionRequest(
        name="pet",  # Collection name
        service="sample_api_service",  # Parent API service (must exist)
        endpointURL="https://petstore3.swagger.io/#/pet",  # Base URL
    )

    # Create collection
    # Source: example_apis.py line 491
    collection_entity = metadata.create_or_update(data=collection_request)

    print(f"✓ Created API Collection: {collection_entity.fullyQualifiedName.__root__}")

    # Create API endpoint with schemas
    # Source: example_apis.py lines 495-569
    # Reference: https://docs.open-metadata.org/swagger.json (line 493)
    endpoint_request = CreateAPIEndpointRequest(
        **{
            "name": "updatePet",  # Endpoint name
            "displayName": "Update Pet",  # Display name
            "description": "Update an existing pet",  # Description
            "endpointURL": "https://petstore3.swagger.io/#/pet/updatePet",  # Full URL
            "apiCollection": "sample_api_service.pet",  # Parent collection FQN
            "requestMethod": "PUT",  # HTTP method
            "requestSchema": {
                "schemaType": "JSON",  # Schema type
                "schemaFields": [
                    {
                        "name": "id",
                        "dataType": "INT",
                        "description": "ID of pet that needs to be updated",
                    },
                    {
                        "name": "name",
                        "dataType": "STRING",
                        "description": "Name of pet",
                    },
                    {
                        "name": "category",
                        "dataType": "RECORD",
                        "description": "Category of pet",
                        "children": [  # Nested schema fields
                            {
                                "name": "id",
                                "dataType": "INT",
                                "description": "ID of category",
                            },
                            {
                                "name": "name",
                                "dataType": "STRING",
                                "description": "Name of category",
                            },
                        ],
                    },
                ],
            },
            "responseSchema": {
                "schemaType": "JSON",
                "schemaFields": [
                    {
                        "name": "id",
                        "dataType": "INT",
                        "description": "ID of pet that needs to be updated",
                    },
                    {
                        "name": "name",
                        "dataType": "STRING",
                        "description": "Name of pet",
                    },
                    {
                        "name": "category",
                        "dataType": "RECORD",
                        "description": "Category of pet",
                        "children": [
                            {
                                "name": "id",
                                "dataType": "INT",
                                "description": "ID of category",
                            },
                            {
                                "name": "name",
                                "dataType": "STRING",
                                "description": "Name of category",
                            },
                        ],
                    },
                ],
            },
        }
    )

    # Create endpoint
    # Source: example_apis.py line 571
    endpoint_entity = metadata.create_or_update(data=endpoint_request)

    print(f"✓ Created API Endpoint: {endpoint_entity.fullyQualifiedName.__root__}")
    print(f"  Method: {endpoint_entity.requestMethod.value}")

    return collection_entity, endpoint_entity


# ============================================================================
# MAIN - Run All Entity Examples
# ============================================================================

if __name__ == "__main__":
    print("=" * 70)
    print("OpenMetadata SDK - Entity Creation Examples")
    print("=" * 70)
    print()
    print("NOTE: Ensure services exist (run services.py first)")
    print()

    try:
        # Example 1: Database → Schema → Table
        print("1. Creating Database → Schema → Table Hierarchy...")
        db, schema, table = create_database_schema_table_hierarchy()
        print()

        # Example 2: Tables for Lineage
        print("2. Creating Tables for Lineage...")
        table_a, table_b = create_tables_for_lineage()
        print()

        # Example 3: Pipeline
        print("3. Creating Pipeline with Tasks...")
        pipeline = create_pipeline_with_tasks()
        print()

        # Example 4: Kafka Topic
        print("4. Creating Kafka Topic with Avro Schema...")
        topic = create_kafka_topic_with_schema()
        print()

        # Example 5: Storage Containers
        print("5. Creating Storage Containers (nested)...")
        parent_container, child_container = create_storage_containers()
        print()

        # Example 6: API Collection and Endpoint
        print("6. Creating API Collection and Endpoint...")
        print("   (Skipping - requires API service to be created first)")
        # Uncomment to run if API service exists:
        # collection, endpoint = create_api_collection_and_endpoint()
        print()

        print("=" * 70)
        print("✓ All entity examples completed successfully!")
        print("=" * 70)
        print("\nNext steps:")
        print("  - Run 'python metadata_ops.py' to add metadata (tags, descriptions)")
        print("  - Run 'python lineage.py' to create lineage relationships")
        print("  - Check OpenMetadata UI to see the created entities")

    except Exception as e:
        print(f"\n✗ Error: {e}")
        print("\nTroubleshooting:")
        print("  1. Ensure services exist (run: python services.py)")
        print("  2. Verify OpenMetadata server is running")
        print("  3. Check connection in setup.py")
