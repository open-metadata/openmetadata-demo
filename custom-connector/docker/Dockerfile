FROM docker.getcollate.io/openmetadata/ingestion:2.0.0-rc1

WORKDIR /opt/airflow/openmetadata-demo-connectors
USER airflow

COPY --chown=airflow:0 pyproject.toml ./
COPY --chown=airflow:0 src ./src
RUN pip install --no-deps .
