import os
import yaml

from metadata.ingestion.api.workflow import Workflow

CONFIG = f"""
source:
  type: snowflake
  serviceName: snowflake_from_github_actions
  serviceConnection:
    config:
      type: Snowflake
      username: {os.getenv('SNOWFLAKE_USERNAME')}
      password: {os.getenv('SNOWFLAKE_PASSWORD')}
      warehouse: {os.getenv('SNOWFLAKE_WAREHOUSE')}
      account: {os.getenv('SNOWFLAKE_ACCOUNT')}
  sourceConfig:
    config:
      type: DatabaseMetadata
      includeViews: true
      databaseFilterPattern:
        includes:
        - SNOWFLAKE_SAMPLE_DATA
      schemaFilterPattern:
        excludes:
        - INFORMATION_SCHEMA
        includes:
        - TPCH_SF1000$
        - PUBLIC
sink:
  type: metadata-rest
  config: {{}}
workflowConfig:
  openMetadataServerConfig:
    hostPort: https://sandbox.open-metadata.org
    authProvider: openmetadata
    securityConfig:
      jwtToken: {os.getenv('SBX_JWT')}
"""


def run():
    workflow_config = yaml.safe_load(CONFIG)
    workflow = Workflow.create(workflow_config)
    workflow.execute()
    workflow.raise_from_status()
    workflow.print_status()
    workflow.stop()


if __name__ == "__main__":
    run()
