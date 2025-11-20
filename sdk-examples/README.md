# OpenMetadata Python SDK Examples

Complete, executable examples for every major OpenMetadata SDK operation.

## Overview

This directory contains lean, efficient examples demonstrating all major operations of the OpenMetadata Python SDK (`openmetadata-ingestion`). Each file is self-contained and runnable, with clear documentation of SDK APIs, required arguments, and source references.

## Quick Start

### Prerequisites
- **OpenMetadata Server**: Running instance (default: `http://localhost:8585/api`)
- **Python**: 3.10 (required for development and CI/CD)
- **SDK Installation**: `pip install openmetadata-ingestion`
- **Authentication**: JWT token (get from Settings > Bots > ingestion-bot)

### Running Examples

**Each example file is self-contained** - no dependencies between files!

```bash
# 1. Open any example file (e.g., services.py)
# 2. Update SERVER_URL and JWT_TOKEN at the top of the file
# 3. Run it directly:

python services.py           # Service creation examples
python entities.py           # Entity creation examples (requires services)
python metadata_ops.py       # Metadata operations (tags, descriptions, owners, domains)
python lineage.py            # Lineage examples (data flow tracking)
python queries.py            # Read/query operations (get, list, search)
python advanced.py           # Advanced patterns (bulk ops, migrations, best practices)

# Optional: Test connection patterns
python setup.py              # Connection reference (JWT, OAuth, etc.)
```

### Copy-Paste Friendly

Want to use an example in your code? Simply:
1. Copy the entire file or specific function
2. Update `SERVER_URL` and `JWT_TOKEN` variables
3. Run it - no external dependencies!

## Index

### 1. Connection Reference (`setup.py`)
Reference examples for different connection methods.

**NOTE**: This file is for reference only. Other files are self-contained and do NOT import from setup.py.

**Examples:**
- Basic JWT authentication (most common)
- Custom authentication providers (OAuth, Google, Okta, etc.)
- Health check patterns
- Connection troubleshooting

**SDK References:**
- `metadata.ingestion.ometa.ometa_api.OpenMetadata`
- `metadata.generated.schema.entity.services.connections.metadata.openMetadataConnection`
- `metadata.generated.schema.security.client.openMetadataJWTClientConfig`

---

### 2. Services (`services.py`)
Examples for creating all service types in OpenMetadata.

| Example | SDK API | Line | Required Args |
|---------|---------|------|---------------|
| **2.1 Database Service (Snowflake)** | `CreateDatabaseServiceRequest` | ~30 | `name`, `serviceType`, `connection` (with `SnowflakeConnection`) |
| **2.2 Pipeline Service (Airflow)** | `CreatePipelineServiceRequest` | ~65 | `name`, `serviceType`, `connection` (with `AirflowConnection`) |
| **2.3 Messaging Service (Kafka)** | `CreateMessagingServiceRequest` | ~95 | `name`, `serviceType`, `connection` (bootstrap servers) |
| **2.4 Storage Service (S3)** | `CreateStorageServiceRequest` | ~125 | `name`, `serviceType`, `connection` (AWS config) |
| **2.5 API Service** | `CreateAPIServiceRequest` | ~155 | `name`, `serviceType`, `connection` |

**SDK Module:** `metadata.generated.schema.api.services.*`

**Source Reference:**
- Database Services: [example_apis.py:102-115](../example_apis.py#L102-L115)
- Storage Services: [example_apis.py:118-128](../example_apis.py#L118-L128)
- Pipeline Services: [example_apis.py:131-151](../example_apis.py#L131-L151)
- Messaging Services: [example_apis.py:153-172](../example_apis.py#L153-L172)

---

### 3. Entities (`entities.py`)
Examples for creating data entities (tables, pipelines, topics, containers, APIs).

| Example | SDK API | Line | Required Args |
|---------|---------|------|---------------|
| **3.1 Database → Schema → Table** | `CreateDatabaseRequest`, `CreateDatabaseSchemaRequest`, `CreateTableRequest` | ~35 | Database: `name`, `service`<br>Schema: `name`, `database`<br>Table: `name`, `databaseSchema`, `columns` |
| **3.2 Pipeline + Tasks** | `CreatePipelineRequest` | ~95 | `name`, `service`, `tasks` (list of `Task`) |
| **3.3 Messaging Topic (Avro)** | `CreateTopicRequest` | ~130 | `name`, `service`, `partitions`, `messageSchema` (Avro) |
| **3.4 Storage Container (nested)** | `CreateContainerRequest` | ~180 | `name`, `service`, `prefix`, optional `parent` for nesting |
| **3.5 API Collection + Endpoint** | `CreateAPICollectionRequest`, `CreateAPIEndpointRequest` | ~250 | Collection: `name`, `service`, `endpointURL`<br>Endpoint: `name`, `apiCollection`, `requestMethod`, schemas |

**SDK Module:** `metadata.generated.schema.api.data.*`

**Source Reference:**
- Database/Schema/Table: [example_apis.py:174-196](../example_apis.py#L174-L196)
- Pipelines: [example_apis.py:293-304](../example_apis.py#L293-L304)
- Topics: [example_apis.py:311-323](../example_apis.py#L311-L323)
- Containers: [example_apis.py:348-434](../example_apis.py#L348-L434)
- API Collections: [example_apis.py:473-571](../example_apis.py#L473-L571)

---

### 4. Metadata Operations (`metadata_ops.py`)
Examples for managing metadata (tags, descriptions, owners, domains, glossaries).

| Example | SDK API | Line | Required Args |
|---------|---------|------|---------------|
| **4.1 Table-Level Tags** | `metadata.patch_tags()` | ~95 | `entity`, `source`, `tag_labels`, `operation` (ADD/REMOVE) |
| **4.2 Column-Level Tags** | `metadata.patch_column_tags()` | ~155 | `table`, `column_tags` (list of `ColumnTag`) |
| **4.3 Update Description** | `metadata.patch()` | ~225 | `entity_type`, `source_entity`, `modified_entity` (with new description) |
| **4.4 Update Owners (User/Team)** | `metadata.patch()` | ~280 | `entity_type`, `source_entity`, `modified_entity` (with `EntityReferenceList`) |
| **4.5 Assign Domain** | `metadata.patch_domain()` | ~355 | `entity`, `domain` |
| **4.6 Glossaries & Terms** | `metadata.list_all_entities()` | ~395 | `entity` (Glossary/GlossaryTerm), `params`, `fields` |
| **4.7 Grouped PATCH Operations** | `metadata.patch()` | ~450 | Multiple field updates in single PATCH |

**SDK Modules:**
- `metadata.ingestion.ometa.mixins.patch_mixin_utils.PatchOperation`
- `metadata.ingestion.models.table_metadata.ColumnTag`
- `metadata.generated.schema.type.tagLabel.TagLabel`
- `metadata.generated.schema.type.entityReference.EntityReference`
- `metadata.generated.schema.type.basic.Markdown`

**Source Reference:**
- Tags (table): [example_apis.py:220-233](../example_apis.py#L220-L233)
- Tags (column): [example_apis.py:236-246](../example_apis.py#L236-L246)
- Descriptions: [example_apis.py:249-257](../example_apis.py#L249-L257)
- Owners: [example_apis.py:259-277](../example_apis.py#L259-L277)
- Domains: [example_apis.py:284-290](../example_apis.py#L284-L290)
- Glossaries: [example_apis.py:454-469](../example_apis.py#L454-L469)
- Grouped Patches: [example_apis.py:575-593](../example_apis.py#L575-L593)

---

### 5. Lineage (`lineage.py`)
Examples for creating lineage relationships between entities.

| Example | SDK API | Line | Required Args |
|---------|---------|------|---------------|
| **5.1 Table → Pipeline → Table** | `metadata.add_lineage()` | ~100 | `edge` with `fromEntity`, `toEntity` (EntityReference) |
| **5.2 Direct Table → Table** | `metadata.add_lineage()` | ~180 | Direct lineage edge (views, CTAS) |
| **5.3 Multi-Source (Many → One)** | `metadata.add_lineage()` | ~220 | Multiple sources to one destination (joins, unions) |
| **5.4 Fan-Out (One → Many)** | `metadata.add_lineage()` | ~290 | One source to multiple destinations (CDC, broadcast) |
| **5.5 Query Entity Lineage** | `metadata.get_by_name()` | ~350 | Retrieve lineage for impact analysis |

**SDK Modules:**
- `metadata.generated.schema.api.lineage.addLineage.AddLineageRequest`
- `metadata.generated.schema.type.entityLineage.EntitiesEdge`
- `metadata.generated.schema.type.entityReference.EntityReference`

**Use Cases:**
- **Impact Analysis**: What breaks if I change this?
- **Data Provenance**: Where did this data come from?
- **Dependency Tracking**: What depends on this entity?

**Source Reference:**
- Table-Pipeline-Table: [example_apis.py:326-344](../example_apis.py#L326-L344)

---

### 6. Queries (`queries.py`)
Examples for reading and querying entities.

| Example | SDK API | Line | Required Args |
|---------|---------|------|---------------|
| **6.1 Get by Name (FQN)** | `metadata.get_by_name()` | ~100 | `entity`, `fqn`, optional `fields` (for performance) |
| **6.2 Get by ID (UUID)** | `metadata.get_by_id()` | ~180 | `entity`, `id`, optional `fields` |
| **6.3 List All Entities** | `metadata.list_all_entities()` | ~230 | `entity`, optional `fields` (generator/iterator) |
| **6.4 List with Filters** | `metadata.list_entities()` | ~280 | `entity`, optional `params` (glossary filter), `fields` |
| **6.5 Health Check** | `metadata.health_check()` | ~350 | None (monitoring, pre-flight checks) |
| **6.6 Query Patterns & Best Practices** | Various | ~410 | Safe retrieval, error handling, batch processing |

**SDK Module:** `metadata.ingestion.ometa.ometa_api.OpenMetadata`

**Key Patterns:**
- Field filtering for performance optimization
- Error handling for missing entities
- Iterator pattern for memory-efficient large datasets
- Conditional queries and batch processing

**Source Reference:**
- Get by Name: [example_apis.py:264, 440-441](../example_apis.py#L264)
- List All: [example_apis.py:443-452](../example_apis.py#L443-L452)
- List with Params: [example_apis.py:287-288, 458-469](../example_apis.py#L287-L288)

---

### 7. Advanced (`advanced.py`)
Advanced patterns for production-ready implementations.

| Example | SDK API | Line | Required Args |
|---------|---------|------|---------------|
| **7.1 Bulk Entity Creation** | `metadata.create_or_update()` in loop | ~110 | List of entity definitions, error handling per entity |
| **7.2 Bulk Updates with Retry** | `metadata.patch()` with retry logic | ~190 | Entities to update, max retries, exponential backoff |
| **7.3 Team User Migration** | `metadata.patch()` on teams | ~260 | Source team ID, dest team ID, user names to migrate |
| **7.4 Error Handling Patterns** | Various | ~390 | Input validation, specific exceptions, graceful degradation |
| **7.5 Production Best Practices** | Various | ~500 | Connection reuse, health checks, field filtering, monitoring |

**SDK Modules:**
- `metadata.ingestion.ometa.ometa_api.OpenMetadata`
- `metadata.generated.schema.entity.teams.team.Team`
- `copy.deepcopy` for safe entity modification

**Production Patterns:**
- **Idempotency**: Use `create_or_update()` for safe re-runs
- **Retry Logic**: Exponential backoff for transient failures
- **Error Handling**: Per-entity error tracking, don't fail entire batch
- **Performance**: Field filtering, connection reuse, batch operations
- **Monitoring**: Health checks, success rate tracking, structured logging

**Source Reference:**
- Team Migration: [example_apis.py:596-622](../example_apis.py#L596-L622)
- Grouped Patches: [example_apis.py:575-593](../example_apis.py#L575-L593)

---

## SDK API Reference Map

| Category | SDK Module Path | Documentation |
|----------|-----------------|---------------|
| **Main Client** | `metadata.ingestion.ometa.ometa_api` | [OpenMetadata Python SDK](https://docs.open-metadata.org/sdk/python) |
| **Connection** | `metadata.generated.schema.entity.services.connections.metadata` | [Connection Configuration](https://docs.open-metadata.org/sdk/python/api-reference/connection) |
| **Services** | `metadata.generated.schema.api.services.*` | [Services API](https://docs.open-metadata.org/sdk/python/api-reference/services) |
| **Entities** | `metadata.generated.schema.api.data.*` | [Data Entities API](https://docs.open-metadata.org/sdk/python/api-reference/entities) |
| **Entity Types** | `metadata.generated.schema.entity.data.*` | [Entity Definitions](https://docs.open-metadata.org/sdk/python/build-connector/define-yaml) |
| **Lineage** | `metadata.generated.schema.api.lineage.*` | [Lineage API](https://docs.open-metadata.org/sdk/python/api-reference/lineage) |
| **Tags** | `metadata.generated.schema.type.tagLabel` | [Tags & Classifications](https://docs.open-metadata.org/sdk/python/api-reference/tags) |
| **Teams** | `metadata.generated.schema.entity.teams.*` | [Teams & Users](https://docs.open-metadata.org/sdk/python/api-reference/teams) |

---

## Testing & Validation

All SDK examples are thoroughly tested to ensure they work correctly.

### Test Suite

Location: `tests/`

The test suite validates:
- ✅ All imports work correctly
- ✅ All pydantic models can be instantiated
- ✅ All example functions execute without errors
- ✅ SDK dependencies are available
- ✅ No syntax or runtime errors

### Running Tests

```bash
# Install test dependencies
pip install -r requirements-test.txt

# Run all tests
pytest tests/ -v

# Run specific test file
pytest tests/test_imports.py -v

# Run with coverage
pytest tests/ --cov=. --cov-report=term-missing
```

### CI/CD

Tests run automatically on every PR that modifies `sdk-examples/**`:
- **Python Version**: 3.10 only
- **Test Coverage**: Imports, models, example functions (with automated coverage comments on PRs)
- **Linting**: black, isort, ruff
- **Validation**: Syntax checks, import verification

See `.github/workflows/test-sdk-examples.yml` for full CI configuration.

### Test Coverage Details

| Test File | Coverage | Description |
|-----------|----------|-------------|
| `test_imports.py` | All 7 example files + SDK modules | Validates imports work |
| `test_models.py` | Service, entity, type, lineage models | Tests pydantic model creation |
| `test_examples.py` | All example functions | Tests function execution (mocked) |

For detailed testing documentation, see [`tests/README.md`](tests/README.md).

---

## Best Practices

### 1. No Hallucinations
✅ All examples reference actual SDK modules and methods
✅ Every import is documented with its source path
✅ Arguments match official SDK signatures

### 2. Clear Documentation
✅ Each example includes: purpose, SDK API, required args, optional args
✅ Source references point to original `example_apis.py` or official docs
✅ Inline comments explain non-obvious logic

### 3. Runnable Examples
✅ Each file can run independently
✅ Connection logic centralized in `setup.py`
✅ Examples include error handling patterns

### 4. Progressive Complexity
✅ Start with services (foundational)
✅ Build entities on top of services
✅ Add metadata operations
✅ Finish with advanced patterns

---

## Common Patterns

### Creating Entities
```python
from metadata.generated.schema.api.data.createTable import CreateTableRequest
from setup import get_metadata_client

metadata = get_metadata_client()

# Pattern: create_or_update returns the created/updated entity
table_entity = metadata.create_or_update(
    data=CreateTableRequest(
        name="my_table",
        databaseSchema="service.database.schema",
        columns=[...]
    )
)
```

### Updating with PATCH
```python
from copy import deepcopy
from metadata.generated.schema.type.basic import Markdown

# Pattern: fetch → modify copy → patch
original = metadata.get_by_name(entity=Table, fqn="fqn")
modified = deepcopy(original)
modified.description = Markdown("New description")

metadata.patch(Table, original, modified)
```

### Adding Lineage
```python
from metadata.generated.schema.api.lineage.addLineage import AddLineageRequest
from metadata.generated.schema.type.entityLineage import EntitiesEdge
from metadata.generated.schema.type.entityReference import EntityReference

# Pattern: define edge with from/to entities
metadata.add_lineage(
    data=AddLineageRequest(
        edge=EntitiesEdge(
            fromEntity=EntityReference(id=source_id, type="table"),
            toEntity=EntityReference(id=dest_id, type="pipeline")
        )
    )
)
```

---

## Troubleshooting

### Connection Issues
```python
# Verify server is reachable
metadata = get_metadata_client()
metadata.health_check()  # Should not raise exception
```

### Entity Not Found
```python
# Use try-except when entity might not exist
try:
    entity = metadata.get_by_name(entity=Table, fqn="my.table.fqn")
except Exception as e:
    print(f"Entity not found: {e}")
```

### Authentication Errors
- Verify JWT token is valid and not expired
- Check `authProvider` matches your OpenMetadata setup
- Ensure user/bot has necessary permissions

---

## Contributing

When adding new examples:
1. Follow existing file structure and documentation patterns
2. Include SDK API references and source links
3. Document all required and optional arguments
4. Add example to this README index
5. Ensure code is runnable and tested

---

## License

This repository follows the OpenMetadata demo repository license.

## Support

- **Documentation**: [OpenMetadata Docs](https://docs.open-metadata.org/)
- **SDK Reference**: [Python SDK API Reference](https://docs.open-metadata.org/sdk/python)
- **Community**: [Slack](https://slack.open-metadata.org/)
- **Issues**: [GitHub Issues](https://github.com/open-metadata/OpenMetadata/issues)
