"""
Define our simple topology based on the OM Ingestion Framework
"""
from typing import List, Optional

from pydantic import BaseModel, Extra


class TopologyNode(BaseModel):
    class Config:
        extra = Extra.forbid

    producer: str
    processor: str
    children: Optional[List[str]] = None


class ServiceTopology(BaseModel):
    """
    Bounds all service topologies
    """

    root: TopologyNode

    class Config:
        extra = Extra.allow


class TopologyContext(BaseModel):
    """
    Bounds all topology contexts
    """

    class Config:
        extra = Extra.allow


def get_topology_nodes(topology: ServiceTopology) -> List[TopologyNode]:
    """
    Fetch all nodes from a ServiceTopology
    """
    return [value for key, value in topology.__dict__.items()]


def get_topology_node(name: str, topology: ServiceTopology) -> TopologyNode:
    """
    Fetch a topology node by name
    """
    node = topology.__dict__.get(name)
    if not node:
        raise ValueError(f"{name} node not found in {topology}")

    return node
