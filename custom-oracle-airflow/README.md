# Airflow with Oracle Database and OpenMetadata Integration

This project provides a complete Docker setup for running Apache Airflow with Oracle Database integration and OpenMetadata ingestion capabilities.

## Components

- **Apache Airflow 3.1.2** with Python 3.11 and LocalExecutor
- **OpenMetadata Ingestion 1.10.5**
- **Oracle Database Express Edition 21.3.0**
- **PostgreSQL 13** (for Airflow metadata)

## Prerequisites

- Docker Engine 20.10+
- Docker Compose 2.0+
- At least 2GB of RAM (simplified setup)
- At least 1 CPU core
- At least 5GB of free disk space

## Quick Start

1. **Clone and navigate to the directory**:
   ```bash
   git clone <your-repo>
   cd custom-oracle-airflow
   ```

2. **Set environment variables**:
   ```bash
   # On Linux/macOS
   export AIRFLOW_UID=$(id -u)
   
   # On Windows (PowerShell)
   $env:AIRFLOW_UID=50000
   ```

3. **Start the services**:
   ```bash
   # Initialize Airflow database (first time only)
   docker-compose up airflow-init
   
   # Start all services
   docker-compose up -d
   ```

4. **Wait for services to be ready**:
   - Oracle Database: ~2-3 minutes
   - Airflow services: ~1-2 minutes

5. **Access the applications**:
   - **Airflow Web UI**: http://localhost:8081
     - Username: `airflow`
     - Password: `airflow`
   - **Oracle Database**: `localhost:1521`
     - SID: `XE`
     - Username: `system`
     - Password: `oracle123`

## Oracle Database Details

### Connection Information
- **Host**: `localhost` (from host) or `oracle-db` (from containers)
- **Port**: `1521`
- **SID**: `XE`
- **System User**: `system` / `oracle123`
- **Demo User**: `openmetadata_demo` / `demo123`

### Sample Data
The Oracle database comes pre-configured with:
- Sample schema: `openmetadata_demo`
- Tables: `customers`, `orders`, `products`
- View: `customer_orders`
- Sample data for testing

### Connect from Airflow
Use this connection string in your Airflow DAGs:
```python
oracle_conn_string = "oracle+cx_oracle://openmetadata_demo:demo123@oracle-db:1521/XE"
```

## OpenMetadata Integration

The Airflow image includes OpenMetadata Ingestion (`openmetadata-ingestion==1.10.5`) with Oracle support.

### Example Connection Configuration
```python
from metadata.generated.schema.entity.services.connections.database.oracleConnection import OracleConnection
from metadata.generated.schema.entity.services.databaseService import DatabaseService

oracle_config = OracleConnection(
    username="openmetadata_demo",
    password="demo123",
    hostPort="oracle-db:1521",
    oracleConnectionType=OracleConnectionType.Oracle,
    service="XE"
)
```

## Directory Structure

```
custom-oracle-airflow/
├── docker-compose.yml          # Main orchestration file
├── Dockerfile.airflow          # Custom Airflow image
├── Dockerfile.oracle           # Custom Oracle image
├── init-scripts/              # Oracle initialization scripts
│   └── 01-init.sql            # Sample data setup
├── dags/                      # Airflow DAGs directory
├── logs/                      # Airflow logs
├── plugins/                   # Airflow plugins
├── config/                    # Airflow configuration
└── README.md                  # This file
```

## Common Operations

### Start Services
```bash
docker-compose up -d
```

### Stop Services
```bash
docker-compose down
```

### View Logs
```bash
# All services
docker-compose logs

# Specific service
docker-compose logs airflow-webserver
docker-compose logs oracle-db
```

### Restart a Service
```bash
docker-compose restart airflow-scheduler
```

### Access Oracle Database
```bash
# Using SQL*Plus
docker-compose exec oracle-db sqlplus system/oracle123@XE

# Using the demo user
docker-compose exec oracle-db sqlplus openmetadata_demo/demo123@XE
```

### Execute Airflow Commands
```bash
# List DAGs
docker-compose exec airflow-webserver airflow dags list

# Test a DAG
docker-compose exec airflow-webserver airflow dags test <dag_id> <execution_date>
```

## Troubleshooting

### Oracle Database Issues

1. **Database taking too long to start**:
   - Oracle XE needs 2-3 minutes on first startup
   - Check logs: `docker-compose logs oracle-db`

2. **Connection refused**:
   - Ensure Oracle container is healthy: `docker-compose ps`
   - Check if port 1521 is available on host

3. **Sample data missing**:
   - Verify init scripts: `docker-compose logs oracle-db | grep -i init`
   - Manually run: `docker-compose exec oracle-db sqlplus system/oracle123@XE @/opt/oracle/scripts/startup/01-init.sql`

### Airflow Issues

1. **Web UI not accessible**:
   - Wait for initialization to complete
   - Check webserver logs: `docker-compose logs airflow-webserver`

2. **DAGs not appearing**:
   - Ensure DAG files are in `./dags/` directory
   - Check scheduler logs: `docker-compose logs airflow-scheduler`

3. **Permission issues**:
   - Set correct AIRFLOW_UID: `export AIRFLOW_UID=$(id -u)`
   - Restart services: `docker-compose down && docker-compose up -d`

### OpenMetadata Issues

1. **Import errors**:
   - Verify OpenMetadata installation: `docker-compose exec airflow-webserver pip show openmetadata-ingestion`
   - Check Oracle client: `docker-compose exec airflow-webserver python -c "import cx_Oracle; print('OK')"`

## Development

### Adding DAGs
Place your DAG files in the `./dags/` directory. They will be automatically detected by Airflow.

### Custom Plugins
Add custom plugins to the `./plugins/` directory.

### Modifying Oracle Setup
Edit `./init-scripts/01-init.sql` to customize the sample data or add new schemas.

## Production Considerations

1. **Security**:
   - Change default passwords
   - Use proper secrets management
   - Configure SSL/TLS

2. **Performance**:
   - Adjust Oracle memory settings
   - Tune Airflow worker count
   - Use external databases for production

3. **Persistence**:
   - Use external volumes for data persistence
   - Regular backups of Oracle data
   - Monitor disk usage

## Environment Variables

| Variable | Default | Description |
|----------|---------|-------------|
| `AIRFLOW_UID` | 50000 | User ID for Airflow processes |
| `ORACLE_PWD` | oracle123 | Oracle system password |
| `ORACLE_CHARACTERSET` | AL32UTF8 | Oracle character set |

## Support

For issues and questions:
1. Check the troubleshooting section above
2. Review Docker logs for specific services
3. Consult official documentation:
   - [Apache Airflow](https://airflow.apache.org/docs/)
   - [Oracle Database XE](https://docs.oracle.com/en/database/oracle/oracle-database/21/xeinl/)
   - [OpenMetadata](https://docs.openmetadata.org/)