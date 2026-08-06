# Dynamic CSV Importer

> [!IMPORTANT]
> This example targets `openmetadata-ingestion==2.0.0.0rc1`. It updates existing assets and does
> not create entities or columns.

The importer matches the `column.name*` field from an OpenMetadata CSV export
against columns on explicitly named tables and dashboard data models. It can
update column descriptions and display names or build the same plan in
report-only mode. It never scans the catalog.

## Run the Example

```bash
python3 -m venv .venv
source .venv/bin/activate
python -m pip install -r dynamic_csv_importer/requirements.txt

export OPENMETADATA_HOST="http://localhost:8585/api"
export OPENMETADATA_JWT_TOKEN="<personal-access-token>"
python -m dynamic_csv_importer.csv_importer \
  --csv-path dynamic_csv_importer/sample_dbt_jaffle.csv \
  --table-fqn sample.database.schema.customers \
  --dashboard-data-model-fqn sample_dashboard.model.customer_model \
  --report-only
```

Both FQN flags are repeatable, and at least one is required. The explicit FQNs
are the authorization boundary: only those named assets can be updated. Remove
`--report-only` after reviewing the counts; live mutation is the default.

Credentials are read only from `OPENMETADATA_HOST` and
`OPENMETADATA_JWT_TOKEN`. There are no URL or token CLI flags.

## CSV Columns

```csv
column.name*,column.displayName,column.description,column.dataTypeDisplay,column.dataType*,column.arrayDataType,column.dataLength,column.tags,column.glossaryTerms
```

Only `column.name*`, `column.displayName`, and `column.description` are used by this example. The
remaining fields make the input compatible with a normal OpenMetadata export.

## Validation Boundary

The complete CSV and every target are loaded before the first update. Invalid
CSV rows or a missing target abort the run before mutation. Each destination is
a deep copy and is sent through `Tables.update()` or
`DashboardDataModels.update()`.

There is a normal concurrency window between the initial reads and facade
updates. Each facade update re-reads the current entity before creating its JSON
Patch, but the planned destination came from the earlier snapshot. Use
`--report-only`, rerun against disposable targets first, and avoid concurrent
edits to the same columns during a live import.

Repository tests validate arguments, full CSV parsing, deep-copy changes,
preflight ordering, and mocked facade updates without connecting to
OpenMetadata.
