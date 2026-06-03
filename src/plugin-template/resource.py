from typing import Literal, Union
from pydantic import BaseModel, Field
from ocelescope import (Resource, Graph, GraphNode, GraphEdge, GraphvizLayoutConfig, generate_color_map)
import uuid
from enum import Enum

mul_obj = Literal['0', '0...1', '1', "1...n", '0...n']
mul_ev = Literal['0', '1','0...n']


class Operator(Enum):
    SEQUENCE = '->'
    XOR = 'X'
    PARALLEL = '||'
    LOOP = '*'
    OR = 'O'



class TreeNode(BaseModel):
    id: str = Field(default_factory=lambda: str(uuid.uuid4()))

class ObjectTypeNode(TreeNode):
    object_type: str

class LeafNode(TreeNode):
    activity: str
    related: set[str] = Field(default_factory=set)
    divergent: set[str] = Field(default_factory=set)
    convergent: set[str] = Field(default_factory=set)
    deficient: set[str] = Field(default_factory=set)

    def get_type_information(self):
        return {(self.activity,"rel"):self.related, (self.activity,"div"):self.divergent,
                (self.activity,"con"):self.convergent, (self.activity,"def"):self.deficient}

    def get_object_types(self):
        return set(sum([list(value) for value in self.get_type_information().values()],[]))

    def get_object_type_nodes(self) -> list[tuple["ObjectTypeNode", str]]:
        type_info = self.get_type_information()

        category_map: dict[str, list[str]] = {}
        for (activity, category), object_types in type_info.items():
            for ot in object_types:
                category_map.setdefault(ot, []).append(category)

        result = []
        for ot, categories in category_map.items():
            label = " + ".join(c for c in categories if c != "rel")
            result.append((ObjectTypeNode(object_type=ot), label))
        return result

class OperationNode(TreeNode):
    operator: Operator
    children: list["ProcessNode"] = Field(default_factory=list)


ProcessNode = Union[LeafNode, OperationNode]


class ProcessTree(Resource):

    label = "Object-centric Process Tree"
    description = "Object-centric Process Tree"

    root: ProcessNode

    def _collect_object_types(self, node: ProcessNode) -> set[str]:
        if isinstance(node, LeafNode):
            return node.get_object_types()
        elif isinstance(node, OperationNode):
            result = set()
            for child in node.children:
                result |= self._collect_object_types(child)
            return result
        return set()

    def _build_graph(
        self,
        node: ProcessNode,
        graph_nodes: list[GraphNode],
        graph_edges: list[GraphEdge],
        parent: str | None = None,
        color_map: dict = {},
    ):
        if isinstance(node, LeafNode):
            graph_nodes.append(
                GraphNode(
                    id=node.id,
                    shape='circle',
                    label=node.activity if node.activity != "" else "τ",
                    color="#A3D5FF",
                )
            )
            for ot_node, category_label in node.get_object_type_nodes():
                graph_nodes.append(
                    GraphNode(
                        id=ot_node.id,
                        shape='rectangle',
                        label=ot_node.object_type,
                        color=color_map.get(ot_node.object_type, "#EE2658"),
                    )
                )
                graph_edges.append(
                    GraphEdge(
                        source=ot_node.id,
                        target=node.id,
                        label=category_label if category_label else "",
                    )
                )

        elif isinstance(node, OperationNode):
            graph_nodes.append(
                GraphNode(
                    id=node.id,
                    shape='circle',
                    label=node.operator.value,
                    color="#FFD580",
                )
            )
            for child in node.children:
                self._build_graph(child, graph_nodes, graph_edges, parent=node.id, color_map=color_map)

        if parent is not None:
            graph_edges.append(GraphEdge(source=node.id, target=parent))

    def visualize(self) -> Graph:
        nodes: list[GraphNode] = []
        edges: list[GraphEdge] = []

        all_object_types = self._collect_object_types(self.root)
        color_map = generate_color_map(list(all_object_types))

        self._build_graph(self.root, nodes, edges, color_map=color_map)

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