import logging
from typing import Iterable

from metadata.generated.schema.api.data.createDatabase import CreateDatabaseRequest
from metadata.generated.schema.api.data.createDatabaseSchema import (
    CreateDatabaseSchemaRequest,
)
from metadata.generated.schema.api.data.createTable import CreateTableRequest
from metadata.generated.schema.api.services.createDatabaseService import (
    CreateDatabaseServiceRequest,
)
from metadata.generated.schema.entity.data.database import Database
from metadata.generated.schema.entity.data.databaseSchema import DatabaseSchema
from metadata.generated.schema.entity.data.table import (
    Column,
    Table,
    TablePartition,
    TableProfilerConfig,
)
from metadata.generated.schema.entity.services.databaseService import (
    DatabaseConnection,
    DatabaseService,
)
from metadata.generated.schema.type.entityReference import EntityReference
from metadata.ingestion.ometa.ometa_api import OpenMetadata
from metadata.utils import fqn

from rename.helpers import get_owner, get_table_constraint, get_tag_label
from rename.runner import TopologyRunner
from rename.topology import ServiceTopology, TopologyContext, TopologyNode


class DatabaseServiceTopology(ServiceTopology):
    """
    Defines the hierarchy in Database Services.
    service -> db -> schema -> table.
    """

    root = TopologyNode(
        producer="get_services",
        processor="create_database_service",
        children=["database"],
    )
    database = TopologyNode(
        producer="get_databases",
        processor="create_database",
        children=["database_schema"],
    )
    database_schema = TopologyNode(
        producer="get_database_schemas",
        processor="create_database_schema",
        children=["table"],
    )
    table = TopologyNode(
        producer="get_tables",
        processor="create_table",
    )


class DatabaseServiceSource(TopologyRunner):
    topology = DatabaseServiceTopology()
    context = TopologyContext()

    def __init__(
        self, input_service_name: str, output_service_name: str, metadata: OpenMetadata
    ):
        self.input_service_name = input_service_name
        self.output_service_name = output_service_name
        self.metadata = metadata

    def get_services(self) -> Iterable[dict]:
        for service in self.list_all_raw_entities(entity=DatabaseService, fields=["*"]):
            if service.get("name") == self.input_service_name:
                yield service

    def create_database_service(self, service: dict) -> None:
        logging.info(f"Processing service {service.get('name')}")

        # update context
        self.context.database_service = self.metadata.create_or_update(
            CreateDatabaseServiceRequest(
                name=self.output_service_name,
                displayName=service.get("displayName"),
                description=service.get("description"),
                owner=get_owner(service),
                serviceType=service.get("serviceType"),
                connection=DatabaseConnection.parse_obj(service.get("connection")),
            )
        )

    def get_databases(self) -> Iterable[dict]:
        yield from self.list_all_raw_entities(
            entity=Database,
            params={"service": self.input_service_name},
        )

    def create_database(self, database: dict) -> None:
        logging.info(f"Processing database {database.get('name')}")

        self.context.database = self.metadata.create_or_update(
            CreateDatabaseRequest(
                name=database.get("name"),
                displayName=database.get("displayName"),
                description=database.get("description"),
                owner=get_owner(database),
                service=EntityReference(
                    id=self.context.database_service.id,
                    type="databaseService",
                ),
                default=database.get("default"),
            )
        )

    def get_database_schemas(self) -> Iterable[dict]:
        yield from self.list_all_raw_entities(
            entity=DatabaseSchema,
            params={
                "database": fqn.build(
                    metadata=self.metadata,
                    entity_type=Database,
                    service_name=self.input_service_name,
                    database_name=self.context.database.name.__root__,
                )
            },
        )

    def create_database_schema(self, schema: dict) -> None:
        logging.info(f"Processing database_schema {schema.get('name')}")

        self.context.database_schema = self.metadata.create_or_update(
            CreateDatabaseSchemaRequest(
                name=schema.get("name"),
                displayName=schema.get("displayName"),
                description=schema.get("description"),
                owner=get_owner(schema),
                database=EntityReference(
                    id=self.context.database.id,
                    type="database",
                ),
            )
        )

    def get_tables(self) -> Iterable[dict]:
        yield from self.list_all_raw_entities(
            entity=Table,
            params={
                "database": fqn.build(
                    metadata=self.metadata,
                    entity_type=DatabaseSchema,
                    service_name=self.input_service_name,
                    database_name=self.context.database.name.__root__,
                    schema_name=self.context.database_schema.name.__root__,
                )
            },
            fields=["*"],
        )

    def create_table(self, table: dict) -> None:
        logging.info(f"Processing table {table.get('name')}")

        try:
            self.metadata.create_or_update(
                CreateTableRequest(
                    name=table.get("name"),
                    displayName=table.get("displayName"),
                    description=table.get("description"),
                    owner=get_owner(table),
                    databaseSchema=EntityReference(
                        id=self.context.database_schema.id,
                        type="databaseSchema",
                    ),
                    tableType=table.get("tableType"),
                    columns=[
                        Column.parse_obj(column) for column in table.get("columns")
                    ],
                    tableConstraints=get_table_constraint(table.get("tableConstraints"))
                    if table.get("tableConstraints")
                    else None,
                    tablePartition=TablePartition.parse_obj(table.get("tablePartition"))
                    if table.get("tablePartition")
                    else None,
                    tableProfilerConfig=TableProfilerConfig.parse_obj(
                        table.get("tableProfilerConfig")
                    )
                    if table.get("tableProfilerConfig")
                    else None,
                    viewDefinition=table.get("viewDefinition"),
                    tags=get_tag_label(table),
                )
            )
        except Exception as err:
            logging.error(f"Error creating table from [{table}] due to [{err}]")
            logging.error(table.get("tableConstraints"))
