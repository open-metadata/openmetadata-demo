# GraphQL User Updater

> [!IMPORTANT]
> This example targets `openmetadata-ingestion==2.0.0.0rc1`. It is not compatible with
> OpenMetadata 1.x.

This custom source reads user attributes from a GraphQL endpoint. It applies targeted JSON Patch
updates to the display name and domains of matching OpenMetadata users. It demonstrates change
detection, domain lookup, and safe handling of users that do not exist in OpenMetadata without
replacing unrelated user fields.

## Run the Example

Start the included GraphQL fixture server:

```bash
cd custom-graphql/server
npm ci
npm start
```

In another terminal, install and run the connector:

```bash
python3 -m venv .venv
source .venv/bin/activate
python -m pip install --editable ./custom-graphql

export GRAPHQL_ENDPOINT="http://localhost:4000/"
export OPENMETADATA_HOST="http://localhost:8585/api"
export OPENMETADATA_JWT_TOKEN="<privileged-personal-access-token>"
metadata ingest -c custom-graphql/user_updater.yaml
```

Create the Finance and Marketing domains and the fixture users in OpenMetadata before running the
workflow. Use a Personal Access Token (PAT) for a non-bot principal that is authorized to edit user
display names and domains. The default ingestion-bot policy cannot make these changes. The
connector updates existing users and deliberately does not create missing accounts.

The source calls the OpenMetadata SDK's targeted patch API itself because the 2.0 RC metadata sink
does not support bulk user updates. The required `metadata-rest` sink remains configured for the
standard metadata workflow but receives no user entity to replace.

## Validation Boundary

Repository tests validate the 2.0 workflow model, environment expansion, targeted patch planning,
and mocked GraphQL/OpenMetadata behavior. They do not contact a live GraphQL or OpenMetadata
server.
