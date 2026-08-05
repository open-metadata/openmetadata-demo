# API Lineage CICD Demo

Demonstrates using the OpenMetadata Python SDK 2.0 to register two REST API services and create lineage between their endpoints — all driven by declarative YAML files that can live alongside your API code in version control.

> [!IMPORTANT]
> This example targets `openmetadata-ingestion==2.0.0.0rc1`. Its tests validate generated models
> and mocked SDK boundaries without contacting a live OpenMetadata server.

## Scenario

An e-commerce platform has two internal APIs:

| Service | Description |
|---------|-------------|
| **Orders API** | Manages order creation and retrieval |
| **Fulfillment API** | Handles warehouse picking, packing, and shipping |

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

## Usage

```bash
cd api-lineage-cicd
pip install -r requirements.txt

export OPENMETADATA_HOST="http://localhost:8585/api"
export OPENMETADATA_JWT_TOKEN="<personal-access-token>"
python api_lineage_cicd.py
```

Expected output (column-mapping lines omitted):

```
1. Creating Orders API...
  Service: orders-api
    Collection: orders-api.orders
      Endpoint: orders-api.orders.createOrder
      Endpoint: orders-api.orders.getOrder

2. Creating Fulfillment API...
  Service: fulfillment-api
    Collection: fulfillment-api.shipments
      Endpoint: fulfillment-api.shipments.createShipment
      Endpoint: fulfillment-api.shipments.getShipment

3. Adding lineage edges...
  Lineage: orders-api.orders.createOrder → fulfillment-api.shipments.createShipment
  Lineage: orders-api.orders.getOrder → fulfillment-api.shipments.getShipment

4. Verifying lineage...
  Verified 2 lineage edges

Done ✅
```

## Idempotency and Overwrite Behavior

The script uses `create_or_update` (HTTP PUT) for services, collections, and endpoints. This means
**every run replaces the full entity** with whatever is defined in the YAML files. If someone edits a
description, tag, or any other field in the OpenMetadata UI, the next execution of this script will
overwrite those changes with the YAML values.

This is by design — the YAML files are the **source of truth** for API definitions in this CI/CD pattern.

### Preserving Manual Edits

If you want the pipeline to only push specific field changes without overwriting the rest, use
`APIEndpoints.update()` instead of `APIEndpoints.create()`. Under the hood, `update()` performs a
**JSON Patch** (HTTP PATCH): it fetches the current entity, diffs it against the version you
provide, and only sends the fields that changed. Fields you don't touch — like a description edited
in the UI — are left as-is.

```python
# create_or_update (PUT) — full replace, YAML always wins
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

## CI/CD Integration

This pattern works well in CI/CD pipelines. Update the YAML files alongside your API code and run the script on merge to keep OpenMetadata in sync with your API definitions.
