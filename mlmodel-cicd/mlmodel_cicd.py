#  Copyright 2022 Collate
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
Sample CICD workflow to add ML Model metadata to OpenMetadata
"""
import time
from pathlib import Path
from typing import Optional

import yaml
from metadata.generated.schema.entity.services.mlmodelService import (
    MlModelService,
    MlModelConnection,
    MlModelServiceType
)
from metadata.generated.schema.entity.services.connections.mlmodel.customMlModelConnection import (
    CustomMlModelConnection, CustomMlModelType
)
from metadata.generated.schema.api.data.createMlModel import CreateMlModelRequest
from metadata.generated.schema.api.services.createMlModelService import CreateMlModelServiceRequest
from metadata.generated.schema.type.entityReference import EntityReference
from metadata.generated.schema.entity.data.table import Table
from metadata.generated.schema.entity.data.mlmodel import MlFeature, MlHyperParameter, FeatureSource, MlStore, MlModel
from metadata.generated.schema.entity.services.connections.metadata.openMetadataConnection import (
    OpenMetadataConnection, AuthProvider,
)
from metadata.generated.schema.security.client.openMetadataJWTClientConfig import (
    OpenMetadataJWTClientConfig,
)
from metadata.generated.schema.type.tagLabel import TagLabel
from metadata.ingestion.ometa.ometa_api import OpenMetadata

OM_HOST_PORT = "http://localhost:8585/api"
OM_JWT_TOKEN = "eyJraWQiOiJHYjM4OWEtOWY3Ni1nZGpzLWE5MmotMDI0MmJrOTQzNTYiLCJhbGciOiJSUzI1NiIsInR5cCI6IkpXVCJ9.eyJpc3MiOiJvcGVuLW1ldGFkYXRhLm9yZyIsInN1YiI6ImluZ2VzdGlvbi1ib3QiLCJlbWFpbCI6ImluZ2VzdGlvbi1ib3RAb3Blbm1ldGFkYXRhLm9yZyIsImlzQm90Ijp0cnVlLCJ0b2tlblR5cGUiOiJCT1QiLCJpYXQiOjE2ODM4MDIyNjUsImV4cCI6bnVsbH0.abHiU2KnFnrtF7QrnygHohPjeu6FGmtyBCLnTlFnf_p-7-Xq8NNz6aDWoFRJf13oAE6z8Tg_CwWmOEbTGqfG4GvWyNYCrxrGlS6RO9Td5QmVxDX6YZUdP4rn2RdvYzOdjQfAzeBTTsPe3VKEFGJB9HpEBy_Uux6QN1K7CQKewm-DrDejqwrkfG5lozPUuFxSx17BE60wJ7Z3TzhK8qAI94touRRodsGHwhFi48vL0fLcTu_tEG_cmJyy12Bzmv25pqHsFombb37lhiHwi-4mJMt_tV7dVCf-_YU13GDFC8pRTxHsi_Srf6hC1Pt4ZY7wA0p88kCRiPbjxLxqR-vgMA"
ML_MODEL_FILE = "ml_model_tags.yaml"


def read_ml_metadata(path: Path) -> dict:
    """
    Open the YAML file and read the metadata

    Args:
         path: YAML file path
    Return:
        YAML as a dictionary
    """
    if not path.is_file():
        raise ValueError(f"Cannot open config file {path}")

    with path.open() as file:
        raw_meta = yaml.safe_load(file)

    print("Loaded metadata YAML ✅")
    return raw_meta


def get_data_source_from_fqn(metadata: OpenMetadata, fqn: Optional[str]) -> Optional[EntityReference]:
    """
    Given the FQN defined in the ML Model meta YAML,
    get the EntityReference from OpenMetadata

    Args:
        metadata: OpenMetadata client
        fqn: Table asset we expect to find in OpenMetadata
    Returns:
        EntityReference
    """
    if fqn:
        table: Table = metadata.get_by_name(entity=Table, fqn=fqn)
        if table:
            return EntityReference(
                id=table.id.root,
                type="table",
                name=table.name.root,
                fullyQualifiedName=table.fullyQualifiedName.root,
            )

    return None


def get_or_create_ml_model_service(metadata: OpenMetadata, service_name: str) -> str:
    """
    Check if the service exists, otherwise create it
    """
    service_entity: MlModelService = metadata.get_by_name(entity=MlModelService, fqn=service_name)
    if not service_entity:
        metadata.create_or_update(
            CreateMlModelServiceRequest(
                name=service_name,
                serviceType=MlModelServiceType.CustomMlModel,
                connection=MlModelConnection(
                    config=CustomMlModelConnection(
                        type=CustomMlModelType.CustomMlModel,
                        sourcePythonClass="my.class",
                    )
                )
            )
        )

    return service_name


def update_openmetadata(raw_meta: dict) -> None:
    """
    Update the ML Model metadata in OM.

    1. Check if we can reach the OpenMetadata server
    2. Look for the sources references in OpenMetadata
    3. Prepare the CreateMlModelRequest
    """

    server_config = OpenMetadataConnection(
        hostPort=OM_HOST_PORT,
        authProvider=AuthProvider.openmetadata,
        securityConfig=OpenMetadataJWTClientConfig(jwtToken=OM_JWT_TOKEN),
    )
    metadata = OpenMetadata(server_config)

    if not metadata.health_check():
        raise RuntimeError("Error connecting to OpenMetadata")




    #create tags getting info form yaml file
    createTagClassificationRaw(metadata, raw_meta)



    print("Connected to OpenMetadata ✅")
    time.sleep(1)
    print (raw_meta)
    create_ml_model = CreateMlModelRequest(

        name=raw_meta["name"],
        description=raw_meta["description"],
        algorithm=raw_meta["algorithm"],
        target=raw_meta["target"],
        tags=[
            TagLabel(
                tagFQN=ml_tag["tagFQN"],
                description=ml_tag["description"],
                labelType=ml_tag["labelType"],
                state=ml_tag["state"],
                source=ml_tag["source"]
            )
            for ml_tag in raw_meta.get("tags") or []
        ],
        mlFeatures=[
            MlFeature(
                name=ml_feature["name"],
                dataType=ml_feature["dataType"],
                featureAlgorithm=ml_feature.get("featureAlgorithm"),
                tags=[
                    TagLabel(
                        tagFQN=ml_tagFeature["tagFQN"],
                        description=ml_tagFeature["description"],
                        labelType=ml_tagFeature["labelType"],
                        state=ml_tagFeature["state"],
                        source=ml_tagFeature["source"]
                    )
                    for ml_tagFeature in ml_feature.get("tags") or []
                ],
                featureSources=[
                    FeatureSource(
                        name=feature_source["name"],
                        dataType=feature_source["dataType"],
                        dataSource=get_data_source_from_fqn(metadata, feature_source.get("dataSourceFqn")) or None
                    )
                    for feature_source in ml_feature.get("featureSources") or []
                ]
            )
            for ml_feature in raw_meta.get("mlFeatures") or []
        ],
        mlHyperParameters=[
            MlHyperParameter(
                name=param["name"],
                value=str(param["value"]),
                description=param.get("description"),
            )
            for param in raw_meta.get("mlHyperParameters") or []
        ],
        mlStore=MlStore(
            storage=raw_meta["mlStore"]["storage"],
            imageRepository=raw_meta["mlStore"]["imageRepository"]
        ),
        service=get_or_create_ml_model_service(metadata, raw_meta["serviceName"])
    )

    mlmodel: MlModel = metadata.create_or_update(create_ml_model)
    metadata.add_mlmodel_lineage(mlmodel)

    print("Updated ML Model metadata ✅")


def mock_tests() -> None:
    """
    Made up function that runs fictional tests on our ML Model
    """
    print("Retraining model... 🕒")
    time.sleep(1)
    print("Validated ML Model performance ✅")
    time.sleep(1)
    print("Released new version ✅")
    time.sleep(1)


def run_workflow() -> None:
    """
    Main workflow entrypoint
    """

    # 1. Read meta
    path = Path(__file__).parent / ML_MODEL_FILE
    raw_meta = read_ml_metadata(path)

    # 2. Validate and publish Model
    mock_tests()

    # 3. Update metadata
    update_openmetadata(raw_meta)


def createTagClassificationRaw(metadata, raw_meta) -> None:
    for ml_tag in raw_meta.get("tags"):

        #print( ml_tag["tagFQN"])
        class_tag=ml_tag["tagFQN"].split(".")
        classificationName=class_tag[0]
        tagName=class_tag[1]
        createTagClassification(metadata,classificationName,tagName)







def createTagClassification(metadata, classification_name, tag_name) -> None:
    from metadata.generated.schema.api.classification.createClassification import (
        CreateClassificationRequest,
    )
    from metadata.generated.schema.api.classification.createTag import CreateTagRequest

    classification_request = CreateClassificationRequest(
        name=classification_name,
        description="Sample classification.",
    )

    metadata.create_or_update(classification_request)

    tag_request = CreateTagRequest(
        classification=classification_request.name,
        name=tag_name,
        description="Sample Tag.",
    )

    metadata.create_or_update(tag_request)



if __name__ == "__main__":

    run_workflow()

