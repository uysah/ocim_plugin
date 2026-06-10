from typing import Literal, Union
from pydantic import BaseModel, Field
from ocelescope import Resource, Graph, GraphNode, GraphEdge, LayoutConfig, generate_color_map
from ocelescope.resource.default.petri_net import PetriNet, Place, Transition, Arc
import uuid
from enum import Enum
from pm4py.objects.process_tree.obj import Operator


# ============================================

#        Object-Centric Process Tree

# ============================================



mul_obj = Literal['0', '0...1', '1', "1...n", '0...n']
mul_ev = Literal['0', '1','0...n']



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
                    shape='circle',
                    label=label,
                    color="#A3D5FF",
                    width=max(120, len(label) * 7),
                    height=40,
                )
            )
            for ot_node, category_label in node.get_object_type_nodes():
                ot_label = f"{ot_node.object_type} ({category_label})" if category_label else ot_node.object_type
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
                    )
                )

        elif isinstance(node, OperationNode):
            graph_nodes.append(
                GraphNode(
                    id=node.id,
                    shape='circle',
                    label= "||" if node.operator.value == '+' else node.operator.value,
                    color="#FFD580",
                    width=30,
                    height=30,
                )
            )
            for child in node.children:
                self._build_graph(child, graph_nodes, graph_edges, parent=node.id, color_map=color_map)

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
            layout_config=LayoutConfig(
                elk_options={
                    "elk.algorithm": "mrtree",
                    "elk.direction": "DOWN",
                    "elk.spacing.nodeNode": 70,
                    "elk.layered.spacing.nodeNodeBetweenLayers": 70,
                    "elk.edgeLabels.inline": True,
                    "elk.edgeLabels.placement": "CENTER",
                }
            )
        )
    

# ============================================

#          Object-Centric Petri Net

# ============================================




# class OCPetriNet(Resource):
#     label = "Object-centric Petri Net"
#     description = "Object-centric Petri Net"

#     places: set[Place]
#     transitions: list[Transition]
#     arc: list[Arc]


#     def visualize(self) -> Graph:
#         ocpn = PetriNet()

        # # Places
        #ocpn.add_place(Place(name="p1", object_type="order"))
        # ocpn.add_place(Place(name="p_order_mid", object_type="order"))
        # ocpn.add_place(Place(name="p_order_end", object_type="order"))
        # ocpn.add_place(Place(name="p_item_start", object_type="item"))
        # ocpn.add_place(Place(name="p_item_end", object_type="item"))

        # # Transitions
        # ocpn.add_transition(Transition(name="place_order", label="place order"))
        # ocpn.add_transition(Transition(name="pick_item", label="pick item"))
        # ocpn.add_transition(Transition(name="ship", label="ship"))

        # # Arcs
        # ocpn.add_arc(Arc(source="place_order", target="p_order_mid"))
        # ocpn.add_arc(Arc(source="p_order_mid", target="ship"))
        # ocpn.add_arc(Arc(source="ship", target="p_order_end"))

        # ocpn.add_arc(Arc(source="p_item_start", target="pick_item"))
        # ocpn.add_arc(Arc(source="pick_item", target="p_item_end"))
        # ocpn.add_arc(Arc(source="p_item_end", target="ship"))

        # # Markings
        # ocpn.initial_marking = {"p_order_start": 1, "p_item_start": 1}
        # ocpn.final_marking = {"p_order_end": 1}

        # return Graph(
        #     type="graph",
        #     nodes=[
        #         GraphNode(
        #             id="p1",
        #             label="Place",
        #             shape="circle",
        #         ),
        #         GraphNode(
        #             id="t1",
        #             label="Transition",
        #             shape="rectangle",
        #         ),
        #     ],
        #     edges=[
        #         GraphEdge(
        #             source="p1",
        #             target="t1",
        #         )
        #     ],
        #     layout_config=GraphvizLayoutConfig(
        #         rankdir="LR"
        #     ),
        # )