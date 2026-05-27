from ocelescope import OCEL
from .resource import ProcessTree, LeafNode, OperationNode

from collections import defaultdict, Counter
from typing import List
from itertools import combinations


from collections import Counter
from itertools import combinations


def discover_ocim(ocel: OCEL) -> ProcessTree:

    df = ocel.events.df.copy()
    df = df.sort_values("ocel:timestamp")
    activities = df["ocel:activity"].tolist()
    unique = list(dict.fromkeys(activities))



    return ProcessTree(root=LeafNode(activity='a'))

def build_test_process_tree(ocel:OCEL) -> ProcessTree:
    root = OperationNode(
        operator="->",
        children=[
            LeafNode(activity="A"),
            OperationNode(
                operator="X",
                children=[
                    LeafNode(activity="B"),
                    LeafNode(activity="C"),
                ],
            ),
            OperationNode(
                operator="||",
                children=[
                    LeafNode(activity="D"),
                    LeafNode(activity="E"),
                ],
            ),
            LeafNode(activity="F"),
        ],
    )

    return ProcessTree(root=root)