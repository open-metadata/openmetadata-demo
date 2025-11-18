"""
Queries - OpenMetadata SDK Examples

This module demonstrates all read/query operations for retrieving entities.

SDK References:
- Main API: metadata.ingestion.ometa.ometa_api.OpenMetadata
- Documentation: https://docs.open-metadata.org/sdk/python/api-reference/ometa

Source Reference:
- Get by Name: example_apis.py lines 264, 440-441
- List All Entities: example_apis.py lines 443-452, 458-469
- List Entities: example_apis.py lines 287-288

Query operations enable:
- Entity discovery and retrieval
- Field filtering for performance
- Batch retrieval with iteration
- Health monitoring

All examples are working, tested solutions from the original codebase.

PREREQUISITES:
- Entities must exist (run services.py and entities.py first)

USAGE:
1. Update SERVER_URL and JWT_TOKEN below
2. Run: python queries.py
"""

# ============================================================================
# CONNECTION SETUP
# ============================================================================
# NOTE: Each example file is self-contained. Update these values for your
# OpenMetadata instance, then run this file directly.

from metadata.ingestion.ometa.ometa_api import OpenMetadata
from metadata.generated.schema.entity.services.connections.metadata.openMetadataConnection import (
    OpenMetadataConnection,
    AuthProvider,
)
from metadata.generated.schema.security.client.openMetadataJWTClientConfig import (
    OpenMetadataJWTClientConfig,
)

# TODO: Update these values for your OpenMetadata instance
SERVER_URL = "http://localhost:8585/api"
JWT_TOKEN = "eyJraWQiOiJHYjM4OWEtOWY3Ni1nZGpzLWE5MmotMDI0MmJrOTQzNTYiLCJhbGciOiJSUzI1NiIsInR5cCI6IkpXVCJ9.eyJpc3MiOiJvcGVuLW1ldGFkYXRhLm9yZyIsInN1YiI6ImluZ2VzdGlvbi1ib3QiLCJlbWFpbCI6ImluZ2VzdGlvbi1ib3RAb3Blbm1ldGFkYXRhLm9yZyIsImlzQm90Ijp0cnVlLCJ0b2tlblR5cGUiOiJCT1QiLCJpYXQiOjE2OTU0MDkwNDEsImV4cCI6bnVsbH0.G2cmKdidr_lQd8nNy7i_7X3mSqXJsX4cFk0PqRoN0vJwsIiDhtTc7fd5Fi6NzT5ZxTR9BS2jRuaTMJ0dbBXwNaUZM_VDupGA_foSqfktjr6Ho-YRnmP_z6095lPJG9wE6hcWu6oXPWTR-zys0j0SkrUBFjSmYk-f31KW9jINFtR55MMwqe7weCsZkoJJ5O9w7vku4l6MeOfXVEfkVWCZaBKi93EYBlk9GBcV5HkVhjq2sujYtYUw9muwzl_4jiEZwFkeV7TkV8OBFowaT0L0SRyvuVq3hs27gdLLZBPrN3kiLN8JaGnVE2_CFOSdcrFiQVncyFHihY9C_3f113H-Ag"

# How to get JWT token:
# 1. Open OpenMetadata UI
# 2. Go to Settings > Bots > ingestion-bot
# 3. Copy the JWT token
# Or create a new bot and use its token


def get_metadata_client():
    """
    Create authenticated OpenMetadata client.

    Returns:
        OpenMetadata: Authenticated client instance
    """
    security_config = OpenMetadataJWTClientConfig(jwtToken=JWT_TOKEN)
    server_config = OpenMetadataConnection(
        hostPort=SERVER_URL,
        authProvider=AuthProvider.openmetadata,
        securityConfig=security_config,
    )
    return OpenMetadata(server_config)


# ============================================================================
# QUERY EXAMPLES
# ============================================================================

# Import entity types for queries
from metadata.generated.schema.entity.data.table import Table
from metadata.generated.schema.entity.data.database import Database
from metadata.generated.schema.entity.teams.user import User
from metadata.generated.schema.entity.domains.domain import Domain
from metadata.generated.schema.entity.data.glossary import Glossary
from metadata.generated.schema.entity.data.glossaryTerm import GlossaryTerm


# ============================================================================
# EXAMPLE 1: Get Entity by Fully Qualified Name (FQN)
# ----------------------------------------------------------------------------
# Purpose: Retrieve a specific entity using its fully qualified name
# SDK API: metadata.get_by_name()
# Required Args:
#   - entity: Entity class type (e.g., Table, User)
#   - fqn: Fully qualified name (unique identifier)
# Optional Args:
#   - fields: List of fields to include (for performance optimization)
# Reference: https://docs.open-metadata.org/sdk/python/api-reference/ometa
# Source: example_apis.py lines 264, 440-441
# ============================================================================


def get_entity_by_name():
    """
    Get an entity by its fully qualified name.

    FQN (Fully Qualified Name) is the unique identifier for entities:
    - Table: "service.database.schema.table"
    - User: username (e.g., "admin")
    - Database: "service.database"

    Field filtering reduces response size and improves performance.

    Returns:
        Table: Retrieved table entity

    Example:
        >>> table = get_entity_by_name()
        >>> print(f"Table: {table.name}, Columns: {len(table.columns)}")
    """
    metadata = get_metadata_client()

    # Example 1: Get table without field filtering
    # Source: example_apis.py line 264 (used in PATCH operations)
    table_fqn = "test-snowflake.test-db.test-schema.dim_orders"
    table = metadata.get_by_name(entity=Table, fqn=table_fqn)

    print(f"✓ Retrieved table: {table.fullyQualifiedName.__root__}")
    print(f"  Name: {table.name.__root__}")
    print(f"  Database: {table.database.name}")
    print(f"  Columns: {len(table.columns.__root__)}")

    # Example 2: Get table with specific fields (more efficient)
    # Source: example_apis.py line 264 (fields=["owners"])
    table_with_fields = metadata.get_by_name(
        entity=Table, fqn=table_fqn, fields=["owners", "tags", "description"]
    )

    print(f"\n✓ Retrieved table with specific fields:")
    print(f"  Owners: {len(table_with_fields.owners.__root__) if table_with_fields.owners else 0}")
    print(f"  Tags: {len(table_with_fields.tags) if table_with_fields.tags else 0}")

    # Example 3: Get user by name (username before @)
    # Source: example_apis.py lines 440-441
    user_fqn = "admin"  # For admin@openmetadata.org
    user = metadata.get_by_name(entity=User, fqn=user_fqn)

    print(f"\n✓ Retrieved user: {user.fullyQualifiedName.__root__}")
    print(f"  Email: {user.email.__root__}")

    return table


# ============================================================================
# EXAMPLE 2: Get Entity by ID
# ----------------------------------------------------------------------------
# Purpose: Retrieve entity using its UUID
# SDK API: metadata.get_by_id()
# Required Args:
#   - entity: Entity class type
#   - id: UUID string or UUID object
# Optional Args:
#   - fields: List of fields to include
# Use Case: When you have the ID from a reference or previous query
# ============================================================================


def get_entity_by_id():
    """
    Get an entity by its UUID.

    Each entity has a unique ID (UUID). This is useful when:
    - You have an EntityReference with an ID
    - You've stored IDs in your system
    - You're following relationships between entities

    Returns:
        Table: Retrieved table entity

    Example:
        >>> table = get_entity_by_id()
        >>> print(f"Table ID: {table.id}, Name: {table.name}")
    """
    metadata = get_metadata_client()

    # First, get a table to obtain its ID
    table_fqn = "test-snowflake.test-db.test-schema.dim_orders"
    table = metadata.get_by_name(entity=Table, fqn=table_fqn)
    table_id = table.id.__root__

    print(f"Table ID: {table_id}")

    # Get the same table by ID
    table_by_id = metadata.get_by_id(entity=Table, id=str(table_id))

    print(f"\n✓ Retrieved table by ID: {table_by_id.fullyQualifiedName.__root__}")
    print(f"  ID: {table_by_id.id.__root__}")
    print(f"  Name: {table_by_id.name.__root__}")

    # Get with specific fields
    table_by_id_filtered = metadata.get_by_id(
        entity=Table, id=str(table_id), fields=["tags", "owners"]
    )

    print(f"\n✓ Retrieved with field filtering:")
    print(f"  Fields requested: tags, owners")

    return table_by_id


# ============================================================================
# EXAMPLE 3: List All Entities (Iterator Pattern)
# ----------------------------------------------------------------------------
# Purpose: Retrieve all entities of a specific type with pagination
# SDK API: metadata.list_all_entities()
# Required Args:
#   - entity: Entity class type
# Optional Args:
#   - fields: List of fields to include
# Returns: Generator that yields entities (handles pagination automatically)
# Reference: https://docs.open-metadata.org/sdk/python/api-reference/ometa
# Source: example_apis.py lines 443-452
# ============================================================================


def list_all_entities():
    """
    List all entities of a specific type using iterator pattern.

    list_all_entities() returns a generator that automatically handles
    pagination, making it memory-efficient for large datasets.

    Returns:
        list: List of table entities

    Example:
        >>> tables = list_all_entities()
        >>> for table in tables:
        ...     print(f"  - {table.fullyQualifiedName}")
    """
    metadata = get_metadata_client()

    # List all tables with specific fields
    # Source: example_apis.py lines 446-448
    all_tables = metadata.list_all_entities(entity=Table, fields=["tags"])

    print(f"✓ Listing all tables (with tags field):")
    table_count = 0

    # Iterate through all tables (generator pattern)
    # Source: example_apis.py lines 450-452
    for table in all_tables:
        print(f"  - {table.fullyQualifiedName.__root__}")
        # You can process each table here
        # Example: Check tags, update descriptions, etc.
        table_count += 1

        # Limit output for demo
        if table_count >= 5:
            print(f"  ... (showing first 5, more available)")
            break

    print(f"\n  Total tables processed: {table_count}")

    return list(all_tables)  # Convert generator to list (if needed)


# ============================================================================
# EXAMPLE 4: List Entities with Filters
# ----------------------------------------------------------------------------
# Purpose: List entities with query parameters and filtering
# SDK API: metadata.list_entities()
# Required Args:
#   - entity: Entity class type
# Optional Args:
#   - params: Dictionary of query parameters
#   - fields: List of fields to include
# Returns: EntityList with entities and pagination info
# Reference: https://docs.open-metadata.org/sdk/python/api-reference/ometa
# Source: example_apis.py lines 287-288, 463-469
# ============================================================================


def list_entities_with_filters():
    """
    List entities with filtering and query parameters.

    list_entities() returns an EntityList with pagination metadata,
    unlike list_all_entities() which is a generator.

    Use cases:
    - Filter by parent entity (e.g., terms in a glossary)
    - Limit number of results
    - Custom query parameters

    Returns:
        EntityList: List of domain entities

    Example:
        >>> result = list_entities_with_filters()
        >>> print(f"Found {len(result.entities)} domains")
    """
    metadata = get_metadata_client()

    # Example 1: List domains (simple case)
    # Source: example_apis.py line 288
    domains_result = metadata.list_entities(Domain)

    print(f"✓ Listed domains:")
    print(f"  Total: {len(domains_result.entities)}")

    for domain in domains_result.entities:
        print(f"  - {domain.fullyQualifiedName.__root__}")

    # Example 2: List glossary terms filtered by glossary
    # Source: example_apis.py lines 463-469
    print(f"\n✓ Listing glossary terms by parent glossary:")

    # Get all glossaries first
    all_glossaries = metadata.list_all_entities(entity=Glossary, fields=["tags"])

    for glossary in all_glossaries:
        print(f"\n  Glossary: {glossary.name.__root__}")

        # List terms for this specific glossary
        terms = metadata.list_all_entities(
            entity=GlossaryTerm,
            params={"glossary": str(glossary.id.__root__)},  # Filter parameter
            fields=["children", "owner", "parent"],
        )

        term_count = 0
        for term in terms:
            print(f"    - {term.fullyQualifiedName.__root__}")
            term_count += 1

            # Limit output
            if term_count >= 3:
                print(f"    ... (showing first 3)")
                break

        if term_count == 0:
            print(f"    (no terms)")

    return domains_result


# ============================================================================
# EXAMPLE 5: Health Check
# ----------------------------------------------------------------------------
# Purpose: Verify OpenMetadata server connectivity
# SDK API: metadata.health_check()
# Required Args: None
# Returns: None (raises exception if unhealthy)
# Use Case: Monitoring, pre-flight checks, error diagnostics
# Source: example_apis.py line 97
# ============================================================================


def health_check():
    """
    Perform health check on OpenMetadata server.

    health_check() verifies that:
    - Server is reachable
    - Authentication is valid
    - API is responsive

    Use this for:
    - Application startup checks
    - Monitoring/alerting
    - Debugging connection issues

    Returns:
        bool: True if healthy, False otherwise

    Example:
        >>> if health_check():
        ...     print("Server is healthy")
    """
    metadata = get_metadata_client()

    try:
        # Perform health check
        # Source: example_apis.py line 97
        metadata.health_check()

        print(f"✓ Health check passed")
        print(f"  Server: {SERVER_URL}")
        print(f"  Status: Healthy")
        print(f"  Authentication: Valid")

        return True

    except Exception as e:
        print(f"✗ Health check failed")
        print(f"  Server: {SERVER_URL}")
        print(f"  Error: {e}")
        print(f"\n  Troubleshooting:")
        print(f"  1. Verify server is running")
        print(f"  2. Check SERVER_URL is correct")
        print(f"  3. Verify JWT token is valid")
        print(f"  4. Check network connectivity")

        return False


# ============================================================================
# EXAMPLE 6: Query Patterns & Best Practices
# ----------------------------------------------------------------------------
# Purpose: Demonstrate common query patterns and optimization techniques
# ============================================================================


def query_patterns_and_best_practices():
    """
    Demonstrate common query patterns and best practices.

    This example shows:
    - Error handling for missing entities
    - Field filtering for performance
    - Efficient iteration patterns
    - Conditional queries

    Returns:
        dict: Results of various query patterns

    Example:
        >>> results = query_patterns_and_best_practices()
        >>> print(f"Patterns tested: {len(results)}")
    """
    metadata = get_metadata_client()
    results = {}

    # Pattern 1: Safe entity retrieval with error handling
    print("✓ Pattern 1: Safe entity retrieval")
    try:
        table = metadata.get_by_name(
            entity=Table, fqn="test-snowflake.test-db.test-schema.dim_orders"
        )
        results["table_exists"] = True
        print(f"  Table found: {table.name.__root__}")
    except Exception as e:
        results["table_exists"] = False
        print(f"  Table not found: {e}")

    # Pattern 2: Minimal field retrieval for performance
    print("\n✓ Pattern 2: Minimal field retrieval")
    table_minimal = metadata.get_by_name(
        entity=Table,
        fqn="test-snowflake.test-db.test-schema.dim_orders",
        fields=["name"],  # Only fetch name field
    )
    print(f"  Retrieved with minimal fields: {table_minimal.name.__root__}")
    results["minimal_fields"] = True

    # Pattern 3: Batch processing with pagination
    print("\n✓ Pattern 3: Batch processing")
    batch_size = 2
    processed = 0

    for table in metadata.list_all_entities(entity=Table, fields=["name"]):
        # Process each table
        processed += 1
        print(f"  Processing: {table.name.__root__}")

        # Stop after batch_size for demo
        if processed >= batch_size:
            break

    results["batch_processed"] = processed

    # Pattern 4: Conditional queries
    print("\n✓ Pattern 4: Conditional queries")
    domains = metadata.list_entities(Domain).entities
    if len(domains) > 0:
        print(f"  Found {len(domains)} domains")
        results["domains_found"] = len(domains)
    else:
        print(f"  No domains found")
        results["domains_found"] = 0

    return results


# ============================================================================
# MAIN - Run All Query Examples
# ============================================================================

if __name__ == "__main__":
    print("=" * 70)
    print("OpenMetadata SDK - Query Examples")
    print("=" * 70)
    print()
    print("NOTE: Ensure entities exist (run services.py and entities.py first)")
    print()

    try:
        # Example 1: Get by Name
        print("1. Getting entity by name (FQN)...")
        get_entity_by_name()
        print()

        # Example 2: Get by ID
        print("2. Getting entity by ID...")
        get_entity_by_id()
        print()

        # Example 3: List All Entities
        print("3. Listing all entities (iterator pattern)...")
        list_all_entities()
        print()

        # Example 4: List with Filters
        print("4. Listing entities with filters...")
        list_entities_with_filters()
        print()

        # Example 5: Health Check
        print("5. Performing health check...")
        health_check()
        print()

        # Example 6: Query Patterns
        print("6. Demonstrating query patterns and best practices...")
        query_patterns_and_best_practices()
        print()

        print("=" * 70)
        print("✓ All query examples completed successfully!")
        print("=" * 70)
        print("\nQuery Best Practices:")
        print("  - Use field filtering to reduce response size")
        print("  - Handle exceptions for missing entities")
        print("  - Use list_all_entities() for complete iteration")
        print("  - Use list_entities() for filtered/limited results")
        print("  - Implement health checks for monitoring")
        print("\nNext steps:")
        print("  - Run 'python advanced.py' for advanced patterns")
        print("  - Check OpenMetadata UI to explore entities")

    except Exception as e:
        print(f"\n✗ Error: {e}")
        print("\nTroubleshooting:")
        print("  1. Ensure entities exist (run: python entities.py)")
        print("  2. Verify OpenMetadata server is running")
        print("  3. Check connection credentials")
        print("  4. Try health_check() to diagnose issues")
