# Schedule an existing executable Test Suite

This example targets **SDK 2.0.7.2** and a compatible OpenMetadata or Collate server.
It creates a Data Quality ingestion pipeline for an **existing executable/table Test Suite**,
schedules it for `0 6 * * *`, deploys it to the server's configured orchestrator, and optionally
requests an immediate run. Rerunning with the same suite FQN and pipeline name updates that
pipeline's schedule instead of creating another pipeline.

## Prerequisites

- An existing table, its executable Test Suite, and Test Cases. In this release, executable suites
  have `basic=true` and `basicEntityReference` pointing to their table. The older `executable` field
  is deprecated. Bundle/logical suites are outside this example.
- The suite's exact `fullyQualifiedName`, available from its API response. A table suite normally
  looks like `warehouse.analytics.public.orders.testSuite`. Preserve quotes in names containing
  dots, for example `warehouse.analytics.public."orders.daily".testSuite`.
- An API token authorized to read the suite, create/update its ingestion pipeline, deploy, and run
  it. The server's ingestion identity must also be able to read the table, its connection, and tests.
- A healthy server-side orchestrator with access to your database credentials and network. For
  **Collate-managed ingestion**, use your tenant URL and existing managed setup; no local Airflow
  installation or local workflow execution is needed.

Use a separate environment from the catalog's RC1 examples. From the repository root:

```bash
python3.11 -m venv test-suite-automation/.venv
source test-suite-automation/.venv/bin/activate
python -m pip install -r test-suite-automation/requirements.txt

export OPENMETADATA_HOST='https://your-tenant.getcollate.io/api'
export OPENMETADATA_JWT_TOKEN='<your-api-token>'
```

Supply your token through your shell or secret manager; do not commit credentials. Keep the SDK
version aligned with the server. This example pins `openmetadata-ingestion==2.0.7.2` and its CI
checks run on Python 3.10, 3.11, and 3.12.

## Create, schedule, and deploy

```bash
python test-suite-automation/test_suite_pipeline.py \
  --test-suite-fqn 'warehouse.analytics.public.orders.testSuite' \
  --pipeline-name daily_data_quality \
  --schedule '0 6 * * *'
```

This requests daily runs at **06:00 in the orchestrator's scheduling timezone**. The API model's
default timezone is UTC, but timezone support depends on the orchestrator. In particular, Collate's
Argo schedule uses the controller's timezone rather than the API's `pipelineTimezone` field.
Confirm your tenant's scheduling timezone and next run in the UI before relying on the schedule.

The pipeline uses `pipelineType="TestSuite"` and associates `service.id` with the **Test Suite ID**,
using `type="testSuite"`. Its `sourceConfig.config.entityFullyQualifiedName` is the **table FQN**
from `basicEntityReference`, rather than the suite FQN. New pipelines omit the `testCases` filter
to execute all Test Cases in the suite.

The generated scheduling model is named `AirflowConfig` for historical reasons. It is also the
API scheduling configuration when Collate dispatches to its managed orchestrator. Deploy and
trigger requests go through the tenant API, not directly to Airflow or Kubernetes.

## Update a pipeline or schedule

Run the same command with the **same suite FQN and pipeline name**, changing `--schedule`.
For an existing pipeline, use its actual `name` from the API, which can differ from the UI display
name. Changing the name creates a separate pipeline.

Only `airflowConfig.scheduleInterval` is patched. Existing timezone, test filters, sampling, retries,
owners, processing engine, and pause/enabled settings are preserved.
The pipeline is then redeployed. If an existing pipeline is paused or disabled, enable it in the UI
before expecting scheduled runs. The script never deletes or recreates your suite or tests.

## Trigger a run when needed

Append `--trigger` to the setup/update command to request an immediate run after a successful
deployment. Without this flag, the script only configures and deploys the schedule.

For an already deployed pipeline, the equivalent Python call is:

```python
# metadata is the authenticated original OpenMetadata client; pipeline_id is its UUID.
response = metadata.client.post(f"/services/ingestionPipelines/trigger/{pipeline_id}")
if not 200 <= response["code"] < 300 or not response.get("platform"):
    raise RuntimeError(f"Trigger was rejected: {response.get('reason')}")
```

A successful response means the run was requested. Use the UI's run history/logs to confirm
execution and Test Case results; a returned run ID depends on the orchestrator.

## Which client and API?

Use the **original `metadata.ingestion.ometa.ometa_api.OpenMetadata` client** with the generated
`CreateIngestionPipelineRequest`, `SourceConfig`, `TestSuitePipeline`, and `AirflowConfig` models.
SDK 2.0.7.2 has no dedicated `IngestionPipelines` facade in `metadata.sdk`. Its `Pipelines` facade
manages cataloged data pipelines, which are a different entity.

The script uses these REST operations through the authenticated client:

| Operation | REST endpoint (relative to the host's `/api`) |
| --- | --- |
| Create/upsert a new pipeline | `PUT /v1/services/ingestionPipelines` |
| Update only schedule fields | `PATCH /v1/services/ingestionPipelines/{id}` |
| Deploy/redeploy | `POST /v1/services/ingestionPipelines/deploy/{id}` |
| Trigger | `POST /v1/services/ingestionPipelines/trigger/{id}` |

The client's paths omit `/v1` because it adds the API version itself. Deploy and trigger return
`PipelineServiceClientResponse`, not an `IngestionPipeline`. SDK 2.0.7.2's `run_pipeline()` helper
expects an ingestion entity, so this example uses REST for those two actions and checks the
response body's `code` as well as HTTP success. A missing/disabled orchestrator is an error.

See the official [Python client-choice guidance](https://docs.open-metadata.org/v2.0.x/api-reference/sdk/python/overview#which-python-sdk-should-i-use)
and the [2.0.7 UI Test Suite configuration](https://github.com/open-metadata/OpenMetadata/blob/2.0.7-release/openmetadata-ui/src/main/resources/ui/src/components/DataQuality/AddDataQualityTest/TestSuiteIngestion.tsx).

## Verification

```bash
python -m pip install pytest ruff
cd test-suite-automation
python -m pytest
ruff check .
ruff format --check .
```

Offline tests exercise real 2.0.7.2 generated models and JSON Patch generation, stable pipeline
lookup, schedule preservation, deployment failures, optional triggering, and socket-free imports.
CI runs this example separately from the RC1 catalog. These checks do **not** deploy to a live
tenant, validate its permissions/credentials, or certify a managed orchestrator run.
