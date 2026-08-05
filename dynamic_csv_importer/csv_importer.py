"""Update existing OpenMetadata column descriptions and display names from CSV."""

import argparse
import csv
import logging
import os
from collections.abc import Generator, Sequence
from dataclasses import dataclass
from enum import Enum
from pathlib import Path

from metadata.generated.schema.entity.data.dashboardDataModel import (
    DashboardDataModel,
)
from metadata.generated.schema.entity.data.table import Table
from metadata.generated.schema.entity.services.connections.metadata.openMetadataConnection import (  # noqa: E501
    AuthProvider,
    OpenMetadataConnection,
)
from metadata.generated.schema.security.client.openMetadataJWTClientConfig import (
    OpenMetadataJWTClientConfig,
)
from metadata.generated.schema.type.basic import Markdown
from metadata.ingestion.ometa.ometa_api import OpenMetadata
from metadata.ingestion.ometa.utils import model_str
from pydantic import BaseModel, ConfigDict, Field, ValidationError

logger = logging.getLogger(__name__)

ALL_ENTITIES = [Table, DashboardDataModel]


class SupportedEntities(Enum):
    """Entity collections supported by the importer."""

    ALL = "all"
    TABLES = Table.__name__
    DASHBOARD_DATA_MODEL = DashboardDataModel.__name__


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
    """Parse CLI options, using standard OpenMetadata environment variables."""
    host = os.environ.get("OPENMETADATA_HOST")
    token = os.environ.get("OPENMETADATA_JWT_TOKEN")
    parser = argparse.ArgumentParser(
        description="Import column metadata from CSV into OpenMetadata"
    )
    parser.add_argument(
        "--csv-path", required=True, help="Path to the CSV file containing metadata"
    )
    parser.add_argument(
        "--entities",
        choices=[entity.value for entity in SupportedEntities],
        default=SupportedEntities.ALL.value,
        help="Entity types to process (default: all)",
    )
    parser.add_argument(
        "--url",
        default=host,
        required=host is None,
        help="OpenMetadata API URL; defaults to OPENMETADATA_HOST",
    )
    parser.add_argument(
        "--jwt-token",
        default=token,
        required=token is None,
        help="JWT token; defaults to OPENMETADATA_JWT_TOKEN",
    )
    parser.add_argument(
        "--report-only",
        action="store_true",
        help="Report matches without updating entities",
    )
    return parser.parse_args(argv)


def clean_column_name(column_name: str) -> str:
    """Remove control and zero-width characters from a column name."""
    return "".join(
        character for character in column_name if ord(character) >= 32 and ord(character) != 8203
    ).strip()


def load_csv_data(csv_path: str | Path) -> dict[str, CSVColumnSchema]:
    """Load valid rows from an OpenMetadata column CSV export."""
    rows: dict[str, CSVColumnSchema] = {}
    with Path(csv_path).open(encoding="utf-8", newline="") as file:
        for row_number, raw_row in enumerate(csv.DictReader(file), 2):
            try:
                row = CSVColumnSchema.model_validate(raw_row)
            except ValidationError as exc:
                logger.warning("Skipping invalid CSV row %d: %s", row_number, exc)
                continue
            row.column_name = clean_column_name(row.column_name)
            rows[row.column_name] = row
    return rows


def initialize_ometa_client(url: str, jwt_token: str) -> OpenMetadata:
    """Construct the OpenMetadata 2.0 client without performing API calls."""
    config = OpenMetadataConnection(
        hostPort=url,
        authProvider=AuthProvider.openmetadata,
        securityConfig=OpenMetadataJWTClientConfig(jwtToken=jwt_token),
    )
    return OpenMetadata(config=config)


def _iter_entity_type(ometa: OpenMetadata, entity_type: type) -> Generator:
    """Yield one entity type through the paginated API."""
    after = None
    while True:
        page = ometa.list_entities(entity=entity_type, limit=100, after=after)
        yield from page.entities
        if not page.after:
            return
        after = page.after


def get_entities_to_process(ometa: OpenMetadata, entities: str) -> Generator:
    """Yield the selected supported entities."""
    if entities == SupportedEntities.ALL.value:
        entity_types = ALL_ENTITIES
    elif entities == SupportedEntities.TABLES.value:
        entity_types = [Table]
    else:
        entity_types = [DashboardDataModel]
    for entity_type in entity_types:
        yield from _iter_entity_type(ometa, entity_type)


def matching_rows(entity, csv_data: dict[str, CSVColumnSchema]) -> list[CSVColumnSchema]:
    """Return CSV rows that match columns on an entity."""
    if not getattr(entity, "columns", None):
        return []
    return [
        csv_data[model_str(column.name)]
        for column in entity.columns
        if model_str(column.name) in csv_data
    ]


def build_updated_entity(entity, matches: list[CSVColumnSchema]):
    """Return an updated entity copy, or None when no value changes."""
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


def process_entities(
    ometa: OpenMetadata,
    entities: str,
    csv_data: dict[str, CSVColumnSchema],
    report_only: bool = False,
) -> ProcessSummary:
    """Match and optionally patch entities, returning deterministic counts."""
    processed = matched = total_matches = updated = 0
    for entity in get_entities_to_process(ometa, entities):
        processed += 1
        matches = matching_rows(entity, csv_data)
        if not matches:
            continue
        matched += 1
        total_matches += len(matches)
        destination = build_updated_entity(entity, matches)
        if not report_only and destination is not None:
            result = ometa.patch(
                entity=type(entity),
                source=entity,
                destination=destination,
                skip_on_failure=False,
            )
            if result is not None:
                updated += 1
    return ProcessSummary(processed, matched, total_matches, updated)


def main(argv: Sequence[str] | None = None) -> int:
    """Run the importer CLI."""
    logging.basicConfig(
        level=logging.INFO,
        format="[%(asctime)s] %(levelname)-8s - %(message)s",
    )
    args = parse_arguments(argv)
    csv_data = load_csv_data(args.csv_path)
    client = initialize_ometa_client(args.url, args.jwt_token)
    summary = process_entities(client, args.entities, csv_data, args.report_only)
    logger.info("Entities processed: %d", summary.entities_processed)
    logger.info("Entities with matches: %d", summary.entities_with_matches)
    logger.info("Column matches: %d", summary.total_matches)
    logger.info("Entities updated: %d", summary.entities_updated)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
