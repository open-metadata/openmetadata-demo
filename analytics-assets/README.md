# Analytics Asset Facades

> OpenMetadata 2.0 RC1 only. This live example uses the exact dependency in
> `requirements-sdk.txt`; automated validation is offline, not server-certified.

This scenario directly demonstrates `DashboardServices`, `Charts`,
`DashboardDataModels`, `Dashboards`, `MLModels`, `Pipelines`, `Queries`, and
`SearchIndexes`. It creates a custom dashboard service, linked chart/data
model/dashboard, representative ML model, three-task pipeline with one status,
SQL query, and typed search index.

OpenMetadata 2.0 RC1 does not expose public service facades for the ML model,
pipeline, or search services. Create those services first and supply their
fully qualified names. Supply an existing database service for the query.

## Run

```bash
python -m pip install -r requirements-sdk.txt
export OPENMETADATA_HOST=http://localhost:8585/api
export OPENMETADATA_JWT_TOKEN='<token>'
export OPENMETADATA_DEMO_NAMESPACE=demo
export OPENMETADATA_DATABASE_SERVICE_FQN=sample_database_service
export OPENMETADATA_ML_MODEL_SERVICE_FQN=sample_ml_service
export OPENMETADATA_PIPELINE_SERVICE_FQN=sample_pipeline_service
export OPENMETADATA_SEARCH_SERVICE_FQN=sample_search_service
python analytics-assets/analytics_assets.py
```

The namespace must match `^[a-z][a-z0-9_]{2,31}$`. The script reads credentials
only from the environment. It prints safe entity FQNs and IDs, not connections
or tokens.

`Facade.create()` performs a full PUT upsert. Every entity created by this
scenario carries `[openmetadata-demo:<namespace>:analytics-assets]`; reruns are
allowed only for that exact marker. Foreign collisions abort. No cleanup,
restore, search reindex, or global settings mutation is included.
