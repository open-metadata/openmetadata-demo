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
Load data into Hive using OpenMetadata connection definitions
"""
import logging
import sys
from metadata.generated.schema.entity.services.connections.database.hiveConnection import (
    HiveConnection,
)
from sqlalchemy.engine.base import Engine, Connection
from sqlalchemy.sql import text
from metadata.utils.connections import get_connection, test_connection

root = logging.getLogger()
root.setLevel(logging.INFO)
handler = logging.StreamHandler(sys.stdout)
formatter = logging.Formatter("%(asctime)s - %(name)s - %(levelname)s - %(message)s")
handler.setFormatter(formatter)
root.addHandler(handler)


STATEMENTS = [
    "DROP DATABASE IF EXISTS lineage_db CASCADE",
    "CREATE DATABASE lineage_db",
    "USE lineage_db",
    """
    CREATE TABLE actor (
      actor_id INT,
      first_name STRING,
      last_name STRING,
      last_update TIMESTAMP
    )
    """,
    """
    CREATE TABLE film_actor (
       actor_id INT,
       film_id INT,
       last_update TIMESTAMP
    )
    """,
    """
    CREATE TABLE actor_catalog AS SELECT first_name AS name, last_name AS surname from actor
    """
]


def run_query(conn: Connection, query: str):
    """Helper to run SQLAlchemy query as text"""
    statement = text(query)
    conn.execute(statement)


def load(connection: HiveConnection):
    """Prepare the Hive instance with sample data"""

    logging.info("Loading sample data...")

    engine: Engine = get_connection(connection)
    test_connection(engine)

    with engine.connect() as conn:
        for query in STATEMENTS:
            run_query(conn=conn, query=query)

    logging.info("Done!")


if __name__ == "__main__":
    hive_connection = HiveConnection(
        username="hive",
        hostPort="localhost:10000"
    )
    logging.info(f"Connecting to {hive_connection}")
    load(hive_connection)
