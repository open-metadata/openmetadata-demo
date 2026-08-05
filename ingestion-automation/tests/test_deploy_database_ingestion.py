"""Tests for the database ingestion deployment example."""

import pytest
from deploy_database_ingestion import (
    DeploymentConfig,
    build_pipeline_request,
    build_service_request,
    deploy_pipeline,
    trigger_pipeline,
)


def test_configuration_uses_environment_variables(monkeypatch) -> None:
    """Secrets and environment-specific connection values stay outside source."""
    monkeypatch.setenv("OPENMETADATA_HOST", "https://metadata.example.com/api")
    monkeypatch.setenv("OPENMETADATA_JWT_TOKEN", "test-token")
    monkeypatch.setenv("POSTGRES_PASSWORD", "test-password")
    monkeypatch.setenv("POSTGRES_HOST", "warehouse.example.com:5432")

    config = DeploymentConfig.from_environment()

    assert config.openmetadata_host == "https://metadata.example.com/api"
    assert config.jwt_token == "test-token"
    assert config.postgres_password == "test-password"
    assert config.postgres_host == "warehouse.example.com:5432"


def test_configuration_respects_an_explicit_empty_mapping(monkeypatch) -> None:
    """An injected empty environment should not read process credentials."""
    monkeypatch.setenv("OPENMETADATA_JWT_TOKEN", "test-token")
    monkeypatch.setenv("POSTGRES_PASSWORD", "test-password")

    with pytest.raises(RuntimeError, match="OPENMETADATA_JWT_TOKEN, POSTGRES_PASSWORD"):
        DeploymentConfig.from_environment({})


def test_builders_return_valid_2_0_service_and_pipeline_requests() -> None:
    """The customer-editable values should produce current generated models."""
    config = DeploymentConfig(
        openmetadata_host="http://localhost:8585/api",
        jwt_token="test-token",
        service_name="warehouse",
        postgres_host="postgres:5432",
        postgres_username="postgres",
        postgres_password="test-password",
        postgres_database="analytics",
    )

    service = build_service_request(config)
    pipeline = build_pipeline_request(
        service_id="11111111-1111-1111-1111-111111111111",
        service_name=config.service_name,
    )

    assert service.name.root == "warehouse"
    assert service.connection.config.database == "analytics"
    assert pipeline.name.root == "warehouse_metadata"
    assert str(pipeline.service.id.root) == "11111111-1111-1111-1111-111111111111"


def test_deploy_and_trigger_helpers_preserve_the_2_0_rest_contract() -> None:
    """REST workarounds should be explicit and independently testable."""
    calls = []

    class FakeClient:
        def post(self, path):
            calls.append(path)
            return {"code": 200}

    class FakeMetadata:
        client = FakeClient()

    pipeline_id = "22222222-2222-2222-2222-222222222222"

    assert deploy_pipeline(FakeMetadata(), pipeline_id) == {"code": 200}
    assert trigger_pipeline(FakeMetadata(), pipeline_id) == {"code": 200}
    assert calls == [
        f"/services/ingestionPipelines/deploy/{pipeline_id}",
        f"/services/ingestionPipelines/trigger/{pipeline_id}",
    ]
