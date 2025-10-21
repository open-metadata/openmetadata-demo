import argparse
import csv
import logging
import sys
from enum import Enum
from pathlib import Path
from typing import List, Optional

from pydantic import BaseModel, Field, ConfigDict
from metadata.generated.schema.entity.data.table import Table
from metadata.generated.schema.entity.data.dashboardDataModel import DashboardDataModel
from metadata.ingestion.ometa.ometa_api import OpenMetadata
from metadata.ingestion.ometa.utils import model_str
from metadata.generated.schema.security.client.openMetadataJWTClientConfig import (
    OpenMetadataJWTClientConfig,
)
from metadata.generated.schema.entity.services.connections.metadata.openMetadataConnection import (
    AuthProvider,
    OpenMetadataConnection,
)

BASE_LOGGING_FORMAT = (
    "[%(asctime)s] %(levelname)-8s - %(message)s"
)

# Configure our own logger to avoid clashes with other libraries
logger = logging.getLogger(__name__)
logger.setLevel(logging.INFO)

# Clear any existing handlers
logger.handlers.clear()

# Create and configure stdout handler
handler = logging.StreamHandler(sys.stdout)
handler.setLevel(logging.INFO)
formatter = logging.Formatter(BASE_LOGGING_FORMAT, datefmt="%Y-%m-%d %H:%M:%S")
handler.setFormatter(formatter)
logger.addHandler(handler)
logger.propagate = False

ALL_ENTITIES = [Table, DashboardDataModel]

class SupportedEntities(Enum):
    ALL = "all"
    TABLES = Table.__name__
    DASHBOARD_DATA_MODEL = DashboardDataModel.__name__


class CSVColumnSchema(BaseModel):
    model_config = ConfigDict(populate_by_name=True)
    
    column_name: str = Field(alias="column.name*")
    column_display_name: Optional[str] = Field(alias="column.displayName", default=None)
    column_description: Optional[str] = Field(alias="column.description", default=None)
    column_data_type_display: Optional[str] = Field(alias="column.dataTypeDisplay", default=None)
    column_data_type: str = Field(alias="column.dataType*")
    column_array_data_type: Optional[str] = Field(alias="column.arrayDataType", default=None)
    column_data_length: Optional[str] = Field(alias="column.dataLength", default=None)
    column_tags: Optional[str] = Field(alias="column.tags", default=None)
    column_glossary_terms: Optional[str] = Field(alias="column.glossaryTerms", default=None)


def parse_arguments():
    parser = argparse.ArgumentParser(description="Import metadata from CSV files into OpenMetadata")
    parser.add_argument(
        "--csv-path",
        required=True,
        help="Path to the CSV file containing metadata"
    )
    parser.add_argument(
        "--entities",
        choices=[e.value for e in SupportedEntities],
        default=SupportedEntities.ALL.value,
        help="Entity types to process (default: all)"
    )
    parser.add_argument(
        "--url",
        required=True,
        help="OpenMetadata/Collate instance URL"
    )
    parser.add_argument(
        "--jwt-token",
        required=True,
        help="JWT token for authentication"
    )
    parser.add_argument(
        "--report-only",
        action="store_true",
        help="Only report matches without updating entities (default: False)",
        default=False,
    )
    return parser.parse_args()


def clean_column_name(column_name: str) -> str:
    """Clean column name by removing invisible Unicode characters"""
    # Remove zero-width characters and other invisible Unicode
    cleaned = ''.join(char for char in column_name if ord(char) >= 32 and ord(char) != 8203)
    return cleaned.strip()

def load_csv_data(csv_path: str) -> dict[str, CSVColumnSchema]:
    csv_data = {}
    try:
        with open(csv_path, 'r', encoding='utf-8') as file:
            reader = csv.DictReader(file)
            for row_num, row in enumerate(reader, 1):
                try:
                    csv_row = CSVColumnSchema(**row)
                    cleaned_name = clean_column_name(csv_row.column_name)

                    # Update the cleaned name
                    csv_row.column_name = cleaned_name
                    csv_data[cleaned_name] = csv_row
                except Exception as e:
                    logger.info(f"Error parsing row {row_num} {row}: {e}")
                    continue
    except FileNotFoundError:
        logger.info(f"Error: CSV file not found at {csv_path}")
        sys.exit(1)
    except Exception as e:
        logger.info(f"Error reading CSV file: {e}")
        sys.exit(1)
    
    logger.info(f"Loaded {len(csv_data)} unique column names from CSV")
    if len(csv_data) <= 10:
        logger.info("Sample column names:")
        for i, key in enumerate(list(csv_data.keys())[:5]):
            logger.info(f"  '{key}' (length: {len(key)})")
    
    return csv_data


def initialize_ometa_client(url: str, jwt_token: str) -> OpenMetadata:
    try:
        config = OpenMetadataConnection(
            hostPort=url,
            authProvider=AuthProvider.openmetadata,
            securityConfig= OpenMetadataJWTClientConfig(jwtToken=jwt_token)
        )
        return OpenMetadata(config=config)
    except Exception as e:
        logger.info(f"Error initializing OpenMetadata client: {e}")
        sys.exit(1)


def get_entities_to_process(ometa: OpenMetadata, entities: str):
    def get_entity_generator(entity_class):
        """Generator that yields entities using pagination"""
        limit = 100
        after = None
        
        entity_list = ometa.list_entities(
            entity=entity_class,
            limit=limit,
            after=after
        )
        
        while entity_list.entities:
            for entity in entity_list.entities:
                yield entity
                
            if not entity_list.after:
                break
                
            after = entity_list.after
            entity_list = ometa.list_entities(
                entity=entity_class,
                limit=limit,
                after=after
            )
    
    if entities == SupportedEntities.ALL.value:
        for type_ in ALL_ENTITIES:
            for entity in get_entity_generator(type_):
                yield entity
    elif entities == SupportedEntities.TABLES.value:
        for entity in get_entity_generator(Table):
            yield entity
    elif entities == SupportedEntities.DASHBOARD_DATA_MODEL.value:
        for entity in get_entity_generator(DashboardDataModel):
            yield entity


def match_columns(entity, csv_data: dict[str, CSVColumnSchema]):
    if not hasattr(entity, 'columns') or not entity.columns:
        return []
    
    matches = []
    
    for col in entity.columns:
        column_name = model_str(col.name)
        if column_name in csv_data:
            matches.append((entity, csv_data[column_name]))
    
    return matches


def update_entity_columns(ometa: OpenMetadata, entity, matches: list):
    """Update entity columns with CSV data"""
    if not matches:
        return False
    
    try:
        # Create a copy of the entity to modify
        updated_entity = entity.model_copy(deep=True)
        updates_made = False
        
        # Update matching columns
        for entity_match, csv_row in matches:
            for col in updated_entity.columns:
                column_name = model_str(col.name)
                if column_name == csv_row.column_name:

                    # Update description if provided
                    if csv_row.column_description and csv_row.column_description.strip():
                        old_desc = col.description if hasattr(col, 'description') else None
                        col.description = csv_row.column_description.strip()
                        updates_made = True

                    # Update display name if provided
                    if csv_row.column_display_name and csv_row.column_display_name.strip():
                        old_name = col.displayName if hasattr(col, 'displayName') else None
                        col.displayName = csv_row.column_display_name.strip()
                        updates_made = True

        if updates_made:
            return ometa.patch(entity=type(entity), source=entity, destination=updated_entity)

    except Exception as e:
        logger.error(f"Error updating entity {entity.fullyQualifiedName}: {e}")
        return False
    
    return False

def process_entities(ometa: OpenMetadata, entities: str, csv_data: dict[str, CSVColumnSchema], report_only: bool = False):
    entities_generator = get_entities_to_process(ometa, entities)
    
    total_matches = 0
    entities_processed = 0
    entities_with_matches = 0
    entities_updated = 0
    
    mode_text = "REPORT ONLY MODE" if report_only else "UPDATE MODE"
    logger.info(f"Running in {mode_text}")
    
    for entity in entities_generator:
        entities_processed += 1
        if entities_processed % 100 == 0:
            logger.info(f"Processed {entities_processed} entities...")
            
        matches = match_columns(entity, csv_data)
        if matches:
            entities_with_matches += 1
            total_matches += len(matches)
            
            if not report_only:
                if update_entity_columns(ometa, entity, matches):
                    entities_updated += 1

    entities_without_matches = entities_processed - entities_with_matches
    
    logger.info(f"\n=== SUMMARY ===")
    logger.info(f"Mode: {mode_text}")
    logger.info(f"Total entities processed: {entities_processed}")
    logger.info(f"Entities with matches: {entities_with_matches}")
    logger.info(f"Entities without matches: {entities_without_matches}")
    logger.info(f"Total column matches found: {total_matches}")
    logger.info(f"Entities successfully updated: {entities_updated}")


def main():
    args = parse_arguments()
    
    logger.info(f"Loading CSV data from: {args.csv_path}")
    csv_data = load_csv_data(args.csv_path)
    logger.info(f"Loaded {len(csv_data)} rows from CSV")
    
    logger.info(f"Initializing OpenMetadata client for: {args.url}")
    ometa = initialize_ometa_client(args.url, args.jwt_token)
    
    logger.info(f"Processing entities: {args.entities}")
    process_entities(ometa, args.entities, csv_data, args.report_only)


if __name__ == "__main__":
    # Debug mode - set DEBUG = True and modify values below for testing
    DEBUG = False
    
    if DEBUG:
        # Hardcoded values for debugging - modify these as needed
        class DebugArgs:
            csv_path = "sample_dbt_jaffle.csv"
            entities = "all"  # or "Table" or "DashboardDataModel"
            url = "http://localhost:8585/api"
            jwt_token = "eyJraWQiOiJHYjM4OWEtOWY3Ni1nZGpzLWE5MmotMDI0MmJrOTQzNTYiLCJ0eXAiOiJKV1QiLCJhbGciOiJSUzI1NiJ9.eyJzdWIiOiJhZG1pbiIsImlzQm90IjpmYWxzZSwiaXNzIjoib3Blbi1tZXRhZGF0YS5vcmciLCJpYXQiOjE2NjM5Mzg0NjIsImVtYWlsIjoiYWRtaW5Ab3Blbm1ldGFkYXRhLm9yZyJ9.tS8um_5DKu7HgzGBzS1VTA5uUjKWOCU0B_j08WXBiEC0mr0zNREkqVfwFDD-d24HlNEbrqioLsBuFRiwIWKc1m_ZlVQbG7P36RUxhuv2vbSp80FKyNM-Tj93FDzq91jsyNmsQhyNv_fNr3TXfzzSPjHt8Go0FMMP66weoKMgW2PbXlhVKwEuXUHyakLLzewm9UMeQaEiRzhiTMU3UkLXcKbYEJJvfNFcLwSl9W8JCO_l0Yj3ud-qt_nQYEZwqW6u5nfdQllN133iikV4fM5QZsMCnm8Rq1mvLR0y9bmJiD7fwM1tmJ791TUWqmKaTnP49U493VanKpUAfzIiOiIbhg"
            report_only = True  # Set to False to actually update entities
        
        args = DebugArgs()
        
        logger.info("=== DEBUG MODE ===")
        logger.info(f"CSV Path: {args.csv_path}")
        logger.info(f"Entities: {args.entities}")
        logger.info(f"URL: {args.url}")
        logger.info(f"JWT Token: {args.jwt_token[:20]}..." if len(args.jwt_token) > 20 else args.jwt_token)
        logger.info("==================")
        
        logger.info(f"Loading CSV data from: {args.csv_path}")
        csv_data = load_csv_data(args.csv_path)
        logger.info(f"Loaded {len(csv_data)} rows from CSV")
        
        logger.info(f"Initializing OpenMetadata client for: {args.url}")
        ometa = initialize_ometa_client(args.url, args.jwt_token)
        
        logger.info(f"Processing entities: {args.entities}")
        process_entities(ometa, args.entities, csv_data, args.report_only)
    else:
        main()

