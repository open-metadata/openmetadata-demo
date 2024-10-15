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
Custom Database Service Extracting metadata from a Protobuf file
"""
import glob
import importlib
import os
import shutil
import sys
import traceback
from distutils.dir_util import copy_tree
from enum import Enum
from pathlib import Path
from typing import Iterable, List, Optional, Type, Union

from connector.custom_parser.protobuf_parser import ProtobufParser 
from metadata.utils.helpers import snake_to_camel

import subprocess

from metadata.generated.schema.api.data.createDatabase import CreateDatabaseRequest
from metadata.generated.schema.api.data.createDatabaseSchema import (
    CreateDatabaseSchemaRequest,
)
from metadata.generated.schema.api.data.createTable import CreateTableRequest
from metadata.generated.schema.entity.data.database import Database
from metadata.generated.schema.entity.data.databaseSchema import DatabaseSchema
from metadata.generated.schema.entity.data.table import Column
from metadata.generated.schema.entity.services.connections.database.customDatabaseConnection import (
    CustomDatabaseConnection,
)
from metadata.generated.schema.entity.services.connections.metadata.openMetadataConnection import (
    OpenMetadataConnection,
)
from metadata.generated.schema.entity.services.databaseService import DatabaseService
from metadata.generated.schema.entity.services.ingestionPipelines.status import (
    StackTraceError,
)
from metadata.generated.schema.metadataIngestion.workflow import (
    Source as WorkflowSource,
)
from metadata.ingestion.api.common import Entity
from metadata.ingestion.api.models import Either
from metadata.ingestion.api.steps import Source
from metadata.ingestion.ometa.ometa_api import OpenMetadata
from metadata.utils.logger import ingestion_logger

logger = ingestion_logger()


class InvalidProtobufConnectorException(Exception):
    """
    Sample data is not valid to be ingested
    """


class AdvancedProtobufConnector(Source):
    """
    Custom connector to ingest Database metadata.

    We'll suppose that we can read metadata from a Protobuf
    with a custom database name from a business_unit connection option.
    """

    def __init__(self, config: WorkflowSource, metadata: OpenMetadata):
        self.config = config
        self.metadata = metadata

        self.service_connection = config.serviceConnection.root.config

        self.source_directory: str = self.service_connection.connectionOptions.root.get(
            "source_directory"
        )
        if not self.source_directory and not Path(self.staging_directory).exists():
            raise InvalidProtobufConnectorException(
                "Missing source_directory connection option"
            )

        self.staging_directory: str = (
            self.service_connection.connectionOptions.root.get("staging_directory")
        )
        if not self.staging_directory:
            raise InvalidProtobufConnectorException(
                "Missing staging_directory connection option"
            )
        self.generated_path = Path(self.staging_directory).joinpath("generated")
        self.generated_path.mkdir(parents=True, exist_ok=True)
        self.interface_path = Path(self.staging_directory).joinpath("interface")
        self.interface_path.mkdir(parents=True, exist_ok=True)
        copy_tree(str(self.source_directory), str(self.interface_path))

        self.business_unit: str = self.service_connection.connectionOptions.root.get(
            "business_unit"
        )
        if not self.business_unit:
            raise InvalidProtobufConnectorException(
                "Missing business_unit connection option"
            )

        self.data = None

        super().__init__()

    def prepare(self):
        # Validate that the file exists
        import re

        try:
            proto_file_list = [
                os.path.join(dirpath, f)
                for (dirpath, dirnames, filenames) in os.walk(str(self.interface_path))
                for f in filenames
                if f.endswith(".proto")
            ]
            for proto_file in proto_file_list:
                with open(proto_file, "r", encoding="utf-8") as file:
                    self.data = file.read()
                    description_pattern = re.compile(r'\[\(description\)\s*=\s*".*?"\]')
                    self.data = description_pattern.sub("", self.data)
                    subprocess.run(
                        [
                            "protoc",
                            proto_file,
                            f"--proto_path={self.interface_path}",
                            f"--python_out={self.generated_path}",
                        ]
                    )

        except Exception as exc:
            logger.error("Unknown error reading the source file")
            raise exc

    @classmethod
    def create(
        cls,
        config_dict: dict,
        metadata: OpenMetadata,
        pipeline_name: Optional[str] = None,
    ) -> "ProtobufConnector":
        config: WorkflowSource = WorkflowSource.parse_obj(config_dict)
        connection: CustomDatabaseConnection = config.serviceConnection.root.config
        if not isinstance(connection, CustomDatabaseConnection):
            raise InvalidProtobufConnectorException(
                f"Expected CustomDatabaseConnection, but got {connection}"
            )
        return cls(config, metadata)

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
        sys.path.append(str(self.generated_path))
        python_file_list = [
            os.path.join(dirpath, f)
            for (dirpath, dirnames, filenames) in os.walk(str(self.generated_path))
            for f in filenames
            if f.endswith("_pb2.py")
        ]
        for proto_file in python_file_list:
            try:
                py_file = glob.glob(proto_file)[0]
                module_name = py_file.replace(str(self.generated_path),"").replace(".py","").replace("/",".")[1:]
                message = importlib.import_module(module_name)
                schema_name = (Path(py_file).stem).replace("_pb2", "")

                # get the class and create a object instance
                class_ = getattr(message, snake_to_camel(schema_name))
                instance = class_()
                columns = ProtobufParser.parse_protobuf_schema(instance, schema_name, cls=Column) or []
                yield Either(
                    right=CreateTableRequest(
                        name=schema_name,
                        databaseSchema=database_schema.fullyQualifiedName,
                        columns=columns,
                    )
                )
            except Exception as exc:
                logger.error(f"Error reading the file {proto_file}: {exc}")
                logger.debug(traceback.format_exc())

    def _iter(self) -> Iterable[Entity]:
        yield from self.yield_create_request_database_service()
        yield from self.yield_business_unit_db()
        yield from self.yield_default_schema()
        yield from self.yield_data()

    def test_connection(self) -> None:
        pass

    def close(self):
        pass
