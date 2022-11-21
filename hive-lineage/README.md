# Hive Lineage in OpenMetadata

For Hive, we do not have an automated workflow we can use to extract lineage. The difference between
Hive and other systems such as BigQuery or Snowflake is that we do not have access to a query history table
we can directly use to extract information (if you know how to get it, please reach out at https://slack.open-metadata.org/).

However, this does not mean that lineage cannot be extracted! What we can do in these cases is to run a Workflow
based on a CSV file containing the queries we want to parse. The only requirement is that the tables referenced
need to be previously ingested in OpenMetadata, which can be achieved using the [Hive connector](https://docs.open-metadata.org/connectors/database/hive).

## Requirements

**OBS**: Note that this demo is based on OpenMetadata version 0.13.0.

We recommend that you prepare a virtual environment in `openmetadata-demo/hive-lineage` to install the packages:
1. `python -m venv venv`
2. `source venv/bin/activate`
3. `pip install "openmetadata-ingestion[hive]==0.13.0"`

## Spinning up the services

Execute `make run` from `openmetadata-demo/hive-lineage` to spin up OpenMetadata and a Hive Server. In order to
bring in Hive data you can run `make load`.

The Hive default user is `hive` without any password.

## Ingestion Hive metadata

If we now connect to the OpenMetadata UI we can ingest the metadata from Hive. Use the service name `hive` if you
don't want to apply any changes as the demo advances. As the service is running from the same compose file, note that 
the Host and Port will be `hive:10000`.

The sample data script prepared some tables in the schema `lineage_db`, so that is the one we want to ingest.

Testing the connection should give us a green check.

After the ingestion is done, we should see the following tables:
- `actor`
- `actor_catalog`
- `film_actor`

## Preparing the query log CSV

Now we want to ingest lineage based on a [Query Log File](https://docs.open-metadata.org/connectors/ingestion/workflows/lineage/lineage-workflow-query-logs).

To keep things simple, we will create a CSV with a single column `query_text`.

It is important that tables exist within OpenMetadata for the lineage workflow to find them and create the edges
between the tables. You can find an example in the `query_log.csv` file.

## Running the Workflow

There is a YAML file already prepared to run the workflow. From `openmetadata-demo/hive-lineage`, you can run
`metadata ingest -c lineage.yaml`. Afterwards, you should be seeing the lineage in the UI.

```
Source Status:
{'failures': [], 'filtered': [], 'records': 0, 'source_start_time': 1669023072.9220438, 'success': [], 'warnings': []}
Sink Status:
{'failures': [], 'records': ['Lineage from: hive.default.lineage_db.actor'], 'warnings': []}

Workflow finished in time 5.49s 
Success % : 100.0
Workflow finished successfully
```
