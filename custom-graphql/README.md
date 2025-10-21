# User Updater Custom Connector

A custom OpenMetadata connector that fetches user data from a GraphQL server and updates user entities in OpenMetadata with `displayName` and `domain` information.

## Overview

This connector:
1. Fetches user data from a GraphQL endpoint
2. Finds existing users in OpenMetadata by email
3. Compares current `displayName` and `domains` with GraphQL data
4. Creates `CreateUserRequest` only for users that need updates
5. Follows OpenMetadata's connector patterns for proper integration

## Prerequisites

- OpenMetadata 1.9.11 or higher
- GraphQL server running (our custom GraphQL server from this demo)
- Python 3.10+

## Quickstart

```bash
python3 -m venv venv
source venv/bin/activate
pip install .
metadata ingest -c user_updater.yaml
```

## Installation & Usage

1. **Set up the environment:**
```bash
python3 -m venv venv
source venv/bin/activate
```

2. **Install the connector:**
```bash
pip install .
```

3. **Configure your settings:**
   - Update `user_updater.yaml` with your OpenMetadata server details
   - Ensure GraphQL server is running on `http://localhost:4000`
   - Set the correct JWT token in the configuration

4. **Run the connector:**
```bash
metadata ingest -c user_updater.yaml
```

## Configuration

The connector is configured through the `user_updater.yaml` file. Key settings:

```yaml
source:
  type: connector.user_updater.UserUpdaterSource
  serviceName: user_updater_service
  serviceConnection:
    config:
      type: Custom
      sourcePythonClass: connector.user_updater.UserUpdaterSource
  sourceConfig:
    config:
      graphql_endpoint: "http://localhost:4000"  # Your GraphQL server endpoint
      
workflowConfig:
  loggerLevel: INFO
  openMetadataServerConfig:
    hostPort: "http://localhost:8585/api"        # Your OpenMetadata server
    authProvider: "openmetadata"
    securityConfig:
      jwtToken: "your-jwt-token-here"            # Your JWT token from OpenMetadata
```

**Important Configuration Notes:**
- **JWT Token**: Get your JWT token from OpenMetadata UI → Settings → Bots → ingestion-bot
- **GraphQL Endpoint**: Ensure your GraphQL server is accessible from where the connector runs
- **OpenMetadata Server**: Update the hostPort to match your OpenMetadata instance

## How it Works

### 1. GraphQL Query
The connector queries your GraphQL server for user data:
```graphql
{
  users {
    email
    displayName
    domain
  }
}
```

### 2. User Matching & Change Detection
- Finds existing OpenMetadata users by email address
- Compares current `displayName` with GraphQL data
- Compares current `domains` with GraphQL domain mappings
- Only processes users that have changes

### 3. Selective Updates
- Creates `CreateUserRequest` only for users with changes
- Preserves existing user `name` and other fields
- Updates only `displayName` and `domains` fields
- Logs specific changes being made

### 4. Domain Linking
The connector tries to find domain entities in OpenMetadata that match the domain names from GraphQL data. If found, it creates proper `EntityReference` objects to link users to domains.

## Expected GraphQL Response Format

Your GraphQL server should return data in this format:
```json
{
  "data": {
    "users": [
      {
        "email": "admin@open-metadata.org",
        "displayName": "Admin User", 
        "domain": "Finance"
      },
      {
        "email": "aaron_johnson0@gmail.com",
        "displayName": "Aaron Johnson",
        "domain": "Marketing"
      },
      {
        "email": "brian_smith7@gmail.com",
        "displayName": "Brian Smith",
        "domain": "Finance"
      }
    ]
  }
}
```

**Domain Requirements:**
- Domains should match existing OpenMetadata domain entities
- In this example: "Finance" and "Marketing" domains should exist in your OpenMetadata instance
- Users will be linked to these domain entities via EntityReference

## Troubleshooting

### Common Issues

1. **GraphQL Connection Failed**
   - Verify GraphQL server is running
   - Check endpoint URL in configuration
   - Ensure GraphQL server is accessible from connector

2. **User Update Issues**
   - Verify users exist in OpenMetadata with matching email addresses
   - Check OpenMetadata connection settings
   - Verify JWT token has proper permissions for user updates

3. **Domain References Not Working**
   - Ensure domain entities exist in OpenMetadata
   - Domain names must match exactly (case-insensitive)
   - Check OpenMetadata logs for domain lookup errors

### Logs

The connector provides detailed logging:
- `INFO`: Successful operations and progress
- `WARNING`: Domain not found issues
- `ERROR`: Connection failures and critical errors
- `DEBUG`: Detailed troubleshooting information

## Development Notes

This connector follows OpenMetadata's custom connector patterns:

1. **Extends Source class**: Inherits from `metadata.ingestion.api.steps.Source`
2. **Implements _iter() method**: Generator function that yields `Either` objects
3. **Uses CreateUserRequest**: Proper entity update mechanism for selective changes
4. **Change Detection**: Compares existing vs. new values to avoid unnecessary updates
5. **Error handling**: Uses `Either` class with `StackTraceError` for proper error reporting
6. **Entity caching**: Preloads domains and users for efficient lookups

## Files Structure

```
user-connector/
├── server/                      # GraphQL server for demo data
│   ├── index.js
│   ├── schema.js
│   ├── resolvers.js
│   └── package.json
├── connector/
│   ├── __init__.py
│   └── user_updater.py          # Main connector logic with change detection and selective updates
├── setup.py                     # Python package setup with openmetadata-ingestion==1.9.11
├── user_updater.yaml           # Connector configuration
└── README.md                   # This documentation
```

## Scheduling Regular Runs

To keep user data synchronized, you can:

1. **Set up a cron job** to run the connector periodically:
```bash
# Run every hour
0 * * * * cd /path/to/connector && source venv/bin/activate && metadata ingest -c user_updater.yaml
```

2. **Use OpenMetadata UI** to schedule the connector as a service workflow

## Next Steps

1. Ensure your GraphQL server is running with the Finance/Marketing domain data
2. Create Finance and Marketing domain entities in OpenMetadata 
3. Ensure target users exist in OpenMetadata (the connector updates existing users)
4. Run the connector to update user displayNames and domain associations from your GraphQL data