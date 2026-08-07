# API Lineage CICD Demo

Demonstrates using the OpenMetadata Python SDK 2.0 public facades to register
collections and endpoints under two existing REST API services, then create
lineage between those endpoints. Declarative YAML can live beside API code in
version control.

> [!IMPORTANT]
> This example targets `openmetadata-ingestion==2.0.0.0rc1`. Its tests validate generated models
> and mocked SDK boundaries without contacting a live OpenMetadata server.

## Scenario

An e-commerce platform has two internal APIs:

| Service | Description |
|---------|-------------|
| **Orders API service** | Existing parent for order collections and endpoints |
| **Fulfillment API service** | Existing parent for fulfillment collections and endpoints |

The Fulfillment API's `createShipment` endpoint **consumes** data produced by the Orders API's `createOrder` endpoint. This data dependency is captured as lineage in OpenMetadata.

## Files

```
orders_api.yaml        # Orders API service, collection, and endpoints
fulfillment_api.yaml   # Fulfillment API service, collection, and endpoints
lineage.yaml           # Lineage edges between endpoints
api_lineage_cicd.py    # Script that reads the YAMLs and calls the SDK
requirements.txt       # Python dependencies
```

## Prerequisites

- OpenMetadata server running at `http://localhost:8585`
- Python 3.10+
- Two existing API services. RC1 does not export an API service facade, so this
  example never creates services through a private client.

## Usage

```bash
cd api-lineage-cicd
pip install -r requirements.txt

export OPENMETADATA_HOST="http://localhost:8585/api"
export OPENMETADATA_JWT_TOKEN="<personal-access-token>"
export OPENMETADATA_DEMO_NAMESPACE="demo"
export OPENMETADATA_ORDERS_API_SERVICE_FQN="existing-orders-service"
export OPENMETADATA_FULFILLMENT_API_SERVICE_FQN="existing-fulfillment-service"
python api_lineage_cicd.py
```

Expected output (column-mapping lines omitted):

```
1. Creating Orders API assets...
  APICollections: existing-orders-service.orders
  APIEndpoints: existing-orders-service.orders.createOrder
  APIEndpoints: existing-orders-service.orders.getOrder

2. Creating Fulfillment API assets...
  APICollections: existing-fulfillment-service.shipments
  APIEndpoints: existing-fulfillment-service.shipments.createShipment
  APIEndpoints: existing-fulfillment-service.shipments.getShipment

3. Adding lineage edges...
  Lineage: existing-orders-service.orders.createOrder → existing-fulfillment-service.shipments.createShipment
  Lineage: existing-orders-service.orders.getOrder → existing-fulfillment-service.shipments.getShipment

4. Verifying lineage...
  Verified 2 lineage edges and 5 column mappings

Done ✅
```

## A Pipeline Asset Is Optional

OpenMetadata lineage connects data assets directly. A Pipeline asset is not
required between an API endpoint and a table—or between the two API endpoints
in this example. `LineageDetails.pipeline` is optional context for identifying
the orchestrated job that performs the movement.

Inside an SDK session already initialized with `configure()`, this direct API
Endpoint → Table request is valid without a Pipeline:

```python
from metadata.generated.schema.api.lineage.addLineage import AddLineageRequest
from metadata.generated.schema.type.basic import FullyQualifiedEntityName
from metadata.generated.schema.type.entityLineage import (
    ColumnLineage,
    EntitiesEdge,
    LineageDetails,
)
from metadata.generated.schema.type.entityReference import EntityReference
from metadata.sdk import APIEndpoints, Tables
from metadata.sdk.api.lineage import Lineage

endpoint = APIEndpoints.retrieve_by_name("orders-api.orders.createOrder")
table = Tables.retrieve_by_name("warehouse.sales.public.orders")

Lineage.add_lineage_request(
    AddLineageRequest(
        edge=EntitiesEdge(
            fromEntity=EntityReference(id=endpoint.id, type="apiEndpoint"),
            toEntity=EntityReference(id=table.id, type="table"),
            lineageDetails=LineageDetails(
                columnsLineage=[
                    ColumnLineage(
                        fromColumns=[
                            FullyQualifiedEntityName(
                                "orders-api.orders.createOrder.responseSchema.order_id"
                            )
                        ],
                        toColumn=FullyQualifiedEntityName("warehouse.sales.public.orders.order_id"),
                    )
                ]
            ),
        )
    )
)
```

The pinned RC1 schema defines the
[`pipeline` reference as optional](https://github.com/open-metadata/OpenMetadata/blob/8e199f486b63df9f44d4c827a9f43559d9e56e07/openmetadata-spec/src/main/resources/json/schema/type/entityLineage.json#L45-L64),
and its server implementation explicitly
[`validates API endpoint request and response fields`](https://github.com/open-metadata/OpenMetadata/blob/8e199f486b63df9f44d4c827a9f43559d9e56e07/openmetadata-service/src/main/java/org/openmetadata/service/jdbi3/LineageRepository.java#L1207-L1229)
for column lineage. The generic edge-schema description still says lineage
details are for table-to-table edges; this example follows the executable RC1
server behavior for API endpoints.

## Troubleshooting Empty `columnsLineage`

RC1 keeps a valid entity-level edge but filters field mappings whose FQNs do
not belong to that edge. This can leave the lineage visible in the UI while the
matching edge returns `columnsLineage: []`.

Use the exact `fullyQualifiedName` values returned by OpenMetadata:

```text
API response field: service.collection.endpoint.responseSchema.field
API request field:  service.collection.endpoint.requestSchema.field
Table column:       service.database.schema.table.column
```

Do not rebuild these names from display names. Retrieve the endpoint with
`requestSchema,responseSchema`, retrieve the table with `columns`, and copy the
field and column FQNs from those responses. Confirm that the source fields
belong to the edge's upstream entity and the destination field belongs to its
downstream entity.

The RC1 server
[`filters invalid source and destination fields`](https://github.com/open-metadata/OpenMetadata/blob/8e199f486b63df9f44d4c827a9f43559d9e56e07/openmetadata-service/src/main/java/org/openmetadata/service/jdbi3/LineageRepository.java#L718-L750)
instead of rejecting the whole edge. This example therefore reads the edge
back and compares all requested mappings. It fails with `Column lineage
mismatch` rather than reporting a partial write as successful.

## Idempotency and Overwrite Behavior

The script uses public `APICollections.create()` and `APIEndpoints.create()`
facades. These are full HTTP PUT upserts. Before each PUT, it retrieves the
expected FQN and requires the exact
`[openmetadata-demo:<namespace>:api-lineage-cicd]` description marker. Missing
entities are created, owned entities are updated, and foreign collisions abort.
The supplied parent services are never modified.

### Preserving Manual Edits

If you want the pipeline to only push specific field changes without overwriting the rest, use
`APIEndpoints.update()` instead of `APIEndpoints.create()`. Under the hood, `update()` performs a
**JSON Patch** (HTTP PATCH): it fetches the current entity, diffs it against the version you
provide, and only sends the fields that changed. Fields you don't touch — like a description edited
in the UI — are left as-is.

```python
# create (PUT) — full replace after the ownership check
endpoint = APIEndpoints.create(CreateAPIEndpointRequest(...))

# patch (PATCH) — partial update, only changed fields are sent
endpoint = APIEndpoints.retrieve_by_name("orders-api.orders.createOrder")
endpoint.description = "Updated via CI/CD"
endpoint = APIEndpoints.update(endpoint)
```

Choose the approach that fits your workflow:

| Method | HTTP | Behavior | Use when |
|--------|------|----------|----------|
| `create()` | PUT | Full replace — YAML is the single source of truth | You want the pipeline to own all metadata |
| `update()` | PATCH | Partial diff — only changed fields are sent | You want to coexist with manual UI edits |

The script reads lineage back after writing it and fails if either requested
edge or any requested column mapping is missing. It does not delete services,
collections, endpoints, or lineage. Credentials are read only from the
environment and are never printed.

## CI/CD Integration

This pattern works well in CI/CD pipelines. Update the YAML files alongside your API code and run the script on merge to keep OpenMetadata in sync with your API definitions.
