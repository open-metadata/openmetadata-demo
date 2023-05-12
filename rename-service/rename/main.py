import argparse
import logging
import pathlib

from metadata.config.common import load_config_file
from metadata.generated.schema.entity.services.connections.metadata.openMetadataConnection import (
    OpenMetadataConnection,
)
from metadata.ingestion.ometa.ometa_api import OpenMetadata

from rename.database_service import DatabaseServiceSource

root = logging.getLogger()
root.setLevel(logging.INFO)


def run(input_: str, output: str, config: str) -> None:
    """
    Execute the renaming
    """
    config_file = pathlib.Path(config)
    config_dict = load_config_file(config_file)
    server_config = OpenMetadataConnection.parse_obj(config_dict)
    metadata = OpenMetadata(server_config)

    db_service = DatabaseServiceSource(
        input_service_name=input_, output_service_name=output, metadata=metadata
    )
    db_service.run()


def cli():
    """
    Prep the CLI
    """
    parser = argparse.ArgumentParser()
    parser.add_argument("-i", "--input", help="Service to rename", type=str)
    parser.add_argument("-o", "--output", help="Output service name", type=str)
    parser.add_argument(
        "-c", "--config", help="OpenMetadata server config file path", type=str
    )

    args = parser.parse_args()

    run(
        input_=args.input,
        output=args.output,
        config=args.config,
    )


if __name__ == "__main__":
    run("mysql", "new_mysql", "../config.yaml")
