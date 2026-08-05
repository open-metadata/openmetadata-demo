# Custom Connector Examples

> [!IMPORTANT]
> These examples target the OpenMetadata 2.0 release candidate. They are validated against
> `openmetadata-ingestion==2.0.0.0rc1` and are not compatible with OpenMetadata 1.x.

This package contains deterministic custom connectors that demonstrate the contract between an
OpenMetadata ingestion workflow and a customer-owned Python source. The examples do not connect to
external source systems; they build small in-memory catalogs so the connector behavior stays easy
to inspect.

## Quickstart

Prerequisites:

- Python 3.10, 3.11, or 3.12
- A running OpenMetadata 2.0 RC1 server
- An ingestion bot token

Install the package and run the database example:

```bash
python3 -m venv .venv
source .venv/bin/activate
python -m pip install --editable "./custom-connector[test]"

export OPENMETADATA_HOST="http://localhost:8585/api"
export OPENMETADATA_JWT_TOKEN="<ingestion-bot-token>"
metadata ingest -c custom-connector/configs/custom-database.yaml
```

The database connector class is
`openmetadata_demo_connectors.database.CustomDatabaseSource`. It produces a database, two schemas,
three tables, a stored procedure, a classification and tag, and table lineage. Set
`connectionOptions.databaseName` in the workflow YAML to change the generated database name.

## Build a Custom Ingestion Image

Download the official 2.0 RC1 Compose file, then overlay the custom ingestion image:

```bash
curl -fsSLO https://github.com/open-metadata/OpenMetadata/releases/download/2.0.0-rc1-release/docker-compose-postgres.yml
docker compose \
  -f docker-compose-postgres.yml \
  -f custom-connector/docker/compose.override.yml \
  up --detach --build
```

In the OpenMetadata UI, configure a Custom Database service and enter the same fully qualified
Python class from the example YAML. The image installs the package without replacing the ingestion
image's matching OpenMetadata dependencies.

## Validation Boundary

The repository checks package installation, imports, workflow models, emitted request models, and
dependency ordering without a live server. Running ingestion against a deployed server remains a
manual validation step.
