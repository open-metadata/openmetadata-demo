"""
SDK 2.0 - Lineage API
======================

Query, add and delete lineage edges between entities.

Prerequisite: run 02_basic_crud.py first to create the demo service
hierarchy and the customers table.

Source: ingestion/src/metadata/sdk/api/lineage.py
"""

from metadata.sdk import configure, Tables
from metadata.sdk.api.lineage import Lineage
from metadata.generated.schema.api.data.createTable import CreateTableRequest
from metadata.generated.schema.entity.data.table import Column, DataType, Table

configure(host="http://localhost:8585/api", jwt_token="<token>")

CUSTOMERS_FQN = "sdk_demo_mysql.sdk_demo_db.demo_schema.customers"
SCHEMA_FQN = "sdk_demo_mysql.sdk_demo_db.demo_schema"

# Retrieve the customers table created in 02_basic_crud.py
customers = Tables.retrieve_by_name(CUSTOMERS_FQN)

# Create the orders table for this example
orders = Tables.create(
    CreateTableRequest(
        name="orders",
        databaseSchema=SCHEMA_FQN,
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

# ================================================================== #
# 1. Add a lineage edge (orders → customers)
# ================================================================== #
result = Lineage.add_lineage(
    from_entity_id=orders.id,
    from_entity_type=Table,
    to_entity_id=customers.id,
    to_entity_type=Table,
    description="ETL: orders → customers join",
)
print(f"Lineage edge created: {result}")

# ================================================================== #
# 2. Get lineage by FQN
# ================================================================== #
lineage = Lineage.get_lineage(
    entity=CUSTOMERS_FQN,
    upstream_depth=2,
    downstream_depth=2,
)
if lineage:
    print(f"Nodes : {len(lineage.nodes)}")
    print(f"Edges : {len(lineage.edges) if lineage.edges else 0}")

# ================================================================== #
# 3. Get lineage by entity type + ID
# ================================================================== #
lineage = Lineage.get_entity_lineage(
    entity_type=Table,
    entity_id=customers.id,
    upstream_depth=3,
    downstream_depth=1,
)

# ================================================================== #
# 4. Export lineage graph
# ================================================================== #
exported = Lineage.export_lineage(
    entity_type=Table,
    entity_id=customers.id,
    upstream_depth=3,
    downstream_depth=3,
)
print(f"Exported lineage: {exported}")

# ================================================================== #
# 5. Builder pattern
# ================================================================== #

# Query lineage via builder
lineage = (
    Lineage.builder()
    .entity(CUSTOMERS_FQN)
    .upstream_depth(2)
    .downstream_depth(1)
    .execute()
)

# Add lineage via builder
result = (
    Lineage.builder()
    .from_entity(orders.id, Table)
    .to_entity(customers.id, Table)
    .description("ETL pipeline dependency")
    .execute()
)

# ================================================================== #
# 6. Delete a lineage edge
# ================================================================== #
Lineage.delete_lineage(
    from_entity=orders.id,
    from_entity_type="table",
    to_entity=customers.id,
    to_entity_type="table",
)
print("Lineage edge deleted")

# ================================================================== #
# 7. Async lineage (for async applications)
# ================================================================== #
# import asyncio
# lineage = asyncio.run(
#     Lineage.get_lineage_async(
#         entity=CUSTOMERS_FQN,
#         upstream_depth=2,
#         downstream_depth=2,
#     )
# )
