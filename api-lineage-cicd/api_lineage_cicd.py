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
  1. Create two API REST services (Orders API, Fulfillment API) from YAML definitions
  2. Register API Collections and Endpoints under each service
  3. Add lineage edges between endpoints across services

Each step reads from a declarative YAML file so this script can be
integrated into a CI/CD pipeline.

Usage:
    pip install "openmetadata-ingestion==2.0.0.0rc1"
    python api_lineage_cicd.py
"""

import os
from collections.abc import Mapping
from pathlib import Path

import yaml
from metadata.generated.schema.api.data.createAPICollection import (
    CreateAPICollectionRequest,
)
from metadata.generated.schema.api.data.createAPIEndpoint import (
    CreateAPIEndpointRequest,
)
from metadata.generated.schema.api.lineage.addLineage import AddLineageRequest
from metadata.generated.schema.api.services.createApiService import (
    CreateApiServiceRequest,
)
from metadata.generated.schema.entity.data.apiEndpoint import (
    APIEndpoint,
    ApiRequestMethod,
)
from metadata.generated.schema.entity.services.apiService import (
    ApiService,
    ApiServiceType,
)
from metadata.generated.schema.type.apiSchema import APISchema
from metadata.generated.schema.type.basic import (
    FullyQualifiedEntityName,
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
from metadata.sdk import APICollections, APIEndpoints, configure
from metadata.sdk.api.lineage import Lineage

# ------------------------------------------------------------------ #
# Helpers
# ------------------------------------------------------------------ #


def load_yaml(filename: str) -> dict:
    path = Path(__file__).parent / filename
    with path.open() as f:
        return yaml.safe_load(f)


def configure_from_environment(
    environ: Mapping[str, str] | None = None,
) -> None:
    """Configure the SDK from the standard OpenMetadata environment variables."""
    values = os.environ if environ is None else environ
    try:
        host = values["OPENMETADATA_HOST"]
        token = values["OPENMETADATA_JWT_TOKEN"]
    except KeyError as exc:
        raise RuntimeError(f"Missing required environment variable: {exc.args[0]}") from exc
    configure(host=host, jwt_token=token)


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
# Step 1 — Create an API Service from YAML
# ------------------------------------------------------------------ #


def build_api_service_request(raw: dict) -> CreateApiServiceRequest:
    """Build a service request from its declarative definition."""
    return CreateApiServiceRequest(
        name=raw["serviceName"],
        serviceType=ApiServiceType(raw["serviceType"]),
        displayName=raw.get("displayName"),
        description=raw.get("description"),
    )


def build_api_collection_request(
    raw: dict,
    service_fqn: str,
) -> CreateAPICollectionRequest:
    """Build a collection request under an API service."""
    return CreateAPICollectionRequest(
        name=raw["name"],
        displayName=raw.get("displayName"),
        description=raw.get("description"),
        endpointURL=raw.get("endpointURL"),
        service=service_fqn,
    )


def build_api_endpoint_request(
    raw: dict,
    collection_fqn: str,
) -> CreateAPIEndpointRequest:
    """Build an endpoint request under an API collection."""
    return CreateAPIEndpointRequest(
        name=raw["name"],
        displayName=raw.get("displayName"),
        description=raw.get("description"),
        apiCollection=collection_fqn,
        endpointURL=raw["endpointURL"],
        requestMethod=ApiRequestMethod(raw.get("requestMethod", "GET")),
        requestSchema=build_api_schema(raw.get("requestSchema")),
        responseSchema=build_api_schema(raw.get("responseSchema")),
    )


def create_api_service(raw: dict) -> ApiService:
    """Create or update an API Service and its collections/endpoints."""
    from metadata.sdk import client as get_client

    ometa = get_client().ometa

    service = ometa.create_or_update(build_api_service_request(raw))
    print(f"  Service: {model_str(service.fullyQualifiedName)}")

    for coll_raw in raw.get("collections", []):
        collection = APICollections.create(
            build_api_collection_request(coll_raw, service.fullyQualifiedName)
        )
        print(f"    Collection: {model_str(collection.fullyQualifiedName)}")

        for ep_raw in coll_raw.get("endpoints", []):
            endpoint = APIEndpoints.create(
                build_api_endpoint_request(ep_raw, collection.fullyQualifiedName)
            )
            print(f"      Endpoint: {model_str(endpoint.fullyQualifiedName)}")

    return service


# ------------------------------------------------------------------ #
# Step 2 — Create lineage edges from YAML
# ------------------------------------------------------------------ #


def build_column_lineage(raw_columns: list | None) -> list[ColumnLineage] | None:
    """Build column-level lineage with transformation functions."""
    if not raw_columns:
        return None
    return [
        ColumnLineage(
            fromColumns=[FullyQualifiedEntityName(col) for col in cl["fromColumns"]],
            toColumn=FullyQualifiedEntityName(cl["toColumn"]),
            function=SqlFunction(cl["function"]) if cl.get("function") else None,
        )
        for cl in raw_columns
    ]


def lineage_edge_fqns(edge: dict) -> tuple[str, str]:
    """Return the upstream and downstream endpoint FQNs for one edge."""
    from_ref = edge["from"]
    to_ref = edge["to"]
    return (
        f"{from_ref['service']}.{from_ref['collection']}.{from_ref['endpoint']}",
        f"{to_ref['service']}.{to_ref['collection']}.{to_ref['endpoint']}",
    )


def create_lineage(raw: dict) -> None:
    """Read lineage edges from YAML and register them in OpenMetadata."""
    for edge in raw.get("edges", []):
        from_fqn, to_fqn = lineage_edge_fqns(edge)

        from_entity = APIEndpoints.retrieve_by_name(from_fqn)
        to_entity = APIEndpoints.retrieve_by_name(to_fqn)

        columns_lineage = build_column_lineage(edge.get("columnLineage"))

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


def verify_lineage(raw: dict) -> None:
    """Fetch lineage back and require every declarative edge to exist."""
    verified = 0
    for edge in raw.get("edges", []):
        from_fqn, to_fqn = lineage_edge_fqns(edge)
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
        found = lineage and any(
            model_str(upstream.fromEntity) == from_id and model_str(upstream.toEntity) == to_id
            for upstream in lineage.upstreamEdges or []
        )
        if not found:
            raise RuntimeError(f"Missing lineage edge: {from_fqn} → {to_fqn}")
        verified += 1
    print(f"  Verified {verified} lineage edges")


# ------------------------------------------------------------------ #
# Main
# ------------------------------------------------------------------ #


def run() -> None:
    configure_from_environment()

    print("\n1. Creating Orders API...")
    orders_raw = load_yaml("orders_api.yaml")
    create_api_service(orders_raw)

    print("\n2. Creating Fulfillment API...")
    fulfillment_raw = load_yaml("fulfillment_api.yaml")
    create_api_service(fulfillment_raw)

    print("\n3. Adding lineage edges...")
    lineage_raw = load_yaml("lineage.yaml")
    create_lineage(lineage_raw)

    print("\n4. Verifying lineage...")
    verify_lineage(lineage_raw)

    print("\nDone ✅")


if __name__ == "__main__":
    run()
