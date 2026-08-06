"""Create a small database catalog with the public OpenMetadata SDK facades."""

from __future__ import annotations

import os
import re
from collections.abc import Mapping
from typing import Any

from metadata.generated.schema.api.data.createDatabase import CreateDatabaseRequest
from metadata.generated.schema.api.data.createDatabaseSchema import (
    CreateDatabaseSchemaRequest,
)
from metadata.generated.schema.api.data.createStoredProcedure import (
    CreateStoredProcedureRequest,
)
from metadata.generated.schema.api.data.createTable import CreateTableRequest
from metadata.generated.schema.api.services.createDatabaseService import (
    CreateDatabaseServiceRequest,
)
from metadata.generated.schema.entity.data.storedProcedure import (
    Language,
    StoredProcedureCode,
)
from metadata.generated.schema.entity.data.table import (
    Column,
    Constraint,
    DataType,
    TableData,
)
from metadata.generated.schema.entity.services.databaseService import (
    DatabaseServiceType,
)
from metadata.generated.schema.type.basic import Markdown
from metadata.ingestion.ometa.utils import model_str
from metadata.sdk import (
    Databases,
    DatabaseSchemas,
    DatabaseServices,
    StoredProcedures,
    Tables,
    configure,
    reset,
)

NAMESPACE_PATTERN = re.compile(r"^[a-z][a-z0-9_]{2,31}$")
SCENARIO = "catalog-assets"
REQUIRED_ENV = (
    "OPENMETADATA_HOST",
    "OPENMETADATA_JWT_TOKEN",
    "OPENMETADATA_DEMO_NAMESPACE",
)


def ownership_marker(namespace: str) -> str:
    """Return the marker used to distinguish demo-owned entities."""
    return f"[openmetadata-demo:{namespace}:{SCENARIO}]"


def validate_environment(environ: Mapping[str, str] | None = None) -> str:
    """Validate credentials and return the safe namespace."""
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
    """Create or PUT-update an entity only when this scenario owns it."""
    existing = facade.retrieve_by_name(fqn, nullable=True)
    description = model_str(getattr(existing, "description", "")) if existing else ""
    if existing is not None and marker not in description:
        raise RuntimeError(f"Refusing to overwrite foreign entity: {fqn}")
    return facade.create(request)


def build_requests(namespace: str) -> dict[str, Any]:
    """Build and validate every request before any server mutation."""
    marker = ownership_marker(namespace)
    service_name = f"{namespace}_database_service"
    database_fqn = f"{service_name}.{namespace}_database"
    schema_fqn = f"{database_fqn}.{namespace}_schema"

    return {
        "service": CreateDatabaseServiceRequest(
            name=service_name,
            description=Markdown(root=f"{marker} Demo database service."),
            serviceType=DatabaseServiceType.CustomDatabase,
        ),
        "database": CreateDatabaseRequest(
            name=f"{namespace}_database",
            description=Markdown(root=f"{marker} Demo database."),
            service=service_name,
        ),
        "schema": CreateDatabaseSchemaRequest(
            name=f"{namespace}_schema",
            description=Markdown(root=f"{marker} Demo schema."),
            database=database_fqn,
        ),
        "table": CreateTableRequest(
            name=f"{namespace}_customers",
            description=Markdown(root=f"{marker} Demo customer table."),
            databaseSchema=schema_fqn,
            columns=[
                Column(
                    name="customer_id",
                    dataType=DataType.BIGINT,
                    constraint=Constraint.PRIMARY_KEY,
                ),
                Column(name="customer_name", dataType=DataType.STRING),
                Column(name="is_active", dataType=DataType.BOOLEAN),
            ],
        ),
        "procedure": CreateStoredProcedureRequest(
            name=f"{namespace}_refresh_customers",
            description=Markdown(root=f"{marker} Demo stored procedure."),
            databaseSchema=schema_fqn,
            storedProcedureCode=StoredProcedureCode(
                language=Language.SQL,
                code="SELECT customer_id, customer_name FROM customers",
            ),
        ),
    }


def run_scenario(namespace: str) -> None:
    """Create parents first, then exercise focused table helpers."""
    requests = build_requests(namespace)
    marker = ownership_marker(namespace)
    service_fqn = f"{namespace}_database_service"
    database_fqn = f"{service_fqn}.{namespace}_database"
    schema_fqn = f"{database_fqn}.{namespace}_schema"
    table_fqn = f"{schema_fqn}.{namespace}_customers"
    procedure_fqn = f"{schema_fqn}.{namespace}_refresh_customers"

    entities = [
        owned_upsert(DatabaseServices, service_fqn, requests["service"], marker),
        owned_upsert(Databases, database_fqn, requests["database"], marker),
        owned_upsert(DatabaseSchemas, schema_fqn, requests["schema"], marker),
    ]
    table = owned_upsert(Tables, table_fqn, requests["table"], marker)
    entities.append(table)
    entities.append(
        owned_upsert(
            StoredProcedures,
            procedure_fqn,
            requests["procedure"],
            marker,
        )
    )

    updated_table = table.model_copy(deep=True)
    updated_table.description = Markdown(root=f"{marker} Updated demo customer table.")
    updated_table = Tables.update(updated_table)
    sample_data = TableData(
        columns=["customer_id", "customer_name", "is_active"],
        rows=[[1, "Ada", True], [2, "Grace", True]],
    )
    Tables.add_sample_data(updated_table.id, sample_data)
    Tables.get_sample_data(updated_table.id)

    for entity in entities:
        print(f"ready fqn={model_str(entity.fullyQualifiedName)} id={model_str(entity.id)}")


def main() -> int:
    """Validate, configure the SDK, run, and always clear global SDK state."""
    try:
        namespace = validate_environment()
        configure()
        try:
            run_scenario(namespace)
        finally:
            reset()
    except (ValueError, RuntimeError) as exc:
        print(f"catalog scenario failed: {exc}")
        return 1
    except Exception as exc:  # SDK errors differ by HTTP response class.
        print(f"catalog scenario failed: {type(exc).__name__}")
        return 1
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
