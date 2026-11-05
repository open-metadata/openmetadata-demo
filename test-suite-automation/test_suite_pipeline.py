#!/usr/bin/env python3
"""Schedule an existing table Test Suite on the server's configured orchestrator."""

import argparse
import os
import sys
from typing import Literal

from metadata.generated.schema.api.services.ingestionPipelines.createIngestionPipeline import (  # noqa: E501
    CreateIngestionPipelineRequest,
)
from metadata.generated.schema.entity.services.connections.metadata.openMetadataConnection import (  # noqa: E501
    OpenMetadataConnection,
)
from metadata.generated.schema.entity.services.ingestionPipelines.ingestionPipeline import (
    AirflowConfig,
    IngestionPipeline,
    PipelineType,
)
from metadata.generated.schema.entity.services.ingestionPipelines.pipelineServiceClientResponse import (  # noqa: E501
    PipelineServiceClientResponse,
)
from metadata.generated.schema.metadataIngestion.testSuitePipeline import TestSuitePipeline
from metadata.generated.schema.metadataIngestion.workflow import SourceConfig
from metadata.generated.schema.security.client.openMetadataJWTClientConfig import (
    OpenMetadataJWTClientConfig,
)
from metadata.generated.schema.tests.testSuite import TestSuite
from metadata.generated.schema.type.entityReference import EntityReference
from metadata.ingestion.ometa.client import APIError
from metadata.ingestion.ometa.ometa_api import OpenMetadata
from metadata.ingestion.ometa.utils import model_str
from metadata.utils.fqn import quote_name


def build_pipeline_request(
    suite: TestSuite, pipeline_name: str, airflow_config: AirflowConfig
) -> CreateIngestionPipelineRequest:
    """Associate the pipeline with the suite and execute against its table FQN."""
    table = suite.basicEntityReference
    if not suite.basic or not suite.id or not suite.fullyQualifiedName:
        raise ValueError(
            "Choose an existing executable (basic/table) Test Suite with an ID and FQN."
        )
    if table is None or table.type != "table" or not table.fullyQualifiedName:
        raise ValueError("The Test Suite must have a basicEntityReference with a table FQN.")
    return CreateIngestionPipelineRequest(
        name=pipeline_name,
        pipelineType=PipelineType.TestSuite,
        service=EntityReference(id=suite.id, type="testSuite"),
        sourceConfig=SourceConfig(
            config=TestSuitePipeline(
                type="TestSuite",
                entityFullyQualifiedName=table.fullyQualifiedName,
            )
        ),
        airflowConfig=airflow_config,
    )


def configure_pipeline(
    metadata: OpenMetadata,
    suite_fqn: str,
    pipeline_name: str,
    airflow_config: AirflowConfig,
) -> IngestionPipeline:
    """Create a pipeline or change only the cron schedule of an existing one."""
    suite = metadata.get_by_name(entity=TestSuite, fqn=suite_fqn, fields=["basicEntityReference"])
    if suite is None:
        raise ValueError(f"Test Suite not found: {suite_fqn}")
    request = build_pipeline_request(suite, pipeline_name, airflow_config)
    pipeline_fqn = f"{model_str(suite.fullyQualifiedName)}.{quote_name(pipeline_name)}"
    pipeline = metadata.get_by_name(
        entity=IngestionPipeline, fqn=pipeline_fqn, fields=["airflowConfig"]
    )
    if pipeline is None:
        return metadata.create_or_update(data=request)
    if (
        pipeline.pipelineType != PipelineType.TestSuite
        or pipeline.service is None
        or pipeline.service.type != "testSuite"
        or pipeline.service.id != suite.id
    ):
        raise ValueError("Existing pipeline does not belong to the selected Test Suite.")
    updated = pipeline.model_copy(deep=True)
    updated.airflowConfig.scheduleInterval = airflow_config.scheduleInterval
    # PUT would reset omitted settings; patch only the cron schedule instead.
    return (
        metadata.patch(
            entity=IngestionPipeline,
            source=pipeline,
            destination=updated,
            skip_on_failure=False,
        )
        or pipeline
    )


def pipeline_action(
    metadata: OpenMetadata, pipeline_id: str, action: Literal["deploy", "trigger"]
) -> PipelineServiceClientResponse:
    """Deploy or trigger without parsing the response as an IngestionPipeline."""
    response = PipelineServiceClientResponse.model_validate(
        metadata.client.post(f"/services/ingestionPipelines/{action}/{pipeline_id}")
    )
    if not 200 <= response.code < 300:
        raise RuntimeError(f"Pipeline {action} failed ({response.code}): {response.reason}")
    return response


def main() -> int:
    """Load credentials at execution time; deploy and optionally trigger the pipeline."""
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--test-suite-fqn", required=True)
    parser.add_argument("--pipeline-name", default="daily_data_quality")
    parser.add_argument("--schedule", default="0 6 * * *", help="Five-field cron expression")
    parser.add_argument("--trigger", action="store_true", help="Also request an immediate run")
    args = parser.parse_args()
    token = os.environ.get("OPENMETADATA_JWT_TOKEN")
    if not token:
        parser.error("Set OPENMETADATA_JWT_TOKEN before running this example.")
    host = os.environ.get("OPENMETADATA_HOST")
    if not host or not host.rstrip("/").endswith("/api"):
        parser.error("Set OPENMETADATA_HOST to your server URL ending in /api.")
    metadata = None
    try:
        metadata = OpenMetadata(
            OpenMetadataConnection(
                hostPort=host.rstrip("/"),
                authProvider="openmetadata",
                securityConfig=OpenMetadataJWTClientConfig(jwtToken=token),
            )
        )
        pipeline = configure_pipeline(
            metadata=metadata,
            suite_fqn=args.test_suite_fqn,
            pipeline_name=args.pipeline_name,
            airflow_config=AirflowConfig(scheduleInterval=args.schedule),
        )
        pipeline_id = model_str(pipeline.id)
        deployed = pipeline_action(metadata, pipeline_id, "deploy")
        print(f"Deployed {model_str(pipeline.fullyQualifiedName)} on {deployed.platform}")
        if args.trigger:
            triggered = pipeline_action(metadata, pipeline_id, "trigger")
            print(
                f"Run requested on {triggered.platform}; "
                f"run ID: {triggered.runId or 'not returned'}"
            )
    except (APIError, ValueError, RuntimeError, OSError) as exc:
        print(f"Error: {exc}", file=sys.stderr)
        return 1
    finally:
        if metadata is not None:
            metadata.close()
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
