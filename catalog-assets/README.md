# Database Catalog Facades

> OpenMetadata 2.0 RC1 only. This example uses
> `openmetadata-ingestion==2.0.0.0rc1` and performs live PUT requests.

This example demonstrates the public `DatabaseServices`, `Databases`,
`DatabaseSchemas`, `Tables`, and `StoredProcedures` SDK facades. It creates a
custom database service, database, schema, three-column table, SQL stored
procedure, and two sample-data rows. It also reads every entity by fully
qualified name and updates the owned table description.

## Run

Use Python 3.10, 3.11, or 3.12 and install the repository SDK dependency:

```bash
python -m pip install -r requirements-sdk.txt
export OPENMETADATA_HOST=http://localhost:8585/api
export OPENMETADATA_JWT_TOKEN='<token>'
export OPENMETADATA_DEMO_NAMESPACE=demo
python catalog-assets/catalog_assets.py
```

The namespace must match `^[a-z][a-z0-9_]{2,31}$`. Choose a unique namespace.
Every created entity has the marker
`[openmetadata-demo:<namespace>:catalog-assets]` in its description.

`Facade.create()` is a full PUT upsert. The example reruns owned entities but
refuses to overwrite an existing entity without the exact ownership marker.
It does not delete or automatically clean up anything. The token is read only
from the environment and never printed.

The automated tests validate request models, ordering, collision handling, and
import safety offline. They do not certify a live OpenMetadata server. Run this
script against a disposable 2.0 RC1 instance before using the pattern elsewhere.
