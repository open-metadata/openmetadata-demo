"""
SDK 2.0 - Configuration
========================

Three ways to configure the OpenMetadata Python SDK:
1. Explicit parameters
2. Builder pattern
3. Environment variables

Source: ingestion/src/metadata/sdk/config.py
         ingestion/src/metadata/sdk/__init__.py
"""

from metadata.sdk import configure, client, reset

# ------------------------------------------------------------------ #
# Option 1: Explicit keyword arguments (simplest)
# ------------------------------------------------------------------ #
om = configure(
    host="http://localhost:8585/api",
    jwt_token="<your-jwt-token>",
)

# The returned object *is* the active client, but you can also grab
# it later from anywhere in your code:
same_client = client()

# ------------------------------------------------------------------ #
# Option 2: Build an OpenMetadataConfig object first
# ------------------------------------------------------------------ #
from metadata.sdk.config import OpenMetadataConfig

config = (
    OpenMetadataConfig.builder()
    .server_url("http://localhost:8585/api")
    .jwt_token("<your-jwt-token>")
    .verify_ssl(False)          # default
    .client_timeout(30)         # seconds, default 30
    # .ca_bundle("/path/to/ca.pem")  # optional CA bundle
    .build()
)

om = configure(config)

# ------------------------------------------------------------------ #
# Option 3: Environment variables (zero-config in CI/CD)
# ------------------------------------------------------------------ #
# Set the following env vars before running:
#   OPENMETADATA_HOST=http://localhost:8585/api
#   OPENMETADATA_JWT_TOKEN=<token>
#   OPENMETADATA_VERIFY_SSL=false          (optional)
#   OPENMETADATA_CA_BUNDLE=/path/to/ca     (optional)
#   OPENMETADATA_CLIENT_TIMEOUT=30         (optional)

om = configure()  # reads from env

# ------------------------------------------------------------------ #
# Resetting / swapping connections
# ------------------------------------------------------------------ #
# Tear down the current client (useful in tests or multi-server scripts)
reset()

# Then re-configure with a different server
om = configure(host="http://other-server:8585/api", jwt_token="...")
