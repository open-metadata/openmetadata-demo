# Creating a Custom Connector

In this demo we'll prepare the ingredients to set up a custom connector for OpenMetadata.

## Step 1 - Prepare your Connector

A connector is a class that extends from `metadata.ingestion.api.source.Source`. It should implement
all the required methods ([docs](https://docs.open-metadata.org/sdk/python/build-connector/source#for-consumers-of-openmetadata-ingestion-to-define-custom-connectors-in-their-own-package-with-same-namespace)).

In `connector/my_awesome_connector.py` you have a minimal example of it.

Note how te important method is the `next_record`. This is the generator function that will be iterated over
to send all the Create Entity Requests to the `Sink`. Read more about the `Workflow` [here](https://docs.open-metadata.org/sdk/python/build-connector).

## Step 2 - Yield the data

The `Sink` is expecting Create Entity Requests. To get familiar with the Python SDK and understand how to create
the different Entities, a recommended read is the Python SDK [docs](https://docs.open-metadata.org/sdk/python).

We do not have docs and examples of all the supported Services. A way to get examples on how to create and fetch
other types of Entities is to directly refer to the `ometa` [integration tests](https://github.com/open-metadata/OpenMetadata/tree/main/ingestion/tests/integration/ometa).

## Step 3 - Prepare the package installation

We'll need to package the code so that it can be shipped to the ingestion container and used there. In this demo
you can find a simple `setup.py` that builds the `connector` module.

## Step 4 - Prepare the Ingestion Image

If you want to use the connector from the UI, the `openmetadata-ingestion` image should be aware of your new package.

We will be running the demo against the OpenMetadata version `0.13.2`, therefore, our Dockerfile looks like:

```Dockerfile
# Base image from the right version
FROM openmetadata/ingestion:0.13.2

# Let's use the same workdir as the ingestion image
WORKDIR ingestion
USER airflow

# Install our custom connector
# For a PROD image, this could be picking up the package from your private package index
COPY connector connector
COPY setup.py .
RUN pip install --no-deps .
```

## Step 5 - Run OpenMetadata with the custom Ingestion image

We have a `Makefile` prepared for you to run `make run`. This will get OpenMetadata up in Docker Compose using the
custom Ingestion image.

## Step 6 - Configure the Connector

In the example we prepared a Database Connector. Thus, go to `Database Services > Add New Service > Custom`
and set the `Source Python Class Name` as `connector.my_awesome_connector.MyAwesomeConnector`.

Note how we are specifying the full module name so that the Ingestion Framework can import the Source class.

---

## CSV Custom Connector

To run the CSV Custom Connector, the Python class will be `connector.my_csv_connector.CsvConnector` and we'll need
to set the following Connection Options:
- `source_directory`: `/opt/airflow/ingestion/sample.csv`
- `business_unit`: Any name you'd like (preferably no special characters).
