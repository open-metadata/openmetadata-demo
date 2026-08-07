"""Create demo identities and read glossary relation settings."""

from __future__ import annotations

import os
import re
from collections.abc import Mapping
from typing import Any

from metadata.generated.schema.api.teams.createTeam import CreateTeamRequest
from metadata.generated.schema.api.teams.createUser import CreateUserRequest
from metadata.generated.schema.entity.teams.team import TeamType
from metadata.generated.schema.type.basic import Markdown
from metadata.generated.schema.type.entityReference import EntityReference
from metadata.ingestion.ometa.utils import model_str
from metadata.sdk import Settings, Teams, Users, configure, reset

NAMESPACE_PATTERN = re.compile(r"^[a-z][a-z0-9_]{2,31}$")
SCENARIO = "identity-and-settings"
REQUIRED_ENV = (
    "OPENMETADATA_HOST",
    "OPENMETADATA_JWT_TOKEN",
    "OPENMETADATA_DEMO_NAMESPACE",
    "OPENMETADATA_DEMO_USER_EMAIL",
)


def ownership_marker(namespace: str) -> str:
    return f"[openmetadata-demo:{namespace}:{SCENARIO}]"


def validate_environment(
    environ: Mapping[str, str] | None = None,
) -> tuple[str, str]:
    values = os.environ if environ is None else environ
    missing = [name for name in REQUIRED_ENV if not values.get(name)]
    if missing:
        raise ValueError(f"Missing required environment variables: {', '.join(missing)}")
    namespace = values["OPENMETADATA_DEMO_NAMESPACE"]
    if not NAMESPACE_PATTERN.fullmatch(namespace):
        raise ValueError("OPENMETADATA_DEMO_NAMESPACE must match ^[a-z][a-z0-9_]{2,31}$")
    return namespace, values["OPENMETADATA_DEMO_USER_EMAIL"]


def owned_upsert(
    facade: Any,
    fqn: str,
    request: Any,
    marker: str,
) -> Any:
    """PUT an absent or exactly owned identity; refuse foreign collisions."""
    existing = facade.retrieve_by_name(fqn, nullable=True)
    description = model_str(getattr(existing, "description", "")) if existing else ""
    if existing is not None and marker not in description:
        raise RuntimeError(f"Refusing to overwrite foreign entity: {fqn}")
    return facade.create(request)


def build_requests(namespace: str, email: str) -> dict[str, Any]:
    """Build both identity requests before any mutation."""
    marker = ownership_marker(namespace)
    return {
        "team": CreateTeamRequest(
            name=f"{namespace}_demo_team",
            displayName="OpenMetadata Demo Team",
            description=Markdown(root=f"{marker} Demo team."),
            teamType=TeamType.Group,
            isJoinable=False,
        ),
        "user": CreateUserRequest(
            name=f"{namespace}_demo_user",
            displayName="OpenMetadata Demo User",
            description=Markdown(root=f"{marker} Demo user."),
            email=email,
            isAdmin=False,
            isBot=False,
        ),
    }


def run_scenario(namespace: str, email: str) -> None:
    """Upsert owned identities, convert references, then read safe settings."""
    requests = build_requests(namespace, email)
    marker = ownership_marker(namespace)
    team_fqn = f"{namespace}_demo_team"
    user_fqn = f"{namespace}_demo_user"

    team = owned_upsert(Teams, team_fqn, requests["team"], marker)
    user = owned_upsert(Users, user_fqn, requests["user"], marker)
    team_reference = EntityReference(**Teams.to_entity_reference(team))
    user_reference = EntityReference(**Users.to_entity_reference(user))

    relation_settings = Settings.glossary_relation_settings()
    relation_types = Settings.glossary_relation_types()

    print(f"ready fqn={model_str(team.fullyQualifiedName)} id={model_str(team.id)}")
    print(f"ready fqn={model_str(user.fullyQualifiedName)} id={model_str(user.id)}")
    print(
        f"references={team_reference.type},{user_reference.type} "
        f"settings={len(relation_settings)} relation_types={len(relation_types)}"
    )


def main() -> int:
    try:
        namespace, email = validate_environment()
        configure()
        try:
            run_scenario(namespace, email)
        finally:
            reset()
    except (ValueError, RuntimeError) as exc:
        print(f"identity scenario failed: {exc}")
        return 1
    except Exception as exc:
        print(f"identity scenario failed: {type(exc).__name__}")
        return 1
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
