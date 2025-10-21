# Dynamic CSV Importer

This python script provides a flexible way to import metadata from CSV files into OpenMetadata or Collate.

It supports dynamic mapping of columns to any asset that contains that metadata field. It will then update the description and display name of the asset based on the CSV data.

> Note that it won't create new assets or add columns; it only updates existing assets with the provided metadata.

## How to run

1. Install the required dependencies:

```bash
python -m venv venv
source venv/bin/activate  # On Windows use `venv\Scripts\activate`
pip install openmetadata-ingestion==1.9.11
```

2. Prepare your CSV file, following the schema of the usual import/export CSV files used by OpenMetadata or Collate.

```csv
column.name*,column.displayName,column.description,column.dataTypeDisplay,column.dataType*,column.arrayDataType,column.dataLength,column.tags,column.glossaryTerms
```

3. Run the script with the necessary parameters:

```bash
python csv_importer.py \
  --csv-path /path/to/your/metadata.csv \
  --entities all \
  --url https://your-instance.com/api \
  --jwt-token your_jwt_token_here
```

## Command Line Options

- `--csv-path` (required): Path to the CSV file containing metadata
- `--entities` (optional): Entity types to process. Options:
  - `all` (default): Process all supported entity types
  - `Table`: Process only tables
  - `DashboardDataModel`: Process only dashboard data models
- `--url` (required): URL of your OpenMetadata or Collate instance API endpoint
- `--jwt-token` (required): JWT authentication token for your OpenMetadata instance

## Examples

### Process all entity types
```bash
python csv_importer.py \
  --csv-path ./metadata.csv \
  --entities all \
  --url https://sandbox.open-metadata.org/api \
  --jwt-token eyJhbGciOiJSUzI1NiIsInR5cCI6IkpXVCJ9...
```

### Process only tables
```bash
python csv_importer.py \
  --csv-path ./table_metadata.csv \
  --entities Table \
  --url https://sandbox.open-metadata.org/api \
  --jwt-token eyJhbGciOiJSUzI1NiIsInR5cCI6IkpXVCJ9...
```

### Process only dashboard data models
```bash
python csv_importer.py \
  --csv-path ./dashboard_metadata.csv \
  --entities DashboardDataModel \
  --url https://sandbox.open-metadata.org/api \
  --jwt-token eyJhbGciOiJSUzI1NiIsInR5cCI6IkpXVCJ9...
```

## How it works

1. **CSV Loading**: The script loads and validates your CSV file using Pydantic schemas
2. **Authentication**: Connects to your OpenMetadata instance using JWT authentication
3. **Entity Pagination**: Efficiently retrieves entities using pagination (100 entities per request)
4. **Column Matching**: For each entity, compares its column names with the `column.name*` field in your CSV
5. **Results**: Reports all matches found, showing which CSV entries correspond to existing entity columns
