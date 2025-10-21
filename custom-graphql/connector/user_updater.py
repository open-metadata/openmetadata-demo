import traceback
from dataclasses import dataclass
from typing import Iterable, Optional

import requests
from metadata.generated.schema.entity.domains.domain import Domain
from metadata.generated.schema.entity.teams.user import User
from metadata.generated.schema.metadataIngestion.workflow import (
    Source as WorkflowSource,
)
from metadata.generated.schema.type.entityReference import EntityReference
from metadata.generated.schema.type.entityReferenceList import EntityReferenceList
from metadata.ingestion.api.models import Either, StackTraceError
from metadata.ingestion.api.steps import Source
from metadata.generated.schema.api.teams.createUser import CreateUserRequest
from metadata.ingestion.ometa.ometa_api import OpenMetadata
from metadata.ingestion.ometa.utils import model_str
from metadata.utils.logger import ingestion_logger

logger = ingestion_logger()


@dataclass
class UserUpdaterConfig:
    """Configuration for User Updater connector"""

    graphql_endpoint: str


class UserUpdaterSource(Source):
    """
    Custom connector that fetches user data from GraphQL server
    and updates OpenMetadata user entities with displayName and domain
    """

    def prepare(self):
        self.domains = list(
            self.metadata.list_all_entities(
                entity=Domain,
            )
        )
        self.users = list(
            self.metadata.list_all_entities(
                entity=User,
                fields=["*"]
            )
        )

    def __init__(self, config: WorkflowSource, metadata: OpenMetadata):
        super().__init__()
        self.config = config
        self.metadata = metadata

        # Extract our custom config from connectionOptions
        connection_options = self.config.serviceConnection.root.config.connectionOptions
        self.graphql_endpoint = connection_options.root.get(
            "graphql_endpoint", "http://localhost:4000"
        )

        self.domains = None
        self.users = None

    @classmethod
    def create(
        cls,
        config_dict: dict,
        metadata: OpenMetadata,
        pipeline_name: Optional[str] = None,
    ) -> "UserUpdaterSource":
        config: WorkflowSource = WorkflowSource.parse_obj(config_dict)
        return cls(config, metadata)

    def _fetch_users_from_graphql(self):
        """Fetch users from GraphQL server"""
        query = """
        {
            users {
                email
                displayName
                domain
            }
        }
        """

        try:
            response = requests.post(
                self.graphql_endpoint,
                json={"query": query},
                headers={"Content-Type": "application/json"},
                timeout=30,
            )
            response.raise_for_status()
            data = response.json()
            return data.get("data", {}).get("users", [])
        except Exception as e:
            logger.error(f"Failed to fetch users from GraphQL: {e}")
            return []

    def _find_domain_by_name(self, domain_name: str) -> Optional[EntityReference]:
        """Find domain entity by name and return as EntityReference"""
        try:
            # Try to find existing domain
            for domain in self.domains:
                if model_str(domain.name).lower() == domain_name.lower():
                    return EntityReference(
                        id=domain.id,
                        type="domain",
                        name=domain.name.root,
                        fullyQualifiedName=domain.fullyQualifiedName.root,
                    )
        except Exception as e:
            logger.debug(f"Error searching for domain {domain_name}: {e}")
        return None

    def _domains_changed(self, current_domains, new_domains) -> bool:
        """Check if domain lists are different"""
        # Handle None cases
        if current_domains is None and new_domains is None:
            return False
        if current_domains is None or new_domains is None:
            return True
        
        # Get domain IDs for comparison
        current_ids = set()
        if current_domains and current_domains.root:
            current_ids = {d.id.root for d in current_domains.root}
        
        new_ids = set()
        if new_domains and new_domains.root:
            new_ids = {d.id.root for d in new_domains.root}
        
        return current_ids != new_ids

    def _update_user_entity(self, user_data):
        """Check existing user and create CreateUserRequest only if displayName or domains need updates"""
        try:
            email = user_data["email"]
            display_name = user_data["displayName"]
            domain_name = user_data["domain"]
            
            # Find existing user
            existing_user = None
            try:
                for user in self.users:
                    if model_str(user.email) == email:
                        existing_user = user
                        break
            except Exception as e:
                logger.debug(f"Error searching for user {email}: {e}")
            
            if not existing_user:
                return f"User {email} not found in OpenMetadata"
            
            # Find domain reference
            domain_ref = self._find_domain_by_name(domain_name)
            new_domains = EntityReferenceList(root=[domain_ref]) if domain_ref else None

            # Check if updates are needed
            needs_update = False

            # Check displayName
            current_display_name = model_str(existing_user.displayName) if existing_user.displayName else None
            if current_display_name != display_name:
                needs_update = True

            # Check domains
            current_domains = existing_user.domains
            domains_changed = self._domains_changed(current_domains, new_domains)
            if domains_changed:
                needs_update = True

            if not needs_update:
                return f"User {email} is already up to date"

            # Create CreateUserRequest with updated fields, preserving existing data
            create_user_request = CreateUserRequest(
                name=model_str(existing_user.name),  # Keep existing name
                email=email,
                displayName=display_name,
                domains=[domain_ref.fullyQualifiedName] if domain_ref else [],
                # Preserve existing user fields
                description=existing_user.description,
                profile=existing_user.profile,
                timezone=existing_user.timezone,
                isBot=existing_user.isBot,
                isAdmin=existing_user.isAdmin,
                authenticationMechanism=existing_user.authenticationMechanism,
                teams=[team.id for team in existing_user.teams.root or []],
                roles=[role.id for role in existing_user.roles.root or []],
                personas=existing_user.personas,
            )

            return create_user_request

        except Exception as e:
            error_msg = f"Failed to process user {user_data.get('email', 'unknown')}: {e}"
            logger.error(error_msg)
            return error_msg


    def _iter(self) -> Iterable[Either]:
        """
        Main method that yields results for each user update
        """
        logger.info("Starting User Updater connector")

        # Fetch users from GraphQL
        users = self._fetch_users_from_graphql()

        if not users:
            yield Either(
                left=StackTraceError(
                    name="GraphQL Fetch Error",
                    error="No users found from GraphQL endpoint or failed to fetch",
                    stackTrace=traceback.format_exc(),
                )
            )
            return

        logger.info(f"Found {len(users)} users from GraphQL")

        # Process each user
        for user_data in users:
            try:
                result = self._update_user_entity(user_data)

                # If result is a CreateUserRequest, yield it as right
                if isinstance(result, CreateUserRequest):
                    yield Either(right=result)
                else:
                    # Handle different types of string messages
                    result_str = str(result)
                    if "already up to date" in result_str:
                        # Just log up-to-date users, don't yield as error
                        logger.info(result_str)
                    elif "not found" in result_str:
                        # Yield user not found as error
                        yield Either(
                            left=StackTraceError(
                                name="User Not Found",
                                error=result_str,
                                stackTrace=traceback.format_exc(),
                            )
                        )
                    else:
                        # Yield other messages as general info
                        yield Either(
                            left=StackTraceError(
                                name="User Processing Info",
                                error=result_str,
                                stackTrace=traceback.format_exc(),
                            )
                        )
            except Exception as e:
                yield Either(
                    left=StackTraceError(
                        name="User Processing Error",
                        error=f"Error processing user {user_data.get('email', 'unknown')}: {e}",
                        stackTrace=traceback.format_exc(),
                    )
                )

    def test_connection(self) -> None:
        """Test connection to both GraphQL endpoint and OpenMetadata"""
        try:
            # Test GraphQL connection
            response = requests.get(self.graphql_endpoint, timeout=10)
            response.raise_for_status()

            # Test OpenMetadata connection
            self.metadata.health_check()

        except Exception as e:
            raise ConnectionError(f"Connection test failed: {e}")

    def close(self):
        """Clean up resources"""
        pass
