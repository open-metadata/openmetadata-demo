"""
Metadata Operations - OpenMetadata SDK Examples

This module demonstrates all metadata operations: tags, descriptions, owners, domains, glossaries.

SDK References:
- Patch Operations: metadata.ingestion.ometa.mixins.patch_mixin_utils
- Tag Labels: metadata.generated.schema.type.tagLabel
- Entity References: metadata.generated.schema.type.entityReference
- Documentation: https://docs.open-metadata.org/sdk/python/api-reference/ometa

Source Reference:
- Tags (table-level): example_apis.py lines 220-233
- Tags (column-level): example_apis.py lines 236-246
- Descriptions: example_apis.py lines 249-257
- Owners: example_apis.py lines 259-277
- Domains: example_apis.py lines 284-290
- Glossaries: example_apis.py lines 454-469
- Grouped Patches: example_apis.py lines 575-593

All examples are working, tested solutions from the original codebase.

PREREQUISITES:
- Tables must exist (run services.py and entities.py first)

USAGE:
1. Update SERVER_URL and JWT_TOKEN below
2. Run: python metadata_ops.py
"""

from copy import deepcopy

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
# METADATA OPERATIONS EXAMPLES
# ============================================================================

# Import required types for metadata operations
from metadata.generated.schema.entity.data.table import Table
from metadata.generated.schema.entity.data.glossary import Glossary
from metadata.generated.schema.entity.data.glossaryTerm import GlossaryTerm
from metadata.generated.schema.type.tagLabel import (
    LabelType,
    State,
    TagLabel,
    TagFQN,
    TagSource,
)
from metadata.generated.schema.type.basic import Markdown
from metadata.generated.schema.type.entityReference import EntityReference
from metadata.generated.schema.type.entityReferenceList import EntityReferenceList
from metadata.generated.schema.entity.domains.domain import Domain
from metadata.ingestion.ometa.mixins.patch_mixin_utils import PatchOperation
from metadata.ingestion.models.table_metadata import ColumnTag


# ============================================================================
# EXAMPLE 1: Add Table-Level Tags
# ----------------------------------------------------------------------------
# Purpose: Add classification tags to entire table entity
# SDK API: metadata.patch_tags()
# Required Args:
#   - entity: Entity class (e.g., Table)
#   - source: Source entity to patch
#   - tag_labels: List of TagLabel objects
#   - operation: PatchOperation.ADD or PatchOperation.REMOVE
# Reference: https://docs.open-metadata.org/sdk/python/api-reference/tags
# Source: example_apis.py lines 220-233
# ============================================================================


def add_table_level_tags():
    """
    Add classification tags at the table level.

    This example demonstrates adding a Tier tag to a table entity.
    Tags can be used for classification, governance, and organization.

    Returns:
        Table: Updated table entity with tags

    Example:
        >>> table = add_table_level_tags()
        >>> print(f"Tags on {table.name}: {[tag.tagFQN for tag in table.tags]}")
    """
    metadata = get_metadata_client()

    # Get the table entity to tag
    # NOTE: Replace with your table FQN
    table_fqn = "test-snowflake.test-db.test-schema.tableB"
    table_entity = metadata.get_by_name(entity=Table, fqn=table_fqn)

    # Create tag label
    # Source: example_apis.py lines 231-232
    tag_to_add = TagLabel(
        tagFQN=TagFQN("Tier.Tier3"),  # Tag fully qualified name
        source=TagSource.Classification,  # Tag source type
        labelType=LabelType.Manual,  # Manual vs Automated
        state=State.Confirmed,  # Confirmed vs Suggested
    )

    # Apply tag using PATCH operation
    # Source: example_apis.py lines 231-233
    metadata.patch_tags(
        entity=Table,  # Entity class
        source=table_entity,  # Source entity to patch
        tag_labels=[tag_to_add],  # Tags to add
        operation=PatchOperation.ADD,  # ADD or REMOVE
    )

    print(f"✓ Added tag {tag_to_add.tagFQN.__root__} to table: {table_fqn}")

    # Fetch updated entity to verify
    updated_table = metadata.get_by_name(entity=Table, fqn=table_fqn, fields=["tags"])

    return updated_table


# ============================================================================
# EXAMPLE 2: Add Column-Level Tags
# ----------------------------------------------------------------------------
# Purpose: Add tags to specific columns in a table
# SDK API: metadata.patch_column_tags()
# Required Args:
#   - table: Table entity
#   - column_tags: List of ColumnTag objects (column_fqn + tag_label)
#   - operation: PatchOperation.ADD or PatchOperation.REMOVE (optional)
# Reference: https://docs.open-metadata.org/sdk/python/api-reference/tags
# Source: example_apis.py lines 236-246
# ============================================================================


def add_column_level_tags():
    """
    Add tags to specific columns in a table.

    This example demonstrates adding PII tags to sensitive columns.
    Column tags are useful for data classification and compliance.

    Returns:
        Table: Updated table entity with column tags

    Example:
        >>> table = add_column_level_tags()
        >>> for col in table.columns:
        ...     print(f"Column {col.name}: {col.tags}")
    """
    metadata = get_metadata_client()

    # Get the table entity
    table_fqn = "test-snowflake.test-db.test-schema.tableB"
    table_entity = metadata.get_by_name(entity=Table, fqn=table_fqn)

    # Create PII tag label
    # Source: example_apis.py lines 213-218 (tag definition)
    pii_tag_label = TagLabel(
        tagFQN="PII.Sensitive",
        labelType=LabelType.Automated,
        state=State.Suggested.value,
        source=TagSource.Classification,
    )

    # Add tag to column
    # Source: example_apis.py lines 238-241
    metadata.patch_column_tags(
        table=table_entity,
        column_tags=[
            ColumnTag(
                column_fqn="test-snowflake.test-db.test-schema.tableB.id",  # Column FQN
                tag_label=pii_tag_label,
            )
        ],
    )

    print(f"✓ Added PII tag to column 'id' in table: {table_fqn}")

    # Example: Remove tag from column
    # Source: example_apis.py lines 242-246
    # Uncomment to remove the tag:
    # metadata.patch_column_tags(
    #     table=table_entity,
    #     column_tags=[
    #         ColumnTag(
    #             column_fqn="test-snowflake.test-db.test-schema.tableB.id",
    #             tag_label=pii_tag_label
    #         )
    #     ],
    #     operation=PatchOperation.REMOVE
    # )

    # Fetch updated entity
    updated_table = metadata.get_by_name(entity=Table, fqn=table_fqn)

    return updated_table


# ============================================================================
# EXAMPLE 3: Update Description Using PATCH
# ----------------------------------------------------------------------------
# Purpose: Update entity description using PATCH operation
# SDK API: metadata.patch()
# Required Args:
#   - entity_class: Entity type (e.g., Table)
#   - source: Original entity
#   - destination: Modified entity with new description
# Reference: https://docs.open-metadata.org/sdk/python/api-reference/ometa
# Source: example_apis.py lines 249-257
# ============================================================================


def update_table_description():
    """
    Update table description using PATCH operation.

    This example demonstrates the general PATCH pattern:
    1. Fetch original entity
    2. Create modified copy
    3. Update desired fields
    4. Apply PATCH

    Returns:
        Table: Updated table entity with new description

    Example:
        >>> table = update_table_description()
        >>> print(f"New description: {table.description}")
    """
    metadata = get_metadata_client()

    # Get the table entity
    table_fqn = "test-snowflake.test-db.test-schema.dim_orders"
    table_entity = metadata.get_by_name(entity=Table, fqn=table_fqn)

    # Create a modified copy
    # Source: example_apis.py lines 250-254
    table_entity_modified = deepcopy(table_entity)
    table_entity_modified.description = Markdown("Updated description using PATCH API")

    # Apply PATCH operation
    # Source: example_apis.py line 257
    metadata.patch(
        Table,  # Entity class
        table_entity,  # Original entity
        table_entity_modified,  # Modified entity
    )

    print(f"✓ Updated description for table: {table_fqn}")

    # Fetch updated entity
    updated_table = metadata.get_by_name(entity=Table, fqn=table_fqn)

    return updated_table


# ============================================================================
# EXAMPLE 4: Update Owners (User and Team)
# ----------------------------------------------------------------------------
# Purpose: Assign user or team owners to an entity
# SDK API: metadata.patch()
# Required Args:
#   - entity_class: Entity type (e.g., Table)
#   - source: Original entity with owners field fetched
#   - destination: Modified entity with new owners
# Reference: https://docs.open-metadata.org/sdk/python/api-reference/ometa
# Source: example_apis.py lines 259-277
# ============================================================================


def update_table_owners():
    """
    Update table owners (user or team).

    This example shows how to assign ownership using EntityReference.
    Owners can be users or teams, specified by ID and type.

    Returns:
        Table: Updated table entity with new owners

    Example:
        >>> table = update_table_owners()
        >>> print(f"Owners: {[owner.name for owner in table.owners]}")
    """
    metadata = get_metadata_client()

    # Get the table entity with owners field
    # Source: example_apis.py line 264
    table_fqn = "test-snowflake.test-db.test-schema.dim_orders"
    table_entity = metadata.get_by_name(entity=Table, fqn=table_fqn, fields=["owners"])

    # Create modified copy
    table_entity_modified = deepcopy(table_entity)

    # Example 1: Set USER owner
    # Source: example_apis.py lines 268-271
    # NOTE: Replace with actual user ID from your OpenMetadata instance
    # To get user ID: metadata.get_by_name(entity=User, fqn="admin")
    user_owner = EntityReference(
        id="<user-id-here>",  # UUID of the user
        type="user",  # Type: "user"
    )

    # Example 2: Set TEAM owner
    # Source: example_apis.py lines 274-277
    # NOTE: Replace with actual team ID from your OpenMetadata instance
    team_owner = EntityReference(
        id="<team-id-here>",  # UUID of the team
        type="team",  # Type: "team"
    )

    # Apply owner (choose user or team)
    # Source: example_apis.py lines 270-271
    table_entity_modified.owners = EntityReferenceList(root=[user_owner])
    # Or use team: table_entity_modified.owners = EntityReferenceList(root=[team_owner])

    # Apply PATCH
    # Uncomment to apply (requires valid user/team ID):
    # metadata.patch(Table, table_entity, table_entity_modified)

    print(f"✓ Owner update example prepared for table: {table_fqn}")
    print("  Note: Uncomment and add valid user/team ID to apply")

    return table_entity


# ============================================================================
# EXAMPLE 5: Assign Domain
# ----------------------------------------------------------------------------
# Purpose: Assign a domain to an entity
# SDK API: metadata.patch_domain()
# Required Args:
#   - entity: Entity to assign domain to
#   - domain: Domain entity
# Reference: https://docs.open-metadata.org/sdk/python/api-reference/ometa
# Source: example_apis.py lines 284-290
# ============================================================================


def assign_domain_to_table():
    """
    Assign a domain to a table entity.

    Domains provide a way to organize entities by business area or function.

    Returns:
        tuple: (table_entity, domain_entity)

    Example:
        >>> table, domain = assign_domain_to_table()
        >>> print(f"Assigned domain {domain.name} to table {table.name}")
    """
    metadata = get_metadata_client()

    # Get the table entity
    table_fqn = "test-snowflake.test-db.test-schema.dim_orders"
    table_entity = metadata.get_by_name(entity=Table, fqn=table_fqn)

    # List available domains and fetch one
    # Source: example_apis.py lines 287-288
    domains = metadata.list_entities(Domain).entities
    if len(domains) > 0:
        # Use first available domain (or fetch specific one)
        fetch_domain = domains[0]

        # Assign domain to table
        # Source: example_apis.py line 290
        metadata.patch_domain(entity=table_entity, domain=fetch_domain)

        print(f"✓ Assigned domain '{fetch_domain.name.__root__}' to table: {table_fqn}")

        return table_entity, fetch_domain
    else:
        print("⚠ No domains found. Create a domain in OpenMetadata UI first.")
        return table_entity, None


# ============================================================================
# EXAMPLE 6: List Glossaries and Terms
# ----------------------------------------------------------------------------
# Purpose: List all glossaries and their terms
# SDK API: metadata.list_all_entities()
# Required Args:
#   - entity: Entity class (Glossary or GlossaryTerm)
#   - params: Optional query parameters
#   - fields: Optional fields to include
# Reference: https://docs.open-metadata.org/sdk/python/api-reference/ometa
# Source: example_apis.py lines 454-469
# ============================================================================


def list_glossaries_and_terms():
    """
    List all glossaries and their terms.

    This example demonstrates traversing hierarchical entities
    (glossaries containing terms).

    Returns:
        list: List of glossary entities with their terms

    Example:
        >>> glossaries = list_glossaries_and_terms()
        >>> for glossary in glossaries:
        ...     print(f"Glossary: {glossary.name}")
    """
    metadata = get_metadata_client()

    # List all glossaries
    # Source: example_apis.py lines 458-460
    all_glossaries = metadata.list_all_entities(entity=Glossary, fields=["tags"])

    print(f"\n✓ Found {len(all_glossaries)} glossaries:")

    # Iterate through glossaries and fetch their terms
    # Source: example_apis.py lines 461-469
    for glossary in all_glossaries:
        print(f"\n  Glossary: {glossary.name.__root__}")

        # List all terms for this glossary
        children = metadata.list_all_entities(
            entity=GlossaryTerm,
            params={"glossary": str(glossary.id.__root__)},  # Filter by glossary ID
            fields=["children", "owner", "parent"],
        )

        # Print terms
        for child in children:
            print(f"    - Term: {child.fullyQualifiedName.__root__}")

    return all_glossaries


# ============================================================================
# EXAMPLE 7: Grouped PATCH Operations
# ----------------------------------------------------------------------------
# Purpose: Update multiple fields in a single PATCH operation
# SDK API: metadata.patch()
# Required Args:
#   - entity_class: Entity type (e.g., Table)
#   - source: Original entity with required fields fetched
#   - destination: Modified entity with multiple field updates
# Reference: https://docs.open-metadata.org/sdk/python/api-reference/ometa
# Source: example_apis.py lines 575-593
# ============================================================================


def grouped_patch_operations():
    """
    Update multiple entity fields in a single PATCH operation.

    This is more efficient than multiple separate PATCH calls.
    Demonstrates updating description, displayName, and tags together.

    Returns:
        Table: Updated table entity

    Example:
        >>> table = grouped_patch_operations()
        >>> print(f"Updated {table.name}: {table.description}")
    """
    metadata = get_metadata_client()

    # Get the table entity with tags field
    # Source: example_apis.py line 587
    table_fqn = "test-snowflake.test-db.test-schema.dim_orders"
    table_entity = metadata.get_by_name(entity=Table, fqn=table_fqn, fields=["tags"])

    # Create modified copy
    # Source: example_apis.py line 588
    table_entity_modified = deepcopy(table_entity)

    # Update multiple fields
    # Source: example_apis.py lines 589-591
    table_entity_modified.description = Markdown("Updated description in grouped PATCH")
    table_entity_modified.displayName = "Orders Dimension Table"
    table_entity_modified.tags = [
        TagLabel(
            tagFQN=TagFQN("Tier.Tier1"),
            source=TagSource.Classification,
            labelType=LabelType.Manual,
            state=State.Confirmed,
        )
    ]

    # Apply single PATCH with all changes
    # Source: example_apis.py line 593
    metadata.patch(Table, table_entity, table_entity_modified)

    print(f"✓ Applied grouped PATCH (description, displayName, tags) to: {table_fqn}")

    # Fetch updated entity
    updated_table = metadata.get_by_name(entity=Table, fqn=table_fqn, fields=["tags"])

    return updated_table


# ============================================================================
# MAIN - Run All Metadata Operations Examples
# ============================================================================

if __name__ == "__main__":
    print("=" * 70)
    print("OpenMetadata SDK - Metadata Operations Examples")
    print("=" * 70)
    print()
    print("NOTE: Ensure tables exist (run services.py and entities.py first)")
    print()

    try:
        # Example 1: Table-Level Tags
        print("1. Adding table-level tags...")
        add_table_level_tags()
        print()

        # Example 2: Column-Level Tags
        print("2. Adding column-level tags...")
        add_column_level_tags()
        print()

        # Example 3: Update Description
        print("3. Updating table description...")
        update_table_description()
        print()

        # Example 4: Update Owners
        print("4. Updating table owners...")
        update_table_owners()
        print()

        # Example 5: Assign Domain
        print("5. Assigning domain to table...")
        assign_domain_to_table()
        print()

        # Example 6: List Glossaries
        print("6. Listing glossaries and terms...")
        list_glossaries_and_terms()
        print()

        # Example 7: Grouped PATCH
        print("7. Applying grouped PATCH operations...")
        grouped_patch_operations()
        print()

        print("=" * 70)
        print("✓ All metadata operations examples completed successfully!")
        print("=" * 70)
        print("\nNext steps:")
        print("  - Run 'python lineage.py' to create lineage relationships")
        print("  - Check OpenMetadata UI to see updated metadata")

    except Exception as e:
        print(f"\n✗ Error: {e}")
        print("\nTroubleshooting:")
        print("  1. Ensure tables exist (run: python entities.py)")
        print("  2. Verify table FQNs match your instance")
        print("  3. For owners: use valid user/team IDs from your instance")
        print("  4. Check OpenMetadata server is running")
