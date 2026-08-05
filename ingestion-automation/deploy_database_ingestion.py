#!/usr/bin/env python3
"""Create, deploy, and trigger a database ingestion pipeline through the API."""

import os
from collections.abc import Mapping
from dataclasses import dataclass

from metadata.generated.schema.api.services.createDatabaseService import (
    CreateDatabaseServiceRequest,
)
from metadata.generated.schema.api.services.ingestionPipelines.createIngestionPipeline import (  # noqa: E501
    CreateIngestionPipelineRequest,
)
from metadata.generated.schema.entity.services.connections.database.common.basicAuth import (
    BasicAuth,
)
from metadata.generated.schema.entity.services.connections.database.postgresConnection import (
    PostgresConnection,
)
from metadata.generated.schema.entity.services.connections.metadata.openMetadataConnection import (  # noqa: E501
    AuthProvider,
    OpenMetadataConnection,
)
from metadata.generated.schema.entity.services.databaseService import (
    DatabaseConnection,
    DatabaseServiceType,
)
from metadata.generated.schema.entity.services.ingestionPipelines.ingestionPipeline import (
    AirflowConfig,
    PipelineType,
)
from metadata.generated.schema.metadataIngestion.databaseServiceMetadataPipeline import (
    DatabaseServiceMetadataPipeline,
)
from metadata.generated.schema.metadataIngestion.workflow import SourceConfig
from metadata.generated.schema.security.client.openMetadataJWTClientConfig import (
    OpenMetadataJWTClientConfig,
)
from metadata.generated.schema.type.entityReference import EntityReference
from metadata.ingestion.ometa.ometa_api import OpenMetadata
from metadata.ingestion.ometa.utils import model_str


@dataclass(frozen=True)
class DeploymentConfig:
    """Environment-specific values for the deployment example."""

    openmetadata_host: str
    jwt_token: str
    service_name: str
    postgres_host: str
    postgres_username: str
    postgres_password: str
    postgres_database: str

    @classmethod
    def from_environment(
        cls,
        environ: Mapping[str, str] | None = None,
    ) -> "DeploymentConfig":
        """Load settings without embedding credentials in source."""
        values = os.environ if environ is None else environ
        required = ["OPENMETADATA_JWT_TOKEN", "POSTGRES_PASSWORD"]
        missing = [name for name in required if not values.get(name)]
        if missing:
            raise RuntimeError(f"Missing required environment variables: {', '.join(missing)}")
        return cls(
            openmetadata_host=values.get("OPENMETADATA_HOST", "http://localhost:8585/api"),
            jwt_token=values["OPENMETADATA_JWT_TOKEN"],
            service_name=values.get("OPENMETADATA_SERVICE_NAME", "warehouse"),
            postgres_host=values.get("POSTGRES_HOST", "localhost:5432"),
            postgres_username=values.get("POSTGRES_USERNAME", "postgres"),
            postgres_password=values["POSTGRES_PASSWORD"],
            postgres_database=values.get("POSTGRES_DATABASE", "analytics"),
        )


def build_metadata_client(config: DeploymentConfig) -> OpenMetadata:
    """Construct the OpenMetadata client when the command is executed."""
    return OpenMetadata(
        OpenMetadataConnection(
            hostPort=config.openmetadata_host,
            securityConfig=OpenMetadataJWTClientConfig(jwtToken=config.jwt_token),
            authProvider=AuthProvider.openmetadata,
        )
    )


def build_service_request(config: DeploymentConfig) -> CreateDatabaseServiceRequest:
    """Build the Postgres service request without contacting the server."""
    return CreateDatabaseServiceRequest(
        name=config.service_name,
        serviceType=DatabaseServiceType.Postgres,
        connection=DatabaseConnection(
            config=PostgresConnection(
                hostPort=config.postgres_host,
                username=config.postgres_username,
                authType=BasicAuth(password=config.postgres_password),
                database=config.postgres_database,
            )
        ),
    )


def build_pipeline_request(
    service_id: str,
    service_name: str,
) -> CreateIngestionPipelineRequest:
    """Build a paused metadata pipeline ready for deployment."""
    return CreateIngestionPipelineRequest(
        name=f"{service_name}_metadata",
        pipelineType=PipelineType.metadata,
        sourceConfig=SourceConfig(
            config=DatabaseServiceMetadataPipeline(
                type="DatabaseMetadata",
                includeTables=True,
                includeViews=True,
            )
        ),
        airflowConfig=AirflowConfig(pausePipeline=True),
        service=EntityReference(id=service_id, type="databaseService"),
    )


def deploy_pipeline(metadata: OpenMetadata, pipeline_id: str) -> dict:
    """Deploy a pipeline using the 2.0 REST response contract."""
    return metadata.client.post(f"/services/ingestionPipelines/deploy/{pipeline_id}")


def trigger_pipeline(metadata: OpenMetadata, pipeline_id: str) -> dict:
    """Trigger a pipeline using the 2.0 REST response contract."""
    return metadata.client.post(f"/services/ingestionPipelines/trigger/{pipeline_id}")


def run(config: DeploymentConfig | None = None) -> int:
    """Create the service and pipeline, then deploy and trigger it."""
    deployment = config or DeploymentConfig.from_environment()
    metadata = build_metadata_client(deployment)

    service = metadata.create_or_update(build_service_request(deployment))
    print(f"Service created: {model_str(service.fullyQualifiedName)}")

    pipeline = metadata.create_or_update(
        build_pipeline_request(
            service_id=model_str(service.id),
            service_name=deployment.service_name,
        )
    )
    pipeline_id = model_str(pipeline.id)
    print(f"Pipeline created: {model_str(pipeline.fullyQualifiedName)}")
    print(f"Pipeline deployed: {deploy_pipeline(metadata, pipeline_id)}")
    print(f"Pipeline triggered: {trigger_pipeline(metadata, pipeline_id)}")
    return 0


if __name__ == "__main__":
    raise SystemExit(run())
