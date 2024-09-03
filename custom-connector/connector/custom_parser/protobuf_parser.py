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
Utils module to parse the protobuf schema
"""

import glob
import importlib
import shutil
import sys
import traceback
from enum import Enum
from pathlib import Path
from typing import List, Optional, Type, Union

import grpc_tools.protoc
from metadata.generated.schema.entity.data.table import Column, DataType
from metadata.generated.schema.type.schema import DataTypeTopic, FieldModel
from metadata.utils.helpers import snake_to_camel
from metadata.utils.logger import ingestion_logger
from pydantic import BaseModel

logger = ingestion_logger()


class ProtobufDataTypes(Enum):
    """
    Enum for Protobuf Datatypes
    """

    UNKNOWN = 0
    DOUBLE = 1
    FLOAT = 2
    INT = 3, 4, 5, 13, 17, 18
    FIXED = 6, 7, 15, 16
    BOOLEAN = 8
    STRING = 9
    UNION = 10
    RECORD = 11
    BYTES = 12
    ENUM = 14

    def __new__(cls, *values):
        obj = object.__new__(cls)
        # first value is canonical value
        obj._value_ = values[0]
        for other_value in values[1:]:
            cls._value2member_map_[other_value] = obj
        obj._all_values = values
        return obj

    def __repr__(self):
        value = ", ".join([repr(v) for v in self._all_values])
        return (
            f"<"  # pylint: disable=no-member
            f"{self.__class__.__name__,}"
            f"{self._name_}"
            f"{value}"
            f">"
        )


class ProtobufParserConfig(BaseModel):
    """
    Protobuf Parser Config class
    :param schema_name: Name of protobuf schema
    :param schema_text: Protobuf schema definition in text format
    :param base_file_path: A temporary directory will be created under this path for
      generating the files required for protobuf parsing and compiling. By default
      the directory will be created under "/tmp/protobuf_openmetadata" unless it is
      specified in the parameter.
    """

    schema_name: str
    schema_text: str
    base_file_path: Optional[str] = "/tmp/protobuf_openmetadata"


class ProtobufParser:
    """
    Protobuf Parser class
    """

    config: ProtobufParserConfig

    def __init__(self, config):
        self.config = config
        self.proto_interface_dir = f"{self.config.base_file_path}/interfaces"
        self.generated_src_dir = f"{self.config.base_file_path}/generated/"

    def load_module(self, module):
        """
        Get the python module from path
        """
        module_path = module
        return __import__(module_path, fromlist=[module])

    def get_protobuf_python_object(self, file_path: str):
        """
        Method to create protobuf python module and get object
        """
        try:
            # compile the .proto file and create python class
            grpc_tools.protoc.main(
                [
                    "protoc",
                    file_path,
                    f"--proto_path={self.proto_interface_dir}",
                    f"--python_out={self.generated_src_dir}",
                ]
            )

            # import the python file
            sys.path.append(self.generated_src_dir)
            generated_src_dir_path = Path(self.generated_src_dir)
            py_file = glob.glob(
                str(
                    generated_src_dir_path.joinpath(f"{self.config.schema_name}_pb2.py")
                )
            )[0]
            module_name = Path(py_file).stem
            message = importlib.import_module(module_name)

            # get the class and create a object instance
            class_ = getattr(message, snake_to_camel(self.config.schema_name))
            instance = class_()
            return instance
        except Exception as exc:  # pylint: disable=broad-except
            logger.debug(traceback.format_exc())
            logger.warning(
                f"Unable to create protobuf python module for {self.config.schema_name}: {exc}"
            )
        return None

    @staticmethod
    def parse_protobuf_schema(
        instance, schema_name, cls: Type[BaseModel] = FieldModel
    ) -> Optional[List[Union[FieldModel, Column]]]:
        """
        Method to parse the protobuf schema
        """

        try:
            field_models = [
                cls(
                    name=instance.DESCRIPTOR.name,
                    dataType="RECORD",
                    children=ProtobufParser.get_protobuf_fields(
                        instance.DESCRIPTOR.fields, cls=cls
                    ),
                )
            ]

            return field_models
        except Exception as exc:  # pylint: disable=broad-except
            logger.debug(traceback.format_exc())
            logger.warning(f"Unable to parse protobuf schema for {schema_name}: {exc}")
        return None

    @staticmethod
    def _get_field_type(type_: int, cls: Type[BaseModel] = FieldModel) -> str:
        if type_ > 18:
            return DataType.UNKNOWN.value
        data_type = ProtobufDataTypes(type_).name
        if cls == Column and data_type == DataTypeTopic.FIXED.value:
            return DataType.INT.value
        return data_type

    @staticmethod
    def get_protobuf_fields(
        fields, cls: Type[BaseModel] = FieldModel
    ) -> Optional[List[Union[FieldModel, Column]]]:
        """
        Recursively convert the parsed schema into required models
        """
        field_models = []

        for field in fields:
            try:
                field_models.append(
                    cls(
                        name=field.name,
                        dataType=ProtobufParser._get_field_type(field.type, cls=cls),
                        children=ProtobufParser.get_protobuf_fields(
                            field.message_type.fields, cls=cls
                        )
                        if field.type == 11
                        else None,
                    )
                )
            except Exception as exc:  # pylint: disable=broad-except
                logger.debug(traceback.format_exc())
                logger.warning(
                    f"Unable to parse the protobuf schema into models: {exc}"
                )

        return field_models
