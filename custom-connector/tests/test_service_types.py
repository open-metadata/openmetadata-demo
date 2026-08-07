"""Contract tests for every non-database custom connector scenario."""

from importlib import import_module

import pytest
from metadata.generated.schema.api.data.createPipeline import CreatePipelineRequest
from metadata.generated.schema.entity.data.container import Container
from metadata.generated.schema.entity.data.topic import Topic
from metadata.generated.schema.type.entityReference import EntityReference


class MockMetadata:
    """Return deterministic persisted entities without contacting OpenMetadata."""

    def get_by_name(self, entity: type, fqn: str):
        entity_name = fqn.rsplit(".", maxsplit=1)[-1]
        service = EntityReference(
            id="00000000-0000-0000-0000-000000000002",
            type="messagingService" if entity is Topic else "storageService",
        )
        if entity is Topic:
            return Topic(
                id="00000000-0000-0000-0000-000000000001",
                name=entity_name,
                fullyQualifiedName=fqn,
                service=service,
                partitions=1,
            )
        if entity is Container:
            return Container(
                id="00000000-0000-0000-0000-000000000001",
                name=entity_name,
                fullyQualifiedName=fqn,
                service=service,
            )
        raise AssertionError(f"unexpected metadata lookup for {entity.__name__}")


SCENARIOS = [
    (
        "dashboard",
        "CustomDashboard",
        "DashboardMetadata",
        "CustomDashboardSource",
        [
            "CreateDashboardServiceRequest",
            "CreateChartRequest",
            "CreateChartRequest",
            "CreateDashboardDataModelRequest",
            "CreateDashboardRequest",
        ],
    ),
    (
        "drive",
        "CustomDrive",
        "DriveMetadata",
        "CustomDriveSource",
        [
            "CreateDriveServiceRequest",
            "CreateDirectoryRequest",
            "CreateFileRequest",
            "CreateSpreadsheetRequest",
            "CreateWorksheetRequest",
        ],
    ),
    (
        "messaging",
        "CustomMessaging",
        "MessagingMetadata",
        "CustomMessagingSource",
        [
            "CreateMessagingServiceRequest",
            "CreateTopicRequest",
            "CreateTopicRequest",
            "Barrier",
            "OMetaTopicSampleData",
            "OMetaTopicSampleData",
        ],
    ),
    (
        "mlmodel",
        "CustomMlModel",
        "MlModelMetadata",
        "CustomMlModelSource",
        ["CreateMlModelServiceRequest", "CreateMlModelRequest"],
    ),
    (
        "pipeline",
        "CustomPipeline",
        "PipelineMetadata",
        "CustomPipelineSource",
        [
            "CreatePipelineServiceRequest",
            "CreatePipelineRequest",
            "Barrier",
            "OMetaPipelineStatus",
        ],
    ),
    (
        "search",
        "CustomSearch",
        "SearchMetadata",
        "CustomSearchSource",
        [
            "CreateSearchServiceRequest",
            "CreateSearchIndexRequest",
            "CreateSearchIndexRequest",
        ],
    ),
    (
        "storage",
        "CustomStorage",
        "StorageMetadata",
        "CustomStorageSource",
        [
            "CreateStorageServiceRequest",
            "CreateContainerRequest",
            "CreateContainerRequest",
        ],
    ),
]


def source_config(
    module_name: str,
    connection_type: str,
    source_type: str,
    class_name: str,
) -> dict:
    """Build the source portion shared by the runnable YAML examples."""
    return {
        "type": f"custom-{module_name}",
        "serviceName": f"custom_{module_name}_demo",
        "serviceConnection": {
            "config": {
                "type": connection_type,
                "sourcePythonClass": (f"openmetadata_demo_connectors.{module_name}.{class_name}"),
            }
        },
        "sourceConfig": {"config": {"type": source_type}},
    }


@pytest.mark.parametrize(
    (
        "module_name",
        "connection_type",
        "source_type",
        "class_name",
        "expected_records",
    ),
    SCENARIOS,
)
def test_connector_emits_expected_records_without_network_access(
    module_name: str,
    connection_type: str,
    source_type: str,
    class_name: str,
    expected_records: list[str],
) -> None:
    """Each scenario should emit its complete catalog in dependency order."""
    module = import_module(f"openmetadata_demo_connectors.{module_name}")
    source_class = getattr(module, class_name)
    source = source_class.create(
        source_config(module_name, connection_type, source_type, class_name),
        metadata=MockMetadata(),
    )

    records = [result.right for result in source._iter()]

    assert [type(record).__name__ for record in records] == expected_records


@pytest.mark.parametrize("module_name", ["messaging", "pipeline"])
def test_dependent_records_are_emitted_after_a_barrier(module_name: str) -> None:
    """Sample data and execution status must follow persistence of their parent entity."""
    scenario = next(item for item in SCENARIOS if item[0] == module_name)
    _, connection_type, source_type, class_name, expected_records = scenario
    module = import_module(f"openmetadata_demo_connectors.{module_name}")
    source_class = getattr(module, class_name)
    records = [
        result.right
        for result in source_class.create(
            source_config(module_name, connection_type, source_type, class_name),
            metadata=MockMetadata(),
        )._iter()
    ]

    record_types = [type(record).__name__ for record in records]
    barrier_index = record_types.index("Barrier")
    assert record_types == expected_records
    assert barrier_index < len(record_types) - 1


def test_pipeline_tasks_point_to_their_actual_downstream_tasks() -> None:
    """The example graph should run extract, then transform, then load."""
    module = import_module("openmetadata_demo_connectors.pipeline")
    source = module.CustomPipelineSource.create(
        source_config("pipeline", "CustomPipeline", "PipelineMetadata", "CustomPipelineSource"),
        metadata=MockMetadata(),
    )

    pipeline = next(
        result.right for result in source._iter() if isinstance(result.right, CreatePipelineRequest)
    )

    assert {str(task.name): task.downstreamTasks for task in pipeline.tasks} == {
        "extract": ["transform"],
        "transform": ["load"],
        "load": [],
    }


@pytest.mark.parametrize("module_name", ["messaging", "storage"])
def test_dependent_records_fail_when_their_parent_lookup_fails(module_name: str) -> None:
    """A missing persisted parent must not silently produce an incomplete catalog."""

    class MissingMetadata:
        def get_by_name(self, **_):
            return None

    scenario = next(item for item in SCENARIOS if item[0] == module_name)
    _, connection_type, source_type, class_name, _ = scenario
    module = import_module(f"openmetadata_demo_connectors.{module_name}")
    source_class = getattr(module, class_name)
    source = source_class.create(
        source_config(module_name, connection_type, source_type, class_name),
        metadata=MissingMetadata(),
    )

    with pytest.raises(RuntimeError, match="persisted"):
        list(source._iter())
