"""
SDK 2.0 - Entity Versioning
=============================

Every change in OpenMetadata is tracked as a version.
You can list all versions or retrieve a specific one.

Prerequisite: run 02_basic_crud.py first (it creates the table and
updates its description, producing at least two versions).

Source: ingestion/src/metadata/sdk/entities/base.py
"""

from metadata.sdk import configure, Tables

configure(host="http://localhost:8585/api", jwt_token="<token>")

TABLE_FQN = "sdk_demo_mysql.sdk_demo_db.demo_schema.customers"

# ================================================================== #
# 1. Get the current entity (latest version)
# ================================================================== #
table = Tables.retrieve_by_name(TABLE_FQN)
print(f"Current version: {table.version}")

# ================================================================== #
# 2. List all historical versions
# ================================================================== #
versions = Tables.get_versions(table.id)
for v in versions:
    print(f"  v{v.version}  updated by {v.updatedBy}")

# ================================================================== #
# 3. Retrieve a specific version
# ================================================================== #
first_version = Tables.get_specific_version(table.id, "0.1")
print(f"Version 0.1 description: {first_version.description}")

# ================================================================== #
# 4. Practical pattern: diff two versions
# ================================================================== #
# 02_basic_crud.py creates the table (v0.1) and then updates the
# description (v0.2), so we can compare the two.
v1 = Tables.get_specific_version(table.id, "0.1")
v2 = Tables.get_specific_version(table.id, "0.2")

if v1.description != v2.description:
    print("Description changed:")
    print(f"  v0.1: {v1.description}")
    print(f"  v0.2: {v2.description}")
