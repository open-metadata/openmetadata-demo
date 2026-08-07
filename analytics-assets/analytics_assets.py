"""Create representative analytics assets with public OpenMetadata facades."""

from __future__ import annotations

import os
import re
from collections.abc import Mapping
from typing import Any

from metadata.generated.schema.api.data.createChart import CreateChartRequest
from metadata.generated.schema.api.data.createDashboard import CreateDashboardRequest
from metadata.generated.schema.api.data.createDashboardDataModel import (
    CreateDashboardDataModelRequest,
)
from metadata.generated.schema.api.data.createMlModel import CreateMlModelRequest
from metadata.generated.schema.api.data.createPipeline import CreatePipelineRequest
from metadata.generated.schema.api.data.createQuery import CreateQueryRequest
from metadata.generated.schema.api.data.createSearchIndex import (
    CreateSearchIndexRequest,
)
from metadata.generated.schema.api.services.createDashboardService import (
    CreateDashboardServiceRequest,
)
from metadata.generated.schema.entity.data.dashboardDataModel import DataModelType
from metadata.generated.schema.entity.data.mlmodel import (
    FeatureType,
    MlFeature,
    MlHyperParameter,
)
from metadata.generated.schema.entity.data.pipeline import (
    PipelineStatus,
    StatusType,
    Task,
    TaskStatus,
)
from metadata.generated.schema.entity.data.searchIndex import (
    DataType as SearchDataType,
)
from metadata.generated.schema.entity.data.searchIndex import SearchIndexField
from metadata.generated.schema.entity.data.table import Column, DataType
from metadata.generated.schema.entity.services.dashboardService import (
    DashboardServiceType,
)
from metadata.generated.schema.type.basic import Markdown
from metadata.ingestion.ometa.utils import model_str
from metadata.sdk import (
    Charts,
    DashboardDataModels,
    Dashboards,
    DashboardServices,
    MLModels,
    Pipelines,
    Queries,
    SearchIndexes,
    configure,
    reset,
)

NAMESPACE_PATTERN = re.compile(r"^[a-z][a-z0-9_]{2,31}$")
SCENARIO = "analytics-assets"
BASE_ENV = (
    "OPENMETADATA_HOST",
    "OPENMETADATA_JWT_TOKEN",
    "OPENMETADATA_DEMO_NAMESPACE",
)
PARENT_ENV = {
    "OPENMETADATA_DATABASE_SERVICE_FQN": "database_service",
    "OPENMETADATA_ML_MODEL_SERVICE_FQN": "ml_model_service",
    "OPENMETADATA_PIPELINE_SERVICE_FQN": "pipeline_service",
    "OPENMETADATA_SEARCH_SERVICE_FQN": "search_service",
}
STATUS_TIMESTAMP = 1_735_689_600_000


def ownership_marker(namespace: str) -> str:
    return f"[openmetadata-demo:{namespace}:{SCENARIO}]"


def validate_environment(
    environ: Mapping[str, str] | None = None,
) -> tuple[str, dict[str, str]]:
    """Validate credentials, namespace, and required existing services."""
    values = os.environ if environ is None else environ
    required = (*BASE_ENV, *PARENT_ENV)
    missing = [name for name in required if not values.get(name)]
    if missing:
        raise ValueError(f"Missing required environment variables: {', '.join(missing)}")

    namespace = values["OPENMETADATA_DEMO_NAMESPACE"]
    if not NAMESPACE_PATTERN.fullmatch(namespace):
        raise ValueError("OPENMETADATA_DEMO_NAMESPACE must match ^[a-z][a-z0-9_]{2,31}$")
    return namespace, {key: values[name] for name, key in PARENT_ENV.items()}


def owned_upsert(
    facade: Any,
    fqn: str,
    request: Any,
    marker: str,
) -> Any:
    """PUT an absent or exactly owned entity; refuse foreign collisions."""
    existing = facade.retrieve_by_name(fqn, nullable=True)
    description = model_str(getattr(existing, "description", "")) if existing else ""
    if existing is not None and marker not in description:
        raise RuntimeError(f"Refusing to overwrite foreign entity: {fqn}")
    return facade.create(request)


def build_requests(namespace: str, parents: Mapping[str, str]) -> dict[str, Any]:
    """Build every RC1 request before the first network mutation."""
    marker = ownership_marker(namespace)
    dashboard_service = f"{namespace}_dashboard_service"
    chart_fqn = f"{dashboard_service}.{namespace}_chart"
    data_model_fqn = f"{dashboard_service}.model.{namespace}_data_model"

    return {
        "service": CreateDashboardServiceRequest(
            name=dashboard_service,
            description=Markdown(root=f"{marker} Demo dashboard service."),
            serviceType=DashboardServiceType.CustomDashboard,
        ),
        "chart": CreateChartRequest(
            name=f"{namespace}_chart",
            description=Markdown(root=f"{marker} Active customers chart."),
            service=dashboard_service,
        ),
        "data_model": CreateDashboardDataModelRequest(
            name=f"{namespace}_data_model",
            description=Markdown(root=f"{marker} Customer analytics model."),
            service=dashboard_service,
            dataModelType=DataModelType.SupersetDataModel,
            columns=[
                Column(name="customer_id", dataType=DataType.BIGINT),
                Column(name="active_orders", dataType=DataType.INT),
            ],
        ),
        "dashboard": CreateDashboardRequest(
            name=f"{namespace}_dashboard",
            description=Markdown(root=f"{marker} Customer analytics dashboard."),
            service=dashboard_service,
            charts=[chart_fqn],
            dataModels=[data_model_fqn],
        ),
        "ml_model": CreateMlModelRequest(
            name=f"{namespace}_churn_model",
            description=Markdown(root=f"{marker} Demo churn model."),
            service=parents["ml_model_service"],
            algorithm="logistic_regression",
            mlFeatures=[
                MlFeature(name="customer_age", dataType=FeatureType.numerical),
                MlFeature(name="segment", dataType=FeatureType.categorical),
            ],
            mlHyperParameters=[MlHyperParameter(name="regularization", value="0.1")],
            target="will_churn",
        ),
        "pipeline": CreatePipelineRequest(
            name=f"{namespace}_customer_pipeline",
            description=Markdown(root=f"{marker} Demo customer pipeline."),
            service=parents["pipeline_service"],
            tasks=[
                Task(name="extract", downstreamTasks=["transform"]),
                Task(name="transform", downstreamTasks=["publish"]),
                Task(name="publish"),
            ],
        ),
        "pipeline_status": PipelineStatus(
            timestamp=STATUS_TIMESTAMP,
            executionStatus=StatusType.Successful,
            executionId=f"{namespace}-demo-run",
            taskStatus=[
                TaskStatus(name=name, executionStatus=StatusType.Successful)
                for name in ("extract", "transform", "publish")
            ],
        ),
        "query": CreateQueryRequest(
            name=f"{namespace}_active_customers",
            description=Markdown(root=f"{marker} Demo analytics query."),
            service=parents["database_service"],
            query="SELECT customer_id FROM customers WHERE is_active = TRUE",
        ),
        "search_index": CreateSearchIndexRequest(
            name=f"{namespace}_customers_index",
            description=Markdown(root=f"{marker} Demo customer search index."),
            service=parents["search_service"],
            fields=[
                SearchIndexField(name="customer_name", dataType=SearchDataType.TEXT),
                SearchIndexField(name="customer_id", dataType=SearchDataType.LONG),
            ],
        ),
    }


def run_scenario(namespace: str, parents: Mapping[str, str]) -> None:
    """Create analytics entities and demonstrate pipeline status helpers."""
    requests = build_requests(namespace, parents)
    marker = ownership_marker(namespace)
    dashboard_service = f"{namespace}_dashboard_service"
    fqns = {
        "service": dashboard_service,
        "chart": f"{dashboard_service}.{namespace}_chart",
        "data_model": f"{dashboard_service}.model.{namespace}_data_model",
        "dashboard": f"{dashboard_service}.{namespace}_dashboard",
        "ml_model": f"{parents['ml_model_service']}.{namespace}_churn_model",
        "pipeline": f"{parents['pipeline_service']}.{namespace}_customer_pipeline",
        "query": f"{parents['database_service']}.{namespace}_active_customers",
        "search_index": f"{parents['search_service']}.{namespace}_customers_index",
    }

    entities = [
        owned_upsert(DashboardServices, fqns["service"], requests["service"], marker),
        owned_upsert(Charts, fqns["chart"], requests["chart"], marker),
        owned_upsert(
            DashboardDataModels,
            fqns["data_model"],
            requests["data_model"],
            marker,
        ),
        owned_upsert(Dashboards, fqns["dashboard"], requests["dashboard"], marker),
        owned_upsert(MLModels, fqns["ml_model"], requests["ml_model"], marker),
        owned_upsert(Pipelines, fqns["pipeline"], requests["pipeline"], marker),
    ]

    Pipelines.add_pipeline_status(fqns["pipeline"], requests["pipeline_status"])
    Pipelines.list_pipeline_statuses(
        fqns["pipeline"],
        start_ts=STATUS_TIMESTAMP - 1,
        end_ts=STATUS_TIMESTAMP + 1,
        limit=10,
    )

    entities.extend(
        [
            owned_upsert(Queries, fqns["query"], requests["query"], marker),
            owned_upsert(
                SearchIndexes,
                fqns["search_index"],
                requests["search_index"],
                marker,
            ),
        ]
    )
    for entity in entities:
        print(f"ready fqn={model_str(entity.fullyQualifiedName)} id={model_str(entity.id)}")


def main() -> int:
    try:
        namespace, parents = validate_environment()
        configure()
        try:
            run_scenario(namespace, parents)
        finally:
            reset()
    except (ValueError, RuntimeError) as exc:
        print(f"analytics scenario failed: {exc}")
        return 1
    except Exception as exc:
        print(f"analytics scenario failed: {type(exc).__name__}")
        return 1
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
