# Dynamic CSV Importer

> [!IMPORTANT]
> This example targets `openmetadata-ingestion==2.0.0.0rc1`. It updates existing assets and does
> not create entities or columns.

The importer matches the `column.name*` field from an OpenMetadata CSV export against columns on
tables and dashboard data models. It can update column descriptions and display names or run in a
report-only mode.

## Run the Example

```bash
python3 -m venv .venv
source .venv/bin/activate
python -m pip install -r dynamic_csv_importer/requirements.txt

export OPENMETADATA_HOST="http://localhost:8585/api"
export OPENMETADATA_JWT_TOKEN="<personal-access-token>"
python -m dynamic_csv_importer.csv_importer \
  --csv-path dynamic_csv_importer/sample_dbt_jaffle.csv \
  --entities all \
  --report-only
```

Remove `--report-only` after reviewing the match counts. Override the environment-based connection
settings with `--url` and `--jwt-token` when needed.

Supported `--entities` values are `all`, `Table`, and `DashboardDataModel`.

## CSV Columns

```csv
column.name*,column.displayName,column.description,column.dataTypeDisplay,column.dataType*,column.arrayDataType,column.dataLength,column.tags,column.glossaryTerms
```

Only `column.name*`, `column.displayName`, and `column.description` are used by this example. The
remaining fields make the input compatible with a normal OpenMetadata export.

## Validation Boundary

Repository tests validate argument handling, CSV parsing, matching, and request-model compatibility
without connecting to OpenMetadata.
