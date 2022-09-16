# Redpanda Demo

## Prepare the data

In this directory you will find a Docker Compose file that will spin up Redpanda and ingest sample data.

```shell
docker compose up
```

## Ingest using OpenMetadata

After spinning up [OpenMetadata](https://docs.open-metadata.org/quick-start/local-deployment), you can try the
ingestion via the [UI](https://docs.open-metadata.org/openmetadata/connectors/messaging/redpanda).

Here you can also find `redpanda.yaml` to run the ingestion through the CLI:

```shell
pip install "openmetadata-ingestion[redpanda]"
metadata ingest -c redpanda.yaml
```
