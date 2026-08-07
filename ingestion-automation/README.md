# Database Ingestion Automation

> [!IMPORTANT]
> This example targets OpenMetadata 2.0 RC1 and requires a server with the ingestion container
> enabled. It creates and triggers resources when executed.

This script creates a Postgres service and its metadata ingestion pipeline. It then deploys the
generated Airflow DAG and triggers a run. Importing the module performs no network calls. All
mutations happen inside `run()`.

## Run the Example

```bash
python3 -m venv .venv
source .venv/bin/activate
python -m pip install -r ingestion-automation/requirements.txt

export OPENMETADATA_HOST="http://localhost:8585/api"
export OPENMETADATA_JWT_TOKEN="<ingestion-bot-token>"
export OPENMETADATA_SERVICE_NAME="warehouse"
export POSTGRES_HOST="postgres:5432"
export POSTGRES_USERNAME="postgres"
export POSTGRES_PASSWORD="<postgres-password>"
export POSTGRES_DATABASE="analytics"

python ingestion-automation/deploy_database_ingestion.py
```

The deploy and trigger endpoints return a pipeline-service response rather than an ingestion
pipeline entity. The example therefore keeps those two operations as explicit REST helpers while
using generated 2.0 request models for service and pipeline creation.

## Validation Boundary

Repository tests validate environment loading, generated request models, and the exact deploy and
trigger paths with a fake client. They do not create services or trigger ingestion in CI.
