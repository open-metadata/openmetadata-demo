# Developers

How to run the examples in this repository locally and contribute new ones.

## Prerequisites

- **Python 3.9+** (3.10 or 3.11 recommended)
- **Docker** and **Docker Compose** — to run OpenMetadata locally
- **Git**

## Run OpenMetadata locally

The fastest path is Docker Compose:

```bash
mkdir openmetadata-docker && cd openmetadata-docker
curl -sL -o docker-compose.yml https://github.com/open-metadata/OpenMetadata/releases/latest/download/docker-compose.yml
docker compose up -d
```

The UI comes up at **http://localhost:8585** and the API at **http://localhost:8585/api**. First boot takes a few minutes while Elasticsearch and the database initialize.

Full deployment options (Kubernetes, Helm, bare metal): https://docs.open-metadata.org/latest/deployment

## Get an authentication token

Most examples need a JWT.

1. Open http://localhost:8585
2. Go to **Settings → Bots → ingestion-bot**
3. Copy the token

Export it along with your host:

```bash
export OPENMETADATA_HOST="http://localhost:8585/api"
export OPENMETADATA_JWT_TOKEN="<your-token>"
```

Never commit tokens. Use environment variables or a local `.env` that stays untracked.

## Set up a Python environment

```bash
python -m venv .venv
source .venv/bin/activate        # Windows: .venv\Scripts\activate

pip install "openmetadata-ingestion~=1.13.1.0"
```

**Version matching matters.** The SDK version should match your OpenMetadata server version. A 1.13 server with a 1.11 SDK will fail on schema differences. Check your server version at the bottom of the UI, or:

```bash
curl -s http://localhost:8585/api/v1/system/version
```

## Run an example

```bash
python example_apis.py
```

Read-only operations run by default. Write operations (create, update, delete, lineage) are commented out in `main()` — uncomment the ones you want.

Individual example folders have their own README with setup specific to that integration. Some need extra dependencies:

```bash
cd custom-connector
pip install -r requirements.txt   # where present
```

## Repository layout

Each top-level folder is a self-contained example. Folders do not depend on each other — copy the one you need.

| Folder | Purpose |
|--------|---------|
| `sdk-examples/` | Python SDK usage — entities, lineage, search, ownership |
| `mcp/` | Connect AI assistants and agents over MCP |
| `custom-connector/` | Build a custom ingestion connector |
| `ingestion-automation/`, `ingestion-github-actions/` | Programmatic and CI-driven ingestion |
| `api-lineage-cicd/`, `hive-lineage/` | Lineage from pipelines and query history |
| `test-suite/` | Data quality tests and assertions |
| `keycloak-sso/`, `sso-with-ssl/` | Authentication and TLS |
| `postgres/`, `redpanda/`, `grafana/` | Source-specific integrations |

## Troubleshooting

**`Could not connect to OpenMetadata`** — Confirm the server is up (`docker compose ps`) and that `OPENMETADATA_HOST` ends in `/api`.

**`401 Unauthorized`** — The token expired or is wrong. Regenerate it under Settings → Bots.

**Pydantic validation errors on create** — Almost always an SDK/server version mismatch. Align the versions.

**`Table not found`** — The sample-data FQNs assume the bundled sample connector ran. Point `OPENMETADATA_SAMPLE_TABLE` at a table that exists in your instance.

## Contributing

1. Fork and branch from `main`.
2. Keep each example self-contained — no cross-folder imports.
3. Include a `README.md` in any new folder: what it demonstrates, prerequisites, and how to run it.
4. Use environment variables for hosts and tokens; never hard-code credentials.
5. Verify your example runs against a current OpenMetadata release before opening a PR.

Issues and pull requests: https://github.com/open-metadata/openmetadata-demo

## Links

- **Docs:** https://docs.open-metadata.org/latest
- **Python SDK:** https://docs.open-metadata.org/latest/sdk/python
- **MCP guide:** https://docs.open-metadata.org/latest/how-to-guides/mcp
- **Main repo:** https://github.com/open-metadata/OpenMetadata
- **Slack community:** https://slack.open-metadata.org
