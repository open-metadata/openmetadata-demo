"""Tests for the dynamic CSV importer."""

from metadata.generated.schema.entity.data.table import Column, DataType, Table

from dynamic_csv_importer.csv_importer import (
    CSVColumnSchema,
    build_updated_entity,
    clean_column_name,
    load_csv_data,
    parse_arguments,
    process_entities,
)


def test_cli_reads_connection_settings_from_environment(monkeypatch) -> None:
    """Customers should not need to place credentials in shell history."""
    monkeypatch.setenv("OPENMETADATA_HOST", "https://metadata.example.com/api")
    monkeypatch.setenv("OPENMETADATA_JWT_TOKEN", "test-token")

    args = parse_arguments(
        [
            "--csv-path",
            "dynamic_csv_importer/sample_dbt_jaffle.csv",
            "--report-only",
        ]
    )

    assert args.url == "https://metadata.example.com/api"
    assert args.jwt_token == "test-token"
    assert args.report_only is True


def test_sample_csv_loads_into_the_2_0_validation_model() -> None:
    """The checked-in fixture must remain a runnable customer example."""
    rows = load_csv_data("dynamic_csv_importer/sample_dbt_jaffle.csv")

    assert rows["customer_id"].column_display_name == "Customer ID"
    assert rows["email"].column_description.startswith("Primary email")


def test_column_names_drop_invisible_characters() -> None:
    """CSV exports can contain zero-width characters around column names."""
    assert clean_column_name("\u200bcustomer_id\u200b") == "customer_id"


def test_matching_csv_values_build_a_valid_2_0_entity_copy() -> None:
    """Updates should preserve the source entity and modify a deep copy."""
    source = Table(
        id="11111111-1111-1111-1111-111111111111",
        name="customers",
        columns=[Column(name="customer_id", dataType=DataType.INT)],
    )
    row = CSVColumnSchema.model_validate(
        {
            "column.name*": "customer_id",
            "column.displayName": "Customer ID",
            "column.description": "Stable customer identifier",
            "column.dataType*": "INT",
        }
    )

    updated = build_updated_entity(source, [row])

    assert updated is not None
    assert source.columns[0].description is None
    assert updated.columns[0].displayName == "Customer ID"
    assert updated.columns[0].description.root == "Stable customer identifier"


def test_matching_unchanged_values_do_not_build_a_patch() -> None:
    """Repeated imports should not patch or count unchanged column metadata."""
    source = Table(
        id="11111111-1111-1111-1111-111111111111",
        name="customers",
        columns=[
            Column(
                name="customer_id",
                dataType=DataType.INT,
                displayName="Customer ID",
                description="Stable customer identifier",
            )
        ],
    )
    row = CSVColumnSchema.model_validate(
        {
            "column.name*": "customer_id",
            "column.displayName": "Customer ID",
            "column.description": "Stable customer identifier",
            "column.dataType*": "INT",
        }
    )

    assert build_updated_entity(source, [row]) is None


def test_process_entities_counts_only_persisted_patches() -> None:
    """The mocked SDK boundary should determine whether an update succeeded."""
    source = Table(
        id="11111111-1111-1111-1111-111111111111",
        name="customers",
        columns=[Column(name="customer_id", dataType=DataType.INT)],
    )
    row = CSVColumnSchema.model_validate(
        {
            "column.name*": "customer_id",
            "column.displayName": "Customer ID",
            "column.dataType*": "INT",
        }
    )

    class Page:
        entities = [source]
        after = None

    class FakeMetadata:
        def __init__(self, patch_result):
            self.patch_result = patch_result
            self.patch_calls = []

        def list_entities(self, **_):
            return Page()

        def patch(self, **kwargs):
            self.patch_calls.append(kwargs)
            return self.patch_result

    successful = FakeMetadata(source)
    failed = FakeMetadata(None)

    success_summary = process_entities(successful, "Table", {"customer_id": row})
    failed_summary = process_entities(failed, "Table", {"customer_id": row})

    assert success_summary.entities_updated == 1
    assert successful.patch_calls[0]["skip_on_failure"] is False
    assert failed_summary.entities_updated == 0


def test_report_only_does_not_call_the_sdk_patch_boundary() -> None:
    """Report-only mode should build matches without mutating OpenMetadata."""
    source = Table(
        id="11111111-1111-1111-1111-111111111111",
        name="customers",
        columns=[Column(name="customer_id", dataType=DataType.INT)],
    )
    row = CSVColumnSchema.model_validate(
        {
            "column.name*": "customer_id",
            "column.displayName": "Customer ID",
            "column.dataType*": "INT",
        }
    )

    class FakeMetadata:
        def list_entities(self, **_):
            return type("Page", (), {"entities": [source], "after": None})()

        def patch(self, **_):
            raise AssertionError("report-only mode must not patch")

    summary = process_entities(FakeMetadata(), "Table", {"customer_id": row}, report_only=True)

    assert summary.entities_with_matches == 1
    assert summary.entities_updated == 0
