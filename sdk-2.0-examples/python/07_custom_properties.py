"""
SDK 2.0 - Custom Properties
=============================

Set, update and clear custom (extension) properties on any entity.

Prerequisite: run 02_basic_crud.py first to create the demo entities.

Source: ingestion/src/metadata/sdk/entities/custom_properties.py
         ingestion/src/metadata/sdk/entities/base.py
"""

from metadata.sdk import configure, Tables
from metadata.sdk.entities.custom_properties import CustomProperties
from metadata.generated.schema.entity.data.table import Table

configure(host="http://localhost:8585/api", jwt_token="<token>")

TABLE_FQN = "sdk_demo_mysql.sdk_demo_db.demo_schema.customers"

# ================================================================== #
# 1. Set a single custom property — by entity ID
# ================================================================== #
table = Tables.retrieve_by_name(TABLE_FQN)

updated = (
    Tables.update_custom_properties(table.id)
    .with_property("department", "Data Engineering")
    .execute()
)
print(f"Set 'department' on {updated.fullyQualifiedName}")

# ================================================================== #
# 2. Set multiple properties at once — by FQN
# ================================================================== #
updated = (
    Tables.update_custom_properties_by_name(TABLE_FQN)
    .with_properties(
        {
            "cost_center": "CC-1234",
            "data_steward": "alice@example.com",
            "retention_days": 365,
        }
    )
    .execute()
)
print(f"Custom props: {updated.extension}")

# ================================================================== #
# 3. Clear a single property
# ================================================================== #
updated = (
    Tables.update_custom_properties(table.id)
    .clear_property("cost_center")
    .execute()
)

# ================================================================== #
# 4. Clear all custom properties
# ================================================================== #
updated = (
    Tables.update_custom_properties(table.id)
    .clear_all()
    .execute()
)

# ================================================================== #
# 5. Using the generic CustomProperties helper
# ================================================================== #
# Works with any entity type — not just Tables.

updated = (
    CustomProperties.update(Table, table.id)
    .with_property("tier", "Gold")
    .with_property("sla_hours", 4)
    .execute()
)

# By FQN
updated = (
    CustomProperties.update_by_name(Table, TABLE_FQN)
    .with_property("tier", "Gold")
    .execute()
)
