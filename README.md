# OpenMetadata 2.0 RC1 Demo Catalog

> [!IMPORTANT]
> These maintained examples target exactly
> `openmetadata-ingestion==2.0.0.0rc1` and Docker images tagged
> `2.0.0-rc1`. They are prerelease examples and are not compatible with
> OpenMetadata 1.x.

This repository contains small, runnable examples for extending and automating
OpenMetadata. The facade scenarios are based on the `2.0.0-rc1-release` source
at commit `8e199f486b63df9f44d4c827a9f43559d9e56e07`.

The earlier generated platform API catalog was removed. This is not an
every-REST-route cookbook or a replacement for the SDK documentation. It shows
plain Python scripts calling the public SDK facades for representative customer
workflows.

## SDK Facade Scenarios

Install the shared dependency with Python 3.10, 3.11, or 3.12:

```bash
python -m pip install -r requirements-sdk.txt
```

| Scenario | What It Creates or Reads | Validation | Guide | Owners |
| --- | --- | --- | --- | --- |
| Database catalog | Custom database service, database, schema, table, stored procedure, and sample data | RC1 models, ordering, ownership, and mocked facade calls | [`catalog-assets/`](catalog-assets/) | Ingestion and Documentation |
| Analytics assets | Dashboard assets, ML model, pipeline status, query, and search index | RC1 models, prerequisites, ordering, and mocked facade calls | [`analytics-assets/`](analytics-assets/) | Ingestion and Documentation |
| Storage assets | Custom storage service and nested containers | RC1 models, hierarchy, retry, and mocked facade calls | [`storage-assets/`](storage-assets/) | Ingestion and Documentation |
| Governance assets | Classification, tag, glossary, terms, domain, product, metrics, and contract | RC1 models, relation order, contract guard, and mocked facade calls | [`governance-assets/`](governance-assets/) | Ingestion and Documentation |
| Identity and Settings | Team, user, entity references, and read-only glossary relation settings | RC1 models, ownership, read-only Settings calls, and mocked facade calls | [`identity-and-settings/`](identity-and-settings/) | Ingestion and Documentation |
| Data quality | Existing definition lookup, suite, case, and latest-result reads | RC1 models, canonical entity link, parent checks, and mocked facade calls | [`data-quality/`](data-quality/) | Ingestion and Documentation |

Together with the API-lineage and CSV examples below, the scripts exercise all
30 route-backed facades exported by `metadata.sdk.entities.__all__`. `Settings`
has a live read example. `ContextFiles`, `Folders`, and `Pages` have valid create
models but no working RC1 route resolution; see
[`SDK_FACADE_LIMITATIONS.md`](SDK_FACADE_LIMITATIONS.md). No private REST
fallback or SDK route override is included.

Most live scenarios require:

```text
OPENMETADATA_HOST
OPENMETADATA_JWT_TOKEN
OPENMETADATA_DEMO_NAMESPACE
```

Each guide lists additional parent services or target assets. The namespace
must match `^[a-z][a-z0-9_]{2,31}$`.

## Other Maintained Examples

| Example | Purpose | Supported Version | Validation | Guide | Owners |
| --- | --- | --- | --- | --- | --- |
| Custom connectors | Deterministic custom sources for all eight service types | 2.0 RC1 | Workflow, import, request-model, and dependency-order tests | [`custom-connector/`](custom-connector/) | Ingestion and Documentation |
| GraphQL updater | Enrich OpenMetadata users from a GraphQL API | 2.0 RC1 | Workflow, targeted-patch, and mocked boundary tests | [`custom-graphql/`](custom-graphql/) | Ingestion and Documentation |
| Dynamic CSV importer | Update explicitly named tables and dashboard data models through public facades | 2.0 RC1 | Full CSV parse, deep-copy plan, preflight targets, and mocked facade updates | [`dynamic_csv_importer/`](dynamic_csv_importer/) | Ingestion and Documentation |
| API lineage CI/CD | Create collections/endpoints under existing API services and verify lineage | 2.0 RC1 | YAML, request-model, ownership, field-reference, and mocked lineage tests | [`api-lineage-cicd/`](api-lineage-cicd/) | Ingestion and Documentation |
| Ingestion automation | Create, deploy, and trigger a database ingestion pipeline | 2.0 RC1 | Request-model and mocked REST-path tests | [`ingestion-automation/`](ingestion-automation/) | Ingestion and Documentation |
| MCP workshop | OpenMetadata MCP, Goose, and Jupyter workshop | 2.0 RC1 | Link and seed-file checks only | [`mcp/`](mcp/) | Documentation |

## Write Safety

`Facade.create()` is a full PUT upsert. The six new live scenarios add an exact
ownership marker to entity descriptions:

```text
[openmetadata-demo:<namespace>:<scenario>]
```

They create missing entities and rerun entities with the same marker. They
abort rather than overwrite a foreign collision. The CSV importer is different:
its repeatable FQN flags are the explicit authorization boundary for existing
assets. None of these examples includes hard delete, recursive delete,
automatic cleanup, restore, global Settings mutation, search reindex, or test
execution.

## Validation Boundary

**Offline request/model/import validation** runs on Python 3.10, 3.11, and 3.12
against the exact RC1 dependency. CI also checks facade coverage, dependency
ordering, socket-free imports, YAML/JSON parsing, Ruff, compileall, Node syntax,
Docker Compose configuration, Markdown links, and repository-wide Gitleaks.

This is not live-server certification. CI does not start OpenMetadata or run
Docker-backed ingestion. Before relying on the examples, run them against a
disposable `2.0.0-rc1` server with the prerequisites named in each guide.

## SDK Learning Material

Comprehensive Python and Java SDK tutorials remain in the product
documentation:

- [OpenMetadata Python SDK documentation](https://docs.open-metadata.org/latest/sdk/python)
- [Collate Python SDK documentation](https://docs.getcollate.io/sdk/python)

After OpenMetadata 2.0 reaches general availability, a separate change will
replace the package and Docker RC pins, revalidate the examples against GA, and
publish a `2.0.0` repository tag.
