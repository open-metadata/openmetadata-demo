"""Custom source that synchronizes existing OpenMetadata users from GraphQL."""

import traceback
from collections.abc import Iterable

import requests
from metadata.generated.schema.entity.domains.domain import Domain
from metadata.generated.schema.entity.services.connections.database.customDatabaseConnection import (  # noqa: E501
    CustomDatabaseConnection,
)
from metadata.generated.schema.entity.teams.user import User
from metadata.generated.schema.metadataIngestion.workflow import (
    Source as WorkflowSource,
)
from metadata.generated.schema.type.entityReference import EntityReference
from metadata.generated.schema.type.entityReferenceList import EntityReferenceList
from metadata.ingestion.api.models import Either, StackTraceError
from metadata.ingestion.api.steps import InvalidSourceException, Source
from metadata.ingestion.models.patch_request import PatchRequest
from metadata.ingestion.ometa.ometa_api import OpenMetadata
from metadata.ingestion.ometa.utils import model_str
from metadata.utils.logger import ingestion_logger

logger = ingestion_logger()


class UserUpdaterSource(Source):
    """Update existing users with display names and domains returned by GraphQL."""

    def __init__(self, config: WorkflowSource, metadata: OpenMetadata):
        super().__init__()
        self.config = config
        self.metadata = metadata
        options = config.serviceConnection.root.config.connectionOptions
        self.graphql_endpoint = (options.root or {}).get(
            "graphql_endpoint", "http://localhost:4000/"
        )
        self.domains: list[Domain] = []
        self.users: list[User] = []

    @classmethod
    def create(
        cls,
        config_dict: dict,
        metadata: OpenMetadata,
        pipeline_name: str | None = None,
    ) -> "UserUpdaterSource":
        """Validate workflow configuration and create the source."""
        config = WorkflowSource.model_validate(config_dict)
        connection = config.serviceConnection.root.config
        if not isinstance(connection, CustomDatabaseConnection):
            raise InvalidSourceException(f"Expected CustomDatabaseConnection, but got {connection}")
        return cls(config, metadata)

    def prepare(self) -> None:
        """Cache the OpenMetadata users and domains used for reconciliation."""
        self.domains = list(self.metadata.list_all_entities(entity=Domain))
        self.users = list(self.metadata.list_all_entities(entity=User, fields=["*"]))

    def _request_graphql(self, query: str) -> dict:
        """Run one GraphQL query and surface transport or protocol failures."""
        try:
            response = requests.post(
                self.graphql_endpoint,
                json={"query": query},
                headers={"Content-Type": "application/json"},
                timeout=30,
            )
            response.raise_for_status()
            payload = response.json()
        except (requests.RequestException, ValueError) as exc:
            raise RuntimeError(f"GraphQL request failed: {exc}") from exc
        if not isinstance(payload, dict):
            raise RuntimeError("GraphQL request failed: response was not an object")
        if payload.get("errors"):
            raise RuntimeError(f"GraphQL request failed: {payload['errors']}")
        return payload

    def _fetch_users_from_graphql(self) -> list[dict]:
        """Fetch the external user records."""
        payload = self._request_graphql(
            """
            {
              users {
                email
                displayName
                domain
              }
            }
            """
        )
        data = payload.get("data")
        users = data.get("users") if isinstance(data, dict) else None
        if not isinstance(users, list):
            raise RuntimeError("GraphQL request failed: data.users was not a list")
        return users

    def _find_domain_by_name(self, domain_name: str) -> EntityReference | None:
        """Return the matching OpenMetadata domain reference, if one exists."""
        for domain in self.domains:
            if model_str(domain.name).lower() == domain_name.lower():
                return EntityReference(
                    id=domain.id,
                    type="domain",
                    name=model_str(domain.name),
                    fullyQualifiedName=model_str(domain.fullyQualifiedName),
                )
        return None

    @staticmethod
    def _domain_ids(domains: EntityReferenceList | None) -> set[str]:
        """Normalize an optional domain list for change detection."""
        if not domains or not domains.root:
            return set()
        return {model_str(domain.id) for domain in domains.root}

    def _build_user_update(self, user_data: dict) -> PatchRequest | None:
        """Build a targeted patch plan only when the GraphQL values differ."""
        email = user_data["email"]
        existing_user = next(
            (user for user in self.users if model_str(user.email) == email),
            None,
        )
        if not existing_user:
            logger.warning("User %s does not exist in OpenMetadata", email)
            return None

        domain = self._find_domain_by_name(user_data["domain"])
        if not domain:
            raise ValueError(f"Unknown OpenMetadata domain: {user_data['domain']}")
        requested_domains = EntityReferenceList(root=[domain])
        display_name = user_data["displayName"]
        if model_str(existing_user.displayName) == display_name and self._domain_ids(
            existing_user.domains
        ) == self._domain_ids(requested_domains):
            return None

        destination = existing_user.model_copy(
            deep=True,
            update={
                "displayName": display_name,
                "domains": requested_domains,
            },
        )
        return PatchRequest(
            original_entity=existing_user,
            new_entity=destination,
            override_metadata=True,
        )

    def _apply_user_update(self, request: PatchRequest) -> User:
        """Apply only the two fields owned by this synchronization."""
        updated = self.metadata.patch(
            entity=User,
            source=request.original_entity,
            destination=request.new_entity,
            allowed_fields={"displayName": True, "domains": True},
            restrict_update_fields=["displayName"],
            override_metadata=request.override_metadata,
            skip_on_failure=False,
        )
        if not updated:
            user_name = model_str(request.original_entity.name)
            raise RuntimeError(f"OpenMetadata returned no updated user for {user_name}")
        return updated

    def _iter(self, *_, **__) -> Iterable[Either]:
        """Yield user updates produced from the GraphQL response."""
        for user_data in self._fetch_users_from_graphql():
            try:
                request = self._build_user_update(user_data)
                if request:
                    self.status.updated(self._apply_user_update(request))
            except (AttributeError, KeyError, RuntimeError, TypeError, ValueError) as exc:
                yield Either(
                    left=StackTraceError(
                        name=user_data.get("email", "unknown user"),
                        error=str(exc),
                        stackTrace=traceback.format_exc(),
                    )
                )

    def test_connection(self) -> None:
        """Check the GraphQL and OpenMetadata endpoints without changing data."""
        self._request_graphql("{ users { email } }")
        if not self.metadata.health_check():
            raise ConnectionError("OpenMetadata health check failed")

    def close(self) -> None:
        """The connector does not retain external resources."""
