# OpenMetadata Custom GraphQL Demo

This demo shows how to create a GraphQL server and custom OpenMetadata connector to update user entities with displayName and domain information.

## Components

1. **GraphQL Server** (`/`) - Simple GraphQL server serving static user data
2. **Custom Connector** (`/user-connector`) - OpenMetadata connector that fetches from GraphQL and updates user entities

## Quick Start

### 1. Start GraphQL Server
```bash
npm install
npm start
```
Server runs at http://localhost:4000/

### 2. Run Custom Connector
```bash
cd connector
python3 -m venv venv
source venv/bin/activate
pip install .
metadata ingest -c user_updater.yaml
```

## Data Flow

1. GraphQL server provides user data with Finance/Marketing domains
2. Custom connector fetches this data
3. Connector updates OpenMetadata user entities using PatchRequest pattern
4. Users get updated displayNames and domain associations

## For detailed instructions, see [user-connector/README.md](../README.md)