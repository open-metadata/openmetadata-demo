"""
SDK 2.0 - CSV Import / Export
==============================

Bulk import and export entities via CSV.

Prerequisite: run 02_basic_crud.py first to create the demo entities.

Source: ingestion/src/metadata/sdk/entities/base.py
"""

from metadata.sdk import configure, DatabaseSchemas, GlossaryTerms

configure(host="http://localhost:8585/api", jwt_token="<token>")

SCHEMA_FQN = "sdk_demo_mysql.sdk_demo_db.demo_schema"

# ================================================================== #
# 1. Export entities to CSV
# ================================================================== #
export_op = DatabaseSchemas.export_csv(SCHEMA_FQN)
csv_content = export_op.execute()
print(f"Exported CSV:\n{csv_content[:500]}...")

# ================================================================== #
# 2. Dry-run import — validate without committing
# ================================================================== #
csv_data = """name*,displayName,description,owner,tags,glossaryTerms,tiers,certification,retentionPeriod,sourceUrl,domains,extension
new_table,New Table,Created via CSV import,admin,,,,,,,,"""

import_op = (
    DatabaseSchemas.import_csv(SCHEMA_FQN)
    .with_data(csv_data)
    .set_dry_run(True)
)
result = import_op.execute()
print(f"Dry run result: {result}")

# ================================================================== #
# 3. Actual import
# ================================================================== #
import_op = (
    DatabaseSchemas.import_csv(SCHEMA_FQN)
    .with_data(csv_data)
    .set_dry_run(False)
)
result = import_op.execute()
print(f"Import result: {result}")

# ================================================================== #
# 4. Glossary terms CSV round-trip
# ================================================================== #
# Export
# csv = GlossaryTerms.export_csv("Business").execute()
# print(f"Glossary CSV:\n{csv[:300]}...")
#
# Import with modifications
# modified_csv = csv.replace("old_description", "new_description")
# GlossaryTerms.import_csv("Business").with_data(modified_csv).set_dry_run(False).execute()
