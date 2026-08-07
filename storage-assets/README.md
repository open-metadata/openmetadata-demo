# Storage Asset Facades

> OpenMetadata 2.0 RC1 only. This example performs live requests; CI validates
> its models and behavior offline against `openmetadata-ingestion==2.0.0.0rc1`.

This scenario directly demonstrates `StorageServices` and `Containers`. It
creates a `CustomStorage` service, a root container, and a child container. It
creates the child with its parent reference, then uses
`Containers.list_children()` and `Containers.list_ancestors()` to read the
hierarchy. No external storage system is required.

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

The child request is built after the owned root exists because its parent
reference requires the root ID. A partial run is safe to retry. The script
never deletes containers, clears parents, or performs automatic cleanup.
Output is limited to entity FQNs and IDs.

`Containers.set_parent()` is not used because its RC1 server path is broken;
see [`SDK_FACADE_LIMITATIONS.md`](../SDK_FACADE_LIMITATIONS.md).
