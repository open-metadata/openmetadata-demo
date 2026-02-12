"""
SDK 2.0 - Field Selection
==========================

By default, retrieve / list calls return only core fields.
Pass `fields=[...]` to request additional relationships or
expensive attributes.

Prerequisite: run 02_basic_crud.py first to create the demo entities.

Source: ingestion/src/metadata/sdk/entities/base.py
"""

from metadata.sdk import configure, Tables, Users

configure(host="http://localhost:8585/api", jwt_token="<token>")

TABLE_FQN = "sdk_demo_mysql.sdk_demo_db.demo_schema.customers"

# ------------------------------------------------------------------ #
# 1. Default fetch — lightweight, no relations
# ------------------------------------------------------------------ #
table = Tables.retrieve_by_name(TABLE_FQN)
# table.owners will be empty / None because we didn't ask for it

# ------------------------------------------------------------------ #
# 2. Request specific fields
# ------------------------------------------------------------------ #
table = Tables.retrieve_by_name(
    TABLE_FQN,
    fields=["columns", "tags", "owners"],
)
print(f"Columns: {len(table.columns)}")
print(f"Tags:    {table.tags}")
print(f"Owners:  {table.owners}")

# ------------------------------------------------------------------ #
# 3. Common field names across entities
# ------------------------------------------------------------------ #
# These work on most entity types:
#   "owners"              — entity owners (users / teams)
#   "tags"                — classification / glossary tags
#   "followers"           — users following the entity
#   "domains"             — governance domains
#   "dataProducts"        — associated data products
#   "extension"           — custom properties
#   "changeDescription"   — last change details
#
# Entity-specific fields:
#   Tables:  "columns", "tableConstraints", "usageSummary",
#            "profile", "joins", "sampleData"
#   Users:   "teams", "roles", "personas"

# ------------------------------------------------------------------ #
# 4. Fields in list() calls — same syntax
# ------------------------------------------------------------------ #
page = Tables.list(
    limit=5,
    fields=["columns", "owners"],
    filters={"database": "sdk_demo_mysql.sdk_demo_db"},
)
for t in page.entities:
    col_count = len(t.columns) if t.columns else 0
    print(f"  {t.fullyQualifiedName}  ({col_count} columns)")

# ------------------------------------------------------------------ #
# 5. Fields in list_all() — autopaginated
# ------------------------------------------------------------------ #
all_tables = Tables.list_all(
    batch_size=50,
    fields=["tags"],
    filters={"database": "sdk_demo_mysql.sdk_demo_db"},
)
tagged = [t for t in all_tables if t.tags]
print(f"{len(tagged)} tables have tags")
