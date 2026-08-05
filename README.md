# OpenMetadata Demo Catalog

> [!IMPORTANT]
> The maintained examples in this repository target the OpenMetadata 2.0 release candidate:
> `openmetadata-ingestion==2.0.0.0rc1` and Docker images tagged `2.0.0-rc1`. They are not
> compatible with OpenMetadata 1.x.

This repository contains focused examples for extending or automating OpenMetadata. Each
maintained example includes its own run instructions and deterministic tests where practical.

## Maintained Examples

| Example | Purpose | Supported version | Validation level | Run instructions | Owners |
| --- | --- | --- | --- | --- | --- |
| [`custom-connector`](custom-connector/) | Custom sources for all eight service types | 2.0 RC1 | Workflow, import, request-model, and mocked dependency-order tests | [Custom connector quickstart](custom-connector/README.md#quickstart) | Ingestion and Documentation |
| [`custom-graphql`](custom-graphql/) | Enrich OpenMetadata users from a GraphQL API | 2.0 RC1 | Workflow, targeted-patch, and mocked GraphQL/OpenMetadata tests | [GraphQL updater guide](custom-graphql/README.md#run-the-example) | Ingestion and Documentation |
| [`dynamic_csv_importer`](dynamic_csv_importer/) | Apply column metadata from an OpenMetadata CSV export | 2.0 RC1 | CLI, CSV conversion, request-model, and mocked SDK tests | [Dynamic CSV importer guide](dynamic_csv_importer/README.md#run-the-example) | Ingestion and Documentation |
| [`api-lineage-cicd`](api-lineage-cicd/) | Manage API services and lineage from declarative YAML | 2.0 RC1 | YAML, request-model, field-reference, and exact mocked lineage tests | [API lineage guide](api-lineage-cicd/README.md#usage) | Ingestion and Documentation |
| [`ingestion-automation`](ingestion-automation/) | Create, deploy, and trigger a database ingestion pipeline | 2.0 RC1 | Request-model and mocked REST-path tests | [Ingestion automation guide](ingestion-automation/README.md#run-the-example) | Ingestion and Documentation |
| [`mcp`](mcp/) | Workshop for OpenMetadata MCP, Goose, and Jupyter | 2.0 RC1 | Link and seed-file checks only | [MCP workshop](mcp/README.md) | Documentation |

## Support Boundary

CI validates Python imports, emitted requests, structured configuration, Node source syntax, Docker
Compose configuration, documentation links, and secrets. Tests mock network boundaries. CI does
not run live OpenMetadata ingestion, so these prerelease examples are not certified integrations.

Only the six areas in the catalog receive a maintenance commitment. Unsupported historical demos
were removed instead of carrying examples that no longer run against current releases.

## SDK Learning Examples

Python and Java SDK tutorials do not live in this repository. Use the maintained
[OpenMetadata Python SDK documentation](https://docs.open-metadata.org/latest/sdk/python) or the
[Collate Python SDK documentation](https://docs.getcollate.io/sdk/python), which track current API
patterns and releases.

After OpenMetadata 2.0 reaches general availability, the release-candidate package and Docker pins
will be updated to the final 2.0 versions.
