"""Tests for the GraphQL-backed user updater connector."""

from pathlib import Path

import pytest
import requests
from metadata.config.common import load_config_file
from metadata.generated.schema.entity.domains.domain import Domain, DomainType
from metadata.generated.schema.entity.teams.user import User
from metadata.generated.schema.metadataIngestion.workflow import (
    OpenMetadataWorkflowConfig,
)
from metadata.generated.schema.type.entityReference import EntityReference
from metadata.generated.schema.type.entityReferenceList import EntityReferenceList
from metadata.generated.schema.type.personaPreferences import (
    AppMode,
    PersonaPreferences,
)
from metadata.ingestion.models.patch_request import build_patch

from connector.user_updater import UserUpdaterSource


class FakeMetadata:
    """Small metadata boundary used by the static connector tests."""

    def list_all_entities(self, **_):
        return []

    def health_check(self) -> bool:
        return True


def test_workflow_reads_server_and_graphql_settings_from_environment(
    monkeypatch,
) -> None:
    """No server address or token should be committed in the workflow."""
    monkeypatch.setenv("OPENMETADATA_HOST", "https://metadata.example.com/api")
    monkeypatch.setenv("OPENMETADATA_JWT_TOKEN", "test-token")
    monkeypatch.setenv("GRAPHQL_ENDPOINT", "https://graphql.example.com/query")

    config = load_config_file(Path("custom-graphql/user_updater.yaml"))

    OpenMetadataWorkflowConfig.model_validate(config)
    connection = config["source"]["serviceConnection"]["config"]
    assert connection["connectionOptions"]["graphql_endpoint"] == (
        "https://graphql.example.com/query"
    )
    assert config["workflowConfig"]["openMetadataServerConfig"]["hostPort"] == (
        "https://metadata.example.com/api"
    )
    assert config["workflowConfig"]["openMetadataServerConfig"]["securityConfig"] == {
        "jwtToken": "test-token"
    }


def test_source_uses_the_configured_graphql_endpoint(monkeypatch) -> None:
    """The source should pass customer configuration to its HTTP boundary."""
    monkeypatch.setenv("OPENMETADATA_HOST", "http://localhost:8585/api")
    monkeypatch.setenv("OPENMETADATA_JWT_TOKEN", "test-token")
    monkeypatch.setenv("GRAPHQL_ENDPOINT", "https://graphql.example.com/query")
    workflow = load_config_file(Path("custom-graphql/user_updater.yaml"))

    source = UserUpdaterSource.create(workflow["source"], FakeMetadata())

    assert source.graphql_endpoint == "https://graphql.example.com/query"


def test_source_fetches_graphql_records_through_a_mocked_http_boundary(
    monkeypatch,
) -> None:
    """GraphQL response handling should be testable without a fixture server."""
    calls = []

    class FakeResponse:
        def raise_for_status(self) -> None:
            return None

        def json(self) -> dict:
            return {
                "data": {
                    "users": [
                        {
                            "email": "analyst@example.com",
                            "displayName": "Data Analyst",
                            "domain": "Finance",
                        }
                    ]
                }
            }

    def fake_post(url: str, **kwargs):
        calls.append((url, kwargs))
        return FakeResponse()

    monkeypatch.setattr("connector.user_updater.requests.post", fake_post)
    monkeypatch.setenv("GRAPHQL_ENDPOINT", "https://graphql.example.com/query")
    workflow = load_config_file(Path("custom-graphql/user_updater.yaml"))
    source = UserUpdaterSource.create(workflow["source"], FakeMetadata())

    users = source._fetch_users_from_graphql()

    assert users[0]["email"] == "analyst@example.com"
    assert calls[0][0] == "https://graphql.example.com/query"
    assert calls[0][1]["timeout"] == 30


def test_graphql_failures_are_not_reported_as_empty_successes(monkeypatch) -> None:
    """An unavailable source should fail the run instead of returning zero records."""
    monkeypatch.setattr(
        "connector.user_updater.requests.post",
        lambda *_args, **_kwargs: (_ for _ in ()).throw(requests.ConnectionError("offline")),
    )
    monkeypatch.setenv("GRAPHQL_ENDPOINT", "https://graphql.example.com/query")
    workflow = load_config_file(Path("custom-graphql/user_updater.yaml"))
    source = UserUpdaterSource.create(workflow["source"], FakeMetadata())

    with pytest.raises(RuntimeError, match="GraphQL request failed"):
        list(source._iter())


def test_source_builds_a_targeted_patch_for_a_changed_existing_user(monkeypatch) -> None:
    """The patch plan should preserve every user field it does not own."""
    monkeypatch.setenv("OPENMETADATA_HOST", "http://localhost:8585/api")
    monkeypatch.setenv("OPENMETADATA_JWT_TOKEN", "test-token")
    monkeypatch.setenv("GRAPHQL_ENDPOINT", "http://localhost:4000/graphql")
    workflow = load_config_file(Path("custom-graphql/user_updater.yaml"))
    source = UserUpdaterSource.create(workflow["source"], FakeMetadata())
    source.domains = [
        Domain(
            id="11111111-1111-1111-1111-111111111111",
            domainType=DomainType.Aggregate,
            name="Finance",
            fullyQualifiedName="Finance",
            description="Finance domain",
        )
    ]
    source.users = [
        User(
            id="22222222-2222-2222-2222-222222222222",
            name="analyst",
            email="analyst@example.com",
            displayName="Old Display Name",
            externalId="identity-provider-42",
            scimUserName="scim-analyst",
            defaultPersona=EntityReference(
                id="33333333-3333-3333-3333-333333333333",
                type="persona",
                fullyQualifiedName="Data Analyst",
            ),
            personaPreferences=[
                PersonaPreferences(
                    personaId="33333333-3333-3333-3333-333333333333",
                    personaName="Data Analyst",
                    appMode=AppMode.AI,
                )
            ],
        )
    ]

    request = source._build_user_update(
        {
            "email": "analyst@example.com",
            "displayName": "Data Analyst",
            "domain": "Finance",
        }
    )

    assert request is not None
    original = request.original_entity
    destination = request.new_entity
    assert destination.displayName == "Data Analyst"
    assert str(destination.domains.root[0].fullyQualifiedName) == "Finance"
    assert destination.externalId == original.externalId == "identity-provider-42"
    assert destination.scimUserName == original.scimUserName == "scim-analyst"
    assert destination.defaultPersona == original.defaultPersona
    assert destination.personaPreferences == original.personaPreferences
    patch = build_patch(
        source=original,
        destination=destination,
        allowed_fields={"displayName": True, "domains": True},
        restrict_update_fields=["displayName"],
        override_metadata=request.override_metadata,
        skip_on_failure=False,
    )
    assert patch is not None
    assert {operation["path"] for operation in patch.patch} == {"/displayName", "/domains"}


def test_source_applies_only_display_name_and_domains_through_the_sdk(monkeypatch) -> None:
    """The source should bypass the unsupported bulk-user sink route."""
    calls = []

    class UpdatingMetadata(FakeMetadata):
        def patch(self, **kwargs):
            calls.append(kwargs)
            return kwargs["destination"]

    monkeypatch.setenv("GRAPHQL_ENDPOINT", "http://localhost:4000/graphql")
    workflow = load_config_file(Path("custom-graphql/user_updater.yaml"))
    source = UserUpdaterSource.create(workflow["source"], UpdatingMetadata())
    source.domains = [
        Domain(
            id="11111111-1111-1111-1111-111111111111",
            domainType=DomainType.Aggregate,
            name="Finance",
            fullyQualifiedName="Finance",
            description="Finance domain",
        )
    ]
    source.users = [
        User(
            id="22222222-2222-2222-2222-222222222222",
            name="analyst",
            email="analyst@example.com",
            displayName="Old Display Name",
        )
    ]
    monkeypatch.setattr(
        source,
        "_fetch_users_from_graphql",
        lambda: [
            {
                "email": "analyst@example.com",
                "displayName": "Data Analyst",
                "domain": "Finance",
            }
        ],
    )

    assert list(source._iter()) == []
    assert len(calls) == 1
    assert calls[0]["allowed_fields"] == {"displayName": True, "domains": True}
    assert calls[0]["override_metadata"] is True
    assert calls[0]["skip_on_failure"] is False
    assert calls[0]["destination"].displayName == "Data Analyst"


def test_unknown_graphql_domain_does_not_clear_existing_assignments(monkeypatch) -> None:
    """A source typo must become a record error instead of a destructive update."""
    monkeypatch.setenv("GRAPHQL_ENDPOINT", "http://localhost:4000/graphql")
    workflow = load_config_file(Path("custom-graphql/user_updater.yaml"))
    source = UserUpdaterSource.create(workflow["source"], FakeMetadata())
    source.users = [
        User(
            id="22222222-2222-2222-2222-222222222222",
            name="analyst",
            email="analyst@example.com",
            displayName="Data Analyst",
            domains=EntityReferenceList(
                root=[
                    EntityReference(
                        id="11111111-1111-1111-1111-111111111111",
                        type="domain",
                        fullyQualifiedName="Finance",
                    )
                ]
            ),
        )
    ]

    with pytest.raises(ValueError, match="Unknown OpenMetadata domain: Financ"):
        source._build_user_update(
            {
                "email": "analyst@example.com",
                "displayName": "Data Analyst",
                "domain": "Financ",
            }
        )

    assert str(source.users[0].domains.root[0].fullyQualifiedName) == "Finance"


def test_prepare_and_connection_check_use_mocked_openmetadata_boundaries(monkeypatch) -> None:
    """Both OpenMetadata calls should remain testable without a live server."""
    calls = []

    class TrackingMetadata(FakeMetadata):
        def list_all_entities(self, **kwargs):
            calls.append(("list", kwargs))
            return []

        def health_check(self) -> bool:
            calls.append(("health", {}))
            return True

    class FakeResponse:
        def raise_for_status(self) -> None:
            return None

        def json(self) -> dict:
            return {"data": {"users": []}}

    monkeypatch.setattr(
        "connector.user_updater.requests.post",
        lambda *_args, **_kwargs: FakeResponse(),
    )
    monkeypatch.setenv("GRAPHQL_ENDPOINT", "https://graphql.example.com/query")
    workflow = load_config_file(Path("custom-graphql/user_updater.yaml"))
    source = UserUpdaterSource.create(workflow["source"], TrackingMetadata())

    source.prepare()
    source.test_connection()

    assert [call[0] for call in calls] == ["list", "list", "health"]
