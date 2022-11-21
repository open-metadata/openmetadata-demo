#  Copyright 2021 Collate
#  Licensed under the Apache License, Version 2.0 (the "License");
#  you may not use this file except in compliance with the License.
#  You may obtain a copy of the License at
#  http://www.apache.org/licenses/LICENSE-2.0
#  Unless required by applicable law or agreed to in writing, software
#  distributed under the License is distributed on an "AS IS" BASIS,
#  WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
#  See the License for the specific language governing permissions and
#  limitations under the License.

"""
Test Suite DAG integration demo
"""

import operator
import time
from datetime import datetime
from typing import Optional

import pandas as pd
import requests
from airflow import DAG
from airflow.decorators import task
from airflow.providers.amazon.aws.hooks.redshift_sql import RedshiftSQLHook
from metadata.generated.schema.entity.services.connections.metadata.openMetadataConnection import \
    OpenMetadataConnection
from metadata.generated.schema.entity.services.ingestionPipelines.ingestionPipeline import (
    IngestionPipeline, PipelineState, PipelineStatus)
from metadata.generated.schema.tests.basic import TestCaseStatus
from metadata.generated.schema.tests.testCase import TestCase
from metadata.ingestion.ometa.ometa_api import OpenMetadata
from metadata.utils.time_utils import (get_beginning_of_day_timestamp_mill,
                                       get_end_of_day_timestamp_mill)

ENDPOINT = "https://data.lacity.org/resource/83wz-48xq.json"
TIMEOUT = 30
OM_SERVER_CONFIG = {
    "hostPort": "http://localhost:8585/api",
    "authProvider": "openmetadata",
    "securityConfig": {
        "jwtToken": "<ingestionToken>"  # pylint: disable=line-too-long
    },
}
OPENMETADATA: OpenMetadata = OpenMetadata(
    OpenMetadataConnection.parse_obj(OM_SERVER_CONFIG)
)


def get_ingestion_pipeline(name: str):
    """get ingestion pipeline by name

    Args:
        name (str): start or full name of ingestion
    """
    pipelines = OPENMETADATA.list_entities(
        IngestionPipeline,
        fields="*",
    ).entities

    test_suite_pipeline: Optional[IngestionPipeline] = next(
        (
            pipeline
            for pipeline in pipelines
            if pipeline.fullyQualifiedName.__root__.startswith(name)
        ),
        None,
    )

    return test_suite_pipeline


with DAG(
    dag_id="los_angeles_sewer",
    schedule_interval=None,
    start_date=datetime(2021, 1, 1),
    catchup=False,
    tags=["example"],
) as dag:

    @task(task_id="extract_and_insert_data")
    def extract_and_insert(**kwargs):
        """Extract function"""
        resp = requests.get(ENDPOINT, timeout=30)
        df = pd.DataFrame(resp.json()).convert_dtypes()
        hook = RedshiftSQLHook()
        engine = hook.get_sqlalchemy_engine()
        engine.dialect.description_encoding = None
        df.iloc[:100, 1:].to_sql(
            "los_angeles_sewer_system",
            con=engine,
            if_exists="replace",
            index=False,
        )

    extract_and_insert_task = extract_and_insert()

    @task(task_id="run_om_test")
    def run_om_test(**kwargs):
        """Run Openmetadata tests"""

        test_suite_pipeline: Optional[IngestionPipeline] = get_ingestion_pipeline(
            "LASewerTests"
        )

        if not test_suite_pipeline:
            raise RuntimeError("No pipeline entity found for {test_suite_pipeline}")

        OPENMETADATA.run_pipeline(test_suite_pipeline.id.__root__)

        timeout = time.time() + TIMEOUT
        while True:
            statuses = OPENMETADATA.get_pipeline_status_between_ts(
                test_suite_pipeline.fullyQualifiedName.__root__,
                get_beginning_of_day_timestamp_mill(),
                get_end_of_day_timestamp_mill(),
            )

            if statuses:
                status = max(statuses, key=operator.attrgetter("timestamp.__root__"))
                if status.pipelineState in {
                    PipelineState.success,
                    PipelineState.partialSuccess,
                }:
                    break
                if status.pipelineState == PipelineState.failed:
                    raise RuntimeError("Execution failed")
            if time.time() > timeout:
                raise RuntimeError("Execution timed out")

    run_om_test_task = run_om_test()

    @task(task_id="check_om_test_results")
    def check_om_test_results(**kwargs):
        """Check test results"""
        test_cases = OPENMETADATA.list_entities(
            TestCase,
            fields="*",
        )

        test_cases = [
            entity
            for entity in test_cases.entities
            if entity.testSuite.name == "LASewerTests"
        ]

        test_suite_pipeline: Optional[IngestionPipeline] = get_ingestion_pipeline(
            "LASewerTests"
        )
        pipelines_statuses = OPENMETADATA.get_pipeline_status_between_ts(
            test_suite_pipeline.fullyQualifiedName.__root__,
            get_beginning_of_day_timestamp_mill(),
            get_end_of_day_timestamp_mill(),
        )

        if not pipelines_statuses:
            raise RuntimeError("Could not find pipeline")

        latest_pipeline_status: PipelineStatus = max(
            pipelines_statuses, key=operator.attrgetter("timestamp.__root__")
        )

        for test_case in test_cases:
            timeout = time.time() + TIMEOUT
            while True:
                test_case_results = OPENMETADATA.get_test_case_results(
                    test_case.fullyQualifiedName.__root__,
                    get_beginning_of_day_timestamp_mill(),
                    get_end_of_day_timestamp_mill(),
                )
                if time.time() > timeout:
                    raise RuntimeError("Execution timed out")
                if test_case_results:
                    latest_test_case_result = max(
                        test_case_results, key=operator.attrgetter("timestamp.__root__")
                    )
                    if (
                        latest_test_case_result.timestamp.__root__
                        < latest_pipeline_status.startDate.__root__ // 1000
                    ):
                        continue
                    if latest_test_case_result.testCaseStatus in {
                        TestCaseStatus.Failed,
                        TestCaseStatus.Aborted,
                    }:
                        raise RuntimeError(
                            f"Test case {test_case.name.__root__} returned status "
                            f"{latest_test_case_result.testCaseStatus.value} "
                        )
                    break

    check_om_test_results_task = check_om_test_results()

    @task(task_id="model")
    def model(**kwargs):
        """model function"""
        hook = RedshiftSQLHook()
        engine = hook.get_sqlalchemy_engine()
        engine.dialect.description_encoding = None
        df = pd.read_sql(
            "SELECT mapsheet, avg(shape_leng) mean_shape_leng "
            "FROM los_angeles_sewer_system GROUP BY 1;",
            con=engine,
        )

        df.to_sql("sewer_mean_len", con=engine, index=False, if_exists="replace")

    model_task = model()

    (
        extract_and_insert_task
        >> run_om_test_task
        >> check_om_test_results_task
        >> model_task
    )
