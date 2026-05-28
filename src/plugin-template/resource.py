from typing import Literal, Union
from pydantic import BaseModel, Field
from ocelescope import (Resource, Graph, GraphNode, GraphEdge, GraphvizLayoutConfig, generate_color_map,)
import uuid


Operation = Literal[
    "->",
    "X",
    "||",
    "loop",
]

mul_obj = Literal['0', '0...1', '1', "1...n", '0...n']
mul_ev = Literal['0', '1','0...n']


class TreeNode(BaseModel):
    id: str = Field(default_factory=lambda: str(uuid.uuid4()))

class ObjectTypeNode(TreeNode):
    object_type: str
    mul_eve: mul_obj 
    mul_obj: mul_ev

class LeafNode(TreeNode):
    activity: str
    children_object: list[ObjectTypeNode] = Field(default_factory=list)


class OperationNode(TreeNode):
    operator: Operation
    children: list["ProcessNode"] = Field(default_factory=list)


ProcessNode = Union[LeafNode, OperationNode,ObjectTypeNode]


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
                    shape='rectangle',
                    label=node.activity,
                    color="#A3D5FF",
                )  
            )
            for child in node.children_object:
                
                graph_edges.append(
                    GraphEdge(
                        source=child.id,
                        target=node.id,
                        label=f"{child.mul_obj}:{child.mul_eve}"  
                    )
                )
                self._build_graph(child, graph_nodes, graph_edges, parent=node.id)

        elif isinstance(node, OperationNode):
            graph_nodes.append(
                GraphNode(
                    id=node.id,
                    shape='rectangle',
                    label=node.operator,
                    color="#FFD580",
                )
            )
            for child in node.children:
                self._build_graph(child, graph_nodes, graph_edges, parent=node.id)

        elif isinstance(node,ObjectTypeNode):
            graph_nodes.append(
                GraphNode(
                id=node.id,
                shape="circle",
                label=node.object_type,
                color="#EE2658",
                )
            )

        if parent is not None and not isinstance(node, ObjectTypeNode):
            graph_edges.append(GraphEdge(source=node.id, target=parent))

    def visualize(self) -> Graph:
        nodes: list[GraphNode] = []
        edges: list[GraphEdge] = []
        self._build_graph(self.root, nodes, edges)

        return Graph(
            type='graph',
            nodes=nodes,
            edges=edges,
            layout_config=GraphvizLayoutConfig(
                rankdir="TB",
                nodesep=0.5,
                ranksep=1.5,
            )
        )