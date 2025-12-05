#!/usr/bin/env python3
"""
Deploy Database Ingestion Pipeline

This script demonstrates how to programmatically:
1. Create a database service with connection details
2. Create an ingestion pipeline for that service
3. Trigger the ingestion pipeline to run

Usage:
    python deploy_database_ingestion.py
"""

# =============================================================================
# Imports
# =============================================================================

from metadata.ingestion.ometa.ometa_api import OpenMetadata
from metadata.generated.schema.entity.services.connections.metadata.openMetadataConnection import (
    OpenMetadataConnection,
    AuthProvider,
)
from metadata.generated.schema.security.client.openMetadataJWTClientConfig import (
    OpenMetadataJWTClientConfig,
)
from metadata.generated.schema.api.services.createDatabaseService import (
    CreateDatabaseServiceRequest,
)
from metadata.generated.schema.entity.services.databaseService import (
    DatabaseService,
    DatabaseServiceType,
    DatabaseConnection,
)
from metadata.generated.schema.api.services.ingestionPipelines.createIngestionPipeline import (
    CreateIngestionPipelineRequest,
)
from metadata.generated.schema.entity.services.ingestionPipelines.ingestionPipeline import (
    AirflowConfig,
    IngestionPipeline,
    PipelineType,
)
from metadata.generated.schema.metadataIngestion.workflow import SourceConfig
from metadata.generated.schema.metadataIngestion.databaseServiceMetadataPipeline import (
    DatabaseServiceMetadataPipeline,
)
from metadata.generated.schema.entity.services.connections.database.postgresConnection import (
    PostgresConnection,
)
from metadata.generated.schema.entity.services.connections.database.common.basicAuth import (
    BasicAuth,
)
from metadata.generated.schema.type.entityReference import EntityReference

# =============================================================================
# Configuration - Update these values for your environment
# =============================================================================

JWT_TOKEN = "eyJraWQiOiJHYjM4OWEtOWY3Ni1nZGpzLWE5MmotMDI0MmJrOTQzNTYiLCJhbGciOiJSUzI1NiIsInR5cCI6IkpXVCJ9.eyJpc3MiOiJvcGVuLW1ldGFkYXRhLm9yZyIsInN1YiI6ImluZ2VzdGlvbi1ib3QiLCJyb2xlcyI6WyJJbmdlc3Rpb25Cb3RSb2xlIl0sImVtYWlsIjoiaW5nZXN0aW9uLWJvdEBvcGVuLW1ldGFkYXRhLm9yZyIsImlzQm90Ijp0cnVlLCJ0b2tlblR5cGUiOiJCT1QiLCJpYXQiOjE3NjQ5MDY5MTQsImV4cCI6bnVsbH0.JQdCi3Uhc3o6xZ6-MotwDQSbJmuOgtZanAvrJN4Kje4bGhXInp5BcL0Fp9KZM7zrA8uM7QbC3_HMEZYbYiMfa9mEzKD8-zHhKFp6XAyvK4GKk8mLW7tQNl0mIFBnXc2AoSSQkl8FSg8XNAqJThiaQoafy6q6X-pk6wrOeMXuUen0EKYe1nkLnxWZLrnIhGamCbOFrYdWSiyZFdIem8UoWBv5hqRTjE2MGshVRriae3PQKCruK96c-HJDTDIQQly78V56j1L06Jk8ceaM7mvadYEIB6iZ25hfwm2Yfr40BF0iOOkkQK1YaZLFIBEQDRQPRZaI4twEALyOq9ZjtNqy8g"
OM_HOST = "http://localhost:8585/api"

SERVICE_NAME = "my_postgres_service"
SERVICE_HOST = "localhost:5432"
SERVICE_USER = "postgres_user"
SERVICE_PASSWORD = "postgres_password"
SERVICE_DATABASE = "my_database"

# =============================================================================
# Step 1: Connect to OpenMetadata
# =============================================================================

metadata = OpenMetadata(
    OpenMetadataConnection(
        hostPort=OM_HOST,
        securityConfig=OpenMetadataJWTClientConfig(jwtToken=JWT_TOKEN),
        authProvider=AuthProvider.openmetadata,
    )
)

assert metadata.health_check(), "Failed to connect to OpenMetadata"

# =============================================================================
# Step 2: Create Database Service
# =============================================================================

service = metadata.create_or_update(
    CreateDatabaseServiceRequest(
        name=SERVICE_NAME,
        serviceType=DatabaseServiceType.Postgres,
        connection=DatabaseConnection(
            config=PostgresConnection(
                hostPort=SERVICE_HOST,
                username=SERVICE_USER,
                authType=BasicAuth(password=SERVICE_PASSWORD),
                database=SERVICE_DATABASE,
            )
        ),
    )
)

print(f"Service created: {service.fullyQualifiedName}")

# =============================================================================
# Step 3: Create Ingestion Pipeline
# =============================================================================

pipeline = metadata.create_or_update(
    CreateIngestionPipelineRequest(
        name=f"{SERVICE_NAME}_metadata",
        pipelineType=PipelineType.metadata,
        sourceConfig=SourceConfig(
            config=DatabaseServiceMetadataPipeline(
                type="DatabaseMetadata",
                includeTables=True,
                includeViews=True,
            )
        ),
        airflowConfig=AirflowConfig(pausePipeline=True),
        service=EntityReference(id=service.id, type="databaseService"),
    )
)

print(f"Pipeline created: {pipeline.fullyQualifiedName}")

# =============================================================================
# Step 4: Deploy Pipeline to Airflow
# =============================================================================

pipeline_id = str(pipeline.id.root if hasattr(pipeline.id, "root") else pipeline.id)

# Deploy creates the DAG in Airflow (required before triggering)
try:
    deploy_response = metadata.client.post(f"/services/ingestionPipelines/deploy/{pipeline_id}")
    print(f"Pipeline deployed: {deploy_response}")
except Exception as e:
    print(f"Pipeline deploy failed: {e}")

# =============================================================================
# Step 5: Trigger Pipeline Run
# =============================================================================

# Note: metadata.run_pipeline() has a bug - the /trigger/{id} endpoint returns
# PipelineServiceClientResponse {'code': 200, 'reason': '...', 'platform': 'Airflow'}
# but the SDK tries to parse it as IngestionPipeline, causing a KeyError: 'sourceConfig'
# Using raw API call until SDK is fixed.
try:
    trigger_response = metadata.client.post(f"/services/ingestionPipelines/trigger/{pipeline_id}")
    print(f"Pipeline triggered: {trigger_response}")
except Exception as e:
    print(f"Pipeline trigger failed: {e}")
