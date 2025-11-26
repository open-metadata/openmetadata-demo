"""
Connection Examples - OpenMetadata SDK

This file demonstrates different connection methods for OpenMetadata SDK.

NOTE: This file is for REFERENCE ONLY. Other example files (services.py,
entities.py, etc.) are self-contained and do NOT import from this file.
Each example file duplicates the connection setup for easy copy-paste usage.

SDK References:
- API Module: metadata.ingestion.ometa.ometa_api.OpenMetadata
- Connection: metadata.generated.schema.entity.services.connections.metadata.openMetadataConnection
- Auth: metadata.generated.schema.security.client.openMetadataJWTClientConfig
- Documentation: https://docs.open-metadata.org/sdk/python/api-reference/connection

Source Reference:
- Original example_apis.py lines 1-97

This file shows:
1. Basic JWT authentication (most common)
2. Custom authentication providers (OAuth, LDAP, etc.)
3. Health check patterns
4. Connection troubleshooting
"""

from metadata.ingestion.ometa.ometa_api import OpenMetadata
from metadata.generated.schema.entity.services.connections.metadata.openMetadataConnection import (
    OpenMetadataConnection,
    AuthProvider,
)
from metadata.generated.schema.security.client.openMetadataJWTClientConfig import (
    OpenMetadataJWTClientConfig,
)


# ============================================================================
# CONFIGURATION
# ============================================================================

# OpenMetadata server URL
# Default: http://localhost:8585/api
# Modify this to match your OpenMetadata instance
SERVER_URL = "http://localhost:8585/api"

# JWT Token for authentication
# How to get: OpenMetadata UI > Settings > Bots > ingestion-bot > Copy Token
# Or create a new bot and copy its token
# IMPORTANT: Replace this with your actual JWT token
JWT_TOKEN = (
    "eyJraWQiOiJHYjM4OWEtOWY3Ni1nZGpzLWE5MmotMDI0MmJrOTQzNTYiLCJhbGciOiJSUzI1NiIsInR5cCI6IkpXVCJ9."
    "eyJpc3MiOiJvcGVuLW1ldGFkYXRhLm9yZyIsInN1YiI6ImluZ2VzdGlvbi1ib3QiLCJlbWFpbCI6ImluZ2VzdGlvbi1ib3"
    "RAb3Blbm1ldGFkYXRhLm9yZyIsImlzQm90Ijp0cnVlLCJ0b2tlblR5cGUiOiJCT1QiLCJpYXQiOjE2OTU0MDkwNDEsImV4"
    "cCI6bnVsbH0.G2cmKdidr_lQd8nNy7i_7X3mSqXJsX4cFk0PqRoN0vJwsIiDhtTc7fd5Fi6NzT5ZxTR9BS2jRuaTMJ0dbBX"
    "wNaUZM_VDupGA_foSqfktjr6Ho-YRnmP_z6095lPJG9wE6hcWu6oXPWTR-zys0j0SkrUBFjSmYk-f31KW9jINFtR55MMwq"
    "e7weCsZkoJJ5O9w7vku4l6MeOfXVEfkVWCZaBKi93EYBlk9GBcV5HkVhjq2sujYtYUw9muwzl_4jiEZwFkeV7TkV8OBFow"
    "aT0L0SRyvuVq3hs27gdLLZBPrN3kiLN8JaGnVE2_CFOSdcrFiQVncyFHihY9C_3f113H-Ag"
)


# ============================================================================
# EXAMPLE 1: Create OpenMetadata Client
# ----------------------------------------------------------------------------
# Purpose: Create authenticated connection to OpenMetadata server
# SDK API: metadata.ingestion.ometa.ometa_api.OpenMetadata
# Required Args:
#   - config: OpenMetadataConnection with hostPort, authProvider, securityConfig
# Reference: https://docs.open-metadata.org/sdk/python/api-reference/connection
# Source: example_apis.py lines 88-96
# ============================================================================


def get_metadata_client(server_url: str = None, jwt_token: str = None) -> OpenMetadata:
    """
    Create and return an authenticated OpenMetadata client.

    Args:
        server_url (str, optional): OpenMetadata server URL.
                                     Defaults to SERVER_URL constant.
        jwt_token (str, optional): JWT authentication token.
                                    Defaults to JWT_TOKEN constant.

    Returns:
        OpenMetadata: Authenticated client instance

    Raises:
        Exception: If connection fails or authentication is invalid

    Example:
        >>> metadata = get_metadata_client()
        >>> # Use metadata client for API operations
        >>> tables = metadata.list_all_entities(entity=Table)
    """
    # Use provided values or fall back to constants
    url = server_url or SERVER_URL
    token = jwt_token or JWT_TOKEN

    # Configure JWT authentication
    # Source: example_apis.py lines 88-90
    security_config = OpenMetadataJWTClientConfig(jwtToken=token)

    # Create server connection configuration
    # Source: example_apis.py lines 91-95
    server_config = OpenMetadataConnection(
        hostPort=url,
        authProvider=AuthProvider.openmetadata,  # Auth provider type
        securityConfig=security_config,
    )

    # Initialize and return OpenMetadata client
    # Source: example_apis.py line 96
    metadata = OpenMetadata(server_config)

    return metadata


# ============================================================================
# EXAMPLE 2: Health Check
# ----------------------------------------------------------------------------
# Purpose: Verify connectivity to OpenMetadata server
# SDK API: metadata.health_check()
# Required Args: None
# Returns: None (raises exception if server unreachable)
# Reference: https://docs.open-metadata.org/sdk/python/api-reference/ometa
# Source: example_apis.py line 97
# ============================================================================


def health_check(metadata: OpenMetadata = None) -> bool:
    """
    Perform health check to verify OpenMetadata server is reachable.

    Args:
        metadata (OpenMetadata, optional): Client instance.
                                            If None, creates new client.

    Returns:
        bool: True if server is healthy, False otherwise

    Example:
        >>> if health_check():
        ...     print("Server is healthy!")
    """
    client = metadata or get_metadata_client()

    try:
        # Perform health check
        # Source: example_apis.py line 97
        client.health_check()
        print(f"✓ Successfully connected to OpenMetadata server at {SERVER_URL}")
        return True
    except Exception as e:
        print(f"✗ Failed to connect to OpenMetadata server: {e}")
        return False


# ============================================================================
# EXAMPLE 3: Get Connection with Custom Config
# ----------------------------------------------------------------------------
# Purpose: Create connection with custom authentication methods
# SDK API: OpenMetadataConnection with different AuthProvider types
# Required Args:
#   - hostPort: Server URL
#   - authProvider: AuthProvider enum (openmetadata, google, okta, etc.)
#   - securityConfig: Appropriate config for auth provider
# Reference: https://docs.open-metadata.org/sdk/python/api-reference/connection
# ============================================================================


def get_metadata_client_with_custom_auth(
    server_url: str, auth_provider: AuthProvider, security_config
) -> OpenMetadata:
    """
    Create OpenMetadata client with custom authentication.

    Args:
        server_url (str): OpenMetadata server URL
        auth_provider (AuthProvider): Authentication provider type
        security_config: Provider-specific security configuration

    Returns:
        OpenMetadata: Authenticated client instance

    Example (Google OAuth):
        >>> from metadata.generated.schema.security.client.googleSSOClientConfig import (
        ...     GoogleSSOClientConfig
        ... )
        >>> google_config = GoogleSSOClientConfig(
        ...     secretKey="path/to/secret.json"
        ... )
        >>> metadata = get_metadata_client_with_custom_auth(
        ...     server_url="http://localhost:8585/api",
        ...     auth_provider=AuthProvider.google,
        ...     security_config=google_config
        ... )
    """
    server_config = OpenMetadataConnection(
        hostPort=server_url,
        authProvider=auth_provider,
        securityConfig=security_config,
    )

    return OpenMetadata(server_config)


# ============================================================================
# MAIN - Test Connection
# ============================================================================

if __name__ == "__main__":
    print("=" * 70)
    print("OpenMetadata SDK - Connection Setup Test")
    print("=" * 70)
    print()

    # Test basic connection
    print("1. Testing connection to OpenMetadata server...")
    metadata = get_metadata_client()

    # Perform health check
    print("\n2. Performing health check...")
    is_healthy = health_check(metadata)

    if is_healthy:
        print("\n✓ Connection setup successful!")
        print(f"  Server: {SERVER_URL}")
        print(f"  Auth: JWT Token")
        print("\nYou can now run other example files:")
        print("  - python services.py")
        print("  - python entities.py")
        print("  - python metadata_ops.py")
        print("  - python lineage.py")
        print("  - python queries.py")
        print("  - python advanced.py")
    else:
        print("\n✗ Connection failed!")
        print("\nTroubleshooting:")
        print("  1. Verify OpenMetadata server is running")
        print(f"  2. Check server URL: {SERVER_URL}")
        print("  3. Verify JWT token is valid (check Settings > Bots)")
        print("  4. Ensure network connectivity to server")

    print()
