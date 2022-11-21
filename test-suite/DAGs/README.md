# Test Suite Integration with Airflow
In this demo folder you will find a sample DAG with an integration execution of OpenMetadata test suite workflow.

This DAG extracts data from Los Angeles Open Data API. ingest it into a redshift database, run and check OpenMetadata tests and then aggregate our source data.

It illustrate the possibility to integrate OpenMetadata tests within a data processing workflow.

**Note**  
You might need to change the `OM_SERVER_CONFIG` variable to match your openmetadata server configuration