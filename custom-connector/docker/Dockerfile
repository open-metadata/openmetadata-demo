FROM openmetadata/ingestion:1.3.0

# Let's use the same workdir as the ingestion image
WORKDIR ingestion
USER airflow

# Install our custom connector
COPY connector connector
COPY setup.py .
COPY sample.csv .
RUN pip install --no-deps .
