import logging
from enum import Enum
from typing import Any, Dict, List, Optional

from metadata.generated.schema.entity.data.table import ConstraintType, TableConstraint
from metadata.generated.schema.type.entityReference import EntityReference
from metadata.generated.schema.type.tagLabel import TagLabel


def get_owner(asset: dict) -> Optional[EntityReference]:
    try:
        owner: Dict[str, str] = asset.get("owner")
        if owner:
            return EntityReference(id=owner.get("id"), type=owner.get("type"))
    except Exception as err:
        logging.warning(f"Error trying to get the owner [{err}]")


def get_tag_label(asset: dict) -> Optional[List[TagLabel]]:
    try:
        tags: Dict[str, Any] = asset.get("tags")
        return [TagLabel.parse_obj(tag) for tag in tags]
    except Exception as err:
        logging.warning(f"Error trying to get the tags [{err}]")


def get_enum_from_value(enum: Enum, value: Any) -> Optional[Enum]:
    return next(elem for elem in enum if elem.value == value)


def get_table_constraint(constraint: List[dict]) -> Optional[List[TableConstraint]]:
    try:
        return [
            TableConstraint(
                constraintType=get_enum_from_value(
                    ConstraintType, elem.get("constraintType")
                ),
                columns=elem.get("columns"),
            )
            for elem in constraint
        ]

    except Exception as err:
        logging.warning(f"Error processing constraints [{constraint}] - [{err}]")
