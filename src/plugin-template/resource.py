from typing import Literal, Union
from pydantic import BaseModel, Field
from ocelescope import (Resource,Graph,GraphNode,GraphEdge,GraphvizLayoutConfig,generate_color_map,)
import uuid


Operation = Literal[
    "->",
    "X",
    "||",
    "loop",
    '+'
    # "strict_sync",
    # "subset_sync",
    # "overlap_sync",
    # "implication",
    # "temporal_implication",
]


class TreeNode(BaseModel):
    id: str = Field(default_factory=lambda: str(uuid.uuid4()))


class LeafNode(TreeNode):
    activity: str
    # number_objects_per_type: dict
    # number_of_events_per_ot: dict


class OperationNode(TreeNode):
    operator: Operation
    children: list["ProcessNode"] = []


ProcessNode = Union[LeafNode, OperationNode]


class ProcessTree(Resource):

    label = "Process Tree"
    description = "Object-centric process tree"

    root: ProcessNode

    def _build_graph(
        self,
        node: ProcessNode,
        graph_nodes: list[GraphNode],
        graph_edges: list[GraphEdge],
        parent: str | None = None,
    ):

        if isinstance(node, LeafNode):

            graph_nodes.append(
                GraphNode(
                    id=node.id,
                    shape='circle',
                    label=node.activity,
                    color="#A3D5FF",
                )
            )


        elif isinstance(node, OperationNode):

            graph_nodes.append(
                GraphNode(
                    id=node.id,
                    shape='circle',
                    label=node.operator,
                    color="#FFD580",
                )
            )

            for child in node.children:

                self._build_graph(
                    child,
                    graph_nodes,
                    graph_edges,
                    parent=node.id,
                )

        if parent is not None:

            graph_edges.append(
                GraphEdge(
                    source=parent,
                    target=node.id,
                )
            )

    def visualize(self) -> Graph:

        nodes: list[GraphNode] = []
        edges: list[GraphEdge] = []

        self._build_graph(
            self.root,
            nodes,
            edges,
        )

        return Graph(
            type='graph',
            nodes=nodes,
            edges=edges,
            layout_config = GraphvizLayoutConfig(
                    rankdir="TB",
                    nodesep=0.5,
                    ranksep=1.5
                )
        )
        # nodes = [
        #     GraphNode(id="A",shape='circle', label="A", color="#A3D5FF"),
        #     GraphNode(id="B",shape='circle', label="B", color="#FFD580"),
        #     GraphNode(id="C",shape='circle', label="C", color="#A3D5FF"),
        # ]

        # edges = [
        #     GraphEdge(source="A", target="B"),
        #     GraphEdge(source="B", target="C"),
        # ]

        # return Graph(
        #     type='graph',
        #     nodes=nodes,
        #     edges=edges,
        #     layout_config = GraphvizLayoutConfig(
        #             engine="neato",
        #             graphAttrs={"overlap": "prism"}
        #         )    
        # )