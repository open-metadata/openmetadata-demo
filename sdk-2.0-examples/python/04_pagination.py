"""
SDK 2.0 - Pagination
=====================

Two approaches:
  - list()      — manual cursor-based pagination (forward / backward)
  - list_all()  — automatic pagination that fetches everything

Prerequisite: run 02_basic_crud.py first to create the demo entities.

Source: ingestion/src/metadata/sdk/entities/base.py
"""

from metadata.sdk import configure, Tables, Users

configure(host="http://localhost:8585/api", jwt_token="<token>")

# ================================================================== #
# 1. Manual cursor pagination with list()
# ================================================================== #
# list() returns an EntityList with .entities, .after, .before

print("=== Manual pagination ===")
cursor = None
page_num = 0

while True:
    page = Tables.list(limit=10, after=cursor, fields=["owners"])
    page_num += 1
    print(f"Page {page_num}: {len(page.entities)} tables")

    for t in page.entities:
        print(f"  - {t.fullyQualifiedName}")

    # No more pages?
    if not page.after:
        break
    cursor = page.after

print(f"Done — {page_num} pages fetched\n")

# ------------------------------------------------------------------ #
# Backward pagination is also supported via `before`:
# page = Tables.list(limit=10, before=page.before)
# ------------------------------------------------------------------ #

# ================================================================== #
# 2. Automatic pagination with list_all()
# ================================================================== #
# list_all() handles cursors internally and returns a flat list.

print("=== Automatic pagination ===")
all_tables = Tables.list_all(batch_size=100, fields=["owners"])
print(f"Total tables: {len(all_tables)}")

# ================================================================== #
# 3. Filtered pagination
# ================================================================== #
# Pass `filters` to narrow down results to our demo database.

print("\n=== Filtered list ===")
page = Tables.list(
    limit=50,
    filters={"database": "sdk_demo_mysql.sdk_demo_db"},
)
print(f"Tables in sdk_demo_db: {len(page.entities)}")
for t in page.entities:
    print(f"  - {t.fullyQualifiedName}")

# ================================================================== #
# 4. Paginating Users
# ================================================================== #
# The same API works on every entity facade.

print("\n=== Users ===")
user_page = Users.list(limit=5)
for u in user_page.entities:
    print(f"  {u.name} ({u.email})")
