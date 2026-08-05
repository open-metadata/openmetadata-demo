# OpenMetadata Demo — Runnable Examples

Runnable examples for **[OpenMetadata](https://github.com/open-metadata/OpenMetadata)**, the open-source data catalog and metadata platform for data discovery, lineage, governance, data quality, and AI context. Each folder is self-contained: copy it, set your host and token, run it.

## Quickstart

The Python SDK ships in the `openmetadata-ingestion` package. Match the version to your OpenMetadata server:

```bash
pip install "openmetadata-ingestion~=1.13.1.0"
```

Connect and verify:

```python
from metadata.generated.schema.entity.services.connections.metadata.openMetadataConnection import (
    OpenMetadataConnection, AuthProvider,
)
from metadata.generated.schema.security.client.openMetadataJWTClientConfig import (
    OpenMetadataJWTClientConfig,
)
from metadata.ingestion.ometa.ometa_api import OpenMetadata

metadata = OpenMetadata(OpenMetadataConnection(
    hostPort="http://localhost:8585/api",
    authProvider=AuthProvider.openmetadata,
    securityConfig=OpenMetadataJWTClientConfig(jwtToken="<your-token>"),
))
assert metadata.health_check()   # True when connected
```

Read an entity:

```python
from metadata.generated.schema.entity.data.table import Table

table = metadata.get_by_name(
    entity=Table,
    fqn="sample_data.ecommerce_db.shopify.raw_product_catalog",
)
print(table.description)
print([c.name.root for c in table.columns])
```

**Entity hierarchy:** a Table belongs to a Schema, which belongs to a Database, which belongs to a DatabaseService. Every entity references its parent by `fullyQualifiedName` — start at the service and work down.

## Connect an AI assistant (MCP)

OpenMetadata includes a built-in **MCP server**, so AI assistants and agents can search your catalog, traverse lineage, and read governed context over the Model Context Protocol. See **[`mcp/`](mcp/)** for a working setup.

```bash
pip install data-ai-sdk
```

```python
from ai_sdk import AISdk, AISdkConfig

client = AISdk.from_config(AISdkConfig.from_env())
tools = client.mcp.as_langchain_tools()          # LangChain-ready in one line
result = client.mcp.call_tool("search_metadata", {"query": "customers"})
```

## What's in here

| Folder | What it shows |
|--------|---------------|
| [`mcp/`](mcp/) | Connect AI assistants and agents to OpenMetadata over MCP |
| [`custom-connector/`](custom-connector/) | Build a custom ingestion connector (Python, protobuf, Docker) |
| [`ingestion-automation/`](ingestion-automation/) | Deploy ingestion pipelines programmatically |
| [`ingestion-github-actions/`](ingestion-github-actions/) | Run metadata ingestion from CI |
| [`api-lineage-cicd/`](api-lineage-cicd/) | Push lineage from a CI/CD pipeline via the API |
| [`hive-lineage/`](hive-lineage/) | Lineage for Hive workloads |
| [`test-suite/`](test-suite/) | Data quality tests and assertions |
| [`custom-graphql/`](custom-graphql/) | Query metadata through GraphQL |
| [`dynamic_csv_importer/`](dynamic_csv_importer/) | Bulk-import metadata from CSV |
| [`mlmodel-cicd/`](mlmodel-cicd/) | Register and track ML models |
| [`webhook_endpoint/`](webhook_endpoint/) | Receive OpenMetadata change events |
| [`keycloak-sso/`](keycloak-sso/), [`sso-with-ssl/`](sso-with-ssl/) | SSO and TLS configuration |
| [`postgres/`](postgres/), [`postgres-foreign/`](postgres-foreign/), [`redpanda/`](redpanda/), [`grafana/`](grafana/) | Source-specific integrations |
| [`rename-service/`](rename-service/), [`scripts/`](scripts/) | Operational utilities |

## SDKs

| SDK | Package | Install |
|-----|---------|---------|
| Python (metadata operations) | [`openmetadata-ingestion`](https://pypi.org/project/openmetadata-ingestion/) | `pip install "openmetadata-ingestion~=1.13.1.0"` |
| Python (AI / MCP / agents) | [`data-ai-sdk`](https://pypi.org/project/data-ai-sdk/) | `pip install data-ai-sdk` |
| TypeScript | [`@openmetadata/ai-sdk`](https://www.npmjs.com/package/@openmetadata/ai-sdk) | `npm install @openmetadata/ai-sdk` |
| Java | [`org.open-metadata:ai-sdk`](https://central.sonatype.com/artifact/org.open-metadata/ai-sdk) | Maven / Gradle |

## Documentation

- **Python SDK reference:** https://docs.open-metadata.org/latest/sdk/python
- **MCP server guide:** https://docs.open-metadata.org/latest/how-to-guides/mcp
- **AI SDK repo:** https://github.com/open-metadata/ai-sdk
- **Main project:** https://github.com/open-metadata/OpenMetadata
- **Docs home:** https://docs.open-metadata.org/latest
