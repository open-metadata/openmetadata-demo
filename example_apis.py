import json
from metadata.ingestion.ometa.ometa_api import OpenMetadata
from metadata.generated.schema.entity.services.connections.metadata.openMetadataConnection import (
    OpenMetadataConnection,
    AuthProvider
)

from metadata.generated.schema.security.client.openMetadataJWTClientConfig import (
    OpenMetadataJWTClientConfig
)

from metadata.generated.schema.api.services.createDatabaseService import (
    CreateDatabaseServiceRequest,
)
from metadata.generated.schema.entity.services.databaseService import (
    DatabaseService,
    DatabaseServiceType,
    DatabaseConnection,
)

from metadata.generated.schema.entity.services.connections.database.snowflakeConnection import (
    SnowflakeConnection
)

from metadata.generated.schema.api.data.createDatabase import (
    CreateDatabaseRequest,
)
from metadata.generated.schema.type.entityReference import EntityReference

from metadata.generated.schema.api.data.createDatabaseSchema import (
    CreateDatabaseSchemaRequest,
)

from metadata.generated.schema.api.data.createTable import CreateTableRequest
from metadata.generated.schema.entity.data.table import (
    Column,
    DataType,
    Table,
)
from metadata.generated.schema.api.data.createLocation import CreateLocationRequest
from metadata.generated.schema.api.data.createPipeline import CreatePipelineRequest
from metadata.generated.schema.api.data.createTopic import CreateTopicRequest
from metadata.generated.schema.api.lineage.addLineage import AddLineageRequest
from metadata.generated.schema.api.services.createStorageService import (
    CreateStorageServiceRequest,
)
from metadata.generated.schema.api.services.createPipelineService import (
    CreatePipelineServiceRequest,
)

from metadata.generated.schema.api.services.createMessagingService import (
    CreateMessagingServiceRequest,
)

from metadata.generated.schema.entity.services.connections.pipeline.airflowConnection import (AirflowConnection)
from metadata.generated.schema.entity.data.dashboard import Dashboard
from metadata.generated.schema.entity.data.database import Database
from metadata.generated.schema.entity.data.databaseSchema import DatabaseSchema
from metadata.generated.schema.entity.data.location import Location
from metadata.generated.schema.entity.data.pipeline import Pipeline, PipelineStatus, Task
from metadata.generated.schema.entity.services.dashboardService import DashboardService
from metadata.generated.schema.entity.services.databaseService import DatabaseService
from metadata.generated.schema.entity.services.messagingService import MessagingService
from metadata.generated.schema.entity.services.mlmodelService import MlModelService
from metadata.generated.schema.entity.services.pipelineService import PipelineService
from metadata.generated.schema.entity.services.storageService import StorageService

from metadata.generated.schema.api.lineage.addLineage import AddLineageRequest
from metadata.generated.schema.type.entityLineage import EntitiesEdge
from metadata.generated.schema.type import basic, entityReference, schema, tagLabel



# to connect to OpenMetadata Server
security_config = OpenMetadataJWTClientConfig(jwtToken="eyJraWQiOiJHYjM4OWEtOWY3Ni1nZGpzLWE5MmotMDI0MmJrOTQzNTYiLCJ0eXAiOiJKV1QiLCJhbGciOiJSUzI1NiJ9.eyJzdWIiOiJpbmdlc3Rpb24tYm90IiwiaXNCb3QiOnRydWUsImlzcyI6Im9wZW4tbWV0YWRhdGEub3JnIiwiaWF0IjoxNjcxNzMwMTEzLCJlbWFpbCI6ImluZ2VzdGlvbi1ib3RAb3Blbm1ldGFkYXRhLm9yZyJ9.KmoEq1WJHz5LDdmUZ_nmNT0X7lpuBmc4OUL4wnMcNfJOERiIzeSJQQ8AnM5p-ctw5byVHV3KnoTfZfU2DGcWYNsVrpTXuxqnDYM6CkC8fXxoTmk9U9AyAy_0N8zEuDVsUF2Vviw4fcnx_AXl0wYDJknDTv3FeJWxjuJjEBmQmonhvIJ9wm1e2QNx5xDfOPtnmitj7y__b3DPdxuTSdQcrMOciwKnd8kmgEscbsKfaG30iNgCUGWDmRaHuRX4QOhcvQ45WIFpkUFggsKLPCLGWZ_Vb0khv3R8mV0RMZAaIZ6a8fZVpi6Juad_nyhiUlkS4pwXywuFJeUJI4sm70KAew")
server_config = OpenMetadataConnection(hostPort="http://localhost:8585/api", securityConfig=security_config, authProvider=AuthProvider.openmetadata)
metadata = OpenMetadata(server_config)
metadata.health_check() # we are able to connect to OpenMetadata Server

# Create DatabaseService
#
#
create_service = CreateDatabaseServiceRequest(
    name="test-snowflake",
    serviceType=DatabaseServiceType.Snowflake,
    connection=DatabaseConnection(
        config=SnowflakeConnection(
            username="username",
            password="password",
            account="http://localhost:1234",
            warehouse="dw"
        )
    ),
)

service_entity = metadata.create_or_update(data=create_service)


# Create a Storage Service
#
create_storage_service_entity = CreateStorageServiceRequest(name='S3 Sample', serviceType='S3', description='S3 Object Store')
storage_service_entity = metadata.create_or_update(data=create_storage_service_entity)


# Create Pipeline Service
#
pipeline_service_json =json.loads("""
{
	"serviceType": "Airflow",
	"name": "sample_airflow1",
	"connection": {
                "config": {
                "type": "Airflow",
                "hostPort": "http://localhost:8080",
                "connection": {
                   "type": "Backend"
                 }
           }
	}
}
""")
create_pipeline_service_entity = CreatePipelineServiceRequest(**pipeline_service_json)
pipeline_service_entity = metadata.create_or_update(create_pipeline_service_entity)

# Create Messaging Service , Kafka
#
messaging_service_json = json.loads("""
{
  "serviceType": "Kafka",
  "name": "sample_kafka1",
  "connection": {
    "config": {
      "type": "Kafka",
      "bootstrapServers": "localhost:9092"
    }
  }
}
""")
create_messaging_service_entity = CreateMessagingServiceRequest(**messaging_service_json)
messaging_service_entity = metadata.create_or_update(create_messaging_service_entity)


# Create location
#

location_request = CreateLocationRequest(
    name="bucket_a",
    displayName="Bucket A",
    description="Bucket A",
    path="s3://bucket-a",
    locationType="Bucket",
    service=EntityReference(id=storage_service_entity.id, type="storageService")
)
location = metadata.create_or_update(location_request)

# Create Database
#
create_db = CreateDatabaseRequest(
    name="test-db",
    service=EntityReference(id=service_entity.id, type="databaseService"),
)

db_entity = metadata.create_or_update(create_db)


create_schema = CreateDatabaseSchemaRequest(
    name="test-schema",
    database=EntityReference(id=db_entity.id, type="database")
)

schema_entity = metadata.create_or_update(data=create_schema)

# We can prepare the EntityReference that will be needed
# in the next step!
schema_reference = EntityReference(
    id=schema_entity.id, name="test-schema", type="databaseSchema"
)


create_table = CreateTableRequest(
    name="dim_orders",
    databaseSchema=schema_reference,
    columns=[Column(name="id", dataType=DataType.BIGINT)],
)

table_entity = metadata.create_or_update(create_table)

table_a = CreateTableRequest(
    name="tableA",
    databaseSchema=EntityReference(
        id=schema_entity.id, name="test-schema", type="databaseSchema"
    ),
    columns=[Column(name="id", dataType=DataType.BIGINT)],
)

table_b = CreateTableRequest(
    name="tableB",
    databaseSchema=EntityReference(
        id=schema_entity.id, name="test-schema", type="databaseSchema"
    ),
    columns=[Column(name="id", dataType=DataType.BIGINT)],
)

table_a_entity = metadata.create_or_update(data=table_a)
table_b_entity = metadata.create_or_update(data=table_b)
metadata.patch_tag(Table,table_b_entity.id,'PII.None')
metadata.patch_tag(Table, table_b_entity.id, 'PII.None', False, 'remove')
metadata.patch_column_tag(table_b_entity.id.__root__, 'id', 'PII.None')
metadata.patch_column_tag(table_b_entity.id.__root__, 'id', 'PII.None', False, 'remove')

# Create pipeline
#
task = Task(name="ingest", taskUrl="http://localhost:8080/table_etl/ingest")
pipeline_request = CreatePipelineRequest(
    name="table_etl",
    displayName="Table ETL",
    description="Table ETL",
    pipelineUrl="http://localhost:8080/table_etl",
    tasks=[task],
    service=EntityReference(
        id=pipeline_service_entity.id, type="pipelineService"
    ),
)
pipeline = metadata.create_or_update(pipeline_request)

topic_request = CreateTopicRequest(
    name="customer_events",
    description="Kafka topic to capture the customer events such as location updates or profile updates",
    partitions=56,
    retentionSize=455858109,
    messageSchema=schema.Topic(
        schemaType="Avro",
        schemaText="{\"namespace\":\"org.open-metadata.kafka\",\"name\":\"Customer\",\"type\":\"record\",\"fields\":[{\"name\":\"id\",\"type\":\"string\"},{\"name\":\"first_name\",\"type\":\"string\"},{\"name\":\"last_name\",\"type\":\"string\"},{\"name\":\"email\",\"type\":\"string\"},{\"name\":\"address_line_1\",\"type\":\"string\"},{\"name\":\"address_line_2\",\"type\":\"string\"},{\"name\":\"post_code\",\"type\":\"string\"},{\"name\":\"country\",\"type\":\"string\"}]}",
    ),
    service=EntityReference(
        id=messaging_service_entity.id, type="messagingService"
    )
)
topic = metadata.create_or_update(topic_request)


add_lineage_request = AddLineageRequest(
    description="test lineage",
    edge=EntitiesEdge(
        fromEntity=EntityReference(id=table_a_entity.id, type="table"),
        toEntity=EntityReference(id=pipeline.id, type="pipeline"),
    ),
)

created_lineage = metadata.add_lineage(data=add_lineage_request)

add_lineage_request = AddLineageRequest(
    description="test lineage",
    edge=EntitiesEdge(
        fromEntity=EntityReference(id=pipeline.id, type="pipeline"),
        toEntity=EntityReference(id=table_b_entity.id, type="table"),
    ),
)

created_lineage = metadata.add_lineage(data=add_lineage_request)

## Fetching Users

from metadata.generated.schema.entity.teams.user import User

# The name is whatever comes before the @ in their email. For example, admin@openmetadata.org you can fetch via:
user = metadata.get_by_name(entity=User, fqn="admin")
