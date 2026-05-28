from ocelescope import OCEL
from ..resource import ProcessTree, LeafNode, OperationNode,ObjectTypeNode
from collections import defaultdict, Counter
from typing import List
from itertools import combinations
from .dfg import * 
from .interaction_patterns import *
from .detect_tau import * 

def object_centric_inductive_miner(ocel:OCEL) -> ProcessTree:

    #-------------------------------------------------------
    #                   local data
    #-------------------------------------------------------
    activities = list(ocel.e2o.df["ocel:activity"].unique())
    object_types = list(ocel.e2o.df["ocel:type"].unique())
    object_set = list(ocel.e2o.df['ocel:oid'].unique())

    dfg = get_cummulative_directly_follows_relation(ocel)
    clos = get_transitive_closure_follows_relation(ocel)
    

    #-------------------------------------------------------
    #                   global data
    #-------------------------------------------------------
    div, con, rel, defi = get_interaction_patterns(ocel)


    partition, operator = detect_tau_cases(activities,rel,clos,object_types,dfg,div)

    if operator:
        pass

















# def discover_ocpt(ocel: OCEL) -> ProcessTree:
#     """
#     Discover a simplified object-centric process tree from an OCEL.
#     """

#     df = ocel.events.df.copy()
#     activities = df["ocel:activity"].unique().tolist()
    
#     def build_object_nodes(activity,df,ocel:OCEL):

#         object_nodes = []

#         activity_events = df[df["ocel:activity"] == activity]["ocel:eid"].tolist()

#         # ---------------------------------------------------------
#         # all event-object relations for these events
#         # ---------------------------------------------------------

#         e2o = ocel.e2o.df

#         related = e2o[e2o["ocel:eid"].isin(activity_events)]

#         for ot in related["ocel:type"].unique():
#             rel_ot = related[
#                 related["ocel:type"] == ot
#             ]

#             objects_per_event = (
#                 rel_ot
#                 .groupby("ocel:eid")["ocel:oid"]
#                 .nunique()
#             )

#             obj_counts = set(objects_per_event.tolist())

#             events_per_object = (
#                 rel_ot
#                 .groupby("ocel:oid")["ocel:eid"]
#                 .nunique()
#             )

#             eve_counts = set(events_per_object.tolist())
#             def map_mul(values, kind="obj"):

#                 if values == {0}:
#                     return "0"

#                 if values == {1}:
#                     return "1"

#                 if values == {0, 1}:
#                     return "0...1"

#                 has_zero = 0 in values
#                 has_gt_one = any(v > 1 for v in values)

#                 if kind == "eve":
#                     if has_zero and has_gt_one:
#                         return "0...n"
                    
#                     if not has_zero and has_gt_one:
#                         return "1...n"

#                 if kind == "obj" and has_gt_one:
#                         return "0...n"
                
#                 return "0...n"

#             mul_obj = map_mul(obj_counts, kind="obj")
#             mul_eve = map_mul(eve_counts, kind="eve")

#             object_nodes.append(
#                 ObjectTypeNode(
#                     object_type=ot,
#                     mul_obj=mul_obj,
#                     mul_eve=mul_eve,
#                 )
#     )
#         return object_nodes

#     leaf_nodes = []
#     for act in activities:
#         leaf_nodes.append(LeafNode(activity=act, children_object=build_object_nodes(act,df,ocel)))

#     # -------------------------------
#     # Step 4: Build simple sequence tree
#     # -------------------------------
#     if len(leaf_nodes) == 1:
#         root = leaf_nodes[0]
#     else:
#         root = OperationNode(operator="->", children=leaf_nodes)

#     return ProcessTree(root=root)

def build_test_process_tree(ocel: OCEL) -> ProcessTree:

    root = OperationNode(
        operator="->",
        children=[

            # -------------------------------------------------
            # Activity A
            # -------------------------------------------------

            LeafNode(
                activity="A",
                children_object=[
                    ObjectTypeNode(
                        object_type="order",
                        mul_eve="1",
                        mul_obj="1",
                    )
                ],
            ),

            # -------------------------------------------------
            # XOR BLOCK
            # -------------------------------------------------

            OperationNode(
                operator="X",
                children=[

                    LeafNode(
                        activity="B",
                        children_object=[

                            ObjectTypeNode(
                                object_type="order",
                                mul_eve="1",
                                mul_obj="1",
                            ),

                            ObjectTypeNode(
                                object_type="item",
                                mul_eve="0...n",
                                mul_obj="1",
                            ),
                        ],
                    ),

                    LeafNode(
                        activity="C",
                        children_object=[

                            ObjectTypeNode(
                                object_type="order",
                                mul_eve="1",
                                mul_obj="1",
                            ),

                            ObjectTypeNode(
                                object_type="item",
                                mul_eve="0...n",
                                mul_obj="1",
                            ),
                        ],
                    ),
                ],
            ),

            # -------------------------------------------------
            # PARALLEL BLOCK
            # -------------------------------------------------

            OperationNode(
                operator="||",
                children=[

                    LeafNode(
                        activity="D",
                        children_object=[

                            ObjectTypeNode(
                                object_type="order",
                                mul_eve="1",
                                mul_obj="1",
                            ),

                            ObjectTypeNode(
                                object_type="employee",
                                mul_eve="0",
                                mul_obj="1",
                            ),
                        ],
                    ),

                    LeafNode(
                        activity="E",
                        children_object=[

                            ObjectTypeNode(
                                object_type="order",
                                mul_eve="1",
                                mul_obj="1",
                            ),

                            ObjectTypeNode(
                                object_type="employee",
                                mul_eve="0",
                                mul_obj="1",
                            ),
                        ],
                    ),
                ],
            ),

            # -------------------------------------------------
            # Activity F
            # -------------------------------------------------

            LeafNode(
                activity="F",
                children_object=[
                    ObjectTypeNode(
                        object_type="order",
                        mul_eve="1",
                        mul_obj="1",
                    )
                ],
            ),
        ],
    )

    return ProcessTree(root=root)



