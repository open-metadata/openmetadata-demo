"""Update named OpenMetadata assets from a fully parsed column CSV."""

from __future__ import annotations

import argparse
import csv
import logging
import os
from collections.abc import Mapping, Sequence
from dataclasses import dataclass
from pathlib import Path
from typing import Any

from metadata.generated.schema.type.basic import Markdown
from metadata.ingestion.ometa.utils import model_str
from metadata.sdk import DashboardDataModels, Tables, configure, reset
from pydantic import BaseModel, ConfigDict, Field, ValidationError

logger = logging.getLogger(__name__)
REQUIRED_ENV = ("OPENMETADATA_HOST", "OPENMETADATA_JWT_TOKEN")


class CSVColumnSchema(BaseModel):
    """Fields consumed from an OpenMetadata column CSV export."""

    model_config = ConfigDict(populate_by_name=True)

    column_name: str = Field(alias="column.name*")
    column_display_name: str | None = Field(alias="column.displayName", default=None)
    column_description: str | None = Field(alias="column.description", default=None)
    column_data_type_display: str | None = Field(alias="column.dataTypeDisplay", default=None)
    column_data_type: str = Field(alias="column.dataType*")
    column_array_data_type: str | None = Field(alias="column.arrayDataType", default=None)
    column_data_length: str | None = Field(alias="column.dataLength", default=None)
    column_tags: str | None = Field(alias="column.tags", default=None)
    column_glossary_terms: str | None = Field(alias="column.glossaryTerms", default=None)


@dataclass(frozen=True)
class ProcessSummary:
    """Counts reported after processing an importer run."""

    entities_processed: int
    entities_with_matches: int
    total_matches: int
    entities_updated: int


def parse_arguments(argv: Sequence[str] | None = None) -> argparse.Namespace:
    """Parse explicit asset targets without accepting credentials on the CLI."""
    parser = argparse.ArgumentParser(
        description="Import column metadata into explicitly named OpenMetadata assets"
    )
    parser.add_argument(
        "--csv-path", required=True, help="Path to the CSV file containing metadata"
    )
    parser.add_argument(
        "--table-fqn",
        action="append",
        default=[],
        help="Table FQN to update; repeat for multiple tables",
    )
    parser.add_argument(
        "--dashboard-data-model-fqn",
        action="append",
        default=[],
        help="Dashboard data model FQN to update; repeat for multiple models",
    )
    parser.add_argument(
        "--report-only",
        action="store_true",
        help="Build and report the update plan without mutating assets",
    )
    args = parser.parse_args(argv)
    if not args.table_fqn and not args.dashboard_data_model_fqn:
        parser.error("at least one --table-fqn or --dashboard-data-model-fqn is required")
    return args


def validate_environment(environ: Mapping[str, str] | None = None) -> None:
    """Require standard credentials before configuring the SDK."""
    values = os.environ if environ is None else environ
    missing = [name for name in REQUIRED_ENV if not values.get(name)]
    if missing:
        raise ValueError(f"Missing required environment variables: {', '.join(missing)}")


def clean_column_name(column_name: str) -> str:
    """Remove control and zero-width characters from a column name."""
    return "".join(
        character for character in column_name if ord(character) >= 32 and ord(character) != 8203
    ).strip()


def load_csv_data(csv_path: str | Path) -> dict[str, CSVColumnSchema]:
    """Parse and validate the complete CSV before any server request."""
    rows: dict[str, CSVColumnSchema] = {}
    failures: list[int] = []
    with Path(csv_path).open(encoding="utf-8", newline="") as file:
        for row_number, raw_row in enumerate(csv.DictReader(file), 2):
            try:
                row = CSVColumnSchema.model_validate(raw_row)
            except ValidationError:
                failures.append(row_number)
                continue
            row.column_name = clean_column_name(row.column_name)
            rows[row.column_name] = row
    if failures:
        lines = ", ".join(str(number) for number in failures)
        raise ValueError(f"Invalid CSV rows: {lines}")
    return rows


def matching_rows(entity: Any, csv_data: dict[str, CSVColumnSchema]) -> list[CSVColumnSchema]:
    """Return CSV rows that match columns on an entity."""
    if not getattr(entity, "columns", None):
        return []
    return [
        csv_data[model_str(column.name)]
        for column in entity.columns
        if model_str(column.name) in csv_data
    ]


def build_updated_entity(entity: Any, matches: list[CSVColumnSchema]) -> Any | None:
    """Return a deep-copied destination, or None when no value changes."""
    updated_entity = entity.model_copy(deep=True)
    updates_made = False
    rows_by_name = {row.column_name: row for row in matches}
    for column in updated_entity.columns:
        row = rows_by_name.get(model_str(column.name))
        if not row:
            continue
        if row.column_description and row.column_description.strip():
            requested_description = row.column_description.strip()
            current_description = model_str(column.description) if column.description else None
            if current_description != requested_description:
                column.description = Markdown(root=requested_description)
                updates_made = True
        if row.column_display_name and row.column_display_name.strip():
            requested_display_name = row.column_display_name.strip()
            current_display_name = model_str(column.displayName) if column.displayName else None
            if current_display_name != requested_display_name:
                column.displayName = requested_display_name
                updates_made = True
    return updated_entity if updates_made else None


def _unique(values: Sequence[str]) -> list[str]:
    return list(dict.fromkeys(values))


def process_entities(
    table_fqns: Sequence[str],
    dashboard_data_model_fqns: Sequence[str],
    csv_data: dict[str, CSVColumnSchema],
    report_only: bool = False,
) -> ProcessSummary:
    """Retrieve every authorized target, build all changes, then update."""
    targets = [(Tables, fqn) for fqn in _unique(table_fqns)]
    targets += [(DashboardDataModels, fqn) for fqn in _unique(dashboard_data_model_fqns)]
    retrieved: list[tuple[Any, Any]] = []
    for facade, fqn in targets:
        entity = facade.retrieve_by_name(fqn, nullable=True)
        if entity is None:
            raise RuntimeError(f"Target not found: {fqn}")
        retrieved.append((facade, entity))

    matched = total_matches = 0
    planned: list[tuple[Any, Any]] = []
    for facade, entity in retrieved:
        matches = matching_rows(entity, csv_data)
        if not matches:
            continue
        matched += 1
        total_matches += len(matches)
        destination = build_updated_entity(entity, matches)
        if destination is not None:
            planned.append((facade, destination))

    updated = 0
    if not report_only:
        for facade, destination in planned:
            if facade.update(destination) is not None:
                updated += 1
    return ProcessSummary(len(retrieved), matched, total_matches, updated)


def main(argv: Sequence[str] | None = None) -> int:
    """Run the importer with environment-only credentials."""
    logging.basicConfig(level=logging.INFO, format="%(levelname)s: %(message)s")
    try:
        args = parse_arguments(argv)
        validate_environment()
        csv_data = load_csv_data(args.csv_path)
        configure()
        try:
            summary = process_entities(
                args.table_fqn,
                args.dashboard_data_model_fqn,
                csv_data,
                args.report_only,
            )
        finally:
            reset()
    except (ValueError, RuntimeError) as exc:
        logger.error("CSV import failed: %s", exc)
        return 1
    except Exception as exc:
        logger.error("CSV import failed: %s", type(exc).__name__)
        return 1

    logger.info("Entities processed: %d", summary.entities_processed)
    logger.info("Entities with matches: %d", summary.entities_with_matches)
    logger.info("Column matches: %d", summary.total_matches)
    logger.info("Entities updated: %d", summary.entities_updated)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
