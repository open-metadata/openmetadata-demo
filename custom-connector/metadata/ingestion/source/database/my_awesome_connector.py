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

    def __init__(self, metadata_config: OpenMetadataConnection):
        self.metadata_config = metadata_config
        self.status = MyAwesomeConnectorStatus()

    @classmethod
    def create(
            cls, _: dict, metadata_config: OpenMetadataConnection
    ) -> "MyAwesomeConnector":

        return cls(metadata_config)

    def prepare(self):
        pass

    def next_record(self) -> Iterable[Entity]:
        pass

    def get_status(self) -> SourceStatus:
        return self.status

    def test_connection(self) -> None:
        pass

    def close(self):
        pass

