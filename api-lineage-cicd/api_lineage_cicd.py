#  Copyright 2024 Collate
#  Licensed under the Apache License, Version 2.0 (the "License");
#  you may not use this file except in compliance with the License.
#  You may obtain a copy of the License at
#  http://www.apache.org/licenses/LICENSE-2.0
#  Unless required by applicable law or agreed to in writing, software
#  distributed under the License is distributed on an "AS IS" BASIS,
#  WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
#  See the License for the specific language governing permissions and
#  limitations under the License.

"""
API Lineage CICD Demo
=====================

Demonstrates how to use the OpenMetadata Python SDK 2.0 to:
  1. Register API Collections and Endpoints under two existing API services
  2. Add lineage edges between endpoints across services

Each step reads from a declarative YAML file so this script can be
integrated into a CI/CD pipeline.

Usage:
    pip install "openmetadata-ingestion==2.0.0.0rc1"
    python api_lineage_cicd.py
"""

import os
import re
from collections.abc import Mapping
from pathlib import Path
from typing import Any

import yaml
from metadata.generated.schema.api.data.createAPICollection import (
    CreateAPICollectionRequest,
)
from metadata.generated.schema.api.data.createAPIEndpoint import (
    CreateAPIEndpointRequest,
)
from metadata.generated.schema.api.lineage.addLineage import AddLineageRequest
from metadata.generated.schema.entity.data.apiEndpoint import (
    APIEndpoint,
    ApiRequestMethod,
)
from metadata.generated.schema.type.apiSchema import APISchema
from metadata.generated.schema.type.basic import (
    FullyQualifiedEntityName,
    Markdown,
    SqlFunction,
    SqlQuery,
)
from metadata.generated.schema.type.entityLineage import (
    ColumnLineage,
    EntitiesEdge,
    LineageDetails,
)
from metadata.generated.schema.type.entityReference import EntityReference
from metadata.generated.schema.type.schema import (
    DataTypeTopic,
    FieldModel,
    FieldName,
    SchemaType,
)
from metadata.ingestion.ometa.utils import model_str
from metadata.sdk import APICollections, APIEndpoints, configure, reset
from metadata.sdk.api.lineage import Lineage

NAMESPACE_PATTERN = re.compile(r"^[a-z][a-z0-9_]{2,31}$")
REQUIRED_ENV = (
    "OPENMETADATA_HOST",
    "OPENMETADATA_JWT_TOKEN",
    "OPENMETADATA_DEMO_NAMESPACE",
    "OPENMETADATA_ORDERS_API_SERVICE_FQN",
    "OPENMETADATA_FULFILLMENT_API_SERVICE_FQN",
)

# ------------------------------------------------------------------ #
# Helpers
# ------------------------------------------------------------------ #


def load_yaml(filename: str) -> dict:
    path = Path(__file__).parent / filename
    with path.open() as f:
        return yaml.safe_load(f)


def validate_environment(
    environ: Mapping[str, str] | None = None,
) -> tuple[str, dict[str, str]]:
    """Validate credentials, namespace, and the two existing API services."""
    values = os.environ if environ is None else environ
    missing = [name for name in REQUIRED_ENV if not values.get(name)]
    if missing:
        raise RuntimeError(f"Missing required environment variable: {missing[0]}")
    namespace = values["OPENMETADATA_DEMO_NAMESPACE"]
    if not NAMESPACE_PATTERN.fullmatch(namespace):
        raise RuntimeError("OPENMETADATA_DEMO_NAMESPACE must match ^[a-z][a-z0-9_]{2,31}$")
    return namespace, {
        "orders-api": values["OPENMETADATA_ORDERS_API_SERVICE_FQN"],
        "fulfillment-api": values["OPENMETADATA_FULFILLMENT_API_SERVICE_FQN"],
    }


def ownership_marker(namespace: str) -> str:
    return f"[openmetadata-demo:{namespace}:api-lineage-cicd]"


def build_api_schema(raw: dict | None) -> APISchema | None:
    if not raw:
        return None
    schema_fields = raw.get("schemaFields") or []
    return APISchema(
        schemaType=SchemaType(raw.get("schemaType", "JSON")),
        schemaFields=[
            FieldModel(
                name=FieldName(f["name"]),
                dataType=DataTypeTopic(f.get("dataType", "STRING")),
                description=f.get("description"),
                children=[
                    FieldModel(
                        name=FieldName(c["name"]),
                        dataType=DataTypeTopic(c.get("dataType", "STRING")),
                        description=c.get("description"),
                    )
                    for c in f.get("children", [])
                ]
                if f.get("children")
                else None,
            )
            for f in schema_fields
        ]
        if schema_fields
        else None,
    )


# ------------------------------------------------------------------ #
# Step 1 — Build and create assets under existing API services
# ------------------------------------------------------------------ #


def build_api_collection_request(
    raw: dict,
    service_fqn: str,
    marker: str,
) -> CreateAPICollectionRequest:
    """Build a collection request under an API service."""
    return CreateAPICollectionRequest(
        name=raw["name"],
        displayName=raw.get("displayName"),
        description=Markdown(root=f"{marker} {raw.get('description', '')}".strip()),
        endpointURL=raw.get("endpointURL"),
        service=service_fqn,
    )


def build_api_endpoint_request(
    raw: dict,
    collection_fqn: str,
    marker: str,
) -> CreateAPIEndpointRequest:
    """Build an endpoint request under an API collection."""
    return CreateAPIEndpointRequest(
        name=raw["name"],
        displayName=raw.get("displayName"),
        description=Markdown(root=f"{marker} {raw.get('description', '')}".strip()),
        apiCollection=collection_fqn,
        endpointURL=raw["endpointURL"],
        requestMethod=ApiRequestMethod(raw.get("requestMethod", "GET")),
        requestSchema=build_api_schema(raw.get("requestSchema")),
        responseSchema=build_api_schema(raw.get("responseSchema")),
    )


def build_api_assets(
    raw: dict,
    service_fqn: str,
    marker: str,
) -> list[tuple[Any, str, Any]]:
    """Validate all collection and endpoint requests before mutation."""
    assets: list[tuple[Any, str, Any]] = []
    for coll_raw in raw.get("collections", []):
        collection_fqn = f"{service_fqn}.{coll_raw['name']}"
        assets.append(
            (
                APICollections,
                collection_fqn,
                build_api_collection_request(coll_raw, service_fqn, marker),
            )
        )
        for ep_raw in coll_raw.get("endpoints", []):
            assets.append(
                (
                    APIEndpoints,
                    f"{collection_fqn}.{ep_raw['name']}",
                    build_api_endpoint_request(ep_raw, collection_fqn, marker),
                )
            )
    return assets


def owned_upsert(facade: Any, fqn: str, request: Any, marker: str) -> Any:
    """PUT an absent or exactly owned API asset; refuse foreign collisions."""
    if facade is APICollections:
        existing = APICollections.retrieve_by_name(fqn, nullable=True)
    else:
        existing = APIEndpoints.retrieve_by_name(fqn, nullable=True)
    description = model_str(getattr(existing, "description", "")) if existing else ""
    if existing is not None and marker not in description:
        raise RuntimeError(f"Refusing to overwrite foreign entity: {fqn}")
    if facade is APICollections:
        return APICollections.create(request)
    return APIEndpoints.create(request)


def apply_api_assets(
    assets: list[tuple[Any, str, Any]],
    marker: str,
) -> None:
    """Create parents before children using public collection/endpoint facades."""
    for facade, fqn, request in assets:
        try:
            entity = owned_upsert(facade, fqn, request, marker)
        except RuntimeError:
            raise
        except Exception as exc:
            if facade is APICollections:
                service_fqn = model_str(request.service)
                raise RuntimeError(
                    f"API service parent not found or inaccessible: {service_fqn}"
                ) from exc
            raise
        print(f"  {facade.__name__}: {model_str(entity.fullyQualifiedName)}")


# ------------------------------------------------------------------ #
# Step 2 — Create lineage edges from YAML
# ------------------------------------------------------------------ #


def _replace_service_prefix(fqn: str, service_fqns: Mapping[str, str]) -> str:
    logical_service, separator, suffix = fqn.partition(".")
    actual_service = service_fqns.get(logical_service, logical_service)
    return f"{actual_service}.{suffix}" if separator else actual_service


def build_column_lineage(
    raw_columns: list | None,
    service_fqns: Mapping[str, str] | None = None,
) -> list[ColumnLineage] | None:
    """Build column-level lineage with transformation functions."""
    if not raw_columns:
        return None
    mappings = {} if service_fqns is None else service_fqns
    return [
        ColumnLineage(
            fromColumns=[
                FullyQualifiedEntityName(_replace_service_prefix(col, mappings))
                for col in cl["fromColumns"]
            ],
            toColumn=FullyQualifiedEntityName(_replace_service_prefix(cl["toColumn"], mappings)),
            function=SqlFunction(cl["function"]) if cl.get("function") else None,
        )
        for cl in raw_columns
    ]


def column_lineage_signatures(
    columns: list[ColumnLineage] | None,
) -> set[tuple[tuple[str, ...], str, str | None]]:
    """Normalize mappings so server filtering or reordering is visible."""
    return {
        (
            tuple(sorted(model_str(source) for source in column.fromColumns or [])),
            model_str(column.toColumn),
            model_str(column.function) if column.function else None,
        )
        for column in columns or []
    }


def lineage_edge_fqns(
    edge: dict,
    service_fqns: Mapping[str, str] | None = None,
) -> tuple[str, str]:
    """Return the upstream and downstream endpoint FQNs for one edge."""
    from_ref = edge["from"]
    to_ref = edge["to"]
    mappings = {} if service_fqns is None else service_fqns
    from_service = mappings.get(from_ref["service"], from_ref["service"])
    to_service = mappings.get(to_ref["service"], to_ref["service"])
    return (
        f"{from_service}.{from_ref['collection']}.{from_ref['endpoint']}",
        f"{to_service}.{to_ref['collection']}.{to_ref['endpoint']}",
    )


def create_lineage(
    raw: dict,
    service_fqns: Mapping[str, str] | None = None,
) -> None:
    """Read lineage edges from YAML and register them in OpenMetadata."""
    for edge in raw.get("edges", []):
        from_fqn, to_fqn = lineage_edge_fqns(edge, service_fqns)

        from_entity = APIEndpoints.retrieve_by_name(from_fqn)
        to_entity = APIEndpoints.retrieve_by_name(to_fqn)

        columns_lineage = build_column_lineage(edge.get("columnLineage"), service_fqns)

        request = AddLineageRequest(
            edge=EntitiesEdge(
                fromEntity=EntityReference(
                    id=from_entity.id,
                    type="apiEndpoint",
                ),
                toEntity=EntityReference(
                    id=to_entity.id,
                    type="apiEndpoint",
                ),
                lineageDetails=LineageDetails(
                    sqlQuery=SqlQuery(edge["sqlQuery"]) if edge.get("sqlQuery") else None,
                    columnsLineage=columns_lineage,
                    description=edge.get("description"),
                ),
            )
        )
        Lineage.add_lineage_request(request)

        print(f"  Lineage: {from_fqn} → {to_fqn}")
        for cl in columns_lineage or []:
            src = ", ".join(model_str(column) for column in (cl.fromColumns or []))
            function = model_str(cl.function) if cl.function else ""
            print(f"    {src} --[{function}]--> {model_str(cl.toColumn)}")


# ------------------------------------------------------------------ #
# Step 3 — Verify lineage
# ------------------------------------------------------------------ #


def verify_lineage(
    raw: dict,
    service_fqns: Mapping[str, str] | None = None,
) -> None:
    """Fetch lineage back and require every edge and column mapping to exist."""
    verified = 0
    verified_columns = 0
    for edge in raw.get("edges", []):
        from_fqn, to_fqn = lineage_edge_fqns(edge, service_fqns)
        from_endpoint = APIEndpoints.retrieve_by_name(from_fqn)
        to_endpoint = APIEndpoints.retrieve_by_name(to_fqn)
        lineage = Lineage.get_entity_lineage(
            entity_type=APIEndpoint,
            entity_id=to_endpoint.id,
            upstream_depth=1,
            downstream_depth=1,
        )
        from_id = model_str(from_endpoint.id)
        to_id = model_str(to_endpoint.id)
        matching_edge = next(
            (
                upstream
                for upstream in ((lineage.upstreamEdges or []) if lineage else [])
                if model_str(upstream.fromEntity) == from_id
                and model_str(upstream.toEntity) == to_id
            ),
            None,
        )
        if matching_edge is None:
            raise RuntimeError(f"Missing lineage edge: {from_fqn} → {to_fqn}")

        expected_columns = build_column_lineage(edge.get("columnLineage"), service_fqns)
        details = matching_edge.lineageDetails
        actual_columns = details.columnsLineage if details else None
        if column_lineage_signatures(actual_columns) != column_lineage_signatures(expected_columns):
            raise RuntimeError(
                f"Column lineage mismatch: {from_fqn} → {to_fqn}. "
                "Use the exact field FQNs returned by OpenMetadata."
            )
        verified += 1
        verified_columns += len(expected_columns or [])
    print(f"  Verified {verified} lineage edges and {verified_columns} column mappings")


# ------------------------------------------------------------------ #
# Main
# ------------------------------------------------------------------ #


def run_scenario(namespace: str, service_fqns: Mapping[str, str]) -> None:
    """Build all requests, create API assets, then add and verify lineage."""
    marker = ownership_marker(namespace)
    orders_raw = load_yaml("orders_api.yaml")
    fulfillment_raw = load_yaml("fulfillment_api.yaml")
    orders_assets = build_api_assets(orders_raw, service_fqns["orders-api"], marker)
    fulfillment_assets = build_api_assets(
        fulfillment_raw,
        service_fqns["fulfillment-api"],
        marker,
    )

    print("\n1. Creating Orders API assets...")
    apply_api_assets(orders_assets, marker)

    print("\n2. Creating Fulfillment API assets...")
    apply_api_assets(fulfillment_assets, marker)

    print("\n3. Adding lineage edges...")
    lineage_raw = load_yaml("lineage.yaml")
    create_lineage(lineage_raw, service_fqns)

    print("\n4. Verifying lineage...")
    verify_lineage(lineage_raw, service_fqns)

    print("\nDone ✅")


def main() -> int:
    try:
        namespace, service_fqns = validate_environment()
        configure()
        try:
            run_scenario(namespace, service_fqns)
        finally:
            reset()
    except RuntimeError as exc:
        print(f"API lineage scenario failed: {exc}")
        return 1
    except Exception as exc:
        print(f"API lineage scenario failed: {type(exc).__name__}")
        return 1
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
