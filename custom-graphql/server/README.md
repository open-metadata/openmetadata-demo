# GraphQL Fixture Server

This directory contains the deterministic GraphQL API used by the OpenMetadata 2.0 user updater
example. It serves three static user records and does not connect to OpenMetadata.

## Run the Server

From the repository root, run:

```bash
cd custom-graphql/server
npm ci
npm start
```

The server listens on `http://localhost:4000/`. Test it with this query:

```graphql
{
  users {
    email
    displayName
    domain
  }
}
```

For connector installation, environment variables, and ingestion commands, see the
[GraphQL user updater guide](../README.md#run-the-example).
