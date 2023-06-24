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
Custom Database Service Source example
"""
from typing import Iterable, List

from metadata.ingestion.api.common import Entity
from metadata.ingestion.api.source import Source, SourceStatus
from metadata.generated.schema.entity.services.connections.metadata.openMetadataConnection import (
    OpenMetadataConnection,
)
from metadata.generated.schema.api.data.createDatabase import CreateDatabaseRequest
from metadata.generated.schema.entity.services.databaseService import (
    DatabaseService,
)
from metadata.generated.schema.metadataIngestion.workflow import (
    Source as WorkflowSource,
)
from metadata.generated.schema.type.entityReference import EntityReference
from metadata.ingestion.ometa.ometa_api import OpenMetadata
from metadata.utils.logger import ingestion_logger

logger = ingestion_logger()


class MyAwesomeConnectorStatus(SourceStatus):
    """
    Custom status. We'll track success and failures.
    """

    success: List[str] = []

    def scanned(self, record: str) -> None:
        self.success.append(record)
        logger.info(f"Scanned [{record}]")


class MyAwesomeConnector(Source):
    """
    Custom connector to ingest Database metadata
    """

    def __init__(self, config: WorkflowSource, metadata_config: OpenMetadataConnection):
        self.config = config
        self.metadata_config = metadata_config

        self.metadata = OpenMetadata(self.metadata_config)
        self.status = MyAwesomeConnectorStatus()

    @classmethod
    def create(
        cls, config_dict: dict, metadata_config: OpenMetadataConnection
    ) -> "MyAwesomeConnector":
        config: WorkflowSource = WorkflowSource.parse_obj(config_dict)
        return cls(config, metadata_config)

    def prepare(self):
        pass

    def yield_create_request_database_service(self, config: WorkflowSource):
        yield self.metadata.get_create_service_from_source(
            entity=DatabaseService, config=config
        )

    def next_record(self) -> Iterable[Entity]:
        yield from self.yield_create_request_database_service(self.config)

        service_entity: DatabaseService = self.metadata.get_by_name(
            entity=DatabaseService, fqn=self.config.serviceName
        )

        yield CreateDatabaseRequest(
            name="awesome-database",
            service=service_entity.fullyQualifiedName,
        )

    def get_status(self) -> SourceStatus:
        return self.status

    def test_connection(self) -> None:
        pass

    def close(self):
        pass
