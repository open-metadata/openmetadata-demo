"""Offline contracts for scheduling an existing Test Suite with SDK 2.0.7.2."""

import json
import subprocess
import sys
from importlib.metadata import version
from pathlib import Path
from unittest.mock import Mock

import pytest
import test_suite_pipeline as example
from metadata.generated.schema.entity.services.connections.metadata.openMetadataConnection import (  # noqa: E501
    OpenMetadataConnection,
)
from metadata.generated.schema.entity.services.ingestionPipelines.ingestionPipeline import (
    AirflowConfig,
    IngestionPipeline,
    PipelineType,
)
from metadata.generated.schema.tests.testSuite import TestSuite as Suite
from metadata.generated.schema.type.entityReference import EntityReference
from metadata.ingestion.ometa.ometa_api import OpenMetadata
from pydantic import ValidationError

SUITE_ID = "11111111-1111-1111-1111-111111111111"
PIPELINE_ID = "22222222-2222-2222-2222-222222222222"
TABLE_FQN = 'warehouse.analytics.public."orders.daily"'
SUITE_FQN = f"{TABLE_FQN}.testSuite"


@pytest.fixture
def suite() -> Suite:
    return Suite(
        id=SUITE_ID,
        name=SUITE_FQN,
        fullyQualifiedName=SUITE_FQN,
        basic=True,
        basicEntityReference=EntityReference(
            id="33333333-3333-3333-3333-333333333333",
            type="table",
            fullyQualifiedName=TABLE_FQN,
        ),
    )


@pytest.fixture
def pipeline(suite: Suite) -> IngestionPipeline:
    request = example.build_pipeline_request(suite, "daily_dq", AirflowConfig())
    return IngestionPipeline(
        id=PIPELINE_ID,
        fullyQualifiedName=f"{SUITE_FQN}.daily_dq",
        **request.model_dump(),
    )


def test_models_use_the_exact_customer_version(suite: Suite) -> None:
    assert version("openmetadata-ingestion") == "2.0.7.2"
    request = example.build_pipeline_request(
        suite, "daily_dq", AirflowConfig(scheduleInterval="0 6 * * *", pipelineTimezone="UTC")
    )
    payload = json.loads(request.model_dump_json())
    assert payload["pipelineType"] == "TestSuite"
    assert payload["service"]["id"] == SUITE_ID
    assert payload["service"]["type"] == "testSuite"
    assert payload["sourceConfig"]["config"]["entityFullyQualifiedName"] == TABLE_FQN
    assert payload["sourceConfig"]["config"].get("testCases") is None
    assert payload["airflowConfig"]["scheduleInterval"] == "0 6 * * *"
    assert payload["airflowConfig"]["pipelineTimezone"] == "UTC"
    assert request.airflowConfig.pausePipeline is False


@pytest.mark.parametrize("missing_field", ["id", "fullyQualifiedName", "basicEntityReference"])
def test_incomplete_suite_is_rejected_before_writing(suite: Suite, missing_field: str) -> None:
    setattr(suite, missing_field, None)
    metadata = Mock(spec=OpenMetadata)
    metadata.get_by_name.return_value = suite

    with pytest.raises(ValueError, match="Test Suite"):
        example.configure_pipeline(metadata, SUITE_FQN, "daily_dq", AirflowConfig())
    metadata.create_or_update.assert_not_called()
    metadata.patch.assert_not_called()


def test_logical_suite_is_rejected(suite: Suite) -> None:
    suite.basic = False
    with pytest.raises(ValueError, match="executable"):
        example.build_pipeline_request(suite, "daily_dq", AirflowConfig())


def test_missing_suite_is_rejected() -> None:
    metadata = Mock(spec=OpenMetadata)
    metadata.get_by_name.return_value = None
    with pytest.raises(ValueError, match="not found"):
        example.configure_pipeline(metadata, SUITE_FQN, "daily_dq", AirflowConfig())
    metadata.create_or_update.assert_not_called()


def test_create_uses_stable_fqn_and_preserves_quoted_names(suite: Suite) -> None:
    metadata = Mock(spec=OpenMetadata)
    metadata.get_by_name.side_effect = [suite, None]
    example.configure_pipeline(metadata, SUITE_FQN, "daily.dq", AirflowConfig())

    assert metadata.get_by_name.call_args.kwargs["fqn"] == f'{SUITE_FQN}."daily.dq"'
    request = metadata.create_or_update.call_args.kwargs["data"]
    assert request.name.root == "daily.dq"
    metadata.patch.assert_not_called()


def test_schedule_patch_preserves_all_other_settings(
    suite: Suite, pipeline: IngestionPipeline
) -> None:
    pipeline.airflowConfig = AirflowConfig(
        scheduleInterval="0 1 * * *",
        retries=4,
        pausePipeline=True,
        pipelineTimezone="America/Toronto",
    )
    pipeline.sourceConfig.config.testCases = ["important_check"]
    pipeline.processingEngine = EntityReference(
        id="44444444-4444-4444-4444-444444444444", type="processingEngine"
    )
    original = pipeline.model_dump(mode="json")
    metadata = OpenMetadata(
        OpenMetadataConnection(hostPort="http://localhost:8585/api", enableVersionValidation=False)
    )
    metadata.client = Mock()
    metadata.get_by_name = Mock(side_effect=[suite, pipeline])
    changed = pipeline.model_copy(deep=True)
    changed.airflowConfig.scheduleInterval = "0 6 * * *"
    metadata.client.patch.return_value = changed.model_dump(mode="json")

    updated = example.configure_pipeline(
        metadata,
        SUITE_FQN,
        "daily_dq",
        AirflowConfig(scheduleInterval="0 6 * * *"),
    )

    assert updated.id == pipeline.id
    assert pipeline.model_dump(mode="json") == original
    assert updated.airflowConfig.retries == 4
    assert updated.airflowConfig.pausePipeline is True
    assert updated.airflowConfig.pipelineTimezone == "America/Toronto"
    assert updated.sourceConfig.model_dump(mode="json") == original["sourceConfig"]
    assert updated.processingEngine == pipeline.processingEngine
    assert metadata.client.patch.call_args.kwargs["path"] == (
        f"/services/ingestionPipelines/{PIPELINE_ID}"
    )
    patch = json.loads(metadata.client.patch.call_args.kwargs["data"])
    assert patch == [
        {"op": "replace", "path": "/airflowConfig/scheduleInterval", "value": "0 6 * * *"}
    ]
    metadata.client.put.assert_not_called()
    metadata.close()


def test_unchanged_schedule_returns_existing_pipeline(suite: Suite, pipeline: IngestionPipeline):
    metadata = Mock(spec=OpenMetadata)
    metadata.get_by_name.side_effect = [suite, pipeline]
    metadata.patch.return_value = None
    assert example.configure_pipeline(metadata, SUITE_FQN, "daily_dq", AirflowConfig()) is pipeline
    assert metadata.patch.call_args.kwargs["skip_on_failure"] is False


def test_patch_failure_is_not_reported_as_success(suite: Suite, pipeline: IngestionPipeline):
    metadata = Mock(spec=OpenMetadata)
    metadata.get_by_name.side_effect = [suite, pipeline]
    metadata.patch.side_effect = RuntimeError("schedule update denied")
    with pytest.raises(RuntimeError, match="schedule update denied"):
        example.configure_pipeline(metadata, SUITE_FQN, "daily_dq", AirflowConfig())


def test_client_setup_failure_exits_cleanly(monkeypatch, capsys) -> None:
    monkeypatch.setenv("OPENMETADATA_HOST", "https://metadata.example.com/api")
    monkeypatch.setenv("OPENMETADATA_JWT_TOKEN", "test-token")
    monkeypatch.setattr(sys, "argv", ["example", "--test-suite-fqn", SUITE_FQN])
    monkeypatch.setattr(
        example, "OpenMetadata", Mock(side_effect=RuntimeError("server unreachable"))
    )
    assert example.main() == 1
    assert "server unreachable" in capsys.readouterr().err


@pytest.mark.parametrize("wrong_type", [True, False])
def test_pipeline_collision_is_rejected(suite: Suite, pipeline: IngestionPipeline, wrong_type):
    if wrong_type:
        pipeline.pipelineType = PipelineType.metadata
    else:
        pipeline.service.id = "55555555-5555-5555-5555-555555555555"
    metadata = Mock(spec=OpenMetadata)
    metadata.get_by_name.side_effect = [suite, pipeline]
    with pytest.raises(ValueError, match="does not belong"):
        example.configure_pipeline(metadata, SUITE_FQN, "daily_dq", AirflowConfig())
    metadata.patch.assert_not_called()


@pytest.mark.parametrize(
    ("trigger", "deploy_code", "expected_actions"),
    [(False, 200, ["deploy"]), (True, 200, ["deploy", "trigger"]), (True, 503, ["deploy"])],
)
def test_cli_deploys_before_optional_trigger(
    monkeypatch, pipeline: IngestionPipeline, trigger: bool, deploy_code: int, expected_actions
) -> None:
    monkeypatch.setenv("OPENMETADATA_HOST", "https://metadata.example.com/api")
    monkeypatch.setenv("OPENMETADATA_JWT_TOKEN", "test-token")
    args = ["example", "--test-suite-fqn", SUITE_FQN]
    if trigger:
        args.append("--trigger")
    monkeypatch.setattr(sys, "argv", args)
    metadata = Mock(spec=OpenMetadata)
    metadata.client = Mock()
    metadata.client.post.side_effect = [
        {"code": deploy_code, "platform": "Argo", "reason": "orchestrator response"},
        {"code": 200, "platform": "Argo", "runId": "run-123"},
    ]
    monkeypatch.setattr(example, "OpenMetadata", Mock(return_value=metadata))
    configure = Mock(return_value=pipeline)
    monkeypatch.setattr(example, "configure_pipeline", configure)

    assert example.main() == (0 if deploy_code == 200 else 1)
    config = configure.call_args.kwargs["airflow_config"]
    assert config.scheduleInterval == "0 6 * * *"
    assert config.pipelineTimezone == "UTC"
    assert [call.args[0] for call in metadata.client.post.call_args_list] == [
        f"/services/ingestionPipelines/{action}/{PIPELINE_ID}" for action in expected_actions
    ]
    metadata.close.assert_called_once()


def test_disabled_orchestrator_is_not_success() -> None:
    metadata = Mock(spec=OpenMetadata)
    metadata.client = Mock()
    metadata.client.post.return_value = {"code": 200, "reason": "Pipeline Client Disabled"}
    with pytest.raises(ValidationError, match="platform"):
        example.pipeline_action(metadata, PIPELINE_ID, "deploy")


def test_import_cannot_open_sockets() -> None:
    script = Path(__file__).parents[1] / "test_suite_pipeline.py"
    probe = """
import runpy
import sys

def deny_socket(event, _args):
    if event in {"socket.connect", "socket.bind"}:
        raise RuntimeError(f"network attempted during import: {event}")

sys.addaudithook(deny_socket)
runpy.run_path(sys.argv[1], run_name="import_probe")
"""
    result = subprocess.run(
        [sys.executable, "-c", probe, str(script)], capture_output=True, text=True, check=False
    )
    assert result.returncode == 0, result.stderr
