"""
SDK 2.0 - Basic CRUD Operations
=================================

Create the full entity hierarchy (Service → Database → Schema → Table),
then retrieve, update and delete using the static entity facades.

Source: ingestion/src/metadata/sdk/entities/base.py
         ingestion/src/metadata/sdk/entities/tables.py
         ingestion/src/metadata/sdk/entities/database_services.py
"""

from metadata.sdk import configure, Tables, Databases, DatabaseSchemas
from metadata.sdk.entities.database_services import DatabaseServices

# ------------------------------------------------------------------ #
# 0. Connect
# ------------------------------------------------------------------ #
configure(host="http://localhost:8585/api", jwt_token="<token>")

# ------------------------------------------------------------------ #
# 1. CREATE — full hierarchy: Service → Database → Schema → Table
# ------------------------------------------------------------------ #
from metadata.generated.schema.api.services.createDatabaseService import (
    CreateDatabaseServiceRequest,
)
from metadata.generated.schema.api.data.createDatabase import (
    CreateDatabaseRequest,
)
from metadata.generated.schema.api.data.createDatabaseSchema import (
    CreateDatabaseSchemaRequest,
)
from metadata.generated.schema.api.data.createTable import (
    CreateTableRequest,
)
from metadata.generated.schema.entity.data.table import Column, DataType
from metadata.generated.schema.entity.services.connections.database.mysqlConnection import (
    MysqlConnection,
    MySQLType,
)
from metadata.generated.schema.entity.services.databaseService import (
    DatabaseConnection,
    DatabaseServiceType,
)

# Create a database service (the top-level container)
service = DatabaseServices.create(
    CreateDatabaseServiceRequest(
        name="sdk_demo_mysql",
        serviceType=DatabaseServiceType.Mysql,
        description="MySQL service created via SDK 2.0",
        connection=DatabaseConnection(
            config=MysqlConnection(
                type=MySQLType.Mysql,
                username="demo_user",
                hostPort="localhost:3306",
            )
        ),
    )
)
print(f"Created service: {service.fullyQualifiedName}")

# Create a database inside the service
db = Databases.create(
    CreateDatabaseRequest(
        name="sdk_demo_db",
        service=service.fullyQualifiedName,
        description="Database created via SDK 2.0",
    )
)
print(f"Created database: {db.fullyQualifiedName}")

# Create a schema inside it
schema = DatabaseSchemas.create(
    CreateDatabaseSchemaRequest(
        name="demo_schema",
        database=db.fullyQualifiedName,
        description="Schema created via SDK 2.0",
    )
)
print(f"Created schema: {schema.fullyQualifiedName}")

# Create tables with columns
customers = Tables.create(
    CreateTableRequest(
        name="customers",
        databaseSchema=schema.fullyQualifiedName,
        description="Customer master data",
        columns=[
            Column(name="id", dataType=DataType.BIGINT, description="Primary key"),
            Column(name="name", dataType=DataType.VARCHAR, dataLength=255),
            Column(
                name="email",
                dataType=DataType.VARCHAR,
                dataLength=320,
                description="Contact email",
            ),
            Column(name="created_at", dataType=DataType.TIMESTAMP),
        ],
    )
)
print(f"Created table: {customers.fullyQualifiedName}")

orders = Tables.create(
    CreateTableRequest(
        name="orders",
        databaseSchema=schema.fullyQualifiedName,
        description="Order transactions",
        columns=[
            Column(name="id", dataType=DataType.BIGINT, description="Primary key"),
            Column(
                name="customer_id",
                dataType=DataType.BIGINT,
                description="FK to customers.id",
            ),
            Column(name="amount", dataType=DataType.DECIMAL),
            Column(name="order_date", dataType=DataType.DATE),
        ],
    )
)
print(f"Created table: {orders.fullyQualifiedName}")

# ------------------------------------------------------------------ #
# 2. RETRIEVE — by ID or by Fully Qualified Name (FQN)
# ------------------------------------------------------------------ #

# By UUID
same_table = Tables.retrieve(customers.id)

# By FQN (most common in practice)
same_table = Tables.retrieve_by_name(
    "sdk_demo_mysql.sdk_demo_db.demo_schema.customers"
)

# Nullable mode: returns None instead of raising when not found
maybe = Tables.retrieve_by_name("does.not.exist", nullable=True)
assert maybe is None

# ------------------------------------------------------------------ #
# 3. UPDATE
# ------------------------------------------------------------------ #

# Mutate the object, then persist.
# Note: description fields are typed as Markdown, not plain str.
from metadata.generated.schema.type.basic import Markdown

customers.description = Markdown("Customer master data (updated via SDK 2.0)")
updated = Tables.update(customers)
print(f"Updated description: {updated.description}")

# ------------------------------------------------------------------ #
# 4. DELETE (run after all other examples)
# ------------------------------------------------------------------ #
# The remaining examples (03–10) reference the entities created above.
# Run this cleanup section only after you are done with the full demo.

# # Soft delete (default) — entity is still recoverable
# Tables.delete(customers.id)
# print("Table soft-deleted")
#
# # Restore
# restored = Tables.restore(customers.id)
# print(f"Table restored: {restored.fullyQualifiedName}")
#
# # Hard delete — permanent removal
# Tables.delete(customers.id, hard_delete=True)
# print("Table permanently deleted")
#
# # Recursive delete — removes the service and everything under it
# DatabaseServices.delete(service.id, recursive=True, hard_delete=True)
# print("Full hierarchy deleted")
