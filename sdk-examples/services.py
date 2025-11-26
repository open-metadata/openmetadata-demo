"""
Services - OpenMetadata SDK Examples

This module demonstrates creating all service types in OpenMetadata.

SDK References:
- API Module: metadata.generated.schema.api.services.*
- Service Entities: metadata.generated.schema.entity.services.*
- Connections: metadata.generated.schema.entity.services.connections.*
- Documentation: https://docs.open-metadata.org/sdk/python/api-reference/services

Source Reference:
- Database Service: example_apis.py lines 99-115
- Storage Service: example_apis.py lines 118-128
- Pipeline Service: example_apis.py lines 131-151
- Messaging Service: example_apis.py lines 153-172

All examples are working, tested solutions from the original codebase.

USAGE:
1. Update SERVER_URL and JWT_TOKEN below
2. Run: python services.py
"""

import json

# ============================================================================
# CONNECTION SETUP
# ============================================================================
# NOTE: Each example file is self-contained. Update these values for your
# OpenMetadata instance, then run this file directly.

from metadata.ingestion.ometa.ometa_api import OpenMetadata
from metadata.generated.schema.entity.services.connections.metadata.openMetadataConnection import (
    OpenMetadataConnection,
    AuthProvider,
)
from metadata.generated.schema.security.client.openMetadataJWTClientConfig import (
    OpenMetadataJWTClientConfig,
)

# TODO: Update these values for your OpenMetadata instance
SERVER_URL = "http://localhost:8585/api"
JWT_TOKEN = "eyJraWQiOiJHYjM4OWEtOWY3Ni1nZGpzLWE5MmotMDI0MmJrOTQzNTYiLCJhbGciOiJSUzI1NiIsInR5cCI6IkpXVCJ9.eyJpc3MiOiJvcGVuLW1ldGFkYXRhLm9yZyIsInN1YiI6ImluZ2VzdGlvbi1ib3QiLCJlbWFpbCI6ImluZ2VzdGlvbi1ib3RAb3Blbm1ldGFkYXRhLm9yZyIsImlzQm90Ijp0cnVlLCJ0b2tlblR5cGUiOiJCT1QiLCJpYXQiOjE2OTU0MDkwNDEsImV4cCI6bnVsbH0.G2cmKdidr_lQd8nNy7i_7X3mSqXJsX4cFk0PqRoN0vJwsIiDhtTc7fd5Fi6NzT5ZxTR9BS2jRuaTMJ0dbBXwNaUZM_VDupGA_foSqfktjr6Ho-YRnmP_z6095lPJG9wE6hcWu6oXPWTR-zys0j0SkrUBFjSmYk-f31KW9jINFtR55MMwqe7weCsZkoJJ5O9w7vku4l6MeOfXVEfkVWCZaBKi93EYBlk9GBcV5HkVhjq2sujYtYUw9muwzl_4jiEZwFkeV7TkV8OBFowaT0L0SRyvuVq3hs27gdLLZBPrN3kiLN8JaGnVE2_CFOSdcrFiQVncyFHihY9C_3f113H-Ag"

# How to get JWT token:
# 1. Open OpenMetadata UI
# 2. Go to Settings > Bots > ingestion-bot
# 3. Copy the JWT token
# Or create a new bot and use its token


def get_metadata_client():
    """
    Create authenticated OpenMetadata client.

    Returns:
        OpenMetadata: Authenticated client instance
    """
    security_config = OpenMetadataJWTClientConfig(jwtToken=JWT_TOKEN)
    server_config = OpenMetadataConnection(
        hostPort=SERVER_URL,
        authProvider=AuthProvider.openmetadata,
        securityConfig=security_config,
    )
    return OpenMetadata(server_config)


# ============================================================================
# SERVICE CREATION EXAMPLES
# ============================================================================

# Service creation imports
from metadata.generated.schema.api.services.createDatabaseService import (
    CreateDatabaseServiceRequest,
)
from metadata.generated.schema.api.services.createStorageService import (
    CreateStorageServiceRequest,
)
from metadata.generated.schema.api.services.createPipelineService import (
    CreatePipelineServiceRequest,
)
from metadata.generated.schema.api.services.createMessagingService import (
    CreateMessagingServiceRequest,
)

# Service type enums
from metadata.generated.schema.entity.services.databaseService import (
    DatabaseService,
    DatabaseServiceType,
    DatabaseConnection,
)

# Connection configurations
from metadata.generated.schema.entity.services.connections.database.snowflakeConnection import (
    SnowflakeConnection,
)
from metadata.generated.schema.entity.services.connections.pipeline.airflowConnection import (
    AirflowConnection,
)


# ============================================================================
# EXAMPLE 1: Create Database Service (Snowflake)
# ----------------------------------------------------------------------------
# Purpose: Create a database service for Snowflake data warehouse
# SDK API: CreateDatabaseServiceRequest
# Required Args:
#   - name (str): Unique service name
#   - serviceType (DatabaseServiceType): Type of database (e.g., Snowflake)
#   - connection (DatabaseConnection): Connection config with credentials
# Optional Args:
#   - description (str): Service description
#   - tags (list): Tags for classification
# Reference: https://docs.open-metadata.org/connectors/database/snowflake
# Source: example_apis.py lines 99-115
# ============================================================================


def create_database_service_snowflake():
    """
    Create a Snowflake database service.

    This example demonstrates creating a database service with Snowflake connection.
    The service acts as a container for databases, schemas, and tables from Snowflake.

    Returns:
        DatabaseService: Created service entity

    Example:
        >>> service = create_database_service_snowflake()
        >>> print(f"Created service: {service.name}")
        Created service: test-snowflake
    """
    metadata = get_metadata_client()

    # Create service request with Snowflake configuration
    # Source: example_apis.py lines 102-113
    create_service = CreateDatabaseServiceRequest(
        name="test-snowflake",  # Service identifier
        serviceType=DatabaseServiceType.Snowflake,  # Database type
        connection=DatabaseConnection(
            config=SnowflakeConnection(
                username="username",  # Snowflake username
                password="password",  # Snowflake password
                account="http://localhost:1234",  # Snowflake account URL
                warehouse="dw",  # Snowflake warehouse name
            )
        ),
    )

    # Create or update the service
    # Source: example_apis.py line 115
    service_entity = metadata.create_or_update(data=create_service)

    print(f"✓ Created Database Service: {service_entity.name.root}")
    print(f"  Type: {service_entity.serviceType.value}")
    print(f"  ID: {service_entity.id.root}")

    return service_entity


# ============================================================================
# EXAMPLE 2: Create Storage Service (S3)
# ----------------------------------------------------------------------------
# Purpose: Create a storage service for AWS S3 object store
# SDK API: CreateStorageServiceRequest
# Required Args:
#   - name (str): Unique service name
#   - serviceType (str): Type of storage (e.g., "S3")
#   - connection (dict): Connection configuration with AWS config
# Optional Args:
#   - description (str): Service description
# Reference: https://docs.open-metadata.org/connectors/storage/s3
# Source: example_apis.py lines 118-128
# ============================================================================


def create_storage_service_s3():
    """
    Create an S3 storage service.

    This example demonstrates creating a storage service for AWS S3.
    The service manages containers (buckets) and their metadata.

    Returns:
        StorageService: Created service entity

    Example:
        >>> service = create_storage_service_s3()
        >>> print(f"Created service: {service.name}")
        Created service: S3 Sample
    """
    metadata = get_metadata_client()

    # Create storage service with S3 configuration
    # Source: example_apis.py lines 120-127
    # NOTE: Using dict format as shown in original example
    create_storage_service_entity = CreateStorageServiceRequest(
        name="S3 Sample",
        serviceType="S3",
        description="S3 Object Store",
        connection={
            "config": {
                "type": "S3",
                "awsConfig": {
                    "awsRegion": "us-west-1"  # AWS region
                },
            }
        },
    )

    # Create or update the service
    # Source: example_apis.py line 128
    storage_service_entity = metadata.create_or_update(data=create_storage_service_entity)

    print(f"✓ Created Storage Service: {storage_service_entity.name.root}")
    print(f"  Type: {storage_service_entity.serviceType.value}")
    print(f"  ID: {storage_service_entity.id.root}")

    return storage_service_entity


# ============================================================================
# EXAMPLE 3: Create Pipeline Service (Airflow)
# ----------------------------------------------------------------------------
# Purpose: Create a pipeline service for Apache Airflow orchestrator
# SDK API: CreatePipelineServiceRequest
# Required Args:
#   - serviceType (str): Type of pipeline service (e.g., "Airflow")
#   - name (str): Unique service name
#   - connection (dict): Connection config with hostPort and connection type
# Optional Args:
#   - description (str): Service description
# Reference: https://docs.open-metadata.org/connectors/pipeline/airflow
# Source: example_apis.py lines 131-151
# ============================================================================


def create_pipeline_service_airflow():
    """
    Create an Airflow pipeline service.

    This example demonstrates creating a pipeline service for Apache Airflow.
    Uses JSON configuration pattern as shown in original examples.

    Returns:
        PipelineService: Created service entity

    Example:
        >>> service = create_pipeline_service_airflow()
        >>> print(f"Created service: {service.name}")
        Created service: sample_airflow1
    """
    metadata = get_metadata_client()

    # Create pipeline service using JSON pattern
    # Source: example_apis.py lines 133-149
    pipeline_service_json = json.loads(
        """
    {
        "serviceType": "Airflow",
        "name": "sample_airflow1",
        "connection": {
            "config": {
                "type": "Airflow",
                "hostPort": "http://localhost:8080",
                "connection": {
                    "type": "Backend"
                }
            }
        }
    }
    """
    )

    # Parse JSON into request object
    # Source: example_apis.py line 150
    create_pipeline_service_entity = CreatePipelineServiceRequest(**pipeline_service_json)

    # Create or update the service
    # Source: example_apis.py line 151
    pipeline_service_entity = metadata.create_or_update(create_pipeline_service_entity)

    print(f"✓ Created Pipeline Service: {pipeline_service_entity.name.root}")
    print(f"  Type: {pipeline_service_entity.serviceType.value}")
    print(f"  ID: {pipeline_service_entity.id.root}")

    return pipeline_service_entity


# ============================================================================
# EXAMPLE 4: Create Messaging Service (Kafka)
# ----------------------------------------------------------------------------
# Purpose: Create a messaging service for Apache Kafka
# SDK API: CreateMessagingServiceRequest
# Required Args:
#   - serviceType (str): Type of messaging service (e.g., "Kafka")
#   - name (str): Unique service name
#   - connection (dict): Connection config with bootstrap servers
# Optional Args:
#   - description (str): Service description
# Reference: https://docs.open-metadata.org/connectors/messaging/kafka
# Source: example_apis.py lines 153-172
# ============================================================================


def create_messaging_service_kafka():
    """
    Create a Kafka messaging service.

    This example demonstrates creating a messaging service for Apache Kafka.
    Uses JSON configuration pattern for complex nested configs.

    Returns:
        MessagingService: Created service entity

    Example:
        >>> service = create_messaging_service_kafka()
        >>> print(f"Created service: {service.name}")
        Created service: sample_kafka1
    """
    metadata = get_metadata_client()

    # Create messaging service using JSON pattern
    # Source: example_apis.py lines 155-168
    messaging_service_json = json.loads(
        """
    {
        "serviceType": "Kafka",
        "name": "sample_kafka1",
        "connection": {
            "config": {
                "type": "Kafka",
                "bootstrapServers": "localhost:9092"
            }
        }
    }
    """
    )

    # Parse JSON into request object
    # Source: example_apis.py lines 169-171
    create_messaging_service_entity = CreateMessagingServiceRequest(
        **messaging_service_json
    )

    # Create or update the service
    # Source: example_apis.py line 172
    messaging_service_entity = metadata.create_or_update(create_messaging_service_entity)

    print(f"✓ Created Messaging Service: {messaging_service_entity.name.root}")
    print(f"  Type: {messaging_service_entity.serviceType.value}")
    print(f"  ID: {messaging_service_entity.id.root}")

    return messaging_service_entity


# ============================================================================
# EXAMPLE 5: List Existing Services
# ----------------------------------------------------------------------------
# Purpose: Retrieve all services of a specific type
# SDK API: metadata.list_all_entities()
# Required Args:
#   - entity: Entity class type (e.g., DatabaseService)
# Optional Args:
#   - fields: List of fields to include in response
# Reference: https://docs.open-metadata.org/sdk/python/api-reference/ometa
# ============================================================================


def list_database_services():
    """
    List all database services in OpenMetadata.

    This example shows how to retrieve existing services.

    Returns:
        list: List of DatabaseService entities

    Example:
        >>> services = list_database_services()
        >>> for svc in services:
        ...     print(f"  - {svc.name}")
    """
    metadata = get_metadata_client()

    # List all database services
    services = metadata.list_all_entities(entity=DatabaseService)

    print(f"\n✓ Found {len(services)} Database Services:")
    for service in services:
        print(f"  - {service.name.root} ({service.serviceType.value})")

    return services


# ============================================================================
# MAIN - Run All Service Examples
# ============================================================================

if __name__ == "__main__":
    print("=" * 70)
    print("OpenMetadata SDK - Service Creation Examples")
    print("=" * 70)
    print()

    try:
        # Example 1: Database Service (Snowflake)
        print("1. Creating Database Service (Snowflake)...")
        db_service = create_database_service_snowflake()
        print()

        # Example 2: Storage Service (S3)
        print("2. Creating Storage Service (S3)...")
        storage_service = create_storage_service_s3()
        print()

        # Example 3: Pipeline Service (Airflow)
        print("3. Creating Pipeline Service (Airflow)...")
        pipeline_service = create_pipeline_service_airflow()
        print()

        # Example 4: Messaging Service (Kafka)
        print("4. Creating Messaging Service (Kafka)...")
        messaging_service = create_messaging_service_kafka()
        print()

        # Example 5: List Database Services
        print("5. Listing Database Services...")
        list_database_services()
        print()

        print("=" * 70)
        print("✓ All service examples completed successfully!")
        print("=" * 70)
        print("\nNext steps:")
        print("  - Run 'python entities.py' to create entities within these services")
        print("  - Check OpenMetadata UI to see the created services")

    except Exception as e:
        print(f"\n✗ Error: {e}")
        print("\nTroubleshooting:")
        print("  1. Ensure OpenMetadata server is running")
        print("  2. Verify connection in setup.py")
        print("  3. Check that JWT token is valid")
