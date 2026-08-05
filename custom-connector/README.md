# Custom Connector Examples

> [!IMPORTANT]
> These examples target the OpenMetadata 2.0 release candidate. They are validated against
> `openmetadata-ingestion==2.0.0.0rc1` and are not compatible with OpenMetadata 1.x.

This package contains deterministic custom connectors that demonstrate the contract between an
OpenMetadata ingestion workflow and a customer-owned Python source. The examples do not connect to
external source systems. They build small in-memory catalogs so the connector behavior stays easy
to inspect.

## Quickstart

Prerequisites:

- Python 3.10, 3.11, or 3.12
- A running OpenMetadata 2.0 RC1 server
- An ingestion bot token

Install the package and run any example:

```bash
python3 -m venv .venv
source .venv/bin/activate
python -m pip install --editable "./custom-connector[test]"

export OPENMETADATA_HOST="http://localhost:8585/api"
export OPENMETADATA_JWT_TOKEN="<ingestion-bot-token>"
metadata ingest -c custom-connector/configs/custom-database.yaml
```

Replace `custom-database.yaml` with one of the configuration files below. For supported service
types, select the matching Custom service connection in the OpenMetadata UI and enter the listed
Python class exactly as shown. The OpenMetadata 2.0 RC1 UI does not expose the Python class field
for Custom Drive, so run that scenario from its YAML file with the CLI.

## Available Scenarios

| Service | Configuration | UI connection / source config | Python class | What the run creates |
| --- | --- | --- | --- | --- |
| Database | `custom-database.yaml` | `CustomDatabase` / `DatabaseMetadata` | `openmetadata_demo_connectors.database.CustomDatabaseSource` | Two schemas, three tables, a stored procedure, tags, and table lineage |
| Dashboard | `custom-dashboard.yaml` | `CustomDashboard` / `DashboardMetadata` | `openmetadata_demo_connectors.dashboard.CustomDashboardSource` | Two charts, a data model, and a dashboard relating them |
| Messaging | `custom-messaging.yaml` | `CustomMessaging` / `MessagingMetadata` | `openmetadata_demo_connectors.messaging.CustomMessagingSource` | Two topics with typed schemas and sample messages |
| ML model | `custom-mlmodel.yaml` | `CustomMlModel` / `MlModelMetadata` | `openmetadata_demo_connectors.mlmodel.CustomMlModelSource` | A model with features, hyperparameters, and model storage details |
| Pipeline | `custom-pipeline.yaml` | `CustomPipeline` / `PipelineMetadata` | `openmetadata_demo_connectors.pipeline.CustomPipelineSource` | A three-task pipeline and a successful execution status |
| Search | `custom-search.yaml` | `CustomSearch` / `SearchMetadata` | `openmetadata_demo_connectors.search.CustomSearchSource` | Two search indexes with typed fields |
| Storage | `custom-storage.yaml` | `CustomStorage` / `StorageMetadata` | `openmetadata_demo_connectors.storage.CustomStorageSource` | A bucket and a prefixed container with a tabular data model |
| Drive | `custom-drive.yaml` | `CustomDrive` / `DriveMetadata` | `openmetadata_demo_connectors.drive.CustomDriveSource` | A directory, file, spreadsheet, and worksheet |

All source-system records are deterministic and generated in memory. The workflow emits each
service request before its entities and uses barriers before lineage, sample data, or execution
status records that depend on persisted entities. Set `connectionOptions.databaseName` in the
database workflow YAML to change its generated catalog name.

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
