"""
Runner
"""
import logging
from typing import Dict, List, Optional, Type, TypeVar

from metadata.ingestion.ometa.ometa_api import OpenMetadata
from pydantic import BaseModel

from rename.topology import ServiceTopology, TopologyNode, get_topology_node

T = TypeVar("T", bound=BaseModel)


class RawEntityList(BaseModel):
    entities: List[dict]
    total: int
    after: Optional[str] = None


class TopologyRunner:
    """
    Simple topology runner
    Each service implementation will read and write the data
    """

    topology: ServiceTopology
    metadata: OpenMetadata

    def process_nodes(self, nodes: List[TopologyNode]) -> None:
        for node in nodes:
            logging.info(f"Node [{node}]")
            node_producer_fn = getattr(self, node.producer)
            processor_fn = getattr(self, node.processor)

            child_nodes = (
                [get_topology_node(child, self.topology) for child in node.children]
                if node.children
                else []
            )

            logging.info(f"Children [{child_nodes}]")

            for element in node_producer_fn() or []:
                processor_fn(element)
                self.process_nodes(child_nodes)

    def run(self) -> None:
        self.process_nodes([self.topology.root])

    def list_raw_entities(
        self,
        entity: Type[T],
        fields: Optional[List[str]] = None,
        after: str = None,
        limit: int = 100,
        params: Optional[Dict[str, str]] = None,
    ) -> RawEntityList:
        """
        Helps us paginate over the collection
        """

        suffix = self.metadata.get_suffix(entity)
        url_limit = f"?limit={limit}"
        url_after = f"&after={after}" if after else ""
        url_fields = f"&fields={','.join(fields)}" if fields else ""
        resp = self.metadata.client.get(
            path=f"{suffix}{url_limit}{url_after}{url_fields}", data=params
        )

        entities = [t for t in resp["data"]]
        total = resp["paging"]["total"]
        after = resp["paging"]["after"] if "after" in resp["paging"] else None
        return RawEntityList(entities=entities, total=total, after=after)

    def list_all_raw_entities(
        self,
        entity: Type[T],
        fields: Optional[List[str]] = None,
        limit: int = 1000,
        params: Optional[Dict[str, str]] = None,
    ) -> RawEntityList:
        """
        Helps us paginate over the collection
        """

        # First batch of Entities
        entity_list = self.list_raw_entities(
            entity=entity, fields=fields, limit=limit, params=params
        )
        for elem in entity_list.entities:
            yield elem

        after = entity_list.after
        while after:
            entity_list = self.list_raw_entities(
                entity=entity, fields=fields, limit=limit, params=params, after=after
            )
            for elem in entity_list.entities:
                yield elem
            after = entity_list.after
