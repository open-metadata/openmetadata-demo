# Postgres Demo

In this directory you will find all the necessary ingredients, instructions and scripts to start OpenMetadata
locally using Docker, ingest data from a local Postgres instance and do a round of exercises interacting with
the OpenMetadata API using the Python SDK.

The goal of the demo is to extract different metadata from a Postgres database:
- Tables and their schema
- What queries have been run
- Lineage from queries
- Profiling & Tests

**OBS**: Note that this demo is based on OpenMetadata version 1.0.3. If playing locally with the `openmetadata-ingestion`
package, make sure to install `openmetadata-ingestion~=1.0.3`

## Requirements

### Docker Compose

Docker compose v2 installed on your laptop. You can install it following the official [docs](https://docs.docker.com/compose/install/).

```bash
❯ docker compose version
Docker Compose version v2.2.3
```

### Python 3

OpenMetadata supports Python 3.7+. This demo has been built and tested using Python 3.9:

```bash
❯ python -V
Python 3.9.13
```

It is recommended to use python within a virtual environment for isolation:

```bash
python -m venv venv
source venv/bin/activate
```

You can now validate that you are using the right python executable with:

```bash
❯ which python
~/openmetadata-demo/postgres/venv/bin/python
```

## What you'll find here

- `docker/docker-compose.yml`: This is the default `docker-compose.yml` file from the 0.13.0 release of OpenMetadata. We added
  a sample Postgres db in there as well to ingest some sample data.
- `python/profiler_workflow.py`: A sample Python script to run the profiler ingestion.
- `python/lineage.ipynb`: With a step-by-step showcase of lineage APIs.

## How to run?

`make run` has you covered. It will spin up the following services:

1. OpenMetadata Server
2. OpenMetadata Ingestion
3. MySQL
4. Elasticsearch
5. Our custom Postgres

OBS: Note that this demo does not have any volumes mounted. You can restart the docker to start with a clean
OpenMetadata deployment, but you should only use this as a playground. You can find more information on
how to deploy OpenMetadata [here](https://docs.open-metadata.org/deployment).

**Question**: What is the OpenMetadata architecture? How do the different components interact?

## Metadata Ingestion

Let's create a service connection to the Postgres Database from the UI:
- username: `openmetadata_user`
- password: `password`
- host and port: `postgresql:5432`
- database: `postgres`

For the rest of the demo to work without any changes, let's name our service `demo_pg`.

**Question**: What happens when we deploy an Ingestion from the UI?

After running the metadata ingestion, we expect that:

1. Databases & Schemas are ingested
2. Tables show their schema and constraints
3. How can we add ownership?

## Updating metadata

Connect to the db via `psql -d postgres -U openmetadata_user -W` inside the `sample_postgres` container. Listing
the tables, we should see:

```
postgres=> \dt
                List of relations
 Schema |    Name    | Type  |       Owner
--------+------------+-------+-------------------
 public | actor      | table | openmetadata_user
 public | bad_actor  | table | openmetadata_user
 public | film_actor | table | openmetadata_user
(3 rows)
```

What we'll do:

1. `DROP TABLE public.bad_actor;`
2. `ALTER TABLE public.actor DROP COLUMN last_update;`
3. `ALTER TABLE public.film_actor ADD money BIGINT DEFAULT 9999999;`
4. `CREATE TABLE actor_catalog AS SELECT first_name AS name, last_name AS surname FROM actor;`

**Question**: What has happened in the assets version?

## Collaboration

**Collaboration**: What's the best place to ask for a table description?

## Lineage Ingestion

Now run the Lineage Workflow 

**Question**: What will we see when checking the lineage tab from `actor_catalog`? Can we check which SQL query 
powered this transformation?

## Usage Ingestion

Let's run a couple of queries against our newly created data:

```sql
select * from actor_catalog;
select max(name) as super_KPI from actor_catalog;
```

Then, prepare a Usage Ingestion workflow. Would that be useful to share our knowledge?

## Profiler Ingestion

We have seen a few examples on how to run workflows from the UI. Now, we will
leverage the `openmetadata-ingestion` package to run a profiler workflow
locally instead.

This can be useful if we want to use our own scheduling systems / scripts / automations
instead of relying on OpenMetadata workflows entirely.

For this step, let's refer to the script under `python/profiler_workflow.py`.

We will now copy this script into the `openmetadata_ingestion` container and run
the ingestion from there. This would help us reuse the service connection information
which is bounded within the Docker network.

```bash
docker cp python/profiler_workflow.py openmetadata_ingestion:/opt/airflow/profiler_workflow.py
```

Then, we'll run the script from within the container:

```bash
docker exec -it openmetadata_ingestion bash
```

and run the script:

```bash
python profiler_workflow.py
```

This is super interesting because we are using exactly the same classes and logic
that OpenMetadata uses when deploying via the UI!

## Test Suites

Now that we have some knowledge on how our data looks like, we might want to create some tests
for our assets. Let's jump back to the UI for this.

- What happens when a test fails?
- How can we collaborate directly on the UI?
- How can we get notified?

### Sending Notifications

1. Check the instructions from the Slack [docs](https://api.slack.com/messaging/webhooks)
2. Copy your webhook URL (App > Features > Incoming Webhooks)
3. Paste that in the OM UI

## Lineage API

Let's dive a bit deeper and interact directly with the OpenMetadata API to create more
and better lineage!

This section will be run on a jupyter notebook on our laptops. Let's prepare the environment
with (requires Python >= 3.7):

```bash
python -m venv venv
source venv/bin/activate
pip install jupyter notebook openmetadata-ingestion~=1.0.3
```
