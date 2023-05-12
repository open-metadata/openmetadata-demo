import logging
from typing import Any, Dict, List, Optional

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
