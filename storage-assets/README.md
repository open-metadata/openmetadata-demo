# Storage Asset Facades

> OpenMetadata 2.0 RC1 only. This example performs live requests; CI validates
> its models and behavior offline against `openmetadata-ingestion==2.0.0.0rc1`.

This scenario directly demonstrates `StorageServices` and `Containers`. It
creates a `CustomStorage` service, a root container, and a child container. It
then uses `Containers.set_parent()`, `Containers.list_children()`, and
`Containers.list_ancestors()` to establish and read the hierarchy. No external
storage system is required.

## Run

```bash
python -m pip install -r requirements-sdk.txt
export OPENMETADATA_HOST=http://localhost:8585/api
export OPENMETADATA_JWT_TOKEN='<token>'
export OPENMETADATA_DEMO_NAMESPACE=demo
python storage-assets/storage_assets.py
```

The namespace must match `^[a-z][a-z0-9_]{2,31}$`. Entities carry
`[openmetadata-demo:<namespace>:storage-assets]`. Full PUT upserts are allowed
only for exact marker matches; foreign collisions abort.

The child starts at the service root and is then re-parented. A partial run is
safe to retry: the script accepts either the temporary root-level child or the
already nested owned child. It never deletes containers, clears parents, or
performs automatic cleanup. Output is limited to entity FQNs and IDs.
