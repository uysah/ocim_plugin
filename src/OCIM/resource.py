from typing import Union
from pydantic import BaseModel, Field
from ocelescope import Resource, Graph, GraphNode, GraphEdge, generate_color_map, ORDERED_TREE_LAYOUT, GraphvizLayoutConfig
import uuid
from pm4py.objects.process_tree.obj import Operator


# ============================================

#        Object-Centric Process Tree

# ============================================


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

    def get_activities(self):
        return set(sum([[key[0]] for key in self.get_type_information().keys()],[]))


class OperationNode(TreeNode):
    operator: Operator
    children: list["ProcessNode"] = Field(default_factory=list)

    def get_activities(self):
        return set(sum([[key[0]] for key in self.get_type_information().keys()],[]))

    def get_object_types(self):
        return set(sum([list(value) for value in self.get_type_information().values()],[]))

    def get_type_information(self):
        return {key:value for subtree in self.children for key,value in subtree.get_type_information().items()}

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
            label = node.activity if node.activity != "" else "τ"
            graph_nodes.append(
                GraphNode(
                    id=node.id,
                    shape='rectangle',
                    label=label,
                    color="#A3D5FF",
                    width=max(100, len(label) * 7),
                    height=40,
                )
            )
            for ot_node, category_label in node.get_object_type_nodes():
                ot_label = f"{ot_node.object_type}" if category_label else ot_node.object_type
                graph_nodes.append(
                    GraphNode(
                        id=ot_node.id,
                        shape='rectangle',
                        label=ot_label,
                        color=color_map.get(ot_node.object_type, "#EE2658"),
                        width=max(100, len(ot_label) * 7),
                        height=40,
                    )
                )
                graph_edges.append(
                    GraphEdge(
                        source=node.id,
                        target=ot_node.id,
                        label=category_label if category_label else "",
                    )
                )

        elif isinstance(node, OperationNode):
            graph_nodes.append(
                GraphNode(
                    id=node.id,
                    shape='circle',
                    label = ("||" if node.operator.value == "+" else "↺" if node.operator.value == "*" else node.operator.value),
                    color="#FFD580",
                    width=35,
                    height=35,
                )
            )
            for child in node.children:
                self._build_graph(
                    child,
                    graph_nodes,
                    graph_edges,
                    parent=node.id,
                    color_map=color_map,
                )

        if parent is not None:
            graph_edges.append(GraphEdge(source=parent, target=node.id))

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
                    engine="dot",
                    graphAttrs={
                        "ordering": "out",
                        "rankdir": "TB",
                        "nodesep": 0.5,
                        "ranksep": 1.5,
                        "splines": "line",
                    },
                )
            )