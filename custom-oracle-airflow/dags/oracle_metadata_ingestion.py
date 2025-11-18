"""
OpenMetadata Oracle Database Ingestion DAG
This DAG demonstrates how to ingest metadata from Oracle database using OpenMetadata
"""

from datetime import datetime, timedelta
from airflow import DAG
from airflow.operators.python import PythonVirtualenvOperator

default_args = {
    "owner": "openmetadata",
    "email": ["admin@example.com"],
    "email_on_failure": False,
    "retries": 0,
    "retry_delay": timedelta(minutes=5),
    "execution_timeout": timedelta(minutes=60),
}

def oracle_metadata_ingestion_workflow():
    """
    OpenMetadata workflow function for Oracle database ingestion.
    All imports must be inside the function when using PythonVirtualenvOperator.
    """
    from metadata.workflow.metadata import MetadataWorkflow
    import yaml

    # OpenMetadata ingestion configuration for Oracle database
    config = """
---
source:
  type: oracle
  serviceName: oracle-demo-service
  serviceConnection:
    config:
      type: Oracle
      username: openmetadata_demo
      password: demo123
      hostPort: oracle-db:1521
      oracleConnectionType:
        oracleServiceName: XE
      # Alternative connection using SID:
      # oracleConnectionType:
      #   sid: XE
  sourceConfig:
    config:
      type: DatabaseMetadata
      # Optional: Include only specific schemas
      schemaFilterPattern:
        includes:
          - "OPENMETADATA_DEMO"
      # Optional: Include only specific tables
      # tableFilterPattern:
      #   includes:
      #     - "CUSTOMERS"
      #     - "ORDERS"
      #     - "PRODUCTS"
      # Include views
      includeViews: true
      # Include stored procedures
      includeTags: true
      # Optional: Mark deleted entities
      markDeletedTables: true
      # Optional: Include table profiling
      # includeDatabaseServiceTags: false
sink:
  type: metadata-rest
  config: {}
workflowConfig:
  # loggerLevel: INFO  # DEBUG, INFO, WARN or ERROR
  openMetadataServerConfig:
    hostPort: "http://host.docker.internal:8585/api"
    authProvider: "openmetadata"
    securityConfig:
      jwtToken: "eyJraWQiOiJHYjM4OWEtOWY3Ni1nZGpzLWE5MmotMDI0MmJrOTQzNTYiLCJhbGciOiJSUzI1NiIsInR5cCI6IkpXVCJ9.eyJpc3MiOiJvcGVuLW1ldGFkYXRhLm9yZyIsInN1YiI6ImluZ2VzdGlvbi1ib3QiLCJyb2xlcyI6WyJJbmdlc3Rpb25Cb3RSb2xlIl0sImVtYWlsIjoiaW5nZXN0aW9uLWJvdEBvcGVuLW1ldGFkYXRhLm9yZyIsImlzQm90Ijp0cnVlLCJ0b2tlblR5cGUiOiJCT1QiLCJpYXQiOjE3NjI0OTY1NTksImV4cCI6bnVsbH0.j-XmgeJns0XHRFVW-o5voe6qafmihrmBV30tgV-yaQL48JTOYs-qQM0ciPyTmc7PC93a3R33CGncQGjzHn3PTXk9qgZF37mF4ng4tr9Xp-9J7loNtnu209g_KNyo99twoIyIaKxQnPZc_j7njcyxMpn3CkG6ecsYLzDD6LkXqV6b9iMcuZ8t4QziH90mycsz-w4u15XDsfr3fuqgyWzF5tXKw1QZfkqEMv6opNdSJgkjTxfDYLh6TsfW5vwCIsDxIui2kwgWpYav-4TmsmUUvRyVlZ67dw6l8wFrrKvTbMnuNtIka9lMXYZAIsXDTjZGhifrEzyZVwoGScFTGPP7sA"
"""

    print("Starting Oracle metadata ingestion workflow...")
    
    try:
        # Parse the YAML configuration
        workflow_config = yaml.safe_load(config)
        
        # Create and execute the workflow
        workflow = MetadataWorkflow.create(workflow_config)
        
        print("Executing workflow...")
        workflow.execute()
        
        # Check for any failures and raise if needed
        workflow.raise_from_status()

        print("Workflow completed successfully!")
        
    except Exception as e:
        print(f"Workflow failed with error: {str(e)}")
        raise
    finally:
        # Always stop the workflow
        try:
            workflow.stop()
        except:
            pass

# Define the DAG
with DAG(
    "oracle_metadata_ingestion",
    default_args=default_args,
    description="OpenMetadata ingestion DAG for Oracle database",
    start_date=datetime(2024, 1, 1),
    schedule=None,  # Manual trigger only
    is_paused_upon_creation=True,  # Start paused
    catchup=False,  # Don't run historical instances
    tags=["openmetadata", "oracle", "metadata-ingestion"],
) as dag:

    # Oracle metadata ingestion task using PythonVirtualenvOperator
    oracle_ingest_task = PythonVirtualenvOperator(
        task_id="ingest_oracle_metadata",
        requirements=[
            "openmetadata-ingestion[oracle]==1.10.5",
        ],
        system_site_packages=True,
        python_version="3.11",  # Use Python 3.11
        python_callable=oracle_metadata_ingestion_workflow,
        dag=dag,
    )