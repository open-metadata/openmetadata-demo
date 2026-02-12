"""
SDK 2.0 - Entity Relationships
================================

Set owners, followers, tags, domains, and link entities together.

Prerequisite: run 02_basic_crud.py first to create the demo entities.

Source: ingestion/src/metadata/sdk/entities/base.py
         ingestion/src/metadata/sdk/entities/tables.py
         ingestion/src/metadata/sdk/__init__.py
"""

from metadata.sdk import configure, to_entity_reference
from metadata.sdk import Tables, Users, Teams, Domains

configure(host="http://localhost:8585/api", jwt_token="<token>")

TABLE_FQN = "sdk_demo_mysql.sdk_demo_db.demo_schema.customers"

# ================================================================== #
# 1. Set owners (user or team)
# ================================================================== #
table = Tables.retrieve_by_name(TABLE_FQN, fields=["owners"])

# to_entity_reference() converts any entity to a reference dict
user = Users.retrieve_by_name("admin")

table.owners = [
    to_entity_reference(user),
]
updated = Tables.update(table)
print(f"Owners: {updated.owners}")

# ================================================================== #
# 2. Add / remove followers
# ================================================================== #
table = Tables.add_followers(table.id, [user.id])
print("Follower added")

table = Tables.remove_followers(table.id, [user.id])
print("Follower removed")

# ================================================================== #
# 3. Add tags to a table
# ================================================================== #
table = Tables.add_tag(table.id, "PII.Sensitive")
print(f"Tags after add: {table.tags}")

# ================================================================== #
# 4. Update a column description
# ================================================================== #
table = Tables.update_column_description(
    table.id,
    column_name="email",
    description="Primary contact email — PII",
)
for col in table.columns:
    if col.name.__root__ == "email":
        print(f"Column 'email' description: {col.description}")

# ================================================================== #
# 5. Assign a domain (if one exists)
# ================================================================== #
# domain = Domains.retrieve_by_name("Marketing")
# table = Tables.retrieve_by_name(TABLE_FQN, fields=["domains"])
# table.domain = to_entity_reference(domain)
# updated = Tables.update(table)
# print(f"Domain: {updated.domain}")

# ================================================================== #
# 6. Entity search — typed results
# ================================================================== #
matching = Tables.search("customers", size=5)
for t in matching:
    print(f"  Found: {t.fullyQualifiedName}")
