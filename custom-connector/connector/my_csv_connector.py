#  Copyright 2021 Collate
#  Licensed under the Apache License, Version 2.0 (the "License");
#  you may not use this file except in compliance with the License.
#  You may obtain a copy of the License at
#  http://www.apache.org/licenses/LICENSE-2.0
#  Unless required by applicable law or agreed to in writing, software
#  distributed under the License is distributed on an "AS IS" BASIS,
#  WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
#  See the License for the specific language governing permissions and
#  limitations under the License.
"""
Custom Database Service Extracting metadata from a CSV file
"""
import csv
import traceback

from pydantic import BaseModel, ValidationError, validator
from pathlib import Path
from typing import Iterable, Optional, List, Dict, Any

from metadata.ingestion.api.common import Entity
from metadata.ingestion.api.models import Either
from metadata.generated.schema.entity.services.ingestionPipelines.status import StackTraceError
from metadata.ingestion.api.steps import Source, InvalidSourceException
from metadata.generated.schema.entity.services.connections.metadata.openMetadataConnection import (
    OpenMetadataConnection,
)
from metadata.generated.schema.entity.services.connections.database.customDatabaseConnection import (
    CustomDatabaseConnection,
)
from metadata.generated.schema.entity.data.database import Database
from metadata.generated.schema.entity.data.databaseSchema import DatabaseSchema
from metadata.generated.schema.api.data.createDatabaseSchema import (
    CreateDatabaseSchemaRequest,
)
from metadata.generated.schema.api.data.createDatabase import CreateDatabaseRequest
from metadata.generated.schema.entity.services.databaseService import (
    DatabaseService,
)
from metadata.generated.schema.entity.data.table import (
    Column,
)
from metadata.generated.schema.metadataIngestion.workflow import (
    Source as WorkflowSource,
)
from metadata.generated.schema.api.data.createTable import CreateTableRequest
from metadata.ingestion.ometa.ometa_api import OpenMetadata
from metadata.utils.logger import ingestion_logger

logger = ingestion_logger()


class InvalidCsvConnectorException(Exception):
    """
    Sample data is not valid to be ingested
    """


class CsvModel(BaseModel):
    name: str
    column_names: List[str]
    column_types: List[str]

    @validator("column_names", "column_types", pre=True)
    def str_to_list(cls, value):
        """
        Suppose that the internal split is in ;
        """
        return value.split(";")


class CsvConnector(Source):
    """
    Custom connector to ingest Database metadata.

    We'll suppose that we can read metadata from a CSV
    with a custom database name from a business_unit connection option.
    """

    def __init__(self, config: WorkflowSource, metadata: OpenMetadata):
        self.config = config
        self.metadata = metadata

        self.service_connection = config.serviceConnection.root.config

        self.source_directory: str = (
            self.service_connection.connectionOptions.root.get("source_directory")
        )
        if not self.source_directory:
            raise InvalidCsvConnectorException(
                "Missing source_directory connection option"
            )

        self.business_unit: str = (
            self.service_connection.connectionOptions.root.get("business_unit")
        )
        if not self.business_unit:
            raise InvalidCsvConnectorException(
                "Missing business_unit connection option"
            )

        self.data: Optional[List[CsvModel]] = None

        super().__init__()

    @classmethod
    def create(
        cls, config_dict: dict, metadata: OpenMetadata, pipeline_name: Optional[str] = None
    ) -> "CsvConnector":
        config: WorkflowSource = WorkflowSource.model_validate(config_dict)
        connection: CustomDatabaseConnection = config.serviceConnection.root.config
        if not isinstance(connection, CustomDatabaseConnection):
            raise InvalidSourceException(
                f"Expected CustomDatabaseConnection, but got {connection}"
            )
        return cls(config, metadata)

    @staticmethod
    def read_row_safe(row: Dict[str, Any]):
        try:
            return CsvModel.parse_obj(row)
        except ValidationError:
            logger.warning(f"Error parsing row {row}. Skipping it.")

    def prepare(self):
        # Validate that the file exists
        source_data = Path(self.source_directory)
        if not source_data.exists():
            raise InvalidCsvConnectorException("Source Data path does not exist")

        try:
            with open(source_data, "r", encoding="utf-8") as file:
                reader = csv.DictReader(file)
                self.data = [self.read_row_safe(row) for row in reader]
        except Exception as exc:
            logger.error("Unknown error reading the source file")
            raise exc

    def yield_create_request_database_service(self):
        yield Either(
            right=self.metadata.get_create_service_from_source(
                entity=DatabaseService, config=self.config
            )
        )

    def yield_business_unit_db(self):
        # Pick up the service we just created (if not UI)
        service_entity: DatabaseService = self.metadata.get_by_name(
            entity=DatabaseService, fqn=self.config.serviceName
        )

        yield Either(
            right=CreateDatabaseRequest(
                name=self.business_unit,
                service=service_entity.fullyQualifiedName,
            )
        )

    def yield_default_schema(self):
        # Pick up the service we just created (if not UI)
        database_entity: Database = self.metadata.get_by_name(
            entity=Database, fqn=f"{self.config.serviceName}.{self.business_unit}"
        )

        yield Either(
            right=CreateDatabaseSchemaRequest(
                name="default",
                database=database_entity.fullyQualifiedName,
            )
        )

    def yield_data(self):
        """
        Iterate over the data list to create tables
        """
        database_schema: DatabaseSchema = self.metadata.get_by_name(
            entity=DatabaseSchema,
            fqn=f"{self.config.serviceName}.{self.business_unit}.default",
        )

        # Let's suppose we had a failure we want to track
        try:
            1 / 0
        except Exception:
            yield Either(
                left=StackTraceError(
                    name="My Error",
                    error="Demoing one error",
                    stackTrace=traceback.format_exc(),
                )
            )

        for row in self.data:
            yield Either(
                right=CreateTableRequest(
                    name=row.name,
                    databaseSchema=database_schema.fullyQualifiedName,
                    columns=[
                        Column(
                            name=model_col[0],
                            dataType=model_col[1],
                        )
                        for model_col in zip(row.column_names, row.column_types)
                    ],
                )
            )

    def _iter(self) -> Iterable[Entity]:
        yield from self.yield_create_request_database_service()
        yield from self.yield_business_unit_db()
        yield from self.yield_default_schema()
        yield from self.yield_data()

    def test_connection(self) -> None:
        pass

    def close(self):
        pass
