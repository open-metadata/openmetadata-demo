# OpenMetadata SDK 2.0 — Examples

Side-by-side **Python** and **Java** examples that cover the entire surface
of the OpenMetadata SDK 2.0.

## What changed in SDK 2.0?

| Concept | Old SDK | SDK 2.0 |
|---------|---------|---------|
| Client init | `OpenMetadata(OpenMetadataConnection(...))` | `configure(host=..., jwt_token=...)` (Python) / `OpenMetadataConfig.builder()...build()` (Java) |
| CRUD | `metadata.create_or_update(entity)` | `Tables.create(request)`, `Tables.retrieve(id)`, `Tables.update(entity)` |
| Pagination | Manual iterator with `list_all_entities()` | `Tables.list(limit=10, after=cursor)` + `Tables.list_all()` |
| Fields | `fields=["columns"]` passed to low-level client | Same — `fields=["columns"]` on every retrieve/list call |
| Relationships | JSON-Patch dicts built by hand | `Tables.add_tag()`, `Tables.add_followers()`, `to_entity_reference()` |
| Search | Direct REST calls | `Search.search()`, `Search.suggest()`, `Search.builder()` |
| Lineage | Direct REST calls | `Lineage.get_lineage()`, `Lineage.add_lineage()`, `Lineage.builder()` |
| Custom props | Manual PATCH | `Tables.update_custom_properties(id).with_property(k, v).execute()` |
| Java updates | Raw `client.tables().update()` | `FluentTable.withDescription(...).addTag(...).save()` |

## Directory layout

```
sdk-2.0-examples/
├── python/
│   ├── 01_configuration.py        # Three ways to configure the client
│   ├── 02_basic_crud.py           # Create, retrieve, update, delete, restore
│   ├── 03_field_selection.py      # Fetch only the fields you need
│   ├── 04_pagination.py           # Manual cursors and auto-pagination
│   ├── 05_search.py               # Full-text search, suggest, aggregate, builder
│   ├── 06_lineage.py              # Query, add and delete lineage edges
│   ├── 07_custom_properties.py    # Set, update and clear extension properties
│   ├── 08_versioning.py           # List and retrieve historical entity versions
│   ├── 09_entity_relationships.py # Owners, followers, tags, domains
│   └── 10_csv_operations.py       # Bulk CSV import / export
│
└── java/
    ├── Configuration.java         # Builder config + global registration
    ├── BasicCrud.java             # Create, retrieve, update, delete (fluent + service)
    ├── FieldSelection.java        # Fields via service, fluent includes, list fields
    ├── Pagination.java            # Cursor-based, fluent forEach, filtered
    ├── SearchExample.java         # Search, suggest, aggregate, advanced raw query
    ├── LineageExample.java        # Get, add, delete, export lineage
    ├── FluentUpdates.java         # FluentTable chaining: tags, columns, descriptions
    ├── ColumnBuilders.java        # ColumnBuilder convenience methods
    ├── EntityRelationships.java   # EntityReferences, owners, tags, column tags
    └── VersioningExample.java     # Version history and snapshot comparison
```

## Topics covered

| # | Topic | Python | Java |
|---|-------|--------|------|
| 1 | **Configuration** — builder, kwargs, env vars | `01_configuration.py` | `Configuration.java` |
| 2 | **CRUD** — create, retrieve (ID/FQN), update, soft/hard delete, restore | `02_basic_crud.py` | `BasicCrud.java` |
| 3 | **Field selection** — fetch only the data you need | `03_field_selection.py` | `FieldSelection.java` |
| 4 | **Pagination** — cursors, list_all, filters | `04_pagination.py` | `Pagination.java` |
| 5 | **Search** — full-text, suggest, aggregations, builder, raw ES | `05_search.py` | `SearchExample.java` |
| 6 | **Lineage** — get, add, delete, export, builder | `06_lineage.py` | `LineageExample.java` |
| 7 | **Custom properties** — set, clear, batch update | `07_custom_properties.py` | _(via FluentUpdates.java)_ |
| 8 | **Versioning** — list versions, retrieve snapshot, diff | `08_versioning.py` | `VersioningExample.java` |
| 9 | **Relationships** — owners, followers, tags, domains, entity refs | `09_entity_relationships.py` | `EntityRelationships.java` |
| 10 | **CSV import/export** — bulk operations, dry-run | `10_csv_operations.py` | _(via CsvOperations)_ |
| 11 | **Fluent updates** — FluentTable chaining, conditional logic | — | `FluentUpdates.java` |
| 12 | **Column builders** — type-safe column creation | — | `ColumnBuilders.java` |

## Running the examples

### Python

```bash
pip install openmetadata-ingestion

# Set connection info
export OPENMETADATA_HOST=http://localhost:8585/api
export OPENMETADATA_JWT_TOKEN=<your-token>

python sdk-2.0-examples/python/01_configuration.py
```

### Java

Add the SDK dependency to your `pom.xml`:

```xml
<dependency>
    <groupId>org.open-metadata</groupId>
    <artifactId>openmetadata-sdk</artifactId>
    <version>2.0.0</version>
</dependency>
```

Then compile and run any example class.
