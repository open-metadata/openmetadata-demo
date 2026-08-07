# Governance Asset Facades

> OpenMetadata 2.0 RC1 only. This example performs live writes; automated tests
> validate its requests and ordering offline against the exact RC1 SDK.

This scenario demonstrates `Classifications`, `Tags`, `Glossaries`,
`GlossaryTerms`, `Domains`, `DataProducts`, `Metrics`, and `DataContracts`.
It creates related terms and metrics, adds a metric to a data product, validates
a table contract model, retrieves the created contract by target entity, and
exercises ODCS YAML export without printing the exported data.

Supply an existing table as the contract target:

```bash
python -m pip install -r requirements-sdk.txt
export OPENMETADATA_HOST=http://localhost:8585/api
export OPENMETADATA_JWT_TOKEN='<token>'
export OPENMETADATA_DEMO_NAMESPACE=demo
export OPENMETADATA_CONTRACT_TABLE_FQN=sample.database.schema.customers
python governance-assets/governance_assets.py
```

The target table is read before any mutation. If it already has a data contract
without `[openmetadata-demo:<namespace>:governance-assets]`, the script aborts
before creating governance entities. The supplied table is never modified.

All demo-created entities use full PUT upserts guarded by that exact marker.
There is no hard delete, result deletion, ODCS import, or automatic cleanup.
Output contains only entity FQNs and IDs. CI does not run a live server.

The scenario uses a deep-copied `Metrics.update()` for metric relationships and
relies on request-model validation before creating the contract. The RC1
`Metrics.add_related_metrics()` and `DataContracts.validate_request()` helper
paths are broken; see
[`SDK_FACADE_LIMITATIONS.md`](../SDK_FACADE_LIMITATIONS.md).
