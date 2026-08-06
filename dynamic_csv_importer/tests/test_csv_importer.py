"""Tests for the explicitly scoped dynamic CSV importer."""

import pytest
from metadata.generated.schema.entity.data.table import Column, DataType, Table

from dynamic_csv_importer.csv_importer import (
    CSVColumnSchema,
    DashboardDataModels,
    Tables,
    build_updated_entity,
    clean_column_name,
    load_csv_data,
    parse_arguments,
    process_entities,
    validate_environment,
)


def csv_row(**overrides) -> CSVColumnSchema:
    values = {
        "column.name*": "customer_id",
        "column.displayName": "Customer ID",
        "column.description": "Stable customer identifier",
        "column.dataType*": "INT",
    }
    values.update(overrides)
    return CSVColumnSchema.model_validate(values)


def table(name: str = "customers") -> Table:
    return Table(
        id="11111111-1111-1111-1111-111111111111",
        name=name,
        fullyQualifiedName=f"sample.database.schema.{name}",
        columns=[Column(name="customer_id", dataType=DataType.INT)],
    )


def test_cli_accepts_repeatable_explicit_targets() -> None:
    args = parse_arguments(
        [
            "--csv-path",
            "dynamic_csv_importer/sample_dbt_jaffle.csv",
            "--table-fqn",
            "sample.database.schema.customers",
            "--table-fqn",
            "sample.database.schema.orders",
            "--dashboard-data-model-fqn",
            "sample_dashboard.customer_model",
            "--report-only",
        ]
    )

    assert args.table_fqn == [
        "sample.database.schema.customers",
        "sample.database.schema.orders",
    ]
    assert args.dashboard_data_model_fqn == ["sample_dashboard.customer_model"]
    assert args.report_only is True
    assert not hasattr(args, "url")
    assert not hasattr(args, "jwt_token")


def test_cli_requires_at_least_one_explicit_target() -> None:
    with pytest.raises(SystemExit):
        parse_arguments(["--csv-path", "dynamic_csv_importer/sample_dbt_jaffle.csv"])


def test_environment_requires_standard_credentials() -> None:
    with pytest.raises(ValueError, match="OPENMETADATA_JWT_TOKEN"):
        validate_environment({"OPENMETADATA_HOST": "http://localhost:8585/api"})


def test_sample_csv_loads_every_row_into_the_2_0_model() -> None:
    rows = load_csv_data("dynamic_csv_importer/sample_dbt_jaffle.csv")

    assert len(rows) == 15
    assert rows["customer_id"].column_display_name == "Customer ID"
    assert rows["email"].column_description.startswith("Primary email")
    assert rows["country_name"].column_data_type == "STRING"


def test_column_names_drop_invisible_characters() -> None:
    assert clean_column_name("\u200bcustomer_id\u200b") == "customer_id"


def test_matching_csv_values_build_a_valid_deep_copy() -> None:
    source = table()

    updated = build_updated_entity(source, [csv_row()])

    assert updated is not None
    assert source.columns[0].description is None
    assert updated.columns[0].displayName == "Customer ID"
    assert updated.columns[0].description.root == "Stable customer identifier"


def test_matching_unchanged_values_do_not_build_an_update() -> None:
    source = table()
    source.columns[0].displayName = "Customer ID"
    source.columns[0].description = "Stable customer identifier"

    assert build_updated_entity(source, [csv_row()]) is None


def test_all_targets_are_retrieved_before_first_update(monkeypatch) -> None:
    calls: list[str] = []
    table_entity = table("customers")
    model_entity = table("customer_model")
    monkeypatch.setattr(
        Tables,
        "retrieve_by_name",
        lambda fqn, **_: calls.append(f"retrieve:{fqn}") or table_entity,
    )
    monkeypatch.setattr(
        DashboardDataModels,
        "retrieve_by_name",
        lambda fqn, **_: calls.append(f"retrieve:{fqn}") or model_entity,
    )
    monkeypatch.setattr(
        Tables,
        "update",
        lambda entity: calls.append("update:table") or entity,
    )
    monkeypatch.setattr(
        DashboardDataModels,
        "update",
        lambda entity: calls.append("update:model") or entity,
    )

    summary = process_entities(
        ["sample.database.schema.customers"],
        ["sample_dashboard.customer_model"],
        {"customer_id": csv_row()},
    )

    assert calls == [
        "retrieve:sample.database.schema.customers",
        "retrieve:sample_dashboard.customer_model",
        "update:table",
        "update:model",
    ]
    assert summary.entities_processed == 2
    assert summary.entities_updated == 2


def test_missing_target_aborts_before_any_update(monkeypatch) -> None:
    monkeypatch.setattr(Tables, "retrieve_by_name", lambda *_args, **_kwargs: None)
    monkeypatch.setattr(
        Tables,
        "update",
        lambda *_: (_ for _ in ()).throw(AssertionError("must not update")),
    )

    with pytest.raises(RuntimeError, match="Target not found"):
        process_entities(
            ["missing.database.schema.table"],
            [],
            {"customer_id": csv_row()},
        )


def test_report_only_builds_plan_without_updating(monkeypatch) -> None:
    source = table()
    monkeypatch.setattr(Tables, "retrieve_by_name", lambda *_args, **_kwargs: source)
    monkeypatch.setattr(
        Tables,
        "update",
        lambda *_: (_ for _ in ()).throw(AssertionError("report-only must not update")),
    )

    summary = process_entities(
        ["sample.database.schema.customers"],
        [],
        {"customer_id": csv_row()},
        report_only=True,
    )

    assert summary.entities_with_matches == 1
    assert summary.entities_updated == 0


def test_failed_facade_update_is_not_counted(monkeypatch) -> None:
    source = table()
    monkeypatch.setattr(Tables, "retrieve_by_name", lambda *_args, **_kwargs: source)
    monkeypatch.setattr(Tables, "update", lambda *_: None)

    summary = process_entities(
        ["sample.database.schema.customers"],
        [],
        {"customer_id": csv_row()},
    )

    assert summary.entities_updated == 0
