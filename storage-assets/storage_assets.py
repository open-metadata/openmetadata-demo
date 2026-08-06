"""Create and navigate a storage hierarchy with public SDK facades."""

from __future__ import annotations

import os
import re
from collections.abc import Mapping
from typing import Any

from metadata.generated.schema.api.data.createContainer import CreateContainerRequest
from metadata.generated.schema.api.services.createStorageService import (
    CreateStorageServiceRequest,
)
from metadata.generated.schema.entity.services.storageService import StorageServiceType
from metadata.generated.schema.type.basic import Markdown
from metadata.generated.schema.type.entityReference import EntityReference
from metadata.ingestion.ometa.utils import model_str
from metadata.sdk import Containers, StorageServices, configure, reset

NAMESPACE_PATTERN = re.compile(r"^[a-z][a-z0-9_]{2,31}$")
SCENARIO = "storage-assets"
REQUIRED_ENV = (
    "OPENMETADATA_HOST",
    "OPENMETADATA_JWT_TOKEN",
    "OPENMETADATA_DEMO_NAMESPACE",
)


def ownership_marker(namespace: str) -> str:
    return f"[openmetadata-demo:{namespace}:{SCENARIO}]"


def validate_environment(environ: Mapping[str, str] | None = None) -> str:
    values = os.environ if environ is None else environ
    missing = [name for name in REQUIRED_ENV if not values.get(name)]
    if missing:
        raise ValueError(f"Missing required environment variables: {', '.join(missing)}")
    namespace = values["OPENMETADATA_DEMO_NAMESPACE"]
    if not NAMESPACE_PATTERN.fullmatch(namespace):
        raise ValueError("OPENMETADATA_DEMO_NAMESPACE must match ^[a-z][a-z0-9_]{2,31}$")
    return namespace


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


def build_requests(namespace: str) -> dict[str, Any]:
    """Build all requests before the first server mutation."""
    marker = ownership_marker(namespace)
    service_name = f"{namespace}_storage_service"
    return {
        "service": CreateStorageServiceRequest(
            name=service_name,
            description=Markdown(root=f"{marker} Demo storage service."),
            serviceType=StorageServiceType.CustomStorage,
        ),
        "root": CreateContainerRequest(
            name=f"{namespace}_exports",
            description=Markdown(root=f"{marker} Demo root container."),
            service=service_name,
            prefix="exports/",
        ),
        "child": CreateContainerRequest(
            name=f"{namespace}_daily_exports",
            description=Markdown(root=f"{marker} Demo child container."),
            service=service_name,
            prefix="exports/daily/",
        ),
    }


def _owned_description(entity: Any, marker: str, fqn: str) -> None:
    description = model_str(getattr(entity, "description", ""))
    if marker not in description:
        raise RuntimeError(f"Refusing to overwrite foreign entity: {fqn}")


def run_scenario(namespace: str) -> None:
    """Create service and containers before establishing their hierarchy."""
    requests = build_requests(namespace)
    marker = ownership_marker(namespace)
    service_fqn = f"{namespace}_storage_service"
    root_fqn = f"{service_fqn}.{namespace}_exports"
    temporary_child_fqn = f"{service_fqn}.{namespace}_daily_exports"
    nested_child_fqn = f"{root_fqn}.{namespace}_daily_exports"

    service = owned_upsert(
        StorageServices,
        service_fqn,
        requests["service"],
        marker,
    )
    root = owned_upsert(Containers, root_fqn, requests["root"], marker)

    child = Containers.retrieve_by_name(nested_child_fqn, nullable=True)
    if child is None:
        child = owned_upsert(
            Containers,
            temporary_child_fqn,
            requests["child"],
            marker,
        )
    else:
        _owned_description(child, marker, nested_child_fqn)

    parent = EntityReference(**Containers.to_entity_reference(root))
    Containers.set_parent(child.id, parent)
    Containers.list_children(root_fqn, limit=100, offset=0)
    Containers.list_ancestors(nested_child_fqn)

    for entity in (service, root, child):
        print(f"ready fqn={model_str(entity.fullyQualifiedName)} id={model_str(entity.id)}")


def main() -> int:
    try:
        namespace = validate_environment()
        configure()
        try:
            run_scenario(namespace)
        finally:
            reset()
    except (ValueError, RuntimeError) as exc:
        print(f"storage scenario failed: {exc}")
        return 1
    except Exception as exc:
        print(f"storage scenario failed: {type(exc).__name__}")
        return 1
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
